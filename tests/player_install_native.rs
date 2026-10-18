#![cfg(all(feature = "desktop", debug_assertions))]
#[path = "support/native_player.rs"]
mod native_player;
use molip_quest::pilot_session::PilotSession;
use std::{
    path::{Path, PathBuf},
    process::Command,
};
fn command(program: &Path, args: &[&std::ffi::OsStr]) {
    let output = Command::new(program).args(args).output().unwrap();
    assert!(
        output.status.success(),
        "{}: {} {}",
        program.display(),
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
}
fn complete(session: &PilotSession, marker: &Path) {
    assert_eq!(std::fs::read_to_string(marker).unwrap(), "new");
    let result = native_player::result(session, "reopen");
    #[cfg(windows)]
    {
        // Wait only; do not signal a process after the result has been written.
        use windows_sys::Win32::{
            Foundation::CloseHandle,
            System::Threading::{OpenProcess, WaitForSingleObject},
        };
        let pid = result["process_id"].as_u64().unwrap() as u32;
        let process = unsafe { OpenProcess(0x0010_0000, 0, pid) }; // SYNCHRONIZE
        if !process.is_null() {
            let outcome = unsafe { WaitForSingleObject(process, 15000) };
            unsafe {
                CloseHandle(process);
            };
            assert_eq!(outcome, 0, "Updated player did not finish its self-test");
        }
    }

    std::fs::write(
        "target/pilot-install-result.json",
        serde_json::json!({"passed":true,"replacement":"new","restored":result}).to_string(),
    )
    .unwrap();
}
#[cfg(windows)]
#[test]
#[ignore = "Requires Inno Setup and an interactive desktop"]
fn real_windows_installer_replaces_disposable_player_and_restores_its_state() {
    let session = PilotSession::new().unwrap();
    // Inno Setup rejects Win32 verbatim prefixes in script filenames and directives.
    // Keep the session's canonical environment, but pass ordinary paths to the compiler.
    let path=session.directory().to_str().unwrap();
    let root=PathBuf::from(path.strip_prefix(r"\\?\").unwrap_or(path));
    let installed = root.join("installed");
    std::fs::create_dir(&installed).unwrap();
    let executable = installed.join("molip-quest.exe");
    std::fs::copy(env!("CARGO_BIN_EXE_molip-quest"), &executable).unwrap();
    let marker = installed.join("generation.txt");
    std::fs::write(&marker, "old").unwrap();
    native_player::run(&executable, &session, "seed");
    let generation = root.join("generation.txt");
    std::fs::write(&generation, "new").unwrap();
    let setup = root.join("fixture.iss");
    let source = format!(
        r#"[Setup]
AppId=MQ3Pilot{}
AppName=MQ3 Pilot
AppVersion=1.1.0
DefaultDirName={}
PrivilegesRequired=lowest
Uninstallable=no
CreateUninstallRegKey=no
UsePreviousAppDir=no
OutputDir={}
OutputBaseFilename=fixture
Compression=none
[Files]
Source: "{}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{}"; DestDir: "{{app}}"; Flags: ignoreversion
"#,
        molip_quest::issue_progress::new_id(),
        installed.display(),
        root.display(),
        env!("CARGO_BIN_EXE_molip-quest"),
        generation.display()
    );
    std::fs::write(&setup, format!("\u{feff}{source}")).unwrap();
    let compiler = std::env::var_os("MQ3_ISCC")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"));
    command(&compiler, &[setup.as_os_str()]);
    let installer = root.join("fixture.exe");
    let script =
        molip_quest::update_handoff::windows_script(&installer, &executable, 99999999).unwrap();
    let mut handoff = Command::new("powershell.exe");
    handoff.args(["-NoProfile", "-NonInteractive", "-Command", &script]);
    native_player::configure(&session, &mut handoff, "reopen");
    let status = native_player::wait(
        &mut handoff.spawn().unwrap(),
        90,
        "Windows installer handoff",
    );
    assert!(status.success());
    let deadline = std::time::Instant::now() + std::time::Duration::from_secs(40);
    while !root.join("restart-reopen.json").exists() {
        assert!(
            std::time::Instant::now() < deadline,
            "Updated player did not report state"
        );
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
    complete(&session, &marker);
}

#[cfg(target_os = "macos")]
fn bundle(root: &Path, generation: &str, session: &PilotSession) -> PathBuf {
    let app = root.join("몰입 퀘스트 3.app");
    let executable = app.join("Contents/MacOS/molip-quest");
    std::fs::create_dir_all(executable.parent().unwrap()).unwrap();
    std::fs::create_dir_all(app.join("Contents/Resources")).unwrap();
    std::fs::copy(env!("CARGO_BIN_EXE_molip-quest"), &executable).unwrap();
    std::fs::write(app.join("Contents/Resources/generation.txt"), generation).unwrap();
    let mut plist = include_str!("../packaging/macos/Info.plist").replace("APP_VERSION", "0.1.0");
    // open -n fallback must retain the isolated fixture even through Launch Services.
    // https://developer.apple.com/documentation/bundleresources/information-property-list/lsenvironment
    let mut environment = Command::new("unused");
    session.configure(&mut environment);
    environment.env("MOLIP_PILOT_SELF_TEST", "restart-reopen");
    let escape = |value: &str| {
        value
            .replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
    };
    let entries = environment
        .get_envs()
        .filter_map(|(key, value)| {
            value.map(|value| {
                format!(
                    "<key>{}</key><string>{}</string>",
                    escape(&key.to_string_lossy()),
                    escape(&value.to_string_lossy())
                )
            })
        })
        .collect::<String>();
    let index = plist.rfind("</dict>").unwrap();
    plist.insert_str(
        index,
        &format!("<key>LSEnvironment</key><dict>{entries}</dict>"),
    );
    std::fs::write(app.join("Contents/Info.plist"), plist).unwrap();
    command(
        Path::new("codesign"),
        &[
            std::ffi::OsStr::new("--force"),
            std::ffi::OsStr::new("--deep"),
            std::ffi::OsStr::new("--sign"),
            std::ffi::OsStr::new("-"),
            app.as_os_str(),
        ],
    );
    app
}
#[cfg(target_os = "macos")]
#[test]
#[ignore = "Requires macOS disk image tools and an interactive desktop"]
fn real_macos_image_replaces_disposable_player_and_restores_its_state() {
    let session = PilotSession::new().unwrap();
    let target = bundle(&session.directory().join("installed"), "old", &session);
    native_player::run(&target.join("Contents/MacOS/molip-quest"), &session, "seed");
    let source = session.directory().join("image");
    bundle(&source, "new", &session);
    let updates = session.directory().join("updates");
    std::fs::create_dir_all(&updates).unwrap();
    let image = updates.join("release.dmg");
    // Temporary probe for the Intel runner's image-creation ENOSPC failure.
    eprintln!("[DEBUG-dmgspace] binary bytes: {}", std::fs::metadata(source.join("몰입 퀘스트 3.app/Contents/MacOS/molip-quest")).unwrap().len());
    for (tool,args) in [("df",vec!["-h"]),("du",vec!["-sk"])] {
        let result=Command::new(tool).args(args).arg(&source).output().unwrap();
        eprintln!("[DEBUG-dmgspace] {tool}: {} {}",String::from_utf8_lossy(&result.stdout),String::from_utf8_lossy(&result.stderr));
    }
    command(
        Path::new("hdiutil"),
        &[
            std::ffi::OsStr::new("create"),
            std::ffi::OsStr::new("-srcfolder"),
            source.as_os_str(),
            std::ffi::OsStr::new("-format"),
            std::ffi::OsStr::new("UDZO"),
            image.as_os_str(),
        ],
    );
    let script = molip_quest::update_handoff::macos_script(&image, &target, 99999999).unwrap();
    let mut handoff = Command::new("sh");
    handoff.args(["-c", &script]);
    native_player::configure(&session, &mut handoff, "reopen");
    let status = native_player::wait(&mut handoff.spawn().unwrap(), 90, "macOS installer handoff");
    assert!(
        status.success(),
        "{}",
        std::fs::read_to_string(format!("{}.handoff.log", image.display())).unwrap_or_default()
    );
    let deadline = std::time::Instant::now() + std::time::Duration::from_secs(40);
    while !session.directory().join("restart-reopen.json").exists() {
        assert!(
            std::time::Instant::now() < deadline,
            "Updated player did not report state"
        );
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
    complete(&session, &target.join("Contents/Resources/generation.txt"));
}
