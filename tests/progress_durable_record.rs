//! A result earned on this device is never lost because SQLite was busy for longer than its
//! 5 second `busy_timeout`. The catalog shows 100% at once; the recorder journals the events
//! before touching SQLite and keeps retrying in the background; after the lock is released the
//! completion is in SQLite, read back by a reopened store and by a separate process - including
//! when the app process exits mid-retry while the database is still locked.
//!
//! Child processes are this test binary re-run on one `#[ignore]`d helper (`--ignored --exact`)
//! with the work described in environment variables; without them the helpers do nothing.
use molip_quest::{
    github_player::{Github, GithubUser},
    issue_progress::{self, EventKind, LearningEvent, ProgressKey, StudyMode},
    pilot_source,
    progress_overlay::{self, CatalogProgress, ProgressScope},
    progress_sync::{self, ProgressStore},
};
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant};

/// Longer than the store's 5 s busy_timeout, so a single SQLite attempt must fail.
const HOLD: Duration = Duration::from_millis(7500);

fn lock_exclusively(database: &Path) -> rusqlite::Connection {
    let lock = rusqlite::Connection::open(database).unwrap();
    lock.execute_batch("BEGIN EXCLUSIVE").unwrap();
    lock
}
fn stored_completions(database: &Path) -> usize {
    let db = rusqlite::Connection::open(database).unwrap();
    db.query_row("SELECT COUNT(*) FROM progress_events WHERE document LIKE '%\"kind\":\"completed\"%'", [], |r| r.get(0))
        .unwrap_or(0)
}
fn child(test: &str, vars: &[(&str, String)]) -> std::process::Output {
    let mut command = std::process::Command::new(std::env::current_exe().unwrap());
    command.args([test, "--exact", "--ignored", "--nocapture", "--test-threads=1"]);
    command.env_remove("MOLIP_PILOT");
    for (name, value) in vars {
        command.env(name, value);
    }
    let output = command.output().unwrap();
    eprintln!("--- child {test} ---\n{}{}", String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr));
    output
}
fn read_in_another_process(database: &Path, repo: &str, user: u64, course: &str, lesson: &str, revision: &str, required: &[String]) {
    let output = child("child_reads_completion", &[
        ("MQ3_DURABLE_READ", database.display().to_string()),
        ("MQ3_DURABLE_REPO", repo.into()),
        ("MQ3_DURABLE_USER", user.to_string()),
        ("MQ3_DURABLE_COURSE", course.into()),
        ("MQ3_DURABLE_LESSON", lesson.into()),
        ("MQ3_DURABLE_REVISION", revision.into()),
        ("MQ3_DURABLE_REQUIRED", required.join(",")),
    ]);
    assert!(output.status.success(), "a separate process must read the completion");
    assert!(String::from_utf8_lossy(&output.stdout).contains("child-read: complete"));
}

/// The lesson start and graded attempts the player produces for a final clear.
fn clear(key: &ProgressKey, revision: &str, required: &[String]) -> (Vec<LearningEvent>, Vec<LearningEvent>) {
    let round = issue_progress::new_id();
    let started = LearningEvent::new(key.clone(), revision, StudyMode::Full, &round, EventKind::Started);
    let mut latest = vec![started.clone()];
    let mut recorded = vec![started];
    for id in required {
        let mut attempt = LearningEvent::new(key.clone(), revision, StudyMode::Full, &round, EventKind::Attempt);
        attempt.task_id = Some(id.clone());
        attempt.passed = true;
        latest = progress_sync::apply_result(latest, &attempt, required);
        recorded.push(attempt);
    }
    (latest, recorded)
}

#[test]
fn a_clear_survives_sqlite_busy_beyond_its_timeout_and_reaches_disk_after_release() {
    std::env::set_var("MOLIP_PILOT", "1");
    let github = Github::new();
    let user = github.user().unwrap();
    let course = github.course(pilot_source::REPOSITORY).unwrap();
    let lesson = github.lesson(&course.lessons[0]).unwrap();
    let required = lesson.required_tasks();
    let scope = ProgressScope::new(&course.repository, user.id, &course.id);
    let key = ProgressKey { user_id: user.id, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
    let database = molip_quest::data_dir().unwrap().join("progress-events.sqlite3");
    let store = ProgressStore::installed().unwrap();
    // Uploads stay off so only the local save is exercised.
    std::fs::write(pilot_source::data_dir().unwrap().join("pilot-progress-blocked"), "").unwrap();

    let lock = lock_exclusively(&database);
    let locked_at = Instant::now();

    // Grading happens in memory and goes to the overlay; the catalog reads 100% at once.
    let (latest, recorded) = clear(&key, &lesson.revision, &required);
    let overlay = progress_overlay::shared();
    overlay.remember(&course.repository, &latest);
    let mut catalog = CatalogProgress::default();
    let started = Instant::now();
    catalog.require(&scope, &lesson.id, &lesson.revision, required.clone());
    let view = catalog.view(&scope, overlay, &course.lessons);
    assert!(started.elapsed() < Duration::from_millis(50));
    assert!(issue_progress::status(&view.0[&lesson.id], &lesson.revision, &required).current, "100% at once");

    // One `progress-record` thread per save, holding the record guard, exactly like the player.
    let mut recorders = vec![];
    for (index, event) in recorded.iter().enumerate() {
        let guard = progress_sync::record_guard();
        let (github, user, repo, title, event) = (github.clone(), user.clone(), course.repository.clone(), lesson.title.clone(), event.clone());
        let required = if index == 0 { vec![] } else { required.clone() };
        recorders.push(std::thread::Builder::new().name("progress-record".into()).spawn(move || {
            let _guard = guard;
            github.record(&repo, &user, &title, &event, &required)
        }).unwrap());
        std::thread::sleep(Duration::from_millis(50));
    }

    // Past the busy timeout: the first SQLite attempt has failed, yet nothing was dropped.
    std::thread::sleep(Duration::from_millis(6500).saturating_sub(locked_at.elapsed()));
    assert!(locked_at.elapsed() > Duration::from_secs(5));
    assert!(recorders.iter().all(|r| !r.is_finished()), "recorders keep retrying instead of logging and dropping");
    assert_eq!(store.journal_len(), recorded.len(), "every save is on disk in the journal");
    let view = catalog.view(&scope, overlay, &course.lessons);
    assert!(issue_progress::status(&view.0[&lesson.id], &lesson.revision, &required).current, "still 100% while locked");

    std::thread::sleep(HOLD.saturating_sub(locked_at.elapsed()));
    lock.execute_batch("ROLLBACK").unwrap();
    drop(lock);
    let released = Instant::now();
    eprintln!("released after {:?}", locked_at.elapsed());
    for recorder in recorders {
        let latest = recorder.join().unwrap().expect("saved once SQLite is free");
        assert!(latest.iter().all(|e| e.key == key));
    }
    eprintln!("all saves committed {:?} after release", released.elapsed());
    assert!(released.elapsed() < Duration::from_secs(12));
    assert_eq!(store.journal_len(), 0, "committed entries leave the journal");

    // A reopened store reads it from SQLite: one completion for this revision, mode and round.
    assert_eq!(stored_completions(&database), 1);
    let reopened = ProgressStore::new(&database);
    let events = reopened.course_events(&course.repository, user.id, &course.id).unwrap();
    assert!(issue_progress::status(&events[&lesson.id], &lesson.revision, &required).current);
    assert_eq!(events[&lesson.id].iter().filter(|e| e.kind == EventKind::Completed).count(), 1);
    assert!(reopened.pending_count(user.id).unwrap() >= recorded.len(), "queued for upload as usual");
    // The account boundary holds for the stored history.
    assert!(reopened.course_events(&course.repository, user.id + 1, &course.id).unwrap().is_empty());
    read_in_another_process(&database, &course.repository, user.id, &course.id, &lesson.id, &lesson.revision, &required);
}

#[test]
fn an_app_that_exits_while_sqlite_is_still_locked_keeps_the_clear_for_the_next_launch() {
    let root = tempfile::tempdir().unwrap();
    let database = root.path().join("progress-events.sqlite3");
    let required = vec!["a".to_string(), "b".to_string()];
    let lock = lock_exclusively(&database);

    // The "app" process records the clear and exits abruptly mid-retry, beyond the busy timeout,
    // with SQLite still locked.
    let output = child("child_records_then_exits_abruptly", &[
        ("MQ3_DURABLE_RECORD", database.display().to_string()),
        ("MQ3_DURABLE_REQUIRED", required.join(",")),
    ]);
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("child-record: journaled 3, finished 0"), "the child exited before any save completed");
    lock.execute_batch("ROLLBACK").unwrap();
    drop(lock);
    assert_eq!(stored_completions(&database), 0, "nothing reached SQLite in the child");
    assert_eq!(ProgressStore::new(&database).journal_len(), 3);

    // Next launch: the first local read stores the journal and shows the completion.
    let store = ProgressStore::new(&database);
    let events = store.course_events("owner/course", 7, "course").unwrap();
    assert!(issue_progress::status(&events["lesson"], "r1", &required).current);
    assert_eq!(store.journal_len(), 0);
    assert_eq!(stored_completions(&database), 1, "replayed into SQLite, not only shown from the journal");
    assert_eq!(store.pending_count(7).unwrap(), 4, "start, two attempts and completion queued for upload");
    read_in_another_process(&database, "owner/course", 7, "course", "lesson", "r1", &required);
}

#[test]
fn when_neither_journal_nor_sqlite_can_be_written_the_error_says_the_save_is_only_in_memory() {
    let root = tempfile::tempdir().unwrap();
    let database = root.path().join("progress-events.sqlite3");
    // A file where the journal folder should be: the journal cannot be created.
    std::fs::write(database.with_extension("journal"), "").unwrap();
    let lock = lock_exclusively(&database);
    let store = ProgressStore::new(&database);
    let user = GithubUser { id: 7, login: "learner".into() };
    let (_, recorded) = clear(&ProgressKey { user_id: 7, course_id: "course".into(), lesson_id: "lesson".into() }, "r1", &["a".into()]);
    let error = store.record_durably("owner/course", &user, "Lesson", &recorded[0], &[], Duration::from_secs(1)).unwrap_err();
    assert!(error.contains("앱을 닫으면 이번 기록은 사라져요"), "{error}");
    drop(lock);
}

fn required_from_env() -> Vec<String> {
    std::env::var("MQ3_DURABLE_REQUIRED").unwrap().split(',').map(String::from).collect()
}

#[test]
#[ignore = "child process of an_app_that_exits_while_sqlite_is_still_locked_keeps_the_clear_for_the_next_launch"]
fn child_records_then_exits_abruptly() {
    let Some(database) = std::env::var_os("MQ3_DURABLE_RECORD").map(PathBuf::from) else { return };
    let required = required_from_env();
    let store = ProgressStore::new(&database);
    let user = GithubUser { id: 7, login: "learner".into() };
    let key = ProgressKey { user_id: 7, course_id: "course".into(), lesson_id: "lesson".into() };
    let mut events = vec![LearningEvent::new(key.clone(), "r1", StudyMode::Full, "round", EventKind::Started)];
    for id in &required {
        let mut attempt = LearningEvent::new(key.clone(), "r1", StudyMode::Full, "round", EventKind::Attempt);
        attempt.task_id = Some(id.clone());
        attempt.passed = true;
        events.push(attempt);
    }
    let finished = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
    for (index, event) in events.into_iter().enumerate() {
        let (store, user, finished) = (store.clone(), user.clone(), finished.clone());
        let required = if index == 0 { vec![] } else { required.clone() };
        std::thread::spawn(move || {
            let result = store.record_durably("owner/course", &user, "Lesson", &event, &required, progress_sync::RECORD_RETRY_WINDOW);
            finished.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            result
        });
        std::thread::sleep(Duration::from_millis(50));
    }
    std::thread::sleep(Duration::from_millis(6000));
    println!("child-record: journaled {}, finished {}", store.journal_len(), finished.load(std::sync::atomic::Ordering::SeqCst));
    use std::io::Write;
    std::io::stdout().flush().unwrap();
    // Like the window closing: no orderly shutdown of the recorder threads.
    std::process::exit(0);
}

#[test]
#[ignore = "child process of the durable record tests"]
fn child_reads_completion() {
    let Some(database) = std::env::var_os("MQ3_DURABLE_READ").map(PathBuf::from) else { return };
    let var = |name: &str| std::env::var(name).unwrap();
    let store = ProgressStore::new(&database);
    let events = store.course_events(&var("MQ3_DURABLE_REPO"), var("MQ3_DURABLE_USER").parse().unwrap(), &var("MQ3_DURABLE_COURSE")).unwrap();
    let lesson = events.get(&var("MQ3_DURABLE_LESSON")).cloned().unwrap_or_default();
    let status = issue_progress::status(&lesson, &var("MQ3_DURABLE_REVISION"), &required_from_env());
    assert!(status.current);
    println!("child-read: complete ({} events, journal {})", lesson.len(), store.journal_len());
}
