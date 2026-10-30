//! 코드 흐름 보기 for Python: a step-by-step trace of the learner's current `main.py`.
//!
//! The grader runs `python -I -X utf8 -u rich_runner.py` in a workspace with the bundled data files and
//! the task's files (crate::runner::execute_python_files). The trace runs that same runner, in the same
//! kind of workspace, with the same interpreter; `assets/python-trace/mq_pytrace.py` only wraps it in
//! `sys.settrace` and records the frames whose code is `main.py`, in the trace document format of the
//! Java core (docs/trace-format.md of java-memory-visualizer), so the same viewer draws it. Grading and
//! progress never read it.
use std::collections::BTreeMap;

const TRACER: &str = include_str!("../assets/python-trace/mq_pytrace.py");
const RUNNER: &str = include_str!("../assets/python/rich_runner.py");
pub const STEP_BUDGET: u32 = 1000;
const SECONDS: u64 = 20;

/// Trace `source` with `input` as standard input. Returns the trace document with `status` ok,
/// compile_error, uncaught_exception or step_limit; an Err only when the tool itself cannot run.
pub async fn trace(source: &str, input: &str, files: &BTreeMap<String, String>) -> Result<String, String> {
    if source.len() > 65536 || input.len() > 65536 { return Err("코드와 입력은 각각 64KB 이하여야 해요.".into()); }
    let dir = crate::runner::python_workspace(source, files)?;
    for (name, text) in [("rich_runner.py", RUNNER), ("mq_pytrace.py", TRACER), ("stdin.txt", input)] {
        std::fs::write(dir.path().join(name), text).map_err(|e| e.to_string())?;
    }
    let mut cmd = crate::lesson_runner::command(crate::runner::python_executable());
    if let Some(path) = crate::runtime_setup::library_path() { cmd.env("DYLD_LIBRARY_PATH", path); }
    cmd.args(["-I", "-X", "utf8", "-u", "mq_pytrace.py", "rich_runner.py", "stdin.txt", "trace.json", &STEP_BUDGET.to_string()])
        .env("TF_CPP_MIN_LOG_LEVEL", "3").env("TF_ENABLE_ONEDNN_OPTS", "0");
    let run = crate::lesson_runner::process(cmd, dir.path(), "", SECONDS).await?;
    if run.state == "timeout" {
        return Err(format!("코드 흐름을 {SECONDS}초 안에 기록하지 못했어요. 반복이 끝나는지 확인하세요."));
    }
    let document = std::fs::read_to_string(dir.path().join("trace.json"))
        .map_err(|_| format!("코드 흐름을 기록하지 못했어요. {}", run.stderr.trim()))?;
    serde_json::from_str::<serde_json::Value>(&document).map_err(|e| format!("코드 흐름 기록을 읽지 못했어요: {e}"))?;
    Ok(document)
}

#[cfg(test)]
mod tests {
    fn frames(step: &serde_json::Value) -> Vec<serde_json::Value> { step["stack_to_render"].as_array().cloned().unwrap_or_default() }
    fn local(step: &serde_json::Value, name: &str) -> Option<serde_json::Value> { frames(step).last().and_then(|f| f["encoded_locals"].get(name).cloned()) }

    /// Every Python step that offers 코드 흐름 보기: the starter and the solution are traced on the real
    /// path and the trace's output is the graded run's output (crate::runner::execute_python_files).
    #[tokio::test]
    #[ignore = "Needs the course Python runtime"]
    async fn every_python_code_flow_step_traces_its_starter_and_solution_like_the_grader() {
        let mut traced = 0;
        for key in ["engineer-python-calls", "engineer-python-values"] {
            let lesson: serde_json::Value = serde_json::from_str(crate::lesson_registry::find(key).unwrap().lesson).unwrap();
            for task in lesson["tasks"].as_array().unwrap().iter().filter(|t| t["code_flow"] == true) {
                let files: std::collections::BTreeMap<String, String> = serde_json::from_value(task["files"].clone()).unwrap_or_default();
                for field in ["starter_code", "solution"] {
                    let source = task[field].as_str().unwrap();
                    let doc: serde_json::Value = serde_json::from_str(&super::trace(source, "", &files).await.unwrap()).unwrap();
                    let graded = crate::runner::execute_python_files(source, "", None, &files).await.unwrap();
                    let label = format!("{key} {} {field}", task["id"]);
                    assert_eq!(doc["stdout"].as_str().unwrap().replace("\r\n", "\n"), graded.stdout, "{label}");
                    assert_eq!(doc["status"] == "ok", graded.success, "{label}: {}", doc["status"]);
                    let steps = doc["trace"].as_array().unwrap();
                    assert!(!steps.is_empty(), "{label}");
                    assert!(steps.iter().all(|s| s["line"].as_i64().is_some_and(|l| l >= 1 && l as usize <= source.lines().count())), "{label}");
                    traced += 1;
                }
            }
        }
        assert!(traced >= 8, "{traced}");
    }

    /// Aliasing, a shared default list, a call stack and an uncaught exception, read from a real run.
    #[tokio::test]
    #[ignore = "Needs the course Python runtime"]
    async fn traces_references_calls_and_an_uncaught_exception_from_the_real_runner() {
        let source = "def record(value, items=[]):\n    items.append(value)\n    return items\n\nfirst = record(2)\nsecond = record(4)\nprint(first is second)\nprint(1 / 0)\n";
        let doc: serde_json::Value = serde_json::from_str(&super::trace(source, "", &Default::default()).await.unwrap()).unwrap();
        let graded = crate::runner::execute_python_files(source, "", None, &Default::default()).await.unwrap();
        assert!(!graded.success);
        assert_eq!(doc["status"], "uncaught_exception", "{doc}");
        assert_eq!(doc["stdout"].as_str().unwrap().replace("\r\n", "\n"), graded.stdout);
        let steps = doc["trace"].as_array().unwrap();
        let last = steps.last().unwrap();
        assert!(last["exception_msg"].as_str().unwrap().starts_with("ZeroDivisionError"));
        // Both calls returned the same list object: the same heap id.
        let after = steps.iter().find(|s| local(s, "second").is_some()).unwrap();
        assert_eq!(local(after, "first"), local(after, "second"));
        // Inside record, the stack is <module> > record.
        let inside = steps.iter().find(|s| frames(s).len() == 2).unwrap();
        assert_eq!(frames(inside)[1]["func_name"], "record");
        // A syntax error is reported with its line, without steps.
        let broken: serde_json::Value = serde_json::from_str(&super::trace("x = (\n", "", &Default::default()).await.unwrap()).unwrap();
        assert_eq!(broken["status"], "compile_error");
    }
}
