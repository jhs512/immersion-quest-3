# 수업 신고 처리 · 2026-10-23

사용자 지시: 새 수업 신고를 조사하고, 끝내 판단할 수 없는 신고는 조사 결과를 남겨 미해결 종료한다. 이전의 일괄 Mac 재검증 대기 정책을 이 지시로 대체한다. 진도·등록 이슈는 처리 대상이 아니다.

| 신고 | 판정과 근거 |
| --- | --- |
| Tailwind 수업 #1 | Node를 지정해도 npm을 PATH로 별도 실행하던 문제를 재현했다. Node와 npm을 같은 설치에서 찾고 절대 경로로 npm CLI를 실행한다. 자식 프로세스 PATH에도 선택한 Node 폴더를 넣는다. 제한 PATH 회귀 검사, 실제 npm 패키지 설치, 웹 실행·채점·미리보기 통과. 실제 Mac 입력·화면 검증은 주장하지 않는다. |
| GitHub PR 수업 #1 | 기존 수정이 macOS에서 실제 HOME을 보존해 실습 PTY의 로그인 불일치를 해결했다. 7b54336의 실제 Mac 계정 일치 검사와 현재 Windows 실습 격리 회귀 검사를 근거로 완료 처리한다. Finder 직접 실행 및 모든 GH_CONFIG_DIR 조합을 검증했다고 주장하지 않는다. |
| 플레이어 #1·#3 | 신고 플랫폼은 Windows다. 현재 실제 Bash의 UTF-8/CP949/UTF-16 판독, 한국어 구형 로캘, 기존 메모 이어쓰기 검사를 재실행했다. 기존 인코딩 보정과 신고 경로의 검증 완료로 종료한다. 신고 시점의 원본 입력 바이트는 없어 정확히 같은 상황을 재현했다고 주장하지 않는다. |
| 플레이어 #2 | 미해결 종료. 설명이 비었고 첨부 화면은 빈 Bash 프롬프트다. 진단의 환경 설치 실패를 신고 증상에 연결할 근거가 없다. 원인 수정 완료로 표시하지 않는다. |
| 플레이어 #4 | 미해결 종료. 한글 조합·공백 확정 등 Chromium/WebKit 입력 브리지 18건은 통과했으나, 실제 Mac 두벌식의 중복 공백을 재현하지 못했다. |
| 플레이어 #6 | 미해결 종료. 진단에 실패한 명령·파일 바이트가 없고 오류 이벤트도 없다. 직접 입력과 복사 입력이 달라지는 실제 Mac 입력 경로를 확정하지 못했다. |

미해결 이슈는 `미해결 완료` 라벨과 GitHub의 `not planned` 종료 이유를 사용한다. 재현 절차와 실제 결과가 추가되면 다시 열 수 있다. 원본 캡처·진단·토큰은 문서나 소스에 복사하지 않는다.

## 재검증

- `cargo test --lib managed_web_tests`: 최소 PATH에서도 선택한 Node로 npm과 자식 Node 실행, 웹 정답·오답·미리보기 검사.
- `cargo test --lib managed_web_tests::fresh_runtime_accepts_a_canonical_data_directory -- --ignored --nocapture`: 빈 별도 폴더에 실제 npm 패키지 설치.
- `cargo test --lib quoted_web_output_tests`: 실제 브라우저 재로딩 후 결과 검사.
- `cargo test --test bash_basics --test github_pr --test git_practice_resume --test redesigned_git_remote -- --test-threads=1`
- `node --test tests/js/terminal-ime.test.cjs`: 18건 통과. 실제 Mac IME 입력과 구분한다.

Node가 설치되지 않은 기기에 Node를 자동 설치하는 변경은 아니다. 명시한 `MOLIP_NODE`, 현재 PATH, 사용자 nvm·Volta·로컬 bin과 일반 설치 경로를 탐색한다. npm이 없으면 필요한 도구를 명확히 안내한다. 시스템 PATH나 사용자 셸 설정은 바꾸지 않는다.


## Mac 추가 확인

Finder에서 직접 연 최신 소스 디버그 앱에서 플레이어의 실제 GitHub 계정과 PR 실습 터미널의 읽기 전용 계정 조회가 일치했다. GH_TOKEN/GITHUB_TOKEN 및 GH_CONFIG_DIR/XDG_CONFIG_HOME을 지정하지 않은 상태였다. 명시적인 GH_CONFIG_DIR/XDG 경로의 별도 PTY 검사도 통과했다. PR 수업 #1의 Finder 추가 확인을 완료했다. 저장소·PR은 생성하지 않았다.

Mac Git 네이티브 검사의 해설 종료 후 시간 초과는 검사 코드가 다른 창의 숨겨진 멈춤 버튼을 고른 문제였다. 현재 문제의 해설 세션을 종료하도록 고친 뒤 전체 네이티브 검사가 통과했다. 자세한 원인·범위는 [Mac 인수인계](../curriculum/macos-handoff-2026-10-23.md)의 추가 검증 절에 기록했다.

두벌식 중복 공백과 직접/복사 입력 차이는 새 재현 근거가 없어 사용자 지시대로 미해결 완료 상태를 유지한다.

## Windows Vim 종료·복원 수정

`bbb3fee`를 pull한 Windows 환경에서 배포 차단 검사인 `unsaved_text_input_mode_and_cursor_survive_reopening`을 조사했다. 단독 실행은 통과했지만, 종료 표시를 기록한 뒤 Vim이 입력 모드에서 일반 모드로 전환되는 경로를 실제 PTY로 재현하면 복원 파일의 모드·커서가 덮어써졌다. 종료 처리의 타이밍에 따라 재열기가 일반 모드로 시작할 수 있는 제품 버그다.

`assets/vim/practice.vim`은 종료 표시 또는 Vim 종료 상태를 감지하면 복원 파일을 더 이상 갱신하지 않는다. 실시간 상태·검사 이벤트는 계속 기록하며, 사용자가 직접 Esc로 일반 모드로 바꾸는 정상 조작은 기존대로 저장한다. 수업 내용이나 정답 조건은 바꾸지 않았다.

추가한 `shutdown_mode_changes_cannot_overwrite_the_saved_insert_state`는 종료 중 모드 전환을 강제로 일으켜 수정 전 실패함을 확인했다. 수정 후 복원 파일 보존, 실제 재열기의 입력 모드·커서·미저장 한글 본문 복원, 이어 입력을 검증했다. Windows Vim 검사 7건(14단계 실습 포함), 실제 앱의 `player_vim_ready_native` 검사, 기존 CI 실패 검사 12회 연속 실행이 통과했다. Mac에서 새 수정 자체를 직접 실행했다고 주장하지 않는다. 새 배포 완료 여부는 새 커밋의 릴리스 CI로 확인한다.
