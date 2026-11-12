# 대표 문제 초안 — 서브넷 B를 지우세요

Status: draft_for_review
관련: [PRD 초안](prd.draft.md) 스텝 5

## 시작 상태 (학생에게 먼저 알림)

준비된 VPC `10.91.0.0/16` 안에 서브넷이 두 개 있어요.

- 서브넷 A `10.91.1.0/24`: 클라이언트 서버 한 대(`$LAB_CLIENT_ID`)
- 서브넷 B `10.91.2.0/24`: 자바 서버 한 대(`$LAB_SERVER_ID`)

## 목표

서브넷 B를 지우세요. 서브넷 A와 클라이언트는 그대로 둬야 해요.

## 본문 복사 블록

```bash
  --endpoint-url "$LAB_ENDPOINT" \
```

## 할 일

1. `aws ec2 delete-subnet`에 `--subnet-id "$LAB_SUBNET_B_ID"`를 붙여 직접 입력하고 실행하세요.
2. 거절 메시지에서 오류 이름을 찾으세요.
3. `aws ec2 describe-instances`로 서브넷 B에 남아 있는 서버를 찾으세요.
4. 그 서버를 `terminate-instances`로 종료하세요.
5. `describe-instances`를 다시 실행해 `terminated`가 될 때까지 확인하세요.
6. 1번 명령을 ↑ 키로 불러와 다시 실행하세요.
7. `describe-subnets`로 서브넷 A만 남았는지 확인하고 제출하세요.

변경 전 관찰(1–3) → 원인 제거(4) → 상태 확인(5) → 같은 명령 재실행(6) → 변경 후 관찰(7) 순서다. 거절 메시지 원문은 실제 출력을 그대로 읽는다(측정: `DependencyViolation … has dependencies and cannot be deleted.`).

## 정답 명령

```bash
# 서브넷 B에 서버가 남아 있으면 거절돼요(DependencyViolation).
aws ec2 delete-subnet \
  --endpoint-url "$LAB_ENDPOINT" \
  --subnet-id "$LAB_SUBNET_B_ID"

# 그 서버부터 없애요. 멈추기(stop)만 하면 여전히 거절돼요.
aws ec2 terminate-instances \
  --endpoint-url "$LAB_ENDPOINT" \
  --instance-ids "$LAB_SERVER_ID"

# shutting-down이 terminated가 될 때까지 확인해요.
aws ec2 describe-instances \
  --endpoint-url "$LAB_ENDPOINT" \
  --instance-ids "$LAB_SERVER_ID"

# 이제 같은 명령이 통과해요.
aws ec2 delete-subnet \
  --endpoint-url "$LAB_ENDPOINT" \
  --subnet-id "$LAB_SUBNET_B_ID"
```

## 채점

- 소유 VPC에 서브넷 B가 없다.
- 서브넷 A가 그대로 있다(ID·CIDR 같음).
- 클라이언트 서버가 `running`이다.
- 준비 서버는 `terminated`다(목록에 남아 있어도 된다).

## 오답과 판정

| 오답 | 결과 |
|---|---|
| 아무것도 지우지 않음(시작 상태) | 「서브넷 B가 아직 있어요」 |
| 서버를 멈추기만 하고 서브넷 삭제 | 삭제가 거절돼 B가 남음 → 실패 (측정으로 확인) |
| 서브넷 A를 지움 / 클라이언트 종료 | 「지우지 말아야 할 자원이 바뀌었어요」 → 실패 |
| VPC를 새로 만들어 그 안의 서브넷을 지움 | 소유 VPC의 B가 남음 → 실패 |
| 터미널에 성공처럼 보이는 문자열 출력 | 실제 상태가 그대로라 실패 |

## 해설의 「조심하세요」

서버를 멈추면 지운 것 같지만 아니에요. 멈춘 서버도 자리를 차지하고 있어서 서브넷이 안 지워져요.
