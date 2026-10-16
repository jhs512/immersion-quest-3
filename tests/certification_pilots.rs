use molip_quest::{lesson_runner,repository_course::Lesson,runner::Artifact};

#[tokio::test]
#[ignore="requires generated pilots, managed pandas Python and JDK 25"]
async fn pilot_lessons_grade_actual_work_and_replay_narration() {
    let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    for course in ["aice-associate","engineer-practical"] {
        let lesson:Lesson=serde_json::from_str(&std::fs::read_to_string(root.join(format!("target/certification-pilots/{course}/lesson.json"))).unwrap()).unwrap();
        lesson.validate().unwrap();
        for task in &lesson.tasks {
            let answer=lesson_runner::check(task,&task.solution).await.unwrap();
            assert!(answer.passed,"{}: {}",task.id,serde_json::to_string(&answer).unwrap());
            assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"{} starter accepted",task.id);
            if course=="aice-associate" {
                assert!(!lesson_runner::check(task,&format!("print({:?})",task.tests[0].expected)).await.unwrap().passed,"memorized output accepted");
            }
            let mut source=String::new();
            for step in &task.narration {
                match step["action"].as_str().unwrap() {
                    "set_code"=>source=step["code"].as_str().unwrap().into(),
                    "patch_code"=>source=source.replacen(step["before"].as_str().unwrap(),step["after"].as_str().unwrap(),1),
                    "run"=>{
                        let output=lesson_runner::run(task,&source,&task.tests[0].input).await.unwrap();
                        assert_eq!(output.success,!step["expected_failure"].as_bool().unwrap_or(false),"{}: {}",task.id,output.stderr);
                    },
                    _=>{},
                }
            }
            assert_eq!(source,task.solution);
        }
        if course=="aice-associate" {
            let task=&lesson.tasks[1];
            let output=lesson_runner::run(task,&task.solution,"").await.unwrap();
            assert!(output.artifacts.iter().any(|a|matches!(a,Artifact::Table{..})),"missing real table");
            let output=lesson_runner::run(task,"import matplotlib.pyplot as plt\nplt.plot([1,2],[3,4])\nplt.show()\n","").await.unwrap();
            assert!(output.success,"{}",output.stderr);
            assert!(output.artifacts.iter().any(|a|matches!(a,Artifact::Image{..})),"missing real plot");
        }
    }
}
