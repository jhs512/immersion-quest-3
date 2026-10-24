#![cfg(all(feature="desktop",debug_assertions))]
//! 관리자 자동 풀이 in the real app on the isolated validation transport: a learner without push
//! permission, then an administrator running Bash -> Java. Afterwards the uploaded history (the
//! validation transport's issue comments) must hold exactly the real passes.
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;
use molip_quest::issue_progress::{self,EventKind,LearningEvent};
use std::collections::{HashMap,HashSet};

fn launch(session:&molip_quest::pilot_session::PilotSession,phase:&str,seconds:u64)->serde_json::Value{
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(session,&mut command,phase);
    command.env("MOLIP_PILOT_SELF_TEST","auto-review").env("MOLIP_AUTO_REVIEW_PHASE",phase);
    let status=native_player::wait(&mut command.spawn().unwrap(),seconds,phase);
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::write(format!("target/pilot-auto-review-{phase}.json"),&raw).unwrap();
    let _=std::fs::copy(session.directory().join(format!("{phase}.log")),format!("target/pilot-auto-review-{phase}.log"));
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{phase}: {result}");
    result
}

#[test]
#[ignore="Requires an interactive desktop"]
fn administrator_runs_lessons_in_order_until_esc_and_only_real_passes_are_recorded(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let initial=serde_json::json!({"corrupted":false,"version":molip_quest::pilot_source::AUTO_CHAIN_VERSION.to_string(),"issue":null,"comments":[]});
    std::fs::write(session.directory().join("pilot-remote.json"),serde_json::to_vec(&initial).unwrap()).unwrap();
    let _=std::fs::remove_file(session.directory().join("pilot-course-reviewer"));
    launch(&session,"student",200);
    std::fs::write(session.directory().join("pilot-course-reviewer"),"").unwrap();
    let admin=launch(&session,"admin",960);
    println!("{}",serde_json::to_string_pretty(&admin["checked"]).unwrap());

    let remote:serde_json::Value=serde_json::from_slice(&std::fs::read(session.directory().join("pilot-remote.json")).unwrap()).unwrap();
    let events:Vec<LearningEvent>=remote["comments"].as_array().unwrap().iter().flat_map(|c|issue_progress::parse_events(c["body"].as_str().unwrap())).collect();
    // Evidence for the record checks below: every uploaded event, in upload order.
    let summary:Vec<String>=events.iter().map(|e|format!("{} {:?} {} {} passed={} {}",&e.key.lesson_id[..12],e.kind,e.task_id.as_deref().unwrap_or("-"),&e.round[..8.min(e.round.len())],e.passed,e.at)).collect();
    std::fs::write("target/pilot-auto-review-remote-events.txt",format!("issue: {}
{}",remote["issue"]["body"].as_str().unwrap_or("").lines().last().unwrap_or(""),summary.join("
"))).unwrap();
    let ids:HashSet<_>=events.iter().map(|e|e.id.clone()).collect();
    assert_eq!(ids.len(),events.len(),"no event is uploaded twice");
    let bash=Lesson::bash();let java=Lesson::java();
    let passes=|lesson:&Lesson,step:usize|events.iter().filter(|e|e.kind==EventKind::Attempt&&e.passed&&e.key.lesson_id==lesson.id&&e.task_id.as_deref()==Some(lesson.tasks[step-1].as_str())).count();
    let failures=events.iter().filter(|e|e.kind==EventKind::Attempt&&!e.passed).count();
    // Step 1 by hand (student); 23 at the stopped lesson change and again after its reset; 22.
    assert_eq!(passes(&bash,1),1,"the learner's own pass is kept");
    assert_eq!(passes(&bash,22),1);
    assert_eq!(passes(&bash,23),2,"two real solves of step 23, each recorded once");
    // Java 1 before Esc, 8 at the course end; 2 (Esc) and 4 (manual move) never passed.
    assert_eq!((passes(&java,1),passes(&java,2),passes(&java,4),passes(&java,8)),(1,0,0,1));
    assert_eq!(failures,0,"the run submits only a solved step");
    let rounds:HashMap<&str,HashSet<&str>>=events.iter().fold(HashMap::new(),|mut m,e|{m.entry(e.key.lesson_id.as_str()).or_default().insert(e.round.as_str());m});
    assert_eq!(rounds.len(),2,"records belong to the two lessons only");
    let explained=events.iter().filter(|e|e.kind==EventKind::ExplanationViewed).count();
    assert!(explained>=6,"each solved step's narration was played ({explained})");
}

struct Lesson { id:String, tasks:Vec<String> }
impl Lesson {
    fn from(raw:&str)->Self{let v:serde_json::Value=serde_json::from_str(raw).unwrap();Self{id:v["id"].as_str().unwrap().into(),tasks:v["tasks"].as_array().unwrap().iter().map(|t|t["id"].as_str().unwrap().into()).collect()}}
    fn bash()->Self{Self::from(include_str!("../courses/redesigned/bash-basics.json"))}
    fn java()->Self{Self::from(include_str!("../courses/redesigned/java-launch.json"))}
}
