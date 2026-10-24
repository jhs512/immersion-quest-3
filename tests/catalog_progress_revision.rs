//! One catalog lives across a content update of the same account and course (the player keeps
//! its `CatalogProgress` signal; `onapply` only swaps the manifest). Requirements read for the
//! previous lesson revision - already in the catalog, or delivered late by a loader that started
//! before the update - must not decide the new revision's card, while the event history of both
//! revisions is still united. Production `Github`, `apply_result` and the catalog overlay run
//! against the isolated pilot transport (`MOLIP_PILOT`): version 'a' -> 'c' replaces one of the
//! lesson's two required problems.
use molip_quest::{
    github_player::Github,
    issue_progress::{self, EventKind, LearningEvent, ProgressKey, StudyMode},
    pilot_source,
    progress_overlay::{self, CatalogProgress, ProgressScope},
    progress_sync,
};

fn percent(view: &(std::collections::HashMap<String, Vec<LearningEvent>>, std::collections::HashMap<String, Vec<String>>), lesson: &str, revision: &str) -> Option<usize> {
    let events = view.0.get(lesson).cloned().unwrap_or_default();
    view.1.get(lesson).map(|required| issue_progress::learning_progress(&events, revision, required).percent)
}

#[test]
fn a_lesson_revision_update_never_uses_the_previous_revisions_requirements() {
    std::env::set_var("MOLIP_PILOT", "1");
    let github = Github::new();
    let user = github.user().unwrap();
    let old_course = github.course(pilot_source::REPOSITORY).unwrap();
    let old_lesson = github.lesson(&old_course.lessons[0]).unwrap();
    let old_required = old_lesson.required_tasks();
    let scope = ProgressScope::new(&old_course.repository, user.id, &old_course.id);
    let overlay = progress_overlay::shared();

    // The catalog's load for the previous revision; a second loader result read at the same
    // time is held back to be delivered late, after the update.
    let mut catalog = CatalogProgress::default();
    assert!(catalog.accept(github.course_progress(&old_course, &user).unwrap(), &scope));
    let delayed_previous = github.course_progress(&old_course, &user).unwrap();
    assert_eq!(delayed_previous.required[&old_lesson.id], old_required);

    // A content update replaces one required problem; same account, course and repository.
    pilot_source::set_version('c').unwrap();
    let course = github.course(pilot_source::REPOSITORY).unwrap();
    let lesson = github.lesson(&course.lessons[0]).unwrap();
    let required = lesson.required_tasks();
    assert_eq!(course.id, old_course.id);
    assert_eq!(lesson.id, old_lesson.id);
    assert_ne!(lesson.revision, old_lesson.revision);
    assert_ne!(required, old_required, "the update changes the required problems");
    let kept: Vec<_> = required.iter().filter(|id| old_required.contains(id)).cloned().collect();
    assert_eq!(kept.len(), 1, "one problem is kept by stable step identity");

    // The learner clears the new revision; the player hands the events to the overlay at once.
    let key = ProgressKey { user_id: user.id, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
    let round = issue_progress::new_id();
    let mut latest = vec![LearningEvent::new(key.clone(), &lesson.revision, StudyMode::Full, &round, EventKind::Started)];
    for id in &required {
        let mut attempt = LearningEvent::new(key.clone(), &lesson.revision, StudyMode::Full, &round, EventKind::Attempt);
        attempt.task_id = Some(id.clone());
        attempt.passed = true;
        latest = progress_sync::apply_result(latest, &attempt, &required);
    }
    assert!(issue_progress::status(&latest, &lesson.revision, &required).current);
    overlay.remember(&course.repository, &latest);

    // Immediate return (`onback`) before the new loader delivers: the open lesson's requirements
    // must decide its card even though the catalog still holds the previous revision's list.
    catalog.require(&scope, &lesson.id, &lesson.revision, required.clone());
    let view = catalog.view(&scope, overlay, &course.lessons);
    assert_eq!(view.1.get(&lesson.id), Some(&required), "require() on return must replace the previous revision's requirements");
    assert_eq!(percent(&view, &lesson.id, &lesson.revision), Some(100));

    // A loader that started before the update delivers its previous-revision result late.
    assert!(catalog.accept(delayed_previous, &scope), "same scope: its events are still united");
    let view = catalog.view(&scope, overlay, &course.lessons);
    assert_eq!(view.1.get(&lesson.id), Some(&required), "a late previous-revision result must not overwrite the current requirements");
    assert_eq!(percent(&view, &lesson.id, &lesson.revision), Some(100));
    assert!(issue_progress::status(&view.0[&lesson.id], &lesson.revision, &required).current);
    assert!(view.0[&lesson.id].iter().all(|e| e.key == key), "only this account, course and lesson");

    // The new loader's own result (read for the current manifest) agrees and replaces nothing.
    let current = github.course_progress(&course, &user).unwrap();
    assert_eq!(current.revisions[&lesson.id], lesson.revision);
    assert!(catalog.accept(current, &scope));
    assert_eq!(percent(&catalog.view(&scope, overlay, &course.lessons), &lesson.id, &lesson.revision), Some(100));
    // The previous revision's list is still the one used where that revision is shown.
    assert_eq!(catalog.view(&scope, overlay, &old_course.lessons).1.get(&lesson.id), Some(&old_required));
}
