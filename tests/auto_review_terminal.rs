#![cfg(not(target_os="android"))]
//! 관리자 자동 풀이 on real Bash and Git practice folders, typed through a real PTY.
//! A solved terminal step passes again without anything typed, so a run prepares each practice
//! workspace once, at its first step, with the official 초기화 (`reset_step`): that rebuilds the
//! step's prepared start (earlier steps' files, folder and Git state as the lesson defines them).
//! The run's action lists then reach each goal by actually running the commands, and later steps
//! continue on the state the earlier ones left (no reset per step; tests/player_auto_state_native.rs).
use molip_quest::{auto_review::{self,Plan},git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson,Task},setup_terminal::SetupTerminal};
use std::time::{Duration,Instant};

fn read(output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,terminal:&mut SetupTerminal,text:&mut String,dsr:&mut usize){
    while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
    let count=text.matches("\x1b[6n").count();if count>*dsr{terminal.input("\x1b[1;1R").unwrap();*dsr=count;}
}
fn prompt(terminal:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,text:&mut String,dsr:&mut usize,from:usize){
    let deadline=Instant::now()+Duration::from_secs(20);
    while Instant::now()<deadline {
        read(output,terminal,text,dsr);
        // The raw PTY stream, unlike xterm's rendered buffer the app reads, keeps escape codes.
        let mut plain=String::new();let mut chars=text.chars().peekable();
        while let Some(c)=chars.next(){if c=='\u{1b}'&&chars.peek()==Some(&'['){chars.next();for d in chars.by_ref(){if d.is_ascii_alphabetic(){break;}}}else{plain.push(c);}}
        if (from==0||text[from..].contains('\n'))&&plain.trim_end().ends_with('$'){return;}
        std::thread::sleep(Duration::from_millis(20));
    }
    panic!("no prompt: {text:?}");
}
/// The same mapping as assets/layout/auto-run.js: each action is one typed command line.
fn shell_argument(value:&str)->String{
    if !value.is_empty()&&value.chars().all(|c|c.is_alphanumeric()||"_./:=+@%^-".contains(c)){return value.into();}
    format!("\"{}\"",value.replace('\\',"\\\\").replace('$',"\\$").replace('`',"\\`").replace('"',"\\\""))
}
fn command_line(action:&serde_json::Value)->String{
    match action["action"].as_str().unwrap(){
        "bash_command"|"inspect_folder"=>action["command"].as_str().unwrap().into(),
        "write_memo"=>format!("echo \"{}\" > memo.txt",action["content"].as_str().unwrap()),
        "read_memo"=>"cat memo.txt".into(),
        "git_command"=>format!("git {}",action["args"].as_array().unwrap().iter().map(|a|shell_argument(a.as_str().unwrap())).collect::<Vec<_>>().join(" ")),
        other=>panic!("not a typed command: {other}"),
    }
}
fn solve(practice:&GitPractice,task:&Task){
    let Ok(Plan::Terminal{actions,answer:None})=auto_review::plan(task) else{panic!("{} is a terminal step",task.title)};
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    let (mut text,mut dsr)=(String::new(),0);
    prompt(&mut terminal,&mut output,&mut text,&mut dsr,0);
    for action in &actions {let from=text.len();terminal.input(&format!("{}\r",command_line(action))).unwrap();prompt(&mut terminal,&mut output,&mut text,&mut dsr,from);}
    // Bash records a command when the prompt returns; let the last record land.
    std::thread::sleep(Duration::from_millis(300));
    terminal.shutdown().unwrap();
}
fn grade(practice:&GitPractice,task:&Task)->bool{
    if let Some(checks)=&task.git_checks{practice.check(checks)}else{practice.check_exercise()}.unwrap().passed
}

#[test]
fn a_solved_bash_step_is_reset_to_its_own_start_and_solved_again_by_real_commands(){
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/부/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/bash-basics.json"),&manifest.lessons[0]).unwrap();
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let scope=|task:&Task|task.git_terminal.as_ref().unwrap().workspace_scope("user:course:lesson:full:bash-practice");
    // Solve the first five steps in order in the shared Bash workspace.
    for task in &lesson.tasks[..5] {
        let practice=store.open(&scope(task),task.git_terminal.clone().unwrap()).unwrap();
        assert!(!grade(&practice,task),"{} passes before any command",task.title);
        solve(&practice,task);
        assert!(grade(&practice,task),"{} passes after its commands",task.title);
    }
    let task=&lesson.tasks[3];let exercise=task.git_terminal.clone().unwrap();let shell=exercise.shell.clone().unwrap();
    // Reopened after later steps changed the folder, the solved step still reports its old commands.
    let reopened=store.open(&scope(task),exercise.clone()).unwrap();
    let later_work=reopened.work();
    // The official reset of this one step: its prepared start, a new shell and no command history.
    let reset=store.reset_step(&scope(task),exercise.clone(),&task.id).unwrap();
    assert!(!grade(&reset,task),"after the step reset nothing passes until the commands run again");
    for (name,body) in &shell.demo.files {assert_eq!(std::fs::read_to_string(reset.work().join(name)).unwrap(),*body,"prerequisite file {name} is kept");}
    assert_eq!(reset.shell_directory().unwrap().canonicalize().unwrap(),reset.work().join(&shell.demo.cwd).canonicalize().unwrap(),"prerequisite folder is kept");
    solve(&reset,task);
    assert!(grade(&reset,task),"the re-solve passes through real commands");
    // The next step continues from the re-solved workspace.
    let next=&lesson.tasks[4];
    let continued=store.open(&scope(next),next.git_terminal.clone().unwrap()).unwrap();
    assert_eq!(continued.work(),reset.work(),"later steps share the re-solved workspace");
    assert_ne!(later_work,reset.work());
}

#[test]
fn a_committed_git_step_would_pass_again_untouched_so_the_run_resets_it_first(){
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/git-first.json")).unwrap();
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let scope=|task:&Task|task.git_terminal.as_ref().unwrap().workspace_scope("user:course:git-first:full:repo");
    for task in &lesson.tasks[..3] {
        let practice=store.open(&scope(task),task.git_terminal.clone().unwrap()).unwrap();
        solve(&practice,task);
        assert!(grade(&practice,task),"{} passes after its commands",task.title);
    }
    let commit=&lesson.tasks[2];let exercise=commit.git_terminal.clone().unwrap();
    let reopened=store.open(&scope(commit),exercise.clone()).unwrap();
    assert!(grade(&reopened,commit),"the solved commit step already holds its goal: submitting now would pass with nothing typed");
    let reset=store.reset_step(&scope(commit),exercise,&commit.id).unwrap();
    assert!(!grade(&reset,commit),"the reset step starts before the commit");
    assert_eq!(reset.git(&["diff","--cached","--name-only"]).unwrap().stdout.trim(),"memo.txt","its prepared start keeps the staged memo");
    solve(&reset,commit);
    assert!(grade(&reset,commit),"the commit is made again for real");
}
