// Embed the quest icon into the Windows executable so Explorer, the taskbar and the
// Start menu show it. Other platforms get their icon from the packaging scripts.
fn main() {
    // Keep instructor-only files local. A clean source checkout builds without their data.
    let out = std::path::PathBuf::from(std::env::var_os("OUT_DIR").expect("OUT_DIR"));
    for (source, name) in [("courses/kpc-solutions.json", "private-solutions.json"),
        ("site/data/instructor.json", "private-instructor.json")] {
        println!("cargo:rerun-if-changed={source}");
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
