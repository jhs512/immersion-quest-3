//! Replays a redesigned lesson against tests/lesson-cases/<key>.json with the real graders:
//! every starter fails, every solution passes, each narration run gives the recorded output (or the
//! recorded compile/runtime error), every misconception answer is rejected and every listed
//! equivalent answer is accepted. The same cases drive `cargo run --example validate_redesigned_lesson`.
#![allow(dead_code)]
use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};
use std::path::Path;

pub async fn replay(key:&str)->Lesson {
    let root=Path::new(env!("CARGO_MANIFEST_DIR"));
    let spec:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(root.join(format!("tests/lesson-cases/{key}.json"))).unwrap()).unwrap();
    let course=CourseManifest::parse(&std::fs::read_to_string(root.join(spec["course"].as_str().unwrap())).unwrap()).unwrap();
    let raw=std::fs::read_to_string(root.join(spec["lesson"].as_str().unwrap())).unwrap();
    let lesson=Lesson::parse(&raw,&course.lessons[0]).unwrap();
    let expected=spec["expected_outputs"].as_array().unwrap();
    assert_eq!(lesson.tasks.len(),expected.len(),"{key}: cases cover every step");
    for (index,task) in lesson.tasks.iter().enumerate() {
        let label=format!("{key} step {}",index+1);
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"{label} starts unsolved");
        let report=lesson_runner::check(task,&task.solution).await.unwrap();
        assert!(report.passed,"{label} solution: {}",serde_json::to_string(&report).unwrap());
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"{label} patch must select exactly one region");
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "set_code"=>source=action["code"].as_str().unwrap().to_owned(),
                "order_answer" if task.example_order_marker.is_some()=>source=task.example_for_answer(&action["ids"].to_string()).unwrap(),
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).is_some(),"{label} highlight is inside the code");
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    match action["expect_error"].as_str() {
                        Some(error)=>assert!(!result.success&&(result.stderr.contains(error)||result.stdout.contains(error)),"{label} expected {error}: {}",result.stderr),
                        None=>assert!(result.success,"{label} teacher: {}",result.stderr),
                    }
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        let wanted:Vec<String>=expected[index].as_array().unwrap().iter().map(|v|v.as_str().unwrap().to_owned()).collect();
        assert_eq!(outputs,wanted,"{label} narration agrees with actual JDK output");
    }
    for (field,should_pass) in [("reject",false),("accept",true)] {
        for case in spec[field].as_array().into_iter().flatten() {
            let task=&lesson.tasks[case["step"].as_u64().unwrap() as usize-1];
            let mut source=task.solution.clone();
            for pair in case["replacements"].as_array().unwrap() {
                let (before,after)=(pair[0].as_str().unwrap(),pair[1].as_str().unwrap());
                assert_eq!(source.matches(before).count(),1,"{key} {field} patch: {}",case["reason"]);
                source=source.replacen(before,after,1);
            }
            assert_eq!(lesson_runner::check(task,&source).await.unwrap().passed,should_pass,"{key} {field}: {}",case["reason"]);
        }
    }
    lesson
}
