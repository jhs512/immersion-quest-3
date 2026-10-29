#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitPractice,GitPracticeStore,VimProgress},repository_course::{CourseManifest,Lesson},setup_terminal::SetupTerminal};
use std::time::{Duration,Instant};
fn wait(practice:&GitPractice,_terminal:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,test:impl Fn(&VimProgress)->bool)->VimProgress {
    let end=Instant::now()+Duration::from_secs(8);let mut text=String::new();
    // Windows ConPTY waits for a startup CPR before Vim can publish any state.
    // macOS Vim instead treats this fabricated response as F3 in Insert mode.
    #[cfg(windows)] let mut dsr=0;
    while Instant::now()<end {
        while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let state=practice.vim_progress().unwrap();
        #[cfg(windows)] {
            let count=text.matches("\x1b[6n").count();
            if count>dsr {
                for _ in dsr..count {_terminal.input("\x1b[1;1R").unwrap();}
            }
            dsr=count;
        }
        if test(&state){return state;}
        std::thread::sleep(Duration::from_millis(25));
    }
    panic!("Vim state timeout: {:?}; output {text:?}",practice.vim_progress().unwrap());
}
fn send(practice:&GitPractice,shell:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,keys:&str) {
    // Service ConPTY cursor-position requests before and after typing, even
    // after Vim has published ready. Discarding output can deadlock the editor.
    wait(practice,shell,output,|p|p.state.is_some());
    practice.note_vim_input().unwrap();shell.input(keys).unwrap();std::thread::sleep(Duration::from_millis(130));
    wait(practice,shell,output,|p|p.state.is_some());
}
fn play(practice:&GitPractice,shell:&mut SetupTerminal,output:&mut tokio::sync::mpsc::Receiver<Vec<u8>>,task:&molip_quest::repository_course::Task,arrows:bool) {
    for action in &task.narration {
        if action["action"]=="vim_keys" {
            let raw=action["keys"].as_str().unwrap();
            let raw=if arrows {match raw{"gg"=>"\x1b[A","j"=>"\x1b[B",s=>s}}else{raw};
            send(practice,shell,output,raw);
        }
    }
    let progress=wait(practice,shell,output,|p|p.passed);assert!(progress.passed);
}
#[test]
fn real_vim_checks_modes_buffers_cursor_undo_search_saving_and_exit_live() {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/브/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/vim-basics.json"),&manifest.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),15);// The last step is the separately started final challenge (tests/final_terminal_challenges.rs).
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();let mut previous_root=None;
    for (index,task) in lesson.tasks[..14].iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();let scope=exercise.workspace_scope("user:course:vim:full");
        let student=store.open(&scope,exercise.clone()).unwrap();
        if let Some(path)=&previous_root{assert_eq!(student.root(),path);}
        assert!(!student.work().join(".git").exists());
        let before=std::fs::read(student.work().join("memo.txt")).ok();
        let resume_before=std::fs::read(student.root().join("vim-resume.json")).ok();
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();let (mut demo,mut demo_output)=teacher.open_terminal().unwrap();
        wait(&teacher,&mut demo,&mut demo_output,|p|p.state.is_some());assert!(!teacher.check_exercise().unwrap().passed,"preparing the editor cannot solve a step");
        play(&teacher,&mut demo,&mut demo_output,task,false);
        teacher.prepare_terminal_shutdown().unwrap();demo.shutdown().unwrap();drop(demo_output);
        assert_eq!(std::fs::read(student.work().join("memo.txt")).ok(),before,"demonstration changed learner files");
        assert_eq!(std::fs::read(student.root().join("vim-resume.json")).ok(),resume_before,"demo changed unsaved student buffer");
        let (mut editor,mut output)=student.open_terminal().unwrap();
        let opened=wait(&student,&mut editor,&mut output,|p|p.state.is_some());assert!(!opened.passed,"student step {index} starts unperformed");
        if index==1 {wait(&student,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"));}
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
    let (mut editor,mut output)=practice.open_terminal().unwrap();wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,":q!\r");wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.exited));
    assert!(!practice.check_exercise().unwrap().passed);editor.shutdown().unwrap();
}
#[test]
fn unsaved_text_input_mode_and_cursor_survive_reopening() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();let exercise=lesson.tasks[0].git_terminal.clone().unwrap();
    let practice=store.open("vim-resume",exercise.clone()).unwrap();let (mut editor,mut output)=practice.open_terminal().unwrap();wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"i임시메모");send(&practice,&mut editor,&mut output,"\x1bhhi");
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"&&s.column==2));
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();drop(output);drop(practice);
    let reopened=store.open("vim-resume",exercise).unwrap();let (mut editor,mut output)=reopened.open_terminal().unwrap();
    let resumed=wait(&reopened,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"));let state=resumed.state.unwrap();
    assert_eq!(state.lines,["임시메모"]);assert_eq!(state.column,2);assert!(state.modified);assert!(!reopened.work().join("memo.txt").exists());
    send(&reopened,&mut editor,&mut output,"X");
    let typed=wait(&reopened,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.lines==["임X시메모"]));
    assert_eq!(typed.state.unwrap().lines,["임X시메모"]);
    reopened.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
}

#[test]
fn shutdown_mode_changes_cannot_overwrite_the_saved_insert_state() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let practice=GitPractice::new(lesson.tasks[0].git_terminal.clone().unwrap()).unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();
    wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"i임시메모");
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"&&s.lines==["임시메모"]));
    let path=practice.root().join("vim-resume.json");
    // The resume file is written separately from the live state; snapshot it only after it
    // holds the typed Insert-mode buffer and has stopped changing (CI read an earlier write).
    let settle=Instant::now()+Duration::from_secs(8);
    let mut before=Vec::new();
    loop {
        let current=std::fs::read(&path).unwrap_or_default();
        let text=String::from_utf8_lossy(&current);
        if current==before&&text.contains(r#""lines":["임시메모"]"#)&&text.contains(r#""mode":"i""#){break}
        assert!(Instant::now()<settle,"resume file never recorded the typed Insert state: {text}");
        before=current;std::thread::sleep(Duration::from_millis(150));
    }
    practice.prepare_terminal_shutdown().unwrap();
    // Windows process termination may leave Insert mode before Vim exits.
    // Reproduce that transition deterministically instead of racing process kill.
    editor.input("\x1b").unwrap();
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="n"));
    std::thread::sleep(Duration::from_millis(180));
    assert_eq!(std::fs::read(&path).unwrap(),before,"closing must freeze the learner's resume state before terminal teardown changes mode");
    editor.shutdown().unwrap();
    let (mut reopened,mut reopened_output)=practice.open_terminal().unwrap();
    let resumed=wait(&practice,&mut reopened,&mut reopened_output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"));
    let state=resumed.state.unwrap();
    assert_eq!(state.lines,["임시메모"]);assert_eq!(state.column,5);assert!(state.modified);
    assert!(!practice.work().join("memo.txt").exists(),"resuming must not save the unsaved buffer to disk");
    send(&practice,&mut reopened,&mut reopened_output,"X");
    wait(&practice,&mut reopened,&mut reopened_output,|p|p.state.as_ref().is_some_and(|s|s.lines==["임시메모X"]));
    practice.prepare_terminal_shutdown().unwrap();reopened.shutdown().unwrap();
}

#[test]
fn step_six_accepts_typing_and_saving_without_waiting_between_actions() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let practice=GitPractice::new(lesson.tasks[5].git_terminal.as_ref().unwrap().demonstration()).unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();
    wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"I새 \x1b:w\r");
    let state=wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.save_count>0));
    assert!(state.passed,"rapid save must count all state goals: {state:?}");
    assert_eq!(std::fs::read_to_string(practice.work().join("memo.txt")).unwrap(),"첫 메모\n새 둘째 메모\n");
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
}

#[test]
fn step_six_saved_content_does_not_require_a_separate_change_notification() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let practice=GitPractice::new(lesson.tasks[5].git_terminal.as_ref().unwrap().demonstration()).unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();
    wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"I새 \x1b:w\r");
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.save_count>0));
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
    let token=std::fs::read_to_string(practice.root().join("vim-active-session")).unwrap();
    let events=practice.root().join(format!("vim-{token}.jsonl"));
    let log=std::fs::read_to_string(&events).unwrap();
    // A completed write proves both the resulting text and that it was saved.
    // No intermediate editor repaint or timer notification should be required.
    let saves=log.lines().filter(|line|serde_json::from_str::<serde_json::Value>(line).unwrap()["event"]=="write").collect::<Vec<_>>();
    assert_eq!(saves.len(),1);
    std::fs::write(&events,saves.join("\n")+"\n").unwrap();
    let report=practice.check_exercise().unwrap();
    assert!(report.passed,"a correct saved file must satisfy both checks: {}",serde_json::to_string(&report).unwrap());
}

#[test]
fn one_save_cannot_satisfy_two_required_write_actions() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let mut exercise=lesson.tasks[5].git_terminal.as_ref().unwrap().demonstration();
    let vim=exercise.vim.as_mut().unwrap();
    let save=vim.checks[1].clone();vim.checks=vec![save.clone(),save];
    let practice=GitPractice::new(exercise).unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();
    wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"I새 \x1b:w\r");
    let state=wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.save_count==1));
    assert!(!state.passed,"one write is not two actions");
    send(&practice,&mut editor,&mut output,":w\r");
    wait(&practice,&mut editor,&mut output,|p|p.passed);
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
}

// Windows CI: the live state reached Insert mode but the reopened editor resumed in Normal mode — the last
// resume update was lost. Another process briefly holding vim-resume.json (on-access scanning) makes Vim's
// rename fail; nothing retried it, because the next state had the same signature.
#[cfg(windows)]
#[test]
fn a_briefly_locked_resume_file_still_receives_the_latest_insert_state() {
    use std::os::windows::fs::OpenOptionsExt;
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();let exercise=lesson.tasks[0].git_terminal.clone().unwrap();
    let practice=store.open("vim-locked-resume",exercise.clone()).unwrap();let (mut editor,mut output)=practice.open_terminal().unwrap();wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"i임시메모");send(&practice,&mut editor,&mut output,"\x1bhh");
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="n"&&s.column==2));
    let resume=practice.root().join("vim-resume.json");
    let settle=Instant::now()+Duration::from_secs(8);
    while !std::fs::read_to_string(&resume).unwrap_or_default().contains("\"column\":2")&&Instant::now()<settle{std::thread::sleep(Duration::from_millis(25));}
    // Share read/write, not delete: renaming over the file fails while this handle is open.
    let lock=std::fs::OpenOptions::new().read(true).share_mode(0x1|0x2).open(&resume).unwrap();
    send(&practice,&mut editor,&mut output,"i");
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"&&s.column==2));
    std::thread::sleep(Duration::from_millis(300));drop(lock);
    let settle=Instant::now()+Duration::from_secs(3);
    while !std::fs::read_to_string(&resume).unwrap_or_default().contains("\"mode\":\"i\"")&&Instant::now()<settle{std::thread::sleep(Duration::from_millis(25));}
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();drop(output);drop(practice);
    let reopened=store.open("vim-locked-resume",exercise).unwrap();let (mut editor,mut output)=reopened.open_terminal().unwrap();
    // A stale resume file reopens in Normal mode, and this wait times out showing it.
    let state=wait(&reopened,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i")).state.unwrap();
    assert_eq!((state.column,state.lines.clone()),(2,vec!["임시메모".to_string()]));
    reopened.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
}

// Windows CI (run 40208488444): step 6 reopened on line 1 although step 5 had ended on line 2, so "I새 "
// edited the first line. Vim replaces vim-resume.json by delete+rename and only retries a failed replace
// on its 80 ms timer; closing the editor before that retry left the previous cursor (or no file at all).
// Hold the file so every replace fails until the editor is gone, then require the latest learner state.
#[cfg(windows)]
#[test]
fn closing_while_the_resume_file_is_held_still_resumes_the_latest_cursor() {
    use std::os::windows::fs::OpenOptionsExt;
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();let exercise=lesson.tasks[4].git_terminal.clone().unwrap();
    let practice=store.open("vim-held-resume",exercise.clone()).unwrap();
    std::fs::write(practice.work().join("memo.txt"),"첫 메모\n둘째 메모\n").unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();wait(&practice,&mut editor,&mut output,|p|p.state.is_some());
    send(&practice,&mut editor,&mut output,"j");
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.line==2));
    let resume=practice.root().join("vim-resume.json");
    let settle=Instant::now()+Duration::from_secs(8);
    while !std::fs::read_to_string(&resume).unwrap_or_default().contains("\"line\":2")&&Instant::now()<settle{std::thread::sleep(Duration::from_millis(25));}
    assert!(std::fs::read_to_string(&resume).unwrap().contains("\"line\":2"));
    // Share read/write, not delete: Vim's replace of the resume file fails while this handle is open.
    let lock=std::fs::OpenOptions::new().read(true).share_mode(0x1|0x2).open(&resume).unwrap();
    send(&practice,&mut editor,&mut output,"k");
    let moved=wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.line==1&&s.mode=="n"));
    std::thread::sleep(Duration::from_millis(300));
    practice.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();drop(output);drop(lock);
    let reopened=store.open("vim-held-resume",exercise).unwrap();let (mut editor,mut output)=reopened.open_terminal().unwrap();
    let state=wait(&reopened,&mut editor,&mut output,|p|p.state.is_some()).state.unwrap();
    let live=moved.state.unwrap();
    assert_eq!((state.line,state.column,state.lines.clone()),(live.line,live.column,live.lines.clone()),"reopening must use the learner's last cursor, not a stale resume file");
    reopened.prepare_terminal_shutdown().unwrap();editor.shutdown().unwrap();
}

// Teardown (notably ConPTY) may leave Insert mode after the app asked the editor to close. That transition is
// not the learner pressing Esc, so it must not complete "returned to Normal mode".
#[test]
fn leaving_insert_mode_during_teardown_does_not_count_as_the_learners_escape() {
    let lesson:Lesson=serde_json::from_str(include_str!("../courses/redesigned/vim-basics.json")).unwrap();
    let practice=GitPractice::new(lesson.tasks[1].git_terminal.as_ref().unwrap().demonstration()).unwrap();
    let (mut editor,mut output)=practice.open_terminal().unwrap();
    wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="i"));
    send(&practice,&mut editor,&mut output,"첫 메모");
    let typed=wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.lines==["첫 메모"]));
    assert_eq!(typed.checks.iter().map(|c|c.1).collect::<Vec<_>>(),[true,false]);
    practice.prepare_terminal_shutdown().unwrap();
    editor.input("\x1b").unwrap();
    let closed=wait(&practice,&mut editor,&mut output,|p|p.state.as_ref().is_some_and(|s|s.mode=="n"&&s.closing));
    assert!(!closed.passed,"a teardown mode change is not the learner's Esc: {closed:?}");
    editor.shutdown().unwrap();
}
