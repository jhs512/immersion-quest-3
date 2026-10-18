//! Append-only events: comments remain authoritative; the issue body is a readable summary.
use serde::{Deserialize,Serialize};
use std::collections::{BTreeMap,HashSet};

#[derive(Clone,Copy,Debug,Deserialize,Serialize,PartialEq,Eq)]
#[serde(rename_all="snake_case")]
pub enum StudyMode { Full, Review }
impl StudyMode { pub fn label(self)->&'static str { match self {Self::Full=>"풀모드",Self::Review=>"복습모드"} } }
#[derive(Clone,Debug,Deserialize,Serialize,PartialEq)]
pub struct ProgressKey { pub user_id:u64, pub course_id:String, pub lesson_id:String }
#[derive(Clone,Debug,Deserialize,Serialize,PartialEq)]
pub struct LearningEvent {
    pub id:String, pub key:ProgressKey, pub revision:String, pub mode:StudyMode,
    pub round:String, pub at:u64, pub kind:EventKind,
    #[serde(default)] pub task_id:Option<String>,
    #[serde(default)] pub passed:bool,
    #[serde(default)] pub required:Vec<String>,
    #[serde(default)] pub success_before_view:bool,
    #[serde(default,skip_serializing_if="Option::is_none")] pub prediction:Option<String>,
}
#[derive(Clone,Copy,Debug,Deserialize,Serialize,PartialEq)]
#[serde(rename_all="snake_case")]
pub enum EventKind { Started, Attempt, Viewed, ExampleRun, Completed, ExplanationViewed }
impl LearningEvent {
    pub fn new(key:ProgressKey, revision:&str, mode:StudyMode, round:&str, kind:EventKind)->Self {
        Self {id:new_id(),key,revision:revision.into(),mode,round:round.into(),at:now(),kind,task_id:None,passed:false,required:vec![],success_before_view:false,prediction:None}
    }
    pub fn comment(&self)->String { format!("{} · {} · {}\n\n<!-- mq3-event:{} -->",self.mode.label(),self.revision,match self.kind {EventKind::Started=>"학습 시작",EventKind::Attempt=>if self.passed {"문제 통과"}else{"문제 다시 풀기"},EventKind::Viewed=>"개념 확인",EventKind::ExampleRun=>"예제 실행",EventKind::Completed=>"수업 완료",EventKind::ExplanationViewed=>"해설 확인"},serde_json::to_string(self).expect("event")) }
}

#[derive(Default,PartialEq,Debug)]
pub struct ExplanationInfo {pub before_success:bool,pub after_success:bool}
pub fn explanation_info(events:&[LearningEvent],task_id:&str)->ExplanationInfo {
    let mut info=ExplanationInfo::default();
    for event in events.iter().filter(|e|e.kind==EventKind::ExplanationViewed && e.task_id.as_deref()==Some(task_id)) {
        if event.success_before_view {info.after_success=true;} else {info.before_success=true;}
    }
    info
}
pub fn now()->u64 {std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs()}
pub fn new_id()->String {
    let mut bytes=[0u8;16];
    ring::rand::SecureRandom::fill(&ring::rand::SystemRandom::new(),&mut bytes).expect("system random");
    bytes.iter().map(|b|format!("{b:02x}")).collect()
}
pub fn marker(key:&ProgressKey)->String {format!("<!-- mq3-progress:{} -->",serde_json::to_string(key).expect("key"))}
pub fn parse_event(body:&str)->Option<LearningEvent> { let text=body.split("<!-- mq3-event:").nth(1)?.split(" -->").next()?;serde_json::from_str(text).ok() }
pub fn merge(events:impl IntoIterator<Item=LearningEvent>, key:&ProgressKey)->Vec<LearningEvent> {
    let mut seen=HashSet::new(); let mut result:Vec<_>=events.into_iter().filter(|e|e.key==*key && seen.insert(e.id.clone())).collect();
    result.sort_by(|a,b|(a.at,&a.id).cmp(&(b.at,&b.id))); result
}
pub fn passed_in_round(events:&[LearningEvent], revision:&str, mode:StudyMode, round:&str)->HashSet<String> {
    events.iter().filter(|e| e.revision==revision && e.mode==mode && e.round==round && e.kind==EventKind::Attempt && e.passed).filter_map(|e|e.task_id.clone()).collect()
}

/// New stable-code problems retain achievement across wording/reordering revisions.
/// A review round still starts fresh; legacy IDs retain their original revision semantics.
pub fn passed_for_study(events:&[LearningEvent], revision:&str, mode:StudyMode, round:&str)->HashSet<String> {
    let mut passed=passed_in_round(events,revision,mode,round);
    if mode==StudyMode::Full {
        passed.extend(events.iter().filter(|e|e.kind==EventKind::Attempt && e.passed)
            .filter_map(|e|e.task_id.as_ref()).filter(|id|crate::repository_course::resource_code(id,"stp")).cloned());
    }
    passed
}
#[derive(Clone,Debug,Default,PartialEq)]
pub struct LessonStatus { pub completed:bool,pub current:bool,pub full_completions:usize,pub review_completions:usize }
pub fn status(events:&[LearningEvent], revision:&str, required:&[String])->LessonStatus {
    let mut rounds:BTreeMap<(String,String,u8),(&LearningEvent,bool)>=BTreeMap::new();
    for e in events.iter().filter(|e|e.kind==EventKind::Completed) {
        let same_key:Vec<_>=events.iter().filter(|other|other.key==e.key).cloned().collect();
        let passed=passed_for_study(&same_key,&e.revision,e.mode,&e.round);
        if e.required.is_empty() || !e.required.iter().all(|id|passed.contains(id)) {continue}
        let stable=!required.is_empty() && required.iter().all(|id|crate::repository_course::resource_code(id,"stp"));
        let known=passed_for_study(&same_key,revision,StudyMode::Full,"");
        let current=if stable {required.iter().all(|id|known.contains(id))} else {e.revision==revision && required.iter().all(|id|passed.contains(id))};
        rounds.entry((e.round.clone(),e.revision.clone(),if e.mode==StudyMode::Full{0}else{1})).or_insert((e,current));
    }
    LessonStatus {completed:!rounds.is_empty(),current:rounds.values().any(|(_,c)|*c),full_completions:rounds.values().filter(|(e,_)|e.mode==StudyMode::Full).count(),review_completions:rounds.values().filter(|(e,_)|e.mode==StudyMode::Review).count()}
}
pub fn summary(key:&ProgressKey,title:&str,events:&[LearningEvent])->String {
    let latest=events.iter().max_by_key(|e|e.at);
    let revision=latest.map(|e|e.revision.as_str()).unwrap_or("");
    let state=status(events,revision,&[]);
    let mut attempts:BTreeMap<&str,usize>=BTreeMap::new();
    for e in events.iter().filter(|e|e.kind==EventKind::Attempt) {if let Some(id)=e.task_id.as_deref(){*attempts.entry(id).or_default()+=1}}
    let tasks=attempts.into_iter().map(|(id,count)|format!("- `{id}`: {} · 시도 {count}회",if events.iter().any(|e|e.kind==EventKind::Attempt&&e.passed&&e.task_id.as_deref()==Some(id)){"통과"}else{"학습 중"})).collect::<Vec<_>>().join("\n");
    format!("# {title}\n\n학습자 ID: {}\n코스: {}\n수업: {}\n\n풀모드 완료: {}회\n복습모드 완료: {}회\n최근 버전: {revision}\n\n{tasks}\n\n학습·복습의 원본 기록은 아래 댓글에 있어요.\n\n{}",key.user_id,key.course_id,key.lesson_id,state.full_completions,state.review_completions,marker(key))
}
