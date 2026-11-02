use molip_quest::repository_course::{CodeFlowAvailability, Task};
use serde_json::json;

fn task(language:&str)->Task {
    serde_json::from_value(json!({
        "id":"code-flow-policy", "title":"코드 흐름", "goal":"실행을 관찰해요.",
        "language":language, "starter_code":"print(1)", "solution":"print(1)"
    })).unwrap()
}

#[test]
fn an_omitted_setting_offers_supported_code_flow() {
    for language in ["java","python","javascript"] {
        let task=task(language);
        assert!(task.code_flow);
        assert_eq!(task.code_flow_availability(),CodeFlowAvailability::Ready);
    }
}

#[test]
fn explicit_opt_out_survives_serialization() {
    let mut task=task("java");
    task.code_flow=false;
    let saved=serde_json::to_value(&task).unwrap();
    assert_eq!(saved["code_flow"],false);
    let restored:Task=serde_json::from_value(saved).unwrap();
    assert_eq!(restored.code_flow_availability(),CodeFlowAvailability::Hidden);
}

#[test]
fn unsupported_execution_remains_visible_with_a_reason() {
    for language in ["web","sql","java_project","junit","java_libraries","docker"] {
        let availability=task(language).code_flow_availability();
        let CodeFlowAvailability::Unsupported(reason)=availability else {panic!("{language}: {availability:?}")};
        assert!(!reason.is_empty());
    }
    assert_eq!(task("c").code_flow_availability()==CodeFlowAvailability::Ready,cfg!(any(windows,target_os="macos")));
    for language in ["cpp", "rust"] {
        assert_eq!(task(language).code_flow_availability()==CodeFlowAvailability::Ready,cfg!(any(windows,target_os="macos")));
        assert_eq!(task(language).language.editor(),language);
    }
}

#[test]
fn a_question_without_executable_code_has_no_visualizer() {
    let mut task=task("python");
    task.interaction=Some(molip_quest::task_interaction::Interaction::Fill{accepted:vec!["1".into()]});
    assert_eq!(task.code_flow_availability(),CodeFlowAvailability::Hidden);
    task.example_code=Some("print(1)".into());
    assert_eq!(task.code_flow_availability(),CodeFlowAvailability::Ready);
    task.git_terminal=Some(Default::default());
    assert_eq!(task.code_flow_availability(),CodeFlowAvailability::Hidden);
}

#[test]
fn native_lesson_drivers_receive_the_effective_availability() {
    let mut checked=0;
    for lesson in molip_quest::lesson_registry::LESSONS.iter().filter(|lesson|lesson.driver!="native") {
        let script=molip_quest::lesson_registry::self_test_script(lesson.key).unwrap();
        assert!(script.contains("\"code_flow_state\""),"{}",lesson.key);
        checked+=1;
    }
    assert!(checked>0);
}
