use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson}};
fn lesson()->Lesson {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/풀/course.json")).unwrap();
    Lesson::parse(include_str!("../courses/redesigned/github-pr.json"),&course.lessons[0]).unwrap()
}
#[test]
fn opening_or_explaining_pr_practice_does_not_create_a_hosted_repository(){
    let lesson=lesson();assert_eq!(lesson.tasks.len(),8);
    let student=GitPractice::new(lesson.tasks[0].git_terminal.clone().unwrap()).unwrap();
    assert!(!student.root().join("remote.git").exists());
    assert!(!student.git(&["remote","get-url","origin"]).unwrap().success);
    assert_eq!(student.git(&["show","HEAD:memo.txt"]).unwrap().stdout,"기본 메모\n");
    assert!(student.github_repository_name().starts_with("mq3-pr-"));
    let environment=student.environment();
    assert!(environment.iter().any(|(k,v)|k=="GIT_ALLOW_PROTOCOL"&&v=="https"));
    assert!(environment.iter().any(|(k,_)|k=="GH_CONFIG_DIR"));
    for task in lesson.tasks {
        assert!(task.narration.iter().all(|a|a["action"]=="say"),"explanation must not run GitHub writes");
        let teacher=GitPractice::new(task.git_terminal.unwrap().demonstration()).unwrap();
        assert!(teacher.check_exercise().err().unwrap().contains("자동으로 변경하지"));
        assert!(teacher.environment().iter().any(|(k,v)|k=="GIT_ALLOW_PROTOCOL"&&v=="file"));
    }
}
#[test]
fn local_git_practice_keeps_its_local_remote_and_protocol(){
    let practice=GitPractice::new(Default::default()).unwrap();
    assert!(practice.root().join("remote.git").is_dir());
    assert!(practice.environment().iter().any(|(k,v)|k=="GIT_ALLOW_PROTOCOL"&&v=="file"));
    assert!(!practice.environment().iter().any(|(k,_)|k=="GH_CONFIG_DIR"));
}

#[tokio::test]
#[ignore="Creates a real private repository and PR with the current gh account; leaves both for manual cleanup"]
async fn real_github_pr_lifecycle_uses_the_actual_practice_terminal_and_grader(){
    use std::time::Duration;
    let lesson=lesson();let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let mut repository_name=String::new();
    let owner=molip_quest::github_player::Github::new().user().unwrap().login;
    for (index,task) in lesson.tasks.iter().enumerate(){
        let practice=store.open("github-pr-authorized-verification",task.git_terminal.clone().unwrap()).unwrap();
        if index==0 {repository_name=practice.github_repository_name();assert!(practice.check_exercise().is_err());}
        let (mut terminal,mut output)=practice.open_terminal().unwrap();
        let mut buffer=String::new();
        let mut dsr=0;
        tokio::time::timeout(Duration::from_secs(30),async {
            while !buffer.contains("$ "){
                buffer.push_str(&String::from_utf8_lossy(&output.recv().await.unwrap()));
                let count=buffer.matches("\x1b[6n").count();if count>dsr{terminal.input("\x1b[1;1R").unwrap();dsr=count;}
            }
        }).await.unwrap_or_else(|_|panic!("terminal startup timed out: {buffer:?}"));
        let commands=task.solution.lines().filter(|line|!line.trim().is_empty()&&!line.starts_with('#')).collect::<Vec<_>>();
        for command in commands {
            terminal.input(&(command.to_owned()+"\r")).unwrap();
            let result=tokio::time::timeout(Duration::from_secs(120),async {
                loop {
                    if let Some(last)=practice.shell_completions().unwrap().last(){if last.command.trim()==command {break last.success}}
                    if let Ok(Some(bytes))=tokio::time::timeout(Duration::from_millis(100),output.recv()).await{buffer.push_str(&String::from_utf8_lossy(&bytes));let count=buffer.matches("\x1b[6n").count();if count>dsr{terminal.input("\x1b[1;1R").unwrap();dsr=count;}}
                }
            }).await.expect("real GitHub command timed out");
            assert!(result,"stage {} command {} failed: {}",index+1,command,buffer);
        }
        let report=practice.check_exercise().unwrap();assert!(report.passed,"stage {}: {}",index+1,serde_json::to_string(&report.cases).unwrap());
        eprintln!("real GitHub stage {} passed",index+1);
        if index==0{eprintln!("Repository retained: https://github.com/{owner}/{repository_name}");}
        if index==5{eprintln!("PR created: https://github.com/{owner}/{repository_name}/pull/1");}
        // Closing and reopening the actual PTY must preserve the same local and hosted workspace.
        terminal.shutdown().unwrap();
    }
    let url=format!("https://github.com/{owner}/{repository_name}/pull/1");
    std::fs::create_dir_all("target").unwrap();
    std::fs::write("target/github-pr-live-result.json",serde_json::json!({"passed":true,"stages":8,"repository":format!("{owner}/{repository_name}"),"pull_request":url,"automatic_deletion":false}).to_string()).unwrap();
    eprintln!("Real PR verified and retained for manual cleanup: {url}");
}
