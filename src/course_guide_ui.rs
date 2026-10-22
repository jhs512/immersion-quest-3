use dioxus::prelude::*;
use molip_quest::{course_guide::CourseGuide,repository_course::CourseManifest};

#[component]
pub fn CourseGuideButton(course:CourseManifest)->Element {
    let mut open=use_signal(||false);
    let mut guide=use_signal(||None::<CourseGuide>);
    let mut loading=use_signal(||false);
    let mut playing=use_signal(||false);
    let mut status=use_signal(String::new);
    use_effect(move||{document::eval(if open(){"document.querySelector('#course-guide-dialog')?.showModal()"}else{"document.querySelector('#course-guide-dialog')?.close()"});});
    use_drop(move||{if *playing.peek(){document::eval("window.molipAgent?.stop()");}});
    let play=use_callback(move |only:Option<usize>|{
        let Some(guide)=guide() else{return;};if playing(){return;}
        let actions=guide.narration(only);playing.set(true);status.set("AI 해설을 준비하고 있어요.".into());
        spawn(async move {
            let script=format!("(async()=>{{try{{dioxus.send({{result:await window.molipAgent.runOverview({},document.querySelector('#course-guide-dialog'))}});}}catch(error){{dioxus.send({{error:String(error)}});}}}})()",serde_json::to_string(&actions).unwrap());
            let mut bridge=document::eval(&script);
            status.set(match bridge.recv::<serde_json::Value>().await {
                Ok(value) if value["error"].is_string()=>"해설을 재생하지 못했어요. 다시 눌러 주세요.".into(),
                Ok(value) if value["result"].as_str().is_some_and(|s|s.contains("오류"))=>"음성을 재생하지 못했어요. 문서는 계속 읽을 수 있어요.".into(),
                Ok(_)=>String::new(),Err(_)=>"해설 창을 다시 열고 눌러 주세요.".into(),
            });playing.set(false);
        });
    });
    rsx! {
        button {class:"course-guide-open",onclick:move |_|{
            open.set(true);loading.set(true);status.set(String::new());let repository=course.repository.clone();
            spawn(async move {
                let result=molip_quest::github_player::background(move||{
                    let snapshot=molip_quest::content_updates::installed_store()?.active(&repository)?.ok_or("코스 자료가 없어요. 코스를 다시 여세요.")?;
                    Ok(CourseGuide::from_snapshot(&snapshot))
                }).await;
                match result{Ok(value)=>guide.set(Some(value)),Err(error)=>status.set(error)}loading.set(false);
            });
        },"코스 목표와 전체 흐름"}
        dialog {id:"course-guide-dialog",class:"course-guide-dialog",aria_labelledby:"course-guide-title",
            onkeydown:move |event|{if event.key()==Key::Escape{open.set(false);}},
            header {h2 {id:"course-guide-title","코스 목표와 전체 흐름"}
                button {autofocus:true,onclick:move |_|open.set(false),"닫기"}}
            if loading(){p {role:"status","설치된 코스 자료를 읽고 있어요."}}
            if let Some(document)=guide(){
                div {class:"course-guide-controls",
                    button {disabled:playing()||loading(),onclick:move |_|play.call(None),"AI 전체 해설 재생"}
                    button {disabled:!playing(),onclick:move |_|{document::eval("window.molipAgent?.stop()");},"멈춤"}
                    span {"목표와 이야기만 살펴봐요. 풀이 기록은 바뀌지 않아요."}
                }
                p {"data-overview-status":"true",class:"course-guide-status",role:"status","{status}"}
                div {class:"course-guide-layout",
                    nav {class:"course-guide-toc",aria_label:"수업 흐름 목차",
                        button {onclick:move |_|{document::eval("document.querySelector('#course-guide-summary')?.scrollIntoView({block:'start'})");},"코스 목표"}
                        for (i,lesson) in document.lessons.iter().enumerate(){button {onclick:move |_|{document::eval(&format!("document.querySelector('#course-guide-lesson-{i}')?.scrollIntoView({{block:'start'}})"));},"{i+1}. {lesson.title}"}}
                    }
                    article {class:"course-guide-document","data-content-fingerprint":"{document.fingerprint}",
                        section {id:"course-guide-summary",h3 {"{document.title}"}p {"{document.description}"}
                            h4 {"코스 목표"}
                            if document.objectives.is_empty(){p {"코스 목표가 아직 등록되지 않았어요."}}
                            ul {for (i,goal) in document.objectives.iter().enumerate(){li {id:"course-guide-goal-{i}","{goal}"}}}
                            if !document.scope_note.is_empty(){p {id:"course-guide-scope",class:"course-guide-scope","{document.scope_note}"}}
                            p {"아래는 현재 등록된 수업의 추천 순서예요. 어떤 수업이든 자유롭게 열 수 있어요."}
                        }
                        for (i,lesson) in document.lessons.iter().enumerate(){
                            section {id:"course-guide-lesson-{i}",class:"course-guide-lesson",
                                h3 {"{i+1}. {lesson.title}"}p {"{lesson.description}"}
                                h4 {"수업 목표"}ul {for (j,goal) in lesson.objectives.iter().enumerate(){li {id:"course-guide-lesson-{i}-goal-{j}","{goal}"}}}
                                if !lesson.story.is_empty(){h4 {"수업 이야기"}for (j,premise) in lesson.story.iter().enumerate(){p {id:"course-guide-lesson-{i}-story-{j}","{premise}"}}}
                                if !lesson.prerequisites.is_empty(){p {class:"course-guide-prerequisites",{format!("앞서 알면 좋아요: {}",lesson.prerequisites.join(" · "))}}}
                                if !lesson.strategy.is_empty(){details {summary {"학습 방법"}p {"{lesson.strategy}"}}}
                                button {disabled:playing(),onclick:move |_|play.call(Some(i)),"이 수업 AI 해설"}
                            }
                        }
                    }
                }
            }else if !loading(){p {role:"status","{status}"}}
        }
    }
}
