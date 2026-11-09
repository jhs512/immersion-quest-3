# Floci로 어떤 AWS 학습 목표를 실제로 검증할 수 있는가

Labels: wayfinder:research
Type: research
Status: resolved
Assignee: floci_capabilities
Blocked by:
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

공식 최신 안정 릴리스와 문서·소스를 기준으로 Floci의 실행 요건, 라이선스, S3·SQS·IAM·EC2/VPC 관련 지원의 의미, 학습용 검증에 적합한 범위와 실제 AWS를 대체하지 못하는 부분은 무엇인가? 비용·로그인 없는 로컬 실습으로 제안할 후보와 보류할 후보를 근거로 구분한다.

## Comments

Research 컨텍스트는 별도 research 브랜치의 연구 자료로 남긴다. 문서 지원 주장과 직접 실행 검증을 혼동하지 않는다.

## Answer

2026-11-09 해결. Floci 안정 릴리스 2.4.0과 해당 커밋의 공식 문서·소스를 조사했다. S3 객체 상태와 SQS 수신·가시성·삭제 등은 학습 목표 후보이나 직접 실행 검증은 하지 않았다. EC2/VPC는 실제 Docker 자원을 만들기도 하며, Linux 선택 기능의 SG 패킷 필터링과 VPC 라우팅·NACL·NAT·피어링을 구분해야 한다. IAM은 기본 강제 모드가 꺼져 있고 `test` 키 등의 우회 경로가 있어 보안 수업은 별도 검증이 필요하다.

릴리스 자산의 빈 목록과 문서의 네이티브 바이너리 안내 사이 차이, 미조회 이미지 digest, 플랫폼별 미실측 동작을 미확인 사항으로 기록했다. 실행 지원이 확정됐거나 첫 수업 범위가 결정됐다고 간주하지 않는다.

Asset: [Floci 지원 범위와 학습 경계 조사](https://github.com/jhs512/immersion-quest-3/blob/4ec9ea72/.scratch/floci-course-wayfinder/research/floci-capabilities.md)

Local asset: [Floci 지원 범위와 학습 경계 조사](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-research-capabilities-20261109/.scratch/floci-course-wayfinder/research/floci-capabilities.md)

Context: `research/floci-capabilities-20261109`, commit `4ec9ea72`. 연구 자료만 원격에 저장했고 PR·병합·운영 배포는 하지 않았다. Claude Code 초안 작성 뒤 소스 대조로 보완했다.
