# 자바 · 비교로 배송비를 고르는 과정 — 사용자 지적 2문제 (2026-10-28)

게시: java-conditions-6 → java-conditions-7 (sha256 9196e21d…). 앱 빌드·배포와 무관한 수업 개정본.

## 1번 「주문 금액이 무료배송 기준 이상인지 출력하세요」 (stp_43daa047)

- 지적: 「amount와 limit을 비교」가 방향·목적을 흐림. 「20,000원으로 바꿔 실행해 보고 처음 값으로 되돌리세요」가 여러 시점의 행동을 한 항목에 묶음.
- 본문: amount=주문 금액, limit=무료배송 기준 금액, 출력할 것=무료배송 대상 여부(true/false)를 먼저 말한다. 「알아두세요」에 true=대상, false=대상 아님을 더했다.
- 할 일(7개): 맨 아래 주석 다음 줄에 출력문 → 실행해 false 확인 → 19999를 20000으로 → 실행해 true 확인 → 19999로 되돌림 → 실행해 false 확인 → 제출.
- 해설 8문장: 같은 순서·같은 대상으로 고침. 예) 「false가 나왔어요. 19,999원은 20,000원보다 작으니 거짓이에요.」 → 「false가 나왔어요. 19,999원은 기준보다 1원 적어서 무료배송 대상이 아니에요.」

## 4번 「할인으로 줄어든 금액으로 무료배송 여부를 다시 판단하세요」 (stp_98425c81)

- 지적: 안내만으로 무엇을 해야 할지 모름. 「더 직관적으로 딱딱 순서를 정해줘」.
- 본문: 시작 사실(free=true 저장) → 할인으로 amount=19,999 → free에 할인 전 true가 남음 → 목표(기존 free에 다시 계산해 저장, 새로 선언 안 함).
- 할 일(5개): 실행해 true 확인 → amount = amount - coupon; 줄 찾기 → 출력문 바로 위 맨 아래 주석 다음 줄에 대입문 → 실행해 false 확인 → 제출.
- 해설 6문장 고침, 첫 상세 발화 강조를 「그런데 free에는 할인 전 결과인 true가 그대로 남아 있어요.」로 옮김(옛 anchor 문장이 본문에서 사라짐).

## 바뀌지 않은 것

코드(starter/solution), 테스트·변형 채점, 해설 동작(patch_code/run 순서·내용), 문제 ID·제목·순서. 공개 java-conditions-6과 경로 단위 비교에서 바뀐 경로: revision, 두 문제 goal, 발화 text/say 14개, 강조 target 1개(4번). tools/publish-narration-audit.py가 이 밖의 변경을 거부함(음성 테스트: solution·다른 문제 goal·patch 내용·동작 삭제·허용 안 된 target을 모두 거부).

## 검증

- 실제 Java 실행: validate_redesigned_lesson 8문제 통과(해설 run 출력 false/true/false, 정답·준비 코드·오답·대안 정답).
- build-redesigned-git --check 전 수업, narration_review status uncovered 0 / open 0, course bundle --check, 수업 도입 순서 별도 검사 통과.
- test_narration_openings.py는 과거 고정 스냅샷 비교라 sql-first·java-values(기존)·java-conditions(이번 goal 변경)와 누적 수에서 실패. 기준선은 갱신하지 않음.
- 실제 합성 음성 청취: 하지 않음.

## 후속: 4번 쿠폰 1원 → 1,000원 (2026-10-28 사용자 「문제에서 쿠폰이 1이면 뭔가 이상하잖아」)

게시: java-conditions-7 → java-conditions-8 (sha256 b95f287c…). 8번 결과 문장 1개 수정도 같은 개정에 포함.

- 바꾼 것(승인된 상수와 그 설명만): starter·solution의 `int coupon = 1;` → `int coupon = 1000;`, 해설 patch_code before(1→0 시연)·after(0→되돌림)의 같은 상수,
  goal 2곳(「1,000원을 할인해 amount는 19,000원」, 할 일 2번 「19,000원으로 바뀌어요」), 해설 4문장(1,000원 줄어요 / 19,000원 ×2 / 1000으로 되돌려요),
  approved-prd core_flow(「coupon 1000원만큼 amount를 19000으로」, 승인 근거에 이번 지시 추가 후 재해시).
- 유지: 문제 ID·제목·순서, 학습 목표, 비교식 `free = amount >= limit;`, tests(false), variations(coupon 0 → true, amount 30000 → true), 오답 사례, 다른 문제의 19,999/20,001 경계 실험, 강조 대상, run 줄 번호.
- 게시 가드: allowed-changes.json에 이 스텝만 code_constant {from 「int coupon = 1;」, to 「int coupon = 1000;」}. 다른 상수·쿠폰 999·tests·variations·비교식·다른 스텝 코드·제목 변경을 모두 거부함(음성 테스트 7건).
- 실제 실행: validate_redesigned_lesson 8문제 통과(4번 해설 run 출력 true/false/true, 채점 3사례, 정답 7·오답 16). 직접 java 25 실행: 준비 코드 true(기대 false와 불일치=실패), 정답 false, coupon 0 변형 true, `free = false` 오답은 coupon 0에서 false로 거부.
- 공개 핀 읽기 확인: 코스 java-conditions-8 = 로컬 파일 바이트 동일, java-values-7 그대로.
- 실제 합성 음성 청취: 하지 않음.
