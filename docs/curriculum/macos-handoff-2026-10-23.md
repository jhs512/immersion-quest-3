# Mac 이어가기 · 수업 신고 검증 (2026-10-23)

## 먼저 읽을 상태

사용자가 Windows에서 가능한 조사를 마친 뒤 Mac에서 이어가겠다고 요청했다. 실제 작업 저장소는 **jhs512/immersion-quest-3**다. Codex의 다른 프로젝트 폴더(CA3)와 혼동하지 않는다. Mac 체크아웃에서 `git status`로 기존 변경을 확인하고 `git pull --ff-only` 후 진행한다. 강제 초기화하지 않는다.

Node/npm 경로 수정 커밋은 `f6fa0ef`다. 이 문서와 실제 Tailwind 문제 회귀 검사는 그 다음 커밋에 있다. 최종 설치 파일 게시 여부는 아래 CI/릴리스 명령으로 새로 확인한다. **수정 소스 푸시와 Mac 앱 배포·실제 Mac 검증을 구분한다.**

사용자 정책은 원인을 확정하지 못한 신고도 조사 내용과 함께 **미해결 완료**로 종료하는 것이다. 기존의 모든 이슈를 Mac 검사까지 열어 두는 지시는 이 정책으로 대체됐다. 이미 닫힌 이슈도 아래처럼 실제 Mac에서 재현되면 다시 열어 수정한다. 미해결 종료는 수정 완료가 아니다.

## 신고 목록과 현재 처리 상태

| 대상 | 상태 | Mac에서 이어갈 내용 |
| --- | --- | --- |
| [Tailwind 수업 #1](https://github.com/jhs512/mq3-lesson-redesigned-java-tailwind/issues/1) | 코드 수정 완료로 닫힘, 배포 대기 | 최우선. Finder에서 앱을 열고 Node가 터미널에만 보이는 환경에서 실행·미리보기·채점을 확인한다. |
| [플레이어 #4](https://github.com/jhs512/immersion-quest-3/issues/4) | 미해결 완료, not planned | 실제 Mac 두벌식에서 첫 메모의 공백이 두 칸이 되는지 확인한다. Windows WebKit 입력 모사는 실기기 검증이 아니다. |
| [플레이어 #6](https://github.com/jhs512/immersion-quest-3/issues/6) | 미해결 완료, not planned | Git 협업 단계에서 직접 입력과 복사 입력의 파일·명령·채점 결과를 비교한다. |
| [GitHub PR 수업 #1](https://github.com/jhs512/mq3-lesson-redesigned-github-pr/issues/1) | 기존 HOME 수정과 Mac PTY 로그인 확인 근거로 닫힘 | 실제 Finder 실행과 GH_CONFIG_DIR/XDG 조합의 읽기 전용 추가 확인. 저장소·PR을 만들 필요 없다. |
| [플레이어 #1](https://github.com/jhs512/immersion-quest-3/issues/1), [#3](https://github.com/jhs512/immersion-quest-3/issues/3) | Windows 신고 경로 재검증 완료로 닫힘 | 신고 OS는 Windows. 새 Mac 오류가 없으면 Mac 검증 미완료를 이유로 자동 재개하지 않는다. |
| [플레이어 #2](https://github.com/jhs512/immersion-quest-3/issues/2) | 설명 부족으로 미해결 완료, not planned | 첨부는 빈 Bash 프롬프트이고 실패 명령이 없다. 추가 정보 없이 원인이나 증상을 지어내지 않는다. |

진도·등록 이슈는 수정하거나 닫지 않았다. [이번 조사 기록](../verification/student-reports-2026-10-23.md)과 [이전 실제 Mac 확인 범위](../verification/student-reports-2026-10-22.md)를 함께 본다.

## 1. 먼저 배포 CI를 확인

```bash
gh run list --repo jhs512/immersion-quest-3 --workflow release.yml --limit 3
gh release view --repo jhs512/immersion-quest-3 --json tagName,publishedAt,url
```

이 작업 직전 최신 게시 버전은 `v0.1.0-build.97`이었다. `f6fa0ef`의 [CI 39919239869](https://github.com/jhs512/immersion-quest-3/actions/runs/39919239869)는 문서 작성 시 진행 중이며, 이후 푸시가 있으면 새 실행으로 대체될 수 있다. 워크플로 전체 성공과 새 설치 파일 게시 전에는 설치된 앱에 수정이 반영됐다고 말하지 않는다.

**기존 Mac CI 실패도 먼저 볼 것:** 이전 `63d1c8f`의 [CI 39898387852](https://github.com/jhs512/immersion-quest-3/actions/runs/39898387852)는 Windows 성공, Mac 네이티브 Git 검사 실패로 릴리스가 게시되지 않았다. 실패는 `player_git_course_native`의 `Timed out: current student terminal owner and prompt`다. 화면에는 Git 입문 1번이 보이지만 terminal 문자열이 비어 있고, `Your app is being rebuilt` 문구도 있었다. 이것이 타이밍·검증 도구 문제인지 실제 PTY 초기화 회귀인지는 아직 확정하지 않았다. Node 수정 때문이라고 결론 내리지 않는다.

```bash
gh run view 39898387852 --repo jhs512/immersion-quest-3 --log-failed
cargo test --locked --test player_git_course_native -- --ignored --nocapture --test-threads=1
```

관련 파일: `tests/player_git_course_native.rs`, `tools/player-pilot-git-course.js`, `tests/support/native_player.rs`, 실습 터미널 소유권·준비 상태. 새 Mac CI에서도 같은 오류면 해당 재현부터 좁힌다. 대기 시간을 늘리는 것만으로 원인 해결이라 하지 않는다.

## 2. Tailwind Node/npm 오류 검증

### 확인된 원인과 변경

`lesson_runner::node()`는 MOLIP_NODE만 보거나 문자열 node를 반환했고, npm은 별도로 PATH의 npm을 실행했다. 따라서 앱이 Node의 경로를 알아도 npm의 `env node`나 자식 프로세스는 실행하지 못할 수 있었다.

`src/node_tools.rs`가 명시한 Node·PATH·사용자 nvm/로컬 bin·일반 설치 경로를 찾는다. 같은 설치의 `npm-cli.js`를 **선택한 Node 절대 경로로** 실행한다. npm, esbuild, Playwright의 자식 PATH에 선택한 Node 폴더를 앞에 넣는다. 시스템 PATH나 셸 설정은 변경하지 않는다. Node/npm 자체가 없는 기기에 자동 설치하는 기능은 추가하지 않았다. 없으면 필요한 도구를 안내한다.

### 자동 검사

```bash
cargo test --locked --lib managed_web_tests -- --nocapture
cargo test --locked --lib node_tools::tests -- --nocapture
cargo test --locked --lib managed_web_tests::fresh_runtime_accepts_a_canonical_data_directory -- --ignored --nocapture
cargo test --locked --lib quoted_web_output_tests -- --nocapture
```

- `npm_uses_the_selected_node_without_node_on_path`: 별도 자식 프로세스에서 PATH를 빈 폴더로 제한한다. 선택한 Node와 같은 설치의 npm CLI, 그 CLI가 다시 띄운 node까지 확인한다. 기존 코드에서 실패 → 수정 후 통과했다.
- `finder_finds_nvm_node_without_shell_initialization`: Mac/Unix에서만 실행한다. 분리된 HOME/nvm fixture를 쓰므로 실제 사용자 셸 설정은 바꾸지 않는다. **Windows에서는 실행되지 않았다. Mac에서 결과 확인이 필요하다.**
- `reported_tailwind_title_runs_and_checks_its_real_font_weight`: 실제 신고 수업의 첫 문제로 실행·미리보기, font-normal 오답, font-bold 정답을 검사한다.
- 빈 폴더 실제 npm 설치 검사는 인터넷을 사용한다. 기존 web-runtime을 삭제할 필요 없다.

### 실제 앱 검사

1. 터미널에서 `command -v node npm`, `node -p 'process.execPath'`, `npm --version`만 확인한다. 토큰·전체 환경 변수는 출력하지 않는다.
2. 실제 Finder에서 최신 MQ 앱을 연다. 터미널에서 직접 실행한 결과와 구분한다.
3. 자바 백엔드 → 「작은 Tailwind 화면의 배치를 읽고 고쳐요」 → 「클래스로 제목의 굵기를 바꿔요」를 연다.
4. 초기 코드 실행으로 HTML 미리보기가 나오는지 확인한다. `font-normal` 상태 제출은 실패해야 한다.
5. 제목을 `font-bold`로 바꾼다. 미리보기에서 굵어지고 제출이 통과하는지 확인한다. `env: node: No such file or directory`가 없어야 한다.
6. 가능하면 nvm으로 설치된 Node만 있는 계정에서도 확인한다. 앱 안과 외부 터미널의 실행 경로를 비교한다.

## 3. 실제 두벌식 입력 검사 (#4와 #6)

기존 사용자 작업을 초기화하지 말고 별도의 테스트 계정/실습에서 진행한다. 직접 입력과 붙여넣기를 같은 실습 상태에서 비교한다. 사용자 명령·파일 전체를 자동 원격 수집하지 않는다.

```bash
node --test tests/js/terminal-ime.test.cjs
cargo test --locked --test bash_basics --test git_practice_resume --test redesigned_git_remote -- --test-threads=1
```

자동 입력 브리지 18건과 실제 Git 명령·채점은 Windows에서 통과했다. 이는 Mac의 실제 한국어 입력기를 검증한 것이 아니다.

- #4: Git 입문 1번에서 실제 두벌식으로 `echo "첫 메모" > memo.txt`를 한 글자씩 입력한다. 첫 뒤 공백은 한 번만 누른다. `cat memo.txt`와 `od -An -tx1 memo.txt`로 공백·파일 바이트를 확인한다. 다시 커서를 옮겨 공백을 지워야만 하는지 확인한다.
- #6: 「공유 기록을 받고 비교하고 되돌려요」의 「다른 팀원의 작업도 직접 만들어 보세요」에서 화면에 제시된 동일 명령을 직접 입력/복사 입력으로 각각 실행한다. 파일명 앞 NBSP, NFC/NFD, 따옴표·공백, 실제 성공 명령 이력과 제출 판정을 비교한다.
- 재현되면 현재 최신 앱 빌드, 수업 revision, 입력기, 실제 입력 이벤트 순서, 파일 바이트, 기대/실제 결과를 최소화한 회귀 검사와 함께 기록한다. 해당 이슈를 다시 열고 원인 확인·수정·재검증 후 completed로 종료한다.

## 4. GitHub 로그인 추가 확인

```bash
cargo test --locked --test github_pr -- --test-threads=1
cargo test --locked --test github_pr current_github_login -- --ignored --nocapture
```

현재 외부 터미널과 앱 실습 터미널에서 각각 `gh api user --jq .login`을 실행해 같은 계정인지 본다. 기존 HOME 수정의 실제 Mac PTY 확인은 이미 통과했다. Finder/키체인/GH_CONFIG_DIR/XDG 조합은 추가 확인이다. **`gh auth token`은 실행하거나 기록하지 않는다.** `real_github_pr_lifecycle`은 실제 비공개 저장소·PR을 만들므로 이번 확인에서는 실행하지 않는다.

## 완료와 인계 기준

Windows에서는 Bash 9건, Git 복원 9건, PR 격리 2건, 원격 Git 2건(21단계와 독립 초기화), 입력 브리지 18건, 웹 경로·실제 npm 설치·실제 브라우저 검사를 통과했다. Mac 체크가 끝나면 이 문서에 실행한 플랫폼·앱 빌드·명령·결과·남은 한계를 덧붙인다. 코드·앱 CI·물리 IME 검증을 서로 대체하지 않는다. 캡처·원본 진단은 .scratch에만 보관하고 저장소에 넣지 않는다.


## Mac에서 이어서 확인한 결과 · 2026-10-23

- `6a1390c`를 main에 fast-forward pull했다. 작업 전 로컬 변경은 없었다.
- 최신 배포 실행 `39919725196`의 **Mac 작업은 성공**, Windows 작업은 실패했다. 실패한 검사는 `vim_practice::unsaved_text_input_mode_and_cursor_survive_reopening`이며 복원 후 입력 모드가 `n`에 머물렀다. 전체 릴리스 작업은 건너뛰었고 게시 버전은 여전히 `v0.1.0-build.97`이다. 새 설치 파일 배포가 완료됐다고 볼 수 없다.
- 실제 Mac의 Homebrew Node 26.0.0/npm 11.12.1로 Node 경로 검사를 실행했다. 테스트가 Node 바이너리만 복사해 상대 동적 라이브러리(`libnode.147.dylib`)를 잃는 문제가 있었다. Unix fixture는 원래 설치를 가리키는 symlink를 사용하도록 고쳤다. 제품의 Node 탐색 코드는 변경하지 않았다.
- `managed_web_tests`: 4건 통과, 보조/네트워크 검사 2건 기본 제외. 제외된 실제 빈 폴더 npm 설치 검사를 따로 실행해 통과했다. `quoted_web_output_tests`, `node_tools::tests`도 통과했다.
- 최신 디버그 바이너리의 `MQ Verification.app`을 격리된 pilot 데이터로 실행하고 PATH를 `/usr/bin:/bin:/usr/sbin:/sbin`으로 제한했다. 실제 Tailwind 수업 `java-tailwind-2`의 첫 문제에서 초기 미리보기 성공, font-normal 제출 실패, font-bold 수정 후 미리보기와 제출 통과를 확인했다. 이어서 Finder에서 같은 앱을 직접 열고 첫 문제의 미리보기·정답 채점이 다시 통과하는 것을 확인했다. 이는 최신 소스 디버그 앱의 검증이며 build.97 설치 파일에 수정이 포함됐다는 뜻은 아니다. nvm만 있는 실제 별도 계정은 사용하지 않았다.
- `github_pr current_github_login` 읽기 전용 PTY 검사를 기본 환경, `GH_CONFIG_DIR=$HOME/.config/gh`, `XDG_CONFIG_HOME=$HOME/.config`에서 각각 실행해 모두 통과했다. 실제 저장소·PR 생성은 하지 않았다. Finder에서 로그인 검증 전용 앱을 여는 추가 시도는 UI 연결 시간 초과로 결과를 확인하지 못했으므로 Finder 로그인 성공 근거로 삼지 않는다.
- 로컬 `player_git_course_native`는 두 번 실행했다. 두 번 모두 앞 단계 복원, 실제 Git 그래프/중간 초기화, 분기 13단계·고급 분기 5단계·PR 8단계 화면과 터미널 검사를 통과한 뒤 해설 종료 후 `새 회차 시작` 대기에서 실패했다. 실패 화면에 Dioxus의 `Your app is being rebuilt`가 포함됐다. 앞선 CI의 초기 터미널 진입 실패와 동일 원인이라고 확정하지 않는다. 최신 CI의 Mac 성공과 로컬 재현 실패를 구분하며, 로컬 전체 네이티브 검사를 통과했다고 기록하지 않는다.
- 실제 사용자의 두벌식 입력에 대한 새 재현 근거는 얻지 못했다. Windows에서 정한 미해결 완료 상태를 수정 완료로 바꾸거나 이슈를 임의로 재개하지 않았다.

다음 우선순위는 배포를 막은 Windows Vim 입력 모드 복원 실패와 로컬 Mac 해설 종료 후 네이티브 검사의 실패 원인 분리다. 실제 두벌식 직접 입력·복사 입력 동등성은 여전히 실기기 재현이 필요하다.
