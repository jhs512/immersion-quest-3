//! Lesson-level progress reset and designated final challenges, judged on the same event history
//! the catalog, lesson player, local store and GitHub sync use.
use molip_quest::github_player::GithubUser;
use molip_quest::issue_progress::*;
use molip_quest::progress_sync::{apply_result, ProgressStore};

const REPO: &str = "owner/course";
fn stp(n: u32) -> String { format!("stp_3f59e7bd-70c1-4e81-9cb0-{n:012}") }
fn key(user: u64, lesson: &str) -> ProgressKey { ProgressKey { user_id: user, course_id: "course".into(), lesson_id: lesson.into() } }
fn attempt(key: &ProgressKey, revision: &str, round: &str, task: &str, passed: bool, at: u64) -> LearningEvent {
    let mut event = LearningEvent::new(key.clone(), revision, StudyMode::Full, round, EventKind::Attempt);
    event.task_id = Some(task.into());
    event.passed = passed;
    event.at = at;
    event
}
fn reset_at(key: &ProgressKey, at: u64, known: &[LearningEvent]) -> LearningEvent {
    let mut event = reset_event(key.clone(), "v1", StudyMode::Full, "round", &[]);
    event.at = at;
    event.voids = known.iter().filter(|e| e.at >= at).map(|e| e.id.clone()).collect();
    event
}
/// Thirteen required problems; the last one is the designated final challenge.
fn required() -> Vec<String> { (1..=13).map(stp).collect() }
fn challenge() -> String { stp(13) }

#[test]
fn challenge_clears_the_lesson_while_the_practice_gauge_stays_truthful() {
    let k = key(7, "lesson");
    let events = vec![attempt(&k, "v1", "r", &stp(1), true, 10), attempt(&k, "v1", "r", &stp(2), true, 11), attempt(&k, "v1", "r", &challenge(), true, 12)];
    let clear = lesson_clear(&events, "v1", &required(), &challenge());
    assert!(clear.challenge && !clear.full && clear.cleared());
    let gauge = learning_progress(&events, "v1", &required());
    // Skipped problems are not made solved: 3 of 13 passed (two practice + the challenge).
    assert_eq!((gauge.solved, gauge.total), (3, 13));
    assert!(gauge.percent < 100);
    assert!(!status(&events, "v1", &required()).current, "a challenge clear is not a full completion");
    // The lesson-completion recorder does not invent a completion for skipped problems either.
    let latest = apply_result(events[..2].to_vec(), &events[2], &required());
    assert!(!latest.iter().any(|e| e.kind == EventKind::Completed));
}

#[test]
fn failing_running_or_undesignated_problems_never_clear_by_challenge() {
    let k = key(7, "lesson");
    let failed = vec![attempt(&k, "v1", "r", &challenge(), false, 10)];
    assert!(!lesson_clear(&failed, "v1", &required(), &challenge()).cleared());
    // An example run or an explanation of the challenge is not a pass.
    let mut run = LearningEvent::new(k.clone(), "v1", StudyMode::Full, "r", EventKind::ExampleRun);
    run.task_id = Some(challenge());
    let mut viewed = LearningEvent::new(k.clone(), "v1", StudyMode::Full, "r", EventKind::ExplanationViewed);
    viewed.task_id = Some(challenge());
    assert!(!lesson_clear(&[run, viewed], "v1", &required(), &challenge()).cleared());
    // Without a designation, or with one that is not a required problem of this revision, the
    // last problem passed alone does not clear the lesson.
    let passed = vec![attempt(&k, "v1", "r", &challenge(), true, 10)];
    assert!(!lesson_clear(&passed, "v1", &required(), "").cleared());
    assert!(!lesson_clear(&passed, "v1", &required()[..12], &challenge()).cleared());
}

#[test]
fn full_completion_still_clears_and_both_states_are_reported() {
    let k = key(7, "lesson");
    let mut events = vec![];
    for task in required() { events = apply_result(events, &attempt(&k, "v1", "r", &task, true, 10), &required()); }
    let clear = lesson_clear(&events, "v1", &required(), &challenge());
    assert!(clear.full && clear.challenge);
    assert_eq!(learning_progress(&events, "v1", &required()).percent, 100);
}

#[test]
fn reset_voids_this_lessons_progress_only() {
    let k = key(7, "lesson");
    let neighbour = key(7, "neighbour");
    let other_account = key(8, "lesson");
    let mut events = vec![];
    for task in required() { events = apply_result(events, &attempt(&k, "v1", "r", &task, true, 10), &required()); }
    let neighbour_events = vec![attempt(&neighbour, "v1", "r", &challenge(), true, 10)];
    let other_events = vec![attempt(&other_account, "v1", "r", &challenge(), true, 10)];
    let reset = reset_at(&k, 20, &events);
    events.push(reset.clone());
    assert_eq!(learning_progress(&events, "v1", &required()).solved, 0);
    let state = status(&events, "v1", &required());
    assert!(!state.completed && !state.current && state.full_completions == 0);
    assert!(!lesson_clear(&events, "v1", &required(), &challenge()).cleared());
    assert!(learned_tasks(&events, "v1").is_empty());
    // Every original event is still in the history; only the count changed.
    assert!(events.iter().filter(|e| e.kind == EventKind::Completed).count() == 1);
    // Neighbouring lesson and another account keep their own progress.
    assert!(lesson_clear(&neighbour_events, "v1", &required(), &challenge()).challenge);
    assert!(lesson_clear(&other_events, "v1", &required(), &challenge()).challenge);
    // A reset recorded for one key never voids another key's events, even in one merged list.
    let mixed = [neighbour_events.clone(), vec![reset]].concat();
    assert_eq!(effective(&mixed).len(), 1);
}

#[test]
fn late_and_same_second_history_stays_void_and_new_work_counts() {
    let k = key(7, "lesson");
    let same_second = attempt(&k, "v1", "r", &stp(1), true, 20);
    let reset = reset_at(&k, 20, &[same_second.clone()]);
    // An upload from another device, made before the reset, arrives afterwards.
    let late = attempt(&k, "v1", "r", &stp(2), true, 15);
    // New work in the same second as the reset, made after it.
    let after_same_second = attempt(&k, "v1", "r", &stp(3), true, 20);
    let events = merge(vec![reset, late, same_second, after_same_second.clone()], &k);
    assert_eq!(learned_tasks(&events, "v1"), [stp(3)].into_iter().collect());
    assert_eq!(effective(&events), vec![after_same_second]);
}

#[test]
fn a_reset_round_can_complete_again_with_its_own_completion() {
    let k = key(7, "lesson");
    let required = vec![stp(1)];
    let first = apply_result(vec![], &attempt(&k, "v1", "r", &stp(1), true, 10), &required);
    let old_done = first.iter().find(|e| e.kind == EventKind::Completed).unwrap().id.clone();
    let mut events = first;
    events.push(reset_at(&k, 20, &events));
    assert!(!status(&events, "v1", &required).completed);
    let again = attempt(&k, "v1", "r", &stp(1), true, 30);
    let events = apply_result(events, &again, &required);
    let done: Vec<_> = events.iter().filter(|e| e.kind == EventKind::Completed).collect();
    assert_eq!(done.len(), 2);
    assert!(done.iter().any(|e| e.id != old_done && e.id.contains("after-reset")));
    assert!(status(&events, "v1", &required).current);
    // Replaying the same pass (another device, a journal replay) does not add a third completion.
    let replayed = apply_result(events.clone(), &again, &required);
    assert_eq!(merge(replayed, &k).iter().filter(|e| e.kind == EventKind::Completed).count(), 2);
}

#[test]
fn revisions_keep_stable_challenges_and_a_changed_designation_needs_the_new_problem() {
    let k = key(7, "lesson");
    let events = vec![attempt(&k, "v1", "r", &challenge(), true, 10)];
    // Same stable step code, revised lesson: the passed challenge still counts.
    assert!(lesson_clear(&events, "v2", &required(), &challenge()).challenge);
    // A revision that designates a different problem requires that problem.
    let mut revised = required();
    revised.push(stp(14));
    assert!(!lesson_clear(&events, "v3", &revised, &stp(14)).challenge);
    // Legacy (non-stable) ids count only in their own revision.
    let legacy = vec![attempt(&k, "v1", "r", "final", true, 10)];
    assert!(lesson_clear(&legacy, "v1", &["final".into()], "final").challenge);
    assert!(!lesson_clear(&legacy, "v2", &["final".into()], "final").challenge);
}

#[test]
fn reset_events_round_trip_through_issue_comments_and_old_events_still_parse() {
    let k = key(7, "lesson");
    let known = attempt(&k, "v1", "r", &stp(1), true, u64::MAX);
    let reset = reset_event(k.clone(), "v1", StudyMode::Full, "r", &[known.clone()]);
    assert_eq!(reset.voids, vec![known.id.clone()], "a future-stamped known event is voided by id");
    let parsed = parse_events(&batch_comment(&[reset.clone(), known.clone()]));
    assert_eq!(parsed, vec![reset.clone(), known]);
    assert!(reset.comment().contains("진도 초기화"));
    // An event written before this field existed has no `voids` and still parses.
    let old = r#"{"id":"x","key":{"user_id":7,"course_id":"course","lesson_id":"lesson"},"revision":"v1","mode":"full","round":"r","at":1,"kind":"attempt","task_id":"t","passed":true}"#;
    let event: LearningEvent = serde_json::from_str(old).unwrap();
    assert!(event.voids.is_empty());
    assert!(!serde_json::to_string(&event).unwrap().contains("voids"));
    // The issue summary says the lesson was reset and counts nothing earlier.
    let summary = summary(&k, "수업", &[attempt(&k, "v1", "r", &stp(1), true, 1), reset_at(&k, 5, &[])]);
    assert!(summary.contains("진도 초기화") && !summary.contains("통과"));
}

#[test]
fn reset_survives_reopening_the_store_and_a_remote_roundtrip_of_older_history() {
    let root = tempfile::tempdir().unwrap();
    let path = root.path().join("progress.sqlite3");
    let user = GithubUser { id: 7, login: "learner".into() };
    let k = key(7, "lesson");
    let neighbour = key(7, "neighbour");
    let store = ProgressStore::new(&path);
    let required = vec![stp(1), stp(2)];
    let first = attempt(&k, "v1", "r", &stp(1), true, 10);
    let second = attempt(&k, "v1", "r", &stp(2), true, 11);
    store.record(REPO, &user, "Lesson", &first, &required).unwrap();
    let before = store.record(REPO, &user, "Lesson", &second, &required).unwrap();
    store.record(REPO, &user, "Neighbour", &attempt(&neighbour, "v1", "r", &stp(1), true, 10), &required).unwrap();
    assert!(status(&before, "v1", &required).current);
    let reset = reset_event(k.clone(), "v1", StudyMode::Full, "r", &before);
    store.record(REPO, &user, "Lesson", &reset, &[]).unwrap();
    // Reopen (app restart) and read back.
    drop(store);
    let reopened = ProgressStore::new(&path);
    let events = reopened.events(REPO, &k).unwrap();
    assert_eq!(learning_progress(&events, "v1", &required).solved, 0);
    assert!(!status(&events, "v1", &required).completed);
    // GitHub still returns the pre-reset comments (the reset is not uploaded yet, or the remote
    // list is older). Caching them back cannot restore the progress.
    reopened.cache(REPO, &before).unwrap();
    let events = reopened.events(REPO, &k).unwrap();
    assert_eq!(learning_progress(&events, "v1", &required).solved, 0);
    // The reset waits for upload like any other event, with the attempts it voids.
    assert!(reopened.pending_count(7).unwrap() >= 1);
    // The neighbouring lesson is untouched.
    let course = reopened.course_events(REPO, 7, "course").unwrap();
    assert_eq!(learned_tasks(&course["neighbour"], "v1").len(), 1);
    assert_eq!(learned_tasks(&course["lesson"], "v1").len(), 0);
    // Working again after the reset counts.
    let again = reopened.record(REPO, &user, "Lesson", &attempt(&k, "v1", "r", &stp(1), true, issue_now() + 1), &required).unwrap();
    assert_eq!(learning_progress(&again, "v1", &required).solved, 1);
}
fn issue_now() -> u64 { now() }
