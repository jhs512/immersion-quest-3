# 네트워크 · HTTP 요청과 응답 읽기

상태: approved
수업 코드: lsn_1d4a522c-3b39-450f-a2c8-6c63cc883e45
코스: crs_0e63ca37-56b5-48ab-82f7-150e3987a0bf

이 문서는 제작자용 PRD예요. 학생에게 핵심 흐름이나 정답을 직접 노출하지 않아요.

## 수업 교육 목표

- HTTP/1.1의 요청·상태·본문을 실제 로컬 연결에서 구별해요.

## 대상과 선수 지식

- 네트워크를 처음 배우며 자바의 기본 문법을 익힌 학습자
- 자바 변수·배열·조건·반복·메서드·기본 예외
- network-udp

## 제작 범위

- 요청 경로를 읽으세요
- 응답 상태 코드를 읽으세요
- 본문 크기는 UTF-8 바이트로 구하세요
- 응답 본문만 읽으세요

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

### HTTP 요청과 응답 읽기

교육 목표: HTTP/1.1의 요청·상태·본문을 실제 로컬 연결에서 구별해요.

#### 첫 관계를 관찰해요

교육 목표: 첫 단어는 GET 메서드이고 둘째 단어가 요청 대상이에요. 서버가 실제로 받은 첫 줄에서 읽었어요. / HTTP 버전과 상태 코드를 구분했어요. 소켓 연결만 성공한 것과 요청 처리가 성공한 것은 달라요.

공통 전제: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

**요청 경로를 읽으세요**

스텝 코드: stp_68372fe6-8fd7-48b6-b97f-269303dbda06

교육 목표: 첫 단어는 GET 메서드이고 둘째 단어가 요청 대상이에요. 서버가 실제로 받은 첫 줄에서 읽었어요.

수업 예고의 1번째 경험이다. 클라이언트가 보낸 첫 줄은 메서드·요청 대상·버전으로 나뉘어요. 서버가 받은 요청에서 경로를 출력하세요.

시작: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요. 준비 코드와 VALUE=6을 제공한다. split(" ")[0]를 평가한 실제 출력을 읽는다.
행동: split(" ")[0] 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 첫 단어는 GET 메서드이고 둘째 단어가 요청 대상이에요. 서버가 실제로 받은 첫 줄에서 읽었어요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

**응답 상태 코드를 읽으세요**

스텝 코드: stp_b873c140-7e35-4555-8e74-119d4f551541

교육 목표: HTTP 버전과 상태 코드를 구분했어요. 소켓 연결만 성공한 것과 요청 처리가 성공한 것은 달라요.

수업 예고의 2번째 경험이다. 응답 첫 줄은 버전·상태 코드·이유 구절이에요. 클라이언트가 받은 상태 코드를 출력하세요.

시작: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요. 준비 코드와 VALUE=6을 제공한다. split(" ")[0]를 평가한 실제 출력을 읽는다.
행동: split(" ")[0] 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: HTTP 버전과 상태 코드를 구분했어요. 소켓 연결만 성공한 것과 요청 처리가 성공한 것은 달라요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

#### 조건을 바꿔 적용해요

교육 목표: 한글 본문은 글자 수와 바이트 수가 달라요. HTTP/1.1의 Content-Length에는 바이트 수를 써요. / 헤더 끝의 빈 줄 뒤에서 본문을 읽었어요. 실제 응답은 Content-Length만큼의 바이트로 끝을 판단해야 해요.

공통 전제: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

**본문 크기는 UTF-8 바이트로 구하세요**

스텝 코드: stp_e7dabc15-320a-41ac-af50-c71dd22d6cc8

교육 목표: 한글 본문은 글자 수와 바이트 수가 달라요. HTTP/1.1의 Content-Length에는 바이트 수를 써요.

수업 예고의 3번째 경험이다. Content-Length는 본문의 바이트 수예요. 한글 응답 본문에 넣을 길이를 계산하세요.

시작: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요. 준비 코드와 VALUE=6을 제공한다. body.length()를 평가한 실제 출력을 읽는다.
행동: body.length() 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 한글 본문은 글자 수와 바이트 수가 달라요. HTTP/1.1의 Content-Length에는 바이트 수를 써요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

**응답 본문만 읽으세요**

스텝 코드: stp_464d4f28-866c-4664-adc0-a81affe946cd

교육 목표: 헤더 끝의 빈 줄 뒤에서 본문을 읽었어요. 실제 응답은 Content-Length만큼의 바이트로 끝을 판단해야 해요.

수업 예고의 4번째 경험이다. 상태 줄과 헤더는 본문이 아니에요. 빈 줄까지 헤더를 읽은 뒤 본문 첫 줄을 출력하세요.

시작: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요. 준비 코드와 VALUE=6을 제공한다. System.out.println("응답 없음")를 평가한 실제 출력을 읽는다.
행동: System.out.println("응답 없음") 한 곳을 고치고 실제 JVM으로 실행한다.
관찰 근거: 헤더 끝의 빈 줄 뒤에서 본문을 읽었어요. 실제 응답은 Content-Length만큼의 바이트로 끝을 판단해야 해요.
판정: 준비 코드 거절, 대표 풀이 통과, 다른 출력 API의 동등 풀이 통과, VALUE=7·9 변형 통과를 실제 실행한다.
주의: 실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

## 채점

- 실제 JDK 실행으로 기본과 변형 출력을 검사한다. 선택·결과 암기 입력을 채점하지 않는다.

## 초기화

- 매 문제 독립 JVM과 새 포트에서 시작한다. 개인 네트워크 설정은 바꾸지 않는다.

## 해설

- 문제의 요구·모형 경계·정확한 식을 강조하고 실행 전후의 근거를 설명한다. 실제 음성 동기화는 앱 검증이 필요하다.

## 검증과 완료

- 준비 코드 실패·정답 통과·동등 출력 API 풀이 통과·준비 값 7·9 변형 통과를 JDK로 확인한다.

## 대표 문제 초안

- step_id: stp_464d4f28-866c-4664-adc0-a81affe946cd
- prompt: 상태 줄과 헤더는 본문이 아니에요. 빈 줄까지 헤더를 읽은 뒤 본문 첫 줄을 출력하세요.

실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.

이번 문제의 준비 코드로 새로 시작해요.
준비된 연결·값은 유지하고 표시한 식을 고치세요.

**할 일**

1. 준비 코드를 실행하고 결과를 읽으세요.
2. `System.out.println("응답 없음")` 부분을 문제의 요구에 맞게 고치세요.
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
// 실제 연결에 최소 요청을 보내요.
String request = "GET /memo/" + VALUE + " HTTP/1.1\r\nHost: localhost\r\n\r\n";
client.getOutputStream().write(request.getBytes(java.nio.charset.StandardCharsets.US_ASCII));
var requestReader = new java.io.BufferedReader(new java.io.InputStreamReader(server.getInputStream(), java.nio.charset.StandardCharsets.US_ASCII));
// 요청 헤더 끝의 빈 줄까지 서버가 읽어요.
while (!requestReader.readLine().isEmpty()) {}
String replyBody = "한" + VALUE;
byte[] reply = replyBody.getBytes(java.nio.charset.StandardCharsets.UTF_8);
String headers = "HTTP/1.1 200 OK\r\nContent-Length: " + reply.length + "\r\nConnection: close\r\n\r\n";
server.getOutputStream().write(headers.getBytes(java.nio.charset.StandardCharsets.US_ASCII));
server.getOutputStream().write(reply);
server.shutdownOutput();
var responseReader = new java.io.BufferedReader(new java.io.InputStreamReader(client.getInputStream(), java.nio.charset.StandardCharsets.UTF_8));
String line;
while (!(line = responseReader.readLine()).isEmpty()) {}
System.out.println("응답 없음");
        }
    }
}
}

- expected_action: System.out.println("응답 없음")를 System.out.println(responseReader.readLine())로 수정한다.
- acceptance: 실제 JVM 기본·변형 실행의 출력이 기대와 일치한다. 준비 코드와 개념 오답은 거절한다.
- reset: 매 실행 새 JVM에서 시작하고 소켓은 try-with-resources로 닫는다.
- narration: 헤더 끝의 빈 줄 뒤에서 본문을 읽었어요. 실제 응답은 Content-Length만큼의 바이트로 끝을 판단해야 해요.

### 대표 문제 검증 입력

```json
{
  "language": "java",
  "starter": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nvar loopback = java.net.InetAddress.getByName(\"127.0.0.1\");\n// 포트 0은 운영체제에 빈 포트 배정을 요청해요.\ntry (var listener = new java.net.ServerSocket(0, 1, loopback)) {\n    listener.setSoTimeout(2000);\n    try (var client = new java.net.Socket()) {\n        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);\n        client.setSoTimeout(2000);\n        try (var server = listener.accept()) {\n            server.setSoTimeout(2000);\n// 실제 연결에 최소 요청을 보내요.\nString request = \"GET /memo/\" + VALUE + \" HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n\";\nclient.getOutputStream().write(request.getBytes(java.nio.charset.StandardCharsets.US_ASCII));\nvar requestReader = new java.io.BufferedReader(new java.io.InputStreamReader(server.getInputStream(), java.nio.charset.StandardCharsets.US_ASCII));\n// 요청 헤더 끝의 빈 줄까지 서버가 읽어요.\nwhile (!requestReader.readLine().isEmpty()) {}\nString replyBody = \"한\" + VALUE;\nbyte[] reply = replyBody.getBytes(java.nio.charset.StandardCharsets.UTF_8);\nString headers = \"HTTP/1.1 200 OK\\r\\nContent-Length: \" + reply.length + \"\\r\\nConnection: close\\r\\n\\r\\n\";\nserver.getOutputStream().write(headers.getBytes(java.nio.charset.StandardCharsets.US_ASCII));\nserver.getOutputStream().write(reply);\nserver.shutdownOutput();\nvar responseReader = new java.io.BufferedReader(new java.io.InputStreamReader(client.getInputStream(), java.nio.charset.StandardCharsets.UTF_8));\nString line;\nwhile (!(line = responseReader.readLine()).isEmpty()) {}\nSystem.out.println(\"응답 없음\");\n        }\n    }\n}\n}\n",
  "solution": "// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\nvar loopback = java.net.InetAddress.getByName(\"127.0.0.1\");\n// 포트 0은 운영체제에 빈 포트 배정을 요청해요.\ntry (var listener = new java.net.ServerSocket(0, 1, loopback)) {\n    listener.setSoTimeout(2000);\n    try (var client = new java.net.Socket()) {\n        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);\n        client.setSoTimeout(2000);\n        try (var server = listener.accept()) {\n            server.setSoTimeout(2000);\n// 실제 연결에 최소 요청을 보내요.\nString request = \"GET /memo/\" + VALUE + \" HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n\";\nclient.getOutputStream().write(request.getBytes(java.nio.charset.StandardCharsets.US_ASCII));\nvar requestReader = new java.io.BufferedReader(new java.io.InputStreamReader(server.getInputStream(), java.nio.charset.StandardCharsets.US_ASCII));\n// 요청 헤더 끝의 빈 줄까지 서버가 읽어요.\nwhile (!requestReader.readLine().isEmpty()) {}\nString replyBody = \"한\" + VALUE;\nbyte[] reply = replyBody.getBytes(java.nio.charset.StandardCharsets.UTF_8);\nString headers = \"HTTP/1.1 200 OK\\r\\nContent-Length: \" + reply.length + \"\\r\\nConnection: close\\r\\n\\r\\n\";\nserver.getOutputStream().write(headers.getBytes(java.nio.charset.StandardCharsets.US_ASCII));\nserver.getOutputStream().write(reply);\nserver.shutdownOutput();\nvar responseReader = new java.io.BufferedReader(new java.io.InputStreamReader(client.getInputStream(), java.nio.charset.StandardCharsets.UTF_8));\nString line;\nwhile (!(line = responseReader.readLine()).isEmpty()) {}\nSystem.out.println(responseReader.readLine());\n        }\n    }\n}\n}\n",
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
- 내용 식별 해시: f1272ace271fbb84616fb1645cba4911b315d1cf167d6199beaaf129250ef6ff
