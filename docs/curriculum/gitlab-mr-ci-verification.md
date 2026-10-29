# GitLab MR · CI/CD 전환과 해설 코드 입력 검증 (2026-10-29)

계획: `docs/plans/2026-10-29-gitlab-mr-ci.md`. 이 문서는 실제로 실행한 확인과 그 한계만 적는다. 비밀번호·토큰·연결 설정은 적지 않는다.

## 게시 대상 수업 바이트

| 수업 키 | 개정 | 스키마 | 스텝 | sha256 |
| --- | --- | --- | --- | --- |
| `github-pr` (표시 제목 GitLab MR, 진도 호환용 키 유지) | `gitlab-mr-1` | 3 | 9 (8개 기존 ID + 새 종합 도전) | `645c6e9835fd2b4d6647456fc174a9c28ed491bdc1ab7e5ea286144aaaa5047c` |
| `git-remote` | `git-remote-13` | 2 | 23 | `67b5559012082f36365a7f8dbc69549751fcd16ea38f952dd21b3add8565f749` |
| `gitlab-ci` (새 선택 수업, 파일럿 갓) | `gitlab-ci-1` | 3 | 10 | `0260002ec98eaf2b30de90bc840f7f4820b7b093d4c5859a12aa0f53f17694f0` |

백엔드 과정 묶음 `courses/redesigned-courses/java-backend.json`: 44수업·438스텝. 원격 과정과의 차이는 위 세 수업의 고정 값, 미리보기 세 개, MR 종합 도전 지정뿐이다(원격 43수업과 나머지 고정 값·순서 동일, 2026-10-29 확인).

## 실제 로컬 GitLab 실행 (모의가 아님)

환경: GitLab CE 19.5.1(고정 다이제스트), 루프백 게이트웨이, 관리자가 아닌 전용 실습 계정, 공식 glab 1.126.0, Alpine 작업만 허용한 Docker Runner.
게이트웨이는 앱에 포함된 `assets/gitlab/lab.py`·`http_client.py`(표준 라이브러리만) 사본을 앱과 같은 방식(데이터 폴더의 `gitlab-lab-tools`)으로 실행했다. 예전 독립 실행 게이트웨이(requests 기반)는 명령줄로 소유를 확인한 뒤 멈췄다.

- `actual_gitlab_mr_lifecycle_passes_each_stage_and_rejects_unmerged_final` 통과.
- `authored_mr_lesson_commands_pass_their_own_graders_in_order` 통과: 수업이 학생에게 주는 명령 그대로 9스텝 모두 채점 통과. 종합 도전은 앱과 같은 작업 공간 규칙(`workspace_group`별 분리)에서 작업 전에는 통과하지 않음. (이전 테스트는 모든 스텝을 한 작업 공간에 열어 앱과 달랐고, 이를 앱 규칙으로 고쳤다.)
- `every_authored_pipeline_rejects_its_starter_and_accepts_actual_fixed_jobs_and_artifacts` 통과(219초): 10스텝 모두 시작 상태는 거절, 고친 커밋은 실제 파이프라인·작업 상태·로그·산출물·작업 순서·제외된 브랜치 작업으로 통과.

### 이번에 찾아 고친 학생 노출 결함

새로 넣은 `glab ci status --live` 단언이 실제 터미널(PTY)에서 실패했다. `--live`는 파이프라인이 끝난 뒤 「Choose an action: View logs / Retry / Exit」 선택 메뉴를 띄우고 프롬프트로 돌아오지 않는다. 수업 9곳이 이 명령을 안내했다. glab 도움말이 밝히는 `--wait`(끝날 때까지 기다리고 프롬프트 없이 출력)로 바꾸고 다시 생성했다. 다시 실행한 결과 `success`가 출력되고 프롬프트로 돌아왔다. `gitlab-ci-1`은 아직 게시 전이라 개정 번호를 유지했다.

## 네이티브 앱 확인 (격리된 파일럿 프로필, 실제 계정·진도 없음)

`target/debug/molip-quest.exe`를 `MOLIP_PILOT`과 일회용 데이터·WebView 폴더로 실행하고 DevTools(루프백)로 조작했다.

- GitLab CI 수업(갓) 1·2스텝: 해설이 자기 데모 터미널·자기 프로젝트에서 명령을 실행하고 학생을 통과시키지 않음. `.gitlab-ci.yml`·`check.sh` 편집 탭, 해설의 줄 강조, 학생 편집→`git push`→`glab ci status --wait`(프롬프트 복귀)→실제 파이프라인 채점 통과. 수업 목록으로 나가자 이 실습 소유의 GitLab·Runner 컨테이너가 모두 멈춤(볼륨 유지).
- MR 수업은 위 실제 PTY 테스트로 9스텝을 확인했다. 네이티브 화면에서 MR 9스텝 전체를 다시 돌리지는 않았다.

## 해설 코드 자동 입력 수정

원인: `assets/layout/agent.js`의 `animateEdit`가 바꿀 조각(`before`) 전체를 뒤에서부터 지우고 `after`를 다시 쳤다. `before`가 줄바꿈으로 끝나면 지우는 동안 다음 줄(`    }`)이 올라붙어 `return fee + 1    }`처럼 보였다. 편집기 자동 괄호·들여쓰기와는 관계없다(프로그램 입력은 입력 이벤트가 아님).

수정: 단어·공백·줄바꿈 단위 차이(Myers)만 지우고 친다. 같은 결과가 되는 위치가 여럿이면 다음 줄을 그대로 두는 위치(줄 끝)를 고른다. 위치만 고르므로 최종 바이트·Python 들여쓰기·문자열·주석·한 줄 구문은 저자가 쓴 그대로다. 끝 바이트가 목표와 다르면 해설을 멈춘다. `assets/layout/auto-run.js`의 문자열 `replace`는 `$&`·`$1`을 특수 패턴으로 해석하므로 split/join으로 바꿨다(현재 수업에는 해당 패턴 없음).

- `tests/js/narration-edit-plan.test.cjs`: 모든 과정 파일의 해설 편집을 실제 시작 코드부터 순서대로 재생(patch 650·set 236·type 514, 다른 파일 탭 등 465개는 두 맥락). 매 중간 상태에서 바뀌지 않는 위·아래 줄이 온전한지, 끝 바이트가 목표와 같은지 확인. CRLF·한국어·결합 이모지·`$&`·템플릿 문자열·중첩 블록·줄 삽입/삭제 포함.
- 같은 기준에서 이전 알고리즘은 활성 patch 1,115개 중 159개가 다음 줄을 올려 붙였고, 새 알고리즘은 0개다.
- `tests/js/narration-edit-editor.test.cjs`: 실제 CodeMirror 번들에서 스크린샷의 Java 문제, 일시정지·재개, 멈춤 후 학생 코드 복원, 반복 재생 동일성.
- 네이티브 파일럿에서 「자바 · 계산을 메서드로 나눠요」 1번 해설을 `return fee + 1;` 순간에 멈춰 화면을 확인: `}`가 다음 줄에 그대로 있음. 7타 입력 뒤 목표와 정확히 같고 해설 뒤 학생 코드가 복원됨.

이 수정은 앱 바이너리(`include_str!`)에 들어가므로 앱 배포가 필요하다. 수업 콘텐츠·해설 캐시는 바꾸지 않았다.

## 구조 검사

- `cargo test --locked --lib --test gitlab_platform --test challenges --test backend_journeys --test bundled_courses --test course_guide --test lesson_registry --test github_pr` 통과(분류 회귀 해결: `backend_journeys` 통과).
- `tests/python/test_gitlab_gateway.py` 4개 통과(`-W error::ResourceWarning`).
- `tools/test_lesson_registry.py`: 새 CI 수업으로 97→98로 기대값 갱신 후 통과.
- 해설 기록부는 바뀐 21개 항목(MR 9, 원격 2, CI 10)만 갱신, 삭제 0.

- `tests/java_code_guide.rs`: 브랜치 이전부터 실패(릴리스 워크플로에는 없는 테스트). 원인은 낡은 기대값이었다. `eb65c184`가 `java_libraries` 과제에도 코드 안내를 붙였고(테스트는 그 언어를 비자바로 취급), `8a22394f`가 Java 12개 수업의 보기 고르기를 코딩·터미널 과제로 바꾸면서 테스트가 가리키던 스텝 3개가 사라졌다. 학생 안내는 실제 화면과 맞으므로 테스트를 고쳤다: `java_libraries` 포함, 현재 배포되는 경우(터미널 Main.java 편집 포함)를 확인, 앱이 여전히 지원하는 「조각 조립」·「터미널+보기」 화면은 퇴역한 실제 과제 정의(`tests/fixtures/java-code-guide-retired-tasks.json`)로 계속 확인. 2개 통과.

- 메인 `92b37e2a`의 데스크톱 릴리스(run 40826768538)가 실패해 있었다. 원인 두 가지를 고쳤다.
  - macOS `player_bash_native`: `92b37e2a`가 Bash 수업에 24번째 종합 도전을 붙였는데 `tools/player-pilot-bash.js`는 문제 버튼 23개를 기다렸다(화면은 `0/24`). 24로 고침. 같은 이유로 `tools/player-pilot-loading.js`(aice-plots 10→11, git-first 6→7)도 고침.
  - Windows `challenges::a_future_problem_runs_on_the_existing_grader`: 병렬 실행 중 `java --version` 10초 제한 초과(「JDK 버전 확인 시간이 초과됐어요.」). 릴리스 워크플로에서 `java_arguments`와 같은 방식으로 `challenges`를 따로 `--test-threads=1`로 돌린다(두 플랫폼).
- 같은 이유(종합 도전이 끝에 붙음)로 깨져 있던 수업별 해설 재실행 테스트 10개(`redesigned_aice_*` 5, `redesigned_engineer_c*` 3, `redesigned_java_arrays`·`redesigned_java_conditions`)의 스텝 수를 고쳤다. 앞 스텝 ID 순서는 그대로임을 확인했다. AICE·C 8개는 교사 실행 표를 가르치는 스텝으로 한정했다(종합 도전은 `docs/curriculum/final-challenges-evidence.md`의 실제 채점 증거가 다룬다). 모두 통과.
- 같은 macOS 실행에서 Bash 실패 뒤 돌지 못한 네이티브 테스트를 이 컴퓨터(Windows)에서 모두 돌렸다. 숨은 실패 3개를 고쳤다.
  - `player_java_launch_native`·`player_java_arguments_native`: 종합 도전 9번째 스텝 때문에 확인 항목이 12→13. 자바 인자 종합 도전은 실행 명령을 학생이 정하게 하려고 작성 명령이 `cat Main.java`뿐이라, 검증 스크립트가 자바를 실행하지 않아 채점기가 올바르게 거절했다. `tools/player-pilot-java-launch.js`가 작성 명령에 `java` 실행이 없으면 스텝의 실제 `java_build.command`를 따옴표 처리해 실행한다.
  - `player_git_course_native`: git-branch 14→15, git-branch-advanced 5→6. 예전 GitHub PR 화면(풀) 검사(첫 단계만 새 회차, GitHub 동의 문구)는 더 이상 활성 수업에 없고, GitLab MR 터미널은 Docker GitLab을 띄우므로 Docker가 없는 릴리스 러너에서 돌 수 없다. 이 크로스 플랫폼 검사에서 풀을 뺐다(확인 항목 7→5). MR 수업은 `tests/gitlab_platform.rs`(구조, 로컬 실습의 실제 MR)로 확인한다. **커버리지 변경으로 명시한다.**
  - `player_loading_native`: 이 작업 트리의 `target/ml-env`에 `edge_tts`가 없어 음성 단계가 실패했다(환경). CI와 같은 `edge-tts==7.3.1`이 있는 Python을 `MOLIP_PYTHON`으로 지정해 다시 돌려 8개 항목 모두 통과(실제 Edge 음성 다운로드 포함).
  - 결과: macOS 릴리스 목록의 네이티브 테스트 12개(`player_toolbar`·`course_identity`·`lesson_link`·`progress_exit_process`·`loading`·`java_launch`·`java_arguments`·`git_course`·`bash`·`async_progress`·`course_guide`·`content_submit`) 모두 Windows에서 통과. macOS 자체 실행은 릴리스 워크플로 결과로 확인한다.
- `tests/step_reset.rs`: MR 9번째 종합 도전은 별도 작업 공간(`gitlab-mr-final`)·별도 프로젝트라 초기화가 허용된다. 2~8번은 계속 거절되는지 확인하도록 고침. 통과.

브랜치 이전부터 실패하던 검사(HEAD에서 같은 결과로 확인, 이번 변경과 무관): `tools/test_lesson_classification.py`(KeyError 'aice'), `tools/test_narration_openings.py`(과거 기준선 비교 89건; `github-pr`는 의도한 GitLab 전환으로 1건 추가), `tools/test_redesigned_highlights.py`(bash-basics). JS 테스트 중 Playwright 기본 Chromium·WebKit을 쓰는 4개는 이 컴퓨터에 해당 브라우저가 없어 실패하며, Edge로 바꾸면 Chromium 변형은 통과한다.

## 한계

- macOS Docker에서의 실제 실행은 확인하지 않았다(코드 검토만).
- GitHub 테스트 저장소·실제 GitHub PR 실험은 보류 지시대로 하지 않았다.
- 한 테스트 환경에서 두 개의 도우미 사본 경로를 썼기 때문에, 나중에 시작한 사본의 `stop`은 앞 사본의 게이트웨이를 끄지 않았다(경로로 소유를 확인하는 안전장치). 앱은 한 경로만 쓰므로 해당하지 않으며, 남은 테스트 게이트웨이는 명령줄을 확인해 수동으로 멈췄다.
