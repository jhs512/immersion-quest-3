//! Real local execution for repository lessons. Each attempt gets a fresh workspace.
use crate::{repository_course::{Task,TaskLanguage},runner::{Execution,TestReport,TestCaseResult}};
use std::{path::{Path,PathBuf},process::Stdio,time::Duration};
use tokio::{process::Command,io::{AsyncReadExt,AsyncWriteExt}};

fn command(executable:impl AsRef<std::ffi::OsStr>)->Command {
    let mut command=Command::new(executable);
    command.kill_on_drop(true).env_remove("JAVA_TOOL_OPTIONS").env_remove("JDK_JAVA_OPTIONS").env_remove("_JAVA_OPTIONS");
    #[cfg(windows)] command.creation_flags(0x08000000);
    command
}
async fn process(mut cmd:Command,dir:&Path,input:&str,seconds:u64)->Result<Execution,String> {
    cmd.current_dir(dir).stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
    let mut child=cmd.spawn().map_err(|e|format!("실행 도구를 찾지 못했어요. 설치 경로를 확인하세요: {e}"))?;
    let mut stdin=child.stdin.take().ok_or("입력 연결 실패")?;
    let out=child.stdout.take().ok_or("출력 연결 실패")?;let err=child.stderr.take().ok_or("오류 연결 실패")?;
    let read=async move {let write=async {let _=stdin.write_all(input.as_bytes()).await;drop(stdin);Ok::<(),std::io::Error>(())};
        let stdout=async {let mut b=vec![];out.take(65537).read_to_end(&mut b).await?;Ok::<_,std::io::Error>(b)};
        let stderr=async {let mut b=vec![];err.take(65537).read_to_end(&mut b).await?;Ok::<_,std::io::Error>(b)};
        tokio::try_join!(stdout,stderr,child.wait(),write)};
    match tokio::time::timeout(Duration::from_secs(seconds),read).await {
        Ok(Ok((out,err,status,())))=>{let limited=out.len()>65536||err.len()>65536;Ok(Execution{stdout:String::from_utf8_lossy(&out[..out.len().min(65536)]).replace("\r\n","\n"),stderr:String::from_utf8_lossy(&err[..err.len().min(65536)]).replace("\r\n","\n"),success:status.success()&&!limited,state:if limited{"output_limit"}else if status.success(){"finished"}else{"runtime_error"}.into(),artifacts:vec![]})},
        Ok(Err(e))=>Err(e.to_string()),Err(_)=>Ok(Execution{stdout:String::new(),stderr:"실행 시간을 초과했어요. 종료 조건을 확인하세요.".into(),success:false,state:"timeout".into(),artifacts:vec![]})
    }
}
fn prepare(task:&Task,source:&str)->Result<tempfile::TempDir,String> {
    if source.len()>65536 {return Err("작성 코드는 64KB 이하여야 해요.".into())}
    let dir=tempfile::tempdir().map_err(|e|e.to_string())?;
    for (name,content) in &task.files {write_file(dir.path(),name,content)?}
    let entry=if task.entry_file.is_empty(){task.language.filename()}else{&task.entry_file};
    write_file(dir.path(),entry,source)?;
    Ok(dir)
}
fn write_file(root:&Path,name:&str,content:&str)->Result<(),String> {
    if !crate::repository_course::safe_file(name) {return Err("실습 파일 경로를 확인하세요.".into())}
    let path=root.join(name);
    std::fs::create_dir_all(path.parent().ok_or("파일 경로 오류")?).map_err(|e|e.to_string())?;
    std::fs::write(path,content).map_err(|e|e.to_string())
}
pub fn node()->String {std::env::var("MOLIP_NODE").unwrap_or_else(|_|"node".into())}

/// Execute the separately prepared example; answer IDs never become its source.
pub async fn run_example(task:&Task,source:&str,input:&str)->Result<Execution,String> {
    if !task.has_runnable_example(){return Err("실행할 예제 코드 구성을 확인하세요.".into())}
    let mut example=task.clone();example.interaction=None;
    run(&example,source,input).await
}

pub async fn run(task:&Task,source:&str,input:&str)->Result<Execution,String> {
    if task.interaction.is_some() {return Err("답안을 고른 뒤 제출해 보세요.".into())}
    if task.language==TaskLanguage::Java {return crate::java::run_files(source,input,&task.files).await}
    if task.language==TaskLanguage::Python {return crate::runner::execute_python_files(source,input,None,&task.files).await}
    if task.language==TaskLanguage::Sql {return crate::sql_practice::execute(&task.files,source).await}
    let dir=prepare(task,source)?;
    match task.language {
        TaskLanguage::Java|TaskLanguage::Sql=>unreachable!(),
        TaskLanguage::JavaProject=>{
            crate::java::version().await?;
            let mut cmd=command(crate::java::executable());
            cmd.args(["-Xmx128m","-Dfile.encoding=UTF-8","-Dstdout.encoding=UTF-8","--source","25","Main.java"]);
            process(cmd,dir.path(),input,25).await
        },
        TaskLanguage::Junit=>run_junit(task,dir.path()).await,
        TaskLanguage::Git=>{
            // A local bare repository is the remote; no real account is modified by exercises.
            let mut init=command("git");init.args(["init","--bare","remote.git"]);
            let initialized=process(init,dir.path(),"",10).await?;if !initialized.success{return Ok(initialized)}
            let bash=if cfg!(windows){"C:/Program Files/Git/bin/bash.exe"}else{"bash"};
            let mut cmd=command(bash);cmd.arg("practice.sh").env("GIT_CONFIG_GLOBAL",if cfg!(windows){"NUL"}else{"/dev/null"}).env("GIT_AUTHOR_NAME","학습자").env("GIT_AUTHOR_EMAIL","learner@example.invalid").env("GIT_COMMITTER_NAME","학습자").env("GIT_COMMITTER_EMAIL","learner@example.invalid");
            process(cmd,dir.path(),input,20).await
        },
        TaskLanguage::Javascript=>{let mut cmd=command(node());cmd.arg("main.js");process(cmd,dir.path(),input,15).await},
        TaskLanguage::Python=>{let mut cmd=command(crate::runner::python_executable());cmd.args(["-X","utf8","main.py"]).env("MPLBACKEND","Agg").env("TF_CPP_MIN_LOG_LEVEL","3");process(cmd,dir.path(),input,60).await},
        TaskLanguage::Web=>run_web(task,source,false).await,
        TaskLanguage::C=>run_c(dir.path(),input).await,
    }
}

/// TinyCC 0.9.27 for Windows from the GNU Savannah release, pinned by hash. Other systems use cc.
const TCC_URL:&str="https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27-win64-bin.zip";
const TCC_SHA256:&str="34a721949a2583fdff725312da092fa0f5f1f284b702e6f811c6954714faabb2";
async fn c_compiler()->Result<PathBuf,String> {
    if !cfg!(windows) {return Ok(PathBuf::from(std::env::var("MOLIP_CC").unwrap_or_else(|_|"cc".into())))}
    if let Ok(path)=std::env::var("MOLIP_TCC") {return Ok(PathBuf::from(path))}
    let root=crate::data_dir()?.join("course-tools");
    let folder=root.join("tcc-0.9.27");
    let exe=folder.join("tcc").join("tcc.exe");
    if exe.is_file() {return Ok(exe)}
    let archive=dependency("tcc-0.9.27-win64-bin.zip",TCC_URL,TCC_SHA256).await?;
    // Extract beside the final folder, then rename, so a half-written compiler is never used.
    let pending=root.join(format!("tcc-0.9.27.{}.tmp",crate::issue_progress::new_id()));
    std::fs::create_dir_all(&pending).map_err(|e|e.to_string())?;
    let tar=std::env::var("SystemRoot").map(|r|PathBuf::from(r).join("System32").join("tar.exe")).unwrap_or_else(|_|PathBuf::from("tar"));
    let mut cmd=command(tar);cmd.arg("-xf").arg(&archive).arg("-C").arg(&pending);
    let extracted=process(cmd,&root,"",60).await?;
    if !extracted.success||!pending.join("tcc").join("tcc.exe").is_file() {let _=std::fs::remove_dir_all(&pending);return Err(format!("C 컴파일러 압축을 풀지 못했어요. {}",extracted.stderr))}
    if std::fs::rename(&pending,&folder).is_err() {let _=std::fs::remove_dir_all(&pending);}
    if exe.is_file() {Ok(exe)} else {Err("C 컴파일러를 준비하지 못했어요.".into())}
}
async fn run_c(dir:&Path,input:&str)->Result<Execution,String> {
    let compiler=c_compiler().await?;
    if cfg!(windows) {
        // tcc -run compiles in memory and runs at once; no executable file is written.
        let mut cmd=command(&compiler);cmd.args(["-run","main.c"]);
        return process(cmd,dir,input,15).await;
    }
    let mut compile=command(&compiler);compile.args(["-std=c11","-o","main","main.c"]);
    let compiled=process(compile,dir,"",30).await.map_err(|e|format!("C 컴파일러(cc)를 찾지 못했어요. Xcode 명령행 도구나 gcc를 설치하세요. {e}"))?;
    if !compiled.success {return Ok(compiled)}
    process(command(dir.join("main")),dir,input,15).await
}

/// Replace the initializer of the first declaration of `name` (`int n = 3;`, `int *p = &a;`, `char s[] = "x";`).
/// Comments, strings and character literals are skipped. Returns None when no such declaration exists.
pub fn mutate_c(source:&str,name:&str,value:&str)->Option<String> {
    let bytes=source.as_bytes();let mut i=0;let mut previous=b';';
    let ident=|c:u8|c.is_ascii_alphanumeric()||c==b'_';
    while i<bytes.len() {
        let c=bytes[i];
        if c==b'/'&&bytes.get(i+1)==Some(&b'/') {while i<bytes.len()&&bytes[i]!=b'\n'{i+=1}continue}
        if c==b'/'&&bytes.get(i+1)==Some(&b'*') {i+=2;while i+1<bytes.len()&&!(bytes[i]==b'*'&&bytes[i+1]==b'/'){i+=1}i+=2;continue}
        if c==b'"'||c==b'\'' {i+=1;while i<bytes.len()&&bytes[i]!=c{if bytes[i]==b'\\'{i+=1}i+=1}i+=1;previous=c;continue}
        if ident(c) {
            let start=i;while i<bytes.len()&&ident(bytes[i]){i+=1}
            let declared=ident(previous)||previous==b'*'||previous==b','||previous==b']';
            if &source[start..i]==name&&declared&&(start==0||!ident(bytes[start-1])) {
                let mut j=i;
                loop {
                    while j<bytes.len()&&bytes[j].is_ascii_whitespace(){j+=1}
                    if bytes.get(j)==Some(&b'[') {while j<bytes.len()&&bytes[j]!=b']'{j+=1}j+=1;continue}
                    break;
                }
                if bytes.get(j)==Some(&b'=')&&bytes.get(j+1)!=Some(&b'=') {
                    let begin=j+1;let mut end=begin;let mut depth=0i32;
                    while end<bytes.len() {
                        match bytes[end] {
                            b'('|b'{'|b'['=>depth+=1, b')'|b'}'|b']'=>depth-=1,
                            b'"'|b'\''=>{let q=bytes[end];end+=1;while end<bytes.len()&&bytes[end]!=q{if bytes[end]==b'\\'{end+=1}end+=1}},
                            b';'|b',' if depth==0=>break,
                            _=>{}
                        }
                        end+=1;
                    }
                    if end>=bytes.len() {return None}
                    return Some(format!("{} {}{}",&source[..begin],value.trim(),&source[end..]));
                }
            }
            previous=bytes[i-1];continue;
        }
        if !c.is_ascii_whitespace() {previous=c}
        i+=1;
    }
    None
}

async fn check_c(task:&Task,source:&str)->Result<TestReport,String> {
    let mut cases=vec![];
    for test in &task.tests {
        let result=run(task,source,&test.input).await?;
        let passed=result.success && result.stdout.trim_end_matches('\n')==test.expected.trim_end_matches('\n');
        cases.push(TestCaseResult{input:test.input.clone(),expected:test.expected.clone(),stdout:result.stdout,stderr:result.stderr,passed,state:result.state});
    }
    append_prepared_variations(task,source,&mut cases).await?;
    Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
}

async fn append_prepared_variations(task:&Task,source:&str,cases:&mut Vec<TestCaseResult>)->Result<(),String> {
    // Changed prepared values only count once the program is right as given.
    if cases.iter().all(|c|c.passed) {
        for variation in &task.variations {
            let label=format!("준비 값 바꿈: {}",variation.values.iter().map(|(k,v)|format!("{k} = {v}")).collect::<Vec<_>>().join(", "));
            let mut changed=source.to_string();let mut missing=None;
            for (name,value) in &variation.values {match mutate_c(&changed,name,value) {Some(next)=>changed=next,None=>{missing=Some(name.clone());break}}}
            if let Some(name)=missing {
                cases.push(TestCaseResult{input:label,expected:variation.expected.clone(),stdout:String::new(),stderr:format!("준비 코드의 {name} 선언과 처음 값은 그대로 두세요."),passed:false,state:"concept_error".into()});
                continue;
            }
            let mut prepared=task.clone();prepared.files.extend(variation.files.clone());prepared.expected_files.extend(variation.expected_files.clone());
            let result=if prepared.language==TaskLanguage::Java {crate::java::run_files_checked(&changed,"",&prepared.files,&prepared.expected_files).await?}else{run(&prepared,&changed,"").await?};
            let passed=result.success && result.stdout.trim_end_matches('\n')==variation.expected.trim_end_matches('\n');
            let stderr=if passed||!result.success{result.stderr}else{"값이 바뀌어도 맞는 식인지 확인하세요.".into()};
            cases.push(TestCaseResult{input:label,expected:variation.expected.clone(),stdout:result.stdout,stderr,passed,state:result.state});
        }
    }
    Ok(())
}
pub async fn check(task:&Task,source:&str)->Result<TestReport,String> {
    if let Some(interaction) = &task.interaction {return interaction.check(source)}
    if task.language==TaskLanguage::Sql {return check_sql(task,source).await}
    if task.language==TaskLanguage::Python {
        if let Some(checker)=task.checker.as_deref().filter(|c|!c.trim().is_empty()) {
            let result=crate::runner::execute_python_files(source,"",Some(checker),&task.files).await?;
            return Ok(report_execution(result,"다른 데이터로 원리 검사"));
        }
    }
    if task.language==TaskLanguage::Java {
        let unit:crate::Unit=serde_json::from_value(serde_json::json!({"id":task.id,"title":task.title,"language":"java","starter_code":task.starter_code,"solution":task.solution,"tests":task.tests,"checker":task.checker})).map_err(|e|e.to_string())?;
        let mut report=crate::runner::check_unit_prepared(&unit,source,&task.files,&task.expected_files).await?;
        append_prepared_variations(task,source,&mut report.cases).await?;
        report.passed=report.cases.iter().all(|case|case.passed);
        return Ok(report);
    }
    if task.language==TaskLanguage::Git {return check_git(task,source).await}
    if task.language==TaskLanguage::C {return check_c(task,source).await}
    if task.language==TaskLanguage::Web {
        let result=run_web(task,source,true).await?;
        return Ok(report_execution(result,"브라우저 동작 검사"));
    }
    if task.language==TaskLanguage::Junit {
        let result=run(task,source,"").await?;
        let mut report=report_execution(result,"JUnit 테스트");
        if report.passed {
            for (index,files) in task.mutations.iter().enumerate() {
                let mut mutant=task.clone();mutant.files.extend(files.clone());
                let result=run(&mutant,source,"").await?;
                let detected=!result.success && result.stdout.contains("tests failed");
                report.cases.push(TestCaseResult{input:format!("결함 구현 {} 탐지",index+1),expected:"작성한 테스트가 결함 구현을 거부해요.".into(),stdout:result.stdout,stderr:result.stderr,passed:detected,state:result.state});
            }
            report.passed=report.cases.iter().all(|c|c.passed);
        }
        return Ok(report);
    }
    if task.tests.is_empty(){return Err("입출력 검사 사례가 없어요.".into())}
    let mut cases=vec![];
    for test in &task.tests {
        let result=run(task,source,&test.input).await?;
        let passed=result.success && result.stdout.trim_end_matches('\n')==test.expected.trim_end_matches('\n');
        cases.push(TestCaseResult{input:test.input.clone(),expected:test.expected.clone(),stdout:result.stdout,stderr:result.stderr,passed,state:result.state});
    }
    Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
}
fn report_execution(result:Execution,name:&str)->TestReport {TestReport{passed:result.success,cases:vec![TestCaseResult{input:name.into(),expected:"실제 실행 검사 통과".into(),stdout:result.stdout,stderr:result.stderr,passed:result.success,state:result.state}]}}

async fn check_git(task:&Task,source:&str)->Result<TestReport,String> {
    let dir=prepare(task,source)?;
    let mut init=command("git");init.args(["init","--bare","remote.git"]);process(init,dir.path(),"",10).await?;
    let bash=if cfg!(windows){"C:/Program Files/Git/bin/bash.exe"}else{"bash"};
    let mut cmd=command(bash);cmd.arg("practice.sh").env("GIT_CONFIG_GLOBAL",if cfg!(windows){"NUL"}else{"/dev/null"}).env("GIT_AUTHOR_NAME","Learner").env("GIT_AUTHOR_EMAIL","learner@example.invalid").env("GIT_COMMITTER_NAME","Learner").env("GIT_COMMITTER_EMAIL","learner@example.invalid");
    let result=process(cmd,dir.path(),"",20).await?;
    if !result.success{return Ok(report_execution(result,"Git 실습 실행"))}
    let checks=task.git_checks.as_ref().ok_or("Git 산출물 검사 기준이 없어요.")?;
    let mut cases=vec![];
    for test in &task.tests {
        cases.push(TestCaseResult{input:"Git 실행 결과".into(),expected:test.expected.clone(),stdout:result.stdout.clone(),stderr:result.stderr.clone(),passed:result.stdout.trim_end_matches('\n')==test.expected.trim_end_matches('\n'),state:"git_output".into()});
    }
    let mut queries=vec![("커밋 개수",vec!["rev-list","--count","HEAD"],checks.minimum_commits.to_string()),("마지막 커밋",vec!["log","-1","--format=%s"],checks.head_message.clone()),("작업 폴더",vec!["status","--porcelain"],String::new())];
    if let Some(branch)=&checks.branch {queries.push(("현재 브랜치",vec!["branch","--show-current"],branch.clone()))}
    for (title,args,expected) in queries {
        let mut cmd=command("git");cmd.arg("-C").arg("work").args(args);
        let result=process(cmd,dir.path(),"",10).await?;
        let matched=if title=="커밋 개수" {result.stdout.trim().parse::<usize>().is_ok_and(|n|n>=checks.minimum_commits)}else{result.stdout.trim_end()==expected};
        cases.push(TestCaseResult{input:title.into(),expected,stdout:result.stdout,stderr:result.stderr,passed:result.success&&matched,state:"git_artifact".into()});
    }
    for (file,expected) in &checks.tracked_files {
        if !crate::repository_course::safe_file(file){return Err("Git 검사 경로 오류".into())}
        let mut cmd=command("git");cmd.arg("-C").arg("work").args(["show",&format!("HEAD:{file}")]);
        let result=process(cmd,dir.path(),"",10).await?;
        cases.push(TestCaseResult{input:format!("추적 파일 {file}"),expected:expected.clone(),passed:result.success&&result.stdout==*expected,stdout:result.stdout,stderr:result.stderr,state:"git_artifact".into()});
    }
    if checks.pushed {
        let mut local=command("git");local.args(["-C","work","rev-parse","HEAD"]);
        let local_head=process(local,dir.path(),"",10).await?;
        let mut cmd=command("git");cmd.args(["--git-dir=remote.git","show","--format=%s","--no-patch","refs/heads/main"]);
        let result=process(cmd,dir.path(),"",10).await?;
        cases.push(TestCaseResult{input:"원격 main 커밋".into(),expected:checks.head_message.clone(),passed:result.success&&result.stdout.trim()==checks.head_message,stdout:result.stdout,stderr:result.stderr,state:"git_artifact".into()});
        let mut remote=command("git");remote.args(["--git-dir=remote.git","rev-parse","refs/heads/main"]);
        let remote_head=process(remote,dir.path(),"",10).await?;
        cases.push(TestCaseResult{input:"로컬과 원격의 같은 커밋".into(),expected:local_head.stdout.clone(),passed:local_head.success&&remote_head.success&&local_head.stdout==remote_head.stdout,stdout:remote_head.stdout,stderr:remote_head.stderr,state:"git_artifact".into()});
    }
    Ok(TestReport{passed:cases.iter().all(|c|c.passed),cases})
}

async fn dependency(name:&str,url:&str,expected:&str)->Result<PathBuf,String> {
    use sha2::{Digest,Sha256};
    let root=crate::data_dir()?.join("course-tools");std::fs::create_dir_all(&root).map_err(|e|e.to_string())?;
    let target=root.join(name);
    if let Ok(bytes)=std::fs::read(&target){if format!("{:x}",Sha256::digest(&bytes))==expected{return Ok(target)}}
    let target_copy=target.clone();let url=url.to_string();let expected=expected.to_string();
    crate::github_player::background(move ||{
        let bytes=crate::github_player::agent().get(&url).call().map_err(|e|e.to_string())?.body_mut().with_config().limit(10_000_000).read_to_vec().map_err(|e|e.to_string())?;
        if format!("{:x}",Sha256::digest(&bytes))!=expected{return Err("검사 도구의 해시가 맞지 않아요.".into())}
        let pending=target_copy.with_extension(format!("{}.tmp",crate::issue_progress::new_id()));
        std::fs::write(&pending,&bytes).map_err(|e|e.to_string())?;
        std::fs::rename(&pending,&target_copy).map_err(|e|e.to_string())?;
        Ok(target_copy)
    }).await
}
async fn run_junit(task:&Task,dir:&Path)->Result<Execution,String> {
    crate::java::version().await?;
    let junit=dependency("junit-platform-console-standalone-1.13.4.jar","https://repo.maven.apache.org/maven2/org/junit/platform/junit-platform-console-standalone/1.13.4/junit-platform-console-standalone-1.13.4.jar","3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892").await?;
    let assertj=dependency("assertj-core-3.27.7.jar","https://repo.maven.apache.org/maven2/org/assertj/assertj-core/3.27.7/assertj-core-3.27.7.jar","c4a445426c3c2861666863b842cc4ec7bbb1c4226fefd370b6d2fe83d6c4ff0f").await?;
    let separator=if cfg!(windows){";"}else{":"};let classpath=format!("{}{separator}{}",junit.display(),assertj.display());
    let executable=crate::java::executable();let javac=if executable=="java"{PathBuf::from("javac")}else{Path::new(&executable).with_file_name(if cfg!(windows){"javac.exe"}else{"javac"})};
    let mut cmd=command(javac);cmd.args(["--release","25","-encoding","UTF-8","-cp",&classpath,"-d","classes"]);
    let entry=if task.entry_file.is_empty(){"Main.java"}else{&task.entry_file};cmd.arg(entry);
    for file in task.files.keys().filter(|f|f.ends_with(".java")){cmd.arg(file);}
    let compiled=process(cmd,dir,"",30).await?;if !compiled.success{return Ok(compiled)}
    let mut cmd=command(executable);cmd.args(["-Dfile.encoding=UTF-8","-Dstdout.encoding=UTF-8","-jar"]).arg(junit).args(["execute","--disable-banner","--disable-ansi-colors","--fail-if-no-tests","--class-path",&format!("classes{separator}{}",assertj.display()),"--scan-class-path"]);
    process(cmd,dir,"",30).await
}

async fn run_web(task:&Task,source:&str,grade:bool)->Result<Execution,String> {
    let dir=prepare(task,source)?;
    let request=serde_json::json!({"entry":if task.entry_file.is_empty(){"index.html"}else{&task.entry_file},"checks":if grade{task.web_checks.clone()}else{vec![]}});
    write_file(dir.path(),"request.json",&serde_json::to_string(&request).map_err(|e|e.to_string())?)?;
    write_file(dir.path(),"web-runner.cjs",include_str!("../assets/web-runner.cjs"))?;
    let local=Path::new(env!("CARGO_MANIFEST_DIR")).join("target/ui-tests/node_modules/playwright-core");
    let runtime=if cfg!(debug_assertions)&&local.is_dir()&&local.parent().unwrap().join("react").is_dir(){local}else{
        let root=crate::data_dir()?.join("web-runtime");std::fs::create_dir_all(&root).map_err(|e|e.to_string())?;
        let package=root.join("node_modules/playwright-core");
        if !package.is_dir()||!root.join("node_modules/react").is_dir(){let mut cmd=if cfg!(windows){let mut c=command("cmd.exe");c.args(["/d","/c","npm.cmd"]);c}else{command("npm")};cmd.args(["install","--prefix"]).arg(&root).args(["playwright-core@1.64.0","esbuild@0.28.2","react@19.3.1","react-dom@19.3.1","@tailwindcss/browser@4.3.3","--no-audit","--no-fund"]);let result=process(cmd,&root,"",180).await?;if !result.success{return Ok(result)}}
        package
    };
    write_file(dir.path(),"web-browser.cjs",include_str!("../assets/web-browser.cjs"))?;
    let mut prepare_browser=command(node());prepare_browser.arg("web-browser.cjs").env("MQ3_PLAYWRIGHT",&runtime);
    let prepared=process(prepare_browser,dir.path(),"",240).await?;
    if !prepared.success {return Ok(prepared)}
    write_file(dir.path(),".mq3-browser.json",&prepared.stdout)?;
    let mut cmd=command(node());cmd.arg("web-runner.cjs").env("MQ3_PLAYWRIGHT",runtime);
    let mut result=process(cmd,dir.path(),"",35).await?;
    if let Ok(html)=std::fs::read_to_string(dir.path().join("preview.html")) {if html.len()<2_000_000 {
        // srcdoc has an opaque sandbox origin. Give its preview isolated in-memory storage;
        // grading still exercises the real browser localStorage, including page reloads.
        let storage=r#"<script>(()=>{const values=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>values.has(String(k))?values.get(String(k)):null,setItem:(k,v)=>values.set(String(k),String(v)),removeItem:k=>values.delete(String(k)),clear:()=>values.clear()}})})()</script>"#;
        result.artifacts.push(crate::runner::Artifact::Html{title:task.title.clone(),srcdoc:format!("{storage}{html}")})
    }}
    Ok(result)
}

#[cfg(test)]
mod c_tests {
    use super::mutate_c;
    #[test]
    fn mutate_c_replaces_only_the_first_declaration() {
        let source="int main(void) {\n    // int n = 9;\n    int n = 3, m = 4;\n    int *p = &n;\n    char s[] = \"a;b\";\n    n = 7;\n    printf(\"%d\", n == 3);\n}\n";
        assert_eq!(mutate_c(source,"n","5").unwrap().matches("int n = 5, m = 4;").count(),1);
        assert!(mutate_c(source,"m","8").unwrap().contains("int n = 3, m = 8;"));
        assert!(mutate_c(source,"p","&m").unwrap().contains("int *p = &m;"));
        assert!(mutate_c(source,"s","\"xy\"").unwrap().contains("char s[] = \"xy\";"));
        assert!(mutate_c(source,"missing","1").is_none());
        assert!(mutate_c("int f(int k) { return k; }","k","1").is_none());
    }
}

#[cfg(test)]
mod java_array_prepared_tests {
    #[test]
    fn java_array_initializers_can_be_replaced_without_touching_comments_or_later_assignments() {
        let source="void main() {\n // int[] prices = {9};\n int[] prices = {2, 4};\n prices = new int[]{8};\n}\n";
        let changed=super::mutate_c(source,"prices","{}").expect("prepared Java array declaration");
        assert!(changed.contains("int[] prices = {};"));
        assert!(changed.contains("// int[] prices = {9};"));
        assert!(changed.contains("prices = new int[]{8};"));
    }
}

#[cfg(test)]
mod managed_web_tests {
    #[tokio::test]
    async fn authored_web_checks_run_real_interactions_and_keep_a_preview() {
        let task:crate::repository_course::Task=serde_json::from_value(serde_json::json!({
            "id":"browser-probe","title":"버튼","goal":"클릭 결과를 확인해요.","language":"web",
            "starter_code":"<button>0</button>","solution":"", "entry_file":"index.html",
            "web_checks":[{"kind":"click","selector":"button"},{"kind":"text","selector":"button","pattern":"^1$"}]
        })).unwrap();
        assert!(!super::check(&task,&task.starter_code).await.unwrap().passed);
        let source=r#"<button onclick="this.textContent=Number(this.textContent)+1">0</button>"#;
        assert!(super::check(&task,source).await.unwrap().passed);
        let preview=super::run(&task,source,"").await.unwrap();
        assert!(preview.success,"{}",preview.stderr);
        assert!(preview.artifacts.iter().any(|item|matches!(item,crate::runner::Artifact::Html{srcdoc,..} if srcdoc.contains("<button"))));
    }
}

#[cfg(test)]
mod quoted_web_output_tests {
    #[tokio::test]
    async fn quoted_empty_text_is_checked_after_a_reload() {
        let task:crate::repository_course::Task=serde_json::from_value(serde_json::json!({
            "id":"quote-probe","title":"빈 글","goal":"표시된 글을 확인해요.","language":"web",
            "starter_code":"", "solution":"", "entry_file":"index.html",
            "web_checks":[{"kind":"reload"},{"kind":"text","selector":"output","pattern":"^\"\"$"}]
        })).unwrap();
        let result=super::check(&task,"<output>\"\"</output>").await.unwrap();
        assert!(result.passed,"{}",serde_json::to_string(&result).unwrap());
    }
}

async fn check_sql(task:&Task,source:&str)->Result<TestReport,String> {
    let mut cases=vec![];
    for test in &task.tests {
        let result=crate::sql_practice::execute(&task.files,source).await?;
        let passed=result.success&&result.stdout.trim_end_matches('\n')==test.expected.trim_end_matches('\n');
        cases.push(TestCaseResult{input:"준비된 표".into(),expected:test.expected.clone(),stdout:result.stdout,stderr:result.stderr,passed,state:result.state});
    }
    if cases.iter().all(|case|case.passed) {
        for (index,variation) in task.variations.iter().enumerate() {
            let mut files=task.files.clone();files.extend(variation.files.clone());
            for (key,value) in &variation.values {files.insert(format!("{key}.sql"),value.clone());}
            let result=crate::sql_practice::execute(&files,source).await?;
            let passed=result.success&&result.stdout.trim_end_matches('\n')==variation.expected.trim_end_matches('\n');
            cases.push(TestCaseResult{input:format!("바꾼 표 {}",index+1),expected:variation.expected.clone(),stdout:result.stdout,stderr:result.stderr,passed,state:result.state});
        }
    }
    Ok(TestReport{passed:!cases.is_empty()&&cases.iter().all(|case|case.passed),cases})
}
