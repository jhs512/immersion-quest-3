use molip_quest::repository_course::CourseManifest;
use serde_json::json;

fn root() -> std::path::PathBuf { env!("CARGO_MANIFEST_DIR").into() }
fn course() -> CourseManifest {
    CourseManifest::parse(&std::fs::read_to_string(root().join("courses/redesigned-courses/java-backend.json")).unwrap()).unwrap()
}

// Lessons 27-34, withdrawn from the course on 2026-10-26 by user order. Their lesson repositories, tags and
// learners' records are kept; the course no longer lists, previews or classifies them.
const WITHDRAWN: [&str; 8] = ["lsn_0783b508-0383-49ec-85d8-ee33a68eafef", "lsn_c0bd2008-1271-47ec-a3b3-960c6bf9f0e9",
    "lsn_70a3aa49-0bd6-4cbc-a04b-28ca43e5be18", "lsn_d03b8a15-633a-4860-8ee4-51d266ee4150",
    "lsn_fc2e0b8b-63f6-4280-b9e9-17703598cb0b", "lsn_2bf46a1f-7613-43b6-90a9-859993baac1f",
    "lsn_bc56070b-0498-48fe-ac5a-0050080a44c1", "lsn_ca915bbe-766c-42ef-96b8-33c36c57f52a"];

#[test]
fn withdrawn_lessons_leave_no_listing_preview_or_empty_topic() {
    let course = course();
    assert_eq!(course.lessons.len(), 43);
    // The 26 lessons of 2026-10-25 keep 필수 and 기본; lessons added on 2026-10-26 are optional with no track.
    let catalog:serde_json::Value=serde_json::from_str(include_str!("../tools/redesigned_courses/catalog.json")).unwrap();
    let legacy:std::collections::BTreeSet<_>=catalog["courses"][0]["lessons"].as_array().unwrap().iter()
        .filter(|l| l.get("added_on").is_none()).map(|l|l["id"].as_str().unwrap()).collect();
    assert_eq!(legacy.len(),26);
    for lesson in &course.lessons {
        assert!(!lesson.category.is_empty());
        if legacy.contains(lesson.id.as_str()) {assert!(lesson.required && lesson.track=="basic");}
        else {assert!(!lesson.required && lesson.track.is_empty());}
    }
    let raw = std::fs::read_to_string(root().join("courses/redesigned-courses/java-backend.json")).unwrap();
    for id in WITHDRAWN { assert!(!raw.contains(id), "{id} still referenced"); }
    let ids: Vec<_> = course.lessons.iter().map(|l| l.id.clone()).collect();
    assert_eq!(course.lesson_previews.keys().cloned().collect::<std::collections::BTreeSet<_>>(), ids.iter().cloned().collect());
    assert!(course.lessons.iter().all(|l| l.prerequisites.iter().all(|p| ids.contains(p))));
    let used: std::collections::BTreeSet<_> = course.lessons.iter().map(|l| l.category.clone()).collect();
    assert_eq!(course.categories.iter().map(|c| c.id.clone()).collect::<std::collections::BTreeSet<_>>(), used, "no empty topic group");
}

#[test]
fn previews_are_ungraded_metadata_and_old_courses_still_open() {
    let course = course();
    assert_eq!(course.lesson_previews.len(), 43);
    let mut old = serde_json::to_value(&course).unwrap();
    old.as_object_mut().unwrap().remove("lesson_previews");
    assert!(CourseManifest::parse(&old.to_string()).unwrap().lesson_previews.is_empty());
    let mut invalid = old.clone();
    invalid["lesson_previews"] = json!({"unknown": serde_json::to_value(course.lesson_previews.values().next().unwrap()).unwrap()});
    assert!(CourseManifest::parse(&invalid.to_string()).is_err());
    let mut invalid = serde_json::to_value(&course).unwrap();
    invalid["lesson_previews"][&course.lessons[0].id]["scenario"] = json!([]);
    assert!(CourseManifest::parse(&invalid.to_string()).is_err());
}
