# 클라우드 · 서버를 멈추고 다시 켜고 없애요

상태: approved
수업 코드: lsn_81d67284-bfe0-49b9-ac29-33f9aea19c00
코스: crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf

이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.

## 수업 교육 목표

- 서버를 멈추고 다시 켜면 무엇이 남고 무엇이 사라지는지 실제 상태로 확인해요.
- 상태가 바로 바뀌지 않는 것을 보고, 다음 명령 전에 원하는 상태가 됐는지 확인해요.
- 자원을 지우는 순서를 거절 메시지로 찾아요. 서버 → 서브넷 → VPC 순서예요.

## 대상과 선수 지식

- 첫 클라우드 수업(cloud-vpc-subnet-ec2)을 마친 자바 과정 학습자. 「클라우드」 분류의 두 번째 수업이다.
- cloud-vpc-subnet-ec2
- docker-image-container
- Docker Desktop의 Linux 컨테이너 엔진(AWS CLI v2는 고정 공식 이미지로 실습 네트워크에서 실행)

## 제작 범위

- 응답하는 서버를 멈추세요
- 멈춘 서버를 다시 켜세요
- 멈출 서버를 골라 멈추세요
- 서버를 종료하세요
- 서브넷 B를 지우세요
- 실습 VPC를 모두 정리하세요

## 제외 범위

- reboot-instances(측정했지만 중지·재시작과 구별되는 관찰이 없다), 스냅샷·AMI·EBS
- 프로그램 자동 기동(서비스 등록·user-data 재실행 설정), 과금 실습
- S3·RDS·DynamoDB·SQS·Lambda, 라우팅·IGW·NAT·NACL·보안 그룹, 실제 AWS 계정

## 근거와 확인 한계

- 인스턴스는 pending·running·stopping·stopped·shutting-down·terminated 상태를 거친다. 종료한 인스턴스는 다시 시작할 수 없다. — AWS 공식 문서의 상태 이름을 따른다. 로컬 실습에서 stop·start·terminate의 상태 변화를 실측했다.; 확인 2026-11-12. [원문](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html)
- 멈춘 인스턴스를 다시 시작하면 사설 IPv4 주소가 유지된다. — AWS 공식 문서 기준. 로컬 실습에서 같은 사설 주소를 관찰했다. 공인 주소는 다루지 않는다.; 확인 2026-11-12. [원문](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Stop_Start.html)
- user-data 셸 스크립트는 기본으로 인스턴스를 처음 시작할 때만 실행된다. — AWS 공식 문서 기준. 로컬 실습에서 재시작 뒤 자바 서버가 응답하지 않는 것을 관찰했다.; 확인 2026-11-12. [원문](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)
- 서브넷을 지우려면 그 안의 실행 중인 인스턴스를 먼저 종료해야 한다. delete-vpc도 VPC 안의 서브넷 등을 먼저 지워야 한다(같은 CLI 참조). — AWS CLI 공식 참조 기준. 로컬 실습에서 DependencyViolation과 종료 뒤 삭제 성공을 실측했다.; 확인 2026-11-12. [원문](https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-subnet.html)
- 고정 Floci 이미지에서 stop·start·reboot·terminate의 상태 변화, 재시작 뒤 같은 사설 주소, terminated 서버의 start 거절, 서브넷·VPC 삭제 의존성을 실측했다. — 실행 근거는 .scratch/floci-course-wayfinder/evidence/lifecycle-preflight/run-1.log에 있다. 실제 AWS의 소요 시간·과금은 주장하지 않는다.; 확인 2026-11-12. [원문](https://github.com/floci-io/floci)

## 적용 교육 철학

- 적용 버전: sha256:c1f286dbaa3a502135fbfd2ca819735359873a210f956252e1007e394aa2854b
- 수업 예고를 먼저 확정하고 목표·경험 순서·최종 수행을 PRD와 실행 문제에 연결한다.
- 한 스텝에 새 관계 하나. 학생 수정은 0~3줄이고 대부분 값 한 곳이다. 준비 명령은 역할과 볼 곳을 밝힌다.
- 정상 관찰 → 한 곳 수정 → 실행 → 변경 후 관찰을 할 일과 해설에 드러낸다.
- 객관식·결과값 입력 없이 실제 명령과 실제 API 상태·채점기 자신의 HTTP 요청으로 판정한다.
- 로컬 실습 환경이 확인한 동작만 가르치고 라우팅·NAT·NACL·피어링·보안 그룹의 AWS 동등성을 주장하지 않는다.
- 문제마다 소유 라벨의 독립 실습 상태에서 시작하고, 해설은 별도 실습 상태에서 시연한다.

## 선택 교육 전략

- 명령은 직접 입력하고 자주 쓰는 옵션은 본문의 복사 블록으로 준다. 상태 변화는 읽기 전용 list-servers.sh 표로 반복 확인한다. 오류 수정 과제는 실행 전에 대상을 확인하거나(3) 실제 거절을 본 뒤 원인을 없앤다(5·6). 마지막 수행은 새 개념 없이 4·5를 조합한다.

## 챕터·단원·스텝과 핵심 흐름

### 서버를 멈추고 다시 켜요

교육 목표: 멈춘 서버는 자리와 주소를 그대로 가지고 다시 켤 수 있어요. 상태가 바뀌는 데 시간이 걸려요.

#### 멈추고 다시 켜기

교육 목표: stop·start의 상태 변화와 재시작 뒤 남는 것을 확인하고, 명령의 대상 서버를 ID로 골라요.

공통 전제: 실습 환경이 VPC 10.91.0.0/16에 서브넷 A·B를 만들고, A에 클라이언트 서버, B에 자바 서버를 실행해 둬요. 문제마다 새 실습 상태에서 시작하고, 서버를 준비하는 데 몇 분 걸릴 수 있어요. 모든 aws 명령은 이 컴퓨터의 로컬 실습 주소로만 가요.

**응답하는 서버를 멈추세요**

스텝 코드: stp_8501d14f-3b50-4c04-8fb6-c27fa6923577

교육 목표: 서버를 멈추면(stop) 상태가 stopping을 거쳐 stopped가 되고, 그동안 요청에 응답하지 않아요.

수업 예고의 1번째 경험이다.

시작: VPC 10.91.0.0/16, 서브넷 A(클라이언트 running)·B(자바 서버 running, HTTP 응답). 준비 파일은 읽기 전용 list-servers.sh.
행동: client-request로 응답 확인 → stop-instances 직접 입력 → 표로 stopping→stopped 확인 → client-request 다시.
관찰 근거: 응답의 PreviousState·CurrentState, 표의 상태, 멈춘 뒤 연결 실패.
판정: 초기 상태(running) 실패, 정답 통과. 종료 실패, 클라이언트를 멈추면 실패. stopping은 정해진 시간 안에서 기다린다.

**멈춘 서버를 다시 켜세요**

스텝 코드: stp_65e476ad-0cc4-4bed-a6e7-e80bd1c63bcf

교육 목표: 멈춘 서버를 다시 켜면 같은 서버가 같은 사설 주소로 running이 돼요. 그 안의 프로그램은 저절로 다시 뜨지 않아요.

수업 예고의 2번째 경험이다.

시작: 1번과 같은 구성. 자바 서버는 HTTP 응답을 확인한 뒤 준비 단계에서 stopped로 만든다(시작 설명에서 먼저 알림).
행동: 표로 stopped·주소 확인 → start-instances → 표로 running·같은 주소 확인 → client-request.
관찰 근거: CurrentState pending, 표의 running과 같은 사설 주소, 연결 거절(user-data는 처음 실행 때만 돈다).
판정: 초기 상태(stopped) 실패, 정답 통과. 새 서버를 만드는 우회는 「새 서버」로 실패. 종료하면 실패.
주의: 프로그램 자동 기동(서비스 등록)은 다루지 않고 안 뜬다는 사실만 관찰한다.

**멈출 서버를 골라 멈추세요**

스텝 코드: stp_25c6d982-502f-4aff-bf81-812df3e61cac

교육 목표: 명령은 --instance-ids가 가리키는 서버에만 가요. 실행 전에 그 ID가 어느 서버인지 확인해요.

수업 예고의 3번째 경험이다.

시작: 1번과 같은 구성. 본문의 시작 명령은 --instance-ids "$LAB_CLIENT_ID"(서브넷 A의 클라이언트 서버).
행동: 표 → echo로 시작 명령의 ID 확인 → ID 한 곳을 자바 서버로 고쳐 실행 → 표.
관찰 근거: 표의 두 서버 ID·서브넷, echo로 본 ID, 고친 뒤 두 서버의 상태.
판정: 시작 명령 그대로 실행하면 클라이언트가 멈춰 실패(「초기화」로 복구). 둘 다 멈추면 실패. 자바 서버 ID를 문자 그대로 적어도 통과.

### 없애고, 순서대로 지워요

교육 목표: 종료한 서버는 돌아오지 않아요. 지울 때는 안에 든 자원부터 서버 → 서브넷 → VPC 순서로 지워요.

#### 종료와 삭제 의존성

교육 목표: terminate의 결과와, 서버가 남은 서브넷이 거절되는 이유를 실제 오류로 확인해요.

공통 전제: 앞 장과 같은 구성에서 시작해요. 서버를 없애거나 자원을 지우는 문제예요.

**서버를 종료하세요**

스텝 코드: stp_fa217c4b-6db8-4c1d-9df0-483147439d4c

교육 목표: 종료한 서버(terminated)는 다시 켤 수 없어요. 멈춘 서버와 달라요.

수업 예고의 4번째 경험이다.

시작: 1번과 같은 구성.
행동: terminate-instances → 표로 shutting-down→terminated 확인 → start-instances 시도.
관찰 근거: CurrentState shutting-down, 표의 terminated, IncorrectInstanceState 거절.
판정: 초기 상태 실패, 정답 통과. 멈추기만 하면 실패. 클라이언트를 종료하면 실패.

**서브넷 B를 지우세요**

스텝 코드: stp_0cbeda4d-c73d-49e7-882f-88d6bc4c5480

교육 목표: 서버가 남아 있는 서브넷은 지울 수 없어요. 그 안의 서버부터 종료해야 해요.

수업 예고의 5번째 경험이자 대표 문제다.

시작: 1번과 같은 구성.
행동: delete-subnet(DependencyViolation) → 표로 남은 서버 확인 → terminate → terminated 확인 → 같은 delete-subnet → 서브넷 목록.
관찰 근거: 실제 DependencyViolation, 표의 서브넷 ID, 삭제 뒤 서브넷 목록.
판정: 초기 상태 실패, 정답 통과. 멈추기만 하면 삭제가 거절돼 실패. 서브넷 A 삭제·클라이언트 종료 실패. 출력 위조 실패.

#### 마지막 수행

교육 목표: 새 개념 없이 종료와 삭제 순서를 조합해 VPC 하나를 정리해요.

공통 전제: 서버 두 대와 서브넷 두 개가 든 VPC를 통째로 정리해요.

**실습 VPC를 모두 정리하세요**

스텝 코드: stp_eb061d59-86eb-4cd6-a985-e05e8e9389d6

교육 목표: 거절 메시지를 따라 서버 → 서브넷 → VPC 순서로 모두 지워요.

수업 예고의 6번째 경험이자 마지막 수행이다. 새 개념 없이 4·5번을 조합한다.

시작: 1번과 같은 구성(서버 두 대 running, 서브넷 둘).
행동: delete-vpc(거절) → 남은 자원 확인 → 서버 둘 종료 → 서브넷 둘 삭제 → delete-vpc → describe-vpcs.
관찰 근거: DependencyViolation, 빈 서브넷 목록, InvalidVpcID.NotFound.
판정: 소유 VPC가 목록에 없으면 통과. 서버를 멈추기만 하거나 서브넷 하나만 지우면 VPC가 남아 실패.

## 채점

- 채점기는 실습 소유 기록(VPC·준비 서브넷·준비 인스턴스 ID)과 실제 EC2 API 상태를 읽는다. 학생 셸 변수·명령 문자열·터미널 출력은 근거가 아니다.
- pending·stopping·shutting-down은 정해진 시간 안에서 안정 상태가 될 때까지 기다려 판정한다. API가 더는 나열하지 않는 서버는 종료된 것으로 본다.
- 목표별로 준비 서버의 상태(stopped·running+같은 주소·terminated), 서버 서브넷 또는 VPC의 부재, 남겨 둘 서브넷·클라이언트 running, 새 서버 0대를 확인한다.
- 런타임 중단·준비 실패는 오답이 아니라 환경 오류다. 수명주기 목표는 준비 서버가 멈춰 있어도 환경 오류로 보지 않는다.

## 초기화

- 스텝마다 소유 라벨의 새 Floci 상태에서 준비 자원을 만들고 시작 상태 설명에서 먼저 알린다. 2번은 응답을 확인한 서버를 준비 단계에서 멈춘다. 「초기화」는 이전 런타임만 정리하고 준비 파일을 되돌린다. 해설은 임시 실습 상태에서 시연한다.

## 해설

- 명령 하나의 실제 출력을 읽은 뒤 다음 행동으로 넘어간다. 기다림은 aws ec2 wait로 보여 주고, 학생에게는 표를 다시 확인하라고 한다. 실제 음성 동기화는 앱 확인이 필요하다.

## 검증과 완료

- 단위: cargo test --lib cloud_practice(목표 검증·수명주기 구성).
- 수업 데이터: 공개 수업 JSON의 6개 스텝을 네이티브 제출 경로(check_exercise)로 실행한다. 초기 실패, 해설 재생 통과, 대표 오답 실패를 확인한다.
- 빌드: build-redesigned-git --lesson, narration_review, build-redesigned-course-bundle --check, lesson_registry. 앱 파일럿과 맥 검증은 따로 기록한다.

## 대표 문제 초안

- step_id: stp_0cbeda4d-c73d-49e7-882f-88d6bc4c5480
- prompt: 서브넷은 `aws ec2 delete-subnet`으로 지워요. 그런데 안에 서버가 남아 있으면 거절돼요. 멈춘 서버도 남아 있는 거예요.

이번 문제는 새 실습 상태에서 시작해요. 실습 환경이 VPC 10.91.0.0/16 안에 서브넷 A 10.91.1.0/24와 서브넷 B 10.91.2.0/24를 만들어 뒀어요. 서브넷 A에는 클라이언트 서버(`LAB_CLIENT_ID`), 서브넷 B에는 자바 서버(`LAB_SERVER_ID`)가 실행 중이에요. 자바 서버의 사설 IP 주소는 `LAB_SERVER_IP`에 있어요.

서브넷 B를 지우세요. 서브넷 A와 클라이언트 서버는 그대로 둬야 해요.

편집기의 `list-servers.sh` 탭(읽기 전용)은 서버의 ID·서브넷 ID·사설 IP 주소·상태를 표로 보여 주는 준비 명령이에요.

**복사해서 쓰는 옵션**

실습 주소와 준비된 자원의 ID는 아래 블록에서 언제든 복사해 붙여 넣을 수 있어요.

```
--endpoint-url "$LAB_ENDPOINT"
```

```
--subnet-id "$LAB_SUBNET_B_ID"
```

```
--instance-ids "$LAB_SERVER_ID"
```

**할 일**

1. 터미널에 `aws ec2 delete-subnet --endpoint-url "$LAB_ENDPOINT" --subnet-id "$LAB_SUBNET_B_ID"`를 입력하고 Enter를 누르세요. 오류 메시지에서 오류 이름을 찾으세요.
2. 터미널에 `bash list-servers.sh`를 입력하세요. 서브넷 B(`LAB_SUBNET_B_ID`)에 남아 있는 서버를 찾으세요.
3. 그 서버를 `aws ec2 terminate-instances --endpoint-url "$LAB_ENDPOINT" --instance-ids "$LAB_SERVER_ID"`로 종료하세요.
4. `bash list-servers.sh`를 다시 실행해 그 서버가 `terminated`가 될 때까지 확인하세요.
5. ↑ 키로 1번 명령을 다시 불러와 Enter를 누르세요.
6. 터미널에 `aws ec2 describe-subnets --endpoint-url "$LAB_ENDPOINT" --filters Name=vpc-id,Values="$LAB_VPC_ID"`를 입력하세요. 서브넷 A만 남았는지 확인하고 제출 버튼을 누르세요.
- starter_state: VPC 10.91.0.0/16, 서브넷 A(클라이언트 running)·B(자바 서버 running).
- expected_action: delete-subnet의 DependencyViolation을 보고, 서브넷 B의 서버를 종료한 뒤 같은 delete-subnet을 다시 실행한다.
- acceptance: 소유 VPC에 서브넷 B가 없고, 서브넷 A·클라이언트 running이 그대로이며 새 서버가 없다. 멈추기만 한 경우·A 삭제·클라이언트 종료는 실패한다.
- reset: 「초기화」는 새 Floci 상태와 같은 준비 자원을 돌려준다.
- narration: 실제 DependencyViolation을 읽고, 멈춘 서버도 자리를 차지한다는 「조심하세요」를 짚은 뒤 종료하고 다시 지운다.

## 제작 승인

- PRD와 대표 문제의 승인을 함께 확인해요.
- 승인된 범위 안의 수정은 가능해요. 목표나 교육 기법 변경은 다시 승인받아요.
- 내용 식별 해시: 2313b7786a5face66fdd0d11cc95cea8e147165cff034488093ab261d5773b13

