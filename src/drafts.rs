use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Clone, Default, Deserialize, Serialize)]
pub struct Draft {
    pub code: String,
    pub answers: HashMap<String, String>,
}
/// A stable answer belongs to the account/course/lesson/mode/step, not a launch's round.
pub fn repository_scope(key:&crate::issue_progress::ProgressKey,mode:crate::issue_progress::StudyMode,task_id:&str)->String {
    format!("repo-v2:{}",serde_json::to_string(&(key.user_id,&key.course_id,&key.lesson_id,mode,task_id)).expect("draft scope"))
}
fn connection() -> Result<Connection, String> {
    let connection =
        Connection::open(crate::data_dir()?.join("drafts.sqlite3")).map_err(|e| e.to_string())?;
    connection
        .execute_batch(
            "CREATE TABLE IF NOT EXISTS drafts (scope TEXT PRIMARY KEY, document TEXT NOT NULL);
             CREATE TABLE IF NOT EXISTS draft_backups (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, course_id TEXT NOT NULL, snapshot TEXT NOT NULL, scope TEXT NOT NULL, document TEXT NOT NULL, UNIQUE(user_id,course_id,snapshot,scope))",
        )
        .map_err(|e| e.to_string())?;
    Ok(connection)
}
pub fn load(scope: &str) -> Result<Option<Draft>, String> {
    let document: Option<String> = connection()?
        .query_row("SELECT document FROM drafts WHERE scope=?1", [scope], |r| {
            r.get(0)
        })
        .optional()
        .map_err(|e| e.to_string())?;
    document
        .map(|d| serde_json::from_str(&d).map_err(|e| e.to_string()))
        .transpose()
}
/// Drop saved code and quiz answers for one course. Scopes are "local:<course>:…" and "quiz:<course>:…".
pub fn clear_course(course: &str) -> Result<(), String> {
    connection()?
        .execute(
            "DELETE FROM drafts WHERE scope LIKE ?1 OR scope LIKE ?2",
            params![format!("local:{course}:%"), format!("quiz:{course}:%")],
        )
        .map_err(|e| e.to_string())?;
    Ok(())
}
pub fn save(scope: &str, code: &str, answers: &HashMap<String, String>) -> Result<(), String> {
    let document = serde_json::to_string(&Draft {
        code: code.into(),
        answers: answers.clone(),
    })
    .map_err(|e| e.to_string())?;
    connection()?.execute("INSERT INTO drafts(scope,document) VALUES (?1,?2) ON CONFLICT(scope) DO UPDATE SET document=excluded.document",params![scope,document]).map_err(|e|e.to_string())?;
    Ok(())
}

#[derive(Clone)]
pub struct RepositoryBackup { pub step_id:String, pub snapshot:String, pub draft:Draft }
fn repository_parts(scope:&str)->Option<(u64,String,String,crate::issue_progress::StudyMode,String)> {
    serde_json::from_str(scope.strip_prefix("repo-v2:")?).ok()
}
/// Backup before switching content; never erase or overwrite the student's live answer.
pub fn backup_repository(user:u64,course:&str,snapshot:&str)->Result<(),String> {
    let snapshot=format!("{snapshot}:{}",crate::issue_progress::new_id());
    let mut connection=connection()?;
    let transaction=connection.transaction().map_err(|e|e.to_string())?;
    {
        let mut query=transaction.prepare("SELECT scope,document FROM drafts").map_err(|e|e.to_string())?;
        let rows=query.query_map([],|row|Ok((row.get::<_,String>(0)?,row.get::<_,String>(1)?))).map_err(|e|e.to_string())?;
        for row in rows {
            let (scope,document)=row.map_err(|e|e.to_string())?;
            if repository_parts(&scope).is_some_and(|parts|parts.0==user&&parts.1==course) {
                transaction.execute("INSERT OR IGNORE INTO draft_backups(user_id,course_id,snapshot,scope,document) VALUES (?1,?2,?3,?4,?5)",params![user,course,snapshot,scope,document]).map_err(|e|e.to_string())?;
            }
        }
    }
    transaction.commit().map_err(|e|e.to_string())
}
pub fn repository_backups(user:u64,course:&str)->Result<Vec<RepositoryBackup>,String> {
    let connection=connection()?;
    let mut query=connection.prepare("SELECT scope,snapshot,document FROM draft_backups WHERE user_id=?1 AND course_id=?2 ORDER BY id DESC").map_err(|e|e.to_string())?;
    let rows=query.query_map(params![user,course],|row|Ok((row.get::<_,String>(0)?,row.get::<_,String>(1)?,row.get::<_,String>(2)?))).map_err(|e|e.to_string())?;
    let mut backups=vec![];
    for row in rows {
        let (scope,snapshot,document)=row.map_err(|e|e.to_string())?;
        let parts=repository_parts(&scope).ok_or("백업 답안의 범위를 확인하세요.")?;
        let draft=serde_json::from_str(&document).map_err(|e|e.to_string())?;
        backups.push(RepositoryBackup{step_id:parts.4,snapshot,draft});
    }
    Ok(backups)
}
