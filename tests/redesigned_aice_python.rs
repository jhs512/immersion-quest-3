use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn seven_python_first_steps_match_real_outputs_and_keep_answers_separate() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/o/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/aice-python-start.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),8); // 7 teaching steps + the appended final challenge (92b37e2a)
    let expected:Vec<Vec<&str>>=vec![vec!["12"],vec!["12","18"],vec!["18","minutes","18"],vec!["18","24"],vec!["[12, 18, 24]","12","[12, 18, 24]"],vec!["12\n18","9\n30"],vec!["12\n4","12\n9","12\n4"]];
    // The teacher-run table covers the teaching steps; the appended final challenge is graded against
    // equivalent and wrong answers in docs/curriculum/final-challenges-evidence.md.
    for (index,task) in lesson.tasks[..lesson.tasks.len()-1].iter().enumerate() {
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
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().contains("print"),"Highlight must name an actual output statement");
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual narration outputs",index+1);
    }
}
