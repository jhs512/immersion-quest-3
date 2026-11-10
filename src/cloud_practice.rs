//! Owned local cloud practice: an emulated AWS EC2 API (pinned Floci) on this computer, graded by
//! the actual VPC/subnet/instance state it holds and by the grader's own HTTP request.
//!
//! This is trusted local Docker Desktop practice, not a multiuser or security sandbox. Subnet
//! steps run Floci in EC2 mock mode as an unprivileged container. Server steps run a privileged
//! Docker-in-Docker engine (an experiment-grade boundary, see docs/floci-first-lesson-preflight.md)
//! so that Floci only ever receives the nested engine's socket, never the host's.
use super::*;
use serde_json::Value;
use std::io::{Read, Seek, SeekFrom};
use std::net::Ipv4Addr;
use std::time::{Duration, Instant};

const RUNTIME_VERSION: u32 = 2;
const LABEL: &str = "gg.molip.cloud-practice";
const STATE_FILE: &str = "cloud-state.json";
const FLOCI: &str =
    "floci/floci@sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c";
const DIND: &str = "docker@sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e";
const TEMURIN: &str = "public.ecr.aws/docker/library/eclipse-temurin@sha256:c7c3d0bdf7f2bbc5a05a6712ed334d198360105634ea9adf76fca94f381b1e3f";
/// AWS CLI v2 runs from this pinned official image on the practice network: learners need no host install.
const AWS_CLI_IMAGE: &str = "public.ecr.aws/aws-cli/aws-cli:2.39.7@sha256:73f81e380c7974c9f03ac7ccd520ef080f17f443e10582f024c828b970ac8b73";
const SERVER_AMI: &str = "ami-0e0000000000a0025";
/// The guest server is always an x86_64 image, because the lesson launches `t3.micro` (an x86_64
/// instance type) and Floci runs the guest with the platform of the AMI's architecture. On an amd64
/// host this is the native platform, so nothing changes there; an arm64 host (Apple Silicon) runs the
/// guest under Docker Desktop's x86_64 emulation. Floci itself stays on the host's native platform.
const GUEST_PLATFORM: &str = "linux/amd64";
const REGION: &str = "us-east-1";
const HTTP_PORT: &str = "8080";
const USER_DATA: &str = include_str!("../assets/cloud-lab/server-user-data.sh");

#[derive(Clone, Copy, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum CloudGoal {
    /// Exactly one new subnet with `target_cidr` in the prepared VPC.
    CreateSubnet,
    /// One new subnet of `new_prefix` anywhere free in the VPC; prepared subnets stay.
    ChooseSubnet,
    /// One running prepared-image server in the prepared `target_subnet`.
    LaunchServer,
    /// The address file names the prepared server's API private address; HTTP from the client.
    RequestServer,
    /// Create `target_cidr`, run the prepared Java server in it, name its address; HTTP from the client.
    DeployServer,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct CloudSubnet {
    pub name: String,
    pub cidr: String,
}

/// One coherent schema for every cloud step. Prepared resources are declared per step;
/// the fields a goal does not use must stay empty.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct CloudExercise {
    pub goal: CloudGoal,
    pub vpc_cidr: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub subnets: Vec<CloudSubnet>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub client_subnet: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub server_subnet: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub target_cidr: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub target_subnet: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub new_prefix: Option<u8>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub address_file: Option<String>,
    /// Prepared files shown in the editor above the terminal; other prepared files stay terminal-only.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub editable: Vec<String>,
}

// -- addresses ---------------------------------------------------------------------------
fn cidr(value: &str) -> Option<(u32, u8)> {
    let (address, prefix) = value.split_once('/')?;
    let address = u32::from(address.parse::<Ipv4Addr>().ok()?);
    let prefix: u8 = prefix.parse().ok().filter(|p| *p <= 32)?;
    (address & !mask(prefix) == 0).then_some((address, prefix))
}
fn mask(prefix: u8) -> u32 {
    if prefix == 0 { 0 } else { u32::MAX << (32 - prefix) }
}
fn contains(outer: (u32, u8), inner: (u32, u8)) -> bool {
    inner.1 >= outer.1 && inner.0 & mask(outer.1) == outer.0
}
fn holds(block: (u32, u8), address: Ipv4Addr) -> bool {
    u32::from(address) & mask(block.1) == block.0
}

impl CloudExercise {
    pub fn guest(&self) -> bool {
        matches!(self.goal, CloudGoal::LaunchServer | CloudGoal::RequestServer | CloudGoal::DeployServer)
    }
    fn subnet(&self, name: &str) -> Option<&CloudSubnet> {
        self.subnets.iter().find(|s| s.name == name)
    }
    pub fn validate(&self) -> Result<(), String> {
        let bad = || Err::<(), String>("클라우드 실습 구성을 확인하세요.".into());
        let Some(vpc) = cidr(&self.vpc_cidr).filter(|c| (16..=24).contains(&c.1)) else { return bad() };
        if self.subnets.len() > 4 {
            return bad();
        }
        let file = |f: &String| crate::repository_course::safe_file(f) && !f.contains('/');
        if self.editable.len() > 4 || !self.editable.iter().all(file) || self.editable.iter().enumerate().any(|(i, f)| self.editable[..i].contains(f)) {
            return bad();
        }
        let mut blocks: Vec<(u32, u8)> = vec![];
        for subnet in &self.subnets {
            let named = !subnet.name.is_empty()
                && subnet.name.len() <= 8
                && subnet.name.bytes().all(|b| b.is_ascii_uppercase() || b.is_ascii_digit());
            let Some(block) = cidr(&subnet.cidr).filter(|c| (16..=28).contains(&c.1)) else { return bad() };
            if !named
                || !contains(vpc, block)
                || blocks.iter().any(|b| contains(*b, block) || contains(block, *b))
                || self.subnets.iter().filter(|s| s.name == subnet.name).count() != 1
            {
                return bad();
            }
            blocks.push(block);
        }
        let free_target = |value: &Option<String>| {
            value.as_deref().and_then(cidr).is_some_and(|t| {
                (16..=28).contains(&t.1) && contains(vpc, t) && !blocks.iter().any(|b| contains(*b, t) || contains(t, *b))
            })
        };
        let known = |value: &Option<String>| value.as_deref().is_some_and(|n| self.subnet(n).is_some());
        let address = || {
            self.address_file.as_deref().is_some_and(|f| crate::repository_course::safe_file(f) && !f.contains('/'))
        };
        let ok = match self.goal {
            CloudGoal::CreateSubnet => {
                free_target(&self.target_cidr)
                    && self.client_subnet.is_none() && self.server_subnet.is_none() && self.target_subnet.is_none()
                    && self.new_prefix.is_none() && self.address_file.is_none()
            }
            CloudGoal::ChooseSubnet => {
                self.new_prefix.is_some_and(|p| p >= vpc.1 && (16..=28).contains(&p))
                    && !self.subnets.is_empty()
                    && self.target_cidr.is_none() && self.client_subnet.is_none() && self.server_subnet.is_none()
                    && self.target_subnet.is_none() && self.address_file.is_none()
            }
            CloudGoal::LaunchServer => {
                known(&self.target_subnet) && self.subnets.len() >= 2
                    && self.client_subnet.is_none() && self.server_subnet.is_none() && self.target_cidr.is_none()
                    && self.new_prefix.is_none() && self.address_file.is_none()
            }
            CloudGoal::RequestServer => {
                known(&self.client_subnet) && known(&self.server_subnet) && self.client_subnet != self.server_subnet
                    && address() && self.target_cidr.is_none() && self.target_subnet.is_none() && self.new_prefix.is_none()
            }
            CloudGoal::DeployServer => {
                known(&self.client_subnet) && free_target(&self.target_cidr) && address()
                    && self.server_subnet.is_none() && self.target_subnet.is_none() && self.new_prefix.is_none()
            }
        };
        if ok { Ok(()) } else { bad() }
    }
    fn fixture(&self) -> String {
        use sha2::{Digest, Sha256};
        let raw = serde_json::to_string(self).unwrap_or_default();
        format!("{:x}", Sha256::digest(format!("{RUNTIME_VERSION}\n{FLOCI}\n{DIND}\n{TEMURIN}\n{raw}")))
    }
}

// -- owned state -------------------------------------------------------------------------
#[derive(Clone, Debug, Serialize, Deserialize)]
struct Instance {
    id: String,
    ip: String,
    container: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
struct State {
    version: u32,
    fixture: String,
    guest: bool,
    port: u16,
    ready: bool,
    vpc_id: String,
    /// prepared subnet name -> (subnet id, cidr)
    subnets: BTreeMap<String, (String, String)>,
    client: Option<Instance>,
    server: Option<Instance>,
    guest_image: Option<String>,
}
fn owner(root: &Path) -> String {
    use sha2::{Digest, Sha256};
    format!("{:x}", Sha256::digest(root.to_string_lossy().as_bytes()))[..16].to_string()
}
fn names(root: &Path) -> (String, String, String) {
    let o = owner(root);
    (format!("mq-cloud-{o}"), format!("mq-cloud-{o}-runtime"), format!("mq-cloud-{o}-docker"))
}
fn load(root: &Path) -> Result<State, String> {
    let raw = std::fs::read(root.join(STATE_FILE)).map_err(|e| e.to_string())?;
    serde_json::from_slice(&raw).map_err(|_| "클라우드 실습 상태 파일을 읽지 못했어요. 초기화하세요.".to_string())
}
fn save(root: &Path, state: &State) -> Result<(), String> {
    std::fs::write(root.join(STATE_FILE), serde_json::to_vec_pretty(state).unwrap()).map_err(|e| e.to_string())
}
fn endpoint(state: &State) -> String {
    format!("http://127.0.0.1:{}", state.port)
}

// -- processes ---------------------------------------------------------------------------
struct Run {
    ok: bool,
    out: String,
    err: String,
}
fn run(mut command: Command, seconds: u64, label: &str) -> Result<Run, String> {
    // File-backed output prevents a full pipe from blocking the timeout.
    let mut stdout = tempfile::tempfile().map_err(|e| e.to_string())?;
    let mut stderr = tempfile::tempfile().map_err(|e| e.to_string())?;
    command
        .stdin(std::process::Stdio::null())
        .stdout(stdout.try_clone().map_err(|e| e.to_string())?)
        .stderr(stderr.try_clone().map_err(|e| e.to_string())?);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let mut child = command.spawn().map_err(|_| format!("{label}를 실행하지 못했어요."))?;
    let start = Instant::now();
    let status = loop {
        if let Some(status) = child.try_wait().map_err(|e| e.to_string())? {
            break status;
        }
        if start.elapsed() > Duration::from_secs(seconds) {
            let _ = child.kill();
            let _ = child.wait();
            return Err(format!("{label} 응답을 기다리다 중단했어요. 실습 환경을 확인한 뒤 다시 시도하세요."));
        }
        std::thread::sleep(Duration::from_millis(50));
    };
    let (mut out, mut err) = (String::new(), String::new());
    stdout.seek(SeekFrom::Start(0)).map_err(|e| e.to_string())?;
    stderr.seek(SeekFrom::Start(0)).map_err(|e| e.to_string())?;
    stdout.take(400_000).read_to_string(&mut out).map_err(|e| e.to_string())?;
    stderr.take(150_000).read_to_string(&mut err).map_err(|e| e.to_string())?;
    Ok(Run { ok: status.success(), out, err })
}
fn docker_cli() -> Result<PathBuf, String> {
    crate::docker_lab::cli().ok_or_else(|| "Docker를 찾을 수 없어요. Docker Desktop을 설치하고 Linux 엔진을 실행하세요.".into())
}
fn docker(args: &[&str], seconds: u64) -> Result<Run, String> {
    let cli = docker_cli()?;
    let mut command = Command::new(&cli);
    command.env("PATH", crate::docker_lab::search_path(&cli)).args(args);
    run(command, seconds, "Docker")
}
fn require(args: &[&str], seconds: u64) -> Result<String, String> {
    let result = docker(args, seconds)?;
    if result.ok {
        Ok(result.out)
    } else {
        Err(format!(
            "클라우드 실습 환경을 준비하지 못했어요. Docker Desktop Linux 엔진을 확인하세요.\n{}",
            result.err.chars().take(1200).collect::<String>()
        ))
    }
}
fn inner(state_container: &str, args: &[&str], seconds: u64) -> Result<Run, String> {
    let mut all = vec!["exec", state_container, "docker"];
    all.extend_from_slice(args);
    docker(&all, seconds)
}
fn inner_ok(container: &str, args: &[&str], seconds: u64) -> Result<String, String> {
    let r = inner(container, args, seconds)?;
    if r.ok { Ok(r.out) } else { Err(format!("클라우드 실습 서버 환경을 준비하지 못했어요.\n{}", r.err.chars().take(1200).collect::<String>())) }
}

/// Inside the practice network the owned runtime answers at its container name.
fn inner_endpoint(root: &Path) -> String {
    format!("http://{}:4566", names(root).1)
}
/// The fixed environment of every AWS CLI container: dummy keys, no files from the host account.
const AWS_CONTAINER_ENV: [&str; 8] = [
    "AWS_ACCESS_KEY_ID=test", "AWS_SECRET_ACCESS_KEY=test", "AWS_DEFAULT_REGION=us-east-1", "AWS_REGION=us-east-1",
    "AWS_EC2_METADATA_DISABLED=true", "AWS_PAGER=", "AWS_CONFIG_FILE=/dev/null", "AWS_SHARED_CREDENTIALS_FILE=/dev/null",
];
/// `docker run` arguments for one AWS CLI call on this practice's own network, mounting `mount` at `at`.
fn aws_container_args(root: &Path, mount: &str, at: &str) -> Vec<String> {
    let (network, _, _) = names(root);
    let mut args: Vec<String> = ["run", "--rm", "--network", &network, "--label", &format!("{LABEL}={}", owner(root))].map(String::from).to_vec();
    for value in AWS_CONTAINER_ENV {
        args.extend(["-e".into(), value.into()]);
    }
    args.extend(["-v".into(), format!("{mount}:{at}"), "-w".into(), at.split(':').next().unwrap_or(at).into(), AWS_CLI_IMAGE.into()]);
    args.extend(["--endpoint-url".into(), inner_endpoint(root)]);
    args
}
/// The pinned AWS CLI image is on this engine, pulled by digest if not.
fn ensure_aws_image() -> Result<(), String> {
    if docker(&["image", "inspect", AWS_CLI_IMAGE], 30)?.ok {
        return Ok(());
    }
    let pulled = docker(&["pull", AWS_CLI_IMAGE], 900)?;
    if pulled.ok { Ok(()) } else { Err("AWS CLI 실습 이미지를 받지 못했어요. 인터넷 연결과 Docker Desktop을 확인한 뒤 다시 여세요.".into()) }
}
fn empty_config(root: &Path) -> Result<PathBuf, String> {
    let path = root.join("cloud-aws-empty-config");
    match std::fs::symlink_metadata(&path) {
        Ok(meta) if meta.is_file() && !meta.file_type().is_symlink() && meta.len() == 0 => {}
        Ok(_) => return Err("실습용 AWS 설정 파일이 바뀌었어요. 초기화해서 새 환경을 만드세요.".into()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            // create_new refuses a link or file that appears after the metadata check.
            std::fs::OpenOptions::new().write(true).create_new(true).open(&path).map_err(|e| e.to_string())?;
        }
        Err(error) => return Err(error.to_string()),
    }
    Ok(path)
}

struct Api {
    ok: bool,
    json: Value,
    err: String,
}
/// Every backend API call names the owned loopback endpoint explicitly.
fn api(root: &Path, state: &State, args: &[&str]) -> Result<Api, String> {
    if state.port == 0 {
        return Err("클라우드 실습 주소가 없어요. 초기화하세요.".into());
    }
    // The practice root is mounted read-only so prepared inputs such as user-data are readable as file:///mq/...
    let mut all = aws_container_args(root, &root.to_string_lossy(), "/mq:ro");
    all.extend(["--region", REGION, "--output", "json", "--cli-connect-timeout", "5", "--cli-read-timeout", "30"].map(String::from));
    all.extend(args.iter().map(|a| a.to_string()));
    let all: Vec<&str> = all.iter().map(String::as_str).collect();
    let r = docker(&all, 90)?;
    if !r.ok && ["Could not connect", "Connect timeout", "Read timeout", "Connection was closed", "Connection reset"]
        .iter()
        .any(|m| r.err.contains(m))
    {
        return Err("실습용 클라우드 API에 연결하지 못했어요. 실습 컨테이너가 멈췄다면 초기화하세요.".into());
    }
    let json = if r.ok && !r.out.trim().is_empty() {
        serde_json::from_str(&r.out).map_err(|_| "실습용 클라우드 API 응답을 읽지 못했어요.".to_string())?
    } else {
        Value::Null
    };
    Ok(Api { ok: r.ok, json, err: r.err })
}
fn api_ok(root: &Path, state: &State, args: &[&str]) -> Result<Value, String> {
    let r = api(root, state, args)?;
    if r.ok { Ok(r.json) } else { Err(format!("실습용 클라우드 API가 준비 요청을 거절했어요.\n{}", r.err.chars().take(800).collect::<String>())) }
}
fn wait<T>(seconds: u64, mut step: impl FnMut() -> Result<Option<T>, String>) -> Result<Option<T>, String> {
    let start = Instant::now();
    loop {
        if let Some(value) = step()? {
            return Ok(Some(value));
        }
        if start.elapsed() > Duration::from_secs(seconds) {
            return Ok(None);
        }
        std::thread::sleep(Duration::from_millis(700));
    }
}

// -- lifecycle ---------------------------------------------------------------------------
/// Remove only resources carrying this root's exact owner label, then the state file.
pub(super) fn cleanup_at(root: &Path) -> Result<(), String> {
    if !root.join(STATE_FILE).exists() {
        return Ok(());
    }
    remove_owned(&owner(root))?;
    std::fs::remove_file(root.join(STATE_FILE)).map_err(|e| e.to_string())
}
fn remove_owned(owner: &str) -> Result<(), String> {
    let filter = format!("label={LABEL}={owner}");
    for id in require(&["ps", "-aq", "--no-trunc", "--filter", &filter], 20)?.split_whitespace() {
        // -v also removes the container's anonymous volumes; named owned volumes go below.
        require(&["rm", "-f", "-v", id], 60)?;
    }
    for id in require(&["network", "ls", "-q", "--no-trunc", "--filter", &filter], 20)?.split_whitespace() {
        require(&["network", "rm", id], 30)?;
    }
    for name in require(&["volume", "ls", "-q", "--filter", &filter], 20)?.split_whitespace() {
        require(&["volume", "rm", name], 60)?;
    }
    Ok(())
}

/// Running, labelled with this root's owner, and answering on the owned endpoint.
fn verify_runtime(root: &Path, state: &State) -> Result<(), String> {
    let (_, container, _) = names(root);
    let format = format!("{{{{.State.Running}}}} {{{{index .Config.Labels \"{LABEL}\"}}}}");
    let p = docker(&["inspect", "--format", &format, &container], 15)?;
    if !p.ok || p.out.trim() != format!("true {}", owner(root)) {
        return Err("클라우드 실습 컨테이너가 실행 중이 아니거나 소유 정보가 달라요. 초기화해서 새 환경을 만드세요.".into());
    }
    let port = require(&["port", &container, "4566/tcp"], 15)?;
    if port.lines().map(str::trim).filter(|l| !l.is_empty()).collect::<Vec<_>>() != [format!("127.0.0.1:{}", state.port)] {
        return Err("클라우드 실습 주소가 준비 때와 달라요. 초기화하세요.".into());
    }
    if state.guest {
        let running = inner(&container, &["inspect", "--format", "{{.State.Running}}", "floci"], 15)?;
        if !running.ok || running.out.trim() != "true" {
            return Err("실습용 클라우드 API가 멈췄어요. 초기화하세요.".into());
        }
        for instance in [&state.client, &state.server].into_iter().flatten() {
            let r = inner(&container, &["inspect", "--format", "{{.State.Running}}", &instance.container], 15)?;
            if !r.ok || r.out.trim() != "true" {
                return Err("준비된 서버가 멈췄어요. 초기화해서 새 환경을 만드세요.".into());
            }
        }
    }
    api(root, state, &["ec2", "describe-vpcs"]).and_then(|r| {
        if r.ok { Ok(()) } else { Err("실습용 클라우드 API가 응답하지 않아요. 초기화하세요.".into()) }
    })
}

fn sq(value: &str) -> String {
    format!("'{}'", value.replace('\'', r"'\''"))
}
fn posix(path: &Path) -> String {
    path.to_string_lossy().replace('\\', "/")
}
/// MQ's own `aws` entrypoint for the practice terminal: normal syntax, only the owned endpoint.
/// The CLI itself runs in the pinned image on the practice network, with the current folder at /aws.
fn aws_wrapper(endpoint: &str, docker: &Path, root: &Path) -> String {
    let mut run: Vec<String> = aws_container_args(root, "HERE", "/aws").iter().map(|a| sq(a)).collect();
    run.insert(1, "-i".into());
    let run = run.join(" ").replace(&sq("HERE:/aws"), "\"$here:/aws\"");
    format!(
        r#"#!/bin/bash
# MQ 실습용 aws: 이 실습의 로컬 주소로만 요청해요.
owned={owned}
args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --endpoint-url) shift; value="${{1-}}"
      if [ "$value" != "$owned" ]; then echo "이 실습의 aws는 실습 주소($owned)로만 요청해요. --endpoint-url 값을 확인하세요." >&2; exit 2; fi ;;
    --endpoint-url=*) value="${{1#--endpoint-url=}}"
      if [ "$value" != "$owned" ]; then echo "이 실습의 aws는 실습 주소($owned)로만 요청해요. --endpoint-url 값을 확인하세요." >&2; exit 2; fi ;;
    --profile|--profile=*|--ca-bundle|--ca-bundle=*|--no-verify-ssl|--no-sign-request)
      echo "이 실습에서는 $1 옵션을 쓰지 않아요." >&2; exit 2 ;;
    --*)
      # AWS CLI accepts abbreviated global options. Reject those prefixes too:
      # --endp must not override the owned endpoint passed to the CLI.
      opt="${{1%%=*}}"
      for guarded in --endpoint-url --profile --ca-bundle --no-verify-ssl --no-sign-request; do
        if [[ "$guarded" == "$opt"* ]]; then
          echo "실습용 aws에서는 옵션 이름을 끝까지 적어 주세요: $1" >&2; exit 2
        fi
      done
      args+=("$1") ;;
    *) args+=("$1") ;;
  esac
  shift
done
# Git Bash gives C:/... with -W; other shells' pwd is already a host path.
here="$(pwd -W 2>/dev/null || pwd)"
export MSYS_NO_PATHCONV=1
exec {docker} {run} "${{args[@]}}"
"#,
        owned = sq(endpoint),
        docker = sq(&posix(docker)),
    )
}
/// The prepared request command: the client guest's own HTTP request to one IPv4 address.
fn client_wrapper(docker: &Path, runtime: &str, client: &str) -> String {
    format!(
        r#"#!/bin/bash
# 준비된 클라이언트 서버 안에서 HTTP 요청을 보내요.
# A Windows `--output text` file ends in CRLF; drop surrounding whitespace before checking.
address="${{1-}}"; address="${{address#"${{address%%[![:space:]]*}}"}}"; address="${{address%"${{address##*[![:space:]]}}"}}"
if [ $# -ne 1 ] || ! [[ "$address" =~ ^[0-9]{{1,3}}(\.[0-9]{{1,3}}){{3}}$ ]]; then echo "사용법: client-request <IPv4 주소>" >&2; exit 2; fi
export MSYS_NO_PATHCONV=1
exec {docker} exec {runtime} docker exec {client} java /opt/mq/HttpCheck.java "$address" {port}
"#,
        docker = sq(&posix(docker)),
        runtime = sq(runtime),
        client = sq(client),
        port = HTTP_PORT,
    )
}

impl GitPractice {
    pub fn cleanup_cloud(&self) -> Result<(), String> {
        cleanup_at(self.root())
    }
    pub(super) fn release_cloud_demo(&self) {
        if self.exercise.cloud_demonstration {
            let _ = self.cleanup_cloud();
        }
    }
    /// Prepare (or reconnect to) this practice's owned cloud and return the terminal environment.
    pub fn prepare_cloud(&self) -> Result<Vec<(String, String)>, String> {
        let Some(exercise) = &self.exercise.cloud else { return Ok(vec![]) };
        exercise.validate()?;
        let root = self.root();
        // Like a Docker lesson: start installed local Docker Desktop once and wait for its engine.
        crate::docker_lab::ensure_engine(&docker_cli()?)?;
        if require(&["info", "--format", "{{.OSType}}"], 20)?.trim() != "linux" {
            return Err("Docker Desktop을 Linux 컨테이너 모드로 실행하세요.".into());
        }
        ensure_aws_image()?;
        if root.join(STATE_FILE).exists() {
            let state = load(root)?;
            if !state.ready || state.version != RUNTIME_VERSION || state.fixture != exercise.fixture() {
                return Err("실습 준비가 중단됐거나 문제의 시작 상태가 바뀌었어요. 초기화해서 새 환경을 만드세요.".into());
            }
            verify_runtime(root, &state)?;
            return self.cloud_env(&state);
        }
        let mut state = State {
            version: RUNTIME_VERSION,
            fixture: exercise.fixture(),
            guest: exercise.guest(),
            port: 0,
            ready: false,
            vpc_id: String::new(),
            subnets: BTreeMap::new(),
            client: None,
            server: None,
            guest_image: None,
        };
        // Written before the first resource so a failed preparation can always be cleaned.
        save(root, &state)?;
        if let Err(error) = self.create_cloud(exercise, &mut state) {
            let cleanup = cleanup_at(root);
            return Err(format!("{error}{}", cleanup.err().map(|e| format!("\n실습 정리도 실패했어요: {e}")).unwrap_or_default()));
        }
        state.ready = true;
        save(root, &state)?;
        self.cloud_env(&state)
    }

    fn create_cloud(&self, exercise: &CloudExercise, state: &mut State) -> Result<(), String> {
        let root = self.root();
        let (network, container, volume) = names(root);
        let label = format!("{LABEL}={}", owner(root));
        require(&["network", "create", "--label", &label, &network], 30)?;
        if state.guest {
            require(&["volume", "create", "--label", &label, &volume], 30)?;
            // Privileged with the host cgroup namespace: needed for Floci's nested guests
            // (preflight). An experiment-grade boundary, not a security sandbox.
            require(&[
                "run", "-d", "--name", &container, "--label", &label, "--privileged", "--cgroupns=host",
                "--cpus", "4", "--memory", "6g", "--pids-limit", "2048", "--network", &network,
                "-p", "127.0.0.1::4566", "-v", &format!("{volume}:/var/lib/docker"),
                "--entrypoint", "dockerd", DIND, "--host=unix:///var/run/docker.sock", "--storage-driver=overlay2",
            ], 300)?;
        } else {
            require(&[
                "run", "-d", "--name", &container, "--label", &label, "--network", &network,
                "-p", "127.0.0.1::4566", "--cpus", "1", "--memory", "1g", "--pids-limit", "512",
                // The image's floci uid skips the entrypoint's root-only chroot step.
                "--user", "1001:0", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                // Explicit tmpfs: the image's VOLUME /app/data would otherwise become an anonymous volume.
                "--tmpfs", "/app/data:rw,size=64m,uid=1001,gid=0,mode=0700",
                "-e", "FLOCI_STORAGE_MODE=memory", "-e", "FLOCI_SERVICES_EC2_MOCK=true", FLOCI,
            ], 300)?;
        }
        let published = require(&["port", &container, "4566/tcp"], 15)?;
        let lines: Vec<&str> = published.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
        state.port = match lines.as_slice() {
            [one] => one.strip_prefix("127.0.0.1:").and_then(|p| p.parse().ok()).ok_or("실습 포트를 확인하지 못했어요.")?,
            _ => return Err("실습 포트를 확인하지 못했어요.".into()),
        };
        save(root, state)?;
        if state.guest {
            self.create_guest_runtime(&container, state)?;
        }
        if wait(180, || Ok(api(root, state, &["ec2", "describe-vpcs"]).ok().filter(|r| r.ok)))?.is_none() {
            return Err("실습용 클라우드 API가 시작되지 않았어요. Docker 상태를 확인한 뒤 초기화하세요.".into());
        }
        let vpc = api_ok(root, state, &["ec2", "create-vpc", "--cidr-block", &exercise.vpc_cidr])?;
        state.vpc_id = vpc["Vpc"]["VpcId"].as_str().ok_or("VPC를 준비하지 못했어요.")?.into();
        for subnet in &exercise.subnets {
            let made = api_ok(root, state, &["ec2", "create-subnet", "--vpc-id", &state.vpc_id, "--cidr-block", &subnet.cidr])?;
            let id = made["Subnet"]["SubnetId"].as_str().ok_or("서브넷을 준비하지 못했어요.")?;
            state.subnets.insert(subnet.name.clone(), (id.into(), subnet.cidr.clone()));
        }
        if let Some(name) = &exercise.client_subnet {
            state.client = Some(self.launch(state, &state.subnets[name].0.clone(), false)?);
        }
        if let Some(name) = &exercise.server_subnet {
            let server = self.launch(state, &state.subnets[name].0.clone(), true)?;
            let client = state.client.clone().ok_or("클라이언트가 준비되지 않았어요.")?;
            // API `running` is not HTTP readiness: wait until the client actually gets an answer.
            if wait(180, || Ok(probe(&container, &client, &server.ip)?.filter(|p| p.ok)))?.is_none() {
                return Err("준비된 서버가 HTTP에 응답하지 않았어요. 초기화해서 다시 준비하세요.".into());
            }
            state.server = Some(server);
        }
        if exercise.guest() && !self.work().join("server-user-data.sh").exists() {
            std::fs::write(self.work().join("server-user-data.sh"), USER_DATA).map_err(|e| e.to_string())?;
        }
        Ok(())
    }

    fn create_guest_runtime(&self, container: &str, state: &mut State) -> Result<(), String> {
        let root = self.root();
        if wait(90, || Ok(inner(container, &["info"], 20)?.ok.then_some(())))?.is_none() {
            return Err("실습 서버용 Docker 엔진이 시작되지 않았어요.".into());
        }
        // The nested engine refers to each pinned image by a reference whose provenance was checked:
        // the digest itself after a registry pull, or the verified image ID after a cache transfer.
        let mut local = BTreeMap::new();
        for image in [FLOCI, TEMURIN] {
            let reference = if inner(container, &["pull", "--platform", image_platform(image), image], 600)?.ok {
                pulled_reference(container, image)?
            } else {
                let loaded = transfer_image(container, image)?;
                transferred_reference(container, image, &loaded)?
            };
            local.insert(image, reference);
        }
        // Guest input comes only from sources embedded in the app.
        let input = root.join("cloud-input");
        std::fs::create_dir_all(&input).map_err(|e| e.to_string())?;
        let dockerfile = include_str!("../assets/cloud-lab/Dockerfile").replace(TEMURIN, &local[TEMURIN]);
        for (name, body) in [
            ("Dockerfile", dockerfile.as_str()),
            ("HelloServer.java", include_str!("../assets/cloud-lab/HelloServer.java")),
            ("HttpCheck.java", include_str!("../assets/cloud-lab/HttpCheck.java")),
            ("server-user-data.sh", USER_DATA),
        ] {
            std::fs::write(input.join(name), body).map_err(|e| e.to_string())?;
        }
        require(&["cp", &input.to_string_lossy(), &format!("{container}:/mq-input")], 60)?;
        let tag = format!("mq-cloud/java25-http-guest:{}", owner(root));
        inner_ok(container, &["build", "--pull=false", "--platform", GUEST_PLATFORM, "-t", &tag, "/mq-input"], 600)?;
        let id = inner_ok(container, &["image", "inspect", "--format", "{{.Id}}", &tag], 30)?.trim().to_string();
        // The AMI architecture is what the built guest image actually is, not the app's own build.
        let built = inner_ok(container, &["image", "inspect", "--format", "{{.Architecture}}", &tag], 30)?;
        let architecture = ami_architecture(built.trim()).ok_or("서버 이미지의 CPU 종류를 확인하지 못했어요.")?;
        let catalog = format!(
            "defaultDockerImage: {id}\nimages:\n  - imageId: {SERVER_AMI}\n    dockerImage: {id}\n    name: mq-java25-http\n    description: MQ prepared Java 25 HTTP server\n    state: available\n    ownerId: \"000000000000\"\n    architecture: {architecture}\n    rootDeviceType: ebs\n    rootDeviceName: /dev/xvda\n    virtualizationType: hvm\n    creationDate: \"2026-11-09T00:00:00.000Z\"\n"
        );
        std::fs::write(input.join("image-catalog.yaml"), catalog).map_err(|e| e.to_string())?;
        require(&["cp", &input.join("image-catalog.yaml").to_string_lossy(), &format!("{container}:/mq-input/image-catalog.yaml")], 30)?;
        inner_ok(container, &[
            "run", "-d", "--name", "floci", "--cpus", "2", "--memory", "2g", "--pids-limit", "512", "--network", "host",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "-v", "/mq-input/image-catalog.yaml:/etc/floci/image-catalog.yaml:ro",
            "--tmpfs", "/app/data:rw,size=256m",
            "-e", &format!("FLOCI_DOCKER_RESOURCE_NAMESPACE=mq-cloud-{}", owner(root)),
            "-e", "FLOCI_STORAGE_MODE=memory",
            "-e", "FLOCI_SERVICES_EC2_PUBLISH_SECURITY_GROUP_PORTS=false",
            "-e", "FLOCI_SERVICES_EC2_IMAGE_CATALOG_PATH=/etc/floci/image-catalog.yaml",
            &local[FLOCI],
        ], 120)?;
        state.guest_image = Some(id);
        save(root, state)
    }

    fn launch(&self, state: &State, subnet: &str, user_data: bool) -> Result<Instance, String> {
        let root = self.root();
        let data = "file:///mq/cloud-input/server-user-data.sh".to_string();
        let mut args = vec!["ec2", "run-instances", "--image-id", SERVER_AMI, "--instance-type", "t3.micro", "--count", "1", "--subnet-id", subnet];
        if user_data {
            args.extend(["--user-data", data.as_str()]);
        }
        let out = api_ok(root, state, &args)?;
        let id = out["Instances"][0]["InstanceId"].as_str().ok_or("준비 서버를 시작하지 못했어요.")?.to_string();
        let running = wait(240, || {
            let d = api_ok(root, state, &["ec2", "describe-instances", "--instance-ids", &id])?;
            let i = &d["Reservations"][0]["Instances"][0];
            Ok((i["State"]["Name"] == "running").then(|| i["PrivateIpAddress"].as_str().unwrap_or_default().to_string()))
        })?
        .ok_or("준비 서버가 실행 상태가 되지 않았어요.")?;
        let (_, container, _) = names(root);
        let guest = guest_container(&container, &id)?.ok_or("준비 서버의 컨테이너를 찾지 못했어요.")?;
        Ok(Instance { id, ip: running, container: guest["Id"].as_str().unwrap_or_default().into() })
    }

    fn cloud_env(&self, state: &State) -> Result<Vec<(String, String)>, String> {
        let root = self.root();
        let url = endpoint(state);
        let config = empty_config(root)?;
        let bin = root.join("cloud-bin");
        std::fs::create_dir_all(&bin).map_err(|e| e.to_string())?;
        std::fs::write(bin.join("aws"), aws_wrapper(&url, &docker_cli()?, root)).map_err(|e| e.to_string())?;
        let (_, container, _) = names(root);
        if let Some(client) = &state.client {
            std::fs::write(bin.join("client-request"), client_wrapper(&docker_cli()?, &container, &client.container)).map_err(|e| e.to_string())?;
        }
        #[cfg(unix)]
        for name in ["aws", "client-request"] {
            use std::os::unix::fs::PermissionsExt;
            if bin.join(name).exists() {
                std::fs::set_permissions(bin.join(name), std::fs::Permissions::from_mode(0o755)).map_err(|e| e.to_string())?;
            }
        }
        let mut env: Vec<(String, String)> = vec![
            ("LAB_ENDPOINT".into(), url.clone()),
            ("LAB_VPC_ID".into(), state.vpc_id.clone()),
            ("AWS_ACCESS_KEY_ID".into(), "test".into()),
            ("AWS_SECRET_ACCESS_KEY".into(), "test".into()),
            ("AWS_DEFAULT_REGION".into(), REGION.into()),
            ("AWS_REGION".into(), REGION.into()),
            ("AWS_ENDPOINT_URL".into(), url),
            ("AWS_CONFIG_FILE".into(), config.to_string_lossy().into_owned()),
            ("AWS_SHARED_CREDENTIALS_FILE".into(), config.to_string_lossy().into_owned()),
            ("AWS_EC2_METADATA_DISABLED".into(), "true".into()),
            ("AWS_PAGER".into(), String::new()),
            ("MSYS_NO_PATHCONV".into(), "1".into()),
        ];
        // Inherited real-account settings must not reach the practice shell.
        for key in ["AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_SESSION_TOKEN", "AWS_SECURITY_TOKEN", "AWS_CA_BUNDLE", "AWS_ROLE_ARN",
            "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_CONTAINER_CREDENTIALS_FULL_URI", "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"] {
            env.push((key.into(), String::new()));
        }
        for (name, (id, _)) in &state.subnets {
            env.push((format!("LAB_SUBNET_{name}_ID"), id.clone()));
        }
        if state.guest {
            env.push(("LAB_SERVER_AMI".into(), SERVER_AMI.into()));
        }
        if let Some(server) = &state.server {
            env.push(("LAB_SERVER_ID".into(), server.id.clone()));
        }
        if let Some(client) = &state.client {
            env.push(("LAB_CLIENT_ID".into(), client.id.clone()));
        }
        let docker = docker_cli()?;
        let mut path = vec![bin];
        path.extend(std::env::split_paths(&crate::docker_lab::search_path(&docker)));
        env.push(("PATH".into(), std::env::join_paths(path).map_err(|e| e.to_string())?.to_string_lossy().into_owned()));
        Ok(env)
    }

    /// Grade the owned cloud state. Runtime problems are errors, never wrong answers.
    pub fn check_cloud(&self) -> Result<crate::runner::TestReport, String> {
        use crate::runner::{TestCaseResult, TestReport};
        let exercise = self.exercise.cloud.as_ref().ok_or("클라우드 실습이 아니에요.")?;
        let root = self.root();
        let state = load(root)?;
        if !state.ready || state.fixture != exercise.fixture() {
            return Err("실습 준비가 끝나지 않았거나 시작 상태가 달라요. 초기화하세요.".into());
        }
        verify_runtime(root, &state)?;
        let mut cases = vec![];
        let mut record = |name: &str, passed: bool, expected: &str, actual: String| {
            cases.push(TestCaseResult { input: name.into(), expected: expected.into(), stdout: actual, stderr: String::new(), passed, state: "cloud_state".into() })
        };
        let vpcs = api(root, &state, &["ec2", "describe-vpcs", "--vpc-ids", &state.vpc_id])?;
        if !vpcs.ok {
            if vpcs.err.contains("InvalidVpcID.NotFound") {
                record("준비된 VPC", false, "준비된 VPC를 지우지 마세요. 「초기화」로 처음 상태를 받으세요.", "준비된 VPC가 없어졌어요.".into());
                return Ok(TestReport { passed: false, cases });
            }
            return Err("실습용 클라우드 API가 VPC 조회를 거절했어요. 초기화하세요.".into());
        }
        let vpc = &vpcs.json["Vpcs"][0];
        record("준비된 VPC의 범위", vpc["VpcId"] == state.vpc_id.as_str() && vpc["CidrBlock"] == exercise.vpc_cidr.as_str(),
            &format!("준비된 VPC는 {} 그대로예요.", exercise.vpc_cidr), format!("{} {}", vpc["VpcId"], vpc["CidrBlock"]));
        let all = api_ok(root, &state, &["ec2", "describe-subnets"])?;
        // Partition by the VpcId each subnet reports instead of trusting a server-side filter.
        let subnets: Vec<&Value> = all["Subnets"].as_array().map(|a| a.iter().collect()).unwrap_or_default();
        let mine: Vec<&Value> = subnets.iter().copied().filter(|s| s["VpcId"] == state.vpc_id.as_str()).collect();
        let prepared_ids: Vec<&str> = state.subnets.values().map(|(id, _)| id.as_str()).collect();
        let kept = state.subnets.values().all(|(id, block)| mine.iter().any(|s| s["SubnetId"] == id.as_str() && s["CidrBlock"] == block.as_str()));
        if !state.subnets.is_empty() {
            record("준비된 서브넷", kept, "준비된 서브넷을 지우거나 바꾸지 않아요.",
                if kept { "준비된 서브넷이 그대로 있어요.".into() } else { "준비된 서브넷이 없어지거나 바뀌었어요.".into() });
        }
        let added: Vec<&Value> = mine.iter().copied().filter(|s| !prepared_ids.contains(&s["SubnetId"].as_str().unwrap_or_default())).collect();
        let list = |items: &[&Value]| items.iter().map(|s| s["CidrBlock"].as_str().unwrap_or("?").to_string()).collect::<Vec<_>>().join(", ");
        let vpc_block = cidr(&exercise.vpc_cidr).unwrap();
        let mut target_subnet: Option<String> = None;
        match exercise.goal {
            CloudGoal::CreateSubnet | CloudGoal::DeployServer => {
                let target = exercise.target_cidr.as_deref().unwrap();
                let hits: Vec<&Value> = added.iter().copied().filter(|s| s["CidrBlock"] == target && s["State"] == "available").collect();
                let elsewhere = subnets.iter().any(|s| s["VpcId"] != state.vpc_id.as_str() && s["CidrBlock"] == target);
                record("목표 서브넷", hits.len() == 1, &format!("준비된 VPC 안에 {target} 서브넷이 하나 있어요."),
                    if hits.len() == 1 { format!("{target} 서브넷이 있어요.") }
                    else if elsewhere { "준비된 VPC가 아닌 곳에 만들었어요. 같은 숫자라도 다른 자리예요.".into() }
                    else if added.is_empty() { "준비된 VPC에 새 서브넷이 없어요.".into() }
                    else { format!("{target}가 아닌 서브넷이 있어요: {}", list(&added)) });
                let extra: Vec<&Value> = added.iter().copied().filter(|s| !hits.iter().any(|h| h["SubnetId"] == s["SubnetId"])).collect();
                record("필요 없는 서브넷", extra.is_empty(), "목표 서브넷 하나만 더 만들어요.",
                    if extra.is_empty() { "목표가 아닌 새 서브넷이 없어요.".into() } else { format!("목표가 아닌 새 서브넷이 있어요: {}", list(&extra)) });
                target_subnet = hits.first().and_then(|s| s["SubnetId"].as_str()).map(String::from);
            }
            CloudGoal::ChooseSubnet => {
                let prefix = exercise.new_prefix.unwrap();
                let fit = added.len() == 1
                    && added[0]["State"] == "available"
                    && added[0]["CidrBlock"].as_str().and_then(cidr).is_some_and(|b| b.1 == prefix && contains(vpc_block, b));
                record("새 서브넷", fit, &format!("준비된 서브넷과 겹치지 않는 /{prefix} 서브넷을 하나 만들어요."),
                    if added.is_empty() { "준비된 VPC에 새 서브넷이 없어요.".into() }
                    else if added.len() > 1 { format!("새 서브넷이 {}개예요: {}", added.len(), list(&added)) }
                    else if fit { format!("{} 서브넷이 있어요.", list(&added)) }
                    else { format!("/{prefix} 크기가 아니에요: {}", list(&added)) });
            }
            CloudGoal::LaunchServer | CloudGoal::RequestServer => {
                record("필요 없는 서브넷", added.is_empty(), "이 문제에서는 서브넷을 더 만들지 않아요.",
                    if added.is_empty() { "추가 서브넷이 없어요.".into() } else { format!("새 서브넷이 있어요: {}", list(&added)) });
                if exercise.goal == CloudGoal::LaunchServer {
                    target_subnet = exercise.target_subnet.as_ref().map(|n| state.subnets[n].0.clone());
                }
            }
        }
        if !state.guest {
            return Ok(TestReport { passed: cases.iter().all(|c| c.passed), cases });
        }
        // Server goals: the learner's instances are the owned VPC's non-prepared, non-terminated ones.
        let prepared: Vec<&str> = [&state.client, &state.server].into_iter().flatten().map(|i| i.id.as_str()).collect();
        let learner = |root: &Path| -> Result<Vec<Value>, String> {
            let d = api_ok(root, &state, &["ec2", "describe-instances"])?;
            Ok(d["Reservations"].as_array().into_iter().flatten()
                .flat_map(|r| r["Instances"].as_array().cloned().unwrap_or_default())
                .filter(|i| i["VpcId"] == state.vpc_id.as_str()
                    && !["terminated", "shutting-down"].contains(&i["State"]["Name"].as_str().unwrap_or_default())
                    && !prepared.contains(&i["InstanceId"].as_str().unwrap_or_default()))
                .collect())
        };
        // A just-launched instance is given a fixed time to reach `running`; sleep length is not the answer.
        let mut instances = learner(root)?;
        if instances.iter().any(|i| i["State"]["Name"] == "pending") {
            instances = wait(90, || { let now = learner(root)?; Ok((!now.iter().any(|i| i["State"]["Name"] == "pending")).then_some(now)) })?
                .unwrap_or(instances);
        }
        let (_, container, _) = names(root);
        let server = match exercise.goal {
            CloudGoal::RequestServer => {
                record("새 서버", instances.is_empty(), "이 문제에서는 서버를 더 만들지 않아요.",
                    format!("새로 만든 서버 {}대", instances.len()));
                state.server.as_ref().map(|s| (s.id.clone(), s.ip.clone()))
            }
            _ => {
                let target_block = match exercise.goal {
                    CloudGoal::LaunchServer => exercise.target_subnet.as_ref().and_then(|n| cidr(&state.subnets[n].1)),
                    _ => exercise.target_cidr.as_deref().and_then(cidr),
                };
                let placed = |i: &Value| target_subnet.as_deref().is_some_and(|t| i["SubnetId"] == t)
                    && i["ImageId"] == SERVER_AMI && i["State"]["Name"] == "running"
                    && target_block.zip(i["PrivateIpAddress"].as_str().and_then(|a| a.parse().ok())).is_some_and(|(b, ip)| holds(b, ip));
                let describe = instances.iter().map(|i| format!("{} {} {}", i["SubnetId"].as_str().unwrap_or("?"),
                    i["PrivateIpAddress"].as_str().unwrap_or("?"), i["State"]["Name"].as_str().unwrap_or("?"))).collect::<Vec<_>>().join(", ");
                let good = instances.len() == 1 && placed(&instances[0]);
                record("서버 배치", good, "준비된 서버 이미지로 목표 서브넷에 서버 한 대를 실행해요.",
                    if instances.is_empty() { "실행 중인 새 서버가 없어요.".into() }
                    else if instances.iter().any(|i| i["State"]["Name"] == "pending") { "서버가 아직 시작 중이에요. 잠시 뒤 다시 제출하세요.".into() }
                    else if good { format!("목표 서브넷에서 실행 중이에요: {describe}") }
                    else if instances.len() > 1 { format!("서버가 {}대예요. 목표 서브넷의 한 대만 남기세요: {describe}", instances.len()) }
                    else { format!("목표 서브넷이 아닌 곳에 있어요: {describe}") });
                good.then(|| (instances[0]["InstanceId"].as_str().unwrap_or_default().to_string(),
                    instances[0]["PrivateIpAddress"].as_str().unwrap_or_default().to_string()))
            }
        };
        if let (Some(file), Some((server_id, server_ip))) = (exercise.address_file.as_deref(), server) {
            let block = target_subnet.as_ref().and_then(|_| exercise.target_cidr.as_deref()).and_then(cidr);
            let written = read_address(&self.work().join(file));
            let same = written.is_some_and(|w| w.to_string() == server_ip);
            record("요청 주소", same, "API가 알려 준 서버의 사설 주소를 주소 파일에 적어요.",
                match written { None => format!("{file}에서 IPv4 주소를 읽지 못했어요."), Some(_) if same => format!("{file}의 주소가 서버의 사설 주소와 같아요."),
                    Some(w) => format!("{file}의 주소 {w}는 API가 알려 준 서버의 사설 주소가 아니에요.") });
            if same {
                let client = state.client.as_ref().ok_or("준비된 클라이언트가 없어요. 초기화하세요.")?;
                // The grader's own request from the owned client, not the learner's terminal output.
                let answer = wait(90, || Ok(probe(&container, client, &server_ip)?.filter(|p| p.ok)))?;
                let guest = guest_container(&container, &server_id)?;
                let identity = answer.as_ref().is_some_and(|p| {
                    p.field("instance") == Some(server_id.as_str()) && p.field("served-on") == Some(server_ip.as_str())
                        && p.field("from") == Some(client.ip.as_str()) && p.field("java.version").is_some_and(|v| v.starts_with("25"))
                }) && block.is_none_or(|b| server_ip.parse().is_ok_and(|ip| holds(b, ip)))
                    && guest.as_ref().is_some_and(|g| g["Image"].as_str() == state.guest_image.as_deref());
                record("다른 서브넷에서 받은 응답", identity, "준비된 클라이언트가 그 주소로 보낸 요청에 이 서버의 자바 프로그램이 응답해요.",
                    match &answer { None => "서버가 HTTP에 응답하지 않았어요. 서버가 다 켜졌는지 확인하세요.".into(),
                        Some(p) => p.body.lines().filter(|l| !l.starts_with("request=")).collect::<Vec<_>>().join("\n") });
            }
        }
        Ok(TestReport { passed: cases.iter().all(|c| c.passed), cases })
    }
}

/// Map the built image's Docker architecture to the EC2 AMI architecture name.
fn ami_architecture(docker: &str) -> Option<&'static str> {
    match docker {
        "amd64" => Some("x86_64"),
        "arm64" => Some("arm64"),
        _ => None,
    }
}

/// The learner's address file: a regular file (not a link) of at most 256 bytes holding one IPv4.
/// The read itself is bounded, and the contents are never echoed back.
fn read_address(path: &Path) -> Option<Ipv4Addr> {
    let metadata = std::fs::symlink_metadata(path).ok()?;
    if !metadata.is_file() || metadata.file_type().is_symlink() || metadata.len() > 256 {
        return None;
    }
    let mut bytes = Vec::with_capacity(257);
    std::fs::File::open(path).ok()?.take(257).read_to_end(&mut bytes).ok()?;
    if bytes.len() > 256 {
        return None;
    }
    std::str::from_utf8(&bytes).ok()?.trim().parse().ok()
}

fn pulled_reference(container: &str, image: &str) -> Result<String, String> {
    let digests = inner_ok(container, &["image", "inspect", "--format", "{{json .RepoDigests}}", image], 30)?;
    if digests.contains(image) { Ok(image.into()) } else { Err("준비 이미지의 출처를 확인하지 못했어요.".into()) }
}

/// After an archive load the digest reference may not survive. Accept the loaded image only when
/// its measured content (layers, platform, runtime config) equals the host's pinned image, and
/// then refer to it by that verified image ID instead of naming it with a trusted tag.
fn transferred_reference(container: &str, image: &str, load_output: &str) -> Result<String, String> {
    if pulled_reference(container, image).is_ok() {
        return Ok(image.into());
    }
    let unverified = || "캐시에서 옮긴 준비 이미지의 내용을 확인하지 못했어요.".to_string();
    let loaded = load_output.lines().find_map(|l| l.trim().strip_prefix("Loaded image ID: ").or_else(|| l.trim().strip_prefix("Loaded image: ")))
        .ok_or_else(unverified)?.trim().to_string();
    let measure = |raw: &str| -> Option<Value> {
        let v: Value = serde_json::from_str::<Value>(raw).ok()?.as_array()?.first()?.clone();
        Some(serde_json::json!({
            "layers": v["RootFS"]["Layers"], "architecture": v["Architecture"], "os": v["Os"],
            "env": v["Config"]["Env"], "cmd": v["Config"]["Cmd"], "entrypoint": v["Config"]["Entrypoint"],
            "workdir": v["Config"]["WorkingDir"], "user": v["Config"]["User"],
        }))
    };
    let host = measure(&require(&["image", "inspect", "--platform", image_platform(image), image], 30)?).ok_or_else(unverified)?;
    let raw = inner_ok(container, &["image", "inspect", &loaded], 30)?;
    let inner_image = measure(&raw).ok_or_else(unverified)?;
    if host["layers"].as_array().is_none_or(|l| l.is_empty()) || host != inner_image {
        return Err(unverified());
    }
    let parsed: Value = serde_json::from_str(&raw).map_err(|_| unverified())?;
    let id = parsed[0]["Id"].as_str().ok_or_else(unverified)?;
    // Named only after the content check, so Dockerfile FROM and `docker run` can use it.
    let name = image.split('@').next().unwrap_or_default().rsplit('/').next().unwrap_or("image");
    let hex = id.trim_start_matches("sha256:");
    let tag = format!("mq-cloud-verified/{name}:{}", &hex[..hex.len().min(16)]);
    inner_ok(container, &["tag", id, &tag], 30)?;
    Ok(tag)
}

/// The platform the nested engine uses for a pinned image: the guest base is always x86_64, and
/// everything else (Floci) is the host's native platform.
fn image_platform(image: &str) -> &'static str {
    if image == TEMURIN { GUEST_PLATFORM } else if cfg!(target_arch = "aarch64") { "linux/arm64" } else { "linux/amd64" }
}

/// Copy the host's cached pinned image into the nested engine (registry unavailable inside it).
/// Both ends are bounded; on any failure both owned processes are killed and reaped.
fn transfer_image(container: &str, image: &str) -> Result<String, String> {
    transfer_image_within(container, image, Duration::from_secs(600))
}
fn transfer_image_within(container: &str, image: &str, limit: Duration) -> Result<String, String> {
    let failed = || "준비 이미지를 실습 엔진에 넣지 못했어요. 인터넷 연결이나 Docker 이미지 캐시를 확인하세요.".to_string();
    let cli = docker_cli()?;
    let platform = image_platform(image);
    let mut output = tempfile::tempfile().map_err(|e| e.to_string())?;
    let mut save = Command::new(&cli);
    save.env("PATH", crate::docker_lab::search_path(&cli)).args(["save", "--platform", platform, image])
        .stdin(std::process::Stdio::null()).stdout(std::process::Stdio::piped()).stderr(std::process::Stdio::null());
    #[cfg(windows)]
    save.creation_flags(0x08000000);
    let mut saver = save.spawn().map_err(|_| failed())?;
    let mut load = Command::new(&cli);
    load.env("PATH", crate::docker_lab::search_path(&cli)).args(["exec", "-i", container, "docker", "load"])
        .stdin(saver.stdout.take().ok_or_else(failed)?)
        .stdout(output.try_clone().map_err(|e| e.to_string())?).stderr(std::process::Stdio::null());
    #[cfg(windows)]
    load.creation_flags(0x08000000);
    let mut loader = match load.spawn() {
        Ok(child) => child,
        Err(_) => {
            let _ = saver.kill();
            let _ = saver.wait();
            return Err(failed());
        }
    };
    let start = Instant::now();
    let (mut saved, mut loaded) = (None, None);
    let outcome = loop {
        if saved.is_none() { saved = saver.try_wait().map_err(|e| e.to_string())?; }
        if loaded.is_none() { loaded = loader.try_wait().map_err(|e| e.to_string())?; }
        match (saved, loaded) {
            (Some(s), Some(l)) => break s.success() && l.success(),
            // A failed sink must not leave the producer blocked on a full pipe, and vice versa.
            (Some(s), None) if !s.success() => break false,
            (None, Some(l)) if !l.success() => break false,
            _ => {}
        }
        if start.elapsed() > limit {
            break false;
        }
        std::thread::sleep(Duration::from_millis(100));
    };
    for child in [&mut saver, &mut loader] {
        if child.try_wait().ok().flatten().is_none() {
            let _ = child.kill();
        }
        let _ = child.wait();
    }
    if !outcome {
        return Err(failed());
    }
    let mut text = String::new();
    output.seek(SeekFrom::Start(0)).map_err(|e| e.to_string())?;
    output.take(64_000).read_to_string(&mut text).map_err(|e| e.to_string())?;
    Ok(text)
}

fn guest_container(container: &str, instance: &str) -> Result<Option<Value>, String> {
    let ids = inner_ok(container, &["ps", "-aq", "--no-trunc"], 20)?;
    let ids: Vec<&str> = ids.split_whitespace().collect();
    if ids.is_empty() {
        return Ok(None);
    }
    let mut args = vec!["inspect"];
    args.extend(ids);
    let all: Value = serde_json::from_str(&inner_ok(container, &args, 30)?).map_err(|e| e.to_string())?;
    let needle = format!("AWS_EC2_INSTANCE_ID={instance}");
    Ok(all.as_array().into_iter().flatten()
        .find(|c| c["Config"]["Env"].as_array().is_some_and(|env| env.iter().any(|e| e == needle.as_str())))
        .cloned())
}

struct Probe {
    ok: bool,
    body: String,
}
impl Probe {
    fn field(&self, key: &str) -> Option<&str> {
        self.body.lines().find_map(|l| l.strip_prefix(key).and_then(|r| r.strip_prefix('=')))
    }
}
fn probe(container: &str, client: &Instance, address: &str) -> Result<Option<Probe>, String> {
    address.parse::<Ipv4Addr>().map_err(|_| "요청 주소가 IPv4가 아니에요.".to_string())?;
    let r = inner(container, &["exec", &client.container, "java", "/opt/mq/HttpCheck.java", address, HTTP_PORT], 60)?;
    Ok(Some(Probe { ok: r.ok && r.out.contains("HTTP/1.1 200 "), body: r.out.replace("\r\n", "\n") }))
}

#[cfg(test)]
#[path = "cloud_practice_tests.rs"]
mod tests;

#[cfg(test)]
mod config_file_regressions {
    use super::*;

    #[test]
    fn empty_config_preserves_existing_nonempty_file() {
        let root = tempfile::tempdir().unwrap();
        let path = empty_config(root.path()).unwrap();
        assert_eq!(std::fs::metadata(&path).unwrap().len(), 0);
        std::fs::write(&path, "keep this existing data").unwrap();
        assert!(empty_config(root.path()).is_err());
        assert_eq!(std::fs::read_to_string(path).unwrap(), "keep this existing data");
    }

    #[test]
    fn empty_config_refuses_a_directory() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join("cloud-aws-empty-config");
        std::fs::create_dir(&path).unwrap();
        assert!(empty_config(root.path()).is_err());
        assert!(path.is_dir());
    }

    #[cfg(unix)]
    #[test]
    fn empty_config_refuses_a_link_without_touching_its_target() {
        let root = tempfile::tempdir().unwrap();
        let target = root.path().join("preserved-config");
        std::fs::write(&target, "keep this existing data").unwrap();
        std::os::unix::fs::symlink(&target, root.path().join("cloud-aws-empty-config")).unwrap();
        assert!(empty_config(root.path()).is_err());
        assert_eq!(std::fs::read_to_string(target).unwrap(), "keep this existing data");
    }
}
