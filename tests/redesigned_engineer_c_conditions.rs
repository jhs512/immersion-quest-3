use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn integer_packing_boundaries_and_every_teacher_run_match_c_output() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/u/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/engineer-c-conditions.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),8);
    let expected=vec![vec!["2","1","2","2"],vec!["1","2","0","1"],vec!["1\n3","0\n2","1\n4","1\n3"],vec!["0","1","0"],vec!["0","2","0"],vec!["0","1","2","1"],vec!["1","0","1"],vec!["2\n2","2\n0"]];
    for (index,task) in lesson.tasks.iter().enumerate() {
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"Step {} starts unsolved",index+1);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed,"Step {} solution",index+1);
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"Step {} patch must select exactly one region",index+1);
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().contains("printf("));
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher failed: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual teacher results",index+1);
    }
    let challenge=&lesson.tasks[5];
    let constant=challenge.solution.replace("printf(\"%d\", packs)","printf(\"%d\", 1)");
    assert!(!lesson_runner::check(challenge,&constant).await.unwrap().passed,"A memorized result must fail");
    let fixed_threshold=challenge.solution.replace("stock >= group","stock >= 3");
    assert!(!lesson_runner::check(challenge,&fixed_threshold).await.unwrap().passed,"Other group sizes must still work");
}
