use molip_quest::{
    github_player::Github,
    issue_progress::{EventKind, LearningEvent, ProgressKey, StudyMode},
    pilot_session::PilotSession,
    pilot_source,
};

#[test]
fn isolated_installed_player_can_reopen_its_draft_and_github_progress_in_a_new_process() {
    let session = PilotSession::new().unwrap();
    let executable = std::env::current_exe().unwrap();
    for phase in ["seed", "reopen"] {
        let mut child = std::process::Command::new(&executable);
        child
            .args(["--exact", "restart_worker", "--nocapture"])
            .env("MQ3_RESTART_PHASE", phase);
        session.configure(&mut child);
        let result = child.output().unwrap();
        assert!(
            result.status.success(),
            "{phase}: {} {}",
            String::from_utf8_lossy(&result.stdout),
            String::from_utf8_lossy(&result.stderr)
        );
    }
    assert!(session.directory().join("drafts.sqlite3").is_file());
}
#[test]
fn restart_worker() {
    let Ok(phase) = std::env::var("MQ3_RESTART_PHASE") else {
        return;
    };
    if phase == "reject" {
        assert!(pilot_source::data_dir().is_err());
        return;
    }
    let github = Github::new();
    let user = github.user().unwrap();
    let course = github.installed_course(pilot_source::REPOSITORY).unwrap();
    let lesson = github
        .installed_lesson(&course, &course.lessons[0])
        .unwrap();
    let key = ProgressKey {
        user_id: user.id,
        course_id: course.id.clone(),
        lesson_id: lesson.id.clone(),
    };
    let scope = molip_quest::drafts::repository_scope(&key, StudyMode::Full, &lesson.tasks[0].id);
    if phase == "seed" {
        molip_quest::drafts::save(&scope, "console.log(99);", &Default::default()).unwrap();
        let mut event = LearningEvent::new(
            key,
            &lesson.revision,
            StudyMode::Full,
            "first-process",
            EventKind::Attempt,
        );
        event.task_id = Some(lesson.tasks[0].id.clone());
        event.passed = true;
        github
            .append(&course.repository, &user, &lesson.title, &event)
            .unwrap();
    } else {
        assert_eq!(
            molip_quest::drafts::load(&scope).unwrap().unwrap().code,
            "console.log(99);"
        );
        let issue = github
            .find_issue(&course.repository, &user, &key)
            .unwrap()
            .unwrap();
        let events = github.events(&course.repository, &issue, &key).unwrap();
        assert_eq!(
            events
                .iter()
                .filter(|e| e.kind == EventKind::Attempt && e.passed)
                .count(),
            1
        );
        assert_eq!(events[0].round, "first-process");
        assert!(github.course("jhs512/immersion-quest-3").is_err());
    }
}

#[test]
fn shared_pilot_data_rejects_wrong_owner_and_unowned_folders() {
    let session = PilotSession::new().unwrap();
    let executable = std::env::current_exe().unwrap();
    let outside = tempfile::tempdir().unwrap();
    std::fs::write(outside.path().join("keep.txt"), "untouched").unwrap();
    for unowned in [false, true] {
        let mut child = std::process::Command::new(&executable);
        child
            .args(["--exact", "restart_worker", "--nocapture"])
            .env("MQ3_RESTART_PHASE", "reject");
        session.configure(&mut child);
        if unowned {
            child.env("MOLIP_PILOT_DIRECTORY", outside.path());
        } else {
            child.env("MOLIP_PILOT_OWNER", "00000000000000000000000000000000");
        }
        let result = child.output().unwrap();
        assert!(
            result.status.success(),
            "{}",
            String::from_utf8_lossy(&result.stdout)
        );
    }
    assert_eq!(
        std::fs::read_to_string(outside.path().join("keep.txt")).unwrap(),
        "untouched"
    );
    assert_eq!(std::fs::read_dir(outside.path()).unwrap().count(), 1);
}
