# MQ의 기존 실습과 채점기 어디에 Floci를 연결할 수 있는가

Labels: wayfinder:research
Type: research
Status: resolved
Assignee: mq_runtime_fit
Blocked by:
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

최신 origin/main의 코스·수업 구조와 Docker 기반 실습·상태 채점·초기화 구조를 조사해 Floci 적용 시 재사용 가능한 부분과 새로 결정해야 할 부분을 찾는다. 기존 네트워크 실습을 대체하는 것과 후속 AWS API 실습을 추가하는 것을 분리하고, 현재 수업과 연결 가능한 학습 목표 후보를 정리한다.

## Comments

원래 작업 브랜치와 사용자 변경을 수정하지 않는다. 연구 자료는 별도 research 브랜치에 기록한다.

## Answer

2026-11-09 해결. 최신 `origin/main`의 불변 기준 `0d551472`를 조사했다. 소유 라벨을 통한 자원 수명주기, 학습·해설 환경 분리, 실제 상태를 읽는 채점과 결과 보고는 재사용 후보이다. 현재 일반 Docker 실행기의 이미지 허용 목록은 Floci 이미지를 허용하지 않으며 Java 라이브러리 묶음에도 AWS SDK가 없다. 네트워크 채점기는 고정된 여덟 종류의 IP·경로·DNS 실습에 특화되어 있어 그대로 AWS 상태 채점기로 사용할 수 없다.

AWS API 상태를 관찰하는 계약이 별도로 필요하며, SQS 수신은 상태를 바꾸므로 무해한 조회로 간주하면 안 된다. 기존 IP·라우팅 실습을 대체할 근거는 없으며 후속 실습은 후보일 뿐 사용자 승인된 범위가 아니다. 소스·정책 조사만 했고 새 런타임 실행·수업 구현·배포 검증은 하지 않았다.

Asset: [MQ 실습 실행기와 채점기 적용 조사](https://github.com/jhs512/immersion-quest-3/blob/f64ab0cd/.scratch/floci-course-wayfinder/research/mq-runtime-fit.md)

Local asset: [MQ 실습 실행기와 채점기 적용 조사](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-research-runtime-20261109/.scratch/floci-course-wayfinder/research/mq-runtime-fit.md)

Context: `research/floci-mq-runtime-20261109`, commit `f64ab0cd`. 연구 자료만 원격에 저장했고 PR·병합은 하지 않았다. Claude Code 소스 검토 후 CLI 쓰기 권한이 거절되어, Codex가 확인된 근거를 대조하고 단일 연구 자료로 작성했다.
