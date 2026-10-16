use base64::{engine::general_purpose::STANDARD, Engine};
use dioxus::prelude::*;
use molip_quest::{learning_store::LearningStore, Course};
use ring::{aead, pbkdf2};
use serde::Deserialize;
use std::{collections::HashMap, num::NonZeroU32};

pub(crate) const COURSE_ID: &str = "kpc-morning-practice-v1";

#[derive(Clone, Deserialize)]
pub(crate) struct Material {
    /// The reference solution; the narration's code chunks join into it (checked by the
    /// instructor-materials test below), and 정답 보기 types those chunks.
    #[allow(dead_code)]
    code: String,
    /// The 풀이 요약 lines: what /tour-all says about the problem.
    explanation: Vec<String>,
    narration: Vec<serde_json::Value>,
}
pub(crate) type Materials = HashMap<String, Material>;

#[derive(Deserialize)]
struct Encrypted {
    iterations: u32,
    salt: String,
    iv: String,
    ciphertext: String,
}

pub(crate) fn decrypt(password: &str) -> Result<Materials, String> {
    let data: Encrypted = serde_json::from_str(include_str!(concat!(env!("OUT_DIR"), "/private-instructor.json")))
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let salt = STANDARD
        .decode(data.salt)
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let iv: [u8; 12] = STANDARD
        .decode(data.iv)
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?
        .try_into()
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let mut ciphertext = STANDARD
        .decode(data.ciphertext)
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let mut key = [0u8; 32];
    pbkdf2::derive(
        pbkdf2::PBKDF2_HMAC_SHA256,
        NonZeroU32::new(data.iterations).ok_or("강사용 자료를 읽지 못했습니다.")?,
        &salt,
        password.as_bytes(),
        &mut key,
    );
    let key = aead::LessSafeKey::new(
        aead::UnboundKey::new(&aead::AES_256_GCM, &key)
            .map_err(|_| "강사용 자료를 읽지 못했습니다.")?,
    );
    let plaintext = key
        .open_in_place(
            aead::Nonce::assume_unique_for_key(iv),
            aead::Aad::empty(),
            &mut ciphertext,
        )
        .map_err(|_| "비밀번호가 맞지 않습니다. 다시 입력하세요.")?;
    serde_json::from_slice(plaintext).map_err(|_| "강사용 자료를 읽지 못했습니다.".into())
}

fn numbered_units(course: &Course) -> Vec<molip_quest::Unit> {
    course
        .chapters
        .iter()
        .enumerate()
        .flat_map(|(chapter, group)| {
            group.units.iter().enumerate().map(move |(ordinal, unit)| {
                let mut unit = unit.clone();
                let title = unit
                    .title
                    .split_once(". ")
                    .filter(|(prefix, _)| prefix.chars().all(|c| c.is_ascii_digit()))
                    .map(|(_, title)| title)
                    .unwrap_or(&unit.title);
                if !unit.title.starts_with("C-") {
                    unit.title = format!("C-{}-{} · {}", chapter + 1, ordinal + 1, title);
                }
                unit
            })
        })
        .collect()
}

#[component]
pub(crate) fn PracticeView() -> Element {
    use molip_quest::curriculum::{Activity, ActivityKind};
    let course = use_hook(|| Course::parse(include_str!("../courses/morning-practice.json")));
    let Ok(course) = course else {
        return rsx! {p {class:"error","실습을 불러올 수 없습니다."}};
    };
    let mut selected = use_signal(|| 0usize);
    let mut refresh = use_signal(|| 0u64);
    let materials = use_context::<crate::instructor_mode::InstructorSession>().0;
    use_drop(|| {
        document::eval("window.molipAgent?.stop()");
    });
    let units = numbered_units(&course);
    let unit = units[selected()].clone();
    let _ = refresh();
    let completed = LearningStore::user_store()
        .and_then(|store| store.completed(&course))
        .unwrap_or_default();
    // The problem as a mission, so the instructor buttons and the AI panel treat it exactly like
    // a coding mission of the course: its 해설 comes from the instructor materials (the bundled
    // Excel lives under data/ in the app's sandbox), 정답 보기 types that script's code and submits.
    let material = materials().and_then(|m| m.get(&unit.id).cloned());
    let tour: Vec<String> = material.as_ref().map(|m| m.explanation.clone()).unwrap_or_default();
    let narration: Vec<serde_json::Value> = material
        .map(|material| {
            let mut actions = material.narration;
            for action in &mut actions {
                if let Some(code) = action.get_mut("code") {
                    if let Some(text) = code.as_str() {
                        *code = text.replace("\"cafe-sales.xlsx\"", "\"data/cafe-sales.xlsx\"").into();
                    }
                }
            }
            actions
        })
        .unwrap_or_default();
    let activity = Activity {
        id: unit.id.clone(),
        title: unit.title.clone(),
        challenge: true,
        ask: Vec::new(),
        narration,
        tour,
        kind: ActivityKind::Coding { problem: unit.clone() },
    };
    // "AI에게 물어보기", as in the learning view: the same panel, /auto, /auto-all and the
    // instructor's 정답 보기 · 해설 보기 all go through it.
    let mut assistant_open = use_signal(|| false);
    let mut assistant_messages = use_signal(Vec::<molip_quest::assistant::Turn>::new);
    let mut autopilot = use_signal(|| false);
    let mut touring = use_signal(|| false);
    let mut auto_round = use_signal(|| 0u32);
    let mut auto_cancel = use_signal(|| 0u32);
    let mut narration_paused = use_signal(|| false);
    let assistant_context = molip_quest::assistant::page_context(
        &course.title,
        &course.chapters[0].title,
        &unit,
        &activity,
        None,
    );
    let assistant_narration = serde_json::to_string(&activity.narration).unwrap_or_else(|_| "[]".into());
    let assistant_tour = serde_json::to_string(&crate::instructor_mode::tour_actions(&activity)).unwrap_or_else(|_| "[]".into());
    let mut assistant_context_signal = use_signal(|| assistant_context.clone());
    {
        let context = assistant_context.clone();
        use_effect(use_reactive!(|context| {
            if *assistant_context_signal.peek() != context {
                assistant_context_signal.set(context.clone());
            }
        }));
    }
    let mut assistant_narration_signal = use_signal(|| assistant_narration.clone());
    {
        let narration = assistant_narration.clone();
        use_effect(use_reactive!(|narration| {
            if *assistant_narration_signal.peek() != narration {
                assistant_narration_signal.set(narration.clone());
            }
        }));
    }
    let mut assistant_tour_signal = use_signal(|| assistant_tour.clone());
    {
        let tour = assistant_tour.clone();
        use_effect(use_reactive!(|tour| {
            if *assistant_tour_signal.peek() != tour {
                assistant_tour_signal.set(tour.clone());
            }
        }));
    }
    // Mark a problem switch in the conversation.
    let mut assistant_last_title = use_signal(|| unit.title.clone());
    let mission_marker = assistant_last_title;
    {
        let title = unit.title.clone();
        use_effect(use_reactive!(|title| {
            if *assistant_last_title.peek() != title {
                if !assistant_messages.peek().is_empty() {
                    assistant_messages.write().push(molip_quest::assistant::Turn {
                        role: "note".into(),
                        text: format!("이제 「{title}」 기준으로 답합니다."),
                    });
                }
                assistant_last_title.set(title.clone());
            }
        }));
    }
    // An instructor button posts a request: show the panel that plays it.
    {
        let requests = use_context::<crate::instructor_mode::InstructorRequests>();
        let mut seen = use_signal(move || requests.seq());
        use_effect(move || {
            if let Some(request) = requests.0.read().as_ref() {
                if request.seq != *seen.peek() {
                    seen.set(request.seq);
                    assistant_open.set(true);
                }
            }
        });
    }
    let last = units.len().saturating_sub(1);
    // Where each chapter starts in the flattened problem list, for Ctrl/⌘+↑↓.
    let chapter_starts: Vec<usize> = course
        .chapters
        .iter()
        .scan(0usize, |offset, chapter| {
            let start = *offset;
            *offset += chapter.units.len();
            Some(start)
        })
        .collect();
    let current_chapter = chapter_starts.iter().rposition(|&start| start <= selected()).unwrap_or(0);
    let prev_chapter_start = current_chapter.checked_sub(1).map(|i| chapter_starts[i]);
    let next_chapter_start = chapter_starts.get(current_chapter + 1).copied();
    rsx! {
        // Keyboard shortcuts (assets/layout/shortcuts.js) click these, as in the learning view:
        // Ctrl/⌘+←→ steps problems, Ctrl/⌘+↑↓ chapters, Ctrl/⌘+I opens or folds the AI panel
        // (Ctrl/⌘+K finds the 도전 과제 목록 dialog by its curriculum-menu class).
        div {class:"shortcut-targets",hidden:true,"aria-hidden":"true",
            button {id:"shortcut-prev-mission",tabindex:"-1",disabled:selected()==0,onclick:move |_|{if selected()>0 {selected-=1;}}}
            button {id:"shortcut-next-mission",tabindex:"-1",disabled:selected()>=last,onclick:move |_|{if selected()<last {selected+=1;}}}
            button {id:"shortcut-prev-unit",tabindex:"-1",disabled:prev_chapter_start.is_none(),onclick:move |_|{if let Some(start)=prev_chapter_start {selected.set(start);}}}
            button {id:"shortcut-next-unit",tabindex:"-1",disabled:next_chapter_start.is_none(),onclick:move |_|{if let Some(start)=next_chapter_start {selected.set(start);}}}
            button {id:"shortcut-assistant",tabindex:"-1",onclick:move |_|{let v=assistant_open();assistant_open.set(!v);}}
        }
        header {class:"practice-header",h1 {"도전 과제"}
        nav {class:"header-course-actions",aria_label:"실습 문제",
            button {class:"curriculum-toggle",onclick:move |_|{document::eval(r#"const dialog = document.querySelector('.practice-list');
                if (!dialog.dataset.dismissBound) {dialog.addEventListener('click', event => {if(event.target === dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});dialog.dataset.dismissBound='true';}
                dialog.showModal();"#);},"도전 과제 목록"}
            if materials().is_some() {
                crate::instructor_mode::InstructorControls {key:"instructor-practice-{unit.id}",activity:activity.clone()}
            }
        }
        button {class:"assistant-open",onclick:move |_|{let v=assistant_open();assistant_open.set(!v);},{if assistant_open() {"AI 접기"} else {"AI에게 물어보기"}}}
        span {class:"practice-current-title","{unit.title}"}
        }
        dialog {class:"curriculum-menu practice-list",aria_label:"도전 과제 목록",
            div {class:"curriculum-modal-header",h2 {"도전 과제 목록"}
                button {class:"curriculum-close",aria_label:"도전 과제 목록 닫기",autofocus:true,onclick:move |_|{document::eval("document.querySelector('.practice-list').close()");},"닫기 ×"}
            }
            div {class:"curriculum-gauge",role:"progressbar",aria_valuemin:"0",aria_valuemax:"100",aria_valuenow:format!("{}",completed.len()*100/units.len()),
                div {class:"curriculum-gauge-head",span {class:"curriculum-gauge-label","클리어"}span {class:"curriculum-gauge-percent",{format!("{}%",completed.len()*100/units.len())}}span {class:"curriculum-gauge-count",{format!("{} / {}",completed.len(),units.len())}}}
                div {class:"curriculum-gauge-track",div {class:"curriculum-gauge-fill",style:format!("width:{}%",completed.len()*100/units.len())}}
            }
            nav {class:"curriculum",
                for chapter in &course.chapters {
                    details {class:"curriculum-chapter",open:chapter.units.iter().any(|problem|problem.id==unit.id),
                        summary {h3 {span {class:"curriculum-kind","📚 챕터"}{format!(" {} · {} / {} · {}%",chapter.title,chapter.units.iter().filter(|problem|completed.contains(&problem.id)).count(),chapter.units.len(),if chapter.units.is_empty() {0} else {chapter.units.iter().filter(|problem|completed.contains(&problem.id)).count()*100/chapter.units.len()})}}
                        }
                        for problem in &chapter.units {
                            {
                                let index=units.iter().position(|candidate|candidate.id==problem.id).unwrap();
                                let title=units[index].title.clone();
                                rsx! {
                                    div {class:"curriculum-unit",button {class:format!("unit{}{}",if selected()==index{" selected"}else{""},if completed.contains(&problem.id){" done"}else{""}),aria_current:if selected()==index {"step"}else{"false"},onclick:move |_|{selected.set(index);document::eval("document.querySelector('.practice-list').close()");},
                                        span {class:"unit-title",{format!("{} {}",if completed.contains(&problem.id){"✓"}else if selected()==index{"▶"}else{"○"},title)}}
                                        if selected()==index {span {class:"unit-current","학습 중"}}
                                    }}
                                }
                            }
                        }
                    }
                }
            }
        }
        if autopilot() {
            div {class:"autopilot-banner",role:"status",
                span {class:"autopilot-dot"} span {{if narration_paused() {"자동 진행 · 일시정지 중 · "} else if touring() {"핵심 훑기 진행 중 · 문제마다 핵심만 말하고 답을 넣어 넘어갑니다 · "} else {"자동 진행 중 · 문제가 끝나면 다음으로 넘어갑니다 · "}}} kbd {"Space"} span {" 일시정지/재개 · "} kbd {"Esc"}
                button {onclick:move |_|{let p=!narration_paused();narration_paused.set(p);document::eval(if p {"window.molipAgent && molipAgent.pause();"} else {"window.molipAgent && molipAgent.resume();"});},{if narration_paused() {"▶ 재개"} else {"⏸ 일시정지"}}}
                button {onclick:move |_|{autopilot.set(false);touring.set(false);narration_paused.set(false);auto_cancel+=1;document::eval("window.molipAgent && molipAgent.stop();");},"해제"}
            }
            button {id:"autopilot-stop",hidden:true,tabindex:"-1",onclick:move |_|{autopilot.set(false);touring.set(false);auto_cancel+=1;document::eval("window.molipAgent && molipAgent.stop();");}}
        }
        div {class:if assistant_open() {"learning-row assistant-docked"} else {"learning-row"},
            div {class:"separate-practice-workspace", {rsx! {
                crate::ui::UnitWorkspace {key:"{unit.id}",course_id:COURSE_ID.to_string(),unit:unit.clone(),
                    oncompleted:move |passed|{if passed {refresh+=1;crate::ui::toast("정답입니다! 실습 완료를 저장했습니다.","success");}}
                }
            }}}
            if assistant_open() {
                div {class:"split-handle split-col assistant-handle",role:"separator",aria_orientation:"vertical",aria_label:"AI 창 너비 조절",tabindex:"0",title:"드래그로 너비 조절"}
            }
            aside {class:"assistant-dock",hidden:!assistant_open(),
                crate::ui::AssistantPanel {title:unit.title.clone(),kind:"도전 과제".to_string(),ask:Vec::<String>::new(),context:assistant_context_signal,narration:assistant_narration_signal,tour:assistant_tour_signal,messages:assistant_messages,
                    autopilot,touring,auto_round,auto_cancel,mission_marker,paused:narration_paused,
                    onauto_advance:move |_|{
                        // The tutor finished this problem: the next one, or the end of the set.
                        if selected() < last {
                            selected+=1;
                            auto_round+=1;
                        } else {
                            autopilot.set(false);
                            touring.set(false);
                            crate::ui::toast("도전 과제의 끝입니다. 자동 진행을 마칩니다.","success");
                        }
                    },
                    onclose:move |_|assistant_open.set(false)}
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn practice_is_separate_and_all_problems_have_tests() {
        let course = Course::parse(include_str!("../courses/morning-practice.json")).unwrap();
        assert_eq!(course.id, COURSE_ID);
        assert!(course.total_units() >= 3);
        let numbered = numbered_units(&course);
        assert_eq!(numbered.len(), course.total_units());
        assert!(numbered[0].title.starts_with("C-1-1"));
        assert_eq!(numbered[0].id, "sales");
        assert_eq!(numbered[1].id, "total");
        assert_eq!(numbered[2].id, "best");
        for unit in &course.chapters[0].units {
            assert_eq!(unit.tests.len(), 1);
            assert!(unit.starter_code.contains("data/cafe-sales.xlsx"));
        }
        assert!(decrypt("incorrect-password").is_err());
    }
    #[test]
    fn numbering_flattens_chapters_without_changing_progress_ids() {
        let mut course = Course::parse(include_str!("../courses/morning-practice.json")).unwrap();
        let mut second = course.chapters[0].clone();
        second.id = "second-numbering-test".into();
        for problem in &mut second.units {
            problem.id = format!("second-{}", problem.id);
        }
        let first_count = course.total_units();
        course.chapters.push(second);
        let numbered = numbered_units(&course);
        assert!(numbered[first_count]
            .title
            .starts_with(&format!("C-{}-1", course.chapters.len())));
        assert_eq!(numbered[first_count].id, "second-sales");
        assert_eq!(numbered[0].id, "sales");
    }
    #[tokio::test]
    #[ignore = "requires local instructor password file"]
    async fn private_instructor_material_and_bundled_excel_run() {
        let path = std::env::var("MOLIP_PRACTICE_TEST_PASSWORD_FILE").unwrap();
        let password = std::fs::read_to_string(path).unwrap();
        let materials = decrypt(password.trim()).unwrap();
        let course = Course::parse(include_str!("../courses/morning-practice.json")).unwrap();
        for unit in course.chapters.iter().flat_map(|chapter| &chapter.units) {
            let code = materials[&unit.id]
                .code
                .replace("\"cafe-sales.xlsx\"", "\"data/cafe-sales.xlsx\"");
            // Replayed as the agent plays it (set_code resets, type_code appends, a try is
            // taken back by set_code), the editor ends as the commented solution.
            let mut editor = String::new();
            for action in &materials[&unit.id].narration {
                match action["action"].as_str().unwrap() {
                    "set_code" => editor = action["code"].as_str().unwrap().to_string(),
                    "type_code" => {
                        if action["replace"] == true {
                            editor.clear();
                        }
                        let mut body = action["code"].as_str().unwrap().to_string();
                        if !body.ends_with('\n') {
                            body.push('\n');
                        }
                        if !editor.is_empty() && !editor.ends_with('\n') {
                            body.insert(0, '\n');
                        }
                        editor.push_str(&body);
                    }
                    _ => {}
                }
            }
            assert_eq!(editor.trim_end(), materials[&unit.id].code.trim_end(), "{}", unit.id);
            let runs = materials[&unit.id].narration.iter().filter(|a| a["action"] == "run").count();
            assert!(runs >= 2, "{}: the 해설 must run more than once", unit.id);
            assert!(materials[&unit.id].code.contains('#'), "{}: the solution needs comments", unit.id);
            let report = molip_quest::runner::check_unit(unit, &code).await.unwrap();
            assert!(
                report.passed,
                "{}: {:?}",
                unit.id,
                report.cases.iter().map(|c| &c.stderr).collect::<Vec<_>>()
            );
        }
    }
}
