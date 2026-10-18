use molip_quest::git_practice::{GitExercise, GitPractice};

#[test]
fn published_git_task_can_require_a_repository_state_without_a_fixed_command_spelling() {
    let mut value:serde_json::Value=serde_json::from_str(include_str!("fixtures/player-pilot/h/lesson.json")).unwrap();
    value["tasks"][0].as_object_mut().unwrap().remove("git_checks");
    value["tasks"][0]["git_terminal"]["commands"]=serde_json::json!([]);
    value["tasks"][0]["git_terminal"]["state_goal"]=serde_json::json!({"head_exists":true,"clean":true});
    let lesson:molip_quest::repository_course::Lesson=serde_json::from_value(value).unwrap();
    assert!(lesson.validate().is_ok());
}

#[test]
fn first_record_exercise_starts_without_a_commit_and_resets_to_the_same_untracked_file() {
    let exercise: GitExercise = serde_json::from_value(serde_json::json!({
        "initial_history": "empty",
        "files": {"memo.txt": "첫 메모\n"}
    })).unwrap();
    let mut practice = GitPractice::new(exercise).unwrap();
    assert!(!practice.git(&["rev-parse", "--verify", "HEAD"]).unwrap().success);
    assert_eq!(practice.git(&["ls-files"]).unwrap().stdout, "");
    assert_eq!(practice.git(&["status", "--porcelain"]).unwrap().stdout, "?? memo.txt\n");
    assert!(practice.git(&["add", "--", "memo.txt"]).unwrap().success);
    assert!(practice.git(&["commit", "-m", "첫 기록"]).unwrap().success);
    std::fs::write(practice.work().join("scratch.txt"), "unfinished").unwrap();
    practice.reset().unwrap();
    assert!(!practice.git(&["rev-parse", "--verify", "HEAD"]).unwrap().success);
    assert_eq!(practice.git(&["status", "--porcelain"]).unwrap().stdout, "?? memo.txt\n");
}

#[test]
fn new_record_goal_checks_the_recorded_tree_and_preserved_parent_not_only_the_message() {
    let exercise:GitExercise=serde_json::from_value(serde_json::json!({
        "initial_history":"empty","files":{"memo.txt":"첫 메모\n"},
        "setup":[{"kind":"git","args":["add","memo.txt"]},{"kind":"git","args":["commit","-m","first"]},
            {"kind":"file","path":"memo.txt","content":"둘째 메모\n"},{"kind":"git","args":["add","memo.txt"]},
            {"kind":"file","path":"memo.txt","content":"셋째 메모\n"}],
        "state_goal":{"head_exists":true,"commit_count":2,"clean":true,
            "head_files":{"memo.txt":"셋째 메모\n"},"parent_files":{"memo.txt":"첫 메모\n"},
            "index":{"memo.txt":"셋째 메모\n"},"working_files":{"memo.txt":"셋째 메모\n"}}
    })).unwrap();
    let mut practice=GitPractice::new(exercise).unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
    assert!(practice.git(&["commit","-m","memo"]).unwrap().success);
    assert!(!practice.check_exercise().unwrap().passed,"The index had the second memo, not the working file's third memo");
    practice.reset().unwrap();
    assert!(practice.git(&["add","--","memo.txt"]).unwrap().success);
    assert!(practice.git(&["commit","-m","any valid message"]).unwrap().success);
    assert!(practice.check_exercise().unwrap().passed);
    assert!(practice.git(&["commit","--allow-empty","-m","extra"]).unwrap().success);
    assert!(!practice.check_exercise().unwrap().passed,"An extra commit is not the requested state");
}

#[test]
fn staging_goal_accepts_equivalent_add_commands_but_rejects_a_commit_or_different_index_bytes() {
    let exercise: GitExercise = serde_json::from_value(serde_json::json!({
        "initial_history":"empty", "files":{"memo.txt":"첫 메모\n"},
        "state_goal":{"head_exists":false,"index":{"memo.txt":"첫 메모\n"},"working_files":{"memo.txt":"첫 메모\n"}}
    })).unwrap();
    let mut practice=GitPractice::new(exercise).unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
    assert!(practice.git(&["add","memo.txt"]).unwrap().success);
    assert!(practice.check_exercise().unwrap().passed);
    assert!(practice.git(&["commit","-m","too soon"]).unwrap().success);
    assert!(!practice.check_exercise().unwrap().passed);
    practice.reset().unwrap();
    assert!(practice.git(&["add","--","memo.txt"]).unwrap().success);
    assert!(practice.check_exercise().unwrap().passed);
    std::fs::write(practice.work().join("memo.txt"),"다른 내용\n").unwrap();
    assert!(practice.git(&["add","memo.txt"]).unwrap().success);
    std::fs::write(practice.work().join("memo.txt"),"첫 메모\n").unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
}
