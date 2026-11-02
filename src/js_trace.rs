//! 코드 흐름 보기 for JavaScript: the steps of the learner's UNMODIFIED `main.js`.
//!
//! The grader runs `node main.js` in a workspace with the task's files, the input on a stdin pipe
//! (crate::lesson_runner). The trace runs that same file, in the same kind of workspace, with the same
//! Node.js (crate::node_tools), once, adding only `--inspect-brk=127.0.0.1:0 --inspect-publish-uid=stderr`.
//! `assets/js-trace/mq_jstrace.cjs` is a separate controller process that attaches over the Chrome
//! DevTools Protocol and stops at every breakable location of main.js; values are read from the paused
//! program (accessors and Proxy traps are not run), object identity is kept by a WeakMap it creates in the
//! program's realm before main.js runs. A run where reading a value would have run the learner's code
//! (an Error whose stack/message/name is a getter: V8 reads those to describe the error) gives
//! `status: unsupported` and no steps. Only the main thread is traced; worker threads run untraced.
//! Grading and progress never read the document.
use std::{collections::BTreeMap, path::{Path, PathBuf}};

const CONTROLLER: &str = include_str!("../assets/js-trace/mq_jstrace.cjs");
pub const STEP_BUDGET: u32 = 1000;
/// The controller's own limit; it ends the program and writes what it has before the outer one.
const DEADLINE_MS: u64 = 20_000;
const SECONDS: u64 = 30;

/// Trace `source` with `input` as standard input. Returns the trace document with `status` ok,
/// compile_error, uncaught_exception, runtime_error, step_limit or unsupported; an Err only when the
/// tool itself cannot run (no suitable Node.js, or no trace within the time limit).
pub async fn trace(source: &str, input: &str, files: &BTreeMap<String, String>) -> Result<String, String> {
    let document = record(source, input, files).await?;
    let value: serde_json::Value = serde_json::from_str(&document).map_err(|e| format!("코드 흐름 기록을 읽지 못했어요: {e}"))?;
    match value["status"].as_str() {
        Some("timeout") => Err(format!("코드 흐름을 {}초 안에 기록하지 못했어요. 반복이 끝나는지 확인하세요.", DEADLINE_MS / 1000)),
        Some("runtime_unavailable" | "tool_error") => Err(value["message"].as_str().unwrap_or("Node.js를 확인하세요.").to_string()),
        _ => Ok(document),
    }
}

/// The controller's document as written, `timeout`, `runtime_unavailable` and `tool_error` included.
async fn record(source: &str, input: &str, files: &BTreeMap<String, String>) -> Result<String, String> {
    if source.len() > 65536 || input.len() > 65536 { return Err("코드와 입력은 각각 64KB 이하여야 해요.".into()); }
    let node = crate::node_tools::executable();
    if !node.is_file() {
        return Err("JavaScript 코드 흐름 보기에는 Node.js 22 이상이 필요해요. Node.js를 설치한 뒤 MQ를 다시 여세요.".into());
    }
    let root = tempfile::tempdir().map_err(|e| e.to_string())?;
    let [workspace, tool, capture] = ["workspace", "tool", "capture"].map(|d| root.path().join(d));
    for d in [&workspace, &tool, &capture] { std::fs::create_dir_all(d).map_err(|e| e.to_string())?; }
    for (name, content) in files.iter().chain([(&"main.js".to_string(), &source.to_string())]) {
        if !crate::repository_course::safe_file(name) { return Err("실습 파일 경로를 확인하세요.".into()); }
        let path = workspace.join(name);
        std::fs::create_dir_all(path.parent().ok_or("파일 경로 오류")?).map_err(|e| e.to_string())?;
        std::fs::write(path, content).map_err(|e| e.to_string())?;
    }
    std::fs::write(tool.join("mq_jstrace.cjs"), CONTROLLER).map_err(|e| e.to_string())?;
    std::fs::write(tool.join("stdin.txt"), input).map_err(|e| e.to_string())?;
    let out = tool.join("trace.json");

    let mut cmd = crate::node_tools::command(&node);
    cmd.arg(tool.join("mq_jstrace.cjs")).arg(&workspace).arg(tool.join("stdin.txt")).arg(&capture).arg(&out)
        .arg(STEP_BUDGET.to_string()).arg(DEADLINE_MS.to_string());
    let guard = Debuggee { capture: capture.clone(), done: false };
    let run = crate::lesson_runner::process(cmd, &tool, "", SECONDS).await?;
    if run.state == "timeout" {
        return Err(format!("코드 흐름을 {SECONDS}초 안에 기록하지 못했어요. 반복이 끝나는지 확인하세요."));
    }
    guard.finished();
    std::fs::read_to_string(&out)
        .map_err(|_| format!("코드 흐름을 기록하지 못했어요. {}", run.stderr.lines().last().unwrap_or("").trim()))
}

/// The program the controller started. The controller ends it itself; this covers the controller being
/// ended first (the outer timeout, or the request dropped): it ends exactly that process and what it started.
struct Debuggee { capture: PathBuf, done: bool }
impl Debuggee {
    fn finished(mut self) { self.done = true; }
}
impl Drop for Debuggee {
    fn drop(&mut self) { if !self.done { end_debuggee(&self.capture); } }
}
fn end_debuggee(capture: &Path) {
    let Some(pid) = std::fs::read_to_string(capture.join("debuggee.pid")).ok().and_then(|p| p.trim().parse::<u32>().ok()) else { return };
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        let taskkill = std::env::var_os("SystemRoot").map(|r| PathBuf::from(r).join("System32").join("taskkill.exe")).unwrap_or_else(|| "taskkill".into());
        let _ = std::process::Command::new(taskkill).args(["/PID", &pid.to_string(), "/T", "/F"]).creation_flags(0x08000000)
            .stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null()).status();
    }
    // The controller starts it as the leader of its own process group.
    #[cfg(unix)]
    let _ = std::process::Command::new("kill").args(["-KILL", "--", &format!("-{pid}")])
        .stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null()).status();
}

#[cfg(test)]
mod tests {
    use serde_json::{json, Value};
    fn frames(step: &Value) -> Vec<Value> { step["stack_to_render"].as_array().cloned().unwrap_or_default() }
    fn local(step: &Value, name: &str) -> Option<Value> { frames(step).last().and_then(|f| f["encoded_locals"].get(name).cloned()) }
    async fn traced(source: &str, input: &str) -> Value { serde_json::from_str(&super::trace(source, input, &Default::default()).await.unwrap()).unwrap() }
    fn alive(pid: u32) -> bool {
        if cfg!(windows) {
            let out = std::process::Command::new("tasklist").args(["/FI", &format!("PID eq {pid}"), "/NH", "/FO", "CSV"]).output().unwrap();
            String::from_utf8_lossy(&out.stdout).contains(&format!("\"{pid}\""))
        } else {
            std::process::Command::new("kill").args(["-0", &pid.to_string()]).status().unwrap().success()
        }
    }
    /// The JavaScript tasks of every registered lesson, and of the Node lesson file that is not in the catalog.
    fn javascript_tasks() -> Vec<(String, Value)> {
        let node = ("node-cpu-offload", include_str!("../courses/redesigned/node-cpu-offload.json"));
        let mut tasks: Vec<(String, Value)> = vec![];
        for (key, text) in crate::lesson_registry::LESSONS.iter().map(|l| (l.key, l.lesson)).chain([node]) {
            let lesson: Value = serde_json::from_str(text).unwrap();
            for task in lesson["tasks"].as_array().into_iter().flatten().filter(|t| t["language"] == "javascript") {
                if !tasks.iter().any(|(_, t)| t["id"] == task["id"]) { tasks.push((key.to_string(), task.clone())); }
            }
        }
        tasks
    }

    /// Every JavaScript step's starter and solution, with every test input: the trace's output is the
    /// output of the grader's own run (crate::lesson_runner::run, done separately), or a prefix of it when
    /// the step budget stopped the trace first.
    #[tokio::test]
    #[ignore = "Needs Node.js 22 or newer"]
    async fn every_javascript_step_traces_its_starter_and_solution_like_the_grader() {
        let (mut complete, mut budget) = (0, 0);
        let tasks = javascript_tasks();
        assert!(tasks.len() >= 5, "{}", tasks.len());
        for (key, value) in tasks {
            let task: crate::repository_course::Task = serde_json::from_value(value.clone()).unwrap();
            for field in ["starter_code", "solution"] {
                let source = value[field].as_str().unwrap();
                let inputs: Vec<String> = if task.tests.is_empty() { vec![String::new()] } else { task.tests.iter().map(|t| t.input.clone()).collect() };
                for input in inputs {
                    let doc: Value = serde_json::from_str(&super::trace(source, &input, &task.files).await.unwrap()).unwrap();
                    let graded = crate::lesson_runner::run(&task, source, &input).await.unwrap();
                    let label = format!("{key} {} {field} {input:?}", task.id);
                    let stdout = doc["stdout"].as_str().unwrap().replace("\r\n", "\n");
                    let steps = doc["trace"].as_array().unwrap();
                    assert!(!steps.is_empty(), "{label}: {}", doc["status"]);
                    assert!(steps.iter().all(|s| s["line"].as_i64().is_some_and(|l| l >= 1 && l as usize <= source.lines().count())), "{label}");
                    if doc["status"] == "step_limit" {
                        assert!(graded.stdout.starts_with(&stdout), "{label}: {stdout:?} / {:?}", graded.stdout);
                        assert_eq!(steps.last().unwrap()["event"], "instruction_limit_reached", "{label}");
                        assert!(steps.len() as u32 <= super::STEP_BUDGET + 1, "{label}");
                        budget += 1;
                    } else {
                        assert_eq!(stdout, graded.stdout, "{label}");
                        assert_eq!(doc["status"] == "ok", graded.success, "{label}: {}", doc["status"]);
                        complete += 1;
                    }
                }
            }
        }
        // Today: four steps finish within the budget; the fifth hashes 300000 rounds and reaches it.
        assert!(complete >= 8, "complete {complete}, budget {budget}");
    }

    /// Aliasing and a cycle by object identity, a call stack with a return value, a closure seen from a
    /// later callback, TDZ, JavaScript's own numbers, stdin, and an uncaught exception from a real run.
    #[tokio::test]
    #[ignore = "Needs Node.js 22 or newer"]
    async fn traces_identity_calls_closures_and_values_of_the_real_program() {
        let source = "const name = require('node:fs').readFileSync(0, 'utf8').trim();\nconst a = [1, 2];\nconst b = a;\nconst c = { label: '<b>' };\nc.self = c;\nconst odd = [NaN, -0, Infinity, 10n, undefined, null];\nfunction twice(x) {\n  const y = x * 2;\n  return y;\n}\nconst r = twice(21);\nsetImmediate(() => { a.push(name); });\nlet later = 1;\nsetTimeout(() => { throw new TypeError('late ' + later); }, 5);\n";
        let doc = traced(source, "kim").await;
        let graded = crate::lesson_runner::run(&serde_json::from_value(javascript_tasks()[0].1.clone()).unwrap(), source, "kim").await.unwrap();
        assert_eq!(doc["status"], "uncaught_exception", "{doc}");
        assert!(!graded.success);
        assert_eq!(doc["stdout"].as_str().unwrap().replace("\r\n", "\n"), graded.stdout);
        let steps = doc["trace"].as_array().unwrap();
        assert_eq!(steps.last().unwrap()["exception_msg"], "TypeError: late 1");
        let end = steps.iter().rev().find(|s| local(s, "later").is_some_and(|v| v == 1)).unwrap();
        // a and b are one array; c refers to itself; the name with markup is data, not HTML.
        assert_eq!(local(end, "a"), local(end, "b"));
        let c = local(end, "c").unwrap();
        let object = &end["heap"][c[1].to_string()];
        assert_eq!(object[0], "INSTANCE");
        assert!(object.as_array().unwrap().contains(&json!(["self", c])));
        assert!(object.as_array().unwrap().contains(&json!(["label", "<b>"])));
        let odd = &end["heap"][local(end, "odd").unwrap()[1].to_string()];
        assert_eq!(odd, &json!(["ARRAY", "Array(6)", ["SPECIAL_FLOAT", "NaN"], ["SPECIAL_FLOAT", "-0"], ["SPECIAL_FLOAT", "Infinity"], ["SPECIAL_FLOAT", "10n"], ["C_NOTE", "undefined"], null]));
        assert_eq!(local(end, "name"), Some(json!("kim")));
        // before its declaration ran, `later` is in the temporal dead zone
        assert!(steps.iter().any(|s| local(s, "later") == Some(json!(["C_NOTE", "초기화 전 (TDZ)"]))));
        // twice: the stack is 전역 코드 > twice, and its return is read at the real return
        let inside = steps.iter().find(|s| frames(s).len() == 2 && s["event"] == "return").unwrap();
        assert_eq!(frames(inside)[1]["func_name"], "twice");
        assert_eq!(local(inside, "__return__"), Some(json!(42)));
        // the setImmediate callback runs after the top level finished; `a` and `name` reach it as a closure
        let callback = steps.iter().find(|s| frames(s).len() == 1 && frames(s)[0]["func_name"] != "전역 코드").unwrap();
        assert!(local(callback, "a (클로저)").is_some(), "{callback}");
    }

    /// The program is the learner's own: what it would do is what it does under the trace, or the trace
    /// is refused. A getter V8 would run to describe an Error refuses it; a getter, Proxy trap or replaced
    /// builtin elsewhere is never run.
    #[tokio::test]
    #[ignore = "Needs Node.js 22 or newer"]
    async fn never_runs_the_learners_getters_or_traps_while_drawing() {
        let source = "let effects = 0;\nconst watched = { get spy() { effects++; return 1; } };\nconst p = new Proxy([1], { get() { effects++; }, ownKeys() { effects++; return []; }, getOwnPropertyDescriptor() { effects++; } });\nconst tagged = { get [Symbol.toStringTag]() { effects++; return 'T'; } };\nWeakMap.prototype.get = function () { effects++; };\nconst list = [watched, p, tagged];\nconsole.log('effects ' + effects);\n";
        let doc = traced(source, "").await;
        assert_eq!(doc["status"], "ok", "{doc}");
        assert_eq!(doc["stdout"].as_str().unwrap().trim(), "effects 0");
        let last = doc["trace"].as_array().unwrap().iter().rev().find(|s| local(s, "watched").is_some_and(|v| v[0] == "REF")).unwrap();
        assert!(last["heap"].as_object().unwrap().values().any(|o| o.as_array().unwrap().contains(&json!(["spy", ["C_NOTE", "getter · 실행하지 않음"]]))));
        for code in [
            "class E extends Error { get message() { console.log('ran'); return 'm'; } }\nconst e = new E();\nconsole.log('end');\n",
            "const e = new Error('x');\nObject.defineProperty(e, 'stack', { get() { console.log('ran'); return 's'; } });\nconsole.log('end');\n",
        ] {
            let refused = traced(code, "").await;
            assert_eq!(refused["status"], "unsupported", "{refused}");
            assert!(refused["trace"].as_array().unwrap().is_empty());
            assert!(refused["message"].as_str().unwrap().contains("getter"));
        }
    }

    /// Syntax errors are reported with their line; a loop that never ends and a flood of output are
    /// stopped by the controller's own limits, and the program (with a process it started) is gone after.
    #[tokio::test]
    #[ignore = "Needs Node.js 22 or newer"]
    async fn reports_syntax_errors_and_ends_runaway_programs_with_what_they_started() {
        let broken = traced("const a = 1;\nconst b = ;\n", "").await;
        assert_eq!(broken["status"], "compile_error");
        assert_eq!(broken["problems"][0]["line"], 2, "{broken}");

        let flood = traced("for (;;) console.log('x'.repeat(80));\n", "").await;
        assert_eq!(flood["status"], "step_limit", "{flood}");

        let spin = "const { spawn } = require('node:child_process');
const c = spawn(process.execPath, ['-e', 'setInterval(() => {}, 1000)'], { stdio: 'ignore' });
console.log(c.pid);
while (true) {}
";
        let started = std::time::Instant::now();
        let error = super::trace(spin, "", &Default::default()).await.unwrap_err();
        assert!(error.contains("기록하지 못했어요"), "{error}");
        assert!(started.elapsed() < std::time::Duration::from_secs(super::SECONDS), "{:?}", started.elapsed());
        let doc: Value = serde_json::from_str(&super::record(spin, "", &Default::default()).await.unwrap()).unwrap();
        assert_eq!(doc["status"], "timeout");
        let child: u32 = doc["stdout"].as_str().unwrap().trim().parse().unwrap();
        assert!(!alive(child), "the process main.js started is still running: {child}");

        let finished = traced("console.log('done');\n", "").await;
        assert_eq!(finished["status"], "ok");
        // A finished program waits for the debugger to detach; the controller detaches at once.
        assert!(finished["timing"]["runMs"].as_u64().unwrap() < 5000, "{finished}");
    }
}
