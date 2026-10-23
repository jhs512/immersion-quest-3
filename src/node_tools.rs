//! Resolve Node and npm together, including GUI sessions with a minimal PATH.
use std::path::{Path, PathBuf};
pub(crate) fn executable() -> PathBuf {
    if let Some(value) = std::env::var_os("MOLIP_NODE").filter(|v| !v.is_empty()) {
        return resolve_on_path(Path::new(&value)).unwrap_or_else(|| value.into());
    }
    for candidate in candidates() {
        if let Some(path) = resolve_on_path(&candidate) {
            return path;
        }
    }
    PathBuf::from(if cfg!(windows) { "node.exe" } else { "node" })
}
fn resolve_on_path(candidate: &Path) -> Option<PathBuf> {
    if candidate.is_absolute() && candidate.is_file() {
        return Some(candidate.to_path_buf());
    }
    if candidate.components().count() != 1 {
        return None;
    }
    std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default())
        .filter(|dir| dir.is_absolute())
        .map(|dir| dir.join(candidate))
        .find(|p| p.is_file())
}
fn candidates() -> Vec<PathBuf> {
    let mut paths = vec![PathBuf::from(if cfg!(windows) {
        "node.exe"
    } else {
        "node"
    })];
    if let Some(home) = std::env::var_os(if cfg!(windows) { "USERPROFILE" } else { "HOME" }) {
        let home = PathBuf::from(home);
        let file = if cfg!(windows) { "node.exe" } else { "node" };
        paths.extend([
            home.join(".volta/bin").join(file),
            home.join(".local/bin").join(file),
        ]);
        // nvm does not put its versions into Finder's PATH. Inspect only known version bins.
        let versions = std::env::var_os("NVM_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(|| home.join(".nvm"))
            .join("versions/node");
        if let Ok(entries) = std::fs::read_dir(versions) {
            let mut bins = entries
                .filter_map(Result::ok)
                .map(|e| e.path().join("bin").join(file))
                .filter(|p| p.is_file())
                .collect::<Vec<_>>();
            bins.sort_by_key(|p| std::cmp::Reverse(version_key(p)));
            paths.extend(bins);
        }
    }
    #[cfg(windows)]
    for key in ["ProgramFiles", "LOCALAPPDATA"] {
        if let Some(root) = std::env::var_os(key) {
            paths.push(PathBuf::from(root).join("nodejs/node.exe"));
        }
    }
    #[cfg(not(windows))]
    paths.extend(["/opt/homebrew/bin/node", "/usr/local/bin/node"].map(PathBuf::from));
    paths
}
fn version_key(path: &Path) -> Vec<u32> {
    path.parent()
        .and_then(Path::parent)
        .and_then(Path::file_name)
        .map(|n| {
            n.to_string_lossy()
                .trim_start_matches('v')
                .split('.')
                .map(|v| v.parse().unwrap_or(0))
                .collect()
        })
        .unwrap_or_default()
}
fn npm_cli(node: &Path) -> Option<PathBuf> {
    let mut roots = vec![node.to_path_buf()];
    if let Ok(real) = node.canonicalize() {
        roots.push(real);
    }
    let mut candidates = Vec::new();
    for node in roots {
        if let Some(bin) = node.parent() {
            candidates.push(bin.join("node_modules/npm/bin/npm-cli.js"));
            candidates.push(bin.join("../lib/node_modules/npm/bin/npm-cli.js"));
            let npm = bin.join("npm");
            if let Ok(real) = npm.canonicalize() {
                if real.file_name().is_some_and(|n| n == "npm-cli.js") {
                    candidates.push(real);
                }
            }
        }
    }
    candidates.into_iter().find(|p| p.is_file())
}
pub(crate) fn command(node: &Path) -> tokio::process::Command {
    let mut command = tokio::process::Command::new(node);
    let mut paths = Vec::new();
    if node.is_absolute() {
        if let Some(parent) = node.parent() {
            paths.push(parent.to_path_buf());
        }
    }
    paths.extend(std::env::split_paths(
        &std::env::var_os("PATH").unwrap_or_default(),
    ));
    if let Ok(path) = std::env::join_paths(paths) {
        command.env("PATH", path);
    }
    // npm/esbuild/Playwright child processes must use this exact executable.
    command
        .env("npm_node_execpath", node)
        .env_remove("NODE_OPTIONS")
        .kill_on_drop(true);
    #[cfg(windows)]
    command.creation_flags(0x08000000);
    command
}
pub(crate) fn npm_command() -> Result<tokio::process::Command, String> {
    let node = executable();
    let cli=npm_cli(&node).ok_or("웹 수업 실행에 Node.js와 npm이 필요해요. 설치한 Node.js 경로를 확인한 뒤 MQ를 다시 여세요.")?;
    let mut command = command(&node);
    command.arg(cli);
    Ok(command)
}
#[cfg(test)]
mod tests {
    #[test]
    fn numeric_versions_sort_newest_first() {
        use std::path::Path;
        assert!(
            super::version_key(Path::new("/v24.10.0/bin/node"))
                > super::version_key(Path::new("/v24.9.0/bin/node"))
        );
    }
}
