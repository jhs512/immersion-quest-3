#![cfg(target_os = "macos")]

#[test]
fn git_terminal_preserves_korean_without_a_login_shell_locale() {
    const NAME:&str="git_terminal_preserves_korean_without_a_login_shell_locale";
    if std::env::var_os("MOLIP_IME_TEST_CHILD").is_none() {
        for locale in ["unset","C"] {
            let mut command=std::process::Command::new(std::env::current_exe().unwrap());
            command.args(["--exact",NAME,"--nocapture"]).env("MOLIP_IME_TEST_CHILD","1")
                .env_remove("LANG").env_remove("LC_ALL").env_remove("LC_CTYPE");
            if locale=="C" {command.env("LANG","C").env("LC_ALL","C");}
            let result=command.output().unwrap();
            assert!(result.status.success(),"{locale}: {}\n{}",String::from_utf8_lossy(&result.stdout),String::from_utf8_lossy(&result.stderr));
        }
        return;
    }
    use std::time::{Duration,Instant};
    let practice=molip_quest::git_practice::GitPractice::new(Default::default()).unwrap();
    std::fs::write(practice.work().join("memo.txt"),"기록\n").unwrap();
    assert!(practice.git(&["add","memo.txt"]).unwrap().success);
    let (mut terminal,mut output)=practice.open_terminal().unwrap();
    let mut seen=String::new();
    let deadline=Instant::now()+Duration::from_secs(10);
    while Instant::now()<deadline && !seen.contains("$ ") {
        while let Ok(bytes)=output.try_recv(){seen.push_str(&String::from_utf8_lossy(&bytes));}
        std::thread::sleep(Duration::from_millis(20));
    }
    assert!(seen.contains("$ "),"No interactive prompt: {seen}");
    for ch in "git commit -m \"첫 기록\"\r".chars() {
        terminal.input(&ch.to_string()).unwrap();
        std::thread::sleep(Duration::from_millis(3));
    }
    let deadline=Instant::now()+Duration::from_secs(5);
    let mut subject=String::new();
    while Instant::now()<deadline {
        while let Ok(bytes)=output.try_recv(){seen.push_str(&String::from_utf8_lossy(&bytes));}
        subject=practice.git(&["log","-1","--format=%s"]).unwrap().stdout;
        if subject.trim()=="첫 기록" {break;}
        std::thread::sleep(Duration::from_millis(40));
    }
    terminal.shutdown().unwrap();
    assert_eq!(subject.trim(),"첫 기록","Interactive terminal lost Korean input: {seen}");
}

#[tokio::test]
async fn c_pointer_exercise_runs_with_the_native_compiler() {
    let source = "#include <stdio.h>\nint main(void) { int a=3; int *p=&a; int **pp=&p; **pp=8; printf(\"%d\\n\",a); return 0; }";
    let task = serde_json::from_value(serde_json::json!({
        "id":"mac-c", "title":"C runtime", "goal":"", "language":"c",
        "starter_code":source, "solution":source, "entry_file":"main.c"
    })).unwrap();
    let result = molip_quest::lesson_runner::run(&task, source, "").await.unwrap();
    assert!(result.success, "{}", result.stderr);
    assert_eq!(result.stdout.trim(), "8");
}

#[tokio::test]
async fn java_static_exercise_runs_on_jdk25() {
    let result = molip_quest::java::run(
        "class Main { static int n=3; Main(){n++;} public static void main(String[] a){new Main();new Main();System.out.println(n);} }", ""
    ).await.unwrap();
    assert!(result.success, "{}", result.stderr);
    assert_eq!(result.stdout.trim(), "5");
}

#[tokio::test]
async fn python_exercise_runs() {
    let result = molip_quest::runner::run_python("print(3 + 4)", "").await.unwrap();
    assert!(result.success, "{}", result.stderr);
    assert_eq!(result.stdout.trim(), "7");
}
