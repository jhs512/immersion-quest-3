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
