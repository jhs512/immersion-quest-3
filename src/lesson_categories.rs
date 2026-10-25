//! Lesson classification on a course: a topic category and a curricular track (기본/필수/고급).
//! 2026-10-25 user decision: every lesson that existed then is 「기본」 (basic). 기본 means neither required
//! nor easy; completion still follows `required`.
//!
//! Both axes are optional course metadata. They never change lesson bytes, revisions or progress, and
//! they are independent of how a lesson teaches (follow-along, final problem) or how a task is answered
//! (code, choice, fill). A manifest without them shows today's flat list. Unknown category ids and unknown
//! track values are tolerated (shown as 미분류 / no label) so a newer manifest never blocks a course.
//! `required` keeps its own meaning: whether a lesson counts toward course completion.
use crate::repository_course::{CourseManifest, LessonRef};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
pub struct LessonCategory {
    pub id: String,
    pub title: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LessonTrack {
    Basic,
    Essential,
    Advanced,
}

impl LessonTrack {
    pub fn parse(value: &str) -> Option<Self> {
        match value {
            "basic" => Some(Self::Basic),
            "essential" => Some(Self::Essential),
            "advanced" => Some(Self::Advanced),
            _ => None,
        }
    }
    pub fn label(self) -> &'static str {
        match self {
            Self::Basic => "기본",
            Self::Essential => "필수",
            Self::Advanced => "고급",
        }
    }
    pub fn class(self) -> &'static str {
        match self {
            Self::Basic => "lesson-track basic",
            Self::Essential => "lesson-track essential",
            Self::Advanced => "lesson-track advanced",
        }
    }
}

impl LessonRef {
    pub fn track(&self) -> Option<LessonTrack> {
        LessonTrack::parse(&self.track)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TrackFilter {
    All,
    Only(LessonTrack),
}

impl TrackFilter {
    fn keeps(self, lesson: &LessonRef) -> bool {
        match self {
            Self::All => true,
            Self::Only(track) => lesson.track() == Some(track),
        }
    }
}

pub const UNCATEGORIZED: &str = "미분류";

/// One heading of the course lesson list. `title` is `None` only for a course without categories,
/// which keeps the legacy flat list. `index` is the manifest position, i.e. the recommended order
/// shown as 「수업 N」, so grouping never renumbers lessons.
#[derive(Debug, PartialEq)]
pub struct LessonGroup<'a> {
    pub title: Option<String>,
    pub lessons: Vec<(usize, &'a LessonRef)>,
}

fn categories(course: &CourseManifest) -> Vec<&LessonCategory> {
    let mut seen = HashSet::new();
    course.categories.iter().filter(|c| !c.id.is_empty() && !c.title.trim().is_empty() && seen.insert(c.id.as_str())).collect()
}

pub fn groups(course: &CourseManifest, filter: TrackFilter) -> Vec<LessonGroup<'_>> {
    let kept: Vec<(usize, &LessonRef)> = course.lessons.iter().enumerate().filter(|(_, l)| filter.keeps(l)).collect();
    let known = categories(course);
    if known.is_empty() {
        return if kept.is_empty() { vec![] } else { vec![LessonGroup { title: None, lessons: kept }] };
    }
    let mut groups: Vec<LessonGroup> = known.iter().map(|c| LessonGroup {
        title: Some(c.title.clone()),
        lessons: kept.iter().copied().filter(|(_, l)| l.category == c.id).collect(),
    }).collect();
    let ids: HashSet<&str> = known.iter().map(|c| c.id.as_str()).collect();
    groups.push(LessonGroup { title: Some(UNCATEGORIZED.into()), lessons: kept.iter().copied().filter(|(_, l)| !ids.contains(l.category.as_str())).collect() });
    groups.retain(|g| !g.lessons.is_empty());
    groups
}

/// Whether the course carries any usable category, so a grouped view can be offered at all.
pub fn has_categories(course: &CourseManifest) -> bool {
    !categories(course).is_empty()
}

/// The whole course in its recommended order, one untitled group, whatever categories it has.
/// Numbers stay the manifest positions, exactly as in the grouped view.
pub fn flat(course: &CourseManifest, filter: TrackFilter) -> Vec<LessonGroup<'_>> {
    let kept: Vec<(usize, &LessonRef)> = course.lessons.iter().enumerate().filter(|(_, l)| filter.keeps(l)).collect();
    if kept.is_empty() { vec![] } else { vec![LessonGroup { title: None, lessons: kept }] }
}

/// Tracks present on the course, in display order (기본, 필수, 고급).
pub fn present_tracks(course: &CourseManifest) -> Vec<LessonTrack> {
    [LessonTrack::Basic, LessonTrack::Essential, LessonTrack::Advanced].into_iter()
        .filter(|track| course.lessons.iter().any(|l| l.track() == Some(*track))).collect()
}

/// A track filter only helps when it can separate lessons: at least two different tracks are present.
/// A single label (e.g. every lesson 기본) is still shown on each card, without a filter.
pub fn has_tracks(course: &CourseManifest) -> bool {
    present_tracks(course).len() >= 2
}

#[cfg(test)]
mod tests {
    use super::*;

    fn lesson(id: &str, category: &str, track: &str) -> serde_json::Value {
        let mut value = serde_json::json!({"id": id, "title": format!("T{id}"), "repository": "o/l", "revision": "r-1",
            "sha256": "a".repeat(64)});
        if !category.is_empty() { value["category"] = category.into(); }
        if !track.is_empty() { value["track"] = track.into(); }
        value
    }
    fn course(categories: serde_json::Value, lessons: Vec<serde_json::Value>) -> CourseManifest {
        let mut value = serde_json::json!({"schema_version": 1, "id": "c", "title": "C", "description": "", "repository": "o/c", "lessons": lessons});
        if !categories.is_null() { value["categories"] = categories; }
        CourseManifest::parse(&value.to_string()).unwrap()
    }
    fn ids(groups: &[LessonGroup]) -> Vec<(Option<String>, Vec<usize>)> {
        groups.iter().map(|g| (g.title.clone(), g.lessons.iter().map(|(i, _)| *i).collect())).collect()
    }

    #[test]
    fn legacy_manifest_stays_a_flat_list_and_round_trips_unchanged() {
        let text = serde_json::json!({"schema_version": 1, "id": "c", "title": "C", "description": "", "repository": "o/c",
            "lessons": [lesson("a", "", ""), lesson("b", "", "")]}).to_string();
        let parsed = CourseManifest::parse(&text).unwrap();
        assert_eq!(ids(&groups(&parsed, TrackFilter::All)), vec![(None, vec![0, 1])]);
        assert!(!has_tracks(&parsed));
        let again: serde_json::Value = serde_json::to_value(&parsed).unwrap();
        assert!(again.get("categories").is_none());
        assert!(again["lessons"][0].get("category").is_none() && again["lessons"][0].get("track").is_none());
        assert!(again["lessons"][0]["required"].as_bool().unwrap(), "required still defaults to true");
    }

    #[test]
    fn groups_follow_category_order_keep_manifest_numbers_and_put_unknown_last() {
        let c = course(serde_json::json!([{"id": "terminal", "title": "터미널 기초"}, {"id": "java", "title": "자바 기초"}, {"id": "empty", "title": "빈 분류"}]),
            vec![lesson("bash", "terminal", "essential"), lesson("values", "java", "essential"), lesson("odd", "missing", ""),
                 lesson("vim", "terminal", "advanced"), lesson("plain", "", "")]);
        assert_eq!(ids(&groups(&c, TrackFilter::All)), vec![
            (Some("터미널 기초".into()), vec![0, 3]), (Some("자바 기초".into()), vec![1]), (Some(UNCATEGORIZED.into()), vec![2, 4])]);
    }

    #[test]
    fn track_filter_shows_only_labelled_lessons_and_unknown_tracks_have_no_label() {
        let c = course(serde_json::json!([{"id": "t", "title": "터미널 기초"}]),
            vec![lesson("a", "t", "essential"), lesson("b", "t", "advanced"), lesson("c", "t", "expert"), lesson("d", "t", "")]);
        assert!(has_tracks(&c));
        assert_eq!(c.lessons[2].track(), None);
        assert_eq!(ids(&groups(&c, TrackFilter::Only(LessonTrack::Essential))), vec![(Some("터미널 기초".into()), vec![0])]);
        assert_eq!(ids(&groups(&c, TrackFilter::Only(LessonTrack::Advanced))), vec![(Some("터미널 기초".into()), vec![1])]);
        assert_eq!(LessonTrack::Essential.label(), "필수");
        assert_eq!(LessonTrack::Advanced.label(), "고급");
    }

    #[test]
    fn basic_label_alone_shows_on_cards_but_offers_no_filter() {
        let c = course(serde_json::Value::Null, vec![lesson("a", "", "basic"), lesson("b", "", "basic"), lesson("new", "", "")]);
        assert_eq!(c.lessons[0].track(), Some(LessonTrack::Basic));
        assert_eq!(LessonTrack::Basic.label(), "기본");
        assert_eq!(c.lessons[2].track(), None, "a lesson without an approved track has no label");
        assert_eq!(present_tracks(&c), vec![LessonTrack::Basic]);
        assert!(!has_tracks(&c), "one track cannot be filtered");
        assert_eq!(ids(&groups(&c, TrackFilter::All)), vec![(None, vec![0, 1, 2])], "flat list and manifest numbers stay");
        let mixed = course(serde_json::Value::Null, vec![lesson("a", "", "basic"), lesson("b", "", "advanced")]);
        assert!(has_tracks(&mixed));
        assert_eq!(present_tracks(&mixed), vec![LessonTrack::Basic, LessonTrack::Advanced]);
    }

    #[test]
    fn broken_category_lists_never_block_the_course() {
        let c = course(serde_json::json!([{"id": "", "title": "빈 id"}, {"id": "a", "title": " "}, {"id": "b", "title": "B"}, {"id": "b", "title": "B again"}]),
            vec![lesson("x", "b", ""), lesson("y", "a", "")]);
        assert_eq!(ids(&groups(&c, TrackFilter::All)), vec![(Some("B".into()), vec![0]), (Some(UNCATEGORIZED.into()), vec![1])]);
        let none = course(serde_json::json!([{"id": "b", "title": "B"}]), vec![lesson("x", "b", "")]);
        assert!(groups(&none, TrackFilter::Only(LessonTrack::Advanced)).is_empty());
    }

    #[test]
    fn flat_view_keeps_recommended_order_and_numbers_even_with_categories() {
        let c = course(serde_json::json!([{"id": "t", "title": "터미널 기초"}, {"id": "j", "title": "자바 기초"}]),
            vec![lesson("bash", "t", "basic"), lesson("values", "j", "basic"), lesson("vim", "t", ""), lesson("odd", "", "")]);
        assert!(has_categories(&c));
        assert_eq!(ids(&flat(&c, TrackFilter::All)), vec![(None, vec![0, 1, 2, 3])]);
        assert_eq!(ids(&flat(&c, TrackFilter::Only(LessonTrack::Basic))), vec![(None, vec![0, 1])]);
        let plain = course(serde_json::Value::Null, vec![lesson("a", "", "basic")]);
        assert!(!has_categories(&plain), "no categories: the grouped view is not offered");
        let broken = course(serde_json::json!([{"id": "", "title": "빈 id"}]), vec![lesson("a", "", "")]);
        assert!(!has_categories(&broken), "an unusable category list offers no grouping");
        assert!(flat(&c, TrackFilter::Only(LessonTrack::Advanced)).is_empty());
    }

    #[test]
    fn classification_does_not_touch_identity_revision_or_completion() {
        let c = course(serde_json::json!([{"id": "t", "title": "T"}]), vec![lesson("a", "t", "advanced")]);
        let l = &c.lessons[0];
        assert_eq!((l.id.as_str(), l.revision.as_str(), l.required), ("a", "r-1", true));
    }
}
