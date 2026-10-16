//! Runs the Node tests of the option matcher (assets/layout/quiz-pick.js) from `cargo test`,
//! so the JavaScript the app really executes is covered too. Skipped when `node` is not on PATH.

#[test]
fn quiz_pick_node_tests_pass() {
    let test_file = concat!(env!("CARGO_MANIFEST_DIR"), "/tests/js/quiz-pick.test.mjs");
    let output = match std::process::Command::new("node")
        .args(["--test", test_file])
        .output()
    {
        Ok(output) => output,
        Err(error) => {
            eprintln!("node를 찾지 못해 JS 테스트를 건너뜁니다: {error}");
            return;
        }
    };
    assert!(
        output.status.success(),
        "node --test tests/js/quiz-pick.test.mjs 실패\n{}\n{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
}
