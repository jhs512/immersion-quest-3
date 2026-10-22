# 수업 신고 검증 · 2026-10-22

상태: **Windows 확인 완료 · Mac 재검증 대기**. 아래 신고는 닫지 않는다.
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
