#![cfg(all(feature="desktop",debug_assertions,target_os="macos"))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
use molip_quest::{pilot_session::PilotSession,progress_sync::ProgressStore,issue_progress::{LearningEvent,ProgressKey,StudyMode,EventKind},repository_course::{CourseManifest,Lesson}};
#[test]
#[ignore="Requires a real Mac desktop; uses only isolated progress and local Git"]
fn old_progress_can_resume_step_three_after_content_update_and_reopen_the_committed_workspace(){
    let session=PilotSession::new().unwrap();
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/k/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/git-first.json"),&manifest.lessons[0]).unwrap();
    let events=lesson.tasks.iter().take(2).map(|task|{
        let mut event=LearningEvent::new(ProgressKey{user_id:987654321,course_id:manifest.id.clone(),lesson_id:lesson.id.clone()},"git-first-2",StudyMode::Full,"prior-content",EventKind::Attempt);
        event.task_id=Some(task.id.clone());event.passed=true;event
    }).collect::<Vec<_>>();
    ProgressStore::new(&session.directory().join("progress-events.sqlite3")).cache(&manifest.repository,&events).unwrap();
    assert!(!session.directory().join("git-practices").exists());
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"student-report-git");command.env("MOLIP_PILOT_SELF_TEST","student-report-git");
    let status=native_player::wait(&mut command.spawn().unwrap(),100,"student-report-git");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();std::fs::write("target/pilot-student-report-git-result.json",&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();assert!(status.success()&&result["passed"]==true,"{result}");
    // Reopen after the app process exits, using the identical production scope.
    let exercise=lesson.tasks[2].git_terminal.clone().unwrap();
    let key=ProgressKey{user_id:987654321,course_id:manifest.id,lesson_id:lesson.id};
    let base=molip_quest::drafts::repository_scope(&key,StudyMode::Full,&exercise.workspace_group);
    let scope=exercise.workspace_scope(&base);
    let store=molip_quest::git_practice::GitPracticeStore::new(&session.directory().join("git-practices")).unwrap();
    let practice=store.open(&scope,exercise).unwrap();
    assert_eq!(practice.git(&["log","-1","--format=%s"]).unwrap().stdout.trim(),"직접 커밋");
    assert_eq!(std::fs::read_to_string(practice.work().join("memo.txt")).unwrap(),"첫 메모\n");
    assert_eq!(std::fs::read_to_string(practice.work().join("keep.txt")).unwrap(),"learner-preserved\n");
}
