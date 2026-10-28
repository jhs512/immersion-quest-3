"""Namespaces, service DNS, bind address, network membership and host ports — typed in the real terminal.

The learner edits compose.yaml in the editor and types docker compose commands. Whether client
reached web is the real exit status of `docker compose run --rm client` (wget fails on no answer);
grading also reads the Compose configuration and the running web container (compose_terminal.py).
"""
from compose_terminal import TERMINAL, bash, compose_step, config, http, patch, running, type_command
from docker_common import BUSYBOX, FOLDER, lesson, unit

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
FILES = {'www/index.html': '메모 서버'}
UP = 'docker compose up -d --wait web'
CLIENT = 'docker compose run --rm client'


def ask(observe):
    return [type_command(UP, '웹 서버를 실행하고 건강해질 때까지 기다려요.'), type_command(CLIENT, observe)]


FIX1 = ('http://localhost:8080', 'http://web:8080')
START1 = WEB
SOLUTION1 = WEB.replace(*FIX1)
S1 = compose_step(
    slug='service-name', title='클라이언트가 web 서비스에 연결하게 하세요',
    objectives=['localhost는 명령을 실행하는 컨테이너 자신을 가리켜요.'],
    start='편집기에는 compose.yaml이 있고 터미널 폴더에는 www/index.html(메모 서버)이 있어요. ' + FOLDER + ' 아직 이 문제의 컨테이너는 없어요.',
    intro=['서버는 web에 있고 요청은 client에서 보내요. client의 localhost에는 서버가 없어요.'],
    know='같은 Compose 네트워크의 서비스는 서비스 이름으로 찾아요. web:8080의 8080은 서버 컨테이너 내부 포트예요. 사용자 PC의 8080을 차지하지 않아요. `docker compose run --rm client`는 client를 한 번 실행하고 끝나면 지워요. 응답을 못 받으면 wget이 실패해요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': START1, **FILES}, solution_files={'compose.yaml': SOLUTION1},
    commands=[UP, CLIENT],
    todo=ask('client의 요청 결과를 읽으세요.') + ['편집기의 compose.yaml에서 client가 요청하는 주소를 web 서비스로 고치세요.'] + ask('이번 응답을 읽으세요.'),
    checks=[running('web'), config('client가 web:8080에 요청', {'services': {'client': {'command': ['http://web:8080']}}})],
    success='지금 compose.yaml의 client가 web:8080에 요청했고, 터미널의 client 실행이 성공했어요.',
    complexity=dict(prior='Compose로 서비스 하나를 실행했어요.', new='localhost는 명령을 실행하는 컨테이너 자신을 가리켜요.',
                    changed='client의 요청 주소', evidence='터미널의 client 실행 결과', lines=1, services=0),
    narration=[
        ('say', '요청을 보내는 쪽은 client예요. 지금 주소 그대로 실행해 볼게요.', 'text:서버는 web에 있고 요청은 client에서 보내요.'),
        bash(UP, '먼저 web 서버를 실행하고 건강해질 때까지 기다려요.', wait=300),
        ('say', 'Healthy가 나왔어요. 서버는 자기 안에서 응답하고 있어요.', TERMINAL),
        bash(CLIENT, 'client에서 요청을 보내 볼게요.', fails=True),
        ('say', '연결할 수 없다는 오류예요. client가 자기 localhost에 요청했어요.', TERMINAL),
        ('say', 'localhost는 명령을 실행하는 컨테이너 자신을 가리켜요. client 안에는 서버가 없어요.', 'code:http://localhost:8080'),
        patch('compose.yaml', *FIX1, '요청 주소를 서비스 이름 web으로 바꿔요.'),
        bash(UP, '고친 파일로 다시 실행해요.'),
        ('say', 'web은 그대로 건강해요. 바뀐 것은 client의 설정이에요.', TERMINAL),
        bash(CLIENT, '다시 요청을 보내요.'),
        ('say', '메모 서버 응답이 나왔어요. web 이름으로 서버 컨테이너를 찾았어요.', TERMINAL),
        ('say', '조심하세요. client에도 서버를 띄워 결과만 맞추면 서로 다른 컨테이너를 연결하는 목표를 놓쳐요.', 'text:같은 Compose 네트워크의 서비스는 서비스 이름으로 찾아요.')],
    review={'조심하세요. client에도 서버를 띄워 결과만 맞추면 서로 다른 컨테이너를 연결하는 목표를 놓쳐요.':
            '채점은 client의 요청 주소가 web:8080인지 설정으로 확인해요. 출력만 맞추는 우회가 왜 목표와 다른지 짚어요.'},
    rejects=[([('http://web:8080', 'http://127.0.0.1:8080')], '127.0.0.1도 client 자신이라 연결되지 않아요.')])

START2 = SOLUTION1.replace('"0.0.0.0:8080"', '"127.0.0.1:8080"')
FIX2 = ('"127.0.0.1:8080"', '"0.0.0.0:8080"')
S2 = compose_step(
    slug='bind-address', title='서버가 다른 컨테이너의 연결도 받게 하세요',
    objectives=['이름을 찾는 것과 서버가 어느 인터페이스에서 기다리는지는 별개의 조건이에요.'],
    start='새 compose.yaml로 시작해요. client의 주소는 이미 web이에요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['주소는 이제 web이에요. 서버는 자기 안에서 건강하지만 client 요청은 여전히 실패해요.'],
    know='서버가 컨테이너의 127.0.0.1에서만 기다리면 다른 컨테이너의 요청을 받지 못해요. 서버 내부의 바인드 주소를 0.0.0.0으로 바꾸세요. 호스트의 모든 주소에 포트를 공개하는 설정과는 달라요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': START2, **FILES}, solution_files={'compose.yaml': SOLUTION1},
    commands=[UP, CLIENT],
    todo=ask('client의 요청 결과를 읽으세요.') + ['편집기의 compose.yaml에서 web 서버가 기다리는 주소를 다른 컨테이너의 요청도 받는 주소로 고치세요.'] + ask('이번 응답을 읽으세요.'),
    checks=[running('web'), config('web 서버가 0.0.0.0:8080에서 기다림', {'services': {'web': {'command': ['0.0.0.0:8080']}}})],
    success='지금 compose.yaml로 만든 web이 0.0.0.0:8080에서 기다리고, 터미널의 client 실행이 성공했어요.',
    complexity=dict(prior='서비스 이름으로 다른 컨테이너를 찾았어요.', new='이름을 찾는 것과 서버가 어느 인터페이스에서 기다리는지는 별개의 조건이에요.',
                    changed='web 서버의 바인드 주소', evidence='터미널의 client 실행 결과와 web의 건강 상태', lines=1, services=0),
    narration=[
        ('say', 'client 주소는 이제 web이에요. 이 상태로 먼저 실행해 볼게요.', 'text:서버는 자기 안에서 건강하지만 client 요청은 여전히 실패해요.'),
        bash(UP, 'web을 실행하고 건강해질 때까지 기다려요.', wait=300),
        ('say', 'Healthy예요. 컨테이너 안의 건강 검사는 성공해요.', TERMINAL),
        bash(CLIENT, 'client에서 요청해 볼게요.', fails=True),
        ('say', '이번에도 연결이 거절돼요. 이름은 찾았지만 받아 주는 곳이 없어요.', TERMINAL),
        ('say', '서버가 127.0.0.1에서만 기다려요. 자기 안에서 온 요청만 받아요.', 'code:"127.0.0.1:8080"'),
        patch('compose.yaml', *FIX2, '서버 내부의 바인드 주소를 0.0.0.0으로 바꿔요.'),
        bash(UP, '고친 파일로 web을 다시 만들어요.'),
        ('say', 'web 컨테이너를 새로 만들고 다시 Healthy가 됐어요.', TERMINAL),
        bash(CLIENT, '다시 요청해요.'),
        ('say', '메모 서버 응답이 왔어요. 다른 컨테이너의 요청도 받아요.', TERMINAL),
        ('say', '조심하세요. 호스트에 0.0.0.0으로 포트를 공개하라는 뜻은 아니에요. 지금 고치는 것은 컨테이너 내부 서버 주소예요.', 'text:호스트의 모든 주소에 포트를 공개하는 설정과는 달라요.')],
    review={'조심하세요. 호스트에 0.0.0.0으로 포트를 공개하라는 뜻은 아니에요. 지금 고치는 것은 컨테이너 내부 서버 주소예요.':
            '같은 0.0.0.0이라는 글자 때문에 포트 공개와 혼동하기 쉬워요. 이 실습은 호스트 포트를 열지 않아요.'})

START3 = SOLUTION1.replace('    healthcheck:', '    networks: [front]\n    healthcheck:').replace('    command: ["wget"', '    networks: [back]\n    command: ["wget"') + 'networks:\n  front:\n  back:\n'
FIX3 = ('networks: [back]', 'networks: [front]')
SOLUTION3 = START3.replace(*FIX3)
S3 = compose_step(
    slug='network-membership', title='통신할 두 서비스를 같은 네트워크에 넣으세요',
    objectives=['서비스 이름으로 통신하려면 통신 가능한 네트워크를 공유해야 해요.'],
    start='새 compose.yaml로 시작해요. web은 front, client는 back 네트워크에 있어요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['이번에는 서버 주소도 맞지만 web과 client를 서로 다른 네트워크로 나눠 두었어요.'],
    know='client가 web과 공유하는 front 네트워크에 참여하도록 고치세요. 네트워크를 분리하는 것은 이름만 다르게 붙이는 것이 아니라 통신 경계를 만드는 일이에요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': START3, **FILES}, solution_files={'compose.yaml': SOLUTION3},
    commands=[UP, CLIENT],
    todo=ask('client의 요청 결과를 읽으세요.') + ['편집기의 compose.yaml에서 client가 web과 같은 네트워크에 참여하게 고치세요.'] + ask('이번 응답을 읽으세요.'),
    checks=[running('web'), config('client가 front 네트워크에 참여', {'services': {'client': {'networks': {'front': None}}}})],
    success='지금 compose.yaml에서 client가 web과 같은 front 네트워크에 있고, 터미널의 client 실행이 성공했어요.',
    complexity=dict(prior='서버의 바인드 주소를 고쳤어요.', new='서비스 이름으로 통신하려면 통신 가능한 네트워크를 공유해야 해요.',
                    changed='client의 네트워크', evidence='터미널의 client 실행 결과', lines=1, services=0),
    narration=[
        ('say', '주소와 바인드는 맞는데 네트워크가 나뉜 문제예요.', 'text:web과 client를 서로 다른 네트워크로 나눠 두었어요.'),
        bash(UP, 'web을 실행해요.', wait=300),
        ('say', 'front 네트워크를 만들고 web이 Healthy가 됐어요. back은 아직 만들지 않았어요.', TERMINAL),
        bash(CLIENT, 'client에서 요청해 볼게요.', fails=True),
        ('say', 'web이라는 이름을 찾지 못해요. back 네트워크에는 web이 없어요.', TERMINAL),
        ('say', 'client는 back에만 있어요. web과 공유하는 네트워크가 없어요.', 'code:networks: [back]'),
        patch('compose.yaml', *FIX3, 'client를 web과 같은 front 네트워크에 넣어요.'),
        bash(UP, '고친 파일로 다시 실행해요.'),
        ('say', 'web은 그대로예요. 바뀐 것은 client의 네트워크예요.', TERMINAL),
        bash(CLIENT, '다시 요청해요.'),
        ('say', '메모 서버 응답이 왔어요. 같은 front에서 web 이름을 찾았어요.', TERMINAL),
        ('say', '조심하세요. network_mode: host로 피하지 마세요. 사용자 PC의 네트워크와 분리된 실습 네트워크를 유지해야 해요.', 'text:네트워크를 분리하는 것은 이름만 다르게 붙이는 것이 아니라 통신 경계를 만드는 일이에요.')],
    review={'조심하세요. network_mode: host로 피하지 마세요. 사용자 PC의 네트워크와 분리된 실습 네트워크를 유지해야 해요.':
            '연결 실패를 host 네트워크로 우회하기 쉬워요. 앱도 이 설정을 실행 전에 거절해요.'})

FIX4 = ('    networks: [front]\n    healthcheck:', '    ports: ["127.0.0.1::8080"]\n    networks: [front]\n    healthcheck:')
SOLUTION4 = SOLUTION3.replace(*FIX4)
PORT = 'docker compose port web 8080'
CURL = 'curl -s "http://$(docker compose port web 8080)"'
S4 = compose_step(
    slug='final-host-port', title='PC에서도 빈 포트로 서버에 연결하게 하세요',
    objectives=['컨테이너 내부 포트와 호스트 공개 포트는 서로 다른 주소 영역이에요.'],
    start='앞 문제의 정답과 같은 compose.yaml로 새로 시작해요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['client에서는 연결돼요. 이번에는 PC의 브라우저에서도 접속할 수 있어야 해요.'],
    know='web에 127.0.0.1::8080 포트 연결을 추가하세요. 가운데 호스트 포트를 비워 Docker가 빈 포트를 고르게 해요. `docker compose port web 8080`은 Docker가 고른 실제 주소를 알려 줘요. curl은 PC에서 그 주소로 요청하는 명령이에요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': SOLUTION3, **FILES}, solution_files={'compose.yaml': SOLUTION4},
    commands=[UP, CLIENT, PORT, CURL],
    todo=ask('client의 응답을 읽으세요.') + [type_command(PORT, 'PC에 공개된 주소가 있는지 읽으세요.'),
          '편집기의 compose.yaml에서 web에 `127.0.0.1::8080` 포트 연결을 더하세요.'] + ask('client의 응답이 그대로인지 읽으세요.') + [
          type_command(PORT, 'Docker가 고른 127.0.0.1 주소를 읽으세요.'),
          type_command(CURL, 'PC에서 받은 응답을 읽으세요.')],
    checks=[running('web'), http('web', 8080, '메모 서버')],
    success='지금 compose.yaml로 만든 web이 127.0.0.1의 빈 포트에 공개됐고, client와 PC 모두 메모 서버 응답을 받았어요.',
    complexity=dict(prior='서비스 이름·바인드·네트워크를 각각 고쳤어요.', new='컨테이너 내부 포트와 호스트 공개 포트는 서로 다른 주소 영역이에요.',
                    changed='web의 호스트 포트 공개', evidence='compose port의 실제 주소와 PC에서의 응답', lines=1, services=0),
    narration=[
        ('say', '컨테이너끼리는 연결되는데 PC에서는 접속할 주소가 없는 문제예요.', 'text:이번에는 PC의 브라우저에서도 접속할 수 있어야 해요.'),
        bash(UP, 'web을 실행해요.', wait=300),
        ('say', 'web이 Healthy가 됐어요.', TERMINAL),
        bash(CLIENT, 'client에서 요청해요.'),
        ('say', '메모 서버 응답이 와요. 내부 연결은 이미 돼요.', TERMINAL),
        bash(PORT, 'PC에 공개된 주소를 물어볼게요.', fails=True),
        ('say', '공개된 포트가 없다는 오류예요. 내부 연결만으로 PC의 접속 주소가 생기지는 않아요.', TERMINAL),
        ('say', 'web에는 ports 설정이 없어요. 여기에 PC 쪽 연결을 더해요.', 'code:healthcheck:'),
        patch('compose.yaml', *FIX4, '127.0.0.1의 빈 포트를 web의 8080에 연결해요.'),
        bash(UP, '고친 파일로 web을 다시 만들어요.'),
        ('say', 'web 컨테이너를 새로 만들고 Healthy가 됐어요.', TERMINAL),
        bash(CLIENT, 'client 요청은 그대로인지 볼게요.'),
        ('say', '그대로 메모 서버예요. 컨테이너끼리는 계속 web:8080을 써요.', TERMINAL),
        bash(PORT, '이제 공개된 주소를 물어봐요.'),
        ('say', '127.0.0.1 뒤에 Docker가 고른 포트 번호가 나왔어요.', TERMINAL),
        bash(CURL, 'PC에서 그 주소로 요청해요.'),
        ('say', 'PC에서도 메모 서버 응답을 받았어요. 같은 서버에 두 경로로 연결됐어요.', TERMINAL),
        ('say', '조심하세요. client의 주소를 호스트 포트로 바꾸지 마세요. 컨테이너 간 연결은 내부 포트와 서비스 이름을 그대로 써요.', 'text:가운데 호스트 포트를 비워 Docker가 빈 포트를 고르게 해요.')],
    review={'조심하세요. client의 주소를 호스트 포트로 바꾸지 마세요. 컨테이너 간 연결은 내부 포트와 서비스 이름을 그대로 써요.':
            '포트를 공개한 직후 내부 주소까지 바꾸는 실수가 흔해요. client 출력이 그대로인 것과 연결해요.'},
    rejects=[([('"127.0.0.1::8080"', '"127.0.0.1::9090"')], '컨테이너에서 기다리지 않는 포트를 공개하면 PC의 요청이 응답을 받지 못해요.')])

LESSON = lesson(key='docker-network-ports', folder='docker_network_ports', pilot='넷',
    title='Docker 네트워크 · localhost는 누구인가요',
    objectives=['컨테이너마다 다른 localhost를 이해해요.', '서비스 이름·바인드·네트워크 경계를 구별해요.', 'PC의 빈 포트와 내부 포트를 연결해요.'],
    units=[unit('이름과 기다리는 주소', '요청을 보내는 위치와 받는 위치를 구별해요.',
                'web은 www 폴더의 메모 서버 페이지를 보여 주고, client는 web에 요청을 한 번 보내요. 터미널에서 docker compose로 실행하고 결과를 읽어요.', [S1, S2]),
           unit('네트워크 경계와 공개 포트', '내부 통신과 PC의 접속 경로를 연결해요.',
                '같은 web과 client를 네트워크로 나누고, PC에서도 접속할 수 있게 포트를 공개해요. 호스트 포트는 127.0.0.1의 빈 포트만 써요.', [S3, S4])],
    final_slug='final-host-port')
LESSON['revision'] = 4
