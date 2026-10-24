//! GitHub transport through the existing gh login. The player never copies a token.
use crate::{issue_progress::{self,LearningEvent,ProgressKey},repository_course::{self,CourseManifest,Lesson,LessonRef}};
use serde::{Deserialize,Serialize};
use serde_json::{json,Value};
use std::time::Duration;

#[derive(Clone,Debug,Deserialize,Serialize,PartialEq)]
pub struct GithubUser { pub id:u64, pub login:String }
#[derive(Clone,PartialEq)]
pub struct Github;
#[derive(Clone, Default, PartialEq)]
pub struct CourseProgress {
    /// The account, course and repository this result was read for; the catalog ignores a
    /// result whose scope is no longer on screen.
    pub scope: crate::progress_overlay::ProgressScope,
    pub events: std::collections::HashMap<String, Vec<LearningEvent>>,
    pub required: std::collections::HashMap<String, Vec<String>>,
    /// The lesson revision each `required` list was read for. The catalog only uses a list for
    /// the revision its manifest currently shows, so a result read before a content update
    /// cannot decide the updated lesson's card.
    pub revisions: std::collections::HashMap<String, String>,
}
#[derive(Clone,Debug,Deserialize)]
pub struct Issue {pub number:u64,pub html_url:String,pub body:Option<String>,pub user:GithubUser}
#[derive(Clone,Deserialize)]
struct Comment {body:String,user:GithubUser}

pub(crate) fn agent()->ureq::Agent {ureq::Agent::config_builder().tls_config(ureq::tls::TlsConfig::builder().provider(ureq::tls::TlsProvider::NativeTls).build()).timeout_global(Some(Duration::from_secs(25))).build().into()}
impl Github {
    pub fn new()->Self {Self}
    fn get<T:serde::de::DeserializeOwned>(&self,path:&str)->Result<T,String> {
        serde_json::from_value(crate::course_authoring::gh(&["api","--hostname","github.com","--method","GET",path],None)?).map_err(|e|e.to_string())
    }
    fn post<T:serde::de::DeserializeOwned>(&self,path:&str,payload:Value)->Result<T,String> {
        serde_json::from_value(crate::course_authoring::gh(&["api","--hostname","github.com","--method","POST",path,"--input","-"],Some(payload))?).map_err(|e|e.to_string())
    }
    pub fn user(&self)->Result<GithubUser,String> {self.get("/user")}
    pub fn ensure_user(&self,expected:u64)->Result<(),String> {if self.user()?.id!=expected {Err("로그인 계정이 바뀌었어요. 현재 수업을 다시 여세요.".into())}else{Ok(())}}
    pub fn content(&self,repo:&str,revision:&str,file:&str)->Result<String,String> {
        use base64::Engine;
        if !repository_course::valid_repository(repo) || !repository_course::safe_file(file) || revision.is_empty() || revision.contains(['\\','/','?','#']) {return Err("저장소와 콘텐츠 경로를 확인하세요.".into())}
        let data:Value=self.get(&format!("/repos/{repo}/contents/{file}?ref={revision}"))?;
        if data["size"].as_u64().unwrap_or(u64::MAX)>4_000_000 || data["encoding"]!="base64" {return Err("수업 파일의 크기나 형식을 확인하세요.".into())}
        let content=data["content"].as_str().ok_or("수업 내용을 찾지 못했어요.")?.replace(['\n','\r'],"");
        let bytes=base64::engine::general_purpose::STANDARD.decode(content).map_err(|_|"수업 파일을 해독하지 못했어요.")?;
        String::from_utf8(bytes).map_err(|_|"수업 파일은 UTF-8이어야 해요.".into())
    }
    pub fn course(&self,repository:&str)->Result<CourseManifest,String> {
        if let Some(raw)=crate::bundled_courses::course_source(repository){
            if let Some(active)=crate::content_updates::installed_store()?.active(repository)? {return Ok(active.course().clone())}
            return CourseManifest::parse(raw)
        }
        let course=CourseManifest::parse(&self.content(repository,"main","course.json")?)?;
        if course.repository!=repository {return Err("코스의 저장소 식별자가 맞지 않아요.".into())}
        Ok(course)
    }
    pub fn prepare_course(&self,repository:&str)->Result<crate::content_updates::Snapshot,String> {
        let raw=self.content(repository,"main","course.json")?;
        let store=crate::content_updates::installed_store()?;
        let installed=store.active(repository)?;
        crate::bundled_courses::prepare_update(&store,repository,&raw,|reference|{
            if let Some(raw)=installed.as_ref().and_then(|snapshot|snapshot.lesson_source(reference)){return Ok(raw.to_owned())}
            if let Some(raw)=crate::bundled_courses::lesson_source(reference){return Ok(raw.to_owned())}
            self.content(&reference.repository,&reference.revision,"lesson.json")
        })
    }
    pub fn installed_course(&self,repository:&str)->Result<CourseManifest,String> {
        let store=crate::content_updates::installed_store()?;
        let active=store.active(repository)?;
        if let Some(current)=active.as_ref().filter(|snapshot|snapshot.is_remote()){return Ok(current.course().clone())}
        if let Some(snapshot)=crate::bundled_courses::prepare(&store,repository)? {
            if !active.as_ref().is_some_and(|current|current.fingerprint()==snapshot.fingerprint()){
                store.apply(&snapshot)?;
            }
            return Ok(snapshot.course().clone())
        }
        if let Some(snapshot)=active {return Ok(snapshot.course().clone())}
        let snapshot=self.prepare_course(repository)?;
        store.apply(&snapshot)?;
        Ok(snapshot.course().clone())
    }
    /// Whether this account can edit the course repository; only such accounts see draft
    /// final problems. GitHub decides, the app keeps no reviewer list.
    pub fn can_edit_course(&self,repository:&str)->Result<bool,String> {
        if !repository_course::valid_repository(repository) {return Err("코스 저장소를 확인하세요.".into())}
        let data:Value=self.get(&format!("/repos/{repository}"))?;
        Ok(data["permissions"]["push"].as_bool()==Some(true))
    }
    /// Final problems for lessons still being prepared, kept in the course repository for now.
    /// A missing file means there are none yet; any other failure is reported, not hidden.
    pub fn future_challenges(&self,course:&CourseManifest)->Result<Option<crate::challenges::FutureChallengeFile>,String> {
        match self.content(&course.repository,"main",crate::challenges::FUTURE_FILE) {
            Ok(text)=>crate::challenges::FutureChallengeFile::parse(&text,course).map(Some),
            Err(error) if error.contains("HTTP 404")=>Ok(None),
            Err(error)=>Err(error),
        }
    }
    pub fn installed_lesson(&self,course:&CourseManifest,reference:&LessonRef)->Result<Lesson,String> {
        crate::telemetry::observe_sync("lesson.load",vec![opentelemetry::KeyValue::new("course.id",course.id.clone()),opentelemetry::KeyValue::new("lesson.id",reference.id.clone())],||self.installed_lesson_inner(course,reference))
    }
    fn installed_lesson_inner(&self,course:&CourseManifest,reference:&LessonRef)->Result<Lesson,String> {
        crate::content_updates::installed_store()?.active(&course.repository)?.and_then(|snapshot|snapshot.lesson(reference).cloned()).ok_or_else(||"설치된 수업이 없어요. 코스를 다시 여세요.".into())
    }
    pub fn lesson(&self,reference:&LessonRef)->Result<Lesson,String> {
        if let Some(raw)=crate::bundled_courses::lesson_source(reference){return Lesson::parse(raw,reference)}
        Lesson::parse(&self.content(&reference.repository,&reference.revision,"lesson.json")?,reference)
    }
    pub fn issues(&self,repo:&str,user:&GithubUser)->Result<Vec<Issue>,String> {
        if !repository_course::valid_repository(repo) || !user.login.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-') {return Err("코스 저장소나 계정을 확인하세요.".into())}
        let mut all=vec![];
        for page in 1..=50 {
            let items:Vec<Issue>=self.get(&format!("/repos/{repo}/issues?creator={}&state=all&per_page=100&page={page}",user.login))?;
            let end=items.len()<100;
            all.extend(items.into_iter().filter(|i|i.user.id==user.id));
            if end {return Ok(all)}
        }
        Err("진도 이슈가 너무 많아요. 코스 관리자에게 문의하세요.".into())
    }
    pub fn find_issue(&self,repo:&str,user:&GithubUser,key:&ProgressKey)->Result<Option<Issue>,String> {
        let marker=issue_progress::marker(key);
        Ok(self.issues(repo,user)?.into_iter().filter(|i|i.body.as_deref().is_some_and(|b|b.contains(&marker))).min_by_key(|i|i.number))
    }
    fn course_events_remote(&self,repo:&str,user:&GithubUser,course_id:&str)->Result<std::collections::HashMap<String,Vec<LearningEvent>>,String> {
        self.ensure_user(user.id)?;
        let mut by_lesson:std::collections::HashMap<String,Vec<LearningEvent>>=Default::default();
        for issue in self.issues(repo,user)? {
            let Some(body)=issue.body.as_deref() else{continue};
            let Some(raw)=body.split("<!-- mq3-progress:").nth(1).and_then(|b|b.split(" -->").next()) else{continue};
            let Ok(key)=serde_json::from_str::<ProgressKey>(raw) else{continue};
            if key.user_id!=user.id || key.course_id!=course_id {continue}
            by_lesson.entry(key.lesson_id.clone()).or_default().extend(self.issue_events(repo,&issue,&key)?);
        }
        for (lesson,events) in &mut by_lesson { *events=issue_progress::merge(std::mem::take(events),&ProgressKey{user_id:user.id,course_id:course_id.into(),lesson_id:lesson.clone()}); }
        Ok(by_lesson)
    }
    /// Every catalog card needs pinned requirements, including partially solved lessons.
    /// Installed snapshots already hold these lessons, so this adds no network reads.
    /// This reads only the local history and returns at once; `refreshed_course_progress`
    /// adds what GitHub holds and is run afterwards in the background.
    pub fn course_progress(&self,course:&CourseManifest,user:&GithubUser)->Result<CourseProgress,String> {
        let events=self.course_events(&course.repository,user,&course.id)?;
        self.with_requirements(course,user,events)
    }
    /// The same catalog progress after reading GitHub and caching what it returned.
    pub fn refreshed_course_progress(&self,course:&CourseManifest,user:&GithubUser)->Result<CourseProgress,String> {
        let events=self.refresh_course_events(&course.repository,user,&course.id)?;
        self.with_requirements(course,user,events)
    }
    fn with_requirements(&self,course:&CourseManifest,user:&GithubUser,events:std::collections::HashMap<String,Vec<LearningEvent>>)->Result<CourseProgress,String> {
        let installed=crate::content_updates::installed_store()?.active(&course.repository)?;
        let mut required=std::collections::HashMap::new();let mut revisions=std::collections::HashMap::new();
        for reference in &course.lessons {
                let lesson=match installed.as_ref().and_then(|snapshot|snapshot.lesson(reference)) {
                    Some(lesson)=>lesson.clone(),None=>self.lesson(reference)?,
                };
                required.insert(reference.id.clone(),lesson.required_tasks());
                revisions.insert(reference.id.clone(),reference.revision.clone());
        }
        Ok(CourseProgress{scope:crate::progress_overlay::ProgressScope::new(&course.repository,user.id,&course.id),events,required,revisions})
    }
    fn events_remote(&self,repo:&str,issue:&Issue,key:&ProgressKey)->Result<Vec<LearningEvent>,String> {
        let marker=issue_progress::marker(key);
        let user=self.user()?;
        if user.id!=key.user_id {return Err("gh 계정이 바뀌었어요. 코스 목록에서 계정을 다시 확인하세요.".into())}
        let mut issues=self.issues(repo,&user)?.into_iter().filter(|i|i.body.as_deref().is_some_and(|b|b.contains(&marker))).collect::<Vec<_>>();
        if !issues.iter().any(|i|i.number==issue.number){issues.push(issue.clone())}
        let mut all=vec![];
        for item in issues {all.extend(self.issue_events(repo,&item,key)?);}
        Ok(issue_progress::merge(all,key))
    }
    fn issue_events(&self,repo:&str,issue:&Issue,key:&ProgressKey)->Result<Vec<LearningEvent>,String> {
        let mut all=vec![];
        for page in 1..=100 {
            let comments:Vec<Comment>=self.get(&format!("/repos/{repo}/issues/{}/comments?per_page=100&page={page}",issue.number))?;
            let end=comments.len()<100;
            all.extend(comments.into_iter().filter(|c|c.user.id==key.user_id).flat_map(|c|issue_progress::parse_events(&c.body)));
            if end {return Ok(issue_progress::merge(all,key))}
        }
        Err("학습 기록이 너무 많아요. 관리자에게 문의하세요.".into())
    }
    pub fn record(&self,repo:&str,user:&GithubUser,title:&str,event:&LearningEvent,required:&[String])->Result<Vec<LearningEvent>,String>{
        crate::telemetry::observe_sync("progress.save.local",vec![opentelemetry::KeyValue::new("course.id",event.key.course_id.clone()),opentelemetry::KeyValue::new("lesson.id",event.key.lesson_id.clone())],||self.record_inner(repo,user,title,event,required))
    }
    fn record_inner(&self,repo:&str,user:&GithubUser,title:&str,event:&LearningEvent,required:&[String])->Result<Vec<LearningEvent>,String>{
        // Journaled before SQLite and retried while SQLite is busy; see progress_sync::journal.
        let latest=crate::progress_sync::ProgressStore::installed()?.record_durably(repo,user,title,event,required,crate::progress_sync::RECORD_RETRY_WINDOW)?;
        if let Err(error)=crate::progress_sync::synchronize(self.clone(),user.clone()){eprintln!("Progress upload deferred: {error}");}
        Ok(latest)
    }
    pub fn events(&self,repo:&str,issue:&Issue,key:&ProgressKey)->Result<Vec<LearningEvent>,String>{
        let store=crate::progress_sync::ProgressStore::installed()?;
        match self.events_remote(repo,issue,key){
            Ok(remote)=>{store.cache(repo,&remote)?;store.events(repo,key)},
            Err(error)=>{let local=store.events(repo,key)?;if local.is_empty(){Err(error)}else{Ok(local)}},
        }
    }
    /// The local history of this account in this course. It never waits for GitHub, so a
    /// completion saved on this device is on the catalog before any remote read finishes.
    pub fn course_events(&self,repo:&str,user:&GithubUser,course_id:&str)->Result<std::collections::HashMap<String,Vec<LearningEvent>>,String>{
        let store=crate::progress_sync::ProgressStore::installed()?;
        store.course_events(repo,user.id,course_id)
    }
    /// Reads GitHub, adds what it returned to the local history (never removing local events,
    /// pending uploads included) and returns the united history. Offline, the local history.
    pub fn refresh_course_events(&self,repo:&str,user:&GithubUser,course_id:&str)->Result<std::collections::HashMap<String,Vec<LearningEvent>>,String>{
        let store=crate::progress_sync::ProgressStore::installed()?;
        match self.course_events_remote(repo,user,course_id){
            Ok(remote)=>{for events in remote.values(){store.cache(repo,events)?;}store.course_events(repo,user.id,course_id)},
            Err(error)=>{let local=store.course_events(repo,user.id,course_id)?;if local.is_empty(){Err(error)}else{Ok(local)}},
        }
    }
    pub fn append(&self,repo:&str,user:&GithubUser,title:&str,event:&LearningEvent)->Result<(Issue,Vec<LearningEvent>),String> {
        crate::telemetry::observe_sync("progress.upload",vec![opentelemetry::KeyValue::new("course.id",event.key.course_id.clone()),opentelemetry::KeyValue::new("lesson.id",event.key.lesson_id.clone())],||self.append_inner(repo,user,title,event))
    }
    fn append_inner(&self,repo:&str,user:&GithubUser,title:&str,event:&LearningEvent)->Result<(Issue,Vec<LearningEvent>),String> {
        self.append_batch(repo,user,title,std::slice::from_ref(event))
    }
    pub fn append_batch(&self,repo:&str,user:&GithubUser,title:&str,batch:&[LearningEvent])->Result<(Issue,Vec<LearningEvent>),String> {
        let event=batch.first().ok_or("보낼 학습 기록이 없어요.")?;
        self.ensure_user(user.id)?;
        if batch.iter().any(|e|e.key!=event.key)||event.key.user_id!=user.id {return Err("다른 계정의 진도를 기록할 수 없어요.".into())}
        let issue=if let Some(i)=self.find_issue(repo,user,&event.key)? {i} else {
            self.post(&format!("/repos/{repo}/issues"),json!({"title":format!("[진도] {title} · @{}",user.login),"body":issue_progress::summary(&event.key,title,&[])}))?
        };
        let mut events=self.events_remote(repo,&issue,&event.key)?;
        let missing=batch.iter().filter(|event|!events.iter().any(|e|e.id==event.id)).cloned().collect::<Vec<_>>();
        if !missing.is_empty() {
            let _:Value=self.post(&format!("/repos/{repo}/issues/{}/comments",issue.number),json!({"body":issue_progress::batch_comment(&missing)}))?;
            events.extend(missing);
        }
        // Re-read includes concurrently appended comments; a summary never erases events.
        let latest=self.events_remote(repo,&issue,&event.key)?;
        let issue=self.find_issue(repo,user,&event.key)?.unwrap_or(issue);
        let body=issue_progress::summary(&event.key,title,&latest);
        let _=crate::course_authoring::gh(&["api","--hostname","github.com","--method","PATCH",&format!("repos/{repo}/issues/{}",issue.number),"--input","-"],Some(json!({"body":body})));
        // Two simultaneous first launches can create duplicate issues. Keep all logs readable,
        // choose the lowest issue number, and close later duplicates without deleting comments.
        let marker=issue_progress::marker(&event.key);
        for duplicate in self.issues(repo,user)?.into_iter().filter(|i|i.number!=issue.number&&i.body.as_deref().is_some_and(|b|b.contains(&marker))) {
            let _=crate::course_authoring::gh(&["api","--hostname","github.com","--method","PATCH",&format!("repos/{repo}/issues/{}",duplicate.number),"--input","-"],Some(json!({"state":"closed","body":format!("진도는 #{} 에서 이어가요. 동시 시작의 원본 기록은 보존해요.\n\n{marker}",issue.number)})));
        }
        Ok((issue,latest))
    }
}

pub async fn background<T:Send+'static>(work:impl FnOnce()->Result<T,String>+Send+'static)->Result<T,String> {
    let context=opentelemetry::Context::current();
    tokio::task::spawn_blocking(move||{let _guard=context.attach();work()}).await.map_err(|e|e.to_string())?
}
