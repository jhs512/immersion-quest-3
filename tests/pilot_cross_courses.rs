#![cfg(debug_assertions)]
use molip_quest::{github_player::Github, pilot_source};

#[test]
fn complete_certification_course_checks_remain_inside_the_isolated_transport() {
    std::env::set_var("MOLIP_PILOT", "1");
    let github = Github::new();
    let versions = pilot_source::versions();
    let unique: std::collections::BTreeSet<_> = versions.iter().collect();
    assert_eq!(versions.len(), unique.len(), "debug course shortcuts must not shadow lesson shortcuts");
    for (version, count) in [(pilot_source::AICE_COURSE_VERSION, 24), (pilot_source::ENGINEER_COURSE_VERSION, 30)] {
        pilot_source::set_version(version).unwrap();
        let course = github.course(pilot_source::REPOSITORY).unwrap();
        assert_eq!(course.repository, pilot_source::REPOSITORY);
        assert_eq!(course.lessons.len(), count);
        for reference in &course.lessons {
            assert_eq!(reference.repository, "mq3-validation/lesson");
            let lesson = github.lesson(reference).unwrap();
            assert!(molip_quest::challenges::designated(reference, &lesson).is_some());
        }
    }
    assert!(github.course("unrelated/private-course").is_err());
}
