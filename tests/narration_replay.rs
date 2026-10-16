//! Every mission's compiled 해설 (courses/kpc-finance.json `narration`) replayed without the
//! app, against a pure model of what the page agent (assets/layout/agent.js) does with each
//! action. This is what `/auto`, `/auto-all` and the instructor's 해설 보기 run, so a rewritten
//! narration (tools/narrate.py) must still:
//!   - type code that ends up byte-for-byte as the reference solution before 제출;
//!   - fill in answers the real grader passes;
//!   - point its spotlight at phrases that exist in the concept body, questions that exist,
//!     options that exist;
//!   - turn every slide of a deck and finish it.
use molip_quest::{
    curriculum::{grade_quiz, ActivityKind, Question, QuestionKind},
    Course,
};
use std::collections::HashMap;

fn course() -> Course {
    Course::parse(include_str!("../courses/kpc-finance.json")).unwrap()
}

fn solutions() -> HashMap<String, String> {
    serde_json::from_str(include_str!("../courses/kpc-solutions.json")).unwrap()
}

/// Text as the agent reads it (agent.js `normalize` / narration.py `spoken`): no backticks or
/// bold marks, whitespace runs collapsed.
fn spoken(text: &str) -> String {
    let text = text.replace("**", "").replace('`', "");
    text.split_whitespace().collect::<Vec<_>>().join(" ")
}

/// The concept body as `textBlock` searches it: prose and fence contents, marks removed.
fn body_text(markdown: &str) -> String {
    spoken(markdown)
}

/// agent.js `pickOption`: exact text, then 1-based number, then containment.
fn pick_option(options: &[String], want: &str) -> Option<usize> {
    let texts: Vec<String> = options.iter().map(|o| spoken(o)).collect();
    let want = spoken(want);
    if let Some(i) = texts.iter().position(|t| *t == want) {
        return Some(i);
    }
    if let Ok(n) = want.parse::<usize>() {
        if (1..=texts.len()).contains(&n) {
            return Some(n - 1);
        }
    }
    texts
        .iter()
        .position(|t| t.contains(&want) || (want.chars().count() > 6 && want.contains(t)))
}

/// agent.js `typeCode`: a chunk always ends in a newline, and starts on a new line when the
/// editor's text does not end in one.
fn type_code(editor: &mut String, chunk: &str, replace: bool) {
    if replace {
        editor.clear();
    }
    let mut body = chunk.to_string();
    if !body.ends_with('\n') {
        body.push('\n');
    }
    if !editor.is_empty() && !editor.ends_with('\n') {
        body.insert(0, '\n');
    }
    editor.push_str(&body);
}

/// What the quiz view stores after answer_quiz steps: option index, typed text or 0-based
/// picks, keyed by question id.
fn stored_answers(answers: &HashMap<String, String>, questions: &[Question]) -> HashMap<String, String> {
    questions
        .iter()
        .enumerate()
        .filter_map(|(i, q)| {
            let want = answers.get(&(i + 1).to_string())?;
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
fn coding_narrations_type_the_reference_solution_then_submit() {
    let solutions = solutions();
    let mut replayed = 0;
    for activity in course().chapters.iter().flat_map(|c| &c.units).flat_map(|u| &u.activities) {
        let ActivityKind::Coding { problem } = &activity.kind else { continue };
        let mut editor = String::new();
        let mut submitted = false;
        let mut ran = false;
        for step in &activity.narration {
            match step["action"].as_str().unwrap() {
                "set_code" => editor = step["code"].as_str().unwrap().to_string(),
                "type_code" => type_code(&mut editor, step["code"].as_str().unwrap(), step["replace"] == true),
                "run" => ran = true,
                "submit" => submitted = true,
                "say" | "answer_quiz" | "fill_blanks" => {}
                other => panic!("{}: unexpected action {other}", activity.id),
            }
        }
        let solution = solutions.get(&problem.id).unwrap_or_else(|| panic!("{}: no solution", activity.id));
        assert_eq!(
            editor.trim_end(),
            solution.trim_end(),
            "{}: the typed code is not the solution",
            activity.id
        );
        assert!(ran && submitted, "{}: must run and submit", activity.id);
        // The content rule: the program grows run by run, and a pitfall is shown or spoken.
        let chunks = activity.narration.iter().filter(|s| s["action"] == "type_code").count();
        let runs = activity.narration.iter().filter(|s| s["action"] == "run").count();
        assert!(chunks < 2 || runs >= 2, "{}: {chunks} chunks but only {runs} run(s): code a little, run, repeat", activity.id);
        let caution = activity.narration.iter().any(|s| s["action"] == "say" && s["target"] == "editor");
        let first_typed = activity.narration.iter().position(|s| s["action"] == "type_code").unwrap_or(0);
        let undo = activity.narration.iter().skip(first_typed + 1).any(|s| s["action"] == "set_code");
        assert!(caution || undo, "{}: no 「이렇게 하기 쉬운데 … 조심하세요」 moment", activity.id);
        // The first chunk starts a clean editor unless the starter was put in first.
        let first = activity.narration.iter().find(|s| matches!(s["action"].as_str(), Some("set_code") | Some("type_code"))).unwrap();
        assert!(
            first["action"] == "set_code" || first["replace"] == true,
            "{}: the first chunk neither replaces nor follows a starter",
            activity.id
        );
        replayed += 1;
    }
    assert!(replayed > 100, "only {replayed} coding missions replayed");
}

#[test]
fn concept_and_quiz_narrations_answer_so_the_grader_passes() {
    let mut graded = 0;
    for activity in course().chapters.iter().flat_map(|c| &c.units).flat_map(|u| &u.activities) {
        let questions: Vec<Question> = match &activity.kind {
            ActivityKind::Concept { check, .. } => vec![check.clone()],
            ActivityKind::Quiz { questions } => questions.clone(),
            _ => continue,
        };
        let mut answers: HashMap<String, String> = HashMap::new();
        let mut graded_at_end = false;
        for step in &activity.narration {
            if step["action"] != "answer_quiz" {
                continue;
            }
            if let Some(map) = step["answers"].as_object() {
                for (n, v) in map {
                    answers.insert(n.clone(), v.as_str().unwrap_or_default().to_string());
                }
            }
            // submit:false ticks and waits; the last answer_quiz must grade.
            graded_at_end = step["submit"] != false;
        }
        assert!(graded_at_end, "{}: the last answer_quiz does not grade", activity.id);
        let stored = stored_answers(&answers, &questions);
        let report = grade_quiz(&questions, &stored);
        let failed: Vec<_> = report
            .cases
            .iter()
            .filter(|c| !c.passed)
            .map(|c| format!("{} -> {}", c.input, c.stdout))
            .collect();
        assert!(report.passed, "{}: {failed:?}", activity.id);
        graded += questions.len();
    }
    assert!(graded > 200, "only {graded} questions graded");
}

#[test]
fn spotlight_targets_exist_on_the_page() {
    for activity in course().chapters.iter().flat_map(|c| &c.units).flat_map(|u| &u.activities) {
        let questions: Vec<&Question> = match &activity.kind {
            ActivityKind::Concept { check, .. } => vec![check],
            ActivityKind::Quiz { questions } => questions.iter().collect(),
            _ => vec![],
        };
        let body = match &activity.kind {
            ActivityKind::Concept { body, .. } => body_text(body),
            _ => String::new(),
        };
        for step in &activity.narration {
            let Some(target) = step["target"].as_str() else { continue };
            let mut parts = target.splitn(3, ':');
            let kind = parts.next().unwrap();
            match kind {
                "text" => {
                    let phrase = parts.next().unwrap_or("");
                    assert!(
                        body.contains(&spoken(phrase)),
                        "{}: phrase not in the body: {phrase:?}",
                        activity.id
                    );
                }
                "quiz" | "option" => {
                    let n: usize = parts.next().and_then(|s| s.parse().ok()).unwrap_or(0);
                    assert!((1..=questions.len()).contains(&n), "{}: no question {n}", activity.id);
                    if kind == "option" {
                        let m: usize = parts.next().and_then(|s| s.parse().ok()).unwrap_or(0);
                        let QuestionKind::Choice { options, .. } = &questions[n - 1].kind else {
                            panic!("{}: option target on a non-choice question {n}", activity.id)
                        };
                        assert!((1..=options.len()).contains(&m), "{}: question {n} has no option {m}", activity.id);
                    }
                }
                "title" | "problem" | "examples" | "hint" | "input" | "output" | "slides" | "editor" => {}
                other => panic!("{}: unknown spotlight target {other:?}", activity.id),
            }
        }
    }
}

#[test]
fn deck_narrations_speak_every_slide_and_finish() {
    for activity in course().chapters.iter().flat_map(|c| &c.units).flat_map(|u| &u.activities) {
        let ActivityKind::Slides { .. } = &activity.kind else { continue };
        let says = activity.narration.iter().filter(|s| s["action"] == "say").count();
        let turns = activity.narration.iter().filter(|s| s["action"] == "next_slide").count();
        assert_eq!(says, turns + 1, "{}: one line per slide, one turn between slides", activity.id);
        assert_eq!(activity.narration.last().unwrap()["action"], "finish_slides", "{}", activity.id);
    }
}
