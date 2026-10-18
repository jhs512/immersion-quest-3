//! Small answer interactions. Stable option IDs, rather than display positions, are graded.
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use crate::runner::{TestCaseResult, TestReport};

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct OptionItem { pub id: String, pub text: String }

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Interaction {
    Choice { options: Vec<OptionItem>, answer: String },
    Order { options: Vec<OptionItem>, accepted: Vec<Vec<String>> },
    Fill { accepted: Vec<String> },
}

impl Interaction {
    pub fn validate(&self) -> Result<(), String> {
        let valid_text = |s: &str| !s.trim().is_empty() && s.len() <= 8000;
        let options = match self { Self::Choice { options, .. } | Self::Order { options, .. } => Some(options), _ => None };
        if let Some(options) = options {
            let mut ids = HashSet::new();
            if options.len() < 2 || options.len() > 20 || options.iter().any(|item| !valid_text(&item.id) || !valid_text(&item.text) || !ids.insert(&item.id)) {
                return Err("선택지의 고유 코드와 내용을 확인하세요.".into());
            }
        }
        let valid = match self {
            Self::Choice { options, answer } => options.iter().any(|option| option.id == *answer),
            Self::Order { options, accepted } => !accepted.is_empty() && accepted.len() <= 50 && accepted.iter().all(|order| {
                let mut ids = HashSet::new();
                !order.is_empty() && order.len() <= options.len() && order.iter().all(|id| ids.insert(id) && options.iter().any(|o| o.id == *id))
            }),
            Self::Fill { accepted } => !accepted.is_empty() && accepted.len() <= 50 && accepted.iter().all(|s| valid_text(s)),
        };
        if valid { Ok(()) } else { Err("답안 판정 기준을 확인하세요.".into()) }
    }

    pub fn check(&self, source: &str) -> Result<TestReport, String> {
        self.validate()?;
        if source.len() > 65536 { return Err("답안 길이를 확인하세요.".into()); }
        let passed = match self {
            Self::Choice { answer, .. } => source == answer,
            Self::Order { accepted, .. } => serde_json::from_str::<Vec<String>>(source).ok().is_some_and(|order| accepted.contains(&order)),
            Self::Fill { accepted } => accepted.iter().any(|answer| answer.trim() == source.trim()),
        };
        Ok(TestReport { passed, cases: vec![TestCaseResult {
            input: String::new(), expected: "문제의 조건을 만족하는 답안".into(),
            stdout: if passed { "맞았어요." } else { "다시 풀어보세요." }.into(),
            stderr: String::new(), passed, state: "answer_checked".into(),
        }] })
    }
}
