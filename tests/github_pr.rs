use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson}};
fn lesson()->Lesson {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/풀/course.json")).unwrap();
    Lesson::parse(include_str!("../courses/redesigned/github-pr.json"),&course.lessons[0]).unwrap()
}
#[test]
fn opening_or_explaining_pr_practice_does_not_create_a_hosted_repository(){
    let lesson=lesson();assert_eq!(lesson.tasks.len(),9);// The last step is the separately started final challenge (tests/final_terminal_challenges.rs).
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
#[cfg(target_os="macos")]
fn pr_terminal_preserves_the_keychain_home_while_git_config_stays_isolated(){
    let lesson=lesson();let practice=GitPractice::new(lesson.tasks[0].git_terminal.clone().unwrap()).unwrap();
    let environment=practice.environment().into_iter().collect::<std::collections::BTreeMap<_,_>>();
    assert_eq!(environment["HOME"],std::env::var("HOME").unwrap());
    assert_eq!(environment["GIT_CONFIG_GLOBAL"],practice.root().join("global.config").to_string_lossy());
    assert_eq!(environment["GIT_CONFIG_NOSYSTEM"],"1");
    assert_ne!(environment["XDG_CONFIG_HOME"],std::env::var("HOME").unwrap());
}

#[test]
fn local_git_practice_keeps_its_local_remote_and_protocol(){
    let practice=GitPractice::new(Default::default()).unwrap();
    assert!(practice.root().join("remote.git").is_dir());
    assert!(practice.environment().iter().any(|(k,v)|k=="GIT_ALLOW_PROTOCOL"&&v=="file"));
    assert!(!practice.environment().iter().any(|(k,_)|k=="GH_CONFIG_DIR"));
}

#[test]
#[ignore="Reads the current GitHub login through a real practice PTY; does not create or change repositories"]
fn current_github_login_is_shared_with_the_practice_terminal(){
    use std::time::{Duration,Instant};
    let expected=molip_quest::github_player::Github::new().user().unwrap().login;
    let practice=GitPractice::new(lesson().tasks[0].git_terminal.clone().unwrap()).unwrap();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    let mut text=String::new();let mut sent=false;let mut dsr=0;
    let deadline=Instant::now()+Duration::from_secs(30);
    while Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let count=text.matches("\x1b[6n").count();while dsr<count{terminal.input("\x1b[1;1R").unwrap();dsr+=1;}
        if !sent&&text.contains("$ "){terminal.input("gh api user --jq .login\r").unwrap();sent=true;}
        if sent&&practice.shell_completions().unwrap().iter().any(|c|c.command=="gh api user --jq .login"&&c.success){break;}
        std::thread::sleep(Duration::from_millis(25));
    }
    terminal.shutdown().unwrap();
    assert!(practice.shell_completions().unwrap().iter().any(|c|c.command=="gh api user --jq .login"&&c.success),"practice terminal cannot use the player's existing login: {text:?}; commands: {:?}",practice.shell_completions().unwrap());
    assert!(text.contains(&expected),"practice must return the same GitHub account as the player");
}

#[tokio::test]
#[ignore="Creates a real private repository and PR with the current gh account; leaves both for manual cleanup"]
async fn real_github_pr_lifecycle_uses_the_actual_practice_terminal_and_grader(){
    use std::time::Duration;
    let lesson=lesson();let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let mut repository_name=String::new();
    let owner=molip_quest::github_player::Github::new().user().unwrap().login;
    for (index,task) in lesson.tasks[..8].iter().enumerate(){
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

#[tokio::test]
#[ignore="Creates one real private repository and PR with the current gh account for the final challenge; leaves both for manual cleanup"]
async fn real_github_final_challenge_passes_only_after_merge_and_pull(){
    use std::time::Duration;
    use sha2::{Digest,Sha256};
    let lesson=lesson();let task=lesson.tasks.last().unwrap().clone();
    assert!(task.git_terminal.as_ref().unwrap().workspace_group.is_empty(),"the challenge starts its own round");
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let practice=store.open("github-pr-final-challenge",task.git_terminal.clone().unwrap()).unwrap();
    assert!(practice.check_exercise().is_err()||!practice.check_exercise().unwrap().passed,"start state must not pass");
    let owner=molip_quest::github_player::Github::new().user().unwrap().login;let repository=practice.github_repository_name();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    let mut buffer=String::new();let mut dsr=0;
    tokio::time::timeout(Duration::from_secs(30),async {
        while !buffer.contains("$ "){
            buffer.push_str(&String::from_utf8_lossy(&output.recv().await.unwrap()));
            let count=buffer.matches("\x1b[6n").count();if count>dsr{terminal.input("\x1b[1;1R").unwrap();dsr=count;}
        }
    }).await.unwrap();
    let mut observations=vec![];
    for command in task.solution.lines().filter(|line|!line.trim().is_empty()&&!line.starts_with('#')) {
        terminal.input(&(command.to_owned()+"\r")).unwrap();
        let ok=tokio::time::timeout(Duration::from_secs(120),async {
            loop {
                if let Some(last)=practice.shell_completions().unwrap().last(){if last.command.trim()==command {break last.success}}
                if let Ok(Some(bytes))=tokio::time::timeout(Duration::from_millis(100),output.recv()).await{buffer.push_str(&String::from_utf8_lossy(&bytes));let count=buffer.matches("\x1b[6n").count();if count>dsr{terminal.input("\x1b[1;1R").unwrap();dsr=count;}}
            }
        }).await.expect("real GitHub command timed out");
        assert!(ok,"challenge command {command} failed: {buffer}");
        // Grade at the moments a learner could stop too early: PR open, merged but not pulled.
        if command.starts_with("gh pr create")||command.starts_with("gh pr merge")||command=="git switch main" {
            let report=practice.check_exercise().unwrap();
            assert!(!report.passed,"stopping after {command} must not pass");
            observations.push(serde_json::json!({"after":command,"passed":false,"failed":report.cases.iter().filter(|c|!c.passed).map(|c|c.input.clone()).collect::<Vec<_>>()}));
        }
    }
    let report=practice.check_exercise().unwrap();
    assert!(report.passed,"final: {}",serde_json::to_string(&report.cases).unwrap());
    terminal.shutdown().unwrap();
    let raw=std::fs::read(concat!(env!("CARGO_MANIFEST_DIR"),"/courses/redesigned/github-pr.json")).unwrap();
    std::fs::create_dir_all(concat!(env!("CARGO_MANIFEST_DIR"),"/target/final-challenges")).unwrap();
    std::fs::write(concat!(env!("CARGO_MANIFEST_DIR"),"/target/final-challenges/github-pr.json"),serde_json::to_vec_pretty(&serde_json::json!({
        "passed":true,"lesson":lesson.id,"revision":lesson.revision,"lesson_sha256":format!("{:x}",Sha256::digest(&raw)),"challenge_task":task.id,
        "runtime":"real GitHub (gh) + git + bash","start_state_fails":true,"early_stops_rejected":observations,
        "repository":format!("{owner}/{repository}"),"automatic_deletion":false,"native_ui_verified":false,"voice_listened":false})).unwrap()).unwrap();
    eprintln!("Final challenge verified; repository retained for manual cleanup: https://github.com/{owner}/{repository}");
}
