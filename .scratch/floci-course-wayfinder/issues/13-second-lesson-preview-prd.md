# 두 번째 클라우드 수업(서버 수명주기·삭제 순서)의 예고·PRD는 적절한가

Labels: wayfinder:prototype
Type: prototype
Status: draft — 사용자 승인 대기
Blocked by: 12
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

첫 수업 다음에 EC2 중지·재시작·종료와 서브넷·VPC 삭제 의존성을 가르치는 예고·PRD·대표 문제가 적절한가?

## Comments

2026-11-12 인수인계 「재개 순서」 3번에 따라 시작했다. 현재 MQ 실행기로 사전 측정을 먼저 했다([run-1.log](../evidence/lifecycle-preflight/run-1.log), 측정 검사 `docker_cloud_lifecycle_preflight`).

초안:
- [수업 예고](../second-lesson/lesson-preview.draft.json)
- [PRD](../second-lesson/prd.draft.md)
- [대표 문제](../second-lesson/representative-problem.draft.md)

승인 전에는 본편·실행기 코드·운영 등록을 바꾸지 않는다. 제작 전 게이트 7개는 PRD 12절에 있다.
