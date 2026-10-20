//! The three standard courses ship with the app. GitHub still owns account and
//! progress events. Packaged content bootstraps offline; validated remote updates
//! remain authoritative after installation, including across app upgrades.
use crate::{content_updates::{Snapshot,SnapshotStore},repository_course::LessonRef};
use sha2::{Digest,Sha256};

pub const REPOSITORIES:[&str;3]=[
    "jhs512/mq3-course-redesigned-java-backend",
    "jhs512/mq3-course-redesigned-engineer-practical",
    "jhs512/mq3-course-redesigned-aice-associate",
];

pub fn course_source(repository:&str)->Option<&'static str>{
    match repository {
        "jhs512/mq3-course-redesigned-java-backend"=>Some(include_str!("../courses/redesigned-courses/java-backend.json")),
        "jhs512/mq3-course-redesigned-engineer-practical"=>Some(include_str!("../courses/redesigned-courses/engineer-practical.json")),
        "jhs512/mq3-course-redesigned-aice-associate"=>Some(include_str!("../courses/redesigned-courses/aice-associate.json")),
        _=>None,
    }
}

/// An older or externally composed reference keeps its original immutable pin.
/// Only an exact repository/revision/hash match may use the packaged bytes.
pub fn lesson_source(reference:&LessonRef)->Option<&'static str>{
    let row=crate::lesson_registry::by_revision(&reference.revision)?;
    if reference.repository!=format!("jhs512/mq3-lesson-redesigned-{}",row.key)
        || reference.sha256!=format!("{:x}",Sha256::digest(row.lesson.as_bytes())){return None}
    Some(row.lesson)
}

pub fn prepare(store:&SnapshotStore,repository:&str)->Result<Option<Snapshot>,String>{
    let Some(raw)=course_source(repository) else{return Ok(None)};
    store.prepare(repository,raw,|reference|lesson_source(reference).map(str::to_owned)
        .ok_or_else(||"앱에 포함된 수업 구성이 맞지 않아요. 앱을 다시 설치하세요.".into())).map(|snapshot|Some(snapshot.packaged()))
}

/// Quarantine the exact pre-sync published manifests observed on 2026-10-20.
/// These snapshots predate the current bundled lessons. New published content is
/// fetched normally; a README-only commit or JSON reformat must not roll back it.
pub fn prepare_update(store:&SnapshotStore,repository:&str,raw:&str,fetch:impl FnMut(&LessonRef)->Result<String,String>)->Result<Snapshot,String>{
    let baseline=match repository {
        "jhs512/mq3-course-redesigned-java-backend"=>Some("0159e22b91b86cc3c8f8fc2002ca0da07d3790d26a69ab82bb204d1d46cd6bd5"),
        "jhs512/mq3-course-redesigned-engineer-practical"=>Some("4388b1e84b0502aca3da76c53f5226f653a17cbe00671596e6555f708a6dd9ca"),
        "jhs512/mq3-course-redesigned-aice-associate"=>Some("7540fd01f8cfbd9d6a35bb69fb600b5facd27cc1831ad08971df4a40fb1278de"),
        _=>None,
    };
    let value:serde_json::Value=serde_json::from_str(raw).map_err(|error|error.to_string())?;
    if baseline.is_some_and(|hash|hash==format!("{:x}",Sha256::digest(value.to_string().as_bytes()))) {
        if let Some(current)=store.active(repository)? {if current.is_remote(){return Ok(current)}}
        if let Some(packaged)=prepare(store,repository)? {return Ok(packaged)}
    }
    store.prepare(repository,raw,fetch)
}
