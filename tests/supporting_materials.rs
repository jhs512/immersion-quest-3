use molip_quest::repository_course::{CourseManifest, Lesson};
use serde_json::json;
use sha2::{Digest, Sha256};

#[test]
fn optional_diagram_is_admitted_without_changing_the_problem_or_other_steps() {
    let mut course =
        CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let mut source: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    let original_second = source["tasks"][1].clone();
    source["tasks"][0]["supporting_materials"] = json!([{
        "id":"value-flow", "title":"값과 출력 그림", "kind":"mermaid",
        "source":"flowchart LR\n A[값] --> B[출력]"
    }]);
    let raw = source.to_string();
    course.lessons[0].sha256 = format!("{:x}", Sha256::digest(raw.as_bytes()));
    let lesson = Lesson::parse(&raw, &course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks[0].supporting_materials.len(), 1);
    assert_eq!(
        serde_json::to_value(&lesson.tasks[1]).unwrap()["id"],
        original_second["id"]
    );
    assert_eq!(lesson.required_tasks().len(), 2);
    assert_eq!(
        lesson.tasks[0].solution,
        source["tasks"][0]["solution"].as_str().unwrap()
    );
}

#[test]
fn diagram_preview_keeps_lesson_text_out_of_executable_html() {
    use molip_quest::supporting_materials::{MaterialContent, SupportingMaterial};
    let aid = SupportingMaterial {
        id: "unsafe-text".into(),
        title: "<img src=x onerror=alert(1)>".into(),
        content: MaterialContent::Mermaid {
            source: "flowchart LR\n A[</script><script>alert(1)</script>]".into(),
        },
    };
    let MaterialContent::Mermaid { source } = &aid.content else {
        panic!("diagram")
    };
    let html = molip_quest::supporting_materials::diagram_document(source);
    assert!(html.contains("connect-src 'none'"));
    assert!(html.contains("default-src 'none'"));
    assert!(!html.contains("<script>alert(1)</script>"));
    assert!(html.contains("securityLevel:'strict'"));
    assert!(html.contains("다이어그램을 그리지 못했어요."));
}

#[test]
fn condition_visualization_is_bounded_data_with_reversible_frames() {
    let mut course =
        CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let mut source: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    source["tasks"][0]["supporting_materials"] = json!([{
        "id":"trace", "title":"값 변화", "kind":"interactive",
        "variants":[
            {"label":"처음 값", "frames":[{"caption":"준비", "facts":{"value":"1"}}, {"caption":"하나 더해요", "facts":{"value":"2"}}]},
            {"label":"다른 값", "frames":[{"caption":"준비", "facts":{"value":"3"}}, {"caption":"하나 더해요", "facts":{"value":"4"}}]}
        ]
    }]);
    let raw = source.to_string();
    course.lessons[0].sha256 = format!("{:x}", Sha256::digest(raw.as_bytes()));
    let lesson = Lesson::parse(&raw, &course.lessons[0]).unwrap();
    let molip_quest::supporting_materials::MaterialContent::Interactive { variants } =
        &lesson.tasks[0].supporting_materials[0].content
    else {
        panic!("interactive")
    };
    assert_eq!(variants[1].frames[1].facts["value"], "4");
    source["tasks"][0]["supporting_materials"][0]["variants"][0]["frames"] = json!([]);
    let invalid = source.to_string();
    course.lessons[0].sha256 = format!("{:x}", Sha256::digest(invalid.as_bytes()));
    assert!(Lesson::parse(&invalid, &course.lessons[0]).is_err());
}

#[test]
fn published_image_is_pinned_local_png_and_cannot_reference_a_remote_resource() {
    let mut course =
        CourseManifest::parse(include_str!("fixtures/player-pilot/a/course.json")).unwrap();
    let mut source: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/a/lesson.json")).unwrap();
    use base64::Engine;
    let bytes = include_bytes!("fixtures/player-pilot/support-pixel.png");
    let data = base64::engine::general_purpose::STANDARD.encode(bytes);

    source["tasks"][0]["supporting_materials"] = json!([{
        "id":"comic", "title":"값 그림", "kind":"comic",
        "image":{"alt":"숫자를 출력하는 장면이에요.","png_base64":data,"sha256":format!("{:x}", Sha256::digest(&bytes))}
    }]);
    let raw = source.to_string();
    course.lessons[0].sha256 = format!("{:x}", Sha256::digest(raw.as_bytes()));
    let lesson = Lesson::parse(&raw, &course.lessons[0]).unwrap();
    assert!(matches!(
        lesson.tasks[0].supporting_materials[0].content,
        molip_quest::supporting_materials::MaterialContent::Comic { .. }
    ));
    source["tasks"][0]["supporting_materials"][0]["image"]["png_base64"] =
        json!("https://example.org/image.png");
    let raw = source.to_string();
    course.lessons[0].sha256 = format!("{:x}", Sha256::digest(raw.as_bytes()));
    assert!(Lesson::parse(&raw, &course.lessons[0]).is_err());
}

#[test]
fn repeated_aid_keys_and_private_generation_prompts_are_rejected() {
    let mut course =
        CourseManifest::parse(include_str!("fixtures/player-pilot/j/course.json")).unwrap();
    let source: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/j/lesson.json")).unwrap();
    for mutation in ["duplicate", "prompt", "hash", "oversized", "truncated"] {
        let mut candidate = source.clone();
        match mutation {
            "duplicate" => candidate["tasks"][0]["supporting_materials"][1]["id"] = json!("flow"),
            "prompt" => {
                candidate["tasks"][0]["supporting_materials"][0]["prompt"] = json!("private prompt")
            }
            "hash" => {
                candidate["tasks"][0]["supporting_materials"][2]["image"]["sha256"] =
                    json!("0".repeat(64))
            }
            "truncated" => {
                use base64::Engine;
                let image = &mut candidate["tasks"][0]["supporting_materials"][2]["image"];
                let bytes = base64::engine::general_purpose::STANDARD
                    .decode(image["png_base64"].as_str().unwrap())
                    .unwrap();
                image["png_base64"] =
                    json!(base64::engine::general_purpose::STANDARD.encode(&bytes[..33]));
                image["sha256"] = json!(format!("{:x}", Sha256::digest(&bytes[..33])));
            }
            _ => {
                candidate["tasks"][0]["supporting_materials"][0]["source"] =
                    json!("x".repeat(32769))
            }
        }
        let raw = candidate.to_string();
        course.lessons[0].sha256 = format!("{:x}", Sha256::digest(raw.as_bytes()));
        assert!(
            Lesson::parse(&raw, &course.lessons[0]).is_err(),
            "accepted {mutation}"
        );
    }
}

#[test]
fn truncated_image_cannot_replace_a_valid_installed_snapshot() {
    use base64::Engine;
    use molip_quest::content_updates::SnapshotStore;
    let root = tempfile::tempdir().unwrap();
    let store = SnapshotStore::new(root.path());
    let repo = "mq3-validation/course";
    let baseline = store
        .prepare(
            repo,
            include_str!("fixtures/player-pilot/a/course.json"),
            |_| Ok(include_str!("fixtures/player-pilot/a/lesson.json").into()),
        )
        .unwrap();
    store.apply(&baseline).unwrap();
    let mut course: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/j/course.json")).unwrap();
    let original: serde_json::Value =
        serde_json::from_str(include_str!("fixtures/player-pilot/j/lesson.json")).unwrap();
    let png = include_bytes!("fixtures/player-pilot/support-pixel.png");
    for bytes in [&png[..33], &png[..png.len() - 12]] {
        let mut candidate = original.clone();
        candidate["tasks"][0]["supporting_materials"][2]["image"]["png_base64"] =
            json!(base64::engine::general_purpose::STANDARD.encode(bytes));
        candidate["tasks"][0]["supporting_materials"][2]["image"]["sha256"] =
            json!(format!("{:x}", Sha256::digest(bytes)));
        let raw = candidate.to_string();
        course["lessons"][0]["sha256"] = json!(format!("{:x}", Sha256::digest(raw.as_bytes())));
        assert!(store
            .prepare(repo, &course.to_string(), |_| Ok(raw.clone()))
            .is_err());
        assert_eq!(
            store.active(repo).unwrap().unwrap().course().lessons[0].revision,
            "pilot-a"
        );
    }
}
