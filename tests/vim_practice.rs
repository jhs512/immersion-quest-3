#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitPractice,GitPracticeStore,VimProgress},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::time::{Duration,Instant};
fn wait(practice:&GitPractice,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,test:impl Fn(&VimProgress)->bool)->VimProgress {
    let end=Instant::now()+Duration::from_secs(8);let mut text=String::new();
    while Instant::now()<end {
        while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let state=practice.vim_progress().unwrap();if test(&state){return state;}
        std::thread::sleep(Duration::from_millis(25));
    }
    panic!("Vim state timeout: {:?}; output {text:?}",practice.vim_progress().unwrap());
}
fn send(practice:&GitPractice,shell:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,keys:&str) {
    practice.note_vim_input().unwrap();shell.input(keys).unwrap();std::thread::sleep(Duration::from_millis(130));while output.try_recv().is_ok(){}
}
fn play(practice:&GitPractice,shell:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,task:&molip_quest::repository_course::Task,arrows:bool) {
    for action in &task.narration {
        if action["action"]=="vim_keys" {
            let raw=action["keys"].as_str().unwrap();
            let raw=if arrows {match raw{"gg"=>"\x1b[A","j"=>"\x1b[B",s=>s}}else{raw};
            send(practice,shell,output,raw);
        }
    }
    let progress=wait(practice,output,|p|p.passed);assert!(progress.passed);
}
#[test]
fn real_vim_checks_modes_buffers_cursor_undo_search_saving_and_exit_live() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/브/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/vim-basics.json"),&manifest.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),14);
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();let mut previous_root=None;
    for (index,task) in lesson.tasks.iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();let scope=exercise.workspace_scope("user:course:vim:full");
        let student=store.open(&scope,exercise.clone()).unwrap();
        if let Some(path)=&previous_root{assert_eq!(student.root(),path);}
        assert!(!student.work().join(".git").exists());
        let before=std::fs::read(student.work().join("memo.txt")).ok();
        let resume_before=std::fs::read(student.root().join("vim-resume.json")).ok();
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();let (mut demo,mut demo_output)=teacher.open_terminal().unwrap();
        wait(&teacher,&mut demo_output,|p|p.state.is_some());assert!(!teacher.check_exercise().unwrap().passed,"preparing the editor cannot solve a step");
        play(&teacher,&mut demo,&mut demo_output,task,false);
        teacher.prepare_terminal_shutdown().unwrap();demo.shutdown().unwrap();drop(demo_output);
        assert_eq!(std::fs::read(student.work().join("memo.txt")).ok(),before,"demonstration changed learner files");
        assert_eq!(std::fs::read(student.root().join("vim-resume.json")).ok(),resume_before,"demo changed unsaved student buffer");
        let (mut editor,mut output)=student.open_terminal().unwrap();
        let opened=wait(&student,&mut output,|p|p.state.is_some());assert!(!opened.passed,"student step {index} starts unperformed");
        if index==1 {wait(&student,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"));}
        if index==2 {let initial=opened.state.unwrap();assert_eq!(initial.lines,["첫 메모"]);assert!(initial.modified);assert!(!student.work().join("memo.txt").exists(),"unsaved text must not be secretly written");}
        play(&student,&mut editor,&mut output,task,index==4);
        assert!(student.check_exercise().unwrap().passed,"step {}",index+1);
        student.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();drop(output);
        previous_root=Some(student.root().to_path_buf());
    }
    let last=store.open(&lesson.tasks[13].git_terminal.as_ref().unwrap().workspace_scope("user:course:vim:full"),lesson.tasks[13].git_terminal.clone().unwrap()).unwrap();
    assert_eq!(std::fs::read_to_string(last.work().join("memo.txt")).unwrap(),"완료 메모\n새 둘째 메모\n새 둘째 메모\n마지막 줄\n");
}

#[test]
fn simply_opening_and_quitting_does_not_satisfy_cursor_movement() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let practice=GitPractice::new(lesson.tasks[4].git_terminal.as_ref().unwrap().demonstration()).unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();wait(&practice,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,":q!\r");wait(&practice,&mut output,|p|p.state.as_ref().is_some_and(|s|s.exited));
    assert!(!practice.check_exercise().unwrap().passed);editor.shutdown().unwrap();
}
#[test]
fn unsaved_text_input_mode_and_cursor_survive_reopening() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();let exercise=lesson.tasks[0].git_terminal.clone().unwrap();
    let practice=store.open("vim-resume",exercise.clone()).unwrap();let (mut editor,mut output)=practice.open_terminal().unwrap();wait(&practice,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"i임시메모");send(&practice,&mut editor,&mut output,"\x1bhhi");
    wait(&practice,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"&&s.column==2));
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();drop(output);drop(practice);
    let reopened=store.open("vim-resume",exercise).unwrap();let (mut editor,mut output)=reopened.open_terminal().unwrap();
    let resumed=wait(&reopened,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"));let state=resumed.state.unwrap();
    assert_eq!(state.lines,["임시메모"]);assert_eq!(state.column,2);assert!(state.modified);assert!(!reopened.work().join("memo.txt").exists());
    send(&reopened,&mut editor,&mut output,"X");assert_eq!(reopened.vim_progress().unwrap().state.unwrap().lines,["임X시메모"]);
    reopened.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
}
