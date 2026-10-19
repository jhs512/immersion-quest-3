use molip_quest::{github_player::Github,lesson_registry,pilot_source};
#[test]
fn every_registered_lesson_opens_through_the_real_isolated_transport() {
    std::env::set_var("MOLIP_PILOT","1");
    let github=Github::new();let mut steps=0;
    let mut versions=std::collections::HashSet::new();
    assert_eq!(lesson_registry::LESSONS.len(),72);
    for row in lesson_registry::LESSONS {
        assert!(versions.insert(row.pilot));
        pilot_source::set_version(row.pilot).unwrap();
        let course=github.course(pilot_source::REPOSITORY).unwrap();
        let lesson=github.lesson(&course.lessons[0]).unwrap();
        assert_eq!(lesson.revision,row.revision);steps+=lesson.tasks.len();
        if row.driver!="native" {
            let script=lesson_registry::self_test_script(row.key).unwrap();
            let source=script.strip_prefix("window.mq3LessonPilot=").unwrap();
            let config=serde_json::Deserializer::from_str(source).into_iter::<serde_json::Value>().next().unwrap().unwrap();
            assert_eq!(config["tasks"].as_array().unwrap().len(),lesson.tasks.len());
            assert_eq!(config["revision"],row.revision);
            if row.key=="java-values" {assert!(config["modifications"]["1"]["source"].as_str().unwrap().contains("println(99)"));}
            if row.key=="git-remote" {assert_eq!(config["studentCommands"].as_array().unwrap().len(),8);}
        }
    }
    assert_eq!(steps,689);
    assert!(lesson_registry::self_test_script("unknown-course").is_none());
    assert!(pilot_source::set_version('!').is_err());
    pilot_source::set_version('a').unwrap();
    assert_eq!(github.lesson(&github.course(pilot_source::REPOSITORY).unwrap().lessons[0]).unwrap().revision,"pilot-a");
}
