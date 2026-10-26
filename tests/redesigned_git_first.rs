use molip_quest::{git_practice::GitPractice, repository_course::Lesson};

#[tokio::test]
async fn six_first_git_steps_grade_real_work_and_replay_teacher_commands_without_changing_student_state() {
    let path=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("courses/redesigned/git-first.json");
    let raw=std::fs::read_to_string(path).unwrap();
    let course=molip_quest::repository_course::CourseManifest::parse(include_str!("fixtures/player-pilot/k/course.json")).unwrap();
    let lesson=Lesson::parse(&raw,&course.lessons[0]).unwrap();
    lesson.validate().unwrap();
    assert_eq!(lesson.tasks.len(),6);
    let root=tempfile::tempdir().unwrap();
    let store=molip_quest::git_practice::GitPracticeStore::new(root.path()).unwrap();
    let solutions=vec![
        vec![vec!["init"],vec!["echo","첫 메모"],vec!["status"]],
        vec![vec!["add","memo.txt"]],
        vec![vec!["commit","-m","첫 기록"]],
        vec![vec!["echo","둘째 메모"],vec!["diff"],vec!["show","HEAD:memo.txt"]],
        vec![vec!["add","memo.txt"],vec!["echo","셋째 메모"],vec!["diff","--cached"],vec!["diff"]],
        vec![vec!["add","memo.txt"],vec!["commit","-m","메모 갱신"]],
    ];
    let mut previous_root=None;
    let mut previous_file=None;
    for (index,task) in lesson.tasks.iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();
        assert_eq!(exercise.workspace_group,"first-git-repository");
        let scope=exercise.workspace_scope(&exercise.workspace_group);
        let student=store.open(&scope,exercise.clone()).unwrap();
        if let Some(path)=&previous_root {assert_eq!(student.root(),path);}
        assert_eq!(std::fs::read_to_string(student.work().join("memo.txt")).ok(),previous_file,"navigation must not change files");
        if index==0 {assert!(!student.work().join(".git").exists());}
        else {assert!(student.work().join(".git").exists());}
        let before=student.git(&["status","--porcelain"]).unwrap().stdout;
        if index>0 {
            assert!(!task.goal.contains("`git init`\n"));
            assert!(!task.narration.iter().any(|a|a["action"]=="git_command"&&a["args"][0]=="init"),"only step one demonstrates init");
        }
        if index==1 {
            let commands:Vec<&serde_json::Value>=task.narration.iter().filter(|a|a["action"]=="git_command").map(|a|&a["args"]).collect();
            assert_eq!(commands,vec![&serde_json::json!(["status"]),&serde_json::json!(["add","memo.txt"]),&serde_json::json!(["status"])]);
        }
        let teacher=GitPractice::new(exercise.demonstration()).unwrap();
        assert_eq!(std::fs::read_to_string(teacher.work().join("memo.txt")).ok(),previous_file,"demo must start where the previous student step ended");
        for args in [vec!["show",":memo.txt"],vec!["show","HEAD:memo.txt"],vec!["rev-list","--count","HEAD"]] {
            let actual=teacher.git(&args).unwrap();let expected=student.git(&args).unwrap();
            assert_eq!((actual.success,actual.stdout),(expected.success,expected.stdout),"demo starting state: {args:?}");
        }
        for action in &task.narration {
            if action["action"]=="write_memo" {run(&teacher,&["echo",action["content"].as_str().unwrap()]);}
            else if action["action"]=="bash_command" {
                shell(&teacher,action["command"].as_str().unwrap());
            }
            else if action["action"]=="git_command" {
                let args:Vec<&str>=action["args"].as_array().unwrap().iter().map(|s|s.as_str().unwrap()).collect();
                if index==1 && args==["status"] {
                    let output=teacher.git(&args).unwrap();
                    let staged=teacher.git(&["show",":memo.txt"]).unwrap().success;
                    assert!(output.stdout.contains(if staged{"Changes to be committed"}else{"Untracked files"}));
                }else{run(&teacher,&args);}
            }
        }
        if task.interaction.is_none() {assert!(teacher.check_exercise().unwrap().passed,"teacher step {}",index+1);}
        assert_eq!(student.git(&["status","--porcelain"]).unwrap().stdout,before,"teacher changed student state");
        for args in &solutions[index] {run(&student,args);}
        if task.interaction.is_none() {assert!(student.check_exercise().unwrap().passed,"student step {}",index+1);}
        else {assert!(molip_quest::lesson_runner::check(task,&task.solution).await.unwrap().passed);}
        previous_root=Some(student.root().to_path_buf());
        previous_file=std::fs::read_to_string(student.work().join("memo.txt")).ok();
        if index==5 {assert_eq!(student.git(&["rev-list","--count","HEAD"]).unwrap().stdout.trim(),"2");}
    }
}

fn run(practice:&GitPractice,args:&[&str]) {
    if args[0]=="echo" {
        #[cfg(windows)] let bash=molip_quest::setup_terminal::git_bash_executable().unwrap();
        #[cfg(not(windows))] let bash=std::path::PathBuf::from("/bin/bash");
        let output=std::process::Command::new(bash).args(["--noprofile","--norc","-c",&format!("echo \"{}\" > memo.txt",args[1])]).current_dir(practice.work()).envs(practice.environment()).output().unwrap();
        assert!(output.status.success(),"{}",String::from_utf8_lossy(&output.stderr));
    }else{assert!(practice.git(args).unwrap().success,"{args:?}");}
}

fn shell(practice:&GitPractice,text:&str) {
    #[cfg(windows)] let bash=molip_quest::setup_terminal::git_bash_executable().unwrap();
    #[cfg(not(windows))] let bash=std::path::PathBuf::from("/bin/bash");
    let mut paths=vec![bash.parent().unwrap().to_path_buf()];
    paths.extend(std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()));
    let output=std::process::Command::new(bash).args(["--noprofile","--norc","-c",text]).current_dir(practice.work()).envs(practice.environment()).env("PATH",std::env::join_paths(paths).unwrap()).output().unwrap();
    assert!(output.status.success(),"{}",String::from_utf8_lossy(&output.stderr));
}
