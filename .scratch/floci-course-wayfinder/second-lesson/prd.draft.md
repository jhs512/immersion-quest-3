# 수업 PRD 초안 — 클라우드 · 서버를 멈추고 다시 켜고 없애요

Status: draft_for_review
작성일: 2026-11-12
관련: [수업 예고 초안](lesson-preview.draft.json), [대표 문제 초안](representative-problem.draft.md), [사전 측정 기록](../evidence/lifecycle-preflight/run-1.log), [첫 수업 PRD](../first-lesson/prd.draft.md)

> 사용자 검토용 초안이다. PRD와 대표 문제를 함께 승인받기 전에는 본편(content.json·정답·해설·음성)과 실행기 코드를 만들지 않는다(`docs/content-rules.md` 「수업 PRD와 승인」).

적용한 공통 교육 철학: 첫 수업과 같다. 새 교육 기법은 쓰지 않는다. 「정상 관찰 → 한 곳 수정 → 실행 → 변경 후 관찰」을 자원 상태에 적용한다.

### 정책 스냅샷 (내부 검토용)

| 정책 파일 | SHA-256 |
|---|---|
| `docs/content-rules.md` | `5c31837e0cf82dc42c540bc739ab6ae37cbcd1f80845b558c96517567be5d363` |
| `docs/voice.md` | `76eebb7a17673d5d3de754cf916656346412f351cc66590f17ccfff04f764c82` |

## 1. 수업 교육 목표

- 서버의 중지·재시작·종료가 각각 무엇을 남기고 무엇을 없애는지 실제 상태로 구별한다.
- 상태 변화가 비동기라는 것을 보고, 다음 행동 전에 원하는 상태가 됐는지 확인한다.
- 삭제 의존성을 거절 메시지로 읽고 서버 → 서브넷 → VPC 순서로 정리한다.

중심 질문: **이 자원을 멈출 것인가 없앨 것인가, 없앤다면 무엇부터.**

## 2. 대상과 위치

- 첫 클라우드 수업(`cloud-vpc-subnet-ec2`)을 마친 학습자. 자바 과정 「클라우드」 분류의 두 번째 수업이다.
- 첫 수업에서 VPC·서브넷·서버의 포함 관계, `describe-*` 출력 읽기, `client-request`로 응답 확인을 배웠다고 전제한다.
- 다음: S3 묶음([추천 순서](../service-teaching-plan.md)).

## 3. 선수 경험

| 수업 | 이 수업에서 쓰는 것 |
|---|---|
| `cloud-vpc-subnet-ec2` | VPC·서브넷·서버 관계, `run-instances`·`describe-instances`, `client-request` |
| `docker-image-container` | 컨테이너를 멈추는 것과 지우는 것의 차이 |

## 4. 범위

포함: `stop-instances`·`start-instances`·`terminate-instances`, `describe-instances`의 `State.Name` 읽기, 재시작 뒤 주소 유지와 프로그램 미기동 관찰, `delete-subnet`·`delete-vpc`의 `DependencyViolation`, 정리 순서.

제외: `reboot-instances`(측정은 했지만 중지·재시작과 구별되는 관찰이 없다), 스냅샷·AMI·EBS, 프로그램 자동 기동(서비스 등록), 과금 실습, S3·DB·Lambda, 라우팅·IGW·NAT·NACL·보안 그룹, 실제 AWS 계정.

## 5. 조사 근거 (내부)

2026-11-12 사전 측정. 현재 MQ 네이티브 실행기(서버 스텝 경로, Floci 고정 이미지, 게스트 Java 25)와 고정 AWS CLI 컨테이너로 실행했다. 실제 AWS 접속 없음. 로그: [run-1.log](../evidence/lifecycle-preflight/run-1.log).

| 동작 | 관찰 |
|---|---|
| 서버가 있는 서브넷 삭제 | `DependencyViolation`: "The subnet '…' has dependencies and cannot be deleted." |
| 서브넷이 있는 VPC 삭제 | `DependencyViolation`: "The vpc '…' has dependencies and cannot be deleted." |
| `stop-instances` | 응답 `running → stopping`, 약 20초(2초 간격 10회) 뒤 `stopped`. 사설 주소·서브넷 그대로. 게스트 컨테이너 Running=false |
| 멈춘 서버에 요청 | `client-request`가 연결 시간 초과 |
| 멈춘 서버의 서브넷 삭제 | 여전히 `DependencyViolation` |
| `start-instances` | 응답 `stopped → pending`, 2초 안에 `running`. 사설 주소 `10.91.2.10` 그대로 |
| 재시작 뒤 요청 | 90초 동안 "Connection refused". 처음 실행 때 서버를 띄운 user-data가 다시 돌지 않는다(실제 EC2의 기본 동작과 같은 방향) |
| `reboot-instances` | `running`, 주소 그대로 |
| `terminate-instances` | 응답 `running → shutting-down`, 2초 안에 `terminated`. 목록에는 `terminated`로 남는다. 게스트 컨테이너 없음 |
| 종료한 서버 `start-instances` | `IncorrectInstanceState`: "…is not in a state from which it can be started." |
| 종료 뒤 서브넷 삭제 | 성공(종료 후 약 20초 지나서 실행) |
| 서브넷 하나만 지운 뒤 VPC 삭제 | 남은 서브넷·클라이언트 때문에 `DependencyViolation` |
| 남은 서버 종료 → 서브넷 삭제 → VPC 삭제 | 모두 성공 |

검사 결과 표기는 "FAILED"였다. 모두 지운 뒤 측정 끝의 채점 호출 하나가 「준비된 서버가 멈췄어요」 오류를 낸 것으로, 측정 자체는 끝까지 실행됐다. 실행 뒤 소유 Docker 자원 0개.

## 6. 교육 원칙 (이 수업에 적용)

- 한 스텝에 새 개념 하나. 새 외부 서비스는 없다(첫 수업과 같은 실습 환경).
- 첫 수업 피드백을 따른다. 짧은 명령은 학생이 직접 입력하고, 반복되는 `--endpoint-url "$LAB_ENDPOINT"` 같은 옵션은 본문의 복사 블록으로 준다. 편집기 파일은 필요할 때만 쓴다.
- 채점은 실제 상태로 한다. 출력 문자열·명령 문자열은 근거가 아니다.
- 비동기 상태는 정해진 시간 안의 안정 상태로 판정한다. 학생에게 sleep 길이를 정답으로 요구하지 않는다.
- 모든 스텝은 독립 초기 상태로 시작한다.

## 7. 구성 — 챕터 → 스텝

표기: **새** = 새 개념, **시작** = 초기 상태, **행동**, **관찰**, **채점**, **오답**.

### 챕터 1. 멈추고 다시 켜요

**스텝 1 서버를 멈추세요**
- 시작: VPC `10.91.0.0/16`, 서브넷 A `10.91.1.0/24`(클라이언트), B `10.91.2.0/24`(응답하는 자바 서버).
- 새: `stop-instances`, `State.Name`의 `stopping → stopped`.
- 행동: `client-request`로 응답 확인 → `stop-instances` 직접 입력 → `describe-instances`를 몇 번 실행해 `stopped` 확인 → `client-request` 다시.
- 관찰: 응답의 `stopping`, 잠시 뒤 `stopped`, 연결 시간 초과.
- 채점: 준비 서버가 `stopped`(제한 시간 안의 `stopping`은 기다려서 판정), 같은 인스턴스가 목록에 있음, 클라이언트 `running`.
- 오답: 종료 → 「멈추라고 했는데 종료됐어요」로 실패. 클라이언트를 멈춤 → 실패.

**스텝 2 멈춘 서버를 다시 켜세요**
- 시작: 스텝 1과 같은 구성, 서버는 준비 단계에서 `stopped`로 만들어 둔다(시작 설명에서 먼저 알린다).
- 새: `start-instances`, 재시작 뒤 사설 주소 유지.
- 행동: `describe-instances`로 주소 기록 → `start-instances` → `running` 확인 → 주소 비교 → `client-request`.
- 관찰: 같은 주소, 그런데 "Connection refused". 「조심하세요」: 서버가 `running`이어도 프로그램은 처음 실행 때만 떴어요.
- 채점: 같은 인스턴스가 `running`, 같은 서브넷·같은 사설 주소.
- 오답: 새 서버를 `run-instances`로 만들어 응답을 받음 → 준비 서버가 여전히 `stopped`라 실패.

**스텝 3 엉뚱한 서버를 멈추지 마세요**
- 시작: 서브넷 A·B에 서버가 한 대씩 `running`. 본문의 시작 명령은 `--instance-ids "$LAB_CLIENT_ID"`(A의 서버).
- 새: 인스턴스 ID로 대상 고르기(어느 자원에 명령이 가는가).
- 행동: `describe-instances`로 ID·서브넷·주소 표 확인 → 시작 명령의 ID 한 곳을 B 서버로 바꿔 실행.
- 채점: B 서버 `stopped`, A 서버 `running`.
- 오답: 시작 명령 그대로 실행 → A가 멈춰 실패(「초기화」로 다시 시작). 둘 다 멈춤 → 실패.

### 챕터 2. 없애고, 순서대로 지워요

**스텝 4 서버를 종료하세요**
- 시작: 스텝 1과 같음.
- 새: `terminate-instances`, `shutting-down → terminated`, 종료한 서버는 다시 켤 수 없음.
- 행동: 종료 → `terminated` 확인 → `start-instances` 시도.
- 관찰: `IncorrectInstanceState` 거절, 목록에 `terminated`로 남은 서버.
- 채점: 준비 서버 `terminated`, 클라이언트 `running`, 서브넷 둘 그대로.
- 오답: 멈추기만 함 → 실패.

**스텝 5 서브넷 B를 지우세요** — 대표 문제
- 시작: 스텝 1과 같음.
- 새: `delete-subnet`과 `DependencyViolation`, 의존하는 자원부터 지우는 순서.
- 행동: `delete-subnet` 직접 입력 → 거절 → 서버 종료 → `terminated` 확인 → 다시 `delete-subnet`.
- 채점·오답: [대표 문제 초안](representative-problem.draft.md).

**스텝 6 실습 VPC를 모두 정리하세요** — 마지막 수행
- 시작: 서브넷 A·B, 서버 두 대 `running`.
- 새: 없음(4·5의 조합). `delete-vpc`의 거절을 읽고 남은 자원을 찾는다.
- 행동: `delete-vpc` 시도 → 거절 → 서버 둘 종료 → 서브넷 둘 삭제 → `delete-vpc`.
- 채점: 소유 VPC가 목록에 없음. 소유 서버 둘 `terminated`.
- 오답: 서버를 멈추기만 함 → 서브넷 삭제가 거절돼 VPC가 남아 실패.

## 8. 대표 문제

스텝 5. 전문은 [representative-problem.draft.md](representative-problem.draft.md).

## 9. 채점 원칙

- 채점기는 스텝 준비의 소유 기록(VPC·서브넷·인스턴스 ID)으로 실제 상태를 읽는다.
- `stopping`·`shutting-down`·`pending`은 제한 시간 동안 안정 상태가 될 때까지 기다려 판정한다.
- 소유 범위 밖 자원은 근거가 아니다. 새로 만든 서버로 응답을 받는 우회는 통과가 아니다.
- 지금 실행기는 준비 서버가 멈추면 채점 전에 「준비된 서버가 멈췄어요」 오류를 낸다. 이 수업은 멈춤·종료·삭제가 정답이므로 목표별로 이 검사를 바꿔야 한다(아래 게이트 1).

## 10. 초기화

- 스텝마다 새 Floci 상태. 스텝 2는 준비 단계에서 서버를 `stopped`로 만든다.
- 「초기화」는 실습 상태를 처음으로 돌린다. 스텝 3에서 잘못 멈춘 경우의 복구 경로다.
- 해설 시연은 학생 상태와 분리된 별도 실습 상태에서 한다.

## 11. 검증 기준 (제작 시)

각 채점 스텝마다 실제 실행으로 남긴다: 정답 통과, 시작 상태 실패, 대표 오답 실패, 동등한 다른 풀이 통과(예: `aws ec2 wait` 사용, 두 서버를 한 명령으로 종료), 준비 값을 바꾼 변형 통과. Windows·맥 각각 Docker 검사와 앱 파일럿.

## 12. 기술 준비 (내부)

### 제작 전 게이트 (미검증 · 해결 전 본편 제작 금지)

1. **새 채점 목표**: `CloudGoal`에 중지·재시작·종료·서브넷 삭제·VPC 삭제 목표를 더하고, 준비 서버가 멈춰 있어도 오류가 아니도록 목표별 검사를 바꾼다.
2. **앱 버전 경계**: `CloudExercise`는 모르는 값을 거절한다. 새 목표를 쓰는 수업을 build.188 이하 앱이 열면 수업 전체가 깨질 수 있다(build.184의 사고와 같은 종류). 수업 형식 번호를 올리거나 최소 앱 버전을 표시하는 방법을 먼저 정한다.
3. **준비된 멈춘 서버**: 스텝 2의 준비 단계 중지와 그 소요 시간.
4. **`aws ec2 wait instance-stopped`/`instance-terminated`**: Floci에서 동작하는지 측정하지 않았다. 동작하면 동등 풀이로 허용한다.
5. **종료 직후 서브넷 삭제**: 측정은 종료 뒤 약 20초가 지난 다음 삭제했다. `terminated` 직후 바로 지워지는지 확인한다.
6. **mock 모드 수명주기**: 서버 스텝은 게스트 엔진이라 준비가 느리다. 응답 확인이 필요 없는 스텝(3·4·5·6)을 가벼운 mock 모드로 돌릴 수 있는지 측정한다.
7. **맥**: 이번 측정은 Windows만. 맥에서 같은 측정을 한다.

### 주장하지 않는 것

- 실제 AWS의 중지·종료 소요 시간, 과금, 종료 뒤 목록 유지 기간.
- 주소 유지의 일반화(이번 측정은 같은 사설 주소를 관찰했을 뿐이다. 공인 주소는 다루지 않는다).
- user-data 재실행 설정이나 서비스 등록 동작.

## 13. 다음 수업 예고

「서버 밖에 파일을 맡겨요」: S3에 값 하나를 쓰고 읽기. 서버를 지워도 남는 저장소로 이어 간다.

## 변경 이력

- 2026-11-12 초안 작성(검토 전). 사전 측정 run-1 기준.
