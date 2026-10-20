//! Persistent source/class exercises. Commands run the real JDK; grading never recompiles.
use super::*;
use sha2::{Digest,Sha256};
use std::{io::{Read,Write},time::{Duration,Instant}};

#[derive(Clone,Debug,Serialize,Deserialize,PartialEq)]
#[serde(deny_unknown_fields)]
pub struct JavaBuildGoal {
    #[serde(default)] pub command:Vec<String>,
    #[serde(default)] pub stdout:String,
    pub class_output:Option<String>,
    #[serde(default)] pub class_relation:String,
    #[serde(default)] pub demo_class_source:Option<String>,
}
#[derive(Clone,Debug,Serialize,Deserialize)]
struct Invocation {args:Vec<String>,source:String,before:Option<String>,after:Option<String>,success:bool,stdout:String,stderr:String}
#[derive(Serialize,Deserialize)]
struct Checkpoint {offset:usize,class:Option<String>}
fn fingerprint(path:&Path)->Result<Option<String>,String> {
    let metadata=match std::fs::symlink_metadata(path){Ok(m)=>m,Err(e) if e.kind()==std::io::ErrorKind::NotFound=>return Ok(None),Err(e)=>return Err(e.to_string())};
    if !metadata.is_file()||metadata.file_type().is_symlink()||metadata.len()>200_000{return Err("실습 파일의 종류와 크기를 확인하세요.".into())}
    Ok(Some(format!("{:x}",Sha256::digest(std::fs::read(path).map_err(|e|e.to_string())?))))
}
fn invocations(root:&Path)->Result<Vec<Invocation>,String> {
    let file=root.join("java-invocations.jsonl");
    if !file.exists(){return Ok(vec![])}
    if std::fs::metadata(&file).map_err(|e|e.to_string())?.len()>4_000_000{return Err("실행 기록이 너무 커요. 첫 단계에서 초기화하세요.".into())}
    std::fs::read_to_string(file).map_err(|e|e.to_string())?.lines().map(|line|serde_json::from_str(line).map_err(|e|e.to_string())).collect()
}
pub fn jdk_tools()->Result<(PathBuf,PathBuf),String> {
    let supplied=crate::java::executable();let mut java=PathBuf::from(&supplied);
    if !java.is_absolute(){
        let output=Command::new(if cfg!(windows){"where.exe"}else{"/usr/bin/which"}).arg(&supplied).output().map_err(|e|e.to_string())?;
        java=PathBuf::from(String::from_utf8_lossy(&output.stdout).lines().next().ok_or("JDK 25의 java를 찾지 못했어요.")?);
    }
    let javac=java.parent().ok_or("JDK 경로를 확인하세요.")?.join(if cfg!(windows){"javac.exe"}else{"javac"});
    if !javac.is_file(){return Err("같은 JDK 25의 javac가 필요해요.".into())}
    let version=Command::new(&java).arg("--version").output().map_err(|e|e.to_string())?;
    if !version.status.success()||!crate::java::is_jdk25(&String::from_utf8_lossy(&version.stdout)){return Err("이 수업은 JDK 25가 필요해요.".into())}
    Ok((java,javac))
}
/// Own the command and descendants, including on timeout/output overflow.
#[cfg(not(target_os="android"))]
fn execute(root:&Path,args:&[String])->Result<Invocation,String> {
    if !matches!(args.iter().map(String::as_str).collect::<Vec<_>>().as_slice(),["java","Main"]|["java","Main.java"]|["javac","Main.java"]){return Err("java Main.java, javac Main.java 또는 java Main을 사용하세요.".into())}
    let (java,javac):(PathBuf,PathBuf)=serde_json::from_slice(&std::fs::read(root.join("java-tools.json")).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    let work=root.join("work");let source=fingerprint(&work.join("Main.java"))?.ok_or("Main.java를 확인하세요.")?;
    let before=fingerprint(&work.join("Main.class"))?;
    let mut command=Command::new(if args[0]=="java"{java}else{javac});
    if args[0]=="java"{command.args(["-Xmx128m","-Dfile.encoding=UTF-8","-Dstdout.encoding=UTF-8","-Dstderr.encoding=UTF-8"]);}else{command.args(["-J-Xmx128m","-encoding","UTF-8"]);}
    command.args(&args[1..]).current_dir(&work).env_remove("CLASSPATH").env_remove("JDK_JAVAC_OPTIONS").env_remove("JDK_JAVA_OPTIONS").env_remove("JAVA_TOOL_OPTIONS").env_remove("_JAVA_OPTIONS")
        .stdin(std::process::Stdio::null()).stdout(std::process::Stdio::piped()).stderr(std::process::Stdio::piped());
    #[cfg(unix)] {use std::os::unix::process::CommandExt;command.process_group(0);}
    #[cfg(windows)] command.creation_flags(0x08000000);
    let mut child=command.spawn().map_err(|e|format!("JDK 실행: {e}"))?;
    let scope=match crate::process_scope::CommandScope::attach(&child){Ok(scope)=>scope,Err(e)=>{let _=child.kill();let _=child.wait();return Err(format!("JDK 프로세스 소유: {e}"))}};
    let overflow=std::sync::Arc::new(std::sync::atomic::AtomicBool::new(false));
    fn collect(mut pipe:impl Read+Send+'static,overflow:std::sync::Arc<std::sync::atomic::AtomicBool>)->std::thread::JoinHandle<Vec<u8>> {
        std::thread::spawn(move||{let mut result=vec![];let mut block=[0;4096];while let Ok(n)=pipe.read(&mut block){if n==0{break}let keep=n.min(65536usize.saturating_sub(result.len()));result.extend_from_slice(&block[..keep]);if keep<n{overflow.store(true,std::sync::atomic::Ordering::Relaxed);}}result})
    }
    let out=collect(child.stdout.take().unwrap(),overflow.clone());let err=collect(child.stderr.take().unwrap(),overflow.clone());
    let started=Instant::now();let mut limited=false;
    let status=loop {
        if let Some(status)=child.try_wait().map_err(|e|e.to_string())?{break status}
        if started.elapsed()>Duration::from_secs(20)||overflow.load(std::sync::atomic::Ordering::Relaxed){limited=true;scope.terminate().map_err(|e|format!("JDK 종료: {e}"))?;let _=child.kill();break child.wait().map_err(|e|e.to_string())?}
        std::thread::sleep(Duration::from_millis(10));
    };
    scope.terminate().map_err(|e|format!("JDK 종료: {e}"))?;
    let stdout=String::from_utf8_lossy(&out.join().map_err(|_|"출력 수집 오류")?).replace("\r\n","\n");
    let mut stderr=String::from_utf8_lossy(&err.join().map_err(|_|"오류 수집 오류")?).replace("\r\n","\n");
    limited|=overflow.load(std::sync::atomic::Ordering::Relaxed);
    if limited{stderr.push_str("\n실행 제한(20초 또는 출력 64KB)을 초과했어요.\n");}
    Ok(Invocation{args:args.to_vec(),source,before,after:fingerprint(&work.join("Main.class"))?,success:status.success()&&!limited,stdout,stderr})
}
#[cfg(target_os="android")]
fn execute(_: &Path,_: &[String])->Result<Invocation,String>{Err("이 실습은 데스크톱에서 실행하세요.".into())}
/// Shell launchers call this mode of the same installed executable, before any UI starts.
pub fn command_cli(args:&[String])->i32 {
    let result=(||{
        let root=PathBuf::from(args.first().ok_or("실습 경로가 없어요.")?);
        if !root.join("java-tools.json").is_file(){return Err("실습 실행 설정을 찾지 못했어요.".to_string())}
        let record=execute(&root,&args[1..])?;
        let mut log=std::fs::OpenOptions::new().read(true).append(true).create(true).open(root.join("java-invocations.jsonl")).map_err(|e|e.to_string())?;
        log.lock().map_err(|e|format!("실행 기록 잠금: {e}"))?;writeln!(log,"{}",serde_json::to_string(&record).unwrap()).map_err(|e|e.to_string())?;
        print!("{}",record.stdout);eprint!("{}",record.stderr);Ok(record.success)
    })();
    match result{Ok(true)=>0,Ok(false)=>1,Err(e)=>{eprintln!("{e}");1}}
}
impl GitPractice {
    pub fn java_source(&self)->Result<String,String>{std::fs::read_to_string(self.work().join("Main.java")).map_err(|e|e.to_string())}
    pub fn save_java_source(&self,source:&str)->Result<(),String>{
        if self.exercise.java_build.is_none(){return Err("자바 파일 편집 실습이 아니에요.".into())}
        validate_file("Main.java",source)?;
        if self.java_source().ok().as_deref()==Some(source){return Ok(())}
        let mut file=tempfile::NamedTempFile::new_in(self.work()).map_err(|e|e.to_string())?;
        file.write_all(source.as_bytes()).map_err(|e|e.to_string())?;file.as_file().sync_all().map_err(|e|e.to_string())?;
        file.persist(self.work().join("Main.java")).map_err(|e|e.to_string())?;Ok(())
    }
    pub fn prepare_java_launcher(&self,player:&Path)->Result<Vec<(String,String)>,String>{
        let tools=jdk_tools()?;
        std::fs::write(self.root().join("java-tools.json"),serde_json::to_vec(&tools).unwrap()).map_err(|e|e.to_string())?;
        let bin=self.root().join("java-bin");std::fs::create_dir_all(&bin).map_err(|e|e.to_string())?;
        for tool in ["java","javac"]{
            let path=bin.join(tool);std::fs::write(&path,format!("#!/bin/bash\nexec \"$MQ3_JAVA_PLAYER\" --mq-java-practice \"$MQ3_JAVA_ROOT\" {tool} \"$@\"\n")).map_err(|e|e.to_string())?;
            #[cfg(unix)] {use std::os::unix::fs::PermissionsExt;std::fs::set_permissions(&path,std::fs::Permissions::from_mode(0o700)).map_err(|e|e.to_string())?;}
        }
        let shell=self.exercise.shell.as_ref().ok_or("실습 단계가 없어요.")?;
        let checkpoint=self.root().join(format!("java-{}.json",shell.step_id));
        if !checkpoint.exists(){std::fs::write(checkpoint,serde_json::to_vec(&Checkpoint{offset:invocations(self.root())?.len(),class:fingerprint(&self.work().join("Main.class"))?}).unwrap()).map_err(|e|e.to_string())?;}
        let inherited=std::env::var_os("PATH").unwrap_or_default();let paths=std::iter::once(bin).chain(std::env::split_paths(&inherited));
        Ok(vec![("PATH".into(),std::env::join_paths(paths).map_err(|e|e.to_string())?.to_string_lossy().into_owned()),("MQ3_JAVA_PLAYER".into(),player.to_string_lossy().replace('\\',"/")),("MQ3_JAVA_ROOT".into(),self.root().to_string_lossy().replace('\\',"/"))])
    }
    pub(super) fn prepare_java_demo(&self)->Result<(),String>{
        if let Some(source)=self.exercise.java_build.as_ref().and_then(|j|j.demo_class_source.as_ref()){
            let tools=jdk_tools()?;std::fs::write(self.root().join("java-tools.json"),serde_json::to_vec(&tools).unwrap()).map_err(|e|e.to_string())?;
            let actual=self.java_source()?;self.save_java_source(source)?;
            let record=execute(self.root(),&["javac".into(),"Main.java".into()]);self.save_java_source(&actual)?;
            if !record?.success{return Err("해설용 클래스를 준비하지 못했어요.".into())}
        }Ok(())
    }
    pub fn check_java_build(&self)->Result<crate::runner::TestReport,String>{
        use crate::runner::TestCaseResult;
        let goal=self.exercise.java_build.as_ref().ok_or("자바 실습 목표가 없어요.")?;
        let mut report=self.check_shell()?;
        let shell=self.exercise.shell.as_ref().unwrap();
        let checkpoint:Checkpoint=std::fs::read(self.root().join(format!("java-{}.json",shell.step_id))).ok().and_then(|b|serde_json::from_slice(&b).ok()).unwrap_or(Checkpoint{offset:usize::MAX,class:None});
        let source=fingerprint(&self.work().join("Main.java"))?;let class=fingerprint(&self.work().join("Main.class"))?;
        let add=|report:&mut crate::runner::TestReport,name:&str,passed:bool,expected:String,actual:String|report.cases.push(TestCaseResult{input:name.into(),expected,stdout:actual,stderr:String::new(),passed,state:"java_build".into()});
        if !goal.command.is_empty(){
            let records=invocations(self.root())?;
            let matching=records.iter().skip(checkpoint.offset.min(records.len())).rev().find(|r|r.args==goal.command);
            let valid=matching.is_some_and(|r|r.success&&Some(&r.source)==source.as_ref()&&r.after==class&&r.stdout==goal.stdout);
            add(&mut report,"실제 JDK 실행 결과",valid,goal.stdout.clone(),matching.map(|r|format!("{}{}",r.stdout,r.stderr)).unwrap_or_else(||"아직 이 단계의 명령을 실행하지 않았어요.".into()));
        }
        let actual=if class.is_some(){
            // Run the binary in a copy: grading must not give user code a second
            // opportunity to change the learner's source or build artifact.
            let probe=tempfile::Builder::new().prefix("mq-java-class-check-").tempdir().map_err(|e|e.to_string())?;
            std::fs::create_dir(probe.path().join("work")).map_err(|e|e.to_string())?;
            for name in ["Main.java","Main.class"]{std::fs::copy(self.work().join(name),probe.path().join("work").join(name)).map_err(|e|e.to_string())?;}
            std::fs::copy(self.root().join("java-tools.json"),probe.path().join("java-tools.json")).map_err(|e|e.to_string())?;
            let r=execute(probe.path(),&["java".into(),"Main".into()])?;
            if r.success&&r.before==class&&r.after==class{Some(r.stdout)}else{Some(format!("클래스 확인 실패: {}",r.stderr))}
        }else{None};
        add(&mut report,"클래스 산출물",actual==goal.class_output,goal.class_output.clone().unwrap_or_else(||"Main.class가 없어요.".into()),actual.unwrap_or_else(||"Main.class가 없어요.".into()));
        if !goal.class_relation.is_empty(){let valid=class.is_some()&&checkpoint.class.is_some()&&if goal.class_relation=="same"{class==checkpoint.class}else{class!=checkpoint.class};add(&mut report,"클래스 변경 여부",valid,goal.class_relation.clone(),if class==checkpoint.class{"same"}else{"changed"}.into());}
        report.passed=report.cases.iter().all(|c|c.passed);Ok(report)
    }
}
