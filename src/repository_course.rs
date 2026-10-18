//! Published course composition and reusable lesson content. No account state lives here.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashSet};

pub const COURSE_REPOSITORY: &str = "jhs512/mq3-course-java-backend";

pub fn initial_repository() -> &'static str {
    if crate::pilot_source::enabled() { crate::pilot_source::REPOSITORY } else { COURSE_REPOSITORY }
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct CourseManifest {
    pub schema_version: u32,
    pub id: String,
    pub title: String,
    pub description: String,
    pub repository: String,
    pub lessons: Vec<LessonRef>,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct LessonRef {
    pub id: String,
    pub title: String,
    pub repository: String,
    pub revision: String,
    pub sha256: String,
    #[serde(default)] pub prerequisites: Vec<String>,
    #[serde(default = "yes")] pub required: bool,
    #[serde(default = "yes")] pub review_enabled: bool,
}
fn yes() -> bool { true }

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Lesson {
    pub schema_version: u32,
    pub id: String,
    pub revision: String,
    pub title: String,
    pub description: String,
    pub sources: Vec<String>,
    #[serde(default)] pub objectives: Vec<String>,
    #[serde(default)] pub chapters: Vec<LessonChapter>,
    pub sections: Vec<Section>,
    pub tasks: Vec<Task>,
    #[serde(default = "yes")] pub review_enabled: bool,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct LessonChapter {
    pub id: String,
    pub title: String,
    pub objectives: Vec<String>,
    pub units: Vec<LessonUnit>,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct LessonUnit {
    pub id: String,
    pub title: String,
    pub objectives: Vec<String>,
    pub premise: String,
    pub steps: Vec<LessonStep>,
}
/// The hierarchy owns order and learning goals; task payloads are indexed by this stable ID.
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct LessonStep {
    pub id: String,
    pub objectives: Vec<String>,
}

pub fn resource_code(id: &str, prefix: &str) -> bool {
    let Some(uuid) = id.strip_prefix(prefix).and_then(|rest| rest.strip_prefix('_')) else { return false };
    let b = uuid.as_bytes();
    b.len() == 36 && b.iter().enumerate().all(|(i, c)| {
        if [8, 13, 18, 23].contains(&i) { *c == b'-' } else { c.is_ascii_hexdigit() && !c.is_ascii_uppercase() }
    }) && b[14] == b'4' && matches!(b[19], b'8' | b'9' | b'a' | b'b')
}

fn goals_valid(goals: &[String]) -> bool {
    !goals.is_empty() && goals.len() <= 20 && goals.iter().all(|g| !g.trim().is_empty() && g.len() <= 4000)
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Section {
    pub id: String,
    pub title: String,
    pub body: String,
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Task {
    pub id: String,
    pub title: String,
    pub goal: String,
    pub language: TaskLanguage,
    pub starter_code: String,
    pub solution: String,
    #[serde(default)] pub entry_file: String,
    #[serde(default)] pub files: BTreeMap<String,String>,
    #[serde(default)] pub tests: Vec<Case>,
    #[serde(default)] pub checker: Option<String>,
    #[serde(default)] pub git_checks: Option<GitChecks>,
    #[serde(default)] pub web_checks: Vec<serde_json::Value>,
    #[serde(default)] pub narration: Vec<serde_json::Value>,
    #[serde(default)] pub hints: Vec<String>,
    #[serde(default)] pub mutations: Vec<BTreeMap<String,String>>,
    /// C only: rerun with prepared values replaced, so a memorized output does not pass.
    #[serde(default, skip_serializing_if="Vec::is_empty")] pub variations: Vec<Variation>,
    #[serde(default = "yes")] pub required: bool,
}
/// Replace the first initializer of each named variable (C literal text), then expect this output.
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Variation { pub values: BTreeMap<String,String>, pub expected: String }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all="snake_case")]
pub enum TaskLanguage { Java, JavaProject, Junit, Git, Javascript, Web, Python, C }
impl TaskLanguage {
    // The editor bundle has no C grammar; Java's is the closest C-family highlighting.
    pub fn editor(self) -> &'static str { match self {
        Self::Java|Self::JavaProject|Self::Junit|Self::C => "java", Self::Javascript => "javascript", Self::Web => "html", Self::Git => "shell", Self::Python=>"python",
    }}
    pub fn filename(self) -> &'static str { match self {
        Self::Java|Self::JavaProject|Self::Junit => "Main.java", Self::Javascript=>"main.js", Self::Web=>"index.html", Self::Git=>"practice.sh", Self::Python=>"main.py", Self::C=>"main.c",
    }}
}
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Case { pub input:String, pub expected:String }
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct GitChecks {
    pub minimum_commits: usize,
    pub head_message: String,
    pub tracked_files: BTreeMap<String,String>,
    #[serde(default)] pub branch: Option<String>,
    #[serde(default)] pub pushed: bool,
}

pub fn valid_repository(repository: &str) -> bool {
    let pieces:Vec<_> = repository.split('/').collect();
    pieces.len()==2 && pieces.iter().all(|p| !p.is_empty() && *p!="." && *p!=".." && p.bytes().all(|c| c.is_ascii_alphanumeric() || b"-_.".contains(&c)))
}
pub fn safe_file(path: &str) -> bool {
    !path.is_empty() && path.len()<240 && !path.contains(['\\',':']) && path.split('/').all(|p| !p.is_empty() && p!="." && p!=".." && p.bytes().all(|c| c.is_ascii_alphanumeric() || b"-_.".contains(&c)))
}
impl CourseManifest {
    pub fn parse(text: &str) -> Result<Self,String> {
        let course:Self=serde_json::from_str(text).map_err(|e|e.to_string())?;
        let mut ids=HashSet::new();
        if !matches!(course.schema_version,1|2) || course.id.is_empty() || course.title.is_empty() || !valid_repository(&course.repository) || course.lessons.is_empty() || course.lessons.len()>200 { return Err("코스 구성정보를 확인하세요.".into()); }
        if course.schema_version==2 && (!resource_code(&course.id,"crs") || course.lessons.iter().any(|l|!resource_code(&l.id,"lsn"))) {return Err("코스와 수업의 고유 코드를 확인하세요.".into())}
        for l in &course.lessons {
            if !ids.insert(l.id.clone()) || l.id.is_empty() || l.title.is_empty() || !valid_repository(&l.repository) || l.revision.is_empty() || l.revision.contains(['/', '\\', '?','#']) || l.sha256.len()!=64 || !l.sha256.bytes().all(|c|c.is_ascii_hexdigit()) { return Err("수업 참조와 버전·해시를 확인하세요.".into()); }
        }
        if course.lessons.iter().any(|l| l.prerequisites.iter().any(|p| !ids.contains(p) || *p==l.id)) { return Err("선수 수업 ID를 확인하세요.".into()); }
        Ok(course)
    }
}
impl Lesson {
    pub fn parse(text:&str, reference:&LessonRef)->Result<Self,String> {
        use sha2::{Digest,Sha256};
        let hash=format!("{:x}",Sha256::digest(text.as_bytes()));
        if hash!=reference.sha256.to_lowercase() { return Err("수업 내용이 코스에 고정한 버전과 달라요. 코스를 새로 불러오세요.".into()); }
        let lesson:Self=serde_json::from_str(text).map_err(|e|e.to_string())?;
        lesson.validate()?;
        if lesson.id!=reference.id || lesson.revision!=reference.revision { return Err("수업 ID 또는 버전이 맞지 않아요.".into()); }
        if lesson.review_enabled!=reference.review_enabled {return Err("코스와 수업의 복습모드 설정이 달라요.".into())}
        Ok(lesson)
    }
    pub fn validate(&self)->Result<(),String> {
        let mut ids=HashSet::new();
        if !matches!(self.schema_version,1|2) || self.id.is_empty() || self.title.is_empty() || self.tasks.is_empty() || !self.tasks.iter().any(|t| t.required) || self.tasks.len()>200 { return Err("수업 구성과 필수 문제를 확인하세요.".into()); }
        if self.schema_version==2 {self.validate_hierarchy()?;}
        for t in &self.tasks {
            if t.hints.len()>5||t.hints.iter().any(|hint|hint.len()>8000){return Err("힌트 개수와 길이를 확인하세요.".into())}
            if !ids.insert(&t.id) || t.id.is_empty() || t.solution.len()>65536 || t.starter_code.len()>65536 || (!t.entry_file.is_empty() && !safe_file(&t.entry_file)) || t.files.iter().any(|(p,v)| !safe_file(p) || v.len()>200_000) || t.files.len()>80 || t.tests.len()>50 || t.mutations.len()>20 || t.mutations.iter().any(|files|files.len()>80||files.iter().any(|(p,v)|!safe_file(p)||v.len()>200_000)) { return Err("문제 ID와 파일 크기·경로를 확인하세요.".into()); }
            if matches!(t.language,TaskLanguage::Web)&&t.web_checks.is_empty() || matches!(t.language,TaskLanguage::Git)&&t.git_checks.is_none() || matches!(t.language,TaskLanguage::JavaProject|TaskLanguage::Javascript|TaskLanguage::C)&&t.tests.is_empty() {return Err("필수 문제의 실행 검사 기준을 확인하세요.".into())}
            if t.variations.len()>20 || t.variations.iter().any(|v|v.values.is_empty()||v.values.len()>20||v.expected.len()>65536||v.values.keys().any(|name|name.is_empty()||!name.bytes().all(|c|c.is_ascii_alphanumeric()||c==b'_'))) {return Err("값 바꾸기 검사를 확인하세요.".into())}
        }
        Ok(())
    }
    pub fn required_tasks(&self)->Vec<String> { self.tasks.iter().filter(|t|t.required).map(|t|t.id.clone()).collect() }

    fn validate_hierarchy(&self) -> Result<(), String> {
        if !resource_code(&self.id,"lsn") || !goals_valid(&self.objectives) || self.chapters.is_empty() || self.chapters.len()>100 || !self.sections.is_empty() {
            return Err("수업 고유 코드와 교육 목표·챕터 구성을 확인하세요.".into());
        }
        let mut ids = HashSet::from([self.id.as_str()]);
        let mut order = Vec::new();
        for chapter in &self.chapters {
            if !resource_code(&chapter.id,"chp") || !ids.insert(chapter.id.as_str()) || chapter.title.trim().is_empty() || !goals_valid(&chapter.objectives) || chapter.units.is_empty() || chapter.units.len()>100 {
                return Err("챕터의 고유 코드·교육 목표·단원을 확인하세요.".into());
            }
            for unit in &chapter.units {
                if !resource_code(&unit.id,"unt") || !ids.insert(unit.id.as_str()) || unit.title.trim().is_empty() || !goals_valid(&unit.objectives) || unit.steps.is_empty() || unit.steps.len()>200 || unit.premise.len()>16000 {
                    return Err("단원의 고유 코드·교육 목표·스텝을 확인하세요.".into());
                }
                for step in &unit.steps {
                    if !resource_code(&step.id,"stp") || !ids.insert(step.id.as_str()) || !goals_valid(&step.objectives) {
                        return Err("스텝의 고유 코드와 교육 목표를 확인하세요.".into());
                    }
                    order.push(step.id.as_str());
                }
            }
        }
        if order != self.tasks.iter().map(|task|task.id.as_str()).collect::<Vec<_>>() {
            return Err("단원의 스텝과 문제의 연결·순서를 확인하세요.".into());
        }
        Ok(())
    }

    pub fn context_for(&self, task_id: &str) -> Option<(&LessonChapter, &LessonUnit, &LessonStep)> {
        self.chapters.iter().find_map(|chapter| chapter.units.iter().find_map(|unit| {
            unit.steps.iter().find(|step| step.id == task_id).map(|step| (chapter, unit, step))
        }))
    }
}
