use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

fn tokens(text: &str) -> String {
    // pandas 3 infers string storage; this lesson checks values and selection,
    // rather than whether the string column is backed by object or str.
    text.split_whitespace().collect::<Vec<_>>().join(" ").replace("dtype: str", "dtype: object")
}

#[tokio::test]
async fn table_lesson_reads_its_own_files_and_teaches_partial_versus_whole() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/q/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/aice-table-csv.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),9); // 8 teaching steps + the appended final challenge (92b37e2a)
    let full="order_id minutes region 0 101 12 서울 1 102 18 부산 2 103 30 서울 3 104 42 부산";
    let two="order_id minutes region 0 101 12 서울 1 102 18 부산";
    let three="order_id minutes region 0 101 12 서울 1 102 18 부산 2 103 30 서울";
    let minutes="0 12 1 18 2 30 3 42 Name: minutes, dtype: int64";
    let region="0 서울 1 부산 2 서울 3 부산 Name: region, dtype: object";
    let columns="order_id minutes 0 101 12 1 102 18 2 103 30 3 104 42";
    let expected:Vec<Vec<String>>=vec![vec![full.into()],vec![two.into(),three.into()],
        vec![format!("{two} (4, 3)"),format!("{three} (4, 3)")],
        vec![minutes.into(),region.into(),minutes.into()],vec![full.into(),String::new(),full.into()],
        vec!["12".into(),"18".into(),"12".into()],vec![columns.into(),minutes.into(),columns.into()],
        vec![format!("{two} (5, 3)"),format!("{full} 4 105 24 서울 (5, 3)")]];
    // The teacher-run table covers the teaching steps; the appended final challenge is graded against
    // equivalent and wrong answers in docs/curriculum/final-challenges-evidence.md.
    for (index,task) in lesson.tasks[..lesson.tasks.len()-1].iter().enumerate() {
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"Step {} starts unsolved",index+1);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed,"Step {} solution",index+1);
        if index>=4 {
            assert_eq!(task.files.len(),1);
            assert!(task.files["delivery.csv"].starts_with("order_id,minutes,region\n"));
            assert_eq!(task.files["delivery.csv"].lines().count(),if index==7 {6}else{5});
        }
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1);
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().starts_with("print("));
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    if let Some(error)=action["expect_error"].as_str() {
                        assert!(!result.success&&result.stderr.contains(error),"Step {} expected {error}: {}",index+1,result.stderr);
                        outputs.push(String::new());
                        continue;
                    }
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(tokens(&result.stdout));
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} actual outputs",index+1);
    }
    let task=&lesson.tasks[1];
    assert!(!lesson_runner::check(task,&task.solution.replace("print(df.head(3))","df = df.head(3)\nprint(df)")).await.unwrap().passed,"Viewing must not shrink the original table");
    assert!(!lesson_runner::check(task,"raise SystemExit(0)\n").await.unwrap().passed,"Early exit is not a completed semantic check");
}
