use dioxus::prelude::*;
use molip_quest::{github_player::{self,Github,GithubUser},issue_progress::{self,LearningEvent,ProgressKey,StudyMode,EventKind},repository_course::{self,CourseManifest,Lesson,Task}};
use std::collections::HashMap;

fn merge_local_events(mut target:Signal<Vec<LearningEvent>>,latest:Vec<LearningEvent>){
    if let Some(event)=latest.first(){let key=event.key.clone();target.with_mut(|current|*current=issue_progress::merge(std::mem::take(current).into_iter().chain(latest),&key));}
}

#[derive(Clone,PartialEq)]
struct Session { github:Github,user:GithubUser }
#[derive(Clone,PartialEq)]
struct OpenLesson { course:CourseManifest,lesson:Lesson,events:Vec<LearningEvent>,mode:StudyMode,round:String }

fn prepare_open_lesson(session:Session,manifest:CourseManifest,reference:repository_course::LessonRef,mode:StudyMode,stage:Option<tokio::sync::mpsc::UnboundedSender<u8>>)->Result<OpenLesson,String>{
    let gh=&session.github;let user=&session.user;
    gh.ensure_user(user.id)?;
    let lesson=gh.installed_lesson(&manifest,&reference)?;
    if let Some(tx)=&stage{let _=tx.send(1);}
    let key=ProgressKey{user_id:user.id,course_id:manifest.id.clone(),lesson_id:lesson.id.clone()};
    let issue=gh.find_issue(&manifest.repository,user,&key)?;
    let mut events=if let Some(issue)=&issue{gh.events(&manifest.repository,issue,&key)?}else{vec![]};
    let unfinished=events.iter().rev().find(|e|e.kind==EventKind::Started&&e.mode==mode&&e.revision==lesson.revision&&!events.iter().any(|done|done.kind==EventKind::Completed&&done.round==e.round)).map(|e|e.round.clone());
    let round=unfinished.unwrap_or_else(issue_progress::new_id);
    if let Some(tx)=&stage{let _=tx.send(2);}
    if !events.iter().any(|event|event.round==round){
        let event=LearningEvent::new(key,&lesson.revision,mode,&round,EventKind::Started);
        events=gh.record(&manifest.repository,user,&lesson.title,&event,&[])?;
    }
    Ok(OpenLesson{course:manifest,lesson,events,mode,round})
}

#[component]
pub fn RepositoryPlayer(window_controls:Element)->Element {
    let mut session=use_signal(||None::<Session>);
    let mut course=use_signal(||None::<CourseManifest>);
    let mut open=use_signal(||None::<OpenLesson>);
    let mut message=use_signal(String::new);
    let mut busy=use_signal(||false);
    let mut launching=use_signal(||None::<(String,u8)>);
    let mut identity_scope=use_signal(String::new);
    let mut waiting_name_link=use_signal(||None::<molip_quest::lesson_link::LessonLink>);
    let mut checked=use_signal(||false);
    let repositories=use_signal(molip_quest::course_authoring::catalog);
    let mut course_search=use_signal(String::new);
    let mut course_titles=use_signal(HashMap::<String,String>::new);
    let mut progress=use_signal(HashMap::<String,Vec<LearningEvent>>::new);
    let mut progress_requirements=use_signal(HashMap::<String,Vec<String>>::new);
    let mut refresh=use_signal(||0u64);
    let connect=move ||async move {
        checked.set(false);
        progress.set(HashMap::new());progress_requirements.set(HashMap::new());course.set(None);session.set(None);
        busy.set(true);message.set("GitHub 계정과 코스 콘텐츠를 확인하고 있어요.".into());
        let github=Github::new();let gh=github.clone();
        match github_player::background(move||{
            let user=gh.user()?;
            if !molip_quest::pilot_source::enabled() {
                if let Err(error)=molip_quest::content_lifecycle::synchronize(&gh,user.id) {
                    eprintln!("Content refresh will retry: {error}");
                }
            }
            let manifest=gh.installed_course(repository_course::initial_repository());Ok((user,manifest))
        }).await {
            Ok((user,manifest))=>{let _=molip_quest::course_identity::synchronize(github.clone(),user.clone());let _=molip_quest::progress_sync::synchronize(github.clone(),user.clone());session.set(Some(Session{github,user}));match manifest {Ok(c)=>{course.set(Some(c));message.set(String::new());},Err(e)=>message.set(e)}},
            Err(e)=>{session.set(None);course.set(None);message.set(e);}
        }
        busy.set(false);
        checked.set(true);
    };
    let setup_preview=use_hook(||cfg!(debug_assertions)&&std::env::var_os("MOLIP_GH_SETUP_PREVIEW").is_some());
    use_future(move ||async move {
        if setup_preview {checked.set(true);}else{connect().await;}
    });
    #[cfg(feature="desktop")]
    let link_window=dioxus::desktop::use_window();
    use_future(move||{
        #[cfg(feature="desktop")]
        let link_window=link_window.clone();
        async move {
        let mut focused=false;
        loop {
            if molip_quest::lesson_link::pending()&&!focused {
                #[cfg(feature="desktop")]
                {link_window.window.set_visible(true);link_window.window.set_minimized(false);link_window.window.set_focus();}
                focused=true;
            }
            if !*busy.peek() {
                let connected={session.peek().clone()};
                if let Some(s)=connected {
                    if let Some(request)=molip_quest::lesson_link::take(){
                        focused=false;
                        match request {
                            molip_quest::lesson_link::Request::Focus=>{},
                            molip_quest::lesson_link::Request::Invalid(error)=>{message.set(error.clone());document::eval(&format!("window.molipToast?.({})",serde_json::to_string(&error).unwrap()));},
                            molip_quest::lesson_link::Request::Open(link)=>{
                                busy.set(true);launching.set(Some((if link.lesson.is_some(){"연결된 수업"}else{"연결된 코스"}.into(),0)));
                                let requested=link.clone();
                                let result=github_player::background(move||{
                                    let manifest=s.github.installed_course(&link.course)?;
                                    let visible=molip_quest::course_visibility::for_account(manifest,&s.user.login);
                                    if link.lesson.is_none(){
                                        molip_quest::course_authoring::remember(&link.course)?;
                                        return Ok((visible,None));
                                    }
                                    let reference=link.reference(&visible)?.clone();
                                    let name=molip_quest::course_identity::Store::installed()?.load(&s.github,&visible.repository,&s.user,&visible.id,false)?;
                                    if name.is_none(){return Ok((visible,None));}
                                    let selected=prepare_open_lesson(s,visible.clone(),reference,StudyMode::Full,None)?;
                                    molip_quest::course_authoring::remember(&link.course)?;
                                    Ok((visible,Some(selected)))
                                }).await;
                                match result {Ok((manifest,selected))=>{
                                    document::eval("window.molipAgent?.stop()");molip_quest::bug_report::forget();
                                    course.set(Some(manifest));if let Some(selected)=selected{open.set(Some(selected));message.set(String::new());}else{open.set(None);if requested.lesson.is_some(){waiting_name_link.set(Some(requested));message.set("이 코스에서 쓸 이름을 먼저 입력하세요.".into());}else{waiting_name_link.set(None);message.set(String::new());}}
                                },Err(error)=>{message.set(error.clone());document::eval(&format!("window.molipToast?.({})",serde_json::to_string(&error).unwrap()));}}
                                launching.set(None);busy.set(false);
                            }
                        }
                    }
                }
            }
            tokio::time::sleep(std::time::Duration::from_millis(250)).await;
        }
    }});
    use_effect(move ||{
        let repos=repositories();let Some(s)=session() else{return};
        for repository in repos {
            let github=s.github.clone();
            spawn(async move {let lookup=repository.clone();if let Ok(manifest)=github_player::background(move||github.course(&lookup)).await {course_titles.write().insert(repository,manifest.title);}});
        }
    });
    let update_key=format!("{}:{}",course().map(|course|course.repository).unwrap_or_default(),session().map(|s|s.user.id).unwrap_or(0));
    let updates=rsx! {ContentUpdates {key:"{update_key}",session:session(),course:course(),active_lesson:open,onapply:move |(manifest,automatic):(CourseManifest,bool)|{
        if !automatic {document::eval("window.molipAgent?.stop()");molip_quest::bug_report::forget();open.set(None);}
        course.set(Some(manifest)); refresh+=1;
    }}};
    let visible_course=course().map(|manifest|molip_quest::course_visibility::for_account(
        manifest,&session().map(|s|s.user.login).unwrap_or_default()));
    if let Some(selected)=open() {
        if let Some(session)=session() {
            let player_key=format!("{}:{}:{}:{}:{}",session.user.id,selected.course.id,selected.lesson.id,selected.mode.label(),selected.round);
            return rsx!{div {class:"repository-session", {rsx!{LessonPlayer {key:"{player_key}",session,selected,window_controls,updates,onback:move |_|{document::eval("window.molipAgent?.stop()");molip_quest::bug_report::forget();open.set(None);refresh+=1;}}}} }};
        }
    }
    rsx!{
        div {class:if session().is_none(){"repository-player needs-gh"}else{"repository-player"},
            header {class:"repository-header",h1 {"MQ"}
                div {class:"repository-tools",
                    if let Some(s)=session() {div {class:"repository-account",span {"gh · @{s.user.login}"}button {class:"account-recheck",title:"GitHub 계정 다시 확인",aria_label:"GitHub 계정 다시 확인",disabled:busy(),onclick:move |_|connect(),"계정 확인"}}}
                    button {class:"shortcut-sheet-open","data-shortcut-action":"help",onclick:move |_|{document::eval("window.molipShortcuts?.toggleSheet()");},"단축키"}{updates}{window_controls}
                }
            }
            if session().is_none() {
                crate::gh_setup_ui::GhSetup {message:message(),checking:!checked(),onretry:move |_|{spawn(connect());}}
            } else {
                div {class:"course-shell",
                aside {class:"course-sidebar",aria_label:"과정 목록",
                    h2 {"내 과정"}
                    label {class:"course-search",span {"과정 검색"}input {r#type:"search",placeholder:"이름으로 찾기",value:course_search(),oninput:move |e|course_search.set(e.value())}}
                    nav {class:"course-switcher",aria_label:"과정 선택",
                    for repository in repositories().into_iter().filter(|repo|{let query=course_search().to_lowercase();repo.to_lowercase().contains(&query)||course_titles().get(repo).is_some_and(|title|title.to_lowercase().contains(&query))}) {
                        button {class:if course().is_some_and(|c|c.repository==repository){"course-selected"}else{""},aria_current:if course().is_some_and(|c|c.repository==repository){"page"}else{"false"},disabled:busy(),onclick:{let repository=repository.clone();move |_|{let Some(s)=session() else{return};let gh=s.github.clone();let repository=repository.clone();spawn(async move {busy.set(true);match github_player::background(move||gh.installed_course(&repository)).await {Ok(manifest)=>{let mut span=molip_quest::telemetry::operation("course.open",vec![opentelemetry::KeyValue::new("course.id",manifest.id.clone())]);span.finish("ok");course.set(Some(manifest));message.set(String::new());},Err(e)=>message.set(e)}busy.set(false);});}},
                            strong {{course_titles().get(&repository).cloned().unwrap_or_else(||repository.split('/').next_back().unwrap_or(&repository).replace("mq3-course-", "").replace('-', " "))}}
                            small {"{repository}"}
                        }
                    }
                    if !repositories().iter().any(|repo|{let query=course_search().to_lowercase();repo.to_lowercase().contains(&query)||course_titles().get(repo).is_some_and(|title|title.to_lowercase().contains(&query))}) {div {class:"course-search-empty",role:"status",p {"일치하는 과정이 없어요."}if !course_search().is_empty(){button {onclick:move |_|course_search.set(String::new()),"검색 지우기"}}}}
                    }
                }
                main {class:"course-main",
                if let Some((title,stage))=launching() {LessonLaunchStatus {title,stage}}

                if let Some(manifest)=visible_course {
                if let Some(s)=session() {CourseProgressLoader {key:"{s.user.id}:{manifest.repository}:{manifest.lessons:?}:{refresh}",session:s,course:manifest.clone(),onloaded:move |records:github_player::CourseProgress|{progress.set(records.events);progress_requirements.set(records.required);}}}
                section {class:"course-catalog",h2 {"{manifest.title}"}p {"{manifest.description}"}
                    crate::course_guide_ui::CourseGuideButton {key:"{manifest:?}",course:manifest.clone()}
                    if let Some(s)=session() {
                        CourseIdentity {key:"{s.user.id}:{manifest.id}",session:s.clone(),course:manifest.clone(),onready:{let scope=format!("{}:{}",s.user.id,manifest.id);move |ready:bool|{
                            let current=format!("{}:{}",session.peek().as_ref().map(|s|s.user.id).unwrap_or(0),course.peek().as_ref().map(|c|c.id.as_str()).unwrap_or(""));
                            if current==scope {if ready {identity_scope.set(scope.clone());if let Some(link)=waiting_name_link(){if link.course==course.peek().as_ref().map(|c|c.repository.as_str()).unwrap_or(""){waiting_name_link.set(None);molip_quest::lesson_link::receive(&link.app_url());}}}else{identity_scope.set(String::new());}}
                        }}}
                    }
                    {let records=progress();let total=manifest.lessons.iter().filter(|l|l.required).count();let complete=manifest.lessons.iter().filter(|l|l.required&&records.get(&l.id).is_some_and(|e|issue_progress::status(e,&l.revision,progress_requirements().get(&l.id).map(Vec::as_slice).unwrap_or(&[])).current)).count();rsx!{p {class:"study-progress","최신 버전 완료: 필수 수업 {complete} / {total}"}}}
                    p {"추천 순서와 상관없이 어떤 수업이든 선택할 수 있어요."}
                    a {href:format!("https://jhs512.github.io/immersion-quest-3/dashboard/{}/",manifest.repository),target:"_blank",rel:"noopener noreferrer","대시보드 보기"}
                    div {class:"repository-lessons",
                        for (index,reference) in manifest.lessons.iter().enumerate() {
                            article {class:"card lesson-card",key:"{reference.id}",
                                div {class:"lesson-card-heading",span {class:"lesson-number","수업 {index+1}"}h3 {"{reference.title}"}}
                                p {class:"lesson-revision","버전 {reference.revision}"}
                                LessonShare {repository:manifest.repository.clone(),lesson_id:reference.id.clone()}
                                {let records=progress().get(&reference.id).cloned().unwrap_or_default();let requirements=progress_requirements().get(&reference.id).cloned();rsx!{
                                    if let Some(required)=requirements {
                                        {let summary=issue_progress::learning_progress(&records,&reference.revision,&required);rsx!{
                                            div {class:"lesson-progress",aria_label:"수업 진도",
                                                strong {"{summary.percent}% 완료"}
                                                span {"필수 문제 {summary.solved} / {summary.total}"}
                                                progress {max:"100",value:summary.percent.to_string(),aria_label:format!("수업 진도 {}%",summary.percent)}
                                            }
                                        }}
                                    }else{p {class:"lesson-status","진도를 확인하고 있어요…"}}
                                }}
                                if !reference.prerequisites.is_empty() {p {class:"prerequisite",{format!("선수 학습: {}",reference.prerequisites.iter().filter_map(|id|manifest.lessons.iter().find(|l|l.id==*id)).map(|l|l.title.clone()).collect::<Vec<_>>().join(", "))}}}
                                for mode in [StudyMode::Full] {
                                    button {class:if mode==StudyMode::Full {"primary"}else{""},disabled:busy()||identity_scope()!=format!("{}:{}",session().map(|s|s.user.id).unwrap_or(0),manifest.id),onclick:{let manifest=manifest.clone();let reference=reference.clone();move |_|{
                                        let manifest=manifest.clone();let reference=reference.clone();let Some(s)=session() else{return};
                                        spawn(async move {
                                            busy.set(true);message.set(String::new());launching.set(Some((reference.title.clone(),0)));
                                            let (stage_tx,mut stage_rx)=tokio::sync::mpsc::unbounded_channel::<u8>();
                                            spawn(async move {while let Some(stage)=stage_rx.recv().await {if let Some((title,current))=launching(){launching.set(Some((title,current.max(stage))));}}});
                                            let result=github_player::background(move||prepare_open_lesson(s,manifest,reference,mode,Some(stage_tx))).await;
                                            match result {Ok(selected)=>{open.set(Some(selected));message.set(String::new());},Err(e)=>message.set(e)}
                                            launching.set(None);busy.set(false);
                                        });
                                    }},"학습 시작"}
                                }
                            }
                        }
                    }
                }
                }
                }
                }
            }
            if session().is_some() {p {class:"repository-status",role:"status","{message}"}}
        }
    }
}

#[component]
fn CourseIdentity(session:Session,course:CourseManifest,onready:EventHandler<bool>)->Element {
    let mut name=use_signal(String::new);let mut saved=use_signal(String::new);let mut notice=use_signal(String::new);let mut loading=use_signal(||true);let mut pending=use_signal(||false);let mut version=use_signal(||0u64);
    let initial_session=session.clone();let initial_course=course.clone();
    use_future(move||{let s=initial_session.clone();let c=initial_course.clone();async move{
        let result=github_player::background(move||molip_quest::course_identity::Store::installed()?.load(&s.github,&c.repository,&s.user,&c.id,false)).await;
        match result {Ok(Some(state))=>{name.set(state.name.clone());saved.set(state.name);pending.set(state.pending);notice.set(state.problem);onready.call(true);},Ok(None)=>onready.call(false),Err(e)=>notice.set(e)}loading.set(false);
    }});
    let poll_session=session.clone();let poll_course=course.clone();
    use_future(move||{let s=poll_session.clone();let c=poll_course.clone();async move{loop{
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        if !*pending.peek(){continue;}
        let repo=c.repository.clone();let id=c.id.clone();let user=s.user.id;
        if let Ok(Some(state))=github_player::background(move||molip_quest::course_identity::Store::installed()?.state(&repo,user,&id)).await {pending.set(state.pending);if !state.problem.is_empty(){notice.set(state.problem);}else if !state.pending{notice.set("이름을 저장했어요.".into());}}
    }}});
    rsx!{section {class:"course-identity",aria_label:"코스별 이름",
        form {onsubmit:{let c=course.clone();let s=session.clone();move |event:FormEvent|{
            event.prevent_default();let c=c.clone();let s=s.clone();let value=name();version+=1;let request=version();
            spawn(async move{loading.set(true);let result=github_player::background(move||{let state=molip_quest::course_identity::Store::installed()?.queue(&c.repository,&s.user,&c.id,&value)?;let _=molip_quest::course_identity::synchronize(s.github,s.user);Ok(state)}).await;
                if request!=version(){return;}
                match result{Ok(state)=>{name.set(state.name.clone());saved.set(state.name);pending.set(true);notice.set("이름 전송 중이에요. 실패하면 다시 시도해요.".into());onready.call(true);},Err(error)=>notice.set(error)}loading.set(false);
            });
        }},
            label {r#for:"course-display-name","이 코스에서 쓸 이름"}
            div {class:"course-name-controls",input {id:"course-display-name",name:"display-name",maxlength:120,value:name(),disabled:loading(),placeholder:"예: [BE16]홍길동",oninput:move |e|name.set(e.value())}
                button {r#type:"submit",disabled:loading(),if saved().is_empty(){"이름 저장 후 시작"}else{"이름 변경"}}
                if !saved().is_empty(){button {r#type:"button",disabled:loading(),onclick:{let s=session.clone();let c=course.clone();move |_|{let s=s.clone();let c=c.clone();spawn(async move{loading.set(true);match github_player::background(move||molip_quest::course_identity::Store::installed()?.load(&s.github,&c.repository,&s.user,&c.id,true)).await{Ok(Some(state))=>{name.set(state.name.clone());saved.set(state.name);pending.set(state.pending);notice.set(state.problem);onready.call(true);},Ok(None)=>{},Err(error)=>notice.set(error)}loading.set(false);});}},"최신 이름 불러오기"}}
            }
            p {"이름의 공백은 없애요. 다른 코스의 이름은 바뀌지 않아요."}
            p {"이 이름은 코스의 공개 학습 기록에 보여요."}
            if !notice().is_empty(){p {role:"status","{notice}"}}
        }
    }}
}

#[component]
fn LessonShare(repository:String,lesson_id:String)->Element {
    let url=molip_quest::lesson_link::LessonLink::new(&repository,&lesson_id).map(|link|link.web_url()).unwrap_or_default();
    rsx!{button {class:"lesson-share",r#type:"button",title:"이 코스의 수업을 여는 웹 링크 복사","data-lesson-link":url.clone(),onclick:move |_|{
        #[cfg(not(target_os="android"))]
        let result=arboard::Clipboard::new().map_err(|e|e.to_string()).and_then(|mut clipboard|clipboard.set_text(url.clone()).map_err(|e|e.to_string()));
        #[cfg(target_os="android")]
        let result:Result<(),String>=Err("링크 복사는 데스크톱에서 사용할 수 있어요.".into());
        let notice=match result {Ok(())=>"수업 링크를 복사했어요.".to_owned(),Err(_)=>"링크를 복사하지 못했어요. 다시 눌러 주세요.".into()};
        document::eval(&format!("window.molipToast?.({})",serde_json::to_string(&notice).unwrap()));
    },"수업 링크 복사"}}
}

#[component]
fn LessonLaunchStatus(title:String,stage:u8)->Element {
    let labels=["수업 파일 확인", "진도 불러오기", "학습 화면 준비"];
    let current=usize::from(stage).min(labels.len()-1);
    rsx!{section {class:"lesson-launch-status",role:"status",aria_live:"polite",aria_busy:"true",
        strong {"{title}"}
        p {"{labels[current]} 중이에요…"}
        div {class:"lesson-launch-track",role:"progressbar",aria_label:"수업 열기",aria_valuetext:labels[current],
            for index in 0..labels.len() {span {class:if index<current{"done"}else if index==current{"active"}else{""}}}
        }
        ol {class:"lesson-launch-steps",aria_label:"준비 단계",
            for (index,label) in labels.iter().enumerate() {li {class:if index<current{"done"}else if index==current{"active"}else{""},aria_current:if index==current{"step"}else{"false"},"{label}"}}
        }
    }}
}

#[component]
fn CourseProgressLoader(session:Session,course:CourseManifest,onloaded:EventHandler<github_player::CourseProgress>)->Element {
    let mut message=use_signal(||"진도를 불러오고 있어요.".to_string());
    use_future(move ||{let session=session.clone();let course=course.clone();async move {
        match github_player::background(move||session.github.course_progress(&course,&session.user)).await {
            Ok(records)=>{onloaded.call(records);message.set(String::new());},Err(e)=>message.set(e)
        }
    }});
    rsx!{p {class:"repository-status",role:"status","{message}"}}
}

#[component]
fn LessonPlayer(session:Session,selected:OpenLesson,window_controls:Element,updates:Element,onback:EventHandler<()>)->Element {
    use_hook({let course=selected.course.id.clone();let lesson=selected.lesson.id.clone();move||{let mut span=molip_quest::telemetry::operation("lesson.open",vec![opentelemetry::KeyValue::new("course.id",course),opentelemetry::KeyValue::new("lesson.id",lesson)]);span.finish("ok");}});
    let mut events=use_signal(||selected.events.clone());
    let mut activity_message=use_signal(String::new);
    let mut show_info=use_signal(||false);
    use_effect(move ||{
        document::eval(if show_info(){"document.getElementById('lesson-info-dialog')?.showModal()"}else{"document.getElementById('lesson-info-dialog')?.close()"});
    });
    let already_passed=issue_progress::learned_tasks(&selected.events,&selected.lesson.revision);
    let first_unfinished=selected.lesson.tasks.iter().position(|task|!already_passed.contains(&task.id)).unwrap_or(0);
    let mut task_index=use_signal(||first_unfinished);
    let mut section_index=use_signal(||0usize);
    use_effect(move || {
        let _ = task_index();
        let _ = section_index();
        document::eval("requestAnimationFrame(()=>document.querySelector('.study-navigation [aria-current=\"step\"]')?.scrollIntoView({block:'nearest',inline:'nearest'}));");
    });
    use_future({let session=session.clone();let selected=selected.clone();move ||{let session=session.clone();let selected=selected.clone();async move {
        if selected.mode==StudyMode::Full {if let Some(first)=selected.lesson.sections.first() {
            let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::Viewed);event.task_id=Some(first.id.clone());
            match github_player::background(move||session.github.record(&selected.course.repository,&session.user,&selected.lesson.title,&event,&[])).await {Ok(latest)=>merge_local_events(events,latest),Err(e)=>activity_message.set(e)}
        }}
    }}});
    let state=issue_progress::status(&events(),&selected.lesson.revision,&selected.lesson.required_tasks());
    let passed=issue_progress::learned_tasks(&events(),&selected.lesson.revision);
    let required=selected.lesson.required_tasks();
    let count=required.iter().filter(|id|passed.contains(*id)).count();
    let view=if selected.mode==StudyMode::Full && section_index()<selected.lesson.sections.len() {None}else{Some(selected.lesson.tasks[task_index().min(selected.lesson.tasks.len()-1)].clone())};
    let is_task=view.is_some();
    let task_count=selected.lesson.tasks.len();
    let record_view={let session=session.clone();let selected=selected.clone();move |index:usize|{
        let session=session.clone();let selected=selected.clone();
        spawn(async move {
            let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::Viewed);
            event.task_id=Some(selected.lesson.sections[index].id.clone());
            let title=selected.lesson.title.clone();let repo=selected.course.repository.clone();
            match github_player::background(move||session.github.record(&repo,&session.user,&title,&event,&[])).await {
                Ok(latest)=>{merge_local_events(events,latest);section_index.set(index);activity_message.set(String::new());},Err(e)=>activity_message.set(e)
            }
        });
    }};
    rsx!{
        div {class:if is_task{"repository-study is-task"}else{"repository-study"},
            header {class:"repository-header",button {class:"course-back",onclick:move |_|onback.call(()),"← 코스 수업 목록"}h1 {title:selected.lesson.title.clone(),"{selected.lesson.title}"}
                LessonShare {repository:selected.course.repository.clone(),lesson_id:selected.lesson.id.clone()}
                button {class:"lesson-info-trigger",aria_label:"학습 정보",title:"진도와 학습 목표 보기",onclick:move |_|show_info.set(true),
                    {format!("{}% · {count}/{} ⓘ",if required.is_empty(){0}else{count*100/required.len()},required.len())}
                }
                div {class:"repository-tools",span {class:"lesson-account","@{session.user.login}"}button {class:"shortcut-sheet-open","data-shortcut-action":"help",onclick:move |_|{document::eval("window.molipShortcuts?.toggleSheet()");},"단축키"}{updates}{window_controls}}
            }
            dialog {id:"lesson-info-dialog",class:"lesson-info-dialog",aria_labelledby:"lesson-info-title",onkeydown:move |event|{if event.key()==Key::Escape {show_info.set(false);}},
                header {h2 {id:"lesson-info-title","학습 정보"}button {autofocus:true,onclick:move |_|show_info.set(false),"닫기"}}
            section {class:"study-progress",span {"필수 문제 {count} / {required.len()}"}
                strong {{format!("{}% 완료",if required.is_empty(){0}else{count*100/required.len()})}}
                if state.current {strong {"✓ 최신 버전 완료"}} else if state.completed {strong {"✓ 이전 완료 보존 · 추가 학습 있음"}}
                span {"수업 완료 {state.full_completions+state.review_completions}회"}
                a {href:format!("https://jhs512.github.io/immersion-quest-3/dashboard/{}/",selected.course.repository),target:"_blank",rel:"noopener noreferrer","대시보드 보기"}
            }
            if let Some(task)=&view {crate::lesson_outline::LessonOutline {lesson:selected.lesson.clone(),task_id:task.id.clone()}}
            crate::lesson_outline::LessonOverview {key:"{selected.lesson.id}",lesson:selected.lesson.clone()}
            }
            nav {class:"study-navigation",aria_label:"수업 학습 항목",
                if selected.mode==StudyMode::Full {
                    for (index,section) in selected.lesson.sections.iter().enumerate() {button {class:if section_index()==index {"selected"}else{""},aria_current:if section_index()==index {"step"}else{"false"},onclick:{let record_view=record_view.clone();move |_|record_view(index)},"{section.title}"}}
                }
                for (index,task) in selected.lesson.tasks.iter().enumerate() {button {class:match (view.as_ref().is_some_and(|t|t.id==task.id),passed.contains(&task.id)){(true,true)=>"selected completed",(true,false)=>"selected",(false,true)=>"completed",_=>""},"data-completed":passed.contains(&task.id).to_string(),"data-step-id":task.id.clone(),aria_current:if view.as_ref().is_some_and(|t|t.id==task.id){"step"}else{"false"},onclick:move |_|{task_index.set(index);section_index.set(usize::MAX);},if passed.contains(&task.id){"✓ "}if !task.required{"도전 · "}"문제 {index+1} · {task.title}" if passed.contains(&task.id){span {class:"step-completed-badge","완료"}}}}
            }
            if let Some(task)=view {
                RepositoryTask {key:"{selected.round}:{task.id}",session:session.clone(),selected:selected.clone(),task,events,
                    has_next:task_index()+1<task_count,
                    onnext:move |_|{if task_index()+1<task_count{task_index+=1;}else{onback.call(());}},
                    onrecord:move |new_events:Vec<LearningEvent>|{if let Some(first)=new_events.first(){let key=first.key.clone();events.set(issue_progress::merge(events().into_iter().chain(new_events),&key));}}}

            } else {
                article {class:"card repository-reading",
                    h2 {"{selected.lesson.sections[section_index()].title}"}
                    crate::ui::Markdown {text:selected.lesson.sections[section_index()].body.clone()}
                    button {class:"primary","data-enter-next":"true",onclick:{let record_view=record_view.clone();let len=selected.lesson.sections.len();move |_|{let next=section_index()+1;if next<len{record_view(next)}else{section_index.set(next);}}},"다음 학습으로"}
                    p {"개념 읽기는 완료 조건이 아니에요. 문제로 바로 이동해도 돼요."}
                }
            }
            p {class:"study-activity",role:"status","{activity_message}"}
        }
    }
}

#[component]
fn RepositoryTask(session:Session,selected:OpenLesson,task:Task,events:Signal<Vec<LearningEvent>>,onrecord:EventHandler<Vec<LearningEvent>>,has_next:bool,onnext:EventHandler<()>)->Element {
    use_future({let session=session.clone();let selected=selected.clone();let task_id=task.id.clone();move ||{
        let session=session.clone();let selected=selected.clone();let task_id=task_id.clone();async move {
            if events.peek().iter().any(|e|e.kind==EventKind::Started&&e.task_id.as_deref()==Some(task_id.as_str())&&e.round==selected.round){return;}
            let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::Started);
            event.task_id=Some(task_id);
            match github_player::background(move||session.github.record(&selected.course.repository,&session.user,&selected.lesson.title,&event,&[])).await {
                Ok(latest)=>merge_local_events(events,latest),Err(error)=>eprintln!("Problem start recording failed: {error}"),
            }
        }
    }});
    use_hook({let course=selected.course.id.clone();let lesson=selected.lesson.id.clone();let task=task.id.clone();move||{
        let mut span=molip_quest::telemetry::operation("task.open",vec![opentelemetry::KeyValue::new("course.id",course),opentelemetry::KeyValue::new("lesson.id",lesson),opentelemetry::KeyValue::new("task.id",task)]);span.finish("ok");
    }});
    use_hook({let location=molip_quest::bug_report::Location{course_id:selected.course.id.clone(),course_title:selected.course.title.clone(),lesson_id:selected.lesson.id.clone(),lesson_title:selected.lesson.title.clone(),lesson_repository:selected.course.lessons.iter().find(|l|l.id==selected.lesson.id).map(|l|l.repository.clone()).unwrap_or_default(),revision:selected.lesson.revision.clone(),task_id:task.id.clone(),task_title:task.title.clone()};move||molip_quest::bug_report::remember(&location)});
    let key=molip_quest::drafts::repository_scope(&ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},selected.mode,&task.id);
    let git_scope=task.git_terminal.as_ref().map(|exercise|molip_quest::drafts::repository_scope(&ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},selected.mode,if exercise.workspace_group.is_empty(){&task.id}else{&exercise.workspace_group}));
    let previous_key=format!("repo:{}:{}:{}:{}:{}",session.user.id,selected.course.id,selected.lesson.id,selected.round,task.id);
    let review_key=molip_quest::drafts::repository_scope(&ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},StudyMode::Review,&task.id);
    let initial=use_hook(||molip_quest::drafts::load(&key).ok().flatten().or_else(||molip_quest::drafts::load(&review_key).ok().flatten()).or_else(||molip_quest::drafts::load(&previous_key).ok().flatten()).map(|d|d.code).unwrap_or_else(||task.starter_code.clone()));
    let has_example=task.has_runnable_example();
    let initial_workspace=crate::explanation_session::TaskWorkspace::new(initial.clone(),task.example_for_answer(&initial).unwrap_or_default(),task.tests.first().map(|case|case.input.clone()).unwrap_or_default());
    let (workspace,mut explanation_session)=crate::explanation_session::use_workspace(initial_workspace);
    let mut code=workspace.map_mut(|state|&state.code,|state|&mut state.code);
    let mut reset=workspace.map_mut(|state|&state.reset,|state|&mut state.reset);
    let mut example_source=workspace.map_mut(|state|&state.example_source,|state|&mut state.example_source);
    let mut input=workspace.map_mut(|state|&state.input,|state|&mut state.input);
    let mut busy=workspace.map_mut(|state|&state.busy,|state|&mut state.busy);
    let mut message=workspace.map_mut(|state|&state.message,|state|&mut state.message);
    let mut output=workspace.map_mut(|state|&state.output,|state|&mut state.output);
    let mut preview=workspace.map_mut(|state|&state.preview,|state|&mut state.preview);
    let mut teacher_preview=workspace.map_mut(|state|&state.teacher_preview,|state|&mut state.teacher_preview);
    let mut artifacts=workspace.map_mut(|state|&state.artifacts,|state|&mut state.artifacts);
    let narrating=workspace.map_mut(|state|&state.narrating,|state|&mut state.narrating);
    let mut execution_id=workspace.map_mut(|state|&state.execution_id,|state|&mut state.execution_id);
    let mut feedback=workspace.map_mut(|state|&state.feedback,|state|&mut state.feedback);
    let mut execution_state=workspace.map_mut(|state|&state.execution_state,|state|&mut state.execution_state);
    let mut execution_seconds=workspace.map_mut(|state|&state.execution_seconds,|state|&mut state.execution_seconds);
    let mut git_practice=use_signal(||None::<crate::git_terminal_ui::Practice>);
    let mut git_control=use_signal(||None::<crate::git_terminal_ui::TerminalControl>);
    let ordered_task=task.clone();
    // A workspace field write also notifies mapped fields. Only a changed answer
    // should expand ordered code; writing its diagnostic must not retrigger it.
    let ordered_answer=use_memo(move||code());
    use_effect(move||{if ordered_task.example_order_marker.is_some(){match ordered_task.example_for_answer(&ordered_answer()){Ok(source)=>{if *example_source.peek()!=source{example_source.set(source);reset.with_mut(|version|*version+=1);}},Err(error)=>{if *message.peek()!=error{message.set(error);}}}}});

    let mut show_solution=use_signal(||false);
    let mut passed_dialog=use_signal(||false);
    let mut submitting=use_signal(||false);
    use_drop(||{document::eval("window.molipAgent?.stop()");});
    let mut history_saves=use_signal(||0usize);
    let mut history_message=use_signal(String::new);
    use_effect(|| { document::eval("const s=document.querySelector('select.repository-narration-rate');if(s&&window.molipVoice)s.value=String(molipVoice.rate);"); });
    let required=selected.lesson.required_tasks();
    let filename=if task.git_terminal.as_ref().is_some_and(|e|e.java_build.is_some()){"Main.java · Bash 터미널".to_string()}else if task.git_terminal.as_ref().is_some_and(|e|e.vim.is_some()){"Vim 편집기".to_string()}else if task.git_terminal.as_ref().is_some_and(|e|e.shell.is_some()){"Bash 터미널".to_string()}else if task.git_terminal.is_some(){"Git 터미널".to_string()}else if task.interaction.is_some()&&!has_example{"답안".to_string()}else if task.entry_file.is_empty(){task.language.filename().to_string()}else{task.entry_file.clone()};
    // Show the data this problem reads before other files bundled with the lesson.
    let mut provided_files=task.files.iter().map(|(name,body)|{
        let used=task.starter_code.contains(name.as_str())||task.solution.contains(name.as_str())
            ||task.example_code.as_deref().is_some_and(|source|source.contains(name.as_str()));
        (name.clone(),body.clone(),used)
    }).collect::<Vec<_>>();
    provided_files.sort_by(|a,b|b.2.cmp(&a.2).then_with(||a.0.cmp(&b.0)));
    let explanation=issue_progress::explanation_info(&events(),&task.id);
    let record_explanation={let session=session.clone();let selected=selected.clone();let task_id=task.id.clone();move ||{
        let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::ExplanationViewed);
        event.task_id=Some(task_id.clone());
        event.success_before_view=events().iter().any(|e|e.kind==EventKind::Attempt&&e.passed&&e.task_id.as_deref()==Some(&task_id));
        let gh=session.github.clone();let user=session.user.clone();let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
        spawn(async move {match github_player::background(move||gh.record(&repo,&user,&title,&event,&[])).await {Ok(latest)=>onrecord.call(latest),Err(e)=>history_message.set(format!("해설 이력을 저장하지 못했어요. {e}"))}});
    }};
    let solution_text=if let Some(exercise)=task.git_terminal.as_ref().filter(|e|e.java_build.is_some()) {
        let shell=exercise.shell.as_ref().unwrap();format!("### Main.java\n```java\n{}\n```\n### 터미널에서 실행할 명령\n```bash\n{}\n```\n{}",shell.goal.files["Main.java"],shell.commands.join("\n"),task.solution)
    }else{format!("```{}\n{}\n```",task.language.editor(),task.solution)};
    rsx!{
        article {class:"lesson repository-task","data-course-id":selected.course.id.clone(),"data-lesson-id":selected.lesson.id.clone(),"data-task-id":task.id.clone(),"data-predict-before-run":task.predict_before_run.to_string(),"data-busy":busy().to_string(),"data-narrating":narrating().to_string(),"data-explanation-session":explanation_session.owner(),"data-git-ready":git_practice().is_some().to_string(),
            section {class:"problem-pane",div {class:"problem-heading",h2 {"{task.title}"}
                button {class:"problem-report",title:"문제 신고 · Ctrl+Alt+Shift+P",onclick:move |_|{if let Err(error)=crate::emergency_report::request("content"){history_message.set(error);}},"문제 신고"}}
                if !task.question.is_empty(){p {class:"task-question",strong {"{task.question}"}}}
                crate::ui::Markdown{text:task.goal.clone()}
                for material in &task.supporting_materials {
                    SupportingMaterialPanel {key:"{task.id}/{material.id}", material:material.clone()}
                }
                if !task.required {p {class:"challenge-note","선택 도전이에요. 수업 완료 후에 풀어도 돼요."}}
                if !task.hints.is_empty() {div {class:"task-hints",for (index,hint) in task.hints.iter().enumerate(){details {summary {"힌트 {index+1}"}crate::ui::Markdown{text:hint.clone()}}}}}
                div {class:"explanation-controls",role:"group",aria_label:"풀이와 해설",
                button {class:"solution-toggle",onclick:{let record=record_explanation.clone();move |_|{if !show_solution(){record();}show_solution.set(!show_solution());}},"정답과 풀이 보기"}
                if !task.narration.is_empty() {
                    button {class:"narration-play",disabled:busy()||narrating(),onclick:{let actions=task.narration.clone();let record=record_explanation.clone();let needs_git=task.git_terminal.is_some();let demo_code=task.starter_code.clone();let demo_example=task.example_for_answer(&demo_code).unwrap_or_default();let has_interaction=task.interaction.is_some();let demo_input=task.tests.first().map(|case|case.input.clone()).unwrap_or_default();move |_|{
                        record();
                        let Some(owner)=explanation_session.begin(demo_code.clone(),demo_example.clone(),demo_input.clone(),needs_git) else{return;};
                        let expected=serde_json::json!({"source":if has_example{Some(demo_example.clone())}else if !needs_git&&!has_interaction{Some(demo_code.clone())}else{None},"answer":if has_interaction{Some(demo_code.clone())}else{None}});
                        let actions=actions.clone();
                        spawn(async move {
                            let script=format!("(async()=>{{try{{const root=document.querySelector('.repository-task'),expected={expected},owner={};const until=Date.now()+45000;const ready=()=>root.dataset.explanationSession===owner&&root.dataset.narrating==='true'&&(!{needs_git}||(window.molipGitTutor?.owner&&window.molipGitTutor.owner===root.querySelector('#git-demo-terminal')?.dataset.terminalSession))&&(expected.source===null||window.molipCodeEditors?.getValue()===expected.source)&&(expected.answer===null||root.querySelector('.answer-state-bridge')?.value===expected.answer);while(root?.isConnected&&!ready()){{if(window.mq3CancelledExplanations?.has(owner))return;if(Date.now()>until)throw new Error('해설 시연을 준비하지 못했어요.');await new Promise(requestAnimationFrame);}}if(root?.isConnected&&!window.mq3CancelledExplanations?.has(owner))await window.molipAgent?.runExplanation({},{{owner,root}});}}finally{{dioxus.send(true);}}}})();",serde_json::to_string(&owner).unwrap(),serde_json::to_string(&actions).unwrap_or_else(|_|"[]".into()));
                            let mut bridge=document::eval(&script);let _=bridge.recv::<bool>().await;
                            document::eval(&format!("window.mq3CancelledExplanations?.delete({});",serde_json::to_string(&owner).unwrap()));
                            explanation_session.finish(&owner);
                        });
                    }},"해설 재생"}
                    button {class:"narration-stop","data-explanation-stop":"true",disabled:!narrating(),onclick:move |_|{let owner=explanation_session.owner();document::eval(&format!("(window.mq3CancelledExplanations??=new Set()).add({});window.molipAgent?.stop();",serde_json::to_string(&owner).unwrap()));explanation_session.finish(&owner);},"멈춤"}
                    label {class:"narration-speed",span {"속도"}
                        select {class:"assistant-rate repository-narration-rate",aria_label:"해설 말 속도",onchange:move |e|{document::eval(&format!("window.molipVoice?.setRate({});",e.value()));},
                            for rate in ["0.75","1","1.25","1.5","1.75","2"] {option {value:rate,selected:rate=="1.5","{rate}배"}}
                        }
                    }
                }
                }
                if explanation.before_success||explanation.after_success {details {class:"explanation-info",summary {"학습 정보"}
                    if explanation.before_success {p {title:"풀이 전에 해설을 함께 봤어요.",aria_label:"풀이 전 해설 확인","💡 풀이 전에 해설을 확인했어요."}}
                    if explanation.after_success {p {title:"성공 후 해설을 다시 봤어요.",aria_label:"성공 후 해설 확인","↺ 성공 후 해설을 다시 확인했어요."}}
                }}
                if show_solution() {crate::ui::Markdown{text:solution_text.clone()}}
                if !provided_files.is_empty() {details {class:"provided-files",summary {"함께 제공한 파일"}
                    for (name,body,used) in &provided_files {details {class:"provided-file",key:"{name}",summary {{format!("{name}{}",if *used {" · 이 문제에서 사용"}else{""})}}crate::ui::Markdown{text:format!("```\n{body}\n```")}}}
                }}
            }
            div {class:"split-handle split-col",role:"separator",tabindex:0,aria_label:"문제와 코드 패널 크기 조절",aria_orientation:"vertical"}
            section {class:"coding-pane",
                if task.git_terminal.as_ref().is_some_and(|e|e.github_pr.is_some()) {p {class:"github-pr-notice",role:"note","실제 GitHub를 사용해요. 중간 초기화는 지원하지 않아요. 첫 단계에서 새 회차를 시작하면 새 저장소 이름이 준비돼요. 기존 저장소와 PR은 남아요."}}
                div {class:"pane-heading",strong {"{filename}"}
                if feedback()=="incorrect"||feedback()=="error"||feedback()=="run-error" {span {class:"submission-indicator",if feedback()=="incorrect"{"제출 실패"}else{"오류 발생"}}}
                div {class:"pane-actions",
                    button {disabled:busy()||narrating()||task.git_terminal.as_ref().and_then(|e|e.github_pr).is_some_and(|stage|stage!=molip_quest::git_practice::GithubPrStage::Repository),title:if task.git_terminal.as_ref().is_some_and(|e|e.github_pr.is_some()){"실제 GitHub 실습은 첫 단계에서만 새 회차를 시작할 수 있어요."}else{"현재 문제의 시작 상태로 돌아가요. 완료 기록은 유지해요."},onclick:{let starter=task.starter_code.clone();let example=task.example_for_answer(&task.starter_code).unwrap_or_default();let hosted=task.git_terminal.as_ref().is_some_and(|e|e.github_pr.is_some());let key=key.clone();move |_|{
                        if narrating(){return;}
                        let starter=starter.clone();let example=example.clone();let key=key.clone();
                        spawn(async move {
                            if hosted {
                                let mut confirmation=document::eval("dioxus.send(window.confirm('새 회차를 시작할까요? 새 저장소 이름으로 처음부터 준비해요. 다음 생성 명령을 실행하면 GitHub에 실제 새 비공개 저장소가 생겨요. 기존 저장소와 PR은 그대로 남아요.'));");
                                if !matches!(confirmation.recv::<bool>().await,Ok(true)){return;}
                            }
                            feedback.set("idle");message.set(String::new());execution_state.set("idle");output.set(String::new());preview.set(String::new());teacher_preview.set(String::new());artifacts.set(vec![]);
                            if let Some(control)=git_control() {
                                busy.set(true);message.set("실습을 초기화하고 있어요.".into());
                                let graph_control=control.clone();
                                match github_player::background(move||control.shutdown()).await {
                                    Ok(())=>{graph_control.clear_graph();git_practice.set(None);git_control.set(None);code.set(starter);let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());reset+=1;message.set(String::new());},Err(error)=>message.set(error)
                                }
                                busy.set(false);
                            }else{code.set(starter);example_source.set(example);reset+=1;let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());}
                        });
                    }},if task.git_terminal.as_ref().is_some_and(|e|e.github_pr.is_some()){"새 회차 시작"}else{"초기화"}}

                    if task.git_terminal.is_none()&&(task.interaction.is_none()||has_example) {
                    button {"data-shortcut-action":"run",disabled:busy()||(task.predict_before_run&&!narrating()&&code().is_empty()),onclick:{let task=task.clone();let github=session.github.clone();let user=session.user.clone();let selected=selected.clone();move |_|{let task=task.clone();let github=github.clone();let user=user.clone();let selected=selected.clone();async move {
                        busy.set(true);feedback.set("idle");execution_id+=1;execution_state.set("running");execution_seconds.set(0);
                        let demonstration=narrating();
                        message.set("코드를 실행하고 있어요.".into());output.set(String::new());if demonstration{teacher_preview.set(String::new());}else{preview.set(String::new());}artifacts.set(vec![]);
                        let source=if has_example{example_source()}else{code()};let prediction=task.predict_before_run.then(||code());let input=input();let started=std::time::Instant::now();let run_id=execution_id();
                        let timer=spawn(async move {loop {tokio::time::sleep(std::time::Duration::from_secs(1)).await;if execution_id()!=run_id{break;}execution_seconds+=1;}});
                        // Local execution never waits for GitHub. The upload worker authenticates
                        // the expected account before recording the separate history operation.
                        let result=molip_quest::telemetry::observe("task.run",vec![opentelemetry::KeyValue::new("course.id",selected.course.id.clone()),opentelemetry::KeyValue::new("lesson.id",selected.lesson.id.clone()),opentelemetry::KeyValue::new("task.id",task.id.clone())],async {if has_example{molip_quest::lesson_runner::run_example(&task,&source,&input).await}else{molip_quest::lesson_runner::run(&task,&source,&input).await}}).await;
                        timer.cancel();
                        if execution_id()!=run_id {return;}
                        match result {
                            Ok(result)=>{
                                output.set(format!("{}\n{}",result.stdout,result.stderr));
                                execution_state.set(if result.success{"finished"}else{"failed"});
                                if !result.success{feedback.set("run-error");}
                                message.set(if result.success {format!("실행을 마쳤어요. {:.2}초 걸렸어요. 제출해서 모든 검사를 확인하세요.",started.elapsed().as_secs_f64())}else{"실행에 실패했어요. 결과를 확인하세요.".into()});
                                let html=result.artifacts.iter().find_map(|a|match a {molip_quest::runner::Artifact::Html{srcdoc,..}=>Some(srcdoc.clone()),_=>None}).unwrap_or_default();
                                if demonstration{teacher_preview.set(html);}else{preview.set(html);}
                                artifacts.set(result.artifacts.into_iter().filter(|a|!matches!(a,molip_quest::runner::Artifact::Html{..})).collect());
                            },
                            Err(error)=>{execution_state.set("failed");feedback.set("run-error");message.set(error);}
                        }
                        busy.set(false);
                        if demonstration{return;}
                        let mut event=LearningEvent::new(ProgressKey{user_id:user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::ExampleRun);event.task_id=Some(task.id.clone());event.prediction=prediction;
                        let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
                        history_saves+=1;
                        spawn(async move {
                            match github_player::background(move||github.record(&repo,&user,&title,&event,&[])).await {
                                Ok(latest)=>onrecord.call(latest),
                                Err(error)=>history_message.set(format!("실행 이력을 저장하지 못했어요. {error}"))
                            }
                            history_saves-=1;
                        });
                    }}},"코드 실행"}
                    }
                    button {class:"primary","data-shortcut-action":"submit","data-enter-submit":"true",disabled:busy()||narrating()||(task.git_terminal.is_some()&&git_practice().is_none()),onclick:{let task=task.clone();let session=session.clone();let selected=selected.clone();let required=required.clone();move |_|{let task=task.clone();let session=session.clone();let selected=selected.clone();let required=required.clone();async move {
                        submitting.set(true);busy.set(true);feedback.set("checking");execution_state.set("idle");output.set(String::new());message.set("검사하고 있어요.".into());
                        match molip_quest::telemetry::observe("task.submit",vec![opentelemetry::KeyValue::new("course.id",selected.course.id.clone()),opentelemetry::KeyValue::new("lesson.id",selected.lesson.id.clone()),opentelemetry::KeyValue::new("task.id",task.id.clone())],async {if task.git_terminal.as_ref().is_some_and(|e|e.java_build.is_some()) {
                                let practice=git_practice();let answer=code();let interaction=task.interaction.clone();
                                github_player::background(move||{
                                    let practice=practice.ok_or("실습 터미널이 준비되지 않았어요.")?;
                                    let mut report=practice.lock().unwrap_or_else(|e|e.into_inner()).check_exercise()?;
                                    if let Some(interaction)=interaction {let choice=interaction.check(&answer)?;report.passed&=choice.passed;report.cases.extend(choice.cases);}
                                    Ok(report)
                                }).await
                            }else if task.git_terminal.is_some()&&task.interaction.is_none() {
                                let practice=git_practice();let checks=task.git_checks.clone();
                                github_player::background(move||{
                                    let practice=practice.ok_or("실습 터미널이 준비되지 않았어요.")?;
                                    let practice=practice.lock().unwrap_or_else(|e|e.into_inner());
                                    if let Some(checks)=checks {practice.check(&checks)}else{practice.check_exercise()}
                                }).await
                            }else{molip_quest::lesson_runner::check(&task,&code()).await}}).await {
                                Err(e)=>{feedback.set("error");message.set(e);},Ok(report)=>{
                                    feedback.set(if report.passed{"passed"}else{"incorrect"});
                                    message.set(if report.passed{"통과했어요."}else{"다시 풀어보세요. 아래 검사에서 예상과 실제 결과를 비교하세요."}.into());
                                    output.set(report.cases.iter().enumerate().map(|(i,c)|format!("검사 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed{"통과"}else{"다시 풀기"},c.input,c.expected,c.stdout,c.stderr)).collect::<Vec<_>>().join("\n\n"));
                                    let key=ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()};
                                    let mut event=LearningEvent::new(key,&selected.lesson.revision,selected.mode,&selected.round,EventKind::Attempt);event.task_id=Some(task.id.clone());event.passed=report.passed;
                                    let github=session.github.clone();let user=session.user.clone();let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
                                    let latest=molip_quest::progress_sync::apply_result(events(),&event,&required);
                                    let complete=issue_progress::status(&latest,&selected.lesson.revision,&required).current;
                                    onrecord.call(latest);
                                    if report.passed&&complete{message.set("수업 완료!".into());}
                                    passed_dialog.set(report.passed);
                                    // Persistence belongs to the process, so navigation cannot cancel it.
                                    let recording=molip_quest::progress_sync::record_guard();
                                    if let Err(error)=std::thread::Builder::new().name("progress-record".into()).spawn(move||{
                                        let _recording=recording;
                                        if let Err(error)=github.record(&repo,&user,&title,&event,&required){eprintln!("Progress recording failed: {error}");}
                                    }){eprintln!("Progress recording could not start: {error}");}
                                }
                            }
                        busy.set(false);submitting.set(false);
                    }}},"제출"}
                }
            }
            if task.predict_before_run&&!narrating()&&code().is_empty(){p {class:"prediction-run-note",role:"status","예상 보기를 먼저 하나 고르면 실행할 수 있어요. 정답 여부와 관계없이 실행돼요."}}
            div {class:if (task.git_terminal.is_some()||has_example)&&task.interaction.is_some(){"editor-pane interaction-example-editor"}else{"editor-pane"},style:if task.git_terminal.as_ref().is_some_and(|exercise|exercise.java_build.is_some())&&task.interaction.is_some(){"display:grid;grid-template-rows:minmax(216px,1fr) 10px minmax(64px,min(var(--example-answer-height,92px),calc(100% - 226px)));gap:0"}else if (task.git_terminal.is_some()||has_example)&&task.interaction.is_some(){"display:grid;grid-template-rows:minmax(48px,1fr) 10px var(--example-answer-height,fit-content(60%));gap:0"}else{""},
                if let Some(exercise)=task.git_terminal.clone() {
                    div {class:"example-code-pane",style:if narrating(){"display:none"}else if task.interaction.is_some(){"display:block;min-height:0;overflow:hidden"}else{"display:block;height:100%"},
                        {rsx!{crate::git_terminal_ui::GitTerminal {key:"git-{reset}",exercise:exercise.clone(),demo:false,scope:git_scope.clone(),fresh:reset()>0,step_id:task.id.clone(),onready:move |practice|git_practice.set(Some(practice)),oncontrol:move |control|git_control.set(Some(control))}}}
                    }
                    if narrating() {div {class:"example-code-pane",style:if task.interaction.is_some(){"min-height:0;overflow:hidden"}else{"height:100%"},crate::git_terminal_ui::GitTerminal {exercise,demo:true,onready:move |_|{},oncontrol:move |_|{}}}}
                }else if has_example {
                    textarea {class:"code-editor","data-code-editor":task.language.editor(),"data-editor-value":example_source(),"data-editor-reset":reset().to_string(),aria_label:"수업 예제 코드",initial_value:task.example_for_answer(&initial).unwrap_or_default(),readonly:true,spellcheck:false,oninput:move |e|example_source.set(e.value())}
                }else if task.interaction.is_none() {
                textarea {class:"code-editor","data-code-editor":if task.entry_file.ends_with(".jsx"){"javascript"}else{task.language.editor()},"data-editor-value":code(),"data-editor-reset":reset().to_string(),aria_label:"수업 코드",initial_value:initial.clone(),spellcheck:false,oninput:{let key=key.clone();move |e|{code.set(e.value());if !narrating(){let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());}}}}
                }
                if (task.git_terminal.is_some()||has_example)&&task.interaction.is_some() {
                    div {class:"split-handle split-row split-example",role:"separator",tabindex:0,aria_label:"예제 코드와 답안 패널 크기 조절",aria_orientation:"horizontal"}
                }
                if let Some(interaction)=task.interaction.clone() {
                    div {class:if task.git_terminal.is_some()||has_example{"interaction-example-answer"}else{""},style:if task.git_terminal.is_some()||has_example{"min-height:0;overflow:hidden"}else{"height:100%;min-height:0"},
                        crate::interaction_ui::InteractionEditor {interaction,question:if task.question.is_empty(){task.title.clone()}else{task.question.clone()},value:code(),disabled:busy()||narrating(),onchange:{let key=key.clone();move |value:String|{code.set(value);if !narrating(){let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());}}}}
                    }
                }
            }
            div {class:"split-handle split-row",role:"separator",tabindex:0,aria_label:"코드와 실행 결과 패널 크기 조절",aria_orientation:"horizontal"}
            section {class:"result-pane","data-execution-id":execution_id().to_string(),"data-execution-state":execution_state(),"data-feedback":feedback(),aria_busy:busy(),h3 {if has_example{"실행·채점 결과"}else if task.interaction.is_some(){"채점 결과"}else{"실행 결과"}}
                if task.git_terminal.is_none()&&(task.interaction.is_none()||has_example) {
                details {class:"run-input",open:task.tests.iter().any(|case|!case.input.is_empty()),
                    summary {"실행 입력"}
                    label {span {"프로그램에 전달할 입력"} textarea {aria_label:"실행 입력",value:input(),oninput:move |e|input.set(e.value())}}
                }
                }
                if matches!(feedback(),"incorrect"|"error"|"run-error"|"passed") {
                    div {class:"submission-feedback",role:if feedback()=="passed"{"status"}else{"alert"},
                        svg {view_box:"0 0 24 24",width:24,height:24,fill:"none",stroke:"currentColor",stroke_width:2,"aria-hidden":"true",
                            circle {cx:12,cy:12,r:9}
                            if feedback()=="passed" {path {d:"m8 12 3 3 5-6"}}else{path {d:"m9 9 6 6m0-6-6 6"}}
                        }
                        div {strong {if feedback()=="incorrect"{"제출 실패 · 다시 풀어보세요"}else if feedback()=="passed"{"검사를 통과했어요"}else if feedback()=="run-error"{"코드 실행에 실패했어요"}else{"검사를 마치지 못했어요"}}
                            p {if feedback()=="incorrect" {if task.interaction.is_some(){"선택한 답과 문제의 조건을 비교한 뒤 다시 제출하세요."}else if task.git_terminal.is_some(){"아래 검사에서 아직 충족하지 못한 조건을 확인하세요."}else{"아래 검사에서 예상값과 실제 결과를 비교한 뒤 코드를 수정하세요."}}else if feedback()=="passed"{"현재 답안이 검사 조건을 만족해요."}else{"아래 오류 내용을 확인한 뒤 다시 시도하세요."}}
                        }
                    }
                }
                p {class:"execution-status",role:"status",aria_live:"polite",
                    if execution_state()=="running" {span {class:"execution-spinner",aria_hidden:"true"} {format!("코드를 실행하고 있어요. {}초 지났어요.",execution_seconds())}}else {"{message}"}
                }
                pre {class:"output","{output}"}
                if history_saves()>0 {p {class:"history-sync",role:"status","실행 이력을 저장하고 있어요. 다음 코드를 실행해도 돼요."}}
                if !history_message().is_empty() {p {class:"history-sync warning",role:"status","{history_message}"}}
                crate::ui::RichResults {artifacts:artifacts()}
                if !preview().is_empty() && task.language==repository_course::TaskLanguage::Web {
                    iframe {key:"{task.id}/student-web-preview",title:"수업 웹 미리보기",hidden:narrating(),"sandbox":"allow-scripts allow-forms",srcdoc:preview(),style:"width:100%;height:400px;border:1px solid #456;"}
                }
                if narrating() && !teacher_preview().is_empty() && task.language==repository_course::TaskLanguage::Web {
                    iframe {key:"{task.id}/teacher-web-preview",title:"해설 웹 미리보기","sandbox":"allow-scripts allow-forms",srcdoc:teacher_preview(),style:"width:100%;height:400px;border:1px solid #456;"}
                }
            }
            }
        }
        if submitting() {SubmissionProgress {}}
        if passed_dialog() && !submitting() {
            TaskPassedDialog {has_next,
                onnext:move |_|{passed_dialog.set(false);onnext.call(());},
                onstay:move |_|{passed_dialog.set(false);document::eval("document.querySelector('.repository-task .primary')?.focus()");}}
        }
    }
}

#[component]
fn SubmissionProgress()->Element {
    rsx! {
        div {class:"submission-progress-backdrop",
            section {class:"submission-progress-dialog",role:"dialog",aria_modal:"true",aria_label:"답안 제출 중",aria_busy:"true",tabindex:-1,
                onmounted:move |event|async move{let _=event.data().set_focus(true).await;},
                onkeydown:move |event|{event.prevent_default();event.stop_propagation();},
                span {class:"execution-spinner",aria_hidden:"true"}
                h2 {"답안을 검사하고 있어요"}
            }
        }
    }
}

#[component]
fn TaskPassedDialog(has_next:bool,onnext:EventHandler<()>,onstay:EventHandler<()>)->Element {
    let mut advancing=use_signal(||false);
    rsx! {
        div {class:"task-passed-backdrop",
            section {class:"task-passed-dialog",role:"dialog",aria_modal:"true",aria_label:"문제 통과",
                onkeydown:move |event|{
                    match event.key() {
                        Key::Escape=>{event.prevent_default();event.stop_propagation();onstay.call(());},
                        Key::Enter=>{event.stop_propagation();if event.is_auto_repeating(){event.prevent_default();}},
                        Key::Tab=>{event.prevent_default();event.stop_propagation();document::eval("const buttons=[...document.querySelectorAll('.task-passed-dialog button')];buttons[(buttons.indexOf(document.activeElement)+1)%buttons.length]?.focus()");},
                        _=>{}
                    }
                },
                div {class:"task-passed-icon",aria_hidden:"true","✓"}
                h2 {"통과했어요!"}
                p {if has_next{"다음 문제로 이어서 풀어보세요."}else{"마지막 문제까지 풀었어요. 수업 목록에서 다음 학습을 선택하세요."}}
                div {class:"task-passed-actions",
                    button {class:"primary",disabled:advancing(),
                        onmounted:move |event|async move{let _=event.data().set_focus(true).await;},
                        onclick:move |_|{if !advancing(){advancing.set(true);onnext.call(());}},
                        if has_next{"다음으로 이동"}else{"수업 목록으로"}}
                    button {onclick:move |_|onstay.call(()),"여기 머물기"}
                }
                small {"Enter로 이동 · Esc로 닫기"}
            }
        }
    }
}

#[component]
fn SupportingMaterialPanel(material: molip_quest::supporting_materials::SupportingMaterial) -> Element {
    let mut expanded = use_signal(|| false);
    rsx! {
        div {class:"supporting-material",
            button {r#type:"button",aria_expanded:expanded().to_string(),
                onclick:move |_| expanded.set(!expanded()),
                "{material.title} · "
                if expanded() {"접기"} else {"펼쳐 보기"}
            }
            if expanded() {
                match &material.content {
                    molip_quest::supporting_materials::MaterialContent::Interactive { variants } => rsx! {
                        InteractiveVisualization {variants:variants.clone()}
                    },
                    molip_quest::supporting_materials::MaterialContent::Image { image }
                    | molip_quest::supporting_materials::MaterialContent::Comic { image } => rsx! {
                        figure {img {src:format!("data:image/png;base64,{}",image.png_base64),alt:image.alt.clone(),style:"max-width:100%;height:auto;"}
                            figcaption {"{image.alt}"}
                        }
                    },
                    molip_quest::supporting_materials::MaterialContent::Mermaid { source } => rsx! {iframe {title:material.title.clone(),"sandbox":"allow-scripts",
                        srcdoc:molip_quest::supporting_materials::diagram_document(source),style:"width:100%;height:320px;border:0;border-radius:8px;"}},
                }
            }
        }
    }
}

#[component]
fn InteractiveVisualization(variants: Vec<molip_quest::supporting_materials::VisualVariant>) -> Element {
    let mut selected = use_signal(|| 0usize);
    let mut position = use_signal(|| 0usize);
    let Some(variant) = variants.get(selected()) else { return rsx!{}; };
    let Some(frame) = variant.frames.get(position()) else { return rsx!{}; };
    let last = variant.frames.len() - 1;
    let count = variants.len();
    rsx! {
        section {class:"interactive-visualization",
            label {"조건 "
                select {aria_label:"시각화 조건",value:selected().to_string(),onchange:move |event| {
                    if let Ok(index) = event.value().parse::<usize>() {
                        if index < count {selected.set(index);position.set(0);}
                    }
                },
                    for (index,variant) in variants.iter().enumerate() {option {value:index.to_string(),"{variant.label}"}}
                }
            }
            div {aria_live:"polite",
                p {"{frame.caption}"}
                table {aria_label:"현재 상태",tbody {for (name,value) in &frame.facts {tr {th {scope:"row","{name}"}td {"{value}"}}}}}
                p {"{position()+1} / {last+1}"}
            }
            button {disabled:position()==0,onclick:move |_| {if position()>0 {position-=1;}},"이전 상태"}
            button {disabled:position()==last,onclick:move |_| {if position()<last {position+=1;}},"다음 상태"}
        }
    }
}


#[component]
fn ContentUpdates(session:Option<Session>,course:Option<CourseManifest>,active_lesson:Signal<Option<OpenLesson>>,onapply:EventHandler<(CourseManifest,bool)>)->Element {
    use molip_quest::{content_updates,updater};
    let mut candidate=use_signal(||None::<content_updates::Snapshot>);
    let mut offered=use_signal(||false);
    let mut message=use_signal(String::new);
    let mut manual=use_signal(||0u64);
    let mut refresh_and_apply=use_signal(||false);
    let mut checking=use_signal(||false);
    let mut applying=use_signal(||false);
    let mut noticed=use_signal(std::collections::HashSet::<String>::new);
    let mut summary=use_signal(String::new);
    let mut auto_attempted=use_signal(||None::<String>);
    let apply=use_callback({let session=session.clone();move |(next,automatic):(content_updates::Snapshot,bool)|{
        let Some(session)=session.clone() else{return};
        if applying(){return;} applying.set(true);
        spawn(async move {
            if !automatic {
                let mut bridge=document::eval("window.molipAgent?.stop();requestAnimationFrame(()=>requestAnimationFrame(()=>dioxus.send(true)))");
                if !matches!(bridge.recv::<bool>().await,Ok(true)) {message.set("해설을 닫고 다시 업데이트하세요.".into());applying.set(false);return;}
            }
            let manifest=next.course().clone();
            let result=github_player::background(move||{
                session.github.ensure_user(session.user.id)?;
                molip_quest::drafts::backup_repository(session.user.id,&next.course().id,&next.fingerprint())?;
                content_updates::installed_store()?.apply(&next)
            }).await;
            match result {Ok(())=>{candidate.set(None);offered.set(false);message.set("수업 내용을 업데이트했어요.".into());onapply.call((manifest,automatic));},Err(error)=>message.set(error)}
            applying.set(false);
        });
    }});
    use_effect(move||{
        let next=candidate();let studying=active_lesson().is_some();let running=applying();
        if !studying&&!running {if let Some(next)=next {
            let fingerprint=next.fingerprint();
            if auto_attempted.peek().as_ref()!=Some(&fingerprint) {auto_attempted.set(Some(fingerprint));apply.call((next,true));}
        }}
    });
    use_future({let session=session.clone();let course=course.clone();move ||{let session=session.clone();let course=course.clone();async move {
        let (Some(session),Some(course))=(session,course) else{return};
        let started=std::time::Instant::now();let mut schedule=updater::UpdateSchedule::default();let mut seen=0;
        loop {
            let request=*manual.peek(); let requested=request!=seen;
            if schedule.begin(started.elapsed().as_secs(),requested) {
                let apply_after_check=requested&&*refresh_and_apply.peek();
                refresh_and_apply.set(false);
                checking.set(true);
                seen=request; let gh=session.github.clone();let repo=course.repository.clone();let user=session.user.id;
                let result=github_player::background(move||{
                    gh.ensure_user(user)?;
                    let next=gh.prepare_course(&repo)?;
                    let current=content_updates::installed_store()?.active(&repo)?.ok_or("설치된 코스가 없어요.")?;
                    if next.course().id!=current.course().id {return Err("코스의 고유 코드가 바뀌었어요.".into())}
                    let changes=next.changes_from(&current);
                    Ok((next.fingerprint()!=current.fingerprint()).then_some((next,changes)))
                }).await;
                schedule.finish();
                checking.set(false);
                match result {
                    Ok(Some((next,changes)))=>{
                        auto_attempted.set(None);
                        let notices=molip_quest::data_dir().map(|dir|dir.join("content-update-notices.json"));
                        let first=notices.and_then(|path|{let mut notices=updater::UpdateNotices::open(&path)?;notices.record(u64::from_str_radix(&next.fingerprint()[..16],16).expect("SHA256 prefix"))}).unwrap_or(true);
                        let first=first&&noticed.write().insert(next.fingerprint());
                        summary.set(format!("문제 추가 {}개 · 수정 {}개 · 제외 {}개",changes.added.len(),changes.modified.len(),changes.removed.len()));
                        if apply_after_check {apply.call((next,false));}
                        else {candidate.set(Some(next)); if first {offered.set(true);} message.set("새 수업 내용이 있어요.".into());}
                    }
                    Ok(None)=>{candidate.set(None);offered.set(false);if requested {message.set("최신 내용이에요.".into());}}
                    Err(error)=>{if requested {message.set(error);}}
                }
            }
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        }
    }}});
    if session.is_none()||course.is_none(){return rsx!{}}
    let backup_user=session.as_ref().map(|session|session.user.id).unwrap_or(0);
    let backup_course=course.as_ref().map(|course|course.id.clone()).unwrap_or_default();
    let history_repository=course.as_ref().map(|course|course.repository.clone()).unwrap_or_default();
    rsx! {div {class:"content-update-controls",
        button {class:"course-refresh-icon",aria_label:"수업 업데이트",
            title:if applying(){"수업 적용 중이에요.".to_string()}else if checking(){"수업 업데이트를 확인하고 있어요.".to_string()}else if message().is_empty(){"수업 업데이트".to_string()}else{format!("수업 업데이트 · {}",message())},
            disabled:applying()||checking(),
            onclick:move |_|{refresh_and_apply.set(true);message.set("수업 업데이트를 확인하고 있어요.".into());manual+=1;},
            svg {width:"18",height:"18",view_box:"0 0 24 24",fill:"none",stroke:"currentColor",stroke_width:"2",stroke_linecap:"round",stroke_linejoin:"round","aria-hidden":"true",
                path {d:"M20 7v5h-5"}
                path {d:"M4 17v-5h5"}
                path {d:"M6.1 7a7 7 0 0 1 11.55-1.1L20 9M4 15l2.35 3.1A7 7 0 0 0 17.9 17"}
            }
        }
        span {class:"course-refresh-status",role:"status",aria_live:"polite","{message}"}
        details {summary {"수업 설정"}
            div {class:"content-update-menu",
            button {disabled:applying()||checking(),onclick:move |_|{refresh_and_apply.set(false);manual+=1;},"수업 업데이트 확인"}
            p {role:"status","{message}"}
            if candidate().is_some() {p {"{summary}"}}
            crate::change_history_ui::ChangeHistory {repository:history_repository}
            DraftBackups {user:backup_user,course:backup_course}
        if candidate().is_some() {
            button {aria_label:"수업 업데이트 적용",disabled:applying(),onclick:move |_|{if let Some(next)=candidate(){apply.call((next,false));}},"↥ 수업 업데이트"}
            if offered() {aside {role:"status",span {"새 수업 내용이 있어요."}button {onclick:move |_|offered.set(false),"닫기"}}}
        }
            }
        }
    }}
}


#[component]
fn DraftBackups(user:u64,course:String)->Element {
    let mut backups=use_signal(Vec::<molip_quest::drafts::RepositoryBackup>::new);
    let mut message=use_signal(String::new);
    rsx! {details {class:"draft-backups",ontoggle:move |_|{
        match molip_quest::drafts::repository_backups(user,&course) {Ok(saved)=>backups.set(saved),Err(error)=>message.set(error)}
    },summary {"업데이트 전 답안"}
        p {"이전 답안은 여기서 복사할 수 있어요."}
        for saved in backups() {details {summary {"{saved.step_id}"}
            pre {"{saved.draft.code}"}
            button {onclick:{let code=saved.draft.code.clone();move |_|{let result=arboard::Clipboard::new().and_then(|mut clipboard|clipboard.set_text(&code));message.set(if result.is_ok(){"이전 답안을 복사했어요.".into()}else{"복사하지 못했어요. 답안을 선택해 복사하세요.".into()});}},"답안 복사"}
        }}
        p {role:"status","{message}"}
    }}
}
