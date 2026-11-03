//! GitHub 로그아웃 next to the account in the player header, and what the signed-out screen says.
use dioxus::prelude::*;
use molip_quest::github_logout::{self,SignedOut,StoredToken,REVOKE_URL};

#[derive(Clone,PartialEq)]
enum Phase {Closed,Confirm,Working,Failed(String)}

#[component]
pub fn GithubLogout(login:String,disabled:bool,onworking:EventHandler<bool>,onsignedout:EventHandler<()>)->Element {
    let mut phase=use_signal(||Phase::Closed);
    let open=!matches!(phase(),Phase::Closed);
    use_effect(move ||{
        let open=!matches!(phase(),Phase::Closed);
        document::eval(if open {"const d=document.getElementById('github-logout-dialog');if(d&&!d.open)d.showModal();"}else{"document.getElementById('github-logout-dialog')?.close()"});
    });
    let confirm={
        let login=login.clone();
        move |_|{
            let login=login.clone();
            phase.set(Phase::Working);onworking.call(true);
            spawn(async move {
                let result=molip_quest::github_player::background(move ||github_logout::sign_out(&login)).await;
                onworking.call(false);
                match result {
                    Ok(_)=>{phase.set(Phase::Closed);onsignedout.call(());}
                    Err(error)=>phase.set(Phase::Failed(format!("{error} 아무것도 바꾸지 않았어요."))),
                }
            });
        }
    };
    let account=format!("@{login}");
    let working=matches!(phase(),Phase::Working);
    rsx!{
        button {r#type:"button",class:"account-logout-open",title:"이 컴퓨터의 gh에서 이 GitHub 계정의 저장된 토큰을 지워요.",disabled:disabled||open,
            onclick:move |_|phase.set(Phase::Confirm),"로그아웃"}
        if open {
        dialog {id:"github-logout-dialog",class:"lesson-info-dialog account-reset-dialog",aria_labelledby:"github-logout-title",
            onkeydown:move |event|{if event.key()==Key::Escape&&!working{phase.set(Phase::Closed);}},
            oncancel:move |event|{if working{event.prevent_default();}else{phase.set(Phase::Closed);}},
            header {h2 {id:"github-logout-title","GitHub 로그아웃"}
                button {r#type:"button",disabled:working,onclick:move |_|phase.set(Phase::Closed),"닫기"}}
            p {class:"account-reset-intro","이 컴퓨터의 gh에서 "strong {{account.clone()}}" 계정(github.com)의 저장된 토큰을 지워요."}
            section {class:"lesson-reset account-reset",
                ul {class:"account-reset-effects",
                    li {"터미널에서 쓰는 gh도 이 계정이 로그아웃돼요. 다른 계정과 다른 호스트는 그대로예요."}
                    li {"MQ는 「다시 연결」을 누를 때까지 GitHub를 쓰지 않아요. 앱을 다시 열어도 로그아웃 상태예요."}
                    li {"수업, 진도, 작성한 코드는 이 컴퓨터에 그대로 남아요. 아직 못 올린 진도는 같은 계정으로 다시 연결하면 올라가요."}
                    li {"GitHub 서버의 토큰은 폐기하지 않아요. 폐기는 로그아웃한 뒤 GitHub 설정에서 직접 할 수 있어요."}
                }
                match phase() {
                    Phase::Working=>rsx!{p {role:"status","로그아웃하고 있어요."}},
                    Phase::Failed(text)=>rsx!{p {class:"lesson-reset-status account-reset-error",role:"alert","{text}"}},
                    _=>rsx!{},
                }
                div {class:"lesson-reset-actions",
                    button {r#type:"button",class:"danger account-reset-confirm",disabled:working,onclick:confirm,"로그아웃"}
                    button {r#type:"button",disabled:working,onmounted:move |event|async move{let _=event.data().set_focus(true).await;},onclick:move |_|phase.set(Phase::Closed),"취소"}
                }
            }
        }
        }
    }
}

/// The saved logout state, so a failed or unverified removal still shows after a restart.
#[component]
pub fn SignedOutNotice(state:SignedOut,onretry:EventHandler<()>,retrying:bool)->Element {
    let account=if state.login.is_empty() {"이".to_string()}else{format!("@{}",state.login)};
    let can_retry=!state.login.is_empty();
    let environment=github_logout::environment_tokens().join(", ");
    let retry=rsx!{if can_retry {button {r#type:"button",disabled:retrying,onclick:move |_|onretry.call(()),if retrying {"토큰을 지우고 있어요"}else{"토큰 삭제 다시 시도"}}}};
    rsx!{
        section {class:"gh-setup-card gh-signed-out",role:"status",aria_label:"GitHub 로그아웃 상태",
            h2 {"GitHub에서 로그아웃했어요"}
            p {"MQ는 "strong {{account.clone()}}" 계정으로 GitHub를 쓰지 않아요. 수업, 진도, 작성한 코드는 이 컴퓨터에 그대로예요."}
            match state.stored {
                Some(StoredToken::Removed{switched_to})=>rsx!{
                    p {"이 컴퓨터의 gh에서 저장된 토큰을 지웠어요."}
                    if let Some(next)=switched_to {p {"gh의 github.com 활성 계정이 "strong {{format!("@{next}")}}"로 바뀌었어요. MQ는 「다시 연결」 전까지 이 계정도 쓰지 않아요."}}
                },
                Some(StoredToken::AlreadyAbsent)=>rsx!{p {"이 컴퓨터의 gh에는 이 계정의 저장된 토큰이 없었어요."}},
                Some(StoredToken::Failed(error))=>rsx!{
                    p {class:"gh-signed-out-warning",role:"alert","gh의 저장된 토큰을 지우지 못했어요. 토큰은 아직 이 컴퓨터에 있어요."}
                    details {class:"gh-setup-error",summary {"gh가 남긴 내용"}pre {"{error}"}}
                    {retry}
                },
                Some(StoredToken::Unverified(error))=>rsx!{
                    p {class:"gh-signed-out-warning",role:"alert","gh의 저장된 토큰을 지웠는지 확인하지 못했어요. {error}"}
                    {retry}
                },
                None=>rsx!{
                    p {class:"gh-signed-out-warning",role:"alert","gh의 저장된 토큰을 지웠는지 확인하지 못했어요."}
                    {retry}
                },
            }
            if !environment.is_empty() {
                p {class:"gh-signed-out-warning",role:"alert","환경변수 {environment}에 토큰이 남아 있어요. gh는 이 값을 먼저 써요. MQ는 이 값을 바꾸지 않아요. 직접 지운 뒤 MQ를 다시 여세요."}
            }
            p {"GitHub 서버의 토큰은 아직 폐기되지 않았어요. 폐기하려면 GitHub 설정의 GitHub CLI 앱에서 Revoke Access를 누르세요. 모든 기기의 gh 토큰이 함께 폐기돼요."}
            a {href:REVOKE_URL,target:"_blank",rel:"noopener noreferrer","GitHub 설정에서 토큰 폐기"}
        }
    }
}
