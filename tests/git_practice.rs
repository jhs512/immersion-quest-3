use molip_quest::git_practice::{GitExercise,GitPractice};
#[test]
fn reset_recreates_repository_remote_and_config_without_touching_other_practices() {
    let mut first=GitPractice::new(GitExercise::default()).unwrap();
    let second=GitPractice::new(GitExercise::default()).unwrap();
    let first_root=first.root().to_owned();let second_root=second.root().to_owned();
    let outside=tempfile::tempdir().unwrap();let marker=outside.path().join("keep.txt");std::fs::write(&marker,"untouched").unwrap();
    let baseline=first.git(&["rev-parse","HEAD"]).unwrap();
    std::fs::write(first.work().join("tracked.txt"),"staged").unwrap();first.git(&["add","tracked.txt"]).unwrap();
    std::fs::write(first.work().join("tracked.txt"),"unstaged").unwrap();std::fs::write(first.work().join("untracked.txt"),"new").unwrap();
    first.git(&["switch","-c","changed"]).unwrap();first.git(&["add","."]).unwrap();first.git(&["commit","-m","changed"]).unwrap();
    first.git(&["push","origin","HEAD:main"]).unwrap();
    first.git(&["config","--global","user.name","practice only"]).unwrap();
    first.reset().unwrap();
    assert_ne!(first.root(),first_root);assert!(!first_root.exists());
    assert_eq!(first.git(&["rev-parse","HEAD"]).unwrap().stdout,baseline.stdout);
    assert!(first.git(&["status","--porcelain"]).unwrap().stdout.is_empty());
    assert_eq!(first.git(&["branch","--show-current"]).unwrap().stdout.trim(),"main");
    assert_eq!(first.git(&["ls-remote","origin","refs/heads/main"]).unwrap().stdout.split_whitespace().next(),baseline.stdout.split_whitespace().next());
    assert!(first.git(&["config","--global","--get","user.name"]).unwrap().stdout.is_empty());
    assert!(second_root.exists());assert_eq!(std::fs::read_to_string(marker).unwrap(),"untouched");
}

#[test]
fn conflict_and_in_progress_operations_are_removed_on_every_reset() {
    for operation in ["merge","rebase","cherry-pick"] {
        let mut practice=GitPractice::new(GitExercise::default()).unwrap();
        let original=practice.git(&["rev-parse","HEAD"]).unwrap().stdout;
        practice.git(&["switch","-c","side"]).unwrap();std::fs::write(practice.work().join("tracked.txt"),"side\n").unwrap();
        practice.git(&["commit","-am","side"]).unwrap();let side=practice.git(&["rev-parse","HEAD"]).unwrap().stdout;
        practice.git(&["switch","main"]).unwrap();std::fs::write(practice.work().join("tracked.txt"),"main\n").unwrap();practice.git(&["commit","-am","main"]).unwrap();
        let conflict=practice.git(&[operation,if operation=="cherry-pick"{side.trim()}else{"side"}]).unwrap();
        assert!(!conflict.success,"{operation} must reach the intended conflict");
        assert!(practice.git(&["status","--porcelain"]).unwrap().stdout.contains("UU tracked.txt"));
        practice.reset().unwrap();
        assert_eq!(practice.git(&["rev-parse","HEAD"]).unwrap().stdout,original);
        assert!(practice.git(&["status","--porcelain"]).unwrap().stdout.is_empty());
        assert_eq!(practice.git(&["branch","--list"]).unwrap().stdout.trim(),"* main");
        practice.reset().unwrap();assert_eq!(practice.git(&["rev-parse","HEAD"]).unwrap().stdout,original);
    }
}
#[test]
fn command_goal_requires_a_successfully_executed_real_git_command() {
    let exercise=GitExercise{commands:vec![vec!["status".into(),"--short".into()]],..Default::default()};
    let mut practice=GitPractice::new(exercise).unwrap();
    assert!(!practice.commands_satisfied().unwrap());
    assert!(!practice.git(&["status","--not-a-real-option"]).unwrap().success);
    assert!(!practice.commands_satisfied().unwrap());
    assert!(practice.git(&["status","--short"]).unwrap().success);
    assert!(practice.commands_satisfied().unwrap());
    practice.reset().unwrap();assert!(!practice.commands_satisfied().unwrap());
}

#[test]
fn real_platform_shell_runs_git_and_grading_does_not_satisfy_command_goals() {
    use molip_quest::repository_course::GitChecks;
    let practice=GitPractice::new(GitExercise{commands:vec![vec!["status".into(),"--porcelain".into()]],..Default::default()}).unwrap();
    let checks=GitChecks{minimum_commits:1,head_message:"Start".into(),tracked_files:Default::default(),branch:Some("main".into()),pushed:true};
    assert!(!practice.check(&checks).unwrap().passed);
    let (mut shell,mut output)=practice.open_terminal().unwrap();
    let mut seen=String::new();let mut cursor_reports=0usize;let mut sent=false;
    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(30);
    while std::time::Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){seen.push_str(&String::from_utf8_lossy(&bytes));let reports=seen.matches("\x1b[6n").count();while cursor_reports<reports{shell.input("\x1b[1;1R").unwrap();cursor_reports+=1;}}
        if !sent&&(!cfg!(windows)||seen.contains("> ")){shell.input("git status --porcelain\r").unwrap();sent=true;}
        if sent&&practice.commands_satisfied().unwrap(){break;}
        std::thread::sleep(std::time::Duration::from_millis(30));
    }
    assert!(practice.check(&checks).unwrap().passed,"shell must execute real git, got {seen}");
    shell.shutdown().unwrap();
}

#[test]
fn a_command_only_goal_does_not_require_an_unrelated_clean_worktree() {
    let practice=GitPractice::new(GitExercise{commands:vec![vec!["status".into(),"--short".into()]],..Default::default()}).unwrap();
    std::fs::write(practice.work().join("new.txt"),"new").unwrap();
    assert!(!practice.check_commands().unwrap().passed);
    practice.git(&["status","--short"]).unwrap();
    assert!(practice.check_commands().unwrap().passed);
}

#[test]
fn published_git_steps_can_choose_command_only_state_only_or_both() {
    let mut raw:serde_json::Value=serde_json::from_str(include_str!("fixtures/player-pilot/h/lesson.json")).unwrap();
    let both:molip_quest::repository_course::Lesson=serde_json::from_value(raw.clone()).unwrap();assert!(both.validate().is_ok());
    raw["tasks"][0].as_object_mut().unwrap().remove("git_checks");
    let command_only:molip_quest::repository_course::Lesson=serde_json::from_value(raw.clone()).unwrap();assert!(command_only.validate().is_ok());
    raw["tasks"][0]["git_terminal"]["commands"]=serde_json::json!([]);
    let no_goal:molip_quest::repository_course::Lesson=serde_json::from_value(raw).unwrap();assert!(no_goal.validate().is_err());
    let mut raw:serde_json::Value=serde_json::from_str(include_str!("fixtures/player-pilot/h/lesson.json")).unwrap();raw["tasks"][0]["git_terminal"]["commands"]=serde_json::json!([]);
    let state_only:molip_quest::repository_course::Lesson=serde_json::from_value(raw).unwrap();assert!(state_only.validate().is_ok());
}

#[test]
fn closing_practice_stops_its_background_child_but_keeps_an_outside_process() {
    use std::process::{Command,Stdio};
    #[cfg(windows)] use std::os::windows::process::CommandExt;
    let outside=tempfile::tempdir().unwrap();let ready=outside.path().join("owned-ready");let leaked=outside.path().join("owned-leaked");let safe=outside.path().join("outside-alive");
    let extension=if cfg!(windows){"ps1"}else{"sh"};let owned_script=outside.path().join(format!("owned.{extension}"));let safe_script=outside.path().join(format!("outside.{extension}"));
    let script=|started:Option<&std::path::Path>,output:&std::path::Path|{
        if cfg!(windows) {format!("{}Start-Sleep -Seconds 3;Set-Content -LiteralPath '{}' alive",started.map(|path|format!("Set-Content -LiteralPath '{}' ready;",path.display())).unwrap_or_default(),output.display())}
        else {format!("{}sleep 3;printf alive > '{}'",started.map(|path|format!("printf ready > '{}';",path.display())).unwrap_or_default(),output.display())}
    };
    std::fs::write(&owned_script,script(Some(&ready),&leaked)).unwrap();std::fs::write(&safe_script,script(None,&safe)).unwrap();
    let mut external=Command::new(if cfg!(windows){"powershell.exe"}else{"/bin/sh"});
    if cfg!(windows){external.args(["-NoProfile","-File"]);}
    external.arg(&safe_script).stdout(Stdio::null()).stderr(Stdio::null());
    #[cfg(windows)] external.creation_flags(0x08000000);
    let mut external=external.spawn().unwrap();
    let practice=GitPractice::new(GitExercise::default()).unwrap();let (mut shell,mut output)=practice.open_terminal().unwrap();
    // The minimal VT responder does not model wrapped cursor positions.
    // Keep the full prompt and absolute script command inside one PTY line.
    shell.resize(20, 512).unwrap();
    let command=if cfg!(windows){format!("Start-Process powershell.exe -WindowStyle Hidden -ArgumentList '-NoProfile','-File','\"{}\"'\r",owned_script.display())}else{format!("nohup /bin/sh '{}' >/dev/null 2>&1 &\r",owned_script.display())};
    let mut seen=String::new();let mut cursor_reports=0usize;let mut sent=false;let deadline=std::time::Instant::now()+std::time::Duration::from_secs(30);
    while std::time::Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){seen.push_str(&String::from_utf8_lossy(&bytes));let reports=seen.matches("\x1b[6n").count();while cursor_reports<reports{shell.input("\x1b[1;1R").unwrap();cursor_reports+=1;}}
        if !sent&&(!cfg!(windows)||seen.contains("> ")){shell.input(&command).unwrap();sent=true;}
        if ready.exists(){break;}std::thread::sleep(std::time::Duration::from_millis(30));
    }
    assert!(ready.exists(),"background process must actually start: {seen}");
    shell.shutdown().unwrap();drop(shell);drop(practice);
    assert!(external.wait().unwrap().success());
    std::thread::sleep(std::time::Duration::from_secs(1));
    assert!(safe.exists(),"unrelated external process must remain alive");
    assert!(!leaked.exists(),"owned background process survived terminal shutdown");
}

#[test]
fn tracked_file_goals_preserve_significant_trailing_bytes() {
    let practice=GitPractice::new(GitExercise::default()).unwrap();
    let checks=molip_quest::repository_course::GitChecks{minimum_commits:1,head_message:"Start".into(),tracked_files:std::collections::BTreeMap::from([("tracked.txt".into(),"initial\n".into())]),branch:Some("main".into()),pushed:false};
    assert!(practice.check(&checks).unwrap().passed);
    std::fs::write(practice.work().join("tracked.txt"),"initial").unwrap();practice.git(&["commit","-am","Start"]).unwrap();
    assert!(!practice.check(&checks).unwrap().passed);
}
