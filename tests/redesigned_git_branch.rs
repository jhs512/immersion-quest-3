use molip_quest::{git_practice::GitPractice,repository_course::{CourseManifest,Lesson}};

fn snapshot(practice:&GitPractice)->Vec<String> {
    [vec!["rev-parse","HEAD"],vec!["rev-parse","MERGE_HEAD"],vec!["ls-files","--stage"],vec!["diff"],vec!["symbolic-ref","HEAD"]].iter().map(|args|practice.git(args).unwrap().stdout).collect()
}

#[tokio::test]
async fn nine_branch_steps_preserve_history_resolve_real_conflicts_and_reset_independently() {
    let path=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("courses/redesigned/git-branch.json");
    let raw=std::fs::read_to_string(path).unwrap();
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/l/course.json")).unwrap();
    let lesson=Lesson::parse(&raw,&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),9);
    let solutions:Vec<Vec<Vec<&str>>>=vec![
        vec![vec!["branch","feature"]],vec![vec!["switch","feature"]],vec![vec!["add","guide.txt"],vec!["commit","-m","feature record"]],
        vec![vec!["merge","feature"]],vec![vec!["merge","--no-edit","feature"]],vec![],vec![],
        vec![vec!["restore","--source=feature","--worktree","--","guide.txt"],vec!["add","guide.txt"]],vec![vec!["commit","--no-edit"]],
    ];
    for (index,task) in lesson.tasks.iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();
        let mut student=GitPractice::new(exercise.clone()).unwrap();
        for _ in 0..2 {
            let before=snapshot(&student);
            if task.interaction.is_none(){assert!(!student.check_exercise().unwrap().passed,"step {} starts unsolved",index+1);}
            let teacher=GitPractice::new(exercise.clone()).unwrap();
            for action in &task.narration {
                if action["action"]=="git_command" {
                    let args=action["args"].as_array().unwrap().iter().map(|v|v.as_str().unwrap()).collect::<Vec<_>>();
                    let result=teacher.git(&args).unwrap();assert!(result.success,"step {}: {:?}: {}",index+1,args,result.stderr);
                }
            }
            if let Some(interaction)=&task.interaction {
                assert!(!interaction.check("").unwrap().passed);
                assert!(molip_quest::lesson_runner::check(task,&task.solution).await.unwrap().passed);
                if index==5 {
                    let merged=teacher.git(&["show","HEAD:guide.txt"]).unwrap().stdout;
                    assert!(merged.starts_with("안내: 메모를 남겨요\n"));assert!(merged.ends_with("문의: 상담 창구\n"));
                }
                if index==6 {assert_eq!(teacher.git(&["diff","--name-only","--diff-filter=U"]).unwrap().stdout,"guide.txt\n");}
            }else{assert!(teacher.check_exercise().unwrap().passed,"teacher step {}",index+1);}
            assert_eq!(snapshot(&student),before,"teacher changed student repository");
            for args in &solutions[index]{assert!(student.git(args).unwrap().success,"student step {}",index+1);}
            if task.interaction.is_none(){assert!(student.check_exercise().unwrap().passed,"student step {}",index+1);}
            std::fs::write(student.work().join("leftover.txt"),"leftover").unwrap();
            student.reset().unwrap();assert!(!student.work().join("leftover.txt").exists());
        }
    }
}
