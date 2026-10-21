use molip_quest::{git_practice::GitPractice,repository_course::{CourseManifest,Lesson}};

fn snapshot(practice:&GitPractice)->Vec<String> {
    [vec!["rev-parse","HEAD"],vec!["rev-parse","MERGE_HEAD"],vec!["ls-files","--stage"],vec!["diff"],vec!["symbolic-ref","HEAD"]].iter().map(|args|practice.git(args).unwrap().stdout).collect()
}

#[tokio::test]
async fn advanced_branch_steps_preserve_history_resolve_real_conflicts_and_reset_independently() {
    let advanced_course=CourseManifest::parse(include_str!("fixtures/player-pilot/굳/course.json")).unwrap();
    let advanced=Lesson::parse(include_str!("../courses/redesigned/git-branch-advanced.json"),&advanced_course.lessons[0]).unwrap();
    assert_eq!(advanced.tasks.len(),5);
    let tasks=advanced.tasks.iter().collect::<Vec<_>>();
    let solutions:Vec<Vec<Vec<&str>>>=vec![
        vec![vec!["merge","--no-edit","feature"]],vec![],vec![],
        vec![vec!["restore","--source=feature","--worktree","--","guide.txt"],vec!["add","guide.txt"]],vec![vec!["commit","--no-edit"]],
    ];
    for (index,task) in tasks.into_iter().enumerate() {
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
                if index==1 {
                    let merged=teacher.git(&["show","HEAD:guide.txt"]).unwrap().stdout;
                    assert!(merged.starts_with("안내: 메모를 남겨요\n"));assert!(merged.ends_with("문의: 상담 창구\n"));
                }
                if index==2 {assert_eq!(teacher.git(&["diff","--name-only","--diff-filter=U"]).unwrap().stdout,"guide.txt\n");}
            }else{assert!(teacher.check_exercise().unwrap().passed,"teacher step {}",index+1);}
            assert_eq!(snapshot(&student),before,"teacher changed student repository");
            for args in &solutions[index]{assert!(student.git(args).unwrap().success,"student step {}",index+1);}
            if task.interaction.is_none(){assert!(student.check_exercise().unwrap().passed,"student step {}",index+1);}
            std::fs::write(student.work().join("leftover.txt"),"leftover").unwrap();
            student.reset().unwrap();assert!(!student.work().join("leftover.txt").exists());
        }
    }
}

#[test]
fn published_branch_goals_accept_checkout_commit_all_and_equivalent_conflict_resolution() {
    let basic_course=CourseManifest::parse(include_str!("fixtures/player-pilot/l/course.json")).unwrap();
    let basic=Lesson::parse(include_str!("../courses/redesigned/git-branch.json"),&basic_course.lessons[0]).unwrap();
    for (index,commands) in [
        (3,vec![vec!["checkout","feature"]]),
        (5,vec![vec!["commit","-am","my feature message"]]),
        (7,vec![vec!["merge","--ff-only","feature"]]),
    ] {
        let practice=GitPractice::new(basic.tasks[index].git_terminal.clone().unwrap().demonstration()).unwrap();
        assert!(!practice.check_exercise().unwrap().passed);
        for args in commands{assert!(practice.git(&args).unwrap().success,"{args:?}");}
        assert!(practice.check_exercise().unwrap().passed,"step {}",index+1);
    }
    let advanced_course=CourseManifest::parse(include_str!("fixtures/player-pilot/굳/course.json")).unwrap();
    let advanced=Lesson::parse(include_str!("../courses/redesigned/git-branch-advanced.json"),&advanced_course.lessons[0]).unwrap();
    let practice=GitPractice::new(advanced.tasks[3].git_terminal.clone().unwrap()).unwrap();
    assert!(practice.git(&["checkout","--theirs","--","guide.txt"]).unwrap().success);
    assert!(!practice.check_exercise().unwrap().passed,"choosing a file does not stage conflict resolution");
    assert!(practice.git(&["add","-A"]).unwrap().success);
    assert!(practice.check_exercise().unwrap().passed);
}
