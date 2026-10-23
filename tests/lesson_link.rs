use molip_quest::{lesson_link::{LessonLink,Instance,Request},repository_course::CourseManifest};
#[test]
fn links_round_trip_and_cannot_pick_a_lesson_from_another_course(){
    let raw=include_str!("../courses/redesigned-courses/java-backend.json");
    let course=CourseManifest::parse(raw).unwrap();
    let link=LessonLink::new(&course.repository,&course.lessons[0].id).unwrap();
    assert_eq!(LessonLink::parse(&link.web_url()).unwrap(),link);assert_eq!(LessonLink::parse(&link.app_url()).unwrap(),link);
    assert_eq!(link.reference(&course).unwrap().id,course.lessons[0].id);
    let other=CourseManifest::parse(include_str!("../courses/redesigned-courses/aice-associate.json")).unwrap();
    assert!(link.reference(&other).is_err());
    for bad in ["molipquest://open?course=a/b&lesson=x&lesson=y","molipquest://open?course=a/b&lesson=x&exec=git","molipquest://open?course=../b&lesson=x","https://evil.invalid/immersion-quest-3/open/?course=a/b&lesson=x","molipquest://open?course=a/b&lesson=x%0A","molipquest://open?course=a/b&lesson=x#more"] {assert!(LessonLink::parse(bad).is_err(),"{bad}");}
}
#[test]
fn existing_instance_acknowledges_links_and_a_new_instance_can_start_after_exit(){
    let directory=tempfile::tempdir().unwrap();
    let primary=Instance::claim(directory.path(),None).unwrap().unwrap();
    let target=LessonLink::new("owner/course","lsn_example").unwrap();
    assert!(Instance::claim(directory.path(),Some(&target.app_url())).unwrap().is_none());
    assert!(matches!(molip_quest::lesson_link::take(),Some(Request::Open(actual)) if actual==target));
    drop(primary);
    assert!(Instance::claim(directory.path(),None).unwrap().is_some());
}

#[test]
fn course_links_round_trip_without_selecting_a_lesson(){
    let link=LessonLink::course("owner/course").unwrap();
    assert_eq!(link.lesson,None);
    assert_eq!(LessonLink::parse(&link.web_url()).unwrap(),link);
    assert_eq!(LessonLink::parse(&link.app_url()).unwrap(),link);
    assert!(!link.web_url().contains("lesson="));
    for bad in ["molipquest://open?course=a/b&lesson=","molipquest://open?lesson=x","molipquest://open?course=a/b&course=c/d","molipquest://open?course=a/b&exec=git","molipquest://open?course=../b"]{
        assert!(LessonLink::parse(bad).is_err(),"{bad}");
    }
    let course=CourseManifest::parse(include_str!("../courses/redesigned-courses/java-backend.json")).unwrap();
    assert!(LessonLink::course(&course.repository).unwrap().reference(&course).is_err());
}
