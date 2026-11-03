//! GitHub 로그아웃. MQ owns no token: it uses gh's login, so signing out removes gh's stored
//! credential for the one github.com account MQ used, and a marker keeps MQ signed out (no gh call,
//! no automatic sign-in) until the learner reconnects. `gh auth logout` only removes the credential
//! locally; GitHub keeps the token valid until the learner revokes it there (`gh auth logout --help`).
use serde::{Deserialize,Serialize};
use std::path::{Path,PathBuf};
use std::time::Duration;

pub const HOST:&str="github.com";
/// Where the learner revokes gh's tokens. That revokes them on every device, so MQ never does it itself.
pub const REVOKE_URL:&str="https://github.com/settings/applications";
/// gh uses these before any stored credential for github.com (`gh help environment`).
pub const TOKEN_VARIABLES:[&str;2]=["GH_TOKEN","GITHUB_TOKEN"];
pub const SIGNED_OUT_ERROR:&str="MQ에서 GitHub 로그아웃한 상태예요. 다시 연결해야 GitHub를 써요.";
const MARKER:&str="github-signed-out";
const GH_DEADLINE:Duration=Duration::from_secs(30);

#[derive(Clone,Debug,PartialEq,Serialize,Deserialize)]
pub enum StoredToken {
    Removed {switched_to:Option<String>},
    AlreadyAbsent,
    /// gh ran and kept the credential.
    Failed(String),
    /// gh did not run or did not finish, so whether the credential is still there is unknown.
    Unverified(String),
}

/// `stored` is None until gh's answer is saved, or when the marker cannot be read.
#[derive(Clone,Debug,PartialEq,Serialize,Deserialize)]
pub struct SignedOut {pub login:String,pub stored:Option<StoredToken>}

fn marker(directory:&Path)->PathBuf {directory.join(MARKER)}

/// Present while MQ stays signed out (across restarts). An unreadable marker or data folder counts as
/// signed out: MQ must not sign itself back in because a file was briefly locked.
pub fn signed_out()->Option<SignedOut> {
    match crate::data_dir() {
        Ok(directory)=>signed_out_in(&directory),
        Err(_)=>Some(SignedOut{login:String::new(),stored:None}),
    }
}
fn signed_out_in(directory:&Path)->Option<SignedOut> {
    match std::fs::read(marker(directory)) {
        Ok(raw)=>Some(serde_json::from_slice(&raw).unwrap_or(SignedOut{login:String::new(),stored:None})),
        Err(error) if error.kind()==std::io::ErrorKind::NotFound=>None,
        Err(_)=>Some(SignedOut{login:String::new(),stored:None}),
    }
}
pub fn ensure_signed_in()->Result<(),String> {
    if signed_out().is_some() {Err(SIGNED_OUT_ERROR.into())}else{Ok(())}
}
fn save(directory:&Path,state:&SignedOut)->Result<(),String> {
    let raw=serde_json::to_vec(state).map_err(|e|e.to_string())?;
    std::fs::write(marker(directory),raw).map_err(|e|format!("로그아웃 상태를 저장하지 못했어요. {e}"))
}

/// Only the learner's 다시 연결 calls this; startup and background work never do.
pub fn sign_in_again()->Result<(),String> {sign_in_again_in(&crate::data_dir()?)}
fn sign_in_again_in(directory:&Path)->Result<(),String> {
    match std::fs::remove_file(marker(directory)) {
        Err(error) if error.kind()!=std::io::ErrorKind::NotFound=>Err(error.to_string()),
        _=>Ok(()),
    }
}

/// Token variables set for MQ's process. MQ reports them and leaves the learner's environment alone.
pub fn environment_tokens()->Vec<&'static str> {
    TOKEN_VARIABLES.into_iter().filter(|name|std::env::var_os(name).is_some_and(|value|!value.is_empty())).collect()
}

/// Blocking: call from a worker thread. Also the retry after a failed or unverified removal.
pub fn sign_out(login:&str)->Result<SignedOut,String> {
    let logout=if crate::pilot_source::enabled() {crate::pilot_source::gh_logout}else{run_gh_logout};
    sign_out_in(&crate::data_dir()?,login,logout)
}
fn sign_out_in(directory:&Path,login:&str,logout:impl FnOnce(&str)->Result<(bool,String),String>)->Result<SignedOut,String> {
    if login.is_empty() {return Err("로그아웃할 GitHub 계정을 찾지 못했어요.".into())}
    // The marker comes first: if gh fails or MQ closes below, MQ still stops using GitHub.
    save(directory,&SignedOut{login:login.into(),stored:None})?;
    let stored=match logout(login) {
        Ok((success,output))=>classify(login,success,&output),
        Err(error)=>StoredToken::Unverified(error),
    };
    let state=SignedOut{login:login.into(),stored:Some(stored)};
    // gh has already run, so this is no longer "nothing changed": an unsaved result reads as unverified.
    let _=save(directory,&state);
    Ok(state)
}

#[cfg(not(target_os="android"))]
fn run_gh_logout(login:&str)->Result<(bool,String),String> {
    use std::io::Read;
    let mut child=logout_command(crate::setup_terminal::gh_executable(),login).spawn().map_err(|_|"GitHub CLI(gh)를 찾지 못했어요.".to_string())?;
    let (mut stdout,mut stderr)=(child.stdout.take().unwrap(),child.stderr.take().unwrap());
    let out=std::thread::spawn(move ||{let mut text=String::new();let _=stdout.read_to_string(&mut text);text});
    let err=std::thread::spawn(move ||{let mut text=String::new();let _=stderr.read_to_string(&mut text);text});
    let started=std::time::Instant::now();
    // A keychain prompt hidden behind the window must not freeze the dialog forever.
    let status=loop {
        if let Some(status)=child.try_wait().map_err(|e|e.to_string())? {break status}
        if started.elapsed()>GH_DEADLINE {let _=child.kill();let _=child.wait();return Err("gh가 30초 안에 끝나지 않았어요.".into())}
        std::thread::sleep(Duration::from_millis(50));
    };
    Ok((status.success(),format!("{}{}",out.join().unwrap_or_default(),err.join().unwrap_or_default())))
}
#[cfg(target_os="android")]
fn run_gh_logout(_:&str)->Result<(bool,String),String> {Err("GitHub 로그아웃은 데스크톱 앱에서 할 수 있어요.".into())}

fn logout_command(executable:PathBuf,login:&str)->std::process::Command {
    use std::process::Stdio;
    let mut command=std::process::Command::new(executable);
    command.args(["auth","logout","--hostname",HOST,"--user",login]).env("GH_PROMPT_DISABLED","1").env("NO_COLOR","1")
        .stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped());
    // With a token variable set, gh refuses to touch the stored credential; the variable itself stays
    // in the learner's environment and the report names it. Forced colour would put escapes in the account name.
    for name in TOKEN_VARIABLES.into_iter().chain(["CLICOLOR_FORCE","GH_FORCE_TTY"]) {command.env_remove(name);}
    #[cfg(windows)] {use std::os::windows::process::CommandExt;command.creation_flags(0x08000000);}
    command
}

/// Reads gh's own result lines (gh 2.87): "Switched active account for github.com to X" after removing
/// the active account, "not logged in to ..." when there was nothing to remove.
fn classify(login:&str,success:bool,output:&str)->StoredToken {
    if success {
        let prefix=format!("Switched active account for {HOST} to ");
        let switched_to=output.lines().find_map(|line|line.split_once(&prefix).map(|(_,next)|next.trim().to_owned())).filter(|next|!next.is_empty());
        return StoredToken::Removed{switched_to};
    }
    let lower=output.to_ascii_lowercase();
    if lower.contains(&format!("not logged in to {HOST} account {}",login.to_ascii_lowercase()))||lower.contains("not logged in to any hosts") {
        return StoredToken::AlreadyAbsent;
    }
    StoredToken::Failed(output.trim().chars().take(400).collect())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signing_out_persists_its_result_until_the_learner_reconnects() {
        let directory=tempfile::tempdir().unwrap();
        assert_eq!(signed_out_in(directory.path()),None);
        let state=sign_out_in(directory.path(),"mq-fake",|_|Ok((true,"✓ Logged out of github.com account mq-fake\n".into()))).unwrap();
        assert_eq!(state.stored,Some(StoredToken::Removed{switched_to:None}));
        assert_eq!(signed_out_in(directory.path()),Some(state),"a restart reads the same account and result");
        sign_in_again_in(directory.path()).unwrap();
        assert_eq!(signed_out_in(directory.path()),None);
        sign_in_again_in(directory.path()).unwrap();
    }

    #[test]
    fn a_failed_or_unfinished_gh_logout_still_signs_mq_out_and_is_remembered() {
        let directory=tempfile::tempdir().unwrap();
        sign_out_in(directory.path(),"mq-fake",|_|Err("gh가 30초 안에 끝나지 않았어요.".into())).unwrap();
        assert_eq!(signed_out_in(directory.path()).unwrap().stored,Some(StoredToken::Unverified("gh가 30초 안에 끝나지 않았어요.".into())));
        sign_out_in(directory.path(),"mq-fake",|_|Ok((false,"keyring: access denied\n".into()))).unwrap();
        assert_eq!(signed_out_in(directory.path()).unwrap().stored,Some(StoredToken::Failed("keyring: access denied".into())));
    }

    #[test]
    fn an_unreadable_marker_keeps_mq_signed_out() {
        let directory=tempfile::tempdir().unwrap();
        std::fs::write(marker(directory.path()),"not json").unwrap();
        assert_eq!(signed_out_in(directory.path()),Some(SignedOut{login:String::new(),stored:None}));
        std::fs::remove_file(marker(directory.path())).unwrap();
        std::fs::create_dir(marker(directory.path())).unwrap();
        assert!(signed_out_in(directory.path()).is_some(),"a marker that cannot be read is not a sign-in");
    }

    #[test]
    fn logout_asks_gh_for_exactly_the_mq_account() {
        let directory=tempfile::tempdir().unwrap();
        let mut asked=String::new();
        sign_out_in(directory.path(),"mq-fake",|login|{asked=login.into();Ok((true,String::new()))}).unwrap();
        assert_eq!(asked,"mq-fake");
        assert!(sign_out_in(directory.path(),"",|_|panic!("gh must not run without an account")).is_err());
    }

    #[test]
    fn the_gh_command_names_one_github_account_and_drops_token_variables() {
        let command=logout_command(PathBuf::from("gh"),"mq-fake");
        let args:Vec<_>=command.get_args().map(|arg|arg.to_string_lossy().into_owned()).collect();
        assert_eq!(args,["auth","logout","--hostname","github.com","--user","mq-fake"]);
        let envs:Vec<_>=command.get_envs().map(|(name,value)|(name.to_string_lossy().into_owned(),value.map(|v|v.to_string_lossy().into_owned()))).collect();
        for name in TOKEN_VARIABLES.into_iter().chain(["CLICOLOR_FORCE","GH_FORCE_TTY"]) {assert!(envs.contains(&(name.to_owned(),None)),"{name} is removed for gh only");}
        assert!(envs.contains(&("GH_PROMPT_DISABLED".to_owned(),Some("1".to_owned()))));
        assert!(envs.contains(&("NO_COLOR".to_owned(),Some("1".to_owned()))));
    }

    #[test]
    fn gh_results_are_classified_from_its_own_lines() {
        assert_eq!(classify("a",true,"✓ Logged out of github.com account a\n✓ Switched active account for github.com to b\n"),StoredToken::Removed{switched_to:Some("b".into())});
        assert_eq!(classify("a",false,"not logged in to github.com account a\n"),StoredToken::AlreadyAbsent);
        assert_eq!(classify("a",false,"not logged in to any hosts\n"),StoredToken::AlreadyAbsent);
        assert!(matches!(classify("a",false,"not logged in to github.com account b\n"),StoredToken::Failed(_)));
        assert!(matches!(classify("a",false,"failed to write config\n"),StoredToken::Failed(_)));
    }
}
