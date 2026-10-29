//! The guide above a Java problem's code must describe what the screen really accepts.
use molip_quest::{repository_course::{CodeAccess,Task,TaskLanguage},task_interaction::Interaction};
use std::{collections::BTreeMap,path::Path};

fn collect(value:&serde_json::Value,out:&mut Vec<serde_json::Value>) {
    match value {
        serde_json::Value::Object(map)=>{
            if map.contains_key("starter_code")&&map.contains_key("language"){out.push(value.clone());}
            for child in map.values(){collect(child,out);}
        }
        serde_json::Value::Array(items)=>for child in items{collect(child,out);},
        _=>{}
    }
}
fn walk(dir:&Path,out:&mut Vec<(String,Task)>) {
    for entry in std::fs::read_dir(dir).unwrap() {
        let path=entry.unwrap().path();
        if path.is_dir(){walk(&path,out);continue;}
        if path.extension().is_none_or(|e|e!="json"){continue;}
        let Ok(value)=serde_json::from_str::<serde_json::Value>(&std::fs::read_to_string(&path).unwrap()) else{continue};
        let mut raw=vec![];collect(&value,&mut raw);
        for task in raw {
            if let Ok(task)=serde_json::from_value::<Task>(task){out.push((path.display().to_string(),task));}
        }
    }
}
fn bundled()->Vec<(String,Task)> {
    let mut tasks=vec![];walk(&Path::new(env!("CARGO_MANIFEST_DIR")).join("courses"),&mut tasks);tasks
}
fn find(file:&str,id:&str)->Task {
    bundled().into_iter().find(|(path,task)|path.replace('\\',"/").ends_with(file)&&task.id==id).unwrap_or_else(||panic!("{file}:{id}")).1
}

#[test]
fn every_bundled_java_task_states_its_real_code_access_and_answer_method() {
    let mut seen=BTreeMap::<(String,bool,bool),usize>::new();
    let mut java=0;
    for (path,task) in bundled() {
        let family=matches!(task.language,TaskLanguage::Java|TaskLanguage::JavaProject|TaskLanguage::Junit|TaskLanguage::JavaLibraries);
        let guide=task.code_guide();
        if !family {assert!(guide.is_none(),"{path}:{} non-Java tasks keep their old screen",task.id);continue;}
        java+=1;
        let guide=guide.unwrap_or_else(||panic!("{path}:{} Java task without guide",task.id));
        let terminal_java=task.git_terminal.as_ref().is_some_and(|e|e.java_build.is_some());
        // Same rule as player_ui: the plain code editor is writable only without an answer interaction;
        // the example editor is readonly; a Java build terminal always offers an editable Main.java.
        let expected=if terminal_java||(task.git_terminal.is_none()&&task.interaction.is_none()){CodeAccess::Editable}
            else if !task.has_runnable_example(){CodeAccess::Absent}
            else if task.example_order_marker.is_some(){CodeAccess::Assembled}else{CodeAccess::ReadOnly};
        assert_eq!(guide.access,expected,"{path}:{}",task.id);
        assert_eq!(guide.label.contains("수정 가능"),expected==CodeAccess::Editable,"{path}:{}",task.id);
        assert_eq!(guide.answer.contains("보기"),matches!(task.interaction,Some(Interaction::Choice{..})),"{path}:{}",task.id);
        assert_eq!(guide.answer.contains("터미널"),terminal_java,"{path}:{}",task.id);
        assert_eq!(guide.answer.contains("예상"),task.predict_before_run,"{path}:{}",task.id);
        assert!(guide.answer.ends_with('.')&&guide.answer.chars().count()<=45,"{path}:{} short sentence",task.id);
        *seen.entry((guide.access.as_str().into(),task.interaction.is_some(),terminal_java)).or_default()+=1;
    }
    assert!(java>150,"{java}");
    // The learner cases the shipped courses use today.
    assert!(seen.contains_key(&("editable".into(),false,false)),"{seen:?}");
    assert!(seen.contains_key(&("readonly".into(),true,false)),"{seen:?}");
    assert!(seen.contains_key(&("editable".into(),false,true)),"{seen:?}");
}

/// Tasks that shipped before 8a22394f replaced answer picking in 12 Java lessons. The player still
/// supports these screens, so their guides stay checked on the real retired task definitions.
fn retired(id:&str)->Task {
    let raw:serde_json::Value=serde_json::from_str(include_str!("fixtures/java-code-guide-retired-tasks.json")).unwrap();
    let task=raw["tasks"].as_array().unwrap().iter().find(|t|t["id"]==id).unwrap_or_else(||panic!("{id}")).clone();
    serde_json::from_value(task).unwrap()
}

#[test]
fn representative_tasks_read_naturally() {
    let code=find("courses/redesigned/java-arrays.json","stp_bfae17a1-f80f-4540-b4e9-36c1c723d98f").code_guide().unwrap();
    assert_eq!((code.access,code.label,code.answer),(CodeAccess::Editable,"코드 수정 가능","코드를 고친 뒤 제출하세요."));
    let predict_task=find("courses/redesigned/engineer-java-flow.json","stp_e89108e7-6f81-4a7f-984b-320d809b411b");
    // No shipped Java lesson currently asks a plain (non-prediction) choice over readonly code
    // (java-arrays replaced it with a coding task); keep the wording checked on the same real task.
    let mut plain_choice=predict_task.clone();plain_choice.predict_before_run=false;
    let choice=plain_choice.code_guide().unwrap();
    assert_eq!((choice.access,choice.label,choice.answer),(CodeAccess::ReadOnly,"코드 읽기 전용","보기 중 답을 골라 제출하세요."));
    let predict=predict_task.code_guide().unwrap();
    assert_eq!(predict.access,CodeAccess::ReadOnly);
    assert_eq!(predict.answer,"예상한 보기를 골라 제출하세요.");
    let terminal=find("courses/redesigned/java-arguments.json","stp_6589e18d-411a-4939-ae85-51528c7cc633").code_guide().unwrap();
    assert_eq!((terminal.access,terminal.label,terminal.answer),(CodeAccess::Editable,"코드 수정 가능","Main.java를 고치고 터미널에서 실행한 뒤 제출하세요."));
    let both=retired("stp_1172ab94-de4d-4ce3-ac0d-87bd557b00a7").code_guide().unwrap();
    assert_eq!((both.access,both.label,both.answer),(CodeAccess::Editable,"코드 수정 가능","터미널에서 실행하고 보기를 골라 제출하세요."));
    let ordered=retired("stp_450a8eec-4dfc-4082-bc19-f6c42f0218e4").code_guide().unwrap();
    assert_eq!((ordered.access,ordered.label),(CodeAccess::Assembled,"코드 직접 수정 불가"));
    let fill=find("courses/redesigned/engineer-java-flow.json","stp_539dc525-7521-4428-ad57-f386fc8f7110").code_guide().unwrap();
    assert_eq!((fill.access,fill.answer),(CodeAccess::ReadOnly,"빈칸에 답을 적어 제출하세요."));
}
