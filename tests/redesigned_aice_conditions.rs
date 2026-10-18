use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn eight_condition_steps_match_boundary_values_and_teacher_outputs() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/p/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/aice-python-conditions.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),8);
    let expected:Vec<Vec<&str>>=vec![vec!["True"],vec!["False\nFalse","True\nTrue","True\nFalse","True\nTrue"],vec!["True","False"],vec!["지연","정상"],vec!["12\n30\n42","[12, 30, 42]","12\n30\n42"],vec!["42","30\n42"],vec!["[30, 42]","[42]","[30, 42]"],vec!["2","1","2","1"]];
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
                "run"=>{
                    let line=source.lines().nth(action["lines"][0].as_u64().unwrap() as usize-1).unwrap().trim();
                    assert!(line.starts_with("print(")||line.starts_with("if "),"Highlight names an actual output or decision statement");
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual narration outputs",index+1);
    }
    for (index,wrong) in [(2,"minutes = 24\nprint(False)\n"),(5,"minutes = [12, 30, 42]\nprint('30\\n42')\n"),(7,"minutes = [12, 30, 42]\nprint(1)\n")] {
        assert!(!lesson_runner::check(&lesson.tasks[index],wrong).await.unwrap().passed,"Step {} must reject memorized output",index+1);
    }
    let early_exit="minutes = 24\nraise SystemExit(0)\n";
    assert!(!lesson_runner::check(&lesson.tasks[2],early_exit).await.unwrap().passed,"Successful early exit is not a completed checker");
}
