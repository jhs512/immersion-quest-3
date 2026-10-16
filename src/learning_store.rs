use crate::{runner::TestReport, Unit};
use rusqlite::OptionalExtension;
use rusqlite::{params, Connection};
use std::{collections::HashSet, path::Path};

pub struct LearningStore(Connection);
impl LearningStore {
    pub fn quiz_passed(
        &self,
        course: &str,
        unit: &Unit,
        questions: &[crate::curriculum::Question],
    ) -> Result<HashSet<String>, String> {
        let mut passed = HashSet::new();
        for q in questions {
            let key = format!("{}/question/{}", unit.id, q.id);
            let exists:bool = self.0.query_row("SELECT EXISTS(SELECT 1 FROM completed WHERE course=?1 AND unit=?2 AND revision=?3)",params![course,key,unit.revision],|r|r.get(0)).map_err(|e|e.to_string())?;
            if exists {
                passed.insert(q.id.clone());
            }
        }
        Ok(passed)
    }
    pub fn save_quiz(
        &mut self,
        course: &str,
        unit: &Unit,
        questions: &[crate::curriculum::Question],
        answers: &std::collections::HashMap<String, String>,
    ) -> Result<TestReport, String> {
        let passed = self.quiz_passed(course, unit, questions)?;
        let mut report = crate::curriculum::grade_quiz(questions, answers);
        for (q, case) in questions.iter().zip(&mut report.cases) {
            if passed.contains(&q.id) {
                case.passed = true;
                case.state = "previously_passed".into();
            }
        }
        report.passed = !report.cases.is_empty() && report.cases.iter().all(|c| c.passed);
        if report.cases.is_empty() {
            return Err("퀴즈 문항이 없습니다.".into());
        }
        let source = serde_json::to_string(answers).map_err(|e| e.to_string())?;
        let report_json = serde_json::to_string(&report).map_err(|e| e.to_string())?;
        let tx = self.0.transaction().map_err(|e| e.to_string())?;
        tx.execute(
            "INSERT INTO attempts(course,unit,revision,code,report) VALUES (?1,?2,?3,?4,?5)",
            params![course, unit.id, unit.revision, source, report_json],
        )
        .map_err(|e| e.to_string())?;
        for (q, case) in questions.iter().zip(&report.cases) {
            if case.passed {
                tx.execute("INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",params![course,format!("{}/question/{}",unit.id,q.id),unit.revision]).map_err(|e|e.to_string())?;
            }
        }
        if report.passed {
            tx.execute("INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",params![course,unit.id,unit.revision]).map_err(|e|e.to_string())?;
        }
        tx.commit().map_err(|e| e.to_string())?;
        Ok(report)
    }
    pub fn open(path: &Path) -> Result<Self, String> {
        let db = Connection::open(path).map_err(|e| e.to_string())?;
        db.execute_batch("CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, course TEXT NOT NULL, unit TEXT NOT NULL, revision INTEGER NOT NULL, code TEXT NOT NULL, report TEXT NOT NULL); CREATE TABLE IF NOT EXISTS completed (course TEXT NOT NULL, unit TEXT NOT NULL, revision INTEGER NOT NULL, PRIMARY KEY(course,unit));").map_err(|e| e.to_string())?;
        Ok(Self(db))
    }
    pub fn user_store() -> Result<Self, String> {
        Self::open(&crate::data_dir()?.join("learning.sqlite3"))
    }
    pub fn save(
        &mut self,
        course: &str,
        unit: &Unit,
        code: &str,
        report: &TestReport,
    ) -> Result<(), String> {
        if report.cases.is_empty() || report.passed != report.cases.iter().all(|case| case.passed) {
            return Err("검사 결과를 확인해 주세요.".into());
        }
        let report_json = serde_json::to_string(report).map_err(|e| e.to_string())?;
        let tx = self.0.transaction().map_err(|e| e.to_string())?;
        tx.execute(
            "INSERT INTO attempts(course,unit,revision,code,report) VALUES (?1,?2,?3,?4,?5)",
            params![course, unit.id, unit.revision, code, report_json],
        )
        .map_err(|e| e.to_string())?;
        if report.passed {
            tx.execute("INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",params![course,unit.id,unit.revision]).map_err(|e|e.to_string())?;
        }
        tx.commit().map_err(|e| e.to_string())
    }
    /// Record a mission the student finished by reading it to the end (slide decks).
    pub fn mark_viewed(&mut self, course: &str, unit: &Unit) -> Result<(), String> {
        self.0
            .execute(
                "INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",
                params![course, unit.id, unit.revision],
            )
            .map(|_| ())
            .map_err(|e| e.to_string())
    }
    /// Forget every attempt and completion for one course so the student starts over.
    pub fn reset(&mut self, course: &str) -> Result<(), String> {
        let tx = self.0.transaction().map_err(|e| e.to_string())?;
        tx.execute("DELETE FROM attempts WHERE course=?1", [course])
            .map_err(|e| e.to_string())?;
        tx.execute("DELETE FROM completed WHERE course=?1", [course])
            .map_err(|e| e.to_string())?;
        tx.commit().map_err(|e| e.to_string())
    }
    pub fn completed(&self, course: &crate::Course) -> Result<HashSet<String>, String> {
        let items = self.completed_items(course)?;
        Ok(course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .filter(|unit| {
                if unit.activities.is_empty() {
                    items.contains(&unit.id)
                } else {
                    unit.activities
                        .iter()
                        .all(|a| items.contains(&a.progress_unit(unit).id))
                }
            })
            .map(|u| u.id.clone())
            .collect())
    }
    /// Whether this unit (a coding problem, or a mission's progress unit) has been passed at
    /// its current revision: what the 제출 button turns into 다시 제출 on.
    pub fn unit_completed(&self, course: &str, unit: &Unit) -> Result<bool, String> {
        let revision: Option<i64> = self
            .0
            .query_row(
                "SELECT revision FROM completed WHERE course=?1 AND unit=?2",
                params![course, unit.id],
                |r| r.get(0),
            )
            .optional()
            .map_err(|e| e.to_string())?;
        Ok(revision == Some(unit.revision))
    }
    pub fn completed_items(&self, course: &crate::Course) -> Result<HashSet<String>, String> {
        let mut statement = self
            .0
            .prepare("SELECT unit,revision FROM completed WHERE course=?1")
            .map_err(|e| e.to_string())?;
        let rows = statement
            .query_map([&course.id], |r| {
                Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?))
            })
            .map_err(|e| e.to_string())?;
        let mut units = HashSet::new();
        for row in rows {
            let (id, revision) = row.map_err(|e| e.to_string())?;
            if course.chapters.iter().flat_map(|c| &c.units).any(|u| {
                (u.activities.is_empty() && u.id == id && u.revision == revision)
                    || u.activities.iter().any(|a| {
                        let progress = a.progress_unit(u);
                        progress.id == id && progress.revision == revision
                    })
            }) {
                units.insert(id);
            }
        }
        Ok(units)
    }
}
