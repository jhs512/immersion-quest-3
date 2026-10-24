//! Write-ahead journal for locally earned progress.
//!
//! A grading result is shown at once from memory (the catalog overlay) and committed to SQLite by
//! a background recorder. SQLite can be busy for longer than its 5 second `busy_timeout` (another
//! app process, the exit helper, a backup or antivirus scan holding the file). The recorder used to
//! try once and only log the failure, so the result lived in RAM until the app closed.
//!
//! Now the recorder first writes the event to its own small file next to the database
//! (`progress-events.journal/<time>-<pid>-<n>.json`, written to a temporary name, fsynced and
//! renamed into place) and deletes it only after SQLite committed it. Until then it is replayed,
//! in the order it was earned, by:
//! - the recorder itself, retrying with backoff for `RECORD_RETRY_WINDOW` (a background thread, so
//!   the UI never waits);
//! - every later local record and every local read (`events`, `course_events`), without waiting
//!   for the lock, so a read never becomes slower than before;
//! - the GUI-less exit helper, before it needs GitHub, and the next launch.
//! Local reads also add entries that are still in the journal, so a reopened store shows them
//! even before they reach SQLite.
//!
//! Replay goes through the same `record_in` transaction as a normal save. Event ids are immutable
//! and inserts are `INSERT OR IGNORE`; the completion id is derived from account, course, lesson,
//! revision, mode and round. Replaying an entry twice (two threads, a crash between commit and
//! delete) therefore stores it once, and account/course/repository/revision/round/mode boundaries
//! are exactly those of the original save.
//!
//! What this cannot promise: if the journal file itself cannot be written (disk full, data folder
//! removed or read-only, permissions) *and* SQLite stays unavailable for the whole retry window,
//! the event exists only in this process's memory. The recorder then returns an error that says
//! so and logs it; the catalog still shows it until the app closes, and it is lost after that.
//! A journal entry that can never be stored (unreadable JSON, or an account/course mismatch) is
//! renamed to `.rejected` and kept for diagnosis instead of blocking later entries forever.
use super::*;
use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicU64, Ordering};

/// How long a recorder thread keeps retrying a busy SQLite before leaving the entry to the next
/// replay point. The entry is already on disk, so giving up here loses nothing.
pub const RECORD_RETRY_WINDOW: Duration = Duration::from_secs(120);

#[derive(Serialize, Deserialize)]
struct Entry {
    repository: String,
    user: GithubUser,
    title: String,
    event: LearningEvent,
    required: Vec<String>,
}

/// One replay at a time per database in this process; readers skip instead of waiting for it.
fn replaying(path: &Path) -> std::sync::Arc<Mutex<()>> {
    static REPLAY: OnceLock<Mutex<HashMap<PathBuf, std::sync::Arc<Mutex<()>>>>> = OnceLock::new();
    REPLAY.get_or_init(Mutex::default).lock().unwrap_or_else(|e| e.into_inner()).entry(path.into()).or_default().clone()
}

impl ProgressStore {
    fn journal_dir(&self) -> PathBuf {
        self.path.with_extension("journal")
    }
    /// Durable before SQLite is touched: temp file, fsync, rename (and fsync the folder on unix).
    fn journal_write(&self, entry: &Entry) -> Result<PathBuf, String> {
        use std::io::Write;
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let dir = self.journal_dir();
        std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0);
        let name = format!("{nanos:024}-{:010}-{:010}", std::process::id(), COUNTER.fetch_add(1, Ordering::SeqCst));
        let pending = dir.join(format!("{name}.tmp"));
        let path = dir.join(format!("{name}.json"));
        let mut file = std::fs::File::create(&pending).map_err(|e| e.to_string())?;
        file.write_all(&serde_json::to_vec(entry).map_err(|e| e.to_string())?)
            .and_then(|_| file.sync_all())
            .map_err(|e| e.to_string())?;
        drop(file);
        std::fs::rename(&pending, &path).map_err(|e| e.to_string())?;
        #[cfg(unix)]
        if let Ok(folder) = std::fs::File::open(&dir) {
            let _ = folder.sync_all();
        }
        Ok(path)
    }
    /// Entries not yet in SQLite, oldest first. Unreadable files are set aside.
    fn journal_entries(&self) -> Vec<(PathBuf, Entry)> {
        let Ok(items) = std::fs::read_dir(self.journal_dir()) else { return vec![] };
        let mut paths: Vec<PathBuf> = items
            .filter_map(|item| item.ok().map(|item| item.path()))
            .filter(|path| path.extension().is_some_and(|ext| ext == "json"))
            .collect();
        paths.sort();
        paths
            .into_iter()
            .filter_map(|path| {
                let raw = std::fs::read(&path).ok()?;
                match serde_json::from_slice::<Entry>(&raw) {
                    Ok(entry) => Some((path, entry)),
                    Err(error) => {
                        eprintln!("Unreadable progress journal entry {}: {error}", path.display());
                        let _ = std::fs::rename(&path, path.with_extension("rejected"));
                        None
                    }
                }
            })
            .collect()
    }
    /// Number of entries that have not reached SQLite yet.
    pub fn journal_len(&self) -> usize {
        std::fs::read_dir(self.journal_dir())
            .map(|items| {
                items
                    .filter_map(Result::ok)
                    .filter(|item| item.path().extension().is_some_and(|ext| ext == "json"))
                    .count()
            })
            .unwrap_or(0)
    }
    /// Commit journaled entries to SQLite in the order they were earned, deleting each one after
    /// its commit. Stops at the first storage failure so later entries never overtake earlier
    /// ones. Returns how many entries were stored.
    fn replay_with(&self, busy: Duration) -> Result<usize, String> {
        let entries = self.journal_entries();
        if entries.is_empty() {
            return Ok(0);
        }
        let mut db = self.connection_waiting(busy)?;
        let mut stored = 0;
        for (path, entry) in entries {
            if Self::validate(&entry.repository, &entry.user, &entry.event).is_err() {
                eprintln!("Progress journal entry {} does not match its account or course", path.display());
                let _ = std::fs::rename(&path, path.with_extension("rejected"));
                continue;
            }
            Self::record_in(&mut db, &entry.repository, &entry.user, &entry.title, &entry.event, &entry.required)?;
            // Already committed; if this delete fails the next replay stores it again as a no-op.
            match std::fs::remove_file(&path) {
                Ok(()) => {}
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
                Err(error) => eprintln!("Stored progress journal entry could not be removed: {error}"),
            }
            stored += 1;
        }
        Ok(stored)
    }
    /// Store journaled entries, waiting for SQLite like a normal save. Used by the exit helper.
    pub fn replay_journal(&self) -> Result<usize, String> {
        let lock = replaying(&self.path);
        let _replay = lock.lock().unwrap_or_else(|e| e.into_inner());
        self.replay_with(Duration::from_secs(5))
    }
    /// A read path's chance to store journaled entries. It neither waits for another replay nor
    /// for a busy database, so it never slows the read down; failures are left for later.
    pub(super) fn replay_journal_without_waiting(&self) {
        let lock = replaying(&self.path);
        let Ok(_replay) = lock.try_lock() else { return };
        let _ = self.replay_with(Duration::ZERO);
    }
    /// Add entries still in the journal to a course's local history, exactly as `record` would.
    pub(super) fn add_journaled(&self, repo: &str, user_id: u64, course_id: &str, lessons: &mut HashMap<String, Vec<LearningEvent>>) {
        for (_, entry) in self.journal_entries() {
            let key = &entry.event.key;
            if entry.repository != repo || entry.user.id != user_id || key.user_id != user_id || key.course_id != course_id {
                continue;
            }
            let current = lessons.remove(&key.lesson_id).unwrap_or_default();
            lessons.insert(key.lesson_id.clone(), apply_result(current, &entry.event, &entry.required));
        }
    }
    /// The recorder's save: journal first, then SQLite, retrying a busy database with backoff for
    /// `give_up_after`. Runs on a background thread; never call it from the UI thread.
    ///
    /// `Ok` means the event is committed to SQLite. `Err` after the window means it is still in the
    /// journal and will be stored at the next replay point - or, if the journal could not be
    /// written either, that it exists only in memory (the message says which).
    pub fn record_durably(
        &self,
        repo: &str,
        user: &GithubUser,
        title: &str,
        event: &LearningEvent,
        required: &[String],
        give_up_after: Duration,
    ) -> Result<Vec<LearningEvent>, String> {
        Self::validate(repo, user, event)?;
        let entry = Entry { repository: repo.into(), user: user.clone(), title: title.into(), event: event.clone(), required: required.into() };
        let journaled = match self.journal_write(&entry) {
            Ok(path) => Some(path),
            Err(error) => {
                eprintln!("Progress journal unavailable, saving to SQLite only: {error}");
                None
            }
        };
        let deadline = std::time::Instant::now() + give_up_after;
        let mut pause = Duration::from_millis(250);
        loop {
            let attempt = match &journaled {
                // Replaying stores every older journaled event first, then this one.
                Some(path) => {
                    let result = {
                        let lock = replaying(&self.path);
                        let _replay = lock.lock().unwrap_or_else(|e| e.into_inner());
                        self.replay_with(Duration::from_secs(5))
                    };
                    match result {
                        Ok(_) if !path.exists() => self.events(repo, &event.key),
                        Ok(_) => Err("journal entry was not stored".into()),
                        Err(error) => Err(error),
                    }
                }
                None => self.record(repo, user, title, event, required),
            };
            let error = match attempt {
                Ok(latest) => return Ok(latest),
                Err(error) => error,
            };
            if std::time::Instant::now() + pause > deadline {
                return Err(match journaled {
                    Some(_) => format!("진도를 아직 저장하지 못했어요. 이 기기의 진도 기록 대기 파일에 남겨 두었고 다음 저장이나 실행 때 다시 저장해요. ({error})"),
                    None => format!("진도를 저장하지 못했어요. 저장 공간을 확인하세요. 앱을 닫으면 이번 기록은 사라져요. ({error})"),
                });
            }
            eprintln!("Progress save retrying in {pause:?}: {error}");
            std::thread::sleep(pause);
            pause = (pause * 2).min(Duration::from_secs(5));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn replaying_twice_and_reading_unreplayed_entries_keep_one_completion() {
        let (root, store, user) = super::super::tests::setup();
        let required = vec!["a".to_string(), "b".to_string()];
        let mut events = vec![];
        for task in ["a", "b"] {
            let mut event = super::super::tests::attempt(user.id, task);
            event.passed = true;
            events.push(event);
        }
        // Journal both without storing them (as if SQLite was busy the whole time).
        for event in &events {
            store
                .journal_write(&Entry { repository: "owner/course".into(), user: user.clone(), title: "Lesson".into(), event: event.clone(), required: required.clone() })
                .unwrap();
        }
        assert_eq!(store.journal_len(), 2);
        // A reopened store's read adds them (the non-waiting replay stores them too).
        let reopened = ProgressStore::new(&root.path().join("progress.sqlite3"));
        let key = &events[0].key;
        let read = reopened.events("owner/course", key).unwrap();
        assert!(issue_progress::status(&read, &events[0].revision, &required).current);
        assert_eq!(reopened.journal_len(), 0);
        // The same entries again (a crash between commit and delete) change nothing.
        for event in &events {
            reopened
                .journal_write(&Entry { repository: "owner/course".into(), user: user.clone(), title: "Lesson".into(), event: event.clone(), required: required.clone() })
                .unwrap();
        }
        assert_eq!(reopened.replay_journal().unwrap(), 2);
        let stored = reopened.events("owner/course", key).unwrap();
        assert_eq!(stored.iter().filter(|e| e.kind == EventKind::Completed).count(), 1);
        assert_eq!(stored.len(), read.len());
    }

    #[test]
    fn entries_for_another_account_are_set_aside_not_stored() {
        let (_root, store, user) = super::super::tests::setup();
        let other = GithubUser { id: user.id + 1, login: "other".into() };
        let event = super::super::tests::attempt(user.id, "a");
        store
            .journal_write(&Entry { repository: "owner/course".into(), user: other, title: "Lesson".into(), event: event.clone(), required: vec![] })
            .unwrap();
        assert_eq!(store.replay_journal().unwrap(), 0);
        assert_eq!(store.journal_len(), 0);
        assert!(store.events("owner/course", &event.key).unwrap().is_empty());
    }
}
