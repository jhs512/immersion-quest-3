use dioxus::prelude::*;
use molip_quest::repository_course::Lesson;

#[component]
pub fn LessonOutline(lesson: Lesson, task_id: String) -> Element {
    if lesson.schema_version != 2 { return rsx! {}; }
    let Some((chapter, unit, step)) = lesson.context_for(&task_id) else { return rsx! {}; };
    rsx! {
        section { class: "lesson-outline", aria_label: "현재 학습 목표",
            div { class: "learning-objective", strong { "수업 목표" }
                ul { for (index,goal) in lesson.objectives.iter().enumerate() { li {id:"lesson-goal-{index}", "{goal}" } } }
            }
            div { class: "learning-objective", strong { "챕터 · {chapter.title}" }
                ul { for goal in &chapter.objectives { li { "{goal}" } } }
            }
            div { class: "learning-objective", strong { "단원 · {unit.title}" }
                ul { for goal in &unit.objectives { li { "{goal}" } } }
                if !unit.premise.is_empty() { details { summary { "기본 전제" } p { "{unit.premise}" } } }
            }
            div { class: "learning-objective", strong { "스텝 목표" }
                ul { for goal in &step.objectives { li { "{goal}" } } }
            }
        }
    }
}

#[component]
pub fn LessonOverview(lesson:Lesson)->Element {
    let mut playing=use_signal(||false);
    let mut status=use_signal(String::new);
    let strategy=if lesson.learning_strategy.is_empty(){format!("{} 한 단계씩 직접 풀고 결과를 비교해요.",lesson.description)}else{lesson.learning_strategy.clone()};
    let mut actions:Vec<serde_json::Value>=lesson.objectives.iter().enumerate().map(|(index,goal)|serde_json::json!({"action":"say","text":if index==0{format!("이 수업의 목표예요. {goal}")}else{goal.clone()},"target":format!("#lesson-goal-{index}")})).collect();
    actions.push(serde_json::json!({"action":"say","text":format!("이렇게 배울 거예요. {strategy}"),"target":"#lesson-learning-strategy"}));
    use_drop(||{document::eval("if(document.querySelector('#lesson-info-dialog')?.dataset.overviewRunning==='true')window.molipAgent?.stop()");});
    rsx! {
        section {class:"lesson-overview",aria_label:"목표와 학습 방법 해설",
            h3 {"학습 방법"}
            p {id:"lesson-learning-strategy","{strategy}"}
            div {class:"lesson-overview-controls",
                button {disabled:playing(),onclick:move |_|{
                    let actions=actions.clone();playing.set(true);status.set("해설을 준비하고 있어요.".into());
                    spawn(async move {
                        let script=format!("(async()=>{{try{{const result=await window.molipAgent.runOverview({},document.querySelector('#lesson-info-dialog'));dioxus.send({{result}});}}catch(error){{dioxus.send({{error:String(error)}});}}}})()",serde_json::to_string(&actions).unwrap());
                        let mut bridge=document::eval(&script);
                        match bridge.recv::<serde_json::Value>().await {
                            Ok(value)=>status.set(if let Some(error)=value["error"].as_str(){format!("해설을 재생하지 못했어요. 다시 눌러 주세요. {error}")}else if value["result"].as_str().is_some_and(|s|s.contains("오류")){"음성을 재생하지 못했어요. 연결과 음성 설정을 확인한 뒤 다시 눌러 주세요.".into()}else{String::new()}),
                            Err(_)=>status.set("해설을 재생하지 못했어요. 창을 다시 열고 눌러 주세요.".into())
                        }
                        playing.set(false);
                    });
                },if playing(){"해설 재생 중…"}else{"목표와 학습 방법 해설"}}
                button {disabled:!playing(),onclick:move |_|{document::eval("window.molipAgent?.stop()");},"멈춤"}
            }
            p {id:"lesson-overview-status",class:"lesson-overview-status",role:"status",aria_live:"polite","{status}"}
        }
    }
}
