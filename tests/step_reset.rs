use molip_quest::{git_practice::{GitPracticeStore,GitExercise},repository_course::Lesson};
use std::{path::Path,time::{Duration,Instant}};
fn lesson(source:&str)->Lesson{serde_json::from_str(source).unwrap()}

#[test]
fn bash_nine_restores_only_its_prerequisites_and_keeps_a_recovery_copy(){
    let lesson=lesson(include_str!("../courses/redesigned/bash-basics.json"));
    let exercise=lesson.tasks[8].git_terminal.clone().unwrap();
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let old=store.open("bash",exercise.clone()).unwrap();let previous=old.root().to_path_buf();
    std::fs::create_dir_all(old.work().join("notes")).unwrap();
    std::fs::write(old.work().join("memo.txt"),"earlier work").unwrap();
    std::fs::write(old.work().join("notes/\u{a0}memo.txt"),"mistake").unwrap();
    let other=store.open("other-lesson",GitExercise::default()).unwrap();
    std::fs::write(other.work().join("personal.txt"),"keep").unwrap();
    let reset=store.reset_step("bash",exercise.clone(),&lesson.tasks[8].id).unwrap();
    assert_ne!(reset.root(),previous);
    assert_eq!(std::fs::read_to_string(reset.work().join("memo.txt")).unwrap(),"첫 메모\n둘째 줄\n");
    assert_eq!(std::fs::read_dir(reset.work().join("notes")).unwrap().count(),0);
    assert_eq!(reset.shell_directory().unwrap(),reset.work().join("notes"));
    // Reopening before executing any command must keep the selected step's cwd.
    let reopened=store.open("bash",exercise).unwrap();
    assert_eq!(reopened.shell_directory().unwrap(),reset.work().join("notes"));
    assert!(previous.join("work/notes/\u{a0}memo.txt").exists());
    assert_eq!(std::fs::read_to_string(other.work().join("personal.txt")).unwrap(),"keep");
    assert!(!reopened.check_exercise().unwrap().passed);
}

#[test]
fn git_middle_step_restores_index_worktree_and_commits_without_resetting_to_step_one(){
    let lesson=lesson(include_str!("../courses/redesigned/git-first.json"));
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    for index in 1..lesson.tasks.len(){
        let task=&lesson.tasks[index];let exercise=task.git_terminal.clone().unwrap();
        let old=store.open("git",exercise.clone()).unwrap();let previous=old.root().to_path_buf();
        std::fs::write(old.work().join("my-work.txt"),"recoverable").unwrap();
        let reset=store.reset_step("git",exercise,&task.id).unwrap();
        assert!(reset.work().join(".git").is_dir());
        assert!(previous.join("work/my-work.txt").exists());
        assert!(!reset.work().join("my-work.txt").exists());
        assert_eq!(reset.git(&["rev-list","--count","HEAD"]).unwrap().stdout.trim(),if index>=3{"1"}else{""});
        if index==2 {assert_eq!(reset.git(&["show",":memo.txt"]).unwrap().stdout,"첫 메모\n");}
        if index==5 {
            assert_eq!(reset.git(&["show",":memo.txt"]).unwrap().stdout,"둘째 메모\n");
            assert_eq!(std::fs::read_to_string(reset.work().join("memo.txt")).unwrap(),"셋째 메모\n");
        }
    }
}

#[test]
fn java_middle_step_restores_the_compiled_prerequisite_without_counting_it_as_learner_work(){
    let lesson=lesson(include_str!("../courses/redesigned/java-launch.json"));let task=&lesson.tasks[5];
    let exercise=task.git_terminal.clone().unwrap();let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let reset=store.reset_step("java",exercise.clone(),&task.id).unwrap();
    assert_eq!(reset.java_source().unwrap(),exercise.shell.as_ref().unwrap().demo.files["Main.java"]);
    assert!(reset.work().join("Main.class").exists());
    let (mut shell,_out)=reset.open_terminal_with_player(Path::new(env!("CARGO_BIN_EXE_molip-quest"))).unwrap();
    assert!(!reset.check_exercise().unwrap().passed);
    shell.shutdown().unwrap();
}

#[test]
fn vim_middle_step_restores_unsaved_insert_mode_after_reopening(){
    let lesson=lesson(include_str!("../courses/redesigned/vim-basics.json"));let task=&lesson.tasks[1];
    let exercise=task.git_terminal.clone().unwrap();let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    store.reset_step("vim",exercise.clone(),&task.id).unwrap();
    let reopened=store.open("vim",exercise).unwrap();let (mut shell,mut out)=reopened.open_terminal().unwrap();
    let end=Instant::now()+Duration::from_secs(8);
    #[cfg(windows)] let mut response=String::new();
    while Instant::now()<end {
        while let Ok(bytes)=out.try_recv(){
            #[cfg(windows)] {response.push_str(&String::from_utf8_lossy(&bytes));if response.contains("\x1b[6n"){shell.input("\x1b[1;1R").unwrap();response.clear();}}
            #[cfg(not(windows))] let _=bytes;
        }
        if reopened.vim_progress().unwrap().state.is_some_and(|state|state.mode=="i"){
            assert!(!reopened.work().join("memo.txt").exists());
            reopened.prepare_terminal_shutdown().unwrap();shell.shutdown().unwrap();return;
        }
        std::thread::sleep(Duration::from_millis(25));
    }
    panic!("reset did not restore Insert mode");
}

#[test]
fn hosted_git_reset_restores_local_checkpoint_and_keeps_the_same_remote_identity(){
    let lesson=lesson(include_str!("../courses/redesigned/github-pr.json"));let task=&lesson.tasks[3];
    let exercise=task.git_terminal.clone().unwrap();let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let old=store.open("pr",exercise.clone()).unwrap();
    assert!(old.git(&["switch","-c","feature"]).unwrap().success);
    let repository=old.github_repository_name();
    assert!(old.git(&["remote","add","origin",&format!("https://github.com/example/{repository}")]).unwrap().success);
    old.remember_step_start(&task.id).unwrap();
    std::fs::write(old.work().join("memo.txt"),"changed").unwrap();
    let reset=store.reset_step("pr",exercise,&task.id).unwrap();
    assert_eq!(reset.github_repository_name(),repository);
    assert_eq!(reset.git(&["branch","--show-current"]).unwrap().stdout.trim(),"feature");
    assert_eq!(std::fs::read_to_string(reset.work().join("memo.txt")).unwrap(),"기본 메모\n");
    assert_eq!(std::fs::read_to_string(old.work().join("memo.txt")).unwrap(),"changed");
    assert!(reset.environment().iter().any(|(key,value)|key=="MQ3_REPO"&&value==&repository));
    // Repeated resets must keep the original entry checkpoint and remote identity.
    std::fs::write(reset.work().join("memo.txt"),"second attempt").unwrap();
    let again=store.reset_step("pr",task.git_terminal.clone().unwrap(),&task.id).unwrap();
    assert_eq!(again.github_repository_name(),repository);
    assert_eq!(std::fs::read_to_string(again.work().join("memo.txt")).unwrap(),"기본 메모\n");
    assert_eq!(std::fs::read_to_string(reset.work().join("memo.txt")).unwrap(),"second attempt");
}
