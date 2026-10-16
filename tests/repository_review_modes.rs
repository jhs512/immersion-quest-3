use molip_quest::repository_course::{CourseManifest,Lesson,LessonRef};
use serde_json::json;
use sha2::{Digest,Sha256};

fn published(review:Option<bool>)->(String,LessonRef) {
    let mut value=json!({"schema_version":1,"id":"sample","revision":"v1.0.0","title":"수업","description":"","sources":[],"sections":[],"tasks":[{"id":"one","title":"문제","goal":"목표","language":"javascript","starter_code":"","solution":"console.log(1);","tests":[{"input":"","expected":"1"}]}]});
    if let Some(enabled)=review{value["review_enabled"]=json!(enabled)}
    let text=serde_json::to_string(&value).unwrap();
    let mut reference=json!({"id":"sample","title":"수업","repository":"owner/lesson","revision":"v1.0.0","sha256":format!("{:x}",Sha256::digest(text.as_bytes()))});
    if let Some(enabled)=review{reference["review_enabled"]=json!(enabled)}
    (text,serde_json::from_value(reference).unwrap())
}
#[test]
fn existing_published_lessons_keep_their_review_mode() {
    let (text,reference)=published(None);
    assert!(reference.review_enabled);
    assert!(Lesson::parse(&text,&reference).unwrap().review_enabled);
}
#[test]
fn a_lesson_without_review_round_trips_through_course_composition() {
    let (text,reference)=published(Some(false));
    assert!(!Lesson::parse(&text,&reference).unwrap().review_enabled);
    let raw=json!({"schema_version":1,"id":"course","title":"코스","description":"","repository":"owner/course","lessons":[reference]});
    let course=CourseManifest::parse(&raw.to_string()).unwrap();
    assert!(!course.lessons[0].review_enabled);
}
#[test]
fn stale_course_cannot_offer_an_unsupported_review_mode() {
    let (text,mut reference)=published(Some(false));reference.review_enabled=true;
    assert!(Lesson::parse(&text,&reference).unwrap_err().contains("복습모드"));
}
