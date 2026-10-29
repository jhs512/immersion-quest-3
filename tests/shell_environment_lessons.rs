//! The three shell variable / environment / argument lessons in a real PTY Bash (and the real JDK for
//! the Java step): every step fails untouched, the teacher's separate shell is never the learner's
//! evidence, the narration passes in the learner's own shell, and each final challenge rejects a real
//! wrong solution and accepts an equivalent one.
#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitExercise,GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::{path::Path,time::{Duration,Instant}};
type Output=tokio::sync::mpsc::Receiver<Vec<u8>>;

fn lesson(fixture:&str,raw:&str)->Lesson {
    let manifest=CourseManifest::parse(fixture).unwrap();
    Lesson::parse(raw,&manifest.lessons[0]).unwrap()
}
fn variables()->Lesson {lesson(include_str!("fixtures/player-pilot/변/course.json"),include_str!("../courses/redesigned/bash-variables.json"))}
fn environment()->Lesson {lesson(include_str!("fixtures/player-pilot/환/course.json"),include_str!("../courses/redesigned/bash-environment.json"))}
fn arguments()->Lesson {lesson(include_str!("fixtures/player-pilot/인/course.json"),include_str!("../courses/redesigned/bash-command-env-args.json"))}

fn open(p:&GitPractice)->(SetupTerminal,Output){
    let opened=p.open_terminal_with_player(Path::new(env!("CARGO_BIN_EXE_molip-quest"))).unwrap();
    opened
}
fn wait(p:&GitPractice,t:&mut SetupTerminal,out:&mut Output,done:impl Fn(&str)->bool)->String {
    let end=Instant::now()+Duration::from_secs(40);let mut text=String::new();let mut dsr=0;
    while Instant::now()<end {
        while let Ok(bytes)=out.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let count=text.matches("\x1b[6n").count();if count>dsr{t.input("\x1b[1;1R").unwrap();dsr=count;}
        if done(&text){return text}
        std::thread::sleep(Duration::from_millis(15));
    }
    panic!("PTY timeout: {text:?}; records {:?}",p.shell_completions().unwrap());
}
/// Type one command and wait until the shell returned to its prompt for it. Returns the new terminal text.
fn run(p:&GitPractice,t:&mut SetupTerminal,out:&mut Output,command:&str)->String {
    let before=p.shell_completions().unwrap().len();
    t.input(&format!("{command}\r")).unwrap();
    wait(p,t,out,|_|p.shell_completions().unwrap().iter().skip(before).any(|r|r.command==command))
}
fn started(p:&GitPractice)->(SetupTerminal,Output){
    let (mut t,mut out)=open(p);wait(p,&mut t,&mut out,|s|s.contains("$ "));(t,out)
}
fn narration_commands(task:&molip_quest::repository_course::Task)->Vec<(String,bool)> {
    let raw=serde_json::to_value(&task.narration).unwrap();
    raw.as_array().unwrap().iter().filter(|a|a["action"]=="bash_command").map(|a|(a["command"].as_str().unwrap().to_owned(),a["fails"]==true)).collect()
}

fn every_step_runs_in_real_bash(lesson:&Lesson,expected_steps:usize) {
    assert_eq!(lesson.tasks.len(),expected_steps);
    let dir=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(dir.path()).unwrap();
    let mut roots=std::collections::HashSet::new();
    for task in &lesson.tasks {
        let exercise=task.git_terminal.clone().unwrap();
        assert!(exercise.workspace_group.is_empty(),"each step starts its own fresh shell and folder");
        let shell=exercise.shell.clone().unwrap();
        // Every step owns its folder (scope per task) and starts from its declared files.
        let scope=exercise.workspace_scope(&format!("user:course:lesson:full:{}",task.id));
        let learner=store.open(&scope,exercise.clone()).unwrap();
        assert!(roots.insert(learner.root().to_path_buf()));
        for (name,body) in &shell.start.as_ref().unwrap().files {assert_eq!(std::fs::read_to_string(learner.work().join(name)).unwrap(),*body);}
        assert!(!learner.check_exercise().unwrap().passed,"untouched step must not pass: {}",task.title);
        // The teacher's demonstration plays in a separate shell and folder.
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();
        let (mut demo,mut demo_out)=started(&teacher);
        for (command,fails) in narration_commands(task) {
            run(&teacher,&mut demo,&mut demo_out,&command);
            let last=teacher.shell_completions().unwrap().last().unwrap().clone();
            assert_eq!(last.success,!fails,"{}: narration command {command} exit status",task.title);
        }
        assert!(teacher.check_exercise().unwrap().passed,"teacher narration must reach the goal: {}",task.title);
        demo.shutdown().unwrap();
        assert!(!learner.check_exercise().unwrap().passed,"the demonstration is not the learner's evidence: {}",task.title);
        // The learner follows the same commands in their own shell.
        let (mut terminal,mut out)=started(&learner);
        for (command,_) in narration_commands(task) {run(&learner,&mut terminal,&mut out,&command);}
        let report=learner.check_exercise().unwrap();
        assert!(report.passed,"{}: {}",task.title,serde_json::to_string(&report).unwrap());
        terminal.shutdown().unwrap();
        // Reopening keeps the passed state; the shell itself is new (variables are not persisted).
        assert!(store.open(&scope,exercise).unwrap().check_exercise().unwrap().passed);
    }
}

fn attempt(exercise:&GitExercise,commands:&[&str])->(bool,String) {
    let p=GitPractice::new(exercise.clone()).unwrap();let (mut t,mut out)=started(&p);
    let mut screen=String::new();
    for command in commands {screen=run(&p,&mut t,&mut out,command);}
    let report=p.check_exercise().unwrap();t.shutdown().unwrap();
    (report.passed,format!("{}\n{screen}",serde_json::to_string(&report).unwrap()))
}

#[test]
fn bash_variables_steps_run_in_real_bash() {every_step_runs_in_real_bash(&variables(),7);}
#[test]
fn bash_environment_steps_run_in_real_bash() {every_step_runs_in_real_bash(&environment(),6);}
#[test]
fn command_environment_and_argument_steps_run_in_real_bash_and_jdk() {every_step_runs_in_real_bash(&arguments(),5);}

#[test]
fn variables_challenge_needs_the_right_values_not_the_shown_commands() {
    let lesson=variables();let challenge=lesson.tasks.last().unwrap().git_terminal.clone().unwrap();
    let fixed=["mkdir \"$day\"","echo \"$memo\" > \"$day/memo.txt\"","cat 2026-10-30/memo.txt"];
    // Unquoted value: `사기` runs as a command, memo stays empty and the file gets an empty line.
    let (passed,detail)=attempt(&challenge,&[&["day=2026-10-30","memo=우유 사기"][..],&fixed[..]].concat());
    assert!(!passed,"unquoted assignment must fail: {detail}");
    // Equivalent spellings of the same values pass.
    let (passed,detail)=attempt(&challenge,&[&["day='2026-10-30'","memo=우유\\ 사기"][..],&fixed[..]].concat());
    assert!(passed,"single quotes and a backslash are equivalent: {detail}");
    // Writing the file directly skips the fixed commands this challenge is about.
    let (passed,_)=attempt(&challenge,&["mkdir 2026-10-30","echo \"우유 사기\" > 2026-10-30/memo.txt","cat 2026-10-30/memo.txt"]);
    assert!(!passed,"the fixed commands must actually run with the learner's variables");
}

#[test]
fn environment_challenge_judges_the_real_log_of_parent_and_child_values() {
    let lesson=environment();let challenge=lesson.tasks.last().unwrap().git_terminal.clone().unwrap();
    let (passed,detail)=attempt(&challenge,&["export COLOR=blue","bash show.sh","bash show.sh","bash change.sh","bash show.sh","cat log.txt"]);
    assert!(!passed,"exporting first changes the first line: {detail}");
    let (passed,detail)=attempt(&challenge,&["bash show.sh","COLOR=blue","bash show.sh","bash change.sh","bash show.sh","cat log.txt"]);
    assert!(!passed,"an unexported shell variable never reaches the child: {detail}");
    let (passed,detail)=attempt(&challenge,&["COLOR=blue","bash show.sh","export COLOR","bash show.sh","bash change.sh","bash show.sh","cat log.txt"]);
    assert!(passed,"assign first and export later is the same timeline: {detail}");
}

#[test]
fn argument_challenge_rejects_a_lasting_export_and_accepts_export_then_unset() {
    let lesson=arguments();let challenge=lesson.tasks.last().unwrap().git_terminal.clone().unwrap();
    let (passed,detail)=attempt(&challenge,&["cat greet.sh","bash greet.sh Minsu","export GREETING=Hello","bash greet.sh Jisu","bash greet.sh Minsu","cat log.txt"]);
    assert!(!passed,"a lasting export also greets the third run with Hello: {detail}");
    let (passed,detail)=attempt(&challenge,&["cat greet.sh","bash greet.sh Minsu","export GREETING=Hello","bash greet.sh Jisu","unset GREETING","bash greet.sh Minsu","cat log.txt"]);
    assert!(passed,"export then unset is equivalent: {detail}");
    let (passed,detail)=attempt(&challenge,&["cat greet.sh","bash greet.sh Minsu","env GREETING=Hello bash greet.sh Jisu","bash greet.sh Minsu","cat log.txt"]);
    assert!(passed,"env is another one-command environment: {detail}");
    let (passed,detail)=attempt(&challenge,&["cat greet.sh","bash greet.sh Minsu","bash greet.sh Hello Jisu","bash greet.sh Minsu","cat log.txt"]);
    assert!(!passed,"Hello as an argument is not the GREETING environment: {detail}");
}

#[test]
fn java_step_grades_the_real_jdk_output_of_the_environment_run() {
    let lesson=arguments();
    let task=lesson.tasks.iter().find(|t|t.git_terminal.as_ref().is_some_and(|e|e.java_build.is_some())).unwrap();
    let exercise=task.git_terminal.clone().unwrap();
    // Without the environment, the argument-less run prints APP_MODE=[null].
    let (passed,detail)=attempt(&exercise,&["java Main.java dev","java Main.java"]);
    assert!(!passed,"{detail}");
    assert!(detail.contains("APP_MODE=[null]"),"{detail}");
    let (passed,detail)=attempt(&exercise,&["java Main.java dev","APP_MODE=dev java Main.java"]);
    assert!(passed,"{detail}");
}
