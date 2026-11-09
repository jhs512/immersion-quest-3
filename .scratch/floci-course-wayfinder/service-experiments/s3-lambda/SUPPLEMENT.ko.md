# 보충 검증: S3 보존과 같은 이벤트 재실행

2026-11-09, `mq-floci-s3lambda-supp-20261109213026`. 기존 [23개 완료 검증](REPORT.ko.md)의 증거는 수정하지 않았다. 그 보고서에서 미검증으로 남긴 두 범위를 아래처럼 추가 확인했다. Windows-hosted Linux DIND/Floci 2.4.0/Python 3.12의 결과다.

## S3 persistent 모드의 깨끗한 프로세스 재시작

공식 [2.4.0 storage 문서](https://github.com/floci-io/floci/blob/2.4.0/docs/configuration/storage.md)에 따라 `FLOCI_STORAGE_MODE=memory`, `FLOCI_STORAGE_SERVICES_S3_MODE=persistent`, `FLOCI_STORAGE_PERSISTENT_PATH=/app/data`를 명시했다. `/app/data`는 소유한 빈 inner Docker volume `mq-s3-persistent`에 mount했다. `persistent-config-inspect.json`이 실제 설정과 mount를 보존한다.

바이트 0~255와 한글 본문을 합친 **270바이트 객체**를 한글 키로 쓴 뒤 내려받고, `docker restart --timeout 20 floci` 뒤 같은 키로 다시 내려받았다. 전후 바이트가 동일하며 SHA-256은 둘 다 `20ac8726c7347977ad5e13f7bd2ab7cd4528097a4c2718f0543258e6287e0c2a`였다. 기존 memory 모드 재시작에서 버킷이 사라진 결과와 대비된다.

수업에서는 **서비스 저장 설정과 실습 초기화를 구별**할 수 있다. 저장 모드는 준비 환경에서 고정 제공한다. 이 결과는 작은 객체 하나의 clean process restart 보존이다. 컨테이너 재생성, 강제 종료·전원 손실·디스크 오류, 객체 metadata/버전의 재시작 보존, 실제 AWS S3 내구성을 검증하지 않았다.

## 같은 대표 S3 이벤트를 실제 handler에 두 번 전달

실제 Lambda 런타임 컨테이너에서, 같은 대표 `ObjectCreated:Put` 이벤트(JSON의 URL-encoded 한글·공백 키)를 **직접 동기 invoke로 순서대로 두 번** 전달했다. 함수는 소유한 Floci endpoint로 SDK 요청을 보내 입력 객체를 읽고 같은 `processed/한글 input.txt`에 변환 결과를 덮어쓴다.

- 두 호출 모두 StatusCode 200, FunctionError 없음, 반환값 `{"records":1}`.
- 각 호출 뒤 정확한 한글 출력 키의 GET 성공. 본문은 두 번 모두 `PROCESSED:REPLAY SOURCE`.
- 각 호출 뒤 같은 버킷의 `processed/` 목록은 AWS CLI 기본 pagination 집계에서 객체 1개다. 이 집계 출력에는 IsTruncated/KeyCount 필드가 없으므로 그 값을 합성하지 않는다. 결과가 누적되어 추가 키가 생기지 않았다.

**원시 matrix는 5/6이며 그대로 보존했다.** 마지막 키 비교 assertion은 Windows AWS CLI stdout의 한글 문자열이 `processed/�ѱ� input.txt`로 decode되어 실패했다. 서비스 응답 실패로 판정하지 않고 fixture 출력 처리 문제로 분리한다. 수업 준비 점검에서는 Windows CLI의 한글 stdout 표시·저장 인코딩을 먼저 확인해야 한다. 원래 목록·실패 조건을 고쳐 쓰지 않았다. `supplementary_audit.py`는 별도로 원시 증거의 **정확한 Unicode 키 GET 2회 성공 + 동일 버킷/prefix의 AWS CLI 기본 pagination 집계(--no-paginate/--max-items/--query/--starting-token 없음, 후속 token 없음) 개수 1 + 두 결과 바이트 일치**를 결합하여 `derived_no_extra_output_keys=true`를 계산했다. 후속 재현 fixture의 assertion도 이 의미를 직접 확인하도록 고쳤으며 그 수정으로 원시 5/6을 6/6이라고 바꾸지 않는다.

따라서 **이 handler가 이 동일 입력 이벤트를 순차 재실행했을 때 결과 객체를 같은 내용으로 유지**함을 확인했다. S3가 이벤트를 정확히 한 번 전달한다는 뜻이 아니다. 동시 중복, 순서가 뒤바뀐 다른 버전 이벤트, 플랫폼 재시도는 미검증이다. 실제 S3 업로드가 Lambda를 실행해 변환하는 경로는 기존 23개 검증에서 별도로 확인했다. [AWS S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)

수업 순서는 기존 권고를 유지한다. Lambda 직접 입출력→실패·코드 변경→SDK 읽기·쓰기→S3 이벤트 양성/음성 비교를 먼저 한다. 그 다음 같은 이벤트를 다시 전달하여 출력이 늘지 않는 이유를 설명한다. 고정 결과 키로 덮어쓰는 단순한 예제이며 일반적인 모든 부작용의 멱등성을 보장하지 않는다.

## 격리·정리·재현 근거

Floci는 host의 고정 index digest 이미지를 binary pipe `docker image save`→소유한 DIND `docker image load`로 전달했다. Docker Desktop containerd의 index ID와 inner classic engine의 config ID가 다르므로, `cache-content-verification.json`은 **전체 RootFS layer 목록·전체 Config·OS/architecture 동일성**으로 콘텐츠를 확인한다. 출처 index는 `5ee85db6…`, inner config ID는 `0afb9695…`다. Python runtime은 기존에 관찰한 공식 digest `238f6bfd…`를 직접 pull했다. registry 로그인과 설치는 하지 않았다.

첫 보충 준비 `mq-floci-s3lambda-supp-20261109212948`는 이미지 전송은 성공했지만 index ID=config ID라는 fixture 가정이 잘못되어 서비스 실험 전에 종료됐다. Windows pipe producer 종료 처리도 보완했다. 실패 증거와 finally cleanup audit를 따로 보관한다. 서비스 검증 통과에 포함하지 않는다.

완료 보충 실행의 기본 `audit.json`은 before/after host 컨테이너·네트워크·볼륨 동일, outer API만 loopback 공개, host socket mount 없음, nested 공개 포트 없음, 모든 host AWS CLI 명시적 loopback을 확인한다. 추가 `supplementary-audit.json`은 **bridge 전체 inspect(IPAM/options 포함) 동일, Docker context=desktop-linux 동일, engine ID 동일**을 확인한다. 이전 준비 실패 실행의 bridge ID 변화 원인을 이 결과로 소급 판정하지 않는다. 소유 outer 컨테이너·network·volume은 finally에서 제거했고 inner persistent volume도 격리 엔진 데이터 volume과 함께 제거됐다. 실제 AWS 자원과 자격 증명은 사용하지 않았다.

직접 Claude CLI의 결과 해석 검토를 받았고 Codex가 원시 API/바이트/목록/정리 증거를 독립 확인했다. 재현 파일은 `supplementary_lab.py`, `supplementary_matrix.py`, `supplementary_audit.py`다. 학생용 수업·배포·채점기는 변경하지 않았다.
