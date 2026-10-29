//! Owned, loopback-only GitLab exercises. Hosting authentication is internal.
use super::*;
use serde_json::Value;

#[derive(Clone,Copy,Debug,Serialize,Deserialize,PartialEq)]
#[serde(rename_all="snake_case")]
pub enum GitlabStage { Repository, MainPushed, Branch, Committed, FeaturePushed, MergeRequest, Reviewed, Merged, Final, Pipeline }

#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct GitlabExercise {
    pub stage:GitlabStage,
    #[serde(default)] pub editable:Vec<String>,
    #[serde(default)] pub pipeline_status:String,
    #[serde(default)] pub jobs:BTreeMap<String,String>,
    #[serde(default)] pub logs:BTreeMap<String,String>,
    #[serde(default)] pub artifacts:BTreeMap<String,String>,
    #[serde(default)] pub required_files:BTreeMap<String,String>,
    #[serde(default)] pub job_order:Vec<String>,
    #[serde(default)] pub absent_jobs:Vec<String>,
    #[serde(default)] pub pipeline_ref:String,
}

#[derive(Clone,Debug,Serialize,Deserialize)]
struct Connection {url:String,username:String,glab_dir:String}

#[derive(Clone)]
pub struct GitlabLessonSession(std::sync::Arc<std::sync::atomic::AtomicBool>);
impl GitlabLessonSession {
    pub fn new()->Self{Self(std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false)))}
    pub fn activate(&self){self.0.store(true,std::sync::atomic::Ordering::SeqCst);}
    pub fn close(&self){
        if self.0.swap(false,std::sync::atomic::Ordering::SeqCst){std::thread::spawn(||{let _=helper("stop");});}
    }
}

fn tools()->Result<PathBuf,String>{
    let directory=crate::data_dir()?.join("gitlab-lab-tools");
    std::fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
    for (file,source) in [("lab.py",include_str!("../assets/gitlab/lab.py")),("http_client.py",include_str!("../assets/gitlab/http_client.py"))] {
        let path=directory.join(file);
        if std::fs::read_to_string(&path).ok().as_deref()!=Some(source){std::fs::write(path,source).map_err(|e|e.to_string())?;}
    }
    Ok(directory)
}

fn state()->Result<PathBuf,String>{
    Ok(std::env::var_os("MQ3_GITLAB_STATE").map(PathBuf::from).unwrap_or(crate::data_dir()?.join("gitlab-lab")))
}

#[cfg(not(target_os="android"))]
fn helper(action:&str)->Result<String,String>{
    let mut command=Command::new(crate::runner::python_executable());
    command.arg(tools()?.join("lab.py")).arg(action).env("MQ3_GITLAB_STATE",state()?).env("PYTHONUTF8","1");
    #[cfg(windows)] command.creation_flags(0x08000000);
    let result=command.output().map_err(|e|format!("GitLab 실습 준비 도구를 실행하지 못했어요. 환경 설치를 확인하세요. {e}"))?;
    if !result.status.success(){return Err(format!("로컬 GitLab 준비에 실패했어요. Docker Desktop과 여유 메모리를 확인하세요. {}",String::from_utf8_lossy(&result.stderr).lines().last().unwrap_or_default()));}
    Ok(String::from_utf8_lossy(&result.stdout).into_owned())
}

#[cfg(target_os="android")]
fn helper(_:&str)->Result<String,String>{Err("GitLab 실습은 Docker가 있는 데스크톱에서 진행하세요.".into())}

impl GitlabExercise {
    pub fn validate(&self)->Result<(),String>{
        if self.editable.len()>4||self.editable.iter().any(|f|!crate::repository_course::safe_file(f)) {return Err("GitLab 실습 파일을 확인하세요.".into())}
        if self.stage==GitlabStage::Pipeline && (!matches!(self.pipeline_status.as_str(),"success"|"failed")||self.jobs.is_empty()) {return Err("파이프라인의 실제 판정 기준이 필요해요.".into())}
        if self.jobs.len()>8||self.artifacts.len()>4||self.required_files.len()>8 {return Err("파이프라인 검사 범위를 확인하세요.".into())}
        for path in self.artifacts.keys().chain(self.required_files.keys()){if !crate::repository_course::safe_file(path){return Err("실습 산출물 경로를 확인하세요.".into())}}
        Ok(())
    }
}

impl GitPractice {
    pub fn hosted(&self)->bool {self.exercise.github_pr.is_some()||self.exercise.gitlab.is_some()}
    pub fn is_gitlab(&self)->bool {self.exercise.gitlab.is_some()}
    fn connection(&self)->Result<Connection,String>{
        let value:Connection=serde_json::from_slice(&std::fs::read(self.root().join("gitlab-connection.json")).map_err(|_|"GitLab 터미널을 먼저 열어 주세요.")?).map_err(|e|e.to_string())?;
        let url=url::Url::parse(&value.url).map_err(|e|e.to_string())?;
        if url.scheme()!="http"||url.host_str()!=Some("127.0.0.1")||url.port().is_none()||!url.username().is_empty()||url.password().is_some(){return Err("이 컴퓨터의 실습 GitLab 주소가 아니에요.".into())}
        Ok(value)
    }
    pub fn prepare_gitlab(&self)->Result<(),String>{
        if self.exercise.gitlab.is_none(){return Ok(())}
        let directory=state()?;std::fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
        let lock=std::fs::OpenOptions::new().create(true).truncate(false).read(true).write(true).open(directory.join("startup.lock")).map_err(|e|e.to_string())?;
        lock.lock().map_err(|e|e.to_string())?;
        helper("start")?;helper("install_cli")?;
        if self.exercise.gitlab.as_ref().is_some_and(|g|g.stage==GitlabStage::Pipeline){helper("runner")?;}
        let raw=helper("ready_json")?;
        let c:Connection=serde_json::from_str(raw.trim()).map_err(|e|e.to_string())?;
        std::fs::write(self.root().join("gitlab-connection.json"),serde_json::to_vec(&c).unwrap()).map_err(|e|e.to_string())?;
        let config=self.root().join("glab-config");std::fs::create_dir_all(&config).map_err(|e|e.to_string())?;
        let host=url::Url::parse(&c.url).map_err(|e|e.to_string())?.authority().to_owned();
        let yaml=format!("git_protocol: http\ncheck_update: false\nhosts:\n  {host}:\n    api_protocol: http\n    git_protocol: http\n    token: mq3-local-gateway\n    user: {}\n",c.username);
        std::fs::write(config.join("config.yml"),yaml).map_err(|e|e.to_string())?;
        if self.exercise.gitlab.as_ref().is_some_and(|g|g.stage==GitlabStage::Pipeline)&&!self.git(&["remote","get-url","origin"])?.success {
            let value=serde_json::json!({"name":self.github_repository_name(),"visibility":"private","default_branch":"main","builds_access_level":"enabled","shared_runners_enabled":true});
            #[cfg(not(target_os="android"))]
            {ureq::post(&format!("{}/api/v4/projects",c.url)).config().timeout_global(Some(std::time::Duration::from_secs(45))).build().send_json(&value).map_err(|e|e.to_string())?;}
            self.checked_at(&self.work(),&["remote","add","origin",&format!("{}/{}/{}.git",c.url,c.username,self.github_repository_name())])?;
            self.checked_at(&self.work(),&["push","-u","origin","main"])?;
        }
        Ok(())
    }
    pub(super) fn gitlab_environment(&self)->Vec<(String,String)>{
        let Ok(c)=self.connection() else{return vec![]};
        let paths=std::iter::once(PathBuf::from(c.glab_dir)).chain(std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()).collect::<Vec<_>>());
        vec![("GITLAB_HOST".into(),c.url.clone()),("GITLAB_TOKEN".into(),"mq3-local-gateway".into()),
            ("GLAB_CONFIG_DIR".into(),self.root().join("glab-config").to_string_lossy().into()),
            ("GLAB_CHECK_UPDATE".into(),"false".into()),("GLAB_PROMPT_DISABLED".into(),"true".into()),("GLAB_PAGER".into(),"cat".into()),
            ("MQ3_REPO".into(),self.github_repository_name()),("MQ3_GITLAB".into(),c.url.clone()),("MQ3_NAMESPACE".into(),c.username),
            ("GIT_ALLOW_PROTOCOL".into(),"http:file".into()),("GIT_CONFIG_COUNT".into(),"1".into()),
            ("GIT_CONFIG_KEY_0".into(),"credential.helper".into()),("GIT_CONFIG_VALUE_0".into(),String::new()),
            ("PATH".into(),std::env::join_paths(paths).unwrap_or_default().to_string_lossy().into())]
    }
    #[cfg(not(target_os="android"))]
    fn gitlab_get(&self,path:&str)->Result<Value,String>{
        let url=format!("{}/api/v4{path}",self.connection()?.url);
        let raw=ureq::get(&url).config().timeout_global(Some(std::time::Duration::from_secs(45))).build().call()
            .map_err(|e|format!("실습 GitLab의 실제 결과를 읽지 못했어요. 명령 결과를 확인하세요. {e}"))?.body_mut().read_to_string().map_err(|e|e.to_string())?;
        serde_json::from_str(&raw).map_err(|e|e.to_string())
    }
    #[cfg(target_os="android")]
    fn gitlab_get(&self,_:&str)->Result<Value,String>{Err("데스크톱에서 GitLab을 실행하세요.".into())}
    #[cfg(not(target_os="android"))]
    fn gitlab_text(&self,path:&str)->Result<String,String>{
        ureq::get(&format!("{}/api/v4{path}",self.connection()?.url)).config().timeout_global(Some(std::time::Duration::from_secs(45))).build().call().map_err(|e|e.to_string())?.body_mut().read_to_string().map_err(|e|e.to_string())
    }
    #[cfg(target_os="android")]
    fn gitlab_text(&self,_:&str)->Result<String,String>{Err("데스크톱에서 GitLab을 실행하세요.".into())}
    pub(super) fn check_gitlab(&self)->Result<crate::runner::TestReport,String>{
        use crate::runner::{TestReport,TestCaseResult};
        let goal=self.exercise.gitlab.as_ref().ok_or("GitLab 실습이 아니에요.")?;
        if self.exercise.github_demonstration{return Err("해설용 저장소는 제출하지 않아요.".into())}
        let c=self.connection()?;let repository=format!("{}/{}",c.username,self.github_repository_name());
        let encoded:String=url::form_urlencoded::byte_serialize(repository.as_bytes()).collect();
        let project=self.gitlab_get(&format!("/projects/{encoded}"))?;
        let id=project["id"].as_u64().ok_or("이번 실습 프로젝트를 먼저 만드세요.")?;
        let mut cases=vec![];
        let mut record=|label:&str,passed:bool,expected:&str,observed:String|cases.push(TestCaseResult{input:label.into(),expected:expected.into(),stdout:observed,stderr:String::new(),passed,state:"gitlab_artifact".into()});
        record("이번 실습의 실제 GitLab 프로젝트",project["path_with_namespace"]==repository&&project["visibility"]=="private",&repository,project["path_with_namespace"].as_str().unwrap_or_default().into());
        let origin=self.git(&["remote","get-url","origin"])?;
        record("실습 origin 연결",origin.success&&origin.stdout.trim().trim_end_matches(".git")==format!("{}/{repository}",c.url),"이번 로컬 GitLab 프로젝트",origin.stdout);
        let text=|args:&[&str]|self.git(args).ok().filter(|r|r.success).map(|r|r.stdout.trim().to_owned()).unwrap_or_default();
        let main=text(&["rev-parse","refs/heads/main"]);let feature=text(&["rev-parse","refs/heads/feature"]);
        let remote=|branch:&str|self.gitlab_get(&format!("/projects/{id}/repository/branches/{branch}")).ok().and_then(|v|v["commit"]["id"].as_str().map(str::to_owned)).unwrap_or_default();
        if goal.stage==GitlabStage::Pipeline {
            let sha=text(&["rev-parse","HEAD"]);
            let pipelines=self.gitlab_get(&format!("/projects/{id}/pipelines?sha={sha}&per_page=1"))?;
            let pipeline=pipelines.as_array().and_then(|a|a.first()).cloned().unwrap_or(Value::Null);
            record("현재 커밋의 실제 파이프라인",pipeline["sha"]==sha&&pipeline["status"]==goal.pipeline_status,&goal.pipeline_status,pipeline["status"].as_str().unwrap_or("아직 실행 중이거나 파이프라인이 없어요").into());
            if !goal.pipeline_ref.is_empty(){record("실행한 브랜치",pipeline["ref"]==goal.pipeline_ref,&goal.pipeline_ref,pipeline["ref"].as_str().unwrap_or_default().into());}
            if let Some(pipeline_id)=pipeline["id"].as_u64(){
                let jobs=self.gitlab_get(&format!("/projects/{id}/pipelines/{pipeline_id}/jobs?per_page=100"))?;
                let rows=jobs.as_array().cloned().unwrap_or_default();
                for name in &goal.absent_jobs {record(&format!("조건에서 제외된 {name}"),!rows.iter().any(|j|j["name"]==*name),"작업이 생성되지 않음",String::new());}
                for pair in goal.job_order.windows(2){let before=rows.iter().find(|j|j["name"]==pair[0]).and_then(|j|j["finished_at"].as_str());let after=rows.iter().find(|j|j["name"]==pair[1]).and_then(|j|j["started_at"].as_str());record(&format!("{} 다음 {}",pair[0],pair[1]),before.zip(after).is_some_and(|(a,b)|a<=b),"앞 작업 종료 뒤 다음 작업 시작",format!("{before:?} -> {after:?}"));}
                for (name,status) in &goal.jobs {let job=rows.iter().find(|j|j["name"]==*name).cloned().unwrap_or(Value::Null);record(&format!("{name} 작업의 실제 상태"),job["status"]==*status,status,job["status"].as_str().unwrap_or("없음").into());}
                for (name,required) in &goal.logs {let log=rows.iter().find(|j|j["name"]==*name).and_then(|j|j["id"].as_u64()).and_then(|job|self.gitlab_text(&format!("/projects/{id}/jobs/{job}/trace")).ok()).unwrap_or_default();record(&format!("{name} 실행 로그"),log.contains(required),required,log);}
                for (path,expected) in &goal.artifacts {
                    let content=rows.iter().filter_map(|j|j["id"].as_u64()).find_map(|job|self.gitlab_text(&format!("/projects/{id}/jobs/{job}/artifacts/{path}")).ok()).unwrap_or_default();
                    record(&format!("실제 산출물 {path}"),content.trim()==expected.trim(),expected,content);
                }
            }
            for (path,wanted) in &goal.required_files {let actual=text(&["show",&format!("HEAD:{path}")]);record(&format!("커밋한 {path}"),actual.contains(wanted),wanted,actual);}
        } else {
            if goal.stage!=GitlabStage::Repository {let sha=remote("main");record("원격 main 커밋",!main.is_empty()&&sha==main,"로컬 main과 같은 커밋",sha);}
            if matches!(goal.stage,GitlabStage::Branch|GitlabStage::Committed|GitlabStage::FeaturePushed|GitlabStage::MergeRequest|GitlabStage::Reviewed){let current=text(&["branch","--show-current"]);record("작업 브랜치",current=="feature"&&!feature.is_empty(),"feature",current);}
            if matches!(goal.stage,GitlabStage::Committed|GitlabStage::FeaturePushed|GitlabStage::MergeRequest|GitlabStage::Reviewed|GitlabStage::Final){let body=text(&["show","feature:memo.txt"]);record("작업 브랜치의 실제 변경",feature!=main&&body=="함께 읽는 메모","함께 읽는 메모",body);}
            if matches!(goal.stage,GitlabStage::FeaturePushed|GitlabStage::MergeRequest|GitlabStage::Reviewed){let sha=remote("feature");record("원격 feature 커밋",!feature.is_empty()&&sha==feature,"로컬 feature와 같은 커밋",sha);}
            if matches!(goal.stage,GitlabStage::MergeRequest|GitlabStage::Reviewed|GitlabStage::Merged|GitlabStage::Final){
                let requests=self.gitlab_get(&format!("/projects/{id}/merge_requests?source_branch=feature&target_branch=main&scope=all"))?;
                let mr=requests.as_array().and_then(|a|a.iter().find(|v|v["sha"]==feature&&v["source_project_id"]==id&&v["target_project_id"]==id)).cloned().unwrap_or(Value::Null);
                let merged=matches!(goal.stage,GitlabStage::Merged|GitlabStage::Final);
                record("실제 MR 상태",mr["state"]==if merged{"merged"}else{"opened"},if merged{"merged"}else{"opened"},mr["web_url"].as_str().unwrap_or_default().into());
                if merged {let current=text(&["branch","--show-current"]);let body=text(&["show","HEAD:memo.txt"]);record("병합 결과를 로컬 main에 받기",current=="main"&&body=="함께 읽는 메모"&&remote("main")==main,"main에서 함께 읽는 메모 확인",body);}
            }
            if matches!(goal.stage,GitlabStage::Reviewed|GitlabStage::Final){let rows=self.shell_completions()?;record("MR 변경 내용 확인",rows.iter().any(|r|r.success&&r.command.trim().starts_with("glab mr diff")),"glab mr diff 실행",String::new());}
        }
        Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
    }
}
