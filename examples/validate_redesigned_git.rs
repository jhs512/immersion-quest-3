//! Replay the remote lesson in real independent repositories, then reset each attempt.
use molip_quest::{git_practice::GitPractice,repository_course::{CourseManifest,Lesson}};
use sha2::{Digest,Sha256};
use std::time::Instant;
fn main()->Result<(),Box<dyn std::error::Error>> {
    let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let raw=std::fs::read(root.join("courses/redesigned/git-remote.json"))?;
    let course=CourseManifest::parse(&std::fs::read_to_string(root.join("tests/fixtures/player-pilot/어/course.json"))?)?;
    let lesson=Lesson::parse(std::str::from_utf8(&raw)?,&course.lessons[0])?;
    let commands:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(root.join("tests/fixtures/player-pilot/어/student-commands.json"))?)?;
    let commands=commands["student_commands"].as_array().ok_or("Missing student commands")?;
    assert_eq!(commands.len(),lesson.tasks.len());
    let observations:Vec<Vec<Option<&str>>>=vec![vec![Some(""),Some("Local guide")],vec![None,Some("main")],vec![Some(""),Some("base"),Some("shared")],vec![Some(""),Some("base"),Some("shared")],vec![Some(""),None,Some("shared")],vec![None],vec![None,Some(""),Some("")],vec![None,Some("base"),Some("3")]];
    let started=Instant::now();let mut results=vec![];
    for (index,task) in lesson.tasks.iter().enumerate() {
        let exercise=task.git_terminal.clone().ok_or("Missing Git exercise")?;
        let mut student=GitPractice::new(exercise.clone())?;
        for _ in 0..2 {
            let before=student.git(&["rev-parse","HEAD"])?.stdout;
            if task.interaction.is_none(){assert!(!grade(&student,task)?.passed,"already passes step {}",index+1);}
            let teacher=GitPractice::new(exercise.clone())?;let mut outputs=vec![];
            for action in &task.narration {
                if action["action"]=="git_command" {
                    let args=action["args"].as_array().ok_or("Missing args")?.iter().map(|v|v.as_str().unwrap()).collect::<Vec<_>>();
                    let result=teacher.git(&args)?;assert!(result.success,"step {}: {}",index+1,result.stderr);outputs.push(result.stdout.trim_end().to_string());
                }
            }
            assert_eq!(outputs.len(),observations[index].len());
            for (output,expected) in outputs.iter().zip(&observations[index]) {if let Some(expected)=expected {assert_eq!(output,expected,"teacher output step {}",index+1);}}
            assert_eq!(student.git(&["rev-parse","HEAD"])?.stdout,before,"teacher changed student HEAD");
            if let Some(interaction)=&task.interaction {assert!(!interaction.check("")?.passed);assert!(interaction.check(&task.solution)?.passed);}
            else {
                assert!(grade(&teacher,task)?.passed,"teacher goal step {}",index+1);
                for args in commands[index].as_array().ok_or("Missing step commands")? {
                    let args=args.as_array().unwrap().iter().map(|v|v.as_str().unwrap()).collect::<Vec<_>>();assert!(student.git(&args)?.success);
                }
                assert!(grade(&student,task)?.passed,"student goal step {}",index+1);
            }
            std::fs::write(student.work().join("leftover.txt"),"leftover")?;
            student.reset()?;assert!(!student.work().join("leftover.txt").exists());
        }
        results.push(serde_json::json!({"id":task.id,"independent_replays":2,"passed":true}));
    }
    let report=serde_json::json!({"passed":true,"source_sha256":format!("{:x}",Sha256::digest(raw)),"seconds":started.elapsed().as_secs_f64(),"steps":results,"native_ui_verified":false,"voice_listened":false});
    let path=root.join("target/player-pilot-audit/git-remote/public-cases.json");std::fs::create_dir_all(path.parent().unwrap())?;std::fs::write(path,serde_json::to_vec_pretty(&report)?)?;
    println!("{} real Git steps passed in {:.2}s",results.len(),started.elapsed().as_secs_f64());Ok(())
}
fn grade(practice:&GitPractice,task:&molip_quest::repository_course::Task)->Result<molip_quest::runner::TestReport,String> {
    if let Some(checks)=&task.git_checks {practice.check(checks)} else {practice.check_exercise()}
}
