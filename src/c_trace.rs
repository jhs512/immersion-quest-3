//! 코드 흐름 보기 for C (Windows): the steps of the learner's `main.c` as the grader's compiler builds it.
//!
//! The grader runs `tcc -run main.c` with TinyCC 0.9.27 (crate::lesson_runner). TinyCC 0.9.27's debug
//! information has function and statement lines but no variables, so `assets/c-trace/` does this:
//!  1. `c_flow.py` compiles the UNMODIFIED code with the same tcc (`-g` adds debug sections; the machine code
//!     is the same) and runs it under the Windows debugger engine (C:\Windows\System32\dbgeng.dll). Every
//!     step is a real stop of that program; values are read from its memory, heap blocks are its own
//!     malloc/calloc/realloc results, the output so far is what its C runtime has written or still buffers.
//!  2. Variable names, types and frame/section offsets come from an instrumented copy of the same code,
//!     compiled by the same tcc (`c_instrument.py`, pycparser from the course Python). `c_verify.py`
//!     checks, on this very run, that every value the copy recorded equals the original's at the same stop,
//!     and that both outputs equal the grader's. Any difference, an unsupported construct (union, bit field,
//!     goto, VLA, setjmp, threads, alloca, va_list, inline assembly, #pragma) or a run that does not finish
//!     within the step budget gives `status: unsupported` with the reason and no steps: a trace that could be
//!     wrong is never drawn. Running and grading are untouched; they never read this.
//! Uninitialized values are shown as their real bytes (with a badge), not as 0.
use std::path::Path;

const TOOL: &[(&str, &str)] = &[
    ("c_flow.py", include_str!("../assets/c-trace/c_flow.py")),
    ("c_verify.py", include_str!("../assets/c-trace/c_verify.py")),
    ("c_instrument.py", include_str!("../assets/c-trace/c_instrument.py")),
    ("stabs.py", include_str!("../assets/c-trace/stabs.py")),
    ("dbgeng.py", include_str!("../assets/c-trace/dbgeng.py")),
    ("mq_rt.c", include_str!("../assets/c-trace/mq_rt.c")),
];
const SECONDS: u64 = 90;

/// Trace `source` with `input` as standard input. Returns the trace document (`status` ok, compile_error,
/// uncaught_exception, step_limit or unsupported); an Err only when the tool itself cannot run.
pub async fn trace(source: &str, input: &str) -> Result<String, String> {
    if !cfg!(windows) { return Err("C 코드 흐름 보기는 지금 Windows에서만 쓸 수 있어요. 코드 실행과 채점은 그대로 쓸 수 있어요.".into()); }
    if source.len() > 65536 || input.len() > 65536 { return Err("코드와 입력은 각각 64KB 이하여야 해요.".into()); }
    let tcc = crate::lesson_runner::c_compiler().await?;
    let dir = tempfile::tempdir().map_err(|e| e.to_string())?;
    let tool = dir.path().join("tool");
    let case = dir.path().join("case");
    for d in [&tool, &case] { std::fs::create_dir_all(d).map_err(|e| e.to_string())?; }
    for (name, text) in TOOL { std::fs::write(tool.join(name), text).map_err(|e| e.to_string())?; }
    std::fs::write(case.join("src.c"), source).map_err(|e| e.to_string())?;
    std::fs::write(case.join("stdin.txt"), input).map_err(|e| e.to_string())?;
    run_tool(&tool, &case, &tcc).await
}

async fn run_tool(tool: &Path, case: &Path, tcc: &Path) -> Result<String, String> {
    let mut cmd = crate::lesson_runner::command(crate::runner::python_executable());
    cmd.args(["-I", "-X", "utf8"]).arg(tool.join("c_flow.py")).arg(case).env("MQ_TCC", tcc);
    let run = crate::lesson_runner::process(cmd, case, "", SECONDS).await?;
    if run.state == "timeout" {
        return Err(format!("코드 흐름을 {SECONDS}초 안에 기록하지 못했어요. 반복이 끝나는지 확인하세요."));
    }
    if run.stderr.contains("No module named 'pycparser'") {
        return Err("C 코드 흐름 도구(pycparser)가 학습 환경에 없어요. 환경 설치를 다시 실행하세요.".into());
    }
    let document = std::fs::read_to_string(case.join("c_flow.json"))
        .map_err(|_| format!("코드 흐름을 기록하지 못했어요. {}", run.stderr.lines().last().unwrap_or("").trim()))?;
    serde_json::from_str::<serde_json::Value>(&document).map_err(|e| format!("코드 흐름 기록을 읽지 못했어요: {e}"))?;
    Ok(document)
}

#[cfg(all(test, windows))]
mod tests {
    fn task(value: &serde_json::Value) -> crate::repository_course::Task { serde_json::from_value(value.clone()).unwrap() }
    fn values(doc: &serde_json::Value, name: &str) -> Vec<serde_json::Value> {
        doc["trace"].as_array().unwrap().iter().filter_map(|s| s["stack_to_render"].as_array().and_then(|f| f.last()).and_then(|f| f["encoded_locals"].get(name).cloned())).collect()
    }

    /// Every C step that offers 코드 흐름 보기, starter and solution, with every test input: the trace is
    /// of a run whose output equals the grader's run (crate::lesson_runner::run), or it is refused with a
    /// reason; a trace is never shown for a run that differs.
    #[tokio::test]
    #[ignore = "Needs Windows, the course TinyCC and Python with pycparser"]
    async fn every_c_code_flow_step_traces_like_the_grader_or_refuses() {
        let (mut traced, mut refused) = (0, 0);
        for key in ["engineer-c-functions", "engineer-c-pointers", "engineer-c-structures"] {
            let lesson: serde_json::Value = serde_json::from_str(crate::lesson_registry::find(key).unwrap().lesson).unwrap();
            for value in lesson["tasks"].as_array().unwrap().iter().filter(|t| t["code_flow"] == true) {
                let task = task(value);
                for field in ["starter_code", "solution"] {
                    let source = value[field].as_str().unwrap();
                    let inputs: Vec<String> = if task.tests.is_empty() { vec![String::new()] } else { task.tests.iter().map(|t| t.input.clone()).collect() };
                    for input in inputs {
                        let doc: serde_json::Value = serde_json::from_str(&super::trace(source, &input).await.unwrap()).unwrap();
                        let graded = crate::lesson_runner::run(&task, source, &input).await.unwrap();
                        let label = format!("{key} {} {field} {input:?}", task.id);
                        match doc["status"].as_str().unwrap() {
                            "unsupported" => { assert!(doc["trace"].as_array().unwrap().is_empty(), "{label}"); refused += 1; }
                            status => {
                                assert_eq!(doc["stdout"].as_str().unwrap().replace("\r\n", "\n"), graded.stdout, "{label}");
                                assert_eq!(status == "ok", graded.success, "{label}: {status}");
                                let steps = doc["trace"].as_array().unwrap();
                                assert!(!steps.is_empty(), "{label}");
                                assert!(steps.iter().all(|s| s["line"].as_i64().is_some_and(|l| l >= 1 && l as usize <= source.lines().count())), "{label}");
                                traced += 1;
                            }
                        }
                    }
                }
                // The solution, at least, is traced: refusing the lesson's own answer would make the step useless.
                let solution: serde_json::Value = serde_json::from_str(&super::trace(value["solution"].as_str().unwrap(), &task.tests.first().map(|t| t.input.clone()).unwrap_or_default()).await.unwrap()).unwrap();
                assert_ne!(solution["status"], "unsupported", "{key} {}: {}", task.id, solution["message"]);
            }
        }
        assert!(traced >= 10, "traced {traced}, refused {refused}");
    }

    /// Real values of the unmodified program: a pointer to a stack cell by name, a heap block, the output
    /// so far, a return value, an uninitialized local shown with its real bytes, and refusals with reasons.
    #[tokio::test]
    #[ignore = "Needs Windows, the course TinyCC and Python with pycparser"]
    async fn traces_pointers_heap_output_returns_and_refuses_what_it_cannot_show() {
        let source = "#include <stdio.h>\n#include <stdlib.h>\nint twice(int v) {\n    return v * 2;\n}\nint main(void) {\n    int stock = 2;\n    int *p = &stock;\n    int *box = malloc(sizeof *box);\n    *box = twice(*p);\n    printf(\"%d\\n\", *box);\n    free(box);\n    printf(\"done\\n\");\n    return 0;\n}\n";
        let doc: serde_json::Value = serde_json::from_str(&super::trace(source, "").await.unwrap()).unwrap();
        assert_eq!(doc["status"], "ok", "{doc}");
        assert_eq!(doc["stdout"], "4\ndone\n");
        assert!(values(&doc, "p").contains(&serde_json::json!(["C_PTR", "stock"])), "{doc}");
        let steps = doc["trace"].as_array().unwrap();
        // the step before the second printf already shows the first line of output, not only the last step
        assert!(steps.iter().any(|s| s["line"] == 13 && s["stdout"] == "4\n"), "{doc}");
        // twice's return value, read at its real return
        assert!(steps.iter().any(|s| s["event"] == "return" && s["stack_to_render"].as_array().unwrap().last().unwrap()["encoded_locals"]["__return__"] == 4));
        // the malloc block is drawn while it lives; after free the pointer is shown as freed memory
        assert!(steps.iter().any(|s| s["heap"].as_object().unwrap().values().any(|o| o[1].as_str().unwrap().contains("동적 할당"))));
        assert!(values(&doc, "box").iter().any(|v| v[0] == "C_NOTE" && v[1].as_str().unwrap().contains("해제된")));

        for (code, reason) in [
            ("union U { int i; float f; };\nint main(void) {\n    union U u;\n    u.i = 1;\n    return u.i;\n}\n", "union"),
            ("struct F { unsigned a : 1; };\nint main(void) {\n    struct F f;\n    f.a = 1;\n    return f.a;\n}\n", "비트필드"),
            ("int main(void) {\n    int n = 2;\n    int a[n];\n    a[0] = 1;\n    return a[0];\n}\n", "VLA"),
        ] {
            let refused: serde_json::Value = serde_json::from_str(&super::trace(code, "").await.unwrap()).unwrap();
            assert_eq!(refused["status"], "unsupported", "{refused}");
            assert!(refused["message"].as_str().unwrap().contains(reason), "{refused}");
            assert!(refused["trace"].as_array().unwrap().is_empty());
        }
        let broken: serde_json::Value = serde_json::from_str(&super::trace("int main(void) {\n    int x = ;\n}\n", "").await.unwrap()).unwrap();
        assert_eq!(broken["status"], "compile_error");
        // tcc's own report (it notices the missing expression at the next token, line 3)
        assert!(broken["problems"].as_array().unwrap().iter().any(|p| p["line"] == 3 && p["message"] == "identifier expected"), "{broken}");
    }
}
