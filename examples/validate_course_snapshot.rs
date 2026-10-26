//! Offline preparation through the same validated snapshot store used by the player.
//! Does not access credentials, drafts or progress. Output directory must be explicit.
use molip_quest::content_updates::SnapshotStore;
fn main(){
    let args:Vec<_>=std::env::args_os().skip(1).collect();
    assert_eq!(args.len(),2,"validate_course_snapshot SOURCE.json OUTPUT_DIRECTORY");
    let source:serde_json::Value=serde_json::from_slice(&std::fs::read(&args[0]).unwrap()).unwrap();
    let store=SnapshotStore::new(&args[1]);
    let candidate=store.prepare(source["repository"].as_str().unwrap(),source["course"].as_str().unwrap(),|reference|
        source["lessons"][&reference.id].as_str().map(str::to_owned).ok_or_else(||"Missing lesson".into())).unwrap();
    store.apply(&candidate).unwrap();
    let loaded=store.active(&candidate.course().repository).unwrap().unwrap();
    assert_eq!(loaded,candidate);
    for reference in &loaded.course().lessons {
        if reference.repository.ends_with("java-react")||reference.repository.ends_with("java-tailwind") {
            let lesson=loaded.lesson(reference).unwrap();
            println!("{}: {} tasks",reference.revision,lesson.tasks.len());
        }
    }
    println!("Validated {} lessons, fingerprint {}",loaded.course().lessons.len(),loaded.fingerprint());
}
