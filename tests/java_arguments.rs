use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::{path::Path,time::{Duration,Instant}};
fn lesson()->Lesson {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/듀/course.json")).unwrap();
    Lesson::parse(include_str!("../courses/redesigned/java-arguments.json"),&manifest.lessons[0]).unwrap()
}
fn open(p:&GitPractice)->(SetupTerminal,tokio::sync::mpsc::Receiver<Vec<u8>>){
    p.open_terminal_with_player(Path::new(env!("CARGO_BIN_EXE_molip-quest"))).unwrap()
}
fn wait(p:&GitPractice,t:&mut SetupTerminal,out:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,done:impl Fn(&str)->bool)->String {
    let end=Instant::now()+Duration::from_secs(30);let mut text=String::new();let mut dsr=0;
    while Instant::now()<end {
        while let Ok(bytes)=out.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let count=text.matches("\x1b[6n").count();if count>dsr{t.input("\x1b[1;1R").unwrap();dsr=count;}
        if done(&text){return text}std::thread::sleep(Duration::from_millis(15));
    }
    panic!("Java argument PTY timeout: {text}; {:?}",p.shell_completions());
}
fn run(p:&GitPractice,t:&mut SetupTerminal,out:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,command:&str){
    let before=p.shell_completions().unwrap().len();t.input(&format!("{command}\r")).unwrap();
    wait(p,t,out,|_|p.shell_completions().unwrap().iter().skip(before).any(|r|r.command==command));
}
#[test]
fn independent_argument_steps_use_real_bash_and_jdk_and_preserve_learner_state(){
    let lesson=lesson();assert_eq!(lesson.tasks.len(),8);
    let dir=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(dir.path()).unwrap();let mut root=None;
    for task in &lesson.tasks {
        let exercise=task.git_terminal.clone().unwrap();let shell=exercise.shell.as_ref().unwrap();
        let scope=exercise.workspace_scope("java-arguments-integration");let p=store.open(&scope,exercise.clone()).unwrap();
        if let Some(root)=&root{assert_eq!(p.root(),root);}root=Some(p.root().to_path_buf());
        let (mut terminal,mut out)=open(&p);wait(&p,&mut terminal,&mut out,|s|s.contains("$ "));
        assert!(!p.check_exercise().unwrap().passed,"not run: {}",task.title);
        let before=p.java_source().unwrap();let teacher=GitPractice::new(exercise.demonstration()).unwrap();
        let (mut demo,mut demo_out)=open(&teacher);wait(&teacher,&mut demo,&mut demo_out,|s|s.contains("$ "));
        teacher.save_java_source(&shell.goal.files["Main.java"]).unwrap();
        for command in &shell.commands{run(&teacher,&mut demo,&mut demo_out,command);}
        assert!(teacher.check_exercise().unwrap().passed,"demo: {}",task.title);demo.shutdown().unwrap();
        assert_eq!(p.java_source().unwrap(),before,"teacher must not change learner source");
        p.save_java_source(&shell.goal.files["Main.java"]).unwrap();
        // Printing the expected text through Bash is not evidence of Java execution.
        run(&p,&mut terminal,&mut out,"echo observed");assert!(!p.check_exercise().unwrap().passed);
        for command in &shell.commands{run(&p,&mut terminal,&mut out,command);}
        let report=p.check_exercise().unwrap();assert!(report.passed,"{}: {}",task.title,serde_json::to_string(&report).unwrap());
        let log=std::fs::read_to_string(p.root().join("java-invocations.jsonl")).unwrap();
        let record:serde_json::Value=serde_json::from_str(log.lines().last().unwrap()).unwrap();
        assert_eq!(record["args"],serde_json::to_value(&exercise.java_build.as_ref().unwrap().command).unwrap());
        assert!(!p.work().join("Main.class").exists());terminal.shutdown().unwrap();
        let reopened=store.open(&scope,exercise.clone()).unwrap();assert_eq!(reopened.java_source().unwrap(),shell.goal.files["Main.java"]);
        assert!(reopened.check_exercise().unwrap().passed);
    }
    let first=lesson.tasks[0].git_terminal.clone().unwrap();let scope=first.workspace_scope("java-arguments-integration");
    let reset=store.reset(&scope,first.clone()).unwrap();assert_eq!(reset.java_source().unwrap(),first.shell.unwrap().start.unwrap().files["Main.java"]);
}
#[test]
fn missing_empty_unicode_and_option_shaped_program_arguments_keep_real_java_semantics(){
    let mut exercise=lesson().tasks[3].git_terminal.clone().unwrap();
    let source=exercise.shell.as_ref().unwrap().goal.files["Main.java"].clone();
    exercise.shell.as_mut().unwrap().start=Some(molip_quest::git_practice::ShellSnapshot{files:std::collections::BTreeMap::from([("Main.java".into(),source)]),..Default::default()});
    let p=GitPractice::new(exercise).unwrap();let(mut terminal,mut out)=open(&p);wait(&p,&mut terminal,&mut out,|s|s.contains("$ "));
    for command in ["java Main.java","java Main.java ''","java Main.java '첫 값ह'","java Main.java -Xmx1m","java -Xmx1m Main.java"]{run(&p,&mut terminal,&mut out,command);}
    let log=std::fs::read_to_string(p.root().join("java-invocations.jsonl")).unwrap();
    let records:Vec<serde_json::Value>=log.lines().map(|s|serde_json::from_str(s).unwrap()).collect();
    assert_eq!(records.len(),4,"launcher options before the entry point are rejected");
    assert_eq!(records[0]["success"],false);assert!(records[0]["stderr"].as_str().unwrap().contains("ArrayIndexOutOfBoundsException"));
    assert_eq!(records[1]["args"][2],"");assert_eq!(records[1]["stdout"],"\n");
    assert_eq!(records[2]["args"][2],"첫 값ह");assert_eq!(records[2]["stdout"],"첫 값ह\n");
    assert_eq!(records[3]["stdout"],"-Xmx1m\n");assert_eq!(records[3]["success"],true);
    assert!(!p.check_exercise().unwrap().passed,"other arguments must not pass this step");
    terminal.shutdown().unwrap();
}
#[test]
fn compiled_entry_and_the_grading_copy_receive_the_same_program_argument(){
    let mut exercise=lesson().tasks[3].git_terminal.clone().unwrap();
    let shell=exercise.shell.as_mut().unwrap();
    shell.start=Some(shell.goal.clone());
    shell.commands=vec!["javac Main.java".into(),"java Main '첫 값ह'".into()];
    let goal=exercise.java_build.as_mut().unwrap();
    goal.command=vec!["java".into(),"Main".into(),"첫 값ह".into()];
    goal.stdout="첫 값ह\n".into();goal.class_output=Some("첫 값ह\n".into());
    let commands=exercise.shell.as_ref().unwrap().commands.clone();
    let p=GitPractice::new(exercise).unwrap();let(mut terminal,mut out)=open(&p);wait(&p,&mut terminal,&mut out,|s|s.contains("$ "));
    for command in &commands{run(&p,&mut terminal,&mut out,command);}
    let class=std::fs::read(p.work().join("Main.class")).unwrap();
    let report=p.check_exercise().unwrap();assert!(report.passed,"{}",serde_json::to_string(&report).unwrap());
    assert_eq!(std::fs::read(p.work().join("Main.class")).unwrap(),class);terminal.shutdown().unwrap();
}
#[test]
fn unicode_transport_preserves_all_program_arguments_without_rewriting_the_source(){
    let p=GitPractice::new(lesson().tasks[0].git_terminal.clone().unwrap()).unwrap();
    let player=Path::new(env!("CARGO_BIN_EXE_molip-quest"));p.prepare_java_launcher(player).unwrap();
    let source="class Main { public static void main(String[] args) { System.out.println(args.length); for (String value : args) System.out.println(\"[\" + value + \"]\"); } }";
    p.save_java_source(source).unwrap();
    // Invoke the same private CLI directly so the test isolates the JDK boundary
    // from MSYS/ConPTY's separate handling of supplementary UTF-16 characters.
    let values=["첫 값🍀","","quote\" slash\\ newline\n","@not-an-argument-file","-Xmx1m"];
    let output=std::process::Command::new(player).arg("--mq-java-practice").arg(p.root()).args(["java","Main.java"]).args(values).output().unwrap();
    assert!(output.status.success(),"{}",String::from_utf8_lossy(&output.stderr));
    let expected=format!("{}\n{}",values.len(),values.iter().map(|s|format!("[{s}]\n")).collect::<String>());
    assert_eq!(String::from_utf8(output.stdout).unwrap().replace("\r\n","\n"),expected);
    assert_eq!(p.java_source().unwrap(),source);assert!(!p.work().join("Main.class").exists());
    let record:serde_json::Value=serde_json::from_str(std::fs::read_to_string(p.root().join("java-invocations.jsonl")).unwrap().lines().last().unwrap()).unwrap();
    assert_eq!(record["args"],serde_json::json!(["java","Main.java",values[0],values[1],values[2],values[3],values[4]]));
}
