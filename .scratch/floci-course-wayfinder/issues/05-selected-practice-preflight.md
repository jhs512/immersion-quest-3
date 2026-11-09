# 선택한 실습은 고정한 로컬 환경에서 재현되고 상태로 판정되는가

Labels: wayfinder:task
Type: task
Mode: AFK
Status: resolved
Assignee: root
Blocked by: 03, 04
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

첫 학습 목표와 CLI·SDK 도구가 선택된 뒤, 고정한 안정 이미지의 amd64·arm64 manifest/digest와 필요한 도구 버전을 확인하고 최소 예제를 격리된 로컬 환경에서 실행한다. 준비 상태·정답 상태·흔한 오답을 서비스 응답으로 구분할 수 있는지, 초기화와 정리가 다른 실습·사용자 자원을 보존하는지 확인해 적용 결정을 위한 실행 근거를 얻는다.

## Comments

현재는 미실행이다. 실제 AWS 계정·인증·리소스를 사용하지 않는다. 기존 이미지 허용 목록을 무작정 풀거나 MQ 채점기·수업을 구현하는 작업이 아니다. 실측이 없는 플랫폼은 검증 완료로 보고하지 않는다. SQS 검사에서는 수신·삭제가 상태를 바꾸는 점과 Floci 전용 비소비 관찰 API를 사용하는 경우 AWS와의 차이를 따로 기록한다.

[VPC·서브넷·EC2 구성과 실제 통신은 어디까지 일치하는가](06-vpc-subnet-runtime-experiments.md)에서 인프라 실행에 관한 별도 실험을 완료했다. 이를 이미 얻은 근거로 재사용하되, 이 티켓은 선택될 대표 학생 문제의 준비·정답·오답 및 교육 목표 판정을 검증하는 단계이므로 아직 해결된 것으로 간주하지 않는다.

2026-11-09 첫 수업 초안 승인 뒤 별도 작업 폴더 `immersion-quest-cloud-first-lesson-20261109`에서 실행 검증을 시작했다. 대표 subnet 문제의 init/check/reset/cleanup과 학생·해설 상태 분리, 실제 Java EC2 게스트 배치가 이번 범위다. Claude Code가 구현하고 Codex가 증거와 실제 실행을 검증한다. 아직 MQ 네이티브 통합·Mac 실행을 완료한 것으로 보지 않는다.

## Answer

Windows 최종 실행 `mq-floci-pf-20261109222727`에서 실제 서브넷 계약 19/19와 Java EC2 배치 15/15가 통과했고 두 부분 모두 호스트 컨테이너·네트워크 전체 inspect·볼륨·context가 전후 동일했다. Codex도 실행 중인 소유 EC2 API를 새로 조회하고 A 서브넷 클라이언트에서 B의 API 사설 주소로 Java HTTP 응답을 직접 받아 확인했다.

첫 실패의 권한 설정과 익명 볼륨 잔재, Java 출처 판정 오류, 결과 요약기 오류는 원자료와 함께 보존했다. 최초 브리지 교체는 첫 기록된 변경 명령보다 앞섰으며 원인을 단정하지 않는다. 네 개의 익명 볼륨은 소유 라벨 컨테이너의 Mounts 기록으로 출처를 확인해 따로 정리했다. 실패 실행을 성공으로 다시 쓰지 않았다.

구현 도구와 보고서는 별도 작업 폴더의 `tools/floci_preflight/`, `docs/floci-first-lesson-preflight.md`에 있다. 원자료와 독립 검토는 `target/floci-preflight/`에 남겼다. 고정 Floci·Java 이미지의 amd64/arm64 manifest는 확인했으나 Mac 실행은 미검증이다. 이 결과는 Python 실행·채점 계약과 실제 Java 게스트의 검증이며 MQ 네이티브 통합 완료를 뜻하지 않는다. 다음 작업은 [MQ 클라우드 실행기 연결](11-native-cloud-runtime.md)이다.
