use molip_quest::repository_course::Task;

#[test]
fn the_edited_file_selects_highlighting_independently_of_the_docker_runtime() {
    for (language,entry,expected) in [
        ("docker","Main.java","java"),("docker","lesson.sql","sql"),
        ("docker","migration.sql","sql"),("docker","compose.yaml","shell"),
        ("java_libraries","Main.java","java"),("web","main.jsx","javascript"),
        ("web","index.html","html"),
    ] {
        let task:Task=serde_json::from_value(serde_json::json!({"id":"editor-probe","title":"editor",
            "goal":"edit","language":language,"entry_file":entry,"starter_code":"","solution":"","tests":[]})).unwrap();
        assert_eq!(task.editor_language(),expected,"{language} {entry}");
    }
}
