//! The Docker CLI lesson in the real practice terminal (PTY Bash) against the real Docker engine.
//! Run: cargo test --test docker_cli_terminal -- --ignored --nocapture --test-threads=1
#![cfg(not(target_os="android"))]
use molip_quest::{docker_lab::LessonSession,git_practice::{GitPractice,GitPracticeStore},repository_course::{CourseManifest,Lesson}};

#[path="../examples/support/docker_terminal.rs"] mod support;
use support::{Terminal,step,docker_goal};

fn docker(args:&[&str])->(bool,String) {
    let output=std::process::Command::new("docker").args(args).output().unwrap();
    (output.status.success(),String::from_utf8_lossy(&output.stdout).trim().to_owned())
}
fn lesson()->Lesson {
    let manifest=CourseManifest::parse(include_str!("fixtures/player-pilot/리/course.json")).unwrap();
    Lesson::parse(include_str!("../courses/redesigned/docker-image-container.json"),&manifest.lessons[0]).unwrap()
}
/// What each step's real Docker output must show. Engine IDs, ports and times are not fixed.
fn markers(index:usize,command:&str,container:&str)->Vec<String> {
    let id=regex::Regex::new(r"(?m)^[0-9a-f]{64}$").unwrap();
    match (index,command) {
        (0,_)=>vec!["1.28-alpine".into(),"Status:".into()],
        (1,_)=>vec![],
        // Docker 29 lists IMAGE ID DISK USAGE…; older engines REPOSITORY TAG…. Both name the image.
        (_,"docker images")=>vec!["IMAGE".into(),"nginx".into(),"1.28-alpine".into()],
        (_,"docker ps")|(_,"docker ps -a")=>vec!["CONTAINER ID".into(),"NAMES".into(),container.into()],
        (3,_)=>vec!["Configuration complete".into()],
        (4,_)=>vec!["hello".into()],
        _=>{let _=id;vec![container.into()]}
    }
}

#[test]
#[ignore="Needs a running Docker engine and Git Bash on Windows"]
fn docker_cli_steps_run_in_the_real_terminal_and_grade_the_real_engine() {
    let lesson=lesson();
    let cli=&lesson.tasks[..8];
    assert!(cli.iter().all(|t|t.git_terminal.as_ref().is_some_and(|e|e.docker.is_some())&&t.starter_code.is_empty()&&t.files.is_empty()),"the CLI steps are terminal steps without commands.sh");
    assert!(lesson.tasks[8..].iter().all(|t|t.git_terminal.is_none()));
    let unique=molip_quest::issue_progress::new_id().to_ascii_lowercase().chars().filter(char::is_ascii_alphanumeric).take(8).collect::<String>();
    // A developer's own container: visible in the real ps table, never changed by the lesson.
    let other=format!("mq3-test-developer-{unique}");
    assert!(docker(&["run","-d","--name",&other,"nginx:1.28-alpine"]).0);
    // Remove exactly this test's own container even when an assertion fails.
    struct Remove(String);
    impl Drop for Remove {fn drop(&mut self){let _=docker(&["rm","-f",&self.0]);}}
    let _remove=Remove(other.clone());
    let session=LessonSession::new();
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    let base="user:course:lesson:full:docker-cli";
    let mut root=None;let mut learner_project=None;let mut demo_project=None;let mut container_id=None;
    for (index,task) in cli.iter().enumerate() {
        let exercise=task.git_terminal.clone().unwrap();
        let practice=store.open(&exercise.workspace_scope(base),exercise.clone()).unwrap();
        if let Some(root)=&root {assert_eq!(practice.root(),root,"the lesson's steps share one practice folder");}
        root=Some(practice.root().to_path_buf());
        let lab=session.terminal(false,&step(task),&docker_goal(task)).unwrap();
        if let Some(project)=&learner_project {assert_eq!(&lab.project,project,"one learner project for the whole lesson");}
        learner_project=Some(lab.project.clone());
        // In order, every start state is the previous step's result: nothing is prepared or recreated.
        assert_eq!(lab.prepared,None,"step {}: the chained start needs no preparation",index+1);
        let mut terminal=Terminal::open(&practice,&lab).unwrap();
        assert!(!practice.check_exercise().unwrap().passed,"step {}: nothing typed yet must not pass",index+1);
        for command in task.solution.lines() {
            let printed=terminal.enter(&practice,command,true).unwrap();
            for marker in markers(index,command,&lab.container) {
                assert!(printed.contains(&marker),"step {} {command}: real output lacks {marker:?}:\n{printed}",index+1);
            }
            if index==1 {assert!(regex::Regex::new(r"(?m)^[0-9a-f]{64}\s*$").unwrap().is_match(&printed),"run prints the real container ID:\n{printed}");}
            if command=="docker ps" {assert!(printed.contains(&other),"the real ps table also lists the developer's container:\n{printed}");}
        }
        let report=practice.check_exercise().unwrap();
        assert!(report.passed,"step {}: {}",index+1,serde_json::to_string_pretty(&report).unwrap());
        let id=docker(&["inspect","-f","{{.Id}}",&lab.container]);
        if (1..7).contains(&index) {
            if let Some(previous)=&container_id {assert_eq!(&id.1,previous,"step {}: the same container is kept",index+1);}
            container_id=Some(id.1.clone());
        }
        if index==2 {
            // Reopening a step keeps the learner's real state: no preparation, the same container.
            terminal.close().unwrap();
            let again=session.terminal(false,&step(task),&docker_goal(task)).unwrap();
            assert_eq!(again.prepared,None);
            assert_eq!(docker(&["inspect","-f","{{.Id}}",&lab.container]).1,id.1);
            let mut terminal=Terminal::open(&practice,&again).unwrap();
            // The guard keeps the developer's resources and fixed ports out of the lesson.
            for refused in [format!("docker stop {other}"),format!("docker rm -f {other}"),"docker run -d --name extra -p 8080:80 nginx:1.28-alpine".into(),
                "docker run -d --name extra -v /:/host nginx:1.28-alpine".into(),"docker image rm nginx:1.28-alpine".into(),"docker rmi nginx:1.28-alpine".into(),"docker system prune -f".into(),"docker volume prune -f".into()] {
                let printed=terminal.enter(&practice,&refused,false).unwrap();
                assert!(printed.contains("MQ 실습 터미널:"),"{refused}: {printed}");
            }
            assert_eq!(docker(&["inspect","-f","{{.State.Status}}",&other]).1,"running");
            assert!(!docker(&["inspect","extra"]).0,"no container was created by a refused run");
            assert!(docker(&["image","inspect","nginx:1.28-alpine"]).0);
            assert!(practice.check_exercise().unwrap().passed,"refused commands do not undo the learner's work");
            terminal.close().unwrap();
        } else {terminal.close().unwrap();}
        // The narration plays in its own project, from the exact start state, without touching the learner's.
        let teacher=GitPractice::new(task.git_terminal.clone().unwrap().demonstration()).unwrap();
        let demo=session.terminal(true,&step(task),&docker_goal(task)).unwrap();
        assert_ne!(demo.project,lab.project);
        demo_project=Some(demo.project.clone());
        let before=docker(&["inspect","-f","{{.Id}} {{.State.Status}}",&lab.container]);
        let mut shown=Terminal::open(&teacher,&demo).unwrap();
        for action in &task.narration {
            if action["action"]=="bash_command" {
                let command=action["command"].as_str().unwrap();
                let printed=shown.enter(&teacher,command,action["fails"]!=true).unwrap();
                if action["fails"]==true {assert!(!printed.trim().is_empty(),"the narration shows the real error of {command}");}
            }
        }
        let report=teacher.check_exercise().unwrap();
        assert!(report.passed,"narration of step {} reaches the goal: {}",index+1,serde_json::to_string_pretty(&report).unwrap());
        shown.close().unwrap();
        assert_eq!(docker(&["inspect","-f","{{.Id}} {{.State.Status}}",&lab.container]),before,"the narration left the learner's container alone");
        eprintln!("step {} passed: {}",index+1,task.title);
    }
    // 초기화 restores one step's exact start state in the learner's project.
    let start=&cli[6];
    session.reset_terminal(&step(start)).unwrap();
    let restored=session.terminal(false,&step(start),&docker_goal(start)).unwrap();
    assert!(restored.prepared.is_some());
    assert_eq!(docker(&["inspect","-f","{{.State.Status}}",&restored.container]).1,"exited");
    // Leaving the lesson removes only what this lesson owns.
    let projects=[learner_project.unwrap(),demo_project.unwrap()];
    let runtime=tokio::runtime::Builder::new_current_thread().enable_all().build().unwrap();
    session.close();runtime.block_on(session.wait_closed());
    for project in projects {
        assert!(docker(&["ps","-aq","--filter",&format!("label=io.mq3.project={project}")]).1.is_empty(),"lesson containers are removed");
    }
    assert!(docker(&["ps","-aq","--filter","label=io.mq3.project","--filter",&format!("name={}",restored.container)]).1.is_empty());
    assert_eq!(docker(&["inspect","-f","{{.State.Status}}",&other]).1,"running","the developer's container is untouched");
    assert!(docker(&["image","inspect","nginx:1.28-alpine"]).0,"the shared image stays");
}

/// 관리자 자동 풀이: the plan replays the narration's typed commands in the learner's own
/// terminal (assets/layout/auto-run.js solveTerminal), and only the real grader decides.
#[test]
#[ignore="Needs a running Docker engine and Git Bash on Windows"]
fn auto_run_types_the_narration_commands_in_the_learner_terminal_and_the_grader_decides() {
    use molip_quest::auto_review::{self,Plan};
    let lesson=lesson();
    let session=LessonSession::new();
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    for (index,task) in lesson.tasks[..8].iter().enumerate() {
        let Ok(Plan::Terminal{actions,answer:None})=auto_review::plan(task) else{panic!("{} is a terminal step",task.title)};
        assert!(!actions.is_empty()&&actions.iter().all(|a|a["action"]=="bash_command"));
        // The run initializes the shared workspace once, at its first step, like the 초기화 button.
        if index==0 {session.reset_terminal(&step(task)).unwrap();}
        let exercise=task.git_terminal.clone().unwrap();
        let practice=if index==0 {store.reset_step(&exercise.workspace_scope("user:course:lesson:full:docker-cli"),exercise,&task.id).unwrap()}
            else {store.open(&exercise.workspace_scope("user:course:lesson:full:docker-cli"),exercise).unwrap()};
        let lab=session.terminal(false,&step(task),&docker_goal(task)).unwrap();
        let mut terminal=Terminal::open(&practice,&lab).unwrap();
        for action in &actions {
            let command=action["command"].as_str().unwrap();
            let printed=terminal.enter(&practice,command,action["fails"]!=true).unwrap();
            assert!(printed.lines().count()>1,"{command} shows its real output before the next command:
{printed}");
        }
        let report=practice.check_exercise().unwrap();
        assert!(report.passed,"auto-run step {}: {}",index+1,serde_json::to_string_pretty(&report).unwrap());
        terminal.close().unwrap();
    }
    let runtime=tokio::runtime::Builder::new_current_thread().enable_all().build().unwrap();
    session.close();runtime.block_on(session.wait_closed());
}

#[test]
#[ignore="Needs a running Docker engine and Git Bash on Windows"]
fn a_missing_start_state_is_prepared_once_and_a_wrong_command_does_not_pass() {
    let lesson=lesson();
    let session=LessonSession::new();
    let directory=tempfile::tempdir().unwrap();let store=GitPracticeStore::new(directory.path()).unwrap();
    // Open the logs step first: the app prepares a running container once and says so.
    let task=&lesson.tasks[3];
    let exercise=task.git_terminal.clone().unwrap();
    let practice=store.open(&exercise.workspace_scope("user:course:lesson:full:docker-cli"),exercise).unwrap();
    let lab=session.terminal(false,&step(task),&docker_goal(task)).unwrap();
    assert!(lab.prepared.as_deref().is_some_and(|note|note.contains("만들어 실행")),"{:?}",lab.prepared);
    assert_eq!(docker(&["inspect","-f","{{.State.Status}}|{{index .Config.Labels \"io.mq3.project\"}}",&lab.container]).1,format!("running|{}",lab.project));
    let mut terminal=Terminal::open(&practice,&lab).unwrap();
    // A different command with real output is not the step's command.
    terminal.enter(&practice,"docker ps",true).unwrap();
    assert!(!practice.check_exercise().unwrap().passed);
    let printed=terminal.enter(&practice,&format!("docker logs {}",lab.container),true).unwrap();
    assert!(printed.contains("Configuration complete"),"{printed}");
    assert!(practice.check_exercise().unwrap().passed,"the real name is the same target as $BOX");
    terminal.close().unwrap();
    assert_eq!(session.terminal(false,&step(task),&docker_goal(task)).unwrap().prepared,None,"prepared only once");
    let runtime=tokio::runtime::Builder::new_current_thread().enable_all().build().unwrap();
    session.close();runtime.block_on(session.wait_closed());
    assert!(!docker(&["inspect",&lab.container]).0);
}
