use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

// Exercise the same source-file execution, variations and output normalization as submission.
#[tokio::test]
async fn real_network_examples_grade_through_the_player_runner() {
    for key in ["network-bytes","network-endpoints","network-ip","network-routing",
                "network-dns","network-tcp","network-udp","network-http"] {
        let path=std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join(format!("courses/redesigned/{key}.json"));
        let lesson:Lesson=serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
        lesson.validate().unwrap();
        let java_tasks:Vec<_>=lesson.tasks.iter().filter(|t|t.git_terminal.is_none()).collect();
        assert_eq!(java_tasks.len(),4);
        // The fourth stage integrates the two units. Check both ends of its grading contract.
        let task=java_tasks.last().unwrap();
        let valid=lesson_runner::check(task,&task.solution).await.unwrap();
        assert!(valid.passed,"{key}: valid source rejected");
        assert!(valid.cases.len()>=3,"{key}: variations were skipped");
        let initial=lesson_runner::check(task,&task.starter_code).await.unwrap();
        assert!(!initial.passed,"{key}: unfinished starter passed");
    }
}

#[test]
fn all_courses_publish_a_preview_for_every_registered_lesson() {
    for file in ["java-backend","aice-associate","engineer-practical"] {
        let path=std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join(format!("courses/redesigned-courses/{file}.json"));
        let course=CourseManifest::parse(&std::fs::read_to_string(path).unwrap()).unwrap();
        assert_eq!(course.lesson_previews.len(),course.lessons.len(),"{file}");
        for lesson in &course.lessons { assert!(course.lesson_previews.contains_key(&lesson.id)); }
    }
}
