use molip_quest::{
    git_practice::{GitExercise, GitPractice},
    setup_terminal::{prepare_practice_exit, shutdown_practices},
};

#[test]
fn update_shutdown_stops_all_practice_shells_without_resetting_their_work() {
    let first = GitPractice::new(GitExercise::default()).unwrap();
    let second = GitPractice::new(GitExercise::default()).unwrap();
    let mut sessions = Vec::new();
    for practice in [&first, &second] {
        std::fs::write(practice.work().join("student.txt"), "keep my answer").unwrap();
        let (mut shell, mut output) = practice.open_terminal().unwrap();
        let mut seen = String::new();
        let mut reports = 0;
        let mut sent = false;
        let deadline = std::time::Instant::now() + std::time::Duration::from_secs(30);
        while std::time::Instant::now() < deadline {
            while let Ok(bytes) = output.try_recv() {
                seen.push_str(&String::from_utf8_lossy(&bytes));
                let count = seen.matches("\x1b[6n").count();
                while reports < count {
                    shell.input("\x1b[1;1R").unwrap();
                    reports += 1;
                }
            }
            if !sent && (!cfg!(windows) || seen.contains("PS ")) {
                let command = if cfg!(windows) {
                    "Set-Content ready.txt ready;while (-not (Test-Path go.txt)) {Start-Sleep -Milliseconds 50};Set-Content leaked.txt leaked\r"
                } else {
                    "printf ready > ready.txt;while [ ! -f go.txt ];do sleep 0.05;done;printf leaked > leaked.txt\r"
                };
                shell.input(command).unwrap();
                sent = true;
            }
            if practice.work().join("ready.txt").exists() {
                break;
            }
            std::thread::sleep(std::time::Duration::from_millis(20));
        }
        assert!(
            practice.work().join("ready.txt").exists(),
            "shell did not start: {seen}"
        );
        sessions.push((shell, output));
    }
    let (continue_tx, continue_rx) = std::sync::mpsc::channel();
    let late = std::thread::spawn(move || {
        let practice = GitPractice::new(GitExercise::default()).unwrap();
        continue_rx.recv().unwrap();
        practice.open_terminal().is_err()
    });
    let exit_guard = prepare_practice_exit().unwrap();
    continue_tx.send(()).unwrap();
    assert!(
        late.join().unwrap(),
        "in-flight initialization must not admit a shell during exit"
    );
    shutdown_practices().unwrap(); // Repeated pre-exit cleanup is harmless.
    for practice in [&first, &second] {
        std::fs::write(practice.work().join("go.txt"), "go").unwrap();
    }
    std::thread::sleep(std::time::Duration::from_secs(1));
    for practice in [&first, &second] {
        assert!(
            !practice.work().join("leaked.txt").exists(),
            "practice continued running after update cleanup"
        );
    }
    for (mut shell, _output) in sessions {
        shell.shutdown().unwrap();
    }
    drop(exit_guard); // A failed installer handoff can resume normal practice creation.
    let (mut reopened, _) = first.open_terminal().unwrap();
    reopened.shutdown().unwrap();
    for practice in [&first, &second] {
        assert_eq!(
            std::fs::read_to_string(practice.work().join("student.txt")).unwrap(),
            "keep my answer"
        );
        assert_eq!(
            practice
                .git(&["branch", "--show-current"])
                .unwrap()
                .stdout
                .trim(),
            "main"
        );
    }
}
