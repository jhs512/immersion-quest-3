//! Final challenges of the terminal lessons (Bash, Vim, Java launcher, Git) graded by the real
//! runtimes. For each lesson's designated challenge: the start state fails, the teacher narration
//! replayed in its own isolated demonstration passes, every recorded equivalent answer passes and
//! every recorded wrong answer or bypass fails. Each attempt starts from the challenge's own start
//! state, without any earlier step (the learner can open the challenge directly).
//! Cases: tests/final-challenge-cases/<key>.json (written by tools/apply-final-challenges.py).
//! Evidence with the lesson hash: target/final-challenges/<key>.json.
#![cfg(not(target_os="android"))]
use molip_quest::{git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson,Task},setup_terminal::SetupTerminal};
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{path::{Path,PathBuf},time::{Duration,Instant}};

type Output=tokio::sync::mpsc::Receiver<Vec<u8>>;
const ROOT:&str=env!("CARGO_MANIFEST_DIR");

struct Loaded {lesson:Lesson,task:Task,sha:String,cases:Value}

fn load(key:&str)->Loaded {
    let raw=std::fs::read(Path::new(ROOT).join(format!("courses/redesigned/{key}.json"))).unwrap();
    let sha=format!("{:x}",Sha256::digest(&raw));
    // The fixture course that pins exactly this lesson version.
    let manifest=std::fs::read_dir(Path::new(ROOT).join("tests/fixtures/player-pilot")).unwrap()
        .filter_map(|entry|std::fs::read_to_string(entry.unwrap().path().join("course.json")).ok())
        .filter_map(|text|CourseManifest::parse(&text).ok())
        .find(|course|course.lessons.len()==1&&course.lessons[0].revision.strip_prefix(&format!("{key}-")).is_some_and(|n|!n.is_empty()&&n.bytes().all(|b|b.is_ascii_digit()))).expect("fixture course");
    assert_eq!(manifest.lessons[0].sha256,sha,"{key}: fixture pins other lesson bytes");
    let lesson=Lesson::parse(std::str::from_utf8(&raw).unwrap(),&manifest.lessons[0]).unwrap();
    let cases:Value=serde_json::from_str(&std::fs::read_to_string(Path::new(ROOT).join(format!("tests/final-challenge-cases/{key}.json"))).unwrap()).unwrap();
    let task=lesson.tasks.iter().find(|t|t.id==cases["step"].as_str().unwrap()).expect("challenge step").clone();
    assert_eq!(lesson.tasks.last().unwrap().id,task.id,"{key}: the challenge is the last step");
    assert!(task.required);
    let exercise=task.git_terminal.as_ref().unwrap();
    assert!(exercise.workspace_group.is_empty(),"{key}: the challenge starts from its own state, not a shared workspace");
    Loaded{lesson,task,sha,cases}
}

fn pump(terminal:&mut SetupTerminal,out:&mut Output,text:&mut String,dsr:&mut usize) {
    while let Ok(bytes)=out.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
    let count=text.matches("\x1b[6n").count();
    while *dsr<count {terminal.input("\x1b[1;1R").unwrap();*dsr+=1;}
}

struct Pty {terminal:SetupTerminal,out:Output,text:String,dsr:usize}
impl Pty {
    fn open(practice:&GitPractice,vim:bool)->Self {
        let (terminal,out)=practice.open_terminal_with_player(Path::new(env!("CARGO_BIN_EXE_molip-quest"))).unwrap();
        let mut pty=Pty{terminal,out,text:String::new(),dsr:0};
        if !vim {pty.until(practice,|text,_|text.contains("$ "));}
        pty
    }
    fn until(&mut self,practice:&GitPractice,done:impl Fn(&str,&GitPractice)->bool) {
        let started=Instant::now();
        while started.elapsed()<Duration::from_secs(40) {
            pump(&mut self.terminal,&mut self.out,&mut self.text,&mut self.dsr);
            if done(&self.text,practice){return;}
            std::thread::sleep(Duration::from_millis(20));
        }
        panic!("terminal timeout: {:?}; records {:?}",self.text,practice.shell_completions());
    }
    /// Type one command and wait until the shell returns to its prompt for it.
    fn command(&mut self,practice:&GitPractice,command:&str) {
        let before=practice.shell_completions().unwrap().len();
        self.terminal.input(&format!("{command}\r")).unwrap();
        self.until(practice,|_,p|p.shell_completions().unwrap().iter().skip(before).any(|r|r.command==command));
    }
    fn vim(&mut self,practice:&GitPractice,keys:&str) {
        self.until(practice,|_,p|p.vim_progress().unwrap().state.is_some());
        practice.note_vim_input().unwrap();self.terminal.input(keys).unwrap();
        std::thread::sleep(Duration::from_millis(150));
        self.until(practice,|_,p|p.vim_progress().unwrap().state.is_some());
    }
    fn close(mut self,practice:&GitPractice) {
        practice.prepare_terminal_shutdown().ok();
        // A final :wq/:q ends Vim; give its exit event a moment to land before closing.
        let started=Instant::now();
        while started.elapsed()<Duration::from_millis(400){pump(&mut self.terminal,&mut self.out,&mut self.text,&mut self.dsr);std::thread::sleep(Duration::from_millis(20));}
        self.terminal.shutdown().unwrap();
    }
}

fn git_bash()->PathBuf {
    #[cfg(windows)] {molip_quest::setup_terminal::git_bash_executable().unwrap()}
    #[cfg(not(windows))] {PathBuf::from("/bin/bash")}
}
/// Run one command line in real Bash inside the Git practice, as the learner's terminal would.
fn bash(practice:&GitPractice,command:&str)->bool {
    let environment=practice.environment();let shell=git_bash();
    let inherited=environment.iter().find(|(k,_)|k=="PATH").map(|(_,v)|std::ffi::OsString::from(v)).unwrap_or_else(||std::env::var_os("PATH").unwrap_or_default());
    let path=std::env::join_paths(shell.parent().map(Path::to_path_buf).into_iter().chain(std::env::split_paths(&inherited))).unwrap();
    let mut cmd=std::process::Command::new(&shell);
    cmd.args(["--noprofile","--norc","-c",command]).current_dir(practice.work()).envs(environment).env("PATH",path)
        .env("GIT_TRACE2_EVENT",practice.root().join("commands.jsonl")).env("GIT_EDITOR","true");
    #[cfg(target_os="macos")] cmd.env("LC_CTYPE","en_US.UTF-8");
    #[cfg(windows)] {use std::os::windows::process::CommandExt;cmd.creation_flags(0x08000000);cmd.env("LC_CTYPE","C.UTF-8");}
    cmd.output().unwrap().status.success()
}
fn quote(value:&str)->String {format!("'{}'",value.replace('\'',"'\\''"))}

enum Kind {Shell,Java,Vim,Git}
fn kind(task:&Task)->Kind {
    let e=task.git_terminal.as_ref().unwrap();
    if e.vim.is_some(){Kind::Vim}else if e.java_build.is_some(){Kind::Java}else if e.shell.is_some(){Kind::Shell}else{Kind::Git}
}

/// Replay the learner-visible teacher narration against a demonstration practice.
fn teacher(task:&Task)->GitPractice {
    let demo=GitPractice::new(task.git_terminal.clone().unwrap().demonstration()).unwrap();
    match kind(task) {
        Kind::Git=>{
            for a in &task.narration {
                let line=match a["action"].as_str().unwrap() {
                    "git_command"=>format!("git {}",a["args"].as_array().unwrap().iter().map(|v|quote(v.as_str().unwrap())).collect::<Vec<_>>().join(" ")),
                    "bash_command"=>a["command"].as_str().unwrap().to_owned(),
                    _=>continue,
                };
                let ok=bash(&demo,&line);
                assert_eq!(ok,a["expected_exit"]!=1,"{}: teacher command {line}",task.title);
            }
        },
        _=>{
            let mut pty=Pty::open(&demo,matches!(kind(task),Kind::Vim));
            let mut source=task.git_terminal.as_ref().unwrap().java_build.as_ref().map(|_|demo.java_source().unwrap());
            for a in &task.narration {
                match a["action"].as_str().unwrap() {
                    "patch_code"=>{let s=source.as_mut().unwrap();assert_eq!(s.matches(a["before"].as_str().unwrap()).count(),1);
                        *s=s.replacen(a["before"].as_str().unwrap(),a["after"].as_str().unwrap(),1);demo.save_java_source(s).unwrap();},
                    "bash_command"=>{
                        let command=a["command"].as_str().unwrap();pty.command(&demo,command);
                        let record=demo.shell_completions().unwrap().into_iter().rev().find(|r|r.command==command).unwrap();
                        assert_eq!(record.success,a["fails"]!=true,"{}: teacher command {command}",task.title);
                    },
                    "vim_keys"=>pty.vim(&demo,a["keys"].as_str().unwrap()),
                    _=>{},
                }
            }
            if let Kind::Vim=kind(task){pty.until(&demo,|_,p|p.vim_progress().unwrap().passed);}
            pty.close(&demo);
        },
    }
    demo
}

/// One learner attempt from the challenge's own start state, in a fresh owned store.
fn attempt(task:&Task,cases:&Value,steps:&[Value])->(bool,Value) {
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let exercise=task.git_terminal.clone().unwrap();
    let practice=store.open(&format!("challenge:{}",task.id),exercise).unwrap();
    assert!(!practice.check_exercise().unwrap().passed,"{}: the start state must not pass",task.title);
    match kind(task) {
        Kind::Git=>{for step in steps {bash(&practice,step.as_str().unwrap());}},
        Kind::Vim=>{let mut pty=Pty::open(&practice,true);for step in steps {pty.vim(&practice,step.as_str().unwrap());}
            // Give the last write/exit time to be recorded before grading.
            let started=Instant::now();while started.elapsed()<Duration::from_secs(3)&&!practice.vim_progress().unwrap().passed{std::thread::sleep(Duration::from_millis(50));}
            pty.close(&practice);},
        _=>{let mut pty=Pty::open(&practice,false);
            for step in steps {let step=step.as_str().unwrap();
                if let Some(name)=step.strip_prefix("SAVE:"){practice.save_java_source(cases["sources"][name].as_str().unwrap()).unwrap();}else{pty.command(&practice,step);}}
            pty.close(&practice);},
    }
    let report=practice.check_exercise().unwrap();
    (report.passed,serde_json::to_value(&report.cases).unwrap())
}

fn verify(key:&str) {
    let started=Instant::now();
    let Loaded{lesson,task,sha,cases}=load(key);
    let demo=teacher(&task);
    let report=demo.check_exercise().unwrap();assert!(report.passed,"{key}: teacher narration: {}",serde_json::to_string(&report).unwrap());
    let mut accepted=vec![];let mut rejected=vec![];
    for case in cases["accept"].as_array().unwrap() {
        let (passed,detail)=attempt(&task,&cases,case["steps"].as_array().unwrap());
        assert!(passed,"{key}: valid answer rejected: {}: {detail}",case["reason"]);
        accepted.push(json!({"reason":case["reason"],"steps":case["steps"]}));
        eprintln!("{key}: accepted as expected: {}",case["reason"]);
    }
    for case in cases["reject"].as_array().unwrap() {
        let (passed,detail)=attempt(&task,&cases,case["steps"].as_array().unwrap());
        assert!(!passed,"{key}: wrong answer accepted: {}",case["reason"]);
        let failed:Vec<_>=detail.as_array().unwrap().iter().filter(|c|c["passed"]==false).map(|c|c["input"].clone()).collect();
        rejected.push(json!({"reason":case["reason"],"steps":case["steps"],"failed_checks":failed}));
        eprintln!("{key}: rejected as expected: {}",case["reason"]);
    }
    let evidence=json!({"passed":true,"lesson":lesson.id,"revision":lesson.revision,"lesson_sha256":sha,"challenge_task":task.id,
        "runtime":match kind(&task){Kind::Shell=>"bash",Kind::Java=>"bash+jdk",Kind::Vim=>"vim",Kind::Git=>"git+bash"},
        "start_state_fails":true,"teacher_narration_passes":true,"accepted_answers":accepted,"rejected_answers":rejected,
        "seconds":started.elapsed().as_secs_f64(),"native_ui_verified":false,"voice_listened":false});
    let path=Path::new(ROOT).join(format!("target/final-challenges/{key}.json"));
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path,serde_json::to_vec_pretty(&evidence).unwrap()).unwrap();
}

#[test] fn bash_basics_final_challenge(){verify("bash-basics");}
#[test] fn vim_basics_final_challenge(){verify("vim-basics");}
#[test] fn java_launch_final_challenge(){verify("java-launch");}
#[test] fn java_arguments_final_challenge(){verify("java-arguments");}
#[test] fn git_first_final_challenge(){verify("git-first");}
#[test] fn git_branch_final_challenge(){verify("git-branch");}
#[test] fn git_remote_final_challenge(){verify("git-remote");}
#[test] fn git_branch_advanced_final_challenge(){verify("git-branch-advanced");}
