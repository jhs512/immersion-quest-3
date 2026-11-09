"""Hand-authored networking lessons, with actual local sockets and explicit models."""

# title, problem, prepared body, mistaken expression, valid expression, explanation
LESSONS = [
('network-bytes', '네트워크 · 글자를 바이트로 보내기', '글자와 바이트를 구별하고 같은 문자 인코딩으로 복원해요.', '모형: 메모리 안의 바이트 변환이에요. 아직 네트워크를 열지 않아요.', [
('보낼 바이트 수를 구하세요', 'UTF-8은 글자를 바이트로 바꾸는 규칙이에요. 한글이 든 메모의 바이트 수를 구하세요.',
 'String memo = "한" + VALUE;\nbyte[] wire = memo.getBytes(java.nio.charset.StandardCharsets.UTF_8);\nSystem.out.println(memo.length());', 'memo.length()', 'wire.length', '글자 수와 UTF-8 바이트 수는 서로 달라요. 전송할 크기는 바이트 배열로 확인해요.'),
('같은 규칙으로 글자를 복원하세요', '보낼 때 UTF-8을 썼어요. 받은 바이트를 같은 규칙으로 복원하세요.',
 'byte[] wire = ("한" + VALUE).getBytes(java.nio.charset.StandardCharsets.UTF_8);\nSystem.out.println(new String(wire, java.nio.charset.StandardCharsets.US_ASCII));', 'StandardCharsets.US_ASCII', 'StandardCharsets.UTF_8', '송신과 수신이 같은 문자 인코딩을 사용해야 원래 글자로 돌아와요.'),
('바이트를 양수 범위로 읽으세요', '자바 byte는 부호가 있어요. 한 옥텟을 0~255의 값으로 출력하세요. &는 같은 자리의 비트를 비교해요.',
 'byte octet = (byte) (200 + VALUE);\nSystem.out.println((int) octet);', '(int) octet', 'octet & 0xff', '0xff와 비트 AND를 하면 하위 8비트를 0~255 범위로 읽어요.'),
('바이트 일부만 복원하세요', '수신 버퍼에는 메모 뒤에 빈칸이 남아요. 실제 받은 바이트 수만 복원하세요.',
 'byte[] memo = ("한" + VALUE).getBytes(java.nio.charset.StandardCharsets.UTF_8);\nbyte[] buffer = java.util.Arrays.copyOf(memo, 32);\nSystem.out.println(new String(buffer, 0, buffer.length, java.nio.charset.StandardCharsets.UTF_8));', '0, buffer.length,', '0, memo.length,', '버퍼 전체 크기와 실제 데이터 길이는 달라요. 받은 길이만큼만 글자로 바꿔요.'),
]),
('network-endpoints', '네트워크 · 주소와 포트로 연결하기', '서버의 대기 주소와 포트, 연결의 양 끝을 실제 소켓으로 확인해요.', '실제 실습: 같은 컴퓨터의 127.0.0.1에 TCP 소켓을 열어요. 포트는 운영체제가 배정해요.', [
('연결한 서버 포트를 확인하세요', 'IP 주소는 연결할 장치를 가리켜요. 포트는 그 장치의 통신 끝점을 구별해요. 클라이언트의 상대 포트와 서버 대기 포트를 비교하세요.',
 'System.out.println(client.getLocalPort() == listener.getLocalPort());', 'client.getLocalPort()', 'client.getPort()', '클라이언트의 상대 포트가 서버의 대기 포트와 같아요. 자기 포트와 비교하면 다른 대상을 보게 돼요.'),
('서버가 보는 상대 포트를 확인하세요', '연결은 양 끝을 가져요. 서버가 받은 연결의 상대 포트를 클라이언트 자기 포트와 비교하세요.',
 'System.out.println(server.getLocalPort() == client.getLocalPort());', 'server.getLocalPort()', 'server.getPort()', '서버에서 보는 상대 포트는 클라이언트의 자기 포트예요.'),
('클라이언트가 보낸 바이트를 읽으세요', '연결 준비와 데이터 수신은 달라요. 클라이언트가 보낸 VALUE 한 바이트를 서버에서 읽으세요.',
 'client.getOutputStream().write(VALUE);\nSystem.out.println(VALUE + 1);', 'VALUE + 1', 'server.getInputStream().read()', '이번 값은 계산으로 만든 값이 아니라 실제 서버 소켓에서 읽은 한 바이트예요.'),
('서버의 응답을 클라이언트에서 읽으세요', '요청을 받은 서버가 VALUE+1을 응답해요. 클라이언트의 수신 쪽에서 읽으세요.',
 'client.getOutputStream().write(VALUE);\nint request = server.getInputStream().read();\nserver.getOutputStream().write(request + 1);\nSystem.out.println(request);', 'System.out.println(request)', 'System.out.println(client.getInputStream().read())', '요청을 읽은 값과 응답을 읽은 값이 구별돼요. 응답도 반대쪽 소켓을 통해 와요.'),
]),
('network-ip', '네트워크 · IPv4 주소와 같은 네트워크', 'IPv4 주소를 비트로 읽고 네트워크 부분을 비교해요.', '모형: 문서용 192.0.2.0/24 주소로 계산해요. 실제 장치의 주소나 경로를 바꾸지 않아요.', [
('IPv4 주소의 바이트 수를 읽으세요', 'IPv4 주소는 32비트예요. 8비트씩 묶은 옥텟이 몇 개인지 주소 배열로 확인하세요.',
 'byte[] ip = java.net.InetAddress.getByName("192.0.2." + VALUE).getAddress();\nSystem.out.println(ip.length * 8);', 'ip.length * 8', 'ip.length', '32비트 주소는 8비트 옥텟 4개로 읽어요. 출력은 비트 수가 아니라 배열의 바이트 수예요.'),
('마스크로 네트워크 부분을 남기세요', '/24는 앞 24비트가 네트워크 부분이에요. 비트 AND로 호스트 부분을 지우세요.',
 'int ip = 0xc0000200 | VALUE;\nint mask = 0xffffff00;\nSystem.out.println(Integer.toHexString(ip | mask));', 'ip | mask', 'ip & mask', '마스크가 1인 앞부분만 남아요. 마지막 옥텟의 호스트 비트는 0이 돼요.'),
('같은 네트워크인지 비교하세요', '두 주소는 마지막 옥텟만 달라요. /24 마스크를 적용한 네트워크 부분끼리 비교하세요.',
 'int first = 0xc0000200 | VALUE;\nint second = 0xc0000200 | (VALUE + 1);\nint mask = 0xffffff00;\nSystem.out.println(first == second);', 'first == second', '(first & mask) == (second & mask)', '장치 주소가 달라도 네트워크 부분은 같을 수 있어요. 전체 주소 비교로는 이 관계를 판단할 수 없어요.'),
('주소 블록의 시작을 구하세요', '/29는 끝의 3비트가 호스트 부분이에요. 마지막 옥텟 VALUE가 든 블록의 시작을 구하세요.',
 'int last = VALUE;\nint mask = 0b11111000;\nSystem.out.println(last | mask);', 'last | mask', 'last & mask', '끝 3비트를 지우면 8개씩 묶인 주소 블록의 시작이 나와요. 이 단계는 사용 가능한 장치 수를 세지 않아요.'),
]),
('network-routing', '네트워크 · 직접 전달과 라우터', '같은 네트워크와 다음 홉을 구별하고 더 구체적인 경로를 선택해요.', '모형: 정적 경로표로 판단해요. 실제 패킷·ARP·운영체제 경로를 관찰하는 실험은 아니에요.', [
('직접 전달할 주소를 판별하세요', '내 주소와 목적지의 /24 네트워크 부분이 같으면 직접 전달하는 모형이에요. 같은 네트워크 여부를 계산하세요.',
 'int mine = 0xc0000200 | VALUE;\nint target = 0xc0000200 | (VALUE + 1);\nSystem.out.println(mine == target);', 'mine == target', '(mine & 0xffffff00) == (target & 0xffffff00)', '이 모형에서는 네트워크 부분이 같으면 다음 라우터를 거치지 않고 목적지로 보내요.'),
('다른 네트워크는 다음 홉으로 보내세요', '목적지는 198.51.100.VALUE예요. 다른 네트워크로 나갈 때 전달할 다음 홉을 출력하세요.',
 'String target = "198.51.100." + VALUE;\nString gateway = "192.0.2.1";\nSystem.out.println(target);', 'System.out.println(target)', 'System.out.println(gateway)', '최종 목적지 주소와 바로 다음에 전달할 라우터 주소는 달라요. 목적지 자체를 바꾸는 뜻은 아니에요.'),
('더 구체적인 경로를 선택하세요', '목적지에 /24와 /29 경로가 모두 맞아요. 프리픽스가 긴 경로를 선택하세요.',
 'int[] prefixes = {24, 29};\nint best = -1;\nfor (int p : prefixes) if (p < best) best = p;\nSystem.out.println(best + ":" + VALUE);', 'p < best', 'p > best', '둘 다 맞는 경로 중 /29가 더 구체적이에요. 경로를 먼저 골라야 그 경로의 다음 홉을 쓸 수 있어요.'),
('홉을 지날 때 TTL을 줄이세요', 'TTL은 패킷이 계속 순환하지 않게 하는 값이에요. 라우터 하나를 지난 뒤의 TTL을 출력하세요.',
 'int ttl = VALUE;\nint forwarded = ttl;\nSystem.out.println(forwarded);', 'forwarded = ttl', 'forwarded = ttl - 1', '전달할 때 TTL을 줄여요. 이 모형은 감소만 확인하고 실제 라우터의 폐기·오류 응답은 만들지 않아요.'),
]),
('network-dns', '네트워크 · 이름을 주소로 바꾸기', '이름 조회·캐시와 실제 연결 성공을 구별해요.', '이름 표와 캐시는 교육용 모형이에요. 마지막 단계만 시스템의 localhost 이름 해석을 실제 호출해요. 외부 DNS 패킷은 보내지 않아요.', [
('요청한 이름의 주소를 조회하세요', '이름은 주소를 찾을 때 쓰는 키예요. 준비된 이름 표에서 memo.test에 대응하는 값을 출력하세요.',
 'var records = java.util.Map.of("memo.test", "192.0.2." + VALUE);\nString name = "memo.test";\nSystem.out.println(name);', 'System.out.println(name)', 'System.out.println(records.get(name))', '이름 문자열과 그 이름에 대응하는 주소가 나뉘었어요. 이 표는 실제 DNS 서버가 아니에요.'),
('없는 이름을 구별하세요', '이름 표에 없는 요청도 들어와요. missing.test의 조회 결과가 없는지 검사하세요.',
 'var records = java.util.Map.of("memo.test", "192.0.2." + VALUE);\nString found = records.get("missing.test");\nSystem.out.println(found != null);', 'found != null', 'found == null', '이 모형에서 null은 이름 표에 값이 없다는 뜻이에요. DNS 서버의 장애를 재현한 것은 아니에요.'),
('만료된 캐시를 사용하지 마세요', '캐시를 받은 시각은 0초이고 TTL은 VALUE초예요. 현재 시각은 만료 시각과 같아요. 아직 쓸 수 있는지 계산하세요.',
 'int ttl = VALUE;\nint now = VALUE;\nSystem.out.println(now <= ttl);', 'now <= ttl', 'now < ttl', '현재 시각이 만료 시각에 닿으면 캐시를 다시 써서는 안 돼요. 실제 캐시 시간을 기다리지 않고 경계를 계산했어요.'),
('시스템에서 localhost를 해석하세요', 'localhost는 자기 컴퓨터를 가리키는 이름이에요. 시스템이 해석한 주소가 루프백 주소인지 확인하세요.',
 'var address = java.net.InetAddress.getByName("localhost");\nSystem.out.println(address.isAnyLocalAddress() + ":" + VALUE);', 'address.isAnyLocalAddress()', 'address.isLoopbackAddress()', '실제 시스템 이름 해석 결과가 루프백 주소예요. 이 호출만으로 외부 DNS 조회나 서버 접속 성공을 증명하지는 못해요.'),
]),
('network-tcp', '네트워크 · TCP 바이트 흐름과 메시지 경계', '실제 TCP 수신과 애플리케이션의 메시지 구분 규칙을 분리해요.', '실제 루프백 TCP예요. 읽기 크기를 직접 정해 비교해요. 운영체제가 패킷을 같은 크기로 나눴다는 뜻은 아니에요.', [
('읽지 않은 나머지도 받으세요', '서버에는 A숫자와 B숫자 두 줄이 와요. 처음 2바이트를 읽은 뒤 나머지 바이트 수도 구하세요.',
 'byte[] first = server.getInputStream().readNBytes(2);\nbyte[] rest = server.getInputStream().readAllBytes();\nSystem.out.println(first.length);', 'System.out.println(first.length)', 'System.out.println(rest.length)', '한 번 읽은 뒤에도 바이트가 남아 있어요. readNBytes의 크기는 이번에 요청한 읽기 크기예요.'),
('보내기 횟수 대신 메시지 끝을 찾으세요', '프로토콜은 줄바꿈으로 메시지를 나눠요. 모두 받은 글에서 완성된 메시지 수를 구하세요.',
 'String text = new String(server.getInputStream().readAllBytes(), java.nio.charset.StandardCharsets.UTF_8);\nSystem.out.println(text.length());', 'text.length()', 'text.split("\\n").length', 'TCP는 바이트 흐름을 보내요. 이 프로그램의 메시지 경계는 줄바꿈 규칙으로 찾았어요.'),
('문자 대신 바이트 길이로 읽으세요', 'TCP로 한글 메모를 보냈어요. 서버가 실제로 받은 바이트 배열의 길이를 출력하세요.',
 'byte[] bytes = server.getInputStream().readAllBytes();\nString text = new String(bytes, java.nio.charset.StandardCharsets.UTF_8);\nSystem.out.println(text.length());', 'text.length()', 'bytes.length', '수신 길이는 바이트 단위예요. 글자 수를 읽기 크기로 쓰면 한글 메모를 중간에서 자를 수 있어요.'),
('송신 종료 뒤 EOF를 확인하세요', '클라이언트는 쓰기를 끝냈어요. 서버가 모든 바이트를 읽은 뒤 다음 read의 결과를 출력하세요.',
 'byte[] all = server.getInputStream().readAllBytes();\nSystem.out.println(all.length);', 'System.out.println(all.length)', 'System.out.println(server.getInputStream().read())', '입력 끝에서는 read가 -1을 돌려줘요. 받은 값 0과 입력의 끝은 서로 달라요.'),
]),
('network-udp', '네트워크 · UDP 데이터그램을 주고받기', '실제 데이터그램의 길이·송신 주소·수신 버퍼의 한계를 확인해요.', '실제 루프백 UDP예요. 제한 시간 안에 받은 데이터그램만 관찰해요. 이 성공이 인터넷에서의 전달·순서를 보장하지 않아요.', [
('받은 데이터그램 길이를 읽으세요', '수신 버퍼에는 여유가 있어요. 실제로 받은 데이터그램의 바이트 수를 출력하세요.',
 'System.out.println(packet.getData().length);', 'packet.getData().length', 'packet.getLength()', '실제 데이터 길이는 패킷의 getLength로 읽어요. 버퍼 크기는 받을 수 있는 공간이에요.'),
('송신자 포트로 응답 대상을 확인하세요', '응답할 대상은 받은 패킷의 송신자예요. 그 포트가 보낸 소켓의 포트와 같은지 비교하세요.',
 'System.out.println(receiver.getLocalPort() == sender.getLocalPort());', 'receiver.getLocalPort() == sender.getLocalPort()', 'packet.getPort() == sender.getLocalPort()', '패킷에 담긴 송신자 포트가 보낸 소켓의 포트와 같아요. 수신자의 자기 포트와 혼동하지 않아요.'),
('작은 버퍼에서 잘린 길이를 확인하세요', '이번 수신 버퍼는 1바이트뿐이에요. 긴 데이터그램을 받은 뒤 보존된 길이를 출력하세요.',
 'System.out.println(payload.length);', 'System.out.println(payload.length)', 'System.out.println(packet.getLength())', '작은 버퍼에 들어간 부분만 남았어요. 남은 부분을 다음 데이터그램처럼 이어 읽을 수는 없어요.'),
('중복 처리는 애플리케이션에서 하세요', '번호가 같은 두 이벤트가 들어왔어요. 아래는 중복 수신을 주입한 모형이에요. 고유 번호의 개수를 출력하세요.',
 'int[] ids = {VALUE, VALUE};\nvar seen = new java.util.HashSet<Integer>();\nfor (int id : ids) seen.add(id);\nSystem.out.println(ids.length);', 'ids.length', 'seen.size()', '중복 번호를 한 번만 세었어요. 이 모형은 UDP가 실제로 중복을 만들었다는 증거가 아니에요.'),
]),
('network-http', '네트워크 · HTTP 요청과 응답 읽기', 'HTTP/1.1의 요청·상태·본문을 실제 로컬 연결에서 구별해요.', '실제 루프백 TCP 위의 최소 HTTP/1.1 예제예요. HTTPS·HTTP/2·쿠키·프레임워크는 아직 다루지 않아요.', [
('요청 경로를 읽으세요', '클라이언트가 보낸 첫 줄은 메서드·요청 대상·버전으로 나뉘어요. 서버가 받은 요청에서 경로를 출력하세요.',
 'String line = requestReader.readLine();\nSystem.out.println(line.split(" ")[0]);', 'split(" ")[0]', 'split(" ")[1]', '첫 단어는 GET 메서드이고 둘째 단어가 요청 대상이에요. 서버가 실제로 받은 첫 줄에서 읽었어요.'),
('응답 상태 코드를 읽으세요', '응답 첫 줄은 버전·상태 코드·이유 구절이에요. 클라이언트가 받은 상태 코드를 출력하세요.',
 'String status = responseReader.readLine();\nSystem.out.println(status.split(" ")[0]);', 'split(" ")[0]', 'split(" ")[1]', 'HTTP 버전과 상태 코드를 구분했어요. 소켓 연결만 성공한 것과 요청 처리가 성공한 것은 달라요.'),
('본문 크기는 UTF-8 바이트로 구하세요', 'Content-Length는 본문의 바이트 수예요. 한글 응답 본문에 넣을 길이를 계산하세요.',
 'String body = "한" + VALUE;\nSystem.out.println(body.length());', 'body.length()', 'body.getBytes(java.nio.charset.StandardCharsets.UTF_8).length', '한글 본문은 글자 수와 바이트 수가 달라요. HTTP/1.1의 Content-Length에는 바이트 수를 써요.'),
('응답 본문만 읽으세요', '상태 줄과 헤더는 본문이 아니에요. 빈 줄까지 헤더를 읽은 뒤 본문 첫 줄을 출력하세요.',
 'String line;\nwhile (!(line = responseReader.readLine()).isEmpty()) {}\nSystem.out.println("응답 없음");', 'System.out.println("응답 없음")', 'System.out.println(responseReader.readLine())', '헤더 끝의 빈 줄 뒤에서 본문을 읽었어요. 실제 응답은 Content-Length만큼의 바이트로 끝을 판단해야 해요.'),
]),
]

TCP_START = '''var loopback = java.net.InetAddress.getByName("127.0.0.1");
// 포트 0은 운영체제에 빈 포트 배정을 요청해요.
try (var listener = new java.net.ServerSocket(0, 1, loopback)) {
    listener.setSoTimeout(2000);
    try (var client = new java.net.Socket()) {
        client.connect(new java.net.InetSocketAddress(loopback, listener.getLocalPort()), 2000);
        client.setSoTimeout(2000);
        try (var server = listener.accept()) {
            server.setSoTimeout(2000);
'''
TCP_END = '\n        }\n    }\n}'

CAUTIONS = {
 'network-bytes': '조심하세요. 버퍼 끝까지 복원하면 받지 않은 빈 바이트도 메모에 들어가요.',
 'network-endpoints': '조심하세요. 요청 변수만 출력하면 응답을 받았는지 확인할 수 없어요.',
 'network-ip': '조심하세요. 비트 OR로 묶으면 호스트 부분을 지우지 못해요.',
 'network-routing': '조심하세요. TTL을 그대로 전달하면 순환 경로를 제한하는 값이 줄지 않아요.',
 'network-dns': '조심하세요. localhost를 해석했다고 외부 DNS와 서버까지 정상이라고 판단하지 마세요.',
 'network-tcp': '조심하세요. read의 -1은 받은 데이터가 아니라 입력 끝을 알리는 값이에요.',
 'network-udp': '조심하세요. 중복을 지운 모형 결과로 실제 UDP가 순서를 보장한다고 판단하지 마세요.',
 'network-http': '조심하세요. 첫 응답 줄을 본문으로 쓰면 HTTP 상태 줄을 데이터로 처리하게 돼요.',
}


def body_for(key, index, body):
    if key == 'network-endpoints':
        return TCP_START + body + TCP_END
    if key == 'network-tcp':
        payload = '"한" + VALUE' if index == 2 else '"A" + VALUE + "\\nB" + VALUE + "\\n"'
        return TCP_START + f'''// 이번 프로토콜의 전송 바이트를 준비해요.
byte[] payload = ({payload}).getBytes(java.nio.charset.StandardCharsets.UTF_8);
client.getOutputStream().write(payload);
// readAllBytes가 끝나도록 송신 방향만 닫아요.
client.shutdownOutput();
''' + body + TCP_END
    if key == 'network-udp' and index != 3:
        capacity = 1 if index == 2 else 64
        return f'''var loopback = java.net.InetAddress.getByName("127.0.0.1");
// 두 소켓은 각자 빈 로컬 포트를 배정받아요.
try (var receiver = new java.net.DatagramSocket(0, loopback);
     var sender = new java.net.DatagramSocket(0, loopback)) {{
    receiver.setSoTimeout(2000);
    byte[] payload = ("한" + VALUE).getBytes(java.nio.charset.StandardCharsets.UTF_8);
    sender.send(new java.net.DatagramPacket(payload, payload.length, loopback, receiver.getLocalPort()));
    // 버퍼 크기를 확인하고 실제 수신 길이와 비교해요.
    var packet = new java.net.DatagramPacket(new byte[{capacity}], {capacity});
    receiver.receive(packet);
{body}
}}'''
    if key == 'network-http' and index in (0, 1, 3):
        setup = '''// 실제 연결에 최소 요청을 보내요.
String request = "GET /memo/" + VALUE + " HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n";
client.getOutputStream().write(request.getBytes(java.nio.charset.StandardCharsets.US_ASCII));
var requestReader = new java.io.BufferedReader(new java.io.InputStreamReader(server.getInputStream(), java.nio.charset.StandardCharsets.US_ASCII));
'''
        if index != 0:
            setup += '''// 요청 헤더 끝의 빈 줄까지 서버가 읽어요.
while (!requestReader.readLine().isEmpty()) {}
String replyBody = "한" + VALUE;
byte[] reply = replyBody.getBytes(java.nio.charset.StandardCharsets.UTF_8);
String headers = "HTTP/1.1 200 OK\\r\\nContent-Length: " + reply.length + "\\r\\nConnection: close\\r\\n\\r\\n";
server.getOutputStream().write(headers.getBytes(java.nio.charset.StandardCharsets.US_ASCII));
server.getOutputStream().write(reply);
server.shutdownOutput();
var responseReader = new java.io.BufferedReader(new java.io.InputStreamReader(client.getInputStream(), java.nio.charset.StandardCharsets.UTF_8));
'''
        return TCP_START + setup + body + TCP_END
    return body


def source(key, index, body):
    return '// 변형 검사에서는 이 준비 값만 달라져요.\nstatic final int VALUE = 6;\n\nvoid main() throws Exception {\n' + body_for(key, index, body) + '\n}\n'
