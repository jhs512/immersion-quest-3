# MQ가 클라우드 실습을 준비·채점·초기화하고 학생 상태를 보존하는가

Labels: ready-for-agent
Type: task
Mode: AFK
Status: resolved
Assignee: root
Blocked by: 05, 10
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

검증된 Floci 동작을 실제 MQ의 준비·터미널·제출·초기화·재접속·해설 경로로 연결한다. 별도 CloudExercise와 실제 자원 상태 채점을 사용하고 일반 Docker 이미지 정책은 넓히지 않는다. Python 시제품 통과를 MQ 통과로 대신하지 않는다.

## Comments

사용자가 승인한 첫 수업 범위의 VPC·서브넷·EC2 배치와 HTTP를 지원한다. 관리되는 AWS 진입점은 소유 로컬 endpoint만 허용하고 사용자 AWS 인증을 읽지 않는다. 임의 호스트 프로그램의 네트워크 샌드박스를 제공한다고 주장하지 않는다. DIND·게스트의 실제 권한과 한계는 기록한다.

Claude Code가 별도 작업 폴더 `immersion-quest-cloud-first-lesson-20261109`에서 구현하며 Codex가 실제 네이티브 검사·상태 보존·정리 결과를 검증한다. 본편 제작·운영 등록은 이 경로가 확인된 뒤 진행한다.

## Answer

2026-11-10 Windows에서 네이티브 연결과 독립 검토를 완료했다. 별도 CloudExercise 5개 목표가 VPC·서브넷·서버 배치·API 주소 선택·최종 Java 배치를 지원한다. GitPractice의 준비·재접속·실제 제출 분기·초기화·해설 분리에 연결했다.

Windows 단위 10개, 실제 Docker 네이티브 경로 8개가 통과했다. 처음 fixture 호스트 브리지 비교 실패와 전송 검사 준비 전 network inspect 실패는 원자료에 남겼으며 해당 검사만 재실행해 통과했다. 원인은 단정하지 않았다. Unix 링크 검사를 Windows 통과로 세지 않았고 Mac·화면·운영 배포는 검증 완료로 보지 않는다.

Codex는 AWS CLI 축약 옵션 우회를 실제 CLI와 loopback 수신기로 재현해 수정했고, 주소·설정 파일 보호와 캐시 파이프라인 검토를 반영했다. 수정 후 스크립트 독립 검사 8/8과 네이티브 검사 결과를 구분했다. 마지막 원본 네트워크 전체 inspect·컨테이너·볼륨 비교 네 쌍을 별도 검토했다. 컨테이너 Networks 표시 순서 차이만 정렬했고 원본은 보존했다. 잔여 소유 컨테이너·네트워크·볼륨은 0개다.

코드·재현 명령·한계는 별도 작업 폴더의 `docs/floci-cloud-native-runtime.md`와 `target/cloud-native-evidence/`에 있다. 기존 registry의 수업 개수 기대값 불일치와 생성 파일 미준비 문제는 본편 등록·빌드 단계에서 구분해 처리한다. 다음은 [첫 수업 본편 제작](12-first-lesson-content.md)이다.
