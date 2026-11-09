# S3 저장과 Lambda 실행·이벤트 연결은 수업용으로 재현되는가

Labels: wayfinder:research
Type: research
Status: resolved
Assignee: floci_s3_lambda_lab
Blocked by: 01, 06
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

사용자 요청에 따라 고정한 Floci의 S3 객체 저장·읽기·덮어쓰기·버전·오류·정리를 실제로 측정한다. Lambda는 실제 함수 실행과 실패·수정·반복 호출을 검사하고, 가능한 경우 S3 업로드 이벤트가 Lambda를 실행해 결과 객체를 남기는 연결을 측정한다. 상태 API의 성공과 실제 객체 바이트·함수 결과·Docker 프로세스·이벤트 처리를 구분한다.

## Comments

실제 AWS 계정·자원·자격 증명을 사용하지 않는다. 앞서 검증한 격리 DIND 방식과 고정 Floci 이미지를 사용한다. 호스트의 기존 Docker 자원은 보존하고 실험 소유 자원만 정리한다. 비동기 이벤트는 실제 관찰 조건과 제한 시간으로 판정한다. 이 조사는 수업 범위·순서 제안을 위한 실행 증거이며 운영 수업 구현이나 게시가 아니다.

## Answer

2026-11-09 해결. 완료된 기본 실행의 23개 판정이 통과했다. S3 바이너리·한글·빈 객체를 정확히 읽었고, 같은 key 덮어쓰기·목록·잘못된 key/버킷·선택 삭제·버전·삭제 마커를 확인했다. 실제 Python 3.12 Lambda 컨테이너로 입력·출력, 반복 호출, 예외·잘못된 입력·timeout, 코드 갱신과 없는 함수를 검증했다. StatusCode 200과 FunctionError를 구분했다. warm 프로세스 상태 재사용은 관찰 사실이지 영속성 보장이 아니다.

S3 incoming 업로드가 Lambda를 호출하고 SDK로 입력 객체를 읽어 processed 결과를 남기는 실제 연결을 확인했다. 입력 변경이 결과 바이트 변경으로 이어졌고 다른 prefix는 제한 시간 안에서 결과를 만들지 않았다. 무한 시간 미호출이나 정확히 한 번 전달을 주장하지 않는다.

별도 보강은 S3 per-service persistent 모드와 소유 볼륨으로 프로세스 정상 재시작 전후 270바이트의 동일 해시를 확인했다. 같은 대표 이벤트를 handler에 두 번 전달한 결과 바이트가 같았다. 원시 판정은 6개 중 5개 통과이며 한글 목록 stdout 디코딩 비교 실패를 그대로 남겼다. 정확한 한글 key GET과 자동 pagination 집계의 객체 한 개라는 증거로 관찰 시점의 보이는 출력 key가 추가되지 않았다는 좁은 판정을 별도로 기록했다. 버전 이력·동시 중복·모든 부수 효과의 멱등성이나 플랫폼 전달 보장을 검증한 것은 아니다.

주 에이전트는 기본 실행 47개와 보강 완료 실행 15개 AWS CLI 요청의 loopback endpoint를 독립 확인했다. 정상 완료·보강 실행의 전후 자원 목록은 같고 보강은 bridge inspect(IPAM/options 포함), context, engine ID도 같았다. 다만 첫 준비 실패 실행에서는 기본 bridge ID·생성 시각 변경이 있었다. 사용자 정의 네트워크·컨테이너·볼륨은 같았지만 원인과 해당 시점 subnet/options 불변은 확인할 수 없다. 이 차이를 숨기거나 호스트가 모든 시도에서 완전히 불변이었다고 보고하지 않는다.

실험은 Windows에서 격리 DIND 안에 한정하며 Mac은 계획상 동일 동작 가정만 사용한다. 최종 실험 소유 컨테이너·네트워크·볼륨은 없고, 실제 AWS 계정·리소스를 쓰지 않았다. 수업 원고·실행기·채점기를 구현하지 않았다.

Assets: [S3·Lambda 실제 실행 보고서](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-s3-lambda-20261109/.scratch/floci-course-wayfinder/service-experiments/s3-lambda/REPORT.ko.md), [저장·재처리 보강 보고서](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-floci-s3-lambda-20261109/.scratch/floci-course-wayfinder/service-experiments/s3-lambda/SUPPLEMENT.ko.md).

Remote context: [불변 연구 자료](https://github.com/jhs512/immersion-quest-3/blob/d74be8d5/.scratch/floci-course-wayfinder/service-experiments/s3-lambda/SUPPLEMENT.ko.md), branch `research/floci-s3-lambda-20261109`. 연구 자료만 commit/push했으며 PR·병합·운영 배포는 하지 않았다.
