//! Run authored lesson cases through the public grader without rebuilding the desktop app.
use molip_quest::{lesson_runner, repository_course::{CourseManifest, Lesson}};
use serde::Deserialize;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{path::PathBuf, time::Instant};
#[path="support/docker_terminal.rs"] mod docker_terminal;

#[derive(Deserialize)]
struct Validation {
    course: PathBuf,
    lesson: PathBuf,
    expected_outputs: Vec<Vec<ExpectedOutput>>,
    #[serde(default)]
    expected_images: Option<Vec<Vec<usize>>>,
    #[serde(default)]
    reject: Vec<RejectedAnswer>,
    /// Other correct answers (a different but valid edit) that the grader must accept.
    #[serde(default)]
    accept: Vec<RejectedAnswer>,
    /// Replay only the lesson's last step (a final challenge appended to a lesson whose earlier steps
    /// have no lesson-case file). expected_outputs then holds that one step; reject/accept still use
    /// lesson step numbers.
    #[serde(default)]
    only_last: bool,
}

#[derive(Deserialize,Debug)]
#[serde(untagged)]
enum ExpectedOutput {
    Literal(String),
    Junit { junit_summary: JunitSummary },
    /// Docker IDs, ports and times vary. Assert native output without replacing it.
    Pattern { pattern: String },
}
#[derive(Deserialize,Debug)]
struct JunitSummary { found:usize, successful:usize, failed:usize }
impl ExpectedOutput {
    fn matches(&self,actual:&str)->bool {
        match self {
            Self::Literal(expected)=>actual==expected,
            Self::Pattern{pattern}=>regex::Regex::new(pattern).is_ok_and(|re|re.is_match(actual)),
            Self::Junit{junit_summary:expected}=>expected.found>0
                &&expected.successful.checked_add(expected.failed)==Some(expected.found)
                &&[("tests found",expected.found),("tests successful",expected.successful),("tests failed",expected.failed)].iter().all(|(label,count)| {
                    let matches:Vec<_>=actual.lines().filter_map(|line| {
                        let body=line.trim().strip_prefix('[')?.strip_suffix(']')?.trim();
                        let (number,name)=body.split_once(char::is_whitespace)?;
                        if name.trim()!=*label {return None;}
                        Some(number.parse::<usize>().ok())
                    }).collect();
                    matches==vec![Some(*count)]
                }),
        }
    }
}

#[derive(Deserialize)]
struct RejectedAnswer {
    step: usize,
    replacements: Vec<[String; 2]>,
    reason: String,
}

async fn validate(spec: Validation) -> Result<Value, String> {
    let session=std::env::var_os("MQ3_VALIDATE_SQL_SESSION").map(|_|molip_quest::docker_lab::LessonSession::new());
    let result=validate_with_session(spec,session.as_ref()).await;
    if let Some(session)=session {session.close();session.wait_closed().await;}
    result
}

async fn validate_with_session(spec: Validation,session:Option<&molip_quest::docker_lab::LessonSession>) -> Result<Value, String> {
    let course = CourseManifest::parse(&std::fs::read_to_string(&spec.course).map_err(|e|e.to_string())?)?;
    let raw=std::fs::read(&spec.lesson).map_err(|e|e.to_string())?;
    let source_hash=format!("{:x}",Sha256::digest(&raw));
    let reference=course.lessons.first().ok_or("No lesson reference")?;
    if source_hash!=reference.sha256 {return Err("Lesson bytes do not match the fixed course reference".into())}
    let lesson = Lesson::parse(std::str::from_utf8(&raw).map_err(|e|e.to_string())?,reference)?;
    if session.is_some() && !lesson.tasks.iter().all(|task|task.entry_file.ends_with(".sql")&&task.files.contains_key("before.sql")) {
        return Err("SQL session validation requires SQL fixture tasks".into())
    }
    let first=if spec.only_last {lesson.tasks.len()-1} else {0};
    if lesson.tasks.len()-first != spec.expected_outputs.len() {return Err("Expected outputs do not cover every step".into())}
    if spec.expected_images.as_ref().is_some_and(|images| images.len()!=lesson.tasks.len()-first) {return Err("Expected images do not cover every step".into())}
    let started = Instant::now();
    let mut steps = Vec::new();
    // Docker CLI steps are typed in the real practice terminal, in lesson order, in one lesson session.
    let terminals=lesson.tasks.iter().any(|t|t.git_terminal.as_ref().is_some_and(|e|e.docker.is_some()))
        .then(||Ok::<_,String>((molip_quest::docker_lab::LessonSession::new(),tempfile::tempdir().map_err(|e|e.to_string())?))).transpose()?;
    for (index, task) in lesson.tasks.iter().enumerate().skip(first) {
        let label = format!("Step {} ({})",index+1,task.title);
        let case_index=index-first;
        if let (Some((session,folder)),true)=(terminals.as_ref(),task.git_terminal.as_ref().is_some_and(|e|e.docker.is_some())) {
            let (task,session,folder)=(task.clone(),session.clone(),folder.path().to_path_buf());
            let (outputs,report)=tokio::task::spawn_blocking(move||docker_terminal::replay(&session,&molip_quest::git_practice::GitPracticeStore::new(&folder)?,"validate:docker-cli",&task)).await.map_err(|e|e.to_string())?.map_err(|e|format!("{label}: {e}"))?;
            let expected=&spec.expected_outputs[case_index];
            if outputs.len()!=expected.len()||!expected.iter().zip(&outputs).all(|(expected,actual)|expected.matches(actual)) {return Err(format!("{label}: expected {:?}, got {outputs:?}",expected))}
            let task=&lesson.tasks[index];
            let mut counterexamples=0;
            if docker_terminal::is_compose(task) {
                // The same commands typed with the start files, or with a recorded wrong edit, must
                // fail; another correct edit must pass. Each attempt starts from the step's 초기화.
                let variants:Vec<(Option<Vec<[String;2]>>,bool,String)>=std::iter::once((None,false,"start files".to_owned()))
                    .chain(spec.reject.iter().filter(|r|r.step==index+1).map(|r|(Some(r.replacements.clone()),false,r.reason.clone())))
                    .chain(spec.accept.iter().filter(|r|r.step==index+1).map(|r|(Some(r.replacements.clone()),true,r.reason.clone()))).collect();
                for (replacements,pass,reason) in variants {
                    let files=match &replacements {Some(r)=>Some(docker_terminal::goal_files(task,r).map_err(|e|format!("{label}: {e}"))?),None=>None};
                    let (task,session,folder)=(task.clone(),terminals.as_ref().unwrap().0.clone(),terminals.as_ref().unwrap().1.path().to_path_buf());
                    let report=tokio::task::spawn_blocking(move||docker_terminal::attempt(&session,&molip_quest::git_practice::GitPracticeStore::new(&folder)?,"validate:docker-attempt",&task,files.as_deref())).await.map_err(|e|e.to_string())?.map_err(|e|format!("{label}: {e}"))?;
                    if report.passed!=pass {return Err(format!("{label}: {reason}: expected passed={pass}: {}",serde_json::to_string(&report).unwrap()))}
                    counterexamples+=1;
                    eprintln!("{label}: {} as expected: {reason}",if pass{"passed"}else{"failed"});
                }
            }
            steps.push(json!({"id":task.id,"terminal":true,"teacher_outputs":outputs,"grading_cases":report.cases.len(),"terminal_attempts":counterexamples}));
            eprintln!("{label}: passed in the real terminal");
            continue;
        }
        let starter=if let Some(session)=session {lesson_runner::check_in_lesson(task,&task.starter_code,session).await}else{lesson_runner::check(task,&task.starter_code).await}?;
        if starter.passed {return Err(format!("{label}: starter already passes"))}
        let report=if let Some(session)=session {lesson_runner::check_in_lesson(task,&task.solution,session).await}else{lesson_runner::check(task,&task.solution).await}?;
        if !report.passed {return Err(format!("{label}: solution failed: {}",serde_json::to_string(&report).unwrap()))}
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        // The player starts a demonstration with the first test's input, as the learner would.
        let mut input=task.tests.first().map(|case|case.input.clone()).unwrap_or_default();
        let mut outputs=Vec::new();
        let mut images=Vec::new();
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
                    let result=if let Some(session)=session {session.demonstrate(task,&source,&input).await}else if task.has_runnable_example(){lesson_runner::run_example(task,&source,&input).await}else{lesson_runner::run(task,&source,&input).await}?;
                    if let Some(error)=action["expect_error"].as_str() {
                        if result.success || !(result.stderr.contains(error)||result.stdout.contains(error)) {return Err(format!("{label}: expected {error}, got {}{}",result.stderr,result.stdout))}
                    } else if !result.success {return Err(format!("{label}: teacher failed: {}",result.stderr))}
                    outputs.push(result.stdout.trim_end().to_owned());
                    images.push(result.artifacts.iter().filter(|artifact|matches!(artifact,molip_quest::runner::Artifact::Image{..})).count());
                },
                "set_input"=>input=action["value"].as_str().ok_or("Missing input value")?.to_owned(),
                // A demonstration never submits: the player's runExplanation filters submit out.
                // web_action acts on the live preview; web_checks in the grader cover clicks and input.
                "say"|"choose_answer"|"fill_answer"|"fill_fields"|"order_answer"|"submit"|"web_action"=>{},
                action=>return Err(format!("{label}: this validator cannot replay {action}")),
            }
        }
        let expected=&spec.expected_outputs[case_index];
        if outputs.len()!=expected.len()||!expected.iter().zip(&outputs).all(|(expected,actual)|expected.matches(actual)) {return Err(format!("{label}: expected {:?}, got {outputs:?}",expected))}
        if let Some(expected)=&spec.expected_images {
            if images!=expected[case_index] {return Err(format!("{label}: expected image counts {:?}, got {images:?}",expected[case_index]))}
        }
        steps.push(json!({"id":task.id,"teacher_outputs":outputs,"teacher_images":images,"grading_cases":report.cases.len()}));
        eprintln!("{label}: passed");
    }
    for rejected in &spec.reject {
        let task=lesson.tasks.get(rejected.step.checked_sub(1).ok_or("Rejected step numbers start at one")?).ok_or("Rejected step is outside the lesson")?;
        if docker_terminal::is_compose(task) {continue}
        let mut source=task.solution.clone();
        for [before,after] in &rejected.replacements {
            if source.matches(before).count()!=1 {return Err(format!("Rejected answer patch is not unique: {}",rejected.reason))}
            source=source.replacen(before,after,1);
        }
        let report=if let Some(session)=session {lesson_runner::check_in_lesson(task,&source,session).await}else{lesson_runner::check(task,&source).await}?;
        if report.passed {return Err(format!("Invalid answer accepted: {}",rejected.reason))}
    }
    for accepted in &spec.accept {
        let task=lesson.tasks.get(accepted.step.checked_sub(1).ok_or("Accepted step numbers start at one")?).ok_or("Accepted step is outside the lesson")?;
        if docker_terminal::is_compose(task) {continue}
        let mut source=task.solution.clone();
        for [before,after] in &accepted.replacements {
            if source.matches(before).count()!=1 {return Err(format!("Accepted answer patch is not unique: {}",accepted.reason))}
            source=source.replacen(before,after,1);
        }
        let report=if let Some(session)=session {lesson_runner::check_in_lesson(task,&source,session).await}else{lesson_runner::check(task,&source).await}?;
        if !report.passed {return Err(format!("Valid answer rejected: {}: {}",accepted.reason,serde_json::to_string(&report).unwrap()))}
    }
    if let Some((session,_))=&terminals {session.close();session.wait_closed().await;}
    Ok(json!({"passed":true,"lesson":lesson.id,"revision":lesson.revision,"lesson_sha256":source_hash,"steps":steps,"rejected_answers":spec.reject.len(),"accepted_answers":spec.accept.len(),"seconds":started.elapsed().as_secs_f64(),"native_ui_verified":false,"voice_listened":false}))
}

#[cfg(test)]
mod output_assertion_tests {
    use super::ExpectedOutput;
    #[test]
    fn junit_counts_are_required_but_elapsed_time_is_not_fixed() {
        let expected=ExpectedOutput::Junit{junit_summary:super::JunitSummary{found:1,successful:1,failed:0}};
        assert!(expected.matches("after 172 ms\n[   1 tests found   ]\n[1 tests successful]\n[0 tests failed]"));
        assert!(!expected.matches("[1 tests found]\n[0 tests successful]\n[1 tests failed]"));
        assert!(!expected.matches("[11 tests found]\n[11 tests successful]\n[10 tests failed]"));
        assert!(!expected.matches("[1 tests found]\n[1 tests successful]\n[10 tests failed]"));
        assert!(!expected.matches("[0 tests found]\n[1 tests successful]\n[0 tests failed]"));
        assert!(!expected.matches("[1 tests found]\n[1 tests successful]\n[0 tests failed]\n[0 tests failed]"));
        assert!(!ExpectedOutput::Literal("exact".into()).matches("exact plus"));
    }

    #[test]
    fn native_docker_output_must_have_real_table_columns() {
        let expected=ExpectedOutput::Pattern{pattern:"(?s)^CONTAINER ID\\s+IMAGE.*PORTS.*NAMES.*nginx".into()};
        assert!(expected.matches("CONTAINER ID   IMAGE   PORTS   NAMES\nabc nginx:1.28-alpine 127.0.0.1:49152->80/tcp mq3lab-test-nginx"));
        assert!(!expected.matches("실행 중인 실습 컨테이너: 1"));
        assert!(!ExpectedOutput::Pattern{pattern:"[".into()}.matches("anything"));
    }
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
