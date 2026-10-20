pub mod assistant;
pub mod avatar;
pub mod markdown;
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::{collections::HashSet, path::Path};
pub mod curriculum;
pub mod doctor;
pub mod drafts;
pub mod java;
pub mod learning_store;
pub mod prefs;
pub mod runner;
pub mod repository_course;
pub mod course_authoring;
pub mod issue_progress;
pub mod github_player;
pub mod bundled_courses;
pub mod course_visibility;
pub mod pilot_source;
pub mod lesson_registry;
pub mod lesson_runner;
pub mod task_interaction;
pub mod supporting_materials;
pub mod tts;
pub mod updater;
pub mod update_handoff;
pub mod content_updates;
pub mod change_history;
pub mod git_practice;
#[cfg(not(target_os="android"))]
mod process_scope;
#[cfg(not(target_os = "android"))]
pub mod setup_terminal;

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Course {
    pub id: String,
    pub title: String,
    pub description: String,
    pub chapters: Vec<Chapter>,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Chapter {
    pub id: String,
    pub title: String,
    pub units: Vec<Unit>,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Unit {
    pub id: String,
    pub title: String,
    #[serde(default)]
    pub language: Language,
    #[serde(default)]
    pub solution: String,
    #[serde(default)]
    pub content: String,
    #[serde(default)]
    pub activities: Vec<curriculum::Activity>,
    #[serde(default)]
    pub starter_code: String,
    #[serde(default)]
    pub tests: Vec<InputOutputTest>,
    #[serde(default)]
    pub checker: Option<String>,
    #[serde(default)]
    pub blanks: Vec<String>,
    #[serde(default = "initial_revision")]
    pub revision: i64,
    #[serde(default)]
    pub reset_completion: bool,
    /// The "human" answer prompt: the few lines a person actually types into an AI for this problem.
    #[serde(default)]
    pub prompt: Option<String>,
    /// Which words in `prompt` carry the expertise and why; shown in the prompt guide.
    #[serde(default)]
    pub prompt_why: Option<String>,
}

#[derive(Clone, Copy, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Language {
    #[default]
    Python,
    Java,
}

impl Language {
    pub fn name(self) -> &'static str {
        match self {
            Self::Python => "python",
            Self::Java => "java",
        }
    }
    pub fn filename(self) -> &'static str {
        match self {
            Self::Python => "main.py",
            Self::Java => "Main.java",
        }
    }
}

pub const DEFAULT_COURSE: &str = include_str!("../courses/java-basics.json");

#[cfg(test)]
mod course_authoring_tests;

fn initial_revision() -> i64 {
    1
}

/// Start a course over: clear completions, attempts, saved code and quiz answers.
pub fn reset_progress(course: &str) -> Result<(), String> {
    learning_store::LearningStore::user_store()?.reset(course)?;
    drafts::clear_course(course)
}

/// Local folder for progress and drafts. Android has no XDG/HOME, so fall back to the
/// app's own files directory (the package id from Dioxus.toml).
pub fn data_dir() -> Result<std::path::PathBuf, String> {
    if crate::pilot_source::enabled() {
        return crate::pilot_source::data_dir();
    }
    if let Some(path) = std::env::var_os("MOLIP_DATA_DIR") {
        let dir = std::path::PathBuf::from(path);
        std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        return Ok(dir);
    }
    let dir = directories::ProjectDirs::from("", "MolipQuest", "MolipQuest")
        .map(|dirs| dirs.data_local_dir().to_path_buf())
        .or_else(|| {
            std::env::var_os("HOME").map(|home| std::path::PathBuf::from(home).join(".molip-quest"))
        })
        .or_else(|| {
            cfg!(target_os = "android")
                .then(|| std::path::PathBuf::from("/data/data/dev.molipquest.app/files"))
        })
        .ok_or("저장 위치를 찾을 수 없습니다.")?;
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir)
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct InputOutputTest {
    pub input: String,
    pub expected: String,
}

impl Course {
    pub fn parse(source: &str) -> Result<Self, String> {
        let course: Self = serde_json::from_str(source).map_err(|e| e.to_string())?;
        if course.id.trim().is_empty()
            || course.title.trim().is_empty()
            || course.chapters.is_empty()
        {
            return Err("수업 ID, 제목과 챕터가 필요합니다.".into());
        }
        let mut chapters = HashSet::new();
        let mut units = HashSet::new();
        for chapter in &course.chapters {
            if chapter.id.trim().is_empty()
                || chapter.title.trim().is_empty()
                || !chapters.insert(&chapter.id)
                || chapter.units.is_empty()
            {
                return Err("챕터 ID는 고유해야 하며 제목과 단원이 필요합니다.".into());
            }
            for unit in &chapter.units {
                if unit.id.trim().is_empty()
                    || unit.title.trim().is_empty()
                    || !units.insert(&unit.id)
                {
                    return Err("단원 ID는 수업 내에서 고유해야 하며 제목이 필요합니다.".into());
                }
                let mut blanks = HashSet::new();
                for blank in &unit.blanks {
                    if blank.trim().is_empty()
                        || blank.contains('{')
                        || blank.contains('}')
                        || !blanks.insert(blank)
                        || !unit.starter_code.contains(&format!("{{{{{blank}}}}}"))
                    {
                        return Err("빈칸 ID와 코드 템플릿을 확인해 주세요.".into());
                    }
                }
                if unit.tests.len() > 30
                    || unit
                        .tests
                        .iter()
                        .any(|t| t.input.len() > 65536 || t.expected.len() > 65536)
                    || unit.starter_code.len() > 65536
                    || unit.checker.as_ref().is_some_and(|c| c.len() > 65536)
                {
                    return Err(
                        "코드·입출력은 64KB 이하, 테스트는 30개 이하로 작성해 주세요.".into(),
                    );
                }
            }
        }
        curriculum::validate(&course)?;
        Ok(course)
    }

    pub fn total_units(&self) -> usize {
        self.chapters.iter().map(|c| c.units.len()).sum()
    }

    pub fn completed_units(&self, completed: &HashSet<String>) -> usize {
        self.chapters
            .iter()
            .flat_map(|c| &c.units)
            .filter(|u| completed.contains(&u.id))
            .count()
    }
}

pub struct ProgressStore(Connection);

impl ProgressStore {
    pub fn open(path: &Path) -> rusqlite::Result<Self> {
        let connection = Connection::open(path)?;
        connection.execute_batch(
            "CREATE TABLE IF NOT EXISTS unit_progress (
             classroom_id TEXT NOT NULL, student_id TEXT NOT NULL,
             course_id TEXT NOT NULL, unit_id TEXT NOT NULL,
             PRIMARY KEY(classroom_id, student_id, course_id, unit_id));",
        )?;
        Ok(Self(connection))
    }

    pub fn completed(
        &self,
        classroom: &str,
        student: &str,
        course: &str,
    ) -> rusqlite::Result<HashSet<String>> {
        let mut statement = self.0.prepare(
            "SELECT unit_id FROM unit_progress WHERE classroom_id=?1 AND student_id=?2 AND course_id=?3"
        )?;
        let rows = statement.query_map(params![classroom, student, course], |row| row.get(0))?;
        rows.collect()
    }

    pub fn set_completed(
        &self,
        classroom: &str,
        student: &str,
        course: &Course,
        unit: &str,
        completed: bool,
    ) -> Result<(), String> {
        if !course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .any(|u| u.id == unit)
        {
            return Err("수업에 없는 단원입니다.".into());
        }
        let sql = if completed {
            "INSERT OR IGNORE INTO unit_progress VALUES (?1, ?2, ?3, ?4)"
        } else {
            "DELETE FROM unit_progress WHERE classroom_id=?1 AND student_id=?2 AND course_id=?3 AND unit_id=?4"
        };
        self.0
            .execute(sql, params![classroom, student, course.id, unit])
            .map_err(|e| e.to_string())?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn course() -> Course {
        Course::parse(include_str!("../courses/getting-started.json")).unwrap()
    }

    #[test]
    fn progress_persists_and_is_scoped_to_classroom_student_and_course() {
        let directory = tempfile::tempdir().unwrap();
        let path = directory.path().join("progress.sqlite3");
        let course = course();
        {
            let store = ProgressStore::open(&path).unwrap();
            store
                .set_completed("a", "student", &course, "choose-tool", true)
                .unwrap();
            store
                .set_completed("a", "student", &course, "choose-tool", true)
                .unwrap();
        }
        let store = ProgressStore::open(&path).unwrap();
        assert_eq!(
            store.completed("a", "student", &course.id).unwrap().len(),
            1
        );
        assert!(store
            .completed("b", "student", &course.id)
            .unwrap()
            .is_empty());
        assert!(store
            .completed("a", "other", &course.id)
            .unwrap()
            .is_empty());
        assert!(store
            .completed("a", "student", "other-course")
            .unwrap()
            .is_empty());
        assert!(store
            .set_completed("a", "student", &course, "missing", true)
            .is_err());
        store
            .set_completed("a", "student", &course, "choose-tool", false)
            .unwrap();
        assert!(store
            .completed("a", "student", &course.id)
            .unwrap()
            .is_empty());
    }

    #[test]
    fn duplicate_units_are_rejected_and_removed_units_do_not_count() {
        let source = include_str!("../courses/getting-started.json");
        assert!(Course::parse(&source.replace("\"review\"", "\"try\"")).is_err());
        let completed = HashSet::from(["try".into(), "removed-unit".into()]);
        assert_eq!(course().completed_units(&completed), 1);
        assert_eq!(course().total_units(), 4);
    }
}

pub mod pilot_session;

#[cfg(test)]
mod sql_practice_tests;

mod sql_practice;
