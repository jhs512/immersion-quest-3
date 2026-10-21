//! Read-only, bounded snapshots of the real practice repository. Never trace these
//! queries: visualisation must not satisfy command goals or trigger itself.
use super::GitPractice;
use serde::Serialize;

#[derive(Clone,Debug,Default,PartialEq,Serialize)]
pub struct GitGraphSnapshot {
    pub initialized:bool,
    pub head:Option<String>,
    pub branch:Option<String>,
    pub commits:Vec<GitGraphCommit>,
    pub references:Vec<GitGraphRef>,
    pub changes:Vec<String>,
    pub merging:bool,
    pub truncated:bool,
}
#[derive(Clone,Debug,PartialEq,Serialize)]
pub struct GitGraphCommit {pub id:String,pub parents:Vec<String>,pub subject:String}
#[derive(Clone,Debug,PartialEq,Serialize)]
pub struct GitGraphRef {pub id:String,pub name:String,pub remote:bool}

impl GitPractice {
    pub fn graph_snapshot(&self)->Result<GitGraphSnapshot,String> {
        let work=self.work();
        // An uninitialised exercise is expected; do not fall through to an
        // enclosing repository or invent a first commit.
        if !work.join(".git").exists(){return Ok(GitGraphSnapshot::default())}
        let query=|args:&[&str]|self.execute(&work,args,false);
        let inside=query(&["rev-parse","--is-inside-work-tree"])?;
        if !inside.status.success(){return Err("커밋 그래프를 읽지 못했어요. 저장소를 확인하세요.".into())}
        let text=|output:std::process::Output|->Result<String,String>{
            if output.status.success(){Ok(String::from_utf8_lossy(&output.stdout).replace("\r\n","\n"))}
            else{Err("저장소가 바뀌는 중이에요. 그래프를 다시 확인하세요.".into())}
        };
        let mut snapshot=GitGraphSnapshot{initialized:true,..Default::default()};
        let branch=query(&["symbolic-ref","--quiet","--short","HEAD"])?;
        if branch.status.success(){snapshot.branch=Some(text(branch)?.trim().into())}
        let head=query(&["rev-parse","--verify","HEAD"])?;
        if head.status.success(){snapshot.head=Some(text(head)?.trim().into())}
        let refs=text(query(&["for-each-ref","--format=%(objectname)%09%(refname:short)%09%(refname)","refs/heads","refs/remotes"])?)?;
        for line in refs.lines(){
            let fields:Vec<_>=line.splitn(3,'\t').collect();
            if fields.len()==3 {snapshot.references.push(GitGraphRef{id:fields[0].into(),name:fields[1].into(),remote:fields[2].starts_with("refs/remotes/")});}
        }
        if snapshot.head.is_some()||!snapshot.references.is_empty(){
            // Include HEAD explicitly so detached HEAD remains visible even
            // when it is not reachable from any branch.
            let mut args=vec!["log","--all","--topo-order","--max-count=201","--format=%H%x1f%P%x1f%s"];
            if snapshot.head.is_some(){args.push("HEAD");}
            let log=text(query(&args)?)?;
            for line in log.lines(){
                let fields:Vec<_>=line.splitn(3,'\x1f').collect();
                if fields.len()==3 {snapshot.commits.push(GitGraphCommit{id:fields[0].into(),parents:fields[1].split_whitespace().map(str::to_owned).collect(),subject:fields[2].into()});}
            }
            snapshot.truncated=snapshot.commits.len()>200;
            snapshot.commits.truncate(200);
        }
        let status=text(query(&["--no-optional-locks","status","--porcelain=v1","--untracked-files=normal"])?)?;
        snapshot.changes=status.lines().map(str::to_owned).collect();
        snapshot.merging=query(&["rev-parse","--quiet","--verify","MERGE_HEAD"])?.status.success();
        Ok(snapshot)
    }
}
