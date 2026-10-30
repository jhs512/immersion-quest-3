#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

fn verify(mode:&str,count:usize) {
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,mode);
    command.env("MOLIP_PILOT_SELF_TEST",mode);
    let status=native_player::wait(&mut command.spawn().unwrap(),if mode=="aice-plots"{1260}else{480},mode);
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write(format!("target/pilot-{mode}-result.json"),&raw).unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    let edited_examples=if matches!(mode,"java-regex"|"java-rq"|"java-calculator") {2}else{3};
    // Each 코드 흐름 보기 step adds one checked item (trace, stepping, output, close).
    let lesson:serde_json::Value=serde_json::from_str(molip_quest::lesson_registry::find(mode).unwrap().lesson).unwrap();
    let code_flow=lesson["tasks"].as_array().unwrap().iter().filter(|task|task["code_flow"]==true).count();
    // A step whose narration itself opens 코드 흐름 보기 adds one more (traced lines, closed, learner code restored).
    let narrated_flow=lesson["tasks"].as_array().unwrap().iter().filter(|task|task["narration"].as_array().into_iter().flatten().any(|action|action["action"]=="code_flow")).count();
    assert_eq!(result["checked"].as_array().unwrap().len(),count+edited_examples+code_flow+narrated_flow,"{result}");
    let store:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<_>=store["comments"].as_array().unwrap().iter().flat_map(|comment|molip_quest::issue_progress::parse_events(comment["body"].as_str().unwrap())).collect();
    use molip_quest::issue_progress::EventKind;
    let passed:std::collections::HashSet<_>=events.iter().filter(|event|event.kind==EventKind::Attempt&&event.passed).filter_map(|event|event.task_id.as_ref()).collect();
    assert_eq!(passed.len(),count);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::Completed).count(),1);
    assert_eq!(events.iter().filter(|event|event.kind==EventKind::ExampleRun).count(),if matches!(mode,"aice-plots"|"java-react"|"java-tailwind") {1}else{0});
}

#[test]
#[ignore="Requires an interactive desktop, pandas and the built player"]
fn pandas_selection_and_summaries_restore_student_state() {verify("aice-selection",11)}

#[test]
#[ignore="Requires an interactive desktop, JDK25 and the built player"]
fn java_array_loops_restore_student_state() {verify("java-arrays",8)}

#[test]
#[ignore="Requires an interactive desktop, a C compiler and the built player"]
fn c_array_loops_and_strings_restore_student_state() {verify("engineer-c-arrays",10)}

#[test]
#[ignore="Requires an interactive desktop, pandas and the built player"]
fn pandas_quality_cases_restore_student_state() {verify("aice-quality",11)}

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
fn aice_plots_restore_student_state() {verify("aice-plots",11)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_references_restore_student_state() {verify("java-references",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_c_double_pointers_restore_student_state() {verify("engineer-c-double-pointers",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_c_structures_restore_student_state() {verify("engineer-c-structures",19)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_static_restore_student_state() {verify("java-static",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_features_restore_student_state() {verify("aice-features",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_split_restore_student_state() {verify("aice-split",11)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_leakage_restore_student_state() {verify("aice-leakage",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_scale_restore_student_state() {verify("aice-scale",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_regression_restore_student_state() {verify("aice-regression",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_regression_metrics_restore_student_state() {verify("aice-regression-metrics",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_classification_restore_student_state() {verify("aice-classification",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_classification_metrics_restore_student_state() {verify("aice-classification-metrics",11)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_models_restore_student_state() {verify("aice-models",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_tuning_restore_student_state() {verify("aice-tuning",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_tensorflow_restore_student_state() {verify("aice-tensorflow",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_neural_regression_restore_student_state() {verify("aice-neural-regression",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_neural_classification_restore_student_state() {verify("aice-neural-classification",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_training_restore_student_state() {verify("aice-training",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_join_restore_student_state() {verify("aice-join",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_boosting_restore_student_state() {verify("aice-boosting",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn aice_integration_restore_student_state() {verify("aice-integration",11)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_roles_restore_student_state() {verify("java-roles",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_collections_restore_student_state() {verify("java-collections",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_streams_restore_student_state() {verify("java-streams",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_files_restore_student_state() {verify("java-files",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_crud_restore_student_state() {verify("java-crud",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_testing_restore_student_state() {verify("java-testing",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_regex_restore_student_state() {verify("java-regex",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_rq_restore_student_state() {verify("java-rq",12)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_calculator_restore_student_state() {verify("java-calculator",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn git_remote_restore_student_state() {verify("git-remote",22)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_react_restore_student_state() {verify("java-react",6)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn java_tailwind_restore_student_state() {verify("java-tailwind",6)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_java_flow_restore_student_state() {verify("engineer-java-flow",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_java_references_restore_student_state() {verify("engineer-java-references",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_java_static_restore_student_state() {verify("engineer-java-static",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_java_polymorphism_restore_student_state() {verify("engineer-java-polymorphism",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_python_values_restore_student_state() {verify("engineer-python-values",9)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_python_calls_restore_student_state() {verify("engineer-python-calls",11)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_db_model_restore_student_state() {verify("engineer-db-model",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_sql_select_restore_student_state() {verify("engineer-sql-select",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_sql_group_restore_student_state() {verify("engineer-sql-group",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_sql_change_restore_student_state() {verify("engineer-sql-change",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_db_storage_restore_student_state() {verify("engineer-db-storage",18)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_requirements_restore_student_state() {verify("engineer-requirements",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_server_restore_student_state() {verify("engineer-server",22)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_interfaces_restore_student_state() {verify("engineer-interfaces",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_ui_restore_student_state() {verify("engineer-ui",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_test_cases_restore_student_state() {verify("engineer-test-cases",8)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_test_integration_restore_student_state() {verify("engineer-test-integration",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_design_restore_student_state() {verify("engineer-design",27)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_security_restore_student_state() {verify("engineer-security",14)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_os_restore_student_state() {verify("engineer-os",15)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_network_restore_student_state() {verify("engineer-network",15)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_build_restore_student_state() {verify("engineer-build",10)}

#[test]
#[ignore="Requires an interactive desktop and the built player"]
fn engineer_mixed_restore_student_state() {verify("engineer-mixed",15)}
