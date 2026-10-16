//! GitHub transport through the existing gh login. The player never copies a token.
use crate::{issue_progress::{self,LearningEvent,ProgressKey},repository_course::{self,CourseManifest,Lesson,LessonRef}};
use serde::{Deserialize,Serialize};
use serde_json::{json,Value};
use std::time::Duration;

#[derive(Clone,Debug,Deserialize,Serialize,PartialEq)]
pub struct GithubUser { pub id:u64, pub login:String }
#[derive(Clone,PartialEq)]
pub struct Github;
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
        let course=CourseManifest::parse(&self.content(repository,"main","course.json")?)?;
        if course.repository!=repository {return Err("코스의 저장소 식별자가 맞지 않아요.".into())}
        Ok(course)
    }
    pub fn lesson(&self,reference:&LessonRef)->Result<Lesson,String> {Lesson::parse(&self.content(&reference.repository,&reference.revision,"lesson.json")?,reference)}
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
    pub fn course_events(&self,repo:&str,user:&GithubUser,course_id:&str)->Result<std::collections::HashMap<String,Vec<LearningEvent>>,String> {
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
    pub fn events(&self,repo:&str,issue:&Issue,key:&ProgressKey)->Result<Vec<LearningEvent>,String> {
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
            all.extend(comments.into_iter().filter(|c|c.user.id==key.user_id).filter_map(|c|issue_progress::parse_event(&c.body)));
            if end {return Ok(issue_progress::merge(all,key))}
        }
        Err("학습 기록이 너무 많아요. 관리자에게 문의하세요.".into())
    }
    pub fn append(&self,repo:&str,user:&GithubUser,title:&str,event:&LearningEvent)->Result<(Issue,Vec<LearningEvent>),String> {
        self.ensure_user(user.id)?;
        if event.key.user_id!=user.id {return Err("다른 계정의 진도를 기록할 수 없어요.".into())}
        let issue=if let Some(i)=self.find_issue(repo,user,&event.key)? {i} else {
            self.post(&format!("/repos/{repo}/issues"),json!({"title":format!("[진도] {title} · @{}",user.login),"body":issue_progress::summary(&event.key,title,&[])}))?
        };
        let mut events=self.events(repo,&issue,&event.key)?;
        if !events.iter().any(|e|e.id==event.id) {
            let _:Value=self.post(&format!("/repos/{repo}/issues/{}/comments",issue.number),json!({"body":event.comment()}))?;
            events.push(event.clone());
        }
        // Re-read includes concurrently appended comments; a summary never erases events.
        let latest=self.events(repo,&issue,&event.key)?;
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
    tokio::task::spawn_blocking(work).await.map_err(|e|e.to_string())?
}
