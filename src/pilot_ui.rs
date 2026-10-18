//! Debug controls around the real RepositoryPlayer, backed by an isolated transport.
use dioxus::prelude::*;
use molip_quest::{pilot_source, repository_course::{CourseManifest, Lesson}};

#[component]
pub fn PilotPlayer() -> Element {
    let mut generation = use_signal(|| 0u64);
    let mut notice = use_signal(String::new);
    use_future(|| async move {
        if !pilot_source::enabled() || std::env::var_os("MOLIP_PILOT_SELF_TEST").is_none() { return; }
        let mut bridge = document::eval(include_str!("../tools/player-pilot-native.js"));
        let result = match tokio::time::timeout(std::time::Duration::from_secs(150), bridge.recv::<serde_json::Value>()).await {
            Ok(Ok(result)) => result,
            _ => serde_json::json!({"passed":false,"error":"Native WebView test timed out or disconnected"}),
        };
        let written = std::fs::write("target/pilot-native-result.json", result.to_string());
        std::process::exit(if written.is_ok() && result["passed"] == true { 0 } else { 1 });
    });
    rsx! {
        aside { class: "pilot-toolbar", aria_label: "개발 검증 도구",
            span { "개발 검증 전용 · 외부 계정 기록 없음" }
            for version in ['a', 'b', 'c', 'd', 'e', 'f'] {
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
            button { onclick: move |_| {
                let result = CourseManifest::parse(include_str!("../tests/fixtures/player-pilot/a/course.json")).and_then(|course| {
                    let damaged = include_str!("../tests/fixtures/player-pilot/a/lesson.json").replace("값과 출력", "손상 후보");
                    Lesson::parse(&damaged, &course.lessons[0])
                });
                notice.set(if result.is_err() { "손상 후보를 거절했어요. 현재 수업을 유지해요." } else { "검증 실패: 손상 후보가 통과했어요." }.into());
            }, "손상 후보 검사" }
            p { role: "status", "{notice}" }
        }
        {rsx! { crate::player_ui::RepositoryPlayer { key: "pilot-{generation}" } }}
    }
}
