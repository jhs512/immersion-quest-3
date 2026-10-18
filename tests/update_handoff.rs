use molip_quest::update_handoff::macos_script;

#[test]
fn installer_handoff_rejects_paths_that_are_not_app_bundles_or_disk_images() {
    let root=tempfile::tempdir().unwrap();
    assert!(macos_script(&root.path().join("release.zip"),&root.path().join("Player.app"),123).is_err());
    assert!(macos_script(&root.path().join("release.dmg"),root.path(),123).is_err());
    assert!(macos_script(std::path::Path::new("release.dmg"),&root.path().join("Player.app"),123).is_err());
}

#[test]
fn startup_acknowledgement_is_bound_to_the_bundle_and_owned_update_directory() {
    use molip_quest::update_handoff::acknowledge_startup;
    let root=tempfile::tempdir().unwrap();let bundle=root.path().join("Player.app");std::fs::create_dir(&bundle).unwrap();
    let nonce="0123456789abcdef0123456789abcdef";
    let ack=root.path().join(format!("macos-startup-{nonce}.ack"));let pending=root.path().join("macos-handoff.pending");
    std::fs::write(&pending,format!("{}\n{nonce}\n{}\n",ack.display(),bundle.display())).unwrap();
    assert!(!acknowledge_startup(&pending,&root.path().join("Other.app")).unwrap());
    assert!(!ack.exists());assert!(acknowledge_startup(&pending,&bundle).unwrap());
    assert_eq!(std::fs::read_to_string(ack).unwrap(),nonce);
    std::fs::write(&pending,format!("{}\n{nonce}\n{}\n",root.path().join("outside.ack").display(),bundle.display())).unwrap();
    assert!(acknowledge_startup(&pending,&bundle).is_err());
}

#[cfg(target_os="macos")]
mod native {
    use super::*;
    use std::{path::Path,process::Command};

    fn command(program:&str,args:&[&std::ffi::OsStr]) {
        let result=Command::new(program).args(args).output().unwrap();
        assert!(result.status.success(),"{program}: {}",String::from_utf8_lossy(&result.stderr));
    }
    fn bundle(root:&Path,version:&str,marker:&Path) -> std::path::PathBuf {
        let app=root.join("몰입 퀘스트 3.app");let bin=app.join("Contents/MacOS/molip-quest");
        std::fs::create_dir_all(bin.parent().unwrap()).unwrap();
        std::fs::write(app.join("Contents/Info.plist"),include_str!("../packaging/macos/Info.plist").replace("APP_VERSION","0.1.0")).unwrap();
        let code=root.join("fixture.c");
        let ready=if version=="new" {format!(r#"FILE*p=fopen({},"r");char ack[4096],nonce[128];if(!p||!fgets(ack,sizeof ack,p)||!fgets(nonce,sizeof nonce,p))return 2;fclose(p);ack[strcspn(ack,"\n")]=0;nonce[strcspn(nonce,"\n")]=0;FILE*a=fopen(ack,"w");if(!a)return 3;fputs(nonce,a);fclose(a);"#,serde_json::to_string(marker.parent().unwrap().join("macos-handoff.pending").to_str().unwrap()).unwrap())}else{String::new()};
        let early=if version=="crash" {"return 42;"}else if version=="hang" {"signal(SIGTERM,SIG_IGN);for(;;)sleep(1);"}else{""};
        std::fs::write(&code,format!("#include <stdio.h>\n#include <string.h>\n#include <signal.h>\n#include <unistd.h>\nint main(void){{{early}FILE*f=fopen({},\"w\");if(!f)return 1;fputs(\"{version}\",f);fclose(f);{ready}return 0;}}",serde_json::to_string(marker.to_str().unwrap()).unwrap())).unwrap();
        command("cc",&[code.as_os_str(),std::ffi::OsStr::new("-o"),bin.as_os_str()]);
        command("codesign",&[std::ffi::OsStr::new("--force"),std::ffi::OsStr::new("--deep"),std::ffi::OsStr::new("--sign"),std::ffi::OsStr::new("-"),app.as_os_str()]);
        app
    }
    fn wait_marker(path:&Path,expected:&str) {
        let start=std::time::Instant::now();
        while start.elapsed().as_secs()<10 {
            if std::fs::read_to_string(path).ok().as_deref()==Some(expected){return}
            std::thread::sleep(std::time::Duration::from_millis(40));
        }
        panic!("Updated fixture app did not restart: {expected}");
    }

    #[test]
    fn real_disk_image_replaces_and_restarts_only_the_disposable_fixture_app() {
        let root=tempfile::Builder::new().prefix("mq3 update's ").tempdir().unwrap();
        let marker=root.path().join("started.txt");let target=bundle(&root.path().join("installed"),"old",&marker);
        let source=root.path().join("image");bundle(&source,"new",&marker);
        let state=root.path().join("student-answer.txt");std::fs::write(&state,"answer-99; completed-step-A").unwrap();
        let dmg=root.path().join("release.dmg");
        command("hdiutil",&[std::ffi::OsStr::new("create"),std::ffi::OsStr::new("-srcfolder"),source.as_os_str(),std::ffi::OsStr::new("-format"),std::ffi::OsStr::new("UDZO"),dmg.as_os_str()]);
        let result=Command::new("sh").args(["-c",&macos_script(&dmg,&target,99999999).unwrap()]).status().unwrap();
        assert!(result.success(),"{}",std::fs::read_to_string(format!("{}.handoff.log",dmg.display())).unwrap_or_default());
        wait_marker(&marker,"new");
        assert_eq!(std::fs::read_to_string(state).unwrap(),"answer-99; completed-step-A");
    }

    #[test]
    fn invalid_image_keeps_and_restarts_the_existing_fixture_app() {
        let root=tempfile::tempdir().unwrap();let marker=root.path().join("started.txt");
        let target=bundle(&root.path().join("installed"),"old",&marker);
        let before=std::fs::read(target.join("Contents/MacOS/molip-quest")).unwrap();
        let dmg=root.path().join("broken.dmg");std::fs::write(&dmg,b"not a disk image").unwrap();
        assert!(!Command::new("sh").args(["-c",&macos_script(&dmg,&target,99999999).unwrap()]).status().unwrap().success());
        assert_eq!(std::fs::read(target.join("Contents/MacOS/molip-quest")).unwrap(),before);
        wait_marker(&marker,"old");
    }

    #[test]
    fn an_unwritable_staging_directory_still_restarts_the_existing_app() {
        use std::os::unix::fs::PermissionsExt;
        let root=tempfile::tempdir().unwrap();let marker=root.path().join("started.txt");let parent=root.path().join("installed");
        let target=bundle(&parent,"old",&marker);let dmg=root.path().join("unused.dmg");std::fs::write(&dmg,b"unused").unwrap();
        std::fs::set_permissions(&parent,std::fs::Permissions::from_mode(0o555)).unwrap();
        let result=Command::new("sh").args(["-c",&macos_script(&dmg,&target,99999999).unwrap()]).status();
        std::fs::set_permissions(&parent,std::fs::Permissions::from_mode(0o755)).unwrap();
        assert!(!result.unwrap().success());wait_marker(&marker,"old");
    }

    #[test]
    fn launch_acceptance_without_startup_acknowledgement_rolls_back() {
        assert_unacknowledged_start_rolls_back("crash");
    }

    #[test]
    fn candidate_ignoring_term_cannot_block_rollback_forever() {
        assert_unacknowledged_start_rolls_back("hang");
    }

    fn assert_unacknowledged_start_rolls_back(version:&str) {
        let root=tempfile::tempdir().unwrap();let marker=root.path().join("started.txt");
        let target=bundle(&root.path().join("installed"),"old",&marker);
        let before=std::fs::read(target.join("Contents/MacOS/molip-quest")).unwrap();
        let source=root.path().join("image");bundle(&source,version,&marker);let dmg=root.path().join("crashing.dmg");
        command("hdiutil",&[std::ffi::OsStr::new("create"),std::ffi::OsStr::new("-srcfolder"),source.as_os_str(),std::ffi::OsStr::new("-format"),std::ffi::OsStr::new("UDZO"),dmg.as_os_str()]);
        let started=std::time::Instant::now();
        assert!(!Command::new("sh").args(["-c",&macos_script(&dmg,&target,99999999).unwrap()]).status().unwrap().success());
        assert!(started.elapsed().as_secs()<45,"Rollback exceeded its startup timeout and termination grace");
        assert_eq!(std::fs::read(target.join("Contents/MacOS/molip-quest")).unwrap(),before);
        wait_marker(&marker,"old");
    }
}

#[test]
fn windows_handoff_requires_absolute_executable_paths_and_a_real_process_id() {
    use molip_quest::update_handoff::windows_script;
    let root=tempfile::tempdir().unwrap();let installer=root.path().join("release.exe");let app=root.path().join("player.exe");
    assert!(windows_script(&installer,&app,123).is_ok());
    assert!(windows_script(std::path::Path::new("relative.exe"),&app,123).is_err());
    assert!(windows_script(&root.path().join("release.zip"),&app,123).is_err());
    assert!(windows_script(&installer,&root.path().join("player.app"),123).is_err());
    assert!(windows_script(&installer,&app,0).is_err());
    assert!(windows_script(&root.path().join("bad\npath.exe"),&app,123).is_err());
}

#[cfg(windows)]
#[test]
fn failed_windows_installation_still_reopens_when_its_log_cannot_be_written() {
    use std::{process::Command,os::windows::process::CommandExt};
    let root=tempfile::Builder::new().prefix("mq3-handoff's ").tempdir().unwrap();
    let installer=root.path().join("installer.exe");let player=root.path().join("player.exe");
    let source=root.path().join("fixture.rs");
    std::fs::write(&source,r#"fn main(){if std::env::args().any(|arg|arg=="/VERYSILENT"){std::process::exit(42);}std::fs::write(std::env::var_os("MQ3_HANDOFF_RELAUNCH_MARKER").unwrap(),std::process::id().to_string()).unwrap();}"#).unwrap();
    let build=Command::new(std::env::var_os("RUSTC").unwrap_or_else(||"rustc".into())).arg(&source).arg("-o").arg(&installer).creation_flags(0x08000000).output().unwrap();
    assert!(build.status.success(),"{}",String::from_utf8_lossy(&build.stderr));
    std::fs::copy(&installer,&player).unwrap();
    // A directory at the log path makes Add-Content fail without changing system ACLs.
    std::fs::create_dir(root.path().join("installer.exe.handoff.log")).unwrap();
    let marker=root.path().join("reopened.txt");
    let script=molip_quest::update_handoff::windows_script(&installer,&player,99999999).unwrap();
    let output=Command::new("powershell.exe").args(["-NoProfile","-NonInteractive","-Command",&script])
        .env("MQ3_HANDOFF_RELAUNCH_MARKER",&marker).creation_flags(0x08000000).output().unwrap();
    assert!(!output.status.success(),"A failed installer must remain a failure");
    let deadline=std::time::Instant::now()+std::time::Duration::from_secs(8);
    while !marker.exists(){
        assert!(std::time::Instant::now()<deadline,"Player was not reopened: {}",String::from_utf8_lossy(&output.stderr));
        std::thread::sleep(std::time::Duration::from_millis(50));
    }
    // The marker is produced by the relaunched test executable; wait for its exit.
    let pid=std::fs::read_to_string(marker).unwrap().parse::<u32>().unwrap();
    use windows_sys::Win32::{Foundation::CloseHandle,System::Threading::{OpenProcess,WaitForSingleObject}};
    let process=unsafe{OpenProcess(0x0010_0000,0,pid)};
    if !process.is_null(){let outcome=unsafe{WaitForSingleObject(process,8000)};unsafe{CloseHandle(process)};assert_eq!(outcome,0);}
}
