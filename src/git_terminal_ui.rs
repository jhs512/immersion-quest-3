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
pub struct TerminalControl {owned:Arc<Mutex<Option<TerminalSession>>>,owner:String}
impl TerminalControl {
    pub fn clear_graph(&self) {document::eval(&format!("window.mq3GitGraphs?.reset('{}');",self.owner));}
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
    let mut restored_start=use_signal(||false);
    let owner=use_hook(molip_quest::issue_progress::new_id);
    let cleanup_owner=owner.clone();
    let rendered_owner=owner.clone();
    let is_shell=exercise.shell.is_some();
    let is_java=exercise.java_build.is_some();
    let mut java_source=use_signal(||None::<String>);
    let is_vim=exercise.vim.is_some();
    let is_docker=exercise.docker.is_some();
    // A Compose step: the files of the terminal's folder in an editor above the terminal.
    let is_compose=exercise.docker.as_ref().is_some_and(|d|d.compose.is_some());
    let is_gitlab=exercise.gitlab.is_some();
    let has_editors=is_compose||exercise.gitlab.as_ref().is_some_and(|g|!g.editable.is_empty());
    let mut editor_files=use_signal(Vec::<(String,String)>::new);
    let mut editor_tab=use_signal(||0usize);
    let mut editor_version=use_signal(||0u64);
    let disk_known=use_hook(||Arc::new(Mutex::new(std::collections::BTreeMap::<String,String>::new())));
    let save_known=disk_known.clone();
    // Docker CLI steps reach the lesson's own Docker project, which outlives this terminal.
    let docker_session=try_use_context::<molip_quest::docker_lab::LessonSession>();
    let gitlab_session=try_use_context::<molip_quest::git_practice::GitlabLessonSession>();
    let mut docker_note=use_signal(||None::<String>);
    // Starting Docker Desktop or pulling a prepared image can take a while before the prompt.
    let mut docker_preparing=use_signal(move||is_docker||is_gitlab);
    let graph_enabled=!is_shell&&!is_java&&!is_vim;
    let graph_requested=use_hook(||Arc::new(std::sync::atomic::AtomicBool::new(true)));
    let graph_request=graph_requested.clone();
    let initial_checks=exercise.vim.as_ref().map(|v|v.checks.iter().map(|c|(c.label.clone(),false)).collect()).unwrap_or_default();
    let mut vim_live=use_signal(move||molip_quest::git_practice::VimProgress{checks:initial_checks,..Default::default()});
    let host=if demo{"git-demo-terminal"}else{"git-student-terminal"};
    let bridge_name=if demo{"mq3GitDemoTerminal"}else{"mq3GitTerminal"};
    let cleanup=owned.clone();
    let edit_owned=owned.clone();
    use_drop(move||{
        cleanup.lock().unwrap_or_else(|e|e.into_inner()).take();
        document::eval(&format!("window.{bridge_name}?.dispose('{cleanup_owner}');window.mq3GitGraphs?.dispose('{cleanup_owner}');window.molipAgent?.retireGitTutor('{cleanup_owner}');"));
    });
    use_future(move||{let exercise=exercise.clone();let scope=scope.clone();let step_id=step_id.clone();let owned=owned.clone();let owner=owner.clone();let graph_requested=graph_requested.clone();let docker_session=docker_session.clone();let disk_known=disk_known.clone();let gitlab_session=gitlab_session.clone();async move {
        if is_gitlab {if let Some(session)=gitlab_session{session.activate();}}
        let docker_step=exercise.shell.as_ref().map(|s|s.step_id.clone()).unwrap_or_default();
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
            // Release the practice lock before the branches below take it again (an if-let
            // scrutinee's guard would otherwise live through the block and deadlock this thread).
            let docker=practice.lock().unwrap_or_else(|e|e.into_inner()).exercise_docker();
            let (shell,output,note)=if let Some(docker)=docker {
                let session=docker_session.ok_or("Docker 실습은 수업 화면에서 열어요.")?;
                let lab=session.terminal(demo,&docker_step,&docker)?;
                let (shell,output)=practice.lock().unwrap_or_else(|e|e.into_inner()).open_docker_terminal(&lab)?;
                (shell,output,lab.prepared)
            }else{let (shell,output)=practice.lock().unwrap_or_else(|e|e.into_inner()).open_terminal()?;(shell,output,None)};
            let closing_marker=practice.lock().unwrap_or_else(|e|e.into_inner()).vim_closing_marker();
            Ok::<_,String>((TerminalSession{shell:Some(shell),practice,closing_marker},output,note))
        }).await;
        docker_preparing.set(false);
        let (session,mut output,note)=match opened {Ok(Ok(opened))=>opened,Ok(Err(e))=>{error.set(e);return;},Err(e)=>{error.set(e.to_string());return;}};
        if !demo {docker_note.set(note);}
        let practice=session.practice.clone();
        restored_start.set(!demo&&practice.lock().unwrap_or_else(|e|e.into_inner()).restored_step_start());
        if is_java {let source=practice.lock().unwrap_or_else(|e|e.into_inner()).java_source();match source{Ok(source)=>java_source.set(Some(source)),Err(e)=>error.set(e)}}
        if has_editors {
            let files={let p=practice.lock().unwrap_or_else(|e|e.into_inner());p.editable_files().into_iter().map(|name|{let text=p.read_editable(&name).unwrap_or_default();(name,text)}).collect::<Vec<_>>()};
            *disk_known.lock().unwrap_or_else(|e|e.into_inner())=files.iter().cloned().collect();
            editor_files.set(files);
            // The terminal may change a file too (vim, echo >>). The editor then shows the real file.
            let (sync_practice,sync_owned,known)=(practice.clone(),owned.clone(),disk_known.clone());
            spawn(async move {
                loop {
                    tokio::time::sleep(std::time::Duration::from_millis(500)).await;
                    if sync_owned.lock().unwrap_or_else(|e|e.into_inner()).is_none(){break}
                    // Read and compare under the practice lock, the same lock the editor saves and
                    // records under: the editor's own keystroke is never mistaken for an outside
                    // change (which reset the editor to the file one keystroke behind).
                    let (source,record)=(sync_practice.clone(),known.clone());
                    let Ok(changed)=tokio::task::spawn_blocking(move||{
                        let p=source.lock().unwrap_or_else(|e|e.into_inner());
                        let mut known=record.lock().unwrap_or_else(|e|e.into_inner());
                        let mut changed=false;
                        for name in p.editable_files() {if let Ok(text)=p.read_editable(&name){if known.get(&name)!=Some(&text){known.insert(name,text);changed=true;}}}
                        changed.then(||known.clone())
                    }).await else{continue};
                    if let Some(known)=changed {
                        let next=editor_files.peek().iter().map(|(name,text)|(name.clone(),known.get(name).cloned().unwrap_or_else(||text.clone()))).collect();
                        editor_files.set(next);editor_version+=1;
                    }
                }
            });
        }
        *owned.lock().unwrap_or_else(|e|e.into_inner())=Some(session);
        oncontrol.call(TerminalControl{owned:owned.clone(),owner:owner.clone()});
        if graph_enabled {
            let graph_practice=practice.clone();let graph_owned=owned.clone();let graph_owner=owner.clone();let graph_requested=graph_requested.clone();
            spawn(async move {
                let mut previous_trace=None;let mut last=String::new();
                while graph_owned.lock().unwrap_or_else(|e|e.into_inner()).is_some() {
                    let source=graph_practice.clone();
                    let requested=graph_requested.swap(false,std::sync::atomic::Ordering::Relaxed);
                    let prior=previous_trace;
                    let result=tokio::task::spawn_blocking(move||{
                        let practice=source.lock().unwrap_or_else(|e|e.into_inner());
                        let trace=std::fs::metadata(practice.root().join("commands.jsonl")).ok().map(|m|(m.len(),m.modified().ok()));
                        let snapshot=if requested||trace!=prior {Some(practice.graph_snapshot())}else{None};
                        (trace,snapshot)
                    }).await;
                    if let Ok((trace,Some(result)))=result {
                        previous_trace=trace;
                        let (snapshot,message)=match result {Ok(state)=>(state,String::new()),Err(message)=>(Default::default(),message)};
                        let raw=serde_json::to_string(&(snapshot,message)).unwrap();
                        if requested||raw!=last {
                            last=raw.clone();
                            document::eval(&format!("{{const [snapshot,error]={raw};window.mq3GitGraphs?.update('{graph_owner}',snapshot,error);}}"));
                        }
                    }
                    tokio::time::sleep(std::time::Duration::from_millis(350)).await;
                }
            });
        }
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
            "window.molipGitTutor={next:0,pending:new Map(),command(args){return new Promise(resolve=>{const token=++this.next;this.pending.set(token,resolve);dioxus.send({kind:'command',args,token});});},graph(){return new Promise(resolve=>{const token=++this.next;this.pending.set(token,resolve);dioxus.send({kind:'graph',token});});},resolve(token,value){this.pending.get(token)?.(value);this.pending.delete(token);},dispose(){for(const resolve of this.pending.values())resolve(false);this.pending.clear();}};"
        }else{""});
        let script=script.replace("window.molipGitTutor={next:",&format!("window.molipGitTutor={{owner:'{owner}',next:"));
        let command_owner=owner.clone();
        let mut bridge=document::eval(&script);let input_owned=owned.clone();let command_practice=practice.clone();
        spawn(async move {while let Ok(event)=bridge.recv::<Input>().await {
            if is_compose&&event.kind=="input"&&event.data.contains('\r') {
                // Record the files for this command and refresh the verdict the docker compose guard reads.
                let source=command_practice.clone();
                match tokio::task::spawn_blocking(move||source.lock().unwrap_or_else(|e|e.into_inner()).refresh_docker_files()).await {Ok(Err(e))=>error.set(e),Err(e)=>error.set(e.to_string()),_=>{}}
            }
            if event.kind=="prediction_required"{error.set("실행 결과를 먼저 예상해 보기를 고르세요. 선택한 뒤 Enter로 실행할 수 있어요.".into());continue;}
            if event.kind=="startup_error" {error.set("터미널을 준비하지 못했어요. 초기화해 다시 여세요.".into());continue;}
            // Replay state that may have arrived before xterm mounted. This is a
            // one-time handshake, not a continuous stream of unchanged UI state.
            if event.kind=="mounted" {if graph_enabled{graph_requested.store(true,std::sync::atomic::Ordering::Relaxed);}if is_vim {document::eval(&format!("window.{bridge_name}?.updateVimState({},'{command_owner}')",serde_json::to_string(&*vim_live.peek()).unwrap()));}continue;}
            if event.kind=="ready" {onready.call(command_practice.clone());if is_vim {document::eval(&format!("window.{bridge_name}?.updateVimState({},'{command_owner}')",serde_json::to_string(&*vim_live.peek()).unwrap()));}continue;}
            if event.kind=="graph"&&demo {
                let source=command_practice.clone();let graph_owner=command_owner.clone();
                spawn(async move {
                    let result=tokio::task::spawn_blocking(move||source.lock().unwrap_or_else(|e|e.into_inner()).graph_snapshot()).await;
                    let (snapshot,ready)=match result {Ok(Ok(snapshot))=>(serde_json::to_string(&snapshot).unwrap(),true),_=>{("null".into(),false)}};
                    document::eval(&format!("if(window.molipGitTutor?.owner==='{graph_owner}'){{if({ready})window.mq3GitGraphs?.update('{graph_owner}',{snapshot});window.molipGitTutor.resolve({},{ready});}}",event.token));
                });continue;
            }
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
    let selected=editor_files().get(editor_tab()).cloned();
    rsx!{div {class:if is_java{"git-terminal-shell java-build-workspace"}else if has_editors{"git-terminal-shell java-build-workspace compose-workspace"}else{"git-terminal-shell"},
        if is_gitlab&&!demo {p {class:"practice-start-notice",role:"status",if docker_preparing(){"로컬 GitLab을 준비하고 있어요. 최초 실행에는 몇 분 걸릴 수 있어요."}else{"로컬 GitLab · 실습 계정 자동 연결"}}}
        if restored_start() {p {class:"practice-start-notice",role:"status","앞 단계의 파일과 Git 상태를 준비했어요. 현재 문제의 작업은 직접 진행하세요."}}
        if is_docker {div {class:"docker-notes",
            if docker_preparing()&&!demo {p {class:"practice-start-notice",role:"status","Docker를 준비하고 있어요. 꺼져 있으면 자동으로 켜요."}}
            if let Some(note)=docker_note() {p {class:"practice-start-notice",role:"status","{note} 현재 문제의 명령은 직접 입력하세요."}}
            if !demo {p {class:"docker-terminal-note",role:"note",if is_compose{"위 파일은 터미널의 현재 폴더에 바로 저장돼요. docker compose는 이 폴더의 파일을 이 문제만의 이름으로 실행하고, 앱이 먼저 확인한 파일만 실행해요. 수업을 나가면 이 수업이 만든 것만 정리해요."}else{"입력한 docker 명령은 이 컴퓨터의 실제 Docker가 실행해요. 이 수업이 만든 컨테이너에는 소유 라벨을 붙이고, 다른 컨테이너·이미지를 바꾸거나 지우는 명령은 막아요. 수업을 나가면 이 수업이 만든 것만 정리해요."}}}
        }}
        if let Some((name,text))=selected {
            div {class:"java-build-source compose-source",
                div {class:"editor-file-tabs",role:"tablist",aria_label:"고칠 파일",
                    for (index,(file,_)) in editor_files().into_iter().enumerate() {
                        button {r#type:"button",role:"tab","data-editor-tab":file.clone(),aria_selected:(index==editor_tab()).to_string(),onclick:move |_|editor_tab.set(index),"{file}"}
                    }
                    span {class:"editor-file-note","터미널 폴더에 자동 저장"}
                }
                textarea {class:"code-editor","data-code-editor":editor_language(&name),"data-compose-editor":rendered_owner.clone(),"data-editor-file":name.clone(),"data-editor-value":text.clone(),"data-editor-reset":format!("{rendered_owner}:{name}:{}",editor_version()),initial_value:text,aria_label:format!("실습 {name}"),spellcheck:false,
                    oninput:{let name=name.clone();let owned=edit_owned.clone();let known=save_known.clone();move |event:FormEvent|{
                        let value=event.value().replace("\r\n","\n");
                        // Save and record as one step under the practice lock (see the disk poll).
                        if let Some(session)=owned.lock().unwrap_or_else(|e|e.into_inner()).as_ref(){
                            let practice=session.practice.lock().unwrap_or_else(|e|e.into_inner());
                            if let Err(e)=practice.save_editable(&name,&value){error.set(e);return;}
                            known.lock().unwrap_or_else(|e|e.into_inner()).insert(name.clone(),value.clone());
                        }
                        editor_files.with_mut(|files|if let Some(file)=files.iter_mut().find(|(n,_)|*n==name){file.1=value.clone();});
                    }}}
            }
            div {class:"split-handle split-row split-java-source",role:"separator",tabindex:0,aria_label:"에디터와 터미널 높이 조절",aria_orientation:"horizontal",title:"드래그로 높이 조절, 더블 클릭으로 되돌리기"}
        }
        if let Some(source)=java_source() {
            div {class:"java-build-source",strong {"Main.java · 같은 폴더에 자동 저장"}
                textarea {class:"code-editor","data-code-editor":"java","data-java-editor":rendered_owner.clone(),"data-editor-value":source.clone(),"data-editor-reset":rendered_owner.clone(),initial_value:source,aria_label:"실습 Main.java",spellcheck:false,
                    oninput:move |event|{if let Some(session)=edit_owned.lock().unwrap_or_else(|e|e.into_inner()).as_ref(){if let Err(e)=session.practice.lock().unwrap_or_else(|e|e.into_inner()).save_java_source(&event.value()){error.set(e);}}}}
            }
            div {class:"split-handle split-row split-java-source",role:"separator",tabindex:0,aria_label:"에디터와 터미널 높이 조절",aria_orientation:"horizontal",title:"드래그로 높이 조절, 더블 클릭으로 되돌리기"}
        }
        div {class:"git-terminal-row",
        div {class:"git-terminal",id:host,"data-shell":is_shell.to_string(),"data-vim":is_vim.to_string(),"data-terminal-session":rendered_owner.clone(),aria_label:if is_vim{if demo{"해설용 별도 Vim 편집기"}else{"실제 Vim 편집기"}}else if is_docker{if demo{"해설용 별도 Docker 터미널"}else{"실제 Docker 터미널"}}else if is_shell{if demo{"해설용 별도 Bash 실습 폴더"}else{"실제 Bash 실습 폴더"}}else if demo{"해설용 별도 Git 저장소"}else{"실제 Git 실습 저장소"}}
        if graph_enabled {details {class:"git-graph-panel",open:true,"data-git-graph-owner":rendered_owner.clone(),
            summary {"커밋 그래프"}
            div {class:"git-graph-body",
                div {class:"git-graph-tools",
                    button {r#type:"button","data-graph-action":"expand",aria_pressed:"false","크게 보기"}
                    button {r#type:"button","data-graph-action":"focus",title:"배율을 되돌려요. HEAD 커밋을 가운데로 옮겨요.","HEAD로 이동"}
                }
                p {class:"git-graph-status",role:"status","저장소를 확인하고 있어요…"}
                div {class:"git-graph-canvas",role:"img",aria_label:"실제 저장소의 커밋과 브랜치 연결"}
                p {class:"git-graph-detail","점을 누르면 커밋 설명을 볼 수 있어요."}
                button {r#type:"button",onclick:move |_|graph_request.store(true,std::sync::atomic::Ordering::Relaxed),"그래프 새로고침"}
            }
        }
        div {class:"split-handle split-col split-git",role:"separator",tabindex:0,aria_label:"터미널과 그래프 너비 조절",aria_orientation:"vertical"}
        }
        }if is_vim {
        section {class:"vim-live-panel",aria_label:"Vim 실시간 확인","data-vim-passed":vim_live().passed.to_string(),
            if let Some(state)=vim_live().state {
                p {class:"vim-current-state",if state.exited{"Vim을 종료했어요."}else{{format!("{} · {}행 {}열 · {}",if state.mode=="i"{"입력 모드"}else if state.mode=="c"{"명령 입력 중"}else{"일반 모드"},state.line,state.column,if state.modified{"저장하지 않은 변경이 있어요"}else{"파일과 같은 상태예요"})}}}
            }else{p {"Vim을 열고 있어요…"}}
            ol {for (label,done) in vim_live().checks {li {class:if done{"confirmed"}else{"pending"},span {aria_hidden:"true",if done{"✓ "}else{"○ "}}"{label}"}}}
            p {class:"vim-goal-status",role:"status",aria_live:"polite",if vim_live().passed{"목표를 확인했어요. 제출 버튼을 누르세요."}}
        }
    }if !error().is_empty(){p {role:"status","{error}"}}}}
}

/// The editor's highlighting for a lesson file.
fn editor_language(name:&str)->&'static str {
    if name.ends_with(".sh"){"shell"}else if name.ends_with(".sql"){"sql"}else if name.ends_with(".yaml")||name.ends_with(".yml"){"yaml"}else if name=="Dockerfile"{"dockerfile"}else{"text"}
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
