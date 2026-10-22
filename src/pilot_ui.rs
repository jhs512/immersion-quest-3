//! Debug controls around the real RepositoryPlayer, backed by an isolated transport.
use dioxus::prelude::*;
use molip_quest::{pilot_source, repository_course::{CourseManifest, Lesson}};

#[component]
pub fn PilotPlayer(window_controls: Element) -> Element {
    let mut generation = use_signal(|| 0u64);
    let mut notice = use_signal(String::new);
    let mut setup_preview = use_signal(|| false);
    #[cfg(feature="desktop")]
    let window = dioxus::desktop::use_window();
    #[cfg(not(feature="desktop"))]
    let window = ();
    use_future({let window=window.clone();move || {let window=window.clone();async move {
        if !pilot_source::enabled() || std::env::var_os("MOLIP_PILOT_SELF_TEST").is_none() { return; }
        let restart_phase=std::env::var("MOLIP_PILOT_SELF_TEST").ok().and_then(|mode|mode.strip_prefix("restart-").map(str::to_owned)).filter(|phase|matches!(phase.as_str(),"seed"|"reopen"));
        let script=if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("toolbar-audit") {
            include_str!("../tools/player-pilot-toolbar.js").to_owned()
        }else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("course-guide") {
            include_str!("../tools/player-pilot-course-guide.js").to_owned()
        }else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("course-identity") {
            include_str!("../tools/player-pilot-course-identity.js").to_owned()
        }else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("lesson-link") {
            format!("window.mq3LinkTargets={};{}",std::env::var("MOLIP_LINK_TARGETS").unwrap(),include_str!("../tools/player-pilot-lesson-link.js"))
        }else if let Some(phase)=&restart_phase {
            format!("window.mq3RestartPhase={};{}",serde_json::to_string(phase).unwrap(),include_str!("../tools/player-pilot-restart.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("async-progress") {
            include_str!("../tools/player-pilot-async-progress.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("content-submit") {
            include_str!("../tools/player-pilot-content-submit.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("invalid-order") {
            include_str!("../tools/player-pilot-invalid-order.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("vim-ready") {
            include_str!("../tools/player-pilot-vim-ready.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("shortcuts-feedback") {
            include_str!("../tools/player-pilot-shortcuts.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("git-course") {
            include_str!("../tools/player-pilot-git-course.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-launch") {
            format!("window.mq3JavaPilot={{pilot:\"뉴\"}};window.mq3JavaLaunch={};{}",include_str!("../courses/redesigned/java-launch.json"),include_str!("../tools/player-pilot-java-launch.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("java-arguments") {
            format!("window.mq3JavaPilot={{pilot:\"듀\"}};window.mq3JavaLaunch={};{}",include_str!("../courses/redesigned/java-arguments.json"),include_str!("../tools/player-pilot-java-launch.js"))
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("bash-basics") {
            include_str!("../tools/player-pilot-bash.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("terminal-restore") {
            include_str!("../tools/player-pilot-terminal-restore.js").to_owned()
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("lesson-loading") {
            include_str!("../tools/player-pilot-loading.js").to_owned()
        } else if let Some(script)=std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref().and_then(molip_quest::lesson_registry::self_test_script) {
            script
        } else if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("interaction-example") {include_str!("../tools/player-pilot-example.js").to_owned()} else {format!("window.mq3FirstGitOnly={};window.mq3IncludeGitBranch={};{}",matches!(std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref(),Some("git-first"|"git-lessons")),std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()!=Some("git-first"),include_str!("../tools/player-pilot-native.js"))};
        let mut bridge = document::eval(&script);
        let mut progress_lock:Option<rusqlite::Connection>=None;
        let result = match tokio::time::timeout(std::time::Duration::from_secs(480), async {
            loop {
                let message=bridge.recv::<serde_json::Value>().await?;
                if matches!(std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref(),Some("toolbar-audit"|"course-guide")) && message["control"]=="resize" {
                    #[cfg(feature="desktop")] {
                        window.window.set_fullscreen(None);
                        window.window.set_inner_size(dioxus::desktop::tao::dpi::LogicalSize::new(message["width"].as_u64().unwrap_or(1280) as f64,message["height"].as_u64().unwrap_or(720) as f64));
                    }
                    continue;
                }
                if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("lesson-link")&&message["control"]=="lesson-link-stage" {
                    if let Some(stage)=message["stage"].as_str().filter(|stage|matches!(*stage,"first"|"second")){
                        let _=std::fs::write(pilot_source::data_dir().unwrap().join(format!("lesson-link-{stage}")),"");
                    }
                    continue;
                }
                if std::env::var("MOLIP_PILOT_SELF_TEST").ok().as_deref()==Some("async-progress")&&message["control"].is_string(){
                    let root=pilot_source::data_dir().unwrap();
                    if message["control"]=="pause-record"{
                        let db=rusqlite::Connection::open(root.join("progress-events.sqlite3")).unwrap();
                        db.busy_timeout(std::time::Duration::from_secs(5)).unwrap();
                        db.execute_batch("BEGIN EXCLUSIVE").unwrap();progress_lock=Some(db);
                    }
                    if message["control"]=="resume-record"{if let Some(db)=progress_lock.take(){db.execute_batch("ROLLBACK").unwrap();}}
                    if message["control"]=="resume"{std::fs::remove_file(root.join("pilot-progress-blocked")).unwrap();}
                    #[cfg(debug_assertions)]
                    if message["control"]=="advance-hour" {
                        let result=tokio::task::spawn_blocking(||molip_quest::progress_sync::ProgressStore::installed()?.flush_pilot_hour()).await;
                        if !matches!(result,Ok(Ok(()))) {document::eval("window.mq3ExpectedUploadFailure=true");}
                    }
                    let pending=if progress_lock.is_some(){0}else{molip_quest::progress_sync::ProgressStore::installed().unwrap().pending_count(987654321).unwrap()};
                    let attempts=std::fs::read_to_string(root.join("pilot-progress-attempts")).unwrap_or_default().lines().count();
                    document::eval(&format!("window.mq3ProgressStats={};",serde_json::json!({"token":message["token"],"pending":pending,"attempts":attempts,"running":molip_quest::progress_sync::is_syncing(987654321).unwrap()})));
                    continue;
                }
                return Ok::<_,dioxus::document::EvalError>(message);
            }
        }).await {
            Ok(Ok(result)) => result,
            _ => serde_json::json!({"passed":false,"error":"Native WebView test timed out or disconnected"}),
        };
        #[cfg(debug_assertions)]
        if let Ok(store)=molip_quest::progress_sync::ProgressStore::installed(){
            // Existing native cases assert the final remote history. Advance their
            // isolated collection window explicitly after the learner scenario.
            tokio::time::sleep(std::time::Duration::from_millis(250)).await;
            let _=tokio::task::spawn_blocking(move||store.flush_pilot_hour()).await;
        }
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
    }}});
    if setup_preview() { return rsx! {div {class:"repository-player needs-gh",
        crate::gh_setup_ui::GhSetup {message:String::new(),checking:false,onretry:move |_|setup_preview.set(false)}
    }}; }
    rsx! {
        aside { class: "pilot-toolbar", aria_label: "개발 검증 도구",
          details {class:"pilot-toolbox",summary {"개발 검증 도구"}
           div {class:"pilot-tool-grid",
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
          }
        }
        {rsx! { crate::player_ui::RepositoryPlayer { key: "pilot-{generation}",window_controls:window_controls.clone() } }}
    }
}
