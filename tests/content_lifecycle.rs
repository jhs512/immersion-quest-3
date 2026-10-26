use molip_quest::{content_lifecycle::refresh_course,content_updates::{Snapshot,SnapshotStore}};

#[test]
fn expired_login_is_visible_even_during_an_automatic_content_check() {
    let error="GitHub CLI request failed: gh: Requires authentication (HTTP 401)";
    let notice=molip_quest::content_lifecycle::update_failure(error,false).unwrap();
    assert!(notice.contains("인증 오류"));
    assert!(notice.contains("새 수업"));
    assert!(molip_quest::content_lifecycle::update_failure("offline",false).is_none());
    assert_eq!(molip_quest::content_lifecycle::update_failure("offline",true),Some("offline".into()));
}

#[test]
fn login_recovery_distinguishes_expired_credentials_from_network_and_repository_errors() {
    use molip_quest::content_lifecycle::authentication_required;
    for error in ["gh: Requires authentication (HTTP 401)","Bad credentials","You are not logged into any GitHub hosts.","To get started with GitHub CLI, please run: gh auth login","The token is invalid","Token has expired"] {
        assert!(authentication_required(error),"{error}");
    }
    for error in ["network is unreachable","HTTP 403: Resource not accessible by integration","HTTP 404: Not Found","GitHub CLI를 찾지 못했어요. gh를 설치하세요.","로그인 계정이 바뀌었어요. 현재 수업을 다시 여세요."] {
        assert!(!authentication_required(error),"{error}");
    }
}
fn snapshot(store:&SnapshotStore,version:&str)->Snapshot {
    let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/player-pilot").join(version);
    store.prepare("mq3-validation/course",&std::fs::read_to_string(root.join("course.json")).unwrap(),|_|Ok(std::fs::read_to_string(root.join("lesson.json")).unwrap())).unwrap()
}

#[test]
fn lifecycle_refresh_installs_verified_content_and_leaves_old_content_on_failure() {
    let root=tempfile::tempdir().unwrap();let store=SnapshotStore::new(root.path());
    let repo="mq3-validation/course";let a=snapshot(&store,"a");let b=snapshot(&store,"b");store.apply(&a).unwrap();
    assert!(refresh_course(&store,repo,||Err("offline".into()),|_|panic!("no backup without content")).is_err());
    assert_eq!(store.active(repo).unwrap().unwrap(),a);
    assert!(refresh_course(&store,repo,||Ok(b.clone()),|_|Err("disk full".into())).is_err());
    assert_eq!(store.active(repo).unwrap().unwrap(),a);
    let mut backed_up=false;
    assert!(refresh_course(&store,repo,||Ok(b.clone()),|next|{assert_eq!(next,&b);backed_up=true;Ok(())}).unwrap());
    assert!(backed_up);assert_eq!(SnapshotStore::new(root.path()).active(repo).unwrap().unwrap(),b);
    assert!(!refresh_course(&store,repo,||Ok(b.clone()),|_|panic!("unchanged content needs no backup")).unwrap());
    assert_eq!(b.lesson_source(&b.course().lessons[0]).unwrap(),std::fs::read_to_string("tests/fixtures/player-pilot/b/lesson.json").unwrap());
    assert!(b.lesson_source(&a.course().lessons[0]).is_none());
}

#[test]
fn lifecycle_refresh_does_not_overwrite_an_update_installed_during_download() {
    let root=tempfile::tempdir().unwrap();let store=SnapshotStore::new(root.path());
    let a=snapshot(&store,"a");let b=snapshot(&store,"b");let c=snapshot(&store,"c");store.apply(&a).unwrap();
    assert!(!refresh_course(&store,"mq3-validation/course",||{store.apply(&c)?;Ok(b)},|_|panic!("newer content must remain active")).unwrap());
    assert_eq!(store.active("mq3-validation/course").unwrap().unwrap(),c);
}
