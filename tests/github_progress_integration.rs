use molip_quest::{github_player::Github,issue_progress::*,repository_course};

#[test]
#[ignore = "Creates clearly marked verification progress in the public course repository"]
fn gh_identity_pinned_content_and_public_issue_round_trip() {
    let github=Github::new();let user=github.user().unwrap();
    assert_eq!(user.login,"jhs512");
    assert!(github.ensure_user(user.id+1).is_err());
    let course=github.course(repository_course::COURSE_REPOSITORY).unwrap();
    assert_eq!(course.lessons.len(),24);
    let first=github.lesson(&course.lessons[0]).unwrap();assert_eq!(first.id,"git-environment");
    // A distinct course/lesson key keeps this smoke test out of real learner progress.
    let key=ProgressKey{user_id:user.id,course_id:"mq3-verification".into(),lesson_id:"progress-protocol".into()};
    let round=new_id();
    let started=LearningEvent::new(key.clone(),"v1.0.0",StudyMode::Review,&round,EventKind::Started);
    let (issue,_)=github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&started).unwrap();
    let mut attempt=LearningEvent::new(key.clone(),"v1.0.0",StudyMode::Review,&round,EventKind::Attempt);
    attempt.task_id=Some("contract-check".into());attempt.passed=true;
    github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&attempt).unwrap();
    let (_,events)=github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&attempt).unwrap();
    assert_eq!(events.iter().filter(|e|e.id==attempt.id).count(),1);
    let mut done=LearningEvent::new(key,"v1.0.0",StudyMode::Review,&round,EventKind::Completed);done.required=vec!["contract-check".into()];
    let (_,events)=github.append(&course.repository,&user,"[시스템 검증] 진도 프로토콜",&done).unwrap();
    assert!(status(&events,"v1.0.0",&done.required).current);
    assert!(!status(&events,"v2.0.0",&done.required).current);
    assert!(status(&events,"v2.0.0",&done.required).completed);
    eprintln!("verified issue {}",issue.html_url);
    let mut cmd=std::process::Command::new("gh");
    cmd.args(["issue","close",&issue.number.to_string(),"--repo",&course.repository,"--reason","completed"]);
    assert!(cmd.output().unwrap().status.success());
}
