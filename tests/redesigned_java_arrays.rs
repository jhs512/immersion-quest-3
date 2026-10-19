use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn array_positions_repetition_and_empty_data_match_the_actual_teacher_runs() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/w/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/java-arrays.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),8);
    let expected=vec![vec!["1000","2000","1000"],vec!["3000","1000","3000"],vec!["3\n2","2\n1","3\n2"],vec!["1000\n2000"],
        vec!["6000","8000","6000"],vec!["6000","3000","6000"],vec!["5000","3000","5000"],vec!["3000","6000","0","6000"]];
    for (index,task) in lesson.tasks.iter().enumerate() {
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"Step {} starts unsolved",index+1);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed,"Step {} solution",index+1);
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"Step {} patch must be unique",index+1);
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().contains("System.out.println"));
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} narration must agree with actual output",index+1);
    }
    let challenge=&lesson.tasks[7];
    let fixed=challenge.solution.replace("System.out.println(total)","System.out.println(6000)");
    assert!(!lesson_runner::check(challenge,&fixed).await.unwrap().passed,"A memorized total must fail");
}
