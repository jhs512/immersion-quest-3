use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn valid_c_array_and_string_cases_match_each_teacher_run_and_varied_inputs() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/x/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/engineer-c-arrays.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),10);
    let expected=vec![vec!["2","4","2"],vec!["3\n2","2\n1","3\n2"],vec!["2\n4"],vec!["12","14","12"],
        vec!["12","6","12"],vec!["6","12"],vec!["0","12","0"],vec!["4\n3","6\n5","4\n3"],
        vec!["BOX","FOX","FAG","FOX"],vec!["6","12","0","12"]];
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
                    assert!(source.lines().nth(line-1).unwrap().contains("printf("));
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} narration must agree with actual output",index+1);
    }
    let challenge=&lesson.tasks[9];
    let fixed=challenge.solution.replace("printf(\"%d\", total)","printf(\"%d\", 12)");
    assert!(!lesson_runner::check(challenge,&fixed).await.unwrap().passed,"A memorized total must fail");
    let label=&lesson.tasks[8];
    let fixed=label.solution.replace("printf(\"%s\", label)","printf(\"%s\", \"FOX\")");
    assert!(!lesson_runner::check(label,&fixed).await.unwrap().passed,"The prepared label must actually change");
}
