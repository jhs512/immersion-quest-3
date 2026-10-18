use dioxus::prelude::*;
use molip_quest::repository_course::Lesson;

#[component]
pub fn LessonOutline(lesson: Lesson, task_id: String) -> Element {
    if lesson.schema_version != 2 { return rsx! {}; }
    let Some((chapter, unit, step)) = lesson.context_for(&task_id) else { return rsx! {}; };
    rsx! {
        section { class: "lesson-outline", aria_label: "현재 학습 목표",
            div { class: "learning-objective", strong { "수업 목표" }
                ul { for goal in &lesson.objectives { li { "{goal}" } } }
            }
            div { class: "learning-objective", strong { "챕터 · {chapter.title}" }
                ul { for goal in &chapter.objectives { li { "{goal}" } } }
            }
            div { class: "learning-objective", strong { "단원 · {unit.title}" }
                ul { for goal in &unit.objectives { li { "{goal}" } } }
                if !unit.premise.is_empty() { details { summary { "기본 전제" } p { "{unit.premise}" } } }
            }
            div { class: "learning-objective", strong { "스텝 목표" }
                ul { for goal in &step.objectives { li { "{goal}" } } }
            }
        }
    }
}
