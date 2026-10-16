//! "AI에게 물어보기": a tutor chat that knows the mission on screen, answered by a CLI assistant
//! installed on this computer (Claude Code or Codex).
//!
//! The current mission (every slide of a deck, a concept's text, a problem with its hint and the
//! student's code, or a quiz's questions) and the conversation so far become one prompt that is
//! handed to `claude -p` or `codex exec`. No API key: the CLI's own login is used. Settings live
//! in `assistant.json` next to the progress database.
use crate::curriculum::{Activity, ActivityKind, QuestionKind};
use crate::Unit;
use serde::{Deserialize, Serialize};

/// The voice guide shared by every LLM call in the project (tools/narrate.py reads the same
/// file), so the tutor's answers and the compiled 해설 sound like one instructor.
const VOICE: &str = include_str!("../docs/voice.md");

const SYSTEM: &str = "당신은 현재 수업의 조교입니다. 자바 미션은 JDK 25 기준이며 preview 기능을 사용하지 않습니다. 아래 '현재 미션 내용'을 기준으로, \
코딩이 처음인 직장인 수강생의 질문에 한국어로 짧고 친절하게 답하세요.\n\
규칙:\n\
1. 미션 내용 범위 안에서 답하고, 범위를 벗어나면 그렇다고 말한 뒤 짧게만 답합니다.\n\
2. 코딩 미션의 정답 코드를 통째로 주지 말고 막힌 줄만 짚어 주거나 힌트를 줍니다. 학생이 '코드만 줘'라고 분명히 말하면 코드를 줍니다.\n\
3. 퀴즈는 정답을 바로 말하지 말고 생각할 거리를 줍니다.\n\
4. 용어는 현재 미션의 자료형·변수·메서드 등 본문 용어를 그대로 씁니다.\n\
5. 답은 다섯 문장 이내로 하고, 코드는 코드 블록으로 보여 줍니다.\n\
앱 조작: 학생이 '해 줘', '풀어 줘', '넣어 줘', '제출해 줘', '다음으로 가 줘'처럼 행동을 부탁하면 짧은 설명 뒤에 \
아래 형식의 코드 블록을 답의 맨 끝에 붙입니다. 앱이 그 동작을 순서대로 실행하고 결과를 '앱:' 메시지로 돌려주니, \
결과를 보고 필요하면 고쳐서 다시 동작을 붙이고, 끝났으면 동작 블록 없이 한 줄로 마무리합니다. \
코딩 미션을 풀어 달라고 하면 규칙 2의 예외로 set_code에 전체 코드를 넣고 submit까지 합니다. \
동작: set_code{code}, fill_blanks{values}, run, submit, answer_quiz{answers: {\"1\": \"보기 글자 그대로 또는 단답\"}}, \
next, prev, goto{mission}, next_slide, finish_slides, say{target, text}, type_code{code, say, replace}. 표에서 행·열을 고르는 문항의 답은 1부터 세는 번호를 쉼표로 잇습니다(\"1,3,5\"). answer_quiz에 \"submit\": false를 주면 채점하지 않고 답만 넣습니다. 행동을 부탁받지 않았으면 블록을 붙이지 않습니다. 예:\n\
```molip-actions\n[{\"action\":\"set_code\",\"code\":\"print('Hello, KPC!')\"},{\"action\":\"submit\"}]\n```\n\
해설 모드: 학생이 '/auto'를 치거나 '해설하며', '설명하면서', '이야기하면서', '보여 주면서' 풀어 달라고 하면 답 글은 한 줄만 쓰고 동작 블록에 단계를 순서대로 담습니다. \
모든 동작에 \"say\"를 붙일 수 있고, 앱은 그 문장을 소리 내어 읽으면서 건드리는 자리를 보라색으로 비춘 뒤에 동작합니다. say는 수강생에게 말하듯 1~2문장으로. \
흐름: say{target:\"problem\", text:문제가 무엇을 묻는지} → say{target:\"examples\", text:예제 입력과 출력 읽기} → \
type_code{code:첫 조각, say:설명, replace:true}(기존 코드를 지우고 시작) → run{say} → say{target:\"output\", text:그 시점의 결과 읽기} → \
type_code{code:다음 조각 1~3줄, say:그 줄들이 하는 일} → run → say{target:\"output\"} … 를 반복한다(한 번에 다 쓰고 끝에 한 번 실행하지 않는다: 살짝 쓰고 실행해 출력을 읽는 걸 되풀이해 프로그램이 자라는 걸 보여 준다). \
중간에 1~2번 '이렇게 해볼까요?'로 틀리기 쉬운 줄을 type_code로 쳐 보고 run → say{target:\"output\", text:무엇이 잘못됐는지} → set_code{code:그 줄을 뺀 전체 코드, say:\"그래서 이렇게 고쳐요\"}로 되돌리거나, say{target:\"editor\", text:\"…하기 쉬운데 …하니 조심하세요\"}로 말만 한다. \
마지막은 run → say{target:\"output\"} → submit{say}. 퀴즈는 say{target:\"quiz:1\", text:문항 풀이} 뒤 answer_quiz{answers, say}. \
빈칸 문제는 say{target:\"blanks\"} 뒤 fill_blanks{values, say}. 개념 미션은 say{target:\"problem\"}을 2~4번 이어 핵심을 짚은 뒤 확인 문항이 있으면 answer_quiz{answers, say}. \
슬라이드 미션은 장마다 say{target:\"slides\", text:그 장의 요지}와 next_slide를 번갈아 넣고 마지막에 finish_slides. \
target 값: problem, examples, editor, input, output, run, submit, hint, quiz, quiz:N, option:N:M, blanks, slides, nav, title, text:본문의 구절(그 구절이 든 문단·코드·만화로 화면을 천천히 내려 비춤). \
type_code의 code는 지금까지의 전체가 아니라 덧붙일 부분만 적고, 조각을 모두 이으면 완전한 정답 코드가 되어야 합니다.";

/// What the `/auto` and `/auto-all` commands ask for, in the words the system prompt expects.
pub const AUTO_REQUEST: &str = "이 미션을 해설하며 끝까지 진행해 줘: 코딩이면 코드를 조각내어 설명하며 넣고 실행·제출까지, 퀴즈나 확인 문항이면 풀이를 말하고 채점까지, 개념이면 핵심을 짚어 주고, 슬라이드면 장마다 요지를 말하며 넘기고 끝까지. 답 글은 한 줄만.";

/// What `/tour-all` asks for when a mission has no precompiled script.
pub const TOUR_REQUEST: &str =
    "이 미션의 핵심만 한두 문장으로 말하고, 답을 넣어 제출·채점까지 끝내 줘. 긴 설명은 하지 마.";

/// `/auto`, `/auto-all` and `/tour-all` are typed as commands; the model sees the request they
/// stand for.
fn spoken_request(text: &str) -> &str {
    match text.trim() {
        "/auto" | "/auto-all" => AUTO_REQUEST,
        "/tour-all" => TOUR_REQUEST,
        other => other,
    }
}

/// Which locally installed CLI answers.
#[derive(Clone, Copy, Debug, Default, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Provider {
    Codex,
    /// Also the fallback for settings files that name a provider that no longer exists.
    #[default]
    #[serde(other)]
    ClaudeCode,
}

impl Provider {
    pub const ALL: [Provider; 2] = [Provider::ClaudeCode, Provider::Codex];
    pub fn id(self) -> &'static str {
        match self {
            Provider::ClaudeCode => "claude_code",
            Provider::Codex => "codex",
        }
    }
    pub fn from_id(id: &str) -> Provider {
        Provider::ALL
            .into_iter()
            .find(|p| p.id() == id)
            .unwrap_or_default()
    }
    pub fn label(self) -> &'static str {
        match self {
            Provider::ClaudeCode => "Claude Code (이 컴퓨터의 claude 명령)",
            Provider::Codex => "Codex CLI (이 컴퓨터의 codex 명령)",
        }
    }
}

fn default_claude_command() -> String {
    "claude".into()
}
fn default_codex_command() -> String {
    "codex".into()
}

fn default_true() -> bool {
    true
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Settings {
    #[serde(default)]
    pub provider: Provider,
    #[serde(default = "default_claude_command")]
    pub claude_command: String,
    #[serde(default = "default_codex_command")]
    pub codex_command: String,
    /// 해설 모드 reads its sentences aloud; off keeps the captions only.
    #[serde(default = "default_true")]
    pub narration_voice: bool,
    /// Which voice reads: an edge-tts neural voice id, or "system" for the device's own.
    #[serde(default = "crate::tts::default_voice")]
    pub narration_voice_name: String,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            provider: Provider::ClaudeCode,
            claude_command: default_claude_command(),
            codex_command: default_codex_command(),
            narration_voice: true,
            narration_voice_name: crate::tts::default_voice(),
        }
    }
}

impl Settings {
    fn path() -> Result<std::path::PathBuf, String> {
        Ok(crate::data_dir()?.join("assistant.json"))
    }

    pub fn load() -> Settings {
        let mut settings: Settings = Self::path()
            .ok()
            .and_then(|path| std::fs::read_to_string(path).ok())
            .and_then(|text| serde_json::from_str(&text).ok())
            .unwrap_or_default();
        if settings.claude_command.trim().is_empty() {
            settings.claude_command = default_claude_command();
        }
        if settings.codex_command.trim().is_empty() {
            settings.codex_command = default_codex_command();
        }
        settings
    }

    pub fn save(&self) -> Result<(), String> {
        let path = Self::path()?;
        if let Some(dir) = path.parent() {
            std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
        }
        let text = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        std::fs::write(path, text).map_err(|e| e.to_string())
    }
}

/// One chat message; `role` is "user" or "model".
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Turn {
    pub role: String,
    pub text: String,
}

/// Everything the tutor should know about the mission on screen.
pub fn page_context(
    course_title: &str,
    chapter_title: &str,
    unit: &Unit,
    activity: &Activity,
    draft_code: Option<&str>,
) -> String {
    let mut out = format!(
        "수업: {course_title}\n챕터: {chapter_title}\n단원: {}\n미션({}): {}\n\n---\n\n",
        unit.title,
        activity.label(),
        activity.title
    );
    match &activity.kind {
        ActivityKind::Slides { markdown } => {
            out.push_str("(강사용 슬라이드 전체. `---`가 장 구분입니다.)\n\n");
            out.push_str(markdown);
        }
        ActivityKind::Concept { body, check } => {
            out.push_str(body);
            out.push_str("\n\n### 확인 문항\n\n");
            out.push_str(&check.prompt);
        }
        ActivityKind::Coding { problem } => {
            out.push_str(&problem.content);
            out.push_str(&format!(
                "\n\n### 기본 코드\n\n```{}\n",
                problem.language.name()
            ));
            out.push_str(&problem.starter_code);
            out.push_str("\n```\n");
            if let Some(code) = draft_code
                .filter(|c| !c.trim().is_empty() && c.trim() != problem.starter_code.trim())
            {
                out.push_str(&format!(
                    "\n### 학생이 지금 쓴 코드\n\n```{}\n",
                    problem.language.name()
                ));
                out.push_str(code);
                out.push_str("\n```\n");
            }
        }
        ActivityKind::Quiz { questions } => {
            out.push_str("(퀴즈. 정답은 알려 주지 않습니다.)\n\n");
            for (n, q) in questions.iter().enumerate() {
                out.push_str(&format!("Q{}. {}\n", n + 1, q.prompt));
                match &q.kind {
                    QuestionKind::Choice { options, .. } => {
                        for option in options {
                            out.push_str(&format!("- {option}\n"));
                        }
                    }
                    QuestionKind::TableSelect { table, pick, .. } => {
                        out.push_str(&format!(
                            "(표에서 {}을 고르는 문항. 답은 1부터 세는 번호를 쉼표로: \"1,3,5\")\n열: {}\n",
                            if pick == "rows" { "행" } else { "열" },
                            table
                                .columns
                                .iter()
                                .enumerate()
                                .map(|(i, c)| format!("{}:{c}", i + 1))
                                .collect::<Vec<_>>()
                                .join(" | ")
                        ));
                        for (i, row) in table.rows.iter().enumerate().take(20) {
                            out.push_str(&format!("{}행: {}\n", i + 1, row.join(" | ")));
                        }
                    }
                    QuestionKind::ShortAnswer { .. } => {}
                }
                out.push('\n');
            }
        }
    }
    out
}

/// Answer the latest question with the mission as context and the conversation so far.
pub async fn ask(settings: &Settings, context: &str, history: &[Turn]) -> Result<String, String> {
    let prompt = transcript(context, history);
    match settings.provider {
        Provider::ClaudeCode => {
            ask_cli(
                &settings.claude_command,
                &["-p", "--output-format", "text"],
                &prompt,
                true,
                None,
            )
            .await
        }
        Provider::Codex => {
            let out = std::env::temp_dir().join(format!("molip-codex-{}.txt", std::process::id()));
            let out_arg = out.to_string_lossy().to_string();
            ask_cli(
                &settings.codex_command,
                &["exec", "--skip-git-repo-check", "-o", &out_arg],
                &prompt,
                false,
                Some(out),
            )
            .await
        }
    }
}

/// The spoken lines of a precompiled 해설 script (an `Activity::narration` as JSON), in order:
/// what the panel shows before the agent starts performing them.
pub fn narration_lines(actions_json: &str) -> Vec<String> {
    let Ok(serde_json::Value::Array(actions)) = serde_json::from_str(actions_json) else {
        return Vec::new();
    };
    actions
        .iter()
        .filter_map(|a| {
            let text = if a.get("action")?.as_str()? == "say" {
                a.get("text")?
            } else {
                a.get("say")?
            };
            text.as_str()
                .map(str::trim)
                .filter(|t| !t.is_empty())
                .map(String::from)
        })
        .collect()
}

/// Split an answer into the text to show and the ```molip-actions JSON array, if the
/// assistant appended one.
pub fn split_actions(reply: &str) -> (String, Option<serde_json::Value>) {
    let marker = "```molip-actions";
    let Some(start) = reply.rfind(marker) else {
        return (reply.trim().to_string(), None);
    };
    let body_start = start + marker.len();
    let rest = &reply[body_start..];
    let end = rest.find("```").map(|i| body_start + i);
    let json = match end {
        Some(e) => &reply[body_start..e],
        None => rest,
    };
    let actions = serde_json::from_str::<serde_json::Value>(json.trim())
        .ok()
        .filter(|v| v.as_array().is_some_and(|a| !a.is_empty()));
    let after = end.map(|e| &reply[e + 3..]).unwrap_or("");
    let text = format!("{}\n{}", reply[..start].trim_end(), after.trim())
        .trim()
        .to_string();
    (text, actions)
}

/// The whole exchange as one prompt for a CLI assistant.
fn transcript(context: &str, history: &[Turn]) -> String {
    let mut text = format!("{SYSTEM}\n\n## 말투와 용어 (docs/voice.md)\n\n{VOICE}\n\n## 현재 미션 내용\n\n{context}\n\n## 지금까지의 대화\n\n");
    for turn in history.iter().filter(|t| t.role != "note") {
        let who = match turn.role.as_str() {
            "user" => "학생",
            "tool" => "앱",
            _ => "조교",
        };
        text.push_str(&format!("{who}: {}\n\n", spoken_request(&turn.text)));
    }
    text.push_str(
        "위 대화의 마지막 학생 질문에 조교로서 답하세요. 인사말이나 머리말 없이 답만 쓰세요.",
    );
    text
}

/// Run a local CLI assistant (claude or codex) with the prompt and return its answer.
async fn ask_cli(
    command: &str,
    args: &[&str],
    prompt: &str,
    via_stdin: bool,
    output_file: Option<std::path::PathBuf>,
) -> Result<String, String> {
    use std::process::Stdio;
    use tokio::io::AsyncWriteExt;
    let command = command.trim();
    if command.is_empty() {
        return Err("명령 이름이 비어 있습니다. 설정에서 적어 주세요.".into());
    }
    // npm shims on Windows are .cmd files, which only a shell resolves.
    let mut cmd = if cfg!(windows) {
        let mut c = tokio::process::Command::new("cmd");
        c.arg("/C").arg(command);
        c
    } else {
        tokio::process::Command::new(command)
    };
    cmd.args(args);
    // Windows command lines are capped near 32K characters; keep a positional prompt under it.
    let prompt_arg: String = if via_stdin {
        String::new()
    } else {
        prompt.chars().take(30_000).collect()
    };
    if !via_stdin {
        cmd.arg(&prompt_arg);
    }
    cmd.current_dir(std::env::temp_dir())
        .stdin(if via_stdin {
            Stdio::piped()
        } else {
            Stdio::null()
        })
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(windows)]
    cmd.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
                                     // Cancelling the request (Esc in /auto-all) drops this future and must end the CLI with it.
    cmd.kill_on_drop(true);
    let mut child = cmd.spawn().map_err(|e| {
        format!("'{command}' 명령을 실행하지 못했습니다: {e}. 설치되어 있고 PATH에 있는지, 설정의 명령 이름이 맞는지 확인하세요.")
    })?;
    if via_stdin {
        if let Some(mut stdin) = child.stdin.take() {
            stdin
                .write_all(prompt.as_bytes())
                .await
                .map_err(|e| format!("프롬프트를 넘기지 못했습니다: {e}"))?;
        }
    }
    let output = tokio::time::timeout(
        std::time::Duration::from_secs(240),
        child.wait_with_output(),
    )
    .await
    .map_err(|_| "4분 안에 답이 오지 않았습니다. 다시 시도해 보세요.".to_string())?
    .map_err(|e| e.to_string())?;
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    if !output.status.success() {
        let detail: String = if stderr.is_empty() {
            stdout.clone()
        } else {
            stderr
        }
        .chars()
        .take(500)
        .collect();
        return Err(format!("{command} 오류 ({}): {detail}", output.status));
    }
    let text = match output_file {
        Some(path) => {
            let saved = std::fs::read_to_string(&path).ok();
            let _ = std::fs::remove_file(&path);
            saved
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .unwrap_or(stdout)
        }
        None => stdout,
    };
    if text.trim().is_empty() {
        return Err(format!(
            "{command}가 빈 답을 돌려줬습니다. 터미널에서 로그인되어 있는지 확인하세요."
        ));
    }
    Ok(text)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_prompt_carries_the_shared_voice_guide() {
        let text = transcript("문제", &[]);
        assert!(text.contains("## 말투와 용어 (docs/voice.md)"));
        // A line that only docs/voice.md states: the guide is embedded, not paraphrased.
        assert!(text.contains("한 문장 45자 이내"));
        assert!(VOICE.contains("# 수업의 목소리"));
    }

    #[test]
    fn auto_commands_become_the_narration_request() {
        let history = vec![Turn {
            role: "user".into(),
            text: "/auto".into(),
        }];
        let text = transcript("문제", &history);
        assert!(text.contains(AUTO_REQUEST));
        assert!(!text.contains("학생: /auto"));
        let history = vec![Turn {
            role: "user".into(),
            text: " /auto-all ".into(),
        }];
        assert!(transcript("문제", &history).contains(AUTO_REQUEST));
        let history = vec![Turn {
            role: "user".into(),
            text: "/autobahn".into(),
        }];
        assert!(transcript("문제", &history).contains("학생: /autobahn"));
    }

    #[test]
    fn actions_block_is_split_from_the_answer() {
        let reply = "코드를 넣고 제출할게요.\n\n```molip-actions\n[{\"action\":\"set_code\",\"code\":\"print(1)\"},{\"action\":\"submit\"}]\n```\n";
        let (text, actions) = split_actions(reply);
        assert_eq!(text, "코드를 넣고 제출할게요.");
        assert_eq!(actions.unwrap().as_array().unwrap().len(), 2);
        let (text, none) = split_actions("그냥 설명입니다.");
        assert_eq!(text, "그냥 설명입니다.");
        assert!(none.is_none());
    }

    #[test]
    fn narration_lines_are_the_spoken_sentences_in_order() {
        let json = r#"[{"action":"say","target":"problem","text":"문제를 볼게요."},{"action":"type_code","code":"print(1)\n","say":"한 줄이에요."},{"action":"next_slide"},{"action":"submit","say":"제출할게요."}]"#;
        assert_eq!(
            narration_lines(json),
            ["문제를 볼게요.", "한 줄이에요.", "제출할게요."]
        );
        assert!(narration_lines("[]").is_empty());
        assert!(narration_lines("not json").is_empty());
    }

    /// Every mission ships with a precompiled 해설 script (tools/kpc_course/narration.py), so
    /// /auto-all never waits for the CLI: concepts walk the text, coding problems type the
    /// solution in pieces and submit, quizzes answer and grade, decks turn every slide.
    #[test]
    fn every_kpc_mission_has_a_narration_that_ends_the_mission() {
        let course = crate::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        for unit in course.chapters.iter().flat_map(|c| &c.units) {
            for activity in &unit.activities {
                let where_ = format!("{}/{}", unit.id, activity.id);
                let last = activity
                    .narration
                    .last()
                    .unwrap_or_else(|| panic!("{where_}: 해설 없음"));
                let last_action = last["action"].as_str().unwrap();
                let expected = match &activity.kind {
                    ActivityKind::Slides { .. } => "finish_slides",
                    ActivityKind::Concept { .. } | ActivityKind::Quiz { .. } => "answer_quiz",
                    ActivityKind::Coding { .. } => "submit",
                };
                assert_eq!(last_action, expected, "{where_}");
                let lines = narration_lines(&serde_json::to_string(&activity.narration).unwrap());
                assert!(lines.len() >= 2, "{where_}: 해설 문장이 너무 적습니다");
                if let ActivityKind::Coding { problem } = &activity.kind {
                    // The kept starter code plus the typed pieces spell a whole program that is
                    // run before it is submitted (the build checks it equals the solution).
                    let actions: Vec<&str> = activity
                        .narration
                        .iter()
                        .filter_map(|a| a["action"].as_str())
                        .collect();
                    assert!(
                        actions.contains(&"type_code") && actions.contains(&"run"),
                        "{where_}"
                    );
                    let typed: String = activity
                        .narration
                        .iter()
                        .filter(|a| matches!(a["action"].as_str(), Some("set_code" | "type_code")))
                        .filter_map(|a| a["code"].as_str())
                        .collect();
                    let kept: Vec<&str> = problem
                        .starter_code
                        .lines()
                        .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with('#'))
                        .collect();
                    assert!(
                        kept.iter().all(|l| typed.contains(l)),
                        "{where_}: 준비 코드가 빠졌습니다"
                    );
                }
            }
        }
    }

    #[test]
    fn old_settings_files_fall_back_to_claude_code() {
        let old: Settings =
            serde_json::from_str(r#"{"provider":"gemini","api_key":"x","model":"m"}"#).unwrap();
        assert_eq!(old.provider, Provider::ClaudeCode);
        assert_eq!(old.claude_command, "claude");
    }

    /// Needs a logged-in `claude` CLI on this machine: `cargo test -- --ignored claude_cli`.
    #[tokio::test]
    #[ignore]
    async fn claude_cli_answers_a_question() {
        let settings = Settings::default();
        let history = vec![Turn {
            role: "user".into(),
            text: "기준 모델이 뭐야? 한 문장으로.".into(),
        }];
        let answer = ask(
            &settings,
            "미션: 기준 모델 소개. 기준 모델은 가장 많은 답만 찍는 DummyClassifier다.",
            &history,
        )
        .await
        .unwrap();
        assert!(
            answer.contains("기준") || answer.contains("Dummy"),
            "{answer}"
        );
    }

    #[test]
    fn context_carries_every_slide_and_the_student_code() {
        let course = crate::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        let chapter = &course.chapters[0];
        let unit = &chapter.units[0];
        let deck = &unit.activities[0];
        let text = page_context(&course.title, &chapter.title, unit, deck, None);
        assert!(text.contains("슬라이드") && text.contains("회사는 매일 숫자를 예측합니다"));
        let problem = unit
            .activities
            .iter()
            .find(|a| matches!(a.kind, ActivityKind::Coding { .. }))
            .unwrap();
        let text = page_context(
            &course.title,
            &chapter.title,
            unit,
            problem,
            Some("print('hi')"),
        );
        assert!(text.contains("학생이 지금 쓴 코드") && text.contains("print('hi')"));
        let same = page_context(
            &course.title,
            &chapter.title,
            unit,
            problem,
            Some("# 첫 문장을 출력하세요\n"),
        );
        assert!(!same.contains("학생이 지금 쓴 코드"));
    }
}
