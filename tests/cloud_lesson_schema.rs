use molip_quest::repository_course::{CourseManifest, Lesson};

/// A player without the cloud runtime ignored the unknown `cloud` field and opened the steps as plain
/// Bash practice: no editor for create-subnet.sh, no local cloud and no grader. Schema 4 makes such
/// players (build 181 accepted only 1-3) refuse the lesson; this player still opens the earlier schema-2 revision.
#[test]
fn cloud_content_cannot_be_opened_as_plain_bash_practice() {
    let course = CourseManifest::parse(include_str!("fixtures/player-pilot/클/course.json")).unwrap();
    let raw = include_str!("../courses/redesigned/cloud-vpc-subnet-ec2.json");
    let lesson = Lesson::parse(raw, &course.lessons[0]).unwrap();
    assert_eq!(lesson.schema_version, 4);
    assert!(lesson.tasks.iter().all(|t| t.git_terminal.as_ref().unwrap().cloud.is_some()));
    // The published -1 revision (schema 2) stays readable: course snapshots installed before build 184
    // hold it, and one unreadable lesson made the whole Java course unreadable.
    let mut legacy: serde_json::Value = serde_json::from_str(raw).unwrap();
    legacy["schema_version"] = 2.into();
    legacy["revision"] = "cloud-vpc-subnet-ec2-1".into();
    assert!(serde_json::from_value::<Lesson>(legacy).unwrap().validate().is_ok(), "installed -1 snapshots must open");
    // Schema 3 stays GitLab's own version.
    let mut gitlab: serde_json::Value = serde_json::from_str(raw).unwrap();
    gitlab["schema_version"] = 3.into();
    assert!(serde_json::from_value::<Lesson>(gitlab).unwrap().validate().is_err());
    // Schema 4 is not a general version bump: a lesson without cloud steps cannot claim it.
    let mut plain: serde_json::Value = serde_json::from_str(include_str!("../courses/redesigned/docker-network-ports.json")).unwrap();
    plain["schema_version"] = 4.into();
    assert!(serde_json::from_value::<Lesson>(plain).unwrap().validate().is_err());
}

/// The lifecycle lesson uses goals that build 188 and older do not know. Such a player fails the whole
/// course update (its installed course stays as it was) instead of opening the steps without a grader.
#[test]
fn lifecycle_lesson_needs_a_player_that_knows_its_goals() {
    let course = CourseManifest::parse(include_str!("fixtures/player-pilot/멈/course.json")).unwrap();
    let raw = include_str!("../courses/redesigned/cloud-ec2-lifecycle.json");
    let lesson = Lesson::parse(raw, &course.lessons[0]).unwrap();
    assert_eq!(lesson.schema_version, 4);
    let goals: Vec<String> = lesson.tasks.iter().map(|t| serde_json::to_value(t.git_terminal.as_ref().unwrap().cloud.as_ref().unwrap().goal).unwrap().as_str().unwrap().to_string()).collect();
    assert_eq!(goals, ["stop_server", "start_server", "stop_server", "terminate_server", "delete_subnet", "delete_vpc"]);
    // An unknown goal is a parse error, never a step that opens without its cloud.
    let unknown = raw.replace("\"goal\": \"delete_vpc\"", "\"goal\": \"delete_everything\"");
    assert_ne!(unknown, raw);
    assert!(serde_json::from_str::<Lesson>(&unknown).is_err());
}
