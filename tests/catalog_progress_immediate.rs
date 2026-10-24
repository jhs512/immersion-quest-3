//! A lesson cleared on this device reads 100% in the course catalog the moment the learner
//! returns, before the background recorder commits it to SQLite and before any GitHub read or
//! upload; slow, stale or failed remote work and account/course/revision boundaries never
//! change that. Production `Github`, `ProgressStore`, `apply_result` and the catalog overlay run
//! against the isolated pilot transport (`MOLIP_PILOT`), whose remote reads can be delayed or
//! cut off and whose uploads can be blocked.
use molip_quest::{
    github_player::{Github, GithubUser},
    issue_progress::{self, EventKind, LearningEvent, ProgressKey, StudyMode},
    pilot_source,
    progress_overlay::{self, CatalogProgress, ProgressScope},
    progress_sync::{self, ProgressStore},
};
use std::time::{Duration, Instant};

const REMOTE_DELAY_MS: u64 = 1500;

fn remote_reads() -> usize {
    std::fs::read_to_string(pilot_source::data_dir().unwrap().join("pilot-remote-reads"))
        .map(|raw| raw.lines().count())
        .unwrap_or(0)
}
fn flag(name: &str, on: bool) {
    let path = pilot_source::data_dir().unwrap().join(name);
    if on { std::fs::write(path, "").unwrap() } else { let _ = std::fs::remove_file(path); }
}
fn percent(view: &(std::collections::HashMap<String, Vec<LearningEvent>>, std::collections::HashMap<String, Vec<String>>), lesson: &str, revision: &str) -> usize {
    let events = view.0.get(lesson).cloned().unwrap_or_default();
    let required = view.1.get(lesson).cloned().unwrap_or_default();
    issue_progress::learning_progress(&events, revision, &required).percent
}

#[test]
fn final_clear_reads_complete_in_the_catalog_before_storage_and_remote_work() {
    std::env::set_var("MOLIP_PILOT", "1");
    let github = Github::new();
    let user = github.user().unwrap();
    let course = github.course(pilot_source::REPOSITORY).unwrap();
    let lesson = github.lesson(&course.lessons[0]).unwrap();
    let required = lesson.required_tasks();
    assert_eq!(required.len(), 2);
    let scope = ProgressScope::new(&course.repository, user.id, &course.id);
    let key = ProgressKey { user_id: user.id, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
    let round = issue_progress::new_id();
    let overlay = progress_overlay::shared();

    // The catalog's first load, before any learning: 0%, and a reply that will be stale later.
    let mut catalog = CatalogProgress::default();
    let before = github.course_progress(&course, &user).unwrap();
    assert!(catalog.accept(before.clone(), &scope));
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 0);

    // GitHub is slow to read and refuses uploads from here on.
    std::fs::write(pilot_source::data_dir().unwrap().join("pilot-remote-read-delay-ms"), REMOTE_DELAY_MS.to_string()).unwrap();
    flag("pilot-progress-blocked", true);

    // The player grades both problems in memory (the same `apply_result` the submit button
    // uses) and hands the events to the catalog overlay, as `onrecord` does.
    let mut latest = vec![LearningEvent::new(key.clone(), &lesson.revision, StudyMode::Full, &round, EventKind::Started)];
    let mut attempts = vec![];
    for id in &required {
        let mut attempt = LearningEvent::new(key.clone(), &lesson.revision, StudyMode::Full, &round, EventKind::Attempt);
        attempt.task_id = Some(id.clone());
        attempt.passed = true;
        latest = progress_sync::apply_result(latest, &attempt, &required);
        attempts.push(attempt);
    }
    assert!(latest.iter().any(|e| e.kind == EventKind::Completed));
    overlay.remember(&course.repository, &latest);

    // The background recorder cannot commit: SQLite is locked exclusively by another writer,
    // exactly as the native pilot's `pause-record` does.
    let database = molip_quest::data_dir().unwrap().join("progress-events.sqlite3");
    let lock = rusqlite::Connection::open(&database).unwrap();
    lock.execute_batch("BEGIN EXCLUSIVE").unwrap();
    let recorder = {
        // The lesson start (recorded at open), then each graded attempt, like the player.
        let started = latest.iter().find(|e| e.kind == EventKind::Started).unwrap().clone();
        let (github, user, repository, title, attempts, required) = (github.clone(), user.clone(), course.repository.clone(), lesson.title.clone(), attempts.clone(), required.clone());
        std::thread::spawn(move || {
            github.record(&repository, &user, &title, &started, &[]).unwrap();
            for attempt in &attempts { github.record(&repository, &user, &title, attempt, &required).unwrap(); }
        })
    };
    std::thread::sleep(Duration::from_millis(200));
    assert!(!recorder.is_finished(), "the local save must still be pending");

    // Return to the catalog: the requirements come from the open lesson (`onback`), the events
    // from the overlay. It is synchronous - no SQLite read, no remote read.
    let reads = remote_reads();
    let started = Instant::now();
    catalog.require(&scope, &lesson.id, &lesson.revision, required.clone());
    let view = catalog.view(&scope, overlay, &course.lessons);
    let elapsed = started.elapsed();
    assert_eq!(percent(&view, &lesson.id, &lesson.revision), 100);
    assert!(issue_progress::status(&view.0[&lesson.id], &lesson.revision, &required).current);
    assert!(elapsed < Duration::from_millis(50), "catalog view took {elapsed:?}");
    assert_eq!(remote_reads(), reads, "showing the catalog must not read GitHub");
    assert!(!recorder.is_finished(), "100% was shown before the local save completed");
    eprintln!("catalog 100% after {elapsed:?} with the local save still blocked and no remote read");

    // A stale reply read before the clear cannot roll the overlay back.
    assert!(catalog.accept(before, &scope));
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 100);

    lock.execute_batch("ROLLBACK").unwrap();
    drop(lock);
    recorder.join().unwrap();

    // The loader's first phase is local: it returns at once although GitHub is slow.
    let reads = remote_reads();
    let started = Instant::now();
    let local = github.course_progress(&course, &user).unwrap();
    let elapsed = started.elapsed();
    assert!(elapsed < Duration::from_millis(REMOTE_DELAY_MS / 3), "local catalog read took {elapsed:?}");
    assert_eq!(remote_reads(), reads, "the local phase must not read GitHub");
    assert!(issue_progress::status(&local.events[&lesson.id], &lesson.revision, &local.required[&lesson.id]).current);
    let raw = github.course_events(&course.repository, &user, &course.id).unwrap();
    assert!(raw[&lesson.id].iter().any(|e| e.kind == EventKind::Completed), "Github::course_events returns local completion without waiting");
    assert!(catalog.accept(local, &scope));

    // The background phase waits for GitHub, which holds nothing yet (uploads are blocked). The
    // late, remotely-stale reply still contains the local completion and only adds to the view.
    let started = Instant::now();
    let refreshed = github.refreshed_course_progress(&course, &user).unwrap();
    assert!(started.elapsed() >= Duration::from_millis(REMOTE_DELAY_MS), "the refresh really waited for the slow remote");
    assert!(remote_reads() > reads);
    assert!(issue_progress::status(&refreshed.events[&lesson.id], &lesson.revision, &refreshed.required[&lesson.id]).current);
    assert!(catalog.accept(refreshed, &scope));
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 100);

    // Offline: the refresh falls back to local history; still complete.
    flag("pilot-remote-offline", true);
    let offline = github.refreshed_course_progress(&course, &user).unwrap();
    assert!(issue_progress::status(&offline.events[&lesson.id], &lesson.revision, &offline.required[&lesson.id]).current);
    assert!(catalog.accept(offline, &scope));
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 100);

    // Upload fails while blocked; history stays pending and the catalog stays complete.
    let store = ProgressStore::installed().unwrap();
    assert!(store.pending_count(user.id).unwrap() >= 4);
    assert!(store.flush_pilot_hour().is_err(), "upload is blocked");
    assert!(store.pending_count(user.id).unwrap() >= 4, "a failed upload keeps the history queued");
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 100);
    // The retry succeeds once GitHub accepts uploads again.
    flag("pilot-progress-blocked", false);
    flag("pilot-remote-offline", false);
    std::fs::remove_file(pilot_source::data_dir().unwrap().join("pilot-remote-read-delay-ms")).unwrap();
    store.flush_pilot_hour().unwrap();
    assert_eq!(store.pending_count(user.id).unwrap(), 0);
    let uploaded = github.refreshed_course_progress(&course, &user).unwrap();
    assert!(issue_progress::status(&uploaded.events[&lesson.id], &lesson.revision, &uploaded.required[&lesson.id]).current);
    assert_eq!(uploaded.events[&lesson.id].iter().filter(|e| e.kind == EventKind::Completed).count(), 1, "overlay and stored completion are one event");
    assert!(catalog.accept(uploaded, &scope));
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 100);

    // Another account on the same course sees none of this, locally, remotely or in the overlay,
    // and a late reply for the first account is not accepted into its catalog.
    let other = GithubUser { id: user.id + 1, login: "someone-else".into() };
    let other_scope = ProgressScope::new(&course.repository, other.id, &course.id);
    assert!(overlay.events(&other_scope).is_empty());
    assert!(github.course_events(&course.repository, &other, &course.id).unwrap().is_empty());
    assert!(github.refreshed_course_progress(&course, &other).is_err(), "a different gh account cannot read through this login");
    let mut switched = catalog.clone();
    let late = github.course_progress(&course, &user).unwrap();
    assert!(!switched.accept(late.clone(), &other_scope));
    assert_eq!(percent(&switched.view(&other_scope, overlay, &course.lessons), &lesson.id, &lesson.revision), 0);

    // Another course of the same account: a late reply for this course is ignored there.
    let other_course = ProgressScope::new(&course.repository, user.id, "another-course");
    assert!(!switched.accept(late, &other_course));
    assert!(switched.view(&other_course, overlay, &course.lessons).0.is_empty());

    // A new revision that replaced one problem: the fresh completion of the old revision does
    // not make the new one complete (the kept problem still counts, by stable step identity).
    pilot_source::set_version('c').unwrap();
    let revised = github.course(pilot_source::REPOSITORY).unwrap();
    let replacement = github.lesson(&revised.lessons[0]).unwrap();
    assert_ne!(replacement.revision, lesson.revision);
    let mut next = CatalogProgress::default();
    assert!(next.accept(github.course_progress(&revised, &user).unwrap(), &scope));
    let view = next.view(&scope, overlay, &revised.lessons);
    assert_eq!(percent(&view, &lesson.id, &replacement.revision), 50);
    assert!(!issue_progress::status(&view.0[&lesson.id], &replacement.revision, &view.1[&lesson.id]).current);
    assert!(issue_progress::status(&view.0[&lesson.id], &replacement.revision, &view.1[&lesson.id]).completed, "the earlier completion is kept as history");
}
