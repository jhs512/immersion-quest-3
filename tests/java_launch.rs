use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::{path::Path,time::{Duration,Instant}};
fn lesson()->Lesson {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/뉴/course.json")).unwrap();
    Lesson::parse(include_str!("../courses/redesigned/java-launch.json"),&manifest.lessons[0]).unwrap()
}
fn open(p:&GitPractice)->(SetupTerminal,tokio::sync::mpsc::Receiver<Vec<u8>>){p.open_terminal_with_player(Path::new(env!("CARGO_BIN_EXE_molip-quest"))).unwrap()}
fn wait(p:&GitPractice,terminal:&mut SetupTerminal,out:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,predicate:impl Fn(&str)->bool)->String {
    let started=Instant::now();let mut text=String::new();let mut dsr=0;
    while started.elapsed()<Duration::from_secs(35){while let Ok(bytes)=out.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}let count=text.matches("\x1b[6n").count();if count>dsr{terminal.input("\x1b[1;1R").unwrap();dsr=count;}if predicate(&text){return text}std::thread::sleep(Duration::from_millis(20));}
    panic!("PTY did not finish; output={text}; records={:?}",p.shell_completions());
}
fn command(p:&GitPractice,terminal:&mut SetupTerminal,out:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,command:&str){
    let before=p.shell_completions().unwrap().len();terminal.input(&format!("{command}\r")).unwrap();
    wait(p,terminal,out,|_|p.shell_completions().unwrap().iter().skip(before).any(|r|r.command==command));
}
#[test]
fn eight_steps_use_real_jdk_preserve_source_class_and_isolate_demonstrations(){
    let lesson=lesson();assert_eq!(lesson.tasks.len(),9);// The last step is the separately started final challenge (tests/final_terminal_challenges.rs).
    let dir=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(dir.path()).unwrap();let mut root=None;
    for (i,task) in lesson.tasks[..8].iter().enumerate(){
        let exercise=task.git_terminal.clone().unwrap();let config=exercise.shell.as_ref().unwrap();
        let scope=exercise.workspace_scope("java-launch-integration");let p=store.open(&scope,exercise.clone()).unwrap();
        if let Some(root)=&root{assert_eq!(p.root(),root);}root=Some(p.root().to_path_buf());
        let (mut terminal,mut out)=open(&p);wait(&p,&mut terminal,&mut out,|s|s.contains("$ "));
        assert!(!p.check_exercise().unwrap().passed,"unexecuted step {}",i+1);
        let before=std::fs::read(p.work().join("Main.java")).unwrap();let class_before=std::fs::read(p.work().join("Main.class")).ok();
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();
        let (mut demo,mut demo_out)=open(&teacher);wait(&teacher,&mut demo,&mut demo_out,|s|s.contains("$ "));
        assert_eq!(teacher.java_source().unwrap(),config.demo.files["Main.java"]);
        teacher.save_java_source(&config.goal.files["Main.java"]).unwrap();
        for cmd in &config.commands{command(&teacher,&mut demo,&mut demo_out,cmd);}
        let report=teacher.check_exercise().unwrap();assert!(report.passed,"demo {}: {}",i+1,serde_json::to_string(&report).unwrap());
        demo.shutdown().unwrap();
        assert_eq!(std::fs::read(p.work().join("Main.java")).unwrap(),before);
        assert_eq!(std::fs::read(p.work().join("Main.class")).ok(),class_before);
        p.save_java_source(&config.goal.files["Main.java"]).unwrap();
        if i==6{assert!(!p.check_exercise().unwrap().passed,"source save alone must not compile");}
        for cmd in &config.commands{command(&p,&mut terminal,&mut out,cmd);}
        let report=p.check_exercise().unwrap();assert!(report.passed,"student {}: {}",i+1,serde_json::to_string(&report).unwrap());
        terminal.shutdown().unwrap();drop(out);
        let resumed=store.open(&scope,exercise.clone()).unwrap();assert_eq!(resumed.java_source().unwrap(),config.goal.files["Main.java"]);assert!(resumed.check_exercise().unwrap().passed);
        if i==5{assert_eq!(std::fs::read(p.work().join("Main.class")).ok(),class_before,"source-only edit cannot change the artifact");}
    }
    let initial=lesson.tasks[0].git_terminal.clone().unwrap();let scope=initial.workspace_scope("java-launch-integration");
    let reset=store.reset(&scope,initial.clone()).unwrap();assert_eq!(reset.java_source().unwrap(),initial.shell.unwrap().start.unwrap().files["Main.java"]);assert!(!reset.work().join("Main.class").exists());
}
#[test]
fn compiler_failure_cannot_pass_even_with_an_old_class_and_output_is_bounded(){
    let lesson=lesson();let mut exercise=lesson.tasks[6].git_terminal.clone().unwrap();
    let source=exercise.shell.as_ref().unwrap().demo.files["Main.java"].clone();exercise.shell.as_mut().unwrap().start=Some(molip_quest::git_practice::ShellSnapshot{files:std::collections::BTreeMap::from([("Main.java".into(),source)]),..Default::default()});
    let p=GitPractice::new(exercise).unwrap();let (mut terminal,mut out)=open(&p);wait(&p,&mut terminal,&mut out,|s|s.contains("$ "));
    p.save_java_source("public class Main { invalid }").unwrap();command(&p,&mut terminal,&mut out,"javac Main.java");assert!(!p.check_exercise().unwrap().passed);
    p.save_java_source("class Main { public static void main(String[] args) { while(true) System.out.println(123456789); } }").unwrap();
    command(&p,&mut terminal,&mut out,"java Main.java");
    assert!(!p.shell_completions().unwrap().last().unwrap().success);
    let journal=std::fs::read_to_string(p.root().join("java-invocations.jsonl")).unwrap();
    let records:Vec<serde_json::Value>=journal.lines().map(|line|serde_json::from_str(line).unwrap()).collect();
    assert_eq!(records.len(),2);assert_eq!(records[0]["success"],false);assert!(!records[0]["stderr"].as_str().unwrap().is_empty());
    assert!(records[1]["stderr"].as_str().unwrap().contains("실행 제한"));assert!(records[1]["stdout"].as_str().unwrap().len()<=65536);
    p.save_java_source("class Main { public static void main(String[] args) { while(true) {} } }").unwrap();
    let started=Instant::now();command(&p,&mut terminal,&mut out,"java Main.java");
    assert!(started.elapsed()>=Duration::from_secs(20)&&started.elapsed()<Duration::from_secs(30));
    let journal=std::fs::read_to_string(p.root().join("java-invocations.jsonl")).unwrap();
    let last:serde_json::Value=serde_json::from_str(journal.lines().last().unwrap()).unwrap();
    assert_eq!(last["success"],false);assert!(last["stderr"].as_str().unwrap().contains("실행 제한"));
    // A limited child must return control to the same shell, not terminate the session.
    command(&p,&mut terminal,&mut out,"echo alive");terminal.shutdown().unwrap();
}
