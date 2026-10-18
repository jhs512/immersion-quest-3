use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn nine_java_steps_and_every_teacher_run_agree_with_actual_jdk_output() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/n/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/java-values.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),9);
    let expected:Vec<Vec<&str>>=vec![vec!["2"],vec!["2","3"],vec!["5"],vec!["2","3"],vec!["2","3"],vec!["3"],vec!["수량: 2"],vec!["수량: 21","수량: 3"],vec!["수량: 71","수량: 8","수량: 5","수량: 8"]];
    for (index,task) in lesson.tasks.iter().enumerate() {
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"Step {} starts unsolved",index+1);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed,"Step {} solution",index+1);
        let mut source=if task.has_runnable_example(){task.example_for_answer(&task.starter_code).unwrap()}else{task.starter_code.clone()};
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();let after=action["after"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"Step {} patch target",index+1);
                    source=source.replacen(before,after,1);
                },
                "order_answer"=>source=task.example_for_answer(&action["ids"].to_string()).unwrap(),
                "run"=>{
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual narration outputs",index+1);
        if index==8 {
            let hardcoded=task.solution.replace("(quantity + 1)","8");
            assert!(!lesson_runner::check(task,&hardcoded).await.unwrap().passed,"Memorized quantity must fail");
        }
    }
}
