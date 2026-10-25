//! 관리자 자동 풀이: how the real player solves each step for a course administrator.
//!
//! This module holds only decisions, no UI. The player plays the step's narration, applies the
//! answer chosen here through the ordinary editor/answer/terminal input, runs and submits with the
//! ordinary buttons, and records through the ordinary progress path. Nothing here marks a step as
//! passed: only the real grader does.
use crate::repository_course::{CourseManifest, LessonRef, Task};
use crate::task_interaction::Interaction;
use serde_json::Value;
use std::sync::atomic::{AtomicU64, Ordering};

/// Narration actions that act on the practice terminal (or its Main.java editor). Replayed in
/// the learner's real terminal they are the same command list the lesson validators replay to
/// reach the step goal from the step start.
pub const TERMINAL_ACTIONS: &[&str] = &[
    "bash_command", "git_command", "vim_keys", "vim_wait", "vim_open",
    "inspect_folder", "write_memo", "read_memo",
];

/// What the player does after the narration to solve the step for real.
#[derive(Clone, Debug, PartialEq)]
pub enum Plan {
    /// Put the final solution in the editor, run it, then submit.
    Code { source: String },
    /// Enter the answer; run the prepared example first when the step has one.
    Answer { answer: String, run_example: bool },
    /// Replay the terminal actions in the learner's own terminal, enter the answer if the step
    /// also asks for one, then submit.
    Terminal { actions: Vec<Value>, answer: Option<String> },
}

/// The answer key in the form the answer widget stores (`InteractionEditor`'s value).
pub fn reference_answer(interaction: &Interaction) -> String {
    use std::collections::BTreeMap;
    match interaction {
        Interaction::Choice { answer, .. } => answer.clone(),
        Interaction::Order { accepted, .. } => serde_json::to_string(&accepted[0]).unwrap(),
        Interaction::Fill { accepted } => accepted[0].clone(),
        Interaction::FillFields { fields } => serde_json::to_string(
            &fields.iter().map(|f| (f.id.clone(), f.accepted[0].clone())).collect::<BTreeMap<_, _>>(),
        ).unwrap(),
    }
}

/// The step's authored answer when the grader would accept it, otherwise the answer key.
/// Some Java steps keep an explanation sentence in `solution`, not the answer value.
pub fn step_answer(task: &Task) -> Option<String> {
    let interaction = task.interaction.as_ref()?;
    Some(if interaction.check(&task.solution).is_ok_and(|r| r.passed) {
        task.solution.clone()
    } else {
        reference_answer(interaction)
    })
}

pub fn plan(task: &Task) -> Result<Plan, String> {
    if let Some(exercise) = &task.git_terminal {
        if exercise.github_pr.is_some() {
            return Err("실제 GitHub 저장소와 PR을 만드는 문제라서 자동 풀이를 지원하지 않아요. 이 문제는 직접 풀어 주세요.".into());
        }
        let java = exercise.java_build.is_some();
        let actions: Vec<Value> = task.narration.iter()
            .filter(|a| a["action"].as_str().is_some_and(|name| TERMINAL_ACTIONS.contains(&name) || (java && name == "patch_code")))
            .cloned().collect();
        if actions.is_empty() && exercise.has_goal() {
            return Err("해설에 실습 명령이 없어서 자동으로 풀 수 없어요.".into());
        }
        return Ok(Plan::Terminal { actions, answer: step_answer(task) });
    }
    if let Some(answer) = step_answer(task) {
        return Ok(Plan::Answer { answer, run_example: task.has_runnable_example() });
    }
    if task.solution.trim().is_empty() {
        return Err("이 문제에는 실행할 정답 코드가 없어요.".into());
    }
    Ok(Plan::Code { source: task.solution.clone() })
}

/// The lesson after `current` in the course's own order. The run never wraps around and never
/// leaves the course.
#[derive(Clone, Debug, PartialEq)]
pub enum NextLesson { Next(LessonRef), CourseEnd, NotInCourse }
pub fn next_lesson(course: &CourseManifest, current: &str) -> NextLesson {
    match course.lessons.iter().position(|l| l.id == current) {
        None => NextLesson::NotInCourse,
        Some(index) => course.lessons.get(index + 1).cloned().map(NextLesson::Next).unwrap_or(NextLesson::CourseEnd),
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub enum Step { Section(usize), Task(String) }

/// The one step the run may act on now. Every callback carries the target it was started for.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Target { pub lesson_id: String, pub round: String, pub step: Step }

#[derive(Clone, Debug, PartialEq)]
pub enum Status {
    Running,
    /// Opening the next lesson of the course; the run keeps control.
    Transition,
    Stopped { reason: String },
    Finished { reason: String },
}

#[derive(Clone, Debug, PartialEq)]
pub struct AutoRun {
    pub generation: u64,
    pub course_repository: String,
    pub user_id: u64,
    pub target: Target,
    pub status: Status,
    pub paused: bool,
    /// What the run is doing now, shown in the bar.
    pub stage: String,
    /// Steps that passed through the real grader in this run, in order.
    pub passed: Vec<String>,
    pub lessons: usize,
    /// Practice workspaces (the store's scope key) this run has initialized. Each is initialized
    /// once, at the first step of the run that uses it; later steps keep its real state.
    pub initialized: Vec<String>,
}

static GENERATION: AtomicU64 = AtomicU64::new(0);
/// A fresh number for each run. Stopping also takes a new number, so no callback started for
/// the old run can match again.
pub fn next_generation() -> u64 { GENERATION.fetch_add(1, Ordering::SeqCst) + 1 }
static ACTIVE: AtomicU64 = AtomicU64::new(0);
/// The generation of the run that is active now (0: none), readable from background threads,
/// so work already handed to a thread can check for Esc before it records anything.
pub fn set_active(run: Option<&AutoRun>) {
    ACTIVE.store(run.filter(|r| r.active()).map(|r| r.generation).unwrap_or(0), Ordering::SeqCst);
}
pub fn is_active(generation: u64) -> bool { generation != 0 && ACTIVE.load(Ordering::SeqCst) == generation }

impl AutoRun {
    pub fn start(course_repository: &str, user_id: u64, target: Target) -> Self {
        Self { generation: next_generation(), course_repository: course_repository.into(), user_id, target,
            status: Status::Running, paused: false, stage: "시작".into(), passed: vec![], lessons: 1, initialized: vec![] }
    }
    pub fn active(&self) -> bool { matches!(self.status, Status::Running | Status::Transition) }
    /// Whether a callback started for (generation, target) may still act.
    pub fn accepts(&self, generation: u64, target: &Target) -> bool {
        self.status == Status::Running && self.generation == generation && self.target == *target
    }
    pub fn owns_lesson(&self, course_repository: &str, user_id: u64, lesson_id: &str, round: &str) -> bool {
        self.active() && self.course_repository == course_repository && self.user_id == user_id
            && self.target.lesson_id == lesson_id && self.target.round == round
    }
    /// Stop at once; the generation changes so late callbacks of this run are ignored.
    pub fn stop(&mut self, reason: impl Into<String>) {
        if !self.active() { return; }
        self.generation = next_generation();
        self.status = Status::Stopped { reason: reason.into() };
        self.paused = false;
    }
    pub fn finish(&mut self, reason: impl Into<String>) {
        self.generation = next_generation();
        self.status = Status::Finished { reason: reason.into() };
        self.paused = false;
    }
    /// Move to `next` only if the step that just passed is still the current target.
    pub fn advance(&mut self, generation: u64, from: &Target, next: Target) -> bool {
        if !self.accepts(generation, from) { return false; }
        self.target = next;
        self.stage = "다음 스텝".into();
        true
    }
    pub fn record_pass(&mut self, generation: u64, from: &Target, label: String) -> bool {
        if !self.accepts(generation, from) { return false; }
        if !self.passed.last().is_some_and(|last| *last == label) { self.passed.push(label); }
        true
    }
    /// True only the first time a step of this run uses the practice `workspace`: the caller then
    /// prepares it once with the step's official 초기화 (the lesson's start for that step, earlier
    /// steps' files, folders and Git state included). Every later step of the run, a solved one too,
    /// works on the state the previous steps really left; nothing resets it again.
    pub fn claim_initialization(&mut self, generation: u64, from: &Target, workspace: &str) -> bool {
        if !self.accepts(generation, from) || self.initialized.iter().any(|w| w == workspace) { return false; }
        self.initialized.push(workspace.into());
        true
    }
    /// The last step of a lesson passed: hand over to the course-level transition.
    pub fn begin_transition(&mut self, generation: u64, from: &Target) -> bool {
        if !self.accepts(generation, from) { return false; }
        self.status = Status::Transition;
        self.stage = "다음 수업을 여는 중".into();
        true
    }
    /// The next lesson opened for this same run.
    pub fn enter_lesson(&mut self, generation: u64, target: Target) -> bool {
        if self.generation != generation || self.status != Status::Transition { return false; }
        self.target = target;
        self.status = Status::Running;
        self.lessons += 1;
        self.stage = "수업 시작".into();
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::repository_course::Lesson;

    #[test]
    fn each_workspace_is_initialized_once_per_run() {
        let target = Target { lesson_id: "bash".into(), round: "r".into(), step: Step::Task("s7".into()) };
        let mut run = AutoRun::start("course", 1, target.clone());
        let g = run.generation;
        assert!(run.claim_initialization(g, &target, "bash-practice"));
        assert!(!run.claim_initialization(g, &target, "bash-practice"), "second step of the same workspace");
        let next = Target { step: Step::Task("s8".into()), ..target.clone() };
        assert!(run.advance(g, &target, next.clone()));
        assert!(!run.claim_initialization(g, &next, "bash-practice"), "a later (even solved) step keeps the state");
        assert!(run.claim_initialization(g, &next, "java-launch"), "another workspace gets its own preparation");
        assert!(!run.claim_initialization(g, &target, "other"), "a callback for an old target cannot claim");
        run.stop("Esc");
        assert!(!run.claim_initialization(g, &next, "late"), "a late callback after Esc cannot claim");
        let again = AutoRun::start("course", 1, target.clone());
        assert!(again.initialized.is_empty(), "a new run starts with nothing initialized");
    }

    fn bundled_lessons() -> Vec<(String, Lesson)> {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("courses/redesigned");
        let mut lessons = vec![];
        for entry in std::fs::read_dir(root).unwrap() {
            let path = entry.unwrap().path();
            if path.extension().is_none_or(|e| e != "json") { continue; }
            let raw = std::fs::read_to_string(&path).unwrap();
            let Ok(lesson) = serde_json::from_str::<Lesson>(&raw) else { continue };
            lessons.push((path.file_name().unwrap().to_string_lossy().into_owned(), lesson));
        }
        assert!(lessons.len() > 40, "bundled lessons were not found");
        lessons
    }

    #[test]
    fn every_bundled_step_has_a_real_solving_plan_or_a_stated_reason() {
        let mut kinds = std::collections::BTreeMap::<&str, usize>::new();
        for (file, lesson) in bundled_lessons() {
            for task in &lesson.tasks {
                match plan(task) {
                    Ok(Plan::Code { source }) => { assert_eq!(source, task.solution); *kinds.entry("code").or_default() += 1; }
                    Ok(Plan::Answer { answer, run_example }) => {
                        let report = task.interaction.as_ref().unwrap().check(&answer).unwrap();
                        assert!(report.passed, "{file} {}: answer key must pass the real grader", task.id);
                        assert_eq!(run_example, task.has_runnable_example());
                        *kinds.entry("answer").or_default() += 1;
                    }
                    Ok(Plan::Terminal { actions, answer }) => {
                        let exercise = task.git_terminal.as_ref().unwrap();
                        assert!(!actions.is_empty() || !exercise.has_goal(), "{file} {}", task.id);
                        assert!(actions.iter().all(|a| a["action"] != "say" && a["action"] != "submit"));
                        if let Some(answer) = answer { assert!(task.interaction.as_ref().unwrap().check(&answer).unwrap().passed); }
                        *kinds.entry("terminal").or_default() += 1;
                    }
                    Err(reason) => {
                        assert!(task.git_terminal.as_ref().is_some_and(|e| e.github_pr.is_some()), "{file} {}: unexpected unsupported step: {reason}", task.id);
                        *kinds.entry("unsupported").or_default() += 1;
                    }
                }
            }
        }
        assert!(kinds["code"] > 0 && kinds["terminal"] > 0, "{kinds:?}");
        assert_eq!(kinds.get("unsupported").copied().unwrap_or(0), 8, "only the hosted GitHub PR steps stop: {kinds:?}");
    }

    #[test]
    fn prose_solutions_fall_back_to_the_answer_key() {
        let (_, lesson) = bundled_lessons().into_iter().find(|(f, _)| f == "java-arguments.json").unwrap();
        // Legacy compatibility must not require a current lesson to remain
        // multiple choice after the user's conversion to coding tasks.
        let mut task=lesson.tasks[0].clone();
        task.solution="터미널에서 실행하고 출력을 확인하세요.".into();
        task.interaction=Some(serde_json::from_value(serde_json::json!({"kind":"choice",
            "options":[{"id":"observed","text":"관찰했어요"},{"id":"other","text":"다른 답"}],"answer":"observed"})).unwrap());
        assert!(!task.interaction.as_ref().unwrap().check(&task.solution).unwrap().passed);
        let Ok(Plan::Terminal { answer: Some(answer), actions }) = plan(&task) else { panic!() };
        assert_eq!(answer, "observed");
        assert_eq!(actions[0]["command"], "java Main.java");
    }

    #[test]
    fn answer_keys_match_every_widget_format() {
        let fields: Interaction = serde_json::from_value(serde_json::json!({"kind":"fill_fields","fields":[{"id":"before","label":"a","accepted":["2"," 2"]},{"id":"after","label":"b","accepted":["3"]}]})).unwrap();
        assert_eq!(reference_answer(&fields), r#"{"after":"3","before":"2"}"#);
        assert!(fields.check(&reference_answer(&fields)).unwrap().passed);
        let order: Interaction = serde_json::from_value(serde_json::json!({"kind":"order","options":[{"id":"a","text":"A"},{"id":"b","text":"B"}],"accepted":[["b","a"]]})).unwrap();
        assert!(order.check(&reference_answer(&order)).unwrap().passed);
    }

    fn course(ids: &[&str]) -> CourseManifest {
        let lessons: Vec<_> = ids.iter().map(|id| serde_json::json!({"id":id,"title":id,"repository":"o/r","revision":"1","sha256":"0"})).collect();
        serde_json::from_value(serde_json::json!({"schema_version":2,"id":"crs_x","title":"t","description":"d","repository":"o/c","lessons":lessons})).unwrap()
    }

    #[test]
    fn the_next_lesson_follows_course_order_and_never_wraps() {
        let c = course(&["a", "b", "c"]);
        assert!(matches!(next_lesson(&c, "a"), NextLesson::Next(l) if l.id == "b"));
        assert!(matches!(next_lesson(&c, "b"), NextLesson::Next(l) if l.id == "c"));
        assert_eq!(next_lesson(&c, "c"), NextLesson::CourseEnd);
        assert_eq!(next_lesson(&c, "z"), NextLesson::NotInCourse);
    }

    fn target(lesson: &str, step: &str) -> Target { Target { lesson_id: lesson.into(), round: "r".into(), step: Step::Task(step.into()) } }

    #[test]
    fn late_callbacks_of_a_stopped_or_moved_run_are_ignored() {
        let mut run = AutoRun::start("o/c", 1, target("a", "1"));
        let generation = run.generation;
        assert!(run.accepts(generation, &target("a", "1")));
        assert!(!run.accepts(generation, &target("a", "2")), "another step");
        assert!(!run.accepts(generation + 99, &target("a", "1")), "another run");
        assert!(run.advance(generation, &target("a", "1"), target("a", "2")));
        // A duplicate success for the step that already advanced does nothing.
        assert!(!run.advance(generation, &target("a", "1"), target("a", "2")));
        assert!(run.record_pass(generation, &target("a", "2"), "a · 2".into()));
        assert!(run.record_pass(generation, &target("a", "2"), "a · 2".into()));
        assert_eq!(run.passed, ["a · 2"], "the same pass is listed once");
        run.stop("Esc");
        assert!(!run.active() && run.generation != generation);
        assert!(!run.accepts(generation, &target("a", "2")), "Esc wins over a late success");
        assert!(!run.advance(generation, &target("a", "2"), target("a", "3")));
        run.stop("again");
        assert_eq!(run.status, Status::Stopped { reason: "Esc".into() }, "the first reason stays");
    }

    #[test]
    fn an_automatic_lesson_change_keeps_the_run_and_a_stale_one_cannot_enter() {
        let mut run = AutoRun::start("o/c", 1, target("a", "last"));
        let generation = run.generation;
        assert!(run.begin_transition(generation, &target("a", "last")));
        assert!(run.active());
        assert!(!run.accepts(generation, &target("a", "last")), "no step acts while the next lesson opens");
        assert!(!run.enter_lesson(generation + 1, target("b", "1")));
        assert!(run.enter_lesson(generation, target("b", "1")));
        assert_eq!((run.lessons, run.generation, &run.status), (2, generation, &Status::Running));
        assert!(run.owns_lesson("o/c", 1, "b", "r") && !run.owns_lesson("o/c", 1, "a", "r") && !run.owns_lesson("o/c", 2, "b", "r"));
        let mut stopped = run.clone();
        assert!(stopped.begin_transition(generation, &target("b", "1")));
        stopped.stop("Esc while opening");
        assert!(!stopped.enter_lesson(generation, target("c", "1")), "Esc during the lesson change cancels it");
        run.finish("course end");
        assert!(!run.active());
    }
}
