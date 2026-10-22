# 수업 신고 검증 · 2026-10-22

상태: **Windows 확인 완료 · Mac 부분 검증 완료**. Mac에서 확인한 범위만 아래에 기록한다.
Windows의 Chromium·WebKit 테스트는 Mac의 실제 한국어 입력기 검증을 대신하지 않는다.

| 신고 | Windows에서 확인한 범위 | Mac에서 남은 확인 |
|---|---|---|
| 플레이어 #1 | Bash 제출·한글 파일의 UTF-8/CP949/UTF-16 판독 검사를 통과했다. | 한글을 직접 입력해 첫 메모 문제를 제출한다. |
| 플레이어 #2 | 설명이 없어 원래 증상은 특정할 수 없다. 신고된 Bash 문제의 실제 명령·채점 경로는 통과했다. | 같은 단계에서 파일 생성·출력·제출을 확인한다. |
| 플레이어 #3 | 구형 한국어 로캘에서도 UTF-8 파일 생성·채점, 기존 CP949 파일의 보존·이어쓰기 검사를 통과했다. | 한글 메모 작성·출력·재실행 후 이어쓰기를 확인한다. |
| 플레이어 #4 | 조합형·완성형 한글, 네이티브 replacement 이벤트, 공백 확정 이벤트의 입력 브리지 검사를 통과했다. 중복 공백은 재현하지 못했다. | 실제 두벌식 입력기로 `echo "첫 메모" > memo.txt`를 직접 입력한다. 공백이 한 칸인지 확인한다. |
| 플레이어 #5 | 중간 단계의 새 작업 공간에 `memo.txt`가 없는 문제를 재현하고 수정했다. 빈 작업 공간에만 앞 단계 시작 상태를 준비하며 기존 작업 공간을 보존한다. | 기존 완료 기록이 있는 상태에서 새 콘텐츠를 적용하고 Git 첫 수업 3번을 바로 연다. 준비 안내·메모·준비 영역·직접 커밋·재실행을 확인한다. |
| 플레이어 #6 | 키보드·붙여넣기의 NBSP 정규화, 입력 브리지 검사를 통과했다. 신고 기록만으로 실패한 실제 명령·파일 바이트는 확인할 수 없다. | 로컬 협업 수업에서 한글 명령 직접 입력과 복사 입력을 각각 실행하고 동일한 파일과 채점 결과인지 비교한다. |
| GitHub PR 수업 #1 | 현재 로그인한 `gh` 계정을 실제 실습 PTY의 읽기 전용 `gh api user --jq .login`으로 조회해 플레이어 계정과 같음을 확인했다. | Finder에서 앱을 열고 기존 터미널 로그인과 앱 실습 터미널 로그인이 같은지 확인한다. 키체인 접근과 `GH_CONFIG_DIR`/XDG 설정의 차이도 확인한다. |

## 수정 범위

Git 연결 실습의 중간 단계를 새로 열 때, 기존 실습 폴더가 없거나 완전히 비어 있으면 해당 단계의 `demo_setup`으로 이전 상태만 복원한다. 현재 단계의 목표 동작이나 통과 기록은 만들지 않는다. 기존 내용이 있는 폴더는 변경하지 않으며, 빈 폴더를 교체해도 이전 폴더는 남긴다. 준비 사실은 실습 화면에 표시한다. 실제 GitHub 저장소 생성이나 PR 변경은 수행하지 않는다.

## 재검증 명령

```bash
node --test tests/js/terminal-ime.test.cjs
cargo test --test bash_basics --test github_pr --test git_practice_resume -- --test-threads=1
cargo test --test redesigned_git_first --test git_branch_story --test git_lesson_goals --test git_merge_goals -- --test-threads=1
cargo test --test player_git_course_native -- --ignored --nocapture
```

로그인한 개발자 환경에서만 실행하는 읽기 전용 검사:

```bash
cargo test --test github_pr current_github_login -- --ignored --nocapture
```

이 검사는 저장소나 PR을 만들지 않는다. 같은 테스트 파일의 `real_github_pr_lifecycle`은 실제 저장소·PR을 생성하므로 이번 검증에 포함하지 않았다.

Mac에서는 위 자동 검사 외에 실제 한국어 입력기를 이용한 수동 검증이 필요하다. 결과를 확인하기 전에는 해결 완료로 닫지 않는다. 원본 진단 자료나 인증 정보는 이 문서에 복사하지 않는다.

## Mac 재검증 결과 · 2026-10-22

- 플레이어 #5: 실제 Mac 앱의 격리된 실습에서 이전 콘텐츠(`git-first-2`)의 1·2번 완료 기록을 넣고 현재 콘텐츠의 3번을 직접 열었다. 복원 안내, `memo.txt`의 `첫 메모\n`, Git 준비 영역을 확인했다. 커밋 전 제출은 실패하고 직접 커밋 후 제출은 통과했다. 앱 종료 후 같은 실습을 다시 열어 커밋과 추가 학습자 파일의 보존을 확인했다. 이 신고는 Mac 검증 완료다.
- GitHub PR 수업 #1: 실제 실습 PTY에서 기존 로그인 조회가 401로 실패하는 문제를 재현했다. macOS PR 실습에서 실제 HOME을 유지하도록 수정하자 읽기 전용 계정 조회 검사가 통과했다. 실제 Mac 검증 앱에서도 플레이어 계정과 PR 터미널의 계정이 같았다. Git 전역 설정은 실습 전용 파일로 계속 격리한다. Finder에서 직접 실행하는 경우와 명시적인 GH_CONFIG_DIR/XDG 설정 조합은 아직 확인하지 않아 신고는 열린 상태로 유지한다.
- 플레이어 #1·#3·#4·#6: 현재 사용자의 입력기는 한국어 두벌식이다. 다만 자동 키 입력은 실제 사용자의 조합 입력을 입증하지 못하므로 직접 입력·복사 입력 동등성 및 공백 문제의 완료 근거로 삼지 않는다. 실제 앱에서 사용자가 입력한 결과 확인이 남아 있어 열린 상태로 유지한다.
- 플레이어 #2: 설명이 없어 원래 증상을 특정할 수 없으므로 열린 상태로 유지한다.

Mac 회귀 검사: 입력 브리지 18건, Bash/Git 관련 회귀 검사, PR 실습 환경 격리 검사 통과. 실제 로그인 조회는 아래 읽기 전용 검사로 통과했으며 저장소·PR을 생성하지 않았다.

```bash
cargo test --locked --test player_student_report_git_native -- --ignored --nocapture --test-threads=1
cargo test --locked --test github_pr current_github_login -- --ignored --nocapture
cargo test --locked --test github_pr --test git_practice_resume -- --test-threads=1
```

Git 중간 단계의 실제 Mac 앱 검사는 `tests/player_student_report_git_native.rs`와 `tools/player-pilot-student-report-git.js`에 남겼다. 로그인 검증 전용 화면은 macOS 디버그 빌드에서만 `MOLIP_MACOS_LOGIN_VERIFY`로 실행하며 일반 배포 화면에는 포함되지 않는다.
