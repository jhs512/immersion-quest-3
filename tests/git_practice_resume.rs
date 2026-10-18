use molip_quest::git_practice::{GitExercise,GitPracticeStore};

#[test]
fn saved_practice_reopens_the_real_index_branch_and_working_files() {
    let root=tempfile::tempdir().unwrap();
    let store=GitPracticeStore::new(root.path()).unwrap();
    let scope="learner:11:course:a:lesson:a:full:step:a";
    let original;
    {
        let practice=store.open(scope,GitExercise::default()).unwrap();
        original=practice.root().to_path_buf();
        assert!(practice.git(&["switch","-c","experiment"]).unwrap().success);
        std::fs::write(practice.work().join("tracked.txt"),"staged\n").unwrap();
        assert!(practice.git(&["add","tracked.txt"]).unwrap().success);
        std::fs::write(practice.work().join("tracked.txt"),"working\n").unwrap();
        std::fs::write(practice.work().join("scratch.txt"),"untracked\n").unwrap();
    }
    let reopened=store.open(scope,GitExercise::default()).unwrap();
    assert_eq!(reopened.root(),original);
    assert_eq!(reopened.git(&["branch","--show-current"]).unwrap().stdout.trim(),"experiment");
    assert_eq!(reopened.git(&["show",":tracked.txt"]).unwrap().stdout,"staged\n");
    assert_eq!(std::fs::read_to_string(reopened.work().join("tracked.txt")).unwrap(),"working\n");
    assert_eq!(std::fs::read_to_string(reopened.work().join("scratch.txt")).unwrap(),"untracked\n");
    assert_eq!(reopened.git(&["rev-list","--count","HEAD"]).unwrap().stdout.trim(),"1");
}

#[test]
fn reset_publishes_a_clean_state_without_deleting_prior_work_or_another_scope() {
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let exercise=GitExercise{commands:vec![vec!["status".into(),"--short".into()]],..Default::default()};
    let mut practice=store.open("account:1:course:a",exercise.clone()).unwrap();
    let previous=practice.root().to_path_buf();
    std::fs::write(practice.work().join("private.txt"),"unfinished").unwrap();
    practice.git(&["status","--short"]).unwrap();assert!(practice.commands_satisfied().unwrap());
    let other=store.open("account:2:course:a",exercise.clone()).unwrap();
    std::fs::write(other.work().join("other.txt"),"other").unwrap();
    practice.reset().unwrap();
    assert_ne!(practice.root(),previous);
    assert!(!practice.work().join("private.txt").exists());
    assert!(!practice.commands_satisfied().unwrap());
    assert_eq!(std::fs::read_to_string(previous.join("work/private.txt")).unwrap(),"unfinished");
    assert_eq!(std::fs::read_to_string(other.work().join("other.txt")).unwrap(),"other");
    let reopened=store.open("account:1:course:a",exercise).unwrap();assert_eq!(reopened.root(),practice.root());
    assert_eq!(reopened.git(&["status","--porcelain"]).unwrap().stdout,"");
}

#[test]
fn damaged_pointer_is_rejected_without_following_it_or_destroying_a_prior_state() {
    let root=tempfile::tempdir().unwrap();let outside=tempfile::tempdir().unwrap();
    let marker=outside.path().join("keep.txt");std::fs::write(&marker,"keep").unwrap();
    let store=GitPracticeStore::new(root.path()).unwrap();
    let first=store.open("one",GitExercise::default()).unwrap();
    let pointer=std::fs::read_dir(root.path()).unwrap().map(|entry|entry.unwrap().path()).find(|path|path.extension().is_some_and(|extension|extension=="json")).unwrap();
    std::fs::write(pointer,serde_json::to_string(&outside.path().to_string_lossy()).unwrap()).unwrap();
    assert!(store.open("one",GitExercise::default()).is_err());
    assert!(store.reset("one",GitExercise{commands:vec![vec![]],..Default::default()}).is_err());
    assert_eq!(std::fs::read_to_string(marker).unwrap(),"keep");assert!(first.work().join("tracked.txt").exists());
}

#[test]
fn overlapping_first_opens_publish_one_repository_for_the_same_scope() {
    let root=tempfile::tempdir().unwrap();let barrier=std::sync::Arc::new(std::sync::Barrier::new(6));
    let workers=(0..6).map(|_|{let path=root.path().to_path_buf();let barrier=barrier.clone();std::thread::spawn(move||{
        let store=GitPracticeStore::new(&path).unwrap();barrier.wait();
        store.open("same",GitExercise::default()).unwrap().root().to_path_buf()
    })}).collect::<Vec<_>>();
    let paths=workers.into_iter().map(|worker|worker.join().unwrap()).collect::<std::collections::BTreeSet<_>>();
    assert_eq!(paths.len(),1,"Concurrent first opens must share the published student state");
    let reopened=GitPracticeStore::new(root.path()).unwrap().open("same",GitExercise::default()).unwrap();
    assert!(paths.contains(reopened.root()));
}

#[test]
fn saved_practice_process_worker() {
    let Some(root)=std::env::var_os("MQ3_GIT_STORE_WORKER") else{return;};
    let root=std::path::PathBuf::from(root);
    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(20);
    while !root.join("go").exists(){assert!(std::time::Instant::now()<deadline);std::thread::sleep(std::time::Duration::from_millis(20));}
    let practice=GitPracticeStore::new(&root).unwrap().open("shared",GitExercise::default()).unwrap();
    std::fs::write(std::env::var_os("MQ3_GIT_STORE_RESULT").unwrap(),practice.root().to_string_lossy().as_bytes()).unwrap();
}

#[test]
fn separate_processes_agree_on_the_same_first_repository() {
    let root=tempfile::tempdir().unwrap();let mut children=vec![];
    for index in 0..3 {
        let mut command=std::process::Command::new(std::env::current_exe().unwrap());
        command.args(["--exact","saved_practice_process_worker"])
            .env("MQ3_GIT_STORE_WORKER",root.path()).env("MQ3_GIT_STORE_RESULT",root.path().join(format!("worker-{index}")))
            .stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null());
        #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
        children.push(command.spawn().unwrap());
    }
    std::fs::write(root.path().join("go"),"").unwrap();
    for mut child in children {assert!(child.wait().unwrap().success());}
    let paths=(0..3).map(|index|std::fs::read_to_string(root.path().join(format!("worker-{index}"))).unwrap()).collect::<std::collections::BTreeSet<_>>();
    assert_eq!(paths.len(),1,"Separate players must not publish competing first repositories");
}
