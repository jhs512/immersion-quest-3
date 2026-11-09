//! Owned Docker lab lifecycle and semantic grading. Host routes/DNS are untouched.
use super::*;
use serde_json::Value;
use std::io::{Read, Seek, SeekFrom};
use std::time::{Duration, Instant};

const IMAGE: &str = "immersion-network-player:1";
const DNS_IMAGE: &str = "coredns/coredns:1.12.0";
const LABEL: &str = "gg.molip.network-practice";

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct NetworkExercise {
    pub kind: String,
}
impl NetworkExercise {
    pub fn validate(&self) -> Result<(), String> {
        if ![
            "loopback",
            "alias",
            "allocation",
            "mask",
            "routing",
            "nat",
            "dns",
            "cache",
        ]
        .contains(&self.kind.as_str())
        {
            return Err("네트워크 실습 종류를 확인하세요.".into());
        }
        Ok(())
    }
}

#[derive(Serialize, Deserialize)]
struct State {
    kind: String,
    base: String,
    roles: BTreeMap<String, String>,
    ready: bool,
    #[serde(default)]
    cache_started_at: Option<String>,
}
struct Run {
    ok: bool,
    out: String,
    err: String,
}
fn network_cli() -> Result<PathBuf, String> {
    crate::docker_lab::cli().ok_or_else(|| "Docker를 찾을 수 없어요. Docker Desktop을 설치하고 Linux 엔진을 실행하세요.".into())
}
fn docker(args: &[String], seconds: u64) -> Result<Run, String> {
    // File-backed output prevents a full build pipe from blocking the timeout.
    let mut stdout = tempfile::tempfile().map_err(|e| e.to_string())?;
    let mut stderr = tempfile::tempfile().map_err(|e| e.to_string())?;
    let cli = network_cli()?;
    let mut command = Command::new(&cli);
    command.env("PATH", crate::docker_lab::search_path(&cli));
    command
        .args(args)
        .stdout(stdout.try_clone().map_err(|e| e.to_string())?)
        .stderr(stderr.try_clone().map_err(|e| e.to_string())?);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let mut child = command.spawn().map_err(|_| {
        "Docker를 찾을 수 없어요. Docker Desktop을 설치하고 Linux 엔진을 실행하세요.".to_string()
    })?;
    let start = Instant::now();
    let status = loop {
        if let Some(status) = child.try_wait().map_err(|e| e.to_string())? {
            break status;
        }
        if start.elapsed() > Duration::from_secs(seconds) {
            let _ = child.kill();
            let _ = child.wait();
            return Err(
                "Docker 응답을 기다리다 중단했어요. 엔진 상태를 확인한 뒤 다시 시도하세요.".into(),
            );
        }
        std::thread::sleep(Duration::from_millis(50));
    };
    let mut out = String::new();
    let mut err = String::new();
    stdout.seek(SeekFrom::Start(0)).map_err(|e| e.to_string())?;
    stderr.seek(SeekFrom::Start(0)).map_err(|e| e.to_string())?;
    stdout
        .take(150_000)
        .read_to_string(&mut out)
        .map_err(|e| e.to_string())?;
    stderr
        .take(150_000)
        .read_to_string(&mut err)
        .map_err(|e| e.to_string())?;
    Ok(Run {
        ok: status.success(),
        out,
        err,
    })
}
fn args(values: &[&str]) -> Vec<String> {
    values.iter().map(|s| (*s).into()).collect()
}
fn require(command: &[String], seconds: u64) -> Result<String, String> {
    let result = docker(command, seconds)?;
    if result.ok {
        Ok(result.out)
    } else {
        Err(format!("네트워크 실습 환경을 준비하지 못했어요. Docker Desktop Linux 엔진과 실습 자원을 확인하세요.\n{}", result.err.chars().take(1400).collect::<String>()))
    }
}
fn tag(root: &Path) -> String {
    use sha2::{Digest, Sha256};
    format!(
        "iq-player-{}",
        &format!("{:x}", Sha256::digest(root.to_string_lossy().as_bytes()))[..16]
    )
}
fn load(root: &Path) -> Result<State, String> {
    let state: State = serde_json::from_slice(
        &std::fs::read(root.join("network-state.json")).map_err(|e| e.to_string())?,
    )
    .map_err(|e| e.to_string())?;
    NetworkExercise {
        kind: state.kind.clone(),
    }
    .validate()?;
    let octets = state
        .base
        .parse::<std::net::Ipv4Addr>()
        .map_err(|_| "실습 주소 장부를 확인하세요.")?
        .octets();
    if octets[0] != 172
        || !(16..=31).contains(&octets[1])
        || octets[2] % 4 != 0
        || octets[2] > 252
        || octets[3] != 0
    {
        return Err("실습 주소 대역을 확인하세요. 초기화해서 새 환경을 만드세요.".into());
    }
    for (role, name) in &state.roles {
        if ![
            "SERVER", "SERVER_B", "CLIENT", "CLIENT_B", "ROUTER", "DNS", "CACHE",
        ]
        .contains(&role.as_str())
            || name
                != &format!(
                    "{}-{}",
                    tag(root),
                    role.to_ascii_lowercase().replace('_', "-")
                )
        {
            return Err("실습 자원의 소유 장부를 확인하세요.".into());
        }
    }
    Ok(state)
}
fn save(root: &Path, state: &State) -> Result<(), String> {
    std::fs::write(
        root.join("network-state.json"),
        serde_json::to_vec(state).unwrap(),
    )
    .map_err(|e| e.to_string())
}
fn ip(state: &State, network: u8, host: u8) -> String {
    let mut parts: Vec<_> = state
        .base
        .split('.')
        .map(|s| s.parse::<u8>().unwrap())
        .collect();
    parts[2] += network;
    parts[3] = host;
    parts
        .iter()
        .map(u8::to_string)
        .collect::<Vec<_>>()
        .join(".")
}
fn cidr(state: &State, network: u8) -> String {
    format!("{}/24", ip(state, network, 0))
}
fn prefix(value: &str) -> Option<(u32, u32)> {
    let (address, bits) = value.split_once('/')?;
    let address = u32::from(address.parse::<std::net::Ipv4Addr>().ok()?);
    let bits: u32 = bits.parse().ok()?;
    if bits > 32 {
        return None;
    }
    let mask = if bits == 0 {
        0
    } else {
        u32::MAX << (32 - bits)
    };
    Some((address & mask, mask))
}
fn unused_base() -> Result<String, String> {
    let ids = require(&args(&["network", "ls", "-q"]), 20)?;
    let mut occupied = vec![];
    if !ids.trim().is_empty() {
        let mut command = args(&["network", "inspect"]);
        command.extend(ids.split_whitespace().map(str::to_owned));
        let networks: Value =
            serde_json::from_str(&require(&command, 20)?).map_err(|e| e.to_string())?;
        for n in networks
            .as_array()
            .ok_or("Docker 네트워크 목록을 확인하세요.")?
        {
            for c in n["IPAM"]["Config"].as_array().into_iter().flatten() {
                if let Some(p) = c["Subnet"].as_str().and_then(prefix) {
                    occupied.push(p);
                }
            }
        }
    }
    for second in (18..=29).rev() {
        for third in (196..=240).rev().filter(|n| n % 4 == 0) {
            let base = format!("172.{second}.{third}.0");
            let (address, mask) = prefix(&format!("{base}/22")).unwrap();
            if !occupied
                .iter()
                .any(|(other, other_mask)| address & mask & other_mask == other & mask & other_mask)
            {
                return Ok(base);
            }
        }
    }
    Err("실습용 사설 주소 대역을 확보하지 못했어요. 기존 Docker 네트워크와 겹치지 않는 공간이 필요해요.".into())
}
fn ex(state: &State, role: &str, command: &[&str]) -> Result<Run, String> {
    let name = state
        .roles
        .get(role)
        .ok_or("실습 컨테이너 역할을 확인하세요.")?;
    let mut command_line = args(&["exec", name]);
    command_line.extend(command.iter().map(|s| (*s).into()));
    docker(&command_line, 15)
}
fn ex_ok(state: &State, role: &str, command: &[&str]) -> Result<String, String> {
    let p = ex(state, role, command)?;
    if p.ok {
        Ok(p.out)
    } else {
        Err(format!("실습 준비 명령이 실패했어요: {}", p.err))
    }
}
fn http(state: &State, role: &str, address: &str) -> Result<Option<Value>, String> {
    let result = ex(
        state,
        role,
        &[
            "curl",
            "--noproxy",
            "*",
            "-fsS",
            "--connect-timeout",
            "2",
            "--max-time",
            "3",
            &format!("http://{address}:8080/"),
        ],
    )?;
    Ok(if result.ok {
        serde_json::from_str(&result.out).ok()
    } else {
        None
    })
}
fn route(state: &State, role: &str, target: &str) -> Result<Option<Value>, String> {
    let result = ex(state, role, &["ip", "-j", "route", "get", target])?;
    Ok(if result.ok {
        serde_json::from_str::<Value>(&result.out)
            .ok()
            .and_then(|v| v.as_array()?.first().cloned())
    } else {
        None
    })
}
fn default_gateway(state: &State) -> Result<bool, String> {
    let table: Value = serde_json::from_str(&ex_ok(
        state,
        "CLIENT",
        &["ip", "-j", "route", "show", "default"],
    )?)
    .map_err(|e| e.to_string())?;
    Ok(table
        .as_array()
        .into_iter()
        .flatten()
        .any(|r| r["dst"] == "default" && r["gateway"] == ip(state, 0, 1)))
}
fn ready(state: &State, role: &str) -> Result<(), String> {
    for _ in 0..40 {
        if http(state, role, "127.0.0.1")?.is_some() {
            return Ok(());
        }
        std::thread::sleep(Duration::from_millis(100));
    }
    Err("실습 서버가 준비되지 않았어요. Docker 상태를 확인한 뒤 초기화하세요.".into())
}

pub(super) fn cleanup_at(root: &Path) -> Result<(), String> {
    if !root.join("network-state.json").exists() {
        return Ok(());
    }
    // Discover by the immutable owner label, never by learner-controlled names.
    let filter = format!("label={LABEL}={}", tag(root));
    let containers = require(&args(&["ps", "-aq", "--filter", &filter]), 20)?;
    for id in containers.split_whitespace() {
        require(&args(&["rm", "-f", id]), 20)?;
    }
    let networks = require(&args(&["network", "ls", "-q", "--filter", &filter]), 20)?;
    for id in networks.split_whitespace() {
        require(&args(&["network", "rm", id]), 20)?;
    }
    std::fs::remove_file(root.join("network-state.json")).map_err(|e| e.to_string())
}

impl GitPractice {
    pub fn cleanup_network(&self) -> Result<(), String> {
        cleanup_at(self.root())
    }
    pub fn release_network_demo(&self) {
        if self.exercise.network_demonstration {
            let _ = self.cleanup_network();
        }
    }
    pub fn prepare_network(&self) -> Result<Vec<(String, String)>, String> {
        let Some(exercise) = &self.exercise.network else {
            return Ok(vec![]);
        };
        exercise.validate()?;
        require(&args(&["info", "--format", "{{.OSType}}"]), 20).and_then(|s| {
            if s.trim() == "linux" {
                Ok(())
            } else {
                Err("Docker Desktop을 Linux 컨테이너 모드로 실행하세요.".into())
            }
        })?;
        let root = self.root();
        if root.join("network-state.json").exists() {
            let state = load(root)?;
            if !state.ready || state.kind != exercise.kind {
                return Err("실습 준비가 중단됐어요. 초기화해서 새 환경을 만드세요.".into());
            }
            for name in state.roles.values() {
                let p = docker(
                    &args(&[
                        "inspect",
                        "--format",
                        &format!("{{{{index .Config.Labels \"{LABEL}\"}}}}"),
                        name,
                    ]),
                    15,
                )?;
                if !p.ok || p.out.trim() != tag(root) {
                    return Err("실습 컨테이너가 없어졌거나 소유 정보가 달라요. 초기화해서 새 환경을 만드세요.".into());
                }
            }
            return network_env(&state);
        }
        let mut state = State {
            kind: exercise.kind.clone(),
            base: unused_base()?,
            roles: BTreeMap::new(),
            ready: false,
            cache_started_at: None,
        };
        save(root, &state)?;
        let result = self.create_network_lab(&mut state);
        if let Err(error) = result {
            let cleanup = cleanup_at(root);
            return Err(format!(
                "{error}{}",
                cleanup
                    .err()
                    .map(|e| format!("\n실습 정리도 실패했어요: {e}"))
                    .unwrap_or_default()
            ));
        }
        state.ready = true;
        save(root, &state)?;
        network_env(&state)
    }
    fn create_network_lab(&self, state: &mut State) -> Result<(), String> {
        let root = self.root();
        let owner = tag(root);
        let label = format!("{LABEL}={owner}");
        let build = root.join("network-build");
        std::fs::create_dir_all(&build).map_err(|e| e.to_string())?;
        std::fs::write(
            build.join("Dockerfile"),
            include_str!("../assets/network-lab/Dockerfile"),
        )
        .map_err(|e| e.to_string())?;
        std::fs::write(
            build.join("server.py"),
            include_str!("../assets/network-lab/server.py"),
        )
        .map_err(|e| e.to_string())?;
        if !docker(&args(&["image", "inspect", IMAGE]), 20)?.ok {
            require(
                &args(&[
                    "build",
                    "-t",
                    IMAGE,
                    build.to_str().ok_or("실습 경로를 확인하세요.")?,
                ]),
                300,
            )?;
        }
        let allocation = state.kind == "allocation";
        let subnet = if allocation {
            format!("{}/29", ip(state, 0, 8))
        } else {
            cidr(state, 0)
        };
        let gateway = ip(state, 0, if allocation { 9 } else { 1 });
        let main = format!("{owner}-main");
        require(
            &args(&[
                "network",
                "create",
                "--label",
                &label,
                "--subnet",
                &subnet,
                "--gateway",
                &gateway,
                &main,
            ]),
            30,
        )?;
        let bind = if state.kind == "loopback" {
            "127.0.0.1\n"
        } else {
            "0.0.0.0\n"
        };
        std::fs::write(self.work().join("bind.txt"), bind).map_err(|e| e.to_string())?;
        let config = canonical_directory(&self.work())?
            .to_string_lossy()
            .into_owned();
        let mount = format!("type=bind,source={config},target=/config,readonly");
        let spawn = |state: &mut State,
                     role: &str,
                     net: &str,
                     address: &str,
                     admin: bool,
                     command: Vec<String>,
                     dns: Option<&str>,
                     forward: bool|
         -> Result<(), String> {
            let name = format!("{owner}-{}", role.to_ascii_lowercase().replace('_', "-"));
            let mut a = args(&[
                "create",
                "--name",
                &name,
                "--label",
                &label,
                "--network",
                net,
                "--ip",
                address,
            ]);
            if admin {
                a.extend(args(&["--cap-add", "NET_ADMIN"]));
            }
            if forward {
                a.extend(args(&["--sysctl", "net.ipv4.ip_forward=1"]));
            }
            if let Some(dns) = dns {
                a.extend(args(&["--dns", dns]));
            }
            a.extend(args(&[
                "--env",
                &format!("LAB_ROLE={role}"),
                "--mount",
                &mount,
            ]));
            a.extend(command);
            require(&a, 30)?;
            state.roles.insert(role.into(), name.clone());
            save(root, state)?;
            require(&args(&["start", &name]), 30)?;
            Ok(())
        };
        let sleeper = || args(&[IMAGE, "sleep", "infinity"]);
        let web = || args(&[IMAGE, "python3", "/lab/server.py"]);
        if allocation {
            spawn(
                state,
                "SERVER",
                &main,
                &ip(state, 0, 10),
                true,
                web(),
                None,
                false,
            )?;
            ready(state, "SERVER")?;
        } else if state.kind == "routing" || state.kind == "nat" {
            let outside = format!("{owner}-outside");
            require(
                &args(&[
                    "network",
                    "create",
                    "--label",
                    &label,
                    "--subnet",
                    &cidr(state, 1),
                    &outside,
                ]),
                30,
            )?;
            spawn(
                state,
                "ROUTER",
                &main,
                &ip(state, 0, 254),
                true,
                sleeper(),
                None,
                true,
            )?;
            require(
                &args(&[
                    "network",
                    "connect",
                    "--ip",
                    &ip(state, 1, 254),
                    &outside,
                    &state.roles["ROUTER"],
                ]),
                30,
            )?;
            spawn(
                state,
                "SERVER",
                &outside,
                &ip(state, 1, 130),
                true,
                web(),
                None,
                false,
            )?;
            ready(state, "SERVER")?;
            if state.kind == "routing" {
                ex_ok(
                    state,
                    "SERVER",
                    &[
                        "ip",
                        "route",
                        "replace",
                        "default",
                        "via",
                        &ip(state, 1, 254),
                    ],
                )?;
                spawn(
                    state,
                    "CLIENT",
                    &main,
                    &ip(state, 0, 10),
                    true,
                    sleeper(),
                    None,
                    false,
                )?;
            } else {
                ex_ok(state, "SERVER", &["ip", "route", "del", "default"])?;
                for (role, host) in [("CLIENT", 10), ("CLIENT_B", 11)] {
                    spawn(
                        state,
                        role,
                        &main,
                        &ip(state, 0, host),
                        true,
                        sleeper(),
                        None,
                        false,
                    )?;
                    ex_ok(
                        state,
                        role,
                        &[
                            "ip",
                            "route",
                            "replace",
                            "default",
                            "via",
                            &ip(state, 0, 254),
                        ],
                    )?;
                }
            }
        } else {
            spawn(
                state,
                "SERVER",
                &main,
                &ip(state, 0, 130),
                state.kind == "alias",
                web(),
                None,
                false,
            )?;
            ready(state, "SERVER")?;
            let is_dns = state.kind == "dns" || state.kind == "cache";
            if is_dns {
                spawn(
                    state,
                    "SERVER_B",
                    &main,
                    &ip(state, 0, 140),
                    false,
                    web(),
                    None,
                    false,
                )?;
                ready(state, "SERVER_B")?;
                if !docker(&args(&["image", "inspect", DNS_IMAGE]), 20)?.ok {
                    require(&args(&["pull", DNS_IMAGE]), 180)?;
                }
                let zone=format!("$ORIGIN memo.test.\n$TTL {}\n@ IN SOA ns.memo.test. hostmaster.memo.test. 1 60 60 60 0\n@ IN NS ns.memo.test.\nns IN A {}\n@ IN A {}\n",if state.kind=="cache" {3600}else{0},ip(state,0,53),ip(state,0,130));
                std::fs::write(self.work().join("memo.zone"), &zone).map_err(|e| e.to_string())?;
                std::fs::write(
                    self.work().join("Corefile"),
                    "memo.test:53 {\n file /config/memo.zone memo.test\n errors\n}\n",
                )
                .map_err(|e| e.to_string())?;
                spawn(
                    state,
                    "DNS",
                    &main,
                    &ip(state, 0, 53),
                    false,
                    args(&[DNS_IMAGE, "-conf", "/config/Corefile"]),
                    None,
                    false,
                )?;
                if state.kind == "cache" {
                    std::fs::write(
                        self.work().join("Cachefile"),
                        format!(
                            "memo.test:53 {{\n forward . {}\n cache 3600\n}}\n",
                            ip(state, 0, 53)
                        ),
                    )
                    .map_err(|e| e.to_string())?;
                    spawn(
                        state,
                        "CACHE",
                        &main,
                        &ip(state, 0, 54),
                        false,
                        args(&[DNS_IMAGE, "-conf", "/config/Cachefile"]),
                        None,
                        false,
                    )?;
                    state.cache_started_at = Some(
                        require(
                            &args(&[
                                "inspect",
                                "--format",
                                "{{.State.StartedAt}}",
                                &state.roles["CACHE"],
                            ]),
                            15,
                        )?
                        .trim()
                        .into(),
                    );
                }
            }
            let resolver = ip(state, 0, if state.kind == "cache" { 54 } else { 53 });
            spawn(
                state,
                "CLIENT",
                &main,
                &ip(state, 0, 10),
                state.kind == "mask",
                sleeper(),
                if is_dns { Some(&resolver) } else { None },
                false,
            )?;
            if state.kind == "mask" {
                let dev = route(state, "CLIENT", &ip(state, 0, 130))?
                    .and_then(|v| v["dev"].as_str().map(str::to_owned))
                    .ok_or("출구 인터페이스를 확인하세요.")?;
                ex_ok(
                    state,
                    "CLIENT",
                    &[
                        "ip",
                        "addr",
                        "del",
                        &format!("{}/24", ip(state, 0, 10)),
                        "dev",
                        &dev,
                    ],
                )?;
                ex_ok(
                    state,
                    "CLIENT",
                    &[
                        "ip",
                        "addr",
                        "add",
                        &format!("{}/25", ip(state, 0, 10)),
                        "dev",
                        &dev,
                    ],
                )?;
                ex_ok(
                    state,
                    "CLIENT",
                    &["ip", "route", "replace", "default", "via", &ip(state, 0, 1)],
                )?;
            }
            if is_dns {
                for _ in 0..30 {
                    if http(state, "CLIENT", "memo.test")?.is_some() {
                        break;
                    }
                    std::thread::sleep(Duration::from_millis(100));
                }
                if http(state, "CLIENT", "memo.test")?.is_none() {
                    return Err("로컬 DNS의 준비 응답을 확인하지 못했어요.".into());
                }
                if state.kind == "cache" {
                    let zone = std::fs::read_to_string(self.work().join("memo.zone"))
                        .map_err(|e| e.to_string())?;
                    std::fs::write(
                        self.work().join("memo.zone"),
                        zone.replace(
                            &format!("@ IN A {}", ip(state, 0, 130)),
                            &format!("@ IN A {}", ip(state, 0, 140)),
                        )
                        .replace(". 1 60", ". 2 60"),
                    )
                    .map_err(|e| e.to_string())?;
                    require(&args(&["restart", &state.roles["DNS"]]), 30)?;
                    // Confirm both sides of the intended starting discrepancy.
                    let cached = ex_ok(
                        state,
                        "CLIENT",
                        &[
                            "dig",
                            &format!("@{}", ip(state, 0, 54)),
                            "memo.test",
                            "A",
                            "+short",
                        ],
                    )?;
                    let direct = ex_ok(
                        state,
                        "CLIENT",
                        &[
                            "dig",
                            &format!("@{}", ip(state, 0, 53)),
                            "memo.test",
                            "A",
                            "+short",
                        ],
                    )?;
                    if !cached.contains(&ip(state, 0, 130)) || !direct.contains(&ip(state, 0, 140))
                    {
                        return Err(
                            "캐시와 권한 DNS의 시작 상태가 맞지 않아요. 초기화하세요.".into()
                        );
                    }
                }
            }
        }
        let env = network_env(state)?;
        let mut ledger = String::from("이번 문제에서만 쓰는 주소 장부예요.\nGATEWAY_IP는 클라이언트의 기본 게이트웨이예요. 클라이언트가 없는 문제에서는 서버의 기본 게이트웨이예요.\n");
        for (key, value) in &env {
            if key != "MSYS_NO_PATHCONV" && key != "PATH" {
                ledger.push_str(&format!("{key}={value}\n"));
            }
        }
        std::fs::write(self.work().join("addresses.txt"), ledger).map_err(|e| e.to_string())?;
        Ok(())
    }
    pub fn check_network(&self) -> Result<crate::runner::TestReport, String> {
        use crate::runner::{TestCaseResult, TestReport};
        let state = load(self.root())?;
        if !state.ready {
            return Err("실습 준비가 끝나지 않았어요. 초기화하세요.".into());
        }
        // Engine/resource failures are setup errors, not learner wrong answers.
        require(&args(&["info", "--format", "{{.OSType}}"]), 20)?;
        for name in state.roles.values() {
            let p = docker(
                &args(&[
                    "inspect",
                    "--format",
                    &format!("{{{{.State.Running}}}} {{{{index .Config.Labels \"{LABEL}\"}}}}"),
                    name,
                ]),
                15,
            )?;
            if !p.ok || p.out.trim() != format!("true {}", tag(self.root())) {
                return Err("실습 컨테이너가 실행 중이 아니거나 소유 정보가 달라요. 중단한 컨테이너를 시작하거나 초기화하세요.".into());
            }
        }
        let mut cases = vec![];
        let mut record = |name: &str, passed: bool, expected: &str, actual: String| {
            cases.push(TestCaseResult {
                input: name.into(),
                expected: expected.into(),
                stdout: actual,
                stderr: String::new(),
                passed,
                state: "network_state".into(),
            })
        };
        let server_ip = ip(
            &state,
            if ["routing", "nat"].contains(&state.kind.as_str()) {
                1
            } else {
                0
            },
            130,
        );
        match state.kind.as_str() {
            "loopback" => {
                let response = http(&state, "CLIENT", &server_ip)?;
                record(
                    "다른 컨테이너의 접속",
                    response.as_ref().is_some_and(|v| v["server"] == "SERVER"),
                    "서버의 네트워크 주소로 실제 서버 응답을 받아요.",
                    format!("{response:?}"),
                );
                record(
                    "클라이언트 루프백의 범위",
                    http(&state, "CLIENT", "127.0.0.1")?.is_none(),
                    "클라이언트 자신의 루프백에는 서버를 새로 만들지 않아요.",
                    "클라이언트 루프백 접속 결과를 따로 검사했어요.".into(),
                );
            }
            "alias" | "allocation" => {
                let interfaces: Value =
                    serde_json::from_str(&ex_ok(&state, "SERVER", &["ip", "-j", "addr"])?)
                        .map_err(|e| e.to_string())?;
                let original = ip(&state, 0, if state.kind == "allocation" { 10 } else { 130 });
                let target = ip(&state, 0, 132);
                let mut found = vec![];
                for interface in interfaces
                    .as_array()
                    .ok_or("인터페이스 목록을 확인하세요.")?
                {
                    let addresses: Vec<_> = interface["addr_info"]
                        .as_array()
                        .into_iter()
                        .flatten()
                        .filter_map(|a| a["local"].as_str())
                        .collect();
                    if addresses.contains(&original.as_str()) {
                        for entry in interface["addr_info"].as_array().into_iter().flatten() {
                            let Some(address) = entry["local"].as_str() else {
                                continue;
                            };
                            let valid = if state.kind == "alias" {
                                address == target
                            } else {
                                (11..=14).any(|h| address == ip(&state, 0, h))
                            };
                            if valid
                                && entry["prefixlen"] == if state.kind == "alias" { 24 } else { 29 }
                            {
                                found.push(address.to_owned());
                            }
                        }
                    }
                }
                record(
                    "같은 인터페이스의 주소",
                    !found.is_empty(),
                    if state.kind == "alias" {
                        "원래 주소를 유지하고 같은 인터페이스에 TARGET_IP를 추가해요."
                    } else {
                        "원래 주소를 유지하고 미사용 호스트 주소 하나를 같은 인터페이스에 추가해요."
                    },
                    format!("{found:?}"),
                );
                let caller = if state.kind == "allocation" {
                    "SERVER"
                } else {
                    "CLIENT"
                };
                let works = found.iter().any(|a| {
                    http(&state, caller, a)
                        .ok()
                        .flatten()
                        .is_some_and(|v| v["server"] == "SERVER")
                });
                record(
                    "새 주소의 실제 응답",
                    works,
                    "추가 주소에서 원래 서버의 응답을 받아요.",
                    format!("접속 가능한 유효 주소가 있어요: {works}"),
                );
            }
            "mask" => {
                let routes = route(&state, "CLIENT", &server_ip)?;
                let address: Value =
                    serde_json::from_str(&ex_ok(&state, "CLIENT", &["ip", "-j", "addr"])?)
                        .map_err(|e| e.to_string())?;
                let correct = address
                    .as_array()
                    .into_iter()
                    .flatten()
                    .flat_map(|i| i["addr_info"].as_array().into_iter().flatten())
                    .any(|a| a["local"] == ip(&state, 0, 10) && a["prefixlen"] == 24);
                record(
                    "주소와 마스크",
                    correct,
                    "CLIENT_IP를 유지하고 /24로 설정해요.",
                    address.to_string(),
                );
                record(
                    "직접 연결 경로",
                    routes.as_ref().is_some_and(|v| v.get("gateway").is_none()),
                    "서버에는 다음 홉 없이 직접 연결 경로를 선택해요.",
                    format!("{routes:?}"),
                );
                let fallback = route(&state, "CLIENT", "192.0.2.50")?;
                record(
                    "기본 경로 보존",
                    default_gateway(&state)?
                        && fallback.is_some_and(|v| v["gateway"] == ip(&state, 0, 1)),
                    "기본 경로를 유지해요. 문서용 주소에 패킷을 보내지 않고 경로만 조회해요.",
                    "기본 경로의 다음 홉을 확인했어요.".into(),
                );
                record(
                    "실제 접속",
                    http(&state, "CLIENT", &server_ip)?.is_some_and(|v| v["server"] == "SERVER"),
                    "서버 응답을 받아요.",
                    server_ip,
                );
            }
            "routing" => {
                let selected = route(&state, "CLIENT", &server_ip)?;
                record(
                    "원격 네트워크의 다음 홉",
                    selected
                        .as_ref()
                        .is_some_and(|v| v["gateway"] == ip(&state, 0, 254)),
                    "원격 서버에는 라우터의 LAN 주소를 다음 홉으로 선택해요.",
                    format!("{selected:?}"),
                );
                record(
                    "다른 목적지의 기본 경로",
                    default_gateway(&state)?
                        && route(&state, "CLIENT", "192.0.2.50")?
                            .is_some_and(|v| v["gateway"] == ip(&state, 0, 1)),
                    "기존 기본 경로는 유지해요.",
                    "특정 목적지를 위한 경로인지 검사했어요.".into(),
                );
                record(
                    "왕복 전달",
                    http(&state, "CLIENT", &server_ip)?.is_some_and(|v| v["server"] == "SERVER"),
                    "원격 서버의 실제 응답을 받아요.",
                    "반환 경로까지 포함해 HTTP로 검사했어요.".into(),
                );
            }
            "nat" => {
                for role in ["CLIENT", "CLIENT_B"] {
                    let addresses: Value =
                        serde_json::from_str(&ex_ok(&state, role, &["ip", "-j", "addr"])?)
                            .map_err(|e| e.to_string())?;
                    let original = ip(&state, 0, if role == "CLIENT" { 10 } else { 11 });
                    let retained = addresses
                        .as_array()
                        .into_iter()
                        .flatten()
                        .flat_map(|i| i["addr_info"].as_array().into_iter().flatten())
                        .any(|a| a["local"] == original && a["prefixlen"] == 24);
                    record(
                        &format!("{role}의 원래 사설 주소"),
                        retained,
                        "각 클라이언트에 직접 할당된 원래 사설 주소는 유지해요.",
                        original,
                    );
                    let response = http(&state, role, &server_ip)?;
                    record(
                        role,
                        response.as_ref().is_some_and(|v| {
                            v["peer"] == ip(&state, 1, 254) && v["server"] == "SERVER"
                        }),
                        "서로 다른 두 클라이언트가 라우터의 바깥쪽 주소로 보여요.",
                        format!("{response:?}"),
                    );
                }
            }
            "dns" | "cache" => {
                let expected = ip(&state, 0, 140);
                let direct = ex_ok(
                    &state,
                    "CLIENT",
                    &[
                        "dig",
                        &format!("@{}", ip(&state, 0, 53)),
                        "memo.test",
                        "A",
                        "+short",
                    ],
                )?;
                record(
                    "권한 DNS의 A 레코드",
                    direct.split_whitespace().any(|s| s == expected),
                    "권한 DNS에서 SERVER_B_IP를 받아요.",
                    direct,
                );
                let response = http(&state, "CLIENT", "memo.test")?;
                record(
                    "이름으로 접속한 실제 서버",
                    response.as_ref().is_some_and(|v| v["server"] == "SERVER_B"),
                    "이름을 바꾸지 않고 서버 B에 접속해요.",
                    format!("{response:?}"),
                );
                if state.kind == "cache" {
                    let cached = ex_ok(
                        &state,
                        "CLIENT",
                        &[
                            "dig",
                            &format!("@{}", ip(&state, 0, 54)),
                            "memo.test",
                            "A",
                            "+short",
                        ],
                    )?;
                    record(
                        "캐시 DNS 응답",
                        cached.split_whitespace().any(|s| s == expected),
                        "클라이언트가 사용하는 캐시 DNS도 현재 서버 B를 가리켜요.",
                        cached,
                    );
                    let current = require(
                        &args(&[
                            "inspect",
                            "--format",
                            "{{.State.StartedAt}}",
                            &state.roles["CACHE"],
                        ]),
                        15,
                    )?;
                    record("캐시 서버의 새 회차",state.cache_started_at.as_deref().is_some_and(|initial|initial!=current.trim()),"캐시 서버를 새로 시작해서 이전 회차의 캐시를 제거해요. TTL 만료를 기다리기만 한 상태와 구별해요.","현재 회차와 준비 회차를 비교했어요.".into());
                }
            }
            _ => return Err("실습 종류를 확인하세요.".into()),
        }
        Ok(TestReport {
            passed: cases.iter().all(|c| c.passed),
            cases,
        })
    }
}
fn network_env(state: &State) -> Result<Vec<(String, String)>, String> {
    let mut env: Vec<_> = state
        .roles
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    env.extend([
        ("MSYS_NO_PATHCONV".into(), "1".into()),
        ("CLIENT_IP".into(), ip(state, 0, 10)),
        (
            "SERVER_IP".into(),
            ip(
                state,
                if ["routing", "nat"].contains(&state.kind.as_str()) {
                    1
                } else {
                    0
                },
                if state.kind == "allocation" { 10 } else { 130 },
            ),
        ),
        ("SERVER_B_IP".into(), ip(state, 0, 140)),
        ("TARGET_IP".into(), ip(state, 0, 132)),
        (
            "GATEWAY_IP".into(),
            ip(
                state,
                0,
                if state.kind == "allocation" {
                    9
                } else if state.kind == "nat" {
                    254
                } else {
                    1
                },
            ),
        ),
        ("ROUTER_IP".into(), ip(state, 0, 254)),
        ("ROUTER_OUT_IP".into(), ip(state, 1, 254)),
        ("DNS_IP".into(), ip(state, 0, 53)),
        ("CACHE_IP".into(), ip(state, 0, 54)),
        (
            "LAN_SUBNET".into(),
            if state.kind == "allocation" {
                format!("{}/29", ip(state, 0, 8))
            } else {
                cidr(state, 0)
            },
        ),
        ("REMOTE_SUBNET".into(), cidr(state, 1)),
        ("FREE_IP".into(), ip(state, 0, 11)),
    ]);
    // The address ledger describes this exercise, not nonexistent roles or
    // unrelated networks. In particular the allocation lab really is a /29.
    env.retain(|(key, _)| {
        state.roles.contains_key(key)
            || match key.as_str() {
                "MSYS_NO_PATHCONV" | "SERVER_IP" | "GATEWAY_IP" | "LAN_SUBNET" => true,
                "CLIENT_IP" => state.roles.contains_key("CLIENT"),
                "SERVER_B_IP" => state.roles.contains_key("SERVER_B"),
                "ROUTER_IP" | "ROUTER_OUT_IP" | "REMOTE_SUBNET" => {
                    state.roles.contains_key("ROUTER")
                }
                "DNS_IP" => state.roles.contains_key("DNS"),
                "CACHE_IP" => state.roles.contains_key("CACHE"),
                "TARGET_IP" => state.kind == "alias",
                "FREE_IP" => state.kind == "allocation",
                _ => false,
            }
    });
    // Share Docker Desktop and credential-helper discovery with the other Docker labs.
    let cli = network_cli()?;
    env.push(("PATH".into(), crate::docker_lab::search_path(&cli).to_string_lossy().into_owned()));
    Ok(env)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn exercise(kind: &str) -> GitExercise {
        GitExercise {
            network: Some(NetworkExercise { kind: kind.into() }),
            initial_history: GitInitialHistory::Uninitialized,
            shell: Some(ShellExercise {
                step_id: format!("network-{kind}"),
                ..Default::default()
            }),
            ..Default::default()
        }
    }
    fn interface(state: &State, role: &str, target: &str) -> String {
        route(state, role, target).unwrap().unwrap()["dev"]
            .as_str()
            .unwrap()
            .into()
    }
    fn dns_record(practice: &GitPractice, state: &State, host: u8) {
        let file = practice.work().join("memo.zone");
        let zone = std::fs::read_to_string(&file).unwrap();
        let changed = zone
            .lines()
            .map(|line| {
                if line.starts_with("@ IN A ") {
                    format!("@ IN A {}", ip(state, 0, host))
                } else {
                    line.into()
                }
            })
            .collect::<Vec<_>>()
            .join("\n")
            + "\n";
        std::fs::write(file, changed).unwrap();
        require(&args(&["restart", &state.roles["DNS"]]), 30).unwrap();
    }
    fn solve(practice: &GitPractice, state: &State) {
        match state.kind.as_str() {
            "loopback" => {
                std::fs::write(practice.work().join("bind.txt"), "0.0.0.0\n").unwrap();
                require(&args(&["restart", &state.roles["SERVER"]]), 30).unwrap();
                ready(state, "SERVER").unwrap();
            }
            "alias" | "allocation" => {
                let original = ip(state, 0, if state.kind == "alias" { 130 } else { 10 });
                let dev = interface(state, "SERVER", &original);
                // Looking up our own address selects lo; find the interface that
                // actually owns the original address instead of hardcoding eth0.
                let all: Value =
                    serde_json::from_str(&ex_ok(state, "SERVER", &["ip", "-j", "addr"]).unwrap())
                        .unwrap();
                let dev = all
                    .as_array()
                    .unwrap()
                    .iter()
                    .find(|i| {
                        i["addr_info"]
                            .as_array()
                            .unwrap()
                            .iter()
                            .any(|a| a["local"] == original)
                    })
                    .map(|i| i["ifname"].as_str().unwrap())
                    .unwrap_or(&dev);
                let new = format!(
                    "{}/{}",
                    ip(state, 0, if state.kind == "alias" { 132 } else { 12 }),
                    if state.kind == "alias" { 24 } else { 29 }
                );
                ex_ok(state, "SERVER", &["ip", "address", "add", &new, "dev", dev]).unwrap();
            }
            "mask" => {
                let dev = interface(state, "CLIENT", &ip(state, 0, 130));
                ex_ok(
                    state,
                    "CLIENT",
                    &[
                        "ip",
                        "addr",
                        "del",
                        &format!("{}/25", ip(state, 0, 10)),
                        "dev",
                        &dev,
                    ],
                )
                .unwrap();
                ex_ok(
                    state,
                    "CLIENT",
                    &[
                        "ip",
                        "addr",
                        "add",
                        &format!("{}/24", ip(state, 0, 10)),
                        "dev",
                        &dev,
                    ],
                )
                .unwrap();
                ex_ok(
                    state,
                    "CLIENT",
                    &["ip", "route", "replace", "default", "via", &ip(state, 0, 1)],
                )
                .unwrap();
            }
            "routing" => {
                ex_ok(
                    state,
                    "CLIENT",
                    &[
                        "ip",
                        "route",
                        "add",
                        &format!("{}/32", ip(state, 1, 130)),
                        "via",
                        &ip(state, 0, 254),
                    ],
                )
                .unwrap();
            }
            "nat" => {
                let dev = interface(state, "ROUTER", &ip(state, 1, 130));
                ex_ok(
                    state,
                    "ROUTER",
                    &[
                        "iptables",
                        "-t",
                        "nat",
                        "-A",
                        "POSTROUTING",
                        "-s",
                        &cidr(state, 0),
                        "-o",
                        &dev,
                        "-j",
                        "MASQUERADE",
                    ],
                )
                .unwrap();
            }
            "dns" => dns_record(practice, state, 140),
            "cache" => {
                require(&args(&["restart", &state.roles["CACHE"]]), 30).unwrap();
            }
            _ => unreachable!(),
        }
    }
    #[test]
    fn network_metadata_does_not_turn_other_exercises_into_ungraded_reading() {
        assert!(exercise("dns").validate().is_ok());
        assert!(exercise("unknown").validate().is_err());
        let mut other = exercise("dns");
        other.network = None;
        assert!(other.validate().is_err()); // empty command history needs a real state grader
    }
    #[cfg(windows)]
    #[test]
    #[ignore = "Requires Docker Desktop and Git Bash; queries the engine without creating resources"]
    fn docker_minimal_windows_path_smoke() {
        const CHILD: &str = "MQ3_NETWORK_MINIMAL_PATH_SMOKE";
        if std::env::var_os(CHILD).is_none() {
            // Isolate the minimal GUI PATH in a child test process, never mutate this process.
            let system = PathBuf::from(std::env::var_os("SystemRoot").unwrap()).join("System32");
            let mut child = Command::new(std::env::current_exe().unwrap());
            child.args(["git_practice::network_practice::tests::docker_minimal_windows_path_smoke", "--exact", "--ignored", "--nocapture", "--test-threads=1"])
                .env("PATH", system).env(CHILD, "1").env_remove("MOLIP_DOCKER").creation_flags(0x08000000);
            let output = child.output().unwrap();
            assert!(output.status.success(), "{}\n{}", String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr));
            println!("{}", String::from_utf8_lossy(&output.stdout));
            return;
        }
        let cli = network_cli().unwrap();
        assert!(!std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()).any(|path| Some(path.as_path()) == cli.parent()));
        assert!(docker(&args(&["info", "--format", "{{.OSType}}"]), 30).unwrap().ok);
        let environment = network_env(&State { kind: "loopback".into(), base: "172.16.0.0".into(), roles: BTreeMap::new(), ready: true, cache_started_at: None }).unwrap();
        let path = &environment.iter().find(|(key, _)| key == "PATH").unwrap().1;
        assert!(std::env::split_paths(path).any(|path| Some(path.as_path()) == cli.parent()));
        let mut bash = Command::new(crate::setup_terminal::git_bash_executable().unwrap());
        bash.args(["--noprofile", "--norc", "-c", "docker info --format '{{.OSType}}'"])
            .envs(environment).creation_flags(0x08000000);
        let output = bash.output().unwrap();
        assert!(output.status.success(), "{}", String::from_utf8_lossy(&output.stderr));
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "linux");
        println!("PASS minimal Windows GUI PATH: resolved {} and Bash reached Linux engine", cli.display());
    }
    #[test]
    #[ignore = "Requires Docker Desktop Linux engine; creates only labelled disposable resources"]
    fn docker_network_state_grading_and_lifecycle() {
        for kind in [
            "loopback",
            "alias",
            "allocation",
            "mask",
            "routing",
            "nat",
            "dns",
            "cache",
        ] {
            let practice = GitPractice::new(exercise(kind)).unwrap();
            let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                practice.prepare_network().unwrap();
                let state = load(practice.root()).unwrap();
                assert!(
                    !practice.check_network().unwrap().passed,
                    "{kind}: incomplete initial state passed"
                );
                solve(&practice, &state);
                let report = practice.check_network().unwrap();
                assert!(
                    report.passed,
                    "{kind}: valid solution rejected: {:?}",
                    report
                        .cases
                        .iter()
                        .filter(|c| !c.passed)
                        .map(|c| (&c.input, &c.stdout))
                        .collect::<Vec<_>>()
                );
                // No command history has been populated; acceptance came from
                // actual state. Allocation .12 and a /32 route are alternatives
                // to the narration's .11 and /24 solutions.
                assert!(practice.shell_completions().unwrap().is_empty());
                let resumed = practice.prepare_network().unwrap();
                assert!(resumed
                    .iter()
                    .any(|(k, v)| k == "SERVER" && v == &state.roles["SERVER"]));
                assert!(
                    practice.check_network().unwrap().passed,
                    "{kind}: reopening overwrote learner state"
                );
                let role = if state.roles.contains_key("CLIENT") {
                    "CLIENT"
                } else {
                    "SERVER"
                };
                require(&args(&["stop", &state.roles[role]]), 30).unwrap();
                assert!(
                    practice.check_network().is_err(),
                    "stopped environment must not be graded as a wrong answer"
                );
                println!("PASS {kind}: incomplete rejected, alternate/valid state accepted, resume preserved, stopped resource distinguished");
            }));
            practice.cleanup_network().unwrap();
            assert!(!practice.root().join("network-state.json").exists());
            if let Err(panic) = outcome {
                std::panic::resume_unwind(panic);
            }
        }
        // Saved scopes persist across reopening; a teacher gets separate resources
        // and can be cleaned without changing the student's solved state.
        let directory = tempfile::tempdir().unwrap();
        let store = GitPracticeStore::new(directory.path()).unwrap();
        let spec = exercise("alias");
        let student = store.open("student-network", spec.clone()).unwrap();
        student.prepare_network().unwrap();
        let old = load(student.root()).unwrap();
        solve(&student, &old);
        let teacher = GitPractice::new(spec.demonstration()).unwrap();
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            teacher.prepare_network().unwrap();
            assert_ne!(
                load(teacher.root()).unwrap().roles["SERVER"],
                old.roles["SERVER"]
            );
            assert!(!teacher.check_network().unwrap().passed);
            assert!(student.check_network().unwrap().passed);
            teacher.release_network_demo();
            assert!(student.check_network().unwrap().passed);
            let reopened = store.open("student-network", spec.clone()).unwrap();
            reopened.prepare_network().unwrap();
            assert!(reopened.check_network().unwrap().passed);
            let reset = store
                .reset_step("student-network", spec, "network-alias")
                .unwrap();
            assert!(
                !docker(&args(&["inspect", &old.roles["SERVER"]]), 15)
                    .unwrap()
                    .ok
            );
            reset.prepare_network().unwrap();
            assert!(!reset.check_network().unwrap().passed);
            reset.cleanup_network().unwrap();
            println!("PASS saved resume, teacher isolation, explicit reset and owned cleanup");
        }));
        let _ = teacher.cleanup_network();
        let _ = student.cleanup_network();
        if let Err(panic) = outcome {
            std::panic::resume_unwind(panic);
        }
    }
    #[test]
    #[ignore = "Executes the actual authored solutions and narration in Docker via Bash"]
    fn docker_authored_solutions_and_demonstrations() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR"));
        for folder in ["network_ip", "network_routing", "network_dns"] {
            let authored: Value = serde_json::from_slice(
                &std::fs::read(
                    root.join("tools/redesigned_lessons")
                        .join(folder)
                        .join("content.json"),
                )
                .unwrap(),
            )
            .unwrap();
            for task in authored["tasks"]
                .as_array()
                .unwrap()
                .iter()
                .filter(|t| !t["git_terminal"]["network"].is_null())
            {
                let spec: GitExercise =
                    serde_json::from_value(task["git_terminal"].clone()).unwrap();
                let practice = GitPractice::new(spec.demonstration()).unwrap();
                let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                    let environment = practice.prepare_network().unwrap();
                    let state = load(practice.root()).unwrap();
                    let primary = if state.roles.contains_key("CLIENT") {
                        "CLIENT"
                    } else {
                        "SERVER"
                    };
                    let selected = route(&state, primary, "192.0.2.50").unwrap().unwrap();
                    let exposed = environment.iter().find(|(k, _)| k == "GATEWAY_IP").unwrap();
                    assert_eq!(
                        selected["gateway"].as_str(),
                        Some(exposed.1.as_str()),
                        "ledger default gateway differs from actual route"
                    );
                    let actual_network: Value = serde_json::from_str(
                        &require(
                            &args(&[
                                "network",
                                "inspect",
                                &format!("{}-main", tag(practice.root())),
                            ]),
                            15,
                        )
                        .unwrap(),
                    )
                    .unwrap();
                    let exposed = environment.iter().find(|(k, _)| k == "LAN_SUBNET").unwrap();
                    assert_eq!(
                        actual_network[0]["IPAM"]["Config"][0]["Subnet"].as_str(),
                        Some(exposed.1.as_str()),
                        "ledger subnet differs from actual allocation pool"
                    );
                    assert!(!practice.check_network().unwrap().passed);
                    #[cfg(windows)]
                    let bash = crate::setup_terminal::git_bash_executable().unwrap();
                    #[cfg(not(windows))]
                    let bash = PathBuf::from("/bin/bash");
                    for action in task["narration"]
                        .as_array()
                        .unwrap()
                        .iter()
                        .filter(|a| a["action"] == "bash_command")
                    {
                        let command = action["command"].as_str().unwrap();
                        let mut runner = Command::new(&bash);
                        runner
                            .args(["--noprofile", "--norc", "-c", command])
                            .current_dir(practice.work())
                            .envs(environment.iter().cloned());
                        #[cfg(windows)]
                        {
                            let inherited = environment.iter().find(|(key, _)| key == "PATH")
                                .map(|(_, value)| std::ffi::OsString::from(value))
                                .unwrap_or_else(|| std::env::var_os("PATH").unwrap_or_default());
                            runner.env(
                                "PATH",
                                std::env::join_paths(
                                    bash.parent()
                                        .map(Path::to_path_buf)
                                        .into_iter()
                                        .chain(std::env::split_paths(&inherited)),
                                )
                                .unwrap(),
                            );
                        }
                        let result = runner.output().unwrap();
                        // The loopback demonstration intentionally shows a failed
                        // connection before correcting the bind address.
                        if !result.status.success()
                            && !(practice.exercise.network.as_ref().unwrap().kind == "loopback"
                                && command.contains("--max-time 3"))
                        {
                            panic!(
                                "{} authored command failed: {}",
                                task["title"],
                                String::from_utf8_lossy(&result.stderr)
                            );
                        }
                    }
                    let report = practice.check_network().unwrap();
                    assert!(
                        report.passed,
                        "{}: narration did not solve actual state: {:?}",
                        task["title"],
                        report
                            .cases
                            .iter()
                            .filter(|c| !c.passed)
                            .map(|c| (&c.input, &c.stdout))
                            .collect::<Vec<_>>()
                    );
                    println!("PASS authored narration: {}", task["title"]);
                }));
                practice.cleanup_network().unwrap();
                if let Err(panic) = outcome {
                    std::panic::resume_unwind(panic);
                }
            }
        }
    }
    #[test]
    #[ignore = "Requires Docker; checks wrong states that can still return HTTP responses"]
    fn docker_network_rejects_superficially_working_wrong_state() {
        for kind in ["alias", "allocation", "routing", "nat"] {
            let practice = GitPractice::new(exercise(kind)).unwrap();
            let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                practice.prepare_network().unwrap();
                let state = load(practice.root()).unwrap();
                solve(&practice, &state);
                assert!(practice.check_network().unwrap().passed);
                match kind {
                    "alias" | "allocation" => {
                        let address = ip(&state, 0, if kind == "alias" { 132 } else { 12 });
                        let all: Value = serde_json::from_str(
                            &ex_ok(&state, "SERVER", &["ip", "-j", "addr"]).unwrap(),
                        )
                        .unwrap();
                        let dev = all
                            .as_array()
                            .unwrap()
                            .iter()
                            .find(|i| {
                                i["addr_info"]
                                    .as_array()
                                    .unwrap()
                                    .iter()
                                    .any(|a| a["local"] == address)
                            })
                            .unwrap()["ifname"]
                            .as_str()
                            .unwrap();
                        ex_ok(
                            &state,
                            "SERVER",
                            &[
                                "ip",
                                "addr",
                                "del",
                                &format!("{address}/{}", if kind == "alias" { 24 } else { 29 }),
                                "dev",
                                dev,
                            ],
                        )
                        .unwrap();
                        ex_ok(
                            &state,
                            "SERVER",
                            &[
                                "ip",
                                "addr",
                                "add",
                                &format!("{address}/{}", if kind == "alias" { 32 } else { 24 }),
                                "dev",
                                dev,
                            ],
                        )
                        .unwrap();
                    }
                    "routing" => {
                        ex_ok(&state, "CLIENT", &["ip", "route", "del", "default"]).unwrap();
                        ex_ok(
                            &state,
                            "CLIENT",
                            &[
                                "ip",
                                "route",
                                "add",
                                "192.0.2.50/32",
                                "via",
                                &ip(&state, 0, 1),
                            ],
                        )
                        .unwrap();
                        assert!(route(&state, "CLIENT", "192.0.2.50").unwrap().is_some());
                    }
                    "nat" => {
                        let dev = interface(&state, "CLIENT", &ip(&state, 1, 130));
                        ex_ok(
                            &state,
                            "CLIENT",
                            &[
                                "ip",
                                "addr",
                                "del",
                                &format!("{}/24", ip(&state, 0, 10)),
                                "dev",
                                &dev,
                            ],
                        )
                        .unwrap();
                        ex_ok(
                            &state,
                            "CLIENT",
                            &[
                                "ip",
                                "addr",
                                "add",
                                &format!("{}/24", ip(&state, 0, 20)),
                                "dev",
                                &dev,
                            ],
                        )
                        .unwrap();
                        ex_ok(
                            &state,
                            "CLIENT",
                            &[
                                "ip",
                                "route",
                                "replace",
                                "default",
                                "via",
                                &ip(&state, 0, 254),
                            ],
                        )
                        .unwrap();
                        assert!(http(&state, "CLIENT", &ip(&state, 1, 130))
                            .unwrap()
                            .is_some());
                    }
                    _ => unreachable!(),
                }
                assert!(
                    !practice.check_network().unwrap().passed,
                    "{kind}: misleading state accepted"
                );
                println!("PASS {kind}: superficially working wrong state rejected");
            }));
            practice.cleanup_network().unwrap();
            if let Err(panic) = outcome {
                std::panic::resume_unwind(panic);
            }
        }
    }
}
