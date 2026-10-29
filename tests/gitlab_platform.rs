use molip_quest::git_practice::{GitExercise,GitPractice,GitPracticeStore};
use std::time::{Duration,Instant};

fn exercise(stage:&str)->GitExercise {
    serde_json::from_value(serde_json::json!({"gitlab":{"stage":stage},"files":{"memo.txt":"기본 메모\n"},"workspace_group":"gitlab-mr","workspace_revision":"gitlab-1"})).unwrap()
}

fn terminal(practice:&GitPractice,commands:&[&str])->String {
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    let mut text=String::new();let mut dsr=0;let mut sent=0;let mut command_baseline=practice.shell_completions().unwrap().len();
    let deadline=Instant::now()+Duration::from_secs(180);
    while Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){text.push_str(&String::from_utf8_lossy(&bytes));}
        let count=text.matches("\x1b[6n").count();while dsr<count{terminal.input("\x1b[1;1R").unwrap();dsr+=1;}
        let rows=practice.shell_completions().unwrap();
        if sent>0&&rows.len()>command_baseline {
            assert!(rows.last().unwrap().success,"command failed: {}\n{text}",commands[sent-1]);
            command_baseline=rows.len();
            if sent==commands.len(){terminal.shutdown().unwrap();return text;}
        }
        if (sent==0&&text.contains("$ "))||(sent>0&&rows.len()==command_baseline&&rows.last().is_some_and(|r|r.command==commands[sent-1])) {
            if sent<commands.len(){terminal.input(&format!("{}\r",commands[sent])).unwrap();sent+=1;}
        }
        std::thread::sleep(Duration::from_millis(30));
    }
    terminal.shutdown().unwrap();panic!("GitLab terminal timeout: {text}")
}

#[test]
fn gitlab_schema_and_opening_do_not_touch_any_hosted_account(){
    let practice=GitPractice::new(exercise("repository")).unwrap();
    assert!(!practice.root().join("remote.git").exists());
    assert!(!practice.git(&["remote","get-url","origin"]).unwrap().success);
    assert!(!practice.environment().iter().any(|(key,_)|key=="GH_CONFIG_DIR"));
    assert!(exercise("repository").validate().is_ok());
}

#[test]
fn gitlab_content_cannot_be_misread_as_a_legacy_no_goal_exercise(){
    use molip_quest::repository_course::{CourseManifest,Lesson};
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/갓/course.json")).unwrap();
    let raw=include_str!("../courses/redesigned/gitlab-ci.json");
    let lesson=Lesson::parse(raw,&course.lessons[0]).unwrap();
    assert_eq!(lesson.schema_version,3,"older binaries reject this version rather than ignoring the new grader");
    let mut downgraded:serde_json::Value=serde_json::from_str(raw).unwrap();downgraded["schema_version"]=2.into();
    assert!(serde_json::from_value::<Lesson>(downgraded).unwrap().validate().is_err());
    assert!(lesson.tasks.iter().all(|t|t.git_terminal.as_ref().unwrap().has_goal()));
}

#[test]
#[ignore="Starts owned local GitLab and writes only local exercise projects; no GitHub account is used"]
fn actual_gitlab_mr_lifecycle_passes_each_stage_and_rejects_unmerged_final(){
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    let steps=[("repository",vec!["glab repo create \"$MQ3_REPO\" --private --defaultBranch main --skipGitInit","git remote add origin \"$MQ3_GITLAB/$MQ3_NAMESPACE/$MQ3_REPO.git\""]),
        ("main_pushed",vec!["git push -u origin main"]),
        ("branch",vec!["git switch -c feature"]),
        ("committed",vec!["printf '함께 읽는 메모\\n' > memo.txt","git add memo.txt","git commit -m '메모 안내 개선'"]),
        ("feature_pushed",vec!["git push -u origin feature"]),
        ("merge_request",vec!["glab mr create --source-branch feature --target-branch main --title '메모 안내 개선' --description '메모 문구를 바꿨어요.' --yes"]),
        ("reviewed",vec!["glab mr diff"]),
        ("merged",vec!["glab mr merge --yes","git switch main","git pull","cat memo.txt"])];
    for (stage,commands) in steps {
        let practice=store.open("native-gitlab-validation",exercise(stage)).unwrap();
        terminal(&practice,&commands);
        let report=practice.check_exercise().unwrap();assert!(report.passed,"{stage}: {}",serde_json::to_string(&report).unwrap());
        if stage=="reviewed" {let final_practice=store.open("native-gitlab-validation",exercise("final")).unwrap();assert!(!final_practice.check_exercise().unwrap().passed);}
    }
    let final_practice=store.open("native-gitlab-validation",exercise("final")).unwrap();
    assert!(final_practice.check_exercise().unwrap().passed);
}

fn await_pipeline(practice:&GitPractice)->molip_quest::runner::TestReport {
    let deadline=Instant::now()+Duration::from_secs(300);
    loop {
        match practice.check_exercise() {
            Ok(report)=>{
                if report.cases.iter().any(|c|c.input=="현재 커밋의 실제 파이프라인"&&matches!(c.stdout.as_str(),"success"|"failed"|"canceled")){return report;}
            },Err(error)=>println!("Waiting for local pipeline: {error}"),
        }
        assert!(Instant::now()<deadline,"Local Docker runner pipeline timeout");
        std::thread::sleep(Duration::from_secs(2));
    }
}

#[test]
#[ignore="Executes the authored CI course through the real local GitLab Docker runner"]
fn every_authored_pipeline_rejects_its_starter_and_accepts_actual_fixed_jobs_and_artifacts(){
    use molip_quest::repository_course::{CourseManifest,Lesson};
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/갓/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/gitlab-ci.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),10);
    for task in &lesson.tasks {
        println!("CI step: {}",task.title);
        let practice=GitPractice::new(task.git_terminal.clone().unwrap()).unwrap();
        if task.git_terminal.as_ref().unwrap().gitlab.is_none(){
            terminal(&practice,&["cat check.sh","sh check.sh"]);
            assert!(practice.check_exercise().unwrap().passed);
            continue;
        }
        practice.prepare_gitlab().unwrap();
        let starter=await_pipeline(&practice);
        assert!(!starter.passed,"Starter must not solve {}",task.title);
        for action in &task.narration {
            if action["action"]=="patch_code" {
                let file=action["file"].as_str().unwrap();let text=practice.read_editable(file).unwrap();
                let before=action["before"].as_str().unwrap();let after=action["after"].as_str().unwrap();
                assert_eq!(text.matches(before).count(),1);
                practice.save_editable(file,&text.replacen(before,after,1)).unwrap();
            }
        }
        if task.git_terminal.as_ref().unwrap().gitlab.as_ref().unwrap().pipeline_ref=="feature" {assert!(practice.git(&["switch","-c","feature"]).unwrap().success);}
        for args in [vec!["add","."],vec!["commit","-m","Fix CI configuration"],vec!["push","-u","origin","HEAD"]] {let result=practice.git(&args).unwrap();assert!(result.success,"{}",result.stderr);}
        let result=await_pipeline(&practice);
        assert!(result.passed,"{}: {}",task.title,serde_json::to_string(&result).unwrap());
        // The learner command the lesson gives: --wait returns to the prompt (--live ends in an action menu).
        if task.title=="검사 명령을 CI 작업에서 실행하세요" {let text=terminal(&practice,&["glab ci status --wait"]);assert!(text.contains("success")&&!text.contains("Choose an action"),"{text}");}
        // A correct but uncommitted configuration cannot replace the actual commit being graded.
        println!("Verified: {}",task.title);
    }
}

#[test]
#[ignore="Runs the published MR lesson's own commands through the real local GitLab; no GitHub account is used"]
fn authored_mr_lesson_commands_pass_their_own_graders_in_order(){
    use molip_quest::repository_course::{CourseManifest,Lesson};
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/풀/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/github-pr.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),9);
    let root=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(root.path()).unwrap();
    for task in &lesson.tasks {
        let exercise=task.git_terminal.clone().unwrap();
        // The player's scope: one workspace per workspace_group, so the final starts apart from steps 1-8.
        let scope=exercise.workspace_scope(&format!("authored-gitlab-mr:{}",exercise.workspace_group));
        let practice=store.open(&scope,exercise).unwrap();
        // Exactly the commands the learner is told to run, in the authored order.
        let commands:Vec<&str>=task.solution.lines().filter(|l|!l.trim().is_empty()).collect();
        if task.id==lesson.tasks.last().unwrap().id {assert!(!practice.check_exercise().map(|r|r.passed).unwrap_or(false),"final must not pass before work");}
        let transcript=terminal(&practice,&commands);
        let report=practice.check_exercise().unwrap();
        assert!(report.passed,"{}: {}\n{transcript}",task.title,serde_json::to_string(&report).unwrap());
        println!("Verified authored MR step: {}",task.title);
    }
}
