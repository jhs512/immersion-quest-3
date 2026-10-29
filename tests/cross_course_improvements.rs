//! The other two courses use the same truthful gauge, challenge clear and durable reset contract.
use molip_quest::{bundled_courses, challenges, github_player::GithubUser, issue_progress::*,
                 progress_sync::ProgressStore, repository_course::{CourseManifest, Lesson}};

#[test]
fn every_cross_course_lesson_has_a_graded_final_category_and_entry_brief() {
    for (repo, count) in [("jhs512/mq3-course-redesigned-aice-associate", 24),
                          ("jhs512/mq3-course-redesigned-engineer-practical", 30)] {
        let raw = bundled_courses::course_source(repo).unwrap();
        let course = CourseManifest::parse(raw).unwrap();
        let data: serde_json::Value = serde_json::from_str(raw).unwrap();
        assert_eq!(course.lessons.len(), count);
        let categories: std::collections::BTreeSet<_> = data["categories"].as_array().unwrap().iter()
            .map(|c| c["id"].as_str().unwrap()).collect();
        let mut ids = std::collections::BTreeSet::new();
        for reference in &course.lessons {
            let lesson = Lesson::parse(bundled_courses::lesson_source(reference).unwrap(), reference).unwrap();
            let (position, task) = challenges::designated(reference, &lesson).expect(&reference.title);
            assert_eq!(position + 1, lesson.tasks.len());
            assert!(task.required && challenges::is_graded(task));
            assert!(ids.insert(task.id.clone()));
            if let Some(molip_quest::task_interaction::Interaction::FillFields { fields }) = &task.interaction {
                let original: std::collections::BTreeMap<String, String> = serde_json::from_str(&task.solution).unwrap();
                for field in fields {
                    for alias in &field.accepted {
                        let mut answers = original.clone();
                        answers.insert(field.id.clone(), alias.clone());
                        assert!(task.interaction.as_ref().unwrap().check(&serde_json::to_string(&answers).unwrap()).unwrap().passed);
                    }
                    let mut wrong = original.clone();
                    wrong.insert(field.id.clone(), "__오답__".into());
                    assert!(!task.interaction.as_ref().unwrap().check(&serde_json::to_string(&wrong).unwrap()).unwrap().passed);
                }
            }
            let row = data["lessons"].as_array().unwrap().iter().find(|r| r["id"] == reference.id).unwrap();
            assert!(categories.contains(row["category"].as_str().unwrap()));
            let brief = &data["lesson_previews"][&reference.id];
            for field in ["learn", "scenario", "constraints"] {
                assert!(!brief[field].as_array().unwrap().is_empty(), "{} {field}", reference.title);
            }
            assert_eq!(brief["challenge"].as_str().unwrap(), task.title);
            assert!(!brief["question"].as_str().unwrap().is_empty());
        }
    }
}

#[test]
fn challenge_alone_clear_survives_restart_then_lesson_reset_on_both_courses() {
    for repo in ["jhs512/mq3-course-redesigned-aice-associate", "jhs512/mq3-course-redesigned-engineer-practical"] {
        let course = CourseManifest::parse(bundled_courses::course_source(repo).unwrap()).unwrap();
        let directory = tempfile::tempdir().unwrap();
        let path = directory.path().join("progress.sqlite3");
        let user = GithubUser { id: 77, login: "cross-course-learner".into() };
        let key = |id: &str| ProgressKey { user_id: user.id, course_id: course.id.clone(), lesson_id: id.into() };
        let store = ProgressStore::new(&path);
        for reference in &course.lessons {
            let lesson = Lesson::parse(bundled_courses::lesson_source(reference).unwrap(), reference).unwrap();
            let required = lesson.required_tasks();
            let mut event = LearningEvent::new(key(&reference.id), &reference.revision, StudyMode::Full, "direct", EventKind::Attempt);
            event.task_id = Some(reference.challenge_task.clone());
            event.passed = true;
            event.at = 10;
            store.record(repo, &user, &reference.title, &event, &required).unwrap();
        }
        drop(store);
        let reopened = ProgressStore::new(&path);
        for reference in &course.lessons {
            let lesson = Lesson::parse(bundled_courses::lesson_source(reference).unwrap(), reference).unwrap();
            let required = lesson.required_tasks();
            let before = reopened.events(repo, &key(&reference.id)).unwrap();
            let clear = lesson_clear(&before, &reference.revision, &required, &reference.challenge_task);
            assert!(clear.challenge && !clear.full && clear.cleared(), "{}", reference.title);
            let gauge = learning_progress(&before, &reference.revision, &required);
            assert_eq!((gauge.solved, gauge.total), (1, required.len()));
            assert!(gauge.percent < 100);
            let reset = reset_event(key(&reference.id), &reference.revision, StudyMode::Full, "direct", &before);
            reopened.record(repo, &user, &reference.title, &reset, &[]).unwrap();
            // Old remote history must not resurrect a locally reset challenge clear.
            reopened.cache(repo, &before).unwrap();
            let after = reopened.events(repo, &key(&reference.id)).unwrap();
            assert!(!lesson_clear(&after, &reference.revision, &required, &reference.challenge_task).cleared());
            assert_eq!(learning_progress(&after, &reference.revision, &required).solved, 0);
        }
    }
}
