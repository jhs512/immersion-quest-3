use molip_quest::task_interaction::Interaction;
use serde_json::json;

fn example()->serde_json::Value {json!({"kind":"fill_fields","fields":[
    {"id":"before","label":"Before","accepted":["2"]},
    {"id":"after","label":"After","accepted":["3"]}
]})}

#[test]
fn independent_state_cells_are_graded_by_field_identity() {
    let mut value=example();
    let interaction:Interaction=serde_json::from_value(value.clone()).unwrap();
    assert!(interaction.check(r#"{"after":" 3 ","before":"2"}"#).unwrap().passed);
    for answer in [r#"{"before":"3","after":"2"}"#,r#"{"before":"2"}"#,r#"{"before":"2","after":"3","extra":"x"}"#,r#"["2","3"]"#,"2 3"] {
        assert!(!interaction.check(answer).unwrap().passed,"{answer}");
    }
    value["fields"].as_array_mut().unwrap().reverse();
    let reordered:Interaction=serde_json::from_value(value).unwrap();
    assert!(reordered.check(r#"{"before":"2","after":"3"}"#).unwrap().passed);
}

#[test]
fn fields_require_unique_ids_nonempty_labels_and_bounded_answers() {
    for replacement in [json!(""),json!("before")] {
        let mut value=example();value["fields"][1]["id"]=replacement;
        assert!(serde_json::from_value::<Interaction>(value).unwrap().validate().is_err());
    }
    for key in ["label","accepted"] {
        let mut value=example();value["fields"][0][key]=if key=="label"{json!(" ")}else{json!([])};
        assert!(serde_json::from_value::<Interaction>(value).unwrap().validate().is_err());
    }
}
