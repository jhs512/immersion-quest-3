//! 내 전체 학습 진도 초기화 (molip_quest::progress_reset) next to the account in the player header.
//! The per-lesson 이 수업 진도 초기화 stays in each lesson's 학습 정보.
use dioxus::prelude::*;
use molip_quest::github_player::{self, Github, GithubUser};
use molip_quest::progress_reset::{self, CourseHistory, Plan};

#[derive(Clone, PartialEq)]
enum Phase { Closed, Loading, Ready(Plan), Saving, Done(String), Failed(String) }

#[component]
pub fn AccountProgressReset(github: Github, user: GithubUser, repositories: Vec<String>, disabled: bool, onreset: EventHandler<()>) -> Element {
    let mut phase = use_signal(|| Phase::Closed);
    let mut histories = use_signal(Vec::<CourseHistory>::new);
    let open = !matches!(phase(), Phase::Closed);
    use_effect(move || {
        let open = !matches!(phase(), Phase::Closed);
        document::eval(if open { "const d=document.getElementById('account-reset-dialog');if(d&&!d.open)d.showModal();" } else { "document.getElementById('account-reset-dialog')?.close()" });
    });
    let load = {
        let (github, user, repositories) = (github.clone(), user.clone(), repositories.clone());
        move || {
            let (github, user, repositories) = (github.clone(), user.clone(), repositories.clone());
            phase.set(Phase::Loading);
            let user_id = user.id;
            spawn(async move {
                // Read GitHub first: a lesson whose history is only on another device must be planned
                // too. If it cannot be read, nothing is changed.
                let loaded = github_player::background(move || {
                    let mut all = Vec::new();
                    for repository in &repositories {
                        let manifest = github.installed_course(repository)?;
                        github.issues(repository, &user).map_err(|e| format!("「{}」의 GitHub 진도 기록을 읽지 못했어요. {e}", manifest.title))?;
                        let events = github.refresh_course_events(repository, &user, &manifest.id)?;
                        all.push(CourseHistory { manifest, events });
                    }
                    Ok(all)
                }).await;
                match loaded {
                    Ok(all) => { let plan = progress_reset::plan(user_id, &all); histories.set(all); phase.set(Phase::Ready(plan)); }
                    Err(error) => phase.set(Phase::Failed(format!("{error} 아무것도 바꾸지 않았어요. 연결과 gh 로그인을 확인한 뒤 다시 열어 보세요."))),
                }
            });
        }
    };
    let apply = {
        let (github, user) = (github.clone(), user.clone());
        move |plan: Plan| {
            let (github, user) = (github.clone(), user.clone());
            let known = histories();
            phase.set(Phase::Saving);
            spawn(async move {
                let recording = molip_quest::progress_sync::record_guard();
                let (courses, lessons) = (plan.course_count(), plan.lesson_count());
                let result = github_player::background(move || {
                    let _recording = recording;
                    // The latest local history, so events saved while the dialog was open are voided too.
                    let fresh: Vec<CourseHistory> = known.into_iter().map(|h| {
                        let events = github.course_events(&h.manifest.repository, &user, &h.manifest.id).unwrap_or(h.events);
                        CourseHistory { manifest: h.manifest, events }
                    }).collect();
                    Ok(progress_reset::apply(user.id, &plan, &fresh, |repository, title, event| {
                        let latest = github.record(repository, &user, title, event, &[])?;
                        molip_quest::progress_overlay::shared().remember(repository, &latest);
                        Ok(())
                    }))
                }).await;
                phase.set(match result {
                    Ok(Ok(_)) => Phase::Done(format!("과정 {courses}개 · 수업 {lessons}개의 진도를 초기화했어요. 작성한 코드와 실습 폴더는 그대로예요.")),
                    Ok(Err((saved, error))) => Phase::Failed(format!("수업 {saved}개까지 초기화하고 멈췄어요. {error} 다시 열면 남은 수업만 초기화해요.")),
                    Err(error) => Phase::Failed(error),
                });
                onreset.call(());
            });
        }
    };
    // The account name, read once: the dialog sentence names whose progress this is.
    // A formatted text node here rendered "@{user.login}" literally (rsx left it uninterpolated), so the name is an expression child.
    let login = format!("@{}", user.login);
    // Only the confirmation of a real plan is the destructive moment; loading, empty, done and errors are status.
    let danger = matches!(phase(), Phase::Ready(ref plan) if !plan.is_empty());
    rsx! {
        button {r#type:"button",class:"account-reset-open",title:"이 계정의 모든 과정 진도를 처음부터 다시 세요. 수업 하나는 수업의 학습 정보에서 초기화해요.",disabled:disabled||open,
            onclick:{let mut load=load.clone();move |_|load()},"진도 초기화"}
        if open {
        dialog {id:"account-reset-dialog",class:"lesson-info-dialog account-reset-dialog",aria_labelledby:"account-reset-title",
            onkeydown:move |event|{if event.key()==Key::Escape && !matches!(phase(),Phase::Saving){phase.set(Phase::Closed);}},
            // Esc closes a modal dialog even when focus is outside it: the state follows, and a reset in
            // progress keeps its dialog (otherwise the opener stayed disabled with no dialog on screen).
            oncancel:move |event|{if matches!(phase(),Phase::Saving){event.prevent_default();}else{phase.set(Phase::Closed);}},
            header {h2 {id:"account-reset-title","내 전체 학습 진도 초기화"}
                button {r#type:"button",autofocus:true,disabled:matches!(phase(),Phase::Saving),onclick:move |_|phase.set(Phase::Closed),"닫기"}}
            p {class:"account-reset-intro","계정 "strong {{login.clone()}}"이 이 플레이어에 설치한 모든 과정의 진도를 처음부터 다시 세요. 수업 하나만 다시 세려면 수업의 학습 정보에서 「이 수업 진도 초기화」를 쓰세요."}
            section {class:"lesson-reset account-reset","data-danger":"{danger}",
                match phase() {
                    Phase::Loading => rsx!{p {role:"status","설치한 과정과 진도 기록을 확인하고 있어요."}},
                    Phase::Saving => rsx!{p {role:"status","진도를 초기화하고 있어요. 창을 닫지 마세요."}},
                    Phase::Done(text) => rsx!{p {class:"lesson-reset-status",role:"status","{text}"}},
                    Phase::Failed(text) => rsx!{p {class:"lesson-reset-status account-reset-error",role:"alert","{text}"}},
                    Phase::Ready(plan) if plan.is_empty() => rsx!{p {role:"status","초기화할 진도가 없어요. 설치한 과정 {plan.courses.len()}개에 이 계정의 기록이 없어요."}},
                    Phase::Ready(plan) => rsx!{
                        ul {class:"account-reset-scope",
                            for course in plan.courses.iter() {
                                li {key:"{course.repository}",strong {"{course.title}"}" · 기록 있는 수업 {course.lessons.len()} / 전체 {course.lessons_total}"}
                            }
                        }
                        p {class:"lesson-reset-question",strong {"과정 {plan.course_count()}개 · 수업 {plan.lesson_count()}개"}"의 진도를 처음부터 다시 셀까요?"}
                        ul {class:"account-reset-effects",
                            li {"통과한 문제, 수업 완료, 도전 클리어, 열람·실행 기록을 더 이상 세지 않아요."}
                            li {"원래 기록은 지우지 않아요. 이 기기의 저장소와 GitHub 진도 이슈에 그대로 남고, 그 뒤에 초기화 기록을 더해요."}
                            li {"작성한 코드 초안, 실습 폴더, 앱 설정, 다른 계정의 진도는 그대로예요."}
                        }
                        div {class:"lesson-reset-actions",
                            button {r#type:"button",class:"danger account-reset-confirm",onclick:{let mut apply=apply.clone();let plan=plan.clone();move |_|apply(plan.clone())},"전체 진도 초기화"}
                            button {r#type:"button",onmounted:move |event|async move{let _=event.data().set_focus(true).await;},onclick:move |_|phase.set(Phase::Closed),"취소"}
                        }
                    },
                    Phase::Closed => rsx!{},
                }
            }
        }
        }
    }
}
