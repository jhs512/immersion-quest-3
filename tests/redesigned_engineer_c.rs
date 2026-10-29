use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn c_reading_steps_compile_prepared_code_and_grade_the_separate_output_answer() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/r/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/engineer-c-start.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),7); // 6 teaching steps + the appended final challenge (92b37e2a)
    let expected:Vec<Vec<&str>>=vec![vec!["2"],vec!["2","5","2"],vec!["2","5"],
        vec!["5 2","9 2","5 2"],vec!["2 3","5 3"],vec!["5 3","5 6"]];
    // The teacher-run table covers the teaching steps; the appended final challenge is graded against
    // equivalent and wrong answers in docs/curriculum/final-challenges-evidence.md.
    for (index,task) in lesson.tasks[..lesson.tasks.len()-1].iter().enumerate() {
        assert!(task.has_runnable_example());
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed);
        let mut source=task.example_code.clone().unwrap();
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"Step {} patch",index+1);
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().contains("printf("));
                    let result=lesson_runner::run_example(task,&source,"").await.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual C outputs",index+1);
        assert!(lesson_runner::run(task,&task.solution,"").await.is_err(),"Output answers are never compiled as C source");
    }
    for (initial,updated,before,after) in [(2,5,"5 3","5 6"),(4,9,"9 5","9 10"),(7,3,"3 8","3 4")] {
        for (index,expected) in [(4,before),(5,after)] {
            let task=&lesson.tasks[index];
            let source=task.example_code.as_ref().unwrap().replace("int stock = 2;",&format!("int stock = {initial};")).replace("stock = 5;",&format!("stock = {updated};"));
            let result=lesson_runner::run_example(task,&source,"").await.unwrap();
            assert!(result.success,"{}",result.stderr);
            assert_eq!(result.stdout.trim(),expected,"The assignment order must work for other initial values");
        }
    }
    assert!(!lesson_runner::check(&lesson.tasks[4],"5 6").await.unwrap().passed);
    assert!(!lesson_runner::check(&lesson.tasks[4],"2 3").await.unwrap().passed);
    assert!(!lesson_runner::check(&lesson.tasks[5],"5 3").await.unwrap().passed);
}
