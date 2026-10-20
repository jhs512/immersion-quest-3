use dioxus::prelude::*;
use molip_quest::{git_practice::{GitExercise,GitPractice},setup_terminal::SetupTerminal};
use std::sync::{Arc,Mutex};
pub type Practice=Arc<Mutex<GitPractice>>;
struct TerminalSession {shell:Option<SetupTerminal>,practice:Practice,closing_marker:Option<std::path::PathBuf>}
impl Drop for TerminalSession {
    fn drop(&mut self){if let Some(path)=&self.closing_marker{let _=std::fs::write(path,"");}if let Some(mut shell)=self.shell.take(){let practice=self.practice.clone();std::thread::spawn(move||{
        // Keep the owned directory alive until the shell has actually terminated.
        if shell.shutdown().is_err(){std::mem::forget(practice);}drop(shell);
    });}}
}
#[derive(Clone)]
pub struct TerminalControl {owned:Arc<Mutex<Option<TerminalSession>>>}
impl TerminalControl {
    pub fn shutdown(&self)->Result<(),String> {
        let mut guard=self.owned.lock().unwrap_or_else(|e|e.into_inner());
        if let Some(session)=guard.as_mut(){if let Some(path)=&session.closing_marker{let _=std::fs::write(path,"");}if let Some(shell)=session.shell.as_mut(){shell.shutdown()?;}}
        guard.take();Ok(())
    }
}
#[derive(serde::Deserialize)]
struct Input {kind:String,#[serde(default)] data:String,#[serde(default)] rows:u16,#[serde(default)] cols:u16,#[serde(default)] source:Option<String>,#[serde(default)] args:Vec<String>,#[serde(default)] token:u64}
fn shell_argument(value:&str)->String {
    if !value.is_empty() && value.chars().all(|c|c.is_alphanumeric()||"_./:=+@%^-".contains(c)) {
        return value.to_owned();
    }
    let escaped=value.replace('\\',"\\\\").replace('$',"\\$").replace('`',"\\`").replace('"',"\\\"");
    format!("\"{escaped}\"")
}
#[component]
pub fn GitTerminal(exercise:GitExercise,demo:bool,#[props(default)] scope:Option<String>,#[props(default)] fresh:bool,#[props(default)] step_id:String,onready:EventHandler<Practice>,oncontrol:EventHandler<TerminalControl>)->Element {
    use base64::Engine;
    let owned=use_hook(||Arc::new(Mutex::new(None::<TerminalSession>)));
    let mut error=use_signal(String::new);
    let owner=use_hook(molip_quest::issue_progress::new_id);
    let cleanup_owner=owner.clone();
    let rendered_owner=owner.clone();
    let is_shell=exercise.shell.is_some();
    let is_java=exercise.java_build.is_some();
    let mut java_source=use_signal(||None::<String>);
    let is_vim=exercise.vim.is_some();
    let initial_checks=exercise.vim.as_ref().map(|v|v.checks.iter().map(|c|(c.label.clone(),false)).collect()).unwrap_or_default();
    let mut vim_live=use_signal(move||molip_quest::git_practice::VimProgress{checks:initial_checks,..Default::default()});
    let host=if demo{"git-demo-terminal"}else{"git-student-terminal"};
    let bridge_name=if demo{"mq3GitDemoTerminal"}else{"mq3GitTerminal"};
    let cleanup=owned.clone();
    let edit_owned=owned.clone();
    use_drop(move||{
        cleanup.lock().unwrap_or_else(|e|e.into_inner()).take();
        document::eval(&format!("window.{bridge_name}?.dispose('{cleanup_owner}');window.molipAgent?.retireGitTutor('{cleanup_owner}');"));
    });
    use_future(move||{let exercise=exercise.clone();let scope=scope.clone();let step_id=step_id.clone();let owned=owned.clone();let owner=owner.clone();async move {
        let opened=tokio::task::spawn_blocking(move||{
            let practice=if !demo {
                if let Some(scope)=scope {
                    let scope=exercise.workspace_scope(&scope);
                    let store=molip_quest::git_practice::GitPracticeStore::installed()?;
                    if fresh {store.reset_step(&scope,exercise,&step_id)?}else{store.open(&scope,exercise)?}
                }else{GitPractice::new(exercise)?}
            }else{GitPractice::new(exercise.demonstration())?};
            if !demo {practice.remember_step_start(&step_id)?;}
            let practice=Arc::new(Mutex::new(practice));
            let (shell,output)=practice.lock().unwrap_or_else(|e|e.into_inner()).open_terminal()?;
            let closing_marker=practice.lock().unwrap_or_else(|e|e.into_inner()).vim_closing_marker();
            Ok::<_,String>((TerminalSession{shell:Some(shell),practice,closing_marker},output))
        }).await;
        let (session,mut output)=match opened {Ok(Ok(pair))=>pair,Ok(Err(e))=>{error.set(e);return;},Err(e)=>{error.set(e.to_string());return;}};
        let practice=session.practice.clone();
        if is_java {let source=practice.lock().unwrap_or_else(|e|e.into_inner()).java_source();match source{Ok(source)=>java_source.set(Some(source)),Err(e)=>error.set(e)}}
        *owned.lock().unwrap_or_else(|e|e.into_inner())=Some(session);
        oncontrol.call(TerminalControl{owned:owned.clone()});
        if is_vim {
            let live_practice=practice.clone();let live_owned=owned.clone();let live_owner=owner.clone();
            spawn(async move {
                let mut last=String::new();
                while live_owned.lock().unwrap_or_else(|e|e.into_inner()).is_some() {
                    let source=live_practice.clone();
                    if let Ok(Ok(progress))=tokio::task::spawn_blocking(move||source.lock().unwrap_or_else(|e|e.into_inner()).vim_progress()).await {
                        let raw=serde_json::to_string(&progress).unwrap();
                        if raw!=last {last=raw.clone();vim_live.set(progress.clone());document::eval(&format!("window.{bridge_name}?.updateVimState({raw},'{live_owner}')"));}
                    }
                    tokio::time::sleep(std::time::Duration::from_millis(80)).await;
                }
            });
        }
        // A redraw can erase Vim's filename message. Its actual session state is
        // the readiness signal; shell exercises still wait for their prompt.
        let ready=if is_vim {format!("window.{bridge_name}.vimState('{owner}')?.state")}else{format!("window.{bridge_name}.text('{owner}').split('\\n').some(line=>line.trimEnd().endsWith('$'))")};
        let gate=if is_java&&!demo{"document.querySelector('.repository-task')?.dataset.predictBeforeRun==='true'"}else{"false"};
        let script=format!("(async()=>{{window.{bridge_name}.mount(event=>{{if(event.kind==='input'&&event.data.includes('\\r')){{event.source=document.querySelector('[data-java-editor=\"{owner}\"]')?.value;if({gate}&&!document.querySelector('.repository-task input[type=radio]:checked')){{const pending=event.data.replaceAll('\\r','');if(pending)dioxus.send({{...event,data:pending}});dioxus.send({{kind:'prediction_required'}});return;}}}}dioxus.send(event)}},()=>{{}},'{owner}');dioxus.send({{kind:'mounted'}});const deadline=Date.now()+45000;while(!({ready})){{if(Date.now()>deadline){{dioxus.send({{kind:'startup_error'}});return;}}await new Promise(resolve=>setTimeout(resolve,30));}}dioxus.send({{kind:'ready'}});{}}})()",if demo {
            "window.molipGitTutor={next:0,pending:new Map(),command(args){return new Promise(resolve=>{const token=++this.next;this.pending.set(token,resolve);dioxus.send({kind:'command',args,token});});},resolve(token,value){this.pending.get(token)?.(value);this.pending.delete(token);},dispose(){for(const resolve of this.pending.values())resolve(false);this.pending.clear();}};"
        }else{""});
        let script=script.replace("window.molipGitTutor={next:",&format!("window.molipGitTutor={{owner:'{owner}',next:"));
        let command_owner=owner.clone();
        let mut bridge=document::eval(&script);let input_owned=owned.clone();let command_practice=practice.clone();
        spawn(async move {while let Ok(event)=bridge.recv::<Input>().await {
            if event.kind=="prediction_required"{error.set("실행 결과를 먼저 예상해 보기를 고르세요. 선택한 뒤 Enter로 실행할 수 있어요.".into());continue;}
            if event.kind=="startup_error" {error.set("터미널을 준비하지 못했어요. 초기화해 다시 여세요.".into());continue;}
            // Replay state that may have arrived before xterm mounted. This is a
            // one-time handshake, not a continuous stream of unchanged UI state.
            if event.kind=="mounted" {if is_vim {document::eval(&format!("window.{bridge_name}?.updateVimState({},'{command_owner}')",serde_json::to_string(&*vim_live.peek()).unwrap()));}continue;}
            if event.kind=="ready" {onready.call(command_practice.clone());if is_vim {document::eval(&format!("window.{bridge_name}?.updateVimState({},'{command_owner}')",serde_json::to_string(&*vim_live.peek()).unwrap()));}continue;}
            if event.kind=="command"&&demo {
                if event.args.is_empty()||event.args.len()>50||event.args.iter().any(|arg|arg.len()>4000){continue;}
                let practice=command_practice.clone();let command_owner=command_owner.clone();
                let before=practice.lock().unwrap_or_else(|e|e.into_inner()).completed_commands().map(|items|items.len()).unwrap_or(usize::MAX);
                let command=format!("git {}",event.args.iter().map(|arg|shell_argument(arg)).collect::<Vec<_>>().join(" "));
                let mut typing=document::eval(&format!("(async()=>{{const typed=await window.mq3GitDemoTerminal?.typeCommand({},'{command_owner}');dioxus.send(typed===true);}})()",serde_json::to_string(&command).unwrap()));
                spawn(async move {
                    // Typing can be throttled while the Mac window is in the
                    // background. Start the execution deadline after Enter.
                    let typed=matches!(tokio::time::timeout(std::time::Duration::from_secs(120),typing.recv::<bool>()).await,Ok(Ok(true)));
                    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(15);
                    let mut completed=false;
                    while typed&&std::time::Instant::now()<deadline {
                        completed=practice.lock().unwrap_or_else(|e|e.into_inner()).completed_commands().is_ok_and(|items|items.iter().skip(before).any(|args|*args==event.args));
                        if completed {break;}tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                    }
                    #[cfg(debug_assertions)]
                    if !completed {
                        let history=practice.lock().unwrap_or_else(|e|e.into_inner()).completed_commands().unwrap_or_default();
                        document::eval(&format!("window.mq3GitDemoFailure={{args:{},history:{},text:window.mq3GitDemoTerminal?.text('{command_owner}')}};",serde_json::to_string(&event.args).unwrap(),serde_json::to_string(&history).unwrap()));
                    }
                    document::eval(&format!("if(window.molipGitTutor?.owner==='{command_owner}')window.molipGitTutor.resolve({},{});",event.token,completed));
                });
            }else{
                let mut guard=input_owned.lock().unwrap_or_else(|e|e.into_inner());let Some(session)=guard.as_mut() else{break};let Some(shell)=session.shell.as_mut() else{break};
                match event.kind.as_str(){"input"=>{let practice=session.practice.lock().unwrap_or_else(|e|e.into_inner());if let Some(source)=event.source{if let Err(e)=practice.save_java_source(&source){error.set(e);continue;}}if event.data.contains('\r'){error.set(String::new());}let _=practice.note_vim_input();let _=shell.input(&event.data);},"resize"=>{let _=shell.resize(event.rows,event.cols);},_=>{}}
            }
        }});
        while let Some(bytes)=output.recv().await {let encoded=base64::engine::general_purpose::STANDARD.encode(bytes);document::eval(&format!("window.{bridge_name}?.write('{encoded}','{owner}')"));}
        if !is_vim{error.set("터미널이 종료됐어요. 초기화해 다시 여세요.".into());}
    }});
    rsx!{div {class:if is_java{"git-terminal-shell java-build-workspace"}else{"git-terminal-shell"},
        if let Some(source)=java_source() {
            div {class:"java-build-source",strong {"Main.java · 같은 폴더에 자동 저장"}
                textarea {class:"code-editor","data-code-editor":"java","data-java-editor":rendered_owner.clone(),"data-editor-value":source.clone(),"data-editor-reset":rendered_owner.clone(),initial_value:source,aria_label:"실습 Main.java",spellcheck:false,
                    oninput:move |event|{if let Some(session)=edit_owned.lock().unwrap_or_else(|e|e.into_inner()).as_ref(){if let Err(e)=session.practice.lock().unwrap_or_else(|e|e.into_inner()).save_java_source(&event.value()){error.set(e);}}}}
            }
        }
        div {class:"git-terminal",id:host,"data-shell":is_shell.to_string(),"data-vim":is_vim.to_string(),"data-terminal-session":rendered_owner,aria_label:if is_vim{if demo{"해설용 별도 Vim 편집기"}else{"실제 Vim 편집기"}}else if is_shell{if demo{"해설용 별도 Bash 실습 폴더"}else{"실제 Bash 실습 폴더"}}else if demo{"해설용 별도 Git 저장소"}else{"실제 Git 실습 저장소"}}if is_vim {
        section {class:"vim-live-panel",aria_label:"Vim 실시간 확인","data-vim-passed":vim_live().passed.to_string(),
            if let Some(state)=vim_live().state {
                p {class:"vim-current-state",if state.exited{"Vim을 종료했어요."}else{{format!("{} · {}행 {}열 · {}",if state.mode=="i"{"입력 모드"}else if state.mode=="c"{"명령 입력 중"}else{"일반 모드"},state.line,state.column,if state.modified{"저장하지 않은 변경이 있어요"}else{"파일과 같은 상태예요"})}}}
            }else{p {"Vim을 열고 있어요…"}}
            ol {for (label,done) in vim_live().checks {li {class:if done{"confirmed"}else{"pending"},span {aria_hidden:"true",if done{"✓ "}else{"○ "}}"{label}"}}}
            p {class:"vim-goal-status",role:"status",aria_live:"polite",if vim_live().passed{"목표를 확인했어요. 제출 버튼을 누르세요."}}
        }
    }if !error().is_empty(){p {role:"status","{error}"}}}}
}

#[cfg(test)]
mod tests {
    use super::shell_argument;
    #[test]
    fn demonstration_uses_familiar_git_command_syntax() {
        let args=["commit","-m","첫 기록"].map(shell_argument).join(" ");
        assert_eq!(format!("git {args}"),"git commit -m \"첫 기록\"");
        assert_eq!(shell_argument("HEAD^:memo.txt"),"HEAD^:memo.txt");
        assert_eq!(shell_argument("메모"),"메모");
        assert_eq!(shell_argument(""),"\"\"");
    }
    #[cfg(unix)]
    #[test]
    fn quoted_messages_reach_bash_literally() {
        let message="첫 기록 \"안녕\" $HOME `echo nope` $(echo nope) \\ '";
        let output=std::process::Command::new("/bin/bash").args(["-c",&format!("printf '%s' {}",shell_argument(message))]).output().unwrap();
        assert!(output.status.success());
        assert_eq!(String::from_utf8(output.stdout).unwrap(),message);
    }
}
