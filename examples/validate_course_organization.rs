//! Validate a metadata proposal with MQ's real snapshot parser and pinned lesson bytes.
use molip_quest::content_updates::SnapshotStore;

fn validate() -> Result<(), String> {
    let paths: Vec<_> = std::env::args_os().skip(1).collect();
    if paths.len() != 2 {
        return Err("Usage: validate_course_organization PROPOSAL_JSON CACHED_SNAPSHOT_JSON".into());
    }
    let proposed = std::fs::read_to_string(&paths[0]).map_err(|e| e.to_string())?;
    let cached: serde_json::Value = serde_json::from_slice(&std::fs::read(&paths[1]).map_err(|e| e.to_string())?)
        .map_err(|e| e.to_string())?;
    let documents = cached["lessons"].as_object().ok_or("Cached lesson documents missing")?;
    let repository = "jhs512/mq3-course-redesigned-engineer-practical";
    if cached["repository"] != repository { return Err("Unexpected cached repository".into()); }
    let temporary = tempfile::tempdir().map_err(|e| e.to_string())?;
    let snapshot = SnapshotStore::new(temporary.path()).prepare(repository, &proposed, |reference| {
        documents.get(&reference.id).and_then(serde_json::Value::as_str)
            .map(str::to_owned).ok_or_else(|| format!("Missing pinned document: {}", reference.id))
    })?;
    println!("VERIFIED: {} lessons, {} topic categories; every pinned lesson passes the application parser",
        snapshot.course().lessons.len(), snapshot.course().categories.len());
    Ok(())
}

fn main() {
    if let Err(error) = validate() {
        eprintln!("FAILED: {error}");
        std::process::exit(1);
    }
}
