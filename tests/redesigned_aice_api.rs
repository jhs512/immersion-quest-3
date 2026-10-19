use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn dictionary_calls_and_aliases_match_real_outputs_including_explained_errors() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/s/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/aice-python-api.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),8);
    let expected:Vec<Vec<&str>>=vec![vec!["18","서쪽","18"],
        vec!["[12, 18, 24]","['서쪽', '동쪽', '서쪽']","[12, 18, 24]"],
        vec!["2\n3","2\n4","2\n3"],vec!["","","[12, 18, 24]"],
        vec!["[12, 18, 24]\n[24, 12, 18]"],
        vec!["[12, 18, 24]\n[24, 12, 18]","[24, 18, 12]\n[24, 12, 18]"],
        vec!["18","8","18"],vec!["","18","18","18"]];
    for (index,task) in lesson.tasks.iter().enumerate() {
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"Step {} starts unsolved",index+1);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed,"Step {} solution",index+1);
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"Step {} patch target",index+1);
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().starts_with("print("));
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    if let Some(error)=action["expect_error"].as_str() {
                        assert!(!result.success,"Step {} deliberately demonstrates an error",index+1);
                        assert!(result.stderr.contains(error),"{}",result.stderr);
                    }else{assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);}
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual outputs",index+1);
    }
    let alias=&lesson.tasks[7];
    let other_alias=alias.solution.replace(" as stats"," as st").replace("stats.mean","st.mean");
    assert!(lesson_runner::check(alias,&other_alias).await.unwrap().passed,"An alias is not a memorized reserved name");
    let truncated=alias.solution.replace("stats.mean(minutes)","sum(minutes) // len(minutes)");
    assert!(!lesson_runner::check(alias,&truncated).await.unwrap().passed,"A fractional mean must not be truncated");
    let constant="minutes=[12,18,24]\nprint(18)\n";
    assert!(!lesson_runner::check(alias,constant).await.unwrap().passed,"A memorized mean is not a general call");
    let mutating="minutes=[24,12,18]\nminutes.sort(reverse=True)\nprint(minutes)\nprint(minutes)\n";
    assert!(!lesson_runner::check(&lesson.tasks[5],mutating).await.unwrap().passed,"Sorting a copy must preserve the original input");
}
