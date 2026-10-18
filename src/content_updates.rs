//! A complete validated course snapshot is the unit of content installation.
//! Preparing a candidate never changes the installed snapshot or learning records.
use crate::repository_course::{CourseManifest,Lesson,LessonRef};
use serde::{Deserialize,Serialize};
use std::{collections::BTreeMap,path::{Path,PathBuf},io::Write};
use sha2::{Digest,Sha256};

#[derive(Clone,Debug,PartialEq)]
pub struct Snapshot { course:CourseManifest, lessons:BTreeMap<String,Lesson>, document:StoredSnapshot }
#[derive(Clone,Debug,Deserialize,Serialize,PartialEq)]
struct StoredSnapshot { repository:String, course:String, lessons:BTreeMap<String,String> }
#[derive(Clone,Debug,Default,PartialEq)]
pub struct ContentChanges { pub added:Vec<String>, pub removed:Vec<String>, pub modified:Vec<String> }
impl Snapshot {
    pub fn course(&self)->&CourseManifest { &self.course }
    pub fn lesson(&self,reference:&LessonRef)->Option<&Lesson> {
        self.course.lessons.iter().find(|installed|*installed==reference)?;
        self.lessons.get(&reference.id)
    }
    pub fn changes_from(&self,previous:&Snapshot)->ContentChanges {
        let tasks=|snapshot:&Snapshot| snapshot.lessons.values().flat_map(|lesson|lesson.tasks.iter().map(move|task|((lesson.id.clone(),task.id.clone()),task.clone()))).collect::<BTreeMap<_,_>>();
        let before=tasks(previous); let after=tasks(self);
        let id=|key:&(String,String)|key.1.clone();
        ContentChanges {
            added:after.keys().filter(|key|!before.contains_key(*key)).map(id).collect(),
            removed:before.keys().filter(|key|!after.contains_key(*key)).map(id).collect(),
            modified:after.iter().filter(|(key,value)|before.get(*key).is_some_and(|old|old!=*value)).map(|(key,_)|id(key)).collect(),
        }
    }
    pub fn fingerprint(&self)->String { format!("{:x}",Sha256::digest(serde_json::to_vec(&(&self.course,&self.lessons)).expect("snapshot serialization"))) }
}
#[derive(Clone)]
pub struct SnapshotStore { root:PathBuf }
impl SnapshotStore {
    pub fn new(root:impl AsRef<Path>)->Self { Self{root:root.as_ref().to_owned()} }
    fn path(&self,repository:&str)->Result<PathBuf,String> {
        if !crate::repository_course::valid_repository(repository) {return Err("코스 저장소를 확인하세요.".into())}
        Ok(self.root.join(format!("{:x}.json",Sha256::digest(repository.as_bytes()))))
    }
    pub fn prepare(&self,repository:&str,raw:&str,mut fetch:impl FnMut(&LessonRef)->Result<String,String>)->Result<Snapshot,String> {
        self.path(repository)?;
        let course=CourseManifest::parse(raw)?;
        if course.repository!=repository {return Err("코스의 저장소 식별자가 맞지 않아요.".into())}
        let mut lessons=BTreeMap::new();
        let mut documents=BTreeMap::new();
        for reference in &course.lessons {
            let document=fetch(reference)?;
            lessons.insert(reference.id.clone(),Lesson::parse(&document,reference)?);
            documents.insert(reference.id.clone(),document);
        }
        Ok(Snapshot{course,lessons,document:StoredSnapshot{repository:repository.into(),course:raw.into(),lessons:documents}})
    }
    pub fn active(&self,repository:&str)->Result<Option<Snapshot>,String> {
        let raw=match std::fs::read(self.path(repository)?) {Ok(raw)=>raw,Err(e) if e.kind()==std::io::ErrorKind::NotFound=>return Ok(None),Err(e)=>return Err(e.to_string())};
        let stored:StoredSnapshot=serde_json::from_slice(&raw).map_err(|e|e.to_string())?;
        if stored.repository!=repository {return Err("저장된 코스 식별자가 맞지 않아요.".into())}
        self.prepare(repository,&stored.course,|reference|stored.lessons.get(&reference.id).cloned().ok_or_else(||"저장된 수업이 없어요.".into())).map(Some)
    }
    pub fn remove(&self,repository:&str)->Result<(),String> {
        match std::fs::remove_file(self.path(repository)?) { Ok(())=>Ok(()),Err(e) if e.kind()==std::io::ErrorKind::NotFound=>Ok(()),Err(e)=>Err(e.to_string()) }
    }
    pub fn apply(&self,candidate:&Snapshot)->Result<(),String> {
        let path=self.path(&candidate.course.repository)?;
        if self.active(&candidate.course.repository)?.is_some_and(|current|current.course.id!=candidate.course.id) {
            return Err("코스의 고유 코드가 바뀌었어요. 새 코스로 추가하세요.".into())
        }
        std::fs::create_dir_all(&self.root).map_err(|e|e.to_string())?;
        let mut temporary=tempfile::NamedTempFile::new_in(&self.root).map_err(|e|e.to_string())?;
        serde_json::to_writer(&mut temporary,&candidate.document).map_err(|e|e.to_string())?;
        temporary.flush().map_err(|e|e.to_string())?;
        temporary.as_file().sync_all().map_err(|e|e.to_string())?;
        temporary.persist(path).map_err(|e|e.to_string())?;
        Ok(())
    }
}

pub fn installed_store()->Result<SnapshotStore,String> { Ok(SnapshotStore::new(crate::data_dir()?.join("content-snapshots"))) }
