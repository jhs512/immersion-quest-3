//! Disposable cross-process data for installed-player validation, never real user data.
use std::{
    path::{Path, PathBuf},
    process::Command,
};
const DIRECTORY_ENV: &str = "MOLIP_PILOT_DIRECTORY";
const OWNER_ENV: &str = "MOLIP_PILOT_OWNER";
const OWNER_FILE: &str = ".mq3-pilot-owner";
const PREFIX: &str = "mq3-player-pilot-installed-";

pub struct PilotSession {
    _directory: tempfile::TempDir,
    path: PathBuf,
    owner: String,
}
impl PilotSession {
    pub fn new() -> Result<Self, String> {
        let directory = tempfile::Builder::new()
            .prefix(PREFIX)
            .tempdir()
            .map_err(|e| e.to_string())?;
        let path = directory.path().canonicalize().map_err(|e| e.to_string())?;
        let owner = crate::issue_progress::new_id();
        std::fs::write(path.join(OWNER_FILE), &owner).map_err(|e| e.to_string())?;
        // Existing native scenarios start as an already registered student.
        // The enrollment scenario removes this fixture before launching.
        crate::course_identity::Store::new(&path.join("course-names.sqlite3")).accept(
            "mq3-validation/course",&crate::course_identity::Enrollment{user_id:987654321,course_id:"crs_3f59e7bd-70c1-4e81-9cb0-000000000001".into(),name:"검증학생".into(),revision:"pilot-name-1".into(),updated_at:1},true)?;
        Ok(Self {
            _directory: directory,
            path,
            owner,
        })
    }
    pub fn directory(&self) -> &Path {
        &self.path
    }
    pub fn configure(&self, command: &mut Command) {
        command
            .env("MOLIP_PILOT", "1")
            .env(DIRECTORY_ENV, &self.path)
            .env(OWNER_ENV, &self.owner);
    }
}
pub fn shared_directory() -> Result<Option<PathBuf>, String> {
    match (std::env::var_os(DIRECTORY_ENV), std::env::var_os(OWNER_ENV)) {
        (None, None) => Ok(None),
        (Some(path), Some(owner)) if crate::pilot_source::enabled() => {
            let path = PathBuf::from(path);
            let owner = owner.to_str().ok_or("검증 소유 코드 오류")?;
            if !path.is_absolute()
                || !path
                    .file_name()
                    .is_some_and(|name| name.to_string_lossy().starts_with(PREFIX))
                || owner.len() != 32
                || !owner.bytes().all(|c| c.is_ascii_hexdigit())
            {
                return Err("검증 폴더의 소유권을 확인하세요.".into());
            }
            let canonical = path.canonicalize().map_err(|e| e.to_string())?;
            if path != canonical
                || std::fs::symlink_metadata(&path)
                    .map_err(|e| e.to_string())?
                    .file_type()
                    .is_symlink()
            {
                return Err("검증 폴더의 경로를 확인하세요.".into());
            }
            let marker = path.join(OWNER_FILE);
            if std::fs::symlink_metadata(&marker)
                .map_err(|e| e.to_string())?
                .file_type()
                .is_symlink()
                || std::fs::read_to_string(marker).map_err(|e| e.to_string())? != owner
            {
                return Err("검증 폴더의 소유 코드가 달라요.".into());
            }
            Ok(Some(path))
        }
        _ => Err("검증 폴더와 소유 코드를 함께 지정하세요.".into()),
    }
}
