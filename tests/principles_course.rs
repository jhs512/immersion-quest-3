//! Requires the generated independent lesson and an installed JDK 25.
use molip_quest::{lesson_runner,repository_course::Lesson};

#[tokio::test]
#[ignore = "requires JDK 25; run python tools/narrate.py --principles first"]
async fn small_experiments_grade_real_java_and_replay_their_explanations() {
    let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let lesson:Lesson=serde_json::from_str(&std::fs::read_to_string(root.join("target/principles-course/lesson.json")).unwrap()).unwrap();
    lesson.validate().unwrap();
    assert!(!lesson.review_enabled);
    for task in lesson.tasks {
        assert!(lesson_runner::check(&task,&task.solution).await.unwrap().passed,"{} answer",task.id);
        assert!(!lesson_runner::check(&task,&task.starter_code).await.unwrap().passed,"{} starter",task.id);
        let mut code=String::new();
        for step in &task.narration {
            match step["action"].as_str().unwrap() {
                "set_code"=>code=step["code"].as_str().unwrap().into(),
                "patch_code"=>{
                    let before=step["before"].as_str().unwrap();
                    assert_eq!(code.matches(before).count(),1,"{} patch",task.id);
                    code=code.replacen(before,step["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let result=lesson_runner::run(&task,&code,"").await.unwrap();
                    assert_eq!(result.success,!step["expected_failure"].as_bool().unwrap_or(false),"{} narration: {}",task.id,result.stderr);
                },
                _=>{},
            }
        }
        assert_eq!(code,task.solution,"{} final narration",task.id);
    }
}
