use crate::{content_updates::SnapshotStore, course_authoring, repository_course::CourseManifest};
use std::{collections::BTreeMap, path::Path};

#[test]
fn redesigned_defaults_open_complete_independent_snapshots_and_preserve_added_courses() {
    // This test changes a process-global environment variable. Run its body
    // alone so parallel web-runtime tests never install into this temp folder.
    if std::env::var_os("MQ3_COURSE_AUTHORING_PROCESS").is_none() {
        let mut command=std::process::Command::new(std::env::current_exe().unwrap());
        command.args(["--exact","course_authoring_tests::redesigned_defaults_open_complete_independent_snapshots_and_preserve_added_courses","--nocapture"])
            .env("MQ3_COURSE_AUTHORING_PROCESS","1");
        #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
        let output=command.output().unwrap();
        assert!(output.status.success(),"{}\n{}",String::from_utf8_lossy(&output.stdout),String::from_utf8_lossy(&output.stderr));
        return;
    }
    let directory = tempfile::tempdir().unwrap();
    // This filtered test owns its process's data directory and never invokes gh.
    let previous = std::env::var_os("MOLIP_DATA_DIR");
    std::env::set_var("MOLIP_DATA_DIR", directory.path());
    let expected = [
        "jhs512/mq3-course-redesigned-java-backend",
        "jhs512/mq3-course-redesigned-engineer-practical",
        "jhs512/mq3-course-redesigned-aice-associate",
    ].map(String::from).to_vec();
    assert_eq!(course_authoring::catalog(), expected);
    let saved = directory.path().join("repository-courses.json");
    let original = br#"["teacher/extra-course","jhs512/mq3-course-java-backend","bad","teacher/extra-course"]"#;
    std::fs::write(&saved, original).unwrap();
    let mut upgraded = expected;
    upgraded.extend(["teacher/extra-course".into(), "jhs512/mq3-course-java-backend".into()]);
    assert_eq!(course_authoring::catalog(), upgraded);
    assert_eq!(std::fs::read(&saved).unwrap(), original);
    assert_eq!(crate::repository_course::initial_repository(), upgraded[0]);

    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let catalog: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(root.join("tools/redesigned_courses/catalog.json")).unwrap()).unwrap();
    let mut documents = BTreeMap::new();
    for course in catalog["courses"].as_array().unwrap() {
        for item in course["lessons"].as_array().unwrap() {
            let raw = std::fs::read_to_string(root.join(format!("courses/redesigned/{}.json", item["key"].as_str().unwrap()))).unwrap();
            assert!(documents.insert(item["id"].as_str().unwrap().to_string(), raw).is_none());
        }
    }
    let store = SnapshotStore::new(directory.path().join("snapshots"));
    let legacy_repo = "mq3-validation/course";
    let old_raw = std::fs::read_to_string(root.join("tests/fixtures/player-pilot/a/course.json")).unwrap();
    let old_lesson = std::fs::read_to_string(root.join("tests/fixtures/player-pilot/a/lesson.json")).unwrap();
    let old = store.prepare(legacy_repo, &old_raw, |_| Ok(old_lesson.clone())).unwrap();
    store.apply(&old).unwrap();
    let old_fingerprint = old.fingerprint();
    let mut all_steps = std::collections::HashSet::new();
    for (name, count) in [("java-backend",43),("aice-associate",24),("engineer-practical",30)] {
        let raw = std::fs::read_to_string(root.join(format!("courses/redesigned-courses/{name}.json"))).unwrap();
        let course = CourseManifest::parse(&raw).unwrap();
        assert_eq!(course.lessons.len(),count);
        let snapshot = store.prepare(&course.repository, &raw, |reference| Ok(documents[&reference.id].clone())).unwrap();
        store.apply(&snapshot).unwrap();
        for reference in &course.lessons {
            let lesson = snapshot.lesson(reference).unwrap();
            assert!(!lesson.objectives.is_empty());
            for task in &lesson.tasks { assert!(all_steps.insert(task.id.clone()),"Shared step across independent courses"); }
        }
        let changed = raw.replacen(&course.lessons[0].sha256, &"0".repeat(64), 1);
        assert!(store.prepare(&course.repository,&changed,|reference|Ok(documents[&reference.id].clone())).is_err());
        assert_eq!(store.active(&course.repository).unwrap().unwrap().fingerprint(),snapshot.fingerprint());
    }
    assert_eq!(store.active(legacy_repo).unwrap().unwrap().fingerprint(),old_fingerprint);
    assert_eq!(std::fs::read(saved).unwrap(),original);
    if let Some(value) = previous { std::env::set_var("MOLIP_DATA_DIR",value); } else { std::env::remove_var("MOLIP_DATA_DIR"); }
}
