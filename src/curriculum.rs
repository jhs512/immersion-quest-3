use crate::{
    runner::{TestCaseResult, TestReport},
    Course, Unit,
};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Activity {
    pub id: String,
    pub title: String,
    /// A chapter capstone that needs everything the chapter taught.
    #[serde(default)]
    pub challenge: bool,
    /// Quick questions for the tutor panel, written for this activity (tools/kpc_course/dsl.py).
    #[serde(default)]
    pub ask: Vec<String>,
    /// 해설 모드 script: the agent actions (assets/layout/agent.js) that `/auto` plays for this
    /// mission, compiled at build time (tools/kpc_course/narration.py). Empty means the tutor
    /// CLI improvises one.
    #[serde(default)]
    pub narration: Vec<serde_json::Value>,
    /// The 1~3 sentences `/tour-all` says about this mission before filling it in and moving
    /// on (tools/kpc_course/narration.py compile_tour). Empty when there is no narration.
    #[serde(default)]
    pub tour: Vec<String>,
    #[serde(flatten)]
    pub kind: ActivityKind,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ActivityKind {
    Concept {
        body: String,
        check: Question,
    },
    Coding {
        problem: Unit,
    },
    Quiz {
        questions: Vec<Question>,
    },
    /// A Marp slide deck the instructor presents; students finish it by reading to the end.
    Slides {
        markdown: String,
    },
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Question {
    pub id: String,
    pub prompt: String,
    pub explanation: String,
    #[serde(flatten)]
    pub kind: QuestionKind,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum QuestionKind {
    Choice {
        options: Vec<String>,
        correct: usize,
    },
    ShortAnswer {
        accepted: Vec<String>,
    },
    /// A real table on screen; the student ticks rows (`pick` = "rows") or columns ("columns")
    /// and the rule says which selections count. The answer is the picked 0-based indices,
    /// sorted and comma-separated ("0,3,5"). `expected` is the model answer in words.
    TableSelect {
        table: SelectTable,
        pick: String,
        rule: SelectRule,
        expected: String,
    },
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct SelectTable {
    pub columns: Vec<String>,
    pub rows: Vec<Vec<String>>,
}

/// Every constraint given must hold. Indices are rows or columns, as `pick` says.
#[derive(Clone, Default, Deserialize, Serialize, PartialEq)]
pub struct SelectRule {
    /// How many to pick: (min, max).
    #[serde(default)]
    pub size: Option<(usize, usize)>,
    /// Must be picked.
    #[serde(default)]
    pub required: Vec<usize>,
    /// Must not be picked.
    #[serde(default)]
    pub forbidden: Vec<usize>,
    /// When given, nothing outside this set may be picked.
    #[serde(default)]
    pub allowed: Option<Vec<usize>>,
    /// Rows only: exactly `count` picked rows must have `column == value`.
    #[serde(default)]
    pub quota: Vec<Quota>,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Quota {
    pub column: String,
    pub value: String,
    pub count: usize,
}

/// The picked indices in a stored answer ("0,3,5"), sorted, without repeats.
pub fn parse_selection(answer: &str) -> Vec<usize> {
    let mut picked: Vec<usize> = answer
        .split(',')
        .filter_map(|s| s.trim().parse().ok())
        .collect();
    picked.sort_unstable();
    picked.dedup();
    picked
}

/// Why a selection fails the rule, in the student's words, or Ok when it passes.
pub fn check_selection(
    table: &SelectTable,
    pick: &str,
    rule: &SelectRule,
    picked: &[usize],
) -> Result<(), String> {
    let label = |i: usize| -> String {
        if pick == "columns" {
            table
                .columns
                .get(i)
                .cloned()
                .unwrap_or_else(|| format!("{}열", i + 1))
        } else {
            format!("{}행", i + 1)
        }
    };
    let names = |ids: &[usize]| ids.iter().map(|&i| label(i)).collect::<Vec<_>>().join(", ");
    if let Some((min, max)) = rule.size {
        if picked.len() < min || picked.len() > max {
            let want = if min == max {
                format!("{min}개")
            } else {
                format!("{min}~{max}개")
            };
            return Err(format!(
                "{want}를 골라야 하는데 {}개를 골랐습니다.",
                picked.len()
            ));
        }
    }
    let missing: Vec<usize> = rule
        .required
        .iter()
        .copied()
        .filter(|i| !picked.contains(i))
        .collect();
    if !missing.is_empty() {
        return Err(format!("{}은(는) 꼭 들어가야 합니다.", names(&missing)));
    }
    let wrong: Vec<usize> = picked
        .iter()
        .copied()
        .filter(|i| rule.forbidden.contains(i))
        .collect();
    if !wrong.is_empty() {
        return Err(format!("{}은(는) 빼야 합니다.", names(&wrong)));
    }
    if let Some(allowed) = &rule.allowed {
        let outside: Vec<usize> = picked
            .iter()
            .copied()
            .filter(|i| !allowed.contains(i))
            .collect();
        if !outside.is_empty() {
            return Err(format!("{}은(는) 고를 수 없습니다.", names(&outside)));
        }
    }
    for quota in &rule.quota {
        let Some(column) = table.columns.iter().position(|c| c == &quota.column) else {
            return Err(format!("표에 '{}' 열이 없습니다.", quota.column));
        };
        let have = picked
            .iter()
            .filter(|&&r| {
                table
                    .rows
                    .get(r)
                    .and_then(|row| row.get(column))
                    .is_some_and(|cell| cell.trim() == quota.value.trim())
            })
            .count();
        if have != quota.count {
            return Err(format!(
                "{}={}인 행을 {}개 골라야 하는데 {}개입니다.",
                quota.column, quota.value, quota.count, have
            ));
        }
    }
    Ok(())
}

/// The bodies of every ```lang fenced block in a Markdown text, in order.
pub fn fenced_blocks(text: &str, lang: &str) -> Vec<String> {
    let mut blocks = Vec::new();
    let mut current: Option<String> = None;
    for line in text.lines() {
        let trimmed = line.trim_start();
        if let Some(block) = current.as_mut() {
            if trimmed.starts_with("```") {
                blocks.push(block.trim_end().to_string());
                current = None;
            } else {
                block.push_str(line);
                block.push('\n');
            }
        } else if trimmed
            .strip_prefix("```")
            .is_some_and(|rest| rest.trim() == lang)
        {
            current = Some(String::new());
        }
    }
    blocks
}

impl Activity {
    pub fn label(&self) -> &'static str {
        match self.kind {
            ActivityKind::Concept { .. } => "개념",
            ActivityKind::Coding { .. } if self.challenge => "도전 과제",
            ActivityKind::Coding { .. } => "코딩 미션",
            ActivityKind::Quiz { .. } => "퀴즈",
            ActivityKind::Slides { .. } => "슬라이드",
        }
    }
    /// One emoji per mission kind, shown in the curriculum menu next to the label.
    pub fn icon(&self) -> &'static str {
        match self.kind {
            ActivityKind::Concept { .. } => "📘",
            ActivityKind::Coding { .. } if self.challenge => "⭐",
            ActivityKind::Coding { .. } => "💻",
            ActivityKind::Quiz { .. } => "❓",
            ActivityKind::Slides { .. } => "🎞️",
        }
    }
    pub fn progress_unit(&self, parent: &Unit) -> Unit {
        let mut unit = match &self.kind {
            ActivityKind::Coding { problem } => problem.clone(),
            _ => parent.clone(),
        };
        unit.id = format!("{}/{}", parent.id, self.id);
        unit.title = self.title.clone();
        unit.revision = unit.revision.max(parent.revision);
        unit.activities.clear();
        unit
    }
}

#[cfg(test)]
mod select_tests {
    use super::*;

    fn table() -> SelectTable {
        SelectTable {
            columns: vec!["등급".into(), "생존".into(), "이름".into()],
            rows: vec![
                vec!["1".into(), "1".into(), "A".into()],
                vec!["1".into(), "0".into(), "B".into()],
                vec!["2".into(), "1".into(), "C".into()],
                vec!["3".into(), "0".into(), "D".into()],
            ],
        }
    }

    #[test]
    fn selections_parse_sorted_without_repeats() {
        assert_eq!(parse_selection("3, 1,1,x,0"), vec![0, 1, 3]);
        assert!(parse_selection("").is_empty());
    }

    #[test]
    fn exact_column_sets_and_quotas_grade_with_a_reason() {
        let t = table();
        let target = SelectRule {
            size: Some((1, 1)),
            required: vec![1],
            allowed: Some(vec![1]),
            ..Default::default()
        };
        assert!(check_selection(&t, "columns", &target, &[1]).is_ok());
        assert_eq!(
            check_selection(&t, "columns", &target, &[0, 1]).unwrap_err(),
            "1개를 골라야 하는데 2개를 골랐습니다."
        );
        assert_eq!(
            check_selection(&t, "columns", &target, &[0]).unwrap_err(),
            "생존은(는) 꼭 들어가야 합니다."
        );
        let balanced = SelectRule {
            size: Some((2, 2)),
            quota: vec![
                Quota {
                    column: "생존".into(),
                    value: "1".into(),
                    count: 1,
                },
                Quota {
                    column: "생존".into(),
                    value: "0".into(),
                    count: 1,
                },
            ],
            ..Default::default()
        };
        assert!(check_selection(&t, "rows", &balanced, &[2, 3]).is_ok());
        assert_eq!(
            check_selection(&t, "rows", &balanced, &[0, 2]).unwrap_err(),
            "생존=1인 행을 1개 골라야 하는데 2개입니다."
        );
        let forbidden = SelectRule {
            forbidden: vec![3],
            ..Default::default()
        };
        assert_eq!(
            check_selection(&t, "rows", &forbidden, &[1, 3]).unwrap_err(),
            "4행은(는) 빼야 합니다."
        );
    }

    #[test]
    fn a_table_question_grades_and_reports_the_miss_first() {
        let q = Question {
            id: "t".into(),
            prompt: "타깃 열".into(),
            explanation: "생존이 타깃입니다.".into(),
            kind: QuestionKind::TableSelect {
                table: table(),
                pick: "columns".into(),
                rule: SelectRule {
                    size: Some((1, 1)),
                    required: vec![1],
                    ..Default::default()
                },
                expected: "생존".into(),
            },
        };
        let ok = grade_quiz(
            std::slice::from_ref(&q),
            &HashMap::from([("t".into(), "1".into())]),
        );
        assert!(ok.passed);
        let miss = grade_quiz(
            std::slice::from_ref(&q),
            &HashMap::from([("t".into(), "0,2".into())]),
        );
        assert!(!miss.passed);
        assert!(miss.cases[0]
            .stderr
            .starts_with("1개를 골라야 하는데 2개를 골랐습니다."));
        assert!(miss.cases[0].stderr.ends_with("생존이 타깃입니다."));
        assert_eq!(miss.cases[0].expected, "생존");
    }
}

pub fn normalize(answer: &str) -> String {
    answer.split_whitespace().collect::<String>().to_lowercase()
}

pub fn unlocked_units(course: &Course, completed: &HashSet<String>) -> HashSet<String> {
    let mut unlocked = HashSet::new();
    for unit in course.chapters.iter().flat_map(|c| &c.units) {
        unlocked.insert(unit.id.clone());
        if !completed.contains(&unit.id) {
            break;
        }
    }
    unlocked
}

pub fn unlocked_activities(unit: &Unit, completed: &HashSet<String>) -> usize {
    unit.activities
        .iter()
        .position(|a| !completed.contains(&a.progress_unit(unit).id))
        .map(|n| n + 1)
        .unwrap_or(unit.activities.len())
}

/// The "human" answer prompt: the two to five lines a person actually types into an AI,
/// authored per problem in tools/kpc_course/prompts.py. Courses without one fall back to
/// the machine prompt.
pub fn answer_prompt(unit: &Unit, code: &str) -> String {
    match unit.prompt.as_deref() {
        Some(prompt) => prompt.trim().to_string(),
        None => machine_prompt(unit, code),
    }
}

/// The "machine" answer prompt: the request as a minimal specification. Only what this
/// problem actually uses appears: the task, the output contract, the starter code when it
/// holds real code, the current code when it differs, the examples, and the checker's
/// variables and assertions. No role line, no environment boilerplate.
pub fn machine_prompt(unit: &Unit, code: &str) -> String {
    // Hints are written for people; the specification carries only the task itself.
    let task = unit
        .content
        .split("### 힌트")
        .next()
        .unwrap_or("")
        .replace("### 문제에서 필요한 설명\n\n", "")
        .replace("### 목표\n\n", "");
    let task = task
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty())
        .collect::<Vec<_>>()
        .join("\n");
    let mut parts = vec![
        format!("과제: {task}"),
        format!(
            "출력: {} 하나. 설명·코드 펜스 없이 코드만. {}",
            unit.language.filename(),
            if unit.language == crate::Language::Java {
                "JDK 25, preview 옵션 없음."
            } else {
                ""
            }
        ),
    ];
    let starter = unit.starter_code.trim_end();
    let has_code = starter
        .lines()
        .any(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'));
    if has_code {
        parts.push(format!("기본 코드(그대로 두고 이어서):\n{starter}"));
    }
    let current = code.trim_end();
    if !current.is_empty() && current != starter {
        parts.push(format!("현재 코드:\n{current}"));
    }
    if !unit.tests.is_empty() {
        let quote = |s: &str| {
            let s = s.trim_end();
            if s.is_empty() {
                "없음".to_string()
            } else if s.contains('\n') {
                format!("{s:?}")
            } else {
                s.to_string()
            }
        };
        let cases = unit
            .tests
            .iter()
            .map(|t| format!("입력 {} → 출력 {}", quote(&t.input), quote(&t.expected)))
            .collect::<Vec<_>>()
            .join("\n");
        parts.push(format!("예시:\n{cases}\n채점: 출력 글자 단위 비교."));
    }
    if let Some(checker) = unit.checker.as_deref() {
        parts.push(format!("채점: {}", checker_summary(checker)));
    }
    parts.join("\n")
}

/// Reduce the checker source to what the AI must satisfy: the result variables it reads and
/// the assertions inside its `try` block, without the runpy boilerplate.
fn checker_summary(checker: &str) -> String {
    let mut lines = Vec::new();
    if let Some(start) = checker.find("assert set([") {
        let rest = &checker[start + "assert set([".len()..];
        if let Some(end) = rest.find("])") {
            let names: Vec<_> = rest[..end]
                .split(',')
                .map(|n| n.trim().trim_matches(|c| c == '\'' || c == '"'))
                .filter(|n| !n.is_empty())
                .collect();
            if !names.is_empty() {
                lines.push(format!("변수 {}.", names.join(", ")));
            }
        }
    }
    if let Some(start) = checker.rfind("\ntry:\n") {
        let body = &checker[start + "\ntry:\n".len()..];
        let body = body.split("\nexcept (KeyError").next().unwrap_or(body);
        let assertions: Vec<_> = body
            .lines()
            .map(|l| l.strip_prefix("    ").unwrap_or(l))
            .filter(|l| !l.trim().is_empty())
            .collect();
        if !assertions.is_empty() {
            lines.push(format!(
                "검사 코드(s는 main.py의 변수들):\n{}",
                assertions.join("\n")
            ));
        }
    }
    if lines.is_empty() {
        "검사 코드가 변수 값을 확인.".to_string()
    } else {
        lines.join("\n")
    }
}

/// Markdown for the prompt guide: the human prompt and, for each word that matters, why.
pub fn prompt_guide(unit: &Unit) -> String {
    let human = answer_prompt(unit, "");
    let why = unit
        .prompt_why
        .as_deref()
        .map(str::trim)
        .unwrap_or("- 입출력 조건이 곧 명세. 그대로 적는다.");
    format!("```text\n{human}\n```\n\n## 왜 이 단어들인가\n\n{why}")
}

pub fn grade_quiz(questions: &[Question], answers: &HashMap<String, String>) -> TestReport {
    let cases: Vec<_> = questions
        .iter()
        .map(|q| {
            let answer = answers.get(&q.id).cloned().unwrap_or_default();
            let (passed, expected) = match &q.kind {
                QuestionKind::Choice { options, correct } => (
                    answer.parse::<usize>().ok() == Some(*correct),
                    options[*correct].clone(),
                ),
                QuestionKind::ShortAnswer { accepted } => (
                    !answer.trim().is_empty()
                        && accepted.iter().any(|a| normalize(a) == normalize(&answer)),
                    accepted[0].clone(),
                ),
                QuestionKind::TableSelect {
                    table,
                    pick,
                    rule,
                    expected,
                } => {
                    let picked = parse_selection(&answer);
                    match check_selection(table, pick, rule, &picked) {
                        Ok(()) => (true, expected.clone()),
                        Err(why) => {
                            // The specific miss comes first, then the explanation.
                            return TestCaseResult {
                                input: q.prompt.clone(),
                                expected: expected.clone(),
                                stdout: answer,
                                stderr: format!("{why}\n\n{}", q.explanation),
                                passed: false,
                                state: "wrong_answer".into(),
                            };
                        }
                    }
                }
            };
            TestCaseResult {
                input: q.prompt.clone(),
                expected,
                stdout: answer,
                stderr: q.explanation.clone(),
                passed,
                state: if passed { "passed" } else { "wrong_answer" }.into(),
            }
        })
        .collect();
    TestReport {
        passed: !cases.is_empty() && cases.iter().all(|c| c.passed),
        cases,
    }
}

pub fn validate(course: &Course) -> Result<(), String> {
    for unit in course.chapters.iter().flat_map(|c| &c.units) {
        if unit.id.contains('/') {
            return Err("단원 ID에는 /를 사용할 수 없습니다.".into());
        }
        let mut ids = HashSet::new();
        for activity in &unit.activities {
            if activity.id.trim().is_empty()
                || activity.id.contains('/')
                || activity.title.trim().is_empty()
                || !ids.insert(&activity.id)
            {
                return Err("미션 ID는 단원 내에서 고유해야 하며 제목이 필요합니다.".into());
            }
            match &activity.kind {
                ActivityKind::Concept { body, .. } if body.trim().is_empty() => {
                    return Err("개념 설명이 필요합니다.".into())
                }
                ActivityKind::Slides { markdown } => {
                    if markdown.trim().is_empty() {
                        return Err("슬라이드 내용이 필요합니다.".into());
                    }
                }
                ActivityKind::Concept { check, .. } => {
                    if !matches!(check.kind, QuestionKind::ShortAnswer { .. }) {
                        return Err("개념 확인은 단답형 한 문항이어야 합니다.".into());
                    }
                    validate_questions(std::slice::from_ref(check))?;
                }
                ActivityKind::Coding { problem } => {
                    if !problem.activities.is_empty()
                        || (problem.tests.is_empty() && problem.checker.is_none())
                    {
                        return Err("코딩 문제는 독립된 코드와 검사 조건이 필요합니다.".into());
                    }
                    let mut single = course.clone();
                    single.chapters.truncate(1);
                    single.chapters[0].units = vec![problem.clone()];
                    Course::parse(&serde_json::to_string(&single).map_err(|e| e.to_string())?)?;
                }
                ActivityKind::Quiz { questions } => {
                    validate_questions(questions)?;
                }
            }
        }
    }
    Ok(())
}

fn validate_questions(questions: &[Question]) -> Result<(), String> {
    let mut question_ids = HashSet::new();
    if questions.is_empty() {
        return Err("퀴즈에는 문항이 필요합니다.".into());
    }
    for q in questions {
        if q.id.trim().is_empty()
            || q.id.contains('/')
            || !question_ids.insert(&q.id)
            || q.prompt.trim().is_empty()
            || q.explanation.trim().is_empty()
        {
            return Err("퀴즈 문항 ID, 질문과 해설을 확인하세요.".into());
        }
        match &q.kind {
            QuestionKind::Choice { options, correct }
                if options.len() < 2
                    || *correct >= options.len()
                    || options.iter().any(|o| o.trim().is_empty()) =>
            {
                return Err("객관식 보기와 정답을 확인하세요.".into())
            }
            QuestionKind::ShortAnswer { accepted }
                if accepted.is_empty() || accepted.iter().any(|a| a.trim().is_empty()) =>
            {
                return Err("주관식 인정 답안이 필요합니다.".into())
            }
            QuestionKind::TableSelect {
                table,
                pick,
                rule,
                expected,
            } => {
                let width = table.columns.len();
                if width == 0
                    || table.rows.is_empty()
                    || table.rows.iter().any(|r| r.len() != width)
                    || table.columns.iter().any(|c| c.trim().is_empty())
                {
                    return Err("표 고르기 문항의 표를 확인하세요 (열 이름, 행 길이).".into());
                }
                let count = match pick.as_str() {
                    "rows" => table.rows.len(),
                    "columns" => width,
                    _ => return Err("표 고르기 문항의 pick은 rows 또는 columns입니다.".into()),
                };
                let indices = rule
                    .required
                    .iter()
                    .chain(&rule.forbidden)
                    .chain(rule.allowed.iter().flatten());
                if indices.into_iter().any(|&i| i >= count)
                    || rule.size.is_some_and(|(min, max)| min > max || max > count)
                    || rule.quota.iter().any(|q| {
                        pick != "rows" || !table.columns.contains(&q.column) || q.count > count
                    })
                    || (rule.size.is_none()
                        && rule.required.is_empty()
                        && rule.forbidden.is_empty()
                        && rule.allowed.is_none()
                        && rule.quota.is_empty())
                    || expected.trim().is_empty()
                {
                    return Err("표 고르기 문항의 규칙을 확인하세요.".into());
                }
            }
            _ => (),
        }
    }
    Ok(())
}
