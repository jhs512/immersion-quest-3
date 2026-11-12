use molip_quest::repository_course::{CourseManifest, Lesson};

/// A player without the cloud runtime ignored the unknown `cloud` field and opened the steps as plain
/// Bash practice: no editor for create-subnet.sh, no local cloud and no grader. Schema 4 makes such
/// players (build 181 accepted only 1-3) refuse the lesson; this player requires 4 for cloud steps.
#[test]
fn cloud_content_cannot_be_opened_as_plain_bash_practice() {
    let course = CourseManifest::parse(include_str!("fixtures/player-pilot/클/course.json")).unwrap();
    let raw = include_str!("../courses/redesigned/cloud-vpc-subnet-ec2.json");
    let lesson = Lesson::parse(raw, &course.lessons[0]).unwrap();
    assert_eq!(lesson.schema_version, 4);
    assert!(lesson.tasks.iter().all(|t| t.git_terminal.as_ref().unwrap().cloud.is_some()));
    for older in [2, 3] {
        let mut downgraded: serde_json::Value = serde_json::from_str(raw).unwrap();
        downgraded["schema_version"] = older.into();
        assert!(serde_json::from_value::<Lesson>(downgraded).unwrap().validate().is_err(), "cloud steps at schema {older}");
    }
    // Schema 4 is not a general version bump: a lesson without cloud steps cannot claim it.
    let mut plain: serde_json::Value = serde_json::from_str(include_str!("../courses/redesigned/docker-network-ports.json")).unwrap();
    plain["schema_version"] = 4.into();
    assert!(serde_json::from_value::<Lesson>(plain).unwrap().validate().is_err());
}
