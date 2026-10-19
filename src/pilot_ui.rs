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
        } else if let Some(script)=std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref().and_then(molip_quest::lesson_registry::self_test_script) {
            script
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
            for version in pilot_source::versions().into_iter().filter(|version|*version!='g') {
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
