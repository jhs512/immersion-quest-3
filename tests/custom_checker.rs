use molip_quest::{runner::check_unit, Course};
use serde_json::json;

#[tokio::test]
async fn student_runs_author_checker_and_sees_pass_or_failure() {
    let checker="import runpy,sys\nstudent=runpy.run_path(sys.argv[1])\nassert student['add'](2,3)==5\nprint('통과')\n";
    let course=Course::parse(&json!({"id":"functions","title":"함수","description":"","chapters":[{"id":"c","title":"c","units":[{"id":"u","title":"함수","content":"","checker":checker}]}]}).to_string()).unwrap();
    let unit = &course.chapters[0].units[0];
    let passed = check_unit(unit, "def add(a,b):\n    return a+b\n")
        .await
        .unwrap();
    assert!(passed.passed);
    assert_eq!(passed.cases[0].stdout, "통과\n");
    let failed = check_unit(unit, "def add(a,b):\n    return a-b\n")
        .await
        .unwrap();
    assert!(!failed.passed);
    assert_eq!(failed.cases[0].state, "wrong_answer");
    let mut broken = unit.clone();
    broken.checker = Some("this is not valid python !!!".into());
    let error = check_unit(&broken, "").await.unwrap();
    assert!(!error.passed);
    assert_eq!(error.cases[0].state, "checker_error");
}
