//! Startup and detached shutdown refresh complete course snapshots, never progress.
use crate::{content_updates::{Snapshot,SnapshotStore},github_player::Github};
use std::sync::atomic::{AtomicBool,Ordering};

/// A background authentication failure must not leave an old course looking current.
pub fn update_failure(error:&str,requested:bool)->Option<String> {
    let lower=error.to_ascii_lowercase();
    if lower.contains("401")||lower.contains("requires authentication")||lower.contains("bad credentials") {
        Some("GitHub 로그인을 확인해 주세요. 인증 오류로 새 수업을 받지 못하고 있어요.".into())
    }else if requested {Some(error.to_owned())}else{None}
}

/// Download and validate first. A failed download or backup leaves the old course usable.
pub fn refresh_course(store:&SnapshotStore,repository:&str,
    fetch:impl FnOnce()->Result<Snapshot,String>,
    backup:impl FnOnce(&Snapshot)->Result<(),String>)->Result<bool,String> {
    let before=store.active(repository)?;
    let next=fetch()?;
    if next.course().repository!=repository {return Err("Course repository changed during refresh".into())}
    if before.as_ref().is_some_and(|old|old.course().id!=next.course().id) {return Err("Course identity changed during refresh".into())}
    let fingerprint=|snapshot:Option<&Snapshot>|snapshot.map(Snapshot::fingerprint);
    if fingerprint(before.as_ref())==Some(next.fingerprint()) {return Ok(false)}
    // Do not overwrite another updater's successful install with an older candidate.
    if fingerprint(store.active(repository)?.as_ref())!=fingerprint(before.as_ref()) {return Ok(false)}
    backup(&next)?;
    store.apply(&next)?;
    Ok(true)
}

pub fn synchronize(github:&Github,user:u64)->Result<(),String> {
    synchronize_inner(github,user,true)
}
pub fn synchronize_on_exit(github:&Github,user:u64)->Result<(),String> {
    synchronize_inner(github,user,false)
}
fn synchronize_inner(github:&Github,user:u64,wait:bool)->Result<(),String> {
    let directory=crate::data_dir()?;
    std::fs::create_dir_all(&directory).map_err(|e|e.to_string())?;
    let lock=std::fs::OpenOptions::new().create(true).truncate(false).read(true).write(true)
        .open(directory.join("content-lifecycle.lock")).map_err(|e|e.to_string())?;
    // A quick restart waits for the previous shutdown worker instead of racing it.
    if wait {lock.lock().map_err(|e|e.to_string())?;}
    else {lock.try_lock().map_err(|e|e.to_string())?;}
    let store=crate::content_updates::installed_store()?;
    let mut errors=Vec::new();
    for repository in crate::course_authoring::catalog() {
        let result=(||{
            github.installed_course(&repository)?;
            refresh_course(&store,&repository,||github.prepare_course(&repository),|next|{
                github.ensure_user(user)?;
                crate::drafts::backup_repository(user,&next.course().id,&next.fingerprint())
            })
        })();
        if let Err(error)=result {errors.push(format!("{repository}: {error}"));}
    }
    if errors.is_empty(){Ok(())}else{Err(errors.join("\n"))}
}

static EXIT_SCHEDULED:AtomicBool=AtomicBool::new(false);
pub fn schedule_exit_refresh() {
    if crate::pilot_source::enabled()||EXIT_SCHEDULED.swap(true,Ordering::SeqCst){return;}
    let Ok(executable)=std::env::current_exe() else{return;};
    let mut command=std::process::Command::new(executable);
    command.arg("--refresh-content-on-exit").stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null());
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
    #[cfg(unix)] {use std::os::unix::process::CommandExt;command.process_group(0);}
    if let Err(error)=command.spawn(){eprintln!("Content refresh will retry at startup: {error}");}
}
