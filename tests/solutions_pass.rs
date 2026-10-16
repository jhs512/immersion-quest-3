//! Every reference solution of the KPC course (courses/kpc-solutions.json, with its comments)
//! really passes its own problem through the app's runner: tests and checkers alike. This is the
//! "play through every coding mission" check; it runs the learning Python, so it is `ignore`d by
//! default and run on demand:
//!   cargo test --test solutions_pass -- --ignored
use molip_quest::{curriculum::ActivityKind, runner::check_unit, Course};
use std::collections::HashMap;

#[tokio::test]
#[ignore = "runs every solution through the learning Python (a few minutes)"]
async fn every_kpc_solution_passes_its_problem() {
    let course = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
    let solutions: HashMap<String, String> =
        serde_json::from_str(include_str!("../courses/kpc-solutions.json")).unwrap();
    let mut failed = Vec::new();
    let mut checked = 0;
    for activity in course.chapters.iter().flat_map(|c| &c.units).flat_map(|u| &u.activities) {
        let ActivityKind::Coding { problem } = &activity.kind else { continue };
        let solution = solutions.get(&problem.id).unwrap_or_else(|| panic!("{}: no solution", problem.id));
        match check_unit(problem, solution).await {
            Ok(report) if report.passed => {}
            Ok(report) => failed.push(format!(
                "{}: {}",
                activity.id,
                report
                    .cases
                    .iter()
                    .filter(|c| !c.passed)
                    .map(|c| format!("[{}] {}", c.state, c.stderr.lines().last().unwrap_or("").trim()))
                    .collect::<Vec<_>>()
                    .join(" | ")
            )),
            Err(error) => failed.push(format!("{}: {error}", activity.id)),
        }
        checked += 1;
    }
    assert!(failed.is_empty(), "{} of {checked} solutions fail:\n{}", failed.len(), failed.join("\n"));
    assert!(checked > 100, "only {checked} coding missions checked");
}
