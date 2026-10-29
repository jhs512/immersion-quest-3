//! 내 전체 학습 진도 초기화: the per-lesson 진도 초기화 (`issue_progress::reset_event`) applied to every
//! lesson with history in every course this account has installed in this player.
//!
//! Nothing is deleted. Each lesson gets one appended `Reset` event, exactly like the lesson reset, so a
//! later union of histories (other devices, GitHub, a late upload) cannot bring the old progress back,
//! and the original events stay in the local store and in the GitHub progress issues. Only this
//! account's keys are touched; drafts, practice folders, settings and other accounts are not.
use std::collections::HashMap;

use crate::issue_progress::{self, effective, EventKind, LearningEvent, ProgressKey, StudyMode};
use crate::repository_course::CourseManifest;

/// One installed course and this account's history in it (lesson id -> events).
#[derive(Clone, Debug)]
pub struct CourseHistory {
    pub manifest: CourseManifest,
    pub events: HashMap<String, Vec<LearningEvent>>,
}

/// What the confirmation shows and what `apply` will write.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Plan {
    pub courses: Vec<CoursePlan>,
}
#[derive(Clone, Debug, PartialEq)]
pub struct CoursePlan {
    pub repository: String,
    pub course_id: String,
    pub title: String,
    pub lessons_total: usize,
    /// Lessons whose counted history is not empty: these get a reset event.
    pub lessons: Vec<(String, String, String)>, // (lesson id, title, revision)
}
impl Plan {
    pub fn lesson_count(&self) -> usize { self.courses.iter().map(|c| c.lessons.len()).sum() }
    pub fn course_count(&self) -> usize { self.courses.iter().filter(|c| !c.lessons.is_empty()).count() }
    pub fn is_empty(&self) -> bool { self.lesson_count() == 0 }
}

/// A lesson needs a reset when anything still counts in it (a pass, a completion, a view, a run…).
/// Lessons never opened, or already reset with nothing after it, are left alone so the reset does
/// not create empty progress issues for them.
pub fn plan(user_id: u64, histories: &[CourseHistory]) -> Plan {
    let mut courses = Vec::new();
    for history in histories {
        let manifest = &history.manifest;
        let mut lessons = Vec::new();
        for reference in &manifest.lessons {
            let known = history.events.get(&reference.id).map(Vec::as_slice).unwrap_or(&[]);
            let own: Vec<LearningEvent> = known.iter()
                .filter(|e| e.key.user_id == user_id && e.key.course_id == manifest.id && e.key.lesson_id == reference.id)
                .cloned().collect();
            if effective(&own).iter().any(|e| e.kind != EventKind::Reset) {
                lessons.push((reference.id.clone(), reference.title.clone(), reference.revision.clone()));
            }
        }
        courses.push(CoursePlan { repository: manifest.repository.clone(), course_id: manifest.id.clone(),
            title: manifest.title.clone(), lessons_total: manifest.lessons.len(), lessons });
    }
    Plan { courses }
}

/// The reset events of a plan, one per planned lesson, each voiding what this account's history of
/// that lesson knows now (including events a skewed clock stamped in the same second or later).
pub fn events(user_id: u64, plan: &Plan, histories: &[CourseHistory]) -> Vec<(String, String, LearningEvent)> {
    let round = issue_progress::new_id();
    let mut out = Vec::new();
    for course in &plan.courses {
        let history = histories.iter().find(|h| h.manifest.repository == course.repository && h.manifest.id == course.course_id);
        for (lesson_id, title, revision) in &course.lessons {
            let key = ProgressKey { user_id, course_id: course.course_id.clone(), lesson_id: lesson_id.clone() };
            let known = history.and_then(|h| h.events.get(lesson_id)).map(Vec::as_slice).unwrap_or(&[]);
            out.push((course.repository.clone(), title.clone(), issue_progress::reset_event(key, revision, StudyMode::Full, &round, known)));
        }
    }
    out
}

/// Write every reset through `record` (the same durable path as the lesson reset). Stops at the
/// first failure and reports how many were saved, so the caller can say exactly what happened.
pub fn apply(user_id: u64, plan: &Plan, histories: &[CourseHistory],
             mut record: impl FnMut(&str, &str, &LearningEvent) -> Result<(), String>) -> Result<usize, (usize, String)> {
    let mut saved = 0;
    for (repository, title, event) in events(user_id, plan, histories) {
        record(&repository, &title, &event).map_err(|error| (saved, error))?;
        saved += 1;
    }
    Ok(saved)
}
