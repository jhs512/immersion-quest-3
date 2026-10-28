//! Typing into the real practice terminal (PTY Bash) like a learner, for Docker CLI and Compose steps.
//! Shared by examples/validate_redesigned_lesson.rs and tests/docker_cli_terminal.rs.
#![allow(dead_code)]
use molip_quest::{docker_lab::{LessonSession,TerminalLab},git_practice::{DockerExercise,GitPractice,GitPracticeStore},repository_course::Task,setup_terminal::SetupTerminal};
use std::time::{Duration,Instant};

pub struct Terminal {pub shell:SetupTerminal,output:tokio::sync::mpsc::Receiver<Vec<u8>>,raw:String,dsr:usize}
/// Terminal text without colour and cursor sequences.
pub fn plain(text:&str)->String {
    let ansi=regex::Regex::new(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b[()][A-Z0-9]|\x1b[=>]").unwrap();
    ansi.replace_all(text,"").replace('\r',"")
}
impl Terminal {
    pub fn open(practice:&GitPractice,lab:&TerminalLab)->Result<Self,String> {
        let (shell,output)=practice.open_docker_terminal(lab)?;
        // Wide enough that the real docker ps table is not wrapped by the PTY.
        shell.resize(50,300)?;
        let mut terminal=Self{shell,output,raw:String::new(),dsr:0};
        terminal.until(30,"first prompt",|text|text.trim_end().ends_with('$'))?;
        Ok(terminal)
    }
    fn pump(&mut self) {
        while let Ok(bytes)=self.output.try_recv(){self.raw.push_str(&String::from_utf8_lossy(&bytes));}
        let count=self.raw.matches("\x1b[6n").count();
        if count>self.dsr{let _=self.shell.input("\x1b[1;1R");self.dsr=count;}
    }
    pub fn until(&mut self,seconds:u64,what:&str,ready:impl Fn(&str)->bool)->Result<String,String> {
        let deadline=Instant::now()+Duration::from_secs(seconds);
        loop {
            self.pump();
            let text=plain(&self.raw);
            if ready(&text){return Ok(text)}
            if Instant::now()>deadline{return Err(format!("{what}: terminal shows {text:?}"))}
            std::thread::sleep(Duration::from_millis(30));
        }
    }
    /// Type a command and press Enter like a learner (the app first checks a Compose step's files,
    /// as the player does right before Enter). `success`: the exit status the shell must record;
    /// None accepts either. Returns what the terminal printed for it.
    pub fn type_line(&mut self,practice:&GitPractice,command:&str,success:Option<bool>)->Result<String,String> {
        let before=practice.shell_completions()?.len();
        let mark=plain(&self.raw).len();
        practice.refresh_docker_files()?;
        self.shell.input(&format!("{command}\r"))?;
        let deadline=Instant::now()+Duration::from_secs(900);
        loop {
            self.pump();
            if let Some(record)=practice.shell_completions()?.iter().skip(before).find(|r|r.command==command) {
                if success.is_some_and(|s|record.success!=s) {return Err(format!("{command}: expected success={success:?}: {}",plain(&self.raw)))}
                break
            }
            if Instant::now()>deadline {return Err(format!("{command} did not finish: {}",plain(&self.raw)))}
            std::thread::sleep(Duration::from_millis(30));
        }
        let text=self.until(10,"prompt after the command",|text|text.trim_end().ends_with('$'))?;
        Ok(text[mark.min(text.len())..].to_owned())
    }
    pub fn enter(&mut self,practice:&GitPractice,command:&str,success:bool)->Result<String,String> {self.type_line(practice,command,Some(success))}
    pub fn close(mut self)->Result<(),String> {self.shell.shutdown()}
}

pub fn step(task:&Task)->String {task.git_terminal.as_ref().and_then(|e|e.shell.as_ref()).map(|s|s.step_id.clone()).unwrap_or_default()}
pub fn docker_goal(task:&Task)->DockerExercise {task.git_terminal.as_ref().unwrap().docker.clone().unwrap()}
/// The practice folder scope the player uses: the lesson's shared workspace group, or the step itself.
pub fn scope_of(base:&str,task:&Task)->String {
    let exercise=task.git_terminal.as_ref().unwrap();
    exercise.workspace_scope(&format!("{base}:{}",if exercise.workspace_group.is_empty(){&task.id}else{&exercise.workspace_group}))
}
pub fn is_compose(task:&Task)->bool {task.git_terminal.as_ref().and_then(|e|e.docker.as_ref()).is_some_and(|d|d.compose.is_some())}

/// The step's solution files (`shell.goal`), with replacements applied to whichever editable file
/// contains each `before` exactly once.
pub fn goal_files(task:&Task,replacements:&[[String;2]])->Result<Vec<(String,String)>,String> {
    let exercise=task.git_terminal.as_ref().ok_or("not a terminal step")?;
    let editable=exercise.docker.as_ref().and_then(|d|d.compose.as_ref()).map(|c|c.editable.clone()).unwrap_or_default();
    let goal=&exercise.shell.as_ref().ok_or("no shell exercise")?.goal.files;
    let mut files:Vec<(String,String)>=editable.iter().map(|name|(name.clone(),goal.get(name).cloned().unwrap_or_default())).collect();
    for [before,after] in replacements {
        let owner=files.iter_mut().filter(|(_,text)|text.matches(before.as_str()).count()==1).collect::<Vec<_>>();
        let [file]=owner.try_into().map_err(|_|format!("replacement is not unique in one file: {before}"))?;
        file.1=file.1.replacen(before.as_str(),after,1);
    }
    Ok(files)
}

/// A learner in a fresh state of this step (new practice folder, new Compose project after
/// 초기화) who writes `files` (None: keeps the start files) in the editor and types the solution's
/// commands, whatever each one's exit status. Returns the grading report.
pub fn attempt(session:&LessonSession,store:&GitPracticeStore,scope:&str,task:&Task,files:Option<&[(String,String)]>)->Result<molip_quest::runner::TestReport,String> {
    let exercise=task.git_terminal.clone().ok_or("not a terminal step")?;
    let practice=store.reset_step(&scope_of(scope,task),exercise.clone(),&step(task))?;
    session.reset_terminal(&step(task))?;
    let lab=session.terminal(false,&step(task),&docker_goal(task))?;
    let mut terminal=Terminal::open(&practice,&lab)?;
    for (name,text) in files.unwrap_or_default() {practice.save_editable(name,text)?;}
    for command in task.solution.lines() {terminal.type_line(&practice,command,None)?;}
    let report=practice.check_exercise()?;
    terminal.close()?;
    Ok(report)
}

/// A learner who types the step's solution commands in the lesson's own terminal (after writing
/// the solution files of a Compose step in the editor), then the narration in its separate
/// project. Returns the narration's printed outputs and the grading report.
pub fn replay(session:&LessonSession,store:&GitPracticeStore,scope:&str,task:&Task)->Result<(Vec<String>,molip_quest::runner::TestReport),String> {
    let exercise=task.git_terminal.clone().ok_or("not a terminal step")?;
    let practice=store.open(&scope_of(scope,task),exercise.clone())?;
    let lab=session.terminal(false,&step(task),&docker_goal(task))?;
    let mut terminal=Terminal::open(&practice,&lab)?;
    if practice.check_exercise()?.passed {return Err(format!("{}: passes before any command",task.title))}
    for (name,text) in goal_files(task,&[])? {practice.save_editable(&name,&text)?;}
    for command in task.solution.lines() {terminal.enter(&practice,command,true)?;}
    let report=practice.check_exercise()?;
    terminal.close()?;
    if !report.passed {return Err(format!("{}: typed solution failed: {}",task.title,serde_json::to_string(&report).unwrap()))}
    let teacher=GitPractice::new(exercise.demonstration())?;
    let demo=session.terminal(true,&step(task),&docker_goal(task))?;
    let mut shown=Terminal::open(&teacher,&demo)?;
    let mut outputs=vec![];
    for action in &task.narration {
        if action["action"]=="patch_code" {
            // The narration edits its own editor, which saves the file in its own folder.
            let file=action["file"].as_str().map(str::to_owned).or_else(||teacher.editable_files().first().cloned()).ok_or("patch without an editable file")?;
            let text=teacher.read_editable(&file)?;
            let before=action["before"].as_str().ok_or("patch before")?;
            if text.matches(before).count()!=1 {return Err(format!("{}: narration patch is not unique in {file}",task.title))}
            teacher.save_editable(&file,&text.replacen(before,action["after"].as_str().ok_or("patch after")?,1))?;
        }
        if action["action"]=="bash_command" {
            let command=action["command"].as_str().ok_or("missing command")?;
            let printed=shown.enter(&teacher,command,action["fails"]!=true)?;
            outputs.push(printed.trim_end().trim_end_matches('$').trim_end().to_owned());
        }
    }
    let demonstrated=teacher.check_exercise()?;
    shown.close()?;
    if !demonstrated.passed {return Err(format!("{}: narration does not reach the goal: {}",task.title,serde_json::to_string(&demonstrated).unwrap()))}
    Ok((outputs,report))
}
