#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitExercise,GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::time::{Duration,Instant};
fn until(shell:&GitPractice,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,predicate:impl Fn(&str)->bool)->String {
    let deadline=Instant::now()+Duration::from_secs(12);let mut text=String::new();
    while Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        if predicate(&text){return text;}
        std::thread::sleep(Duration::from_millis(20));
    }
    panic!("PTY timeout: {text:?}; records {:?}",shell.shell_completions().unwrap());
}
fn play(practice:&GitPractice,shell:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,actions:&[serde_json::Value]) {
    for action in actions {
        match action["action"].as_str().unwrap() {
            "bash_command"=>{
                let command=action["command"].as_str().unwrap();let before=practice.shell_completions().unwrap().len();
                shell.input(&format!("{command}\r")).unwrap();
                until(practice,output,|_|practice.shell_completions().unwrap().iter().skip(before).any(|r|r.success&&r.command==command));
            },
            "vim_open"=>{
                shell.input("vim memo.txt\r").unwrap();
                until(practice,output,|text|text.contains("\"memo.txt\"")&&text.contains("L"));
            },
            "vim_keys"=>{
                let before=practice.shell_completions().unwrap().len();shell.input(action["keys"].as_str().unwrap()).unwrap();
                if action["wait_prompt"]==true {until(practice,output,|_|practice.shell_completions().unwrap().iter().skip(before).any(|r|r.success&&r.command=="vim memo.txt"));}
                else {std::thread::sleep(Duration::from_millis(70));while output.try_recv().is_ok(){}}
            },
            _=>{}
        }
    }
}
#[test]
fn all_twenty_three_steps_run_in_real_bash_and_vim_without_hidden_student_changes() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/부/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/bash-basics.json"),&manifest.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),23);
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let mut prior_root=None;let mut saved=None;
    for (index,task) in lesson.tasks.iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();let config=exercise.shell.as_ref().unwrap();let scope=exercise.workspace_scope("user:course:lesson:full:bash-practice");
        let practice=store.open(&scope,exercise.clone()).unwrap();
        if let Some(path)=&prior_root{assert_eq!(practice.root(),path);}
        assert!(!practice.work().join(".git").exists());
        for (name,body) in &config.demo.files {assert_eq!(std::fs::read_to_string(practice.work().join(name)).unwrap(),*body,"step {index} must resume previous files");}
        assert!(!practice.check_exercise().unwrap().passed,"unexecuted commands must not pass step {}",index+1);
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();
        let (mut teacher_shell,mut teacher_output)=teacher.open_terminal().unwrap();
        until(&teacher,&mut teacher_output,|text|text.ends_with("$ "));
        assert!(!teacher.check_exercise().unwrap().passed,"preparing demo state cannot satisfy command goals");
        if index==1 {
            play(&teacher,&mut teacher_shell,&mut teacher_output,&task.narration);
            let report=teacher.check_exercise().unwrap();assert!(report.passed,"teacher step {}: {:?}",index+1,serde_json::to_string(&report).unwrap());
        }
        teacher_shell.shutdown().unwrap();drop(teacher_output);
        let (mut shell,mut output)=practice.open_terminal().unwrap();until(&practice,&mut output,|text|text.ends_with("$ "));
        let actual_cwd=practice.shell_directory().unwrap().canonicalize().unwrap();
        assert_eq!(actual_cwd,practice.work().join(&config.demo.cwd).canonicalize().unwrap(),"restore current folder");
        play(&practice,&mut shell,&mut output,&task.narration);
        let report=practice.check_exercise().unwrap();assert!(report.passed,"student step {}: {:?}",index+1,serde_json::to_string(&report).unwrap());
        shell.shutdown().unwrap();drop(output);
        prior_root=Some(practice.root().to_path_buf());saved=Some((scope,exercise));
    }
    let (scope,exercise)=saved.unwrap();let resumed=store.open(&scope,exercise).unwrap();assert!(resumed.check_exercise().unwrap().passed);
    assert_eq!(std::fs::read_to_string(resumed.work().join("memo.txt")).unwrap(),"첫 메모\n둘째 줄\n");
    assert_eq!(std::fs::read_to_string(resumed.work().join("notes/memo.txt")).unwrap(),"첫 메모\n둘째 줄\n");
    assert!(!resumed.work().join("storage/archive").exists());
}
#[test]
fn shell_validation_rejects_escaping_paths_and_invalid_commands() {
    for value in [serde_json::json!({"initial_history":"uninitialized","shell":{"step_id":"a","goal":{"cwd":"../outside"},"demo":{},"commands":["pwd"]}}),serde_json::json!({"initial_history":"uninitialized","shell":{"step_id":"a","goal":{},"demo":{},"commands":["pwd\nls"]}})] {
        let exercise:GitExercise=serde_json::from_value(value).unwrap();assert!(exercise.validate().is_err());
    }
}
