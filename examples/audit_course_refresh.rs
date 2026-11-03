//! Read live public course content through the actual application's validation path.
//! Uses a temporary profile; never reads or writes learner progress.
fn main() {
    let profile = tempfile::tempdir().expect("temporary audit profile");
    std::env::set_var("MOLIP_DATA_DIR", profile.path());
    let github = molip_quest::github_player::Github::new();
    let mut failed = false;
    for repository in molip_quest::bundled_courses::REPOSITORIES {
        let before = github.installed_course(repository).expect("bundled bootstrap");
        match github.prepare_course(repository) {
            Ok(next) => println!("VERIFIED {repository}: bundled={} remote={} rust={}",
                before.lessons.len(), next.course().lessons.len(),
                next.course().lessons.iter().filter(|l| l.revision.starts_with("rust-")).count()),
            Err(error) => { failed = true; println!("FAILED {repository}: {error}"); }
        }
    }
    if failed { std::process::exit(1); }
}
