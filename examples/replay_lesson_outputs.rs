//! Authoring aid: replay every step's demonstration through the real grader and print the outputs
//! each `run` produced, then check the `accept` answers (other valid edits) of a lesson-cases file.
//! It never writes the lesson. `validate_redesigned_lesson` stays the evidence-producing check.
//!
//! Usage: replay_lesson_outputs LESSON.json [CASES.json]
use molip_quest::{lesson_runner, repository_course::Lesson};
use serde::Deserialize;
use serde_json::json;

#[derive(Deserialize)]
struct Cases { #[serde(default)] accept: Vec<Answer>, #[serde(default)] reject: Vec<Answer> }
#[derive(Deserialize)]
struct Answer { step: usize, replacements: Vec<[String; 2]>, reason: String }

fn patched(source:&str,answer:&Answer)->Result<String,String> {
    let mut source=source.to_owned();
    for [before,after] in &answer.replacements {
        if source.matches(before.as_str()).count()!=1 {return Err(format!("patch is not unique: {}",answer.reason))}
        source=source.replacen(before.as_str(),after,1);
    }
    Ok(source)
}

#[tokio::main]
async fn main() {
    let args:Vec<String>=std::env::args().skip(1).collect();
    let raw=std::fs::read_to_string(&args[0]).expect("lesson file");
    let lesson:Lesson=serde_json::from_str(&raw).expect("lesson json");
    lesson.validate().expect("lesson validates");
    let mut steps=Vec::new();
    for (index,task) in lesson.tasks.iter().enumerate() {
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut input=task.tests.first().map(|case|case.input.clone()).unwrap_or_default();
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap_or("") {
                "patch_code"=>{let before=action["before"].as_str().unwrap();assert_eq!(source.matches(before).count(),1,"step {}: patch not unique: {before}",index+1);source=source.replacen(before,action["after"].as_str().unwrap(),1);},
                "set_code"=>source=action["code"].as_str().unwrap().to_owned(),
                "set_input"=>input=action["value"].as_str().unwrap().to_owned(),
                "run"=>{
                    let result=lesson_runner::run(task,&source,&input).await;
                    match result {
                        Ok(result)=>outputs.push(json!({"success":result.success,"stdout":result.stdout.trim_end(),"stderr":result.stderr.trim_end()})),
                        Err(error)=>outputs.push(json!({"error":error})),
                    }
                },
                _=>{}
            }
        }
        let starter=lesson_runner::check(task,&task.starter_code).await.map(|r|r.passed);
        let solution=lesson_runner::check(task,&task.solution).await;
        steps.push(json!({"step":index+1,"title":task.title,"outputs":outputs,"starter_passes":starter,
            "solution":solution.as_ref().map(|r|json!({"passed":r.passed,"cases":r.cases})).unwrap_or_else(|e|json!({"error":e}))}));
    }
    let mut answers=Vec::new();
    if let Some(path)=args.get(1) {
        let cases:Cases=serde_json::from_str(&std::fs::read_to_string(path).expect("cases")).expect("cases json");
        for (kind,list) in [("accept",&cases.accept),("reject",&cases.reject)] {
            for answer in list {
                let task=&lesson.tasks[answer.step-1];
                let verdict=match patched(&task.solution,answer) {
                    Ok(source)=>lesson_runner::check(task,&source).await.map(|r|json!({"passed":r.passed,"cases":r.cases})).unwrap_or_else(|e|json!({"error":e})),
                    Err(error)=>json!({"error":error}),
                };
                answers.push(json!({"kind":kind,"step":answer.step,"reason":answer.reason,"verdict":verdict}));
            }
        }
    }
    println!("{}",serde_json::to_string_pretty(&json!({"steps":steps,"answers":answers})).unwrap());
}
