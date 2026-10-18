#![cfg_attr(all(windows, not(debug_assertions)), windows_subsystem = "windows")]

mod instructor_mode;
mod practice;
mod ui;
mod player_ui;
mod lesson_outline;
mod interaction_ui;
mod pilot_ui;
mod gh_setup_ui;
use dioxus::prelude::*;
use molip_quest::Course;
use ui::Learning;

#[cfg(feature = "desktop")]
fn main() {
    molip_quest::setup_terminal::prepare_desktop_path();
    // No menu bar on Windows and Linux: the app is driven from its own screens, slides have their
    // own fullscreen button. macOS keeps Dioxus's default menu, which is what makes ⌘C, ⌘V, ⌘X
    // and ⌘A reach the page (without an Edit menu the WebView never sees them); it lives in the
    // system menu bar, so the window itself looks the same.
    let config = dioxus::desktop::Config::new();
    #[cfg(not(target_os = "macos"))]
    let config = config.with_menu(None);
    dioxus::LaunchBuilder::new()
        .with_cfg(
            config
                // 해설 모드 asks for neural speech here: POST /tts with {"text","voice"} → MP3.
                .with_asynchronous_custom_protocol("molip", |_, request, responder| {
                    std::thread::spawn(move || responder.respond(tts_response(request)));
                })
                .with_window(
                    dioxus::desktop::WindowBuilder::new()
                        .with_title("몰입 퀘스트 3")
                        .with_window_icon(window_icon()),
                ),
        )
        .launch(App);
}

/// The Q icon for the title bar and taskbar (the taskbar shows the window's icon, not the
/// executable's). Raw 128×128 RGBA written by tools/make-icon.py, so no image decoder is needed.
#[cfg(feature = "desktop")]
fn window_icon() -> Option<dioxus::desktop::tao::window::Icon> {
    dioxus::desktop::tao::window::Icon::from_rgba(
        include_bytes!("../assets/icon/icon-128.rgba").to_vec(),
        128,
        128,
    )
    .ok()
}

// Mobile builds (Android view-only).
#[cfg(not(feature = "desktop"))]
fn main() {
    dioxus::launch(App);
}

/// No auto-update on Android: the APK is installed by hand.
#[cfg(not(feature = "desktop"))]
#[component]
fn UpdateGate() -> Element {
    rsx! {}
}

#[component]
fn App() -> Element {
    use_context_provider(|| Signal::new(0u32));
    use_context_provider(|| Signal::new(String::new()));
    // The app runs fullscreen. F11 (macOS: control+command+F) toggles it through a hidden
    // button that assets/layout/shortcuts.js clicks; slides read its state to go fullscreen.
    #[cfg(feature = "desktop")]
    let fullscreen_toggle = {
        use dioxus::desktop::tao::window::Fullscreen;
        let window = dioxus::desktop::use_window();
        let mut fullscreen = use_signal(|| true);
        use_effect({
            let window = window.clone();
            move || {
                place_on_screen(&window.window);
                window
                    .window
                    .set_fullscreen(Some(Fullscreen::Borderless(None)));
            }
        });
        rsx! {
            button {
                id: "app-fullscreen-toggle",
                class: "window-fullscreen-control",
                title: "F11 · 전체화면 전환",
                "aria-label": if fullscreen() { "전체화면 해제 (F11)" } else { "전체화면 켜기 (F11)" },
                "data-fullscreen": fullscreen().to_string(),
                onclick: move |_| {
                    let w = &window.window;
                    if w.fullscreen().is_some() {
                        w.set_fullscreen(None);
                        place_on_screen(w);
                        fullscreen.set(false);
                    } else {
                        w.set_fullscreen(Some(Fullscreen::Borderless(None)));
                        fullscreen.set(true);
                    }
                },
                if fullscreen() { "창 모드 · F11" } else { "전체화면 · F11" }
            }
        }
    };
    #[cfg(not(feature = "desktop"))]
    let fullscreen_toggle = rsx! {};
    use_effect(|| {
        // First, so every input created later inherits the IME-safe value setter.
        document::eval(include_str!("../assets/layout/ime.js"));
        document::eval(include_str!("../assets/editor/editor.bundle.js"));
        document::eval(include_str!("../assets/terminal/terminal.bundle.js"));
        // The comic SDK is an ES module, so the loader imports it from a Blob URL built from this string.
        document::eval(&format!(
            "window.__molipComicGenSource={};window.__molipMermaidSource={};{}",
            serde_json::to_string(include_str!("../assets/comics/comic-gen.js"))
                .expect("comic sdk"),
            serde_json::to_string(include_str!("../assets/comics/mermaid.min.js"))
                .expect("mermaid"),
            include_str!("../assets/comics/comics.js")
        ));
        // The neural voice first, then the readers that use it; the chosen voice comes from the
        // assistant settings so 읽어주기 speaks with it before the AI panel is ever opened.
        document::eval(&format!(
            "{}
window.molipVoice && molipVoice.setName({});",
            include_str!("../assets/layout/voice.js"),
            serde_json::to_string(&molip_quest::assistant::Settings::load().narration_voice_name)
                .expect("voice name")
        ));
        document::eval(include_str!("../assets/speech/speech.js"));
        document::eval(include_str!("../assets/layout/split.js"));
        document::eval(include_str!("../assets/layout/shortcuts.js"));
        document::eval(include_str!("../assets/layout/toast.js"));
        document::eval(include_str!("../assets/layout/focus.js"));
        document::eval(include_str!("../assets/layout/victory.js"));
        // Reward effects on or off, as saved from the home screen.
        document::eval(&molip_quest::prefs::Prefs::load().script());
        document::eval(include_str!("../assets/layout/diagrams.js"));
        document::eval(include_str!("../assets/layout/interactive.js"));
        document::eval(include_str!("../assets/layout/quiz-pick.js"));
        document::eval(include_str!("../assets/layout/agent.js"));
        document::eval(include_str!("../assets/slides/slides.bundle.js"));
    });
    rsx! {
        if cfg!(debug_assertions) && std::env::var_os("MOLIP_DEV_LIVE").is_some() {
            style {{include_str!("../assets/fonts/fonts.css")}}
            document::Stylesheet { href: asset!("/assets/app.css") }
        } else {
            style {{include_str!("../assets/fonts/fonts.css")}}
            style {{include_str!("../assets/app.css")}}
        }
        {fullscreen_toggle}
        UpdateGate {}
        style {{include_str!("../assets/repository-player.css")}}
        style {{include_str!("../assets/terminal/terminal.bundle.css")}}
        if cfg!(debug_assertions) && std::env::var_os("MOLIP_PILOT").is_some() { pilot_ui::PilotPlayer {} }
        else if cfg!(debug_assertions) && std::env::var_os("MOLIP_LEGACY").is_some() { Workspace {} } else { player_ui::RepositoryPlayer {} }
    }
}
/// Some Windows sessions hand a new window the off-screen placeholder position (-32000, -32000)
/// with a tiny size, so the app seems to start minimized and only appears after maximizing.
/// When that happens, size the window to most of the primary screen and center it.
#[cfg(feature = "desktop")]
fn place_on_screen(window: &dioxus::desktop::tao::window::Window) {
    use dioxus::desktop::tao::dpi::{PhysicalPosition, PhysicalSize};
    let off_screen = window
        .outer_position()
        .map(|p| p.x <= -30000 || p.y <= -30000)
        .unwrap_or(false);
    if !off_screen {
        return;
    }
    let Some(monitor) = window
        .primary_monitor()
        .or_else(|| window.current_monitor())
    else {
        return;
    };
    let screen = monitor.size();
    let origin = monitor.position();
    let width = screen.width * 85 / 100;
    let height = screen.height * 85 / 100;
    window.set_minimized(false);
    window.set_inner_size(PhysicalSize::new(width, height));
    window.set_outer_position(PhysicalPosition::new(
        origin.x + ((screen.width - width) / 2) as i32,
        origin.y + ((screen.height - height) / 2) as i32,
    ));
}

/// The `molip` protocol: `/tts` turns a sentence into speech for the narration mode. The page
/// lives on another origin (dioxus://, or http://dioxus.index.html on Windows), so the response
/// allows any origin; the request is a "simple" POST (text/plain body), which needs no preflight.
/// Desktop only: the Android build has no `dioxus::desktop` and no narration.
#[cfg(feature = "desktop")]
fn tts_response(
    request: dioxus::desktop::wry::http::Request<Vec<u8>>,
) -> dioxus::desktop::wry::http::Response<std::borrow::Cow<'static, [u8]>> {
    use dioxus::desktop::wry::http::Response;
    use std::borrow::Cow;
    let reply = |status: u16, kind: &str, engine: &str, body: Vec<u8>| {
        Response::builder()
            .status(status)
            .header("Content-Type", kind)
            .header("Access-Control-Allow-Origin", "*")
            .header("Access-Control-Expose-Headers", "X-Molip-Engine")
            .header("X-Molip-Engine", engine)
            .header("Cache-Control", "no-store")
            .body(Cow::Owned(body))
            .expect("tts response")
    };
    if request.uri().path() != "/tts" {
        return reply(
            404,
            "text/plain; charset=utf-8",
            "none",
            b"not found".to_vec(),
        );
    }
    if request.method() != dioxus::desktop::wry::http::Method::POST {
        return reply(
            405,
            "text/plain; charset=utf-8",
            "none",
            b"POST only".to_vec(),
        );
    }
    let Ok(body) = serde_json::from_slice::<serde_json::Value>(request.body()) else {
        return reply(
            400,
            "text/plain; charset=utf-8",
            "none",
            b"bad json".to_vec(),
        );
    };
    let text = body["text"].as_str().unwrap_or_default();
    let voice = body["voice"].as_str().unwrap_or_default();
    match molip_quest::tts::synthesize(voice, text) {
        Ok((bytes, engine)) => reply(200, "audio/mpeg", engine, bytes),
        Err(error) => reply(503, "text/plain; charset=utf-8", "none", error.into_bytes()),
    }
}

/// Which screen fills the window: the classroom home, the learning flow, or one gallery page.
#[derive(Clone, Copy, PartialEq)]
enum View {
    Home,
    Learning,
    Practice,
    Gallery(ui::GalleryKind),
    Avatars,
}

/// Updates are offered once per build. Installation always starts with an explicit click.
/// "HH:MM" of the local time, for the update status line.
fn chrono_like_now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0) as i64;
    // Local offset from the C runtime is not available without a crate; show Korean time
    // (UTC+9), the class's time zone.
    let local = secs + 9 * 3600;
    format!("{:02}:{:02}", local / 3600 % 24, local / 60 % 60)
}

#[cfg(feature = "desktop")]
#[derive(Clone, PartialEq)]
enum UpdatePhase {
    Hidden,
    Offered,
    Downloading(u64, u64),
    Installing,
    Failed(String),
}

#[cfg(feature = "desktop")]
#[component]
fn UpdateGate() -> Element {
    use molip_quest::updater::{self, Release};
    let mut release = use_signal(|| None::<Release>);

    let mut phase = use_signal(|| UpdatePhase::Hidden);
    // The build the student answered 나중에 to; it is not offered again.
    let mut notified = use_signal(||molip_quest::data_dir().and_then(|dir|updater::UpdateNotices::open(&dir.join("update-notices.json"))).unwrap_or_default());
    let install = Callback::new(move |_: ()| {
        let Some(found) = release() else { return };
        if matches!(*phase.peek(),UpdatePhase::Downloading(_,_)|UpdatePhase::Installing) {return;}
        phase.set(UpdatePhase::Downloading(0, found.size));
        spawn(async move {
            let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel::<(u64, u64)>();
            let target = found.clone();
            let worker = tokio::task::spawn_blocking(move || {
                updater::download(&target, |done, total| {
                    let _ = tx.send((done, total));
                })
            });
            let mut shown = 0u64;
            while let Some((done, total)) = rx.recv().await {
                // Repaint on every percent, not every chunk.
                let percent = if total > 0 { done * 100 / total } else { 0 };
                if percent != shown || done == total {
                    shown = percent;
                    phase.set(UpdatePhase::Downloading(done, total));
                }
            }
            match worker.await.unwrap_or_else(|e| Err(e.to_string())) {
                Ok(path) => {
                    phase.set(UpdatePhase::Installing);
                    // Returns only when the hand-over failed; otherwise the process exits here.
                    if let Err(e) = updater::install_and_restart(&path) {
                        phase.set(UpdatePhase::Failed(e));
                    }
                }
                Err(e) => phase.set(UpdatePhase::Failed(e)),
            }
        });
    });
    // Startup, then every five minutes, or a manual request. One worker owns checks.
    let request = use_context::<Signal<u32>>();
    let mut status = use_context::<Signal<String>>();
    use_future(move || async move {
        let mut schedule=updater::UpdateSchedule::default();
        let started=std::time::Instant::now();
        let mut seen = *request.peek();
        loop {
            let manual=*request.peek()!=seen;
            if manual {seen=*request.peek();}
            if updater::enabled() && schedule.begin(started.elapsed().as_secs(),manual) {
                status.set("업데이트 확인 중…".into());
                let result = tokio::task::spawn_blocking(updater::check)
                    .await
                    .unwrap_or_else(|e| Err(e.to_string()));
                schedule.finish();
                let stamp = chrono_like_now();
                match &result {
                    Ok(Some(found)) => {
                        status.set(format!("새 버전 있음 · {} ({stamp} 확인)", found.title))
                    }
                    Ok(None) => status.set(format!(
                        "최신 버전입니다 · 빌드 {} ({stamp} 확인)",
                        updater::current_build()
                    )),
                    Err(e) => status.set(format!("확인 실패 · {e} ({stamp})")),
                }
                if let Ok(Some(found)) = result {

                    let idle = matches!(*phase.peek(), UpdatePhase::Hidden | UpdatePhase::Offered);
                    if idle {
                        let first_notice=match notified.write().record(found.build) {Ok(first)=>first,Err(error)=>{status.set(format!("새 버전 있음 · 안내 기록 저장 실패: {error}"));true}};
                        release.set(Some(found));
                        if first_notice {phase.set(UpdatePhase::Offered);}
                    }
                }
            } else if !updater::enabled() {
                status.set("개발 빌드는 업데이트를 확인하지 않아요.".into());
            }
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        }
    });
    let settings=rsx! {details {class:"app-update-settings",summary {"설정"}
        p {"{status}"}
        button {onclick:move |_|{let mut request=request;request+=1;},"업데이트 확인"}
        button {disabled:release().is_none(),onclick:move |_|install.call(()),"새 버전 설치"}
    }};
    let Some(found) = release() else {
        return rsx! {{settings}button {class:"app-update-icon",aria_label:"앱 업데이트 확인",title:status(),onclick:move |_|{let mut request=request;request+=1;},"↻"}};
    };
    let title = found.title.clone();
    let content=match phase() {
        UpdatePhase::Hidden => rsx! {button {class:"app-update-icon has-update",aria_label:"앱 업데이트 설치",title:format!("새 버전 · {title}"),onclick:move |_|install.call(()),"↥"}},
        UpdatePhase::Offered => rsx! {
            div { class:"update-banner", role:"status",
                span { class:"update-dot" }
                span { {format!("새 버전이 나왔습니다 · {title}")} }
                button { class:"primary", onclick: move |_| install.call(()), "지금 업데이트" }
                button { onclick: move |_| { phase.set(UpdatePhase::Hidden); }, "나중에" }
            }
        },
        state => {
            let (line, percent, failed) = match &state {
                UpdatePhase::Downloading(done, total) => (
                    if *total > 0 {
                        format!(
                            "설치 파일을 받는 중 · {} / {} MB",
                            done / 1_048_576,
                            total / 1_048_576
                        )
                    } else {
                        format!("설치 파일을 받는 중 · {} MB", done / 1_048_576)
                    },
                    if *total > 0 {
                        (done * 100 / total) as usize
                    } else {
                        0
                    },
                    None,
                ),
                UpdatePhase::Installing => {
                    ("설치하고 다시 시작합니다. 잠시만요.".to_string(), 100, None)
                }
                UpdatePhase::Failed(e) => (e.clone(), 0, Some(())),
                _ => ("새 버전을 설치합니다.".to_string(), 0, None),
            };
            rsx! {
                div { class:"doctor-backdrop update-backdrop", section { class:"doctor-panel update-panel", role:"dialog", aria_modal:"true", aria_label:"업데이트",
                    h2 { "새 버전 업데이트" }
                    p { class:"update-title", "{title}" }
                    p { "업데이트하면 앱을 닫고 새 버전으로 다시 열어요." }
                    div { class:"update-track", div { class:"update-fill", style: format!("width:{percent}%") } }
                    p { class: if failed.is_some() {"error"} else {"update-line"}, "{line}" }
                    if failed.is_some() {
                        div { class:"actions",
                            button { class:"primary", onclick: move |_| install.call(()), "다시 시도" }
                            button { onclick: move |_| { phase.set(UpdatePhase::Hidden); }, "이대로 계속" }
                        }
                    }
                } }
            }
        }
    };
    rsx! {{settings}{content}}
}

#[component]
fn Workspace() -> Element {
    let mut view = use_signal(|| View::Home);
    use_context_provider(|| {
        instructor_mode::InstructorSession(Signal::new(None::<practice::Materials>))
    });
    use_context_provider(|| instructor_mode::InstructorRequests(Signal::new(None)));
    let mut study_target = use_signal(|| (String::new(), usize::MAX));
    // Bumped when progress is reset from home, so the avatar card reads the store again.
    let mut home_epoch = use_signal(|| 0u32);
    // Reward effects: animation and sound switches shown on the home card.
    let mut prefs = use_signal(molip_quest::prefs::Prefs::load);
    // Update check on demand (sidebar button) and its last outcome, shared with UpdateGate.
    let mut update_request = use_context::<Signal<u32>>();
    let update_status = use_context::<Signal<String>>();
    let mut active_course = use_signal(|| {
        let source = if let Ok(path) = std::env::var("MOLIP_COURSE_PATH") {
            std::fs::read_to_string(path).map_err(|e| e.to_string())?
        } else {
            molip_quest::DEFAULT_COURSE.to_string()
        };
        Course::parse(&source)
    });
    match active_course() {
        Err(error) => {
            rsx! { main { h1 {"수업을 불러올 수 없습니다."} p {"{error}"} ui::JavaDoctorPanel {} } }
        }
        Ok(course) => {
            rsx! { div { class: match view() { View::Home => "shell", View::Learning | View::Practice => "shell practice-shell", View::Gallery(_) | View::Avatars => "shell practice-shell gallery-shell" },
                aside { class:"sidebar", div {class:"brand", "몰입 퀘스트 3"} h3 {"{course.title}"} p {{format!("{}챕터 · {}단원", course.chapters.len(), course.total_units())}}
                    button { onclick:move |_| { document::eval("window.molipAgent?.stop()"); active_course.set(Course::parse(molip_quest::DEFAULT_COURSE)); view.set(View::Home); }, "자바 기초 · JDK 25" }
                    button { onclick:move |_| { document::eval("window.molipAgent?.stop()"); active_course.set(Course::parse(include_str!("../courses/kpc-finance.json"))); view.set(View::Home); }, "기존 샘플 · 금융 데이터 분석" }
                    p {class:"build-number", {let build = molip_quest::updater::current_build(); if build > 0 {format!("빌드 {build} · 새 버전은 선택해서 설치해요")} else {"개발 빌드".to_string()}}}
                    div {class:"update-check",
                        button {onclick:move |_| update_request += 1, "업데이트 확인"}
                        span {class:"update-status", "{update_status}"}
                    }
                    if ui::VIEW_ONLY { p {class:"view-only-note","Android 열람 모드 · 모든 단원과 미션이 열려 있습니다. 개념과 퀴즈를 풀고, 코딩 미션은 읽고 넘어갑니다. 코드 실행·채점은 데스크톱 앱에서 하세요."} }
                    if course.id == "immersion-quest-3-java25-v1" { ui::JavaDoctorPanel {} } else { ui::DoctorPanel {} } }
                main {
                    match view() {
                        View::Practice => rsx! {
                            button {class:"classroom-back", onclick:move |_|view.set(View::Home), "← 클래스룸"}
                            practice::PracticeView {}
                        },
                        View::Learning => rsx! {
                            button {class:"classroom-back", onclick:move |_|view.set(View::Home), "← 클래스룸"}
                            Learning { course:course.clone(),start_unit:study_target().0,start_mission:study_target().1 }
                        },
                        View::Gallery(kind) => rsx! {
                            button {class:"classroom-back", onclick:move |_|view.set(View::Home), "← 클래스룸"}
                            ui::Gallery { course:course.clone(), kind }
                        },
                        View::Avatars => rsx! {
                            button {class:"classroom-back", onclick:move |_|view.set(View::Home), "← 클래스룸"}
                            ui::AvatarGallery { course:course.clone() }
                        },
                        View::Home => rsx! {
                            h1 {"{course.title}"} p {"개념을 확인하고 코딩 미션과 퀴즈를 클리어하며 성장하세요."}
                        p {class:"shortcut-help",
                            "단축키 (맥은 Ctrl 대신 ⌘) · " kbd {"Ctrl+←"} " " kbd {"Ctrl+→"} " 이전·다음 단계 · " kbd {"Ctrl+↑"} " " kbd {"Ctrl+↓"} " 이전·다음 단원 · " kbd {"Ctrl+K"} " 목차 · " kbd {"Ctrl+I"} " AI 창 · " kbd {"Ctrl+Enter"} " 코드 실행, 두 번 연타 제출 · " kbd {"Enter"} " 주관식 채점 · 슬라이드 " kbd {"←"} " " kbd {"→"} ", 마지막 장에서 →는 다음 단계 · " kbd {"Ctrl"} "+더블 클릭 읽어 주기 · " kbd {"Space"} " 해설 일시정지 · " kbd {"F11"} " 전체 화면 (맥 ⌃⌘F) · "
                            button {class:"shortcut-sheet-open",onclick:move |_|{document::eval("window.molipShortcuts && molipShortcuts.toggleSheet(true);");},"전체 단축키 (Ctrl+/)"}
                        }
                            {let _ = home_epoch(); let completed = ui::completed_missions(&course); let level = molip_quest::avatar::level_for(completed); let within = completed % molip_quest::avatar::MISSIONS_PER_LEVEL; let last = molip_quest::avatar::max_level(ui::total_missions(&course)); rsx!{
                            section {class:"card home-progress",
                                div {class:"home-avatar",dangerous_inner_html:molip_quest::avatar::svg(level)}
                                div {class:"home-progress-body",
                                    h3 {{format!("Lv. {level} · {}",molip_quest::avatar::title(level))}}
                                    p {class:"home-title",{format!("미션 {completed}개 클리어 · {} XP",completed*molip_quest::avatar::XP_PER_MISSION)}}
                                    div {class:"home-track",div {class:"home-fill",style:format!("width:{}%",if level>=last {100} else {within*100/molip_quest::avatar::MISSIONS_PER_LEVEL})}}
                                    p {class:"home-next",{if level>=last {"마지막 레벨입니다. 큐가 다 자랐어요.".to_string()} else {format!("다음 레벨까지 미션 {}개 · 레벨 {}개마다 큐의 모습이 바뀝니다",molip_quest::avatar::MISSIONS_PER_LEVEL-within,molip_quest::avatar::LEVELS_PER_TIER)}}}
                                    div {class:"course-actions",button {class:"gallery-link",onclick:move |_|view.set(View::Avatars),"아바타 모아보기"}}
                                    div {class:"home-fx",
                                        button {class:if prefs().animations {""} else {"off"},title:"경험치·레벨업 애니메이션",onclick:move |_|{let mut p=prefs();p.animations=!p.animations;let _=p.save();prefs.set(p);document::eval(&p.script());},
                                            {if prefs().animations {"✨ 애니메이션 켬"} else {"✨ 애니메이션 끔"}}}
                                        button {class:if prefs().sounds {""} else {"off"},title:"경험치 효과음과 레벨업 팡파르",onclick:move |_|{let mut p=prefs();p.sounds=!p.sounds;let _=p.save();prefs.set(p);document::eval(&p.script());},
                                            {if prefs().sounds {"🔔 효과음 켬"} else {"🔔 효과음 끔"}}}
                                    }
                                }
                            }}}
                            section {class:"card course-row", h2 {"{course.title}"} p {"{course.description}"}
                                p {{format!("{} 단원",course.total_units())}}
                                div {class:"course-actions",
                                    button {class:"primary",onclick:move |_|{study_target.set((String::new(),usize::MAX));view.set(View::Learning);},"학습 시작 · 이어하기"}
                                    if course.id != "immersion-quest-3-java25-v1" { button {class:"gallery-link",onclick:move |_|view.set(View::Practice),"도전 과제"} }
                                    for kind in ui::GalleryKind::ALL {
                                        button {class:"gallery-link",onclick:move |_|view.set(View::Gallery(kind)),{kind.label()}}
                                    }
                                    ui::ResetProgress {course_id:course.id.clone(),onreset:move |_|{home_epoch+=1;}}
                                }
                                div {class:"course-actions instructor-row", instructor_mode::InstructorLogin {}}
                            }
                        },
                    }
                }
            } }
        }
    }
}
