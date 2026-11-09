# 첫 클라우드 수업 구현 상태

2026-11-09. 사용자는 예고·PRD·대표 문제를 확인하고 다음 단계 진행을 승인했다.

| 구분 | 현재 근거 |
|---|---|
| 서브넷 대표 문제 실행·상태 판정·초기화 | Windows 실제 API 계약 19/19, 학생·해설 상태 분리 확인 |
| Java EC2 게스트 배치 | Windows 실제 배치·user-data·HTTP·출처 검사 15/15 |
| 독립 검토 | Codex가 실행 중 API를 새로 조회하고 다른 서브넷에서 Java HTTP 응답을 직접 확인 |
| 정리 | 최종 두 부분 모두 컨테이너·네트워크 전체 inspect·볼륨·context 전후 동일 |
| Mac | 이미지 amd64/arm64 manifest만 확인. Mac 실행은 미검증 |
| MQ 네이티브 연결 | 2026-11-10 Windows 단위 10개·실제 Docker 경로 8개 통과. 첫 실패·재실행 기록 보존. 실제 제출 분기·상태 보존·정리를 검사함 |
| 본편·해설·운영 등록 | 아직 제작·반영 완료가 아님 |

실행 도구와 상세 보고서는 별도 작업 폴더의 [사전 검증 보고서](C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-cloud-first-lesson-20261109/docs/floci-first-lesson-preflight.md)에 있다. 원자료는 같은 작업 폴더의 `target/floci-preflight/`에 보존했다. 실패 실행은 성공 결과로 덮어쓰지 않았다.

현재 사용자의 체크포인트 요청으로 제작 프로세스를 종료했다. [인수인계](../../../docs/floci-cloud-handoff.md)에 완료 범위와 재개 순서를 기록했다. 실행기는 앞서 검증했으나 마지막 PowerShell 확인은 9 통과·1 실패·8 ignored로, 현재 상태를 모두 녹색이라고 표시하지 않는다. [첫 수업 본편](../issues/12-first-lesson-content.md)의 소스 폴더는 아직 생성 전이다. PRD의 제작 전 검증 문장은 초안 작성 당시 상태다. Mac·화면 검증·운영 배포는 미완료이며 S3·SQS·DB·Lambda를 첫 수업 범위에 추가하지 않는다.
