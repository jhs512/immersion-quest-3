//! Runs the Python tests of the course tooling (tools/kpc_course/test_*.py: source identity,
//! stale detection, the coding 해설 compiler rules) from `cargo test`. Skipped when python or pytest is missing.

#[test]
fn source_identity_python_tests_pass() {
    let test_file = concat!(env!("CARGO_MANIFEST_DIR"), "/tools/kpc_course");
    let output = match std::process::Command::new("python")
        .args(["-m", "pytest", "-q", test_file])
        .env("PYTHONIOENCODING", "utf-8")
        .output()
    {
        Ok(output) => output,
        Err(error) => {
            eprintln!("python을 찾지 못해 Python 테스트를 건너뜁니다: {error}");
            return;
        }
    };
    let stdout = String::from_utf8_lossy(&output.stdout);
    if stdout.contains("No module named pytest") {
        eprintln!("pytest가 없어 Python 테스트를 건너뜁니다");
        return;
    }
    assert!(
        output.status.success(),
        "python -m pytest tools/kpc_course 실패\n{stdout}\n{}",
        String::from_utf8_lossy(&output.stderr)
    );
}
