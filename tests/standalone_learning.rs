use molip_quest::{learning_store::LearningStore, runner::check_unit, Course};

#[tokio::test]
async fn student_tests_and_persists_completion_without_an_account_or_server() {
    let mut course = Course::parse(include_str!("../courses/getting-started.json")).unwrap();
    let unit = &course.chapters[0].units[0];
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("learning.sqlite3");
    let mut store = LearningStore::open(&path).unwrap();
    let failed = check_unit(unit, "print('wrong')").await.unwrap();
    store
        .save(&course.id, unit, "print('wrong')", &failed)
        .unwrap();
    assert!(store.completed(&course).unwrap().is_empty());
    let source = "print('Hello, Python!')";
    let passed = check_unit(unit, source).await.unwrap();
    assert!(passed.passed);
    store.save(&course.id, unit, source, &passed).unwrap();
    store.save(&course.id, unit, source, &passed).unwrap();
    drop(store);
    let store = LearningStore::open(&path).unwrap();
    assert_eq!(store.completed(&course).unwrap().len(), 1);
    let db = rusqlite::Connection::open(&path).unwrap();
    assert_eq!(
        db.query_row(
            "SELECT code FROM attempts ORDER BY id DESC LIMIT 1",
            [],
            |row| row.get::<_, String>(0)
        )
        .unwrap(),
        source
    );
    course.chapters[0].units[0].revision += 1;
    assert!(store.completed(&course).unwrap().is_empty());
}
