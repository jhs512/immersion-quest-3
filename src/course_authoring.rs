//! Course composition uses GitHub reads. Explicit publication delegates to the user's gh login.
use crate::{github_player::Github,repository_course::{self,CourseManifest,Lesson,LessonRef}};
use serde::{Deserialize,Serialize};
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{io::Write,process::{Command,Stdio}};
#[cfg(windows)] use std::os::windows::process::CommandExt;

#[derive(Clone,Debug,PartialEq,Serialize,Deserialize)]
pub struct CourseDraft {pub owner:String,pub name:String,pub title:String,pub description:String,pub lessons:Vec<LessonRef>}
impl CourseDraft {
    pub fn manifest(&self)->Result<CourseManifest,String> {
        let manifest=CourseManifest{change_history:vec![],schema_version:1,id:self.name.clone(),title:self.title.clone(),description:self.description.clone(),repository:format!("{}/{}",self.owner,self.name),lessons:self.lessons.clone()};
        CourseManifest::parse(&serde_json::to_string(&manifest).map_err(|e|e.to_string())?)
    }
}
pub fn reference(github:&Github,text:&str)->Result<LessonRef,String> {
    let (repo,revision)=text.trim().rsplit_once('@').ok_or("수업은 owner/repository@v1.0.0 형식으로 입력하세요.")?;
    let raw=github.content(repo,revision,"lesson.json")?;
    let lesson:Lesson=serde_json::from_str(&raw).map_err(|e|e.to_string())?;lesson.validate()?;
    if lesson.revision!=revision {return Err("수업 파일과 선택한 버전이 달라요.".into())}
    Ok(LessonRef{id:lesson.id,title:lesson.title,repository:repo.into(),revision:revision.into(),sha256:format!("{:x}",Sha256::digest(raw.as_bytes())),prerequisites:vec![],required:true,review_enabled:lesson.review_enabled})
}
pub(crate) fn gh(args:&[&str],body:Option<Value>)->Result<Value,String> {
    if crate::pilot_source::enabled() { return crate::pilot_source::request(args,body); }
    #[cfg(not(target_os="android"))]
    let executable=crate::setup_terminal::gh_executable();
    #[cfg(target_os="android")]
    let executable=std::path::PathBuf::from("gh");
    let mut command=Command::new(executable);command.args(args).env("GH_HOST","github.com").env("GH_PROMPT_DISABLED","1").stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
    #[cfg(windows)] command.creation_flags(0x08000000);
    let mut child=command.spawn().map_err(|_|"GitHub CLI를 찾지 못했어요. gh를 설치하고 gh auth login을 실행하세요.")?;
    if let Some(body)=body {child.stdin.take().ok_or("gh 입력 연결 실패")?.write_all(serde_json::to_string(&body).map_err(|e|e.to_string())?.as_bytes()).map_err(|e|e.to_string())?;}
    let output=child.wait_with_output().map_err(|e|e.to_string())?;
    if !output.status.success() {return Err(format!("GitHub CLI 요청 실패. gh auth status와 리포 권한을 확인하세요. {}",String::from_utf8_lossy(&output.stderr).chars().take(600).collect::<String>()))}
    serde_json::from_slice(&output.stdout).map_err(|e|e.to_string())
}
pub fn publisher()->Result<String,String> {gh(&["api","user"],None)?["login"].as_str().map(String::from).ok_or("gh 로그인 계정을 확인하세요.".into())}
pub fn publish(draft:&CourseDraft,expected_user:u64)->Result<String,String> {
    use base64::Engine;
    let manifest=draft.manifest()?;
    let user=gh(&["api","user"],None)?;
    if user["id"].as_u64()!=Some(expected_user) || user["login"].as_str()!=Some(&draft.owner) {return Err("플레이어와 gh의 로그인 계정이 달라요. gh auth switch로 같은 계정을 선택하세요.".into())}
    let repo=manifest.repository.clone();
    let tag="Created with Molip Quest 3 course builder";
    match gh(&["api",&format!("repos/{repo}")],None) {
        Ok(existing)=>if existing["description"].as_str()!=Some(tag)||existing["private"]==true {return Err("같은 이름의 리포가 있어요. 새 이름을 선택하세요.".into())},
        Err(_)=>{gh(&["api","--method","POST","user/repos","--input","-"],Some(json!({"name":draft.name,"description":tag,"private":false,"auto_init":true,"has_issues":true})))?;}
    }
    let metadata=gh(&["api",&format!("repos/{repo}")],None)?;
    if metadata["default_branch"]!="main" {
        let branch=metadata["default_branch"].as_str().ok_or("기본 브랜치를 찾지 못했어요.")?;
        let head=gh(&["api",&format!("repos/{repo}/git/ref/heads/{branch}")],None)?;
        gh(&["api","--method","POST",&format!("repos/{repo}/git/refs"),"--input","-"],Some(json!({"ref":"refs/heads/main","sha":head["object"]["sha"]})))?;
        gh(&["api","--method","PATCH",&format!("repos/{repo}"),"--input","-"],Some(json!({"default_branch":"main"})))?;
    }
    let body=serde_json::to_string_pretty(&manifest).map_err(|e|e.to_string())?+"\n";
    let path=format!("repos/{repo}/contents/course.json");
    if let Ok(existing)=gh(&["api",&path],None) {
        let encoded=existing["content"].as_str().unwrap_or("").replace(['\r','\n'],"");
        if base64::engine::general_purpose::STANDARD.decode(encoded).ok().as_deref()!=Some(body.as_bytes()) {return Err("이미 게시한 코스가 있어요. 덮어쓰지 않았어요. 새 이름을 선택하세요.".into())}
    }else{
        gh(&["api","--method","PUT",&path,"--input","-"],Some(json!({"message":"Publish course composition","branch":"main","content":base64::engine::general_purpose::STANDARD.encode(body.as_bytes())})))?;
    }
    remember(&repo)?;
    Ok(format!("https://github.com/{repo}"))
}
pub fn catalog()->Vec<String> {
    if crate::pilot_source::enabled() { return vec![crate::pilot_source::REPOSITORY.into()]; }
    let mut repositories=vec![
        repository_course::COURSE_REPOSITORY.to_string(),
        "jhs512/mq3-course-redesigned-engineer-practical".to_string(),
        "jhs512/mq3-course-redesigned-aice-associate".to_string(),
    ];
    if let Ok(root)=crate::data_dir() {if let Ok(text)=std::fs::read_to_string(root.join("repository-courses.json")) {if let Ok(saved)=serde_json::from_str::<Vec<String>>(&text) {for repo in saved {if repository_course::valid_repository(&repo)&&!repositories.contains(&repo) {repositories.push(repo)}}}}}
    repositories
}
pub fn remember(repository:&str)->Result<(),String> {
    if !repository_course::valid_repository(repository) {return Err("owner/repository 형식으로 입력하세요.".into())}
    let mut saved=catalog();if !saved.contains(&repository.to_string()){saved.push(repository.into())}
    std::fs::write(crate::data_dir()?.join("repository-courses.json"),serde_json::to_string_pretty(&saved).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}
