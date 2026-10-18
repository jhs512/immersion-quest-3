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
    let mut seen=String::new();let mut sent=false;
    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(15);
    while std::time::Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){let chunk=String::from_utf8_lossy(&bytes);if chunk.contains("\x1b[6n"){shell.input("\x1b[1;1R").unwrap();}seen.push_str(&chunk);}
        if !sent&&(!cfg!(windows)||seen.contains("PS ")){shell.input("git status --porcelain\r").unwrap();sent=true;}
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
