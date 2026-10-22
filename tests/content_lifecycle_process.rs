#![cfg(all(feature="desktop",debug_assertions))]
#[test]
fn detached_content_worker_updates_a_closed_player_and_preserves_its_answer() {
    use molip_quest::{pilot_session::PilotSession,pilot_source,content_updates,drafts,github_player::Github,issue_progress::{ProgressKey,StudyMode}};
    let session=PilotSession::new().unwrap();
    let mut worker=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    session.configure(&mut worker);worker.arg("--refresh-content-on-exit");
    for (key,value) in worker.get_envs() {if let Some(value)=value {std::env::set_var(key,value);}}
    pilot_source::set_version('a').unwrap();
    let github=Github::new();let user=github.user().unwrap();
    let initial=github.installed_course(pilot_source::REPOSITORY).unwrap();
    let key=ProgressKey{user_id:user.id,course_id:initial.id.clone(),lesson_id:initial.lessons[0].id.clone()};
    let scope=drafts::repository_scope(&key,StudyMode::Full,"student-task");
    drafts::save(&scope,"my unfinished answer",&Default::default()).unwrap();
    pilot_source::set_version('b').unwrap();
    assert!(worker.status().unwrap().success());
    let store=content_updates::installed_store().unwrap();
    let updated=store.active(pilot_source::REPOSITORY).unwrap().unwrap();
    assert_eq!(updated.course().lessons[0].revision,"pilot-b");
    assert_eq!(drafts::load(&scope).unwrap().unwrap().code,"my unfinished answer");
    assert_eq!(drafts::repository_backups(user.id,&initial.id).unwrap().len(),1);
    assert!(worker.status().unwrap().success());
    assert_eq!(drafts::repository_backups(user.id,&initial.id).unwrap().len(),1,"unchanged exit must not duplicate backups");
    // The immutable revision is already verified locally: an unchanged manifest
    // must not download every lesson again, even if the remote copy is damaged.
    pilot_source::corrupt_update().unwrap();
    assert_eq!(github.prepare_course(pilot_source::REPOSITORY).unwrap().fingerprint(),updated.fingerprint());
    let lock=std::fs::OpenOptions::new().read(true).write(true).open(session.directory().join("content-lifecycle.lock")).unwrap();
    lock.lock().unwrap();
    let mut child=worker.spawn().unwrap();
    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(5);
    loop {
        if let Some(status)=child.try_wait().unwrap() {assert!(!status.success(),"a second exit worker should defer to the existing worker");break;}
        if std::time::Instant::now()>deadline {let _=child.kill();let _=child.wait();panic!("duplicate shutdown worker queued behind an existing updater");}
        std::thread::sleep(std::time::Duration::from_millis(20));
    }
}
