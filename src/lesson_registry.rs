//! One registration drives authoring, isolated transport, and native validation.
//! Content stays in its authored files; this module owns only their relationships.
#[derive(Debug)]
pub struct RegisteredLesson {
    pub key: &'static str,
    pub revision: &'static str,
    pub pilot: char,
    pub driver: &'static str,
    pub course: &'static str,
    pub lesson: &'static str,
    config: &'static str,
    commands: Option<&'static str>,
}
include!(concat!(env!("OUT_DIR"), "/lesson-registry.rs"));

pub fn find(key:&str)->Option<&'static RegisteredLesson> { LESSONS.iter().find(|lesson|lesson.key==key) }
pub fn by_version(version:char)->Option<&'static RegisteredLesson> { LESSONS.iter().find(|lesson|lesson.pilot==version) }
pub fn by_revision(revision:&str)->Option<&'static RegisteredLesson> { LESSONS.iter().find(|lesson|lesson.revision==revision) }

/// The authored case adjustments are data, so adding a lesson needs no UI branch.
pub fn self_test_script(key:&str)->Option<String> {
    let row=find(if key=="web-preview"{"java-tailwind"}else{key})?;
    if row.driver=="native" {return None;}
    let lesson:serde_json::Value=serde_json::from_str(row.lesson).expect("registered lesson");
    let tasks=&lesson["tasks"];
    let mut config:serde_json::Value=serde_json::from_str(row.config).expect("registered native case");
    if let Some(modifications)=config["modifications"].as_object_mut() {
        for (index,change) in modifications {
            if let Some(replacement)=change.as_object_mut().unwrap().remove("source_replace") {
                let index=index.parse::<usize>().expect("native case index");
                let source=tasks[index]["starter_code"].as_str().expect("native starter");
                change["source"]=source.replace(replacement[0].as_str().unwrap(),replacement[1].as_str().unwrap()).into();
            }
        }
    }
    config["version"]=row.pilot.to_string().into();config["revision"]=row.revision.into();config["tasks"]=tasks.clone();
    if key=="web-preview" {config["webPreviewOnly"]=true.into();}
    let script=if let Some(commands)=row.commands {
        let commands:serde_json::Value=serde_json::from_str(commands).expect("registered student commands");
        config["studentCommands"]=commands["student_commands"].clone();
        config["studentShellCommands"]=commands["student_shell_commands"].clone();
        include_str!("../tools/player-pilot-git-remote.js")
    }else{include_str!("../tools/player-pilot-code-lesson.js")};
    Some(format!("window.mq3LessonPilot={config};{script}"))
}
