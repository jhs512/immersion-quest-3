#![cfg(target_os = "macos")]

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
