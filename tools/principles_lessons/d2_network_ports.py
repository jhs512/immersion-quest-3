"""Namespaces, service DNS, bind address, network membership and host ports."""
from docker_common import step, lesson, BUSYBOX
from sql_lab import unit

WEB = f'''services:
  web:
    image: {BUSYBOX}
    command: ["httpd", "-f", "-p", "0.0.0.0:8080", "-h", "/www"]
    volumes:
      - ./www:/www:ro
    healthcheck:
      test: ["CMD", "wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080"]
      interval: 1s
      timeout: 1s
      retries: 20
  client:
    image: {BUSYBOX}
    command: ["wget", "-q", "-T", "3", "-O", "-", "http://localhost:8080"]
'''
SCRIPT = '''set -e
docker compose up -d --wait web >/dev/null 2>&1
if content=$(docker compose run --rm -T client 2>/dev/null); then
  printf '응답:%s\\n' "$content"
else
  echo '응답:연결 실패'
fi
'''
FILES={'www/index.html':'메모 서버'}
FIX1=WEB.replace('http://localhost:8080','http://web:8080')
S1=step(slug='service-name',title='클라이언트가 web 서비스에 연결하게 하세요',
    concept='localhost는 명령을 실행하는 컨테이너 자신을 가리켜요.',
    intro='서버는 web에 있고 요청은 client에서 보내요. client의 localhost에는 서버가 없어요.',
    know='같은 Compose 네트워크의 서비스는 서비스 이름으로 찾아요. web:8080의 8080은 서버 컨테이너 내부 포트예요. 사용자 PC의 8080을 차지하지 않아요.',
    starter=WEB,solution=FIX1,script=SCRIPT,files=FILES,expected='응답:메모 서버',
    first='서버가 건강해도 응답은 연결 실패예요. 요청한 localhost가 client 자신이기 때문이에요.',
    result='web 이름으로 서버 컨테이너를 찾아 메모 서버 응답을 받았어요.',
    caution='조심하세요. client에도 서버를 띄워 결과만 맞추면 서로 다른 컨테이너를 연결하는 목표를 놓쳐요.',
    variants=[dict(files={'www/index.html':'다른 메모'},expected='응답:다른 메모')])

START2=FIX1.replace('"0.0.0.0:8080"','"127.0.0.1:8080"')
S2=step(slug='bind-address',title='서버가 다른 컨테이너의 연결도 받게 하세요',
    concept='이름을 찾는 것과 서버가 어느 인터페이스에서 기다리는지는 별개의 조건이에요.',
    intro='주소는 이제 web이에요. 서버는 자기 안에서 건강하지만 client 요청은 여전히 실패해요.',
    know='서버가 컨테이너의 127.0.0.1에서만 기다리면 다른 컨테이너의 요청을 받지 못해요. 서버 내부의 바인드 주소를 0.0.0.0으로 바꾸세요. 호스트의 모든 주소에 포트를 공개하는 설정과는 달라요.',
    starter=START2,solution=FIX1,script=SCRIPT,files=FILES,expected='응답:메모 서버',
    first='컨테이너 안 건강 검사는 성공해요. 하지만 서버가 루프백에서만 받아 외부 요청이 실패해요.',
    result='컨테이너의 네트워크 인터페이스에서도 요청을 받아 client가 연결됐어요. 호스트 포트는 열지 않았어요.',
    caution='조심하세요. 호스트에 0.0.0.0으로 포트를 공개하라는 뜻은 아니에요. 지금 고치는 것은 컨테이너 내부 서버 주소예요.')

START3=FIX1.replace('    healthcheck:', '    networks: [front]\n    healthcheck:').replace('    command: ["wget"','    networks: [back]\n    command: ["wget"')+'networks:\n  front:\n  back:\n'
FIX3=START3.replace('networks: [back]','networks: [front]')
S3=step(slug='network-membership',title='통신할 두 서비스를 같은 네트워크에 넣으세요',
    concept='서비스 이름으로 통신하려면 통신 가능한 네트워크를 공유해야 해요.',
    intro='이번에는 서버 주소도 맞지만 web과 client를 서로 다른 네트워크로 나눠 두었어요.',
    know='client가 web과 공유하는 front 네트워크에 참여하도록 고치세요. 네트워크를 분리하는 것은 이름만 다르게 붙이는 것이 아니라 통신 경계를 만드는 일이에요.',
    starter=START3,solution=FIX3,script=SCRIPT,files=FILES,expected='응답:메모 서버',
    first='서비스 이름이 맞아도 연결 실패예요. client와 web이 공유하는 네트워크가 없어요.',
    result='같은 front 네트워크에서 web 이름을 찾고 요청을 보냈어요.',
    caution='조심하세요. network_mode: host로 피하지 마세요. 사용자 PC의 네트워크와 분리된 실습 네트워크를 유지해야 해요.')

# Host-port assignment is observed from the real engine. The host request uses
# Bash TCP support so there is no dependency on a learner-installed HTTP client.
HOST_SCRIPT=SCRIPT+'''address=$(docker compose port web 8080 2>/dev/null || true)
host=${address%:*}; port=${address##*:}
if [ "$host" != 127.0.0.1 ] || [ -z "$port" ]; then echo '호스트:미연결'; exit 0; fi
exec 3<>/dev/tcp/127.0.0.1/"$port"
printf 'GET / HTTP/1.0\\r\\nHost: web\\r\\nConnection: close\\r\\n\\r\\n' >&3
body=$(cat <&3 | tr -d '\\r' | sed '1,/^$/d')
exec 3<&-; exec 3>&-
printf '호스트:%s\\n' "$body"
'''
START4=FIX3
FIX4=FIX3.replace('    networks: [front]\n    healthcheck:', '    ports: ["127.0.0.1::8080"]\n    networks: [front]\n    healthcheck:')
S4=step(slug='final-host-port',title='PC에서도 빈 포트로 서버에 연결하게 하세요',
    concept='컨테이너 내부 포트와 호스트 공개 포트는 서로 다른 주소 영역이에요.',
    intro='client에서는 연결돼요. 이번에는 PC의 브라우저에서도 접속할 수 있어야 해요.',
    know='web에 127.0.0.1::8080 포트 연결을 추가하세요. 가운데 호스트 포트를 비워 Docker가 빈 포트를 고르게 해요. 실습 스크립트가 실제 배정 주소를 엔진에 물어보고 PC에서 요청해요.',
    starter=START4,solution=FIX4,script=HOST_SCRIPT,files=FILES,
    expected='응답:메모 서버\n호스트:메모 서버',
    first='client 응답은 오지만 호스트에 공개된 포트는 없어요. 내부 연결만으로 PC의 접속 주소가 생기지는 않아요.',
    result='내부 client는 web:8080으로, PC는 자동 배정된 127.0.0.1 포트로 같은 서버에 연결됐어요.',
    caution='조심하세요. client의 주소를 호스트 포트로 바꾸지 마세요. 컨테이너 간 연결은 내부 포트와 서비스 이름을 그대로 써요.',
    variants=[dict(files={'www/index.html':'새 서버'},expected='응답:새 서버\n호스트:새 서버')])

LESSON=lesson(key='docker-network-ports',folder='docker_network_ports',pilot='넷',
    title='Docker 네트워크 · localhost는 누구인가요',
    objectives=['컨테이너마다 다른 localhost를 이해해요.', '서비스 이름·바인드·네트워크 경계를 구별해요.', 'PC의 빈 포트와 내부 포트를 연결해요.'],
    units=[unit('이름과 기다리는 주소','요청을 보내는 위치와 받는 위치를 구별해요.',[S1,S2]),
           unit('네트워크 경계와 공개 포트','내부 통신과 PC의 접속 경로를 연결해요.',[S3,S4])],final_slug='final-host-port')
