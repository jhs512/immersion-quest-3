# 네트워크 · TCP 바이트 흐름과 메시지 경계

상태: approved
수업 코드: lsn_3edd1620-d43f-4e21-a4a4-634a86d4c911
코스: crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf

이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.

## 수업 교육 목표

- 실제 TCP 수신과 애플리케이션의 메시지 구분 규칙을 분리해요.

## 대상과 선수 지식

- 네트워크를 처음 배우며 자바의 기본 문법을 익힌 학습자
- 자바 변수·배열·조건·반복·메서드·기본 예외
- network-dns

## 제작 범위

- 읽지 않은 나머지도 받으세요
- 보내기 횟수 대신 메시지 끝을 찾으세요
- 문자 대신 바이트 길이로 읽으세요
- 송신 종료 뒤 EOF를 확인하세요

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

### TCP 바이트 흐름과 메시지 경계

교육 목표: 실제 TCP 수신과 애플리케이션의 메시지 구분 규칙을 분리해요.

#### 첫 관계를 관찰해요

교육 목표: 한 번 읽은 뒤에도 바이트가 남아 있어요. readNBytes의 크기는 이번에 요청한 읽기 크기예요. / TCP는 바이트 흐름을 보내요. 이 프로그램의 메시지 경계는 줄바꿈 규칙으로 찾았어요.

공통 전제: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

**읽지 않은 나머지도 받으세요**

스텝 코드: stp_44e93442-9e19-4885-8cf8-8a5e104acc5d

교육 목표: 한 번 읽은 뒤에도 바이트가 남아 있어요. readNBytes의 크기는 이번에 요청한 읽기 크기예요.

수업 예고의 1번째 경험이다. 서버에는 A숫자와 B숫자 두 줄이 와요. 처음 2바이트를 읽은 뒤 나머지 바이트 수도 구하세요.

시작: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요. 준비 코드와 VALUE=6을 제공한다. System.out.println(first.length)를 평가한 실제 출력을 읽는다.
행동: System.out.println(first.length) 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 한 번 읽은 뒤에도 바이트가 남아 있어요. readNBytes의 크기는 이번에 요청한 읽기 크기예요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

**보내기 횟수 대신 메시지 끝을 찾으세요**

스텝 코드: stp_dd214a27-5e54-436d-a2a8-403c518ca841

교육 목표: TCP는 바이트 흐름을 보내요. 이 프로그램의 메시지 경계는 줄바꿈 규칙으로 찾았어요.

수업 예고의 2번째 경험이다. 프로토콜은 줄바꿈으로 메시지를 나눠요. 모두 받은 글에서 완성된 메시지 수를 구하세요.

시작: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요. 준비 코드와 VALUE=6을 제공한다. text.length()를 평가한 실제 출력을 읽는다.
행동: text.length() 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: TCP는 바이트 흐름을 보내요. 이 프로그램의 메시지 경계는 줄바꿈 규칙으로 찾았어요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

#### 조건을 바꿔 적용해요

교육 목표: 수신 길이는 바이트 단위예요. 글자 수를 읽기 크기로 쓰면 한글 메모를 중간에서 자를 수 있어요. / 입력 끝에서는 read가 -1을 돌려줘요. 받은 값 0과 입력의 끝은 서로 달라요.

공통 전제: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

**문자 대신 바이트 길이로 읽으세요**

스텝 코드: stp_a4115f51-71fb-4014-b564-3c6b3911251d

교육 목표: 수신 길이는 바이트 단위예요. 글자 수를 읽기 크기로 쓰면 한글 메모를 중간에서 자를 수 있어요.

수업 예고의 3번째 경험이다. TCP로 한글 메모를 보냈어요. 서버가 실제로 받은 바이트 배열의 길이를 출력하세요.

시작: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요. 준비 코드와 VALUE=6을 제공한다. text.length()를 평가한 실제 출력을 읽는다.
행동: text.length() 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 수신 길이는 바이트 단위예요. 글자 수를 읽기 크기로 쓰면 한글 메모를 중간에서 자를 수 있어요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

**송신 종료 뒤 EOF를 확인하세요**

스텝 코드: stp_8f9b64eb-0128-4fda-bb43-035d74e5ff56

교육 목표: 입력 끝에서는 read가 -1을 돌려줘요. 받은 값 0과 입력의 끝은 서로 달라요.

수업 예고의 4번째 경험이다. 클라이언트는 쓰기를 끝냈어요. 서버가 모든 바이트를 읽은 뒤 다음 read의 결과를 출력하세요.

시작: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요. 준비 코드와 VALUE=6을 제공한다. System.out.println(all.length)를 평가한 실제 출력을 읽는다.
행동: System.out.println(all.length) 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 입력 끝에서는 read가 -1을 돌려줘요. 받은 값 0과 입력의 끝은 서로 달라요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

## 채점

- 실제 JDK 실행으로 기본과 변형 출력을 검사한다. 선택·결과 암기 입력을 채점하지 않는다.

## 초기화

- 매 문제 독립 JVM과 새 포트에서 시작한다. 개인 네트워크 설정은 바꾸지 않는다.

## 해설

- 문제의 요구·모형 경계·정확한 식을 강조하고 실행 전후의 근거를 설명한다. 실제 음성 동기화는 앱 검증이 필요하다.

## 검증과 완료

- 준비 코드 실패·정답 통과·동등 출력 API 풀이 통과·준비 값 7·9 변형 통과를 JDK로 확인한다.

## 대표 문제 초안

- step_id: stp_8f9b64eb-0128-4fda-bb43-035d74e5ff56
- prompt: 클라이언트는 쓰기를 끝냈어요. 서버가 모든 바이트를 읽은 뒤 다음 read의 결과를 출력하세요.

실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.

이번 문제의 준비 코드로 새로 시작해요.
준비된 연결·값은 유지하고 표시한 식을 고치세요.

**할 일**

1. 준비 코드를 실행하고 결과를 읽으세요.
2. `System.out.println(all.length)` 부분을 문제의 요구에 맞게 고치세요.
3. 다시 실행하고 처음 결과와 비교하세요.
4. 수정한 코드를 제출하세요. 준비 값을 바꿔서도 검사해요.
- starter_state: // 변형 검사에서는 이 준비 값만 달라져요.
static final int VALUE = 6;

void main() throws Exception {
var loopback = java.net.InetAddress.getByName("127.0.0.1");
// 포트 0은 운영체제에 빈 포트 배정을 요청해요.
try (var listener = new java.net.ServerSocket(0, 1, loopback)) {
    listener.setSoTimeout(2000);
    try (var client = new java.net.Socket()) {
        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);
        client.setSoTimeout(2000);
        try (var server = listener.accept()) {
            server.setSoTimeout(2000);
// 이번 프로토콜의 전송 바이트를 준비해요.
byte[] payload = ("A" + VALUE + "\nB" + VALUE + "\n").getBytes(java.nio.charset.StandardCharsets.UTF_8);
client.getOutputStream().write(payload);
// readAllBytes가 끝나도록 송신 방향만 닫아요.
client.shutdownOutput();
byte[] all = server.getInputStream().readAllBytes();
System.out.println(all.length);
        }
    }
}
}

- expected_action: System.out.println(all.length)를 System.out.println(server.getInputStream().read())로 수정한다.
- acceptance: 실제 JVM 기본·변형 실행의 출력이 기대와 일치한다. 준비 코드와 개념 오답은 거절한다.
- reset: 매 실행 새 JVM에서 시작하고 소켓은 try-with-resources로 닫는다.
- narration: 입력 끝에서는 read가 -1을 돌려줘요. 받은 값 0과 입력의 끝은 서로 달라요.

### 대표 문제 검증 입력

```json
{
  "language": "java",
  "starter": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nvar loopback = java.net.InetAddress.getByName(\"127.0.0.1\");\n// 포트 0은 운영체제에 빈 포트 배정을 요청해요.\ntry (var listener = new java.net.ServerSocket(0, 1, loopback)) {\n    listener.setSoTimeout(2000);\n    try (var client = new java.net.Socket()) {\n        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);\n        client.setSoTimeout(2000);\n        try (var server = listener.accept()) {\n            server.setSoTimeout(2000);\n// 이번 프로토콜의 전송 바이트를 준비해요.\nbyte[] payload = (\"A\" + VALUE + \"\\nB\" + VALUE + \"\\n\").getBytes(java.nio.charset.StandardCharsets.UTF_8);\nclient.getOutputStream().write(payload);\n// readAllBytes가 끝나도록 송신 방향만 닫아요.\nclient.shutdownOutput();\nbyte[] all = server.getInputStream().readAllBytes();\nSystem.out.println(all.length);\n        }\n    }\n}\n}\n",
  "solution": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nvar loopback = java.net.InetAddress.getByName(\"127.0.0.1\");\n// 포트 0은 운영체제에 빈 포트 배정을 요청해요.\ntry (var listener = new java.net.ServerSocket(0, 1, loopback)) {\n    listener.setSoTimeout(2000);\n    try (var client = new java.net.Socket()) {\n        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);\n        client.setSoTimeout(2000);\n        try (var server = listener.accept()) {\n            server.setSoTimeout(2000);\n// 이번 프로토콜의 전송 바이트를 준비해요.\nbyte[] payload = (\"A\" + VALUE + \"\\nB\" + VALUE + \"\\n\").getBytes(java.nio.charset.StandardCharsets.UTF_8);\nclient.getOutputStream().write(payload);\n// readAllBytes가 끝나도록 송신 방향만 닫아요.\nclient.shutdownOutput();\nbyte[] all = server.getInputStream().readAllBytes();\nSystem.out.println(server.getInputStream().read());\n        }\n    }\n}\n}\n",
  "tests": [
    {
      "input": "",
      "expected": "-1\n"
    }
  ],
  "variations": [
    {
      "values": {
        "VALUE": "7"
      },
      "expected": "-1\n"
    },
    {
      "values": {
        "VALUE": "9"
      },
      "expected": "-1\n"
    }
  ]
}
```

## 제작 승인

- PRD와 대표 문제의 승인을 함께 확인해요.
- 승인된 범위 안의 수정은 가능해요. 목표나 교육 기법 변경은 다시 승인받아요.
- 내용 식별 해시: 6b3cf04fd0b6019d0c5485d9c14a8f8bd48dcadfa41dfb53e6f8e4b631acc779
