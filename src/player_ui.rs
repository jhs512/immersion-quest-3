use dioxus::prelude::*;
use molip_quest::{github_player::{self,Github,GithubUser},issue_progress::{self,LearningEvent,ProgressKey,StudyMode,EventKind},repository_course::{self,CourseManifest,Lesson,Task}};
use std::collections::HashMap;

#[derive(Clone,PartialEq)]
struct Session { github:Github,user:GithubUser }
#[derive(Clone,PartialEq)]
struct OpenLesson { course:CourseManifest,lesson:Lesson,events:Vec<LearningEvent>,mode:StudyMode,round:String,issue_url:Option<String> }

#[component]
pub fn RepositoryPlayer()->Element {
    let mut session=use_signal(||None::<Session>);
    let mut course=use_signal(||None::<CourseManifest>);
    let mut open=use_signal(||None::<OpenLesson>);
    let mut message=use_signal(String::new);
    let mut busy=use_signal(||false);
    let mut checked=use_signal(||false);
    let mut repositories=use_signal(molip_quest::course_authoring::catalog);
    let mut show_builder=use_signal(||false);
    let mut course_search=use_signal(String::new);
    let mut course_titles=use_signal(HashMap::<String,String>::new);
    let mut progress=use_signal(HashMap::<String,Vec<LearningEvent>>::new);
    let mut progress_requirements=use_signal(HashMap::<String,Vec<String>>::new);
    let mut refresh=use_signal(||0u64);
    let connect=move ||async move {
        checked.set(false);
        progress.set(HashMap::new());progress_requirements.set(HashMap::new());course.set(None);session.set(None);
        busy.set(true);message.set("gh 계정과 온라인 연결을 확인하고 있어요.".into());
        let github=Github::new();let gh=github.clone();
        match github_player::background(move||{let user=gh.user()?;let manifest=gh.installed_course(repository_course::initial_repository());Ok((user,manifest))}).await {
            Ok((user,manifest))=>{session.set(Some(Session{github,user}));match manifest {Ok(c)=>{course.set(Some(c));message.set(String::new());},Err(e)=>message.set(e)}},
            Err(e)=>{session.set(None);course.set(None);message.set(e);}
        }
        busy.set(false);
        checked.set(true);
    };
    let setup_preview=use_hook(||cfg!(debug_assertions)&&std::env::var_os("MOLIP_GH_SETUP_PREVIEW").is_some());
    use_future(move ||async move {
        if setup_preview {checked.set(true);}else{connect().await;}
    });
    use_effect(move ||{
        let repos=repositories();let Some(s)=session() else{return};
        for repository in repos {
            let github=s.github.clone();
            spawn(async move {let lookup=repository.clone();if let Ok(manifest)=github_player::background(move||github.course(&lookup)).await {course_titles.write().insert(repository,manifest.title);}});
        }
    });
    let update_key=format!("{}:{}",course().map(|course|course.repository).unwrap_or_default(),session().map(|s|s.user.id).unwrap_or(0));
    let updates=rsx! {ContentUpdates {key:"{update_key}",session:session(),course:course(),onapply:move |manifest:CourseManifest|{
        document::eval("window.molipAgent?.stop()");
        open.set(None); course.set(Some(manifest)); refresh+=1;
    }}};
    if let Some(selected)=open() {
        if let Some(session)=session() {
            let player_key=format!("{}:{}:{}:{}",session.user.id,selected.lesson.id,selected.mode.label(),selected.round);
            return rsx!{div {class:"repository-session", {updates} {rsx!{LessonPlayer {key:"{player_key}",session,selected,onback:move |_|{document::eval("window.molipAgent?.stop()");open.set(None);refresh+=1;}}}} }};
        }
    }
    rsx!{
        {updates}
        div {class:if session().is_none(){"repository-player needs-gh"}else{"repository-player"},
            header {class:"repository-header",h1 {"몰입 퀘스트 3"}
                if let Some(s)=session() {div {span {"gh · @{s.user.login}"}button {disabled:busy(),onclick:move |_|connect(),"gh 계정 다시 확인"}}}
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
                        button {class:if !show_builder()&&course().is_some_and(|c|c.repository==repository){"course-selected"}else{""},disabled:busy(),onclick:{let repository=repository.clone();move |_|{let Some(s)=session() else{return};let gh=s.github.clone();let repository=repository.clone();spawn(async move {busy.set(true);match github_player::background(move||gh.installed_course(&repository)).await {Ok(manifest)=>{course.set(Some(manifest));show_builder.set(false);message.set(String::new());},Err(e)=>message.set(e)}busy.set(false);});}},
                            strong {{course_titles().get(&repository).cloned().unwrap_or_else(||repository.split('/').next_back().unwrap_or(&repository).replace("mq3-course-", "").replace('-', " "))}}
                            small {"{repository}"}
                        }
                    }
                    if !repositories().iter().any(|repo|{let query=course_search().to_lowercase();repo.to_lowercase().contains(&query)||course_titles().get(repo).is_some_and(|title|title.to_lowercase().contains(&query))}) {p {class:"course-search-empty","일치하는 과정이 없어요."}}
                    }
                    button {class:"course-create",onclick:move |_|show_builder.set(!show_builder()),"코스 추가·만들기"}
                }
                main {class:"course-main",
                if show_builder() {if let Some(s)=session() {CourseBuilder {session:s,onselect:move |manifest:CourseManifest|{course.set(Some(manifest));repositories.set(molip_quest::course_authoring::catalog());show_builder.set(false);}}}}
                if !show_builder() {if let Some(manifest)=course() {
                if let Some(s)=session() {CourseProgressLoader {key:"{s.user.id}:{manifest.repository}:{manifest.lessons:?}:{refresh}",session:s,course:manifest.clone(),onloaded:move |records:github_player::CourseProgress|{progress.set(records.events);progress_requirements.set(records.required);}}}
                section {class:"course-catalog",h2 {"{manifest.title}"}p {"{manifest.description}"}
                    {let records=progress();let total=manifest.lessons.iter().filter(|l|l.required).count();let complete=manifest.lessons.iter().filter(|l|l.required&&records.get(&l.id).is_some_and(|e|issue_progress::status(e,&l.revision,progress_requirements().get(&l.id).map(Vec::as_slice).unwrap_or(&[])).current)).count();rsx!{p {class:"study-progress","최신 버전 완료: 필수 수업 {complete} / {total}"}}}
                    p {"추천 순서와 상관없이 어떤 수업이든 선택할 수 있어요."}
                    a {href:format!("https://github.com/{}/issues",manifest.repository),target:"_blank",rel:"noopener noreferrer","코스의 공개 학습 기록"}
                    div {class:"repository-lessons",
                        for (index,reference) in manifest.lessons.iter().enumerate() {
                            article {class:"card lesson-card",key:"{reference.id}",
                                span {class:"badge","수업 {index+1}"}h3 {"{reference.title}"}
                                p {"버전 {reference.revision}"}
                                {let records=progress().get(&reference.id).cloned().unwrap_or_default();let state=issue_progress::status(&records,&reference.revision,progress_requirements().get(&reference.id).map(Vec::as_slice).unwrap_or(&[]));rsx!{p {class:"lesson-status",if state.current {"✓ 최신 버전 완료"} else if state.completed {"✓ 완료 보존 · 추가 학습 있음"} else if !records.is_empty() {"학습 중"} else {"아직 시작하지 않았어요"}}p {"풀모드 {state.full_completions}회 · 복습 {state.review_completions}회"}}}
                                if !reference.prerequisites.is_empty() {p {class:"prerequisite",{format!("선수 학습: {}",reference.prerequisites.iter().filter_map(|id|manifest.lessons.iter().find(|l|l.id==*id)).map(|l|l.title.clone()).collect::<Vec<_>>().join(", "))}}}
                                for mode in [StudyMode::Full,StudyMode::Review].into_iter().filter(|mode|*mode!=StudyMode::Review||reference.review_enabled) {
                                    button {class:if mode==StudyMode::Full {"primary"}else{""},disabled:busy(),onclick:{let manifest=manifest.clone();let reference=reference.clone();move |_|{
                                        let manifest=manifest.clone();let reference=reference.clone();let Some(s)=session() else{return};
                                        spawn(async move {
                                            busy.set(true);message.set("수업과 진도를 불러오고 있어요.".into());let gh=s.github.clone();let user=s.user.clone();let c=manifest.clone();let r=reference.clone();
                                            let result=github_player::background(move||{
                                                gh.ensure_user(user.id)?;let lesson=gh.installed_lesson(&c,&r)?;
                                                let key=ProgressKey{user_id:user.id,course_id:c.id.clone(),lesson_id:lesson.id.clone()};
                                                let issue=gh.find_issue(&c.repository,&user,&key)?;
                                                let events=if let Some(issue)=&issue {gh.events(&c.repository,issue,&key)?}else{vec![]};
                                                Ok((lesson,events,issue.map(|i|i.html_url)))
                                            }).await;
                                            match result {
                                                Ok((lesson,mut events,url))=>{
                                                    let unfinished=events.iter().rev().find(|e|e.kind==EventKind::Started&&e.mode==mode&&e.revision==lesson.revision&&!events.iter().any(|done|done.kind==EventKind::Completed&&done.round==e.round)).map(|e|e.round.clone());
                                                    let round=unfinished.unwrap_or_else(issue_progress::new_id);
                                                    if !events.iter().any(|e|e.round==round) {
                                                        let event=LearningEvent::new(ProgressKey{user_id:s.user.id,course_id:manifest.id.clone(),lesson_id:lesson.id.clone()},&lesson.revision,mode,&round,EventKind::Started);
                                                        let gh=s.github.clone();let user=s.user.clone();let repo=manifest.repository.clone();let title=lesson.title.clone();
                                                        match github_player::background(move||gh.append(&repo,&user,&title,&event)).await {
                                                            Ok((issue,latest))=>{events=latest;open.set(Some(OpenLesson{course:manifest,lesson,events,mode,round,issue_url:Some(issue.html_url)}));message.set(String::new());},Err(e)=>message.set(e),
                                                        }
                                                    } else {open.set(Some(OpenLesson{course:manifest,lesson,events,mode,round,issue_url:url}));message.set(String::new());}
                                                },Err(e)=>message.set(e),
                                            }
                                            busy.set(false);
                                        });
                                    }},"{mode.label()} 시작"}
                                }
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
fn CourseBuilder(session:Session,onselect:EventHandler<CourseManifest>)->Element {
    use molip_quest::course_authoring::{self,CourseDraft};
    let mut repository=use_signal(String::new);
    let mut name=use_signal(String::new);let mut title=use_signal(String::new);let mut description=use_signal(String::new);
    let mut lesson_text=use_signal(String::new);let mut references=use_signal(Vec::<repository_course::LessonRef>::new);
    let mut message=use_signal(String::new);let mut busy=use_signal(||false);
    let mut publisher=use_signal(String::new);let mut published=use_signal(||false);
    let mut prepared=use_signal(||None::<CourseDraft>);
    rsx!{section {class:"card course-builder",h2 {"코스 추가·만들기"}
        h3 {"공개 코스 불러오기"}
        label {"코스 저장소 · owner/repository" input {value:repository(),oninput:move |e|repository.set(e.value())}}
        button {disabled:busy(),onclick:{let gh=session.github.clone();move |_|{let gh=gh.clone();async move {busy.set(true);let repo=repository();match github_player::background(move||{let c=gh.installed_course(&repo)?;course_authoring::remember(&repo)?;Ok(c)}).await {Ok(c)=>onselect.call(c),Err(e)=>message.set(e)}busy.set(false);}}},"코스 불러오기"}
        h3 {"새 공개 코스 만들기"}
        p {"수업을 추가하고 순서를 정하세요. 게시 전에 계정과 구성을 확인할 수 있어요."}
        label {"새 저장소 이름" input {value:name(),oninput:move |e|{name.set(e.value());prepared.set(None);}}}
        label {"코스 제목" input {value:title(),oninput:move |e|{title.set(e.value());prepared.set(None);}}}
        label {"코스 소개" textarea {value:description(),oninput:move |e|{description.set(e.value());prepared.set(None);}}}
        label {"수업 저장소와 버전 · owner/repository@v1.0.0" input {value:lesson_text(),oninput:move |e|lesson_text.set(e.value())}}
        button {disabled:busy(),onclick:{let gh=session.github.clone();move |_|{let gh=gh.clone();async move {busy.set(true);let text=lesson_text();match github_player::background(move||course_authoring::reference(&gh,&text)).await {Ok(r)=>{if references().iter().any(|old|old.id==r.id) {message.set("이미 추가한 수업이에요.".into())}else{references.write().push(r);lesson_text.set(String::new());prepared.set(None);}},Err(e)=>message.set(e)}busy.set(false);}}},"수업 추가"}
        ol {for (index,reference) in references().iter().enumerate() {li {key:"{reference.id}","{reference.title} · {reference.revision}"
            button {disabled:index==0,onclick:move |_|{references.write().swap(index,index-1);prepared.set(None);},"위로"}
            button {disabled:index+1>=references().len(),onclick:move |_|{references.write().swap(index,index+1);prepared.set(None);},"아래로"}
            button {onclick:move |_|{references.write().remove(index);prepared.set(None);},"제외"}
        }}}
        button {disabled:busy()||references().is_empty(),onclick:{let owner=session.user.login.clone();move |_|{let owner=owner.clone();async move {
            let draft=CourseDraft{owner,name:name().trim().into(),title:title().trim().into(),description:description(),lessons:references()};
            if let Err(e)=draft.manifest(){message.set(e);return}
            busy.set(true);match github_player::background(course_authoring::publisher).await {Ok(account)=>{publisher.set(account);prepared.set(Some(draft));message.set("공개할 계정과 구성을 확인하세요.".into());},Err(e)=>message.set(e)}busy.set(false);
        }}},"게시 구성 확인"}
        if let Some(draft)=prepared() {
            p {strong {"게시 계정: @{publisher}"} " · 공개 저장소: {draft.owner}/{draft.name}"}
            p {"수업 {draft.lessons.len()}개를 이 순서로 연결해요. 수업 본문은 복사하지 않아요."}
            details {summary {"게시할 구성정보 보기"}pre {"{serde_json::to_string_pretty(&draft.manifest().unwrap()).unwrap_or_default()}"}}
            button {class:"primary",disabled:busy()||publisher()!=session.user.login,onclick:{let uid=session.user.id;move |_|async move {let Some(draft)=prepared() else{return};busy.set(true);match github_player::background(move||course_authoring::publish(&draft,uid)).await {Ok(url)=>{published.set(true);message.set(format!("공개 코스를 게시했어요. {url}"));repository.set(url.trim_start_matches("https://github.com/").into());},Err(e)=>message.set(e)}busy.set(false);}},"이 구성으로 공개 코스 게시"}
        }
        if published() {p {"이제 위의 코스 불러오기로 새 코스를 열 수 있어요."}}
        p {role:"status","{message}"}
    }}
}

#[component]
fn LessonPlayer(session:Session,selected:OpenLesson,onback:EventHandler<()>)->Element {
    let mut events=use_signal(||selected.events.clone());
    let mut activity_message=use_signal(String::new);
    let mut task_index=use_signal(||0usize);
    let mut section_index=use_signal(||0usize);
    use_future({let session=session.clone();let selected=selected.clone();move ||{let session=session.clone();let selected=selected.clone();async move {
        if selected.mode==StudyMode::Full {if let Some(first)=selected.lesson.sections.first() {
            let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::Viewed);event.task_id=Some(first.id.clone());
            match github_player::background(move||session.github.append(&selected.course.repository,&session.user,&selected.lesson.title,&event)).await {Ok((_,latest))=>events.set(latest),Err(e)=>activity_message.set(e)}
        }}
    }}});
    let state=issue_progress::status(&events(),&selected.lesson.revision,&selected.lesson.required_tasks());
    let passed=issue_progress::passed_for_study(&events(),&selected.lesson.revision,selected.mode,&selected.round);
    let required=selected.lesson.required_tasks();
    let count=required.iter().filter(|id|passed.contains(*id)).count();
    let view=if selected.mode==StudyMode::Full && section_index()<selected.lesson.sections.len() {None}else{Some(selected.lesson.tasks[task_index().min(selected.lesson.tasks.len()-1)].clone())};
    let is_task=view.is_some();
    let record_view={let session=session.clone();let selected=selected.clone();move |index:usize|{
        let session=session.clone();let selected=selected.clone();
        spawn(async move {
            let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::Viewed);
            event.task_id=Some(selected.lesson.sections[index].id.clone());
            let title=selected.lesson.title.clone();let repo=selected.course.repository.clone();
            match github_player::background(move||session.github.append(&repo,&session.user,&title,&event)).await {
                Ok((_,latest))=>{events.set(latest);section_index.set(index);activity_message.set(String::new());},Err(e)=>activity_message.set(e)
            }
        });
    }};
    rsx!{
        div {class:if is_task{"repository-study is-task"}else{"repository-study"},
            header {class:"repository-header",button {onclick:move |_|onback.call(()),"← 코스 수업 목록"}h1 {"{selected.lesson.title}"}span {"{selected.mode.label()} · @{session.user.login}"}}
            section {class:"study-progress",span {"이번 학습: 필수 문제 {count} / {required.len()}"}
                if state.current {strong {"✓ 최신 버전 완료"}} else if state.completed {strong {"✓ 이전 완료 보존 · 추가 학습 있음"}}
                span {"학습 완료 {state.full_completions}회 · 복습 완료 {state.review_completions}회"}
                if let Some(url)=&selected.issue_url {a {href:url.clone(),target:"_blank",rel:"noopener noreferrer","내 진도 이슈"}}
            }
            if let Some(task)=&view {crate::lesson_outline::LessonOutline {lesson:selected.lesson.clone(),task_id:task.id.clone()}}
            nav {class:"study-navigation",
                if selected.mode==StudyMode::Full {
                    for (index,section) in selected.lesson.sections.iter().enumerate() {button {class:if section_index()==index {"selected"}else{""},onclick:{let record_view=record_view.clone();move |_|record_view(index)},"{section.title}"}}
                }
                for (index,task) in selected.lesson.tasks.iter().enumerate() {button {class:if view.as_ref().is_some_and(|t|t.id==task.id){"selected"}else{""},onclick:move |_|{task_index.set(index);section_index.set(usize::MAX);},if passed.contains(&task.id){"✓ "}if !task.required{"도전 · "}"문제 {index+1} · {task.title}"}}
            }
            if let Some(task)=view {
                RepositoryTask {key:"{selected.round}:{task.id}",session:session.clone(),selected:selected.clone(),task,events,
                    onrecord:move |new_events:Vec<LearningEvent>|{if let Some(first)=new_events.first(){let key=first.key.clone();events.set(issue_progress::merge(events().into_iter().chain(new_events),&key));}}}
                div {class:"task-paging",
                    button {disabled:task_index()==0,onclick:move |_|{task_index-=1;},"← 이전 문제"}
                    span {"문제 {task_index()+1} / {selected.lesson.tasks.len()}"}
                    button {disabled:task_index()+1>=selected.lesson.tasks.len(),onclick:move |_|{task_index+=1;},"다음 문제 →"}
                }
            } else {
                article {class:"card repository-reading",
                    h2 {"{selected.lesson.sections[section_index()].title}"}
                    crate::ui::Markdown {text:selected.lesson.sections[section_index()].body.clone()}
                    button {class:"primary",onclick:{let record_view=record_view.clone();let len=selected.lesson.sections.len();move |_|{let next=section_index()+1;if next<len{record_view(next)}else{section_index.set(next);}}},"다음 학습으로"}
                    p {"개념 읽기는 완료 조건이 아니에요. 문제로 바로 이동해도 돼요."}
                }
            }
            p {class:"study-activity",role:"status","{activity_message}"}
        }
    }
}

#[component]
fn RepositoryTask(session:Session,selected:OpenLesson,task:Task,events:Signal<Vec<LearningEvent>>,onrecord:EventHandler<Vec<LearningEvent>>)->Element {
    let key=molip_quest::drafts::repository_scope(&ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},selected.mode,&task.id);
    let previous_key=format!("repo:{}:{}:{}:{}:{}",session.user.id,selected.course.id,selected.lesson.id,selected.round,task.id);
    let initial=use_hook(||molip_quest::drafts::load(&key).ok().flatten().or_else(||molip_quest::drafts::load(&previous_key).ok().flatten()).map(|d|d.code).unwrap_or_else(||task.starter_code.clone()));
    let mut code=use_signal(||initial.clone());let mut reset=use_signal(||0u64);
    let has_example=task.has_runnable_example();
    let mut example_source=use_signal(||task.example_for_answer(&initial).unwrap_or_default());
    let mut git_practice=use_signal(||None::<crate::git_terminal_ui::Practice>);
    let mut git_control=use_signal(||None::<crate::git_terminal_ui::TerminalControl>);
    let mut input=use_signal(||task.tests.first().map(|t|t.input.clone()).unwrap_or_default());
    let mut busy=use_signal(||false);let mut message=use_signal(String::new);let mut output=use_signal(String::new);
    let mut preview=use_signal(String::new);
    let ordered_task=task.clone();
    use_effect(move||{if ordered_task.example_order_marker.is_some(){match ordered_task.example_for_answer(&code()){Ok(source)=>{if *example_source.peek()!=source{example_source.set(source);reset.with_mut(|version|*version+=1);}},Err(error)=>message.set(error)}}});

    let mut narrating=use_signal(||false);
    let mut show_solution=use_signal(||false);
    use_drop(||{document::eval("window.molipAgent?.stop()");});
    let mut execution_id=use_signal(||0u64);
    let mut execution_state=use_signal(||"idle");
    let mut execution_seconds=use_signal(||0u64);
    let mut history_saves=use_signal(||0usize);
    let mut history_message=use_signal(String::new);
    use_effect(|| { document::eval("const s=document.querySelector('select.repository-narration-rate');if(s&&window.molipVoice)s.value=String(molipVoice.rate);"); });
    let required=selected.lesson.required_tasks();
    let filename=if task.git_terminal.is_some(){"Git 터미널".to_string()}else if task.interaction.is_some()&&!has_example{"답안".to_string()}else if task.entry_file.is_empty(){task.language.filename().to_string()}else{task.entry_file.clone()};
    // Show the data this problem reads before other files bundled with the lesson.
    let mut provided_files=task.files.iter().map(|(name,body)|{
        let used=task.starter_code.contains(name.as_str())||task.solution.contains(name.as_str());
        (name.clone(),body.clone(),used)
    }).collect::<Vec<_>>();
    provided_files.sort_by(|a,b|b.2.cmp(&a.2).then_with(||a.0.cmp(&b.0)));
    let explanation=issue_progress::explanation_info(&events(),&task.id);
    let record_explanation={let session=session.clone();let selected=selected.clone();let task_id=task.id.clone();move ||{
        let mut event=LearningEvent::new(ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::ExplanationViewed);
        event.task_id=Some(task_id.clone());
        event.success_before_view=events().iter().any(|e|e.kind==EventKind::Attempt&&e.passed&&e.task_id.as_deref()==Some(&task_id));
        let gh=session.github.clone();let user=session.user.clone();let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
        spawn(async move {match github_player::background(move||gh.append(&repo,&user,&title,&event)).await {Ok((_,latest))=>onrecord.call(latest),Err(e)=>history_message.set(format!("해설 이력을 저장하지 못했어요. {e}"))}});
    }};
    rsx!{
        article {class:"lesson repository-task","data-task-id":task.id.clone(),"data-narrating":narrating().to_string(),"data-git-ready":git_practice().is_some().to_string(),
            section {class:"problem-pane",h2 {"{task.title}"}crate::ui::Markdown{text:task.goal.clone()}
                for material in &task.supporting_materials {
                    SupportingMaterialPanel {key:"{task.id}/{material.id}", material:material.clone()}
                }
                if !task.required {p {class:"challenge-note","선택 도전이에요. 수업 완료 후에 풀어도 돼요."}}
                if !task.hints.is_empty() {div {class:"task-hints",for (index,hint) in task.hints.iter().enumerate(){details {summary {"힌트 {index+1}"}crate::ui::Markdown{text:hint.clone()}}}}}
                button {onclick:{let record=record_explanation.clone();move |_|{if !show_solution(){record();}show_solution.set(!show_solution());}},"정답과 풀이 보기"}
                if show_solution() {crate::ui::Markdown{text:format!("```{}\n{}\n```",task.language.editor(),task.solution)}}
                if explanation.before_success||explanation.after_success {details {class:"explanation-info",summary {"학습 정보"}
                    if explanation.before_success {span {title:"풀이 전에 해설을 함께 봤어요.",aria_label:"풀이 전 해설 확인","💡"}}
                    if explanation.after_success {span {title:"성공 후 해설을 다시 봤어요.",aria_label:"성공 후 해설 확인","↺"}}
                }}
                if !task.narration.is_empty() {
                    button {disabled:busy()||narrating(),onclick:{let actions=task.narration.clone();let record=record_explanation.clone();let needs_git=task.git_terminal.is_some();move |_|{
                        record();let student_code=code();let student_example=example_source();let student_output=output();let student_input=input();let student_preview=preview();let student_message=message();let student_state=execution_state();let student_seconds=execution_seconds();
                        narrating.set(true);let actions=actions.clone();
                        spawn(async move {
                            let script=format!("(async()=>{{try{{const root=document.querySelector('.repository-task');const until=Date.now()+45000;while(root?.isConnected&&(root.dataset.narrating!=='true'||({needs_git}&&!window.molipGitTutor))){{if(Date.now()>until)throw new Error('Git 시연을 준비하지 못했어요.');await new Promise(requestAnimationFrame);}}if(root?.isConnected)await window.molipAgent?.runExplanation({});}}finally{{dioxus.send(true);}}}})();",serde_json::to_string(&actions).unwrap_or_else(|_|"[]".into()));
                            let mut bridge=document::eval(&script);let _=bridge.recv::<bool>().await;
                            execution_id+=1;execution_state.set(student_state);execution_seconds.set(student_seconds);busy.set(false);code.set(student_code);example_source.set(student_example);input.set(student_input);output.set(student_output);preview.set(student_preview);message.set(student_message);if !needs_git {reset+=1;}narrating.set(false);
                        });
                    }},"해설 재생 · 정답 실행"}
                    button {"data-explanation-stop":"true",onclick:move |_|{document::eval("window.molipAgent?.stop()");},"해설 멈춤"}
                    label {class:"narration-speed","말 속도 "
                        select {class:"assistant-rate repository-narration-rate",aria_label:"해설 말 속도",onchange:move |e|{document::eval(&format!("window.molipVoice?.setRate({});",e.value()));},
                            for rate in ["0.75","1","1.25","1.5","1.75","2"] {option {value:rate,selected:rate=="1.5","{rate}배"}}
                        }
                    }
                }
                if !provided_files.is_empty() {details {class:"provided-files",summary {"함께 제공한 파일"}
                    for (name,body,used) in &provided_files {details {class:"provided-file",key:"{name}",summary {{format!("{name}{}",if *used {" · 이 문제에서 사용"}else{""})}}crate::ui::Markdown{text:format!("```\n{body}\n```")}}}
                }}
            }
            div {class:"split-handle split-col",role:"separator",tabindex:0,aria_label:"문제와 코드 패널 크기 조절",aria_orientation:"vertical"}
            section {class:"coding-pane",div {class:"pane-heading",strong {"{filename}"}
                div {class:"pane-actions",
                    button {disabled:busy()||narrating(),onclick:{let starter=task.starter_code.clone();let example=task.example_for_answer(&task.starter_code).unwrap_or_default();let key=key.clone();move |_|{
                        if narrating(){return;}
                        if let Some(control)=git_control() {
                            busy.set(true);message.set("Git 실습을 초기화하고 있어요.".into());
                            let key=key.clone();let starter=starter.clone();
                            spawn(async move {
                                match github_player::background(move||control.shutdown()).await {
                                    Ok(())=>{git_practice.set(None);git_control.set(None);code.set(starter);let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());reset+=1;message.set(String::new());},Err(error)=>message.set(error)
                                }
                                busy.set(false);
                            });
                        }else{code.set(starter.clone());example_source.set(example.clone());reset+=1;let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());}
                    }},"초기화"}
                    if task.git_terminal.is_none()&&(task.interaction.is_none()||has_example) {
                    button {disabled:busy()||(task.predict_before_run&&!narrating()&&code().is_empty()),onclick:{let task=task.clone();let github=session.github.clone();let user=session.user.clone();let selected=selected.clone();move |_|{let task=task.clone();let github=github.clone();let user=user.clone();let selected=selected.clone();async move {
                        busy.set(true);execution_id+=1;execution_state.set("running");execution_seconds.set(0);
                        message.set("코드를 실행하고 있어요.".into());output.set(String::new());preview.set(String::new());
                        let source=if has_example{example_source()}else{code()};let prediction=task.predict_before_run.then(||code());let demonstration=narrating();let input=input();let started=std::time::Instant::now();let run_id=execution_id();
                        let timer=spawn(async move {loop {tokio::time::sleep(std::time::Duration::from_secs(1)).await;if execution_id()!=run_id{break;}execution_seconds+=1;}});
                        // Local execution never waits for GitHub. append() still authenticates
                        // the expected account before recording the separate history operation.
                        let result=if has_example{molip_quest::lesson_runner::run_example(&task,&source,&input).await}else{molip_quest::lesson_runner::run(&task,&source,&input).await};
                        timer.cancel();
                        if execution_id()!=run_id {return;}
                        match result {
                            Ok(result)=>{
                                output.set(format!("{}\n{}",result.stdout,result.stderr));
                                execution_state.set(if result.success{"finished"}else{"failed"});
                                message.set(if result.success {format!("실행을 마쳤어요. {:.2}초 걸렸어요. 제출해서 모든 검사를 확인하세요.",started.elapsed().as_secs_f64())}else{"실행에 실패했어요. 결과를 확인하세요.".into()});
                                preview.set(result.artifacts.into_iter().find_map(|a|match a {molip_quest::runner::Artifact::Html{srcdoc,..}=>Some(srcdoc),_=>None}).unwrap_or_default());
                            },
                            Err(error)=>{execution_state.set("failed");message.set(error);}
                        }
                        busy.set(false);
                        if demonstration{return;}
                        let mut event=LearningEvent::new(ProgressKey{user_id:user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()},&selected.lesson.revision,selected.mode,&selected.round,EventKind::ExampleRun);event.task_id=Some(task.id.clone());event.prediction=prediction;
                        let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
                        history_saves+=1;
                        spawn(async move {
                            match github_player::background(move||github.append(&repo,&user,&title,&event)).await {
                                Ok((_,latest))=>onrecord.call(latest),
                                Err(error)=>history_message.set(format!("실행 이력을 저장하지 못했어요. {error}"))
                            }
                            history_saves-=1;
                        });
                    }}},"코드 실행"}
                    }
                    button {class:"primary",disabled:busy()||narrating()||(task.git_terminal.is_some()&&git_practice().is_none()),onclick:{let task=task.clone();let session=session.clone();let selected=selected.clone();let required=required.clone();move |_|{let task=task.clone();let session=session.clone();let selected=selected.clone();let required=required.clone();async move {
                        busy.set(true);message.set("검사하고 있어요.".into());let gh=session.github.clone();let uid=session.user.id;
                        let authenticated=github_player::background(move||gh.ensure_user(uid)).await;
                        match authenticated {
                            Err(e)=>message.set(e),Ok(())=>match if task.git_terminal.is_some()&&task.interaction.is_none() {
                                let practice=git_practice();let checks=task.git_checks.clone();
                                github_player::background(move||{
                                    let practice=practice.ok_or("Git 터미널이 준비되지 않았어요.")?;
                                    let practice=practice.lock().unwrap_or_else(|e|e.into_inner());
                                    if let Some(checks)=checks {practice.check(&checks)}else{practice.check_exercise()}
                                }).await
                            }else{molip_quest::lesson_runner::check(&task,&code()).await} {
                                Err(e)=>message.set(e),Ok(report)=>{
                                    output.set(report.cases.iter().enumerate().map(|(i,c)|format!("검사 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed{"통과"}else{"다시 풀기"},c.input,c.expected,c.stdout,c.stderr)).collect::<Vec<_>>().join("\n\n"));
                                    let key=ProgressKey{user_id:session.user.id,course_id:selected.course.id.clone(),lesson_id:selected.lesson.id.clone()};
                                    let mut event=LearningEvent::new(key.clone(),&selected.lesson.revision,selected.mode,&selected.round,EventKind::Attempt);event.task_id=Some(task.id.clone());event.passed=report.passed;
                                    let github=session.github.clone();let user=session.user.clone();let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
                                    match github_player::background(move||github.append(&repo,&user,&title,&event)).await {
                                        Err(e)=>message.set(format!("검사 결과를 GitHub에 저장하지 못했어요. {e}")),
                                        Ok((_,latest))=>{
                                            let passed=issue_progress::passed_for_study(&latest,&selected.lesson.revision,selected.mode,&selected.round);
                                            let complete=required.iter().all(|id|passed.contains(id));
                                            if complete && !latest.iter().any(|e|e.kind==EventKind::Completed&&e.round==selected.round) {
                                                let mut done=LearningEvent::new(key,&selected.lesson.revision,selected.mode,&selected.round,EventKind::Completed);done.required=required;
                                                let gh=session.github.clone();let user=session.user.clone();let repo=selected.course.repository.clone();let title=selected.lesson.title.clone();
                                                match github_player::background(move||gh.append(&repo,&user,&title,&done)).await {
                                                    Ok((_,latest))=>{onrecord.call(latest);message.set("수업 완료! 학습·복습 기록을 GitHub에 저장했어요.".into());},Err(e)=>{onrecord.call(latest);message.set(format!("문제는 기록했지만 수업 완료 저장은 다시 시도해야 해요. {e}"));}
                                                }
                                            }else{onrecord.call(latest);message.set(if report.passed{"통과했어요. GitHub에 진도를 저장했어요."}else{"다시 풀어보세요. 시도 기록을 GitHub에 저장했어요."}.into());}
                                        }
                                    }
                                }
                            }
                        }busy.set(false);
                    }}},"제출"}
                }
            }
            div {class:if (task.git_terminal.is_some()||has_example)&&task.interaction.is_some(){"editor-pane interaction-example-editor"}else{"editor-pane"},style:if (task.git_terminal.is_some()||has_example)&&task.interaction.is_some(){"display:grid;grid-template-rows:minmax(0,2fr) minmax(0,3fr);gap:6px"}else{""},
                if let Some(exercise)=task.git_terminal.clone() {
                    div {style:if narrating(){"display:none"}else if task.interaction.is_some(){"min-height:0;overflow:hidden"}else{"height:100%"},
                        {rsx!{crate::git_terminal_ui::GitTerminal {key:"git-{reset}",exercise:exercise.clone(),demo:false,scope:Some(key.clone()),fresh:reset()>0,onready:move |practice|git_practice.set(Some(practice)),oncontrol:move |control|git_control.set(Some(control))}}}
                    }
                    if narrating() {div {style:if task.interaction.is_some(){"min-height:0;overflow:hidden"}else{"height:100%"},crate::git_terminal_ui::GitTerminal {exercise,demo:true,onready:move |_|{},oncontrol:move |_|{}}}}
                }else if has_example {
                    textarea {class:"code-editor","data-code-editor":task.language.editor(),"data-editor-value":example_source(),"data-editor-reset":reset().to_string(),aria_label:"수업 예제 코드",initial_value:task.example_for_answer(&initial).unwrap_or_default(),readonly:true,spellcheck:false,oninput:move |e|example_source.set(e.value())}
                }else if task.interaction.is_none() {
                textarea {class:"code-editor","data-code-editor":if task.entry_file.ends_with(".jsx"){"javascript"}else{task.language.editor()},"data-editor-value":code(),"data-editor-reset":reset().to_string(),aria_label:"수업 코드",initial_value:initial.clone(),spellcheck:false,oninput:{let key=key.clone();move |e|{code.set(e.value());if !narrating(){let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());}}}}
                }
                if let Some(interaction)=task.interaction.clone() {
                    div {class:if task.git_terminal.is_some()||has_example{"interaction-example-answer"}else{""},style:if task.git_terminal.is_some()||has_example{"min-height:0;overflow:hidden"}else{"height:100%;min-height:0"},
                        crate::interaction_ui::InteractionEditor {interaction,value:code(),disabled:busy()||narrating(),onchange:{let key=key.clone();move |value:String|{code.set(value);if !narrating(){let _=molip_quest::drafts::save(&key,&code(),&HashMap::new());}}}}
                    }
                }
            }
            div {class:"split-handle split-row",role:"separator",tabindex:0,aria_label:"코드와 실행 결과 패널 크기 조절",aria_orientation:"horizontal"}
            section {class:"result-pane","data-execution-id":execution_id().to_string(),"data-execution-state":execution_state(),aria_busy:busy(),h3 {if has_example{"실행·채점 결과"}else if task.interaction.is_some(){"채점 결과"}else{"실행 결과"}}
                if task.git_terminal.is_none()&&(task.interaction.is_none()||has_example) {
                details {class:"run-input",open:task.tests.iter().any(|case|!case.input.is_empty()),
                    summary {"실행 입력"}
                    label {span {"프로그램에 전달할 입력"} textarea {aria_label:"실행 입력",initial_value:input(),oninput:move |e|input.set(e.value())}}
                }
                }
                p {class:"execution-status",role:"status",
                    if execution_state()=="running" {span {class:"execution-spinner",aria_hidden:"true"} {format!("코드를 실행하고 있어요. {}초 지났어요.",execution_seconds())}}else {"{message}"}
                }
                pre {class:"output","{output}"}
                if history_saves()>0 {p {class:"history-sync",role:"status","실행 이력을 저장하고 있어요. 다음 코드를 실행해도 돼요."}}
                if !history_message().is_empty() {p {class:"history-sync warning",role:"status","{history_message}"}}
                if !preview().is_empty() && task.language==repository_course::TaskLanguage::Web {
                    iframe {title:"수업 웹 미리보기","sandbox":"allow-scripts allow-forms",srcdoc:preview(),style:"width:100%;height:400px;border:1px solid #456;"}
                }
            }
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
fn ContentUpdates(session:Option<Session>,course:Option<CourseManifest>,onapply:EventHandler<CourseManifest>)->Element {
    use molip_quest::{content_updates,updater};
    let mut candidate=use_signal(||None::<content_updates::Snapshot>);
    let mut offered=use_signal(||false);
    let mut message=use_signal(String::new);
    let mut manual=use_signal(||0u64);
    let mut applying=use_signal(||false);
    let mut noticed=use_signal(std::collections::HashSet::<String>::new);
    let mut summary=use_signal(String::new);
    use_future({let session=session.clone();let course=course.clone();move ||{let session=session.clone();let course=course.clone();async move {
        let (Some(session),Some(course))=(session,course) else{return};
        let started=std::time::Instant::now();let mut schedule=updater::UpdateSchedule::default();let mut seen=0;
        loop {
            let request=*manual.peek(); let requested=request!=seen;
            if schedule.begin(started.elapsed().as_secs(),requested) {
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
                match result {
                    Ok(Some((next,changes)))=>{
                        let notices=molip_quest::data_dir().map(|dir|dir.join("content-update-notices.json"));
                        let first=notices.and_then(|path|{let mut notices=updater::UpdateNotices::open(&path)?;notices.record(u64::from_str_radix(&next.fingerprint()[..16],16).expect("SHA256 prefix"))}).unwrap_or(true);
                        let first=first&&noticed.write().insert(next.fingerprint());
                        summary.set(format!("문제 추가 {}개 · 수정 {}개 · 제외 {}개",changes.added.len(),changes.modified.len(),changes.removed.len()));
                        candidate.set(Some(next)); if first {offered.set(true);} message.set("새 수업 내용이 있어요.".into());
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
    let apply=move |_|{
        let Some(next)=candidate() else{return};let Some(session)=session.clone() else{return};
        if applying(){return;} applying.set(true);
        spawn(async move {
            // Restore the student document before saving the update backup.
            let mut bridge=document::eval("window.molipAgent?.stop();requestAnimationFrame(()=>requestAnimationFrame(()=>dioxus.send(true)))");
            if !matches!(bridge.recv::<bool>().await,Ok(true)) {message.set("해설을 닫고 다시 업데이트하세요.".into());applying.set(false);return;}
            let manifest=next.course().clone();
            let result=github_player::background(move||{
                session.github.ensure_user(session.user.id)?;
                molip_quest::drafts::backup_repository(session.user.id,&next.course().id,&next.fingerprint())?;
                content_updates::installed_store()?.apply(&next)
            }).await;
            match result {Ok(())=>{candidate.set(None);offered.set(false);onapply.call(manifest);},Err(error)=>message.set(error)}
            applying.set(false);
        });
    };
    rsx! {div {class:"content-update-controls",
        details {summary {"수업 설정"}
            button {disabled:applying(),onclick:move |_|manual+=1,"수업 업데이트 확인"}
            p {role:"status","{message}"}
            if candidate().is_some() {p {"{summary}"}}
            crate::change_history_ui::ChangeHistory {repository:history_repository}
            DraftBackups {user:backup_user,course:backup_course}
        }
        if candidate().is_some() {
            button {aria_label:"수업 업데이트 적용",disabled:applying(),onclick:apply,"↥ 수업 업데이트"}
            if offered() {aside {role:"status",span {"새 수업 내용이 있어요."}button {onclick:move |_|offered.set(false),"닫기"}}}
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
