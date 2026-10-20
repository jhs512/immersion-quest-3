//! Per-user learning tools. No system PATH, Java installation, or workspace is replaced.
use std::{path::{Path,PathBuf},time::Duration,io::{Read,Write}};
use tokio::sync::mpsc::UnboundedSender;

fn platform(os:&str,arch:&str)->Result<(&'static str,&'static str),String> {
    match (os,arch) {
        ("windows","x86_64")=>Ok(("windows","x64")),
        ("macos","aarch64")=>Ok(("mac","aarch64")),
        ("macos","x86_64")=>Ok(("mac","x64")),
        ("linux","x86_64")=>Ok(("linux","x64")),
        ("linux","aarch64")=>Ok(("linux","aarch64")),
        _=>Err("이 OS·CPU의 Java 자동 설치는 아직 지원하지 않아요.".into()),
    }
}

fn java_in(folder:&Path)->PathBuf {
    folder.join(if cfg!(target_os="macos"){"Contents/Home/bin/java"}else if cfg!(windows){"bin/java.exe"}else{"bin/java"})
}

fn managed_at(root:&Path)->Option<PathBuf> {
    let name:String=serde_json::from_slice(&std::fs::read(root.join("jdk25-current.json")).ok()?).ok()?;
    if !name.starts_with("jdk25-")||name.len()>100||!name.bytes().all(|c|c.is_ascii_alphanumeric()||c==b'-'){return None;}
    let path=java_in(&root.join(name));path.is_file().then_some(path)
}

pub fn managed_java()->Option<PathBuf> {managed_at(&crate::data_dir().ok()?.join("toolchains"))}

pub async fn inspect_java()->Result<String,String> {
    #[cfg(target_os="macos")]
    if crate::java::executable()=="java" {
        let found=crate::doctor::probe_with_timeout("/usr/bin/which",&["java"],Duration::from_secs(10)).await.unwrap_or_default();
        if String::from_utf8_lossy(&found).trim()=="/usr/bin/java"{return Err("JDK 25가 없어요. 환경 설치로 준비하세요.".into());}
    }
    let text=crate::java::version().await?;
    let tools=tokio::task::spawn_blocking(crate::git_practice::java_build_practice::jdk_tools).await.map_err(|e|e.to_string())??;
    verify_java(&tools.0).await?;
    Ok(format!("{} · {}",text.lines().next().unwrap_or("JDK 25"),tools.0.display()))
}

async fn verify_java(java:&Path)->Result<(),String> {
    let java=java.to_string_lossy().into_owned();
    let version=crate::doctor::probe_with_timeout(&java,&["--version"],Duration::from_secs(20)).await?;
    if !crate::java::is_jdk25(&String::from_utf8_lossy(&version)){return Err("JDK 25가 아니에요.".into());}
    let compiler=Path::new(&java).with_file_name(if cfg!(windows){"javac.exe"}else{"javac"});
    let compiler=compiler.to_string_lossy().into_owned();
    let version=crate::doctor::probe_with_timeout(&compiler,&["--version"],Duration::from_secs(20)).await?;
    if !String::from_utf8_lossy(&version).trim().starts_with("javac 25"){return Err("같은 JDK 25의 컴파일러가 필요해요.".into());}
    let temporary=tempfile::tempdir().map_err(|e|e.to_string())?;
    let source=temporary.path().join("Main.java");
    std::fs::write(&source,"class Main {public static void main(String[] args){System.out.print(\"MQ3_JAVA_READY\");}}").map_err(|e|e.to_string())?;
    let result=crate::doctor::probe_with_timeout(&java,&["--source","25",&source.to_string_lossy()],Duration::from_secs(30)).await?;
    if result!=b"MQ3_JAVA_READY"{return Err("Java 예제 실행을 확인하지 못했어요.".into());}Ok(())
}

fn package(metadata:&serde_json::Value)->Result<(&str,&str,u64),String> {
    let package=&metadata[0]["binary"]["package"];
    let url=package["link"].as_str().ok_or("JDK 다운로드 주소가 없어요.")?;
    let checksum=package["checksum"].as_str().ok_or("JDK 검증 정보가 없어요.")?;
    let size=package["size"].as_u64().ok_or("JDK 파일 크기를 확인하지 못했어요.")?;
    if !url.starts_with("https://github.com/adoptium/temurin25-binaries/releases/download/")||checksum.len()!=64||!checksum.bytes().all(|c|c.is_ascii_hexdigit())||size==0||size>512*1024*1024 {
        return Err("JDK 다운로드 정보를 확인하지 못했어요.".into());
    }Ok((url,checksum,size))
}

async fn download_java(root:&Path,report:&UnboundedSender<String>)->Result<PathBuf,String> {
    use sha2::{Digest,Sha256};
    let (os,arch)=platform(std::env::consts::OS,std::env::consts::ARCH)?;
    let _=report.send(format!("Java · {os}/{arch}용 JDK 25를 확인해요."));
    let curl=if cfg!(windows){"curl.exe"}else{"/usr/bin/curl"};
    let api=format!("https://api.adoptium.net/v3/assets/latest/25/hotspot?architecture={arch}&image_type=jdk&os={os}&vendor=eclipse");
    let raw=crate::doctor::probe_with_timeout(curl,&["-fsSL","--connect-timeout","20","--max-time","60",&api],Duration::from_secs(70)).await?;
    let metadata:serde_json::Value=serde_json::from_slice(&raw).map_err(|e|e.to_string())?;
    let (url,checksum,size)=package(&metadata)?;
    std::fs::create_dir_all(root).map_err(|e|format!("JDK 설치 폴더 생성 · {}: {e}",root.display()))?;
    let pending=tempfile::Builder::new().prefix("jdk25-").tempdir_in(root).map_err(|e|e.to_string())?;
    let archive=pending.path().join(if cfg!(windows){"jdk.zip"}else{"jdk.tar.gz"});
    let _=report.send(format!("Java · 약 {} MB를 받아요.",size/1_048_576));
    crate::doctor::run_logged(report,curl,&["-fL","--proto","=https","--proto-redir","=https","--retry","2","--connect-timeout","20","--max-time","1200","--output",&archive.to_string_lossy(),url],None).await?;
    let downloaded=archive.clone();let checksum=checksum.to_owned();
    tokio::task::spawn_blocking(move||{
        let mut file=std::fs::File::open(downloaded).map_err(|e|e.to_string())?;
        if file.metadata().map_err(|e|e.to_string())?.len()!=size{return Err("JDK 파일 크기가 일치하지 않아요.".to_string());}
        let mut digest=Sha256::new();let mut block=[0u8;65536];
        loop {let count=file.read(&mut block).map_err(|e|e.to_string())?;if count==0{break;}digest.update(&block[..count]);}
        if format!("{:x}",digest.finalize())!=checksum.to_ascii_lowercase(){return Err("JDK 파일의 검증값이 일치하지 않아요.".into());}Ok(())
    }).await.map_err(|e|e.to_string())??;
    let extracted=pending.path().join("unpacked");std::fs::create_dir(&extracted).map_err(|e|e.to_string())?;
    let tar=if cfg!(windows){std::env::var("SystemRoot").map(|p|PathBuf::from(p).join("System32/tar.exe")).unwrap_or_else(|_|"tar.exe".into())}else{"/usr/bin/tar".into()};
    crate::doctor::run_logged(report,&tar.to_string_lossy(),&["-xf",&archive.to_string_lossy(),"-C",&extracted.to_string_lossy()],None).await?;
    let folder=std::fs::read_dir(&extracted).map_err(|e|e.to_string())?.filter_map(Result::ok).map(|e|e.path()).find(|p|java_in(p).is_file()).ok_or("압축 파일에서 JDK를 찾지 못했어요.")?;
    verify_java(&java_in(&folder)).await?;
    // Commit only a verified installation. Existing tools remain available on failure.
    let name=format!("jdk25-{}",crate::issue_progress::new_id());
    let canonical_root=root.canonicalize().map_err(|e|e.to_string())?;
    if !folder.canonicalize().map_err(|e|e.to_string())?.starts_with(&canonical_root)||root.join(&name).exists(){return Err("앱 전용 설치 경로를 확인하세요.".into());}
    std::fs::rename(&folder,root.join(&name)).map_err(|e|format!("JDK 설치 확정 · {} → {}: {e}",folder.display(),root.join(&name).display()))?;
    let mut marker=tempfile::NamedTempFile::new_in(root).map_err(|e|e.to_string())?;
    marker.write_all(&serde_json::to_vec(&name).unwrap()).map_err(|e|e.to_string())?;
    marker.persist(root.join("jdk25-current.json")).map_err(|e|format!("JDK 선택 정보 저장 · {}: {e}",root.join("jdk25-current.json").display()))?;
    Ok(java_in(&root.join(name)))
}

pub async fn prepare_java(report:&UnboundedSender<String>)->Result<String,String> {
    if let Ok(ready)=inspect_java().await{return Ok(format!("Java · 준비되어 있어요. {ready}"));}
    let java=download_java(&crate::data_dir()?.join("toolchains"),report).await?;
    inspect_java().await?;
    Ok(format!("Java · 설치와 실행을 확인했어요. {}",java.display()))
}

pub async fn inspect_c()->Result<String,String> {
    #[cfg(target_os="macos")]
    crate::doctor::probe_with_timeout("/usr/bin/xcode-select",&["-p"],Duration::from_secs(10)).await.map_err(|_|"C 실행 도구가 없어요. 환경 설치로 준비하세요.".to_string())?;
    crate::lesson_runner::inspect_c().await
}

pub async fn prepare_c(_report:&UnboundedSender<String>)->Result<String,String> {
    if let Ok(ready)=inspect_c().await{return Ok(ready);}
    #[cfg(target_os="macos")]
    {
        let _=_report.send("C · macOS 설치 창을 열어요. 설치와 약관 확인을 완료한 뒤 다시 검사하세요.".into());
        crate::doctor::run_logged(_report,"/usr/bin/xcode-select",&["--install"],None).await?;
        return Err("C · macOS 설치 창에서 설치를 완료한 뒤 다시 검사하세요.".into());
    }
    #[cfg(not(target_os="macos"))]
    {crate::lesson_runner::prepare_c().await}
}

#[cfg(test)]
mod tests {
    #[test]
    fn selects_the_native_cpu_and_rejects_foreign_packages(){
        assert_eq!(super::platform("macos","aarch64").unwrap(),("mac","aarch64"));
        assert_eq!(super::platform("macos","x86_64").unwrap(),("mac","x64"));
        assert_eq!(super::platform("windows","x86_64").unwrap(),("windows","x64"));
        assert!(super::platform("windows","aarch64").is_err());
        let invalid=serde_json::json!([{"binary":{"package":{"link":"https://example.com/jdk.zip","size":1,"checksum":"0".repeat(64)}}}]);
        assert!(super::package(&invalid).is_err());
        let root=tempfile::tempdir().unwrap();std::fs::write(root.path().join("jdk25-current.json"),"\"jdk25-../../outside\"").unwrap();
        assert!(super::managed_at(root.path()).is_none());
    }

    #[cfg(target_os="macos")]
    #[test]
    fn incompatible_openmp_is_replaced_without_removing_the_old_installation(){
        let root=tempfile::tempdir().unwrap();
        for name in ["libomp14-old","libomp21-new"] {
            let folder=root.path().join(name).join("lib");std::fs::create_dir_all(&folder).unwrap();
            std::fs::write(folder.join("libomp.dylib"),b"fixture").unwrap();
        }
        let marker=root.path().join("libomp-current.json");
        std::fs::write(&marker,"\"libomp14-old\"").unwrap();
        assert!(super::openmp_at(root.path()).is_none());
        std::fs::write(&marker,"\"libomp21-new\"").unwrap();
        assert_eq!(super::openmp_at(root.path()),Some(root.path().join("libomp21-new/lib")));
        assert!(root.path().join("libomp14-old/lib/libomp.dylib").exists());
    }

    #[tokio::test]
    #[ignore="May download the app-owned C compiler; requires platform developer tools on macOS"]
    async fn c_preparation_compiles_and_runs_on_this_platform(){
        let temporary=tempfile::tempdir().unwrap();let previous=std::env::var_os("MOLIP_DATA_DIR");
        std::env::set_var("MOLIP_DATA_DIR",temporary.path());
        let (tx,_rx)=tokio::sync::mpsc::unbounded_channel();
        let result=super::prepare_c(&tx).await;
        if let Some(previous)=previous{std::env::set_var("MOLIP_DATA_DIR",previous);}else{std::env::remove_var("MOLIP_DATA_DIR");}
        assert!(result.is_ok(),"{result:?}");
    }

    #[tokio::test]
    #[ignore="Downloads and executes an official JDK in a disposable directory"]
    async fn clean_java_install_runs_without_a_system_jdk_or_path_changes(){
        let path_before=std::env::var_os("PATH");
        let root=tempfile::tempdir().unwrap();let (tx,mut rx)=tokio::sync::mpsc::unbounded_channel();
        let logger=tokio::spawn(async move{while let Some(line)=rx.recv().await{eprintln!("{line}");}});
        let java=super::download_java(root.path(),&tx).await.unwrap();
        assert_eq!(super::managed_at(root.path()),Some(java.clone()));
        super::verify_java(&java).await.unwrap();
        assert_eq!(std::env::var_os("PATH"),path_before);
        drop(tx);logger.await.unwrap();
    }
}

/// Record an attempted bootstrap, not a claim that every tool is ready.
pub fn mark_bootstrap()->Result<(),String> {
    let root=crate::data_dir()?;std::fs::create_dir_all(&root).map_err(|e|e.to_string())?;
    std::fs::write(root.join("environment-bootstrap-v1.json"),"{\"attempted\":true}\n").map_err(|e|e.to_string())
}
pub fn should_bootstrap()->bool {
    option_env!("MOLIP_BUILD").is_some_and(|b|b!="0")&&!crate::pilot_source::enabled()
        &&std::env::var_os("MOLIP_SKIP_AUTO_SETUP").is_none()
        &&crate::data_dir().is_ok_and(|p|!p.join("environment-bootstrap-v1.json").exists())
}

#[cfg(target_os="macos")]
fn openmp_directory()->Option<PathBuf> {openmp_at(&crate::data_dir().ok()?.join("runtime-libs"))}

#[cfg(target_os="macos")]
fn openmp_at(root:&Path)->Option<PathBuf> {
    let name:String=serde_json::from_slice(&std::fs::read(root.join("libomp-current.json")).ok()?).ok()?;
    if !name.starts_with("libomp21-")||name.len()>100||!name.bytes().all(|c|c.is_ascii_alphanumeric()||c==b'-'){return None;}
    let folder=root.join(name).join("lib");folder.join("libomp.dylib").is_file().then_some(folder)
}

pub fn library_path()->Option<std::ffi::OsString> {
    #[cfg(target_os="macos")]
    {
        let mut paths=vec![openmp_directory()?];
        if let Some(existing)=std::env::var_os("DYLD_LIBRARY_PATH"){paths.extend(std::env::split_paths(&existing));}
        std::env::join_paths(paths).ok()
    }
    #[cfg(not(target_os="macos"))]
    {None}
}

#[cfg(target_os="macos")]
pub async fn prepare_openmp(report:&UnboundedSender<String>)->Result<(),String> {
    if openmp_directory().is_some(){return Ok(());}
    // Conda-forge's standalone LLVM runtime works without Homebrew or admin writes.
    // Pin the redistributable with its license; keep Apple Silicon and Intel distinct.
    let (name,checksum)=if cfg!(target_arch="aarch64") {
        ("osx-arm64/llvm-openmp-21.1.8-hc225544_2.conda","74093c0f1169da8d16f1cf722062f388ad9bc9a5b0c3f43cdaf54763a2fa6a70")
    }else{
        ("osx-64/llvm-openmp-21.1.8-h8e721bf_2.conda","2533db6470221b80403a7a54d1cf1069128cc8efd61b66226b10ea8e4bce92d8")
    };
    let _=report.send("Python · 병렬 실행 라이브러리를 앱 전용 폴더에 준비해요.".into());
    let archive=crate::lesson_runner::dependency(&format!("libomp-21.1.8-{}.conda",std::env::consts::ARCH),&format!("https://conda.anaconda.org/conda-forge/{name}"),checksum).await?;
    let root=crate::data_dir()?.join("runtime-libs");std::fs::create_dir_all(&root).map_err(|e|e.to_string())?;
    let pending=tempfile::Builder::new().prefix("libomp21-").tempdir_in(&root).map_err(|e|e.to_string())?;
    let compressed=tempfile::tempdir_in(&root).map_err(|e|e.to_string())?;
    crate::doctor::run_logged(report,"/usr/bin/tar",&["-xf",&archive.to_string_lossy(),"-C",&compressed.path().to_string_lossy()],None).await?;
    let stem=name.rsplit('/').next().and_then(|s|s.strip_suffix(".conda")).ok_or("라이브러리 압축 이름 오류")?;
    // .conda contains separate package and license archives. macOS tar cannot
    // decode zstd without an external executable, so decode inside the app.
    for kind in ["pkg","info"] {
        let source=compressed.path().join(format!("{kind}-{stem}.tar.zst"));
        let decoded=tokio::task::spawn_blocking(move||->Result<tempfile::NamedTempFile,String>{
            let file=std::fs::File::open(source).map_err(|e|e.to_string())?;
            let mut decoder=ruzstd::decoding::StreamingDecoder::new(file).map_err(|e|e.to_string())?;
            let mut output=tempfile::NamedTempFile::new().map_err(|e|e.to_string())?;
            std::io::copy(&mut decoder,&mut output).map_err(|e|e.to_string())?;
            output.flush().map_err(|e|e.to_string())?;
            Ok(output)
        }).await.map_err(|e|e.to_string())??;
        crate::doctor::run_logged(report,"/usr/bin/tar",&["-xf",&decoded.path().to_string_lossy(),"-C",&pending.path().to_string_lossy()],None).await?;
    }
    if !pending.path().join("lib/libomp.dylib").is_file()||!pending.path().join("info/licenses/openmp/LICENSE.TXT").is_file(){return Err("병렬 실행 라이브러리를 확인하지 못했어요.".into());}
    let name=pending.path().file_name().ok_or("라이브러리 설치 경로 오류")?.to_string_lossy().into_owned();
    let _=pending.keep();
    let mut marker=tempfile::NamedTempFile::new_in(&root).map_err(|e|e.to_string())?;
    marker.write_all(&serde_json::to_vec(&name).unwrap()).map_err(|e|e.to_string())?;
    marker.persist(root.join("libomp-current.json")).map_err(|e|e.to_string())?;
    Ok(())
}
