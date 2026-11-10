//! The Git worktree lesson graded by the player's own path (`check_exercise`) on real repositories.
//! For every step: the prepared start fails; the teacher narration replayed in its own demonstration
//! passes (refused commands really fail with their recorded exit code) without touching the learner's
//! folder; every equivalent answer passes; every common wrong answer fails. Each attempt starts from the
//! step's own start state in a fresh owned store, and each line runs in real Bash from the practice
//! folder `work`, as the learner's terminal would.
#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitExercise,GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson,Task}};
use std::path::{Path,PathBuf};

const ROOT:&str=env!("CARGO_MANIFEST_DIR");
const HOURS:&str="echo \"운영: 평일 9시부터\" >> guide.txt";

fn lesson()->Lesson {
    let raw=std::fs::read_to_string(Path::new(ROOT).join("courses/redesigned/git-worktree.json")).unwrap();
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/워/course.json")).unwrap();
    Lesson::parse(&raw,&course.lessons[0]).unwrap()
}

fn git_bash()->PathBuf {
    #[cfg(windows)] {molip_quest::setup_terminal::git_bash_executable().unwrap()}
    #[cfg(not(windows))] {PathBuf::from("/bin/bash")}
}
/// One command line in real Bash from the practice folder, with the practice's Git environment.
fn bash(practice:&GitPractice,line:&str)->Option<i32> {
    let environment=practice.environment();let shell=git_bash();
    let inherited=environment.iter().find(|(k,_)|k=="PATH").map(|(_,v)|std::ffi::OsString::from(v)).unwrap_or_else(||std::env::var_os("PATH").unwrap_or_default());
    let path=std::env::join_paths(shell.parent().map(Path::to_path_buf).into_iter().chain(std::env::split_paths(&inherited))).unwrap();
    let mut command=std::process::Command::new(&shell);
    command.args(["--noprofile","--norc","-c",line]).current_dir(practice.work()).envs(environment).env("PATH",path)
        .env("GIT_TRACE2_EVENT",practice.root().join("commands.jsonl"));
    #[cfg(target_os="macos")] command.env("LC_CTYPE","en_US.UTF-8");
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);command.env("LC_CTYPE","C.UTF-8");}
    command.output().unwrap().status.code()
}
fn quote(value:&str)->String {format!("'{}'",value.replace('\'',"'\\''"))}

/// The narration as one Bash session (its cd carries to the next command), checking every exit code.
fn teacher(task:&Task)->GitPractice {
    let demo=GitPractice::new(task.git_terminal.clone().unwrap().demonstration()).unwrap();
    let mut lines=vec![];
    for a in &task.narration {
        let line=match a["action"].as_str().unwrap() {
            "git_command"=>format!("git {}",a["args"].as_array().unwrap().iter().map(|v|quote(v.as_str().unwrap())).collect::<Vec<_>>().join(" ")),
            "bash_command"=>a["command"].as_str().unwrap().to_owned(),
            _=>continue,
        };
        let code=a["expected_exit"].as_i64().unwrap_or(0);
        lines.push(format!("{line}; test $? -eq {code} || exit 90"));
    }
    assert_eq!(bash(&demo,&lines.join("\n")),Some(0),"{}: a teacher command ended with another exit code",task.title);
    demo
}

fn attempt(task:&Task,lines:&[String])->(bool,String) {
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let practice=store.open(&format!("attempt:{}",task.id),task.git_terminal.clone().unwrap()).unwrap();
    let start=practice.check_exercise().unwrap();
    assert!(!start.passed,"{}: the prepared start must not pass",task.title);
    for line in lines {bash(&practice,line);}
    let report=practice.check_exercise().unwrap();
    let failed=report.cases.iter().filter(|c|!c.passed).map(|c|format!("{}: {:?}",c.input,c.stdout)).collect::<Vec<_>>().join(" | ");
    (report.passed,failed)
}

type Answers=Vec<(&'static str,Vec<String>)>;
struct Case {step:usize,accept:Answers,reject:Answers}
fn lines(items:&[&str])->Vec<String> {items.iter().map(|line|line.replace("{HOURS}",HOURS)).collect()}

fn cases()->Vec<Case> {
    vec![
        Case{step:1,
            accept:vec![("teacher commands",lines(&["git status","git switch hotfix","git show hotfix:guide.txt","cat guide.txt"])),
                        ("read only",lines(&["git show hotfix:guide.txt"]))],
            reject:vec![("forced switch discards the search line",lines(&["git switch -f hotfix","git show hotfix:guide.txt"])),
                        ("half-done work committed to get clean",lines(&["git commit -am wip","git show hotfix:guide.txt"])),
                        ("change discarded, then switched and back",lines(&["git restore guide.txt","git switch hotfix","git show hotfix:guide.txt","git switch main"])),
                        ("no observation of hotfix",lines(&["git status","cat guide.txt"]))]},
        Case{step:2,
            accept:vec![("teacher commands",lines(&["git worktree add ../hotfix hotfix","git worktree list","cat ../hotfix/guide.txt","git status"])),
                        ("branch named after the folder",lines(&["git worktree add ../hotfix"]))],
            reject:vec![("folder inside work",lines(&["git worktree add hotfix hotfix"])),
                        ("detached HEAD instead of the branch",lines(&["git worktree add --detach ../hotfix hotfix"])),
                        ("forced switch instead of a folder",lines(&["git switch -f hotfix"])),
                        ("other folder name",lines(&["git worktree add ../fix hotfix"]))]},
        Case{step:3,
            accept:vec![("teacher commands",lines(&["cd ../hotfix && git branch && {HOURS} && git add guide.txt && git commit -m \"운영 시간 안내\"","git log --oneline hotfix","git status"])),
                        ("from work with git -C, another message",lines(&["printf '%s\\n' '운영: 평일 9시부터' >> ../hotfix/guide.txt","git -C ../hotfix commit -am 운영"]))],
            reject:vec![("forgot cd: committed on main",lines(&["{HOURS}","git add guide.txt","git commit -m \"운영 시간 안내\""])),
                        ("file changed but not committed",lines(&["cd ../hotfix && {HOURS}"])),
                        ("committed, then the folder deleted by hand",lines(&["cd ../hotfix && {HOURS} && git commit -am x","rm -r ../hotfix"])),
                        ("the line added twice",lines(&["cd ../hotfix && {HOURS} && {HOURS} && git commit -am x"]))]},
        Case{step:4,
            accept:vec![("teacher commands",lines(&["git worktree add ../hotfix-try hotfix","git worktree add -b hotfix-try ../hotfix-try hotfix","git worktree list"])),
                        ("branch first, then the folder",lines(&["git branch hotfix-try hotfix","git worktree add ../hotfix-try hotfix-try"]))],
            reject:vec![("same branch forced into a second folder",lines(&["git worktree add -f ../hotfix-try hotfix"])),
                        ("new branch from main",lines(&["git worktree add -b hotfix-try ../hotfix-try main"])),
                        ("new branch inside work",lines(&["git worktree add -b hotfix-try hotfix-try hotfix"])),
                        ("hotfix folder given up for the new folder",lines(&["git worktree remove ../hotfix","git worktree add ../hotfix-try hotfix"]))]},
        Case{step:5,
            accept:vec![("teacher commands",lines(&["git worktree list","git worktree remove ../hotfix","git worktree list","git log --oneline hotfix"])),
                        ("removed from inside the folder itself",lines(&["cd ../hotfix && git worktree remove ."]))],
            reject:vec![("folder deleted by hand only",lines(&["rm -r ../hotfix"])),
                        ("branch deleted with the folder",lines(&["git worktree remove ../hotfix","git branch -D hotfix"])),
                        ("nothing cleaned",lines(&["git worktree list"]))]},
        Case{step:6,
            accept:vec![("teacher commands",lines(&["rm -r ../hotfix","git worktree list","git worktree add ../hotfix hotfix","git worktree prune","git worktree list"])),
                        ("remove also clears a missing folder",lines(&["rm -r ../hotfix","git worktree remove ../hotfix"]))],
            reject:vec![("folder deleted, record left",lines(&["rm -r ../hotfix","git worktree list"])),
                        ("re-added with -f instead of cleaning",lines(&["rm -r ../hotfix","git worktree add -f ../hotfix hotfix"])),
                        ("empty folder recreated by hand",lines(&["rm -r ../hotfix","mkdir ../hotfix"]))]},
        Case{step:7,
            accept:vec![("teacher commands",lines(&["git worktree add ../hotfix hotfix","cd ../hotfix && {HOURS} && git add guide.txt && git commit -m \"운영 시간 안내\"","git log --oneline hotfix","git worktree remove ../hotfix","git worktree list","git status"])),
                        ("folder deleted by hand and pruned",lines(&["git worktree add ../hotfix","cd ../hotfix && {HOURS} && git commit -am 운영","rm -r ../hotfix","git worktree prune"]))],
            reject:vec![("committed on main",lines(&["{HOURS}","git commit -am 운영"])),
                        ("folder left in place",lines(&["git worktree add ../hotfix hotfix","cd ../hotfix && {HOURS} && git commit -am 운영"])),
                        ("folder deleted, record left",lines(&["git worktree add ../hotfix hotfix","cd ../hotfix && {HOURS} && git commit -am 운영","rm -r ../hotfix"])),
                        ("forced switch loses the search line",lines(&["git switch -f hotfix","{HOURS}","git commit -am 운영","git switch main"]))]},
    ]
}

#[test]
fn every_worktree_step_fails_at_start_passes_the_teacher_and_answers_and_rejects_wrong_ones() {
    let lesson=lesson();
    assert_eq!(lesson.tasks.len(),7);
    let cases=cases();
    assert_eq!(cases.len(),lesson.tasks.len());
    let (mut accepted,mut rejected)=(0,0);
    for case in cases {
        let task=&lesson.tasks[case.step-1];
        // The teacher works in its own demonstration; the learner's folder is never touched by it.
        let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
        let student=store.open(&format!("student:{}",task.id),task.git_terminal.clone().unwrap()).unwrap();
        let before=std::fs::read(student.work().join("guide.txt")).unwrap();
        let demo=teacher(task);
        let report=demo.check_exercise().unwrap();
        assert!(report.passed,"{}: teacher narration: {}",task.title,serde_json::to_string(&report).unwrap());
        assert_eq!(std::fs::read(student.work().join("guide.txt")).unwrap(),before,"{}: the demonstration changed the learner's folder",task.title);
        assert!(!student.check_exercise().unwrap().passed,"{}: the learner's start must not pass",task.title);
        for (reason,lines) in &case.accept {
            let (passed,failed)=attempt(task,lines);
            assert!(passed,"{} {}: valid answer rejected: {reason}: {failed}",case.step,task.title);
            accepted+=1;eprintln!("step {}: accepted as expected: {reason}",case.step);
        }
        for (reason,lines) in &case.reject {
            let (passed,failed)=attempt(task,lines);
            assert!(!passed,"{} {}: wrong answer accepted: {reason}",case.step,task.title);
            rejected+=1;eprintln!("step {}: rejected as expected: {reason} ({failed})",case.step);
        }
    }
    eprintln!("git-worktree: 7 steps, {accepted} answers accepted, {rejected} wrong answers rejected");
}

#[test]
fn a_reset_step_rebuilds_its_prepared_worktree_in_the_new_folder() {
    let lesson=lesson();let task=&lesson.tasks[2];
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let exercise=task.git_terminal.clone().unwrap();
    let first=store.open("reset:worktree",exercise.clone()).unwrap();
    bash(&first,&format!("cd ../hotfix && {HOURS} && git commit -am 운영"));
    assert!(first.check_exercise().unwrap().passed);
    let reset=store.reset_step("reset:worktree",exercise,&task.id).unwrap();
    assert_ne!(reset.root(),first.root(),"a reset publishes a new owned folder");
    assert!(reset.root().join("hotfix/guide.txt").is_file(),"the prepared second folder exists beside the new work folder");
    assert!(!reset.check_exercise().unwrap().passed,"the reset folder starts over");
    bash(&reset,&format!("cd ../hotfix && {HOURS} && git commit -am 운영"));
    assert!(reset.check_exercise().unwrap().passed);
}

#[test]
fn worktree_goals_and_the_prepared_folder_command_are_validated() {
    let exercise=|goal:serde_json::Value,setup:serde_json::Value|->GitExercise {
        serde_json::from_value(serde_json::json!({"initial_history":"empty","files":{"a.txt":"a\n"},
            "setup":setup,"state_goal":goal})).unwrap()
    };
    let base=serde_json::json!([{"kind":"git","args":["add","a.txt"]},{"kind":"git","args":["commit","-m","a"]},{"kind":"git","args":["branch","b"]}]);
    let valid=exercise(serde_json::json!({"worktrees":{".":"main","../b":"b"},"branch_files":{"b":{"a.txt":"a\n"}}}),base.clone());
    assert!(valid.validate().is_ok());
    for goal in [serde_json::json!({"worktrees":{"../b":"b"}}),serde_json::json!({"worktrees":{".":"main","../b":"main"}}),
                 serde_json::json!({"worktrees":{".":"main","/tmp/b":"b"}}),serde_json::json!({"worktrees":{".":"main","../../b":"b"}}),
                 serde_json::json!({"worktrees":{".":"main","../work":"b"}}),serde_json::json!({"branch_files":{}}),
                 serde_json::json!({"branch_files":{"-x":{"a.txt":"a\n"}}}),serde_json::json!({"branch_files":{"b":{".git/config":"x"}}})] {
        assert!(exercise(goal.clone(),base.clone()).validate().is_err(),"accepted {goal}");
    }
    let mut prepared=base.as_array().unwrap().clone();prepared.push(serde_json::json!({"kind":"git","args":["worktree","add","../b","b"]}));
    assert!(exercise(serde_json::json!({"worktrees":{".":"main","../b":"b"}}),serde_json::Value::Array(prepared.clone())).validate().is_ok());
    for args in [serde_json::json!(["worktree","add","../../b","b"]),serde_json::json!(["worktree","add","/tmp/b","b"]),serde_json::json!(["worktree","remove","../b"]),
                 serde_json::json!(["worktree","add","--force","../b","b"]),serde_json::json!(["worktree","add","../b"])] {
        let mut setup=base.as_array().unwrap().clone();setup.push(serde_json::json!({"kind":"git","args":args}));
        assert!(exercise(serde_json::json!({"worktrees":{".":"main"}}),serde_json::Value::Array(setup)).validate().is_err(),"accepted setup {args}");
    }
    // A prepared folder beside work really exists and is graded by its place and branch.
    let practice=GitPractice::new(exercise(serde_json::json!({"worktrees":{".":"main","../b":"b"}}),serde_json::Value::Array(prepared))).unwrap();
    assert!(practice.root().join("b/a.txt").is_file());
    assert!(practice.check_exercise().unwrap().passed);
}
