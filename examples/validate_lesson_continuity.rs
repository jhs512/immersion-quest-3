//! Check the normal learner path, keeping the same task's DB between both runs.
//! This complements the isolated grading proof; it does not change app execution.
use molip_quest::{docker_lab::LessonSession,lesson_runner,repository_course::{Lesson,TaskLanguage}};
use serde_json::json;
use sha2::{Digest,Sha256};

#[tokio::main]
async fn main() {
    let args:Vec<String>=std::env::args().skip(1).collect();
    let raw=std::fs::read(&args[0]).expect("lesson file");
    let lesson:Lesson=serde_json::from_slice(&raw).expect("lesson json");
    lesson.validate().expect("valid lesson");
    let selected=args.get(2).map(|s|s.parse::<usize>().expect("optional step"));
    let session=LessonSession::new();
    let mut rows=vec![];
    for(index,task)in lesson.tasks.iter().enumerate() {
        if selected.is_some_and(|n|n!=index+1){continue}
        let test=task.tests.first().expect("first test");
        let mut results=vec![];
        for source in [&task.starter_code,&task.solution] {
            let r=if task.language==TaskLanguage::Docker {session.run(task,source,&test.input).await}
                else {lesson_runner::run(task,source,&test.input).await};
            results.push(match r {Ok(r)=>json!({"success":r.success,"stdout":r.stdout.trim_end(),"stderr":r.stderr.trim_end()}),Err(e)=>json!({"error":e})});
        }
        let expected=serde_json::to_value(test).expect("test serialize");
        let expected=expected.get("expected").or_else(||expected.get("output")).and_then(|v|v.as_str()).expect("expected output");
        let passed=results[1]["success"]==true&&results[1]["stdout"]==expected.trim_end();
        eprintln!("{} {}: {}",index+1,task.title,passed);
        rows.push(json!({"step":index+1,"title":task.title,"passed":passed,"expected":expected,"runs":results}));
    }
    session.close();session.wait_closed().await;
    let passed=rows.iter().all(|r|r["passed"]==true);
    let result=json!({"passed":passed,"lesson_sha256":format!("{:x}",Sha256::digest(&raw)),"mode":"normal run: starter then solution; same task session retained","steps":rows});
    std::fs::write(&args[1],serde_json::to_vec_pretty(&result).unwrap()).expect("write proof");
    assert!(passed,"normal starter to solution path failed");
}
