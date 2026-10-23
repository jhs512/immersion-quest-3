//! Debug-only Finder launch check: real account lookup and the actual PR terminal,
//! without enrollment, progress events, repository creation or PR operations.
use dioxus::prelude::*;
use molip_quest::{github_player::{self,Github}, repository_course::Lesson};
#[component]
pub fn MacosLoginVerification()->Element {
    let mut account=use_signal(||"계정을 확인하고 있어요.".to_string());
    use_future(move||async move {
        let result=github_player::background(||Github::new().user().map(|user|user.login)).await;
        account.set(match result{Ok(login)=>format!("플레이어 계정: @{login}"),Err(error)=>format!("계정 확인 실패: {error}")});
    });
    let row=molip_quest::lesson_registry::find("github-pr").expect("registered PR lesson");
    let lesson:Lesson=serde_json::from_str(row.lesson).expect("PR lesson");
    let exercise=lesson.tasks[0].git_terminal.clone().expect("PR terminal");
    // xterm fits to its host: constrain the flex root so its measured height
    // cannot feed back into document growth on every ResizeObserver callback.
    rsx!{main {class:"repository-player",style:"height:100dvh;box-sizing:border-box;display:flex;flex-direction:column;overflow:hidden",
        h1 {"Mac 로그인 공유 검증"}
        p {"{account}"}
        p {"기존 로그인만 읽어요. 저장소나 PR을 만들지 않아요."}
        p {"실습 터미널에서 gh api user --jq .login을 실행하세요."}
        crate::git_terminal_ui::GitTerminal {exercise,demo:false,scope:Some("macos-auth-verification".into()),onready:move |_|{},oncontrol:move |_|{}}
    }}
}
