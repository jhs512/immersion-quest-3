//! Durable local learning history and a retryable GitHub outbox.
use crate::{
    github_player::{Github, GithubUser},
    issue_progress::{self, EventKind, LearningEvent, ProgressKey},
};
use rusqlite::{params, Connection, TransactionBehavior};
use std::{
    collections::{HashMap, HashSet},
    path::{Path, PathBuf},
    sync::{Mutex, OnceLock},
    time::Duration,
};

#[derive(Clone)]
pub struct ProgressStore {
    path: PathBuf,
}
#[derive(Clone)]
struct Pending {
    repository: String,
    title: String,
    event: LearningEvent,
}
impl ProgressStore {
    pub fn new(path: &Path) -> Self {
        Self { path: path.into() }
    }
    pub fn installed() -> Result<Self, String> {
        Ok(Self::new(
            &crate::data_dir()?.join("progress-events.sqlite3"),
        ))
    }
    fn connection(&self) -> Result<Connection, String> {
        let db = Connection::open(&self.path).map_err(|e| e.to_string())?;
        db.busy_timeout(Duration::from_secs(5))
            .map_err(|e| e.to_string())?;
        db.execute_batch("CREATE TABLE IF NOT EXISTS progress_events (
          sequence INTEGER PRIMARY KEY AUTOINCREMENT, repository TEXT NOT NULL,
          event_id TEXT NOT NULL, user_id TEXT NOT NULL, course_id TEXT NOT NULL,
          lesson_id TEXT NOT NULL, title TEXT NOT NULL, document TEXT NOT NULL,
          pending INTEGER NOT NULL, UNIQUE(repository,user_id,event_id));
          CREATE INDEX IF NOT EXISTS progress_pending ON progress_events(user_id,pending,sequence);
          CREATE INDEX IF NOT EXISTS progress_scope ON progress_events(repository,user_id,course_id,lesson_id,sequence);").map_err(|e|e.to_string())?;
        Ok(db)
    }
    fn insert(
        db: &Connection,
        repo: &str,
        title: &str,
        event: &LearningEvent,
        pending: bool,
    ) -> Result<(), String> {
        db.execute("INSERT OR IGNORE INTO progress_events(repository,event_id,user_id,course_id,lesson_id,title,document,pending)
          VALUES(?1,?2,?3,?4,?5,?6,?7,?8)",params![repo,event.id,event.key.user_id.to_string(),event.key.course_id,event.key.lesson_id,title,serde_json::to_string(event).map_err(|e|e.to_string())?,pending]).map_err(|e|e.to_string())?;
        Ok(())
    }
    fn read(db: &Connection, repo: &str, key: &ProgressKey) -> Result<Vec<LearningEvent>, String> {
        let mut query=db.prepare("SELECT document FROM progress_events WHERE repository=?1 AND user_id=?2 AND course_id=?3 AND lesson_id=?4 ORDER BY sequence").map_err(|e|e.to_string())?;
        let rows = query
            .query_map(
                params![repo, key.user_id.to_string(), key.course_id, key.lesson_id],
                |row| row.get::<_, String>(0),
            )
            .map_err(|e| e.to_string())?;
        let events = rows
            .map(|row| {
                serde_json::from_str(&row.map_err(|e| e.to_string())?).map_err(|e| e.to_string())
            })
            .collect::<Result<Vec<_>, _>>()?;
        Ok(issue_progress::merge(events, key))
    }
    pub fn events(&self, repo: &str, key: &ProgressKey) -> Result<Vec<LearningEvent>, String> {
        Self::read(&self.connection()?, repo, key)
    }
    pub fn course_events(
        &self,
        repo: &str,
        user_id: u64,
        course_id: &str,
    ) -> Result<HashMap<String, Vec<LearningEvent>>, String> {
        let db = self.connection()?;
        let mut query=db.prepare("SELECT document FROM progress_events WHERE repository=?1 AND user_id=?2 AND course_id=?3 ORDER BY sequence").map_err(|e|e.to_string())?;
        let rows = query
            .query_map(params![repo, user_id.to_string(), course_id], |row| {
                row.get::<_, String>(0)
            })
            .map_err(|e| e.to_string())?;
        let mut result: HashMap<String, Vec<LearningEvent>> = HashMap::new();
        for row in rows {
            let event: LearningEvent = serde_json::from_str(&row.map_err(|e| e.to_string())?)
                .map_err(|e| e.to_string())?;
            result
                .entry(event.key.lesson_id.clone())
                .or_default()
                .push(event);
        }
        for (id, events) in &mut result {
            *events = issue_progress::merge(
                std::mem::take(events),
                &ProgressKey {
                    user_id,
                    course_id: course_id.into(),
                    lesson_id: id.clone(),
                },
            );
        }
        Ok(result)
    }
    pub fn cache(&self, repo: &str, events: &[LearningEvent]) -> Result<(), String> {
        let mut db = self.connection()?;
        let tx = db.transaction().map_err(|e| e.to_string())?;
        for event in events {
            Self::insert(&tx, repo, "", event, false)?;
        }
        tx.commit().map_err(|e| e.to_string())
    }
    /// The attempt and any lesson completion are committed together before navigation.
    pub fn record(
        &self,
        repo: &str,
        user: &GithubUser,
        title: &str,
        event: &LearningEvent,
        required: &[String],
    ) -> Result<Vec<LearningEvent>, String> {
        if event.key.user_id != user.id || !crate::repository_course::valid_repository(repo) {
            return Err("진도를 보관할 계정과 코스를 확인하세요.".into());
        }
        let mut db = self.connection()?;
        let tx = db
            .transaction_with_behavior(TransactionBehavior::Immediate)
            .map_err(|e| e.to_string())?;
        Self::insert(&tx, repo, title, event, true)?;
        let mut latest = Self::read(&tx, repo, &event.key)?;
        if event.kind == EventKind::Attempt
            && event.passed
            && !required.is_empty()
            && required
                .iter()
                .all(|id| issue_progress::learned_tasks(&latest, &event.revision).contains(id))
            && !latest.iter().any(|e| {
                e.kind == EventKind::Completed
                    && e.round == event.round
                    && e.revision == event.revision
                    && e.mode == event.mode
            })
        {
            let mut done = LearningEvent::new(
                event.key.clone(),
                &event.revision,
                event.mode,
                &event.round,
                EventKind::Completed,
            );
            done.required = required.into();
            Self::insert(&tx, repo, title, &done, true)?;
            latest.push(done);
        }
        tx.commit().map_err(|e| e.to_string())?;
        Ok(issue_progress::merge(latest, &event.key))
    }
    #[cfg(test)]
    fn next(&self, user_id: u64) -> Result<Option<Pending>, String> {
        self.next_except(user_id, &HashSet::new())
    }
    fn next_except(
        &self,
        user_id: u64,
        blocked: &HashSet<String>,
    ) -> Result<Option<Pending>, String> {
        let db = self.connection()?;
        let mut query=db.prepare("SELECT repository,title,document FROM progress_events WHERE user_id=?1 AND pending=1 ORDER BY sequence").map_err(|e|e.to_string())?;
        let rows = query
            .query_map([user_id.to_string()], |r| {
                Ok((
                    r.get::<_, String>(0)?,
                    r.get::<_, String>(1)?,
                    r.get::<_, String>(2)?,
                ))
            })
            .map_err(|e| e.to_string())?;
        for row in rows {
            let (repository, title, document) = row.map_err(|e| e.to_string())?;
            if !blocked.contains(&repository) {
                return Ok(Some(Pending {
                    repository,
                    title,
                    event: serde_json::from_str(&document).map_err(|e| e.to_string())?,
                }));
            }
        }
        Ok(None)
    }
    pub fn pending_count(&self, user_id: u64) -> Result<usize, String> {
        self.connection()?
            .query_row(
                "SELECT COUNT(*) FROM progress_events WHERE user_id=?1 AND pending=1",
                [user_id.to_string()],
                |row| row.get(0),
            )
            .map_err(|e| e.to_string())
    }
    fn send_pending(&self, github: &Github, user: &GithubUser) -> Result<(), String> {
        // Separate app processes share the queue but never upload it concurrently.
        // Recording new clears uses only SQLite and never waits for this lock.
        let lock = std::fs::OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(self.path.with_extension(format!("sync-{}.lock", user.id)))
            .map_err(|e| e.to_string())?;
        lock.lock().map_err(|e| e.to_string())?;
        self.flush(
            user.id,
            |item| {
                github
                    .append(&item.repository, user, &item.title, &item.event)
                    .map(|(_, events)| events)
            },
            std::thread::sleep,
        )
    }
    fn acknowledge(&self, item: &Pending, remote: &[LearningEvent]) -> Result<(), String> {
        // A response lost after POST is retried using the same immutable event id.
        if !remote.iter().any(|event| event == &item.event) {
            return Err("저장한 학습 기록을 확인하지 못했어요.".into());
        }
        let mut db = self.connection()?;
        let tx = db.transaction().map_err(|e| e.to_string())?;
        for event in remote.iter().filter(|e| e.key == item.event.key) {
            Self::insert(&tx, &item.repository, "", event, false)?;
        }
        tx.execute("UPDATE progress_events SET pending=0 WHERE repository=?1 AND user_id=?2 AND event_id=?3",params![item.repository,item.event.key.user_id.to_string(),item.event.id]).map_err(|e|e.to_string())?;
        tx.commit().map_err(|e| e.to_string())
    }
    fn flush(
        &self,
        user_id: u64,
        mut send: impl FnMut(&Pending) -> Result<Vec<LearningEvent>, String>,
        mut sleep: impl FnMut(Duration),
    ) -> Result<(), String> {
        let mut blocked = HashSet::new();
        let mut error = None;
        while let Some(item) = self.next_except(user_id, &blocked)? {
            let mut result = Err(String::new());
            for attempt in 0..3 {
                result = send(&item).and_then(|remote| self.acknowledge(&item, &remote));
                if result.is_ok() {
                    break;
                }
                if attempt < 2 {
                    sleep(Duration::from_secs(if attempt == 0 { 1 } else { 3 }));
                }
            }
            // Defer the failing repository, allowing other courses to upload.
            if let Err(problem) = result {
                blocked.insert(item.repository);
                error = Some(problem);
            }
        }
        match error {
            Some(error) => Err(error),
            None => Ok(()),
        }
    }
}

#[derive(Default)]
struct SyncState {
    running: bool,
    requested: u64,
}
fn workers() -> &'static Mutex<HashMap<(PathBuf, u64), SyncState>> {
    static WORKERS: OnceLock<Mutex<HashMap<(PathBuf, u64), SyncState>>> = OnceLock::new();
    WORKERS.get_or_init(Mutex::default)
}
pub fn is_syncing(user_id: u64) -> Result<bool, String> {
    let store = ProgressStore::installed()?;
    Ok(workers()
        .lock()
        .unwrap_or_else(|e| e.into_inner())
        .get(&(store.path, user_id))
        .is_some_and(|state| state.running))
}
/// Process-owned, so leaving a problem/lesson cannot cancel an upload.
pub fn synchronize(github: Github, user: GithubUser) -> Result<(), String> {
    let store = ProgressStore::installed()?;
    let key = (store.path.clone(), user.id);
    {
        let mut workers = workers().lock().unwrap_or_else(|e| e.into_inner());
        let state = workers.entry(key.clone()).or_default();
        state.requested += 1;
        if state.running {
            return Ok(());
        }
        state.running = true;
    }
    let cleanup = key.clone();
    if let Err(error) = std::thread::Builder::new()
        .name("progress-sync".into())
        .spawn(move || loop {
            let generation = workers().lock().unwrap_or_else(|e| e.into_inner())[&key].requested;
            if let Err(error) = store.send_pending(&github, &user) {
                eprintln!("Progress upload deferred: {error}");
            }
            let mut workers = workers().lock().unwrap_or_else(|e| e.into_inner());
            let state = workers.get_mut(&key).unwrap();
            if state.requested == generation {
                state.running = false;
                break;
            }
        })
    {
        workers()
            .lock()
            .unwrap_or_else(|e| e.into_inner())
            .get_mut(&cleanup)
            .unwrap()
            .running = false;
        return Err(error.to_string());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn setup() -> (tempfile::TempDir, ProgressStore, GithubUser) {
        let root = tempfile::tempdir().unwrap();
        let store = ProgressStore::new(&root.path().join("progress.sqlite3"));
        (
            root,
            store,
            GithubUser {
                id: 7,
                login: "learner".into(),
            },
        )
    }
    fn attempt(user_id: u64, task: &str) -> LearningEvent {
        let mut event = LearningEvent::new(
            ProgressKey {
                user_id,
                course_id: "course".into(),
                lesson_id: "lesson".into(),
            },
            "revision",
            crate::issue_progress::StudyMode::Full,
            "round",
            EventKind::Attempt,
        );
        event.task_id = Some(task.into());
        event.passed = true;
        event
    }
    #[test]
    fn exhausted_retries_survive_restart_and_are_sent_with_the_next_clear() {
        let (root, store, user) = setup();
        let first = attempt(user.id, "a");
        let required = vec!["a".into(), "b".into()];
        store
            .record("owner/course", &user, "Lesson", &first, &required)
            .unwrap();
        let mut attempts = 0;
        let mut delays = vec![];
        assert!(store
            .flush(
                user.id,
                |_| {
                    attempts += 1;
                    Err("offline".into())
                },
                |delay| delays.push(delay)
            )
            .is_err());
        assert_eq!(attempts, 3);
        assert_eq!(delays, [Duration::from_secs(1), Duration::from_secs(3)]);
        drop(store);
        let reopened = ProgressStore::new(&root.path().join("progress.sqlite3"));
        let second = attempt(user.id, "b");
        let latest = reopened
            .record("owner/course", &user, "Lesson", &second, &required)
            .unwrap();
        assert_eq!(issue_progress::learned_tasks(&latest, "revision").len(), 2);
        assert_eq!(
            latest
                .iter()
                .filter(|e| e.kind == EventKind::Completed)
                .count(),
            1
        );
        let mut sent = vec![];
        reopened
            .flush(
                user.id,
                |item| {
                    sent.push(item.event.clone());
                    Ok(vec![item.event.clone()])
                },
                |_| {},
            )
            .unwrap();
        assert_eq!(
            sent.iter()
                .map(|e| e.id.as_str())
                .take(2)
                .collect::<Vec<_>>(),
            [first.id.as_str(), second.id.as_str()]
        );
        assert_eq!(sent.len(), 3);
        assert!(reopened.next(user.id).unwrap().is_none());
        assert_eq!(
            reopened.events("owner/course", &first.key).unwrap().len(),
            3,
            "history remains after upload"
        );
    }
    #[test]
    fn lost_post_response_retries_the_same_id_and_does_not_duplicate_completion() {
        let (_root, store, user) = setup();
        let event = attempt(user.id, "a");
        let required = vec!["a".into()];
        store
            .record("owner/course", &user, "Lesson", &event, &required)
            .unwrap();
        store
            .record("owner/course", &user, "Lesson", &event, &required)
            .unwrap();
        let mut remote = HashMap::new();
        let mut lost = true;
        store
            .flush(
                user.id,
                |item| {
                    remote.insert(item.event.id.clone(), item.event.clone());
                    if lost {
                        lost = false;
                        return Err("response lost".into());
                    }
                    Ok(remote.values().cloned().collect())
                },
                |_| {},
            )
            .unwrap();
        assert_eq!(remote.len(), 2);
        assert_eq!(
            remote
                .values()
                .filter(|e| e.kind == EventKind::Completed)
                .count(),
            1
        );
    }
    #[test]
    fn queues_and_local_progress_are_isolated_by_account_course_and_repository() {
        let (_root, store, user) = setup();
        let first = attempt(7, "a");
        let second = attempt(8, "b");
        let other = GithubUser {
            id: 8,
            login: "other".into(),
        };
        store
            .record("owner/course", &user, "Lesson", &first, &[])
            .unwrap();
        store
            .record("owner/other", &other, "Lesson", &second, &[])
            .unwrap();
        assert!(store
            .record("owner/course", &user, "Lesson", &second, &[])
            .is_err());
        store
            .flush(
                7,
                |item| {
                    assert_eq!(item.event.key.user_id, 7);
                    Ok(vec![item.event.clone()])
                },
                |_| {},
            )
            .unwrap();
        assert!(store.next(8).unwrap().is_some());
        assert!(store
            .events("owner/course", &second.key)
            .unwrap()
            .is_empty());
        assert!(store
            .course_events("owner/other", 7, "course")
            .unwrap()
            .is_empty());
    }
    #[test]
    fn a_slow_upload_does_not_lock_recording_or_remove_a_new_clear() {
        let (_root, store, user) = setup();
        let first = attempt(7, "a");
        store
            .record("owner/course", &user, "Lesson", &first, &[])
            .unwrap();
        let (started_tx, started_rx) = std::sync::mpsc::channel();
        let (release_tx, release_rx) = std::sync::mpsc::channel();
        let worker = store.clone();
        let thread = std::thread::spawn(move || {
            let mut first = true;
            worker
                .flush(
                    7,
                    |item| {
                        if first {
                            first = false;
                            started_tx.send(()).unwrap();
                            release_rx.recv().unwrap();
                        }
                        Ok(vec![item.event.clone()])
                    },
                    |_| {},
                )
                .unwrap();
        });
        started_rx.recv_timeout(Duration::from_secs(5)).unwrap();
        let second = attempt(7, "b");
        let latest = store
            .record("owner/course", &user, "Lesson", &second, &[])
            .unwrap();
        assert_eq!(issue_progress::learned_tasks(&latest, "revision").len(), 2);
        release_tx.send(()).unwrap();
        thread.join().unwrap();
        assert!(store.next(7).unwrap().is_none());
    }
    #[test]
    fn an_unavailable_repository_does_not_block_other_courses() {
        let (_root, store, user) = setup();
        let first = attempt(7, "a");
        let second = attempt(7, "b");
        store
            .record("owner/unavailable", &user, "Lesson", &first, &[])
            .unwrap();
        store
            .record("owner/working", &user, "Lesson", &second, &[])
            .unwrap();
        let mut uploaded = vec![];
        assert!(store
            .flush(
                7,
                |item| {
                    if item.repository == "owner/unavailable" {
                        Err("access denied".into())
                    } else {
                        uploaded.push(item.event.id.clone());
                        Ok(vec![item.event.clone()])
                    }
                },
                |_| {}
            )
            .is_err());
        assert_eq!(uploaded, [second.id]);
        assert_eq!(store.pending_count(7).unwrap(), 1);
    }
    #[test]
    fn an_unconfirmed_event_is_not_removed_from_the_outbox() {
        let (_root, store, user) = setup();
        let event = attempt(7, "a");
        store
            .record("owner/course", &user, "Lesson", &event, &[])
            .unwrap();
        assert!(store.flush(7, |_| Ok(vec![]), |_| {}).is_err());
        assert_eq!(store.next(7).unwrap().unwrap().event.id, event.id);
    }
}
