//! The three standard courses ship with the app. GitHub still owns account and
//! progress events; an outdated server manifest cannot replace these lesson bytes.
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
        .ok_or_else(||"앱에 포함된 수업 구성이 맞지 않아요. 앱을 다시 설치하세요.".into())).map(Some)
}
