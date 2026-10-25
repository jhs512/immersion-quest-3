#![cfg(all(feature="desktop",debug_assertions))]
//! The eight final-problem lessons applied to java-backend on 2026-10-25, opened in the real player
//! (isolated pilot session, never a real account): lesson entry, narration replay, real grading of the
//! learner's submission, and the progress events written to the isolated progress store.
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

const APPLIED:[&str;8]=["sys-sliding-window","sys-page-table","sys-buffer-pool","sys-cache-locality",
    "sys-interpreter-env","sys-interleavings","socket-partial-frames","node-cpu-offload"];

#[test]
#[ignore="Requires an interactive desktop, JDK25, Node and the built player binary"]
fn applied_final_problem_lessons_open_grade_and_record_progress() {
    let only=std::env::var("MQ3_APPLIED_ONLY").ok();
    for key in APPLIED.iter().filter(|key|only.as_deref().is_none_or(|o|o==**key)) {
        let session=molip_quest::pilot_session::PilotSession::new().unwrap();
        let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
        native_player::configure(&session,&mut command,key);
        command.env("MOLIP_PILOT_SELF_TEST",key);
        let status=native_player::wait(&mut command.spawn().unwrap(),480,key);
        let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
        std::fs::write(format!("target/pilot-applied-{key}.json"),&raw).unwrap();
        let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
        assert!(status.success()&&result["passed"]==true,"{key}: {result}");
        let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
        let events:Vec<_>=store["comments"].as_array().unwrap().iter().flat_map(|comment|molip_quest::issue_progress::parse_events(comment["body"].as_str().unwrap())).collect();
        use molip_quest::issue_progress::EventKind;
        let passed:std::collections::HashSet<_>=events.iter().filter(|event|event.kind==EventKind::Attempt&&event.passed).filter_map(|event|event.task_id.as_ref()).collect();
        assert_eq!(passed.len(),1,"{key}: the one final problem passed");
        assert_eq!(events.iter().filter(|event|event.kind==EventKind::Completed).count(),1,"{key}: lesson completed once");
        assert!(!events.iter().any(|event|event.kind==EventKind::ExampleRun),"{key}: teacher runs are not student runs");
        eprintln!("{key}: opened, narration replayed, submission graded, progress recorded ({} checks)",result["checked"].as_array().map_or(0,|c|c.len()));
    }
}
