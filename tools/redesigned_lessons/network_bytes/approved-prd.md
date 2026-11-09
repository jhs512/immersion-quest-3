# 네트워크 · 글자를 바이트로 보내기

상태: approved
수업 코드: lsn_3e49154e-8272-466a-b449-333849968825
코스: crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf

이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.

## 수업 교육 목표

- 글자와 바이트를 구별하고 같은 문자 인코딩으로 복원해요.

## 대상과 선수 지식

- 네트워크를 처음 배우며 자바의 기본 문법을 익힌 학습자
- 자바 변수·배열·조건·반복·메서드·기본 예외
- java-testing

## 제작 범위

- 보낼 바이트 수를 구하세요
- 같은 규칙으로 글자를 복원하세요
- 바이트를 양수 범위로 읽으세요
- 바이트 일부만 복원하세요

## 제외 범위

- 외부 인터넷·관리자 권한·운영체제 네트워크 설정
- 이 수업 예고에서 약속하지 않은 프로토콜과 운영 실무

## 근거와 확인 한계

- TCP는 바이트 스트림이며 응용 메시지 경계를 제공하지 않는다. — 공식 명세/API를 열어 확인했다. 실제 실행 근거는 .scratch/network-foundations/execution-evidence.json에 별도로 남긴다.; 확인 2026-11-09. [원문](https://www.rfc-editor.org/rfc/rfc9293.html)
- UDP는 데이터그램을 다루며 전달·중복 방지를 보장하지 않는다. — 공식 명세/API를 열어 확인했다. 실제 실행 근거는 .scratch/network-foundations/execution-evidence.json에 별도로 남긴다.; 확인 2026-11-09. [원문](https://www.rfc-editor.org/rfc/rfc768.html)
- 이름·이름 서버·해석기·캐시를 구별한다. — 공식 명세/API를 열어 확인했다. 실제 실행 근거는 .scratch/network-foundations/execution-evidence.json에 별도로 남긴다.; 확인 2026-11-09. [원문](https://www.rfc-editor.org/rfc/rfc1034.html)
- HTTP 메서드·상태·표현 메타데이터를 구별한다. — 공식 명세/API를 열어 확인했다. 실제 실행 근거는 .scratch/network-foundations/execution-evidence.json에 별도로 남긴다.; 확인 2026-11-09. [원문](https://www.rfc-editor.org/rfc/rfc9110.html)
- IPv4 프리픽스 표기와 더 구체적인 경로를 구별한다. — 공식 명세/API를 열어 확인했다. 실제 실행 근거는 .scratch/network-foundations/execution-evidence.json에 별도로 남긴다.; 확인 2026-11-09. [원문](https://www.rfc-editor.org/rfc/rfc4632.html)
- Socket의 자기·상대 끝점과 스트림 API를 확인한다. — 공식 명세/API를 열어 확인했다. 실제 실행 근거는 .scratch/network-foundations/execution-evidence.json에 별도로 남긴다.; 확인 2026-11-09. [원문](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/net/Socket.html)

## 적용 교육 철학

- 적용 버전: sha256:aa23fe4c2533d47df44f7630fc9f7637224f7810e0caf64add7b713facb24216
- 수업 예고를 먼저 확정하고 목표·경험 순서·최종 수행을 PRD와 실행 문제에 연결한다.
- 한 스텝에서 새 관계 하나를 1~3줄 수정으로 확인한다. 준비 코드는 역할과 관찰 대상을 밝힌다.
- 준비 코드 실행 → 한 조건 수정 → 재실행 → 관찰 근거 설명을 따른다.
- 실제 소켓과 교육용 모형의 증명 범위를 문제·해설에서 구별한다.
- 객관식·결과값 입력 대신 실제 Java 코드를 수정하고 실행으로 판정한다.
- 동적 포트·루프백·제한 시간·자동 자원 해제로 독립 실습한다.

## 선택 교육 전략

- 기존 공통 원칙을 적용한다. 준비 코드 실행 → 핵심 식 수정 → 재실행·관찰을 반복한다. 새 교육 기법은 도입하지 않는다.

## 챕터·단원·스텝과 핵심 흐름

### 글자를 바이트로 보내기

교육 목표: 글자와 바이트를 구별하고 같은 문자 인코딩으로 복원해요.

#### 첫 관계를 관찰해요

교육 목표: 글자 수와 UTF-8 바이트 수는 서로 달라요. 전송할 크기는 바이트 배열로 확인해요. / 송신과 수신이 같은 문자 인코딩을 사용해야 원래 글자로 돌아와요.

공통 전제: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

**보낼 바이트 수를 구하세요**

스텝 코드: stp_54d30ab7-26dc-4f83-83cc-8317730b68c2

교육 목표: 글자 수와 UTF-8 바이트 수는 서로 달라요. 전송할 크기는 바이트 배열로 확인해요.

수업 예고의 1번째 경험이다. UTF-8은 글자를 바이트로 바꾸는 규칙이에요. 한글이 든 메모의 바이트 수를 구하세요.

시작: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요. 준비 코드와 VALUE=6을 제공한다. memo.length()를 평가한 실제 출력을 읽는다.
행동: memo.length() 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 글자 수와 UTF-8 바이트 수는 서로 달라요. 전송할 크기는 바이트 배열로 확인해요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

**같은 규칙으로 글자를 복원하세요**

스텝 코드: stp_71c37da6-cd1e-4a70-818c-00993a236146

교육 목표: 송신과 수신이 같은 문자 인코딩을 사용해야 원래 글자로 돌아와요.

수업 예고의 2번째 경험이다. 보낼 때 UTF-8을 썼어요. 받은 바이트를 같은 규칙으로 복원하세요.

시작: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요. 준비 코드와 VALUE=6을 제공한다. StandardCharsets.US_ASCII를 평가한 실제 출력을 읽는다.
행동: StandardCharsets.US_ASCII 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 송신과 수신이 같은 문자 인코딩을 사용해야 원래 글자로 돌아와요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

#### 조건을 바꿔 적용해요

교육 목표: 0xff와 비트 AND를 하면 하위 8비트를 0~255 범위로 읽어요. / 버퍼 전체 크기와 실제 데이터 길이는 달라요. 받은 길이만큼만 글자로 바꿔요.

공통 전제: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

**바이트를 양수 범위로 읽으세요**

스텝 코드: stp_2260b7a3-cd72-4b8b-8146-10c06da56cd8

교육 목표: 0xff와 비트 AND를 하면 하위 8비트를 0~255 범위로 읽어요.

수업 예고의 3번째 경험이다. 자바 byte는 부호가 있어요. 한 옥텟을 0~255의 값으로 출력하세요. &는 같은 자리의 비트를 비교해요.

시작: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요. 준비 코드와 VALUE=6을 제공한다. (int) octet를 평가한 실제 출력을 읽는다.
행동: (int) octet 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 0xff와 비트 AND를 하면 하위 8비트를 0~255 범위로 읽어요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

**바이트 일부만 복원하세요**

스텝 코드: stp_03542e9f-f194-4c13-a57d-cfa352b469f1

교육 목표: 버퍼 전체 크기와 실제 데이터 길이는 달라요. 받은 길이만큼만 글자로 바꿔요.

수업 예고의 4번째 경험이다. 수신 버퍼에는 메모 뒤에 빈칸이 남아요. 실제 받은 바이트 수만 복원하세요.

시작: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요. 준비 코드와 VALUE=6을 제공한다. 0, buffer.length,를 평가한 실제 출력을 읽는다.
행동: 0, buffer.length, 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 버퍼 전체 크기와 실제 데이터 길이는 달라요. 받은 길이만큼만 글자로 바꿔요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

## 채점

- 실제 JDK 실행으로 기본과 변형 출력을 검사한다. 선택·결과 암기 입력을 채점하지 않는다.

## 초기화

- 매 문제 독립 JVM과 새 포트에서 시작한다. 개인 네트워크 설정은 바꾸지 않는다.

## 해설

- 문제의 요구·모형 경계·정확한 식을 강조하고 실행 전후의 근거를 설명한다. 실제 음성 동기화는 앱 검증이 필요하다.

## 검증과 완료

- 준비 코드 실패·정답 통과·동등 출력 API 풀이 통과·준비 값 7·9 변형 통과를 JDK로 확인한다.

## 대표 문제 초안

- step_id: stp_03542e9f-f194-4c13-a57d-cfa352b469f1
- prompt: 수신 버퍼에는 메모 뒤에 빈칸이 남아요. 실제 받은 바이트 수만 복원하세요.

모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.

이번 문제의 준비 코드로 새로 시작해요.
준비된 연결·값은 유지하고 표시한 식을 고치세요.

**할 일**

1. 준비 코드를 실행하고 결과를 읽으세요.
2. `0, buffer.length,` 부분을 문제의 요구에 맞게 고치세요.
3. 다시 실행하고 처음 결과와 비교하세요.
4. 수정한 코드를 제출하세요. 준비 값을 바꿔서도 검사해요.
- starter_state: // 변형 검사에서는 이 준비 값만 달라져요.
static final int VALUE = 6;

void main() throws Exception {
byte[] memo = ("한" + VALUE).getBytes(java.nio.charset.StandardCharsets.UTF_8);
byte[] buffer = java.util.Arrays.copyOf(memo, 32);
System.out.println(new String(buffer, 0, buffer.length, java.nio.charset.StandardCharsets.UTF_8));
}

- expected_action: 0, buffer.length,를 0, memo.length,로 수정한다.
- acceptance: 실제 JVM 기본·변형 실행의 출력이 기대와 일치한다. 준비 코드와 개념 오답은 거절한다.
- reset: 매 실행 새 JVM에서 시작하고 소켓은 try-with-resources로 닫는다.
- narration: 버퍼 전체 크기와 실제 데이터 길이는 달라요. 받은 길이만큼만 글자로 바꿔요.

### 대표 문제 검증 입력

```json
{
  "language": "java",
  "starter": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nbyte[] memo = (\"한\" + VALUE).getBytes(java.nio.charset.StandardCharsets.UTF_8);\nbyte[] buffer = java.util.Arrays.copyOf(memo, 32);\nSystem.out.println(new String(buffer, 0, buffer.length, java.nio.charset.StandardCharsets.UTF_8));\n}\n",
  "solution": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nbyte[] memo = (\"한\" + VALUE).getBytes(java.nio.charset.StandardCharsets.UTF_8);\nbyte[] buffer = java.util.Arrays.copyOf(memo, 32);\nSystem.out.println(new String(buffer, 0, memo.length, java.nio.charset.StandardCharsets.UTF_8));\n}\n",
  "tests": [
    {
      "input": "",
      "expected": "한6\n"
    }
  ],
  "variations": [
    {
      "values": {
        "VALUE": "7"
      },
      "expected": "한7\n"
    },
    {
      "values": {
        "VALUE": "9"
      },
      "expected": "한9\n"
    }
  ]
}
```

## 제작 승인

- PRD와 대표 문제의 승인을 함께 확인해요.
- 승인된 범위 안의 수정은 가능해요. 목표나 교육 기법 변경은 다시 승인받아요.
- 내용 식별 해시: 47ce42a15cdf062cb555e3f68dac8531caaee0350a3d6598740112526e57f159
