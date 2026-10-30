//! 코드 흐름 보기: a step-by-step trace of the learner's current Java code.
//!
//! The tracing core is the java-memory-visualizer's `Instrumenter` + `Tracer` (ASM bytecode hooks for
//! lines, calls, returns, locals, statics and reachable objects), vendored unchanged in
//! `assets/java-trace/jmv` (see `assets/java-trace/PROVENANCE.md`). Its original front end compiles with
//! ECJ for Java 17 inside CheerpJ. MQ grades with the real JDK 25 source launcher, so the small adapter
//! `MqTrace.java` compiles the same `Main.java` with that same JDK's javac (`--release 25`) and starts
//! `main` with the JDK 25 launch rules. The trace is therefore of the code the grader runs, compiled by
//! the same compiler. It is an explanation aid only: grading and progress never read it.
use std::path::{Path, PathBuf};

use crate::library_sets::Jar;

/// ASM 9.9 reads JDK 25 class files (major 69); the core's own ASM 9.7.1 stops at Java 23.
pub const ASM: &[Jar] = &[
    Jar { file: "asm-9.9.jar", url: "https://repo.maven.apache.org/maven2/org/ow2/asm/asm/9.9/asm-9.9.jar",
        sha256: "03d99a74ad1ee5c71334ef67437f4ef4fe3488caa7c96d8645abc73c8e2017d4" },
    Jar { file: "asm-tree-9.9.jar", url: "https://repo.maven.apache.org/maven2/org/ow2/asm/asm-tree/9.9/asm-tree-9.9.jar",
        sha256: "42178f3775c9c63f9e5e1446747d29b4eca4d91bd6e75e5c43cfa372a47d38c6" },
];

pub const SOURCES: &[(&str, &str)] = &[
    ("Instrumenter.java", include_str!("../assets/java-trace/jmv/Instrumenter.java")),
    ("Tracer.java", include_str!("../assets/java-trace/jmv/Tracer.java")),
    ("MqTrace.java", include_str!("../assets/java-trace/jmv/MqTrace.java")),
];

/// Steps recorded before the core stops (its own default). The trace says when it stopped early.
pub const STEP_BUDGET: u32 = 1000;
const SECONDS: u64 = 20;

/// The page-side viewer: the core's `TraceView` (render.js + highlight.js, unchanged) as a classic
/// script, then the MQ dialog that opens it. The core files are ES modules; only their
/// import/export keywords are removed here so the bytes on disk stay identical to the core.
pub fn viewer_script() -> String {
    let highlight = include_str!("../assets/java-trace/core/highlight.js").replace("export function", "function");
    let render = include_str!("../assets/java-trace/core/render.js")
        .replace("import { highlightLines } from './highlight.js';", "")
        .replace("export function", "function").replace("export class", "class");
    // Each module keeps its own scope (both declare a top-level `esc`), as it would as a module.
    format!("(()=>{{if(window.MqTraceView)return;\nconst highlightLines=(()=>{{\n{highlight}\nreturn highlightLines;}})();\n(()=>{{\n{render}\nwindow.MqTraceView=TraceView;}})();\n}})();\n{}",
        include_str!("../assets/java-trace/code-flow.js"))
}

fn fingerprint() -> String {
    use sha2::{Digest, Sha256};
    let mut hash = Sha256::new();
    for (name, source) in SOURCES { hash.update(name.as_bytes()); hash.update([0]); hash.update(source.as_bytes()); hash.update([0]); }
    for jar in ASM { hash.update(jar.sha256.as_bytes()); }
    format!("{:x}", hash.finalize())[..16].to_owned()
}

/// A Windows verbatim path (`\\?\C:\...`, from canonicalize) is not understood inside a Java
/// class path, so class path entries are written in their ordinary form.
fn class_path_entry(path: PathBuf) -> PathBuf {
    let text = path.to_string_lossy().into_owned();
    match text.strip_prefix(r"\\?\") {
        Some(rest) if !rest.starts_with(r"UNC\") => PathBuf::from(rest),
        _ => path,
    }
}

async fn asm() -> Result<Vec<PathBuf>, String> {
    let mut paths = Vec::new();
    for jar in ASM {
        paths.push(class_path_entry(crate::lesson_runner::dependency(jar.file, jar.url, jar.sha256).await
            .map_err(|e| format!("코드 흐름 도구 {}를 준비하지 못했어요. 인터넷 연결을 확인하세요: {e}", jar.file))?));
    }
    Ok(paths)
}

/// Compile the tracer once per (sources, ASM) fingerprint with the same JDK 25 javac that the
/// lessons use; later traces reuse the classes.
async fn tracer(javac: &Path, asm: &[PathBuf]) -> Result<PathBuf, String> {
    let root = class_path_entry(crate::data_dir()?).join("course-tools").join(format!("java-trace-{}", fingerprint()));
    let classes = root.join("classes");
    if classes.join("jmv/MqTrace.class").is_file() { return Ok(classes); }
    let staging = root.with_extension(format!("{}.tmp", crate::issue_progress::new_id()));
    let source_dir = staging.join("src/jmv");
    std::fs::create_dir_all(&source_dir).map_err(|e| e.to_string())?;
    for (name, source) in SOURCES { std::fs::write(source_dir.join(name), source).map_err(|e| e.to_string())?; }
    let mut cmd = crate::lesson_runner::command(javac);
    cmd.args(["--release", "25", "-encoding", "UTF-8", "-nowarn", "-cp"]).arg(crate::library_sets::joined(asm))
        .arg("-d").arg(staging.join("classes"));
    for (name, _) in SOURCES { cmd.arg(source_dir.join(name)); }
    let built = crate::lesson_runner::process(cmd, &staging, "", 120).await?;
    if !built.success {
        let _ = std::fs::remove_dir_all(&staging);
        return Err(format!("코드 흐름 도구를 준비하지 못했어요. {}", built.stderr.trim()));
    }
    std::fs::create_dir_all(&root).map_err(|e| e.to_string())?;
    // Another window may have finished first; its identical classes are kept.
    if std::fs::rename(staging.join("classes"), &classes).is_err() && !classes.join("jmv/MqTrace.class").is_file() {
        return Err("코드 흐름 도구를 저장하지 못했어요.".into());
    }
    let _ = std::fs::remove_dir_all(&staging);
    Ok(classes)
}

/// Trace `source` (the editor's Main.java) with `input` as standard input. Returns the core's trace
/// document (docs/trace-format.md of the core) with `status` ok, compile_error, uncaught_exception,
/// step_limit, no_main or internal_error; an Err only when the tool itself cannot start.
pub async fn trace(source: &str, input: &str) -> Result<String, String> {
    if source.len() > 65536 || input.len() > 65536 { return Err("코드와 입력은 각각 64KB 이하여야 해요.".into()); }
    let (java, javac) = tokio::task::spawn_blocking(crate::git_practice::java_build_practice::jdk_tools).await
        .map_err(|e| e.to_string())?.map_err(|e| format!("코드 흐름 보기는 수업과 같은 JDK 25가 필요해요. {e}"))?;
    let asm = asm().await?;
    let classes = tracer(&javac, &asm).await?;
    let dir = tempfile::tempdir().map_err(|e| e.to_string())?;
    std::fs::write(dir.path().join("Main.java"), source).map_err(|e| e.to_string())?;
    std::fs::write(dir.path().join("stdin.txt"), input).map_err(|e| e.to_string())?;
    let mut paths = vec![classes];
    paths.extend(asm);
    let mut cmd = crate::lesson_runner::command(&java);
    cmd.env_remove("CLASSPATH").args(["-Xmx256m", "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8",
        // The core reads collection internals through sun.misc.Unsafe; JDK 25 would warn on stderr.
        "--sun-misc-unsafe-memory-access=allow", "-cp"]).arg(crate::library_sets::joined(&paths))
        .args(["jmv.MqTrace", "Main.java", "stdin.txt", "trace.json", &STEP_BUDGET.to_string()]);
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
    #[test]
    fn verbatim_windows_paths_become_ordinary_class_path_entries() {
        use std::path::PathBuf;
        assert_eq!(super::class_path_entry(PathBuf::from(r"\\?\C:\Temp\asm.jar")), PathBuf::from(r"C:\Temp\asm.jar"));
        assert_eq!(super::class_path_entry(PathBuf::from(r"\\?\UNC\host\share\a.jar")), PathBuf::from(r"\\?\UNC\host\share\a.jar"));
        assert_eq!(super::class_path_entry(PathBuf::from("/tmp/asm.jar")), PathBuf::from("/tmp/asm.jar"));
    }

    #[test]
    fn pinned_asm_comes_from_maven_central_with_a_hash() {
        for jar in super::ASM {
            assert!(jar.url.starts_with("https://repo.maven.apache.org/maven2/org/ow2/asm/") && jar.url.ends_with(jar.file));
            assert_eq!(jar.sha256.len(), 64);
        }
    }

    /// The vendored core stays byte-identical to java-memory-visualizer 6db1560, except the recorded MQ change to render.js (PROVENANCE.md).
    #[test]
    fn vendored_core_matches_the_recorded_upstream_bytes() {
        use sha2::{Digest, Sha256};
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("assets/java-trace");
        for (file, expected) in [
            ("jmv/Instrumenter.java", "332ad452513da7dbe2f0f96bf2a71f515ca0bf0cbf7276b517866416c4a64cbf"),
            ("jmv/Tracer.java", "bc213569cd2bf335da08f2b24dcc7b799af1f56a642f60321dd3937b03317e20"),
            ("core/highlight.js", "092f3fc7f041231d8cf8367115c64f5167ea94e412374bec287c826b7e70e1e4"),
            // MQ changes for Python and C traces (PROVENANCE.md); upstream b4fcc7e0…a7.
            ("core/render.js", "8f465761ca11e25acfe912f18ba493e15c4b995da9f0dae6fe15abf3ac702d45"),
        ] {
            let bytes = std::fs::read(root.join(file)).unwrap();
            assert_eq!(format!("{:x}", Sha256::digest(&bytes)), expected, "{file}");
        }
        let script = super::viewer_script();
        assert!(!script.contains("\nimport ") && !script.contains("export class") && script.contains("window.MqTraceView=TraceView"));
        // The page evaluates this one script; a duplicate top-level name would leave mqCodeFlow undefined.
        if std::process::Command::new("node").arg("--version").output().is_ok_and(|o| o.status.success()) {
            let file = tempfile::Builder::new().suffix(".js").tempfile().unwrap();
            std::fs::write(file.path(), &script).unwrap();
            let checked = std::process::Command::new("node").arg("--check").arg(file.path()).output().unwrap();
            assert!(checked.status.success(), "{}", String::from_utf8_lossy(&checked.stderr));
        }
    }

    /// Every lesson step that offers 코드 흐름 보기: the starter and the solution trace on the real path,
    /// the trace's output is the graded run's output, and the step reaches a written method or constructor.
    #[tokio::test]
    #[ignore="Needs JDK 25 and the pinned ASM download on first use"]
    async fn every_code_flow_step_traces_its_starter_and_solution_like_the_grader() {
        let mut traced=0;
        for key in ["engineer-java-references","engineer-java-static","engineer-java-polymorphism","engineer-java-flow"] {
            let lesson:serde_json::Value=serde_json::from_str(crate::lesson_registry::find(key).unwrap().lesson).unwrap();
            for task in lesson["tasks"].as_array().unwrap().iter().filter(|t|t["code_flow"]==true) {
                for field in ["starter_code","solution"] {
                    let source=task[field].as_str().unwrap();
                    let doc:serde_json::Value=serde_json::from_str(&super::trace(source,"").await.unwrap()).unwrap();
                    let graded=crate::java::run(source,"").await.unwrap();
                    let label=format!("{key} {} {field}",task["id"]);
                    if graded.success {
                        assert_eq!(doc["status"],"ok","{label}: {doc}");
                        assert_eq!(doc["stdout"].as_str().unwrap().replace("\r\n","\n"),graded.stdout,"{label}");
                    } else {
                        assert_ne!(doc["status"],"ok","{label}");
                    }
                    let steps=doc["trace"].as_array().unwrap();
                    assert!(!steps.is_empty(),"{label}");
                    assert!(steps.iter().all(|s|s["line"].as_i64().is_some_and(|l|l>=1&&l as usize<=source.lines().count())),"{label}: lines stay in the editor's code");
                    traced+=1;
                }
            }
        }
        // references 4, static 7, polymorphism 4, flow 1 steps; starter and solution each.
        assert_eq!(traced,32);
    }

    fn frames(step:&serde_json::Value)->Vec<serde_json::Value> {step["stack_to_render"].as_array().cloned().unwrap_or_default()}
    fn local(step:&serde_json::Value,name:&str)->Option<serde_json::Value> {frames(step).first().and_then(|f|f["encoded_locals"].get(name).cloned())}

    /// The real JDK 25 + pinned ASM path on the learner's code: aliasing, separate objects, an implicit
    /// and an explicit no-argument constructor, a static counter, dispatch, and the grader's output.
    #[tokio::test]
    #[ignore="Needs JDK 25 and the pinned ASM download on first use"]
    async fn traces_the_graded_jdk25_program_with_references_constructors_static_and_dispatch() {
        let source="class Box {\n    int count;\n}\n\nclass Ticket {\n    static int issued = 0;\n    int number;\n    Ticket() {\n        issued = issued + 1;\n        number = issued;\n    }\n}\n\nclass Rule {\n    int rate() { return 2; }\n}\n\nclass Bonus extends Rule {\n    @Override int rate() { return 7; }\n}\n\nvoid main() {\n    Box a = new Box();\n    Box b = a;\n    b.count = 7;\n    Box c = new Box();\n    Ticket first = new Ticket();\n    Ticket second = new Ticket();\n    Rule rule = new Bonus();\n    System.out.println(a.count + \":\" + c.count + \":\" + second.number + \":\" + rule.rate());\n}\n";
        let doc:serde_json::Value=serde_json::from_str(&super::trace(source,"").await.unwrap()).unwrap();
        assert_eq!(doc["status"],"ok","{doc}");
        let steps=doc["trace"].as_array().unwrap();
        // The first recorded step is main itself, not the launcher's own `new Main()`.
        assert_eq!((steps[0]["event"].as_str(),steps[0]["line"].as_i64()),(Some("call"),Some(23)));
        let graded=crate::java::run(source,"").await.unwrap();
        assert!(graded.success);
        assert_eq!(doc["stdout"].as_str().unwrap().replace("\r\n","\n"),graded.stdout);
        // b = a: both names hold the same object; c is another one with its own count.
        let after_c=steps.iter().find(|s|local(s,"c").is_some()).unwrap();
        let (a,b,c)=(local(after_c,"a").unwrap(),local(after_c,"b").unwrap(),local(after_c,"c").unwrap());
        assert_eq!(a,b);assert_ne!(a,c);
        let id=|v:&serde_json::Value|v[1].to_string();
        assert_eq!(after_c["heap"][id(&a)],serde_json::json!(["INSTANCE","Box",["count",7]]));
        assert_eq!(after_c["heap"][id(&c)],serde_json::json!(["INSTANCE","Box",["count",0]]));
        // Box has no written constructor: the compiler's no-argument Box() is still a real call.
        let constructors:Vec<_>=steps.iter().filter(|s|s["event"]=="call").filter_map(|s|frames(s).last().cloned()).filter(|f|f["func_name"]=="<init>").collect();
        assert!(constructors.iter().any(|f|f["class"]=="Box"),"{constructors:?}");
        // The written Ticket() runs its body lines once per new Ticket(); the static counter is shared.
        let ticket_lines:Vec<i64>=steps.iter().filter(|s|frames(s).last().is_some_and(|f|f["func_name"]=="<init>"&&f["class"]=="Ticket")&&s["event"]=="step_line").map(|s|s["line"].as_i64().unwrap()).collect();
        assert_eq!(ticket_lines,vec![9,10,11,9,10,11]);
        let issued:Vec<i64>=steps.iter().filter_map(|s|s["globals"]["Ticket.issued"].as_i64()).collect();
        assert!(issued.contains(&1)&&issued.last()==Some(&2));
        // rule is declared as Rule but holds a Bonus: the overriding Bonus.rate is the frame that runs.
        let rate=steps.iter().filter_map(|s|frames(s).last().cloned()).find(|f|f["func_name"]=="rate").unwrap();
        assert_eq!(rate["class"],"Bonus");

        // A classic static main and a compile error, with the javac line.
        let classic=serde_json::from_str::<serde_json::Value>(&super::trace("public class Main {\n    public static void main(String[] args) {\n        int x = 2;\n        System.out.println(x);\n    }\n}\n","").await.unwrap()).unwrap();
        assert_eq!(classic["status"],"ok");assert_eq!(classic["stdout"].as_str().unwrap().trim(),"2");
        let broken=serde_json::from_str::<serde_json::Value>(&super::trace("void main() {\n    int x = ;\n}\n","").await.unwrap()).unwrap();
        assert_eq!(broken["status"],"compile_error");
        assert!(broken["problems"].as_array().unwrap().iter().any(|p|p["line"]==2&&p["error"]==true),"{broken}");
    }
}

