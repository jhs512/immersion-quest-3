# Compose·Dockerfile 문제도 실제 터미널에서 (2026-10-28)

사용자 요청: 「도커 문제도 터미널 환경으로 바꾸라니까 왜 자꾸 command.sh로 하는거야.」 CLI 8문제(개정 6)는 이미 실제 PTY 터미널이다. 이 문서는 남은 12문제의 전환 계획과 결과를 기록한다.

## 전환 전 경로 (확인한 사실)

| 수업 · 문제 | 학습자가 고치는 파일 | 그 밖의 준비 파일 | 실행 | 채점 |
| --- | --- | --- | --- | --- |
| 이미지·컨테이너 9 pid1-lifetime | compose.yaml | — | 코드 실행 → lab.sh(up, 3초 뒤 상태·로그) | lab.sh 출력 비교 |
| 10 volume-survives-recreate | compose.yaml | memos.txt | lab.sh(쓰기·restart·recreate·down·down -v) | 출력 비교 + 변형 자료 |
| 11 separate-volumes | compose.yaml | memos.txt | lab.sh(두 가게 쓰기·recreate) | 출력 비교 + 변형 |
| 12 layer-cache-order | Dockerfile | compose.yaml, menu.txt | lab.sh(build 두 번, 메뉴 변경) | 출력 비교 + 변형 |
| 13 final-memo-app | compose.yaml | Dockerfile, add.sh, show.sh, memos.txt | lab.sh(빌드·쓰기·sed v2·재빌드·down) | 출력 비교 + 변형 |
| 네트워크 1 service-name | compose.yaml | www/index.html | lab.sh(up web, run client) | 출력 비교 + 변형 |
| 2 bind-address · 3 network-membership | compose.yaml | www/index.html | 같은 lab.sh | 출력 비교 |
| 4 final-host-port | compose.yaml | www/index.html | lab.sh(+ compose port, /dev/tcp 요청) | 출력 비교 + 변형 |
| Compose·DB 1 db-address | compose.yaml | — | lab.sh(up db, run app) | 출력 비교 |
| 2 db-volume | compose.yaml | — | lab.sh(표 생성·restart·recreate·down) | 출력 비교 |
| 3 final-migration | migration.sql | compose.yaml, init.sql | lab.sh(init 교체·recreate·migration·조회) | 출력 비교 + 변형 |

모든 문제가 `language: docker`, `files.lab.sh`, `tests`로 판정했고, 제출은 lab.sh를 별도 채점 프로젝트에서 다시 실행했다. 학습자가 명령을 입력하지 않았다.

## 계획 (최소 변경)

- 같은 `git_terminal.docker`를 쓴다. `docker.compose`가 있으면 파일 편집기 + 실제 터미널 실습이다. Java 빌드 실습의 「편집기 → 같은 폴더에 저장 → 터미널」 구조를 그대로 넓힌다.
- 작업 폴더는 문제마다 하나(`GitPracticeStore`, 문제 ID 범위)다. 시작 파일은 `shell.start`, 해설은 `shell.demo`, 정답 파일은 `shell.goal`에 둔다. 편집기는 `compose.editable` 파일만 보여 주고 입력할 때마다 그 폴더의 실제 파일에 저장한다. 터미널에서 파일을 바꾸면 편집기도 디스크 내용을 다시 읽는다.
- Compose 프로젝트는 문제마다 소유 프로젝트 하나(`mq3lab-…`, 소유 영수증·잠금·감시자 포함)를 수업 세션 동안 유지한다. 해설은 문제마다 별도 프로젝트를 매번 새로 만든다. 초기화는 그 문제의 학습자 프로젝트만 지우고 새로 만든다. 수업을 나가면 라벨이 붙은 것만 정리한다(기존 `remove_project`).
- 터미널의 `docker compose`는 보호 함수가 `-p`·`-f`를 고정하고 쓰기 명령 전에 현재 compose.yaml·Dockerfile이 앱의 기존 검사(`compose_problem`·`dockerfile_problem`: 127.0.0.1 빈 포트, 실습 폴더 밖 바인드 금지, 고정 이름·host 네트워크·권한 금지, 고정 이미지)를 통과했는지 확인한다. 앱은 Enter를 셸에 보내기 직전 파일 해시가 바뀌었으면 다시 검사해 판정 파일을 쓴다. 판정이 없거나 해시가 다르면 실행하지 않는다.
- 채점(`check_docker`)은 실행하지 않는다. 읽기만 한다: 학습자 셸이 성공으로 마친 명령(순서), 그 명령을 입력할 때의 설정 파일이 지금 파일과 같은지(Enter 기록), Compose 설정(`docker compose config`), 서비스 컨테이너의 실제 상태·현재 파일로 만든 것인지(config-hash 라벨), 마운트, 로그, 컨테이너 안 읽기 명령(cat·psql SELECT), 빌드 이미지의 레이어 기록, 127.0.0.1 공개 포트의 실제 응답.
- 해설은 해설용 편집기에서 실제로 고치고 해설용 터미널에 명령을 입력해 실제 출력을 읽는다. 관리자 자동 풀이는 같은 편집과 명령을 학습자 편집기·터미널에 입력하고 같은 채점기가 정한다.
- 검증기는 정답 파일을 쓰고 명령을 터미널에 입력해 통과를, 시작 파일과 기록된 오답 파일은 같은 명령 뒤 실패를, 다른 정답은 통과를 확인한다(실제 PTY·Docker).
- 문제 ID·목표·진도는 유지한다. 수업 개정은 이미지·컨테이너 7, 네트워크 4, Compose·DB 5다. 처음 계획한 네트워크 3·Compose·DB 4는 다른 작업(전체 해설 감사)이 이미 원격 태그로 게시해 쓰지 않는다(2026-10-28 `git ls-remote --tags`로 확인).

## 구현 (2026-10-28)

- 앱: `DockerExercise.compose`(`src/docker_practice.rs`)에 이미지 목록, 편집 파일, 고정 파일(`same_files`), 읽기 전용 확인 항목(`ComposeCheck`: config·running·mount·logs·exec·file·history·http)을 둔다. CLI 문제의 형식은 그대로다.
- 편집기: `src/git_terminal_ui.rs`가 Java 빌드 실습과 같은 자리(터미널 위)에 편집 파일 탭을 보여 준다. 입력은 `save_editable`로 터미널 폴더의 실제 파일에 바로 저장한다. 0.5초마다 디스크를 다시 읽어 터미널에서 바꾼 내용도 편집기에 보인다.
- Enter 직전: 화면(또는 검증기)이 `refresh_docker_files`를 부른다. 고정 파일의 해시를 그 명령 번호와 함께 기록하고, compose.yaml·Dockerfile·.env가 바뀌었으면 `compose_folder_problem`으로 다시 검사해 판정 파일을 쓴다.
- 보호 함수(`TERMINAL_GUARD`, `src/docker_lab/terminal.rs`): `docker compose`는 `-p 이 문제의 프로젝트 -f 이 폴더의 compose.yaml`로만 실행한다. 쓰기 명령(up·down·run·exec·build…)은 판정 파일의 해시가 지금 파일과 같고 판정이 ok일 때만 실행한다. `-f`·`-p` 같은 전역 옵션, `--rmi`, `--push`, run·exec의 `-v`·`-p`·`--service-ports`·`--privileged`·`--cap-add`는 막는다. `docker volume|network ls|inspect`는 조회만 허용한다.
- 세션: `LessonSession::terminal`이 Compose 문제마다 소유 프로젝트 하나를 만든다(`learn:<문제>`). 해설은 매번 새 프로젝트(`demo:<문제>`)다. 초기화는 그 문제의 학습자 프로젝트만 지운 뒤 새로 만든다. 수업을 나가면 모든 소유 프로젝트를 라벨로만 정리한다. 고정 이미지는 처음 열 때 미리 받는다(학습 목표가 아니어서). 그 밖의 컨테이너·볼륨·빌드는 학습자의 명령만 만든다.
- 채점(`check_compose`): ① 해시 기록상 지금 고정 파일로 입력해 성공한 명령이 순서대로 있는가 ② 지금 파일이 실행 가능한가 ③ 엔진 상태: 서비스 컨테이너가 실행 중이고 config-hash 라벨이 지금 파일의 `docker compose config --hash`와 같은가, 마운트, 로그, 컨테이너 안 `cat`·psql SELECT, 빌드 이미지의 `docker history` 순서, 127.0.0.1 공개 포트의 실제 HTTP 응답. 채점은 서비스를 시작·빌드·변경하지 않는다.
- 수업 원본: `tools/principles_lessons/compose_terminal.py`(공통 도우미), `d1_image_container.py`(9~13번), `d2_network_ports.py`, `d3_compose_db.py`, `docker_common.py`. `make.py`는 Compose 문제의 해설 편집(patch_code `file`)이 정답 파일로 끝나는지 확인한다. `build-redesigned-git.py`는 편집 중인 파일 기준으로 `code:` 강조를 검사한다. `setup`은 시작 상태에서 먼저 입력하는 명령(채점은 엔진 상태로)이다.
- 해설·자동 풀이: 해설은 해설용 편집기에서 `patch_code`(필요하면 탭 전환)로 고치고 해설용 터미널에 명령을 입력한다. 관리자 자동 풀이(`auto_review::plan`)는 같은 편집을 학습자 편집기에, 같은 명령을 학습자 터미널에 입력하고 채점기가 판정한다.

## 검증 결과 (2026-10-28, Windows 11 · Git Bash · Docker Desktop)

### 실제 PTY·Docker 채점 (`validate_redesigned_lesson`)

검증기는 정답 파일을 쓰고 명령을 실제 PTY 터미널에 입력해 통과를, 시작 파일과 기록된 오답 파일은 같은 명령 뒤 실패를, 다른 정답은 통과를 확인한다. 해설은 해설용 프로젝트에서 재생해 실제 출력을 `recorded/*.json` 패턴과 비교한다. 아래는 현재 수업 파일 해시로 새로 돌린 결과다(`target/docker-compose-terminal-3/<수업>.json`·`.log`).

| 수업 · 개정 | 수업 파일 SHA-256 | 문제 | 오답 거절 | 다른 정답 통과 | 시간 | 결과 |
| --- | --- | --- | --- | --- | --- | --- |
| 이미지·컨테이너 `docker-image-container-7` | `236a6fd842dee543a6eb5b20da9b39c4f4e829a3e75ef4a47e2fa5418805e6c3` | 13 (CLI 8 + Compose 5) | 7 | 4 | 416.39s | 통과, exit 0 |
| 네트워크 `docker-network-ports-4` | `4e34655320981dafb72251dee6efe525a3bc45d5948abdc08cdc1d9228f542f4` | 4 | 2 | 0 | 168.86s | 통과, exit 0 |
| Compose·DB `docker-compose-db-5` | `8a2fe5dd5ebab9ee136648d0597b726cd8c42bb13d917e78c5eabb21c875b14f` | 3 | 3 | 0 | 167.56s | 통과, exit 0 |

세 결과 파일의 `lesson_sha256`이 현재 `courses/redesigned/*.json`의 해시와 같다. 각 결과의 `native_ui_verified:false`, `voice_listened:false`는 검증기 자신이 화면·음성을 보지 않았다는 뜻이다(화면은 아래에서 따로 확인).

`target/docker-compose-terminal-2`의 이전 결과(이미지·컨테이너 412.54s, 네트워크 167.70s, Compose·DB 173.98s)는 그 뒤 수업 파일이 바뀌어(이미지·컨테이너 13번 해설 수정, 네트워크 해설 수정, 두 수업의 개정 번호 변경) 현재 해시의 근거가 아니다.

### 실제 PTY·Docker 통합 시험 (`cargo test --test docker_cli_terminal -- --ignored`)

다섯 시험 모두 통과했다. `target/docker-cli-terminal-ignored-final.log`의 한 번 실행에서 앞의 세 시험이 통과했다. 네 번째 시험 `compose_steps_run_the_edited_files_in_the_real_terminal_and_grade_only_current_work`가 도는 중에 이전 작업이 시간 초과로 끝나면서 시험 프로세스도 함께 끝났다. 그래서 이 로그에는 네 번째·다섯 번째 결과가 없다. 남은 소유 자원(컨테이너 `mq3lab-18f3f324-55ebf506b2-web-1`은 healthy 상태로 127.0.0.1 공개 포트를 가졌고, `mq3-test-developer-55507f09`와 네트워크도 남았다)으로 보아 정답 파일 `up`까지는 진행했다. 멈춘 것이 아니라 바깥에서 중단된 것이다. 이 자원들은 정확한 이름으로만 지웠다. 그 뒤 두 시험을 하나씩 다시 돌렸다.

- `compose_steps_run_the_edited_files_in_the_real_terminal_and_grade_only_current_work`: 통과, 35.53s (`target/docker-cli-terminal-compose-single.log`)
- `docker_cli_steps_run_in_the_real_terminal_and_grade_the_real_engine`: 통과, 61.29s (`target/docker-cli-terminal-engine-single.log`)

두 실행이 끝난 뒤 Docker에 시험 자원이 남지 않았다. 이 시험들을 빌드하면 `target/debug/molip-quest.exe`가 다시 링크되어 해시가 `1f8928f0…`로 바뀐다. 소스는 23:45 뒤로 바뀌지 않았고, 아래 화면 근거는 그 전에 기록한 앱 해시 `14577e5f…`의 것이다.

### 실제 앱 화면 (디버그 앱, 격리 검증 전송)

`node tools/design-capture.cjs tools/design-scenarios/docker-compose-terminal.cjs target/docker-compose-terminal-ui-8` 통과(exit 0, 화면 10장, `capture.json`, 단계별 `progress.jsonl`). 최종 디버그 앱(`target/debug/molip-quest.exe` SHA-256 `14577e5f0d380779…`, `target/docker-final-app.sha256`)과 이미지·컨테이너 수업(`리` 고정 코스, 현재 해시 `236a6fd8…`)에서 확인했다. 같은 코드의 직전 빌드(고정 코스 `넷`·`콤`만 다름)로 돌린 `ui-7`도 통과했다. 같은 최종 앱에서 CLI 8문제 시나리오(`tools/design-scenarios/docker-terminal.cjs`)도 다시 통과했다(`target/docker-terminal-ui-7`, 화면 13장: 실제 pull·run·ps 출력, 자동 풀이 칩 상태 점 안쪽 여백, 해설용 별도 터미널의 실제 `docker logs`, 학습자 터미널 자동 풀이).

- 9번: compose.yaml 편집기가 「실제 Docker 터미널」 위에 있고 코드 실행 버튼·lab.sh·commands.sh 안내가 없다. 아무것도 입력하지 않은 제출은 실패한다. `docker compose up -d` → `ps -a`에 실제 Exited가 보인다. 편집기에서 키보드로 ` &`를 지우면 터미널 폴더의 실제 파일이 바뀌고(`grep sleep compose.yaml`로 확인) 다시 up·ps·logs 뒤 제출이 통과한다. 그 뒤 파일을 한 글자 바꾸면 「바꾸기 전」 명령으로 표시되며 실패하고, 되돌리면 다시 통과한다.
- 10번: 해설은 「해설용 별도 Docker 터미널」과 해설용 편집기에서 실제 `cat: can't open '/memo/list.txt'` 오류를 보여 준 뒤 volumes를 편집하고 recreate 뒤 실제 `우유`를 읽는다. 해설 전후 학습자 터미널 글자와 학습자 compose.yaml이 완전히 같다.
- 13번: 편집기 탭 compose.yaml·show.sh. 관리자 자동 풀이가 해설 재생 → 이 문제의 시작 상태로 초기화 → 학습자 편집기에서 두 파일 편집(디스크 파일 내용 변경 확인) → 학습자 터미널에 `docker compose up -d --build`·`exec app sh /app/add.sh 우유`·`--force-recreate`·`show.sh` 입력 → 실제 `[v2] 우유` → 채점 통과 → 통과 기록 저장까지 약 130초에 끝났다(해설 속도 3배, 목소리 끔).
- 알림 줄과 파일 탭이 1440px·760px(다크)에서 겹치지 않는다(간격 0px, 아래 결함 2).
- 수업을 나가면(← 코스 수업 목록) 이 실행이 만든 소유 프로젝트 7개의 자원 13개(컨테이너·볼륨·네트워크·빌드 이미지)가 20초 안에 모두 사라졌다. 이름이 아니라 라벨로 확인했다.

### 이 화면 검증에서 찾아 고친 앱 결함

1. 편집기 저장과 디스크 다시 읽기의 경합(`src/git_terminal_ui.rs`). 0.5초마다 도는 디스크 확인이 파일을 읽은 뒤 잠금을 풀고 「앱이 마지막으로 저장한 내용」과 비교했다. 그 사이 다음 글자가 저장되면 자기 저장을 바깥 변경으로 오인해 편집기를 한 글자 전 내용으로 되돌렸다. 해설 편집은 「코드가 바뀌었어요. 해설을 다시 재생해 주세요.」로 멈췄고(`target/docker-compose-terminal-ui-4`, 10번), 학습자 입력도 한 글자를 잃을 수 있었다. 저장+기록과 읽기+비교를 같은 실습 잠금 안에서 하도록 고쳤다.
2. 좁은 화면에서 Docker 알림이 파일 탭 아래로 깔림(`assets/player-workspace.css`). 시작 상태 복원 알림이 함께 보이면 알림 줄이 136px인데 `auto` 행이 편집기 행이 남긴 77px만 받아 탭이 59px 겹쳤다(`target/docker-compose-terminal-ui-6/failure.png`, `target/docker-compose-layout-probe-2`). 첫 행을 `min-content`로 바꿨다. 시나리오가 두 폭에서 겹침을 검사한다.

`ui-3`(이전 작업 시간 초과로 13번 자동 풀이 도중 중단)·`ui-4`(결함 1)·`ui-6`(결함 2)의 실패 기록은 그대로 둔다. `ui-5`는 결함 1 수정 뒤, 결함 2 수정 전의 통과 기록이다. 각 실패는 시나리오의 단계별 기록과 화면으로 원인을 확인한 뒤 앱을 고쳤고, 검사를 느슨하게 하지 않았다.

### 확인하지 않은 것과 제한

- macOS(실제 PTY·Docker Desktop)는 실행하지 않았다. Windows 디버그 앱만 확인했다.
- 일반 `cargo test`(무시한 시험 제외): lib·bin과 나머지 시험 대상은 통과했다. 다만 이 브랜치와 관계없는 기존 실패가 있다. `java_code_guide` 2개와 `lesson_registry` 1개가 실패한다. `kpc_learning`·`narration_replay`·`solutions_pass`는 이 작업 폴더에 git이 무시하는 `courses/kpc-solutions.json`이 없어 컴파일되지 않는다. `redesigned_java_conditions`는 전체 실행 부하 속에서 한 번 메시지 없이 실패했고, 따로 돌리면 통과했다(60.62s).
- 실제 음성은 듣지 않았다. 화면 시험은 목소리를 끄고 자막·동작·실제 출력만 확인했다.
- 실제 앱 화면은 이미지·컨테이너 9·10·13번만 거쳤다. 11·12번과 네트워크(4문제)·Compose·DB(3문제)는 위 검증기(실제 PTY·Docker, 앱 채점기)로만 확인했고 앱 화면으로는 열지 않았다. 관리자 자동 풀이도 화면에서는 13번만 실행했다.
- `design-capture.cjs`는 끝날 때 앱 프로세스 트리를 강제로 끝내므로 정리 감시자도 함께 끝난다. 그때 남은 소유 프로젝트는 다음 앱 시작의 `sweep_stale`이 지운다(이번에 강제 종료된 실행의 프로젝트 2개가 다음 실행 시작 때 사라진 것을 확인). 일반 종료는 수업 세션 정리(`Lab` drop)가, 앱 프로세스만 비정상 종료되는 경우는 남은 감시자가 정리하도록 되어 있다(코드 기준, 이번 화면 시험에서 따로 관찰하지 않음).
- 디버그 앱은 Dioxus 개발 재빌드 감시를 켠다. 화면 시험 중 소스를 고치거나 같은 크레이트를 빌드하면 「Your app is being rebuilt」가 뜬다. 증거 실행 중에는 빌드하지 않는다.

### 게시 순서

1. `git_terminal.docker.compose`를 이해하는 앱을 먼저 릴리스한다. 이전 앱은 이 수업 파일을 검증하지 못한다.
2. 이 브랜치의 수업 내용을 해설 감사 변경(c60e491, 97e5c6f)과 합친다. 합친 뒤 `make.py --only docker-image-container docker-network-ports docker-compose-db` → `build-redesigned-git.py --lesson …` → `build-redesigned-course-bundle.py` → 검증기를 다시 돌리고, 그 해시로만 게시한다.
3. 원격 태그를 다시 확인해 비어 있는 다음 개정으로 수업 저장소에 게시한다(지금 이 브랜치: 7·4·5). 게시된 태그는 다시 쓰지 않는다.
4. 마지막으로 코스 참조(`java-backend.json` 핀)를 게시한다.

## 해설 감사·첫 자바 수업과 합치기 (2026-10-29)

통합 브랜치 `codex/docker-terminal-integration-20261029`(합친 커밋 `0ce5423`)는 이 브랜치의 세 커밋과 해설 전수 감사(c60e491 `:wq` 읽기, 97e5c6f), 이미 게시된 첫 자바 수업 해설(java-values-7, `4d05d28`)을 합쳤다.

- 충돌은 Docker 세 수업의 생성 파일(content.json·해설 캐시·수업 파일)과 공유 목록(catalog·course-prd·java-backend.json·고정 코스 넷·리·콤·narration-review.json)의 Docker 항목뿐이었다. 앱 코드는 충돌 없이 이 브랜치의 코드에 `assets/speech/pronunciation.js`(`:wq`)만 더해졌다.
- 감사의 Docker 덮어쓰기 55개(`narration-overrides.json`) 중 42개는 commands.sh·lab.sh 시절의 문장이라 터미널 해설에 없다. 같은 결함이 터미널 해설에 남은 곳만 템플릿에서 말(text·say)만 고쳤다: CLI 8문제의 첫 문장이 본문을 다시 읽던 것을 시작 상태를 말하게 바꿨다(`cli_step(opening=…)`). pid1-lifetime은 문제 도입을 반복하지 않는다. 네트워크 1·2번과 마이그레이션 문제는 본문을 읽는 대신 시작 조건을 말한다. 조심하세요 강조 대상과 「루프백」 대신 127.0.0.1은 이미 감사와 같았다. 그래서 Docker 덮어쓰기 항목은 지우고 다른 수업의 항목은 그대로 둔다.
- 다시 만들기: `make.py --only …` → `make.py --review --only …` → `build-redesigned-git.py --lesson …`(세 수업) → `build-redesigned-course-bundle.py`(`--check` 통과). 바뀐 핀은 Docker 세 개뿐이고 java-values-7과 나머지 91개 핀, 수업 순서는 같다. 수업 파일은 이 브랜치의 검증본과 말(text·say)만 다르고, 네트워크 2번은 첫 말이 「…문제예요」가 아니게 되어 빌드가 제목 도입 한 줄을 앞에 붙였다.

### 합친 해시의 실제 PTY·Docker 검증 (Windows 11 · Docker Desktop)

`target/docker-terminal-integration/<수업>.json`·`.log`, 세 수업을 동시에 실행.

| 수업 · 개정 | 수업 파일 SHA-256 | 문제 | 오답 거절 | 다른 정답 통과 | 시간 | 결과 |
| --- | --- | --- | --- | --- | --- | --- |
| `docker-image-container-7` | `ae6179e1de3e845b9b748c56bf1ce8a238ec226be99a5e15b9874e918e6cad34` | 13 | 7 | 4 | 427.94s | 통과, exit 0 |
| `docker-network-ports-4` | `20ef970dcc288fc2d2b09aedd13271a97a811433e8d4faa2124cc6d13fa3c28c` | 4 | 2 | 0 | 183.46s | 통과, exit 0 |
| `docker-compose-db-5` | `dede8d94e4558461ed35909d0824fe8c3ed904b12b5d79d1bad39d0a3104fa8c` | 3 | 3 | 0 | 186.70s | 통과, exit 0 |

실행 뒤 `mq3`로 시작하는 컨테이너가 남지 않았다. 바뀐 해설 문장은 앱 화면·음성으로 다시 확인하지 않았다(위 화면 근거는 말만 다른 이전 해시의 것이다).

그 밖의 확인: `node assets/speech/symbols-lexicon.test.mjs`, `cargo test --test bundled_courses` 통과. Python 검사 `test_narration_review`·`test_lesson_classification`·`test_backend_sequence`·`test_lesson_registry`·`test_lesson_prd`·`test_publish_principles_expansion` 통과. `test_redesigned_highlights`(1개, bash-basics)와 `test_narration_openings`(32개)는 합치기 전 `4d05d28`과 같은 항목이 실패한다. `cargo test --test java_code_guide`(h2-memory-file·java-arrays 기대값)와 `--test lesson_registry`(수업 수 925≠871)도 합치기 전부터 실패하며 Docker·java-values와 관계없다.

게시는 `tools/publish-docker-terminal.py --runtime-release <태그> --runtime-commit <커밋> [--publish]`로 한다. 공개 릴리스(설치 파일 .exe·.dmg)가 그 커밋을 포함해야 하고, 위 증거의 해시가 수업 파일과 같아야 하며, 원격 코스의 세 핀이 6·3·4(또는 이미 7·4·5)여야 한다. 태그가 이미 있으면 같은 바이트일 때만 진행한다. 코스에서는 세 핀과 미리보기만 바꾼다.
