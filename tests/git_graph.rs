use molip_quest::git_practice::{GitExercise,GitPractice};

fn git(practice:&GitPractice,args:&[&str]) {let result=practice.git(args).unwrap();assert!(result.success,"{args:?}: {}",result.stderr);}
fn commit(practice:&GitPractice,text:&str) {std::fs::write(practice.work().join("memo.txt"),text).unwrap();git(practice,&["add","memo.txt"]);git(practice,&["commit","-m",text]);}

#[test]
fn graph_tracks_real_refs_merge_parents_detached_head_and_reset_without_recording_queries() {
    let mut practice=GitPractice::new(GitExercise::default()).unwrap();
    let initial=practice.graph_snapshot().unwrap();
    assert_eq!(initial.commits.len(),1);
    git(&practice,&["switch","-c","feature"]);commit(&practice,"feature");
    let feature=practice.graph_snapshot().unwrap();
    assert_eq!(feature.branch.as_deref(),Some("feature"));assert_eq!(feature.commits.len(),2);
    git(&practice,&["switch","main"]);
    std::fs::write(practice.work().join("other.txt"),"main").unwrap();git(&practice,&["add","other.txt"]);git(&practice,&["commit","-m","main"]);
    git(&practice,&["merge","--no-edit","feature"]);
    let before=std::fs::read(practice.root().join("commands.jsonl")).unwrap();
    let merged=practice.graph_snapshot().unwrap();
    assert_eq!(merged.commits[0].parents.len(),2);assert_eq!(merged.head.as_ref(),Some(&merged.commits[0].id));
    assert!(merged.references.iter().any(|r|r.name=="main"&&Some(&r.id)==merged.head.as_ref()));
    assert_eq!(before,std::fs::read(practice.root().join("commands.jsonl")).unwrap(),"graph reads must not count as learner commands");
    let hash=merged.commits[0].id.clone();git(&practice,&["checkout","--detach",&hash]);
    assert!(practice.graph_snapshot().unwrap().branch.is_none());
    practice.reset().unwrap();assert_eq!(practice.graph_snapshot().unwrap(),initial);
}

#[test]
fn graph_does_not_invent_a_commit_before_init_or_first_commit() {
    let exercise:GitExercise=serde_json::from_value(serde_json::json!({"initial_history":"uninitialized"})).unwrap();
    let practice=GitPractice::new(exercise).unwrap();
    assert!(!practice.graph_snapshot().unwrap().initialized);
    git(&practice,&["init"]);
    let empty=practice.graph_snapshot().unwrap();assert!(empty.initialized);assert!(empty.head.is_none());assert!(empty.commits.is_empty());
}

#[test]
fn graph_reads_conflict_and_remote_tracking_state_from_real_repositories() {
    let advanced:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/git-branch-advanced.json")).unwrap();
    let practice=GitPractice::new(serde_json::from_value(advanced["tasks"][2]["git_terminal"].clone()).unwrap()).unwrap();
    let conflicted=practice.graph_snapshot().unwrap();
    assert!(conflicted.merging);assert!(conflicted.changes.iter().any(|line|line.starts_with("UU ")));
    assert!(conflicted.commits.iter().all(|commit|commit.parents.len()<2),"resolving a file does not invent a merge commit");
    let remote:serde_json::Value=serde_json::from_str(include_str!("../courses/redesigned/git-remote.json")).unwrap();
    let task = remote["tasks"].as_array().unwrap().iter().find(|task| task["id"].as_str() == Some("stp_bb240382-615b-4679-ae14-79ee9f38940a")).expect("remote lesson includes a fetch step");
    let exercise: GitExercise = serde_json::from_value(task["git_terminal"].clone()).unwrap();
    let practice=GitPractice::new(exercise.demonstration()).unwrap();
    git(&practice,&["fetch","origin"]);
    let fetched=practice.graph_snapshot().unwrap();
    let tracking=fetched.references.iter().find(|r|r.name=="origin/main").unwrap();
    assert!(tracking.remote);assert_ne!(Some(&tracking.id),fetched.head.as_ref());
    git(&practice,&["merge","--ff-only","origin/main"]);
    let merged=practice.graph_snapshot().unwrap();assert_eq!(merged.head.as_ref(),Some(&tracking.id));
    assert!(merged.commits.iter().all(|commit|commit.parents.len()<2),"fast-forward creates no merge commit");
}

/// Git starts `git maintenance run --auto --detach` after merge and commit. In a practice it is a background
/// process the learner never ran: it keeps writing to the command log after the learner's command returned
/// (the macOS release check read a log that grew under it) and runs in the learner's repository during reset.
#[test]
fn practice_git_never_starts_background_maintenance_and_keeps_learner_global_config() {
    let started=|practice:&GitPractice|->Vec<String>{std::fs::read_to_string(practice.root().join("commands.jsonl")).unwrap_or_default().lines()
        .filter_map(|line|serde_json::from_str::<serde_json::Value>(line).ok())
        .filter(|event|matches!(event["event"].as_str(),Some("start"|"child_start")))
        .map(|event|event["argv"].to_string()).filter(|argv|argv.contains("maintenance")).collect()};
    let practice=GitPractice::new(GitExercise::default()).unwrap();
    git(&practice,&["switch","-c","feature"]);commit(&practice,"feature");git(&practice,&["switch","main"]);
    std::fs::write(practice.work().join("other.txt"),"main").unwrap();git(&practice,&["add","other.txt"]);git(&practice,&["commit","-m","main"]);
    git(&practice,&["merge","--no-edit","feature"]);
    assert_eq!(started(&practice),Vec::<String>::new());
    // The learner's own global settings still go to the practice's global file.
    git(&practice,&["config","--global","user.name","학습자"]);
    assert_eq!(practice.git(&["config","--global","user.name"]).unwrap().stdout,"학습자\n");
    let uninitialized:GitExercise=serde_json::from_value(serde_json::json!({"initial_history":"uninitialized"})).unwrap();
    let practice=GitPractice::new(uninitialized).unwrap();
    git(&practice,&["init"]);commit(&practice,"first");
    assert_eq!(practice.git(&["branch","--show-current"]).unwrap().stdout,"main\n","git init still starts on main");
    assert_eq!(started(&practice),Vec::<String>::new());
}
