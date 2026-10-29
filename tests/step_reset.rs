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
    // The last git-first step is the separately started final challenge.
    for index in 1..lesson.tasks.len()-1{
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
fn hosted_git_reset_is_only_allowed_at_first_stage_and_creates_a_new_identity(){
    let lesson=lesson(include_str!("../courses/redesigned/github-pr.json"));
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let first=&lesson.tasks[0];let old=store.open("pr",first.git_terminal.clone().unwrap()).unwrap();
    let repository=old.github_repository_name();let previous=old.root().to_path_buf();
    std::fs::write(old.work().join("personal.txt"),"keep").unwrap();
    // Steps 2-8 continue the first step's project; the independent final (own workspace group and
    // project) starts its own round and may be reset.
    let (continued,last)=lesson.tasks[1..].split_at(lesson.tasks.len()-2);
    for task in continued{assert!(store.reset_step("pr",task.git_terminal.clone().unwrap(),&task.id).err().unwrap().contains("첫 단계"),"{}",task.id);}
    let final_step=last[0].git_terminal.clone().unwrap();
    assert!(final_step.hosted_reset_allowed());
    assert_ne!(final_step.workspace_group,first.git_terminal.as_ref().unwrap().workspace_group);
    assert_eq!(store.open("pr",first.git_terminal.clone().unwrap()).unwrap().root(),previous);
    let fresh=store.reset_step("pr",first.git_terminal.clone().unwrap(),&first.id).unwrap();
    assert_ne!(fresh.github_repository_name(),repository);assert_ne!(fresh.root(),previous);
    assert_eq!(std::fs::read_to_string(old.work().join("personal.txt")).unwrap(),"keep");
    assert!(!fresh.git(&["remote","get-url","origin"]).unwrap().success);
    assert_eq!(fresh.git(&["show","HEAD:memo.txt"]).unwrap().stdout,"기본 메모\n");
}
