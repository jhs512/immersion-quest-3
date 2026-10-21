use molip_quest::{bundled_courses,repository_course::{CourseManifest,Lesson},task_interaction::Interaction};
#[test]
fn java_choices_ask_explicit_questions_and_keep_existing_answers(){
    let course=CourseManifest::parse(bundled_courses::course_source(bundled_courses::REPOSITORIES[0]).unwrap()).unwrap();
    let mut checked=0;
    for reference in &course.lessons {
        if !reference.repository.contains("-java-"){continue;}
        let lesson=Lesson::parse(bundled_courses::lesson_source(reference).unwrap(),reference).unwrap();
        for task in &lesson.tasks {
            if let Some(Interaction::Choice{options,answer})=&task.interaction {
                assert!(task.question.ends_with('?'),"{} has no explicit question",task.title);
                assert!(options.iter().any(|o|o.id==*answer));
                if reference.repository.ends_with("java-conditions") {
                    assert!(!task.question.contains("어떨까요"));
                }
                checked+=1;
            }
        }
        if reference.repository.ends_with("java-conditions"){
            assert!(lesson.tasks[0].question.contains("19,999"));
            assert!(lesson.tasks[0].question.contains("출력"));
            assert!(lesson.tasks[1].question.contains("20,000"));
            assert!(lesson.tasks[1].question.contains("비교식"));
            assert_eq!(lesson.tasks[0].solution,"false");assert_eq!(lesson.tasks[1].solution,"inclusive");
        }
    }
    assert_eq!(checked,112);
    let keys=course.lessons.iter().map(|r|r.repository.rsplit('-').next().unwrap()).collect::<Vec<_>>();
    assert!(keys.iter().position(|k|*k=="values").unwrap()<keys.iter().position(|k|*k=="first").unwrap());
    assert!(keys.iter().position(|k|*k=="methods").unwrap()<keys.iter().position(|k|*k=="branch").unwrap());
}
