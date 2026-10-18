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
        let early=if version=="crash" {"return 42;"}else{""};
        std::fs::write(&code,format!("#include <stdio.h>\n#include <string.h>\nint main(void){{{early}FILE*f=fopen({},\"w\");if(!f)return 1;fputs(\"{version}\",f);fclose(f);{ready}return 0;}}",serde_json::to_string(marker.to_str().unwrap()).unwrap())).unwrap();
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
        let root=tempfile::tempdir().unwrap();let marker=root.path().join("started.txt");
        let target=bundle(&root.path().join("installed"),"old",&marker);
        let before=std::fs::read(target.join("Contents/MacOS/molip-quest")).unwrap();
        let source=root.path().join("image");bundle(&source,"crash",&marker);let dmg=root.path().join("crashing.dmg");
        command("hdiutil",&[std::ffi::OsStr::new("create"),std::ffi::OsStr::new("-srcfolder"),source.as_os_str(),std::ffi::OsStr::new("-format"),std::ffi::OsStr::new("UDZO"),dmg.as_os_str()]);
        assert!(!Command::new("sh").args(["-c",&macos_script(&dmg,&target,99999999).unwrap()]).status().unwrap().success());
        assert_eq!(std::fs::read(target.join("Contents/MacOS/molip-quest")).unwrap(),before);
        wait_marker(&marker,"old");
    }
}
