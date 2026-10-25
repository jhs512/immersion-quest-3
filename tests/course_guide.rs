use molip_quest::{bundled_courses,content_updates::SnapshotStore,course_guide::CourseGuide};
#[test]
fn course_guide_matches_all_installed_goals_and_order_without_teaching_answers() {
    let root=tempfile::tempdir().unwrap();let store=SnapshotStore::new(root.path());
    for repository in bundled_courses::REPOSITORIES {
        let snapshot=bundled_courses::prepare(&store,repository).unwrap().unwrap();
        let guide=CourseGuide::from_snapshot(&snapshot);
        assert!(!guide.objectives.is_empty());assert!(!guide.scope_note.is_empty());
        assert_eq!(guide.lessons.len(),snapshot.course().lessons.len());
        for (row,reference) in guide.lessons.iter().zip(&snapshot.course().lessons) {
            let lesson=snapshot.lesson(reference).unwrap();assert_eq!(row.title,lesson.title);assert_eq!(row.objectives,lesson.objectives);
            assert!(!row.objectives.is_empty());
        }
        let raw=serde_json::to_string(&guide).unwrap();
        for forbidden in ["starter_code","solution","core_flow","policy_snapshot","narration_cache","task_id"] {assert!(!raw.contains(&format!("\"{forbidden}\"")));}
        let actions=guide.narration(None);assert!(actions.iter().all(|a|a["action"]=="say"));
        for (i,row) in guide.lessons.iter().enumerate(){
            let single=guide.narration(Some(i));assert!(!single.is_empty());
            assert!(single.iter().all(|a|a["target"].as_str().unwrap().starts_with(&format!("#course-guide-lesson-{i}"))));
            assert!(single.iter().any(|a|a["text"].as_str().unwrap().contains(&row.title)));
        }
        if repository.ends_with("java-backend") {
            assert!(guide.description.contains("Spring Boot"));assert!(!guide.description.starts_with("Bash"));
            assert!(guide.objectives[0].contains("기초가 탄탄한"));assert!(guide.scope_note.contains("후속 확장"));
            assert_eq!(guide.lessons.len(),40);
        }
    }
}
#[test]
fn a_guide_follows_the_snapshot_revision_and_never_invents_missing_course_goals() {
    let root=tempfile::tempdir().unwrap();let store=SnapshotStore::new(root.path());
    let make=|v:&str|{let path=std::path::Path::new("tests/fixtures/player-pilot").join(v);let snap=store.prepare("mq3-validation/course",&std::fs::read_to_string(path.join("course.json")).unwrap(),|_|Ok(std::fs::read_to_string(path.join("lesson.json")).unwrap())).unwrap();CourseGuide::from_snapshot(&snap)};
    let a=make("a");let b=make("b");assert_ne!(a.fingerprint,b.fingerprint);
    assert_eq!(a.lessons,b.lessons,"changed task answers must not leak into the course guide");
    assert!(a.objectives.is_empty());assert!(!a.lessons[0].objectives.is_empty());
}
