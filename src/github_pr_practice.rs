//! Opt-in GitHub PR exercises. Checks only read GitHub; learners perform all writes.
use super::*;
use serde_json::Value;
#[derive(Clone,Copy,Debug,Serialize,Deserialize,PartialEq)]
#[serde(rename_all="snake_case")]
pub enum GithubPrStage { Repository, MainPushed, Branch, Committed, FeaturePushed, PullRequest, Reviewed, Merged }

fn real_gh_config()->Option<PathBuf>{
    std::env::var_os("GH_CONFIG_DIR").filter(|v|!v.is_empty()).map(PathBuf::from)
        .or_else(||std::env::var_os("XDG_CONFIG_HOME").filter(|v|!v.is_empty()).map(|v|PathBuf::from(v).join("gh")))
        .or_else(||if cfg!(windows){std::env::var_os("APPDATA").map(|v|PathBuf::from(v).join("GitHub CLI"))}else{None})
        .or_else(||std::env::var_os("HOME").map(|v|PathBuf::from(v).join(".config/gh")))
}
impl GitPractice {
    pub fn github_repository_name(&self)->String{
        if let Ok(name)=std::fs::read_to_string(self.root().join("github-repository-name")) {
            if name.starts_with("mq3-pr-")&&name.len()==19&&name.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-'){return name;}
        }
        use sha2::{Digest,Sha256};
        format!("mq3-pr-{}",&format!("{:x}",Sha256::digest(self.root().to_string_lossy().as_bytes()))[..12])
    }
    pub(super) fn github_environment(&self)->Vec<(String,String)>{
        let mut result=vec![("MQ3_REPO".into(),self.github_repository_name()),("GH_HOST".into(),"github.com".into()),
            ("GH_REPO".into(),String::new()),("GH_PROMPT_DISABLED".into(),"1".into()),("GH_PAGER".into(),"cat".into()),
            ("GIT_ALLOW_PROTOCOL".into(),"https".into()),("GIT_HTTP_LOW_SPEED_LIMIT".into(),"1".into()),("GIT_HTTP_LOW_SPEED_TIME".into(),"30".into())];
        if let Some(path)=real_gh_config(){result.push(("GH_CONFIG_DIR".into(),path.to_string_lossy().into()));}
        // macOS gh's keychain provider uses the account's real home directory.
        // GH_CONFIG_DIR alone is insufficient if HOME points at the exercise.
        // Git configuration remains pinned to the owned practice config file.
        #[cfg(target_os="macos")]
        if let Some(home)=std::env::var_os("HOME") {result.push(("HOME".into(),home.to_string_lossy().into()));}
        #[cfg(not(target_os="android"))]
        {
            let gh=crate::setup_terminal::gh_executable().to_string_lossy().replace('\\',"/");
            // Credential access is delegated to gh, never copied into the practice folder.
            result.extend([("GIT_CONFIG_COUNT".into(),"3".into()),
                ("GIT_CONFIG_KEY_0".into(),"credential.https://github.com.helper".into()),
                ("GIT_CONFIG_VALUE_0".into(),format!("!\"{gh}\" auth git-credential")),
                ("GIT_CONFIG_KEY_1".into(),"url.https://github.com/.insteadOf".into()),("GIT_CONFIG_VALUE_1".into(),"git@github.com:".into()),
                ("GIT_CONFIG_KEY_2".into(),"url.https://github.com/.insteadOf".into()),("GIT_CONFIG_VALUE_2".into(),"ssh://git@github.com/".into())]);
        }
        result
    }
    #[cfg(not(target_os="android"))]
    fn github_json(&self,path:&str)->Result<Value,String>{
        use std::{io::Read,process::Stdio,time::{Duration,Instant}};
        let mut command=Command::new(crate::setup_terminal::gh_executable());
        command.args(["api","--hostname","github.com","--method","GET",path]).current_dir(self.work()).envs(self.environment()).stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped());
        #[cfg(windows)] command.creation_flags(0x08000000);
        let mut child=command.spawn().map_err(|_|"gh 설치와 GitHub 로그인을 확인하세요.")?;
        let stdout=child.stdout.take().unwrap();let stderr=child.stderr.take().unwrap();
        let out=std::thread::spawn(move||{let mut bytes=vec![];let _=stdout.take(1_000_001).read_to_end(&mut bytes);bytes});
        let err=std::thread::spawn(move||{let mut bytes=vec![];let _=stderr.take(8192).read_to_end(&mut bytes);bytes});
        let started=Instant::now();
        let status=loop {if let Some(status)=child.try_wait().map_err(|e|e.to_string())?{break status}
            if started.elapsed()>Duration::from_secs(45){let _=child.kill();let _=child.wait();return Err("GitHub 응답이 늦어요. 연결을 확인하고 다시 제출하세요.".into())}
            std::thread::sleep(Duration::from_millis(25));};
        let output=out.join().map_err(|_|"GitHub 응답 수집 실패")?;let error=err.join().unwrap_or_default();
        if !status.success(){
            crate::content_lifecycle::note_github_failure(&String::from_utf8_lossy(&error));
            return Err("GitHub 저장소나 PR을 확인하지 못했어요. 앞 단계와 gh 로그인 상태를 확인하세요.".into())
        }
        serde_json::from_slice(&output).map_err(|_|"GitHub 응답 형식을 확인하세요.".into())
    }
    #[cfg(target_os="android")]
    fn github_json(&self,_:&str)->Result<Value,String>{Err("GitHub PR 실습은 데스크톱에서 진행하세요.".into())}

    pub(super) fn check_github_pr(&self)->Result<crate::runner::TestReport,String>{
        use crate::runner::{TestReport,TestCaseResult};
        let stage=self.exercise.github_pr.ok_or("GitHub 실습이 아니에요.")?;
        if self.exercise.github_demonstration{return Err("해설은 GitHub를 자동으로 변경하지 않아요. 학습 터미널에서 직접 실습하세요.".into())}
        let user=self.github_json("user")?;
        let login=user["login"].as_str().ok_or("GitHub 계정을 확인하세요.")?;
        if !login.bytes().all(|c|c.is_ascii_alphanumeric()||c==b'-'){return Err("GitHub 계정을 확인하세요.".into())}
        let repository=format!("{login}/{}",self.github_repository_name());
        let actual=self.github_json(&format!("repos/{repository}"))?;
        let origin=self.git(&["remote","get-url","origin"])?;
        let url=origin.stdout.trim().trim_end_matches(".git");
        let origin_matches=url.eq_ignore_ascii_case(&format!("https://github.com/{repository}"))||url.eq_ignore_ascii_case(&format!("git@github.com:{repository}"))||url.eq_ignore_ascii_case(&format!("ssh://git@github.com/{repository}"));
        let mut cases=vec![];
        let mut record=|label:&str,passed:bool,expected:&str,observed:String|cases.push(TestCaseResult{input:label.into(),expected:expected.into(),stdout:observed,stderr:String::new(),passed,state:"github_artifact".into()});
        record("본인 계정의 실제 비공개 저장소",actual["full_name"].as_str().is_some_and(|s|s.eq_ignore_ascii_case(&repository))&&actual["private"]==true&&actual["owner"]["id"]==user["id"],&repository,actual["full_name"].as_str().unwrap_or_default().into());
        record("origin 연결",origin.success&&origin_matches,"이번 실습의 GitHub 저장소",origin.stdout);
        let git_text=|args:&[&str]|->String{self.git(args).ok().filter(|r|r.success).map(|r|r.stdout.trim().to_owned()).unwrap_or_default()};
        let main=git_text(&["rev-parse","refs/heads/main"]);let feature=git_text(&["rev-parse","refs/heads/feature"]);
        let remote_sha=|branch:&str|->String{self.github_json(&format!("repos/{repository}/git/ref/heads/{branch}")).ok().and_then(|v|v["object"]["sha"].as_str().map(str::to_owned)).unwrap_or_default()};
        if stage!=GithubPrStage::Repository{
            let remote=remote_sha("main");record("GitHub main의 실제 커밋",!main.is_empty()&&remote==main,"로컬 main과 같은 커밋",remote);
        }
        if matches!(stage,GithubPrStage::Branch|GithubPrStage::Committed|GithubPrStage::FeaturePushed|GithubPrStage::PullRequest|GithubPrStage::Reviewed){
            let branch=git_text(&["branch","--show-current"]);record("작업 브랜치",branch=="feature","feature",branch);
            record("feature 브랜치",!feature.is_empty(),"실제 feature 브랜치",feature.clone());
        }
        if matches!(stage,GithubPrStage::Committed|GithubPrStage::FeaturePushed|GithubPrStage::PullRequest|GithubPrStage::Reviewed){
            let body=git_text(&["show","feature:memo.txt"]);
            record("별도 브랜치의 변경",feature!=main&&body=="함께 읽는 메모","feature에 함께 읽는 메모를 커밋",body);
        }
        if matches!(stage,GithubPrStage::FeaturePushed|GithubPrStage::PullRequest|GithubPrStage::Reviewed){
            let remote=remote_sha("feature");record("GitHub feature의 실제 커밋",!feature.is_empty()&&remote==feature,"로컬 feature와 같은 커밋",remote);
        }
        if matches!(stage,GithubPrStage::PullRequest|GithubPrStage::Reviewed|GithubPrStage::Merged){
            let prs=self.github_json(&format!("repos/{repository}/pulls?state=all&head={login}:feature&base=main"))?;
            let pr=prs.as_array().and_then(|rows|rows.iter().find(|pr|pr["head"]["sha"].as_str()==Some(&feature)&&pr["user"]["id"]==user["id"]&&pr["head"]["repo"]["full_name"].as_str().is_some_and(|s|s.eq_ignore_ascii_case(&repository)))).cloned().unwrap_or(Value::Null);
            let merged=stage==GithubPrStage::Merged;
            record("실제 GitHub PR 상태",if merged{!pr["merged_at"].is_null()&&pr["state"]=="closed"}else{pr["state"]=="open"&&pr["merged_at"].is_null()},if merged{"병합 완료"}else{"열린 PR"},pr["html_url"].as_str().unwrap_or_default().into());
            if merged {
                let current=git_text(&["branch","--show-current"]);
                record("병합한 기록을 로컬 main에 받기",current=="main"&&pr["merge_commit_sha"].as_str()==Some(&main)&&git_text(&["show","HEAD:memo.txt"])=="함께 읽는 메모","GitHub 병합 커밋을 main으로 받기",main.clone());
            }
        }
        if stage==GithubPrStage::Reviewed{
            let records=self.shell_completions()?;
            record("PR 변경 내용 직접 확인",records.iter().any(|r|r.success&&r.command.trim().starts_with("gh pr diff")),"gh pr diff 실행",String::new());
        }
        Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
    }
}
