use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};
use std::collections::{BTreeMap,HashSet};
use std::path::{Path,PathBuf};

// Every lesson that a certificate course lists, or MQ3_CERT_LESSONS=a,b under MQ3_CERT_ROOT for drafts.
fn lessons(root:&Path)->Vec<(String,PathBuf)> {
    if let Ok(ids)=std::env::var("MQ3_CERT_LESSONS") {
        return ids.split(',').filter(|id|!id.is_empty()).map(|id|(id.to_string(),root.join(id).join("lesson.json"))).collect();
    }
    let mut found=vec![];
    let mut course_ids=vec![];
    for course in ["aice-associate","engineer-practical"] {
        let manifest=CourseManifest::parse(&std::fs::read_to_string(root.join(course).join("course.json")).unwrap()).unwrap();
        course_ids.push(manifest.lessons.iter().map(|l|l.repository.clone()).collect::<HashSet<_>>());
        for lesson in manifest.lessons {
            let own=root.join(&lesson.id).join("lesson.json");
            let path=if own.exists(){own}else{root.parent().unwrap().join("certification-pilots").join(course).join("lesson.json")};
            let raw=std::fs::read(&path).unwrap();
            use sha2::{Digest,Sha256};
            assert_eq!(format!("{:x}",Sha256::digest(&raw)),lesson.sha256,"{} must match the course pin",lesson.id);
            found.push((lesson.id,path));
        }
    }
    assert!(course_ids[0].is_disjoint(&course_ids[1]),"certificate lessons must be independent");
    found
}

async fn prove(id:String,path:PathBuf)->usize {
    let lesson:Lesson=serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    lesson.validate().unwrap();
    let mistakes:BTreeMap<String,Vec<String>>=std::fs::read_to_string(path.with_file_name("mistakes.json")).ok()
        .map(|text|serde_json::from_str(&text).unwrap()).unwrap_or_default();
    let mut rejected=0;
    for task in lesson.tasks {
        let answer=lesson_runner::check(&task,&task.solution).await.unwrap();
        assert!(answer.passed,"{id}/{} {}",task.id,serde_json::to_string(&answer).unwrap());
        assert!(!lesson_runner::check(&task,&task.starter_code).await.unwrap().passed,"{id}/{} starter passed",task.id);
        for (index,source) in mistakes.get(&task.id).into_iter().flatten().enumerate() {
            assert!(!lesson_runner::check(&task,source).await.unwrap().passed,"{id}/{} mistake {} passed",task.id,index+1);
            rejected+=1;
        }
        // Narration runs with the first sample input, as tools/principles_course/common.py records it.
        let sample=task.tests.first().map(|case|case.input.clone()).unwrap_or_default();
        let mut source=String::new();
        for step in &task.narration {
            match step["action"].as_str().unwrap() {
                "set_code"=>source=step["code"].as_str().unwrap().into(),
                "patch_code"=>source=source.replacen(step["before"].as_str().unwrap(),step["after"].as_str().unwrap(),1),
                "run"=>{
                    let result=lesson_runner::run(&task,&source,&sample).await.unwrap();
                    assert_eq!(result.success,!step["expected_failure"].as_bool().unwrap_or(false),"{id}/{} {}",task.id,result.stderr);
                },
                _=>{},
            }
        }
        assert_eq!(source,task.solution);
    }
    println!("PASS {id}: solutions pass, starters fail, {rejected} representative mistakes rejected, narration replays");
    rejected
}

#[tokio::test(flavor="multi_thread",worker_threads=4)]
#[ignore="requires generated independent foundations, Python and JDK"]
async fn independent_foundations_run_grade_and_replay_from_the_beginning() {
    let root=std::env::var("MQ3_CERT_ROOT").map(PathBuf::from)
        .unwrap_or_else(|_|Path::new(env!("CARGO_MANIFEST_DIR")).join("target/certification-foundations"));
    let jobs:Vec<_>=lessons(&root).into_iter().map(|(id,path)|tokio::spawn(prove(id,path))).collect();
    for job in jobs {job.await.unwrap();}
}
