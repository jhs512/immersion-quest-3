use dioxus::prelude::*;
use molip_quest::{git_practice::{GitExercise,GitPractice},setup_terminal::SetupTerminal};
use std::sync::{Arc,Mutex};
pub type Practice=Arc<Mutex<GitPractice>>;
struct TerminalSession {shell:Option<SetupTerminal>,practice:Practice}
impl Drop for TerminalSession {
    fn drop(&mut self){if let Some(mut shell)=self.shell.take(){let practice=self.practice.clone();std::thread::spawn(move||{
        // Keep the owned directory alive until the shell has actually terminated.
        if shell.shutdown().is_err(){std::mem::forget(practice);}drop(shell);
    });}}
}
#[derive(serde::Deserialize)]
struct Input {kind:String,#[serde(default)] data:String,#[serde(default)] rows:u16,#[serde(default)] cols:u16,#[serde(default)] args:Vec<String>,#[serde(default)] token:u64}
fn shell_quote(value:&str)->String {if cfg!(windows){format!("'{}'",value.replace('\'',"''"))}else{format!("'{}'",value.replace('\'',"'\\''"))}}
#[component]
pub fn GitTerminal(exercise:GitExercise,demo:bool,onready:EventHandler<Practice>)->Element {
    use base64::Engine;
    let owned=use_hook(||Arc::new(Mutex::new(None::<TerminalSession>)));
    let mut error=use_signal(String::new);
    let owner=use_hook(molip_quest::issue_progress::new_id);
    let cleanup_owner=owner.clone();
    let host=if demo{"git-demo-terminal"}else{"git-student-terminal"};
    let bridge_name=if demo{"mq3GitDemoTerminal"}else{"mq3GitTerminal"};
    let cleanup=owned.clone();
    use_drop(move||{
        cleanup.lock().unwrap_or_else(|e|e.into_inner()).take();
        document::eval(&format!("window.{bridge_name}?.dispose('{cleanup_owner}');if(window.molipGitTutor?.owner==='{cleanup_owner}')window.molipGitTutor.dispose();"));
    });
    use_future(move||{let exercise=exercise.clone();let owned=owned.clone();let owner=owner.clone();async move {
        let opened=tokio::task::spawn_blocking(move||{
            let practice=Arc::new(Mutex::new(GitPractice::new(exercise)?));
            let (shell,output)=practice.lock().unwrap_or_else(|e|e.into_inner()).open_terminal()?;
            Ok::<_,String>((TerminalSession{shell:Some(shell),practice},output))
        }).await;
        let (session,mut output)=match opened {Ok(Ok(pair))=>pair,Ok(Err(e))=>{error.set(e);return;},Err(e)=>{error.set(e.to_string());return;}};
        let practice=session.practice.clone();
        *owned.lock().unwrap_or_else(|e|e.into_inner())=Some(session);
        let prompt=if cfg!(windows){"PS "}else{"$ "};
        let script=format!("(async()=>{{window.{bridge_name}.mount(event=>dioxus.send(event),()=>{{}},'{owner}');const deadline=Date.now()+15000;while(!window.{bridge_name}.text('{owner}').includes('{prompt}')){{if(Date.now()>deadline)return;await new Promise(resolve=>setTimeout(resolve,30));}}dioxus.send({{kind:'ready'}});{}}})()",if demo {
            "window.molipGitTutor={next:0,pending:new Map(),command(args){return new Promise(resolve=>{const token=++this.next;this.pending.set(token,resolve);dioxus.send({kind:'command',args,token});});},resolve(token,value){this.pending.get(token)?.(value);this.pending.delete(token);},dispose(){for(const resolve of this.pending.values())resolve(false);this.pending.clear();}};"
        }else{""});
        let script=script.replace("window.molipGitTutor={next:",&format!("window.molipGitTutor={{owner:'{owner}',next:"));
        let command_owner=owner.clone();
        let mut bridge=document::eval(&script);let input_owned=owned.clone();let command_practice=practice.clone();
        spawn(async move {while let Ok(event)=bridge.recv::<Input>().await {
            if event.kind=="ready" {onready.call(command_practice.clone());continue;}
            if event.kind=="command"&&demo {
                if event.args.is_empty()||event.args.len()>50||event.args.iter().any(|arg|arg.len()>4000){continue;}
                let practice=command_practice.clone();let command_owner=command_owner.clone();
                let before=practice.lock().unwrap_or_else(|e|e.into_inner()).completed_commands().map(|items|items.len()).unwrap_or(usize::MAX);
                let command=format!("git {}",event.args.iter().map(|arg|shell_quote(arg)).collect::<Vec<_>>().join(" "));
                document::eval(&format!("window.mq3GitDemoTerminal?.typeCommand({},'{command_owner}');",serde_json::to_string(&command).unwrap()));
                spawn(async move {
                    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(15);
                    let mut completed=false;
                    while std::time::Instant::now()<deadline {
                        completed=practice.lock().unwrap_or_else(|e|e.into_inner()).completed_commands().is_ok_and(|items|items.iter().skip(before).any(|args|*args==event.args));
                        if completed {break;}tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                    }
                    document::eval(&format!("if(window.molipGitTutor?.owner==='{command_owner}')window.molipGitTutor.resolve({},{});",event.token,completed));
                });
            }else{
                let mut guard=input_owned.lock().unwrap_or_else(|e|e.into_inner());let Some(session)=guard.as_mut() else{break};let Some(shell)=session.shell.as_mut() else{break};
                match event.kind.as_str(){"input"=>{let _=shell.input(&event.data);},"resize"=>{let _=shell.resize(event.rows,event.cols);},_=>{}}
            }
        }});
        while let Some(bytes)=output.recv().await {let encoded=base64::engine::general_purpose::STANDARD.encode(bytes);document::eval(&format!("window.{bridge_name}?.write('{encoded}','{owner}')"));}
    }});
    rsx!{div {class:"git-terminal",id:host,aria_label:if demo{"해설용 별도 Git 저장소"}else{"실제 Git 실습 저장소"}}p {role:"status","{error}"}}
}
