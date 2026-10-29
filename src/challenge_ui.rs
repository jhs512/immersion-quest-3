//! 도전 과제 board: each published lesson's final graded problem, opened in its own lesson, and
//! final problems for lessons still being prepared, with their real review and execution state.
use dioxus::prelude::*;
use molip_quest::{challenges::{self,ExecutionState,FutureChallenge,FutureChallengeFile,LessonChallenge,ReviewState},
    github_player::{self,Github},issue_progress::{self,LearningEvent},repository_course::{CourseManifest,LessonRef}};
use std::collections::HashMap;

#[derive(Clone,PartialEq)]
pub(crate) enum ChallengeOpen { Lesson{reference:LessonRef,task_id:String}, Future(FutureChallenge) }

#[derive(Clone,PartialEq)]
struct Loaded {
    lessons:Vec<(usize,LessonRef,Result<LessonChallenge,String>)>,
    reviewer:Result<bool,String>,
    future:Result<Option<FutureChallengeFile>,String>,
}

/// The prompt's situation (before its 할 일 list), without markdown emphasis or code marks.
fn short(text:&str,limit:usize)->String {
    let paragraph=text.split("**할 일**").next().unwrap_or(text);
    let line=paragraph.lines().map(str::trim).filter(|l|!l.is_empty()).collect::<Vec<_>>().join(" ").replace("**","").replace('`',"");
    if line.chars().count()<=limit {line}else{format!("{}…",line.chars().take(limit).collect::<String>())}
}

#[component]
pub(crate) fn ChallengeBoard(github:Github,course:CourseManifest,progress:HashMap<String,Vec<LearningEvent>>,ready:bool,busy:bool,onopen:EventHandler<ChallengeOpen>)->Element {
    let loaded=use_resource({let github=github.clone();let course=course.clone();move ||{let github=github.clone();let course=course.clone();async move {
        github_player::background(move||{
            let lessons=course.lessons.iter().enumerate().map(|(index,reference)|{
                let found=github.installed_lesson(&course,reference).and_then(|lesson|challenges::lesson_challenge(index,reference,&lesson).ok_or_else(||"채점하는 문제가 없는 수업이에요.".to_string()));
                (index,reference.clone(),found)
            }).collect();
            Ok::<_,String>(Loaded{lessons,reviewer:github.can_edit_course(&course.repository),future:github.future_challenges(&course)})
        }).await
    }}});
    let state=loaded.read().clone();
    rsx!{
        section {class:"challenge-board",aria_labelledby:"challenge-board-title",
            h3 {id:"challenge-board-title","도전 과제"}
            p {"수업마다 마지막으로 채점하는 문제를 모았어요. 원래 수업 화면에서 풀고, 통과하면 그 수업 진도에 기록돼요."}
            p {class:"challenge-review-note",role:"note","「수업 클리어 도전」 문제는 수업의 마지막 종합 문제로 지정됐어요. 통과하면 앞 문제를 건너뛰었어도 그 수업을 클리어해요. 나머지는 수업의 마지막 문제일 뿐 종합 문제로 검토하지 않았어요."}
            match state {
                None=>rsx!{p {class:"lesson-status",role:"status","수업의 마지막 문제를 찾고 있어요…"}},
                Some(Err(error))=>rsx!{p {class:"challenge-error",role:"alert","도전 과제를 불러오지 못했어요. {error}"}},
                Some(Ok(loaded))=>{
                    let reviewer=*loaded.reviewer.as_ref().unwrap_or(&false);
                    rsx!{
                        h4 {class:"challenge-group-title","공개된 수업 · {loaded.lessons.len()}개"}
                        ol {class:"challenge-list",
                            for (index,reference,found) in loaded.lessons.clone() {
                                li {key:"{reference.id}",
                                    match found {
                                        Err(error)=>rsx!{article {class:"card challenge-card","data-state":"published","data-lesson-id":reference.id.clone(),
                                            div {class:"challenge-card-heading",span {class:"lesson-number","수업 {index+1}"}h5 {"{reference.title}"}}
                                            p {class:"challenge-error",role:"status","{error}"}
                                        }},
                                        Ok(challenge)=>{
                                            let passed=progress.get(&challenge.lesson_id).is_some_and(|events|issue_progress::learned_tasks(events,&challenge.revision).contains(&challenge.task_id));
                                            rsx!{article {class:"card challenge-card","data-state":"published","data-designated":challenge.designated.to_string(),"data-lesson-id":challenge.lesson_id.clone(),"data-task-id":challenge.task_id.clone(),"data-revision":challenge.revision.clone(),"data-passed":passed.to_string(),
                                                div {class:"challenge-card-heading",span {class:"lesson-number","수업 {index+1}"}h5 {"{challenge.lesson_title}"}}
                                                p {class:"challenge-task",strong {"문제 {challenge.position.0} / {challenge.position.1} · {challenge.task_title}"}}
                                                p {class:"challenge-prompt",{short(&challenge.prompt,140)}}
                                                ul {class:"challenge-tags",aria_label:"문제 상태",
                                                    li {"공개 수업 · 버전 {challenge.revision}"}
                                                    li {"{challenge.kind}"}
                                                    if challenge.designated {li {class:"challenge-designated","수업 클리어 도전"}} else {li {"종합 문제 검토 전"}}
                                                    if passed&&challenge.designated {li {class:"challenge-cleared",crate::player_ui::ChallengeBadge {}}}
                                                    else {li {class:if passed{"challenge-passed"}else{""},if passed{"✓ 통과"}else{"아직 풀지 않음"}}}
                                                }
                                                button {class:"primary",disabled:busy||!ready,title:if ready{"원래 수업에서 이 문제를 열어요"}else{"이 코스에서 쓸 이름을 먼저 입력하세요"},onclick:{let reference=reference.clone();let task_id=challenge.task_id.clone();move |_|onopen.call(ChallengeOpen::Lesson{reference:reference.clone(),task_id:task_id.clone()})},"수업에서 풀기"}
                                            }}
                                        }
                                    }
                                }
                            }
                        }
                        h4 {class:"challenge-group-title","수업 준비 중"}
                        if reviewer {p {class:"challenge-reviewer-note",role:"note","이 계정은 코스 저장소에 쓸 수 있어서 검토 대기 초안도 보여요. 학생에게는 승인된 문제만 보여요."}}
                        if let Err(error)=&loaded.reviewer {p {class:"challenge-error",role:"status","코스 편집 권한을 확인하지 못해 승인된 문제만 보여요. {error}"}}
                        match &loaded.future {
                            Err(error)=>rsx!{p {class:"challenge-error",role:"alert","수업 준비 중인 도전 과제를 불러오지 못했어요. {error}"}},
                            Ok(file)=>{
                                let visible:Vec<FutureChallenge>=file.as_ref().map(|file|file.visible(reviewer).into_iter().cloned().collect()).unwrap_or_default();
                                if visible.is_empty() {
                                    rsx!{p {class:"challenge-empty",role:"status","아직 수업 준비 중인 도전 과제가 없어요."}}
                                } else {rsx!{
                                    ol {class:"challenge-list",
                                        for challenge in visible {
                                            li {key:"{challenge.id}",article {class:"card challenge-card challenge-future","data-state":"preparing","data-challenge-id":challenge.id.clone(),"data-review":if challenge.review.state==ReviewState::Approved{"approved"}else{"draft"},"data-execution":if challenge.runnable(){"ready"}else{"pending"},
                                                div {class:"challenge-card-heading",span {class:"lesson-number","예정 · {challenge.planned_lesson.phase}"}h5 {"{challenge.planned_lesson.title}"}}
                                                p {class:"challenge-preparing",strong {"이 문제를 위한 수업은 아직 준비 중"}}
                                                p {class:"challenge-task",strong {"{challenge.task.title}"}}
                                                p {class:"challenge-prompt",{short(if challenge.task.question.trim().is_empty(){&challenge.task.goal}else{&challenge.task.question},140)}}
                                                ul {class:"challenge-tags",aria_label:"문제 상태",
                                                    li {class:if challenge.review.state==ReviewState::Draft{"challenge-draft"}else{""},if challenge.review.state==ReviewState::Draft{"검토 대기 초안 · 학생에게 보이지 않아요"}else{"검토 완료"}}
                                                    li {{challenges::answer_kind(&challenge.task)}}
                                                    if challenge.planned_lesson.elective {li {"선택 학습"}}
                                                    if challenge.planned_lesson.advanced {li {"심화"}}
                                                }
                                                if challenge.execution.state==ExecutionState::PendingEnvironment {p {class:"challenge-pending",role:"note","실행 환경 준비 중이라 아직 풀 수 없어요. {challenge.execution.note}"}}
                                                button {disabled:busy||!challenge.runnable(),onclick:{let challenge=challenge.clone();move |_|onopen.call(ChallengeOpen::Future(challenge.clone()))},"미리 풀어 보기"}
                                            }}
                                        }
                                    }
                                }}
                            }
                        }
                    }
                }
            }
        }
    }
}
