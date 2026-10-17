use dioxus::prelude::*;

fn command(text:&str) {
    document::eval(&format!("window.mq3SetupTerminal?.command({});",serde_json::to_string(text).unwrap()));
}

#[component]
pub fn GhSetup(message:String,checking:bool,onretry:EventHandler<()>)->Element {
    let mut ready=use_signal(||false);
    if checking {return rsx!{section {class:"gh-checking",role:"status",h2 {"GitHub 연결을 확인하고 있어요"}p {"설치된 gh의 로그인 상태를 확인해요."}}};}
    rsx!{
        section {class:"gh-setup-card",aria_label:"GitHub CLI 준비",
            div {class:"gh-setup-intro",p {class:"gh-setup-kicker","GITHUB CLI"}h2 {"여기서 준비하고 바로 시작해요"}
                p {"아래 터미널에서 gh를 설치하고 로그인하세요."}
                p {"GitHub 승인은 브라우저에서 진행해요."}
            }
            div {class:"gh-setup-commands",
                button {disabled:!ready(),onclick:move |_|command(if cfg!(windows){"winget install --id GitHub.cli --exact --source winget"}else if cfg!(target_os="macos"){"brew install gh"}else{"sudo apt install gh"}),"1 · gh 설치"}
                button {disabled:!ready(),onclick:move |_|command("gh auth login --hostname github.com --git-protocol https --web"),"2 · GitHub 로그인"}
                button {disabled:!ready(),onclick:move |_|command("gh auth status --hostname github.com"),"로그인 상태 확인"}
            }
            div {class:"gh-terminal-frame",
                div {class:"gh-terminal-heading",span {"이 컴퓨터의 터미널"}span {"직접 입력할 수 있어요"}}
                EmbeddedSetupTerminal {onready:move |value|ready.set(value)}
            }
            p {class:"gh-setup-help","이미 gh가 있으면 로그인부터 진행하세요. 질문에는 터미널에서 직접 답하면 돼요."}
            div {class:"gh-setup-footer",
                a {href:"https://cli.github.com/",target:"_blank",rel:"noopener noreferrer","gh 설치 안내"}
                button {class:"primary",onclick:move |_|onretry.call(()),"준비 완료 · 연결 확인"}
            }
            if !message.is_empty() {details {class:"gh-setup-error",summary {"연결 확인 내용"}pre {"{message}"}}}
        }
    }
}

#[cfg(not(target_os="android"))]
#[component]
fn EmbeddedSetupTerminal(onready:EventHandler<bool>)->Element {
    use base64::Engine;
    use molip_quest::setup_terminal::SetupTerminal;
    use std::sync::{Arc,Mutex};
    #[derive(serde::Deserialize)]
    struct Input {kind:String,#[serde(default)] data:String,#[serde(default)] rows:u16,#[serde(default)] cols:u16}
    let terminal=use_hook(||Arc::new(Mutex::new(None::<SetupTerminal>)));
    let mut error=use_signal(String::new);
    let cleanup=terminal.clone();
    use_drop(move ||{
        let shell=cleanup.lock().unwrap_or_else(|e|e.into_inner()).take();
        // ConPTY may drain pending output while closing. Never hold the UI thread there.
        if let Some(shell)=shell {std::thread::spawn(move ||drop(shell));}
        document::eval("window.mq3SetupTerminal?.dispose()");
    });
    use_future(move ||{
        let terminal=terminal.clone();
        async move {
            let opened=tokio::task::spawn_blocking(SetupTerminal::open).await;
            let (shell,mut output)=match opened {
                Ok(Ok(pair))=>pair,
                Ok(Err(e))=>{error.set(format!("터미널을 열지 못했어요. {e}"));return;},
                Err(e)=>{error.set(format!("터미널을 열지 못했어요. {e}"));return;},
            };
            *terminal.lock().unwrap_or_else(|e|e.into_inner())=Some(shell);
            let mut bridge=document::eval("(async()=>{await new Promise(done=>window.mq3SetupTerminal.mount(event=>dioxus.send(event),done));})()");
            let input_terminal=terminal.clone();
            spawn(async move {
                while let Ok(event)=bridge.recv::<Input>().await {
                    let mut guard=input_terminal.lock().unwrap_or_else(|e|e.into_inner());
                    let Some(shell)=guard.as_mut() else{break};
                    match event.kind.as_str() {
                        "input"=>{let _=shell.input(&event.data);},
                        "resize"=>{let _=shell.resize(event.rows,event.cols);},
                        _=>{},
                    }
                }
            });
            onready.call(true);
            while let Some(bytes)=output.recv().await {
                let encoded=base64::engine::general_purpose::STANDARD.encode(bytes);
                document::eval(&format!("window.mq3SetupTerminal?.write('{encoded}')"));
            }
            onready.call(false);
            terminal.lock().unwrap_or_else(|e|e.into_inner()).take();
            error.set("터미널이 종료됐어요. 연결 확인을 눌러주세요.".into());
        }
    });
    rsx!{div {id:"gh-setup-terminal",aria_label:"설정 터미널"}
        if !error().is_empty() {p {class:"gh-terminal-error",role:"status","{error}"}}
    }
}

#[cfg(target_os="android")]
#[component]
fn EmbeddedSetupTerminal(onready:EventHandler<bool>)->Element {
    rsx!{p {"터미널은 데스크톱 앱에서 사용할 수 있어요."}}
}
