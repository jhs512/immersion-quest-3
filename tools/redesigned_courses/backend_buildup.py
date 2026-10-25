"""Small executable bridges into the eight systems challenges.

Each tuple supplies the actual edit, what to observe, and the modelling boundary.
These are source exercises, not generated paraphrases of the final answer.
"""

MODEL = '아래 코드는 Java 교육용 모형이에요. 실제 장치의 실행 기록은 아니에요.'

# title, question/context, source, edit before/after, output interpretation
STAGES = {
 'sys-sliding-window': [
  ('조각 하나의 확인을 읽어요', '확인 번호는 마지막으로 받은 조각 번호예요. 확인 뒤 다음에 보낼 번호를 구하세요.',
   'int ack = VALUE;\nint next = ack;\nSystem.out.println("다음 조각 " + next);', 'next = ack;', 'next = ack + 1;', '확인한 조각 다음 번호가 출력됐어요. 이미 받은 조각을 다시 새 조각으로 세지 않아요.'),
  ('중복 확인과 늦은 확인을 비교해요', '이미 VALUE번부터 기다리고 있어요. 더 오래된 확인이 오면 창의 앞을 어디에 둘까요?',
   'int base = VALUE;\nint ack = VALUE - 2;\nbase = ack + 1;\nSystem.out.println("창의 앞 " + base);', 'base = ack + 1;', 'base = Math.max(base, ack + 1);', '늦은 확인을 받아도 창의 앞이 뒤로 가지 않아요. 중복 확인도 같은 기준으로 비교해 보세요.'),
  ('창의 안과 밖을 나눠요', '창의 앞은 VALUE예요. 크기 3인 창에서 새로 보낼 수 있는 번호만 세세요.',
   'int base = VALUE;\nint count = 0;\nfor (int next = base; next <= base + 3; next++) count++;\nSystem.out.println("보낼 개수 " + count + ", 마지막 " + (base + count - 1));', 'next <= base + 3', 'next < base + 3', '창 크기만큼의 번호만 포함됐어요. 이제 유실과 확인이 섞인 송신자에서 이 경계를 따라가 보세요.'),
 ],
 'sys-page-table': [
  ('주소를 두 부분으로 나눠요', '한 페이지는 4바이트예요. 주소 VALUE의 페이지 안 위치를 구하세요.',
   'int page = VALUE / 4;\nint offset = VALUE / 4;\nSystem.out.println("페이지 " + page + ", 위치 " + offset);', 'offset = VALUE / 4', 'offset = VALUE % 4', '몫은 페이지 번호이고 나머지는 페이지 안 위치예요. 두 값은 역할이 달라요.'),
  ('페이지를 프레임에 연결해요', '가상 페이지가 물리 프레임 3에 연결돼 있어요. 페이지 안 위치를 유지해 주소를 구하세요.',
   'int frame = 3;\nint offset = VALUE % 4;\nint physical = frame * 4;\nSystem.out.println("물리 주소 " + physical);', 'physical = frame * 4;', 'physical = frame * 4 + offset;', '프레임의 시작에 페이지 안 위치가 더해졌어요. 같은 페이지의 다른 바이트를 구분할 수 있어요.'),
  ('연결 없는 페이지를 구분해요', '표의 1번 페이지만 연결돼 있어요. VALUE가 그 밖을 가리키면 폴트라고 출력하세요.',
   'int[] table = {-1, 3, -1};\nint frame = table[VALUE / 4];\nSystem.out.println(frame == 0 ? "폴트" : "프레임 " + frame);', 'frame == 0', 'frame == -1', '미연결 표시는 프레임 번호와 구분해요. 다음 문제에서는 프로세스마다 다른 표도 함께 다뤄요.'),
 ],
 'sys-buffer-pool': [
  ('이미 적재한 페이지를 찾아요', '버퍼의 한 칸에 VALUE번 페이지가 있어요. 같은 페이지를 다시 읽을 때 적중 여부를 구하세요.',
   'int loaded = VALUE;\nint requested = VALUE;\nboolean hit = loaded != requested;\nSystem.out.println("적중 " + hit + ", 페이지 " + requested);', 'loaded != requested', 'loaded == requested', '요청한 페이지가 이미 들어 있어요. 다음에는 다른 페이지가 들어올 때 빈 공간을 살펴봐요.'),
  ('사용 중인 칸을 후보에서 빼요', '첫 칸은 사용 중이고 둘째 칸은 비어 있지 않지만 사용 중이 아니에요. 교체할 칸을 찾으세요.',
   'boolean[] pinned = {true, false};\nint candidate = -1;\nfor (int i = 0; i < pinned.length; i++) {\n    if (pinned[i]) { candidate = i; break; }\n}\nSystem.out.println("교체 칸 " + candidate + ", 새 페이지 " + VALUE);', 'if (pinned[i])', 'if (!pinned[i])', '사용 중이 아닌 칸을 골랐어요. 오래된 순서만으로 고르면 사용 중인 페이지를 잃을 수 있어요.'),
  ('수정한 페이지를 내보내요', 'VALUE번 페이지를 메모리에서 수정했어요. 내보내기 전에 디스크 쓰기가 필요한지 구하세요.',
   'boolean dirty = true;\nint writes = 0;\nif (!dirty) writes++;\nSystem.out.println("페이지 " + VALUE + ", 디스크 쓰기 " + writes);', 'if (!dirty)', 'if (dirty)', '수정한 페이지를 내보낼 때 쓰기 횟수가 늘었어요. 이 모형은 실제 DB 장애 복구까지 증명하지 않아요.'),
 ],
 'sys-cache-locality': [
  ('주소가 속한 캐시 줄을 구해요', '한 캐시 줄에 값 4개가 들어가요. 주소 VALUE가 속한 줄 번호를 구하세요.',
   'int line = VALUE % 4;\nSystem.out.println("주소 " + VALUE + ", 줄 " + line);', 'line = VALUE % 4', 'line = VALUE / 4', '주소를 줄 단위로 묶었어요. 주소가 달라도 같은 줄에 들어갈 수 있어요.'),
  ('이웃한 주소를 다시 읽어요', 'VALUE와 VALUE+1을 차례로 읽어요. 같은 줄인지 비교하세요.',
   'int first = VALUE / 4;\nint second = (VALUE + 1) / 4;\nboolean hit = first != second;\nSystem.out.println("첫 줄 " + first + ", 둘째 줄 " + second + ", 적중 " + hit);', 'first != second', 'first == second', '두 주소의 줄 번호를 비교했어요. 변형 검사에서는 줄의 끝도 지나가요.'),
  ('행의 이웃한 값을 찾아요', '너비가 4인 행 우선 배열이에요. 같은 행의 바로 다음 열 주소를 구하세요.',
   'int address = VALUE;\nint next = address + 4;\nSystem.out.println("이동 " + address + " -> " + next);', 'next = address + 4', 'next = address + 1', '같은 행에서 다음 열로 한 칸 이동했어요. 다음 문제에서 순회 순서와 미스 수를 함께 비교해요.'),
 ],
 'sys-interpreter-env': [
  ('정의한 이름을 읽어요', '작은 언어가 count라는 이름에 VALUE를 넣었어요. 그 이름을 읽어 출력하세요.',
   'var env = new java.util.HashMap<String, Integer>();\nenv.put("count", VALUE);\nSystem.out.println(env.get("total"));', 'env.get("total")', 'env.get("count")', '정의한 이름으로 값을 찾았어요. 아직 바깥 환경이나 대입은 없어요.'),
  ('안쪽에 없는 이름을 찾아요', '안쪽 환경에는 count가 없고 바깥에는 있어요. 어느 환경을 읽을지 고르세요.',
   'var outer = java.util.Map.of("count", VALUE);\nvar inner = java.util.Map.of("temp", 1);\nint value = inner.getOrDefault("count", 0);\nSystem.out.println("count " + value);', 'inner.getOrDefault("count", 0)', 'inner.getOrDefault("count", outer.get("count"))', '안쪽에 없는 이름은 바깥에서 찾았어요. 안쪽에 같은 이름이 있을 때도 구분해야 해요.'),
  ('대입할 환경을 찾아요', 'count는 바깥에서 정의했어요. 안쪽에서 1을 더한 뒤 바깥 값을 확인하세요.',
   'var outer = new java.util.HashMap<String, Integer>();\nvar inner = new java.util.HashMap<String, Integer>();\nouter.put("count", VALUE);\ninner.put("count", outer.get("count") + 1);\nSystem.out.println("바깥 count " + outer.get("count"));', 'inner.put("count", outer.get("count") + 1)', 'outer.put("count", outer.get("count") + 1)', '바깥의 count가 바뀌었어요. 정의와 대입을 같은 동작으로 처리하면 이 차이가 사라져요.'),
 ],
 'sys-interleavings': [
  ('한 작업의 읽기와 쓰기를 이어 봐요', '조회수가 VALUE예요. 읽은 값에 1을 더한 뒤 저장하세요.',
   'int shared = VALUE;\nint read = shared;\nshared = read;\nSystem.out.println("조회수 " + shared);', 'shared = read;', 'shared = read + 1;', '한 작업의 읽기와 쓰기가 끝났어요. 이제 다른 작업이 사이에 들어오는 상황을 봐요.'),
  ('두 읽기 뒤의 쓰기를 따라가요', '두 작업이 같은 값을 읽었어요. 두 번 써도 마지막 값이 어떻게 되는지 읽기 시점을 바꿔 비교하세요.',
   'int shared = VALUE;\nint a = shared;\nint b = shared;\nshared = a + 1;\nshared = b + 1;\nSystem.out.println("조회수 " + shared);', 'int b = shared;\nshared = a + 1;', 'shared = a + 1;\nint b = shared;', '둘째 작업의 읽기가 첫 쓰기 뒤로 옮겨졌어요. 이 순서에서 맞는 것과 모든 순서에서 맞는 것은 달라요.'),
  ('작업 안의 순서는 지켜요', '네 자리 중 A의 두 자리를 골라요. 먼저 고른 자리는 읽기예요. 나머지는 B의 읽기·쓰기예요. 마지막 자리까지 빠짐없이 세세요.',
   'int schedules = 0;\nfor (int first = 0; first < 4; first++) {\n    for (int second = first + 1; second < 3; second++) schedules++;\n}\nSystem.out.println("시작 조회수 " + VALUE + ", 순서 수 " + schedules);', 'second < 3', 'second < 4', 'A의 읽기보다 쓰기가 앞서지 않는 순서를 모두 셌어요. 다음 문제에서 각 순서의 마지막 값까지 따라가요.'),
 ],
 'socket-partial-frames': [
  ('메시지의 끝을 구분해요', '이 프로토콜은 줄바꿈으로 메시지를 마쳐요. 한 글자만 받았을 때 완성 여부를 판단하세요.',
   'String received = "A" + VALUE;\nboolean complete = !received.isEmpty();\nSystem.out.println("완성 " + complete + ", 받은 값 " + received);', '!received.isEmpty()', 'received.contains("\\n")', '받은 글자가 있어도 줄바꿈이 없어서 완성된 메시지는 아니에요.'),
  ('앞부분과 뒷부분을 이어 붙여요', '처음 받은 앞부분을 보관했어요. 다음 수신 내용을 붙여 메시지를 완성하세요.',
   'String pending = "A";\nString chunk = VALUE + "\\n";\npending = chunk;\nSystem.out.print("메시지 " + pending);', 'pending = chunk;', 'pending += chunk;', '처음 받은 A가 남아 있어요. 수신 호출을 새 메시지의 시작으로 취급하지 않았어요.'),
  ('연결별로 앞부분을 보관해요', 'A는 앞부분만 보냈어요. B가 보낸 자료를 B의 보관함에 넣으세요.',
   'var pending = new java.util.TreeMap<String, String>();\npending.put("A", "A");\npending.put("A", "B" + VALUE + "\\n");\nSystem.out.println("A " + pending.get("A"));\nSystem.out.println("B " + pending.get("B"));', 'pending.put("A", "B" + VALUE', 'pending.put("B", "B" + VALUE', 'A의 앞부분과 B의 메시지를 구분했어요. 다음 문제에서는 실제 소켓에서 보낸 한 줄을 읽어요.'),
  ('실제 연결에서 한 줄을 읽어요', '실제 클라이언트가 한 줄을 보냈어요. 첫 바이트만 읽는 부분을 한 줄을 읽도록 고치세요.',
   'try (var server = new java.net.ServerSocket(0, 1, java.net.InetAddress.getByName("127.0.0.1"))) {\n    try (var client = new java.net.Socket("127.0.0.1", server.getLocalPort())) {\n        client.getOutputStream().write(("A" + VALUE + "\\n").getBytes(java.nio.charset.StandardCharsets.UTF_8));\n        try (var peer = server.accept()) {\n            String message = Integer.toString(peer.getInputStream().read());\n            System.out.println("받은 메시지 " + message);\n        }\n    }\n} catch (Exception error) { throw new RuntimeException(error); }', 'Integer.toString(peer.getInputStream().read())', 'new java.io.BufferedReader(new java.io.InputStreamReader(peer.getInputStream(), java.nio.charset.StandardCharsets.UTF_8)).readLine()', '한 바이트의 수 대신 보낸 한 줄을 읽었어요. 이 클라이언트는 이미 줄 전체를 보냈어요. 다음 도전에서 앞부분만 보낸 연결을 추가해요.'),
 ],
 'node-cpu-offload': [
  ('예약한 콜백의 실행 순서를 봐요', 'ping을 바로 부르는 대신 다음 차례에 실행하게 예약하세요. 동기 코드와 예약된 코드의 순서를 비교해요.',
   'const events = [];\nfunction ping() { events.push("ping"); }\nping();\nevents.push("계산 " + VALUE);\nsetImmediate(() => console.log(events.join(" -> ")));', 'ping();', 'setImmediate(ping);', '동기 코드의 계산 기록 뒤에 콜백의 ping이 나왔어요. 예약한 위치와 실행된 위치를 구분해요.'),
  ('await 앞뒤의 실행을 비교해요', 'Promise를 만든 것과 기다린 것을 비교해요. 기다린 뒤의 계산 기록은 ping 다음에 남아야 해요.',
   'const events = [];\nasync function heavy() {\n    Promise.resolve();\n    events.push("계산 " + VALUE);\n}\nheavy();\nevents.push("ping");\nsetImmediate(() => console.log(events.join(" -> ")));', 'Promise.resolve();', 'await Promise.resolve();', 'await 뒤의 기록이 ping 다음으로 옮겨졌어요. 기다린 다음 계산도 같은 스레드예요. worker를 만든 것은 아니에요.'),
  ('계산 중에 예약된 일을 관찰해요', 'ping 콜백을 먼저 예약해요. 반복 계산을 끝낸 뒤 합계를 출력하도록 반복 범위를 고치세요.',
   'setImmediate(() => console.log("ping"));\nlet sum = 0;\nfor (let n = 1; n < VALUE; n++) sum += n;\nconsole.log("합계 " + sum);', 'n < VALUE', 'n <= VALUE', '콜백을 먼저 예약했지만 합계가 먼저 출력됐어요. 다음 문제에서 실제 worker로 실행 위치를 나눠 봐요.'),
  ('worker에서 결과를 받아요', '별도 스레드가 VALUE의 두 배를 보내요. 종료 코드 대신 계산 결과 메시지를 받도록 고치세요.',
   'const {Worker} = require("node:worker_threads");\nconst source = `require("node:worker_threads").parentPort.postMessage(${VALUE} * 2);`;\nconst worker = new Worker(source, {eval:true});\nworker.on("exit", value => console.log("계산 결과 " + value));', 'worker.on("exit"', 'worker.on("message"', '종료 코드가 아니라 별도 스레드가 보낸 계산 결과를 받았어요. 마지막 도전에서는 정해진 수의 worker를 돌려 써요.'),
 ],
}
