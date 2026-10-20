//! Editor-reported state, not guessed key presses, drives interactive Vim lessons.
use super::*;
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct VimSnapshot {
    #[serde(default)] pub file_lines:Option<Vec<String>>,
    #[serde(default)] pub lines:Vec<String>,
    #[serde(default="normal_mode")] pub mode:String,
    #[serde(default="one")] pub line:usize,
    #[serde(default="one")] pub column:usize,
    #[serde(default)] pub modified:bool,
    #[serde(default)] pub search:String,
}
fn one()->usize{1}fn normal_mode()->String{"n".into()}
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct VimPredicate {
    #[serde(default,skip_serializing_if="Option::is_none")] pub mode:Option<String>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub line:Option<usize>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub column:Option<usize>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub lines:Option<Vec<String>>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub modified:Option<bool>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub event:Option<String>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub exited:Option<bool>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub search:Option<String>,
}
#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
pub struct VimCheck {pub label:String,pub state:VimPredicate}
#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct VimExercise {
    pub step_id:String,
    pub checks:Vec<VimCheck>,
    pub demo:VimSnapshot,
    #[serde(default,skip_serializing_if="Option::is_none")] pub start:Option<VimSnapshot>,
    #[serde(default,skip_serializing_if="Option::is_none")] pub final_file:Option<Vec<String>>,
}
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
pub struct VimState {
    pub session:String,pub sequence:usize,pub event:String,pub mode:String,pub line:usize,pub column:usize,
    pub lines:Vec<String>,pub modified:bool,pub save_count:usize,pub search:String,pub exited:bool,pub interactive:bool,
}
#[derive(Clone,Debug,Default,Serialize,Deserialize,PartialEq)]
pub struct VimProgress {pub state:Option<VimState>,pub checks:Vec<(String,bool)>,pub passed:bool}
impl VimExercise {
    pub fn validate(&self)->Result<(),String> {
        if self.step_id.is_empty()||self.step_id.len()>80||!self.step_id.bytes().all(|b|b.is_ascii_alphanumeric()||b"_-".contains(&b))||self.checks.is_empty()||self.checks.len()>20{return Err("Vim 스텝의 확인 기준을 확인하세요.".into())}
        for check in &self.checks {
            let p=&check.state;
            if check.label.is_empty()||check.label.len()>500||p==&VimPredicate::default()||p.mode.as_ref().is_some_and(|s|!["n","i","v","c"].contains(&s.as_str()))||p.line==Some(0)||p.column==Some(0){return Err("Vim 상태 조건을 확인하세요.".into())}
            if let Some(lines)=&p.lines{validate_lines(lines)?;}
        }
        for snapshot in [&self.demo].into_iter().chain(self.start.iter()) {validate_lines(&snapshot.lines)?;if let Some(lines)=&snapshot.file_lines{validate_lines(lines)?;}if snapshot.line==0||snapshot.column==0||!["n","i"].contains(&snapshot.mode.as_str()){return Err("Vim 시작 위치를 확인하세요.".into())}}
        if let Some(lines)=&self.final_file{validate_lines(lines)?;}Ok(())
    }
}
fn validate_lines(lines:&[String])->Result<(),String>{if lines.is_empty()||lines.len()>500||lines.iter().any(|s|s.len()>4000||s.contains(['\n','\r','\0'])){Err("Vim 메모 내용을 확인하세요.".into())}else{Ok(())}}
impl VimPredicate {
    fn matches(&self,state:&VimState)->bool {
        self.mode.as_ref().is_none_or(|v|v==&state.mode)&&self.line.is_none_or(|v|v==state.line)&&self.column.is_none_or(|v|v==state.column)&&self.lines.as_ref().is_none_or(|v|v==&state.lines)&&self.modified.is_none_or(|v|v==state.modified)&&self.event.as_ref().is_none_or(|v|v==&state.event)&&self.exited.is_none_or(|v|v==state.exited)&&self.search.as_ref().is_none_or(|v|v==&state.search)
    }
}
impl GitPractice {
    fn vim_token(&self)->Result<String,String> {
        let token=std::fs::read_to_string(self.root().join("vim-active-session")).map_err(|e|e.to_string())?;
        if token.len()!=32||!token.bytes().all(|b|b.is_ascii_hexdigit()){return Err("Vim 실습 세션을 확인하세요.".into())}Ok(token)
    }
    fn vim_path(&self,token:&str,suffix:&str)->PathBuf{self.root().join(format!("vim-{token}.{suffix}"))}
    pub(super) fn prepare_vim_start(&self)->Result<(),String> {
        if let Some(start)=self.exercise.vim.as_ref().and_then(|v|v.start.as_ref()) {
            if let Some(lines)=&start.file_lines{self.write("memo.txt",&(lines.join("\n")+"\n"))?;}
            std::fs::write(self.root().join("vim-initial.json"),serde_json::to_vec(start).unwrap()).map_err(|e|e.to_string())?;
        }Ok(())
    }
    pub fn open_vim_terminal(&self)->Result<(crate::setup_terminal::SetupTerminal,tokio::sync::mpsc::Receiver<Vec<u8>>),String> {
        let config=self.exercise.vim.as_ref().ok_or("Vim 실습이 아니에요.")?;
        let token=crate::issue_progress::new_id();
        let resume=if let Some(start)=&config.start {start.clone()} else if let Ok(raw)=std::fs::read_to_string(self.root().join("vim-resume.json")) {
            let state:VimState=serde_json::from_str(&raw).map_err(|e|e.to_string())?;
            if state.exited {self.vim_file_snapshot()?}else{VimSnapshot{file_lines:None,lines:state.lines,mode:if state.mode=="i"{"i".into()}else{"n".into()},line:state.line,column:state.column,modified:state.modified,search:state.search}}
        }else if let Ok(raw)=std::fs::read(self.root().join("vim-initial.json")){serde_json::from_slice(&raw).map_err(|e|e.to_string())?}else{self.vim_file_snapshot()?};
        let mut environment=self.environment();
        for (name,path) in [("MQ3_VIM_ACTIVE",self.root().join("vim-active-session")),("MQ3_VIM_RESUME",self.root().join("vim-resume.json")),("MQ3_VIM_STATE",self.vim_path(&token,"json")),("MQ3_VIM_EVENTS",self.vim_path(&token,"jsonl")),("MQ3_VIM_CLOSING",self.vim_path(&token,"closing")),("MQ3_VIM_INPUT",self.vim_path(&token,"input")),("MQ3_VIM_START",self.vim_path(&token,"start"))] {environment.push((name.into(),path.to_string_lossy().replace('\\',"/")));}
        environment.push(("MQ3_VIM_SESSION".into(),token.clone()));
        std::fs::write(self.vim_path(&token,"start"),serde_json::to_vec(&resume).unwrap()).map_err(|e|e.to_string())?;
        std::fs::write(self.root().join("vim-active-session"),&token).map_err(|e|e.to_string())?;
        let script=self.root().join("vim-practice.vim");std::fs::write(&script,include_str!("../assets/vim/practice.vim")).map_err(|e|e.to_string())?;
        crate::setup_terminal::SetupTerminal::open_vim(&self.work(),&environment,&script,"memo.txt")
    }
    fn vim_file_snapshot(&self)->Result<VimSnapshot,String> {
        let raw=match std::fs::read_to_string(self.work().join("memo.txt")){Ok(s)=>Some(s),Err(e) if e.kind()==std::io::ErrorKind::NotFound=>None,Err(e)=>return Err(e.to_string())};
        let file_lines=raw.map(|s|s.strip_suffix('\n').unwrap_or(&s).split('\n').map(str::to_owned).collect::<Vec<_>>());
        Ok(VimSnapshot{lines:file_lines.clone().unwrap_or_else(||vec![String::new()]),file_lines,mode:"n".into(),line:1,column:1,modified:false,search:String::new()})
    }
    pub fn note_vim_input(&self)->Result<(),String>{if self.exercise.vim.is_some(){let token=self.vim_token()?;let path=self.vim_path(&token,"input");if !path.exists(){std::fs::write(path,"").map_err(|e|e.to_string())?;}}Ok(())}
    pub fn vim_closing_marker(&self)->Option<PathBuf>{self.exercise.vim.as_ref()?;let token=self.vim_token().ok()?;Some(self.vim_path(&token,"closing"))}
    pub fn prepare_terminal_shutdown(&self)->Result<(),String>{if self.exercise.vim.is_some(){let token=self.vim_token()?;std::fs::write(self.vim_path(&token,"closing"),"").map_err(|e|e.to_string())?;}Ok(())}
    pub fn vim_progress(&self)->Result<VimProgress,String> {
        let config=self.exercise.vim.as_ref().ok_or("Vim 실습이 아니에요.")?;
        let Ok(token)=self.vim_token() else{return Ok(VimProgress{checks:config.checks.iter().map(|c|(c.label.clone(),false)).collect(),..Default::default()})};
        let raw=match std::fs::read_to_string(self.vim_path(&token,"jsonl")){Ok(s) if s.len()<=4_000_000=>s,Ok(_)=>return Err("Vim 상태 기록이 너무 많아요. 실습을 다시 여세요.".into()),Err(e) if e.kind()==std::io::ErrorKind::NotFound=>String::new(),Err(e)=>return Err(e.to_string())};
        let mut cursor=0;let mut latest=None;
        for line in raw.lines(){
            let Ok(state)=serde_json::from_str::<VimState>(line) else{continue};
            if state.session!=token{continue;}
            if state.interactive {
                // A write can prove both the resulting buffer and its saved state.
                // Do not require a preceding change/timer event for stable facts.
                // An action event itself still counts only once (e.g. two writes).
                let mut event_used=false;
                while let Some(check)=config.checks.get(cursor) {
                    if (event_used&&check.state.event.is_some())||!check.state.matches(&state){break;}
                    event_used|=check.state.event.is_some();
                    cursor+=1;
                }
            }
            latest=Some(state);
        }
        let file_ok=if let Some(lines)=&config.final_file{std::fs::read_to_string(self.work().join("memo.txt")).is_ok_and(|s|s==lines.join("\n")+"\n")}else{true};
        Ok(VimProgress{state:latest,checks:config.checks.iter().enumerate().map(|(i,c)|(c.label.clone(),i<cursor)).collect(),passed:cursor==config.checks.len()&&file_ok})
    }
    pub fn check_vim(&self)->Result<crate::runner::TestReport,String> {
        use crate::runner::{TestReport,TestCaseResult};let config=self.exercise.vim.as_ref().ok_or("Vim 실습이 아니에요.")?;let progress=self.vim_progress()?;
        let mut cases=progress.checks.iter().map(|(label,passed)|TestCaseResult{input:label.clone(),expected:"Vim에서 실제로 수행하세요.".into(),stdout:if *passed{"확인했어요."}else{"아직 확인하지 못했어요."}.into(),stderr:String::new(),passed:*passed,state:"vim_state".into()}).collect::<Vec<_>>();
        if let Some(lines)=&config.final_file{let actual=std::fs::read_to_string(self.work().join("memo.txt")).unwrap_or_default();cases.push(TestCaseResult{input:"저장한 파일".into(),expected:lines.join("\n")+"\n",passed:actual==lines.join("\n")+"\n",stdout:actual,stderr:String::new(),state:"vim_file".into()});}
        Ok(TestReport{passed:progress.passed,cases})
    }
}
