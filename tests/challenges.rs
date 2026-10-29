//! 도전 과제 references each lesson's final graded problem and keeps future drafts away from learners.
use molip_quest::{bundled_courses, challenges::{self, ExecutionState, FutureChallengeFile, ReviewState},
    lesson_runner, repository_course::{CourseManifest, Lesson, Task, COURSE_REPOSITORY}};

fn backend() -> (CourseManifest, Vec<Lesson>) {
    let course = CourseManifest::parse(bundled_courses::course_source(COURSE_REPOSITORY).unwrap()).unwrap();
    let lessons = course.lessons.iter().map(|reference| {
        Lesson::parse(bundled_courses::lesson_source(reference).unwrap_or_else(|| panic!("{} bundled", reference.revision)), reference).unwrap()
    }).collect();
    (course, lessons)
}
fn fixture(course: &CourseManifest) -> FutureChallengeFile {
    FutureChallengeFile::parse(include_str!("fixtures/challenges/future.json"), course).unwrap()
}

#[test]
fn every_backend_lesson_offers_its_last_graded_problem_by_reference() {
    let (course, lessons) = backend();
    assert_eq!(course.lessons.len(), 43);
    for (index, (reference, lesson)) in course.lessons.iter().zip(&lessons).enumerate() {
        let challenge = challenges::lesson_challenge(index, reference, lesson).unwrap_or_else(|| panic!("{} has no graded problem", reference.title));
        let position = lesson.tasks.iter().position(|task| task.id == challenge.task_id).unwrap();
        assert!(challenges::is_graded(&lesson.tasks[position]), "{}", reference.title);
        assert!(lesson.tasks[position + 1..].iter().all(|task| !challenges::is_graded(task)), "{}: a later graded task exists", reference.title);
        // A reference, pinned to the revision the course uses; nothing is copied or renamed.
        assert_eq!((challenge.lesson_id.as_str(), challenge.revision.as_str()), (reference.id.as_str(), reference.revision.as_str()));
        assert_eq!(challenge.task_title, lesson.tasks[position].title);
        assert_eq!(challenge.position, (position + 1, lesson.tasks.len()));
        assert!(!challenge.prompt.trim().is_empty(), "{}", reference.title);
    }
    // Bash, Vim, Git, GitHub, React and Tailwind basics are included, each with its own answer form.
    let kinds: Vec<_> = course.lessons.iter().zip(&lessons).enumerate()
        .map(|(i, (r, l))| (r.repository.rsplit('-').next().unwrap().to_owned(), challenges::lesson_challenge(i, r, l).unwrap().kind)).collect();
    for key in ["basics", "pr", "tailwind", "react"] { assert!(kinds.iter().any(|(k, _)| k == key), "{key}: {kinds:?}"); }
    assert!(kinds.iter().any(|(_, kind)| *kind == "터미널 실습") && kinds.iter().any(|(_, kind)| *kind == "화면 고치기") && kinds.iter().any(|(_, kind)| *kind == "코드 작성"), "{kinds:?}");
}

#[test]
fn an_ungraded_closing_step_is_skipped_and_a_stale_revision_is_not_referenced() {
    let (course, lessons) = backend();
    let mut lesson = lessons[1].clone();
    let last = lesson.tasks.last().unwrap().id.clone();
    let mut reading: Task = lesson.tasks.last().unwrap().clone();
    reading.id = "stp_20000000-0000-4000-8000-000000000001".into();
    reading.interaction = None; reading.tests.clear(); reading.variations.clear(); reading.checker = None; reading.expected_files.clear();
    assert!(!challenges::is_graded(&reading), "explanation-only Java step");
    lesson.tasks.push(reading);
    let challenge = challenges::lesson_challenge(1, &course.lessons[1], &lesson).unwrap();
    assert_eq!(challenge.task_id, last);
    assert_eq!(challenge.position.1, lesson.tasks.len());
    let mut stale = course.lessons[1].clone();
    stale.revision.push_str("-old");
    assert!(challenges::lesson_challenge(1, &stale, &lessons[1]).is_none());
}

#[test]
fn future_problems_keep_draft_approved_and_execution_states_apart() {
    let (course, _) = backend();
    let file = fixture(&course);
    assert_eq!(file.challenges.len(), 3);
    let learner: Vec<_> = file.visible(false).iter().map(|c| c.id.clone()).collect();
    assert_eq!(learner, ["chl_10000000-0000-4000-8000-000000000002"], "learners see approved problems only");
    assert_eq!(file.visible(true).len(), 3, "a course editor sees drafts for review");
    assert!(file.challenges.iter().filter(|c| c.review.state == ReviewState::Draft).all(|c| c.review.reviewed_by.is_empty()));
    let pending = &file.challenges[2];
    assert_eq!(pending.execution.state, ExecutionState::PendingEnvironment);
    assert!(!pending.runnable() && file.challenges[0].runnable());
    for challenge in &file.challenges {
        let lesson = challenge.lesson();
        lesson.validate().unwrap();
        assert_eq!((lesson.id.as_str(), lesson.tasks.len(), lesson.chapters.len()), (challenge.id.as_str(), 1, 0));
        assert!(lesson.revision.starts_with("future-") && lesson.tasks[0].required);
        assert!(!course.lessons.iter().any(|l| l.id == lesson.id), "never posing as a published lesson");
    }
    // A changed task gets a new revision, so old local drafts are not reused for it.
    let mut changed = file.challenges[0].clone();
    changed.task.solution.push('\n');
    assert_ne!(changed.lesson().revision, file.challenges[0].lesson().revision);
}

#[test]
fn malformed_or_overclaiming_future_files_are_rejected() {
    let (course, _) = backend();
    let base: serde_json::Value = serde_json::from_str(include_str!("fixtures/challenges/future.json")).unwrap();
    let reject = |edit: &dyn Fn(&mut serde_json::Value), why: &str| {
        let mut value = base.clone(); edit(&mut value);
        assert!(FutureChallengeFile::parse(&value.to_string(), &course).is_err(), "{why}");
    };
    reject(&|v| v["course_id"] = "crs_00000000-0000-4000-8000-000000000000".into(), "another course");
    reject(&|v| v["challenges"][1]["review"] = serde_json::json!({"state":"approved"}), "approval without a reviewer record");
    reject(&|v| v["challenges"][0]["planned_lesson"]["key"] = "java-values".into(), "a lesson that is already published");
    reject(&|v| v["challenges"][1]["id"] = v["challenges"][0]["id"].clone(), "duplicate challenge id");
    reject(&|v| v["challenges"][0]["id"] = "challenge-1".into(), "not a resource code");
    reject(&|v| { v["challenges"][0]["task"]["tests"] = serde_json::json!([]); v["challenges"][0]["task"]["variations"] = serde_json::json!([]); }, "nothing to grade");
    reject(&|v| v["challenges"][2]["execution"]["note"] = "".into(), "pending environment without explanation");
    reject(&|v| v["challenges"][0]["published"] = true.into(), "unknown fields cannot smuggle state");
    reject(&|v| v["schema_version"] = 2.into(), "unknown schema");
}

#[tokio::test]
async fn a_future_problem_runs_on_the_existing_grader() {
    let (course, _) = backend();
    let file = fixture(&course);
    let task = &file.challenges[0].lesson().tasks[0];
    assert!(lesson_runner::check(task, &task.solution).await.unwrap().passed);
    assert!(!lesson_runner::check(task, &task.starter_code).await.unwrap().passed);
    // A memorized answer fails the prepared-value variation.
    let memorized = task.solution.replace("count * price", "3600");
    assert!(!lesson_runner::check(task, &memorized).await.unwrap().passed);
}

/// Every designated final challenge in the packaged backend course resolves, through the app's own
/// rule, to a required problem of the pinned revision that has a real grader; the lessons without a
/// designation fall back to the unreviewed last problem and never clear a lesson by challenge.
#[test]
fn packaged_backend_course_designates_only_real_graded_final_challenges() {
    use molip_quest::{bundled_courses, challenges, repository_course::{CourseManifest, Lesson}};
    let course = CourseManifest::parse(bundled_courses::course_source("jhs512/mq3-course-redesigned-java-backend").unwrap()).unwrap();
    let mut designated = 0;
    for (index, reference) in course.lessons.iter().enumerate() {
        let lesson = Lesson::parse(bundled_courses::lesson_source(reference).unwrap(), reference).unwrap();
        let resolved = challenges::designated(reference, &lesson);
        let card = challenges::lesson_challenge(index, reference, &lesson).unwrap();
        if reference.challenge_task.is_empty() {
            assert!(resolved.is_none() && !card.designated, "{}", reference.title);
            continue;
        }
        designated += 1;
        let (position, task) = resolved.unwrap_or_else(|| panic!("designation must resolve: {}", reference.title));
        assert!(task.required && challenges::is_graded(task), "{}", reference.title);
        assert_eq!(position + 1, lesson.tasks.len(), "the final problem: {}", reference.title);
        assert!(card.designated && card.task_id == reference.challenge_task);
    }
    assert_eq!(designated, 19);
    // A designation that is not a required graded problem of this revision is ignored.
    let mut reference = course.lessons.iter().find(|l| !l.challenge_task.is_empty()).unwrap().clone();
    let lesson = Lesson::parse(bundled_courses::lesson_source(&reference).unwrap(), &reference).unwrap();
    reference.challenge_task = "stp_3f59e7bd-70c1-4e81-9cb0-000000000099".into();
    assert!(challenges::designated(&reference, &lesson).is_none());
    let mut wrong_revision = course.lessons.iter().find(|l| !l.challenge_task.is_empty()).unwrap().clone();
    wrong_revision.revision.push_str("-other");
    assert!(challenges::designated(&wrong_revision, &lesson).is_none());
    // A malformed designation is refused with the course.
    let raw = bundled_courses::course_source("jhs512/mq3-course-redesigned-java-backend").unwrap();
    let mut value: serde_json::Value = serde_json::from_str(raw).unwrap();
    value["lessons"][0]["challenge_task"] = "last".into();
    assert!(CourseManifest::parse(&value.to_string()).is_err());
}
