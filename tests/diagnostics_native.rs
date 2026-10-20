#![cfg(all(windows, feature = "desktop"))]
#[test]
#[ignore = "Requires an interactive Windows desktop; suspends only its own fixture window"]
fn emergency_report_survives_suspended_player_and_content_targets_lesson() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let script = root.join("tests/support/diagnostics-native.ps1");
    let quote = |path: &std::path::Path| path.to_string_lossy().replace('\'', "''");
    let source = format!(
        "& ([scriptblock]::Create([System.IO.File]::ReadAllText('{}'))) -Binary '{}'",
        quote(&script),
        quote(std::path::Path::new(env!("CARGO_BIN_EXE_molip-quest")))
    );
    let output = std::process::Command::new("powershell.exe")
        .args(["-NoProfile", "-Command", &source])
        .current_dir(root)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}\n{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    let result: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(result["passed"], true);
    assert_eq!(result["main_process_suspended"], true);
    assert_eq!(result["sent_to_github"], false);
    println!("{result}");
}
