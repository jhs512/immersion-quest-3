use molip_quest::git_practice::{GitExercise,GitPractice};

fn conflict_exercise()->serde_json::Value {
    serde_json::json!({"initial_history":"empty","files":{"guide.txt":"base\n"},"setup":[
        {"kind":"git","args":["add","guide.txt"]},{"kind":"git","args":["commit","-m","base"]},{"kind":"git","args":["branch","feature"]},
        {"kind":"file","path":"guide.txt","content":"main version\n"},{"kind":"git","args":["add","guide.txt"]},{"kind":"git","args":["commit","-m","main change"]},
        {"kind":"git","args":["switch","feature"]},{"kind":"file","path":"guide.txt","content":"feature version\n"},{"kind":"git","args":["add","guide.txt"]},{"kind":"git","args":["commit","-m","feature change"]},
        {"kind":"git","args":["switch","main"]},{"kind":"merge_conflict","branch":"feature"}
    ]})
}

#[test]
fn conflict_preparation_recreates_real_unmerged_state_and_rejects_unexpected_failures() {
    let raw=conflict_exercise();
    let exercise:GitExercise=serde_json::from_value(raw.clone()).unwrap();
    let mut practice=GitPractice::new(exercise).unwrap();
    for _ in 0..2 {
        assert_eq!(practice.git(&["diff","--name-only","--diff-filter=U"]).unwrap().stdout,"guide.txt\n");
        assert!(practice.git(&["rev-parse","--verify","MERGE_HEAD"]).unwrap().success);
        assert_eq!(practice.git(&["show","HEAD:guide.txt"]).unwrap().stdout,"main version\n");
        std::fs::write(practice.work().join("guide.txt"),"attempted fix\n").unwrap();
        assert!(practice.git(&["add","guide.txt"]).unwrap().success);
        std::fs::write(practice.work().join("leftover.txt"),"leftover").unwrap();
        practice.reset().unwrap();
        assert!(!practice.work().join("leftover.txt").exists());
    }
    for branch in ["main","missing"] {
        let mut invalid=raw.clone();invalid["setup"][11]["branch"]=serde_json::json!(branch);
        let exercise:GitExercise=serde_json::from_value(invalid).unwrap();
        assert!(GitPractice::new(exercise).is_err(),"A successful merge or a missing branch is not the intended conflict");
    }
}

#[test]
fn resolving_the_file_is_not_enough_until_the_unmerged_index_is_prepared() {
    let mut raw=conflict_exercise();
    raw["state_goal"]=serde_json::json!({"current_branch":"main","merge_in_progress":true,"unmerged_paths":[],"commit_count":2,"head_files":{"guide.txt":"main version\n"},"index":{"guide.txt":"feature version\n"},"working_files":{"guide.txt":"feature version\n"}});
    let practice=GitPractice::new(serde_json::from_value(raw).unwrap()).unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
    std::fs::write(practice.work().join("guide.txt"),"feature version\n").unwrap();
    assert!(!practice.check_exercise().unwrap().passed,"Removing conflict markers alone does not resolve the index");
    assert!(practice.git(&["add","guide.txt"]).unwrap().success);
    assert!(practice.check_exercise().unwrap().passed);
    assert!(practice.git(&["commit","-m","merge"]).unwrap().success);
    assert!(!practice.check_exercise().unwrap().passed,"This step asks for preparation, before completing the merge");
}

#[test]
fn a_completed_merge_preserves_exactly_two_parents_and_both_branch_histories() {
    let mut raw=conflict_exercise();
    raw["setup"].as_array_mut().unwrap().extend([
        serde_json::json!({"kind":"file","path":"guide.txt","content":"feature version\n"}),
        serde_json::json!({"kind":"git","args":["add","guide.txt"]})
    ]);
    raw["state_goal"]=serde_json::json!({"current_branch":"main","merge_in_progress":false,"unmerged_paths":[],"parent_count":2,"references":{"refs/heads/feature":"HEAD^2"},"commit_count":4,"clean":true,"head_files":{"guide.txt":"feature version\n"},"parent_files":{"guide.txt":"main version\n"}});
    let practice=GitPractice::new(serde_json::from_value(raw).unwrap()).unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
    assert!(practice.git(&["commit","-m","resolved"]).unwrap().success);
    assert!(practice.check_exercise().unwrap().passed);
    let extra=practice.git(&["commit-tree","HEAD^{tree}","-p","HEAD^1","-p","HEAD^2","-p","HEAD~2","-m","extra parent"]).unwrap();
    assert!(extra.success);
    assert!(practice.git(&["reset","--hard",extra.stdout.trim()]).unwrap().success);
    assert!(!practice.check_exercise().unwrap().passed,"A redundant third parent must not satisfy a two-parent merge");
}
