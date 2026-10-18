use molip_quest::{git_practice::GitPractice, repository_course::Lesson};

#[tokio::test]
async fn six_first_git_steps_grade_real_work_and_replay_teacher_commands_without_changing_student_state() {
    let path=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("courses/redesigned/git-first.json");
    let raw=std::fs::read_to_string(path).unwrap();
    let course=molip_quest::repository_course::CourseManifest::parse(include_str!("fixtures/player-pilot/k/course.json")).unwrap();
    let lesson=Lesson::parse(&raw,&course.lessons[0]).unwrap();
    lesson.validate().unwrap();
    assert_eq!(lesson.tasks.len(),6);
    let solutions:Vec<Vec<Vec<&str>>>=vec![
        vec![vec!["status"]],vec![vec!["add","--","memo.txt"]],vec![vec!["commit","-m","my first record"]],
        vec![],vec![],vec![vec!["add","memo.txt"],vec!["commit","-m","my updated record"]],
    ];
    for (index,task) in lesson.tasks.iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();
        let mut student=GitPractice::new(exercise.clone()).unwrap();
        for _ in 0..2 {
            let before=student.git(&["status","--porcelain"]).unwrap().stdout;
            if task.interaction.is_none() {assert!(!student.check_exercise().unwrap().passed,"step {} starts unsolved",index+1);}
            let teacher=GitPractice::new(exercise.clone()).unwrap();
            for action in &task.narration {
                if action["action"]=="git_command" {
                    let args:Vec<&str>=action["args"].as_array().unwrap().iter().map(|s|s.as_str().unwrap()).collect();
                    let result=teacher.git(&args).unwrap();assert!(result.success,"step {}: {:?}: {}",index+1,args,result.stderr);
                }
            }
            if let Some(interaction)=&task.interaction {
                assert!(!interaction.check("").unwrap().passed);
                assert!(molip_quest::lesson_runner::check(task,&task.solution).await.unwrap().passed);
                if index==3 {assert_eq!(teacher.git(&["show","HEAD:memo.txt"]).unwrap().stdout,"첫 메모\n");}
                if index==4 {assert_eq!(teacher.git(&["show","HEAD:memo.txt"]).unwrap().stdout,"둘째 메모\n");}
            } else {assert!(teacher.check_exercise().unwrap().passed,"teacher did not demonstrate step {}",index+1);}
            assert_eq!(student.git(&["status","--porcelain"]).unwrap().stdout,before,"teacher changed student state");
            for args in &solutions[index] {assert!(student.git(args).unwrap().success);}
            if task.interaction.is_none() {assert!(student.check_exercise().unwrap().passed,"student step {}",index+1);}
            std::fs::write(student.work().join("leftover.txt"),"remove on reset").unwrap();
            student.reset().unwrap();
            assert!(!student.work().join("leftover.txt").exists());
        }
    }
}
