//! Replays a converted lesson against its validated lesson-case file (tests/lesson-cases/<key>.json),
//! the same contract as examples/validate_redesigned_lesson.rs for plain-output lessons: every starter
//! fails and every solution passes the real grader, the teacher narration's real outputs are the pinned
//! ones, recorded wrong answers fail and other correct answers pass.
use molip_quest::{lesson_runner, repository_course::{CourseManifest, Lesson}};

fn patched(source: &str, replacements: &serde_json::Value, label: &str) -> String {
    let mut source = source.to_owned();
    for pair in replacements.as_array().unwrap() {
        let (before, after) = (pair[0].as_str().unwrap(), pair[1].as_str().unwrap());
        assert_eq!(source.matches(before).count(), 1, "{label}: patch target {before:?}");
        source = source.replacen(before, after, 1);
    }
    source
}

pub async fn replay(key: &str) {
    let spec: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(format!("tests/lesson-cases/{key}.json")).unwrap()).unwrap();
    let course = CourseManifest::parse(&std::fs::read_to_string(spec["course"].as_str().unwrap()).unwrap()).unwrap();
    let lesson = Lesson::parse(&std::fs::read_to_string(spec["lesson"].as_str().unwrap()).unwrap(), &course.lessons[0]).unwrap();
    let expected = spec["expected_outputs"].as_array().unwrap();
    assert_eq!(expected.len(), lesson.tasks.len(), "{key}: every step has pinned teacher outputs");
    for (index, task) in lesson.tasks.iter().enumerate() {
        let label = format!("{key} step {} ({})", index + 1, task.title);
        assert!(!lesson_runner::check(task, &task.starter_code).await.unwrap().passed, "{label}: starts unsolved");
        let report = lesson_runner::check(task, &task.solution).await.unwrap();
        assert!(report.passed, "{label}: solution {}", serde_json::to_string(&report).unwrap());
        let mut source = task.example_code.clone().unwrap_or_else(|| task.starter_code.clone());
        let mut input = task.tests.first().map(|case| case.input.clone()).unwrap_or_default();
        let mut outputs = Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code" => source = patched(&source, &serde_json::json!([[action["before"], action["after"]]]), &label),
                "set_code" => source = action["code"].as_str().unwrap().to_owned(),
                "set_input" => input = action["value"].as_str().unwrap().to_owned(),
                "run" => {
                    let result = if task.has_runnable_example() { lesson_runner::run_example(task, &source, &input).await }
                        else { lesson_runner::run(task, &source, &input).await }.unwrap();
                    match action["expect_error"].as_str() {
                        Some(error) => assert!(!result.success && (result.stderr.contains(error) || result.stdout.contains(error)),
                            "{label}: teacher demonstrates {error}: {}", result.stderr),
                        None => assert!(result.success, "{label}: teacher run: {}", result.stderr),
                    }
                    outputs.push(result.stdout.trim_end().to_owned());
                }
                _ => {}
            }
        }
        let pinned: Vec<&str> = expected[index].as_array().unwrap().iter().map(|v| v.as_str().unwrap()).collect();
        assert_eq!(outputs, pinned, "{label}: teacher outputs");
    }
    for (kind, pass) in [("reject", false), ("accept", true)] {
        for case in spec[kind].as_array().into_iter().flatten() {
            let task = &lesson.tasks[case["step"].as_u64().unwrap() as usize - 1];
            let reason = case["reason"].as_str().unwrap();
            let answer = patched(&task.solution, &case["replacements"], reason);
            assert_eq!(lesson_runner::check(task, &answer).await.unwrap().passed, pass, "{key} {kind}: {reason}");
        }
    }
}
