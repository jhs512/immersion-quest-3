//! Run authored lesson cases through the public grader without rebuilding the desktop app.
use molip_quest::{lesson_runner, repository_course::{CourseManifest, Lesson}};
use serde::Deserialize;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{path::PathBuf, time::Instant};

#[derive(Deserialize)]
struct Validation {
    course: PathBuf,
    lesson: PathBuf,
    expected_outputs: Vec<Vec<String>>,
    #[serde(default)]
    reject: Vec<RejectedAnswer>,
}

#[derive(Deserialize)]
struct RejectedAnswer {
    step: usize,
    replacements: Vec<[String; 2]>,
    reason: String,
}

async fn validate(spec: Validation) -> Result<Value, String> {
    let course = CourseManifest::parse(&std::fs::read_to_string(&spec.course).map_err(|e|e.to_string())?)?;
    let raw=std::fs::read(&spec.lesson).map_err(|e|e.to_string())?;
    let source_hash=format!("{:x}",Sha256::digest(&raw));
    let reference=course.lessons.first().ok_or("No lesson reference")?;
    if source_hash!=reference.sha256 {return Err("Lesson bytes do not match the fixed course reference".into())}
    let lesson = Lesson::parse(std::str::from_utf8(&raw).map_err(|e|e.to_string())?,reference)?;
    if lesson.tasks.len() != spec.expected_outputs.len() {return Err("Expected outputs do not cover every step".into())}
    let started = Instant::now();
    let mut steps = Vec::new();
    for (index, task) in lesson.tasks.iter().enumerate() {
        let label = format!("Step {} ({})",index+1,task.title);
        if lesson_runner::check(task,&task.starter_code).await?.passed {return Err(format!("{label}: starter already passes"))}
        let report=lesson_runner::check(task,&task.solution).await?;
        if !report.passed {return Err(format!("{label}: solution failed: {}",serde_json::to_string(&report).unwrap()))}
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().ok_or("Narration action is missing")? {
                "patch_code"=>{
                    let before=action["before"].as_str().ok_or("Missing patch before")?;
                    if source.matches(before).count()!=1 {return Err(format!("{label}: teacher patch is not unique"))}
                    source=source.replacen(before,action["after"].as_str().ok_or("Missing patch after")?,1);
                },
                "set_code"=>source=action["code"].as_str().ok_or("Missing replacement code")?.to_owned(),
                "order_answer" if task.example_order_marker.is_some()=>source=task.example_for_answer(&action["ids"].to_string())?,
                "run"=>{
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}?;
                    if let Some(error)=action["expect_error"].as_str() {
                        if result.success || !result.stderr.contains(error) {return Err(format!("{label}: expected {error}, got {}",result.stderr))}
                    } else if !result.success {return Err(format!("{label}: teacher failed: {}",result.stderr))}
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                "say"|"choose_answer"|"fill_answer"|"fill_fields"|"order_answer"=>{},
                action=>return Err(format!("{label}: this validator cannot replay {action}")),
            }
        }
        if outputs!=spec.expected_outputs[index] {return Err(format!("{label}: expected {:?}, got {outputs:?}",spec.expected_outputs[index]))}
        steps.push(json!({"id":task.id,"teacher_outputs":outputs,"grading_cases":report.cases.len()}));
    }
    for rejected in &spec.reject {
        let task=lesson.tasks.get(rejected.step.checked_sub(1).ok_or("Rejected step numbers start at one")?).ok_or("Rejected step is outside the lesson")?;
        let mut source=task.solution.clone();
        for [before,after] in &rejected.replacements {
            if source.matches(before).count()!=1 {return Err(format!("Rejected answer patch is not unique: {}",rejected.reason))}
            source=source.replacen(before,after,1);
        }
        if lesson_runner::check(task,&source).await?.passed {return Err(format!("Invalid answer accepted: {}",rejected.reason))}
    }
    Ok(json!({"passed":true,"lesson":lesson.id,"revision":lesson.revision,"lesson_sha256":source_hash,"steps":steps,"rejected_answers":spec.reject.len(),"seconds":started.elapsed().as_secs_f64(),"native_ui_verified":false,"voice_listened":false}))
}

#[tokio::main]
async fn main() {
    let args:Vec<_>=std::env::args_os().skip(1).collect();
    if args.len()!=2 {eprintln!("Usage: validate_redesigned_lesson SPEC.json EVIDENCE.json");std::process::exit(2)}
    let result=match std::fs::read(&args[0]).map_err(|e|e.to_string()).and_then(|raw|serde_json::from_slice(&raw).map_err(|e|e.to_string())) {
        Ok(spec)=>validate(spec).await,
        Err(error)=>Err(error),
    };
    let evidence=match &result {Ok(value)=>value.clone(),Err(error)=>json!({"passed":false,"error":error})};
    let output=PathBuf::from(&args[1]);
    if let Some(parent)=output.parent(){std::fs::create_dir_all(parent).unwrap()}
    std::fs::write(output,serde_json::to_vec_pretty(&evidence).unwrap()).unwrap();
    match result {Ok(value)=>println!("{} steps passed in {:.2}s",value["steps"].as_array().unwrap().len(),value["seconds"].as_f64().unwrap()),Err(error)=>{eprintln!("{error}");std::process::exit(1)}}
}
