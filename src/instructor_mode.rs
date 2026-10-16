use dioxus::prelude::*;
use molip_quest::curriculum::{Activity, ActivityKind, Question, QuestionKind};

#[derive(Clone, Copy)]
pub(crate) struct InstructorSession(pub Signal<Option<crate::practice::Materials>>);

/// What the instructor asked the AI panel to do on the mission on screen. The panel plays it
/// exactly like a typed `/auto` (same progress line, 일시정지 and 멈춤), so the buttons only post
/// here. `seq` grows per click so the same request can be repeated.
#[derive(Clone, PartialEq)]
pub(crate) enum InstructorAction {
    /// The mission's precompiled 해설, as `/auto` plays it.
    Narrate,
    /// A JSON action list that fills in the answers and grades, no speech.
    Solve(String),
}
#[derive(Clone, PartialEq)]
pub(crate) struct InstructorRequest {
    pub seq: u32,
    pub action: InstructorAction,
}
#[derive(Clone, Copy)]
pub(crate) struct InstructorRequests(pub Signal<Option<InstructorRequest>>);

impl InstructorRequests {
    pub(crate) fn post(mut self, action: InstructorAction) {
        let seq = self.0.peek().as_ref().map_or(0, |r| r.seq) + 1;
        self.0.set(Some(InstructorRequest { seq, action }));
    }
    /// The sequence number as of now: a view that mounts later starts from here, so a request
    /// posted before it existed is not replayed.
    pub(crate) fn seq(self) -> u32 {
        self.0.peek().as_ref().map_or(0, |r| r.seq)
    }
}

#[component]
pub(crate) fn InstructorLogin() -> Element {
    let mut session = use_context::<InstructorSession>().0;
    let mut open = use_signal(|| false);
    let mut password = use_signal(String::new);
    let mut error = use_signal(String::new);
    let mut busy = use_signal(|| false);
    rsx! {
        button {class:"instructor-login",onclick:move |_|{if session().is_some(){document::eval("window.molipAgent?.stop()");session.set(None);}else{open.set(true);error.set(String::new());}}, {if session().is_some(){"강사모드 종료"}else{"강사모드 접속"}}}
        if open() {
            div {class:"doctor-backdrop",onclick:move |_|{if !busy(){open.set(false);password.set(String::new());}},
                form {class:"doctor-panel practice-password",role:"dialog",aria_modal:"true",aria_label:"강사모드 접속",onclick:move |e|e.stop_propagation(),onkeydown:move |e|{if e.key()==Key::Escape&&!busy(){open.set(false);password.set(String::new());}},
                    onsubmit:move |e|{e.prevent_default();if busy(){return;}let supplied=password();password.set(String::new());busy.set(true);error.set(String::new());spawn(async move {match tokio::task::spawn_blocking(move ||crate::practice::decrypt(&supplied)).await {Ok(Ok(materials))=>{session.set(Some(materials));open.set(false);},Ok(Err(message))=>error.set(message),Err(_)=>error.set("확인하지 못했습니다. 다시 시도하세요.".into())}busy.set(false);});},
                    h2 {"강사모드 접속"}label {r#for:"instructor-password","비밀번호"}
                    input {id:"instructor-password",r#type:"password",autofocus:true,autocomplete:"off",value:password(),oninput:move |e|password.set(e.value())}
                    p {class:"error",role:"status","{error}"}
                    div {class:"actions",button {class:"primary",r#type:"submit",disabled:busy()||password().is_empty(),{if busy(){"확인 중…"}else{"접속"}}}button {r#type:"button",disabled:busy(),onclick:move |_|{open.set(false);password.set(String::new());},"취소"}}
                }
            }
        }
    }
}

fn question_answer(question: &Question) -> String {
    let answer = match &question.kind {
        QuestionKind::Choice { options, correct } => format!(
            "{}. {}",
            correct + 1,
            options.get(*correct).map(String::as_str).unwrap_or("")
        ),
        QuestionKind::ShortAnswer { accepted } => accepted.join(" / "),
        QuestionKind::TableSelect { expected, .. } => expected.clone(),
    };
    format!(
        "{}\n정답: {}\n{}",
        question.prompt, answer, question.explanation
    )
}
fn answer(activity: &Activity) -> String {
    match &activity.kind {
        ActivityKind::Coding { problem } => {
            if !problem.solution.is_empty() {
                return problem.solution.clone();
            }
            let solutions: std::collections::HashMap<String, String> =
                serde_json::from_str(include_str!(concat!(env!("OUT_DIR"), "/private-solutions.json")))
                    .unwrap_or_default();
            if let Some(code) = solutions.get(&activity.id) {
                return code.clone();
            }
            let mut code = String::new();
            for action in &activity.narration {
                if action["action"] == "type_code" || action["action"] == "set_code" {
                    if action["replace"] == true || action["action"] == "set_code" {
                        code.clear();
                    }
                    if let Some(chunk) = action["code"].as_str() {
                        code.push_str(chunk);
                    }
                }
            }
            if code.is_empty() {
                "이 미션의 준비된 정답 코드가 없습니다.".into()
            } else {
                code
            }
        }
        ActivityKind::Concept { check, .. } => question_answer(check),
        ActivityKind::Quiz { questions } => questions
            .iter()
            .map(question_answer)
            .collect::<Vec<_>>()
            .join("\n\n"),
        ActivityKind::Slides { .. } => "슬라이드를 읽고 다음 장으로 진행하세요.".into(),
    }
}

/// What "정답 보기" runs through the tutor agent: the answers go in and grading is pressed, with
/// no answer card. Coding puts the solution in the editor and submits; concept and quiz replay the
/// answer_quiz steps of the compiled narration (the same answers the 해설 ticks) without speech.
pub(crate) fn solve_actions(activity: &Activity) -> serde_json::Value {
    use serde_json::json;
    match &activity.kind {
        ActivityKind::Coding { .. } => json!([
            {"action": "set_code", "code": answer(activity)},
            {"action": "submit"}
        ]),
        ActivityKind::Concept { .. } | ActivityKind::Quiz { .. } => {
            let mut steps: Vec<serde_json::Value> = activity
                .narration
                .iter()
                .filter(|a| a["action"] == "answer_quiz")
                .cloned()
                .map(|mut a| {
                    a.as_object_mut().map(|o| o.remove("say"));
                    a
                })
                .collect();
            if steps.is_empty() {
                let questions: Vec<&Question> = match &activity.kind {
                    ActivityKind::Concept { check, .. } => vec![check],
                    ActivityKind::Quiz { questions } => questions.iter().collect(),
                    _ => vec![],
                };
                let answers: serde_json::Map<String, serde_json::Value> = questions
                    .iter()
                    .enumerate()
                    .filter_map(|(i, q)| {
                        match &q.kind {
                            QuestionKind::Choice { correct, .. } => Some((correct + 1).to_string()),
                            QuestionKind::ShortAnswer { accepted } => accepted.first().cloned(),
                            QuestionKind::TableSelect { .. } => None,
                        }
                        .map(|a| ((i + 1).to_string(), serde_json::Value::String(a)))
                    })
                    .collect();
                steps.push(json!({"action": "answer_quiz", "answers": answers}));
            }
            serde_json::Value::Array(steps)
        }
        ActivityKind::Slides { .. } => json!([]),
    }
}

/// What `/tour-all` plays on a mission: its `tour` sentences, then the answers go in and the
/// mission is graded (a deck is marked watched without entering presentation mode).
pub(crate) fn tour_actions(activity: &Activity) -> serde_json::Value {
    use serde_json::json;
    let mut steps: Vec<serde_json::Value> = activity
        .tour
        .iter()
        .map(|line| json!({"action": "say", "target": "title", "text": line}))
        .collect();
    match &activity.kind {
        ActivityKind::Slides { .. } => {
            steps.push(json!({"action": "finish_slides", "quiet": true}))
        }
        _ => steps.extend(
            solve_actions(activity)
                .as_array()
                .cloned()
                .unwrap_or_default(),
        ),
    }
    serde_json::Value::Array(steps)
}

#[component]
pub(crate) fn InstructorControls(activity: Activity) -> Element {
    let session = use_context::<InstructorSession>().0;
    let requests = use_context::<InstructorRequests>();
    use_drop(|| {
        document::eval("window.molipAgent?.stop()");
    });
    if session().is_none() {
        return rsx! {};
    }
    // A deck has nothing to fill in: "정답 보기" marks it watched, the same as "다 봤어요 · 미션 완료".
    let slides = matches!(activity.kind, ActivityKind::Slides { .. });
    let solve = serde_json::to_string(&solve_actions(&activity)).unwrap_or_else(|_| "[]".into());
    let has_narration = !activity.narration.is_empty();
    rsx! {
        div {class:"instructor-controls",
            button {class:"instructor-answer",onclick:move |_|{
                if slides {document::eval("window.molipAgent?.stop();document.querySelector('.slides-finish')?.click()");return;}
                requests.post(InstructorAction::Solve(solve.clone()));
            },"정답 보기"}
            button {class:"instructor-explain",disabled:!has_narration,onclick:move |_|{requests.post(InstructorAction::Narrate);},"해설 보기"}
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use molip_quest::curriculum::grade_quiz;
    use std::collections::HashMap;

    /// The option the agent clicks for an answer: exact text, then 1-based number, then text
    /// containment. Mirrors assets/layout/quiz-pick.js (tests/js/quiz-pick.test.mjs runs the
    /// real one); keep the two in step.
    fn pick_option(options: &[String], want: &str) -> Option<usize> {
        fn normalize(text: &str) -> String {
            text.replace(['`', '*'], "")
                .split_whitespace()
                .collect::<Vec<_>>()
                .join(" ")
        }
        let texts: Vec<String> = options.iter().map(|o| normalize(o)).collect();
        let want = normalize(want);
        if let Some(i) = texts.iter().position(|t| *t == want) {
            return Some(i);
        }
        if let Ok(n) = want.parse::<usize>() {
            if (1..=texts.len()).contains(&n) {
                return Some(n - 1);
            }
        }
        if want.is_empty() {
            return None;
        }
        texts
            .iter()
            .position(|t| t.contains(&want) || (want.chars().count() > 6 && want.contains(t)))
    }

    /// What the quiz view would hold after the agent performed the answer_quiz steps: the
    /// option index, the typed text, or the 0-based picks, keyed by question id.
    fn answers_after(steps: &serde_json::Value, questions: &[Question]) -> HashMap<String, String> {
        let mut by_number: HashMap<String, String> = HashMap::new();
        for step in steps.as_array().expect("array") {
            assert_eq!(step["action"], "answer_quiz", "정답 보기 step {step}");
            if let Some(answers) = step["answers"].as_object() {
                for (n, v) in answers {
                    by_number.insert(n.clone(), v.as_str().unwrap_or_default().to_string());
                }
            }
        }
        questions
            .iter()
            .enumerate()
            .filter_map(|(i, q)| {
                let want = by_number.get(&(i + 1).to_string())?;
                let stored = match &q.kind {
                    QuestionKind::Choice { options, .. } => pick_option(options, want)?.to_string(),
                    QuestionKind::ShortAnswer { .. } => want.clone(),
                    QuestionKind::TableSelect { .. } => want
                        .split(',')
                        .filter_map(|s| s.trim().parse::<usize>().ok())
                        .map(|n| (n - 1).to_string())
                        .collect::<Vec<_>>()
                        .join(","),
                };
                Some((q.id.clone(), stored))
            })
            .collect()
    }

    #[test]
    fn a_number_names_the_nth_option_even_when_another_option_contains_that_digit() {
        let options: Vec<String> = [
            "10000 곱하기 3이 얼마야?",
            "`30000`",
            "파이썬. 10000 * 3 계산해서 출력",
        ]
        .map(String::from)
        .to_vec();
        assert_eq!(pick_option(&options, "3"), Some(2));
        assert_eq!(pick_option(&options, "1"), Some(0));
        assert_eq!(pick_option(&options, "4"), None);
        assert_eq!(pick_option(&["`2`".into(), "3".into()], "3"), Some(1));
        assert_eq!(
            pick_option(&["오류가 난다".into(), "`30000`이 나온다".into()], "오류"),
            Some(0)
        );
    }

    /// /tour-all says one to three sentences on every mission, then performs the same steps
    /// 정답 보기 does (a deck is finished quietly, without presentation mode).
    #[test]
    fn tour_actions_say_a_little_and_end_every_kpc_mission() {
        let course =
            molip_quest::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        for activity in course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .flat_map(|u| &u.activities)
        {
            assert!(
                (1..=3).contains(&activity.tour.len()),
                "{}: tour {:?}",
                activity.id,
                activity.tour
            );
            let steps = tour_actions(activity);
            let steps = steps.as_array().unwrap();
            let said: Vec<_> = steps.iter().take_while(|s| s["action"] == "say").collect();
            assert_eq!(said.len(), activity.tour.len(), "{}", activity.id);
            let rest: Vec<_> = steps.iter().skip(said.len()).cloned().collect();
            match &activity.kind {
                ActivityKind::Slides { .. } => {
                    assert_eq!(
                        rest,
                        vec![serde_json::json!({"action": "finish_slides", "quiet": true})],
                        "{}",
                        activity.id
                    );
                }
                _ => assert_eq!(
                    serde_json::Value::Array(rest),
                    solve_actions(activity),
                    "{}",
                    activity.id
                ),
            }
        }
    }

    /// 정답 보기 on every concept and quiz mission fills answers that the real grader passes;
    /// on a coding mission it submits the solution; a deck has no steps (it is marked watched).
    #[test]
    fn solve_actions_pass_every_kpc_mission() {
        let course =
            molip_quest::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        let mut graded = 0;
        for activity in course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .flat_map(|u| &u.activities)
        {
            let steps = solve_actions(activity);
            match &activity.kind {
                ActivityKind::Concept { check, .. } => {
                    let answers = answers_after(&steps, std::slice::from_ref(check));
                    let report = grade_quiz(std::slice::from_ref(check), &answers);
                    let failed: Vec<_> = report
                        .cases
                        .iter()
                        .filter(|c| !c.passed)
                        .map(|c| format!("{} -> {}", c.input, c.stdout))
                        .collect();
                    assert!(report.passed, "{}: {failed:?}", activity.id);
                    graded += 1;
                }
                ActivityKind::Quiz { questions } => {
                    let answers = answers_after(&steps, questions);
                    let report = grade_quiz(questions, &answers);
                    let failed: Vec<_> = report
                        .cases
                        .iter()
                        .filter(|c| !c.passed)
                        .map(|c| format!("{} → {}", c.input, c.stdout))
                        .collect();
                    assert!(report.passed, "{}: {failed:?}", activity.id);
                    graded += questions.len();
                }
                ActivityKind::Coding { .. } => {
                    assert_eq!(steps[0]["action"], "set_code", "{}", activity.id);
                    assert_eq!(steps[0]["code"], answer(activity), "{}", activity.id);
                    assert_eq!(steps[1]["action"], "submit", "{}", activity.id);
                }
                ActivityKind::Slides { .. } => {
                    assert_eq!(steps, serde_json::json!([]), "{}", activity.id);
                }
            }
        }
        assert!(graded > 200, "only {graded} questions graded");
    }

    #[test]
    fn every_coding_answer_matches_compiled_narration_and_challenge_reference() {
        let course =
            molip_quest::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        for activity in course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .flat_map(|u| &u.activities)
        {
            if matches!(activity.kind, ActivityKind::Coding { .. }) {
                assert!(
                    !answer(activity).contains("정답 코드가 없습니다"),
                    "{}",
                    activity.id
                );
            }
        }
        let hello = course.chapters[0].units[0]
            .activities
            .iter()
            .find(|a| a.id == "hello")
            .unwrap();
        assert!(answer(hello).contains("print("));
        let concept = course.chapters[0].units[0]
            .activities
            .iter()
            .find(|a| a.id == "runtime")
            .unwrap();
        assert!(answer(concept).contains("정답:"));
    }
}
