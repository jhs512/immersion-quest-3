use molip_quest::{git_practice::{GitPractice,GitPracticeStore}, repository_course::{CourseManifest,Lesson,Task}};
fn play(practice:&GitPractice,task:&Task){
    let mut lines=vec!["set -e".to_string()];
    for a in &task.narration {
        if a["action"]=="git_command" {lines.push(format!("git {}",a["args"].as_array().unwrap().iter().map(|v|format!("'{}'",v.as_str().unwrap().replace('\\',"/"))).collect::<Vec<_>>().join(" ")));}
        else if a["action"]=="bash_command" {let cmd=a["command"].as_str().unwrap();lines.push(if a["expected_exit"]==1 {format!("{cmd} && exit 99; test $? -eq 1")}else{cmd.into()});}
    }
    let shell=if cfg!(windows){"C:/Program Files/Git/bin/bash.exe"}else{"/bin/bash"};
    let mut command=std::process::Command::new(shell);
    command.args(["-c",&lines.join("\n")]).current_dir(practice.work()).envs(practice.environment());
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
    let output=command.output().unwrap();assert!(output.status.success(),"{}: {}",task.title,String::from_utf8_lossy(&output.stderr));
}
fn grade(p:&GitPractice,t:&Task)->bool{if let Some(checks)=&t.git_checks{p.check(checks).unwrap().passed}else{p.check_exercise().unwrap().passed}}
#[tokio::test]
async fn remote_team_story_uses_real_learner_edits_and_independent_resettable_demonstrations(){
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/어/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/git-remote.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),21);
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    for (i,t) in lesson.tasks.iter().enumerate(){
        let exercise=t.git_terminal.clone().unwrap();assert!(exercise.setup.is_empty()&&exercise.files.is_empty());
        let student=store.open("team",exercise.clone()).unwrap();
        let before=std::fs::read(student.work().join("guide.txt")).ok();
        if t.interaction.is_none(){assert!(!grade(&student,t),"step {} started solved",i+1);}
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();play(&teacher,t);
        assert!(t.interaction.is_some()||grade(&teacher,t),"teacher step {}: {:?}",i+1,serde_json::to_string(&teacher.check_exercise().unwrap()).unwrap());
        assert_eq!(std::fs::read(student.work().join("guide.txt")).ok(),before);
        play(&student,t);assert!(t.interaction.is_some()||grade(&student,t),"student step {}: {:?}",i+1,serde_json::to_string(&student.check_exercise().unwrap()).unwrap());
        if t.interaction.is_some(){assert!(molip_quest::lesson_runner::check(t,&t.solution).await.unwrap().passed);assert!(!molip_quest::lesson_runner::check(t,"").await.unwrap().passed);}
    }
    for (i,t) in lesson.tasks.iter().enumerate(){
        let reset=store.reset_step("team",t.git_terminal.clone().unwrap(),&t.id).unwrap();
        if t.interaction.is_none(){assert!(!grade(&reset,t),"reset solved step {}",i+1);}
        play(&reset,t);assert!(t.interaction.is_some()||grade(&reset,t),"reset step {}",i+1);
    }
}

#[test]
fn local_remote_connection_requires_an_existing_correct_destination(){
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/git-remote.json")).unwrap();
    let first=&lesson.tasks[0];let p=GitPractice::new(first.git_terminal.clone().unwrap()).unwrap();play(&p,first);assert!(grade(&p,first));
    let remote=p.root().join("remote.git");let moved=p.root().join("moved-remote.git");std::fs::rename(&remote,&moved).unwrap();assert!(!grade(&p,first),"missing local remote accepted");std::fs::rename(&moved,&remote).unwrap();
    assert!(p.git(&["remote","set-url","origin","../wrong.git"]).unwrap().success);assert!(!grade(&p,first),"wrong origin accepted");
    let absolute=p.root().join("remote.git");assert!(p.git(&["remote","set-url","origin",absolute.to_str().unwrap()]).unwrap().success);assert!(grade(&p,first),"equivalent absolute path rejected");
    assert!(p.git(&["remote","remove","origin"]).unwrap().success);assert!(!grade(&p,first),"missing origin accepted");
}
