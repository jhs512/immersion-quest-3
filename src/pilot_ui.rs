//! Debug-only entry point: fixed content snapshots, real parser and runner, no account writes.
use dioxus::prelude::*;
use molip_quest::{lesson_runner, repository_course::{CourseManifest, Lesson}};

fn snapshot(version: &str) -> Result<(CourseManifest, Lesson), String> {
    let (course, lesson) = match version {
        "b" => (include_str!("../tests/fixtures/player-pilot/b/course.json"), include_str!("../tests/fixtures/player-pilot/b/lesson.json")),
        _ => (include_str!("../tests/fixtures/player-pilot/a/course.json"), include_str!("../tests/fixtures/player-pilot/a/lesson.json")),
    };
    let course = CourseManifest::parse(course)?;
    let lesson = Lesson::parse(lesson, &course.lessons[0])?;
    Ok((course, lesson))
}

#[component]
pub fn PilotPlayer() -> Element {
    let initial = use_hook(|| snapshot("a"));
    let Ok(initial) = initial else { return rsx! { p { role: "alert", "검증용 수업을 읽지 못했어요." } }; };
    let mut content = use_signal(|| initial);
    let mut index = use_signal(|| 0usize);
    let mut code = use_signal(|| content().1.tasks[0].starter_code.clone());
    let mut reset = use_signal(|| 0u64);
    let mut busy = use_signal(|| false);
    let mut message = use_signal(String::new);
    let mut output = use_signal(String::new);
    let (course, lesson) = content();
    let task = lesson.tasks[index()].clone();
    rsx! {
        main { class: "repository-study is-task pilot-player", "data-pilot-revision": lesson.revision.clone(),
            header { class: "repository-header",
                h1 { "{course.title} · {lesson.title}" }
                span { "개발 검증 전용 · 실제 계정 기록 없음" }
            }
            nav { class: "study-navigation", aria_label: "검증 스냅샷",
                for version in ["a", "b"] {
                    button { disabled: busy(), onclick: move |_| {
                        match snapshot(version) {
                            Ok(next) => { code.set(next.1.tasks[0].starter_code.clone()); content.set(next); index.set(0); reset += 1; output.set(String::new()); message.set(String::new()); }
                            Err(error) => message.set(error),
                        }
                    }, "버전 {version}" }
                }
                button { disabled: busy(), onclick: move |_| {
                    let previous = content();
                    let damaged = include_str!("../tests/fixtures/player-pilot/b/lesson.json").replace("값과 출력", "손상 후보");
                    match Lesson::parse(&damaged, &previous.0.lessons[0]) {
                        Err(_) => message.set("손상 후보를 거절했어요. 현재 수업을 유지해요.".into()),
                        Ok(_) => message.set("검증 실패: 손상 후보가 통과했어요.".into()),
                    }
                }, "손상 후보 검사" }
            }
            crate::lesson_outline::LessonOutline { lesson: lesson.clone(), task_id: task.id.clone() }
            nav { class: "study-navigation", aria_label: "스텝 선택",
                for (position, item) in lesson.tasks.iter().enumerate() {
                    button { class: if position == index() { "selected" } else { "" }, disabled: busy(), onclick: {
                        let starter = item.starter_code.clone();
                        move |_| { index.set(position); code.set(starter.clone()); reset += 1; output.set(String::new()); message.set(String::new()); }
                    }, "{item.title}" }
                }
            }
            article { class: "lesson repository-task",
                section { class: "problem-pane", h2 { "{task.title}" } crate::ui::Markdown { text: task.goal.clone() } }
                div { class: "split-handle split-col", role: "separator", tabindex: 0, aria_label: "문제와 코드 패널 크기 조절", aria_orientation: "vertical" }
                section { class: "coding-pane",
                    div { class: "pane-heading", strong { "{task.entry_file}" }
                        div { class: "pane-actions",
                            button { disabled: busy(), onclick: { let starter = task.starter_code.clone(); move |_| { code.set(starter.clone()); reset += 1; output.set(String::new()); message.set(String::new()); } }, "초기화" }
                            button { disabled: busy(), onclick: { let task = task.clone(); move |_| { let task = task.clone(); async move {
                                busy.set(true);
                                match lesson_runner::run(&task, &code(), "").await {
                                    Ok(result) => { output.set(format!("{}{}", result.stdout, result.stderr)); message.set(if result.success { "실행을 마쳤어요." } else { "실행 결과를 확인하세요." }.into()); }
                                    Err(error) => message.set(error),
                                }
                                busy.set(false);
                            } } }, "코드 실행" }
                            button { class: "primary", disabled: busy(), onclick: { let task = task.clone(); move |_| { let task = task.clone(); async move {
                                busy.set(true);
                                match lesson_runner::check(&task, &code()).await {
                                    Ok(report) => { output.set(report.cases.iter().map(|case| format!("예상: {} / 결과: {}", case.expected, case.stdout)).collect::<Vec<_>>().join("\n")); message.set(if report.passed { "통과했어요." } else { "다시 풀어보세요." }.into()); }
                                    Err(error) => message.set(error),
                                }
                                busy.set(false);
                            } } }, "제출" }
                        }
                    }
                    div { class: "editor-pane",
                        textarea { key: "{index}:{reset}", class: "code-editor", "data-code-editor": task.language.editor(), "data-editor-value": code(), "data-editor-reset": reset().to_string(), aria_label: "수업 코드", initial_value: code(), spellcheck: false, oninput: move |event| code.set(event.value()) }
                    }
                div { class: "split-handle split-row", role: "separator", tabindex: 0, aria_label: "코드와 실행 결과 패널 크기 조절", aria_orientation: "horizontal" }
                section { class: "result-pane", h3 { "실행 결과" } p { class: "execution-status", role: "status", "{message}" } pre { class: "output", "{output}" } }
                }
            }
        }
    }
}
