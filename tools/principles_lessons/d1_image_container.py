"""D1 이미지와 컨테이너: 프로세스로서의 컨테이너, 쓰기 레이어, 볼륨, 빌드 캐시 (실제 Docker 엔진).

Every Docker command is typed by the learner in the real practice terminal (PTY Bash). The CLI
chapter (d0_cli_intro.py) uses plain docker commands. From the Compose chapter on, the learner edits
compose.yaml, the Dockerfile or the app's files in the editor above the same terminal; the editor
saves into the terminal's folder and `docker compose` there runs as this step's own owned project
(compose_terminal.py, src/docker_lab/terminal.rs). Grading only reads the commands and the real
engine state (src/docker_practice.rs). Nothing is simulated and no lab script runs.
"""
from compose_terminal import (TERMINAL, bash, compose_step, file_text, history, logs, mount, patch,
                              read, running, type_command)

BUSYBOX = 'busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662'

DOCKER_GRADING = [
    '터미널에서 내가 실행해 성공한 docker 명령과 실제 Docker 엔진의 상태로 판정해요. 앱이 정답 명령이나 실습 스크립트를 대신 실행하지 않아요.',
    'Compose 문제는 지금 편집기의 파일(터미널 폴더의 실제 파일)로 실행한 명령만 세요. 컨테이너가 지금 파일로 만들어졌는지, 볼륨·로그·컨테이너 안 파일·빌드 이미지 레이어를 읽어서만 확인해요.',
    '시작 파일로 같은 명령을 입력하면 실패하고, 흔한 오해에 맞춘 파일도 실패하는지 실제 터미널로 확인해요.',
]
DOCKER_RESET = ['각 문제는 본문에서 알린 준비 상태로 시작해요. 초기화는 그 문제의 파일과 그 문제가 만든 Docker 자원만 시작 상태로 되돌려요.',
                '컨테이너·볼륨은 수업 동안 유지돼요. 문제를 옮기거나 명령을 다시 실행해도 앱이 다시 만들지 않아요. 해설은 별도 프로젝트로 시연해요.',
                '수업을 나가면 이 수업이 만든 것만 정리해요. 내 컴퓨터에 원래 있던 컨테이너·볼륨·이미지와 학습 진도는 지우지 않아요.']
DOCKER_NARRATION = ['수정 전 명령 입력 → Docker가 보여 준 결과 읽기 → 고칠 한 곳 → 같은 명령으로 다시 비교해요.',
                    '「조심하세요」는 그 스텝에서 실제로 하기 쉬운 실수에만 써요.']
DOCKER_VERIFY = ['실제 PTY 터미널과 실제 Docker 엔진으로 정답 통과·시작 파일 실패·기록된 오답 거절·다른 정답 허용을 확인해요(tests/lesson-cases, examples/validate_redesigned_lesson).',
                 '해설의 출력은 해설용 터미널의 실제 출력과 기록된 패턴으로 비교해요. Windows(Docker Desktop)에서 확인했고 macOS는 이 기록에 포함하지 않아요.']
STRATEGY = '각 스텝은 먼저 터미널에서 명령을 입력해 실제 상태를 봐요. 원인을 찾은 뒤 표시한 한 곳만 고치고 같은 명령으로 다시 확인해요. Docker Desktop이 켜져 있어야 해요.'

FOLDER = ('편집기의 파일은 터미널의 현재 폴더에 바로 저장돼요. docker compose는 이 폴더의 compose.yaml을 읽어요. '
          '이 문제만의 프로젝트 이름으로 실행해서 다른 컨테이너와 섞이지 않아요.')

# ---------------------------------------------------------------- unit 1: 컨테이너는 프로세스예요
S1_START = f"""# 메모 서버 컨테이너 하나를 띄워요.
services:
  memo:
    image: {BUSYBOX}
    # 고칠 곳: 시작 메시지를 찍고 메모 서버(여기서는 sleep)를 띄우는 명령이에요.
    command: ["sh", "-c", "echo 메모 서버 시작 && sleep 3600 &"]
"""
FIX1 = ("""    # 고칠 곳: 시작 메시지를 찍고 메모 서버(여기서는 sleep)를 띄우는 명령이에요.
    command: ["sh", "-c", "echo 메모 서버 시작 && sleep 3600 &"]""",
        """    # 컨테이너는 첫 프로세스(PID 1)가 살아 있는 동안만 실행 중이에요.
    # &를 빼서 sh가 sleep이 끝날 때까지 기다리게 해요. 그래야 PID 1이 끝나지 않아요.
    command: ["sh", "-c", "echo 메모 서버 시작 && sleep 3600"]""")
S1_SOLUTION = S1_START.replace(*FIX1)

# ---------------------------------------------------------------- unit 2: 쓰기 레이어와 볼륨
S2_START = f"""# 메모를 기억하는 컨테이너예요. 메모는 /memo/list.txt에 써요.
services:
  memo:
    image: {BUSYBOX}
    # /memo 폴더를 만든 뒤 sleep으로 계속 실행해요.
    command: ["sh", "-c", "mkdir -p /memo && sleep 3600"]
    # 고칠 곳: 지금 /memo는 컨테이너 자기 파일 시스템(쓰기 레이어)에 있어요.
"""
FIX2 = ("""    # 고칠 곳: 지금 /memo는 컨테이너 자기 파일 시스템(쓰기 레이어)에 있어요.
""", """    # memo라는 이름의 볼륨을 컨테이너의 /memo에 연결해요.
    # 이제 /memo에 쓴 파일은 컨테이너가 아니라 볼륨에 저장돼요.
    volumes:
      - memo:/memo

# 볼륨은 컨테이너 밖에서 Docker가 따로 관리해요. 컨테이너를 지워도 남아요.
volumes:
  memo:
""")
S2_SOLUTION = S2_START.replace(*FIX2)
WRITE2 = "docker compose exec memo sh -c 'echo 우유 >> /memo/list.txt'"
READ2 = 'docker compose exec memo cat /memo/list.txt'

S3_START = f"""# 같은 이미지로 두 가게의 메모 컨테이너를 띄워요.
services:
  shop_a:
    image: {BUSYBOX}
    command: ["sleep", "3600"]
    volumes:
      - memo_a:/memo
  shop_b:
    image: {BUSYBOX}
    command: ["sleep", "3600"]
    volumes:
      # 고칠 곳: B 가게가 연결한 볼륨이에요.
      - memo_a:/memo

volumes:
  memo_a:
"""
FIX3 = ("""      # 고칠 곳: B 가게가 연결한 볼륨이에요.
      - memo_a:/memo

volumes:
  memo_a:
""", """      # B 가게는 자기 볼륨 memo_b를 써요. 같은 볼륨 이름이면 같은 데이터를 함께 써요.
      - memo_b:/memo

volumes:
  memo_a:
  memo_b:
""")
S3_SOLUTION = S3_START.replace(*FIX3)
WRITE3A = "docker compose exec shop_a sh -c 'echo 우유 >> /memo/list.txt'"
WRITE3B = "docker compose exec shop_b sh -c 'echo 계란 >> /memo/list.txt'"
READ3A = 'docker compose exec shop_a cat /memo/list.txt'
READ3B = 'docker compose exec shop_b cat /memo/list.txt'

# ---------------------------------------------------------------- unit 3: 이미지는 레이어로 쌓여요
COMPOSE4 = """# shop 서비스의 이미지는 이 폴더의 Dockerfile로 만들어요.
services:
  shop:
    build:
      context: .
      # 제공 설정: 다른 실습의 빌드 캐시와 섞이지 않게 이 문제의 이름을 넘겨요.
      args:
        MQ3_CACHE_SEED: ${MQ3_PROJECT}
"""
S4_START = f"""# 가게 이미지를 만드는 Dockerfile이에요. COPY·RUN은 파일 시스템 레이어를 만들어요.
FROM {BUSYBOX}
# 제공 설정: 이전 실습의 빌드 캐시와 구분해요. 같은 문제의 빌드는 같은 값을 써요.
ARG MQ3_CACHE_SEED
RUN echo "$MQ3_CACHE_SEED" > /mq3-cache-seed
WORKDIR /app
# 고칠 곳: 메뉴 복사와 오래 걸리는 준비 단계의 순서예요.
COPY menu.txt .
RUN sleep 3 && echo "준비""완료" && echo ok > tool.txt
CMD ["cat", "menu.txt"]
"""
FIX4 = ("""# 고칠 곳: 메뉴 복사와 오래 걸리는 준비 단계의 순서예요.
COPY menu.txt .
RUN sleep 3 && echo "준비""완료" && echo ok > tool.txt""",
        """# 자주 바뀌지 않는 준비 단계를 먼저 둬요. 앞 레이어가 그대로면 Docker가 캐시를 써요.
RUN sleep 3 && echo "준비""완료" && echo ok > tool.txt
# 자주 바뀌는 메뉴는 마지막에 복사해요. 메뉴가 바뀌면 이 줄부터만 다시 만들어요.
COPY menu.txt .""")
S4_SOLUTION = S4_START.replace(*FIX4)

# ---------------------------------------------------------------- unit 4: 최종 도전
ADD5 = """# 메모 하나를 /data/memo.txt 끝에 더해요.
mkdir -p /data
echo "$1" >> /data/memo.txt
"""
SHOW5 = """# 메모 앱 버전과 지금까지의 메모를 한 줄로 보여 줘요.
memo=$(cat /data/memo.txt 2>/dev/null | tr '\\n' ' ' | sed 's/ $//')
echo "[v1] ${memo:-(없음)}"
"""
SHOW5_V2 = SHOW5.replace('[v1]', '[v2]')
DOCKERFILE5 = f"""# 메모 앱 이미지예요. 앱 코드(sh 스크립트)만 담아요. 메모 데이터는 담지 않아요.
FROM {BUSYBOX}
WORKDIR /app
COPY add.sh show.sh ./
CMD ["sleep", "3600"]
"""
S5_START = """# 메모 앱 서비스예요. 이미지는 이 폴더의 Dockerfile로 만들어요.
services:
  app:
    build: .
    # 고칠 곳: 앱이 메모를 쓰는 폴더가 지금은 컨테이너 안에만 있어요.
"""
FIX5 = ("""    # 고칠 곳: 앱이 메모를 쓰는 폴더가 지금은 컨테이너 안에만 있어요.
""", """    # add.sh는 /data에 메모를 써요. 그 폴더에 볼륨을 연결해요.
    # 앱 코드는 이미지에, 메모 데이터는 볼륨에 있어서 이미지를 바꿔도 메모가 남아요.
    volumes:
      - memos:/data

volumes:
  memos:
""")
S5_SOLUTION = S5_START.replace(*FIX5)
ADD = 'docker compose exec app sh /app/add.sh 우유'
SHOW = 'docker compose exec app sh /app/show.sh'
REBUILD = 'docker compose up -d --build --force-recreate'


def step(**fields):
    fields.setdefault('language', 'docker')
    fields.setdefault('docker_images', [BUSYBOX])
    return fields


def complexity(prior, new, changed, evidence, lines, services=0):
    return dict(prior=prior, new=new, changed=changed, evidence=evidence, lines=lines, services=services)


PID1 = compose_step(
    slug='pid1-lifetime', title='메모 서버 컨테이너가 계속 실행되게 하세요',
    objectives=['명령 끝의 &가 PID 1을 바로 끝나게 만든다는 것을 확인하고, 컨테이너가 계속 실행되게 고쳐요.'],
    start='오른쪽 위 편집기에는 compose.yaml이, 아래에는 실제 터미널이 있어요. ' + FOLDER + ' 아직 이 문제의 컨테이너는 없어요.',
    intro=['`command`는 시작 메시지와 메모 서버(여기서는 `sleep 3600`) 실행을 지시해요. 그런데 실행하면 상태가 `exited`로 나와요. 서버를 기다리지 않고 컨테이너가 끝났어요.'],
    know='컨테이너는 이미지로 시작한 프로세스예요. `command`로 시작한 첫 프로세스가 PID 1이고, PID 1이 끝나면 컨테이너도 끝나요. 셸에서 명령 끝의 `&`는 그 명령을 뒤에서 돌리고 셸은 바로 다음으로 넘어가요. `docker compose up -d`는 compose.yaml대로 컨테이너를 뒤에서 실행하고, 설정이 바뀌었으면 컨테이너를 새로 만들어요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': S1_START}, solution_files={'compose.yaml': S1_SOLUTION},
    commands=['docker compose up -d', 'docker compose ps -a', 'docker compose logs memo'],
    todo=[type_command('docker compose up -d', 'memo 서비스를 뒤에서 실행해요. 처음에는 이미지를 받느라 조금 걸릴 수 있어요.'),
          type_command('docker compose ps -a', 'STATUS 열에서 memo의 상태를 읽으세요.'),
          '편집기의 compose.yaml에서 `command` 줄을 sh가 바로 끝나지 않게 고치세요.',
          type_command('docker compose up -d', '바뀐 파일로 다시 실행해요.'),
          type_command('docker compose ps -a', 'STATUS 열을 다시 읽으세요.'),
          type_command('docker compose logs memo', '시작 메시지를 찾으세요.')],
    checks=[running('memo'), logs('memo', '메모 서버 시작')],
    success='지금 파일로 만든 memo 컨테이너가 running이고, 시작 메시지가 로그에 있어요.',
    complexity=complexity('터미널에서 docker run·ps·logs를 실행해 봤어요.', 'PID 1과 컨테이너의 수명', '첫 프로세스가 끝나지 않게 함',
                          '터미널의 실제 ps 상태(Exited·Up)와 로그', 1, 1),
    narration=[
        ('say', '지금 설정 그대로 실행해서 상태를 볼게요.', 'text:그런데 실행하면 상태가 `exited`로 나와요.'),
        bash('docker compose up -d', 'compose.yaml대로 memo 서비스를 뒤에서 실행할게요.', wait=600),
        ('say', 'Started가 나왔어요. 컨테이너를 시작했다는 뜻이에요.', TERMINAL),
        bash('docker compose ps -a', '-a를 붙여 끝난 컨테이너까지 표로 볼게요.'),
        ('say', 'STATUS가 Exited예요. 서버를 기다리지 않고 컨테이너가 끝났어요.', TERMINAL),
        ('say', '끝의 &가 sleep을 뒤로 보내요. sh는 할 일이 없어 바로 끝나요.', 'code:sleep 3600 &'),
        patch('compose.yaml', *FIX1, '&를 빼서 sh가 sleep을 기다리게 해요.'),
        bash('docker compose up -d', '고친 파일로 다시 실행해요.'),
        ('say', 'Recreated가 보여요. 설정이 바뀌어 컨테이너를 새로 만들었어요.', TERMINAL),
        bash('docker compose ps -a', '다시 상태를 볼게요.'),
        ('say', '이제 STATUS가 Up이에요. PID 1인 sh가 sleep을 기다리고 있어요.', TERMINAL),
        bash('docker compose logs memo', 'logs로 시작 메시지를 읽을게요.'),
        ('say', '메모 서버 시작이 보여요. 첫 프로세스가 남긴 출력이에요.', TERMINAL),
        ('say', '조심하세요. 이 셸 명령에서 &를 붙이면 셸이 기다리지 않고 끝나요. 서버가 직접 PID 1이 되거나 PID 1이 서버를 기다려야 컨테이너가 유지돼요.', 'text:셸에서 명령 끝의 `&`는 그 명령을 뒤에서 돌리고 셸은 바로 다음으로 넘어가요.')],
    review={'조심하세요. 이 셸 명령에서 &를 붙이면 셸이 기다리지 않고 끝나요. 서버가 직접 PID 1이 되거나 PID 1이 서버를 기다려야 컨테이너가 유지돼요.':
            '시작 파일이 바로 그 실수(sleep 3600 &)이고, 앞에서 터미널의 ps -a로 Exited를 봤어요.'},
    accepts=[([('"echo 메모 서버 시작 && sleep 3600"', '"echo 메모 서버 시작 && exec sleep 3600"')], 'exec로 sh를 sleep으로 바꿔도 PID 1이 계속 살아 있어요.'),
             ([('"echo 메모 서버 시작 && sleep 3600"', '"echo 메모 서버 시작; tail -f /dev/null"')], '끝나지 않는 다른 앞 프로세스도 같은 원리예요.')],
    rejects=[([('"echo 메모 서버 시작 && sleep 3600"', '"sleep 3600 & echo 메모 서버 시작"')], 'sleep을 뒤로 보내고 echo가 끝나면 sh가 끝나요.')])

VOLUME = compose_step(
    slug='volume-survives-recreate', title='다시 만들어도 메모가 남게 볼륨을 연결하세요',
    objectives=['컨테이너를 다시 만들면 쓰기 레이어의 파일이 사라진다는 것을 보고, 이름 있는 볼륨을 연결해 남게 해요.'],
    start='새 문제의 compose.yaml과 빈 터미널 폴더로 시작해요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['메모를 쓰고 컨테이너를 다시 만든 뒤 읽으면 메모 파일이 없다고 나와요. 같은 이미지, 같은 설정인데 메모가 사라졌어요.'],
    know='컨테이너 안에서 쓴 파일은 그 컨테이너의 쓰기 레이어에 저장돼요. `docker compose up -d --force-recreate`는 컨테이너를 지우고 이미지에서 새로 만들어요. `restart`는 같은 컨테이너를 다시 켜요. 볼륨은 컨테이너 밖에서 Docker가 관리하는 저장소이고 `down -v`를 해야 지워져요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': S2_START}, solution_files={'compose.yaml': S2_SOLUTION},
    commands=['docker compose up -d', WRITE2, 'docker compose up -d --force-recreate', READ2],
    todo=[type_command('docker compose up -d', 'memo 서비스를 실행해요.'),
          type_command(WRITE2, '컨테이너 안 /memo/list.txt에 우유를 써요.'),
          type_command('docker compose up -d --force-recreate', '컨테이너를 새로 만들어요.'),
          type_command(READ2, '메모가 남았는지 읽으세요.'),
          '편집기의 compose.yaml `고칠 곳` 자리에 `memo` 볼륨을 `/memo`에 연결하는 `volumes`를 쓰고, 파일 끝에 볼륨 선언을 더하세요.',
          type_command('docker compose up -d', '볼륨을 연결한 컨테이너로 바꿔요.'),
          type_command(WRITE2, '다시 우유를 써요.'),
          type_command('docker compose up -d --force-recreate', '컨테이너를 다시 새로 만들어요.'),
          type_command(READ2, '이번에는 메모가 남았는지 읽으세요.')],
    checks=[running('memo'), mount('memo', '/memo', 'memo'), read('memo 컨테이너의 /memo/list.txt', 'memo', ['cat', '/memo/list.txt'], has=['우유'])],
    success='새로 만든 memo 컨테이너의 /memo가 이름 있는 볼륨 memo이고, 다시 만들기 전에 쓴 우유가 남아 있어요.',
    complexity=complexity('컨테이너가 프로세스라는 것을 확인했어요.', '쓰기 레이어와 이름 있는 볼륨', '/memo에 볼륨 연결',
                          '다시 만든 뒤 터미널의 cat 결과와 실제 마운트', 3),
    narration=[
        ('say', '같은 설정으로 다시 만들었는데 메모가 사라지는 문제예요.', 'text:같은 이미지, 같은 설정인데 메모가 사라졌어요.'),
        bash('docker compose up -d', '먼저 memo 서비스를 실행할게요.'),
        ('say', 'Started가 나왔어요. memo 컨테이너가 실행 중이에요.', TERMINAL),
        bash(WRITE2, '컨테이너 안 /memo/list.txt에 우유를 써요.'),
        ('say', '아무것도 출력하지 않고 프롬프트로 돌아왔어요. 파일에 썼어요.', TERMINAL),
        bash('docker compose up -d --force-recreate', '이번에는 컨테이너를 지우고 새로 만들게요.'),
        ('say', 'Recreated가 보여요. 이미지에서 새 컨테이너를 만들었어요.', TERMINAL),
        bash(READ2, '메모를 다시 읽어 볼게요.', fails=True),
        ('say', '파일이 없다는 오류가 나요. 새 컨테이너는 새 쓰기 레이어에서 시작했어요.', TERMINAL),
        ('say', '지금 이 서비스에는 volumes가 없어요. /memo는 컨테이너의 쓰기 레이어에 있어요.', 'code:# 고칠 곳: 지금 /memo는 컨테이너 자기 파일 시스템(쓰기 레이어)에 있어요.'),
        patch('compose.yaml', *FIX2, '/memo에 이름 있는 볼륨을 연결하고, 파일 끝에 볼륨을 선언해요.'),
        bash('docker compose up -d', '바꾼 파일로 다시 실행해요.'),
        ('say', '볼륨 memo를 만들고 컨테이너를 새로 만들었어요.', TERMINAL),
        bash(WRITE2, '우유를 다시 써요.'),
        ('say', '이번 메모는 볼륨에 저장됐어요.', TERMINAL),
        bash('docker compose up -d --force-recreate', '컨테이너를 다시 새로 만들어요.'),
        ('say', '또 Recreated예요. 컨테이너는 새것이에요.', TERMINAL),
        bash(READ2, '메모를 읽어 볼게요.'),
        ('say', '우유가 그대로 나와요. 새 컨테이너가 같은 볼륨을 연결했어요.', TERMINAL),
        ('say', '조심하세요. 처음 상태로 돌리려고 down -v를 쓰면 볼륨의 데이터도 지워져요. 데이터를 지킬 때는 -v 없이 down 해요.', 'text:볼륨은 컨테이너 밖에서 Docker가 관리하는 저장소이고 `down -v`를 해야 지워져요.')],
    review={'조심하세요. 처음 상태로 돌리려고 down -v를 쓰면 볼륨의 데이터도 지워져요. 데이터를 지킬 때는 -v 없이 down 해요.':
            '볼륨을 붙인 직후 학습자가 초기화 대신 down -v를 쓰기 쉬워요. 알아두세요의 down -v 문장과 연결해요.'},
    accepts=[([('      - memo:/memo', '      - type: volume\n        source: memo\n        target: /memo')], '긴 문법으로 같은 볼륨을 연결해도 같아요.')],
    rejects=[([('      - memo:/memo', '      - memo:/data')], '볼륨을 다른 폴더에 연결하면 /memo는 여전히 쓰기 레이어예요.'),
             ([('      - memo:/memo', '      - ./memo:/memo')], '실습 폴더를 직접 연결(바인드 마운트)하면 Docker가 관리하는 볼륨이 아니에요.')])

SEPARATE = compose_step(
    slug='separate-volumes', title='두 가게가 각자 메모를 갖게 하세요',
    objectives=['볼륨 이름이 같으면 두 컨테이너가 같은 데이터를 본다는 것을 확인하고, 가게마다 볼륨을 나눠요.'],
    start='두 가게(shop_a, shop_b)의 compose.yaml로 새로 시작해요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['B 가게에 계란을 쓰고 A 가게의 메모를 읽으면 계란이 보여요. B 가게의 메모가 A 가게에 섞였어요.'],
    know='같은 이미지로 만든 컨테이너도 쓰기 레이어는 저마다 따로예요. 볼륨은 이름으로 찾아요. 두 서비스가 같은 볼륨 이름을 연결하면 같은 저장소를 함께 써요. `docker compose down -v`는 이 프로젝트의 컨테이너와 볼륨을 지워요.',
    images=[BUSYBOX], editable=['compose.yaml'], files={'compose.yaml': S3_START}, solution_files={'compose.yaml': S3_SOLUTION},
    commands=['docker compose down -v', 'docker compose up -d', WRITE3A, WRITE3B, READ3A, READ3B],
    todo=[type_command('docker compose up -d', '두 가게를 실행해요.'),
          type_command(WRITE3B, 'B 가게에 계란을 써요.'),
          type_command(READ3A, 'A 가게의 메모를 읽으세요.'),
          '편집기의 compose.yaml에서 B 가게가 자기 볼륨 `memo_b`를 쓰게 고치고, 파일 끝의 볼륨 선언에도 더하세요.',
          type_command('docker compose down -v', '앞에서 섞인 볼륨을 지워요.'),
          type_command('docker compose up -d', '고친 파일로 두 가게를 실행해요.'),
          type_command(WRITE3A, 'A 가게에 우유를 써요.'),
          type_command(WRITE3B, 'B 가게에 계란을 써요.'),
          type_command(READ3A, 'A 가게의 메모를 읽으세요.'),
          type_command(READ3B, 'B 가게의 메모를 읽으세요.')],
    checks=[running('shop_b'), mount('shop_a', '/memo', 'memo_a'), mount('shop_b', '/memo', 'memo_b'),
            read('A 가게의 /memo/list.txt', 'shop_a', ['cat', '/memo/list.txt'], has=['우유'], lacks=['계란']),
            read('B 가게의 /memo/list.txt', 'shop_b', ['cat', '/memo/list.txt'], has=['계란'], lacks=['우유'])],
    success='A 가게는 memo_a, B 가게는 memo_b를 연결했고, 각자 쓴 메모만 있어요.',
    complexity=complexity('볼륨을 연결해 다시 만들어도 데이터가 남게 했어요.', '볼륨 이름으로 공유되는 저장소', 'B 가게의 볼륨 이름',
                          '두 가게에서 cat으로 읽은 메모와 실제 마운트', 2),
    narration=[
        ('say', '두 가게의 메모가 섞이는 문제예요.', 'text:B 가게의 메모가 A 가게에 섞였어요.'),
        bash('docker compose up -d', '두 가게를 실행할게요.'),
        ('say', 'shop_a와 shop_b 컨테이너가 시작됐어요.', TERMINAL),
        bash(WRITE3B, 'B 가게에만 계란을 써요.'),
        ('say', 'B 가게의 /memo/list.txt에 썼어요.', TERMINAL),
        bash(READ3A, '이제 A 가게의 메모를 읽어요.'),
        ('say', 'A 가게에서도 계란이 나와요. 쓰지 않은 메모가 보여요.', TERMINAL),
        ('say', '두 서비스가 모두 memo_a를 /memo에 연결했어요. 컨테이너는 둘이지만 저장소는 하나예요.', 'code:# 고칠 곳: B 가게가 연결한 볼륨이에요.'),
        patch('compose.yaml', *FIX3, 'B 가게에 자기 볼륨 memo_b를 연결하고 선언해요.'),
        bash('docker compose down -v', '섞인 memo_a의 데이터부터 지울게요.'),
        ('say', '컨테이너와 볼륨이 지워졌어요. 이 문제의 것만 지웠어요.', TERMINAL),
        bash('docker compose up -d', '고친 파일로 다시 실행해요.'),
        ('say', '이번에는 memo_a와 memo_b 두 볼륨을 만들었어요.', TERMINAL),
        bash(WRITE3A, 'A 가게에 우유를 써요.'),
        ('say', 'A 가게의 볼륨에 썼어요.', TERMINAL),
        bash(WRITE3B, 'B 가게에 계란을 써요.'),
        ('say', 'B 가게의 볼륨에 썼어요.', TERMINAL),
        bash(READ3A, 'A 가게를 읽어요.'),
        ('say', 'A 가게에는 우유만 있어요.', TERMINAL),
        bash(READ3B, 'B 가게도 읽어요.'),
        ('say', 'B 가게에는 계란만 있어요. 이제 각자 메모를 가져요.', TERMINAL),
        ('say', '같은 이미지에서 시작해도 데이터는 어느 볼륨을 연결했는지가 정해요.', 'text:볼륨은 이름으로 찾아요.')],
    review={'같은 이미지에서 시작해도 데이터는 어느 볼륨을 연결했는지가 정해요.':
            '같은 이미지와 다른 볼륨이라는 조건을 두 가게 출력과 연결해요. 이미지가 같다는 것만으로 데이터 공유가 정해지지 않아요.'},
    rejects=[([('      - memo_b:/memo\n', '')], 'B의 볼륨을 빼면 B 가게의 /memo가 없어 메모를 쓰지 못해요.')])

CACHE = compose_step(
    slug='layer-cache-order', title='메뉴만 바꿨을 때 준비 단계를 다시 하지 않게 하세요',
    objectives=['앞 레이어가 바뀌면 그 뒤의 레이어를 모두 다시 만든다는 것을 보고, 자주 바뀌는 COPY를 뒤로 옮겨요.'],
    start='편집기에는 Dockerfile이 있어요. 터미널 폴더에는 compose.yaml과 menu.txt(우유)도 준비돼 있어요. 준비 단계(RUN)는 3초 걸리고 준비완료를 찍어요.',
    intro=['메뉴 한 줄만 바꾸고 다시 빌드해도 3초 걸리는 준비 단계를 다시 해요.'],
    know='`COPY`와 `RUN`은 이미지의 파일 시스템을 바꾸는 레이어를 만들어요. `CMD` 같은 명령은 실행 설정을 기록해요. 입력이 같은 단계는 캐시를 쓸 수 있어요. 빌드 출력에서 캐시를 쓴 단계에는 CACHED가 붙어요. `COPY`는 복사할 파일 내용도 입력이에요. 앞 단계가 바뀌면 뒤 단계도 캐시를 새로 판단해요.',
    images=[BUSYBOX], editable=['Dockerfile'], files={'Dockerfile': S4_START, 'compose.yaml': COMPOSE4, 'menu.txt': '우유\n'},
    solution_files={'Dockerfile': S4_SOLUTION},
    commands=['docker compose build', 'echo 빵 >> menu.txt', 'docker compose build', 'docker compose run --rm shop'],
    todo=[type_command('docker compose build', '처음 빌드에서 준비완료 줄을 찾으세요.'),
          type_command('echo 빵 >> menu.txt', '메뉴에 빵을 더해요.'),
          type_command('docker compose build', '두 번째 빌드에서 RUN sleep 단계가 다시 실행됐는지 읽으세요.'),
          '편집기의 Dockerfile에서 `COPY menu.txt .` 줄과 `RUN` 줄의 순서를 바꾸세요.',
          type_command('docker compose build', '바꾼 순서로 빌드해요.'),
          type_command('echo 빵 >> menu.txt', '메뉴를 다시 바꿔요.'),
          type_command('docker compose build', 'RUN sleep 단계에 CACHED가 붙었는지 읽으세요.'),
          type_command('docker compose run --rm shop', '이미지에 들어간 메뉴를 확인하세요.')],
    checks=[history('shop', 'sleep 3', 'COPY menu.txt'), file_text('menu.txt', has=['빵'])],
    same_files=['Dockerfile'],
    success='지금 Dockerfile로 빌드한 shop 이미지의 레이어가 준비 단계 → 메뉴 복사 순서이고, 메뉴를 바꾼 뒤 다시 빌드하고 실행했어요.',
    complexity=complexity('이미지에서 컨테이너를 만들어 봤어요.', '레이어와 빌드 캐시', 'COPY와 RUN의 순서',
                          '두 번째 빌드 출력의 CACHED와 실제 이미지 레이어 순서', 2),
    narration=[
        ('say', '메뉴 한 줄만 바꿨는데 오래 걸리는 준비를 또 하는 문제예요.', 'text:메뉴 한 줄만 바꾸고 다시 빌드해도 3초 걸리는 준비 단계를 다시 해요.'),
        bash('docker compose build', '먼저 이미지를 빌드할게요.', wait=300),
        ('say', '단계마다 줄이 나와요. RUN sleep 단계에서 준비완료가 찍혔어요.', TERMINAL),
        bash('echo 빵 >> menu.txt', '메뉴 파일에 빵을 더해요.'),
        ('say', 'menu.txt만 바뀌었어요.', TERMINAL),
        bash('docker compose build', '같은 명령으로 다시 빌드해요.', wait=300),
        ('say', '두 번째 빌드도 RUN sleep 단계를 다시 실행했어요. 준비완료가 또 나와요.', TERMINAL),
        ('say', '메뉴가 바뀌어 COPY 레이어가 달라졌어요. 그 뒤에 있는 RUN도 다시 만들어요.', 'code:COPY menu.txt .'),
        patch('Dockerfile', *FIX4, '준비 단계를 먼저, 메뉴 복사를 뒤에 둬요.'),
        bash('docker compose build', '바꾼 순서로 빌드해요.', wait=300),
        ('say', '순서가 바뀌어 이번 빌드는 준비 단계부터 새로 만들었어요.', TERMINAL),
        bash('echo 빵 >> menu.txt', '메뉴를 다시 바꿔요.'),
        ('say', '또 menu.txt만 바뀌었어요.', TERMINAL),
        bash('docker compose build', '다시 빌드해요.', wait=300),
        ('say', '이번에는 RUN sleep 단계에 CACHED가 붙었어요. COPY부터만 다시 만들었어요.', TERMINAL),
        bash('docker compose run --rm shop', '이미지의 메뉴를 출력해요.'),
        ('say', '새 메뉴가 보여요. 메뉴는 새것이고 준비 단계는 캐시를 썼어요.', TERMINAL),
        ('say', '조심하세요. 파일이 필요한 RUN을 COPY 앞으로 옮기면 아직 그 파일이 없어요. 그 파일이 필요한 단계는 COPY 뒤에 둬요.', 'text:앞 단계가 바뀌면 뒤 단계도 캐시를 새로 판단해요.')],
    review={'조심하세요. 파일이 필요한 RUN을 COPY 앞으로 옮기면 아직 그 파일이 없어요. 그 파일이 필요한 단계는 COPY 뒤에 둬요.':
            '순서를 바꾸는 이 스텝에서 바로 생기는 다음 실수예요. RUN이 menu.txt를 쓰면 COPY 전이라 파일이 없어요. 이 RUN은 menu.txt를 쓰지 않아 순서를 바꿔도 돼요.'},
    accepts=[([('COPY menu.txt .', 'COPY menu.txt /app/')], '절대 경로로 같은 곳에 복사해도 같아요.')],
    rejects=[([('COPY menu.txt .', 'COPY menu.txt /tmp/')], '메뉴를 다른 곳에 복사하면 CMD가 /app/menu.txt를 찾지 못해 run이 실패해요.')])

FINAL = compose_step(
    slug='final-memo-app', title='앱을 고쳐 다시 빌드해도 메모가 남게 하세요',
    objectives=['앱이 데이터를 쓰는 경로를 코드에서 찾아 볼륨을 연결하고, 새 이미지와 남은 데이터를 함께 확인해요.'],
    start='편집기에는 compose.yaml과 show.sh가 있어요. 터미널 폴더에는 Dockerfile과 add.sh도 준비돼 있어요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['메모를 쓰고 앱을 고쳐 다시 빌드하면 앱 버전은 v2로 바뀌는데 메모는 `(없음)`이에요. 앱을 고칠 때마다 메모가 사라지면 쓸 수 없어요.',
           'add.sh와 show.sh를 읽고, 메모가 실제로 어느 폴더에 저장되는지 찾으세요.'],
    know='`up -d --build`는 이미지를 새로 만들고, 바뀐 이미지로 컨테이너를 새로 만들어요. `--force-recreate`는 바뀐 것이 없어도 컨테이너를 새로 만들어요. 새 컨테이너는 새 쓰기 레이어에서 시작해요. 볼륨은 연결한 폴더의 데이터만 지켜요.',
    images=[BUSYBOX], editable=['compose.yaml', 'show.sh'],
    files={'compose.yaml': S5_START, 'show.sh': SHOW5, 'Dockerfile': DOCKERFILE5, 'add.sh': ADD5},
    solution_files={'compose.yaml': S5_SOLUTION, 'show.sh': SHOW5_V2},
    commands=['docker compose up -d --build', ADD, REBUILD, SHOW], same_files=['compose.yaml'],
    todo=[type_command('cat add.sh', '메모를 쓰는 폴더를 찾으세요.'),
          type_command('docker compose up -d --build', '앱 이미지를 빌드하고 실행해요.'),
          type_command(ADD, '메모 우유를 더해요.'),
          '편집기의 show.sh 탭에서 `[v1]`을 `[v2]`로 바꿔 앱을 고치세요.',
          type_command(REBUILD, '고친 앱으로 이미지와 컨테이너를 새로 만들어요.'),
          type_command(SHOW, '버전과 메모를 읽으세요.'),
          '편집기의 compose.yaml `고칠 곳` 자리에 그 폴더에 이름 있는 볼륨을 연결하는 `volumes`를 쓰고, 파일 끝에 볼륨을 선언하세요.',
          type_command('docker compose up -d --build', '볼륨을 연결한 컨테이너로 바꿔요.'),
          type_command(ADD, '메모 우유를 다시 더해요.'),
          type_command(REBUILD, '컨테이너를 다시 새로 만들어요.'),
          type_command(SHOW, '버전과 메모를 다시 읽으세요.')],
    checks=[running('app'), mount('app', '/data'), read('app 컨테이너의 /data/memo.txt', 'app', ['cat', '/data/memo.txt'], has=['우유']),
            read('app 이미지의 show.sh', 'app', ['cat', '/app/show.sh'], has=['[v2]'])],
    success='새로 만든 app 컨테이너가 v2 앱을 담고 있고, /data의 이름 있는 볼륨에 우유가 남아 있어요.',
    complexity=complexity('볼륨·공유·빌드 캐시를 각각 확인했어요.', '', '앱의 데이터 폴더에 볼륨 연결',
                          '다시 빌드 전후의 버전·메모와 실제 마운트', 3),
    narration=[
        ('say', '앱을 고쳐 다시 빌드하면 메모가 사라지는 문제예요.', 'text:앱을 고칠 때마다 메모가 사라지면 쓸 수 없어요.'),
        bash('cat add.sh', '먼저 메모를 쓰는 add.sh를 읽을게요.'),
        ('say', 'add.sh는 메모를 /data/memo.txt에 써요. 이 폴더가 핵심이에요.', 'text:add.sh와 show.sh를 읽고, 메모가 실제로 어느 폴더에 저장되는지 찾으세요.'),
        ('say', 'build 줄 때문에 up --build가 이미지를 새로 만들고, 그 이미지로 컨테이너도 새로 만들어요.', 'code:build: .'),
        bash('docker compose up -d --build', '앱 이미지를 빌드하고 실행해요.', wait=300),
        ('say', '이미지를 빌드하고 app 컨테이너를 시작했어요.', TERMINAL),
        bash(ADD, '메모 우유를 더해요.'),
        ('say', 'add.sh가 /data/memo.txt에 우유를 썼어요.', TERMINAL),
        patch('show.sh', '[v1]', '[v2]', '앱을 고쳐요. 버전 표시를 v2로 바꿔요.'),
        bash(REBUILD, '고친 앱으로 이미지와 컨테이너를 새로 만들어요.', wait=300),
        ('say', '바뀐 show.sh가 든 이미지로 컨테이너를 새로 만들었어요.', TERMINAL),
        bash(SHOW, '버전과 메모를 볼게요.'),
        ('say', 'v2로 바뀌었는데 메모는 없음이에요. /data가 옛 컨테이너의 쓰기 레이어에 있었어요.', TERMINAL),
        patch('compose.yaml', *FIX5, '/data에 memos 볼륨을 연결하고 선언해요.'),
        bash('docker compose up -d --build', '바꾼 파일로 다시 실행해요.', wait=300),
        ('say', '볼륨 memos를 만들고 컨테이너를 새로 만들었어요.', TERMINAL),
        bash(ADD, '우유를 다시 더해요.'),
        ('say', '이번 메모는 볼륨에 저장됐어요.', TERMINAL),
        bash(REBUILD, '컨테이너를 다시 새로 만들어요.', wait=300),
        ('say', '컨테이너는 또 새것이에요.', TERMINAL),
        bash(SHOW, '버전과 메모를 다시 볼게요.'),
        ('say', 'v2와 우유가 함께 보여요. 새 컨테이너가 같은 볼륨을 연결했어요.', TERMINAL),
        ('say', '이미지는 새것으로 바뀌었고, 메모는 볼륨에 있어서 그대로예요. 코드와 데이터가 다른 곳에 있어요.', 'text:볼륨은 연결한 폴더의 데이터만 지켜요.')],
    review={},
    rejects=[([('      - memos:/data', '      - memos:/app')], '/app에 볼륨을 연결하면 메모는 여전히 쓰기 레이어에 있고, 볼륨이 앱 코드 폴더를 덮어 새 버전도 보이지 않아요.'),
             ([('      - memos:/data', '      - memos:/memo')], '앱이 쓰지 않는 폴더에 연결하면 메모는 지켜지지 않아요.')])


LESSON = dict(
    key='docker-image-container', folder='docker_image_container', pilot='리', revision=7,
    title='이미지와 컨테이너 · 지워도 남는 것과 사라지는 것',
    category='docker', category_title='Docker', track=None,
    category_evidence='실제 Docker 엔진으로 컨테이너·볼륨·이미지를 다루는 수업이에요.',
    track_evidence='트랙 없음: 「기본」은 2026-10-25에 있던 수업에만 붙인 사용자 결정이고, 새 수업의 트랙(필수·고급)은 사용자 승인 없이 정하지 않아요.',
    audience='docker run을 따라 해 봤지만 컨테이너를 지우면 무엇이 사라지는지 설명하기 어려운 학습자',
    prerequisites=['터미널에서 명령을 실행하고 결과를 읽을 수 있어요.', 'Docker Desktop을 설치하고 켤 수 있어요(설치는 학습자가 해요).'],
    objectives=['컨테이너는 이미지로 시작한 프로세스이고, 첫 프로세스(PID 1)가 끝나면 컨테이너도 끝난다는 것을 실제 상태로 설명해요.',
                '다시 만들기와 down -v에서 쓰기 레이어와 볼륨의 데이터가 각각 어떻게 되는지 관찰하고, 남아야 할 데이터를 볼륨에 두는 구성을 직접 써요.',
                '이미지가 레이어로 쌓이고 바뀐 줄부터 다시 만든다는 것을 빌드 결과로 확인하고, 캐시를 살리는 순서로 Dockerfile을 고쳐요.'],
    scope=['PID 1과 컨테이너 수명, 같은 이미지의 독립 컨테이너, 쓰기 레이어, 이름 있는 볼륨과 공유, force-recreate·down -v, Dockerfile 레이어와 빌드 캐시, 코드(이미지)와 데이터(볼륨)의 분리'],
    out_of_scope=['네트워크와 포트(다음 수업 docker-network-ports)', 'DB 컨테이너(docker-compose-db)', '레지스트리에 이미지 올리기', '멀티 스테이지 빌드·이미지 크기 줄이기'],
    sources=[
        ('https://docs.docker.com/engine/containers/multi-service_container/', '컨테이너의 주 실행 프로세스는 ENTRYPOINT·CMD이고, 그 프로세스가 끝나면 컨테이너도 멈춰요.', 'Docker 공식 문서예요. 실제 엔진의 상태(exited·running)로 확인해요.'),
        ('https://docs.docker.com/engine/storage/', '컨테이너 안에서 만든 파일은 쓰기 레이어에 저장되고 컨테이너를 지우면 함께 사라져요. 볼륨은 컨테이너와 따로 남아요.', 'Docker 공식 문서예요. 다시 만들기·down -v로 실제 확인해요.'),
        ('https://docs.docker.com/build/cache/', '한 레이어가 바뀌면 그 뒤의 레이어도 모두 다시 만들어요. 자주 바뀌는 것을 뒤에 둬요.', 'Docker 공식 문서예요. 실제 빌드 출력으로 확인해요.'),
        ('https://docs.docker.com/reference/cli/docker/compose/down/', 'down은 컨테이너와 네트워크를 지우고, -v를 붙이면 이름 있는 볼륨도 지워요.', 'Docker 공식 CLI 문서예요. 실제 실행으로 확인해요.'),
    ],
    description='메모를 기억하는 작은 컨테이너로, 컨테이너의 수명·쓰기 레이어·볼륨·이미지 레이어를 차례로 고쳐요.',
    brief=('컨테이너가 프로세스라는 것, 쓰기 레이어와 볼륨, 이미지 레이어와 빌드 캐시를 실제 Docker로 다뤄요.',
           '앱 이미지를 고쳐 다시 빌드하고 컨테이너를 새로 만들어도 메모가 남게 구성해요.',
           ['컨테이너가 바로 끝나는 이유를 PID 1로 설명해요.', '지워지는 데이터와 남는 데이터를 구별해요.', '바뀐 줄부터 다시 빌드되는 것을 봐요.'],
           '실제 Docker 엔진에서 실행해요. Docker Desktop이 켜져 있어야 해요.',
           '컨테이너를 지우면 무엇이 사라지고 무엇이 남을까요?'),
    representative=dict(slug='final-memo-app', expected_action='앱이 메모를 쓰는 폴더(/data)에 이름 있는 볼륨을 연결해요.',
                        acceptance='메모를 쓴 뒤 앱을 고쳐 이미지를 다시 빌드하고 컨테이너를 새로 만들어도 메모가 남고 새 앱 버전이 보여야 해요.',
                        reset='이 문제의 시작 파일로 돌아가고, 이 문제가 만든 컨테이너·볼륨·빌드 이미지만 지워요.',
                        narration='다시 빌드한 뒤 메모가 사라지는 것을 터미널에서 보고, add.sh가 쓰는 폴더를 찾아 볼륨을 연결한 뒤 같은 명령으로 다시 확인해요.'),
    grading=DOCKER_GRADING, reset=DOCKER_RESET, narration_policy=DOCKER_NARRATION, verification=DOCKER_VERIFY,
    learning_strategy=STRATEGY,
    chapters=[
        dict(title='컨테이너는 프로세스예요', objectives=['컨테이너가 실행 중인지 아닌지는 첫 프로세스가 정한다는 것을 실제 상태로 확인해요.'],
             units=[dict(title='PID 1이 끝나면 컨테이너도 끝나요', objectives=['컨테이너의 첫 프로세스와 그 프로세스가 띄운 다른 프로세스를 구별해요.'],
                         premise='메모 서버 컨테이너 하나를 compose.yaml로 띄워요. 터미널에서 docker compose로 실행하고 상태를 직접 읽어요.',
                         steps=[PID1])]),
        dict(title='지워지는 데이터와 남는 데이터', objectives=['컨테이너의 쓰기 레이어와 볼륨을 구별하고, 남아야 할 데이터를 볼륨에 둬요.'],
             units=[
                 dict(title='다시 만들면 쓰기 레이어는 새것이에요', objectives=['다시 만든 컨테이너는 새 쓰기 레이어에서 시작한다는 것을 메모로 확인해요.'],
                      premise='메모 컨테이너가 /memo/list.txt에 메모를 써요. 터미널에서 메모를 쓰고 컨테이너를 다시 만든 뒤 읽어요.',
                      steps=[VOLUME]),
                 dict(title='볼륨은 이름으로 공유돼요', objectives=['같은 이미지의 두 컨테이너가 각자 쓰기 레이어를 갖고, 같은 이름의 볼륨은 함께 쓴다는 것을 확인해요.'],
                      premise='같은 busybox 이미지로 두 가게(shop_a, shop_b)의 메모 컨테이너를 띄워요. A 가게에는 우유를, B 가게에는 계란을 써요.',
                      steps=[SEPARATE]),
             ]),
        dict(title='이미지는 레이어로 쌓여요', objectives=['COPY·RUN으로 파일 시스템이 쌓이고, 앞 단계의 입력 변경이 뒤 단계 캐시에도 영향을 준다는 것을 빌드 결과로 확인해요.'],
             units=[dict(title='바뀐 줄부터 다시 만들어요', objectives=['자주 바뀌는 파일을 뒤에 두면 앞 레이어의 캐시를 다시 쓴다는 것을 확인해요.'],
                         premise='가게 이미지를 Dockerfile로 만들어요. 준비 단계(RUN)는 3초 걸리고 준비완료를 찍어요. 메뉴(menu.txt)만 바꿔 두 번 빌드해요.',
                         steps=[CACHE])]),
        dict(title='최종 도전: 다시 빌드해도 남는 메모', objectives=['코드는 이미지에, 데이터는 볼륨에 두는 구성을 처음 보는 앱에 적용해요.'],
             units=[dict(title='코드는 이미지, 데이터는 볼륨', objectives=['이미지를 새로 빌드해 컨테이너를 바꿔도 데이터가 남게 구성해요.'],
                         premise='메모 앱 이미지는 add.sh(메모 더하기)와 show.sh(버전과 메모 보기)를 담아요. 메모를 쓰고 show.sh를 v2로 고쳐 다시 빌드한 뒤 메모를 읽어요.',
                         steps=[FINAL])]),
    ],
)

# The new beginner chapter precedes Compose while every published chapter/unit
# keeps its original identity. Existing task IDs are already keyed by slug.
from d0_cli_intro import chapter as cli_chapter
for index, existing_chapter in enumerate(LESSON['chapters']):
    existing_chapter['identity'] = f'c{index}'
LESSON['chapters'].insert(0, cli_chapter(BUSYBOX))
LESSON['audience'] = 'Docker를 처음 배우고 이미지와 컨테이너를 직접 실행해 보려는 학습자'
LESSON['description'] = '설치·버전이 다른 문제에서 시작해 pull·run으로 직접 실행해요. 실행 재료와 컨테이너 수명을 구별한 뒤 Compose·볼륨·빌드로 이어져요.'
LESSON['objectives'].insert(0, '컴퓨터마다 다른 설치·버전 문제를 설명하고 pull·run·ps·logs·exec·stop·start·rm을 직접 실행해요.')
LESSON['scope'].insert(0, '왜 Docker가 필요한가, 이미지와 레지스트리, CLI pull·run·ps·logs·exec·stop·start·rm, 그 다음 Compose로 실행 설정 기록')
LESSON['sources'].insert(0, ('https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/', '이미지와 실행 중인 컨테이너를 구별하고 같은 실행 재료를 공유하는 이유를 설명해요.', 'Docker 공식 개념 문서를 기준으로 실제 CLI에서 확인해요.'))
LESSON['sources'].insert(1, ('https://docs.docker.com/reference/cli/docker/container/run/', 'run은 이미지를 바탕으로 새 컨테이너를 만들고 프로세스를 실행해요.', 'Docker 공식 CLI 문서예요. 실제 엔진 상태와 식별자를 비교해요.'))
LESSON['brief'] = (
    '컴퓨터마다 다른 설치·버전 문제를 보고 이미지와 컨테이너를 직접 실행해요.',
    LESSON['brief'][1],
    ['왜 실행 환경을 묶는지 이해해요.', 'pull·run으로 시작하고 ps·logs·exec를 실행해요.',
     'stop·start·rm의 차이를 확인한 뒤 Compose로 옮겨요.', '컨테이너 수명·볼륨·빌드 캐시로 확장해요.',
     '다음 네트워크 수업 예고: nip.io의 여러 이름을 같은 루프백 IP에 연결하고 Nginx에서 요청을 나누는 흐름을 살펴볼 예정이에요.'],
    '실제 Docker 엔진을 써요. 실습 컨테이너만 관리하고 수업을 나가면 정리해요. 기본 호스트 포트를 점유하지 않아요.',
    '이미지를 받는 것과 프로그램을 켜는 것은 같은 일일까요?')
LESSON['chapters'][1]['units'][0]['steps'][0]['intro'].insert(0,
    '앞에서는 run에 이미지와 명령을 직접 썼어요. 이제 같은 실행 설정을 compose.yaml에 기록해요. services 아래에는 서비스 이름, image에는 이미지, command에는 실행할 명령을 써요. 터미널에서 docker compose up을 입력하면 Compose가 그 파일을 읽어 실행해요. 여러 실행 설정을 파일로 관리하는 단계예요.')
LESSON['chapters'][1]['units'][0]['steps'][0]['narration'].insert(0,
    ('say', '앞에서 쓴 run의 이미지와 실행 명령을 파일로 옮겨요. services 아래에 설정을 기록하고 Compose가 읽게 해요.',
     'text:앞에서는 run에 이미지와 명령을 직접 썼어요.'))
LESSON['chapters'][1]['units'][0]['steps'][0]['narration'].insert(1,
    ('say', 'image가 실행 재료이고 command가 시작할 명령이에요. Compose는 이 설정을 읽어 컨테이너를 만들어요.', 'code:services:'))
LESSON['verification'] = LESSON['verification'] + ['CLI 문제는 실제 PTY 터미널에 명령을 입력해 실제 Docker 출력과 채점을 확인해요(tests/docker_cli_terminal.rs).']
