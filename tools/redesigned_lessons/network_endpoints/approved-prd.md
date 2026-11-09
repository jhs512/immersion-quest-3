# 네트워크 · 주소와 포트로 연결하기

상태: approved
수업 코드: lsn_80ccc79f-6d71-4703-b6f2-eb695a68ab03
코스: crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf

이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.

## 수업 교육 목표

- 서버의 대기 주소와 포트, 연결의 양 끝을 실제 소켓으로 확인해요.

## 대상과 선수 지식

- 네트워크를 처음 배우며 자바의 기본 문법을 익힌 학습자
- 자바 변수·배열·조건·반복·메서드·기본 예외
- network-bytes

## 제작 범위

- 연결한 서버 포트를 확인하세요
- 서버가 보는 상대 포트를 확인하세요
- 클라이언트가 보낸 바이트를 읽으세요
- 서버의 응답을 클라이언트에서 읽으세요

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

### 주소와 포트로 연결하기

교육 목표: 서버의 대기 주소와 포트, 연결의 양 끝을 실제 소켓으로 확인해요.

#### 첫 관계를 관찰해요

교육 목표: 클라이언트의 상대 포트가 서버의 대기 포트와 같아요. 자기 포트와 비교하면 다른 대상을 보게 돼요. / 서버에서 보는 상대 포트는 클라이언트의 자기 포트예요.

공통 전제: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

**연결한 서버 포트를 확인하세요**

스텝 코드: stp_e98c8c1e-d1da-489a-8107-3c13424d5213

교육 목표: 클라이언트의 상대 포트가 서버의 대기 포트와 같아요. 자기 포트와 비교하면 다른 대상을 보게 돼요.

수업 예고의 1번째 경험이다. IP 주소는 연결할 장치를 가리켜요. 포트는 그 장치의 통신 끝점을 구별해요. 클라이언트의 상대 포트와 서버 대기 포트를 비교하세요.

시작: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요. 준비 코드와 VALUE=6을 제공한다. client.getLocalPort()를 평가한 실제 출력을 읽는다.
행동: client.getLocalPort() 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 클라이언트의 상대 포트가 서버의 대기 포트와 같아요. 자기 포트와 비교하면 다른 대상을 보게 돼요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

**서버가 보는 상대 포트를 확인하세요**

스텝 코드: stp_f607bddf-915f-4658-bf5a-a05ea632a3df

교육 목표: 서버에서 보는 상대 포트는 클라이언트의 자기 포트예요.

수업 예고의 2번째 경험이다. 연결은 양 끝을 가져요. 서버가 받은 연결의 상대 포트를 클라이언트 자기 포트와 비교하세요.

시작: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요. 준비 코드와 VALUE=6을 제공한다. server.getLocalPort()를 평가한 실제 출력을 읽는다.
행동: server.getLocalPort() 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 서버에서 보는 상대 포트는 클라이언트의 자기 포트예요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

#### 조건을 바꿔 적용해요

교육 목표: 이번 값은 계산으로 만든 값이 아니라 실제 서버 소켓에서 읽은 한 바이트예요. / 요청을 읽은 값과 응답을 읽은 값이 구별돼요. 응답도 반대쪽 소켓을 통해 와요.

공통 전제: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

**클라이언트가 보낸 바이트를 읽으세요**

스텝 코드: stp_f8aadf7e-7fce-482f-9670-b062d308fc1f

교육 목표: 이번 값은 계산으로 만든 값이 아니라 실제 서버 소켓에서 읽은 한 바이트예요.

수업 예고의 3번째 경험이다. 연결 준비와 데이터 수신은 달라요. 클라이언트가 보낸 VALUE 한 바이트를 서버에서 읽으세요.

시작: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요. 준비 코드와 VALUE=6을 제공한다. VALUE + 1를 평가한 실제 출력을 읽는다.
행동: VALUE + 1 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 이번 값은 계산으로 만든 값이 아니라 실제 서버 소켓에서 읽은 한 바이트예요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

**서버의 응답을 클라이언트에서 읽으세요**

스텝 코드: stp_b1d6f73e-fc59-4e08-ba81-da4835f7def7

교육 목표: 요청을 읽은 값과 응답을 읽은 값이 구별돼요. 응답도 반대쪽 소켓을 통해 와요.

수업 예고의 4번째 경험이다. 요청을 받은 서버가 VALUE+1을 응답해요. 클라이언트의 수신 쪽에서 읽으세요.

시작: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요. 준비 코드와 VALUE=6을 제공한다. System.out.println(request)를 평가한 실제 출력을 읽는다.
행동: System.out.println(request) 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 요청을 읽은 값과 응답을 읽은 값이 구별돼요. 응답도 반대쪽 소켓을 통해 와요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

## 채점

- 실제 JDK 실행으로 기본과 변형 출력을 검사한다. 선택·결과 암기 입력을 채점하지 않는다.

## 초기화

- 매 문제 독립 JVM과 새 포트에서 시작한다. 개인 네트워크 설정은 바꾸지 않는다.

## 해설

- 문제의 요구·모형 경계·정확한 식을 강조하고 실행 전후의 근거를 설명한다. 실제 음성 동기화는 앱 검증이 필요하다.

## 검증과 완료

- 준비 코드 실패·정답 통과·동등 출력 API 풀이 통과·준비 값 7·9 변형 통과를 JDK로 확인한다.

## 대표 문제 초안

- step_id: stp_b1d6f73e-fc59-4e08-ba81-da4835f7def7
- prompt: 요청을 받은 서버가 VALUE+1을 응답해요. 클라이언트의 수신 쪽에서 읽으세요.

실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.

이번 문제의 준비 코드로 새로 시작해요.
준비된 연결·값은 유지하고 표시한 식을 고치세요.

**할 일**

1. 준비 코드를 실행하고 결과를 읽으세요.
2. `System.out.println(request)` 부분을 문제의 요구에 맞게 고치세요.
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
client.getOutputStream().write(VALUE);
int request = server.getInputStream().read();
server.getOutputStream().write(request + 1);
System.out.println(request);
        }
    }
}
}

- expected_action: System.out.println(request)를 System.out.println(client.getInputStream().read())로 수정한다.
- acceptance: 실제 JVM 기본·변형 실행의 출력이 기대와 일치한다. 준비 코드와 개념 오답은 거절한다.
- reset: 매 실행 새 JVM에서 시작하고 소켓은 try-with-resources로 닫는다.
- narration: 요청을 읽은 값과 응답을 읽은 값이 구별돼요. 응답도 반대쪽 소켓을 통해 와요.

### 대표 문제 검증 입력

```json
{
  "language": "java",
  "starter": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nvar loopback = java.net.InetAddress.getByName(\"127.0.0.1\");\n// 포트 0은 운영체제에 빈 포트 배정을 요청해요.\ntry (var listener = new java.net.ServerSocket(0, 1, loopback)) {\n    listener.setSoTimeout(2000);\n    try (var client = new java.net.Socket()) {\n        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);\n        client.setSoTimeout(2000);\n        try (var server = listener.accept()) {\n            server.setSoTimeout(2000);\nclient.getOutputStream().write(VALUE);\nint request = server.getInputStream().read();\nserver.getOutputStream().write(request + 1);\nSystem.out.println(request);\n        }\n    }\n}\n}\n",
  "solution": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nvar loopback = java.net.InetAddress.getByName(\"127.0.0.1\");\n// 포트 0은 운영체제에 빈 포트 배정을 요청해요.\ntry (var listener = new java.net.ServerSocket(0, 1, loopback)) {\n    listener.setSoTimeout(2000);\n    try (var client = new java.net.Socket()) {\n        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);\n        client.setSoTimeout(2000);\n        try (var server = listener.accept()) {\n            server.setSoTimeout(2000);\nclient.getOutputStream().write(VALUE);\nint request = server.getInputStream().read();\nserver.getOutputStream().write(request + 1);\nSystem.out.println(client.getInputStream().read());\n        }\n    }\n}\n}\n",
  "tests": [
    {
      "input": "",
      "expected": "7\n"
    }
  ],
  "variations": [
    {
      "values": {
        "VALUE": "7"
      },
      "expected": "8\n"
    },
    {
      "values": {
        "VALUE": "9"
      },
      "expected": "10\n"
    }
  ]
}
```

## 제작 승인

- PRD와 대표 문제의 승인을 함께 확인해요.
- 승인된 범위 안의 수정은 가능해요. 목표나 교육 기법 변경은 다시 승인받아요.
- 내용 식별 해시: 922e224496906b77a3dded31c4dec340481e81541dc8b4e3e9ed6e25ef5a12d3
