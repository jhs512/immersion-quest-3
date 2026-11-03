//! C++ and Rust: running, grading and 코드 흐름 보기 with one compiler command (`assets/native-trace/`).
//!
//! `native_flow.py` compiles the learner's unmodified source with the same command for `run` (which grading uses) and
//! `trace`, so the traced binary is the graded one. `trace` records that program once under LLDB: real stops, real
//! memory, typed values. LLDB still shows a moved Rust binding's old stack bytes as a value, so moves come from the
//! same rustc's MIR (`rust_mir.py`) and moved bindings are drawn as notes, never as live values.
//!
//! macOS: Xcode's `clang++` and `lldb` through `xcrun`, and rustc 1.95.0 installed by the official rustup into MQ's
//! own folder (the learner's rustup, if any, is not used or changed).
//! Windows: every step runs in one local image built from the official `rust:1.95.0-slim-trixie` digest plus
//! Debian's clang/lldb 19 (`Dockerfile`); containers have no network, no capabilities and the default seccomp
//! profile, and see only this attempt's temporary folder.
use crate::runner::Execution;
use std::path::{Path,PathBuf};

#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum NativeLanguage {Cpp,Rust}
impl NativeLanguage {
    fn key(self)->&'static str {match self {Self::Cpp=>"cpp",Self::Rust=>"rust"}}
    fn label(self)->&'static str {match self {Self::Cpp=>"C++",Self::Rust=>"Rust"}}
}

const TOOL:&[(&str,&str)]=&[
    ("native_flow.py",include_str!("../assets/native-trace/native_flow.py")),
    ("native_lldb.py",include_str!("../assets/native-trace/native_lldb.py")),
    ("rust_mir.py",include_str!("../assets/native-trace/rust_mir.py")),
];
const DOCKERFILE:&str=include_str!("../assets/native-trace/Dockerfile");
const OWNER_LABEL:&str="mq.owner=mq-native-trace";
const RUN_SECONDS:u64=40;
const TRACE_SECONDS:u64=150;
const RUST_TOOLCHAIN:&str="1.95.0";
const RUSTUP_VERSION:&str="1.29.2";
const RUSTUP_SHA256:&[(&str,&str)]=&[
    ("aarch64-apple-darwin","f7c7e11eb2e07f006e532a8aaac77b32f4527d305ac386c0c633ca6133d35ca9"),
    ("x86_64-apple-darwin","b9610730ddeef52765723847866fd1e3540b2bf7d5ab0c324aa143a5edf25ba0"),
];

/// Compile and run `source` with `input` on standard input, as grading does.
/// A compile failure is `state: "compile_error"` with the compiler's report in `stderr`.
pub async fn run(language:NativeLanguage,source:&str,input:&str)->Result<Execution,String> {
    let dir=stage(source,input)?;
    let run=invoke("run",language,dir.path(),input,RUN_SECONDS).await?;
    let case=dir.path().join("case");
    let Ok(text)=std::fs::read_to_string(case.join("compile.json")) else {
        return Err(format!("{} 실행 도구가 시작되지 못했어요. {}",language.label(),last_line(&run.stderr)));
    };
    let compiled:serde_json::Value=serde_json::from_str(&text).map_err(|e|e.to_string())?;
    if compiled["success"]!=true {
        return Ok(Execution{stdout:String::new(),stderr:compiled["stderr"].as_str().unwrap_or("").into(),success:false,state:"compile_error".into(),artifacts:vec![]});
    }
    Ok(run)
}

/// Trace `source` with `input`. The document follows the TraceView contract (`status` ok, compile_error,
/// uncaught_exception, step_limit or unsupported); Err only when the tool itself cannot run.
pub async fn trace(language:NativeLanguage,source:&str,input:&str)->Result<String,String> {
    let dir=stage(source,input)?;
    let run=invoke("trace",language,dir.path(),"",TRACE_SECONDS).await?;
    if run.state=="timeout" {return Err(format!("코드 흐름을 {TRACE_SECONDS}초 안에 기록하지 못했어요. 반복이 끝나는지 확인하세요."))}
    let document=std::fs::read_to_string(dir.path().join("case/native_flow.json"))
        .map_err(|_|format!("코드 흐름을 기록하지 못했어요. {}",last_line(&run.stderr)))?;
    serde_json::from_str::<serde_json::Value>(&document).map_err(|e|format!("코드 흐름 기록을 읽지 못했어요: {e}"))?;
    Ok(document)
}

/// Install what `language` needs here (Windows: the image; macOS: rustc for Rust), then check it runs.
pub async fn prepare(language:NativeLanguage)->Result<String,String> {
    #[cfg(target_os="macos")] if language==NativeLanguage::Rust {rust_toolchain().await?;}
    #[cfg(not(target_os="macos"))] image().await?;
    inspect(language).await
}

/// The environment check: compiles and runs a tiny program. Installs nothing.
pub async fn inspect(language:NativeLanguage)->Result<String,String> {
    #[cfg(not(target_os="macos"))] if !image_present()? {return Err(format!("{} 실행 환경(Docker 이미지)이 없어요. 환경 설치로 준비하세요.",language.label()))}
    #[cfg(target_os="macos")] if language==NativeLanguage::Rust&&!rustc_path()?.is_file() {return Err(NO_RUSTC.into())}
    let source=match language {
        NativeLanguage::Cpp=>"#include <iostream>\nint main() { std::cout << \"MQ_NATIVE_READY\"; }\n",
        NativeLanguage::Rust=>"fn main() { print!(\"MQ_NATIVE_READY\"); }\n",
    };
    let result=run(language,source,"").await?;
    if result.success&&result.stdout=="MQ_NATIVE_READY" {Ok(format!("{} · 컴파일과 실행을 확인했어요.",language.label()))}
    else {Err(format!("{} 실행을 확인하지 못했어요. {}",language.label(),result.stderr))}
}

fn last_line(text:&str)->&str {text.lines().rev().find(|l|!l.trim().is_empty()).unwrap_or("").trim()}

fn stage(source:&str,input:&str)->Result<tempfile::TempDir,String> {
    if source.len()>65536||input.len()>65536 {return Err("코드와 입력은 각각 64KB 이하여야 해요.".into())}
    let dir=tempfile::tempdir().map_err(|e|e.to_string())?;
    let (tool,case)=(dir.path().join("tool"),dir.path().join("case"));
    for d in [&tool,&case] {std::fs::create_dir_all(d).map_err(|e|e.to_string())?;}
    for (name,text) in TOOL {std::fs::write(tool.join(name),text).map_err(|e|e.to_string())?;}
    std::fs::write(case.join("src"),source).map_err(|e|e.to_string())?;
    std::fs::write(case.join("stdin.txt"),input).map_err(|e|e.to_string())?;
    Ok(dir)
}

#[cfg(target_os="macos")]
async fn invoke(mode:&str,language:NativeLanguage,dir:&Path,input:&str,seconds:u64)->Result<Execution,String> {
    let mut cmd=crate::lesson_runner::command(crate::runner::python_executable());
    cmd.args(["-I","-X","utf8"]).arg(dir.join("tool/native_flow.py")).arg(mode).arg(dir.join("case")).arg(language.key())
        .env("MQ_CXX","xcrun clang++").env("MQ_LLDB","xcrun lldb").env("MQ_TRACE_SECONDS",(seconds-15).to_string());
    if language==NativeLanguage::Rust {
        if !rustc_path()?.is_file() {return Err(NO_RUSTC.into())}
        let (rustup,cargo)=rust_homes()?;
        // native_flow.py splits MQ_* like a shell; MQ's data folder is under "Application Support".
        let quoted=format!("'{}'",rustc_path()?.display().to_string().replace('\'',"'\\''"));
        cmd.env("MQ_RUSTC",quoted).env("RUSTUP_HOME",rustup).env("CARGO_HOME",cargo).env("RUSTUP_TOOLCHAIN",RUST_TOOLCHAIN);
    }
    crate::lesson_runner::process(cmd,&dir.join("case"),input,seconds).await
}

#[cfg(not(target_os="macos"))]
async fn invoke(mode:&str,language:NativeLanguage,dir:&Path,input:&str,seconds:u64)->Result<Execution,String> {
    let cli=docker_cli()?;
    let name=format!("mq-native-{}",crate::issue_progress::new_id());
    let tool=format!("{}:/tool:ro",dir.join("tool").display());
    let case=format!("{}:/case",dir.join("case").display());
    // `timeout` is the container's first process: if MQ itself dies, the container still ends and `--rm` removes it.
    let limit=(seconds+5).to_string();
    let mut cmd=crate::lesson_runner::command(&cli);
    cmd.args(["run","--rm","-i","--name",&name,"--label",OWNER_LABEL,"--network","none","--cap-drop","ALL",
        "--security-opt","no-new-privileges","--memory","512m","--pids-limit","128","--cpus","2","-v",&tool,"-v",&case,&image_tag(),
        "timeout","-s","KILL",&limit,"python3","/tool/native_flow.py",mode,"/case",language.key()]);
    let result=crate::lesson_runner::process(cmd,dir,input,seconds).await;
    if !matches!(&result,Ok(run) if run.state!="timeout") {
        // The docker client was stopped; the container it started is removed by its own name only.
        let mut remove=crate::lesson_runner::command(&cli);remove.args(["rm","-f",&name]);
        let _=crate::lesson_runner::process(remove,dir,"",30).await;
    }
    result
}

#[cfg(not(target_os="macos"))]
fn docker_cli()->Result<PathBuf,String> {
    crate::docker_lab::cli().ok_or_else(||format!("C++·Rust 실습에는 Docker Desktop이 필요해요. 설치한 뒤 실행하세요. 설치 안내: {}",crate::docker_lab::INSTALL_GUIDE))
}

#[cfg(not(target_os="macos"))]
fn image_tag()->String {
    use sha2::{Digest,Sha256};
    format!("mq-native-trace:{}",&format!("{:x}",Sha256::digest(DOCKERFILE.as_bytes()))[..12])
}

#[cfg(not(target_os="macos"))]
fn image_present()->Result<bool,String> {
    let output=std::process::Command::new(docker_cli()?).args(["image","inspect","--format","{{.Id}}",&image_tag()]).output().map_err(|e|e.to_string())?;
    Ok(output.status.success())
}

/// Build the image from the embedded Dockerfile. Only this build uses the network (base pull and apt).
#[cfg(not(target_os="macos"))]
async fn image()->Result<(),String> {
    if image_present()? {return Ok(())}
    let cli=docker_cli()?;
    let dir=tempfile::tempdir().map_err(|e|e.to_string())?;
    let mut cmd=crate::lesson_runner::command(&cli);
    cmd.args(["build","--label",OWNER_LABEL,"-t",&image_tag(),"-"]);
    let built=crate::lesson_runner::process(cmd,dir.path(),DOCKERFILE,900).await?;
    if built.success {Ok(())} else {Err(format!("C++·Rust 실행 이미지를 만들지 못했어요. {}",last_line(&built.stderr)))}
}

#[cfg(target_os="macos")]
fn rust_homes()->Result<(PathBuf,PathBuf),String> {
    // Like MOLIP_TCC: a validation run can reuse a toolchain installed outside its fresh data folder.
    let root=match std::env::var_os("MOLIP_RUST_HOME") {Some(path)=>PathBuf::from(path),None=>crate::data_dir()?.join("course-tools/rust")};
    Ok((root.join("rustup"),root.join("cargo")))
}

#[cfg(target_os="macos")]
const NO_RUSTC:&str="Rust 컴파일러가 없어요. 환경 설치로 준비하세요.";

#[cfg(target_os="macos")]
fn rustc_path()->Result<PathBuf,String> {Ok(rust_homes()?.1.join("bin/rustc"))}

/// rustc 1.95.0 through the official rustup-init (pinned by hash) into MQ's folder; PATH and profiles are untouched.
#[cfg(target_os="macos")]
async fn rust_toolchain()->Result<(),String> {
    use sha2::{Digest,Sha256};
    let (rustup,cargo)=rust_homes()?;
    let rustc=rustc_path()?;
    if rustc.is_file() {
        let mut check=crate::lesson_runner::command(&rustc);check.arg("--version").env("RUSTUP_HOME",&rustup).env("CARGO_HOME",&cargo).env("RUSTUP_TOOLCHAIN",RUST_TOOLCHAIN);
        if crate::lesson_runner::process(check,Path::new("/"),"",60).await?.stdout.starts_with(&format!("rustc {RUST_TOOLCHAIN} ")) {return Ok(())}
    }
    let target=if cfg!(target_arch="aarch64"){"aarch64-apple-darwin"}else{"x86_64-apple-darwin"};
    let expected=RUSTUP_SHA256.iter().find(|(t,_)|*t==target).map(|(_,h)|*h).ok_or("이 Mac의 Rust 설치 파일을 찾지 못했어요.")?;
    let url=format!("https://static.rust-lang.org/rustup/archive/{RUSTUP_VERSION}/{target}/rustup-init");
    let bytes=crate::github_player::background(move ||{
        let agent:ureq::Agent=ureq::Agent::config_builder().tls_config(ureq::tls::TlsConfig::builder().provider(ureq::tls::TlsProvider::NativeTls).build())
            .timeout_global(Some(std::time::Duration::from_secs(300))).build().into();
        let bytes=agent.get(&url).call().map_err(|e|e.to_string())?.body_mut().with_config().limit(40_000_000).read_to_vec().map_err(|e|e.to_string())?;
        if format!("{:x}",Sha256::digest(&bytes))!=expected {return Err("Rust 설치 파일의 해시가 맞지 않아요.".into())}
        Ok(bytes)
    }).await?;
    let dir=tempfile::tempdir().map_err(|e|e.to_string())?;
    let installer=dir.path().join("rustup-init");
    std::fs::write(&installer,bytes).map_err(|e|e.to_string())?;
    {use std::os::unix::fs::PermissionsExt;std::fs::set_permissions(&installer,std::fs::Permissions::from_mode(0o700)).map_err(|e|e.to_string())?;}
    let mut cmd=crate::lesson_runner::command(&installer);
    cmd.args(["-y","--no-modify-path","--profile","minimal","--default-toolchain",RUST_TOOLCHAIN]).env("RUSTUP_HOME",&rustup).env("CARGO_HOME",&cargo);
    let installed=crate::lesson_runner::process(cmd,dir.path(),"",900).await?;
    if installed.success&&rustc.is_file() {Ok(())} else {Err(format!("Rust를 설치하지 못했어요. {}",last_line(&installed.stderr)))}
}

#[cfg(test)]
mod tests {
    use super::*;
    const OWNERSHIP:&str="#[derive(Debug, Clone)]\nstruct Item {\n    name: String,\n    stock: u32,\n}\n\nfn take(item: Item) -> u32 {\n    item.stock\n}\n\nfn main() {\n    let first = String::from(\"pen\");\n    let moved = first;\n    let item = Item { name: moved.clone(), stock: 3 };\n    let stock = take(item);\n    println!(\"{} {}\", moved, stock);\n}\n";

    fn locals<'a>(doc:&'a serde_json::Value,name:&str)->Vec<(i64,&'a serde_json::Value)> {
        doc["trace"].as_array().unwrap().iter().flat_map(|s|s["stack_to_render"].as_array().unwrap().iter()
            .filter_map(move |f|f["encoded_locals"].get(name).map(|v|(s["line"].as_i64().unwrap(),v)))).collect()
    }
    fn moved(value:&serde_json::Value)->bool {value[0]=="C_NOTE"&&value[1].as_str().unwrap_or("").contains("옮겨진 값")}

    #[tokio::test]
    #[ignore = "Needs Docker (Windows) or Xcode tools and network for the first Rust install (macOS)"]
    async fn rust_runs_grades_and_traces_moves_from_one_build() {
        prepare(NativeLanguage::Rust).await.unwrap();
        let executed=run(NativeLanguage::Rust,OWNERSHIP,"").await.unwrap();
        assert_eq!((executed.success,executed.stdout.as_str()),(true,"pen 3\n"),"{}",executed.stderr);
        let doc:serde_json::Value=serde_json::from_str(&trace(NativeLanguage::Rust,OWNERSHIP,"").await.unwrap()).unwrap();
        assert_eq!(doc["status"],"ok","{doc}");
        assert_eq!(doc["stdout"],executed.stdout);
        assert_eq!(doc["verification"]["program_runs"],1);
        assert!(locals(&doc,"first").iter().filter(|(line,_)|*line>13).all(|(_,v)|moved(v)),"{doc}");
        assert!(locals(&doc,"item").iter().any(|(line,v)|*line==9&&moved(v)),"caller's item is moved while take runs: {doc}");
        // rust-values 1: a body of macros only has no statement of its own in main.rs but the block at the signature.
        let printed="fn main() {\n    // note\n    println!(\"hello\");\n}\n";
        let doc:serde_json::Value=serde_json::from_str(&trace(NativeLanguage::Rust,printed,"").await.unwrap()).unwrap();
        let lines:Vec<_>=doc["trace"].as_array().unwrap().iter().map(|s|s["line"].as_i64().unwrap()).collect();
        assert_eq!((doc["status"].as_str(),doc["stdout"].as_str(),lines.first()),(Some("ok"),Some("hello\n"),Some(&3)),"{doc}");
        let broken=run(NativeLanguage::Rust,"fn main() {\n    let a = String::new();\n    let b = a;\n    println!(\"{}\", a);\n}\n","").await.unwrap();
        assert_eq!(broken.state,"compile_error");
        assert!(broken.stderr.contains("E0382"),"{}",broken.stderr);
    }

    /// A Mac without MQ's rustc tells the learner to install it, not a Python FileNotFoundError.
    #[cfg(target_os="macos")]
    #[tokio::test]
    async fn rust_without_the_toolchain_asks_for_the_environment_install() {
        let empty=tempfile::tempdir().unwrap();
        let previous=std::env::var_os("MOLIP_RUST_HOME");
        std::env::set_var("MOLIP_RUST_HOME",empty.path());
        let result=run(NativeLanguage::Rust,"fn main() {}\n","").await;
        match previous {Some(path)=>std::env::set_var("MOLIP_RUST_HOME",path),None=>std::env::remove_var("MOLIP_RUST_HOME")}
        assert_eq!(result.err().as_deref(),Some(NO_RUSTC));
    }

    #[tokio::test]
    #[ignore = "Needs Docker (Windows) or Xcode tools (macOS)"]
    async fn cpp_runs_and_traces_heap_lifetimes() {
        prepare(NativeLanguage::Cpp).await.unwrap();
        let source="#include <iostream>\n#include <memory>\nint main() {\n    int stock = 2;\n    int &alias = stock;\n    int *raw = new int(4);\n    auto owned = std::make_unique<int>(5);\n    delete raw;\n    std::cout << alias + *owned << \"\\n\";\n}\n";
        let executed=run(NativeLanguage::Cpp,source,"").await.unwrap();
        assert_eq!(executed.stdout,"7\n","{}",executed.stderr);
        let doc:serde_json::Value=serde_json::from_str(&trace(NativeLanguage::Cpp,source,"").await.unwrap()).unwrap();
        assert_eq!(doc["status"],"ok","{doc}");
        assert_eq!(doc["stdout"],executed.stdout);
        assert!(locals(&doc,"alias").iter().any(|(_,v)|**v==serde_json::json!(["C_PTR","stock"])),"{doc}");
        assert!(locals(&doc,"raw").iter().any(|(line,v)|*line==9&&v[1].as_str().unwrap_or("").contains("해제된")),"{doc}");
        let endless=run(NativeLanguage::Cpp,"int main() {\n    for (;;) {}\n}\n","").await.unwrap();
        assert_eq!(endless.state,"timeout");
    }
}
