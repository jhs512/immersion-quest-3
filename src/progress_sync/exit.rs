//! Exit hands the durable outbox to a separate GUI-less helper.
use super::*;
use std::sync::atomic::{AtomicBool,AtomicUsize,Ordering};
static RECORDERS:AtomicUsize=AtomicUsize::new(0);
static SCHEDULED:AtomicBool=AtomicBool::new(false);
pub struct RecordGuard;
pub fn record_guard()->RecordGuard{RECORDERS.fetch_add(1,Ordering::SeqCst);RecordGuard}
impl Drop for RecordGuard {fn drop(&mut self){RECORDERS.fetch_sub(1,Ordering::SeqCst);}}
/// The child process shares the normal upload lock and durable retry queue.
/// A budget slot is reserved before writing, including an ambiguous lost response.
pub fn flush_before_exit()->Result<(),String>{
    // Journaled saves reach SQLite first; that needs neither GitHub nor a login.
    let store=ProgressStore::installed()?;
    if let Err(error)=store.replay_journal(){eprintln!("Journaled progress remains on disk: {error}");}
    let github=Github::new();let user=github.user()?;
    let _=crate::course_identity::Store::installed()?.sync(&github,&user);
    store.send_pending_mode(&github,&user,true)
}
pub fn schedule_exit_flush(){
    if crate::pilot_source::enabled()||SCHEDULED.swap(true,Ordering::SeqCst){return;}
    let until=std::time::Instant::now()+Duration::from_secs(6);
    while RECORDERS.load(Ordering::SeqCst)>0&&std::time::Instant::now()<until{std::thread::sleep(Duration::from_millis(10));}
    let pending=ProgressStore::installed().and_then(|store|store.connection()?.query_row("SELECT COUNT(*) FROM progress_events WHERE pending=1",[],|row|row.get::<_,u64>(0)).map_err(|e|e.to_string())).unwrap_or(0);
    let names=crate::course_identity::Store::installed().and_then(|store|store.has_pending()).unwrap_or(false);
    // Saves still in the write-ahead journal (SQLite was busy) also need the helper; under a
    // lock the pending count above reads 0.
    let journaled=ProgressStore::installed().map(|store|store.journal_len()).unwrap_or(0);
    if pending==0&&!names&&journaled==0{return;}
    let Ok(executable)=std::env::current_exe() else{return;};
    let mut command=std::process::Command::new(executable);
    command.arg("--flush-progress-on-exit").stdin(std::process::Stdio::null()).stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null());
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
    #[cfg(unix)] {use std::os::unix::process::CommandExt;command.process_group(0);}
    if let Err(error)=command.spawn(){eprintln!("Pending progress remains local: {error}");}
}

#[cfg(test)]
mod tests {
    use super::*;
    fn record(store:&ProgressStore,user:&GithubUser,n:u64){let event=super::super::tests::attempt(user.id,&format!("task-{n}"));store.record("owner/course",user,"Lesson",&event,&[]).unwrap();}
    #[test]
    fn forced_exit_bypasses_normal_window_but_tenth_attempt_blocks_for_a_day(){
        let (root,store,user)=super::super::tests::setup();
        for n in 0..10 {record(&store,&user,n);let mut sent=0;store.flush_batches_mode(1000+n,user.id,true,|batch|{sent+=1;Ok(batch.iter().map(|p|p.event.clone()).collect())}).unwrap();assert_eq!(sent,1);}
        record(&store,&user,11);
        let reopened=ProgressStore::new(&root.path().join("progress.sqlite3"));
        reopened.flush_batches_mode(1010,user.id,true,|_|panic!("budget survives restart")).unwrap();
        assert_eq!(reopened.pending_count(user.id).unwrap(),1);
        reopened.flush_batches(1310,user.id,|batch|Ok(batch.iter().map(|p|p.event.clone()).collect())).unwrap();
        assert_eq!(reopened.pending_count(user.id).unwrap(),0,"normal five-minute sync remains available");
        record(&store,&user,12);
        reopened.flush_batches_mode(1009+86400,user.id,true,|batch|Ok(batch.iter().map(|p|p.event.clone()).collect())).unwrap();
        assert_eq!(reopened.pending_count(user.id).unwrap(),0);
    }
    #[test]
    fn empty_exits_do_not_consume_budget_and_failures_remain_pending(){
        let (_root,store,user)=super::super::tests::setup();
        for _ in 0..15 {store.flush_batches_mode(1000,user.id,true,|_|panic!("no pending events")).unwrap();}
        record(&store,&user,1);
        assert!(store.flush_batches_mode(1000,user.id,true,|_|Err("response lost".into())).is_err());
        assert_eq!(store.pending_count(user.id).unwrap(),1);
        assert_eq!(store.connection().unwrap().query_row("SELECT COUNT(*) FROM progress_exit_attempts",[],|r|r.get::<_,usize>(0)).unwrap(),1);
    }
    #[test]
    fn one_exit_flushes_multiple_course_issues_using_one_slot(){
        let (_root,store,user)=super::super::tests::setup();
        record(&store,&user,1);
        let mut other=super::super::tests::attempt(user.id,"another-course");other.key.course_id="second-course".into();
        store.record("owner/course",&user,"Lesson",&other,&[]).unwrap();
        let mut calls=0;store.flush_batches_mode(1000,user.id,true,|batch|{calls+=1;Ok(batch.iter().map(|p|p.event.clone()).collect())}).unwrap();
        assert_eq!(calls,2);assert_eq!(store.connection().unwrap().query_row("SELECT COUNT(*) FROM progress_exit_attempts",[],|r|r.get::<_,usize>(0)).unwrap(),1);
    }
}
