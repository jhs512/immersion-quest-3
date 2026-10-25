use molip_quest::{bundled_courses,repository_course::{CourseManifest,Lesson},task_interaction::Interaction};
/// Java lessons converted from multiple choice to coding tasks (user decision 2026-10-26). Every step of
/// these lessons is graded by running the learner's own code or commands, never by picking an answer.
const CODING_ONLY:&[&str]=&["java-values","java-conditions","java-launch","java-arguments","java-arrays","java-methods",
    "java-references","java-static","java-roles","java-collections","java-streams","java-files"];
#[test]
fn java_steps_are_coding_tasks_and_remaining_choices_ask_explicit_questions(){
    let course=CourseManifest::parse(bundled_courses::course_source(bundled_courses::REPOSITORIES[0]).unwrap()).unwrap();
    let mut converted=0;
    for reference in &course.lessons {
        if !reference.repository.contains("-java-"){continue;}
        let key=reference.repository.trim_start_matches("jhs512/mq3-lesson-redesigned-");
        let lesson=Lesson::parse(bundled_courses::lesson_source(reference).unwrap(),reference).unwrap();
        let coding_only=CODING_ONLY.contains(&key);
        for task in &lesson.tasks {
            if coding_only {
                assert!(task.interaction.is_none(),"{key} {}: converted lessons have no answer-picking step",task.title);
                // The step states the work to do; the to-do list ends with submitting it.
                assert!(task.title.ends_with('요'),"{key} {}: a coding step names the work, not a question",task.title);
                assert!(task.goal.contains("**할 일**")&&!task.goal.contains("보기"),"{key} {}",task.title);
                if task.git_terminal.is_none(){
                    assert!(!task.tests.is_empty()||task.checker.is_some(),"{key} {}: graded by running code",task.title);
                }
                converted+=1;
            }
            if let Some(Interaction::Choice{options,answer})=&task.interaction {
                assert!(task.question.ends_with('?'),"{} has no explicit question",task.title);
                assert!(task.title.ends_with('?'),"{} labels an activity instead of asking a question",task.title);
                assert!(options.iter().any(|o|o.id==*answer));
            }
        }
        if key=="java-conditions"{
            // The first step now asks the learner to write the comparison itself; the boundary is graded by changed amounts.
            assert!(lesson.tasks[0].solution.contains("System.out.println(amount >= limit);"));
            assert!(lesson.tasks[0].variations.iter().any(|v|v.values.get("amount").map(String::as_str)==Some("20000")&&v.expected=="true"));
        }
    }
    assert_eq!(converted,CODING_ONLY.iter().map(|key|course.lessons.iter().find(|r|r.repository.ends_with(&format!("-{key}"))).map(|r|Lesson::parse(bundled_courses::lesson_source(r).unwrap(),r).unwrap().tasks.len()).unwrap()).sum::<usize>());
    let keys=course.lessons.iter().map(|r|r.repository.rsplit('-').next().unwrap()).collect::<Vec<_>>();
    assert!(keys.iter().position(|k|*k=="values").unwrap()<keys.iter().position(|k|*k=="first").unwrap());
    assert!(keys.iter().position(|k|*k=="methods").unwrap()<keys.iter().position(|k|*k=="branch").unwrap());
}
