//! 도전 과제: each lesson's final solvable problem, referenced (never copied) from the pinned
//! lesson, plus final problems for lessons that are still being prepared. The future ones live
//! temporarily in the course repository and carry their own review and execution state.
use crate::repository_course::{resource_code, CourseManifest, Lesson, LessonRef, Task, TaskLanguage};
use crate::task_interaction::Interaction;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

/// Where the course repository keeps final problems for lessons that are not built yet.
pub const FUTURE_FILE: &str = "challenges/future.json";

/// True when the real grader (`lesson_runner::check_inner` and the Java build submit path) has a
/// criterion to decide this task. Reading-only or explanatory steps never qualify.
pub fn is_graded(task: &Task) -> bool {
    if task.interaction.is_some() { return true }
    let goal = task.git_terminal.as_ref().is_some_and(|exercise| exercise.has_goal());
    let checker = task.checker.as_deref().is_some_and(|c| !c.trim().is_empty());
    match task.language {
        TaskLanguage::Java => !task.tests.is_empty() || checker || !task.variations.is_empty() || !task.expected_files.is_empty() || goal,
        TaskLanguage::Junit => true,
        TaskLanguage::Git => task.git_checks.is_some() || goal,
        TaskLanguage::Web => !task.web_checks.is_empty(),
        TaskLanguage::Python => !task.tests.is_empty() || checker,
        TaskLanguage::JavaProject | TaskLanguage::Javascript | TaskLanguage::C | TaskLanguage::Sql | TaskLanguage::JavaLibraries | TaskLanguage::Docker => !task.tests.is_empty(),
    }
}

/// The last graded task in the lesson's own order.
pub fn final_task(lesson: &Lesson) -> Option<(usize, &Task)> {
    lesson.tasks.iter().enumerate().rev().find(|(_, task)| is_graded(task))
}

/// How the learner answers, in a few words.
pub fn answer_kind(task: &Task) -> &'static str {
    match &task.interaction {
        Some(Interaction::Choice { .. }) => "보기 선택",
        Some(Interaction::Fill { .. }) | Some(Interaction::FillFields { .. }) => "답 입력",
        Some(Interaction::Order { .. }) => "순서 맞추기",
        None => match task.language {
            TaskLanguage::Git => "터미널 실습",
            TaskLanguage::Web => "화면 고치기",
            TaskLanguage::Junit => "테스트 작성",
            TaskLanguage::Docker => "Docker 실습",
            _ if task.git_terminal.is_some() => "터미널 실습",
            _ => "코드 작성",
        },
    }
}

/// A reference to an existing lesson's final problem at the revision the course pins.
#[derive(Clone, Debug, PartialEq)]
pub struct LessonChallenge {
    pub lesson_index: usize,
    pub lesson_id: String,
    pub lesson_title: String,
    pub revision: String,
    pub task_id: String,
    pub task_title: String,
    pub prompt: String,
    pub kind: &'static str,
    /// 1-based position of the task in its lesson, and the lesson's task count.
    pub position: (usize, usize),
}

pub fn lesson_challenge(lesson_index: usize, reference: &LessonRef, lesson: &Lesson) -> Option<LessonChallenge> {
    if lesson.id != reference.id || lesson.revision != reference.revision { return None }
    let (index, task) = final_task(lesson)?;
    Some(LessonChallenge {
        lesson_index,
        lesson_id: lesson.id.clone(),
        lesson_title: reference.title.clone(),
        revision: lesson.revision.clone(),
        task_id: task.id.clone(),
        task_title: task.title.clone(),
        prompt: if task.question.trim().is_empty() { task.goal.clone() } else { task.question.clone() },
        kind: answer_kind(task),
        position: (index + 1, lesson.tasks.len()),
    })
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct FutureChallengeFile {
    pub schema_version: u32,
    pub course_id: String,
    #[serde(default)]
    pub challenges: Vec<FutureChallenge>,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct FutureChallenge {
    pub id: String,
    pub planned_lesson: PlannedLesson,
    pub review: Review,
    pub execution: Execution,
    /// Published lesson IDs (or planned lesson keys) the learner should know first.
    #[serde(default)]
    pub prerequisites: Vec<String>,
    pub assessed_goal: String,
    pub task: Task,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct PlannedLesson {
    pub key: String,
    pub title: String,
    pub phase: String,
    #[serde(default)]
    pub elective: bool,
    #[serde(default)]
    pub advanced: bool,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ReviewState { Draft, Approved }

/// Only a person edits `approved`; the app and tools never set it.
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Review {
    pub state: ReviewState,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub reviewed_by: String,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub reviewed_at: String,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub note: String,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ExecutionState { Ready, PendingEnvironment }

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct Execution {
    pub state: ExecutionState,
    /// Environment the grader needs, e.g. `docker:redis`. Informational; nothing is started.
    #[serde(default)]
    pub requires: Vec<String>,
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub note: String,
}

fn safe_key(key: &str) -> bool {
    !key.is_empty() && key.len() <= 64 && key.bytes().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == b'-')
}

impl FutureChallengeFile {
    pub fn parse(text: &str, course: &CourseManifest) -> Result<Self, String> {
        let file: Self = serde_json::from_str(text).map_err(|e| format!("도전 과제 파일을 읽지 못했어요. {e}"))?;
        file.validate(course)?;
        Ok(file)
    }
    pub fn validate(&self, course: &CourseManifest) -> Result<(), String> {
        if self.schema_version != 1 || self.course_id != course.id || self.challenges.len() > 200 {
            return Err("도전 과제 파일의 버전과 코스 ID를 확인하세요.".into());
        }
        let mut ids = HashSet::new();
        let published: HashSet<&str> = course.lessons.iter().map(|l| l.id.as_str()).collect();
        for challenge in &self.challenges {
            if !resource_code(&challenge.id, "chl") || !ids.insert(challenge.id.as_str()) || !ids.insert(challenge.task.id.as_str()) {
                return Err("도전 과제와 문제의 고유 코드를 확인하세요.".into());
            }
            let planned = &challenge.planned_lesson;
            if !safe_key(&planned.key) || planned.title.trim().is_empty() || planned.phase.trim().is_empty() || challenge.assessed_goal.trim().is_empty() {
                return Err(format!("{}: 예정 수업과 평가 목표를 확인하세요.", challenge.id));
            }
            let built = |repository: &str| repository.split('/').nth(1).is_some_and(|name| name == planned.key || name.strip_prefix("mq3-lesson-redesigned-") == Some(planned.key.as_str()));
            if published.contains(planned.key.as_str()) || course.lessons.iter().any(|l| built(&l.repository)) {
                return Err(format!("{}: 이미 공개된 수업이에요. 수업의 마지막 문제를 쓰세요.", challenge.id));
            }
            if challenge.review.state == ReviewState::Approved && (challenge.review.reviewed_by.trim().is_empty() || challenge.review.reviewed_at.trim().is_empty()) {
                return Err(format!("{}: 승인에는 검토한 사람과 날짜가 필요해요.", challenge.id));
            }
            if challenge.execution.state == ExecutionState::PendingEnvironment && challenge.execution.note.trim().is_empty() {
                return Err(format!("{}: 실행 환경 준비 상태를 설명하세요.", challenge.id));
            }
            if challenge.prerequisites.iter().any(|p| !published.contains(p.as_str()) && !safe_key(p)) {
                return Err(format!("{}: 선수 학습을 확인하세요.", challenge.id));
            }
            let lesson = challenge.lesson();
            lesson.validate().map_err(|e| format!("{}: {e}", challenge.id))?;
            if !is_graded(&challenge.task) {
                return Err(format!("{}: 채점 기준이 있는 문제여야 해요.", challenge.id));
            }
        }
        Ok(())
    }
    /// Learners see approved problems only; drafts are for accounts that can edit the course.
    pub fn visible(&self, reviewer: bool) -> Vec<&FutureChallenge> {
        self.challenges.iter().filter(|c| reviewer || c.review.state == ReviewState::Approved).collect()
    }
}

impl FutureChallenge {
    /// A one-problem lesson so the existing task screen and grader run it unchanged. Its revision
    /// follows the task bytes, so saved drafts of an older version are not reused.
    pub fn lesson(&self) -> Lesson {
        use sha2::{Digest, Sha256};
        let mut task = self.task.clone();
        task.required = true;
        let bytes = serde_json::to_vec(&task).unwrap_or_default();
        Lesson {
            change_history: vec![],
            schema_version: 1,
            id: self.id.clone(),
            revision: format!("future-{}", &format!("{:x}", Sha256::digest(&bytes))[..12]),
            title: self.planned_lesson.title.clone(),
            description: self.assessed_goal.clone(),
            sources: vec![],
            objectives: vec![self.assessed_goal.clone()],
            learning_strategy: String::new(),
            chapters: vec![],
            sections: vec![],
            tasks: vec![task],
            review_enabled: false,
        }
    }
    pub fn runnable(&self) -> bool { self.execution.state == ExecutionState::Ready }
}
