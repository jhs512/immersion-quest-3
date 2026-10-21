#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitExercise,GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::time::{Duration,Instant};
fn until(shell:&GitPractice,terminal:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,predicate:impl Fn(&str)->bool)->String {
    let deadline=Instant::now()+Duration::from_secs(12);let mut text=String::new();let mut dsr=0;
    while Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let count=text.matches("\x1b[6n").count();if count>dsr{terminal.input("\x1b[1;1R").unwrap();dsr=count;}
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
                until(practice,shell,output,|_|practice.shell_completions().unwrap().iter().skip(before).any(|r|r.success&&r.command==command));
            },
            "vim_open"=>{
                shell.input("vim memo.txt\r").unwrap();
                until(practice,shell,output,|text|text.contains("\"memo.txt\"")&&text.contains("L"));
            },
            "vim_keys"=>{
                let before=practice.shell_completions().unwrap().len();shell.input(action["keys"].as_str().unwrap()).unwrap();
                if action["wait_prompt"]==true {until(practice,shell,output,|_|practice.shell_completions().unwrap().iter().skip(before).any(|r|r.success&&r.command=="vim memo.txt"));}
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
        until(&teacher,&mut teacher_shell,&mut teacher_output,|text|text.contains("$ "));
        assert!(!teacher.check_exercise().unwrap().passed,"preparing demo state cannot satisfy command goals");
        if index==1 {
            play(&teacher,&mut teacher_shell,&mut teacher_output,&task.narration);
            let report=teacher.check_exercise().unwrap();assert!(report.passed,"teacher step {}: {:?}",index+1,serde_json::to_string(&report).unwrap());
        }
        teacher_shell.shutdown().unwrap();drop(teacher_output);
        let (mut shell,mut output)=practice.open_terminal().unwrap();until(&practice,&mut shell,&mut output,|text|text.contains("$ "));
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

#[cfg(windows)]
#[test]
fn korean_windows_memo_encoding_does_not_abort_a_correct_submission() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/bash-basics.json")).unwrap();
    let task=lesson.tasks.iter().find(|t|t.git_terminal.as_ref().and_then(|g|g.shell.as_ref()).is_some_and(|s|s.goal.files.get("memo.txt").is_some_and(|text|text=="첫 메모\n")&&s.commands.iter().any(|c|c.contains("> memo.txt")))).unwrap();let practice=GitPractice::new(task.git_terminal.clone().unwrap().demonstration()).unwrap();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
    play(&practice,&mut terminal,&mut output,&task.narration);
    assert!(practice.check_exercise().unwrap().passed);
    // Existing Korean Windows workspaces can contain a CP949 echo redirection.
    let korean_cp949=[0xc3,0xb9,0x20,0xb8,0xde,0xb8,0xf0,0x0a];
    let log_path=practice.root().join("shell-commands.log");let mut log=std::fs::read(&log_path).unwrap();
    let position=log.windows("첫 메모".len()).position(|p|p=="첫 메모".as_bytes()).unwrap();
    log.splice(position..position+"첫 메모".len(),korean_cp949[..7].iter().copied());std::fs::write(log_path,&log).unwrap();
    assert!(practice.check_exercise().unwrap().passed,"existing CP949 command history must remain readable");
    let utf16=std::iter::once(vec![0xff,0xfe]).chain("첫 메모\r\n".encode_utf16().map(|u|u.to_le_bytes().to_vec())).flatten().collect::<Vec<_>>();
    for bytes in [korean_cp949.to_vec(),utf16,[vec![0xef,0xbb,0xbf],"첫 메모\r\n".as_bytes().to_vec()].concat()] {
        std::fs::write(practice.work().join("memo.txt"),&bytes).unwrap();
        let result=practice.check_exercise();
        assert!(result.is_ok(),"valid Korean text must not abort grading: {:?}",result.as_ref().err());
        let report=result.unwrap();assert!(report.passed,"the same Korean memo must pass: {}",serde_json::to_string(&report).unwrap());
        assert_eq!(std::fs::read(practice.work().join("memo.txt")).unwrap(),bytes);
    }
    std::fs::write(practice.work().join("memo.txt"),[0x81]).unwrap();
    let report=practice.check_exercise().expect("invalid text should give feedback instead of aborting grading");
    assert!(!report.passed);assert!(report.cases.iter().any(|c|!c.passed&&c.input=="파일 인코딩"));
    terminal.shutdown().unwrap();
}

#[cfg(windows)]
#[test]
fn practice_shell_uses_utf8_even_when_started_with_a_legacy_korean_locale(){
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/bash-basics.json")).unwrap();
    let practice=GitPractice::new(lesson.tasks[0].git_terminal.clone().unwrap().demonstration()).unwrap();
    let mut env=practice.environment();env.extend([("LC_ALL".into(),"ko_KR.CP949".into()),("LC_CTYPE".into(),"ko_KR.CP949".into()),("PS1".into(),"$ ".into())]);
    let (mut terminal,mut output)=SetupTerminal::open_practice(&practice.work(),&env).unwrap();
    until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
    terminal.input("locale charmap\r").unwrap();until(&practice,&mut terminal,&mut output,|text|text.contains("UTF-8"));
    terminal.input("echo \"첫 메모\" > memo.txt\r").unwrap();
    until(&practice,&mut terminal,&mut output,|_|std::fs::read(practice.work().join("memo.txt")).is_ok_and(|b|b=="첫 메모\n".as_bytes()));
    terminal.shutdown().unwrap();
}

#[cfg(windows)]
#[test]
fn resumed_legacy_korean_memo_can_be_appended_without_mixing_encodings(){
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/bash-basics.json")).unwrap();
    let task=&lesson.tasks[5];let practice=GitPractice::new(task.git_terminal.clone().unwrap().demonstration()).unwrap();
    let original=[0xc3,0xb9,0x20,0xb8,0xde,0xb8,0xf0,0x0a];std::fs::write(practice.work().join("memo.txt"),original).unwrap();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
    play(&practice,&mut terminal,&mut output,&task.narration);let report=practice.check_exercise().unwrap();terminal.shutdown().unwrap();
    assert!(report.passed,"resumed memo must remain editable: {}",serde_json::to_string(&report).unwrap());
    assert_eq!(std::fs::read(practice.work().join("memo.txt")).unwrap(),"첫 메모\n둘째 줄\n".as_bytes());
    assert!(std::fs::read_dir(practice.root().join("text-encoding-backups")).unwrap().filter_map(Result::ok).any(|f|std::fs::read(f.path()).ok().as_deref()==Some(original.as_slice())),"original bytes must be recoverable");
}

#[test]
fn step_eight_accepts_directory_slash_and_screen_clearing() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/부/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/bash-basics.json"),&manifest.lessons[0]).unwrap();
    for cd in ["cd notes", "cd notes/", "cd   ./notes/", "cd \"notes/\""] {
        let practice=GitPractice::new(lesson.tasks[7].git_terminal.clone().unwrap().demonstration()).unwrap();
        let (mut terminal,mut output)=practice.open_terminal().unwrap();
        until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
        terminal.input("cd missing-folder\r").unwrap();
        until(&practice,&mut terminal,&mut output,|_|practice.shell_completions().unwrap().iter().any(|r|r.command=="cd missing-folder"&&!r.success));
        let actions:Vec<_>=[cd,"pwd","ls","clear","pwd","ls"].iter().map(|command|serde_json::json!({"action":"bash_command","command":command})).collect();
        play(&practice,&mut terminal,&mut output,&actions);
        let report=practice.check_exercise().unwrap();
        assert!(report.passed,"{cd}: {}",serde_json::to_string(&report).unwrap());
        play(&practice,&mut terminal,&mut output,&[serde_json::json!({"action":"bash_command","command":"cd .."})]);
        assert!(!practice.check_exercise().unwrap().passed,"past correct commands cannot hide an incorrect final folder");
        play(&practice,&mut terminal,&mut output,&[serde_json::json!({"action":"bash_command","command":"cd notes/"}),serde_json::json!({"action":"bash_command","command":"pwd"}),serde_json::json!({"action":"bash_command","command":"ls"})]);
        assert!(practice.check_exercise().unwrap().passed,"correcting the final folder must allow a retry");
        terminal.shutdown().unwrap();
    }
}

#[test]
fn step_nine_accepts_trailing_spaces_in_successful_commands() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/부/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/bash-basics.json"),&manifest.lessons[0]).unwrap();
    let practice=GitPractice::new(lesson.tasks[8].git_terminal.clone().unwrap().demonstration()).unwrap();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
    play(&practice,&mut terminal,&mut output,&[
        serde_json::json!({"action":"bash_command","command":"echo \"폴더 안 메모\" > memo.txt"}),
        serde_json::json!({"action":"bash_command","command":"cat memo.txt "}),
    ]);
    let report=practice.check_exercise().unwrap();
    terminal.shutdown().unwrap();
    assert!(report.passed,"{}",serde_json::to_string(&report).unwrap());
}

#[test]
fn step_fifteen_accepts_directory_slash_and_later_inspection_retries() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/부/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/bash-basics.json"),&manifest.lessons[0]).unwrap();
    let practice=GitPractice::new(lesson.tasks[14].git_terminal.clone().unwrap().demonstration()).unwrap();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
    let commands=["cp memo.txt notes/","ls notes/","cat notes/memo.txt ","ls notes/","ls notes"];
    let actions:Vec<_>=commands.iter().map(|command|serde_json::json!({"action":"bash_command","command":command})).collect();
    play(&practice,&mut terminal,&mut output,&actions);
    let report=practice.check_exercise().unwrap();
    terminal.shutdown().unwrap();
    assert!(report.passed,"{}",serde_json::to_string(&report).unwrap());
}

#[test]
fn step_twenty_three_accepts_recursive_force_and_trailing_directory_slashes() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/부/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/bash-basics.json"),&manifest.lessons[0]).unwrap();
    let practice=GitPractice::new(lesson.tasks[22].git_terminal.clone().unwrap().demonstration()).unwrap();
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    until(&practice,&mut terminal,&mut output,|text|text.contains("$ "));
    let actions:Vec<_>=["ls storage/archive/","rm -rf storage/archive/","ls storage/"].iter().map(|command|serde_json::json!({"action":"bash_command","command":command})).collect();
    play(&practice,&mut terminal,&mut output,&actions);
    let report=practice.check_exercise().unwrap();
    assert!(report.passed,"{}",serde_json::to_string(&report).unwrap());
    // Matching command history cannot hide damage to the preserved original.
    std::fs::write(practice.work().join("notes/memo.txt"),"changed original\n").unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
    terminal.shutdown().unwrap();
}
