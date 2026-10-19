#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

fn verify(mode:&str,count:usize) {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,mode);
    command.env("MOLIP_PILOT_SELF_TEST",mode);
    let status=native_player::wait(&mut command.spawn().unwrap(),480,mode);
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write(format!("target/pilot-{mode}-result.json"),&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    assert_eq!(result["checked"].as_array().unwrap().len(),count+3);
    let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=store["comments"].as_array().unwrap().iter().filter_map(|comment|molip_quest::issue_progress::parse_event(comment["body"].as_str().unwrap())).collect();
    use molip_quest::issue_progress::EventKind;
    let passed:std::collections::HashSet<_>=events.iter().filter(|event|event.kind==EventKind::Attempt&&event.passed).filter_map(|event|event.task_id.as_ref()).collect();
    assert_eq!(passed.len(),count);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::Completed).count(),1);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::ExampleRun).count(),if mode=="aice-plots" {1}else{0});
}

#[test]
#[ignore="Requires an interactive desktop, pandas and the built player"]
fn pandas_selection_and_summaries_restore_student_state() {verify("aice-selection",10)}

#[test]
#[ignore="Requires an interactive desktop, JDK25 and the built player"]
fn java_array_loops_restore_student_state() {verify("java-arrays",8)}

#[test]
#[ignore="Requires an interactive desktop, a C compiler and the built player"]
fn c_array_loops_and_strings_restore_student_state() {verify("engineer-c-arrays",10)}

#[test]
#[ignore="Requires an interactive desktop, pandas and the built player"]
fn pandas_quality_cases_restore_student_state() {verify("aice-quality",10)}

#[test]
#[ignore="Requires an interactive desktop, a C compiler and the built player"]
fn c_functions_and_recursion_restore_student_state() {verify("engineer-c-functions",10)}

#[test]
#[ignore="Requires an interactive desktop, JDK25 and the built player"]
fn java_method_calls_and_returns_restore_student_state() {verify("java-methods",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_c_pointers_restore_student_state() {verify("engineer-c-pointers",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_plots_restore_student_state() {verify("aice-plots",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_references_restore_student_state() {verify("java-references",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_c_double_pointers_restore_student_state() {verify("engineer-c-double-pointers",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_c_structures_restore_student_state() {verify("engineer-c-structures",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_static_restore_student_state() {verify("java-static",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_features_restore_student_state() {verify("aice-features",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_split_restore_student_state() {verify("aice-split",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_leakage_restore_student_state() {verify("aice-leakage",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_scale_restore_student_state() {verify("aice-scale",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_regression_restore_student_state() {verify("aice-regression",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_regression_metrics_restore_student_state() {verify("aice-regression-metrics",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_classification_restore_student_state() {verify("aice-classification",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_classification_metrics_restore_student_state() {verify("aice-classification-metrics",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_models_restore_student_state() {verify("aice-models",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_tuning_restore_student_state() {verify("aice-tuning",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_tensorflow_restore_student_state() {verify("aice-tensorflow",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_neural_regression_restore_student_state() {verify("aice-neural-regression",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_neural_classification_restore_student_state() {verify("aice-neural-classification",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_training_restore_student_state() {verify("aice-training",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_join_restore_student_state() {verify("aice-join",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_boosting_restore_student_state() {verify("aice-boosting",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_integration_restore_student_state() {verify("aice-integration",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_roles_restore_student_state() {verify("java-roles",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_collections_restore_student_state() {verify("java-collections",10)}
