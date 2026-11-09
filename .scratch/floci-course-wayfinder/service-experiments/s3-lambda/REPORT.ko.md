# Floci S3·Lambda 수업 가능 범위: 실제 실행 기록

2026-11-09. Windows Docker Desktop 안에 별도 Linux Docker 엔진(DIND)을 만들고 Floci 2.4.0으로 실행했다. **기본 S3 실습, 독립 Lambda 실습, S3 이벤트로 파일을 변환하는 후속 실습에 사용할 수 있다.** 완료 실행은 `mq-floci-s3lambda-20261109212218`이며 판정 23개가 모두 통과했다. macOS 실제 검증 결과는 아니다. Mac도 같은 구성이 가능하다는 수업 계획상의 가정과 실제 검증을 구별한다.

## 검증한 행동

| 영역 | 실제 관찰 | 수업에서 확인할 교육 목표 |
|---|---|---|
| 버킷·객체 | 버킷 생성/목록, 0~255 바이트, 한글·공백 키와 UTF-8 본문, 빈 객체를 내려받아 바이트가 정확히 일치 | 객체는 키로 찾는 바이트 데이터이며 키와 본문은 별개다 |
| 키·삭제 | 같은 키 쓰기는 본문 교체, 다른 키 3개는 prefix 목록에 별도로 남음. 없는 버킷/키 오류, 비어 있지 않은 버킷 삭제 거절, 객체 하나 선택 삭제 | 키의 동일성, prefix, 자원 의존성을 작은 변경으로 관찰한다 |
| 버전 | versioning Enabled 뒤 두 번 쓰면 버전 2개, 일반 삭제 뒤 delete marker 1개 | 현재 객체 삭제와 과거 버전 제거를 구별한다. 과거 버전 직접 복원은 이번 실행에서 미검증 |
| 초기화 | 명시적인 memory 모드에서 Floci 프로세스를 재시작하자 버킷 목록이 비었음 | 실습 환경 초기화다. 실제 S3 내구성에 관한 결론으로 쓰지 않는다 |
| Lambda 실제 실행 | Python 3.12 AWS 공식 런타임 컨테이너에서 입력 3→출력 6, 다음 입력 5→10. 동일 warm 컨테이너의 모듈 카운터 1→2 | 함수의 입력·출력과 실행 환경 재사용을 구별한다. 재사용 보장은 가르치지 않는다 |
| 함수 오류 | 필수 입력 누락, 의도적인 ValueError, 2초 제한에 4초 대기 모두 호출 응답 StatusCode 200이면서 FunctionError. 없는 함수는 ResourceNotFoundException | API 호출 성공과 함수 실행 성공은 다르다. 함수 결과·오류 본문을 확인한다 |
| 코드 변경 | update-function-code 뒤 revision 1→2와 입력 7→출력 14 확인 | 코드 배포가 다음 실행 결과를 바꾼다 |
| 실제 이벤트 경로 | incoming/한글 input.txt 업로드→Lambda가 SDK로 객체를 읽음→processed/한글 input.txt에 정확한 변환 바이트 기록. hello event→PROCESSED:HELLO EVENT, 수정 입력→PROCESSED:MODIFIED EVENT | 업로드가 후속 작업을 일으키며 입력 변화가 결과 변화로 이어진다 |
| 이벤트 대조 | 결과를 최대 30초 polling했으며 두 양성 관찰은 각각 0.72초. 다른 prefix 업로드 후 6.24초/5회 polling 동안 대응 processed 객체 없음 | prefix 필터를 변경해 비교한다. 유한 시간의 음성 대조이며 모든 미래의 미호출을 증명하지는 않는다 |

알림 설정 API의 성공만 세지 않았다. 실제 내려받은 변환 본문을 비교했다. 출력은 `processed/`로 보내 `incoming/` 필터와 겹치지 않게 했다. 무한 루프 방지 설정은 확인했지만 정확히 한 번 전달, 중복 이벤트 재처리, 순서 보장은 검증하지 않았다. AWS 문서는 S3 이벤트를 최소 한 번 전달하며 순서를 보장하지 않는다고 설명한다. [S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)

## 권장 가르칠 순서

사용자가 정한 **VPC/EC2→S3** 이후에는 다음 순서를 권한다. DB의 위치는 별도 DB 실험 결과와 합쳐 결정한다.

1. **S3의 가장 작은 예제:** 준비된 버킷에 값 하나 쓰기→같은 키로 읽기→본문 한 곳 수정→다시 읽기. 선수는 명령 실행, 문자열·바이트, 요청과 응답이다. Docker·인증·endpoint 설정은 제공한다.
2. **키와 목록:** 키 한 곳만 바꿔 새 객체가 되는지 비교하고 prefix를 추가한다. 다음에 없는 키와 선택 삭제를 관찰한다. 빈 버킷 의존성은 그 뒤에 둔다.
3. **버전은 선택 확장:** 먼저 덮어쓰기의 손실을 겪은 뒤 versioning과 delete marker를 도입한다. 첫 객체 실습에 함께 넣지 않는다.
4. **Lambda 독립 입출력:** 준비된 함수에서 계산식 1줄을 바꿔 직접 invoke 결과를 비교한다. JSON과 함수/반환값만 선수로 삼는다. S3 SDK와 이벤트는 이 도입 예제에 넣지 않는다.
5. **Lambda 실패·배포:** 잘못된 입력 하나→StatusCode와 FunctionError 비교→조건 수정. 다음 스텝에서 코드 변경과 재배포, 다음에 timeout을 다룬다. warm 카운터는 실행 환경에 관한 선택 관찰이다.
6. **Lambda에서 S3 읽기·쓰기:** 먼저 직접 호출로 준비된 SDK 코드의 키나 변환식 1~3줄만 고친다. SDK·endpoint·path addressing 설정은 고정 제공한다.
7. **S3 이벤트 연결:** 수동 호출이 필요한 불편을 겪은 뒤 알림을 추가한다. incoming prefix 양성/다른 prefix 음성 비교→입력 수정→결과 본문 비교 순서다. 마지막에 중복 이벤트에도 같은 결과를 내는 설계와 출력 prefix 분리를 설명한다. 중복 재실행 자체는 추가 실험이 필요하다.

각 단계는 목표 하나와 관찰 가능한 행동을 맞춘다. 예측→실행→출력 비교→한 곳 수정 흐름으로 구성한다. 이 자료는 수업 제작 전 판단용 연구이며 학생용 본문·채점기·해설을 구현하지 않았다.

## 환경·재현·제한

- Floci 고정 index: `sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c` (2.4.0).
- DIND 고정 index: `sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e` (29.0.1). outer는 privileged, cgroupns=host, 4 CPU/6 GiB/2048 PID 제한이다.
- 실제 Python runtime digest: `public.ecr.aws/lambda/python@sha256:238f6bfd2c1c188aff3955c2f7ceb767fe9da1b3597d84264426a11690fcf2d7`. 실제 실행은 `python:3.12`를 pull한 뒤 관찰한 digest를 tag해 사용했고, 재현 하네스는 그 digest를 직접 pull하도록 강화했다.
- 실제 Lambda 컨테이너 메모리 128 MiB, CPU/PID 개별 제한 없음. outer DIND 전체 제한이 적용된다. Floci는 2 CPU/2 GiB/512 PID이다.
- host 공개 포트는 Floci API `127.0.0.1:45670` 하나다. Lambda runtime callback 포트·서비스 포트는 host에 공개하지 않았다. host Docker socket, 홈, SSH, 실제 AWS 자격 증명을 mount하지 않았다. Floci는 소유한 inner Docker socket만 사용했다.
- host AWS CLI 호출은 매번 명시적인 loopback endpoint, test/test, 빈 config/credentials 파일, metadata 비활성화를 사용했다. 함수 SDK도 소유한 inner bridge gateway `http://172.17.0.1:4566`와 dummy 자격 증명, path-style S3를 고정했다. 공개 AWS endpoint fallback을 쓰지 않는다. 이 주소는 이 격리 토폴로지 전용 준비 설정이다.
- 특수 토폴로지에서 callback 주소를 고정하는 `FLOCI_SERVICES_LAMBDA_DOCKER_HOST_OVERRIDE`와 real Docker 실행은 [Floci 2.4.0 Lambda 문서](https://github.com/floci-io/floci/blob/2.4.0/docs/services/lambda.md)에 근거한다. endpoint/SDK 설정 난도를 학생에게 전가하지 않는다.
- persistent/filesystem 모드 재시작 보존, 프로세스 장애 복구, 실제 AWS 내구성·IAM 격리·과금·확장·가용성은 이번 실행으로 검증하지 않았다. memory 초기화 결과를 S3 저장 원리와 섞지 않는다. [Floci storage configuration](https://floci.io/floci/configuration/storage/)
- API의 성공 응답과 함수 오류가 별개라는 해석은 [AWS Invoke API](https://docs.aws.amazon.com/lambda/latest/api/API_Invoke.html)에 부합한다. 실제 AWS의 재시도 정책을 Floci에서 검증했다고 말하지 않는다.
- S3 연결과 출력 prefix 분리는 [AWS S3→Lambda 가이드](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html)의 재귀 호출 경고를 따른다. 운영 IAM 권한·완전한 AWS 동작 동일성은 확인하지 않았다.

## 증거와 준비 실패 분리

`lab.py`는 기존 검증 하네스를 재사용했다. `service_matrix.py`는 비교 대상을 구체화하며, `audit.py <run-directory>`는 Docker를 조작하지 않고 저장된 증거로 점검을 재계산한다. 완료 실행의 `checks.json`, `summary.json`, `events.json`, runtime/컨테이너 inspect, before/after inventory를 함께 보관한다. `audit.json`은 baseline 컨테이너·네트워크·볼륨 완전 일치, loopback 공개, host socket 부재, AWS endpoint 고정을 확인한다. 소유 label을 확인한 exact run container/network/volume만 finally에서 삭제했다. 이미지 cache는 남겼다.

앞선 `mq-floci-s3lambda-20261109212145`는 불필요한 Alpine 준비 이미지 pull이 rate limit에 걸려 본 실험 전에 중단됐다. 이 실행도 cleanup inventory를 보관하며 수업 검증 통과 수에 포함하지 않는다. 두 번째 실행은 Alpine pull도 성공했으나 S3/Lambda에 필요하지 않으므로 최종 재현 하네스에서 제거했다. 그 하네스 정리는 완료 실험의 23개 판정을 늘리지 않는다.

준비 실패 실행의 별도 감사에서는 기본 `bridge` 네트워크 ID/CreatedAt가 변경됐다(`53543f059f62`→`62ebcdc75075`). 사용자 정의 기존 네트워크·host/none 네트워크·컨테이너·볼륨은 유지됐다. 하네스는 이름과 소유 label이 일치하는 run 네트워크만 삭제했으며 기본 bridge를 삭제하는 명령은 없다. 변경 원인은 이번 증거만으로 단정하지 않는다. 따라서 **두 실행 전체에서 모든 host 네트워크가 보존됐다고 주장하지 않는다.** 완료 실행의 before/after는 전부 동일하다. 실패 실행 `audit.json`의 false 판정도 그대로 보관했다.

저장된 bridge 요약에서 Driver/Scope/IPv4/IPv6/Internal/Labels는 동일하다. baseline에 IPAM/options 상세를 저장하지 않았으므로 subnet/config 불변은 판정할 수 없다. outer Docker 변경 명령 전수는 run 전용 network/volume 생성, 격리 컨테이너 실행, 그 run 컨테이너·volume·network 삭제이며 host daemon 재시작/설정 변경 명령은 없다. host engine은 Desktop 4.93.0 / Engine 29.8.1 / Linux amd64 / WSL2 kernel 6.6.87.2였다. 이후 재현 시 기본 network inspect와 Docker context/info도 baseline 증거에 추가해야 한다.

직접 Claude CLI로 사전 체크리스트와 결과 해석 검토를 요청했다. 실제 API·바이트·컨테이너·정리는 Codex가 독립 확인했다. 별도 Claude bridge나 승인 설정 변경은 사용하지 않았다.
