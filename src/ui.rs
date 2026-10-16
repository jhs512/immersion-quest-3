use dioxus::prelude::*;
use molip_quest::{
    curriculum::{Activity, ActivityKind, Question, QuestionKind},
    drafts,
    runner::{assemble, check_unit, run_code, run_python, Artifact},
    Course, Unit,
};
use std::collections::{HashMap, HashSet};

/// The Android build cannot spawn Python, so coding missions are read and acknowledged instead.
pub const VIEW_ONLY: bool = cfg!(target_os = "android");

#[cfg(not(target_os = "android"))]
fn copy_to_clipboard(text: String) -> Result<(), String> {
    arboard::Clipboard::new()
        .and_then(|mut clipboard| clipboard.set_text(text))
        .map_err(|e| e.to_string())
}
#[cfg(target_os = "android")]
fn copy_to_clipboard(_text: String) -> Result<(), String> {
    Err("Android 열람 모드에서는 클립보드 복사를 지원하지 않습니다.".into())
}

/// Every unit and mission can be opened at any time so students can look ahead; clearing
/// still requires passing the mission, and progress still decides where a unit resumes.
fn unlocked_units(course: &Course, _completed: &HashSet<String>) -> HashSet<String> {
    course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .map(|u| u.id.clone())
        .collect()
}
fn unlocked_activities(unit: &Unit, _completed: &HashSet<String>) -> usize {
    unit.activities.len()
}

/// Brief feedback that floats over the page (assets/layout/toast.js) instead of taking up layout.
pub(crate) fn toast(message: &str, kind: &str) {
    document::eval(&format!(
        "window.molipToast && molipToast({}, {})",
        serde_json::to_string(message).expect("toast text"),
        serde_json::to_string(kind).expect("toast kind")
    ));
}

fn mission_progress<'a>(
    units: impl Iterator<Item = &'a Unit>,
    completed: &HashSet<String>,
) -> String {
    let mut total = 0;
    let mut done = 0;
    for unit in units {
        for activity in &unit.activities {
            total += 1;
            done += usize::from(completed.contains(&activity.progress_unit(unit).id));
        }
    }
    let percent = if total == 0 { 0 } else { done * 100 / total };
    format!("{done} / {total} 미션 · {percent}%")
}

/// (done, total, percent) for a gauge.
fn mission_counts<'a>(
    units: impl Iterator<Item = &'a Unit>,
    completed: &HashSet<String>,
) -> (usize, usize, usize) {
    let mut total = 0;
    let mut done = 0;
    for unit in units {
        for activity in &unit.activities {
            total += 1;
            done += usize::from(completed.contains(&activity.progress_unit(unit).id));
        }
    }
    (done, total, if total == 0 { 0 } else { done * 100 / total })
}

#[component]
pub fn Learning(
    course: Course,
    #[props(default)] start_unit: String,
    #[props(default = usize::MAX)] start_mission: usize,
) -> Element {
    let mut selected = use_signal(|| start_unit);
    let mut mission_index = use_signal(|| start_mission);
    let mut clear_popup = use_signal(|| false);
    let mut earned_xp = use_signal(|| (0usize, 0usize));
    // (unit finished, unit to show next, next mission index, current mission index) for the popup.
    let mut pending_next = use_signal(|| None::<(bool, String, usize, usize)>);
    let mut refresh = use_signal(|| 0u64);
    // Bumped on reset so the mounted mission re-reads drafts and quiz state from scratch.
    let mut epoch = use_signal(|| 0u64);
    let progress_course = course.clone();
    let completed = use_memo(move || {
        let _ = refresh();
        let store = molip_quest::learning_store::LearningStore::user_store()?;
        Ok::<_, String>((
            store.completed(&progress_course)?,
            store.completed_items(&progress_course)?,
        ))
    });
    let (completed, completed_items) = match completed() {
        Ok(completed) => completed,
        Err(error) => return rsx! {p {class:"error", "{error}"}},
    };
    let unlocked = unlocked_units(&course, &completed);
    let active = course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .find(|u| u.id == selected() && unlocked.contains(&u.id))
        .or_else(|| {
            course
                .chapters
                .iter()
                .flat_map(|c| &c.units)
                .find(|u| unlocked.contains(&u.id) && !completed.contains(&u.id))
        })
        .unwrap_or(&course.chapters[0].units[0])
        .clone();
    let units: Vec<_> = course.chapters.iter().flat_map(|c| &c.units).collect();
    let position = units.iter().position(|u| u.id == active.id).unwrap();
    let previous = position.checked_sub(1).map(|i| units[i].id.clone());
    let next = units
        .get(position + 1)
        .filter(|u| unlocked.contains(&u.id))
        .map(|u| u.id.clone());
    let active_id = active.id.clone();
    let following_id = units.get(position + 1).map(|u| u.id.clone());
    let active_unlocked = unlocked_activities(&active, &completed_items);
    let active_total = active.activities.len();
    // A unit resumes at its first mission that is not cleared yet.
    let active_mission = if mission_index() == usize::MAX {
        molip_quest::curriculum::unlocked_activities(&active, &completed_items)
            .saturating_sub(1)
            .min(active_unlocked.saturating_sub(1))
    } else {
        mission_index().min(active_unlocked.saturating_sub(1))
    };
    let can_prev = !(active_mission == 0 && previous.is_none());
    let can_next = !(active_mission + 1 >= active_unlocked
        && !(active_mission + 1 == active_total && next.is_some()));
    // "AI에게 물어보기": the tutor chat knows the mission on screen.
    let mut assistant_open = use_signal(|| false);
    // An instructor button (정답 보기 · 해설 보기) posts a request: show the panel that plays it.
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
    // /auto-all: the tutor narrates and clears mission after mission until the course ends or
    // Esc. `auto_round` is bumped after every move so the panel starts the next /auto;
    // `auto_cancel` is bumped to abandon whatever the tutor is doing right now.
    let mut autopilot = use_signal(|| false);
    let mut auto_round = use_signal(|| 0u32);
    let mut auto_cancel = use_signal(|| 0u32);
    // A running 해설 is paused (the panel's ⏸, the banner's, or Space); the agent holds its
    // sentence and its typing until 재개.
    let mut narration_paused = use_signal(|| false);
    let mut assistant_messages = use_signal(Vec::<molip_quest::assistant::Turn>::new);
    let mut assistant_kind = String::new();
    let mut assistant_ask: Vec<String> = Vec::new();
    // The mission's precompiled 해설 script as JSON ("[]" when it has none), and the /tour-all
    // script (its tour sentences, then the answers).
    let mut assistant_narration = String::from("[]");
    let mut assistant_tour = String::from("[]");
    let (assistant_title, assistant_context) = {
        let chapter_title = course
            .chapters
            .iter()
            .find(|c| c.units.iter().any(|u| u.id == active.id))
            .map(|c| c.title.as_str())
            .unwrap_or("");
        match active.activities.get(active_mission) {
            Some(activity) => {
                assistant_kind = activity.label().to_string();
                assistant_ask = activity.ask.clone();
                assistant_narration =
                    serde_json::to_string(&activity.narration).unwrap_or_else(|_| "[]".into());
                assistant_tour =
                    serde_json::to_string(&crate::instructor_mode::tour_actions(activity))
                        .unwrap_or_else(|_| "[]".into());
                let draft_code = match &activity.kind {
                    ActivityKind::Coding { problem } => drafts::load(&format!(
                        "local:{}:{}:{}",
                        course.id, problem.id, problem.revision
                    ))
                    .ok()
                    .flatten()
                    .map(|d| d.code),
                    _ => None,
                };
                (
                    activity.title.clone(),
                    molip_quest::assistant::page_context(
                        &course.title,
                        chapter_title,
                        &active,
                        activity,
                        draft_code.as_deref(),
                    ),
                )
            }
            None => (active.title.clone(), String::new()),
        }
    };
    // The chat always answers about the mission on screen: the context lives in a signal the
    // panel reads at every call (also mid-loop, after the agent moved to another mission).
    let mut assistant_context_signal = use_signal(|| assistant_context.clone());
    {
        let context = assistant_context.clone();
        use_effect(use_reactive!(|context| {
            if *assistant_context_signal.peek() != context {
                assistant_context_signal.set(context.clone());
            }
        }));
    }
    // Same for the mission's 해설 script: read by the panel when /auto starts a round.
    let mut assistant_narration_signal = use_signal(|| assistant_narration.clone());
    {
        let narration = assistant_narration.clone();
        use_effect(use_reactive!(|narration| {
            if *assistant_narration_signal.peek() != narration {
                assistant_narration_signal.set(narration.clone());
            }
        }));
    }
    // And the /tour-all script.
    let mut assistant_tour_signal = use_signal(|| assistant_tour.clone());
    {
        let tour = assistant_tour.clone();
        use_effect(use_reactive!(|tour| {
            if *assistant_tour_signal.peek() != tour {
                assistant_tour_signal.set(tour.clone());
            }
        }));
    }
    // /tour-all: autopilot that says each mission's gist and fills it in instead of narrating.
    let mut touring = use_signal(|| false);
    // Mark a mission switch in the conversation.
    let mut assistant_last_title = use_signal(|| assistant_title.clone());
    let mission_marker = assistant_last_title;
    {
        let title = assistant_title.clone();
        use_effect(use_reactive!(|title| {
            if *assistant_last_title.peek() != title {
                if !assistant_messages.peek().is_empty() {
                    assistant_messages
                        .write()
                        .push(molip_quest::assistant::Turn {
                            role: "note".into(),
                            text: format!("이제 「{title}」 기준으로 답합니다."),
                        });
                }
                assistant_last_title.set(title.clone());
            }
        }));
    }
    // Unit moves for the keyboard (Ctrl/⌘ + ↑/↓, assets/layout/shortcuts.js).
    let previous_unit = previous.clone();
    let next_unit = next.clone();
    // Shared by the header buttons and the buttons at the bottom of concept and quiz missions.
    let navigate = Callback::new(move |delta: i32| {
        if delta < 0 {
            if active_mission > 0 {
                mission_index.set(active_mission - 1);
            } else if let Some(id) = &previous {
                mission_index.set(usize::MAX);
                selected.set(id.clone());
            }
        } else if active_mission + 1 < active_unlocked {
            mission_index.set(active_mission + 1);
        } else if let Some(id) = &next {
            mission_index.set(usize::MAX);
            selected.set(id.clone());
        }
    });
    rsx! {header {class:"practice-header", h1 {"{course.title}"}
        div {class:"learning-mission-toolbar",
        button {class:"curriculum-toggle",onclick:move |_|{document::eval(r#"const dialog = document.querySelector('.curriculum-menu');
            if (!dialog.dataset.dismissBound) {
                dialog.addEventListener('click', event => { if (event.target === dialog) {
                    const rect = dialog.getBoundingClientRect();
                    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
                }});
                dialog.dataset.dismissBound = 'true';
            }
            dialog.showModal();"#);},"수업 목차"}
            if let Some(activity)=active.activities.get(active_mission) {
                crate::instructor_mode::InstructorControls {key:"instructor-controls-{active.id}-{activity.id}",activity:activity.clone()}
            }
        }
        button {class:"assistant-open",onclick:move |_|{let v=assistant_open();assistant_open.set(!v);},{if assistant_open() {"AI 접기"} else {"AI에게 물어보기"}}}
        div {class:"header-navigation",aria_label:"학습 이동",
            button {disabled:!can_prev,onclick:move |_|navigate.call(-1),"← 이전"}
            button {disabled:!can_next,onclick:move |_|navigate.call(1),"다음 →"}
        }
        span {{format!("완료 {} / {} 단원",completed.len(),course.total_units())}}
        span {class:"learning-avatar",title:molip_quest::avatar::title(molip_quest::avatar::level_for(completed_items.len())),dangerous_inner_html:molip_quest::avatar::svg(molip_quest::avatar::level_for(completed_items.len()))}
        span {class:"learning-xp",{format!("Lv. {} · {} XP",molip_quest::avatar::level_for(completed_items.len()),completed_items.len()*molip_quest::avatar::XP_PER_MISSION)}}
        ResetProgress {course_id:course.id.clone(),onreset:move |_|{selected.set(String::new());mission_index.set(usize::MAX);clear_popup.set(false);refresh+=1;epoch+=1;}}}
        div {class:if assistant_open() {"learning-row assistant-docked"} else {"learning-row"},
        div {class:"learning",
        dialog {class:"curriculum-menu",aria_label:"수업 목차",
            div {class:"curriculum-modal-header",h2 {"수업 목차"}
                button {class:"curriculum-close",aria_label:"수업 목차 닫기",autofocus:true,onclick:move |_|{document::eval("document.querySelector('.curriculum-menu').close();");},"닫기 ×"}
            }
            {
                let (done,total,percent)=mission_counts(course.chapters.iter().flat_map(|c|c.units.iter()),&completed_items);
                rsx! {
                    div {class:"curriculum-gauge",role:"progressbar",aria_valuemin:"0",aria_valuemax:"100",aria_valuenow:"{percent}",
                        div {class:"curriculum-gauge-head",span {class:"curriculum-gauge-label","클리어"}span {class:"curriculum-gauge-percent","{percent}%"}span {class:"curriculum-gauge-count",{format!("{done} / {total} 미션")}}}
                        div {class:"curriculum-gauge-track",div {class:"curriculum-gauge-fill",style:"width:{percent}%"}}
                    }
                }
            }
            nav {class:"curriculum",
            // Chapters fold; the one being studied opens by default, the rest stay closed.
            for chapter in &course.chapters {details {class:"curriculum-chapter",open:chapter.units.iter().any(|u|u.id==active_id),
                summary {h3 {span {class:"curriculum-kind","📚 챕터"}{format!(" {} · {}",chapter.title,mission_progress(chapter.units.iter(),&completed_items))}}}
                for unit in &chapter.units {div {class:"curriculum-unit",button {class:format!("unit{}{}",if unit.id==active_id {" selected"}else{""},if completed.contains(&unit.id) {" done"}else{""}),aria_current:if unit.id==active_id {"step"}else{"false"},disabled:!unlocked.contains(&unit.id),onclick:{let id=unit.id.clone();let active_id=active_id.clone();move |_|{if id!=active_id {mission_index.set(usize::MAX);}selected.set(id.clone());document::eval("document.querySelector('.curriculum-menu').close();");}},
                    span {class:"unit-summary",span {class:"unit-title",span {class:"curriculum-kind","📖 단원"}{format!(" {} {}",if unit.id==active_id {"▶"}else if completed.contains(&unit.id) {"✓"} else if unlocked.contains(&unit.id) {"○"} else {"🔒"},unit.title)}}span {class:"unit-progress",{mission_progress(std::iter::once(unit),&completed_items)}}}
                    if unit.id==active_id {span {class:"unit-current","학습 중"}}
                }
                // Every unit's missions stay on screen: the menu never folds.
                {
                    let is_active = unit.id==active_id;
                    let unit_unlocked = if unlocked.contains(&unit.id) { unlocked_activities(unit,&completed_items) } else { 0 };
                    rsx! {
                    nav {class:"curriculum-missions",aria_label:"단원 미션",
                        for (n,activity) in unit.activities.iter().enumerate() {
                            button {class:format!("curriculum-mission{}{}{}", if is_active && n==active_mission {" selected"} else {""}, if activity.challenge {" challenge"} else {""}, if completed_items.contains(&activity.progress_unit(unit).id) {" done"} else if n<unit_unlocked {" todo"} else {""}),
                                aria_current:if is_active && n==active_mission {"step"}else{"false"},disabled:n>=unit_unlocked,
                                onclick:{let id=unit.id.clone();move |_|{if !is_active {selected.set(id.clone());}mission_index.set(n);document::eval("document.querySelector('.curriculum-menu').close();");}},
                                span {class:"mission-kind",{format!("{} {} {}",if is_active && n==active_mission {"▶"}else if completed_items.contains(&activity.progress_unit(unit).id){"✓"}else if n<unit_unlocked {"○"}else{"🔒"},activity.icon(),activity.label())}
                                    span {class:"mission-state",{if completed_items.contains(&activity.progress_unit(unit).id) {"클리어"} else if n<unit_unlocked {"미완료"} else {"잠김"}}}}
                                span {class:"mission-title","{activity.title}"}
                            }
                        }
                    }
                    }
                }
                }}
            }}
        }}
        for active in [active] {UnitFlow {key:"{active.id}-{active.revision}-{epoch}", course_id:course.id.clone(), unit:active,index:mission_index,nav_prev:can_prev,nav_next:can_next,onnavigate:navigate,
            oncompleted:{let active_id=active_id.clone();let following_id=following_id.clone();let course=course.clone();let already_completed=completed_items.clone();move |passed: bool|{
                if !passed {selected.set(active_id.clone());refresh+=1;return;}
                let unit_finished=molip_quest::learning_store::LearningStore::user_store().and_then(|store|store.completed(&course)).is_ok_and(|done|done.contains(&active_id));
                let total=molip_quest::learning_store::LearningStore::user_store().and_then(|store|store.completed_items(&course)).map(|items|items.len()).unwrap_or(already_completed.len());
                earned_xp.set((already_completed.len()*100,total*100));
                // Stay on the cleared mission: the popup's 다음 button is what moves on.
                let target=if unit_finished {following_id.clone().unwrap_or_else(||active_id.clone())}else{active_id.clone()};
                pending_next.set(Some((unit_finished,target,(active_mission+1).min(active_total.saturating_sub(1)),active_mission)));
                clear_popup.set(true);
            }}}}
        }
        if assistant_open() {
            div {class:"split-handle split-col assistant-handle",role:"separator",aria_orientation:"vertical",aria_label:"AI 창 너비 조절",tabindex:"0",title:"드래그로 너비 조절, 더블 클릭으로 되돌리기"}
        }
        // 접기 hides the dock; the panel stays mounted so a running request or /auto-all continues.
        aside {class:"assistant-dock",hidden:!assistant_open(),
                AssistantPanel {title:assistant_title.clone(),kind:assistant_kind.clone(),ask:assistant_ask.clone(),context:assistant_context_signal,narration:assistant_narration_signal,tour:assistant_tour_signal,messages:assistant_messages,
                    autopilot,touring,auto_round,auto_cancel,mission_marker,paused:narration_paused,
                    onauto_advance:move |_|{
                        // The tutor is done with this mission: take the clear popup's 다음 미션, or the
                        // header's 다음 →, or stop at the end of the course.
                        if clear_popup() {
                            let next=pending_next();pending_next.set(None);
                            if let Some((unit_finished,target,next_mission,_))=next {mission_index.set(if unit_finished {usize::MAX} else {next_mission});selected.set(target);}
                            refresh+=1;clear_popup.set(false);
                            auto_round+=1;
                        } else if can_next {
                            navigate.call(1);
                            auto_round+=1;
                        } else {
                            autopilot.set(false);
                            touring.set(false);
                            toast("과정의 끝입니다. 자동 진행을 마칩니다.","success");
                        }
                    },
                    onclose:move |_|assistant_open.set(false)}
        }
        }
        // Keyboard shortcuts (assets/layout/shortcuts.js) click these: Ctrl/⌘+←→ steps missions,
        // Ctrl/⌘+↑↓ units, Ctrl/⌘+I opens or folds the AI panel.
        div {class:"shortcut-targets",hidden:true,"aria-hidden":"true",
            button {id:"shortcut-prev-mission",tabindex:"-1",disabled:!can_prev,onclick:move |_|navigate.call(-1)}
            button {id:"shortcut-next-mission",tabindex:"-1",disabled:!can_next,onclick:move |_|navigate.call(1)}
            button {id:"shortcut-prev-unit",tabindex:"-1",disabled:previous_unit.is_none(),onclick:{let previous_unit=previous_unit.clone();move |_|{if let Some(id)=previous_unit.clone(){mission_index.set(usize::MAX);selected.set(id);}}}}
            button {id:"shortcut-next-unit",tabindex:"-1",disabled:next_unit.is_none(),onclick:{let next_unit=next_unit.clone();move |_|{if let Some(id)=next_unit.clone(){mission_index.set(usize::MAX);selected.set(id);}}}}
            button {id:"shortcut-assistant",tabindex:"-1",onclick:move |_|{let v=assistant_open();assistant_open.set(!v);}}
        }
        if autopilot() {
            div {class:"autopilot-banner",role:"status",
                span {class:"autopilot-dot"} span {{if narration_paused() {"자동 진행 · 일시정지 중 · "} else if touring() {"핵심 훑기 진행 중 · 미션마다 핵심만 말하고 답을 넣어 넘어갑니다 · "} else {"자동 진행 중 · 미션이 끝나면 다음으로 넘어갑니다 · "}}} kbd {"Space"} span {" 일시정지/재개 · "} kbd {"Esc"} span {" 해제"}
                button {onclick:move |_|{let p=!narration_paused();narration_paused.set(p);document::eval(if p {"window.molipAgent && molipAgent.pause();"} else {"window.molipAgent && molipAgent.resume();"});},{if narration_paused() {"▶ 재개"} else {"⏸ 일시정지"}}}
                button {onclick:move |_|{autopilot.set(false);narration_paused.set(false);auto_cancel+=1;document::eval("window.molipAgent && molipAgent.stop();");},"해제"}
            }
            // Esc anywhere (assets/layout/shortcuts.js) clicks this.
            button {id:"autopilot-stop",hidden:true,tabindex:"-1",onclick:move |_|{autopilot.set(false);auto_cancel+=1;document::eval("window.molipAgent && molipAgent.stop();");}}
        }
        if clear_popup() {div {class:"doctor-backdrop victory-backdrop",section {class:"doctor-panel victory-panel",role:"dialog",aria_label:"정답 확인",aria_modal:"true",
            "data-xp-before":earned_xp().0.to_string(),"data-xp-after":earned_xp().1.to_string(),
            {let before_level=molip_quest::avatar::level_for(earned_xp().0/molip_quest::avatar::XP_PER_MISSION);let after_level=molip_quest::avatar::level_for(earned_xp().1/molip_quest::avatar::XP_PER_MISSION);rsx!{
            div {class:"victory-avatar-stage","data-level-before":before_level.to_string(),"data-level-after":after_level.to_string(),"data-title-after":molip_quest::avatar::title(after_level),
                div {class:"victory-avatar current",dangerous_inner_html:molip_quest::avatar::svg(before_level)}
                if after_level>before_level {div {class:"victory-avatar next",dangerous_inner_html:molip_quest::avatar::svg(after_level)}}
            }
            p {class:"victory-levelup",aria_live:"polite"}
            p {class:"victory-eyebrow","MISSION COMPLETE"}
            p {class:"victory-title",{format!("칭호 · {}",molip_quest::avatar::title(before_level))}}}}
            if VIEW_ONLY {h2 {"미션 클리어!"} p {"진도를 저장했습니다."}}
            else {h2 {"정답입니다!"} p {"한 걸음 더 성장했어요."}}
            div {class:"victory-reward",{if earned_xp().1>earned_xp().0 {format!("+{} XP",earned_xp().1-earned_xp().0)}else{"복습 완료!".into()}}}
            div {class:"victory-xp",div {class:"victory-xp-label",strong {class:"victory-level",{format!("Lv. {}",earned_xp().0/500+1)}}span {class:"victory-total",{format!("{} XP",earned_xp().0)}}}
                div {class:"victory-track",div {class:"victory-fill"}}
                p {class:"victory-level-note","미션마다 100 XP · 500 XP마다 레벨 업"}
            }
            div {class:"popup-actions",
                button {class:"primary",autofocus:true,onclick:move |_|{
                    let next=pending_next();pending_next.set(None);
                    if let Some((unit_finished,target,next_mission,_))=next {mission_index.set(if unit_finished {usize::MAX} else {next_mission});selected.set(target);}
                    refresh+=1;clear_popup.set(false);
                },"다음 미션 ›"}
                button {onclick:move |_|{
                    let next=pending_next();pending_next.set(None);
                    if let Some((_,_,_,current))=next {mission_index.set(current);}
                    refresh+=1;clear_popup.set(false);
                },"여기 머물기"}
            }
        }}}
    }
}

#[component]
fn UnitFlow(
    course_id: String,
    unit: Unit,
    mut index: Signal<usize>,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    let mut refresh = use_signal(|| 0u64);
    let progress_course = course_id.clone();
    let progress_unit = unit.clone();
    let completed = use_memo(move || {
        let _ = refresh();
        let course = Course {
            id: progress_course.clone(),
            title: "KPC".into(),
            description: String::new(),
            chapters: vec![molip_quest::Chapter {
                id: "unit".into(),
                title: "unit".into(),
                units: vec![progress_unit.clone()],
            }],
        };
        molip_quest::learning_store::LearningStore::user_store()?.completed_items(&course)
    });
    if unit.activities.is_empty() {
        return rsx! { UnitWorkspace {course_id,unit,oncompleted} };
    }
    let completed = match completed() {
        Ok(items) => items,
        Err(e) => return rsx! {p {class:"error","{e}"}},
    };
    let unlocked_count = unlocked_activities(&unit, &completed);
    // A unit resumes at its first mission that is not cleared yet (the same rule as Learning).
    let active_index = if index() == usize::MAX {
        molip_quest::curriculum::unlocked_activities(&unit, &completed)
            .saturating_sub(1)
            .min(unlocked_count.saturating_sub(1))
    } else {
        index().min(unlocked_count.saturating_sub(1))
    };
    let active = unit.activities[active_index].clone();
    let progress = active.progress_unit(&unit);
    let count = unit
        .activities
        .iter()
        .filter(|a| completed.contains(&a.progress_unit(&unit).id))
        .count();
    let total = unit.activities.len();
    rsx! {
        section {class:"mission-strip",
            div {class:"mission-heading",strong {"{unit.title}"} span {"클리어 {count} / {total} · 현재 {active_index + 1}번째"}}
            // One cell per mission: cleared cells fill, the current one is outlined, and any cell jumps there.
            div {class:"mission-bar",role:"list",aria_label:"단원 진도",
                for (n, activity) in unit.activities.iter().enumerate() {
                    button {key:"{activity.id}",role:"listitem",
                        class:format!("mission-cell{}{}{}", if completed.contains(&activity.progress_unit(&unit).id) {" cleared"} else {""}, if n == active_index {" current"} else {""}, if activity.challenge {" challenge"} else {""}),
                        title:format!("{}{}", activity.title, if completed.contains(&activity.progress_unit(&unit).id) {" (클리어)"} else {""}),
                        aria_current:if n == active_index {"step"} else {"false"},
                        onclick:move |_| index.set(n)}
                }
            }

        }
        for active in [active] {ActivityView {key:"{progress.id}-{progress.revision}",course_id:course_id.clone(),activity:active,progress:progress.clone(),nav_prev,nav_next,onnavigate,// Pin the index (it may be the resume marker) so the cleared mission stays on screen under the
        // reward card; the card's 다음 미션 is what moves on.
        oncompleted:move |passed|{index.set(active_index);refresh+=1;oncompleted.call(passed);}}}
    }
}

#[component]
fn ActivityView(
    course_id: String,
    activity: Activity,
    progress: Unit,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    match activity.kind {
        ActivityKind::Coding { .. } if VIEW_ONLY => {
            rsx! {ReadOnlyMission {course_id,unit:progress,oncompleted}}
        }
        ActivityKind::Coding { .. } => rsx! {UnitWorkspace {course_id,unit:progress,oncompleted}},
        ActivityKind::Concept { body, check } => rsx! {
            div {class:"concept-flow",
                article {class:"reading-mission",span {class:"badge","개념"} h2 {"{activity.title}"}Markdown {text:body}}
                QuizView {course_id,unit:progress,questions:vec![check],nav_prev,nav_next,onnavigate,oncompleted}
            }
        },
        ActivityKind::Quiz { questions } => {
            rsx! {QuizView {course_id,unit:progress,questions,nav_prev,nav_next,onnavigate,oncompleted}}
        }
        ActivityKind::Slides { markdown } => rsx! {
            SlidesView {course_id,unit:progress,title:activity.title.clone(),markdown,nav_prev,nav_next,onnavigate,oncompleted}
        },
    }
}

#[component]
fn QuizView(
    course_id: String,
    unit: Unit,
    questions: Vec<Question>,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    let key = format!("quiz:{course_id}:{}:{}", unit.id, unit.revision);
    let initial = use_hook(|| -> Result<_, String> {
        let answers = drafts::load(&key)?.map(|d| d.answers).unwrap_or_default();
        let passed = molip_quest::learning_store::LearningStore::user_store()?
            .quiz_passed(&course_id, &unit, &questions)?;
        Ok((answers, passed))
    });
    let (initial_answers, initial_passed) = match initial {
        Ok(v) => v,
        Err(e) => return rsx! {p {class:"error","{e}"}},
    };
    // Keep the DOM value independent of answer updates: writing a controlled value
    // on every input interrupts native Korean IME composition in WebView2.
    let input_defaults = initial_answers.clone();
    let mut answers = use_signal(|| initial_answers);
    let mut passed = use_signal(|| initial_passed);
    let mut report = use_signal(|| None::<molip_quest::runner::TestReport>);
    let mut message = use_signal(String::new);
    let all_passed = passed.read().len() == questions.len();
    rsx! {article {class:"reading-mission quiz-mission",span {class:"badge",if questions.len()==1 {"개념 확인"}else{"퀴즈"}} h2 {"{unit.title}"}
        p {{format!("정답 완료 {} / {} 문항",passed.read().len(),questions.len())}}
        if all_passed {p {class:"clear-banner",role:"status","미션 클리어! 다음 미션으로 이동할 수 있어요."}}
        else {p {"맞힌 문항은 저장됩니다. 아직 맞히지 못한 문항만 다시 도전하세요."}}
        for (n,q) in questions.iter().enumerate() {
            // A solved question stays on screen, locked, with the student's answer marked, the
            // correct answer and the explanation (why the other options are wrong) under it,
            // so the quiz can be reviewed in place. data-question numbers the question for the
            // tutor agent ("quiz:N").
            {let solved=passed.read().contains(&q.id); let chosen=answers.read().get(&q.id).cloned().unwrap_or_default(); rsx!{
            section {key:"{q.id}",class:if solved {"quiz-question solved"} else {"quiz-question"},"data-question":(n+1).to_string(),div {class:"question-heading",Markdown {text:format!("{}. {}",n+1,q.prompt)}}
                match &q.kind {
                    QuestionKind::Choice {options,correct}=>rsx! {
                        for (option,text) in options.iter().enumerate() {
                            label {class:format!("quiz-option{}{}",if solved&&option==*correct {" correct"} else {""},if solved&&chosen==option.to_string() {" chosen"} else {""}),
                                input {r#type:"radio",name:q.id.clone(),value:option.to_string(),disabled:solved,checked:answers.read().get(&q.id)==Some(&option.to_string()),onchange:{let id=q.id.clone();let key=key.clone();move |_|{answers.write().insert(id.clone(),option.to_string());report.set(None);if let Err(e)=drafts::save(&key,"",&answers()){message.set(e);}}}}
                                Markdown {text:text.clone()}
                                if solved&&option==*correct {span {class:"quiz-mark correct","정답"}}
                                if solved&&chosen==option.to_string()&&option!=*correct {span {class:"quiz-mark chosen","내 답"}}
                            }
                        }
                    },
                    QuestionKind::ShortAnswer {accepted}=>rsx! {
                        input {aria_label:q.prompt.clone(),placeholder:"답을 입력하세요",disabled:solved,initial_value:input_defaults.get(&q.id).cloned().unwrap_or_default(),oninput:{let id=q.id.clone();let key=key.clone();move |e|{answers.write().insert(id.clone(),e.value());report.set(None);if let Err(e)=drafts::save(&key,"",&answers()){message.set(e);}}}}
                        if solved {p {class:"quiz-answer-line",{format!("내 답: {} · 인정 답안: {}",if chosen.trim().is_empty() {"(저장된 답 없음)".to_string()} else {chosen.clone()},accepted.join(", "))}}}
                    },
                    QuestionKind::TableSelect {table,pick,expected,..}=>{
                        // The picked indices live in the answer as "0,3,5"; a tick toggles one.
                        let picked=molip_quest::curriculum::parse_selection(answers.read().get(&q.id).map(String::as_str).unwrap_or(""));
                        let rows_mode=pick=="rows";
                        let toggle={let id=q.id.clone();let key=key.clone();move |index:usize|{
                            let mut picked=molip_quest::curriculum::parse_selection(answers.read().get(&id).map(String::as_str).unwrap_or(""));
                            match picked.iter().position(|&i|i==index) {Some(at)=>{picked.remove(at);},None=>{picked.push(index);picked.sort_unstable();}}
                            answers.write().insert(id.clone(),picked.iter().map(|i|i.to_string()).collect::<Vec<_>>().join(","));
                            report.set(None);
                            if let Err(e)=drafts::save(&key,"",&answers()){message.set(e);}
                        }};
                        rsx! {
                            div {class:"table-select","data-pick":pick.clone(),
                                p {class:"table-select-help",{if solved {format!("정답 · {} ({}개 고름)",expected,picked.len())} else if rows_mode {format!("행 왼쪽의 네모를 눌러 고르세요 · {}개 고름",picked.len())} else {format!("열 머리글을 눌러 고르세요 · {}개 고름",picked.len())}}}
                                div {class:"data-grid",table {
                                    thead {tr {th {class:"table-select-corner",{if rows_mode {"선택"} else {"#"}}}
                                        for (c,name) in table.columns.iter().enumerate() {
                                            th {class:if !rows_mode&&picked.contains(&c) {"picked"} else {""},
                                                if rows_mode {"{name}"}
                                                else {label {class:"table-select-column",input {r#type:"checkbox","data-index":c.to_string(),disabled:solved,checked:picked.contains(&c),onchange:{let mut toggle=toggle.clone();move |_|toggle(c)}}" {name}"}}
                                            }
                                        }
                                    }}
                                    tbody {
                                        for (r,row) in table.rows.iter().enumerate() {
                                            tr {class:if rows_mode&&picked.contains(&r) {"picked"} else {""},
                                                td {class:"table-select-corner",
                                                    if rows_mode {label {class:"table-select-row",input {r#type:"checkbox","data-index":r.to_string(),disabled:solved,checked:picked.contains(&r),onchange:{let mut toggle=toggle.clone();move |_|toggle(r)}}" {r+1}"}}
                                                    else {"{r+1}"}
                                                }
                                                for (c,cell) in row.iter().enumerate() {
                                                    td {class:if !rows_mode&&picked.contains(&c) {"picked"} else {""},{if cell.is_empty() {"·".to_string()} else {cell.clone()}}}
                                                }
                                            }
                                        }
                                    }
                                }}
                            }
                        }
                    },
                }
                if solved {
                    div {class:"quiz-review",
                        p {class:"quiz-solved-mark","✓ 정답 · 해설"}
                        Markdown {text:q.explanation.clone()}
                    }
                } else if let Some(result)=report.read().as_ref().and_then(|r|r.cases.get(n)) {
                    p {class:"error","다시 생각해보세요."}
                    Markdown {text:result.stderr.clone()}
                    p {"인정 답안: {result.expected}"}
                }
            }
            }}
        }
        p {class:"execution-status",role:"status","{message}"}
        div {class:"quiz-actions",
        button {class:"primary",disabled:all_passed,onclick:move |_|{
            let result=molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|{
                let graded=store.save_quiz(&course_id,&unit,&questions,&answers())?;
                let completed=store.quiz_passed(&course_id,&unit,&questions)?;
                Ok((graded,completed))
            });
            match result {
                Ok((graded,completed))=>{message.set(format!("{} / {} 정답 · {}",completed.len(),questions.len(),if graded.passed {"미션 클리어!"}else{"오답 문항만 다시 풀어보세요."}));let cleared=graded.passed;passed.set(completed);report.set(Some(graded));oncompleted.call(cleared);},Err(e)=>message.set(e)
            }
        },"제출"}
        MissionNav {nav_prev,nav_next,onnavigate}
        }
    }}
}

/// `data/...csv|xlsx|html` paths mentioned by a problem's starter code or text, in order, once each.
fn data_files(text: &str) -> Vec<String> {
    let mut files = Vec::new();
    for (start, _) in text.match_indices("data/") {
        let end = text[start..]
            .find(|c: char| !(c.is_ascii_alphanumeric() || matches!(c, '/' | '.' | '_' | '-')))
            .map(|n| start + n)
            .unwrap_or(text.len());
        let path = text[start..end].trim_end_matches('.');
        if (path.ends_with(".csv") || path.ends_with(".xlsx") || path.ends_with(".html"))
            && !files.iter().any(|f| f == path)
        {
            files.push(path.to_string());
        }
    }
    files
}

/// Full-screen preview of a data file: tables through pandas (first 100 rows), HTML as source text.
#[component]
fn DataViewer(path: String, onclose: EventHandler<()>) -> Element {
    let code = if path.ends_with(".html") {
        format!("from pathlib import Path\nprint(Path({path:?}).read_text(encoding='utf-8'))")
    } else {
        let reader = if path.ends_with(".xlsx") {
            "read_excel"
        } else {
            "read_csv"
        };
        format!("import pandas as pd\ndf = pd.{reader}({path:?})\nprint(f'{{len(df)}}행 × {{len(df.columns)}}열')\ndf")
    };
    let result = use_resource(move || {
        let code = code.clone();
        async move { run_python(&code, "").await }
    });
    rsx! { div { class:"prompt-guide-layer data-viewer", role:"dialog", aria_modal:"true", aria_label:"자료 보기",
        onkeydown: move |e| { if e.key() == Key::Escape { onclose.call(()); } },
        header { class:"prompt-guide-header",
            h2 { "자료 보기" }
            span { class:"prompt-guide-unit", "{path}" }
            button { class:"prompt-guide-close", autofocus:true, onclick: move |_| onclose.call(()), "닫기 ×" }
        }
        div { class:"data-viewer-body",
            match &*result.read() {
                None => rsx! { p { class:"data-viewer-note", "읽는 중…" } },
                Some(Err(error)) => rsx! { p { class:"error", "{error}" } },
                Some(Ok(run)) => rsx! {
                    if !run.success { p { class:"error", "{run.stderr}" } }
                    if path.ends_with(".html") { pre { class:"data-viewer-source", "{run.stdout}" } }
                    else {
                        p { class:"data-viewer-note", "{run.stdout.trim()} · 앞 100행만 보여 줍니다." }
                        RichResults { artifacts: run.artifacts.clone() }
                    }
                },
            }
        }
    } }
}

/// A slide deck mission: Marp renders the Markdown (assets/slides/slides.js); reaching the
/// last slide or pressing the button records the mission as finished.
#[component]
fn SlidesView(
    course_id: String,
    unit: Unit,
    title: String,
    markdown: String,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    let mut done = use_signal(|| {
        molip_quest::learning_store::LearningStore::user_store()
            .and_then(|store| {
                store.completed_items(&Course {
                    id: course_id.clone(),
                    title: String::new(),
                    description: String::new(),
                    chapters: vec![molip_quest::Chapter {
                        id: "unit".into(),
                        title: String::new(),
                        units: vec![unit.clone()],
                    }],
                })
            })
            .map(|items| items.contains(&unit.id))
            .unwrap_or(false)
    });
    let mut message = use_signal(String::new);
    let finish = {
        let course_id = course_id.clone();
        let unit = unit.clone();
        move || match molip_quest::learning_store::LearningStore::user_store()
            .and_then(|mut store| store.mark_viewed(&course_id, &unit))
        {
            Ok(()) => {
                done.set(true);
                // Record quietly: no "정답입니다" popup and no jump to the next mission, which
                // would yank the reader off the last slide (and the tutor agent off the deck).
                oncompleted.call(false);
            }
            Err(e) => message.set(e),
        }
    };
    rsx! { article { class:"reading-mission slides-mission",
        span { class:"badge", "슬라이드" } h2 { "{title}" }
        p { class:"slides-help", "← → 키나 아래 버튼으로 넘기고, 수업 때는 「전체 화면」으로 발표 모드에 들어가세요(마우스를 움직이면 아래에 조작 바, Esc로 해제). 마지막 장까지 보면 미션이 완료됩니다." }
        div { class:"slides-host", "data-marp-source": markdown.clone() }
        // The slide script clicks this when the last slide is reached.
        button { class:"slides-finish", hidden: true, "aria-hidden": "true", tabindex: "-1", onclick: { let mut finish = finish.clone(); move |_| if !done() { finish(); } } }
        p { class:"execution-status", role:"status", "{message}" }
        if done() { p { class:"clear-banner", role:"status", "슬라이드를 끝까지 봤습니다. 미션 완료." } }
        div { class:"quiz-actions",
            button { class:"primary", disabled: done(), onclick: { let mut finish = finish.clone(); move |_| finish() }, "다 봤어요 · 미션 완료" }
            MissionNav {nav_prev,nav_next,onnavigate}
        }
    } }
}

/// "AI에게 물어보기": a tutor chat over the mission on screen (src/assistant.rs). The chat
/// history lives in the caller so closing and reopening the panel keeps it; 대화 지우기 clears it.
#[component]
pub(crate) fn AssistantPanel(
    title: String,
    kind: String,
    ask: Vec<String>,
    context: Signal<String>,
    narration: Signal<String>,
    tour: Signal<String>,
    messages: Signal<Vec<molip_quest::assistant::Turn>>,
    autopilot: Signal<bool>,
    touring: Signal<bool>,
    auto_round: Signal<u32>,
    auto_cancel: Signal<u32>,
    mission_marker: Signal<String>,
    paused: Signal<bool>,
    onauto_advance: EventHandler<()>,
    onclose: EventHandler<()>,
) -> Element {
    use molip_quest::assistant::{self, Provider, Settings, Turn};
    const AUTO: &str = "/auto";
    const AUTO_ALL: &str = "/auto-all";
    const TOUR_ALL: &str = "/tour-all";
    let mut current_task = use_signal(|| None::<dioxus::core::Task>);
    // The mission a /auto round started on: if the tutor itself moved on (a `next` action), the
    // flow must not move a second time.
    let mut auto_started_on = use_signal(String::new);
    let mut settings = use_signal(Settings::load);
    let mut show_settings = use_signal(|| false);
    let mut draft = use_signal(String::new);
    let mut pending = use_signal(|| false);
    let mut error = use_signal(String::new);
    const SCROLL: &str =
        "const m=document.querySelector('.assistant-messages');if(m)m.scrollTop=m.scrollHeight;";
    let mut running = use_signal(|| false);
    // Which answer is being read aloud (its index in `messages`), so that message shows
    // 읽는 중 · ⏹ 멈춤 while the others offer 🔊 읽기. The token tells a finished reading from
    // one that was replaced.
    let mut speaking = use_signal(|| None::<usize>);
    let mut speak_token = use_signal(|| 0u32);
    let read_aloud = Callback::new(move |(index, text, force): (usize, String, bool)| {
        speak_token += 1;
        let token = speak_token();
        speaking.set(Some(index));
        spawn(async move {
            let script = format!(
                "(async () => {{ try {{ dioxus.send(await window.molipAgent.speakReply({}, {force})); }} catch (e) {{ dioxus.send(false); }} }})()",
                serde_json::to_string(&text).unwrap_or_default()
            );
            let mut eval = document::eval(&script);
            let _ = eval.recv::<bool>().await;
            if speak_token() == token {
                speaking.set(None);
            }
        });
    });
    let stop_reading = Callback::new(move |_: ()| {
        speak_token += 1;
        speaking.set(None);
        document::eval("window.molipAgent && molipAgent.stopReply();");
    });
    // A round (an answer with its actions, or a precompiled narration) is over: in /auto-all, hand
    // control back to the learning flow, which moves on and bumps auto_round; an error ends the
    // run where it is.
    let settle = Callback::new(move |_: ()| {
        pending.set(false);
        document::eval(SCROLL);
        if *autopilot.peek() {
            if !error.peek().is_empty() {
                autopilot.set(false);
                touring.set(false);
                messages.write().push(Turn {
                    role: "note".into(),
                    text: "오류가 나서 자동 진행을 멈췄습니다.".into(),
                });
            } else if *mission_marker.peek() == *auto_started_on.peek() {
                onauto_advance.call(());
            } else {
                auto_round += 1;
            }
        }
    });
    // Play a precompiled action script on screen: the lines go into the conversation at once,
    // then the agent performs them and reports back. `/auto` plays the mission's 해설
    // (courses/*.json `narration`); the instructor's 정답 보기 plays its answer-filling steps.
    let mut narrating = use_signal(|| false);
    let perform = Callback::new(move |(heading, actions): (String, String)| {
        pending.set(true);
        error.set(String::new());
        let lines = assistant::narration_lines(&actions);
        // Spoken lines when the script has them, else the actions themselves (정답 입력 is silent).
        let steps = if lines.is_empty() {
            serde_json::from_str::<Vec<serde_json::Value>>(&actions).map_or(0, |a| a.len())
        } else {
            lines.len()
        };
        narrating.set(true);
        paused.set(false);
        document::eval("window.molipAgent && molipAgent.stop();");
        messages.write().push(Turn {
            role: "model".into(),
            text: format!(
                "▶ {heading} · {steps}단계\n\n{}",
                lines
                    .iter()
                    .map(|l| format!("- {l}"))
                    .collect::<Vec<_>>()
                    .join("\n")
            ),
        });
        document::eval(SCROLL);
        let task = spawn(async move {
            running.set(true);
            let script = format!(
                "(async () => {{ try {{ dioxus.send(await window.molipAgent.run({actions})); }} catch (e) {{ dioxus.send('동작 실행 실패: ' + (e && e.message ? e.message : e)); }} }})()"
            );
            let mut eval = document::eval(&script);
            let report: String = eval
                .recv()
                .await
                .unwrap_or_else(|e| format!("동작 실행 실패: {e:?}"));
            running.set(false);
            narrating.set(false);
            paused.set(false);
            if report.contains("오류 - ") || report.starts_with("동작 실행 실패") {
                error.set("해설 동작이 중간에 멈췄습니다. 화면을 확인하세요.".into());
            }
            messages.write().push(Turn {
                role: "tool".into(),
                text: report,
            });
            settle.call(());
        });
        current_task.set(Some(task));
    });
    let narrate = Callback::new(move |_: ()| perform.call(("자동 해설".into(), narration())));
    // Ask with the conversation as it stands (the last turn is the student's question). When the
    // assistant appends actions, run them on the screen, hand the report back and ask again,
    // until it answers without actions (at most a few rounds).
    let request = Callback::new(move |_: ()| {
        pending.set(true);
        error.set(String::new());
        document::eval(SCROLL);
        let settings_now = settings();
        let task = spawn(async move {
            let mut rounds = 0;
            loop {
                let history = messages();
                let current = context();
                match assistant::ask(&settings_now, &current, &history).await {
                    Err(e) => {
                        error.set(e);
                        break;
                    }
                    Ok(reply) => {
                        let (text, actions) = assistant::split_actions(&reply);
                        if !text.is_empty() {
                            // 소리 on: a plain answer is read aloud; an answer with actions
                            // lets the actions' own lines speak instead.
                            let spoken = actions.is_none() && settings_now.narration_voice;
                            let index = messages.read().len();
                            messages.write().push(Turn {
                                role: "model".into(),
                                text: text.clone(),
                            });
                            if spoken {
                                read_aloud.call((index, text, false));
                            }
                        }
                        let Some(actions) = actions else { break };
                        rounds += 1;
                        if rounds > 4 {
                            messages.write().push(Turn {
                                role: "tool".into(),
                                text: "동작을 네 번 반복해서 여기서 멈춥니다. 필요하면 다시 부탁하세요.".into(),
                            });
                            break;
                        }
                        running.set(true);
                        document::eval(SCROLL);
                        let script = format!(
                            "(async () => {{ try {{ dioxus.send(await window.molipAgent.run({})); }} catch (e) {{ dioxus.send('동작 실행 실패: ' + (e && e.message ? e.message : e)); }} }})()",
                            serde_json::to_string(&actions).unwrap_or_else(|_| "[]".into())
                        );
                        let mut eval = document::eval(&script);
                        let report: String = eval
                            .recv()
                            .await
                            .unwrap_or_else(|e| format!("동작 실행 실패: {e:?}"));
                        running.set(false);
                        messages.write().push(Turn {
                            role: "tool".into(),
                            text: report,
                        });
                        document::eval(SCROLL);
                    }
                }
            }
            settle.call(());
        });
        current_task.set(Some(task));
    });
    // /auto on the mission on screen: its precompiled script when it has one, else the CLI.
    // While /tour-all runs, the mission's tour script (gist, then the answers) plays instead.
    let auto = Callback::new(move |_: ()| {
        if *touring.peek() && tour.peek().trim() != "[]" {
            perform.call(("핵심 훑기".into(), tour.peek().clone()));
        } else if narration.peek().trim() != "[]" {
            narrate.call(());
        } else {
            request.call(());
        }
    });
    // The instructor's buttons: 해설 보기 is a typed /auto; 정답 보기 performs the answer steps.
    {
        let requests = use_context::<crate::instructor_mode::InstructorRequests>();
        let mut seen = use_signal(move || requests.seq());
        use_effect(move || {
            let Some(request) = requests.0.read().clone() else {
                return;
            };
            if request.seq == *seen.peek() {
                return;
            }
            seen.set(request.seq);
            if let Some(task) = current_task.take() {
                task.cancel();
            }
            match request.action {
                crate::instructor_mode::InstructorAction::Narrate => {
                    messages.write().push(Turn {
                        role: "user".into(),
                        text: AUTO.into(),
                    });
                    auto.call(());
                }
                crate::instructor_mode::InstructorAction::Solve(actions) => {
                    messages.write().push(Turn {
                        role: "user".into(),
                        text: "정답 보기".into(),
                    });
                    perform.call(("정답 입력".into(), actions));
                }
            }
        });
    }
    // The next mission's /auto, a moment after the screen has switched.
    let mut handled_round = use_signal(|| 0u32);
    use_effect(move || {
        let round = auto_round();
        if round == *handled_round.peek() {
            return;
        }
        handled_round.set(round);
        if !*autopilot.peek() {
            return;
        }
        spawn(async move {
            tokio::time::sleep(std::time::Duration::from_millis(1500)).await;
            if !*autopilot.peek() || *pending.peek() {
                return;
            }
            auto_started_on.set(mission_marker.peek().clone());
            messages.write().push(Turn {
                role: "user".into(),
                text: if *touring.peek() { TOUR_ALL } else { AUTO }.into(),
            });
            document::eval(SCROLL);
            auto.call(());
        });
    });
    // Esc / 해제: drop the running request (which kills the CLI) and settle the panel.
    let mut handled_cancel = use_signal(|| 0u32);
    use_effect(move || {
        let cancel = auto_cancel();
        if cancel == *handled_cancel.peek() {
            return;
        }
        handled_cancel.set(cancel);
        if let Some(task) = current_task.write().take() {
            task.cancel();
        }
        touring.set(false);
        pending.set(false);
        running.set(false);
        narrating.set(false);
        paused.set(false);
        messages.write().push(Turn {
            role: "note".into(),
            text: "자동 진행을 해제했습니다.".into(),
        });
        document::eval(SCROLL);
    });
    let send = Callback::new(move |_: ()| {
        let question = draft().trim().to_string();
        if question.is_empty() || pending() {
            return;
        }
        draft.set(String::new());
        // The textarea is uncontrolled (no value binding) so Korean IME composition survives
        // re-renders; clear it in the DOM directly.
        document::eval(
            "const t=document.querySelector('.assistant-compose textarea');if(t){t.value='';}",
        );
        if question == "/clear" {
            messages.set(Vec::new());
            error.set(String::new());
            return;
        }
        if question == AUTO_ALL || question == TOUR_ALL {
            autopilot.set(true);
            touring.set(question == TOUR_ALL);
            auto_started_on.set(mission_marker.peek().clone());
        }
        let is_auto = question == AUTO || question == AUTO_ALL || question == TOUR_ALL;
        messages.write().push(Turn {
            role: "user".into(),
            text: question,
        });
        if is_auto {
            auto.call(());
        } else {
            request.call(());
        }
    });
    // Suggested-question chips were removed: the student types their own question.
    let _ = (&kind, &ask);
    // The speed lives in the page (shared with 읽어주기): show the saved value once mounted.
    use_effect(|| {
        document::eval("const s=document.querySelector('select.assistant-rate');if(s&&window.molipVoice)s.value=String(molipVoice.rate);");
    });
    // The page scripts load after the first render; tell the agent whether to speak.
    use_effect(move || {
        let on = settings.read().narration_voice;
        let name = serde_json::to_string(&settings.read().narration_voice_name).unwrap_or_default();
        document::eval(&format!(
            "window.molipAgent && (molipAgent.setVoice({on}), molipAgent.setVoiceName({name}));"
        ));
    });
    // A failed question stays in the conversation; 다시 시도 re-sends it without duplicating it.
    let can_retry = move || messages.read().last().is_some_and(|t| t.role == "user") && !pending();
    rsx! {
        section { class:"assistant-panel", aria_label:"AI에게 물어보기",
            header { class:"assistant-head",
                div { h2 { "AI에게 물어보기" } p { class:"assistant-scope", "'해 줘'라고 하면 코드 넣기·실행·제출·퀴즈 답·이동까지 대신합니다 · /clear 로 대화 지우기 · {settings.read().provider.label()}" } }
                div { class:"assistant-actions",
                    if running() {
                        // id narration-pause: the Space key (assets/layout/shortcuts.js) clicks it.
                        button { id:"narration-pause", class:"assistant-pause", title:"Space", onclick: move |_| {
                            let p = !paused();
                            paused.set(p);
                            document::eval(if p {"window.molipAgent && molipAgent.pause();"} else {"window.molipAgent && molipAgent.resume();"});
                        }, {if paused() {"▶ 재개"} else {"⏸ 일시정지"}} }
                    }
                    if running() || autopilot() {
                        button { class:"assistant-stop", onclick: move |_| { if autopilot() { autopilot.set(false); auto_cancel += 1; } paused.set(false); document::eval("window.molipAgent && molipAgent.stop();"); }, "⏹ 멈춤" }
                    }
                    select { class:"assistant-rate", title:"해설·읽어주기 속도", onchange: move |e| { document::eval(&format!("window.molipVoice && molipVoice.setRate({});", e.value())); },
                        for rate in ["0.75", "1", "1.25", "1.5", "1.75", "2"] {
                            option { value: rate, {format!("{rate}배")} }
                        }
                    }
                    button { title:"해설 모드의 설명과 AI의 답을 소리 내어 읽을지", onclick: move |_| {
                        let on = !settings.read().narration_voice;
                        settings.write().narration_voice = on;
                        let _ = settings.read().save();
                        document::eval(&format!("window.molipAgent && molipAgent.setVoice({on});"));
                    }, {if settings.read().narration_voice {"🔊 소리"} else {"🔇 무음"}} }
                    button { onclick: move |_| { let v = show_settings(); show_settings.set(!v); }, "설정" }
                    button { class:"danger-outline", onclick: move |_| { messages.set(Vec::new()); error.set(String::new()); }, "대화 지우기" }
                    button { onclick: move |_| onclose.call(()), "접기 ×" }
                }
            }
            if show_settings() { div { class:"assistant-settings",
                label { "답하는 쪽"
                    select { onchange: move |e| settings.write().provider = Provider::from_id(&e.value()),
                        for p in Provider::ALL {
                            option { value: p.id(), selected: settings.read().provider == p, {p.label()} }
                        }
                    }
                }
                label { "명령"
                    if settings.read().provider == Provider::ClaudeCode {
                        input { initial_value:"{settings.read().claude_command}", placeholder:"claude", oninput: move |e| settings.write().claude_command = e.value() }
                    } else {
                        input { initial_value:"{settings.read().codex_command}", placeholder:"codex", oninput: move |e| settings.write().codex_command = e.value() }
                    }
                }
                p { class:"assistant-hint", "이 컴퓨터에 설치되어 터미널에서 로그인된 CLI를 그대로 씁니다. API 키는 필요 없고, 답에 10초~1분쯤 걸립니다. 명령을 못 찾으면 전체 경로를 적으세요." }
                label { "해설 목소리"
                    select { onchange: move |e| settings.write().narration_voice_name = e.value(),
                        for (id, label) in molip_quest::tts::VOICES {
                            option { value: id, selected: settings.read().narration_voice_name == id, {label} }
                        }
                    }
                }
                p { class:"assistant-hint", "자연스러운 음성은 Microsoft Edge의 읽어 주기 음성을 앱이 직접 받아 오며 인터넷을 씁니다. 끊기면 기기 음성으로 읽습니다." }
                div { class:"assistant-settings-actions",
                    button { class:"primary", onclick: move |_| {
                        let result = settings.read().save();
                        match result {
                            Ok(()) => { show_settings.set(false); error.set(String::new()); }
                            Err(e) => error.set(e),
                        }
                    }, "저장" }
                }
            } }
            div { class:"assistant-messages",
                if messages.read().is_empty() {
                    p { class:"assistant-empty", "예: 이 장의 '기준 모델'이 왜 필요한지 다시 설명해 줘 · 지금 쓴 코드가 왜 안 되는지 봐 줘 · 이 표에서 분모가 뭐야" }
                }
                for (i, turn) in messages.read().iter().enumerate() {
                    if turn.role == "note" {
                        div { key:"{i}", class:"assistant-note", "{turn.text}" }
                    } else if turn.role == "tool" {
                        div { key:"{i}", class:"assistant-tool", span { class:"assistant-tool-label", "앱" } pre { "{turn.text}" } }
                    } else {
                        div { key:"{i}", class: if turn.role == "user" {"assistant-msg user"} else {"assistant-msg model"},
                            if turn.role == "user" { p { "{turn.text}" } } else { Markdown { text: turn.text.clone() } }
                            // Reading controls under an answer (not under a narration's script dump).
                            if turn.role == "model" && !turn.text.starts_with("▶ 자동 해설") {
                                div { class:"assistant-tts",
                                    if speaking() == Some(i) {
                                        span { class:"assistant-tts-live", span { class:"assistant-tts-dot" } "읽는 중" }
                                        button { onclick: move |_| stop_reading.call(()), "⏹ 멈춤" }
                                    } else {
                                        button { onclick: { let text = turn.text.clone(); move |_| read_aloud.call((i, text.clone(), true)) }, "🔊 읽기" }
                                    }
                                }
                            }
                        }
                    }
                }
                if pending() { div { class:"assistant-msg model pending", {if paused() {"⏸ 일시정지 중 · ▶ 재개 또는 Space"} else if narrating() {"▶ 자동 해설 진행 중 · ⏸ 또는 Space로 일시정지"} else if running() {"앱에서 동작을 실행하는 중…"} else {"생각하는 중…"}} } }
                if !error().is_empty() {
                    div { class:"assistant-error",
                        p { class:"error", "{error}" }
                        if can_retry() { button { onclick: move |_| request.call(()), "다시 시도" } }
                    }
                }
            }
            div { class:"assistant-footer",
                div { class:"assistant-context", span { class:"assistant-context-dot" } "「{title}」 기준으로 답하는 중" }
            }
            div { class:"assistant-compose",
                textarea { initial_value:"", placeholder:"질문을 적고 Enter (줄 바꿈은 Shift+Enter)", rows:"2",
                    oninput: move |e| draft.set(e.value()),
                    onkeydown: move |e| {
                        if e.key() == Key::Enter && !e.modifiers().contains(Modifiers::SHIFT) {
                            e.prevent_default();
                            send.call(());
                        }
                    }
                }
                button { class:"primary", disabled: pending(), onclick: move |_| send.call(()), "보내기" }
            }
        }
    }
}

/// Previous/next mission buttons for the bottom of a concept or quiz card.
#[component]
fn MissionNav(nav_prev: bool, nav_next: bool, onnavigate: EventHandler<i32>) -> Element {
    rsx! { div {class:"mission-nav",aria_label:"학습 이동",
        button {disabled:!nav_prev,onclick:move |_|onnavigate.call(-1),"← 이전"}
        button {disabled:!nav_next,onclick:move |_|onnavigate.call(1),"다음 →"}
    } }
}

#[component]
pub(crate) fn UnitWorkspace(
    course_id: String,
    unit: Unit,
    oncompleted: EventHandler<bool>,
) -> Element {
    let language = unit.language;
    let key = format!("local:{course_id}:{}:{}", unit.id, unit.revision);
    // Already passed at this revision: 제출 reads 다시 제출 and turns green, and stays so.
    let mut solved = use_signal({
        let course_id = course_id.clone();
        let unit = unit.clone();
        move || {
            molip_quest::learning_store::LearningStore::user_store()
                .and_then(|store| store.unit_completed(&course_id, &unit))
                .unwrap_or(false)
        }
    });
    let initial = use_hook(|| {
        drafts::load(&key)
            .ok()
            .flatten()
            .unwrap_or_else(|| drafts::Draft {
                code: unit.starter_code.clone(),
                answers: HashMap::new(),
            })
    });
    let mut code = use_signal(|| initial.code.clone());
    let mut editor_reset = use_signal(|| 0u64);
    let mut answers = use_signal(|| initial.answers.clone());
    let sample_input = use_hook(|| {
        unit.tests
            .first()
            .map(|test| test.input.clone())
            .unwrap_or_default()
    });
    let mut input = use_signal(|| sample_input.clone());
    let mut output = use_signal(String::new);
    // The last run or submission failed: the result pane turns red.
    let mut output_failed = use_signal(|| false);
    let mut artifacts = use_signal(Vec::<Artifact>::new);
    let mut message = use_signal(String::new);
    let mut busy = use_signal(|| false);
    let lines: Vec<Vec<(String, Option<String>)>> = unit
        .starter_code
        .lines()
        .map(|line| {
            let mut rest = line;
            let mut parts = Vec::new();
            while let Some(start) = rest.find("{{") {
                let Some(end) = rest[start + 2..].find("}}") else {
                    break;
                };
                let name = &rest[start + 2..start + 2 + end];
                parts.push((rest[..start].to_string(), None));
                if unit.blanks.iter().any(|b| b == name) {
                    parts.push((String::new(), Some(name.to_string())));
                } else {
                    parts.push((rest[start..start + end + 4].to_string(), None));
                }
                rest = &rest[start + end + 4..];
            }
            parts.push((rest.to_string(), None));
            parts
        })
        .collect();
    let mut guide_open = use_signal(|| false);
    let mut viewer = use_signal(|| None::<String>);
    let data_files = data_files(&format!("{}\n{}", unit.starter_code, unit.content));
    rsx! {article{class:"lesson",
        if guide_open() {PromptGuide {unit:unit.clone(),code:code(),onclose:move |_|guide_open.set(false)}}
        if let Some(path)=viewer() {DataViewer {path,onclose:move |_|viewer.set(None)}}
        section{class:"problem-pane",h2{"{unit.title}"}h3{"문제 설명"}Markdown {text:unit.content.clone()}
            if !VIEW_ONLY && !data_files.is_empty() {div {class:"data-files",
                for file in data_files.iter().cloned() {button {class:"data-file-open",onclick:move |_|viewer.set(Some(file.clone())),"자료 보기 · {file}"}}
            }}
            div {class:"prompt-buttons",
                button {class:"prompt-copy",onclick:{let unit=unit.clone();move |_|{
                    let prompt=molip_quest::curriculum::answer_prompt(&unit,&code());
                    match copy_to_clipboard(prompt) {
                        Ok(())=>toast("인간 버전을 복사했습니다. AI에 붙여넣고, 받은 코드를 편집기에 넣으세요.", "success"),
                        Err(e)=>toast(&format!("클립보드 복사에 실패했습니다: {e}"), "error")
                    }
                }},"프롬프트 복사 · 인간 버전"}
                button {class:"prompt-copy",onclick:{let unit=unit.clone();move |_|{
                    let prompt=molip_quest::curriculum::machine_prompt(&unit,&code());
                    match copy_to_clipboard(prompt) {
                        Ok(())=>toast("기계 버전을 복사했습니다. AI에 붙여넣고, 받은 코드를 편집기에 넣으세요.", "success"),
                        Err(e)=>toast(&format!("클립보드 복사에 실패했습니다: {e}"), "error")
                    }
                }},"프롬프트 복사 · 기계 버전"}
                button {class:"prompt-guide-open",onclick:move |_|guide_open.set(true),"프롬프트 해설"}
            }

            if !unit.solution.is_empty() { details { summary {"정답과 풀이 보기"} Markdown { text:format!("```{}\n{}\n```", unit.language.name(), unit.solution) } } }
            if !unit.blanks.is_empty(){p{class:"blank-note","코드의 빈칸만 채워보세요. 나머지 코드는 수정하지 않습니다."}}
        }
        div{class:"split-handle split-col",role:"separator",aria_orientation:"vertical",aria_label:"문제와 코드 영역 너비 조절",tabindex:"0",title:"드래그로 너비 조절, 더블 클릭으로 되돌리기"}
        section{class:"coding-pane",div{class:"pane-heading",strong{{unit.language.filename()}}
        div{class:"pane-actions",button{class:"danger-outline",title:"작성 중인 코드를 지우고 준비 코드로 되돌립니다",disabled:busy(),onclick:{let unit=unit.clone();let key=key.clone();move |_|{code.set(unit.starter_code.clone());editor_reset+=1;answers.set(HashMap::new());output.set(String::new());output_failed.set(false);artifacts.set(vec![]);message.set(String::new());let _=drafts::save(&key,&code(),&answers());}},"초기화"}
        button{disabled:busy(),title:if cfg!(target_os="macos") {"⌘Enter"} else {"Ctrl+Enter"},onclick:move |_|async move{busy.set(true);message.set(String::new());artifacts.set(vec![]);match run_code(language,&code(),&input()).await{Ok(result)=>{artifacts.set(result.artifacts);if result.stderr.contains("EOFError: EOF when reading a line") {message.set("실행 입력이 부족합니다. 실행 입력 칸에 문제에서 요구한 값을 넣어주세요.".into());}else if result.success {message.set("실행 완료. 제출하면 전체 테스트로 정답을 확인합니다.".into());}output_failed.set(!result.success);output.set(format!("{}\n{}\n{}",result.stdout,result.stderr,if result.success {"실행 완료"} else {"실행 실패"}));},Err(e)=>message.set(e)}busy.set(false);},"코드 실행"}
            button{class:if solved() {"primary resubmit"} else {"primary"},disabled:busy(),title:if cfg!(target_os="macos") {"⌘Enter 두 번 연타, 또는 ⌘⇧Enter"} else {"Ctrl+Enter 두 번 연타, 또는 Ctrl+Shift+Enter"},onclick:{let unit=unit.clone();let course_id=course_id.clone();move |_|{let unit=unit.clone();let course_id=course_id.clone();async move{
                busy.set(true);message.set(String::new());artifacts.set(vec![]);let source=code();let blank_answers=answers();
                if !unit.blanks.is_empty()&&assemble(&unit,&blank_answers).as_deref()!=Ok(source.as_str()){message.set("지정된 빈칸을 모두 채워주세요.".into());busy.set(false);return;}
                match check_unit(&unit,&source).await{Err(e)=>message.set(e),Ok(report)=>{output.set(report.cases.iter().enumerate().map(|(i,c)|format!("테스트 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed {"통과"} else {"실패"},c.input.trim(),c.expected.trim(),c.stdout.trim(),c.stderr.trim())).collect::<Vec<_>>().join("\n\n"));let passed=report.passed;output_failed.set(!passed);
                    match molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|store.save(&course_id,&unit,&source,&report)) {
                        Ok(())=>{message.set(if passed {"통과했습니다. 완료 기록을 이 컴퓨터에 저장했습니다."} else {"검사를 통과하지 못했습니다. 결과를 이 컴퓨터에 저장했습니다."}.into());if passed {solved.set(true);}oncompleted.call(passed);},
                        Err(e)=>message.set(e)
                    }
                }}busy.set(false);
            }}},{if solved() {"다시 제출"} else {"제출"}}}
        }
        }
        div{class:"editor-pane",
        if unit.blanks.is_empty(){textarea{class:"code-editor", "data-code-editor":unit.language.name(), "data-editor-value":code(),"data-editor-reset":editor_reset().to_string(),aria_label:format!("{} 코드",unit.language.name()),spellcheck:false,initial_value:initial.code.clone(),oninput:{let key=key.clone();move|e|{code.set(e.value());if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}
        else{div{class:"inline-code",for (number,parts) in lines.iter().enumerate(){div{class:"code-line",span{class:"line-number","{number+1}"}div{class:"line-source",for (text,blank) in parts {if let Some(blank)=blank {input{class:"code-blank",aria_label:"빈칸 {blank}",spellcheck:false,value:answers.read().get(blank).cloned().unwrap_or_default(),oninput:{let blank=blank.clone();let unit=unit.clone();let key=key.clone();move|e|{answers.write().insert(blank.clone(),e.value());if let Ok(assembled)=assemble(&unit,&answers()){code.set(assembled);if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}}else{span{"{text}"}}}}}}}}
        }
        div{class:"split-handle split-row",role:"separator",aria_orientation:"horizontal",aria_label:"편집기와 실행 결과 높이 조절",tabindex:"0",title:"드래그로 높이 조절, 더블 클릭으로 되돌리기"}
        section{class:"result-pane",h3{"실행 결과"}details{open:!unit.tests.is_empty(),summary{"실행 입력"}p{"아래 입력값으로 실행합니다. 예제 입력을 바꾸며 연습할 수 있어요."}textarea{aria_label:"실행 입력",initial_value:sample_input.clone(),oninput:move|e|input.set(e.value())}}
            p{class:if output_failed() {"execution-status failed"} else {"execution-status"},role:"status","{message}"}
            pre{class:if output_failed() {"output failed"} else {"output"},if output().is_empty(){"실행 결과가 여기에 표시됩니다."}else{"{output}"}}
            RichResults { artifacts: artifacts() }
        }}
    }}
}

/// View-only coding mission for the Android build: read the problem, acknowledge, move on.
#[component]
fn ReadOnlyMission(course_id: String, unit: Unit, oncompleted: EventHandler<bool>) -> Element {
    let mut message = use_signal(String::new);
    rsx! {article {class:"reading-mission view-only-mission",span {class:"badge","코딩 미션 · 열람"} h2 {"{unit.title}"}
        p {class:"muted","Android에서는 코드를 실행·채점하지 않습니다. 문제와 준비 코드를 읽고 데스크톱 앱에서 직접 풀어보세요. 아래 버튼을 누르면 다음 미션이 열립니다."}
        Markdown {text:unit.content.clone()}
        h3 {{format!("준비 코드 · {}", unit.language.filename())}} pre {class:"output","{unit.starter_code}"}
        if !unit.tests.is_empty() {details {summary {"입출력 예제"}
            for (n,test) in unit.tests.iter().enumerate() {pre {class:"output",{format!("예제 {}\n입력:\n{}\n예상 출력:\n{}",n+1,test.input.trim_end(),test.expected.trim_end())}}}
        }}
        p {class:"execution-status",role:"status","{message}"}
        button {class:"primary",onclick:{let unit=unit.clone();move |_|{
            let report=molip_quest::runner::TestReport{passed:true,cases:vec![molip_quest::runner::TestCaseResult{input:String::new(),expected:"열람 확인".into(),stdout:"열람 확인".into(),stderr:String::new(),passed:true,state:"viewed".into()}]};
            match molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|store.save(&course_id,&unit,&unit.starter_code,&report)) {
                Ok(())=>oncompleted.call(true),
                Err(e)=>message.set(e)
            }
        }},"읽었어요 · 다음 미션"}
    }}
}

#[component]
fn RichResults(artifacts: Vec<Artifact>) -> Element {
    rsx! { div { class: "rich-results",
        for artifact in artifacts { match artifact {
            Artifact::Html { title, srcdoc } => rsx! { iframe { title, srcdoc, "sandbox":"allow-scripts allow-forms" } },
            Artifact::Image { title, data_url } => rsx! { figure { class:"plot-result", figcaption { "{title}" } img { src: data_url, alt: title } } },
            Artifact::Table { title, columns, rows, total_rows, total_columns } => rsx! { section { class:"table-result",
                h4 { "{title} · {total_rows}행 × {total_columns}열" }
                if total_rows > 100 || total_columns > 30 { p { class:"muted", "앞 100행·30열까지만 미리보기로 표시합니다." } }
                div { class:"data-grid", table { thead { tr { for column in columns { th { "{column}" } } } }
                    tbody { for row in rows { tr { for cell in row { td { "{cell}" } } } } }
                } }
            } },
        } }
    } }
}

/// "Start over" button with a confirmation step; wipes completions, attempts and drafts for the course.
/// Full-screen explanation of the human prompt (which words carry the expertise and why),
/// with the machine version of the same request beside it.
#[component]
fn PromptGuide(unit: Unit, code: String, onclose: EventHandler<()>) -> Element {
    let guide = molip_quest::curriculum::prompt_guide(&unit);
    let prompt = molip_quest::curriculum::machine_prompt(&unit, &code);
    rsx! { div { class:"prompt-guide-layer", role:"dialog", aria_modal:"true", aria_label:"정답 구하는 프롬프트 해설",
        onkeydown: move |e| { if e.key() == Key::Escape { onclose.call(()); } },
        header { class:"prompt-guide-header",
            h2 { "프롬프트 해설 · 인간 버전" }
            span { class:"prompt-guide-unit", "{unit.title}" }
            button { class:"prompt-guide-close", autofocus:true, onclick: move |_| onclose.call(()), "닫기 ×" }
        }
        div { class:"prompt-guide-body",
            section { class:"prompt-guide-text", Markdown { text: guide } }
            section { class:"prompt-guide-prompt",
                h3 { "기계 버전" }
                p { class:"prompt-guide-note", "같은 요청을 명세서로 쓴 것. 자동화할 때 쓴다." }
                button { class:"prompt-copy", onclick: {let prompt=prompt.clone(); move |_| {
                    match copy_to_clipboard(prompt.clone()) {
                        Ok(()) => toast("기계 버전을 복사했습니다.", "success"),
                        Err(e) => toast(&format!("클립보드 복사에 실패했습니다: {e}"), "error"),
                    }
                }}, "기계 버전 복사" }
                pre { class:"prompt-guide-source", "{prompt}" }
            }
        }
    } }
}

/// One-page overviews reachable from the classroom home: every deck, every comic, every
/// interactive picture, or every concept text of the course.
#[derive(Clone, Copy, PartialEq, Debug)]
pub enum GalleryKind {
    Slides,
    Comics,
    Interactive,
    Concepts,
}

impl GalleryKind {
    pub const ALL: [GalleryKind; 4] = [
        GalleryKind::Slides,
        GalleryKind::Comics,
        GalleryKind::Interactive,
        GalleryKind::Concepts,
    ];
    pub fn label(self) -> &'static str {
        match self {
            GalleryKind::Slides => "PPT 모아보기",
            GalleryKind::Comics => "만화 모아보기",
            GalleryKind::Interactive => "발전적 시각화 모아보기",
            GalleryKind::Concepts => "개념 모아보기",
        }
    }
    fn blurb(self) -> &'static str {
        match self {
            GalleryKind::Slides => "수업에서 띄우는 슬라이드 목록입니다. 하나를 열면 이전·다음 장과 전체 화면으로 넘겨 볼 수 있습니다.",
            GalleryKind::Comics => "개념, 문제, 슬라이드에 들어 있는 만화 목록입니다. 열어서 보고, Ctrl을 누른 채 더블 클릭하면 읽어 줍니다.",
            GalleryKind::Interactive => "한 단계씩 쌓이는 시각화 목록입니다. 열어서 다음 단계 버튼과 슬라이더를 직접 움직여 보세요.",
            GalleryKind::Concepts => "문제와 퀴즈를 뺀 개념 설명 목록입니다. 개념만 빠르게 훑고 싶을 때 쓰세요.",
        }
    }
}

struct GalleryItem {
    location: String,
    title: String,
    markdown: String,
    deck: bool,
}

fn gallery_items(course: &Course, kind: GalleryKind) -> Vec<GalleryItem> {
    let mut items = Vec::new();
    for chapter in &course.chapters {
        for unit in &chapter.units {
            for activity in &unit.activities {
                // Course order is time order: the unit (day · period) leads, the chapter follows.
                let location = format!("{} · {}", unit.title, chapter.title);
                match kind {
                    GalleryKind::Slides => {
                        if let ActivityKind::Slides { markdown } = &activity.kind {
                            items.push(GalleryItem {
                                location,
                                title: activity.title.clone(),
                                markdown: markdown.clone(),
                                deck: true,
                            });
                        }
                    }
                    GalleryKind::Concepts => {
                        if let ActivityKind::Concept { body, .. } = &activity.kind {
                            items.push(GalleryItem {
                                location,
                                title: activity.title.clone(),
                                markdown: body.clone(),
                                deck: false,
                            });
                        }
                    }
                    GalleryKind::Comics | GalleryKind::Interactive => {
                        let lang = if kind == GalleryKind::Comics {
                            "comic-gen"
                        } else {
                            "interactive"
                        };
                        let texts: Vec<&str> = match &activity.kind {
                            ActivityKind::Concept { body, check } => {
                                vec![body, &check.prompt, &check.explanation]
                            }
                            ActivityKind::Coding { problem } => vec![&problem.content],
                            ActivityKind::Quiz { questions } => questions
                                .iter()
                                .flat_map(|q| [q.prompt.as_str(), q.explanation.as_str()])
                                .collect(),
                            ActivityKind::Slides { markdown } => vec![markdown],
                        };
                        for block in texts
                            .iter()
                            .flat_map(|text| molip_quest::curriculum::fenced_blocks(text, lang))
                        {
                            let own_title = block
                                .lines()
                                .find_map(|line| line.trim().strip_prefix("제목:"))
                                .map(|t| t.trim().to_string());
                            items.push(GalleryItem {
                                location: format!(
                                    "{location} · {} · {}",
                                    activity.label(),
                                    activity.title
                                ),
                                title: own_title.unwrap_or_else(|| {
                                    format!("{} · {}", activity.label(), activity.title)
                                }),
                                markdown: format!("```{lang}\n{block}\n```"),
                                deck: false,
                            });
                        }
                    }
                }
            }
        }
    }
    items
}

/// A gallery page: the list of entries first; one entry opens on click, with
/// previous/next to walk through them and a button back to the list.
#[component]
pub fn Gallery(course: Course, kind: GalleryKind) -> Element {
    let items = gallery_items(&course, kind);
    let mut selected: Signal<Option<usize>> = use_signal(|| None);
    let total = items.len();
    rsx! { article { class:"reading-mission gallery",
        span { class:"badge", {kind.label()} } h2 { {kind.label()} }
        p { class:"slides-help", {kind.blurb()} }
        match selected() {
            None => rsx! {
                p { class:"gallery-count", {format!("모두 {total}개 · 제목을 누르면 열립니다")} }
                ol { class:"gallery-list",
                    for (n, item) in items.iter().enumerate() {
                        li { key:"{kind:?}-{n}",
                            button { class:"gallery-entry", onclick: move |_| selected.set(Some(n)),
                                span { class:"gallery-entry-title", {format!("{}. {}", n + 1, item.title)} }
                                span { class:"gallery-location", "{item.location}" }
                            }
                        }
                    }
                }
            },
            Some(n) => {
                let item = &items[n.min(total.saturating_sub(1))];
                rsx! {
                    div { class:"gallery-nav",
                        button { onclick: move |_| selected.set(None), "← 목록" }
                        button { disabled: n == 0, onclick: move |_| selected.set(Some(n.saturating_sub(1))), "← 이전" }
                        span { class:"gallery-count", {format!("{} / {total}", n + 1)} }
                        button { disabled: n + 1 >= total, onclick: move |_| selected.set(Some(n + 1)), "다음 →" }
                    }
                    // Keyboard (assets/layout/shortcuts.js): Ctrl/⌘+←/→ step entries, Ctrl/⌘+↑ back to
                    // the list. A deck's → past its last slide also lands here (slides.js leaveTo).
                    div { class:"shortcut-targets", hidden:true, "aria-hidden":"true",
                        button { id:"shortcut-prev-mission", tabindex:"-1", disabled: n == 0, onclick: move |_| selected.set(Some(n.saturating_sub(1))) }
                        button { id:"shortcut-next-mission", tabindex:"-1", disabled: n + 1 >= total, onclick: move |_| selected.set(Some(n + 1)) }
                        button { id:"shortcut-prev-unit", tabindex:"-1", onclick: move |_| selected.set(None) }
                    }
                    section { class:"gallery-item",
                        p { class:"gallery-location", "{item.location}" }
                        h3 { "{item.title}" }
                        if item.deck {
                            div { class:"slides-host", "data-marp-source": item.markdown.clone() }
                        } else {
                            Markdown { text: item.markdown.clone() }
                        }
                    }
                }
            }
        }
    } }
}

/// Missions in the course, which is what levels count.
pub fn total_missions(course: &Course) -> usize {
    course
        .chapters
        .iter()
        .flat_map(|c| c.units.iter())
        .map(|u| u.activities.len())
        .sum()
}

/// Cleared missions of this course on this computer.
pub fn completed_missions(course: &Course) -> usize {
    molip_quest::learning_store::LearningStore::user_store()
        .and_then(|store| store.completed_items(course))
        .map(|items| items.len())
        .unwrap_or(0)
}

/// Every level's avatar in order: the levels already reached, the current one highlighted,
/// and the ones ahead dimmed so the student sees what 큐 grows into.
#[component]
pub fn AvatarGallery(course: Course) -> Element {
    use molip_quest::avatar;
    let completed = completed_missions(&course);
    let current = avatar::level_for(completed);
    let last = avatar::max_level(total_missions(&course));
    rsx! { article { class:"reading-mission gallery avatar-gallery",
        span { class:"badge", "아바타 모아보기" } h2 { "레벨 아바타" }
        p { class:"slides-help", {format!("미션 {}개마다 레벨이 오르고, 레벨 {}개마다 큐가 새 모습으로 자랍니다. 지금은 Lv. {current} · {}.", avatar::MISSIONS_PER_LEVEL, avatar::LEVELS_PER_TIER, avatar::title(current))} }
        ol { class:"avatar-grid",
            for level in 1..=last {
                li { key:"avatar-{level}", class: if level == current {"avatar-cell current"} else if level < current {"avatar-cell reached"} else {"avatar-cell ahead"},
                    div { dangerous_inner_html: avatar::svg(level) }
                    strong { {format!("Lv. {level}")} }
                    span { {avatar::title(level)} }
                    span { {format!("{} XP", (level - 1) * avatar::MISSIONS_PER_LEVEL * avatar::XP_PER_MISSION)} }
                }
            }
        }
    } }
}

#[component]
pub fn ResetProgress(course_id: String, onreset: EventHandler<()>) -> Element {
    let mut confirming = use_signal(|| false);
    let mut message = use_signal(String::new);
    rsx! {
        button { class:"reset-progress", onclick: move |_| { message.set(String::new()); confirming.set(true); }, "진도 초기화" }
        if confirming() { div { class:"doctor-backdrop", section { class:"doctor-panel", role:"dialog", aria_label:"진도 초기화", aria_modal:"true",
            h2 { "처음부터 다시 시작할까요?" }
            p { "이 컴퓨터에 저장된 클리어 기록, 제출 기록, 작성 중인 코드와 퀴즈 답안을 모두 지웁니다. 되돌릴 수 없습니다." }
            if !message().is_empty() { p { class:"error", "{message}" } }
            div { class:"actions",
                button { onclick: move |_| confirming.set(false), "취소" }
                button { class:"danger", autofocus:true, onclick: {let course_id=course_id.clone(); move |_| {
                    match molip_quest::reset_progress(&course_id) {
                        Ok(()) => { confirming.set(false); onreset.call(()); }
                        Err(e) => message.set(e),
                    }
                }}, "모두 지우고 처음부터" }
            }
        } } }
    }
}

#[component]
pub fn JavaDoctorPanel() -> Element {
    let mut open = use_signal(|| false);
    let mut busy = use_signal(|| false);
    let mut result = use_signal(|| None::<Result<String, String>>);
    let inspect = Callback::new(move |_: ()| {
        if busy() {
            return;
        }
        open.set(true);
        busy.set(true);
        spawn(async move {
            let checked = async {
                let version = molip_quest::java::version().await?;
                let run = molip_quest::java::run("class Main { public static void main(String[] args) { System.out.println(25); } }", "").await?;
                if !run.success || run.stdout.trim() != "25" { return Err(format!("JDK 25 소스 실행을 확인하지 못했어요: {}", run.stderr)); }
                Ok(format!("{version}\nMain.java 컴파일·실행 확인 완료"))
            }.await;
            result.set(Some(checked));
            busy.set(false);
        });
    });
    rsx! {
        button { disabled:busy(), onclick:move |_|inspect.call(()), "환경 진단 · JDK 25" }
        if open() { div { class:"doctor-backdrop", section { class:"doctor-panel", role:"dialog", aria_label:"JDK 25 학습 환경",
            h2 { "자바 학습 환경 · JDK 25" }
            p { "JDK 25를 설치한 뒤 앱을 다시 여세요. JAVA_HOME에 JDK 폴더를 지정할 수 있어요. MOLIP_JAVA로 java 실행 파일을 지정할 수도 있어요." }
            p { "터미널에서 java --version과 javac --version을 확인하세요. 이 과정은 preview 옵션을 사용하지 않아요." }
            a { href:"https://adoptium.net/temurin/releases/?version=25", target:"_blank", "JDK 25 설치 파일" }
            if busy() { p { role:"status", "버전과 실제 소스 실행을 확인하는 중이에요…" } }
            match result() { Some(Ok(text)) => rsx! { pre { class:"doctor-check ready", "{text}" } }, Some(Err(error)) => rsx! { p { class:"error", "{error}" } }, None => rsx! {} }
            div { class:"actions", button { disabled:busy(), onclick:move |_|inspect.call(()), "다시 검사" } button { onclick:move |_|open.set(false), "닫기" } }
        } } }
    }
}

#[component]
pub fn DoctorPanel() -> Element {
    if VIEW_ONLY {
        return rsx! { span { class:"muted", "열람 모드 · Python 실행 없음" } };
    }
    let mut open = use_signal(|| false);
    let mut busy = use_signal(|| false);
    let mut checks = use_signal(Vec::<molip_quest::doctor::Check>::new);
    // 환경 설치: the installer's output, line by line, and whether it is running.
    let mut installing = use_signal(|| false);
    let mut install_log = use_signal(Vec::<String>::new);
    let inspect = Callback::new(move |_: ()| {
        if busy() || installing() {
            return;
        }
        spawn(async move {
            busy.set(true);
            checks.set(vec![]);
            checks.set(molip_quest::doctor::inspect().await);
            busy.set(false);
        });
    });
    let install = Callback::new(move |_: ()| {
        if installing() || busy() {
            return;
        }
        open.set(true);
        installing.set(true);
        install_log.set(vec![
            "학습용 Python 환경을 이 컴퓨터에 새로 설치합니다. 인터넷이 필요하고 몇 분 걸립니다."
                .into(),
        ]);
        spawn(async move {
            let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel::<String>();
            let worker = tokio::spawn(molip_quest::doctor::install(tx));
            while let Some(line) = rx.recv().await {
                let mut log = install_log.write();
                log.push(line);
                if log.len() > 200 {
                    log.remove(0);
                }
            }
            match worker.await.unwrap_or_else(|e| Err(e.to_string())) {
                Ok(done) => install_log.write().push(format!("✓ {done}")),
                Err(e) => install_log.write().push(format!("! 설치 실패: {e}")),
            }
            installing.set(false);
            inspect.call(());
        });
    });
    rsx! {
        button { disabled: installing() || busy(), onclick: move |_| { open.set(true); inspect.call(()); }, "환경 진단" }
        button { disabled: installing() || busy(), title:"uv로 Python 3.13 환경을 새로 만들고 수업 패키지를 설치합니다", onclick: move |_| install.call(()), "환경 설치" }
        if open() { div { class:"doctor-backdrop", section { class:"doctor-panel", role:"dialog", aria_label:"학습 환경 진단",
            h2 { "학습 환경" }
            p { "Python과 실습 패키지 설치 상태를 확인합니다. 「환경 설치」는 이 컴퓨터에 맞는 환경을 처음부터 다시 만듭니다." }
            if busy() { p { role:"status", "검사 중입니다… 설치 직후 첫 검사는 최대 2분 정도 걸릴 수 있습니다." } }
            for check in checks() { div { class:if check.ready {"doctor-check ready"} else {"doctor-check missing"},
                strong { if check.ready {"✓ "} else {"! "} "{check.name}" } p { "{check.detail}" }
            } }
            if !install_log().is_empty() {
                h3 { class:"doctor-install-title", {if installing() {"환경 설치 중…"} else {"환경 설치"}} }
                pre { class:"doctor-install-log", {install_log().iter().rev().take(14).rev().cloned().collect::<Vec<_>>().join("\n")} }
            }
            div { class:"actions",
                button { disabled: installing() || busy(), onclick: move |_| inspect.call(()), "다시 검사" }
                button { disabled: installing() || busy(), onclick: move |_| install.call(()), {if installing() {"설치 중…"} else {"환경 설치 (다시)"}} }
                button { onclick:move |_|open.set(false), "닫기" }
            }
        } } }
    }
}

#[component]
pub(crate) fn Markdown(text: String) -> Element {
    rsx! {div {class:"markdown",dangerous_inner_html:molip_quest::markdown::render(&text)}}
}
