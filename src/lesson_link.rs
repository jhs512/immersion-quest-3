//! Stable course-scoped links. Links choose content, never shell commands or
//! revisions: the normal manifest/hash/visibility checks still apply.
use serde::{Deserialize,Serialize};
use std::sync::{Mutex,OnceLock};
const WEB:&str="https://jhs512.github.io/immersion-quest-3/open/";
#[derive(Clone,Debug,PartialEq,Serialize,Deserialize)]
pub struct LessonLink {pub course:String,pub lesson:Option<String>}
impl LessonLink {
    pub fn new(course:&str,lesson:&str)->Result<Self,String>{
        if course.len()>160||!crate::repository_course::valid_repository(course)||lesson.is_empty()||lesson.len()>160||!lesson.bytes().all(|c|c.is_ascii_alphanumeric()||b"_-".contains(&c)) {return Err("코스와 수업 링크를 확인하세요.".into())}
        Ok(Self{course:course.into(),lesson:Some(lesson.into())})
    }
    pub fn course(course:&str)->Result<Self,String>{
        if course.len()>160||!crate::repository_course::valid_repository(course){return Err("코스 링크를 확인하세요.".into())}
        Ok(Self{course:course.into(),lesson:None})
    }
    pub fn parse(raw:&str)->Result<Self,String>{
        if raw.len()>2048{return Err("수업 링크가 너무 길어요.".into())}
        let url=url::Url::parse(raw).map_err(|_|"수업 링크 형식을 확인하세요.")?;
        let native=url.scheme()=="molipquest"&&url.host_str()==Some("open")&&matches!(url.path(),""|"/");
        let web=url.scheme()=="https"&&url.host_str()==Some("jhs512.github.io")&&url.path()=="/immersion-quest-3/open/";
        if !(native||web)||!url.username().is_empty()||url.password().is_some()||url.port().is_some()||url.fragment().is_some(){return Err("MQ 수업 링크를 확인하세요.".into())}
        let mut course=None;let mut lesson=None;
        for (key,value) in url.query_pairs(){match key.as_ref(){
            "course" if course.is_none()=>course=Some(value.into_owned()),
            "lesson" if lesson.is_none()=>lesson=Some(value.into_owned()),
            _=>return Err("수업 링크의 항목을 확인하세요.".into())
        }}
        let course=course.ok_or("코스가 없는 링크예요.")?;
        match lesson {Some(lesson)=>Self::new(&course,&lesson),None=>Self::course(&course)}
    }
    fn url(&self,base:&str)->String {let mut url=url::Url::parse(base).unwrap();url.query_pairs_mut().append_pair("course",&self.course);if let Some(lesson)=&self.lesson{url.query_pairs_mut().append_pair("lesson",lesson);}url.into()}
    pub fn web_url(&self)->String {self.url(WEB)}
    pub fn app_url(&self)->String {self.url("molipquest://open")}
    pub fn reference<'a>(&self,course:&'a crate::repository_course::CourseManifest)->Result<&'a crate::repository_course::LessonRef,String>{
        if course.repository!=self.course{return Err("링크와 코스가 일치하지 않아요.".into())}
        let lesson=self.lesson.as_deref().ok_or("코스 링크에는 선택한 수업이 없어요.")?;
        course.lessons.iter().find(|reference|reference.id==lesson).ok_or_else(||"코스에 이 수업이 없거나 현재 계정에서 열 수 없어요.".into())
    }
}
#[derive(Clone,Debug)]
pub enum Request {Open(LessonLink),Invalid(String),Focus}
static PENDING:OnceLock<Mutex<Option<Request>>>=OnceLock::new();
pub fn receive(raw:&str){let request=match LessonLink::parse(raw){Ok(link)=>Request::Open(link),Err(error)=>Request::Invalid(error)};put(request);}
fn put(request:Request){*PENDING.get_or_init(||Mutex::new(None)).lock().unwrap_or_else(|e|e.into_inner())=Some(request);}
pub fn take()->Option<Request>{PENDING.get_or_init(||Mutex::new(None)).lock().unwrap_or_else(|e|e.into_inner()).take()}
pub fn pending()->bool{PENDING.get_or_init(||Mutex::new(None)).lock().unwrap_or_else(|e|e.into_inner()).is_some()}

#[cfg(not(target_os="android"))]
mod instance;
#[cfg(not(target_os="android"))]
pub use instance::Instance;
