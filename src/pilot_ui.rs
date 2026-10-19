//! Debug controls around the real RepositoryPlayer, backed by an isolated transport.
use dioxus::prelude::*;
use molip_quest::{pilot_source, repository_course::{CourseManifest, Lesson}};

#[component]
pub fn PilotPlayer() -> Element {
    let mut generation = use_signal(|| 0u64);
    let mut notice = use_signal(String::new);
    let mut setup_preview = use_signal(|| false);
    #[cfg(feature="desktop")]
    let window = dioxus::desktop::use_window();
    #[cfg(not(feature="desktop"))]
    let window = ();
    use_future(|| async move {
        if !pilot_source::enabled() || std::env::var_os("MOLIP_PILOT_SELF_TEST").is_none() { return; }
        let restart_phase=std::env::var("MOLIP_PILOT_SELF_TEST").ok().and_then(|mode|mode.strip_prefix("restart-").map(str::to_owned)).filter(|phase|matches!(phase.as_str(),"seed"|"reopen"));
        let script=if let Some(phase)=&restart_phase {
            format!("window.mq3RestartPhase={};{}",serde_json::to_string(phase).unwrap(),include_str!("../tools/player-pilot-restart.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-values") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-values.json")).expect("compiled Java lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Java","version":"n","revision":"java-values-1","tasks":tasks,"modifications":{"1":{"source":tasks[1]["starter_code"].as_str().unwrap().replace("println(2)","println(99)")},"4":{"correct":true},"8":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-python-start") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-python-start.json")).expect("compiled Python lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Python","version":"o","revision":"aice-python-start-1","tasks":tasks,"modifications":{"1":{"source":tasks[1]["starter_code"].as_str().unwrap().replace("print(12)","print(99)")},"2":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-python-conditions") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-python-conditions.json")).expect("compiled Python condition lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Python conditions","version":"p","revision":"aice-python-conditions-1","tasks":tasks,"modifications":{"2":{"source":tasks[2]["starter_code"].as_str().unwrap().replace("limit = 20","limit = 999")},"6":{"correct":true},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-table-csv") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-table-csv.json")).expect("compiled table lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"CSV table","version":"q","revision":"aice-table-csv-1","tasks":tasks,"modifications":{"1":{"source":tasks[1]["starter_code"].as_str().unwrap().replace("head(2)","head(1)")},"2":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-start") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-start.json")).expect("compiled C lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"C integer reading","version":"r","revision":"engineer-c-start-1","tasks":tasks,"modifications":{"1":{"correct":true},"4":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-python-api") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-python-api.json")).expect("compiled Python API lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Python API","version":"s","revision":"aice-python-api-1","tasks":tasks,"modifications":{"2":{"correct":true},"3":{"source":tasks[3]["starter_code"].as_str().unwrap().replace("minute\"","region\"")},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-conditions") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-conditions.json")).expect("compiled conditions lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Java conditions","version":"t","revision":"java-conditions-1","tasks":tasks,"modifications":{"1":{"correct":true},"5":{"correct":true},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-conditions") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-conditions.json")).expect("compiled conditions lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"C conditions","version":"u","revision":"engineer-c-conditions-1","tasks":tasks,"modifications":{"1":{"correct":true},"5":{"correct":true},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-selection") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-selection.json")).expect("compiled data lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Data selection","version":"v","revision":"aice-selection-1","tasks":tasks,"modifications":{"1":{"correct":true},"5":{"correct":true},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-arrays") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-arrays.json")).expect("compiled data lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Java arrays","version":"w","revision":"java-arrays-1","tasks":tasks,"modifications":{"1":{"correct":true},"5":{"correct":true},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-arrays") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-arrays.json")).expect("compiled C array lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"C arrays","version":"x","revision":"engineer-c-arrays-1","tasks":tasks,"modifications":{"1":{"correct":true},"5":{"correct":true},"8":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-quality") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-quality.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Data quality","version":"y","revision":"aice-quality-1","tasks":tasks,"modifications":{"3":{"source":tasks[3]["starter_code"].as_str().unwrap().replace("fillna(0)","fillna(99)")},"6":{"correct":true},"9":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-pointers") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-pointers.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"CPointers","version":"1","revision":"engineer-c-pointers-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-plots") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-plots.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICEPlots","requirePlot":true,"version":"2","revision":"aice-plots-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-references") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-references.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"JavaReferences","version":"3","revision":"java-references-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-double-pointers") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-double-pointers.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"CDoublePointers","version":"4","revision":"engineer-c-double-pointers-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-structures") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-structures.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"CStructures","version":"5","revision":"engineer-c-structures-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-static") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-static.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"JavaStatic","version":"6","revision":"java-static-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-features") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-features.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICEFeatures","version":"7","revision":"aice-features-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-split") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-split.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICESplit","version":"8","revision":"aice-split-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-leakage") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-leakage.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICELeakage","version":"9","revision":"aice-leakage-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-scale") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-scale.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICEScale","version":"가","revision":"aice-scale-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-regression") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-regression.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICERegression","version":"나","revision":"aice-regression-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-regression-metrics") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-regression-metrics.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"AICERegressionMetrics","version":"다","revision":"aice-regression-metrics-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-classification") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-classification.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"배송 분류","version":"라","revision":"aice-classification-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-classification-metrics") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-classification-metrics.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"경보 평가","version":"마","revision":"aice-classification-metrics-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-models") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-models.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"모델 비교","version":"바","revision":"aice-models-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-tuning") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-tuning.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"설정 검증","version":"사","revision":"aice-tuning-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-tensorflow") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-tensorflow.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"TensorFlow 흐름","version":"아","revision":"aice-tensorflow-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-neural-regression") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-neural-regression.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"신경망 회귀","version":"자","revision":"aice-neural-regression-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-neural-classification") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-neural-classification.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"신경망 분류","version":"차","revision":"aice-neural-classification-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-training") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-training.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"학습 개선","version":"카","revision":"aice-training-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-join") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-join.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"자료 연결","version":"타","revision":"aice-join-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-boosting") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-boosting.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"부스팅 비교","version":"파","revision":"aice-boosting-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("aice-integration") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/aice-integration.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"전체 분석 연결","version":"하","revision":"aice-integration-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-roles") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-roles.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"객체 역할","version":"거","revision":"java-roles-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-collections") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-collections.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"자료 묶음","version":"너","revision":"java-collections-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-streams") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-streams.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"자료 흐름","version":"더","revision":"java-streams-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-files") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-files.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"java-files","version":"러","revision":"java-files-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-crud") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-crud.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"java-crud","version":"머","revision":"java-crud-1","modifications":{"1":{"correct":true},"5":{"correct":true},"9":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-testing") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-testing.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"java-testing","version":"버","revision":"java-testing-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-parser") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-parser.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"java-parser","version":"서","revision":"java-parser-1","modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}},"tasks":tasks});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-methods") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/java-methods.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"Java methods","version":"0","revision":"java-methods-1","tasks":tasks,"modifications":{"1":{"correct":true},"4":{"correct":true},"7":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("engineer-c-functions") {
            let lesson:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/engineer-c-functions.json")).expect("compiled lesson");
            let tasks=&lesson["tasks"];
            let config=serde_json::json!({"label":"C functions","version":"z","revision":"engineer-c-functions-1","tasks":tasks,"modifications":{"1":{"correct":true},"4":{"correct":true},"9":{"correct":true}}});
            format!("window.mq3LessonPilot={config};{}",include_str!("../tools/player-pilot-code-lesson.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("interaction-example") {include_str!("../tools/player-pilot-example.js").to_owned()} else {format!("window.mq3FirstGitOnly={};window.mq3IncludeGitBranch={};{}",matches!(std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref(),Some("git-first"|"git-lessons")),std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()!=Some("git-first"),include_str!("../tools/player-pilot-native.js"))};
        let mut bridge = document::eval(&script);
        let result = match tokio::time::timeout(std::time::Duration::from_secs(480), bridge.recv::<serde_json::Value>()).await {
            Ok(Ok(result)) => result,
            _ => serde_json::json!({"passed":false,"error":"Native WebView test timed out or disconnected"}),
        };
        let exit_preparation = tokio::task::spawn_blocking(molip_quest::setup_terminal::prepare_practice_exit).await;
        let result = if matches!(&exit_preparation, Ok(Ok(_))) { result } else {
            serde_json::json!({"passed":false,"error":"Practice shutdown before exit failed"})
        };
        let mut result=result;
        if let Some(object)=result.as_object_mut(){object.insert("process_id".into(),serde_json::json!(std::process::id()));}
        let destination=if let Some(phase)=restart_phase {
            pilot_source::data_dir().map(|directory|directory.join(format!("restart-{phase}.json")))
        } else {Ok(std::path::PathBuf::from("target/pilot-native-result.json"))};
        let written=destination.and_then(|path|{
            use std::io::Write;
            let parent=path.parent().ok_or("검증 결과 폴더 오류")?;
            let mut temporary=tempfile::NamedTempFile::new_in(parent).map_err(|error|error.to_string())?;
            temporary.write_all(result.to_string().as_bytes()).map_err(|error|error.to_string())?;
            temporary.as_file().sync_all().map_err(|error|error.to_string())?;
            temporary.persist(path).map_err(|error|error.to_string())?;
            Ok::<_,String>(())
        });
        std::process::exit(if written.is_ok() && result["passed"] == true { 0 } else { 1 });
    });
    if setup_preview() { return rsx! {div {class:"repository-player needs-gh",
        crate::gh_setup_ui::GhSetup {message:String::new(),checking:false,onretry:move |_|setup_preview.set(false)}
    }}; }
    rsx! {
        aside { class: "pilot-toolbar", aria_label: "개발 검증 도구",
            span { "개발 검증 전용 · 외부 계정 기록 없음" }
            for version in ['a', 'b', 'c', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하', '거', '너', '더', '러', '머', '버', '서', '0'] {
                button { onclick: move |_| {
                    match pilot_source::set_version(version) {
                        Ok(()) => {
                            if let Err(error)=molip_quest::content_updates::installed_store().and_then(|store|store.remove(pilot_source::REPOSITORY)) { notice.set(error); return; }
                            generation += 1; notice.set(String::new());
                        }
                        Err(error) => notice.set(error),
                    }
                }, "버전 {version}" }
            }
            button {onclick:move |_|{let _=pilot_source::set_version('g');},"새 업데이트 공개"}
            button {onclick:move |_|{let _=pilot_source::corrupt_update();},"손상 업데이트 공개"}
            button {onclick:move |_|{let _=molip_quest::content_updates::installed_store().and_then(|store|store.remove(pilot_source::REPOSITORY));},"검증 캐시 지우기"}
            button { onclick: move |_| {
                let result = CourseManifest::parse(include_str!("../tests/fixtures/player-pilot/a/course.json")).and_then(|course| {
                    let damaged = include_str!("../tests/fixtures/player-pilot/a/lesson.json").replace("값과 출력", "손상 후보");
                    Lesson::parse(&damaged, &course.lessons[0])
                });
                notice.set(if result.is_err() { "손상 후보를 거절했어요. 현재 수업을 유지해요." } else { "검증 실패: 손상 후보가 통과했어요." }.into());
            }, "손상 후보 검사" }
            for height in [720u32,480u32] {
                button { onclick:{let window=window.clone();move |_|{
                    #[cfg(feature="desktop")] {
                        window.window.set_fullscreen(None);
                        window.window.set_inner_size(dioxus::desktop::tao::dpi::LogicalSize::new(1280.0,height as f64));
                    }
                    #[cfg(not(feature="desktop"))] let _=(window,height);
                }},"검증 높이 {height}"}
            }
            button {onclick:move |_|setup_preview.set(true),"gh 준비 검증"}
            p { role: "status", "{notice}" }
        }
        {rsx! { crate::player_ui::RepositoryPlayer { key: "pilot-{generation}" } }}
    }
}
