use molip_quest::{repository_course::{CourseManifest,Lesson},lesson_runner};
use std::path::Path;

#[tokio::test]
#[ignore = "Executes published lesson answers with JDK, Git, Node, JUnit and Edge"]
async fn every_repository_answer_passes_and_starter_is_rejected() {
    let root=Path::new(env!("CARGO_MANIFEST_DIR")).join("target/backend-course");
    let course=CourseManifest::parse(&std::fs::read_to_string(root.join("mq3-course-java-backend/course.json")).unwrap()).unwrap();
    assert_eq!(course.lessons.len(),24);
    let selected=std::env::var("MQ3_VERIFY_LESSON").ok();
    for reference in course.lessons {
        if selected.as_ref().is_some_and(|s| !reference.id.contains(s)) {continue}
        let text=std::fs::read_to_string(root.join(format!("mq3-lesson-{}/lesson.json",reference.id))).unwrap();
        let lesson=Lesson::parse(&text,&reference).unwrap();
        for task in lesson.tasks {
            eprintln!("checking {}/{}",lesson.id,task.id);
            let report=lesson_runner::check(&task,&task.solution).await.unwrap();
            assert!(report.passed,"{}/{} answer failed: {}",lesson.id,task.id,serde_json::to_string(&report).unwrap());
            let report=lesson_runner::check(&task,&task.starter_code).await.unwrap();
            assert!(!report.passed,"{}/{} empty starter was accepted",lesson.id,task.id);
        }
    }
}

#[tokio::test]
#[ignore = "Replays small narration edits and executes every runnable stage"]
async fn repository_walkthroughs_reconstruct_answers_and_run() {
    let root=Path::new(env!("CARGO_MANIFEST_DIR")).join("target/backend-course");
    let course=CourseManifest::parse(&std::fs::read_to_string(root.join("mq3-course-java-backend/course.json")).unwrap()).unwrap();
    for reference in course.lessons {
        let lesson:Lesson=serde_json::from_str(&std::fs::read_to_string(root.join(format!("mq3-lesson-{}/lesson.json",reference.id))).unwrap()).unwrap();
        for task in lesson.tasks {
            if task.language==molip_quest::repository_course::TaskLanguage::Java {continue} // existing Java narration suite covers these
            eprintln!("replaying {}/{}",lesson.id,task.id);
            let mut code=String::new();let mut runs=0;
            for action in &task.narration {
                match action["action"].as_str().unwrap() {
                    "set_code"=>code=action["code"].as_str().unwrap().into(),
                    "patch_code"=>{let before=action["before"].as_str().unwrap();assert_eq!(code.matches(before).count(),1);code=code.replacen(before,action["after"].as_str().unwrap(),1);},
                    "run"=>{runs+=1;let input=task.tests.first().map(|c|c.input.as_str()).unwrap_or("");let result=lesson_runner::run(&task,&code,input).await.unwrap();
                        assert!(result.success||action["expected_failure"]==true,"{}/{} narration stage failed: {}",lesson.id,task.id,result.stderr);
                    },_=>()
                }
            }
            assert_eq!(code,task.solution,"{}/{} final narration differs",lesson.id,task.id);assert!(runs>=2);
        }
    }
}
