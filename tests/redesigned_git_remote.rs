use molip_quest::{git_practice::GitPractice, repository_course::{CourseManifest,Lesson}};

fn grade(practice:&GitPractice,task:&molip_quest::repository_course::Task)->bool {
    if let Some(checks)=&task.git_checks{practice.check(checks).unwrap().passed}else{practice.check_exercise().unwrap().passed}
}
#[tokio::test]
async fn eight_remote_steps_grade_actual_git_state_and_preserve_student_work_during_explanations() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/어/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/git-remote.json"),&course.lessons[0]).unwrap();
    let commands:serde_json::Value=serde_json::from_str(include_str!("fixtures/player-pilot/어/student-commands.json")).unwrap();
    assert_eq!(lesson.tasks.len(),8);
    for (index,task) in lesson.tasks.iter().enumerate(){
        let exercise=task.git_terminal.clone().unwrap();
        let mut student=GitPractice::new(exercise.clone()).unwrap();
        for _ in 0..2 {
            let before=student.git(&["show","HEAD:guide.txt"]).unwrap().stdout;
            let teacher=GitPractice::new(exercise.demonstration()).unwrap();
            for action in &task.narration {
                if action["action"]=="git_command" {
                    let args=action["args"].as_array().unwrap().iter().map(|a|a.as_str().unwrap()).collect::<Vec<_>>();
                    assert!(teacher.git(&args).unwrap().success,"teacher step {}: {args:?}",index+1);
                }
            }
            assert_eq!(student.git(&["show","HEAD:guide.txt"]).unwrap().stdout,before);
            if task.interaction.is_some(){
                assert!(molip_quest::lesson_runner::check(task,&task.solution).await.unwrap().passed);
                assert!(!molip_quest::lesson_runner::check(task,"").await.unwrap().passed);
            }else{
                assert!(!grade(&student,task),"step {} must start unsolved",index+1);
                assert!(grade(&teacher,task),"teacher step {}",index+1);
                for args in commands["student_commands"][index].as_array().unwrap(){
                    let args=args.as_array().unwrap().iter().map(|a|a.as_str().unwrap()).collect::<Vec<_>>();
                    assert!(student.git(&args).unwrap().success,"student step {}: {args:?}",index+1);
                }
                assert!(grade(&student,task),"student step {}",index+1);
            }
            student.reset().unwrap();
        }
    }
}
