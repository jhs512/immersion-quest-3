//! Editable names belong to (repository, GitHub identity, course), never a lesson.
use crate::{github_player::{Github,GithubUser,Issue},issue_progress};
use rusqlite::{params,Connection};
use serde::{Deserialize,Serialize};
use serde_json::json;
use std::{path::{Path,PathBuf},sync::{Mutex,OnceLock},collections::HashMap,time::Duration};

#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
pub struct Enrollment {pub user_id:u64,pub course_id:String,pub name:String,pub revision:String,pub updated_at:u64}
#[derive(Clone,Debug,PartialEq)]
pub struct NameState {pub name:String,pub pending:bool,pub problem:String}
#[derive(Clone)]
pub struct Store {path:PathBuf}
#[derive(Clone)]
struct Pending {repo:String,profile:Enrollment,expected:String}
pub fn normalize(name:&str)->Result<String,String>{
    let name:String=name.chars().filter(|c|!c.is_whitespace()).collect();
    if name.is_empty()||name.chars().count()>80||name.chars().any(|c|c.is_control()||matches!(c,'<'|'>')) {return Err("이름을 1~80자로 입력하세요. 꺾쇠는 쓸 수 없어요.".into());}
    Ok(name)
}
pub fn from_issue(issue:&Issue,course_id:&str)->Option<Enrollment>{
    let raw=issue.body.as_ref()?.split("<!-- mq3-enrollment:").nth(1)?.split(" -->").next()?;
    let profile:Enrollment=serde_json::from_str(raw).ok()?;
    (profile.user_id==issue.user.id&&profile.course_id==course_id&&normalize(&profile.name).ok().as_deref()==Some(profile.name.as_str())&&!profile.revision.is_empty()).then_some(profile)
}
fn remote(github:&Github,repo:&str,user:&GithubUser,course:&str)->Result<Option<(Issue,Enrollment)>,String>{
    Ok(github.issues(repo,user)?.into_iter().filter_map(|issue|from_issue(&issue,course).map(|profile|(issue,profile))).min_by_key(|(issue,_)|issue.number))
}
impl Store {
    pub fn new(path:&Path)->Self{Self{path:path.into()}}
    pub fn installed()->Result<Self,String>{Ok(Self::new(&crate::data_dir()?.join("course-names.sqlite3")))}
    fn db(&self)->Result<Connection,String>{
        let db=Connection::open(&self.path).map_err(|e|e.to_string())?;db.busy_timeout(Duration::from_secs(5)).map_err(|e|e.to_string())?;
        db.execute_batch("CREATE TABLE IF NOT EXISTS names(repository TEXT NOT NULL,user_id TEXT NOT NULL,course_id TEXT NOT NULL,document TEXT NOT NULL,expected TEXT NOT NULL,pending INTEGER NOT NULL,problem TEXT NOT NULL DEFAULT '',PRIMARY KEY(repository,user_id,course_id));").map_err(|e|e.to_string())?;Ok(db)
    }
    fn local(&self,repo:&str,user:u64,course:&str)->Result<Option<(Enrollment,bool,String)>,String>{
        use rusqlite::OptionalExtension;
        let row:Option<(String,bool,String)>=self.db()?.query_row("SELECT document,pending,problem FROM names WHERE repository=?1 AND user_id=?2 AND course_id=?3",params![repo,user.to_string(),course],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional().map_err(|e|e.to_string())?;
        row.map(|(raw,pending,problem)|Ok((serde_json::from_str(&raw).map_err(|e|e.to_string())?,pending,problem))).transpose()
    }
    pub fn state(&self,repo:&str,user:u64,course:&str)->Result<Option<NameState>,String>{Ok(self.local(repo,user,course)?.map(|(p,pending,problem)|NameState{name:p.name,pending,problem}))}
    fn lock(&self,user:u64)->Result<std::fs::File,String>{
        let file=std::fs::OpenOptions::new().read(true).write(true).create(true).truncate(false).open(self.path.with_extension(format!("{user}.lock"))).map_err(|e|e.to_string())?;
        file.lock().map_err(|e|e.to_string())?;Ok(file)
    }
    pub(crate) fn accept(&self,repo:&str,profile:&Enrollment,replace_pending:bool)->Result<(),String>{
        self.db()?.execute("INSERT INTO names VALUES(?1,?2,?3,?4,?5,0,'') ON CONFLICT(repository,user_id,course_id) DO UPDATE SET document=excluded.document,expected=excluded.expected,pending=0,problem='' WHERE names.pending=0 OR ?6",params![repo,profile.user_id.to_string(),profile.course_id,serde_json::to_string(profile).map_err(|e|e.to_string())?,profile.revision,replace_pending]).map_err(|e|e.to_string())?;Ok(())
    }
    pub fn load(&self,github:&Github,repo:&str,user:&GithubUser,course:&str,discard_pending:bool)->Result<Option<NameState>,String>{
        let _lock=self.lock(user.id)?;
        github.ensure_user(user.id)?;
        match remote(github,repo,user,course){
            Ok(Some((_,profile)))=>self.accept(repo,&profile,discard_pending)?,
            Ok(None)=>{},
            Err(error)=>if self.local(repo,user.id,course)?.is_none(){return Err(error)},
        }
        self.state(repo,user.id,course)
    }
    pub fn queue(&self,repo:&str,user:&GithubUser,course:&str,name:&str)->Result<NameState,String>{
        if !crate::repository_course::valid_repository(repo)||course.is_empty(){return Err("코스를 확인하세요.".into());}
        let profile=Enrollment{user_id:user.id,course_id:course.into(),name:normalize(name)?,revision:issue_progress::new_id(),updated_at:issue_progress::now()};
        let mut db=self.db()?;let tx=db.transaction().map_err(|e|e.to_string())?;
        // Repeated offline edits retain the last acknowledged remote version.
        tx.execute("INSERT INTO names VALUES(?1,?2,?3,?4,'',1,'') ON CONFLICT(repository,user_id,course_id) DO UPDATE SET document=excluded.document,pending=1,problem=''",params![repo,user.id.to_string(),course,serde_json::to_string(&profile).map_err(|e|e.to_string())?]).map_err(|e|e.to_string())?;
        tx.commit().map_err(|e|e.to_string())?;Ok(NameState{name:profile.name,pending:true,problem:String::new()})
    }
    pub fn has_pending(&self)->Result<bool,String>{self.db()?.query_row("SELECT EXISTS(SELECT 1 FROM names WHERE pending=1 AND problem='')",[],|r|r.get(0)).map_err(|e|e.to_string())}
    fn pending(&self,user:u64)->Result<Vec<Pending>,String>{
        let db=self.db()?;let mut q=db.prepare("SELECT repository,document,expected FROM names WHERE user_id=?1 AND pending=1 AND problem='' ORDER BY course_id").map_err(|e|e.to_string())?;
        let rows=q.query_map([user.to_string()],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?,r.get::<_,String>(2)?))).map_err(|e|e.to_string())?;
        rows.map(|row|{let (repo,raw,expected)=row.map_err(|e|e.to_string())?;Ok(Pending{repo,profile:serde_json::from_str(&raw).map_err(|e|e.to_string())?,expected})}).collect()
    }
    fn acknowledge(&self,item:&Pending)->Result<(),String>{
        self.db()?.execute("UPDATE names SET expected=?4,pending=CASE WHEN json_extract(document,'$.revision')=?4 THEN 0 ELSE pending END,problem='' WHERE repository=?1 AND user_id=?2 AND course_id=?3 AND expected=?5",params![item.repo,item.profile.user_id.to_string(),item.profile.course_id,item.profile.revision,item.expected]).map_err(|e|e.to_string())?;Ok(())
    }
    pub fn sync(&self,github:&Github,user:&GithubUser)->Result<(),String>{
        let _lock=self.lock(user.id)?;let mut failure=None;
        for item in self.pending(user.id)? {
            if let Err(error)=self.sync_one(github,user,&item){failure=Some(error);}
        }
        failure.map_or(Ok(()),Err)
    }
    fn sync_one(&self,github:&Github,user:&GithubUser,item:&Pending)->Result<(),String>{
        github.ensure_user(user.id)?;
        let found=remote(github,&item.repo,user,&item.profile.course_id)?;
        if found.as_ref().is_some_and(|(_,p)|p.revision==item.profile.revision){return self.acknowledge(item);}
        if found.as_ref().map(|(_,p)|p.revision.as_str()).unwrap_or("")!=item.expected {
            let problem="다른 기기에서 이름이 바뀌었어요. 최신 이름을 불러온 뒤 수정하세요.";
            self.db()?.execute("UPDATE names SET problem=?4 WHERE repository=?1 AND user_id=?2 AND course_id=?3 AND json_extract(document,'$.revision')=?5",params![item.repo,user.id.to_string(),item.profile.course_id,problem,item.profile.revision]).map_err(|e|e.to_string())?;
            return Err(problem.into());
        }
        let profile=&item.profile;
        let body=format!("# 코스 등록\n\n이름: {}\n\n<!-- mq3-enrollment:{} -->",profile.name,serde_json::to_string(profile).map_err(|e|e.to_string())?);
        let endpoint=found.as_ref().map(|(issue,_)|format!("repos/{}/issues/{}",item.repo,issue.number)).unwrap_or_else(||format!("repos/{}/issues",item.repo));
        let method=if found.is_some(){"PATCH"}else{"POST"};
        let written:Issue=serde_json::from_value(crate::course_authoring::gh(&["api","--hostname","github.com","--method",method,&endpoint,"--input","-"],Some(json!({"title":format!("[등록] {} · @{}",profile.name,user.login),"body":body})))?).map_err(|e|e.to_string())?;
        if from_issue(&written,&profile.course_id).as_ref()!=Some(profile){return Err("저장한 이름을 확인하지 못했어요.".into());}
        self.acknowledge(item)
    }
}
/// Durable pending names retry separately from five-minute progress batches.
pub fn synchronize(github:Github,user:GithubUser)->Result<(),String>{
    let store=Store::installed()?;
    type Key=(PathBuf,u64);
    static WORKERS:OnceLock<Mutex<HashMap<Key,(u64,bool)>>>=OnceLock::new();
    let workers=WORKERS.get_or_init(Mutex::default);let key=(store.path.clone(),user.id);
    {let mut state=workers.lock().unwrap_or_else(|e|e.into_inner());let v=state.entry(key.clone()).or_default();v.0+=1;if v.1{return Ok(());}v.1=true;}
    let cleanup=key.clone();
    if let Err(error)=std::thread::Builder::new().name("course-name-sync".into()).spawn(move||loop{
        let generation=workers.lock().unwrap_or_else(|e|e.into_inner())[&key].0;
        let _=store.sync(&github,&user);
        let pending=store.pending(user.id).map(|p|!p.is_empty()).unwrap_or(true);
        {let mut state=workers.lock().unwrap_or_else(|e|e.into_inner());let v=state.get_mut(&key).unwrap();if !pending&&v.0==generation{v.1=false;break;}}
        std::thread::sleep(Duration::from_secs(30));
    }){if let Some(v)=workers.lock().unwrap_or_else(|e|e.into_inner()).get_mut(&cleanup){v.1=false;}return Err(error.to_string());}
    Ok(())
}

#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn names_are_normalized_and_scoped_and_survive_restart(){
        let dir=tempfile::tempdir().unwrap();let path=dir.path().join("names.db");let store=Store::new(&path);let user=GithubUser{id:7,login:"student".into()};
        assert_eq!(store.queue("owner/course-a",&user,"a"," [BE16]홍 길동 \t").unwrap().name,"[BE16]홍길동");
        store.queue("owner/course-b",&user,"b","다른이름").unwrap();
        let reopened=Store::new(&path);assert_eq!(reopened.state("owner/course-a",7,"a").unwrap().unwrap().name,"[BE16]홍길동");
        assert!(reopened.state("owner/course-a",8,"a").unwrap().is_none());assert!(reopened.state("owner/course-b",7,"a").unwrap().is_none());
        assert_eq!(normalize("\u{3000}홍\u{a0}길동").unwrap(),"홍길동");assert!(normalize(" \t").is_err());assert!(normalize("<script>").is_err());
    }
    #[test]fn older_remote_values_and_slow_acknowledgements_cannot_erase_pending_edits(){
        let dir=tempfile::tempdir().unwrap();let store=Store::new(&dir.path().join("names.db"));let user=GithubUser{id:7,login:"student".into()};
        let remote=Enrollment{user_id:7,course_id:"a".into(),name:"기존".into(),revision:"v1".into(),updated_at:1};store.accept("o/r",&remote,false).unwrap();
        store.queue("o/r",&user,"a","변경1").unwrap();let pending=store.pending(7).unwrap().pop().unwrap();assert_eq!(pending.expected,"v1");
        store.queue("o/r",&user,"a","변경2").unwrap();store.acknowledge(&pending).unwrap();store.accept("o/r",&remote,false).unwrap();
        assert_eq!(store.state("o/r",7,"a").unwrap().unwrap(),NameState{name:"변경2".into(),pending:true,problem:String::new()});
        store.accept("o/r",&remote,true).unwrap();assert!(!store.state("o/r",7,"a").unwrap().unwrap().pending);
    }
    #[test]fn registration_body_cannot_impersonate_another_user_or_course(){
        let profile=Enrollment{user_id:7,course_id:"a".into(),name:"홍길동".into(),revision:"v1".into(),updated_at:1};
        let mut issue=Issue{number:1,html_url:String::new(),body:Some(format!("<!-- mq3-enrollment:{} -->",serde_json::to_string(&profile).unwrap())),user:GithubUser{id:7,login:"student".into()}};
        assert_eq!(from_issue(&issue,"a"),Some(profile));assert!(from_issue(&issue,"b").is_none());issue.user.id=8;assert!(from_issue(&issue,"a").is_none());
    }
}
