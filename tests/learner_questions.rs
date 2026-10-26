use molip_quest::{bundled_courses,repository_course::{CourseManifest,Lesson,TaskLanguage}};
/// Every backend step now requires implementation or actual terminal commands.
#[test]
fn every_backend_step_is_coding_or_real_terminal_work(){
    let course=CourseManifest::parse(bundled_courses::course_source(bundled_courses::REPOSITORIES[0]).unwrap()).unwrap();
    let mut converted=0;
    for reference in &course.lessons {
        let key=reference.repository.trim_start_matches("jhs512/mq3-lesson-redesigned-");
        let lesson=Lesson::parse(bundled_courses::lesson_source(reference).unwrap(),reference).unwrap();
        for task in &lesson.tasks {
                assert!(task.interaction.is_none(),"{key} {}: converted lessons have no answer-picking step",task.title);
                // The step states the work to do; the to-do list ends with submitting it.
                assert!(task.title.trim_end_matches('.').ends_with('요'),"{key} {}: a coding step names the work, not a question",task.title);
                assert!(task.goal.contains("**할 일**")&&!["보기를 고르","선택한 보기","객관식"].iter().any(|text|task.goal.contains(text)),"{key} {}",task.title);
                if task.git_terminal.is_none()&&task.language==TaskLanguage::Java {
                    assert!(!task.tests.is_empty()||task.checker.is_some(),"{key} {}: graded by running code",task.title);
                }
                converted+=1;
        }
        if key=="java-conditions"{
            // The first step now asks the learner to write the comparison itself; the boundary is graded by changed amounts.
            assert!(lesson.tasks[0].solution.contains("System.out.println(amount >= limit);"));
            assert!(lesson.tasks[0].variations.iter().any(|v|v.values.get("amount").map(String::as_str)==Some("20000")&&v.expected=="true"));
        }
    }
    assert_eq!(converted,course.lessons.iter().map(|r|Lesson::parse(bundled_courses::lesson_source(r).unwrap(),r).unwrap().tasks.len()).sum::<usize>());
    let keys=course.lessons.iter().map(|r|r.repository.rsplit('-').next().unwrap()).collect::<Vec<_>>();
    assert!(keys.iter().position(|k|*k=="values").unwrap()<keys.iter().position(|k|*k=="first").unwrap());
    assert!(keys.iter().position(|k|*k=="methods").unwrap()<keys.iter().position(|k|*k=="branch").unwrap());
}
