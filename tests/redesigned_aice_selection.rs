use molip_quest::{lesson_runner,repository_course::{CourseManifest,Lesson}};

#[tokio::test]
async fn selected_rows_and_summary_meanings_match_every_actual_teacher_run() {
    let course=CourseManifest::parse(include_str!("fixtures/player-pilot/v/course.json")).unwrap();
    let lesson=Lesson::parse(include_str!("../courses/redesigned/aice-selection.json"),&course.lessons[0]).unwrap();
    assert_eq!(lesson.tasks.len(),10);
    let expected=vec![vec!["[12, 18, 30, 42]","['서울', '부산', '서울', '부산']","[12, 18, 30, 42]"],
        vec!["12","18","12"],vec!["12","18","12"],vec!["[False, False, False, True]\n[42]","[False, False, True, True]\n[30, 42]","[False, False, False, True]\n[42]","[False, False, True, True]\n[30, 42]"],
        vec!["[30]","[30, 42]","[30]"],vec!["[12, 18, 30, 42]\n[12, 18, 30, 42]","[42, 30, 18, 12]\n[12, 18, 30, 42]"],
        vec!["25.5\n24.0","40.5\n24.0","25.5\n24.0"],
        vec!["{'부산': 30.0, '서울': 21.0}","{'부산': 60.0, '서울': 21.0}","{'부산': 30.0, '서울': 21.0}"],
        vec!["0.99","-0.99","0.99"],vec!["[30, 42]","[42, 30]","[42, 30, 18]","[42, 30]"]];
    for (index,task) in lesson.tasks.iter().enumerate() {
        assert!(!lesson_runner::check(task,&task.starter_code).await.unwrap().passed,"Step {} starts unsolved",index+1);
        assert!(lesson_runner::check(task,&task.solution).await.unwrap().passed,"Step {} solution",index+1);
        let mut source=task.example_code.clone().unwrap_or_else(||task.starter_code.clone());
        let mut outputs=Vec::new();
        for action in &task.narration {
            match action["action"].as_str().unwrap() {
                "patch_code"=>{
                    let before=action["before"].as_str().unwrap();
                    assert_eq!(source.matches(before).count(),1,"Step {} patch must be unique",index+1);
                    source=source.replacen(before,action["after"].as_str().unwrap(),1);
                },
                "run"=>{
                    let line=action["lines"][0].as_u64().unwrap() as usize;
                    assert!(source.lines().nth(line-1).unwrap().starts_with("print("));
                    let result=if task.has_runnable_example(){lesson_runner::run_example(task,&source,"").await}else{lesson_runner::run(task,&source,"").await}.unwrap();
                    assert!(result.success,"Step {} teacher: {}",index+1,result.stderr);
                    outputs.push(result.stdout.trim_end().to_owned());
                },
                _=>{}
            }
        }
        assert_eq!(outputs,expected[index],"Step {} narration must agree with actual output",index+1);
    }
    let filter=&lesson.tasks[3];
    let fixed=filter.solution.replace("df.loc[mask, \"minutes\"].tolist()","[30, 42]");
    assert!(!lesson_runner::check(filter,&fixed).await.unwrap().passed,"A memorized selection must fail");
    let sort=&lesson.tasks[9];
    let unfiltered=sort.solution.replace("selected = df.loc[df[\"minutes\"] >= limit]","selected = df");
    assert!(!lesson_runner::check(sort,&unfiltered).await.unwrap().passed,"Sorting must retain the filter");
}
