// Embed the quest icon into the Windows executable so Explorer, the taskbar and the
// Start menu show it. Other platforms get their icon from the packaging scripts.
fn main() {
    // Keep instructor-only files local. A clean source checkout builds without their data.
    let out = std::path::PathBuf::from(std::env::var_os("OUT_DIR").expect("OUT_DIR"));
    compile_lesson_registry(&out);
    for (source, name) in [("courses/kpc-solutions.json", "private-solutions.json"),
        ("site/data/instructor.json", "private-instructor.json")] {
        watch_optional_input(std::path::Path::new(source));
        let content = std::fs::read_to_string(source).unwrap_or_else(|_| "{}".into());
        std::fs::write(out.join(name), content).expect("prepare optional local instructor data");
    }
    println!("cargo:rerun-if-changed=assets/icon/icon.ico");
    // The release workflow sets MOLIP_BUILD to its run number (the "build.N" of the release
    // tag); src/updater.rs compares it with the latest release. Absent = development build.
    println!("cargo:rerun-if-env-changed=MOLIP_BUILD");
    println!(
        "cargo:rustc-env=MOLIP_BUILD={}",
        std::env::var("MOLIP_BUILD").unwrap_or_default()
    );
    #[cfg(windows)]
    {
        let mut resource = winresource::WindowsResource::new();
        resource.set_icon("assets/icon/icon.ico");
        resource.compile().expect("embed Windows icon");
    }
}

fn watch_optional_input(source: &std::path::Path) {
    // Cargo treats a missing watched file as dirty on EVERY invocation. Watch its
    // closest existing directory until it appears, then watch the file itself.
    // This preserves creation, modification and deletion detection on clean CI
    // checkouts without copying instructor-only data into the repository.
    let mut watched = source;
    while !watched.exists() {
        watched = watched.parent().filter(|parent| !parent.as_os_str().is_empty())
            .unwrap_or_else(|| std::path::Path::new("."));
    }
    println!("cargo:rerun-if-changed={}", watched.display());
}

fn compile_lesson_registry(out: &std::path::Path) {
    use std::collections::HashSet;
    let root=std::path::PathBuf::from(std::env::var_os("CARGO_MANIFEST_DIR").unwrap());
    let source="tools/redesigned_courses/catalog.json";
    println!("cargo:rerun-if-changed={source}");
    let catalog:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(root.join(source)).expect("lesson catalog")).expect("valid lesson catalog");
    let mut keys=HashSet::new();let mut versions=HashSet::new();let mut revisions=HashSet::new();
    let mut generated=String::from("pub static LESSONS: &[RegisteredLesson] = &[\n");
    for course in catalog["courses"].as_array().expect("catalog courses") {
        for item in course["lessons"].as_array().expect("catalog lessons") {
            let key=item["key"].as_str().expect("lesson key");
            assert!(key.bytes().all(|c|c.is_ascii_lowercase()||c.is_ascii_digit()||c==b'-'),"invalid lesson key");
            let revision=item["revision"].as_str().expect("lesson revision");
            let mut validation=item["validation"].as_object().expect("validation registration").clone();
            let pilot=validation.remove("pilot").unwrap().as_str().unwrap().to_owned();
            assert_eq!(pilot.chars().count(),1,"one validation character");
            let pilot=pilot.chars().next().unwrap();
            assert!(!"abcdefghijm".contains(pilot.to_ascii_lowercase()),"reserved legacy validation character");
            assert!(keys.insert(key.to_owned())&&versions.insert(pilot.to_lowercase().collect::<String>())&&revisions.insert(revision.to_owned()),"duplicate lesson registration");
            let driver=validation.remove("driver").unwrap().as_str().unwrap().to_owned();
            assert!(matches!(driver.as_str(),"native"|"code"|"git-remote"),"unknown validation driver");
            let include=|relative:&str| {println!("cargo:rerun-if-changed={relative}");format!("include_str!({:?})",root.join(relative).to_string_lossy())};
            let course=include(&format!("tests/fixtures/player-pilot/{pilot}/course.json"));
            let lesson=include(&format!("courses/redesigned/{key}.json"));
            let commands=if driver=="git-remote" {format!("Some({})",include(&format!("tests/fixtures/player-pilot/{pilot}/student-commands.json")))}else{"None".into()};
            generated.push_str(&format!("RegisteredLesson {{ key:{key:?}, revision:{revision:?}, pilot:{pilot:?}, driver:{driver:?}, course:{course}, lesson:{lesson}, config:{:?}, commands:{commands} }},\n",serde_json::Value::Object(validation).to_string()));
        }
    }
    generated.push_str("];\n");
    std::fs::write(out.join("lesson-registry.rs"),generated).expect("compile lesson registration");
}
