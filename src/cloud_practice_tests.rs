use super::*;

const STARTER: &str = "# 준비된 VPC 안에 서브넷 하나를 만드는 명령이에요.\n# 실행 전에 --cidr-block 값을 VPC 범위와 비교해 보세요.\naws ec2 create-subnet \\\n  --endpoint-url \"$LAB_ENDPOINT\" \\\n  --vpc-id \"$LAB_VPC_ID\" \\\n  --cidr-block STARTER_CIDR\n";

fn cloud(goal: CloudGoal, vpc: &str) -> CloudExercise {
    CloudExercise { goal, vpc_cidr: vpc.into(), subnets: vec![], client_subnet: None, server_subnet: None, target_cidr: None, target_subnet: None, new_prefix: None, address_file: None, editable: vec![] }
}
fn subnet(name: &str, block: &str) -> CloudSubnet {
    CloudSubnet { name: name.into(), cidr: block.into() }
}
fn exercise(spec: CloudExercise, files: &[(&str, &str)]) -> GitExercise {
    let files: BTreeMap<String, String> = files.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();
    GitExercise {
        cloud: Some(spec),
        initial_history: GitInitialHistory::Uninitialized,
        shell: Some(ShellExercise {
            step_id: "cloud-step".into(),
            start: Some(ShellSnapshot { files: files.clone(), ..Default::default() }),
            demo: ShellSnapshot { files, ..Default::default() },
            ..Default::default()
        }),
        ..Default::default()
    }
}
fn representative(vpc: &str, target: &str, starter: &str) -> GitExercise {
    let mut spec = cloud(CloudGoal::CreateSubnet, vpc);
    spec.target_cidr = Some(target.into());
    exercise(spec, &[("create-subnet.sh", &STARTER.replace("STARTER_CIDR", starter))])
}

#[test]
fn schema_round_trips_and_rejects_unknown_fields() {
    let spec = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24");
    let raw = serde_json::to_string(&spec).unwrap();
    assert_eq!(serde_json::from_str::<GitExercise>(&raw).unwrap(), spec);
    assert!(!raw.contains("cloud_demonstration"));
    let bad = r#"{"goal":"create_subnet","vpc_cidr":"10.91.0.0/16","target_cidr":"10.91.2.0/24","extra":1}"#;
    assert!(serde_json::from_str::<CloudExercise>(bad).is_err());
    let missing: GitExercise = serde_json::from_str("{}").unwrap();
    assert!(missing.cloud.is_none());
}

#[test]
fn goal_specific_validation() {
    let vpc = "10.91.0.0/16";
    let mut create = cloud(CloudGoal::CreateSubnet, vpc);
    assert!(create.validate().is_err(), "target required");
    create.target_cidr = Some("10.91.2.0/24".into());
    assert!(create.validate().is_ok());
    create.target_cidr = Some("10.92.2.0/24".into());
    assert!(create.validate().is_err(), "target outside VPC");
    create.target_cidr = Some("10.91.2.1/24".into());
    assert!(create.validate().is_err(), "unaligned");
    create.target_cidr = Some("10.91.2.0/24".into());
    create.subnets = vec![subnet("A", "10.91.2.0/25")];
    assert!(create.validate().is_err(), "target overlaps prepared");
    create.subnets = vec![];
    create.new_prefix = Some(24);
    assert!(create.validate().is_err(), "unused field must stay empty");

    let mut choose = cloud(CloudGoal::ChooseSubnet, vpc);
    choose.subnets = vec![subnet("A", "10.91.1.0/24")];
    choose.new_prefix = Some(24);
    assert!(choose.validate().is_ok());
    choose.new_prefix = Some(8);
    assert!(choose.validate().is_err());

    let mut launch = cloud(CloudGoal::LaunchServer, vpc);
    launch.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("B", "10.91.2.0/24")];
    launch.target_subnet = Some("B".into());
    assert!(launch.validate().is_ok() && launch.guest());
    launch.target_subnet = Some("C".into());
    assert!(launch.validate().is_err());
    launch.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("A", "10.91.2.0/24")];
    launch.target_subnet = Some("A".into());
    assert!(launch.validate().is_err(), "duplicate names");
    launch.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("b", "10.91.2.0/24")];
    assert!(launch.validate().is_err(), "lowercase names become env names");

    let mut request = cloud(CloudGoal::RequestServer, vpc);
    request.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("B", "10.91.2.0/24")];
    request.client_subnet = Some("A".into());
    request.server_subnet = Some("B".into());
    assert!(request.validate().is_err(), "address file required");
    request.address_file = Some("server-address.txt".into());
    assert!(request.validate().is_ok());
    request.server_subnet = Some("A".into());
    assert!(request.validate().is_err(), "client and server in different subnets");

    let mut deploy = cloud(CloudGoal::DeployServer, vpc);
    deploy.subnets = vec![subnet("A", "10.91.1.0/24")];
    deploy.client_subnet = Some("A".into());
    deploy.target_cidr = Some("10.91.2.0/24".into());
    deploy.address_file = Some("../escape.txt".into());
    assert!(deploy.validate().is_err());
    deploy.address_file = Some("server-address.txt".into());
    assert!(deploy.validate().is_ok());
}

#[test]
fn git_exercise_validation_keeps_cloud_separate() {
    assert!(representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24").validate().is_ok());
    let mut mixed = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24");
    mixed.network = Some(NetworkExercise { kind: "mask".into() });
    assert!(mixed.validate().is_err(), "cloud is not a NetworkExercise kind");
    let mut shell_less = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24");
    shell_less.shell = None;
    assert!(shell_less.validate().is_err());
    let mut deploy = cloud(CloudGoal::DeployServer, "10.91.0.0/16");
    deploy.subnets = vec![subnet("A", "10.91.1.0/24")];
    deploy.client_subnet = Some("A".into());
    deploy.target_cidr = Some("10.91.2.0/24".into());
    deploy.address_file = Some("server-address.txt".into());
    assert!(exercise(deploy.clone(), &[]).validate().is_err(), "address file must be a prepared file");
    assert!(exercise(deploy, &[("server-address.txt", "0.0.0.0\n")]).validate().is_ok());
    let demo = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24").demonstration();
    assert!(demo.cloud_demonstration && !demo.network_demonstration);
}

#[test]
fn editor_shows_only_listed_prepared_files() {
    let mut shown = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24");
    assert!(GitPractice::new(shown.clone()).unwrap().editable_files().is_empty(), "no list, terminal only");
    shown.cloud.as_mut().unwrap().editable = vec!["create-subnet.sh".into()];
    assert!(shown.validate().is_ok());
    let practice = GitPractice::new(shown.clone()).unwrap();
    assert_eq!(practice.editable_files(), vec!["create-subnet.sh".to_string()]);
    assert!(practice.read_editable("create-subnet.sh").unwrap().contains("--cidr-block 10.92.2.0/24"));
    assert!(practice.save_editable("other.sh", "x").is_err(), "an unlisted file is not editable");
    for bad in [vec!["missing.sh"], vec!["../create-subnet.sh"], vec!["create-subnet.sh", "create-subnet.sh"]] {
        let mut spec = shown.clone();
        spec.cloud.as_mut().unwrap().editable = bad.iter().map(|f| f.to_string()).collect();
        assert!(spec.validate().is_err(), "{bad:?}");
    }
    // Read-only helper tabs: prepared files, never the editable ones, only on cloud steps, never saved.
    let mut helper = shown.clone();
    let shell = helper.shell.as_mut().unwrap();
    for files in [&mut shell.start.as_mut().unwrap().files, &mut shell.demo.files] {
        files.insert("list-servers.sh".into(), "aws ec2 describe-instances\n".into());
    }
    helper.readonly_files = vec!["list-servers.sh".into()];
    assert!(helper.validate().is_ok());
    let practice = GitPractice::new(helper.clone()).unwrap();
    assert_eq!(practice.read_shown("list-servers.sh").unwrap(), "aws ec2 describe-instances\n");
    assert!(practice.save_editable("list-servers.sh", "rm -rf /").is_err(), "a read-only tab is not saved");
    for bad in [vec!["missing.sh"], vec!["create-subnet.sh"], vec!["list-servers.sh", "list-servers.sh"]] {
        let mut spec = helper.clone();
        spec.readonly_files = bad.iter().map(|f| f.to_string()).collect();
        assert!(spec.validate().is_err(), "readonly {bad:?}");
    }
    let mut plain = helper.clone();
    plain.cloud = None;
    assert!(plain.validate().is_err(), "read-only tabs are a cloud-step feature");
}

#[test]
fn fixture_identity_changes_with_the_prepared_state() {
    let a = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24");
    let b = representative("10.73.0.0/16", "10.73.2.0/24", "10.74.2.0/24");
    assert_ne!(a.cloud.as_ref().unwrap().fixture(), b.cloud.as_ref().unwrap().fixture());
    assert_eq!(a.cloud.as_ref().unwrap().fixture(), a.clone().cloud.unwrap().fixture());
    assert!(cidr("10.91.2.0/24").is_some_and(|t| contains(cidr("10.91.0.0/16").unwrap(), t)));
    assert!(!contains(cidr("10.91.0.0/16").unwrap(), cidr("10.92.2.0/24").unwrap()));
    assert!(holds(cidr("10.91.2.0/24").unwrap(), "10.91.2.10".parse().unwrap()));
}

fn bash_program() -> PathBuf {
    #[cfg(windows)]
    return crate::setup_terminal::git_bash_executable().unwrap();
    #[cfg(not(windows))]
    return PathBuf::from("bash");
}
fn bash_in(dir: &Path, env: &[(String, String)], script: &str) -> (bool, String, String) {
    let mut command = Command::new(bash_program());
    command.args(["--noprofile", "--norc", "-c", script]).current_dir(dir).envs(env.iter().cloned());
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    let out = command.output().unwrap();
    (out.status.success(), String::from_utf8_lossy(&out.stdout).replace("\r\n", "\n"), String::from_utf8_lossy(&out.stderr).into_owned())
}

/// The wrapper's argument guard, against a stand-in docker that only prints its argv.
#[test]
fn aws_wrapper_guards_endpoint_profile_and_environment() {
    if bash_program().as_os_str() == "bash" && Command::new("bash").arg("--version").output().is_err() {
        return;
    }
    let dir = tempfile::tempdir().unwrap();
    let docker = dir.path().join("fake docker");
    std::fs::write(&docker, "#!/bin/bash
printf 'ARG<%s>\n' \"$@\"
").unwrap();
    let owned = "http://127.0.0.1:45555";
    std::fs::write(dir.path().join("aws"), aws_wrapper(owned, &docker, dir.path())).unwrap();
    #[cfg(unix)]
    for f in ["aws", "fake docker"] {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(dir.path().join(f), std::fs::Permissions::from_mode(0o755)).unwrap();
    }
    let inner = inner_endpoint(dir.path());
    let (network, _, _) = names(dir.path());
    let env = vec![("AWS_PROFILE".to_string(), "real-account".to_string()), ("AWS_ACCESS_KEY_ID".to_string(), "AKIAREAL".to_string())];
    let (ok, out, err) = bash_in(dir.path(), &env, "./aws ec2 describe-vpcs --query 'Vpcs[0]'");
    assert!(ok, "{out}{err}");
    let args: Vec<&str> = out.lines().map(|l| l.trim_start_matches("ARG<").trim_end_matches('>')).collect();
    assert_eq!(&args[..5], ["run", "-i", "--rm", "--network", network.as_str()], "{out}");
    assert!(out.ends_with(&format!("ARG<{AWS_CLI_IMAGE}>
ARG<--endpoint-url>
ARG<{inner}>
ARG<ec2>
ARG<describe-vpcs>
ARG<--query>
ARG<Vpcs[0]>
")), "{out}");
    for value in AWS_CONTAINER_ENV {
        assert!(out.contains(&format!("ARG<-e>
ARG<{value}>
")), "{value}: {out}");
    }
    assert!(!out.contains("real-account") && !out.contains("AKIAREAL"), "the host account must not reach the CLI: {out}");
    let mount = args.iter().position(|a| *a == "-v").map(|i| args[i + 1]).unwrap();
    assert!(mount.ends_with(":/aws") && mount.len() > ":/aws".len(), "the current folder is mounted at /aws: {mount}");
    // Exact owned endpoint, alone, in equals form, or repeated: only the inner endpoint reaches the CLI.
    for accepted in [
        format!("./aws --endpoint-url {owned} ec2 describe-vpcs"),
        format!("./aws --endpoint-url={owned} ec2 describe-vpcs"),
        format!("./aws --endpoint-url {owned} ec2 describe-vpcs --endpoint-url={owned}"),
    ] {
        let (ok, out, _) = bash_in(dir.path(), &env, &accepted);
        assert!(ok && out.matches("ARG<--endpoint-url>").count() == 1 && !out.contains(owned) && out.contains(&format!("ARG<{inner}>")), "{accepted}: {out}");
    }
    // The wrapper's docker stand-in never runs for these, so nothing is contacted.
    let rejected_cases = [
        "./aws --endpoint-url https://ec2.us-east-1.amazonaws.com ec2 describe-vpcs".to_string(),
        "./aws --endpoint-url=https://ec2.us-east-1.amazonaws.com ec2 describe-vpcs".to_string(),
        "./aws --endpoint-url http://127.0.0.1:45556 ec2 describe-vpcs".to_string(),
        "./aws --endpoint-url= ec2 describe-vpcs".to_string(),
        "./aws ec2 describe-vpcs --endpoint-url".to_string(),
        format!("./aws --endpoint-url {owned} ec2 describe-vpcs --endpoint-url http://127.0.0.1:45556"),
        format!("./aws --endpoint-url={owned} --endpoint-url=https://ec2.us-east-1.amazonaws.com ec2 describe-vpcs"),
        format!("./aws --endp {owned} ec2 describe-vpcs"),
        "./aws --endp=https://ec2.us-east-1.amazonaws.com ec2 describe-vpcs".to_string(),
        "./aws --endpoint https://ec2.us-east-1.amazonaws.com ec2 describe-vpcs".to_string(),
        "./aws ec2 describe-vpcs --profile default".to_string(),
        "./aws ec2 describe-vpcs --prof default".to_string(),
        "./aws ec2 describe-vpcs --profile=default".to_string(),
        "./aws ec2 describe-vpcs --ca-b /tmp/x.pem".to_string(),
        "./aws ec2 describe-vpcs --no-verify-ssl".to_string(),
        "./aws ec2 describe-vpcs --no-verify".to_string(),
        "./aws ec2 describe-vpcs --no-sign".to_string(),
    ];
    for rejected in &rejected_cases {
        let (ok, out, err) = bash_in(dir.path(), &env, rejected);
        assert!(!ok && !out.contains("ARG<"), "{rejected} must be rejected before docker runs: {out}{err}");
    }
    println!("PASS wrapper: inner endpoint injected, only dummy keys passed, external/other endpoint and profile rejected before docker");
}

/// `client-request` trims a Windows `--output text` CRLF and surrounding blanks, nothing inside.
#[test]
fn client_request_trims_only_surrounding_whitespace() {
    if bash_program().as_os_str() == "bash" && Command::new("bash").arg("--version").output().is_err() {
        return;
    }
    let dir = tempfile::tempdir().unwrap();
    let docker = dir.path().join("fake docker");
    std::fs::write(&docker, "#!/bin/bash\nprintf 'ARG<%s>\\n' \"$@\"\n").unwrap();
    std::fs::write(dir.path().join("client-request"), client_wrapper(&docker, "runtime", "client")).unwrap();
    #[cfg(unix)]
    for f in ["client-request", "fake docker"] {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(dir.path().join(f), std::fs::Permissions::from_mode(0o755)).unwrap();
    }
    let expected = format!("ARG<exec>\nARG<runtime>\nARG<docker>\nARG<exec>\nARG<client>\nARG<java>\nARG</opt/mq/HttpCheck.java>\nARG<10.91.2.10>\nARG<{HTTP_PORT}>\n");
    std::fs::write(dir.path().join("crlf.txt"), "10.91.2.10\r\n").unwrap();
    for accepted in ["./client-request 10.91.2.10", "./client-request \"$(< crlf.txt)\"", "./client-request $' 10.91.2.10\\t\\r\\n'"] {
        let (ok, out, err) = bash_in(dir.path(), &[], accepted);
        assert!(ok && out == expected, "{accepted}: {out}{err}");
    }
    for rejected in ["./client-request", "./client-request '10.91. 2.10'", "./client-request 10.91.2.10 10.91.2.11", "./client-request http://10.91.2.10", "./client-request $'\\r\\n'"] {
        let (ok, out, err) = bash_in(dir.path(), &[], rejected);
        assert!(!ok && !out.contains("ARG<"), "{rejected} must be rejected before docker runs: {out}{err}");
    }
}

#[test]
fn address_file_reads_are_bounded_and_regular() {
    let dir = tempfile::tempdir().unwrap();
    let file = dir.path().join("server-address.txt");
    std::fs::write(&file, "  10.91.2.10\r\n").unwrap();
    assert_eq!(read_address(&file), Some("10.91.2.10".parse().unwrap()));
    for bad in ["", "10.91.2", "10.91.2.256", "http://10.91.2.10", "10.91.2.10\n10.91.2.11\n", "\u{feff}garbage"] {
        std::fs::write(&file, bad).unwrap();
        assert_eq!(read_address(&file), None, "{bad:?}");
    }
    std::fs::write(&file, format!("10.91.2.10{}", " ".repeat(300))).unwrap();
    assert_eq!(read_address(&file), None, "over 256 bytes is rejected even if it would parse");
    std::fs::write(&file, vec![b'1'; 5_000_000]).unwrap();
    assert_eq!(read_address(&file), None, "large file rejected by size before reading");
    std::fs::write(&file, [0xff, 0xfe, 0x00]).unwrap();
    assert_eq!(read_address(&file), None, "invalid UTF-8");
    std::fs::remove_file(&file).unwrap();
    std::fs::create_dir(&file).unwrap();
    assert_eq!(read_address(&file), None, "a directory is not an address file");
    assert_eq!(read_address(&dir.path().join("missing.txt")), None);
    #[cfg(unix)]
    {
        let target = dir.path().join("target.txt");
        std::fs::write(&target, "10.91.2.10\n").unwrap();
        let link = dir.path().join("link.txt");
        std::os::unix::fs::symlink(&target, &link).unwrap();
        assert_eq!(read_address(&link), None, "links are not followed");
    }
}

#[test]
fn ami_architecture_comes_from_the_docker_image() {
    assert_eq!(ami_architecture("amd64"), Some("x86_64"));
    assert_eq!(ami_architecture("arm64"), Some("arm64"));
    assert_eq!(ami_architecture("arm"), None);
    assert_eq!(ami_architecture(""), None);
}

#[test]
fn guest_base_is_x86_64_for_the_lessons_t3_micro_and_floci_is_native() {
    // Floci launches the guest with the AMI's platform, and t3.micro accepts only x86_64.
    assert_eq!(image_platform(TEMURIN), "linux/amd64");
    let native = if cfg!(target_arch = "aarch64") { "linux/arm64" } else { "linux/amd64" };
    assert_eq!(image_platform(FLOCI), native);
}

// -- Docker-gated native tests ------------------------------------------------------------
fn evidence_dir() -> PathBuf {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("target/cloud-native-evidence");
    std::fs::create_dir_all(&dir).unwrap();
    dir
}
/// Raw host inventory with safe metadata only: `docker ps`/`volume ls` rows (no container
/// Config/Env) and the full `docker network inspect` of every network (IPAM, options, labels).
fn raw_inventory() -> Result<Value, String> {
    let rows = |args: &[&str]| -> Result<Vec<Value>, String> {
        require(args, 30)?.lines().filter(|l| !l.trim().is_empty()).map(|l| serde_json::from_str(l).map_err(|e| e.to_string())).collect()
    };
    let ids: Vec<String> = require(&["network", "ls", "-q", "--no-trunc"], 30)?.split_whitespace().map(String::from).collect();
    let mut args = vec!["network", "inspect"];
    args.extend(ids.iter().map(String::as_str));
    // A network can vanish between `ls` and `inspect` (seen when the default bridge was replaced).
    let networks = serde_json::from_str::<Value>(&require(&args, 30)?).map_err(|e| e.to_string())?;
    Ok(serde_json::json!({
        "containers": rows(&["ps", "-a", "--no-trunc", "--format", "{{json .}}"])?,
        "networks": networks,
        "volumes": rows(&["volume", "ls", "--format", "{{json .}}"])?,
        "context": require(&["context", "show"], 20)?.trim(),
    }))
}
/// Stable comparison view. Networks are keyed by Id, so a replaced bridge stays a difference;
/// only per-network attachment lists and `docker ps` relative-time text are left to the raw file.
fn semantic(raw: &Value) -> Value {
    let pick = |v: &Value, keys: &[&str]| -> Value { keys.iter().map(|k| (k.to_string(), v[*k].clone())).collect::<serde_json::Map<_, _>>().into() };
    let mut containers: Vec<Value> = raw["containers"].as_array().unwrap().iter().map(|c| {
        let mut nets: Vec<&str> = c["Networks"].as_str().unwrap_or_default().split(',').collect();
        nets.sort();
        let mut v = pick(c, &["ID", "Names", "Image", "State", "Ports", "Labels"]);
        v["Networks"] = nets.join(",").into();
        v
    }).collect();
    containers.sort_by_key(|c| c["ID"].to_string());
    let mut networks: Vec<Value> = raw["networks"].as_array().unwrap().iter()
        .map(|n| pick(n, &["Id", "Name", "Created", "Driver", "Scope", "EnableIPv4", "EnableIPv6", "IPAM", "Internal", "Attachable", "Ingress", "ConfigOnly", "Options", "Labels"]))
        .collect();
    networks.sort_by_key(|n| n["Id"].to_string());
    let mut volumes: Vec<Value> = raw["volumes"].as_array().unwrap().iter().map(|v| pick(v, &["Name", "Driver", "Labels", "Scope"])).collect();
    volumes.sort_by_key(|v| v["Name"].to_string());
    serde_json::json!({"containers": containers, "networks": networks, "volumes": volumes, "context": raw["context"]})
}
fn try_inventory(name: &str, phase: &str) -> Result<Value, String> {
    let raw = match raw_inventory() {
        Ok(raw) => raw,
        Err(error) => {
            std::fs::write(evidence_dir().join(format!("{name}-{phase}-error.txt")), &error).unwrap();
            return Err(error);
        }
    };
    std::fs::write(evidence_dir().join(format!("{name}-{phase}-raw.json")), serde_json::to_vec_pretty(&raw).unwrap()).unwrap();
    let view = semantic(&raw);
    std::fs::write(evidence_dir().join(format!("{name}-{phase}.json")), serde_json::to_vec_pretty(&view).unwrap()).unwrap();
    Ok(view)
}
fn inventory(name: &str, phase: &str) -> Value {
    try_inventory(name, phase).unwrap()
}
/// Before a test: the engine answers and two successive snapshots two seconds apart agree.
/// A failed or changed probe is kept on disk and the probe repeats; nothing is normalized away.
fn stable_inventory(name: &str) -> Value {
    assert!(wait(120, || Ok(docker(&["info", "--format", "{{.OSType}}"], 30)?.ok.then_some(()))).unwrap().is_some(), "Docker not ready");
    let mut previous: Option<Value> = None;
    for attempt in 0..=15 {
        if attempt > 0 {
            std::thread::sleep(Duration::from_secs(2));
        }
        let current = try_inventory(name, &format!("before-probe-{attempt}")).ok();
        if current.is_some() && current == previous {
            return inventory(name, "before");
        }
        previous = current;
    }
    panic!("host inventory did not settle before {name}; see before-probe-*.json");
}
fn assert_no_owned_leftovers() {
    let filter = format!("label={LABEL}");
    for args in [vec!["ps", "-aq", "--filter", &filter], vec!["network", "ls", "-q", "--filter", &filter], vec!["volume", "ls", "-q", "--filter", &filter]] {
        assert!(require(&args, 20).unwrap().trim().is_empty(), "owned cloud resources left: {args:?}");
    }
}
/// Run a Docker test with before/after host inventories; cleanup runs even if the body panics.
/// Tests record each practice's owner tag: a panic drops temporary roots, so the guard
/// removes by exact owner label rather than by the (possibly deleted) state file.
fn guarded(name: &str, body: impl FnOnce(&mut Vec<String>)) {
    // Each run gets its own evidence names so earlier (failed) runs are never overwritten.
    let stamp = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis();
    let name = &format!("{name}-{stamp}");
    let before = stable_inventory(name);
    let mut owners = vec![];
    let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| body(&mut owners)));
    for tag in &owners {
        if let Err(error) = remove_owned(tag) {
            eprintln!("cleanup failed: {error}");
        }
    }
    let after = inventory(name, "after");
    if let Err(panic) = outcome {
        std::panic::resume_unwind(panic);
    }
    assert_no_owned_leftovers();
    assert_eq!(before, after, "host inventory changed; see target/cloud-native-evidence/{name}-*.json");
    println!("PASS {name}: host containers/networks/volumes/context identical before and after");
}
/// Graded through the app's submission dispatch (check_exercise -> check_shell -> check_cloud).
fn report(practice: &GitPractice) -> crate::runner::TestReport {
    let r = practice.check_exercise().unwrap();
    for c in &r.cases {
        println!("    [{}] {}: {}", if c.passed { "o" } else { "x" }, c.input, c.stdout.replace('\n', " | "));
    }
    r
}
fn sh(practice: &GitPractice, env: &[(String, String)], script: &str) -> (bool, String, String) {
    println!("  $ {script}");
    let r = bash_in(&practice.work(), env, script);
    println!("    rc_ok={} {}{}", r.0, r.1.trim(), r.2.trim().chars().take(300).collect::<String>());
    r
}
fn with_cidr(script: &str, from: &str, to: &str) -> String {
    script.replace(&format!("--cidr-block {from}"), &format!("--cidr-block {to}"))
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine, and Git Bash; creates only labelled disposable resources"]
fn docker_cloud_representative_subnet_lifecycle() {
    guarded("representative", |owned| {
        let directory = tempfile::tempdir().unwrap();
        let store = GitPracticeStore::new(directory.path()).unwrap();
        let spec = representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24");
        let student = store.open("cloud-rep", spec.clone()).unwrap();
        owned.push(owner(student.root()));
        let env = student.prepare_cloud().unwrap();
        let state = load(student.root()).unwrap();
        let original = std::fs::read(student.work().join("create-subnet.sh")).unwrap();
        let first = report(&student);
        assert!(!first.passed, "initial state passed");

        // MQ's aws entrypoint: external endpoint rejected, omitted endpoint stays on the owned API.
        let (ok, _, err) = sh(&student, &env, "aws --endpoint-url https://ec2.us-east-1.amazonaws.com ec2 describe-vpcs");
        assert!(!ok && err.contains("실습 주소"));
        let (ok, out, _) = sh(&student, &env, "aws ec2 describe-vpcs --vpc-ids \"$LAB_VPC_ID\" --query 'Vpcs[0].CidrBlock' --output text");
        assert!(ok && out.trim() == "10.91.0.0/16", "omitted --endpoint-url must reach the owned VPC");
        let (ok, _, _) = sh(&student, &env, "aws ec2 describe-vpcs --profile default");
        assert!(!ok);

        let (ok, _, err) = sh(&student, &env, "bash create-subnet.sh");
        assert!(!ok && err.contains("InvalidSubnet.Range"));
        assert!(!report(&student).passed, "starter outside CIDR");
        let (ok, out, _) = sh(&student, &env, r#"echo '{"Subnet":{"VpcId":"'"$LAB_VPC_ID"'","CidrBlock":"10.91.2.0/24","State":"available"}}'"#);
        assert!(ok && out.contains("10.91.2.0/24"));
        assert!(!report(&student).passed, "printed success JSON is not state");
        let fixed = with_cidr(&String::from_utf8_lossy(&original), "10.92.2.0/24", "10.91.2.0/24");
        std::fs::write(student.work().join("fixed.sh"), &fixed).unwrap();
        let (ok, _, _) = sh(&student, &env, "v=$(aws ec2 create-vpc --cidr-block 10.91.0.0/16 --query Vpc.VpcId --output text | tr -d '\\r') && LAB_VPC_ID=$v bash fixed.sh");
        assert!(ok);
        let wrong_vpc = report(&student);
        assert!(!wrong_vpc.passed && wrong_vpc.cases.iter().any(|c| c.stdout.contains("다른 자리")), "same CIDR in a learner VPC");
        std::fs::remove_file(student.work().join("fixed.sh")).unwrap();
        let (ok, _, _) = sh(&student, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.3.0/24");
        assert!(ok);
        let in_range = report(&student);
        assert!(!in_range.passed, "other in-range CIDR");
        let extra = in_range.cases.iter().find(|c| c.input == "필요 없는 서브넷").unwrap();
        assert!(!extra.passed && extra.stdout.contains("목표가 아닌 새 서브넷이 있어요: 10.91.3.0/24"), "feedback names the observed wrong subnet: {}", extra.stdout);
        let (ok, _, _) = sh(&student, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.2.0/24");
        assert!(ok);
        assert!(!report(&student).passed, "target plus an extra subnet");
        let (ok, _, _) = sh(&student, &env, "id=$(aws ec2 describe-subnets --filters Name=cidr-block,Values=10.91.3.0/24 Name=vpc-id,Values=\"$LAB_VPC_ID\" --query 'Subnets[0].SubnetId' --output text | tr -d '\\r') && aws ec2 delete-subnet --subnet-id \"$id\"");
        assert!(ok);
        assert!(report(&student).passed, "equivalent direct commands after deleting the extra subnet");

        // Reconnect: same owned runtime and state, nothing recreated.
        let reopened = store.open("cloud-rep", spec.clone()).unwrap();
        reopened.prepare_cloud().unwrap();
        assert_eq!(load(reopened.root()).unwrap().vpc_id, state.vpc_id);
        assert!(reopened.check_exercise().unwrap().passed, "reconnect kept the learner state");

        // Explanation lane: separate resources, released without touching the student.
        let teacher = GitPractice::new(spec.demonstration()).unwrap();
        owned.push(owner(teacher.root()));
        let teacher_env = teacher.prepare_cloud().unwrap();
        let teacher_state = load(teacher.root()).unwrap();
        assert_ne!(teacher_state.port, state.port);
        assert!(!teacher.check_exercise().unwrap().passed);
        let teacher_fix = with_cidr(&std::fs::read_to_string(teacher.work().join("create-subnet.sh")).unwrap(), "10.92.2.0/24", "10.91.2.0/24");
        std::fs::write(teacher.work().join("create-subnet.sh"), teacher_fix).unwrap();
        assert!(sh(&teacher, &teacher_env, "bash create-subnet.sh").0);
        assert!(teacher.check_exercise().unwrap().passed);
        teacher.release_network_demo();
        assert!(!docker(&["inspect", &names(teacher.root()).1], 15).unwrap().ok, "demonstration runtime released");
        assert!(student.check_exercise().unwrap().passed, "explanation did not change the student");
        assert_eq!(std::fs::read(student.work().join("create-subnet.sh")).unwrap(), original);

        // Runtime gone is an environment error, not a wrong answer, on check and on reconnect.
        require(&["stop", "-t", "2", &names(student.root()).1], 30).unwrap();
        assert!(student.check_exercise().is_err());
        assert!(store.open("cloud-rep", spec.clone()).unwrap().prepare_cloud().is_err());

        // Reset: fresh owned runtime and the prepared file back byte for byte; old copy kept.
        let reset = store.reset_step("cloud-rep", spec.clone(), "cloud-step").unwrap();
        owned.push(owner(reset.root()));
        assert!(!docker(&["inspect", &names(student.root()).1], 15).unwrap().ok, "old runtime removed by reset");
        assert!(student.root().is_dir(), "previous practice kept as a recovery copy");
        let reset_env = reset.prepare_cloud().unwrap();
        assert_eq!(std::fs::read(reset.work().join("create-subnet.sh")).unwrap(), original);
        assert!(!report(&reset).passed);
        std::fs::write(reset.work().join("create-subnet.sh"), with_cidr(&String::from_utf8_lossy(&original), "10.92.2.0/24", "10.91.2.0/24")).unwrap();
        assert!(sh(&reset, &reset_env, "bash create-subnet.sh").0);
        assert!(report(&reset).passed, "one-line fix passes");
        // A content revision changes the fixture: reconnect refuses instead of grading stale state.
        let revised = representative("10.91.0.0/16", "10.91.4.0/24", "10.92.2.0/24");
        assert!(store.open("cloud-rep", revised).unwrap().prepare_cloud().is_err());
        reset.cleanup_cloud().unwrap();
        println!("PASS representative: initial/starter/spoof/wrong VPC/in-range/extra fail, direct+delete pass, wrapper guard, reconnect, explanation isolation, env error, reset, stale fixture");
    });
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine, and Git Bash; creates only labelled disposable resources"]
fn docker_cloud_changed_fixture_and_choose_subnet() {
    guarded("fixtures", |owned| {
        let changed = GitPractice::new(representative("10.73.0.0/16", "10.73.2.0/24", "10.74.2.0/24")).unwrap();
        owned.push(owner(changed.root()));
        let env = changed.prepare_cloud().unwrap();
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            assert!(!report(&changed).passed);
            let (ok, _, err) = sh(&changed, &env, "bash create-subnet.sh");
            assert!(!ok && err.contains("InvalidSubnet.Range"));
            let (ok, _, _) = sh(&changed, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.2.0/24");
            assert!(!ok, "the default lesson's target is outside this fixture");
            assert!(!report(&changed).passed);
            let fix = with_cidr(&std::fs::read_to_string(changed.work().join("create-subnet.sh")).unwrap(), "10.74.2.0/24", "10.73.2.0/24");
            std::fs::write(changed.work().join("create-subnet.sh"), fix).unwrap();
            assert!(sh(&changed, &env, "bash create-subnet.sh").0);
            assert!(report(&changed).passed);
        }));
        changed.cleanup_cloud().unwrap();
        if let Err(p) = outcome { std::panic::resume_unwind(p); }

        let mut spec = cloud(CloudGoal::ChooseSubnet, "10.91.0.0/16");
        spec.subnets = vec![subnet("A", "10.91.1.0/24")];
        spec.new_prefix = Some(24);
        let choose = GitPractice::new(exercise(spec, &[])).unwrap();
        owned.push(owner(choose.root()));
        let env = choose.prepare_cloud().unwrap();
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            assert!(env.iter().any(|(k, _)| k == "LAB_SUBNET_A_ID"));
            assert!(!report(&choose).passed);
            assert!(!sh(&choose, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.1.128/25").0, "overlap rejected");
            assert!(sh(&choose, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.7.0/24").0);
            assert!(report(&choose).passed, "any free /24 preserving A");
            assert!(sh(&choose, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.8.0/26").0);
            assert!(!report(&choose).passed, "a second new subnet");
            assert!(sh(&choose, &env, "id=$(aws ec2 describe-subnets --filters Name=cidr-block,Values=10.91.8.0/26 --query 'Subnets[0].SubnetId' --output text | tr -d '\\r') && aws ec2 delete-subnet --subnet-id \"$id\" && aws ec2 delete-subnet --subnet-id \"$LAB_SUBNET_A_ID\"").0);
            assert!(!report(&choose).passed, "prepared subnet must stay");
        }));
        choose.cleanup_cloud().unwrap();
        if let Err(p) = outcome { std::panic::resume_unwind(p); }
        println!("PASS changed fixture 10.73 and choose-subnet goal");
    });
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine; creates one foreign-labelled stand-in and only labelled resources"]
fn docker_cloud_refuses_foreign_resources() {
    guarded("foreign", |owned| {
        let practice = GitPractice::new(representative("10.91.0.0/16", "10.91.2.0/24", "10.92.2.0/24")).unwrap();
        owned.push(owner(practice.root()));
        let (network, container, _) = names(practice.root());
        let foreign = format!("{LABEL}=foreign-{}", std::process::id());
        require(&["create", "--name", &container, "--label", &foreign, "alpine:3.22", "true"], 60).unwrap();
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            assert!(practice.prepare_cloud().is_err(), "name taken by a foreign container");
            assert!(!practice.root().join(STATE_FILE).exists(), "failed preparation cleaned its own state");
            assert!(!docker(&["network", "inspect", &network], 15).unwrap().ok, "failed preparation removed its own network");
            practice.cleanup_cloud().unwrap();
            let label = require(&["inspect", "--format", &format!("{{{{index .Config.Labels \"{LABEL}\"}}}}"), &container], 15).unwrap();
            assert_eq!(label.trim(), foreign.split_once('=').unwrap().1, "foreign container untouched");
        }));
        // Test-owned stand-in: removed only after re-checking its exact foreign label.
        let label = require(&["inspect", "--format", &format!("{{{{index .Config.Labels \"{LABEL}\"}}}}"), &container], 15).unwrap();
        if label.trim() == foreign.split_once('=').unwrap().1 {
            require(&["rm", &container], 30).unwrap();
        }
        if let Err(p) = outcome { std::panic::resume_unwind(p); }
        println!("PASS foreign-labelled resource refused and preserved; partial owned network cleaned");
    });
}

fn launch_spec() -> GitExercise {
    let mut spec = cloud(CloudGoal::LaunchServer, "10.91.0.0/16");
    spec.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("B", "10.91.2.0/24")];
    spec.target_subnet = Some("B".into());
    exercise(spec, &[("launch-server.sh", "# 준비된 서버 이미지로 서버 한 대를 실행해요.\naws ec2 run-instances \\\n  --image-id \"$LAB_SERVER_AMI\" \\\n  --instance-type t3.micro \\\n  --subnet-id \"$LAB_SUBNET_A_ID\" \\\n  --user-data file://server-user-data.sh\n")])
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs privileged Docker-in-Docker with real Java 25 EC2 guests"]
fn docker_cloud_guest_wrong_placement_reset_and_correct() {
    guarded("guest-launch", |owned| {
        let directory = tempfile::tempdir().unwrap();
        let store = GitPracticeStore::new(directory.path()).unwrap();
        let spec = launch_spec();
        let first = store.open("cloud-launch", spec.clone()).unwrap();
        owned.push(owner(first.root()));
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let env = first.prepare_cloud().unwrap();
            assert!(!report(&first).passed);
            assert!(sh(&first, &env, "bash launch-server.sh > /dev/null").0);
            let wrong = report(&first);
            assert!(!wrong.passed && wrong.cases.iter().any(|c| c.stdout.contains("목표 서브넷이 아닌 곳")), "wrong subnet placement");
        }));
        if let Err(p) = outcome { let _ = first.cleanup_cloud(); std::panic::resume_unwind(p); }
        let second = store.reset_step("cloud-launch", spec, "cloud-step").unwrap();
        owned.push(owner(second.root()));
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            assert!(!docker(&["inspect", &names(first.root()).1], 15).unwrap().ok, "reset removed the old runtime");
            let env = second.prepare_cloud().unwrap();
            assert!(!report(&second).passed, "reset gives a fresh state without the wrong server");
            let script = std::fs::read_to_string(second.work().join("launch-server.sh")).unwrap().replace("LAB_SUBNET_A_ID", "LAB_SUBNET_B_ID");
            std::fs::write(second.work().join("launch-server.sh"), script).unwrap();
            assert!(sh(&second, &env, "bash launch-server.sh > /dev/null").0);
            assert!(report(&second).passed, "corrected placement");
        }));
        let _ = first.cleanup_cloud();
        second.cleanup_cloud().unwrap();
        if let Err(p) = outcome { std::panic::resume_unwind(p); }
        println!("PASS guest launch: subnet A fails, reset gives fresh runtime, subnet B passes");
    });
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs privileged Docker-in-Docker with real Java 25 EC2 guests"]
fn docker_cloud_guest_request_uses_api_private_address() {
    guarded("guest-request", |owned| {
        let mut spec = cloud(CloudGoal::RequestServer, "10.91.0.0/16");
        spec.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("B", "10.91.2.0/24")];
        spec.client_subnet = Some("A".into());
        spec.server_subnet = Some("B".into());
        spec.address_file = Some("server-address.txt".into());
        let practice = GitPractice::new(exercise(spec, &[("server-address.txt", "10.91.2.99\n")])).unwrap();
        owned.push(owner(practice.root()));
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let env = practice.prepare_cloud().unwrap();
            let state = load(practice.root()).unwrap();
            assert!(!report(&practice).passed, "placeholder address");
            // A Docker address of the same server that the API never reported.
            let (_, runtime, _) = names(practice.root());
            let server = guest_container(&runtime, &state.server.as_ref().unwrap().id).unwrap().unwrap();
            let other = server["NetworkSettings"]["Networks"].as_object().unwrap().values()
                .filter_map(|n| n["IPAddress"].as_str()).find(|ip| !ip.is_empty() && *ip != state.server.as_ref().unwrap().ip).unwrap().to_string();
            std::fs::write(practice.work().join("server-address.txt"), format!("{other}\n")).unwrap();
            sh(&practice, &env, &format!("client-request {other} | head -3"));
            let bridge = report(&practice);
            assert!(!bridge.passed && bridge.cases.iter().any(|c| c.stdout.contains("API가 알려 준")), "bridge address is not the API private address");
            assert!(sh(&practice, &env, "echo 'HTTP/1.1 200 OK'; echo 'java.version=25'").0);
            assert!(!report(&practice).passed, "printed response is not graded");
            assert!(sh(&practice, &env, "aws ec2 describe-instances --instance-ids \"$LAB_SERVER_ID\" --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text | tr -d '\\r' > server-address.txt").0);
            let (ok, out, _) = sh(&practice, &env, "client-request \"$(cat server-address.txt)\"");
            assert!(ok && out.contains("HTTP/1.1 200 OK") && out.contains("java.version=25"));
            assert!(report(&practice).passed, "API private address answered from the other subnet's client");
        }));
        practice.cleanup_cloud().unwrap();
        if let Err(p) = outcome { std::panic::resume_unwind(p); }
        println!("PASS guest request: placeholder/bridge/printed output fail, API private address passes with grader's own HTTP");
    });
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs privileged Docker-in-Docker with real Java 25 EC2 guests"]
fn docker_cloud_guest_deploy_java_server() {
    guarded("guest-deploy", |owned| {
        let mut spec = cloud(CloudGoal::DeployServer, "10.91.0.0/16");
        spec.subnets = vec![subnet("A", "10.91.1.0/24")];
        spec.client_subnet = Some("A".into());
        spec.target_cidr = Some("10.91.2.0/24".into());
        spec.address_file = Some("server-address.txt".into());
        let practice = GitPractice::new(exercise(spec, &[("server-address.txt", "0.0.0.0\n")])).unwrap();
        owned.push(owner(practice.root()));
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let env = practice.prepare_cloud().unwrap();
            assert!(!report(&practice).passed);
            let launch = |subnet: &str| format!("aws ec2 run-instances --image-id \"$LAB_SERVER_AMI\" --instance-type t3.micro --subnet-id {subnet} --user-data file://server-user-data.sh --query 'Instances[0].PrivateIpAddress' --output text | tr -d '\\r' > server-address.txt");
            assert!(sh(&practice, &env, "aws ec2 create-subnet --vpc-id \"$LAB_VPC_ID\" --cidr-block 10.91.2.0/24 > /dev/null").0);
            assert!(sh(&practice, &env, &launch("\"$LAB_SUBNET_A_ID\"")).0);
            let wrong = report(&practice);
            assert!(!wrong.passed && wrong.cases.iter().any(|c| c.stdout.contains("목표 서브넷이 아닌 곳")), "server in the client's subnet");
            assert!(sh(&practice, &env, "aws ec2 terminate-instances --instance-ids $(aws ec2 describe-instances --filters Name=subnet-id,Values=\"$LAB_SUBNET_A_ID\" Name=instance-state-name,Values=running --query \"Reservations[].Instances[?InstanceId!='$LAB_CLIENT_ID'].InstanceId\" --output text | tr -d '\\r') > /dev/null").0);
            let b = "\"$(aws ec2 describe-subnets --filters Name=vpc-id,Values=\"$LAB_VPC_ID\" Name=cidr-block,Values=10.91.2.0/24 --query 'Subnets[0].SubnetId' --output text | tr -d '\\r')\"";
            assert!(sh(&practice, &env, &launch(b)).0);
            let done = report(&practice);
            assert!(done.passed, "created subnet + Java server + HTTP from subnet A");
            let http = done.cases.iter().find(|c| c.input == "다른 서브넷에서 받은 응답").unwrap();
            assert!(http.stdout.contains("served-on=10.91.2.") && http.stdout.contains("from=10.91.1.") && http.stdout.contains("java.version=25"));
        }));
        practice.cleanup_cloud().unwrap();
        if let Err(p) = outcome { std::panic::resume_unwind(p); }
        println!("PASS guest deploy: wrong subnet fails, target subnet Java 25 server answers the client in subnet A");
    });
}

/// A cached pinned image copied into a fresh owned nested engine without any inner pull, then
/// accepted only by the same provenance check preparation uses.
#[test]
#[ignore = "Requires Docker Desktop Linux engine and the cached pinned Temurin image; runs one owned privileged Docker-in-Docker"]
fn docker_cloud_transfer_cached_image_and_verify_provenance() {
    guarded("transfer", |owned| {
        let tag = format!("transfer-test-{}", std::process::id());
        owned.push(tag.clone());
        let label = format!("{LABEL}={tag}");
        let (container, volume) = (format!("mq-cloud-{tag}-runtime"), format!("mq-cloud-{tag}-docker"));
        require(&["image", "inspect", TEMURIN], 30).expect("pinned Temurin must be cached on the host for this test");
        require(&["volume", "create", "--label", &label, &volume], 30).unwrap();
        require(&["run", "-d", "--name", &container, "--label", &label, "--privileged", "--network", "none",
            "-v", &format!("{volume}:/var/lib/docker"), "--entrypoint", "dockerd", DIND,
            "--host=unix:///var/run/docker.sock", "--storage-driver=overlay2"], 300).unwrap();
        assert!(wait(90, || Ok(inner(&container, &["info"], 20)?.ok.then_some(()))).unwrap().is_some());
        assert!(inner_ok(&container, &["images", "-q"], 30).unwrap().trim().is_empty(), "fresh engine has no images");
        // --network none: the nested engine cannot reach a registry, so only the archive can supply the image.
        let started = Instant::now();
        let loaded = transfer_image(&container, TEMURIN).unwrap();
        println!("  transfer {:?}: {}", started.elapsed(), loaded.trim());
        let digests = inner(&container, &["image", "inspect", "--format", "{{json .RepoDigests}}", TEMURIN], 30).unwrap();
        println!("  digest reference after load: ok={} {}{}", digests.ok, digests.out.trim(), digests.err.trim());
        let reference = transferred_reference(&container, TEMURIN, &loaded).unwrap();
        println!("  verified reference: {reference}");
        let arch = inner_ok(&container, &["image", "inspect", "--format", "{{.Architecture}}", &reference], 30).unwrap();
        assert!(ami_architecture(arch.trim()).is_some());
        // The verified reference is usable the way preparation uses it (Dockerfile FROM), offline.
        let probe = inner(&container, &["run", "--rm", "--network", "none", &reference, "java", "-version"], 120).unwrap();
        assert!(probe.ok && probe.err.contains("version \"25"), "{}", probe.err);
        // A different cached image must not pass as the pinned one.
        assert!(transferred_reference(&container, FLOCI, &loaded).is_err(), "provenance must not accept another image");
        println!("PASS transfer: archive load into an offline nested engine, provenance by measured content, Java 25 runs");
    });
}

/// A failed sink returns promptly and leaves no producer behind.
#[test]
#[ignore = "Requires Docker Desktop Linux engine and the cached pinned Temurin image; creates no resources"]
fn docker_cloud_transfer_failure_reaps_both_processes() {
    guarded("transfer-failure", |_| {
        let missing = format!("mq-cloud-missing-{}", std::process::id());
        let started = Instant::now();
        assert!(transfer_image_within(&missing, TEMURIN, Duration::from_secs(120)).is_err());
        assert!(started.elapsed() < Duration::from_secs(60), "failure path took {:?}", started.elapsed());
        println!("PASS transfer failure: returned Err in {:?} with both processes reaped", started.elapsed());
    });
}

// -- The published first cloud lesson, step by step, through the submission path ----------------
const LESSON: &str = "courses/redesigned/cloud-vpc-subnet-ec2.json";
/// The create-subnet command learners type (no prepared file since revision -3).
fn create(block: &str) -> String {
    format!("aws ec2 create-subnet --endpoint-url \"$LAB_ENDPOINT\" --vpc-id \"$LAB_VPC_ID\" --cidr-block {block}")
}
struct LessonStep { id: String, title: String, exercise: GitExercise, narration: Vec<Value> }
fn lesson_steps() -> Vec<LessonStep> {
    let raw = std::fs::read(Path::new(env!("CARGO_MANIFEST_DIR")).join(LESSON)).expect("build the lesson first");
    let lesson: Value = serde_json::from_slice(&raw).unwrap();
    lesson["tasks"].as_array().unwrap().iter().map(|t| LessonStep {
        id: t["id"].as_str().unwrap().into(), title: t["title"].as_str().unwrap().into(),
        exercise: serde_json::from_value(t["git_terminal"].clone()).unwrap(),
        narration: t["narration"].as_array().unwrap().clone(),
    }).collect()
}
fn edit(practice: &GitPractice, file: &str, before: &str, after: &str) {
    let path = practice.work().join(file);
    let text = std::fs::read_to_string(&path).unwrap();
    assert_eq!(text.matches(before).count(), 1, "{file}: {before}");
    std::fs::write(&path, text.replacen(before, after, 1)).unwrap();
}
/// Replay the narration's editor patches and terminal commands, as auto-review does, and keep
/// every command's real output as evidence. A command marked `fails` must fail; others succeed.
fn replay(practice: &GitPractice, env: &[(String, String)], step: &LessonStep, lane: &str) -> Vec<String> {
    let mut outputs = vec![];
    for (index, action) in step.narration.iter().enumerate() {
        match action["action"].as_str() {
            Some("patch_code") => edit(practice, action["file"].as_str().unwrap(), action["before"].as_str().unwrap(), action["after"].as_str().unwrap()),
            Some("bash_command") => {
                let command = action["command"].as_str().unwrap();
                let (ok, out, err) = sh(practice, env, command);
                let text = format!("$ {command}\n{out}{err}");
                std::fs::write(evidence_dir().join(format!("lesson-{}-{lane}-{index:02}.txt", &step.id[4..12])), &text).unwrap();
                assert_eq!(ok, !action["fails"].as_bool().unwrap_or(false), "{}: {text}", step.title);
                outputs.push(text);
            }
            _ => {}
        }
    }
    outputs
}
fn has(outputs: &[String], index: usize, wanted: &[&str]) {
    for w in wanted {
        assert!(outputs[index].contains(w), "narration command {index} should show {w:?}: {}", outputs[index]);
    }
}
fn feedback(report: &crate::runner::TestReport, wanted: &str) -> bool {
    report.cases.iter().any(|c| !c.passed && c.stdout.contains(wanted))
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine, and Git Bash; runs the published lesson's subnet steps"]
fn docker_cloud_lesson_subnet_steps() {
    let steps = lesson_steps();
    assert_eq!(steps.len(), 7);
    guarded("lesson-subnets", |owned| {
        let open = |owned: &mut Vec<String>, spec: GitExercise| {
            let p = GitPractice::new(spec).unwrap();
            owned.push(owner(p.root()));
            let env = p.prepare_cloud().unwrap();
            (p, env)
        };
        // 1: a run task. The start state fails; the prepared command makes it pass.
        let (p, env) = open(owned, steps[0].exercise.clone());
        assert!(!report(&p).passed, "step 1 initial");
        let out = replay(&p, &env, &steps[0], "student");
        has(&out, 0, &["\"CidrBlock\": \"10.91.0.0/16\""]);
        has(&out, 1, &["\"Subnets\": []"]);
        has(&out, 2, &["\"CidrBlock\": \"10.91.1.0/24\""]);
        assert!(report(&p).passed, "step 1 after the prepared command");
        p.cleanup_cloud().unwrap();

        // 2 (representative): starter refused, printed success is not state, the narration's fix passes.
        let (p, env) = open(owned, steps[1].exercise.clone());
        assert!(!report(&p).passed, "step 2 initial");
        let (ok, _, err) = sh(&p, &env, &create("10.92.2.0/24"));
        assert!(!ok && err.contains("InvalidSubnet.Range"));
        assert!(sh(&p, &env, r#"echo '{"Subnet":{"CidrBlock":"10.91.2.0/24","State":"available"}}'"#).0);
        assert!(!report(&p).passed, "step 2 printed success");
        // The explanation lane: its own resources; the student's files and state stay as they were.
        let teacher = GitPractice::new(steps[1].exercise.demonstration()).unwrap();
        owned.push(owner(teacher.root()));
        let teacher_env = teacher.prepare_cloud().unwrap();
        let out = replay(&teacher, &teacher_env, &steps[1], "demo");
        has(&out, 0, &["InvalidSubnet.Range"]);
        has(&out, 1, &["\"Subnets\": []"]);
        has(&out, 2, &["\"CidrBlock\": \"10.91.2.0/24\""]);
        assert!(teacher.check_exercise().unwrap().passed, "step 2 narration reaches the goal");
        teacher.release_network_demo();
        assert!(!report(&p).passed, "the demonstration did not change the student");
        replay(&p, &env, &steps[1], "student");
        assert!(report(&p).passed, "step 2 one-line fix");
        p.cleanup_cloud().unwrap();
        // Changed fixture: the same step with another VPC.
        let mut changed = steps[1].exercise.clone();
        let cloud = changed.cloud.as_mut().unwrap();
        cloud.vpc_cidr = "10.73.0.0/16".into();
        cloud.target_cidr = Some("10.73.2.0/24".into());
        let (p, env) = open(owned, changed);
        assert!(!sh(&p, &env, &create("10.74.2.0/24")).0);
        assert!(!sh(&p, &env, &create("10.91.2.0/24")).0, "the default answer is outside the changed VPC");
        assert!(!report(&p).passed);
        assert!(sh(&p, &env, &create("10.73.2.0/24")).0);
        assert!(report(&p).passed, "step 2 changed fixture");
        p.cleanup_cloud().unwrap();

        // 3: any free /25 passes; overlap is refused; another size fails.
        let (p, env) = open(owned, steps[2].exercise.clone());
        assert!(!report(&p).passed, "step 3 initial");
        let (ok, _, err) = sh(&p, &env, &create("10.91.1.128/25"));
        assert!(!ok && err.contains("InvalidSubnet.Conflict"), "overlap refused: {err}");
        assert!(sh(&p, &env, &create("10.91.2.0/24")).0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "/25 크기가 아니에요"), "step 3 a /24");
        p.cleanup_cloud().unwrap();
        let (p, env) = open(owned, steps[2].exercise.clone());
        let out = replay(&p, &env, &steps[2], "student");
        has(&out, 0, &["\"CidrBlock\": \"10.91.1.0/24\""]);
        has(&out, 1, &["InvalidSubnet.Conflict"]);
        has(&out, 2, &["\"CidrBlock\": \"10.91.2.0/25\""]);
        assert!(report(&p).passed, "step 3 narration");
        p.cleanup_cloud().unwrap();
        let (p, env) = open(owned, steps[2].exercise.clone());
        assert!(sh(&p, &env, &create("10.91.3.0/25")).0);
        assert!(report(&p).passed, "step 3 another free /25");
        p.cleanup_cloud().unwrap();
        println!("PASS lesson subnet steps 1-3");
    });
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs privileged Docker-in-Docker with real Java 25 EC2 guests for the published lesson"]
fn docker_cloud_lesson_server_steps() {
    let steps = lesson_steps();
    guarded("lesson-servers", |owned| {
        let directory = tempfile::tempdir().unwrap();
        let store = GitPracticeStore::new(directory.path()).unwrap();
        let open = |owned: &mut Vec<String>, scope: &str, spec: GitExercise| {
            let p = store.open(scope, spec).unwrap();
            owned.push(owner(p.root()));
            let env = p.prepare_cloud().unwrap();
            (p, env)
        };
        let reset = |owned: &mut Vec<String>, scope: &str, step: &LessonStep| {
            let p = store.reset_step(scope, step.exercise.clone(), &step.id).unwrap();
            owned.push(owner(p.root()));
            let env = p.prepare_cloud().unwrap();
            (p, env)
        };
        // 4: a run task on a real guest.
        let (p, env) = open(owned, "step4", steps[3].exercise.clone());
        assert!(!report(&p).passed, "step 4 initial");
        let out = replay(&p, &env, &steps[3], "student");
        has(&out, 0, &["\"PrivateIpAddress\": \"10.91.2."]);
        has(&out, 3, &["10.91.2.", "running"]);
        assert!(report(&p).passed, "step 4 prepared command");
        p.cleanup_cloud().unwrap();

        // 5: the starter places the server in A; a second server in B is still wrong; 초기화 then the fix.
        let (p, env) = open(owned, "step5", steps[4].exercise.clone());
        assert!(sh(&p, &env, "bash launch-server.sh > /dev/null").0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "목표 서브넷이 아닌 곳"), "step 5 starter in A");
        let (_, table, _) = sh(&p, &env, "bash list-servers.sh");
        assert!(table.contains("10.91.1."), "the learner can see the A address: {table}");
        edit(&p, "launch-server.sh", "\"$LAB_SUBNET_A_ID\"", "\"$LAB_SUBNET_B_ID\"");
        assert!(sh(&p, &env, "bash launch-server.sh > /dev/null").0);
        let two = report(&p);
        assert!(!two.passed && feedback(&two, "서버가 2대예요"), "step 5 A left behind");
        let (p2, env2) = reset(owned, "step5", &steps[4]);
        assert!(!docker(&["inspect", &names(p.root()).1], 15).unwrap().ok, "초기화 removed the old runtime");
        assert!(std::fs::read_to_string(p2.work().join("launch-server.sh")).unwrap().contains("\"$LAB_SUBNET_A_ID\""), "prepared file restored");
        assert!(!report(&p2).passed, "step 5 after 초기화");
        let out = replay(&p2, &env2, &steps[4], "student");
        has(&out, 0, &["10.91.1.0/24", "10.91.2.0/24"]);
        has(&out, 1, &["\"PrivateIpAddress\": \"10.91.2."]);
        assert!(report(&p2).passed, "step 5 narration");
        p2.cleanup_cloud().unwrap();

        // 6: placeholder and printed output fail; the API private address passes the grader's own request.
        let (p, env) = open(owned, "step6", steps[5].exercise.clone());
        assert!(!report(&p).passed, "step 6 placeholder");
        assert!(sh(&p, &env, "echo 'HTTP/1.1 200 OK'; echo 'from=10.91.1.10'").0);
        assert!(!report(&p).passed, "step 6 printed response");
        let out = replay(&p, &env, &steps[5], "student");
        has(&out, 0, &["CONNECT_FAIL"]);
        has(&out, 4, &["HTTP/1.1 200 OK", "served-on=10.91.2.", "from=10.91.1.", "java.version=25"]);
        assert!(report(&p).passed, "step 6 narration");
        p.cleanup_cloud().unwrap();

        // 7: a server left in the client's subnet fails; after 초기화 the narration passes with real HTTP.
        let (p, env) = open(owned, "step7", steps[6].exercise.clone());
        assert!(!report(&p).passed, "step 7 initial");
        assert!(!sh(&p, &env, &create("10.91.1.0/24")).0, "an overlapping subnet is refused");
        assert!(sh(&p, &env, &format!("{} > /dev/null", create("10.91.2.0/24"))).0);
        assert!(sh(&p, &env, "bash launch-server.sh > /dev/null").0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "목표 서브넷이 아닌 곳"), "step 7 server in A");
        let (p2, env2) = reset(owned, "step7", &steps[6]);
        let out = replay(&p2, &env2, &steps[6], "student");
        has(&out, 0, &["\"CidrBlock\": \"10.91.2.0/24\""]);
        has(&out, 1, &["\"PrivateIpAddress\": \"10.91.2."]);
        has(&out, 5, &["HTTP/1.1 200 OK", "served-on=10.91.2.", "from=10.91.1."]);
        assert!(report(&p2).passed, "step 7 narration");
        p2.cleanup_cloud().unwrap();
        println!("PASS lesson server steps 4-7");
    });
}

/// Step 6's explanation lane while the learner's own runtime of that step is running, as in the player.
#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs two privileged Docker-in-Docker runtimes with Java guests"]
fn docker_cloud_lesson_request_demo_beside_student() {
    let steps = lesson_steps();
    guarded("lesson-request-demo", |owned| {
        let student = GitPractice::new(steps[5].exercise.clone()).unwrap();
        owned.push(owner(student.root()));
        let started = Instant::now();
        student.prepare_cloud().unwrap();
        println!("  student ready in {:?}", started.elapsed());
        let teacher = GitPractice::new(steps[5].exercise.demonstration()).unwrap();
        owned.push(owner(teacher.root()));
        let started = Instant::now();
        let prepared = teacher.prepare_cloud();
        println!("  teacher prepare in {:?}: {:?}", started.elapsed(), prepared.as_ref().map(|_| "ok"));
        let env = prepared.unwrap();
        let out = replay(&teacher, &env, &steps[5], "demo-beside");
        has(&out, 4, &["HTTP/1.1 200 OK"]);
        assert!(teacher.check_exercise().unwrap().passed);
        teacher.release_network_demo();
        student.cleanup_cloud().unwrap();
    });
}

/// Preflight for the lifecycle lesson (measurement only, prints observations).
#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs privileged Docker-in-Docker with real Java 25 EC2 guests"]
fn docker_cloud_lifecycle_preflight() {
    guarded("lifecycle-preflight", |owned| {
        let mut spec = cloud(CloudGoal::RequestServer, "10.91.0.0/16");
        spec.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("B", "10.91.2.0/24")];
        spec.client_subnet = Some("A".into());
        spec.server_subnet = Some("B".into());
        spec.address_file = Some("server-address.txt".into());
        let practice = GitPractice::new(exercise(spec, &[("server-address.txt", "10.91.2.99\n")])).unwrap();
        owned.push(owner(practice.root()));
        let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let env = practice.prepare_cloud().unwrap();
            let (_, runtime, _) = names(practice.root());
            let id = load(practice.root()).unwrap().server.unwrap().id;
            let state = "aws ec2 describe-instances --instance-ids \"$LAB_SERVER_ID\" --query 'Reservations[0].Instances[0].[State.Name,PrivateIpAddress,SubnetId]' --output text";
            let poll = |want: &str| format!("for i in $(seq 1 60); do s=$({state} | tr -d '\r'); case \"$s\" in {want}*) echo \"after ${{i}}x2s: $s\"; break;; esac; sleep 2; done; {state}");
            let guest = |label: &str| {
                let c = guest_container(&runtime, &id).unwrap();
                println!("  [guest {label}] {}", c.map(|v| format!("running={} ips={:?}", v["State"]["Running"], v["NetworkSettings"]["Networks"].as_object().map(|n| n.values().map(|x| x["IPAddress"].clone()).collect::<Vec<_>>()))).unwrap_or("absent".into()));
            };
            sh(&practice, &env, &format!("{state}; client-request \"$({state} | awk '{{print $2}}' | tr -d '\r')\" | head -1"));
            guest("initial");
            sh(&practice, &env, "aws ec2 delete-subnet --subnet-id \"$LAB_SUBNET_B_ID\"");
            sh(&practice, &env, "aws ec2 delete-vpc --vpc-id \"$LAB_VPC_ID\"");
            sh(&practice, &env, "aws ec2 stop-instances --instance-ids \"$LAB_SERVER_ID\" --query 'StoppingInstances[0].[PreviousState.Name,CurrentState.Name]' --output text");
            sh(&practice, &env, &poll("stopped"));
            guest("stopped");
            sh(&practice, &env, &format!("client-request \"$({state} | awk '{{print $2}}' | tr -d '\r')\" | head -1"));
            sh(&practice, &env, "aws ec2 delete-subnet --subnet-id \"$LAB_SUBNET_B_ID\"");
            sh(&practice, &env, "aws ec2 start-instances --instance-ids \"$LAB_SERVER_ID\" --query 'StartingInstances[0].[PreviousState.Name,CurrentState.Name]' --output text");
            sh(&practice, &env, &poll("running"));
            guest("restarted");
            sh(&practice, &env, &format!("ip=$({state} | awk '{{print $2}}' | tr -d '\r'); for i in $(seq 1 45); do if client-request \"$ip\" 2>/dev/null | head -1 | grep -q 200; then echo \"answered after ${{i}}x2s\"; break; fi; sleep 2; done; client-request \"$ip\" | head -1"));
            sh(&practice, &env, "aws ec2 reboot-instances --instance-ids \"$LAB_SERVER_ID\"; sleep 5");
            sh(&practice, &env, &format!("{state}; ip=$({state} | awk '{{print $2}}' | tr -d '\r'); for i in $(seq 1 45); do if client-request \"$ip\" 2>/dev/null | head -1 | grep -q 200; then echo \"answered after ${{i}}x2s\"; break; fi; sleep 2; done"));
            guest("rebooted");
            sh(&practice, &env, "aws ec2 terminate-instances --instance-ids \"$LAB_SERVER_ID\" --query 'TerminatingInstances[0].[PreviousState.Name,CurrentState.Name]' --output text");
            sh(&practice, &env, &poll("terminated"));
            guest("terminated");
            sh(&practice, &env, "aws ec2 start-instances --instance-ids \"$LAB_SERVER_ID\"");
            sh(&practice, &env, "sleep 20; aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name]' --output text");
            sh(&practice, &env, "aws ec2 delete-subnet --subnet-id \"$LAB_SUBNET_B_ID\" && echo deleted-B");
            sh(&practice, &env, "aws ec2 describe-subnets --filters Name=vpc-id,Values=\"$LAB_VPC_ID\" --query 'Subnets[].CidrBlock' --output text");
            sh(&practice, &env, "aws ec2 delete-vpc --vpc-id \"$LAB_VPC_ID\"");
            sh(&practice, &env, "aws ec2 terminate-instances --instance-ids \"$LAB_CLIENT_ID\" > /dev/null; for i in $(seq 1 60); do s=$(aws ec2 describe-instances --instance-ids \"$LAB_CLIENT_ID\" --query 'Reservations[0].Instances[0].State.Name' --output text | tr -d '\r'); [ \"$s\" = terminated ] && break; sleep 2; done; echo client=$s; aws ec2 delete-subnet --subnet-id \"$LAB_SUBNET_A_ID\" && echo deleted-A; aws ec2 delete-vpc --vpc-id \"$LAB_VPC_ID\" && echo deleted-vpc");
            println!("  report after teardown: passed={}", report(&practice).passed);
        }));
        let _ = practice.cleanup_cloud();
        if let Err(p) = outcome { std::panic::resume_unwind(p); }
    });
}

#[test]
fn lifecycle_goals_need_a_client_and_a_server_in_two_subnets() {
    let base = |goal| {
        let mut spec = cloud(goal, "10.91.0.0/16");
        spec.subnets = vec![subnet("A", "10.91.1.0/24"), subnet("B", "10.91.2.0/24")];
        spec.client_subnet = Some("A".into());
        spec.server_subnet = Some("B".into());
        spec
    };
    for goal in [CloudGoal::StopServer, CloudGoal::StartServer, CloudGoal::TerminateServer, CloudGoal::DeleteVpc] {
        assert!(goal.lifecycle() && base(goal).guest());
        assert!(base(goal).validate().is_ok(), "{goal:?}");
        let mut same = base(goal);
        same.server_subnet = Some("A".into());
        assert!(same.validate().is_err(), "{goal:?} client and server share a subnet");
        let mut address = base(goal);
        address.address_file = Some("server-address.txt".into());
        assert!(address.validate().is_err(), "{goal:?} has no address file");
        let mut target = base(goal);
        target.target_subnet = Some("B".into());
        assert!(target.validate().is_err(), "{goal:?} has no target subnet");
    }
    let mut delete = base(CloudGoal::DeleteSubnet);
    assert!(delete.validate().is_err(), "delete_subnet names its target");
    delete.target_subnet = Some("A".into());
    assert!(delete.validate().is_err(), "the target is the server's subnet");
    delete.target_subnet = Some("B".into());
    assert!(delete.validate().is_ok());
    assert!(!CloudGoal::RequestServer.lifecycle() && !CloudGoal::CreateSubnet.lifecycle());
    let parsed: CloudExercise = serde_json::from_value(serde_json::json!({"goal": "delete_vpc", "vpc_cidr": "10.91.0.0/16",
        "subnets": [{"name": "A", "cidr": "10.91.1.0/24"}, {"name": "B", "cidr": "10.91.2.0/24"}], "client_subnet": "A", "server_subnet": "B"})).unwrap();
    assert_eq!(parsed.goal, CloudGoal::DeleteVpc);
}

const LIFECYCLE_LESSON: &str = "courses/redesigned/cloud-ec2-lifecycle.json";
fn lifecycle_steps() -> Vec<LessonStep> {
    let raw = std::fs::read(Path::new(env!("CARGO_MANIFEST_DIR")).join(LIFECYCLE_LESSON)).expect("build the lesson first");
    let lesson: Value = serde_json::from_slice(&raw).unwrap();
    assert_eq!(lesson["schema_version"], 4);
    lesson["tasks"].as_array().unwrap().iter().map(|t| LessonStep {
        id: t["id"].as_str().unwrap().into(), title: t["title"].as_str().unwrap().into(),
        exercise: serde_json::from_value(t["git_terminal"].clone()).unwrap(),
        narration: t["narration"].as_array().unwrap().clone(),
    }).collect()
}
fn ec2(verb_and_options: &str) -> String {
    let (verb, options) = verb_and_options.split_once(' ').unwrap();
    format!("aws ec2 {verb} --endpoint-url \"$LAB_ENDPOINT\" {options}")
}

#[test]
#[ignore = "Requires Docker Desktop Linux engine; runs privileged Docker-in-Docker with real Java 25 EC2 guests for the lifecycle lesson"]
fn docker_cloud_lifecycle_lesson_steps() {
    let steps = lifecycle_steps();
    assert_eq!(steps.len(), 6);
    guarded("lifecycle-lesson", |owned| {
        let directory = tempfile::tempdir().unwrap();
        let store = GitPracticeStore::new(directory.path()).unwrap();
        let open = |owned: &mut Vec<String>, scope: &str, step: &LessonStep| {
            let p = store.open(scope, step.exercise.clone()).unwrap();
            owned.push(owner(p.root()));
            let env = p.prepare_cloud().unwrap();
            (p, env)
        };
        let reset = |owned: &mut Vec<String>, scope: &str, step: &LessonStep| {
            let p = store.reset_step(scope, step.exercise.clone(), &step.id).unwrap();
            owned.push(owner(p.root()));
            let env = p.prepare_cloud().unwrap();
            (p, env)
        };
        let server = |state: &str| ec2(&format!("wait instance-{state} --instance-ids \"$LAB_SERVER_ID\""));

        // 1: terminating instead of stopping fails; after 초기화 the narration stops the server.
        let (p, env) = open(owned, "s1", &steps[0]);
        assert!(!report(&p).passed, "step 1 initial");
        assert!(sh(&p, &env, &ec2("terminate-instances --instance-ids \"$LAB_SERVER_ID\"")).0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "종료됐어요"), "step 1 terminated");
        let (p, env) = reset(owned, "s1", &steps[0]);
        assert!(!report(&p).passed, "step 1 after 초기화");
        let out = replay(&p, &env, &steps[0], "student");
        has(&out, 0, &["HTTP/1.1 200 OK", "java.version=25"]);
        has(&out, 1, &["running", "stopping"]);
        has(&out, 3, &["stopped", "10.91.2."]);
        has(&out, 4, &["CONNECT_FAIL"]);
        assert!(report(&p).passed, "step 1 narration");
        p.cleanup_cloud().unwrap();

        // 2: prepared stopped; start keeps the address, the program does not come back.
        let (p, env) = open(owned, "s2", &steps[1]);
        let ip = env.iter().find(|(k, _)| k == "LAB_SERVER_IP").unwrap().1.clone();
        assert!(!report(&p).passed, "step 2 initial (stopped)");
        let out = replay(&p, &env, &steps[1], "student");
        has(&out, 0, &["stopped", &ip]);
        has(&out, 1, &["stopped", "pending"]);
        has(&out, 3, &["running", &ip]);
        has(&out, 4, &["CONNECT_FAIL"]);
        assert!(report(&p).passed, "step 2 narration");
        p.cleanup_cloud().unwrap();

        // 3: the starter stops the client; 초기화 then the narration stops only the server.
        let (p, env) = open(owned, "s3", &steps[2]);
        assert!(!report(&p).passed, "step 3 initial");
        assert!(sh(&p, &env, &ec2("stop-instances --instance-ids \"$LAB_CLIENT_ID\"")).0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "클라이언트 서버가"), "step 3 starter");
        let (p, env) = reset(owned, "s3", &steps[2]);
        let out = replay(&p, &env, &steps[2], "student");
        has(&out, 1, &["i-"]);
        has(&out, 4, &["stopped", "running"]);
        assert!(report(&p).passed, "step 3 narration");
        p.cleanup_cloud().unwrap();

        // 4: stopping is not terminating; the narration terminates and start is refused.
        let (p, env) = open(owned, "s4", &steps[3]);
        assert!(!report(&p).passed, "step 4 initial");
        assert!(sh(&p, &env, &format!("{} > /dev/null && {}", ec2("stop-instances --instance-ids \"$LAB_SERVER_ID\""), server("stopped"))).0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "멈추기만"), "step 4 stopped only");
        let (p, env) = reset(owned, "s4", &steps[3]);
        let out = replay(&p, &env, &steps[3], "student");
        has(&out, 0, &["running", "shutting-down"]);
        has(&out, 2, &["terminated"]);
        has(&out, 3, &["IncorrectInstanceState"]);
        assert!(report(&p).passed, "step 4 narration");
        p.cleanup_cloud().unwrap();

        // 5 (representative): a stopped server still holds the subnet; printed success is not state.
        let (p, env) = open(owned, "s5", &steps[4]);
        assert!(!report(&p).passed, "step 5 initial");
        assert!(sh(&p, &env, &format!("{} > /dev/null && {}", ec2("stop-instances --instance-ids \"$LAB_SERVER_ID\""), server("stopped"))).0);
        let (ok, _, err) = sh(&p, &env, &ec2("delete-subnet --subnet-id \"$LAB_SUBNET_B_ID\""));
        assert!(!ok && err.contains("DependencyViolation"), "a stopped server blocks the subnet: {err}");
        assert!(sh(&p, &env, "echo 'deleted subnet B'").0);
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "서브넷이 아직 있어요"), "step 5 stopped only");
        let (p, env) = reset(owned, "s5", &steps[4]);
        let out = replay(&p, &env, &steps[4], "student");
        has(&out, 0, &["DependencyViolation"]);
        has(&out, 5, &["10.91.1.0/24"]);
        assert!(!out[5].contains("10.91.2.0/24"), "subnet B is gone: {}", out[5]);
        assert!(report(&p).passed, "step 5 narration");
        p.cleanup_cloud().unwrap();

        // 6: one subnet left keeps the VPC; the narration removes everything in order.
        let (p, env) = open(owned, "s6", &steps[5]);
        assert!(!report(&p).passed, "step 6 initial");
        assert!(sh(&p, &env, &format!("{} > /dev/null && {} && {}", ec2("terminate-instances --instance-ids \"$LAB_SERVER_ID\""),
            server("terminated"), ec2("delete-subnet --subnet-id \"$LAB_SUBNET_B_ID\""))).0);
        let (ok, _, err) = sh(&p, &env, &ec2("delete-vpc --vpc-id \"$LAB_VPC_ID\""));
        assert!(!ok && err.contains("DependencyViolation"), "{err}");
        let wrong = report(&p);
        assert!(!wrong.passed && feedback(&wrong, "VPC가 아직 있어요"), "step 6 half done");
        let (p, env) = reset(owned, "s6", &steps[5]);
        let out = replay(&p, &env, &steps[5], "student");
        has(&out, 0, &["DependencyViolation"]);
        has(&out, 1, &["running"]);
        has(&out, 6, &["\"Subnets\": []"]);
        has(&out, 8, &["InvalidVpcID.NotFound"]);
        assert!(report(&p).passed, "step 6 narration");
        p.cleanup_cloud().unwrap();
        println!("PASS lifecycle lesson steps 1-6");
    });
}
