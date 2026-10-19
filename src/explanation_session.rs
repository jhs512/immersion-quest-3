//! The explanation lifetime owns a complete learner workspace, not a second list
//! of fields for every caller to copy and restore.
use dioxus::prelude::*;

#[derive(Clone)]
pub struct TaskWorkspace {
    pub code:String,
    pub example_source:String,
    pub input:String,
    pub output:String,
    pub preview:String,
    pub artifacts:Vec<molip_quest::runner::Artifact>,
    pub message:String,
    pub feedback:&'static str,
    pub execution_state:&'static str,
    pub execution_seconds:u64,
    pub execution_id:u64,
    pub reset:u64,
    pub busy:bool,
    pub narrating:bool,
    pub teacher_preview:String,
}
impl TaskWorkspace {
    pub fn new(code:String,example_source:String,input:String)->Self {
        Self{code,example_source,input,output:String::new(),preview:String::new(),artifacts:vec![],message:String::new(),feedback:"idle",execution_state:"idle",execution_seconds:0,execution_id:0,reset:0,busy:false,narrating:false,teacher_preview:String::new()}
    }
}
#[derive(Clone)]
struct SavedWorkspace { owner:String, student:TaskWorkspace, git:bool }
#[derive(Clone,Copy)]
pub struct ExplanationSession { workspace:Signal<TaskWorkspace>,saved:Signal<Option<SavedWorkspace>> }
impl ExplanationSession {
    pub fn owner(&self)->String {self.saved.read().as_ref().map(|saved|saved.owner.clone()).unwrap_or_default()}
    pub fn begin(&mut self,code:String,example:String,input:String,git:bool)->Option<String> {
        if self.saved.peek().is_some(){return None;}
        let owner=molip_quest::issue_progress::new_id();
        let student=(self.workspace)();
        self.saved.set(Some(SavedWorkspace{owner:owner.clone(),student,git}));
        self.workspace.with_mut(|state|{
            state.code=code;
            if !git {state.example_source=example;state.input=input;state.reset+=1;}
            state.teacher_preview.clear();state.feedback="idle";state.narrating=true;
        });
        Some(owner)
    }
    /// A late completion from a retired explanation cannot restore over a new one.
    pub fn finish(&mut self,owner:&str)->bool {
        if self.saved.peek().as_ref().is_none_or(|saved|saved.owner!=owner){return false;}
        let saved=self.saved.write().take().unwrap();
        let execution_id=self.workspace.peek().execution_id+1;
        let reset=self.workspace.peek().reset+u64::from(!saved.git);
        let mut restored=saved.student;
        restored.execution_id=execution_id;restored.reset=reset;restored.busy=false;restored.narrating=false;restored.teacher_preview.clear();
        self.workspace.set(restored);true
    }
}
pub fn use_workspace(initial:TaskWorkspace)->(Signal<TaskWorkspace>,ExplanationSession) {
    let workspace=use_signal(||initial);
    let saved=use_signal(||None::<SavedWorkspace>);
    (workspace,ExplanationSession{workspace,saved})
}
