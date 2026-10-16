use molip_quest::{
    curriculum::{ActivityKind, QuestionKind},
    learning_store::LearningStore,
    runner, Course, Language, DEFAULT_COURSE,
};
use std::collections::HashMap;

#[tokio::test]
async fn default_java_course_executes_grades_and_persists_every_mission() {
    let course = Course::parse(DEFAULT_COURSE).unwrap();
    assert_eq!(course.id, "immersion-quest-3-java25-v1");
    assert_eq!(course.total_units(), 12);
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("progress.sqlite3");
    let mut store = LearningStore::open(&path).unwrap();
    let mut cases = 0;
    for unit in course.chapters.iter().flat_map(|c| &c.units) {
        for activity in &unit.activities {
            let progress = activity.progress_unit(unit);
            match &activity.kind {
                ActivityKind::Coding { problem } => {
                    assert_eq!(problem.language.name(), "java");
                    assert!(problem.solution.contains("//"));
                    let report = runner::check_unit(problem, &problem.solution)
                        .await
                        .unwrap();
                    assert!(
                        report.passed,
                        "{}: {}",
                        problem.id,
                        serde_json::to_string(&report).unwrap()
                    );
                    cases += report.cases.len();
                    store
                        .save(&course.id, &progress, &problem.solution, &report)
                        .unwrap();
                }
                ActivityKind::Concept { check, .. } => {
                    let QuestionKind::ShortAnswer { accepted } = &check.kind else {
                        panic!()
                    };
                    let answers = HashMap::from([(check.id.clone(), accepted[0].clone())]);
                    assert!(
                        store
                            .save_quiz(&course.id, &progress, std::slice::from_ref(check), &answers)
                            .unwrap()
                            .passed
                    );
                }
                ActivityKind::Quiz { questions } => {
                    let answers = questions
                        .iter()
                        .map(|q| {
                            (
                                q.id.clone(),
                                match &q.kind {
                                    QuestionKind::Choice { correct, .. } => correct.to_string(),
                                    QuestionKind::ShortAnswer { accepted } => accepted[0].clone(),
                                    _ => panic!(),
                                },
                            )
                        })
                        .collect();
                    assert!(
                        store
                            .save_quiz(&course.id, &progress, questions, &answers)
                            .unwrap()
                            .passed
                    );
                }
                _ => panic!(),
            }
            for action in &activity.narration {
                assert!(matches!(
                    action["action"].as_str().unwrap(),
                    "say" | "set_code" | "patch_code" | "run" | "submit" | "answer_quiz"
                ));
                if action["action"] == "say" {
                    assert!(action["text"].as_str().is_some_and(|s| !s.is_empty()));
                }
            }
        }
    }
    assert!(cases >= 50);
    drop(store);
    let reopened = LearningStore::open(&path).unwrap();
    assert_eq!(reopened.completed_items(&course).unwrap().len(), 39);
    let legacy = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
    assert!(reopened.completed_items(&legacy).unwrap().is_empty());
    for unit in legacy.chapters.iter().flat_map(|c| &c.units) {
        for activity in &unit.activities {
            if let ActivityKind::Coding { problem } = &activity.kind {
                assert!(problem.language == Language::Python);
            }
        }
    }
}

#[tokio::test]
async fn java_feedback_distinguishes_wrong_output_compilation_and_runtime_errors() {
    let course = Course::parse(DEFAULT_COURSE).unwrap();
    let ActivityKind::Coding { problem } = &course.chapters[0].units[0].activities[1].kind else {
        panic!()
    };
    let report = runner::check_unit(
        problem,
        "class Main { public static void main(String[] args) { System.out.println(0); } }",
    )
    .await
    .unwrap();
    assert!(!report.passed);
    assert_eq!(report.cases[0].state, "finished");
    let bad = runner::run_code(Language::Java, "class Main { broken }", "")
        .await
        .unwrap();
    assert!(!bad.success);
    assert_eq!(bad.state, "compile_error");
    let bad = runner::run_code(Language::Java, "class Main { public static void main(String[] args) { int[] a = {}; System.out.println(a[0]); } }", "").await.unwrap();
    assert!(!bad.success);
    assert_eq!(bad.state, "runtime_error");
    assert!(bad.stderr.contains("ArrayIndexOutOfBoundsException"));
    let large = runner::run_code(Language::Java, &"x".repeat(65537), "").await;
    assert!(large.is_err());
}

#[tokio::test]
async fn java_contracts_reject_unused_methods_fake_aliases_and_shared_field_bypasses() {
    let course = Course::parse(DEFAULT_COURSE).unwrap();
    let problems: Vec<_> = course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .flat_map(|u| &u.activities)
        .filter_map(|a| match &a.kind {
            ActivityKind::Coding { problem } => Some(problem),
            _ => None,
        })
        .collect();
    for (id, before, after) in [
        (
            "java25-09-code",
            "System.out.println(twice(value));",
            "if (false) twice(value); System.out.println(value * 2);",
        ),
        (
            "java25-11-code",
            "counter.add(scanner.nextInt());\n        System.out.println(counter.value);",
            "int amount = scanner.nextInt();\n        System.out.println(counter.value + amount);",
        ),
        (
            "java25-11-code-alias",
            "Counter alias = first;",
            "Counter alias = new Counter(first.value);",
        ),
        ("java25-12-code", "if (isPassed(score))", "if (score >= 60)"),
        (
            "java25-12-code",
            "System.out.println(book.average());",
            "System.out.println(book.sum / n);",
        ),
        (
            "java25-11-code-static",
            "first.add(scanner.nextInt());\n        second.add(scanner.nextInt());",
            "int x = scanner.nextInt(); int y = scanner.nextInt(); first.add(x); second.add(y);",
        ),
    ] {
        let p = problems.iter().find(|p| p.id == id).unwrap();
        assert!(p.solution.contains(before));
        let mut bypass = p.solution.replace(before, after);
        if id.ends_with("alias") {
            bypass = bypass
                .replace(
                    "alias.add(scanner.nextInt());",
                    "int amount = scanner.nextInt(); alias.add(amount); first.add(amount);",
                )
                .replace(
                    "System.out.println(first == alias);",
                    "System.out.println(true);",
                );
        }
        if id.ends_with("static") {
            bypass = bypass.replace(
                "System.out.println(Counter.totalAdded);",
                "System.out.println(x + y);",
            );
        }
        // Every bypass produces the expected stdout before concept checking.
        for test in &p.tests {
            let output = runner::run_code(Language::Java, &bypass, &test.input)
                .await
                .unwrap();
            assert!(output.success, "{id}: {}", output.stderr);
            assert_eq!(output.stdout, test.expected, "{id}");
        }
        let report = runner::check_unit(p, &bypass).await.unwrap();
        assert!(!report.passed, "{id} bypass passed");
        assert_eq!(report.cases.last().unwrap().state, "concept_error");
    }
    let p = problems.iter().find(|p| p.id == "java25-11-code").unwrap();
    let report = runner::check_unit(
        p,
        "class Main { public static void main(String[] args) { System.out.println(3); } }",
    )
    .await
    .unwrap();
    assert!(!report.passed);
}

#[tokio::test]
async fn java_contracts_accept_equivalent_calculations_and_default_static_initialization() {
    let course = Course::parse(DEFAULT_COURSE).unwrap();
    for activity in course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .flat_map(|u| &u.activities)
    {
        let ActivityKind::Coding { problem } = &activity.kind else {
            continue;
        };
        let alternative = match problem.id.as_str() {
            "java25-09-code" => problem
                .solution
                .replace("return value * 2;", "return value + value;"),
            "java25-11-code-static" => problem
                .solution
                .replace("static int totalAdded = 0;", "static int totalAdded;"),
            "java25-11-code-alias" => problem
                .solution
                .replace("Counter alias = first;", "Counter alias = (first);"),
            _ => continue,
        };
        let report = runner::check_unit(problem, &alternative).await.unwrap();
        assert!(
            report.passed,
            "{}: {}",
            problem.id,
            serde_json::to_string(&report).unwrap()
        );
    }
}

#[test]
fn java_narration_patches_are_unique_and_finish_at_the_commented_answer() {
    let course = Course::parse(DEFAULT_COURSE).unwrap();
    for activity in course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .flat_map(|u| &u.activities)
    {
        let ActivityKind::Coding { problem } = &activity.kind else {
            continue;
        };
        let mut code = String::new();
        let mut patches = 0;
        for action in &activity.narration {
            match action["action"].as_str().unwrap() {
                "set_code" => code = action["code"].as_str().unwrap().into(),
                "patch_code" => {
                    let before = action["before"].as_str().unwrap();
                    assert_eq!(code.matches(before).count(), 1, "{}", problem.id);
                    code = code.replacen(before, action["after"].as_str().unwrap(), 1);
                    patches += 1;
                }
                _ => (),
            }
        }
        assert_eq!(code, problem.solution, "{}", problem.id);
        if problem.checker.is_some() {
            assert!(patches >= 3);
        }
    }
}

#[test]
fn stronger_coding_revision_requires_resubmission_without_losing_other_progress() {
    let course = Course::parse(DEFAULT_COURSE).unwrap();
    let directory = tempfile::tempdir().unwrap();
    let mut store = LearningStore::open(&directory.path().join("progress.sqlite3")).unwrap();
    let unit = &course.chapters[2].units[0];
    let strengthened = unit.activities[1].progress_unit(unit);
    assert_eq!(strengthened.revision, 2);
    let mut old = strengthened.clone();
    old.revision = 1;
    let untouched_unit = &course.chapters[0].units[0];
    let untouched = untouched_unit.activities[1].progress_unit(untouched_unit);
    let report = runner::TestReport {
        passed: true,
        cases: vec![runner::TestCaseResult {
            input: String::new(),
            expected: "ok".into(),
            stdout: "ok".into(),
            stderr: String::new(),
            passed: true,
            state: "finished".into(),
        }],
    };
    store.save(&course.id, &old, "", &report).unwrap();
    store.save(&course.id, &untouched, "", &report).unwrap();
    let completed = store.completed_items(&course).unwrap();
    assert!(!completed.contains(&strengthened.id));
    assert!(completed.contains(&untouched.id));
    store.save(&course.id, &strengthened, "", &report).unwrap();
    assert!(store
        .completed_items(&course)
        .unwrap()
        .contains(&strengthened.id));
}
