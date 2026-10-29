//! What the course catalog shows: stored and remote progress, plus the events a learner just
//! earned in this process. A cleared lesson must read 100% the moment the learner returns to
//! the list, before the background recorder commits it to SQLite and long before any GitHub
//! read or upload. Nothing here ever removes an event: progress is an append-only history, so a
//! slow or stale response, an offline read or a failed upload can add to it but never roll a
//! fresh completion back.
//!
//! Every event carries its own account, course and lesson (`ProgressKey`) and its revision,
//! mode and round. Events are merged only through `issue_progress::merge`, which keeps the key
//! boundary and de-duplicates by event id; revision, mode and round are then judged by the same
//! `learning_progress`/`status` rules as stored history.
use crate::github_player::CourseProgress;
use crate::issue_progress::{self, LearningEvent, ProgressKey};
use crate::repository_course::LessonRef;
use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};

/// One account's progress in one course, as published by one repository.
#[derive(Clone, Debug, Default, Hash, Eq, PartialEq)]
pub struct ProgressScope {
    pub repository: String,
    pub user_id: u64,
    pub course_id: String,
}
impl ProgressScope {
    pub fn new(repository: &str, user_id: u64, course_id: &str) -> Self {
        Self { repository: repository.into(), user_id, course_id: course_id.into() }
    }
    fn key(&self, lesson_id: &str) -> ProgressKey {
        ProgressKey { user_id: self.user_id, course_id: self.course_id.clone(), lesson_id: lesson_id.into() }
    }
}

type Lessons = HashMap<String, Vec<LearningEvent>>;

fn union_into(target: &mut Lessons, scope: &ProgressScope, incoming: &Lessons) {
    for (lesson, events) in incoming {
        let key = scope.key(lesson);
        let current = target.remove(lesson).unwrap_or_default();
        // `merge` drops any event whose key is not this scope's lesson.
        let merged = issue_progress::merge(current.into_iter().chain(events.iter().cloned()), &key);
        if !merged.is_empty() {
            target.insert(lesson.clone(), merged);
        }
    }
}

/// Events earned in this process, kept in memory for as long as the app runs. The lesson
/// player adds to it synchronously whenever it records something, so the catalog can show the
/// result without waiting for the recorder thread, SQLite or GitHub.
#[derive(Default)]
pub struct Overlay {
    scopes: Mutex<HashMap<ProgressScope, Lessons>>,
}
impl Overlay {
    pub fn new() -> Self {
        Self::default()
    }
    pub fn remember(&self, repository: &str, events: &[LearningEvent]) {
        let mut scopes = self.scopes.lock().unwrap_or_else(|e| e.into_inner());
        for event in events {
            let scope = ProgressScope::new(repository, event.key.user_id, &event.key.course_id);
            let lessons = scopes.entry(scope.clone()).or_default();
            let incoming = HashMap::from([(event.key.lesson_id.clone(), vec![event.clone()])]);
            union_into(lessons, &scope, &incoming);
        }
    }
    /// Only this account's events in this course; another scope is never visible.
    pub fn events(&self, scope: &ProgressScope) -> Lessons {
        self.scopes.lock().unwrap_or_else(|e| e.into_inner()).get(scope).cloned().unwrap_or_default()
    }
}

/// The overlay the running app uses.
pub fn shared() -> &'static Overlay {
    static OVERLAY: OnceLock<Overlay> = OnceLock::new();
    OVERLAY.get_or_init(Overlay::new)
}

/// The catalog's loaded progress. Loader results are tagged with the scope they were read for;
/// a result for another account or course is ignored, and results for the current scope are
/// united, so a late response read before a newer one cannot hide what the newer one showed.
///
/// The catalog outlives a content update of the same account and course (only the manifest is
/// swapped), so a lesson's required problems are kept per lesson *revision*: a list read for the
/// previous revision - already here, or delivered late by a loader that started before the
/// update - is never used for the revision the manifest now shows. Events stay one united,
/// append-only history across revisions; `learning_progress` judges them per revision.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct CatalogProgress {
    scope: Option<ProgressScope>,
    events: Lessons,
    /// lesson id -> lesson revision -> required problems of that revision.
    required: HashMap<String, HashMap<String, Vec<String>>>,
}
impl CatalogProgress {
    fn enter(&mut self, current: &ProgressScope) {
        if self.scope.as_ref() != Some(current) {
            *self = Self { scope: Some(current.clone()), ..Self::default() };
        }
    }
    /// Returns false when the result belongs to a scope that is no longer on screen.
    pub fn accept(&mut self, loaded: CourseProgress, current: &ProgressScope) -> bool {
        if loaded.scope != *current {
            return false;
        }
        self.enter(current);
        union_into(&mut self.events, current, &loaded.events);
        for (lesson, required) in loaded.required {
            // A list without the revision it was read for cannot be placed safely; skip it.
            if let Some(revision) = loaded.revisions.get(&lesson) {
                self.required.entry(lesson).or_default().insert(revision.clone(), required);
            }
        }
        true
    }
    /// The open lesson already knows its revision and required problems; a catalog that has not
    /// finished loading that revision can still compute the lesson's percentage on return.
    pub fn require(&mut self, current: &ProgressScope, lesson_id: &str, revision: &str, required: Vec<String>) {
        self.enter(current);
        self.required.entry(lesson_id.into()).or_default().insert(revision.into(), required);
    }
    /// What the catalog renders for the current scope: loaded progress united with the overlay,
    /// and for each lesson of the manifest only the requirements of the revision it shows.
    pub fn view(&self, current: &ProgressScope, overlay: &Overlay, lessons: &[LessonRef]) -> (Lessons, HashMap<String, Vec<String>>) {
        let mut events = if self.scope.as_ref() == Some(current) { self.events.clone() } else { Lessons::new() };
        let mut required = HashMap::new();
        if self.scope.as_ref() == Some(current) {
            for lesson in lessons {
                if let Some(list) = self.required.get(&lesson.id).and_then(|by_revision| by_revision.get(&lesson.revision)) {
                    required.insert(lesson.id.clone(), list.clone());
                }
            }
        }
        union_into(&mut events, current, &overlay.events(current));
        (events, required)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::issue_progress::{EventKind, StudyMode};

    fn passed(user_id: u64, course: &str, lesson: &str, revision: &str, round: &str, task: &str) -> LearningEvent {
        let key = ProgressKey { user_id, course_id: course.into(), lesson_id: lesson.into() };
        let mut event = LearningEvent::new(key, revision, StudyMode::Full, round, EventKind::Attempt);
        event.task_id = Some(task.into());
        event.passed = true;
        event
    }
    fn loaded(scope: &ProgressScope, events: Vec<LearningEvent>) -> CourseProgress {
        loaded_at(scope, events, "v1", &["a", "b"])
    }
    fn loaded_at(scope: &ProgressScope, events: Vec<LearningEvent>, revision: &str, required: &[&str]) -> CourseProgress {
        let mut map: Lessons = HashMap::new();
        for event in events { map.entry(event.key.lesson_id.clone()).or_default().push(event); }
        CourseProgress {
            scope: scope.clone(),
            events: map,
            required: HashMap::from([("l".to_string(), required.iter().map(|id| id.to_string()).collect())]),
            revisions: HashMap::from([("l".to_string(), revision.to_string())]),
        }
    }
    fn lessons(revision: &str) -> Vec<LessonRef> {
        vec![LessonRef { id: "l".into(), title: "L".into(), repository: "o/l".into(), revision: revision.into(), sha256: String::new(), prerequisites: vec![], required: true, review_enabled: true, category: String::new(), track: String::new(), challenge_task: String::new() }]
    }

    #[test]
    fn overlay_events_stay_in_their_account_course_and_repository() {
        let overlay = Overlay::new();
        overlay.remember("o/r", &[passed(1, "c", "l", "v1", "r1", "a"), passed(2, "c", "l", "v1", "r1", "a"), passed(1, "d", "l", "v1", "r1", "a")]);
        assert_eq!(overlay.events(&ProgressScope::new("o/r", 1, "c"))["l"].len(), 1);
        assert_eq!(overlay.events(&ProgressScope::new("o/r", 2, "c"))["l"].len(), 1);
        assert!(overlay.events(&ProgressScope::new("o/other", 1, "c")).is_empty());
        assert!(overlay.events(&ProgressScope::new("o/r", 3, "c")).is_empty());
    }

    #[test]
    fn remembering_the_same_event_twice_keeps_one_and_rounds_stay_distinct() {
        let overlay = Overlay::new();
        let first = passed(1, "c", "l", "v1", "r1", "a");
        overlay.remember("o/r", &[first.clone(), first.clone()]);
        overlay.remember("o/r", &[first, passed(1, "c", "l", "v1", "r2", "a")]);
        assert_eq!(overlay.events(&ProgressScope::new("o/r", 1, "c"))["l"].len(), 2);
    }

    #[test]
    fn loaded_results_only_add_and_other_scopes_are_ignored() {
        let scope = ProgressScope::new("o/r", 1, "c");
        let overlay = Overlay::new();
        let mut catalog = CatalogProgress::default();
        let a = passed(1, "c", "l", "v1", "r1", "a");
        let b = passed(1, "c", "l", "v1", "r1", "b");
        assert!(catalog.accept(loaded(&scope, vec![a.clone(), b]), &scope));
        // A late, older reply that lacks `b` cannot remove it.
        assert!(catalog.accept(loaded(&scope, vec![a.clone()]), &scope));
        let view = catalog.view(&scope, &overlay, &lessons("v1"));
        assert_eq!(issue_progress::learning_progress(&view.0["l"], "v1", &view.1["l"]).percent, 100);
        // A reply for another account is dropped and does not reset this one.
        let other = ProgressScope::new("o/r", 2, "c");
        assert!(!catalog.accept(loaded(&other, vec![passed(2, "c", "l", "v1", "r1", "a")]), &scope));
        assert_eq!(catalog.view(&scope, &overlay, &lessons("v1")).0["l"].len(), 2);
        // Events with a foreign key inside a result are filtered out by `merge`.
        assert!(catalog.accept(loaded(&scope, vec![passed(9, "c", "l", "v1", "r1", "z")]), &scope));
        assert!(catalog.view(&scope, &overlay, &lessons("v1")).0["l"].iter().all(|e| e.key.user_id == 1));
        // Switching course shows nothing from the previous one.
        assert!(catalog.view(&ProgressScope::new("o/r", 1, "other"), &overlay, &lessons("v1")).0.is_empty());
    }

    #[test]
    fn overlay_completes_the_view_before_any_load_and_respects_revision() {
        let scope = ProgressScope::new("o/r", 1, "c");
        let overlay = Overlay::new();
        overlay.remember("o/r", &[passed(1, "c", "l", "v1", "r1", "a"), passed(1, "c", "l", "v1", "r1", "b")]);
        let mut catalog = CatalogProgress::default();
        catalog.require(&scope, "l", "v1", vec!["a".into(), "b".into()]);
        let view = catalog.view(&scope, &overlay, &lessons("v1"));
        assert_eq!(issue_progress::learning_progress(&view.0["l"], "v1", &view.1["l"]).percent, 100);
        // Legacy (non-stable) problem ids count only for their own revision.
        assert_eq!(issue_progress::learning_progress(&view.0["l"], "v2", &view.1["l"]).percent, 0);
        // A manifest showing v2 has no v2 requirements yet: the card waits instead of using v1's.
        assert!(catalog.view(&scope, &overlay, &lessons("v2")).1.is_empty());
    }

    #[test]
    fn requirements_follow_the_revision_the_manifest_shows_in_the_same_catalog() {
        let scope = ProgressScope::new("o/r", 1, "c");
        let overlay = Overlay::new();
        let mut catalog = CatalogProgress::default();
        // Loaded for v1, plus a second v1 result held back to arrive late.
        assert!(catalog.accept(loaded_at(&scope, vec![passed(1, "c", "l", "v1", "r1", "a")], "v1", &["a", "b"]), &scope));
        let late_v1 = loaded_at(&scope, vec![passed(1, "c", "l", "v1", "r1", "a")], "v1", &["a", "b"]);
        // The update to v2 replaces `b` with `c`; the learner clears v2 and returns at once.
        overlay.remember("o/r", &[passed(1, "c", "l", "v2", "r2", "a"), passed(1, "c", "l", "v2", "r2", "c")]);
        catalog.require(&scope, "l", "v2", vec!["a".into(), "c".into()]);
        let view = catalog.view(&scope, &overlay, &lessons("v2"));
        assert_eq!(view.1["l"], vec!["a".to_string(), "c".to_string()]);
        assert_eq!(issue_progress::learning_progress(&view.0["l"], "v2", &view.1["l"]).percent, 100);
        // The late v1 result adds its events but cannot replace v2's requirements.
        assert!(catalog.accept(late_v1, &scope));
        let view = catalog.view(&scope, &overlay, &lessons("v2"));
        assert_eq!(view.1["l"], vec!["a".to_string(), "c".to_string()]);
        assert_eq!(issue_progress::learning_progress(&view.0["l"], "v2", &view.1["l"]).percent, 100);
        assert!(view.0["l"].iter().any(|e| e.revision == "v1"), "previous-revision history is kept");
        // A v2 load replaces v2's list (same revision: latest read wins); v1 still renders for v1.
        assert!(catalog.accept(loaded_at(&scope, vec![], "v2", &["a", "c"]), &scope));
        assert_eq!(catalog.view(&scope, &overlay, &lessons("v1")).1["l"], vec!["a".to_string(), "b".to_string()]);
        // A result without revision tags carries no requirements into the catalog.
        let mut untagged = loaded_at(&scope, vec![], "v3", &["z"]);
        untagged.revisions.clear();
        assert!(catalog.accept(untagged, &scope));
        assert!(catalog.view(&scope, &overlay, &lessons("v3")).1.is_empty());
    }
}
