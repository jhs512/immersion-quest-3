#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
use molip_quest::{lesson_link::LessonLink,repository_course::CourseManifest};
#[test]
#[ignore="Requires an interactive native desktop"]
fn web_link_and_secondary_launch_use_the_real_authenticated_player(){
    std::fs::create_dir_all("target").unwrap();
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let first=LessonLink::new(&course.repository,&course.lessons[0].id).unwrap();
    let second=first.clone();
    let first_lesson:serde_json::Value=serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    let exe=env!("CARGO_BIN_EXE_molip-quest");let mut command=std::process::Command::new(exe);
    native_player::configure(&session,&mut command,"lesson-link");
    command.env("MOLIP_PILOT_SELF_TEST","lesson-link").env("MOLIP_LINK_TARGETS",serde_json::json!({"course":course.repository,"first":first_lesson["tasks"][0]["id"],"second":first_lesson["tasks"][0]["id"]}).to_string()).args(["--open",&first.web_url()]);
    let mut primary=command.spawn().unwrap();
    for (stage,url) in [("first",second.app_url()),("second",LessonLink::new(&course.repository,"lsn_wrong_course").unwrap().app_url()),("course",LessonLink::course(&course.repository).unwrap().app_url())]{
        let deadline=std::time::Instant::now()+std::time::Duration::from_secs(50);
        while !session.directory().join(format!("lesson-link-{stage}")).exists(){
            if primary.try_wait().unwrap().is_some(){panic!("primary exited before {stage}: {}",std::fs::read_to_string("target/pilot-native-result.json").unwrap_or_default());}
            if std::time::Instant::now()>deadline{let _=primary.kill();panic!("link stage {stage} timed out");}
            std::thread::sleep(std::time::Duration::from_millis(50));
        }
        let mut command=std::process::Command::new(exe);native_player::configure(&session,&mut command,"lesson-link-forward");command.env_remove("MOLIP_PILOT_SELF_TEST").args(["--open",&url]);
        assert!(native_player::wait(&mut command.spawn().unwrap(),10,"link forward").success());
    }
    let status=native_player::wait(&mut primary,60,"lesson-link");
    let result:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("target/pilot-native-result.json").unwrap()).unwrap();
    std::fs::copy("target/pilot-native-result.json","target/pilot-lesson-link-native-result.json").unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
}
