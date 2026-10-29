//! 내 전체 학습 진도 초기화 on an isolated store (never the learner's real data directory).
use molip_quest::{
    bundled_courses,
    github_player::GithubUser,
    issue_progress::*,
    progress_reset::{self, CourseHistory},
    progress_sync::ProgressStore,
    repository_course::{CourseManifest, LessonRef},
};
use std::collections::HashMap;

const ENGINEER: &str = "jhs512/mq3-course-redesigned-engineer-practical";
const AICE: &str = "jhs512/mq3-course-redesigned-aice-associate";

fn course(repository: &str) -> CourseManifest { CourseManifest::parse(bundled_courses::course_source(repository).unwrap()).unwrap() }

fn pass(user: u64, course: &CourseManifest, lesson: &LessonRef, task: &str, at: u64) -> LearningEvent {
    let key = ProgressKey { user_id: user, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
    let mut event = LearningEvent::new(key, &lesson.revision, StudyMode::Full, "round-1", EventKind::Attempt);
    event.task_id = Some(task.into());
    event.passed = true;
    event.at = at;
    event
}

fn histories(store: &ProgressStore, user: u64, courses: &[CourseManifest]) -> Vec<CourseHistory> {
    courses.iter().map(|c| CourseHistory { manifest: c.clone(), events: store.course_events(&c.repository, user, &c.id).unwrap() }).collect()
}

fn counted(store: &ProgressStore, user: u64, course: &CourseManifest, lesson: &LessonRef) -> usize {
    let key = ProgressKey { user_id: user, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
    effective(&store.events(&course.repository, &key).unwrap()).len()
}

#[test]
fn resets_every_course_of_this_account_durably_and_leaves_others_and_the_raw_history() {
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("progress.sqlite3");
    let (engineer, aice) = (course(ENGINEER), course(AICE));
    let (me, other) = (GithubUser { id: 7, login: "learner".into() }, GithubUser { id: 8, login: "friend".into() });
    let (e1, e2, e3, a1) = (&engineer.lessons[0], &engineer.lessons[1], &engineer.lessons[2], &aice.lessons[0]);
    let mut recorded = Vec::new();
    {
        let store = ProgressStore::new(&path);
        for (course, lesson, user, at) in [(&engineer, e1, &me, 10), (&engineer, e2, &me, 11), (&aice, a1, &me, 12), (&engineer, e1, &other, 13)] {
            let event = pass(user.id, course, lesson, "stp_x", at);
            store.record(&course.repository, user, &lesson.title, &event, &[]).unwrap();
            recorded.push(event);
        }
    }
    let store = ProgressStore::new(&path);
    let courses = [engineer.clone(), aice.clone()];
    let before = histories(&store, me.id, &courses);
    let plan = progress_reset::plan(me.id, &before);
    // Both courses, only the three lessons this account touched; the untouched e3 is not planned.
    assert_eq!((plan.course_count(), plan.lesson_count()), (2, 3));
    assert_eq!(plan.courses[0].lessons_total, engineer.lessons.len());
    assert!(!plan.courses.iter().flat_map(|c| &c.lessons).any(|(id, ..)| *id == e3.id));

    // 취소: planning writes nothing.
    assert_eq!(counted(&store, me.id, &engineer, e1), 1);
    let pending_before = store.pending_count(me.id).unwrap();

    let saved = progress_reset::apply(me.id, &plan, &before, |repository, title, event| {
        store.record(repository, &me, title, event, &[]).map(|_| ())
    }).unwrap();
    assert_eq!(saved, 3);
    // The resets wait for upload like any other event.
    assert_eq!(store.pending_count(me.id).unwrap(), pending_before + 3);
    drop(store);

    // After a restart, and after the pre-reset history comes back from sync, nothing of mine counts.
    let reopened = ProgressStore::new(&path);
    reopened.cache(ENGINEER, &recorded[..2]).unwrap();
    reopened.cache(AICE, &recorded[2..3]).unwrap();
    for (course, lesson) in [(&engineer, e1), (&engineer, e2), (&aice, a1)] {
        assert_eq!(counted(&reopened, me.id, course, lesson), 0, "{}", lesson.title);
        let key = ProgressKey { user_id: me.id, course_id: course.id.clone(), lesson_id: lesson.id.clone() };
        let raw = reopened.events(&course.repository, &key).unwrap();
        // The original pass is still stored next to the appended reset.
        assert!(raw.iter().any(|e| e.kind == EventKind::Attempt) && raw.iter().any(|e| e.kind == EventKind::Reset));
        assert_eq!(learning_progress(&raw, &lesson.revision, &["stp_x".to_string()]).solved, 0);
    }
    // Another account in the same course and lesson keeps its progress.
    assert_eq!(counted(&reopened, other.id, &engineer, e1), 1);
    // Learning after the reset counts again, and a second account-wide reset plans only that lesson.
    let again = pass(me.id, &engineer, e3, "stp_y", now() + 5);
    reopened.record(ENGINEER, &me, &e3.title, &again, &[]).unwrap();
    assert_eq!(counted(&reopened, me.id, &engineer, e3), 1);
    let next = progress_reset::plan(me.id, &histories(&reopened, me.id, &courses));
    assert_eq!(next.lesson_count(), 1);
    assert_eq!(next.courses[0].lessons[0].0, e3.id);
}

#[test]
fn a_lesson_reset_still_leaves_the_other_lessons_and_accounts_alone() {
    let directory = tempfile::tempdir().unwrap();
    let store = ProgressStore::new(&directory.path().join("progress.sqlite3"));
    let engineer = course(ENGINEER);
    let (me, other) = (GithubUser { id: 7, login: "learner".into() }, GithubUser { id: 8, login: "friend".into() });
    let (first, second) = (&engineer.lessons[0], &engineer.lessons[1]);
    for (lesson, user) in [(first, &me), (second, &me), (first, &other)] {
        store.record(ENGINEER, user, &lesson.title, &pass(user.id, &engineer, lesson, "stp_x", 10), &[]).unwrap();
    }
    let key = ProgressKey { user_id: me.id, course_id: engineer.id.clone(), lesson_id: first.id.clone() };
    let known = store.events(ENGINEER, &key).unwrap();
    store.record(ENGINEER, &me, &first.title, &reset_event(key, &first.revision, StudyMode::Full, "round-1", &known), &[]).unwrap();
    assert_eq!(counted(&store, me.id, &engineer, first), 0);
    assert_eq!(counted(&store, me.id, &engineer, second), 1);
    assert_eq!(counted(&store, other.id, &engineer, first), 1);
    let _: HashMap<String, Vec<LearningEvent>> = store.course_events(ENGINEER, me.id, &engineer.id).unwrap();
}
