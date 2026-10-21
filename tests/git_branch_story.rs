use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson,Task}};
fn play(practice:&GitPractice,task:&Task){
    for action in &task.narration {
        if action["action"]=="git_command" {
            let args=action["args"].as_array().unwrap().iter().map(|a|a.as_str().unwrap()).collect::<Vec<_>>();
            let result=practice.git(&args).unwrap();assert!(result.success,"{}: {args:?}: {}",task.title,result.stderr);
        }else if action["action"]=="bash_command" {
            let shell=if cfg!(windows){"C:/Program Files/Git/bin/bash.exe"}else{"/bin/bash"};
            let mut cmd=std::process::Command::new(shell);
            cmd.args(["-c",action["command"].as_str().unwrap()]).current_dir(practice.work()).envs(practice.environment());
            #[cfg(windows)] {use std::os::windows::process::CommandExt;cmd.creation_flags(0x08000000);}
            let result=cmd.output().unwrap();assert!(result.status.success(),"{}: {}",task.title,String::from_utf8_lossy(&result.stderr));
        }
    }
}
#[test]
fn imported_guide_and_two_features_are_one_real_continuous_repository(){
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/l/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/git-branch.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),13);
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let scope="guide-story";let mut prior=None;
    for (index,task) in lesson.tasks.iter().enumerate(){
        let exercise=task.git_terminal.clone().unwrap();
        assert!(exercise.files.is_empty()&&exercise.setup.is_empty(),"learner state was secretly prepared");
        let student=store.open(scope,exercise.clone()).unwrap();
        if let Some(path)=&prior{assert_eq!(student.root(),path,"step lost the learner repository");}
        student.remember_step_start(&task.id).unwrap();
        assert!(!student.check_exercise().unwrap().passed,"step {} started solved",index+1);
        let before=std::fs::read(student.work().join("guide.txt")).ok();
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();play(&teacher,task);
        assert!(teacher.check_exercise().unwrap().passed,"teacher step {}",index+1);
        assert_eq!(std::fs::read(student.work().join("guide.txt")).ok(),before,"teacher changed learner work");
        play(&student,task);assert!(student.check_exercise().unwrap().passed,"student step {}",index+1);
        if index==0{assert!(!student.root().join("inbox/guide.txt").exists(),"mv left the source file behind");}
        if index==6{assert_eq!(student.git(&["show","feature:guide.txt"]).unwrap().stdout,"안내: 메모 기능\n");}
        if index==11{assert_eq!(student.git(&["show","HEAD:guide.txt"]).unwrap().stdout,"안내: 메모 기능\n");}
        prior=Some(student.root().to_path_buf());
    }
    let last=store.open(scope,lesson.tasks.last().unwrap().git_terminal.clone().unwrap()).unwrap();
    assert_eq!(last.git(&["show","HEAD:guide.txt"]).unwrap().stdout,"안내: 메모 기능\n문의: 상담 창구\n");
    let graph=last.graph_snapshot().unwrap();assert_eq!(graph.commits.len(),3);
    for (index,task) in lesson.tasks.iter().enumerate(){
        let reset=store.reset_step(scope,task.git_terminal.clone().unwrap(),&task.id).unwrap();
        assert!(!reset.check_exercise().unwrap().passed,"reset solved step {}",index+1);
        play(&reset,task);assert!(reset.check_exercise().unwrap().passed,"reset step {} cannot be solved",index+1);
    }
}
