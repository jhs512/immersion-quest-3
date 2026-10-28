# Docker 입문: 필요성에서 직접 실행으로

2026-10-26 사용자의 수정 요청을 반영한다. 기존 수업은 `docker run` 경험을 가정하면서 첫 문제부터 Compose YAML을 편집했다. 처음 배우는 사람이 실행 재료와 실행 상태를 구별하기 전에 여러 설정을 함께 읽어야 했다.

## 학습 흐름

수업 예고와 첫 문제에서 컴퓨터마다 설치 여부·버전이 달라지는 상황을 설명한다. Docker를 쓰지 않고도 환경을 맞출 수 있지만 반복해서 일치시켜야 한다는 점, 이미지가 프로그램과 필요한 사용자 공간 파일을 전달한다는 점을 먼저 다룬다. 모든 호스트 환경 차이를 실제로 재현했다고 주장하지 않는다. 같은 이미지가 CPU 구조·커널·외부 서비스 차이까지 없애는 것도 아니다.

그다음 학습자가 실제 터미널 프롬프트에 명령을 직접 입력하고 Enter로 실행한다(2026-10-28 개정 6부터. 그 전에는 `commands.sh`에 명령을 쓰고 코드 실행 버튼을 눌렀다).

1. `docker pull`: 실행 재료를 받지만 프로세스는 아직 없다.
2. `docker run`: 이미지에서 새 컨테이너와 프로세스를 시작한다.
3. `docker ps`: 이미지 목록과 실행 중인 컨테이너 목록을 구별한다.
4. `docker logs`: 실행 상태와 프로세스의 출력 기록을 구별한다.
5. `docker exec`: 새 컨테이너를 만들지 않고 기존 컨테이너 안에서 메모를 쓴다.
6. `docker stop`: 프로세스는 멈추고 객체는 남는다.
7. `docker start`: 같은 식별자의 컨테이너를 다시 실행한다.
8. `docker stop` 뒤 `docker rm`: 실행 중인 컨테이너의 rm이 거절되는 것을 본 뒤, 컨테이너 객체는 없어지고 이미지는 남는 것을 `docker images`로 확인한다.

이 경험 뒤에 Compose가 `run`의 이미지·명령을 파일로 기록해 실행하는 단계임을 설명한다. 기존 PID 1·볼륨·레이어 캐시·최종 도전 5개로 이어진다. 문제 수를 맞추기 위한 추가가 아니라 명령마다 다른 관찰 대상을 하나씩 분리했다.

## 실제 터미널과 수업 단위 상태 (개정 6)

2026-10-28 사용자 요청: 「도커 문제도 터미널 환경으로 바꾸라니까 왜 자꾸 command.sh로 하는거야.」 CLI 8문제는 Bash·Git 수업과 같은 실제 PTY 터미널(`src/git_terminal_ui.rs`, `SetupTerminal::open_practice`)을 쓴다. 과제 정의는 `git_terminal.docker`(`src/docker_practice.rs`)이고 언어는 `docker`로 남는다. 코드 편집기, `commands.sh`, `lab.sh`, 코드 실행 버튼은 없다.

- 터미널의 `docker`는 실제 Docker CLI이며 stdout/stderr가 그대로 보인다. `docker ps` 표에는 사용자가 원래 켜 둔 컨테이너도 나온다. 요약 문장으로 바꾸지 않는다.
- Bash에 미리 넣는 보호 함수(`TERMINAL_GUARD`, `src/docker_lab/terminal.rs`)는 run·create에 소유 라벨만 붙인다. 이 수업이 만들지 않은 컨테이너의 stop·rm·exec 등, 고정·외부 포트, 볼륨·호스트 네트워크·권한 옵션, 이미지 삭제·prune·볼륨·네트워크 명령은 실제 Docker를 부르기 전에 거절한다. 조회 명령(ps·images·logs·inspect 등)은 그대로 통과한다.
- 수업 세션(`LessonSession::terminal`)은 학습자용 프로젝트 하나와 해설용 프로젝트 하나를 수업 동안 유지한다. 문제 이동·재실행으로 컨테이너를 다시 만들지 않는다. 문제를 처음 열 때 시작 상태가 없으면 없는 것만 만든다(예: 실행 중이어야 하는데 없으면 만들어 실행). 화면에 무엇을 준비했는지 표시한다. 초기화는 이 문제의 시작 상태를 정확히 되돌린다. 해설은 해설용 프로젝트에서 매번 정확한 시작 상태로 시연한다. 수업을 나가면 소유 라벨이 붙은 자원만 지운다. 공유 이미지는 지우지 않는다.
- `$BOX`는 `<소유 프로젝트>-nginx`이다. 준비 컨테이너는 `127.0.0.1::80`으로 Docker가 고른 빈 포트에만 연결한다.
- 채점은 학습자 터미널의 Bash 기록 훅(명령 줄·종료 상태)과 이 수업 컨테이너의 실제 엔진 상태(실행 상태·식별자·생성 이미지·로그·컨테이너 안 파일·이미지 존재)만 읽는다. 문제를 연 시점 이후에 성공한 명령만 센다. 앱이 정답 명령을 대신 실행해 판정하지 않는다. `$BOX`와 실제 이름, 옵션 순서와 `--name=` 같은 표기 차이는 같은 명령으로 본다.
- 관리자 자동 풀이는 해설의 `bash_command`를 학습자 터미널에 입력하고 결과가 나온 뒤 다음 명령으로 넘어간다. 통과 여부는 같은 채점기가 정한다.
- Compose·Dockerfile 문제 5개(9~13번)도 개정 7부터 같은 실제 터미널에서 명령을 입력한다. 파일은 터미널 위 편집기에서 고친다. 구조와 검증은 `docs/curriculum/docker-compose-terminal.md`에 있다.

## 식별자와 생성 원본

- 원본: `tools/principles_lessons/d0_cli_intro.py`, 기존 메타데이터 연결은 `d1_image_container.py`. `make.py`가 `git_terminal`과 해설의 `('bash', 명령, 말, 대상)` 항목을 수업 파일로 옮긴다.
- 13개 문제 ID는 그대로다. 입문 8개는 문제 내용·할 일·해설·채점 방식이 바뀌었고 8번 제목을 「컨테이너를 멈춘 뒤 삭제하고 이미지는 남기세요」로 고쳤다.
- 개정은 `docker-image-container-6`이다. 이 개정은 `git_terminal.docker`를 이해하는 앱이 필요하다. 이전 앱은 이 수업 파일을 검증하지 못하므로 앱 릴리스가 먼저 공개된 뒤 수업 저장소와 코스 참조를 게시한다.

## 검증

`make.py` → `build-redesigned-git.py`(해설 문맥 검토 기록 포함) → `validate_redesigned_lesson` 순서로 확인한다. 검증기는 CLI 8문제를 실제 PTY 터미널에 학습자처럼 입력해 채점하고, 해설을 해설용 프로젝트에서 재생해 실제 출력을 `recorded/docker-image-container.json`의 패턴과 비교한다. 최종 게시의 근거는 `target/mcq/docker-image-container.json`의 현재 파일 해시와 실제 채점 결과다.

`cargo test --test docker_cli_terminal -- --ignored --test-threads=1`은 실제 PTY와 Docker로 다음을 확인한다: 첫 `docker pull`을 Enter로 실행, run의 실제 ID, `docker ps` 실제 표(개발자 컨테이너 포함), 문제 이동·재진입 시 같은 컨테이너 ID 유지, 해설 프로젝트 분리, 보호 함수의 거절(다른 컨테이너 stop·rm, 8080 고정 포트, `-v`, rmi, prune), 초기화의 시작 상태 복원, 수업 종료 시 소유 자원만 정리, 자동 풀이 재생과 채점. 네이티브 화면이나 실제 음성을 확인하지 않은 경우 그 검증까지 통과했다고 표현하지 않는다.

`tools/test_docker_cli_intro.py`는 삭제했다. 이 스크립트는 `commands.sh`를 `lab.sh`로 실행하는 개정 5까지의 방식만 시험했고 그 파일들은 개정 6에 없다. 같은 항목(실제 표·로그·exec 출력, 반복 시 같은 ID, 127.0.0.1 빈 포트, 무관한 컨테이너 보존, 고정 포트 거절, 명령별 정답과 무동작 오답)은 위 `docker_cli_terminal` 시험과 `docker_practice` 단위 시험(옵션 순서·`$BOX` 동등성, 다른 명령 거절)이 실제 터미널 경로에서 확인한다.

실제 앱 화면(Windows, 디버그 앱, 격리 검증 전송): `node tools/design-capture.cjs tools/design-scenarios/docker-terminal.cjs <출력 폴더>`. 2026-10-28 실행 결과 통과했다. 확인한 것은 다음과 같다. 문제 1에 코드 편집기·코드 실행 버튼 없이 「실제 Docker 터미널」이 열리고, 아무것도 입력하지 않은 제출은 실패한다. `docker pull nginx:1.28-alpine` 입력 후 Enter를 누르면 실제 Digest·Status 줄이 나오고 제출이 통과한다. 문제 2 run에서 실제 64자리 ID가 나온다. 문제 3의 `docker ps` 실제 표에는 다른 MQ 세션의 컨테이너도 보인다. 관리자 자동 풀이 칩의 상태 점은 진행·일시정지에서 칩 왼쪽 테두리와 8px 떨어져 있다(라이트·다크). 멈춘 뒤 학습자 상태는 그대로 통과한다. 문제 4 해설은 「해설용 별도 Docker 터미널」에서 실제 `docker logs` 출력(Configuration complete)을 보여 주고 학습자 터미널 내용은 바뀌지 않는다. 같은 문제의 관리자 자동 풀이는 학습자 터미널에 `docker logs "$BOX"`를 입력하고 채점 통과 뒤 문제 5로 넘어간다. 760px 폭 화면도 확인했다. 앱을 종료한 뒤 감시 프로세스가 이 실행의 `mq3lab-` 컨테이너만 정리했다. 실제 음성은 듣지 않았다(목소리를 끄고 자막과 동작만 확인).

이 화면 검증에서 찾은 앱 결함 하나를 고쳤다. `git_terminal_ui.rs`의 `if let Some(docker)=practice.lock()….exercise_docker()`에서 MutexGuard가 if-let 블록 끝까지 살아 있었다. 그래서 블록 안의 `practice.lock()`이 같은 스레드에서 교착하고 터미널이 「Docker를 준비하고 있어요」에 멈췄다. 통합 시험은 이 UI 경로를 거치지 않아 통과했었다. 잠금을 먼저 풀도록 고쳤다.

## 남은 제한과 게시 순서 (2026-10-28)

- (2026-10-28 개정 7에서 해소) 이 수업 9~13번과 `docker-network-ports`(4문제), `docker-compose-db`(3문제)도 편집기 + 실제 터미널로 바꿨다. `lab.sh`와 코드 실행 버튼은 더 이상 없다. 자세한 내용은 `docs/curriculum/docker-compose-terminal.md`. `commands.sh`를 쓰는 문제도 없다. SQL 수업 6개는 의도대로 SQL 편집기를 유지한다.
- macOS의 실제 PTY·Docker Desktop 경로는 이번에 실행하지 않았다(Windows Git Bash만). CI 작업(`principles-runtime.yml`)에 `docker_cli_terminal` 단계를 더했다.
- 전체 회귀 검사의 실패 3건(`java_code_guide` 2건, `lesson_registry` 단계 수 925≠871)은 이 변경 전 HEAD 224fb34를 그대로 꺼낸 폴더에서도 같은 메시지로 재현된다. 이 변경과 무관하며 고치지 않았다.
- 게시 순서: `git_terminal.docker.compose`까지 이해하는 앱 릴리스 → 수업 저장소에 새 불변 개정 게시 → 코스 참조(`java-backend.json` 핀) 게시. 이전 앱은 이 수업 파일을 검증하지 못하므로 순서를 바꾸지 않는다. 이 브랜치의 개정은 `docker-image-container-7`·`docker-network-ports-4`·`docker-compose-db-5`다. 2026-10-28 원격에는 `docker-image-container-6`, `docker-network-ports-3`, `docker-compose-db-4`까지 게시돼 있다(뒤의 둘은 전체 해설 감사가 게시했다). 해설 감사의 변경과 합친 뒤 내용이 바뀌면 그때의 원격 태그를 다시 확인하고 비어 있는 다음 번호를 쓴다. 이미 게시된 태그는 다시 쓰지 않는다. 자세한 검증 결과는 `docs/curriculum/docker-compose-terminal.md`.

공식 근거: [컨테이너의 필요성](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/), [pull](https://docs.docker.com/reference/cli/docker/image/pull/), [run과 start](https://docs.docker.com/reference/cli/docker/container/run/).

## 다음 네트워크·Nginx 수업 연결 메모

CLI 입문 중간에 DNS를 끼워 넣지 않는다. 다음 네트워크 실습 후보에서 `shop.127.0.0.1.nip.io`, `api.127.0.0.1.nip.io`처럼 서로 다른 이름을 같은 루프백 IP로 연결하고 Nginx의 `server_name`으로 요청을 나누는 흐름을 연결한다. 이 문단은 교육 계획이며 해당 nip.io 실습이 구현·검증됐다는 기록이 아니다.

- 도메인 이름은 IP를 찾는 이름이며 포트 번호를 정하지 않는다. 같은 IP·같은 호스트 포트에 접속해도 HTTP Host에 따라 Nginx가 다른 서버 블록을 선택할 수 있다.
- `127.0.0.1`은 명령이나 브라우저를 실행하는 컴퓨터 자신이다. 휴대전화에서 그 주소를 열면 개발자의 PC가 아니라 휴대전화 자신을 가리킨다. 컨테이너 안의 루프백도 그 컨테이너 자신이다.
- 호스트 포트는 기존 정책대로 `127.0.0.1`에 빈 포트를 자동 배정한다. 80·8080·3306 같은 고정 호스트 포트를 점유하지 않는다. 컨테이너 내부 포트와 호스트에 노출한 포트는 구별한다.
- 일부 DNS·공유기의 재바인딩 보호는 공용 이름이 루프백 주소로 해석되는 것을 차단한다. 보안 설정을 꺼서 해결하지 않는다. DNS가 실패했는지와 Nginx의 이름 분기가 실패했는지를 나눠 확인한다.
- `curl --resolve shop.127.0.0.1.nip.io:$PORT:127.0.0.1 http://shop.127.0.0.1.nip.io:$PORT/`는 이 요청의 이름→IP 매핑을 지정한다. DNS가 실제로 성공했다는 증거는 아니다.
- `curl -H 'Host: shop.127.0.0.1.nip.io' http://127.0.0.1:$PORT/`는 HTTP Host 분기를 별도로 검사한다. 이것도 DNS 해석 검사나 HTTPS 인증서·SNI 검사와는 다르다.
