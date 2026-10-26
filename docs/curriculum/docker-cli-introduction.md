# Docker 입문: 필요성에서 직접 실행으로

2026-10-26 사용자의 수정 요청을 반영한다. 기존 수업은 `docker run` 경험을 가정하면서 첫 문제부터 Compose YAML을 편집했다. 처음 배우는 사람이 실행 재료와 실행 상태를 구별하기 전에 여러 설정을 함께 읽어야 했다.

## 학습 흐름

수업 예고와 첫 문제에서 컴퓨터마다 설치 여부·버전이 달라지는 상황을 설명한다. Docker를 쓰지 않고도 환경을 맞출 수 있지만 반복해서 일치시켜야 한다는 점, 이미지가 프로그램과 필요한 사용자 공간 파일을 전달한다는 점을 먼저 다룬다. 모든 호스트 환경 차이를 실제로 재현했다고 주장하지 않는다. 같은 이미지가 CPU 구조·커널·외부 서비스 차이까지 없애는 것도 아니다.

그다음 학습자가 `commands.sh`에 명령 하나를 직접 작성한다.

1. `docker pull`: 실행 재료를 받지만 프로세스는 아직 없다.
2. `docker run`: 이미지에서 새 컨테이너와 프로세스를 시작한다.
3. `docker ps`: 이미지 목록과 실행 중인 컨테이너 목록을 구별한다.
4. `docker logs`: 실행 상태와 프로세스의 출력 기록을 구별한다.
5. `docker exec`: 새 컨테이너를 만들지 않고 기존 컨테이너 안에서 메모를 쓴다.
6. `docker stop`: 프로세스는 멈추고 객체는 남는다.
7. `docker start`: 같은 식별자의 컨테이너를 다시 실행한다.
8. `docker rm`: 컨테이너 객체는 없어지고 이미지는 남는다.

이 경험 뒤에 Compose가 `run`의 이미지·명령을 파일로 기록해 실행하는 단계임을 설명한다. 기존 PID 1·볼륨·레이어 캐시·최종 도전 5개로 이어진다. 문제 수를 맞추기 위한 추가가 아니라 명령마다 다른 관찰 대상을 하나씩 분리했다.

## 실제 실행과 준비 상태

2026-10-26 후속 수정: 이미지 변수를 감춘 BusyBox 명령 대신 `docker pull nginx:1.28-alpine`과 `docker run -d --name "$BOX" -p 127.0.0.1::80 nginx:1.28-alpine`을 직접 작성한다. BOX는 실습별 고유 이름이다. 준비 스크립트는 소유 라벨만 추가하며, 조회는 실제 Docker의 표·컨테이너 ID·로그를 그대로 보여 준다. `docker ps`에는 사용자가 원래 켜 둔 컨테이너도 보이며 이름으로 구별한다. 변경 명령은 실습 소유 자원만 허용하고 고정 포트·외부 공개 포트·추가 대상은 거절한다.

각 문제는 설명한 시작 상태를 한 번 준비한다. 같은 문제의 코드 재실행에서는 컨테이너를 재생성하지 않는다. 초기화 또는 수업 종료 때 소유 자원만 정리한다. 제출과 해설은 별도 실행 공간을 사용해 학생의 상태를 보존한다. `MQ3_OUTPUT=raw`는 실제 stdout/stderr, `grading`은 엔진 상태로 만든 결정적 판정 결과를 반환한다. 컨테이너 ID·포트·시각을 고정하기 위해 실제 출력을 대체하지 않는다. SQL/DB의 상태 유지 정책은 그대로다. 디렉터리 격리를 OS 샌드박스라고 주장하지 않는다.

## 식별자와 생성 원본

- 원본: `tools/principles_lessons/d0_cli_intro.py`, 기존 메타데이터 연결은 `d1_image_container.py`.
- 새 챕터에는 명시적 `identity=cli-introduction`을 주고 기존 챕터는 원래 `c0`~`c3` 정체성을 유지한다.
- 기존 문제 5개·챕터 4개·단원 5개의 ID는 보존한다. 새 8개 문제에만 새 ID를 부여한다.
- 개정은 `docker-image-container-4`이다. 수업 게시는 별도지만 이번 개정은 Nginx 이미지 허용과 화면/채점 출력 분리가 있는 앱이 필요하다. 해당 런타임 릴리스가 공개된 뒤 수업 저장소와 코스 참조를 게시한다.

## 검증

`make.py` → 대본 문맥 검토 → `build-redesigned-git.py` → 실제 Docker 재생 → `validate_redesigned_lesson` 순서로 확인한다. 최종 게시의 근거는 `target/mcq/docker-image-container.json`의 현재 파일 해시와 실제 채점 결과다. 네이티브 화면이나 실제 음성을 확인하지 않은 경우 그 검증까지 통과했다고 표현하지 않는다.

`python tools/test_docker_cli_intro.py`는 실제 표/로그, 반복 실행 시 동일 ID, 동적 루프백 포트, 무관한 컨테이너 보존, 고정·중복 포트 거절, 8개 명령의 정답/무동작 오답을 확인한다. 앱 실행기의 raw/grading 분리는 `docker_lab::tests::learner_and_narration_keep_raw_output_while_checks_use_grading_output`에서 확인한다.

공식 근거: [컨테이너의 필요성](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/), [pull](https://docs.docker.com/reference/cli/docker/image/pull/), [run과 start](https://docs.docker.com/reference/cli/docker/container/run/).

## 다음 네트워크·Nginx 수업 연결 메모

CLI 입문 중간에 DNS를 끼워 넣지 않는다. 다음 네트워크 실습 후보에서 `shop.127.0.0.1.nip.io`, `api.127.0.0.1.nip.io`처럼 서로 다른 이름을 같은 루프백 IP로 연결하고 Nginx의 `server_name`으로 요청을 나누는 흐름을 연결한다. 이 문단은 교육 계획이며 해당 nip.io 실습이 구현·검증됐다는 기록이 아니다.

- 도메인 이름은 IP를 찾는 이름이며 포트 번호를 정하지 않는다. 같은 IP·같은 호스트 포트에 접속해도 HTTP Host에 따라 Nginx가 다른 서버 블록을 선택할 수 있다.
- `127.0.0.1`은 명령이나 브라우저를 실행하는 컴퓨터 자신이다. 휴대전화에서 그 주소를 열면 개발자의 PC가 아니라 휴대전화 자신을 가리킨다. 컨테이너 안의 루프백도 그 컨테이너 자신이다.
- 호스트 포트는 기존 정책대로 `127.0.0.1`에 빈 포트를 자동 배정한다. 80·8080·3306 같은 고정 호스트 포트를 점유하지 않는다. 컨테이너 내부 포트와 호스트에 노출한 포트는 구별한다.
- 일부 DNS·공유기의 재바인딩 보호는 공용 이름이 루프백 주소로 해석되는 것을 차단한다. 보안 설정을 꺼서 해결하지 않는다. DNS가 실패했는지와 Nginx의 이름 분기가 실패했는지를 나눠 확인한다.
- `curl --resolve shop.127.0.0.1.nip.io:$PORT:127.0.0.1 http://shop.127.0.0.1.nip.io:$PORT/`는 이 요청의 이름→IP 매핑을 지정한다. DNS가 실제로 성공했다는 증거는 아니다.
- `curl -H 'Host: shop.127.0.0.1.nip.io' http://127.0.0.1:$PORT/`는 HTTP Host 분기를 별도로 검사한다. 이것도 DNS 해석 검사나 HTTPS 인증서·SNI 검사와는 다르다.
