"""D1 이미지와 컨테이너: 프로세스로서의 컨테이너, 쓰기 레이어, 볼륨, 빌드 캐시 (실제 Docker 엔진).

Every run is the app's own `mq3lab-…` Compose project (src/docker_lab.rs). lab.sh is the authored
observation script: it drives the real engine and prints only what it observed. The learner first
edits commands.sh for CLI experiments, then compose.yaml or the Dockerfile. Nothing is simulated.
"""
from common import START_NEW, START_PREV, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT

BUSYBOX = 'busybox:1.36@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662'

DOCKER_GRADING = [
    '제출한 파일로 실제 Docker 엔진에서 실습 스크립트(lab.sh)를 실행하고, 스크립트가 엔진에서 읽은 결과를 정답 출력과 비교해요.',
    '준비 자료(메모·메뉴)를 바꿔 한 번 더 실행해요. 출력만 맞춘 파일은 통과하지 못해요.',
    '시작 파일은 실패하고, 흔한 오해에 맞춘 답도 실패하는지 기록된 오답으로 확인해요.',
]
DOCKER_RESET = ['실행마다 앱이 새 실습 프로젝트(mq3lab-…)를 만들고, 끝나면 그 프로젝트의 컨테이너·네트워크·볼륨·빌드 이미지만 지워요.',
                '그래서 앞 실행에서 남긴 데이터가 다음 판정을 바꾸지 않아요. 「다시 만들어도 남는가」는 한 번의 실행 안에서 실제로 지우고 다시 만들어 확인해요.',
                '내 컴퓨터에 원래 있던 컨테이너·볼륨·이미지는 건드리지 않아요.']
DOCKER_NARRATION = ['수정 전 실행 → 엔진이 보여 준 결과 읽기 → 고칠 한 곳 → 다시 실행해 비교해요.',
                    '「조심하세요」는 그 스텝에서 실제로 하기 쉬운 실수에만 써요.']
DOCKER_VERIFY = ['실제 MQ 채점기와 실제 Docker 엔진으로 정답 통과·시작 파일 실패·기록된 오답 거절·다른 정답 허용을 확인해요(tests/lesson-cases).',
                 '해설의 실행 결과는 실제 실행 기록과 비교해요. Windows(Docker Desktop)에서 확인했고, macOS는 같은 스크립트를 쓰지만 이 기록에 포함하지 않아요.']
STRATEGY = '각 스텝은 먼저 실행해 엔진이 보여 주는 실제 상태를 봐요. 원인을 찾은 뒤 표시한 한 곳만 고치고 다시 실행해요. Docker Desktop이 켜져 있어야 해요.'

TODO_DOCKER_BEFORE = '코드 실행 버튼을 눌러 고치기 전 결과를 확인하세요. 처음에는 이미지를 내려받느라 조금 걸려요.'

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
LAB1 = """# 실습 스크립트: 컨테이너를 띄우고 3초 뒤 엔진이 보는 상태를 읽어요.
set -e
docker compose up -d memo
sleep 3
state=$(docker compose ps -a --format '{{.State}}' memo)
echo "상태: $state"
# 시작 전 종료된 작업의 로그 유무는 경합이라 정답이나 관찰 근거로 고정하지 않아요.
if [ "$state" = running ]; then
  echo "로그: $(docker compose logs --no-log-prefix memo | head -n 1)"
fi
"""

# ---------------------------------------------------------------- unit 2: 쓰기 레이어와 볼륨
MEMO_READ = """read_memo() {
  # 컨테이너 안의 /memo/list.txt를 한 줄로 읽어요. 파일이 없으면 (없음)이에요.
  local text
  text=$(docker compose exec -T "$1" sh -c 'cat /memo/list.txt 2>/dev/null' | tr '\\n' ' ' | sed 's/ $//')
  echo "${text:-(없음)}"
}
"""
LAB2 = """# 실습 스크립트: 메모를 쓰고, 재시작·다시 만들기·down·down -v 뒤에 남는지 읽어요.
set -e
""" + MEMO_READ + """docker compose up -d memo
while IFS= read -r word || [ -n "$word" ]; do
  [ -n "$word" ] && docker compose exec -T memo sh -c 'mkdir -p /memo && printf "%s\\n" "$1" >> /memo/list.txt' sh "$word" </dev/null
done < memos.txt
docker compose restart -t 1 memo
echo "재시작 뒤: $(read_memo memo)"
docker compose up -d --force-recreate -t 1 memo
echo "다시 만든 뒤: $(read_memo memo)"
docker compose down -t 1
docker compose up -d memo
echo "down 뒤: $(read_memo memo)"
docker compose down -v -t 1
docker compose up -d memo
echo "down -v 뒤: $(read_memo memo)"
"""
S2_START = f"""# 메모를 기억하는 컨테이너예요. 메모는 /memo/list.txt에 써요.
services:
  memo:
    image: {BUSYBOX}
    command: ["sleep", "3600"]
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

LAB3 = """# 실습 스크립트: 두 가게가 각자 메모를 쓰고, 다시 만든 뒤에도 각자 남는지 읽어요.
set -e
""" + MEMO_READ + """docker compose up -d
while IFS= read -r word || [ -n "$word" ]; do
  [ -n "$word" ] && docker compose exec -T shop_a sh -c 'mkdir -p /memo && printf "%s\\n" "$1" >> /memo/list.txt' sh "$word" </dev/null
done < memos.txt
docker compose exec -T shop_b sh -c "mkdir -p /memo && echo 계란 >> /memo/list.txt"
echo "A 가게: $(read_memo shop_a)"
echo "B 가게: $(read_memo shop_b)"
docker compose up -d --force-recreate -t 1
echo "다시 만든 뒤 A 가게: $(read_memo shop_a)"
echo "다시 만든 뒤 B 가게: $(read_memo shop_b)"
"""
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

# ---------------------------------------------------------------- unit 3: 이미지는 레이어로 쌓여요
LAB4 = """# 실습 스크립트: 두 번 빌드해요. 두 번째 빌드 전에는 메뉴 파일만 바꿔요.
set -e
docker compose build --build-arg "MQ3_CACHE_SEED=$MQ3_PROJECT" shop > build1.txt 2>&1 || { cat build1.txt >&2; exit 1; }
first=$(grep -c '준비완료' build1.txt || true)
echo "빵" >> menu.txt
docker compose build --build-arg "MQ3_CACHE_SEED=$MQ3_PROJECT" shop > build2.txt 2>&1 || { cat build2.txt >&2; exit 1; }
second=$(grep -c '준비완료' build2.txt || true)
[ "$first" -gt 0 ] && echo "첫 빌드: 준비 단계 실행" || echo "첫 빌드: 준비 단계 캐시 사용"
[ "$second" -gt 0 ] && echo "메뉴만 바꾼 두 번째 빌드: 준비 단계 다시 실행" || echo "메뉴만 바꾼 두 번째 빌드: 준비 단계 캐시 사용"
echo "메뉴: $(docker compose run --rm -T shop | tr '\\n' ' ' | sed 's/ $//')"
"""
COMPOSE4 = """# shop 서비스의 이미지는 이 폴더의 Dockerfile로 만들어요.
services:
  shop:
    build: .
"""
S4_START = f"""# 가게 이미지를 만드는 Dockerfile이에요. COPY·RUN은 파일 시스템 레이어를 만들어요.
FROM {BUSYBOX}
# 제공 설정: 이전 실습의 빌드 캐시와 구분해요. 같은 실행의 두 빌드는 같은 값을 써요.
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
LAB5 = """# 실습 스크립트: 메모를 쓰고, 앱 코드를 고쳐 이미지를 다시 빌드한 뒤에도 메모가 남는지 읽어요.
set -e
docker compose up -d --build app > /dev/null 2>&1 || docker compose up -d --build app
while IFS= read -r word || [ -n "$word" ]; do
  [ -n "$word" ] && docker compose exec -T app sh /app/add.sh "$word" </dev/null
done < memos.txt
echo "처음: $(docker compose exec -T app sh /app/show.sh)"
# 앱 코드를 고쳐요(새 버전 표시). 이미지를 다시 빌드하고 컨테이너를 새로 만들어요.
sed -i 's/v1/v2/' show.sh
docker compose up -d --build -t 1 app > /dev/null 2>&1
echo "앱을 고쳐 다시 빌드한 뒤: $(docker compose exec -T app sh /app/show.sh)"
docker compose down -t 1 > /dev/null 2>&1
docker compose up -d app > /dev/null 2>&1
echo "down 뒤: $(docker compose exec -T app sh /app/show.sh)"
"""
ADD5 = """# 메모 하나를 /data/memo.txt 끝에 더해요.
mkdir -p /data
echo "$1" >> /data/memo.txt
"""
SHOW5 = """# 메모 앱 버전과 지금까지의 메모를 한 줄로 보여 줘요.
memo=$(cat /data/memo.txt 2>/dev/null | tr '\\n' ' ' | sed 's/ $//')
echo "[v1] ${memo:-(없음)}"
"""
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


def step(**fields):
    fields.setdefault('language', 'docker')
    fields.setdefault('docker_images', [BUSYBOX])
    return fields


LESSON = dict(
    key='docker-image-container', folder='docker_image_container', pilot='리', revision=3,
    title='이미지와 컨테이너 · 지워도 남는 것과 사라지는 것',
    category='docker', category_title='Docker', track=None,
    category_evidence='실제 Docker 엔진으로 컨테이너·볼륨·이미지를 다루는 수업이에요.',
    track_evidence='트랙 없음: 「기본」은 2026-10-25에 있던 수업에만 붙인 사용자 결정이고, 새 수업의 트랙(필수·고급)은 사용자 승인 없이 정하지 않아요.',
    audience='docker run을 따라 해 봤지만 컨테이너를 지우면 무엇이 사라지는지 설명하기 어려운 학습자',
    prerequisites=['터미널에서 명령을 실행하고 결과를 읽을 수 있어요.', 'Docker Desktop을 설치하고 켤 수 있어요(설치는 학습자가 해요).'],
    objectives=['컨테이너는 이미지로 시작한 프로세스이고, 첫 프로세스(PID 1)가 끝나면 컨테이너도 끝난다는 것을 실제 상태로 설명해요.',
                '재시작·다시 만들기·down·down -v에서 쓰기 레이어와 볼륨의 데이터가 각각 어떻게 되는지 관찰하고, 남아야 할 데이터를 볼륨에 두는 구성을 직접 써요.',
                '이미지가 레이어로 쌓이고 바뀐 줄부터 다시 만든다는 것을 빌드 결과로 확인하고, 캐시를 살리는 순서로 Dockerfile을 고쳐요.'],
    scope=['PID 1과 컨테이너 수명, 같은 이미지의 독립 컨테이너, 쓰기 레이어, 이름 있는 볼륨과 공유, restart·force-recreate·down·down -v, Dockerfile 레이어와 빌드 캐시, 코드(이미지)와 데이터(볼륨)의 분리'],
    out_of_scope=['네트워크와 포트(다음 수업 docker-network-ports)', 'DB 컨테이너(docker-compose-db)', '레지스트리에 이미지 올리기', '멀티 스테이지 빌드·이미지 크기 줄이기'],
    sources=[
        ('https://docs.docker.com/engine/containers/multi-service_container/', '컨테이너의 주 실행 프로세스는 ENTRYPOINT·CMD이고, 그 프로세스가 끝나면 컨테이너도 멈춰요.', 'Docker 공식 문서예요. 실제 엔진의 상태(exited·running)로 확인해요.'),
        ('https://docs.docker.com/engine/storage/', '컨테이너 안에서 만든 파일은 쓰기 레이어에 저장되고 컨테이너를 지우면 함께 사라져요. 볼륨은 컨테이너와 따로 남아요.', 'Docker 공식 문서예요. 다시 만들기·down·down -v로 실제 확인해요.'),
        ('https://docs.docker.com/build/cache/', '한 레이어가 바뀌면 그 뒤의 레이어도 모두 다시 만들어요. 자주 바뀌는 것을 뒤에 둬요.', 'Docker 공식 문서예요. 실제 빌드 출력으로 확인해요.'),
        ('https://docs.docker.com/reference/cli/docker/compose/down/', 'down은 컨테이너와 네트워크를 지우고, -v를 붙이면 이름 있는 볼륨도 지워요.', 'Docker 공식 CLI 문서예요. 실제 실행으로 확인해요.'),
    ],
    description='메모를 기억하는 작은 컨테이너로, 컨테이너의 수명·쓰기 레이어·볼륨·이미지 레이어를 차례로 고쳐요.',
    brief=('컨테이너가 프로세스라는 것, 쓰기 레이어와 볼륨, 이미지 레이어와 빌드 캐시를 실제 Docker로 다뤄요.',
           '앱 이미지를 고쳐 다시 빌드하고 컨테이너를 새로 만들어도 메모가 남게 구성해요.',
           ['컨테이너가 바로 끝나는 이유를 PID 1로 설명해요.', '지워지는 데이터와 남는 데이터를 구별해요.', '바뀐 줄부터 다시 빌드되는 것을 봐요.'],
           '실제 Docker 엔진에서 실행해요. Docker Desktop이 켜져 있어야 하고, 실행마다 새 실습 프로젝트를 만들고 지워요.',
           '컨테이너를 지우면 무엇이 사라지고 무엇이 남을까요?'),
    representative=dict(slug='final-memo-app', expected_action='앱이 메모를 쓰는 폴더(/data)에 이름 있는 볼륨을 연결해요.',
                        acceptance='메모를 쓴 뒤 이미지를 다시 빌드해 컨테이너를 새로 만들어도, down 뒤에도 메모가 남고 새 앱 버전이 보여야 해요.',
                        reset='준비 파일로 돌아가고, 실행마다 새 실습 프로젝트에서 시작해요.',
                        narration='다시 빌드한 뒤 메모가 사라지는 것을 보고, add.sh가 쓰는 폴더를 찾아 볼륨을 연결한 뒤 다시 실행해요.'),
    grading=DOCKER_GRADING, reset=DOCKER_RESET, narration_policy=DOCKER_NARRATION, verification=DOCKER_VERIFY,
    learning_strategy=STRATEGY,
    chapters=[
        dict(title='컨테이너는 프로세스예요', objectives=['컨테이너가 실행 중인지 아닌지는 첫 프로세스가 정한다는 것을 실제 상태로 확인해요.'],
             units=[
                 dict(title='PID 1이 끝나면 컨테이너도 끝나요', objectives=['컨테이너의 첫 프로세스와 그 프로세스가 띄운 다른 프로세스를 구별해요.'],
                      premise='메모 서버 컨테이너 하나를 띄워요. 실습 스크립트(lab.sh)가 3초 뒤 엔진에 상태를 물어봐요.',
                      steps=[
                          step(slug='pid1-lifetime', title='메모 서버 컨테이너가 계속 실행되게 하세요',
                               objectives=['명령 끝의 &가 PID 1을 바로 끝나게 만든다는 것을 확인하고, 컨테이너가 계속 실행되게 고쳐요.'],
                               start=START_NEW,
                               intro=['`command`는 시작 메시지와 메모 서버(여기서는 `sleep 3600`) 실행을 지시해요. 그런데 실행하면 상태가 `exited`로 나와요. 서버를 기다리지 않고 컨테이너가 끝났어요.'],
                               know='컨테이너는 이미지로 시작한 프로세스예요. `command`로 시작한 첫 프로세스가 PID 1이고, PID 1이 끝나면 컨테이너도 끝나요. 셸에서 명령 끝의 `&`는 그 명령을 뒤에서 돌리고 셸은 바로 다음으로 넘어가요.',
                               todo=[TODO_DOCKER_BEFORE + ' `상태:` 줄을 보고, 실행 중이면 `로그:` 줄도 읽으세요.',
                                     '`command` 줄에서 sh가 바로 끝나지 않게 고치세요.',
                                     TODO_RUN_AFTER, TODO_SUBMIT],
                               entry_file='compose.yaml', files={'lab.sh': LAB1},
                               starter=S1_START, solution=S1_SOLUTION,
                               tests=[('', '상태: running\n로그: 메모 서버 시작')],
                               success='3초 뒤에도 컨테이너가 running이고, 시작 메시지가 로그에 있어요.',
                               complexity=dict(prior='터미널에서 명령을 실행해 봤어요.', new='PID 1과 컨테이너의 수명',
                                               changed='첫 프로세스가 끝나지 않게 함', evidence='엔진이 보고한 상태(running·exited)와 로그', lines=1, services=1),
                               narration=[
                                   ('say', '서버를 띄웠는데 컨테이너가 끝나 버리는 문제예요.', 'text:그런데 실행하면 상태가 `exited`로 나와요.'),
                                   ('run',),
                                   ('say', '상태는 exited예요. 첫 프로세스가 백그라운드 작업을 기다리지 않고 끝났어요. 시작 로그도 남기기 전에 종료될 수 있어요.', 'output'),
                                   ('say', '끝의 &가 sleep을 뒤로 보내요. 그러면 sh는 할 일이 없어서 바로 끝나요. sh가 PID 1이라 컨테이너도 끝나요.', 'code:sleep 3600 &'),
                                   ('patch', *FIX1, '&를 빼서 sh가 sleep을 기다리게 해요.'),
                                   ('run',),
                                   ('say', '이제 3초 뒤에도 running이에요. PID 1인 sh가 sleep을 기다리는 동안 컨테이너가 살아 있어요.', 'output'),
                                   ('say', '조심하세요. 이 셸 명령에서 &를 붙이면 셸이 기다리지 않고 끝나요. 서버가 직접 PID 1이 되거나 PID 1이 서버를 기다려야 컨테이너가 유지돼요.', 'text:셸에서 명령 끝의 `&`는 그 명령을 뒤에서 돌리고 셸은 바로 다음으로 넘어가요.'),
                                   ('submit',)],
                               review={'조심하세요. 이 셸 명령에서 &를 붙이면 셸이 기다리지 않고 끝나요. 서버가 직접 PID 1이 되거나 PID 1이 서버를 기다려야 컨테이너가 유지돼요.':
                                       '시작 파일이 바로 그 실수(sleep 3600 &)이고, 실제 엔진에서 exited를 앞 실행에서 봤어요.'},
                               accepts=[([('"echo 메모 서버 시작 && sleep 3600"', '"echo 메모 서버 시작 && exec sleep 3600"')], 'exec로 sh를 sleep으로 바꿔도 PID 1이 계속 살아 있어요.'),
                                        ([('"echo 메모 서버 시작 && sleep 3600"', '"echo 메모 서버 시작; tail -f /dev/null"')], '끝나지 않는 다른 앞 프로세스도 같은 원리예요.')],
                               rejects=[([('"echo 메모 서버 시작 && sleep 3600"', '"echo 메모 서버 시작 && sleep 1"')], '1초 뒤 PID 1이 끝나 3초 뒤에는 exited예요.'),
                                        ([('"echo 메모 서버 시작 && sleep 3600"', '"sleep 3600 & echo 메모 서버 시작"')], 'sleep을 뒤로 보내고 echo가 끝나면 sh가 끝나요.')]),
                      ]),
             ]),
        dict(title='지워지는 데이터와 남는 데이터', objectives=['컨테이너의 쓰기 레이어와 볼륨을 구별하고, 남아야 할 데이터를 볼륨에 둬요.'],
             units=[
                 dict(title='다시 만들면 쓰기 레이어는 새것이에요', objectives=['restart는 같은 컨테이너, force-recreate는 새 컨테이너라는 것을 메모로 확인해요.'],
                      premise='메모 컨테이너가 /memo/list.txt에 메모를 써요. 실습 스크립트가 memos.txt의 메모를 쓰고, 재시작·다시 만들기·down·down -v 뒤에 읽어요.',
                      steps=[
                          step(slug='volume-survives-recreate', title='다시 만들어도 메모가 남게 볼륨을 연결하세요',
                               objectives=['컨테이너를 다시 만들면 쓰기 레이어의 파일이 사라진다는 것을 보고, 이름 있는 볼륨을 연결해 남게 해요.'],
                               start=START_NEW,
                               intro=['실행하면 재시작 뒤에는 메모가 있는데, 다시 만든 뒤에는 `(없음)`이에요. 같은 이미지, 같은 설정인데 메모가 사라졌어요.'],
                               know='컨테이너 안에서 쓴 파일은 그 컨테이너의 쓰기 레이어에 저장돼요. `restart`는 같은 컨테이너를 다시 켜요. `up --force-recreate`와 `down`은 컨테이너를 지우고 이미지에서 새로 만들어요. 볼륨은 컨테이너 밖에서 Docker가 관리하는 저장소이고 `down -v`를 해야 지워져요.',
                               todo=[TODO_DOCKER_BEFORE + ' 네 줄에서 메모가 어디서 사라지는지 보세요.',
                                     '`고칠 곳` 자리에 `memo` 볼륨을 `/memo`에 연결하는 `volumes`를 쓰고, 파일 끝에 볼륨 선언을 더하세요.',
                                     TODO_RUN_AFTER, TODO_SUBMIT],
                               entry_file='compose.yaml', files={'lab.sh': LAB2, 'memos.txt': '우유\n빵\n'},
                               variations=[dict(files={'memos.txt': '사과\n귤\n계란\n'},
                                                expected='재시작 뒤: 사과 귤 계란\n다시 만든 뒤: 사과 귤 계란\ndown 뒤: 사과 귤 계란\ndown -v 뒤: (없음)')],
                               starter=S2_START, solution=S2_SOLUTION,
                               tests=[('', '재시작 뒤: 우유 빵\n다시 만든 뒤: 우유 빵\ndown 뒤: 우유 빵\ndown -v 뒤: (없음)')],
                               success='재시작·다시 만들기·down 뒤에 메모가 남고, 볼륨까지 지우는 down -v 뒤에만 사라져요.',
                               complexity=dict(prior='컨테이너가 프로세스라는 것을 확인했어요.', new='쓰기 레이어와 이름 있는 볼륨',
                                               changed='/memo에 볼륨 연결', evidence='네 시점의 메모 내용', lines=3),
                               narration=[
                                   ('say', '같은 설정으로 다시 만들었는데 메모가 사라지는 문제예요.', 'text:같은 이미지, 같은 설정인데 메모가 사라졌어요.'),
                                   ('run',),
                                   ('say', '재시작 뒤에는 우유 빵이 있어요. 다시 만든 뒤부터는 없음이에요.', 'output'),
                                   ('say', '재시작은 같은 컨테이너라 쓰기 레이어가 그대로예요. 다시 만들면 이미지에서 새 컨테이너가 생겨요. 이미지에는 메모가 없어요.', 'text:`restart`는 같은 컨테이너를 다시 켜요.'),
                                   ('say', '지금 이 서비스에는 volumes가 없어요. /memo는 컨테이너의 쓰기 레이어에 있어요.', 'code:# 고칠 곳: 지금 /memo는 컨테이너 자기 파일 시스템(쓰기 레이어)에 있어요.'),
                                   ('patch', *FIX2, '/memo에 이름 있는 볼륨을 연결하고, 파일 끝에 볼륨을 선언해요.'),
                                   ('run',),
                                   ('say', '다시 만든 뒤에도, down 뒤에도 우유 빵이 남아요. 새 컨테이너가 같은 볼륨을 연결했어요.', 'output'),
                                   ('say', 'down -v 뒤에만 없음이에요. -v가 볼륨까지 지웠어요.', 'output'),
                                   ('say', '조심하세요. 처음 상태로 돌리려고 down -v를 쓰면 볼륨의 데이터도 지워져요. 데이터를 지킬 때는 -v 없이 down 해요.', 'text:볼륨은 컨테이너 밖에서 Docker가 관리하는 저장소이고 `down -v`를 해야 지워져요.'),
                                   ('submit',)],
                               review={'조심하세요. 처음 상태로 돌리려고 down -v를 쓰면 볼륨의 데이터도 지워져요. 데이터를 지킬 때는 -v 없이 down 해요.':
                                       '실제 실행 출력의 마지막 줄(down -v 뒤: (없음))이 그 결과예요. 앞 줄(down 뒤)과 대비돼요.'},
                               accepts=[([('      - memo:/memo', '      - type: volume\n        source: memo\n        target: /memo')], '긴 문법으로 같은 볼륨을 연결해도 같아요.')],
                               rejects=[([('      - memo:/memo', '      - memo:/data')], '볼륨을 다른 폴더에 연결하면 /memo는 여전히 쓰기 레이어예요.'),
                                        ([('      - memo:/memo', '      - ./memo:/memo')], '실습 폴더를 직접 연결(바인드 마운트)하면 down -v로도 지워지지 않아요. 이 스텝은 Docker가 관리하는 볼륨을 써요.')]),
                      ]),
                 dict(title='볼륨은 이름으로 공유돼요', objectives=['같은 이미지의 두 컨테이너가 각자 쓰기 레이어를 갖고, 같은 이름의 볼륨은 함께 쓴다는 것을 확인해요.'],
                      premise='같은 busybox 이미지로 두 가게(shop_a, shop_b)의 메모 컨테이너를 띄워요. A 가게에는 memos.txt의 메모를, B 가게에는 계란을 써요.',
                      steps=[
                          step(slug='separate-volumes', title='두 가게가 각자 메모를 갖게 하세요',
                               objectives=['볼륨 이름이 같으면 두 컨테이너가 같은 데이터를 본다는 것을 확인하고, 가게마다 볼륨을 나눠요.'],
                               start=START_NEW,
                               intro=['실행하면 A 가게와 B 가게의 메모가 똑같이 나와요. B 가게에는 계란만 써야 하는데 A의 메모도 섞여 있어요.'],
                               know='같은 이미지로 만든 컨테이너도 쓰기 레이어는 저마다 따로예요. 볼륨은 이름으로 찾아요. 두 서비스가 같은 볼륨 이름을 연결하면 같은 저장소를 함께 써요.',
                               todo=[TODO_DOCKER_BEFORE + ' A와 B의 메모를 비교하세요.',
                                     'B 가게가 자기 볼륨 `memo_b`를 쓰게 고치고, 파일 끝의 볼륨 선언에도 더하세요.',
                                     TODO_RUN_AFTER, TODO_SUBMIT],
                               entry_file='compose.yaml', files={'lab.sh': LAB3, 'memos.txt': '우유\n빵\n'},
                               variations=[dict(files={'memos.txt': '사과\n'},
                                                expected='A 가게: 사과\nB 가게: 계란\n다시 만든 뒤 A 가게: 사과\n다시 만든 뒤 B 가게: 계란')],
                               starter=S3_START, solution=S3_SOLUTION,
                               tests=[('', 'A 가게: 우유 빵\nB 가게: 계란\n다시 만든 뒤 A 가게: 우유 빵\n다시 만든 뒤 B 가게: 계란')],
                               success='두 가게의 메모가 섞이지 않고, 다시 만든 뒤에도 각자 남아요.',
                               complexity=dict(prior='볼륨을 연결해 다시 만들어도 데이터가 남게 했어요.', new='볼륨 이름으로 공유되는 저장소',
                                               changed='B 가게의 볼륨 이름', evidence='두 가게의 메모', lines=2),
                               narration=[
                                   ('say', '두 가게의 메모가 섞이는 문제예요.', 'text:B 가게에는 계란만 써야 하는데 A의 메모도 섞여 있어요.'),
                                   ('run',),
                                   ('say', 'A도 B도 우유 빵 계란이에요.', 'output'),
                                   ('say', '두 서비스가 모두 memo_a를 /memo에 연결했어요. 컨테이너는 둘이지만 저장소는 하나예요.', 'code:# 고칠 곳: B 가게가 연결한 볼륨이에요.'),
                                   ('patch', *FIX3, 'B 가게에 자기 볼륨 memo_b를 연결하고 선언해요.'),
                                   ('run',),
                                   ('say', 'A는 우유 빵, B는 계란이에요. 다시 만든 뒤에도 각자 남아요.', 'output'),
                                   ('say', '같은 이미지에서 시작해도 데이터는 어느 볼륨을 연결했는지가 정해요.', 'text:볼륨은 이름으로 찾아요.'),
                                   ('submit',)],
                               review={'같은 이미지에서 시작해도 데이터는 어느 볼륨을 연결했는지가 정해요.':
                                       '같은 이미지와 다른 볼륨이라는 조건을 두 가게 출력과 연결해요. 이미지가 같다는 것만으로 데이터 공유가 정해지지 않아요.'},
                               rejects=[([('      - memo_b:/memo\n', '')], 'B의 볼륨을 빼면 처음엔 계란이 보여도, 다시 만든 뒤 사라져요.')]),
                      ]),
             ]),
        dict(title='이미지는 레이어로 쌓여요', objectives=['COPY·RUN으로 파일 시스템이 쌓이고, 앞 단계의 입력 변경이 뒤 단계 캐시에도 영향을 준다는 것을 빌드 결과로 확인해요.'],
             units=[
                 dict(title='바뀐 줄부터 다시 만들어요', objectives=['자주 바뀌는 파일을 뒤에 두면 앞 레이어의 캐시를 다시 쓴다는 것을 확인해요.'],
                      premise='가게 이미지를 Dockerfile로 만들어요. 준비 단계(RUN)는 3초 걸리고 `준비완료`를 찍어요. 실습 스크립트는 메뉴(menu.txt)만 바꿔 두 번 빌드해요.',
                      steps=[
                          step(slug='layer-cache-order', title='메뉴만 바꿨을 때 준비 단계를 다시 하지 않게 하세요',
                               objectives=['앞 레이어가 바뀌면 그 뒤의 레이어를 모두 다시 만든다는 것을 보고, 자주 바뀌는 COPY를 뒤로 옮겨요.'],
                               start=START_NEW,
                               intro=['실행하면 메뉴 한 줄만 바꾼 두 번째 빌드도 3초 걸리는 준비 단계를 다시 해요.'],
                               know='`COPY`와 `RUN`은 이미지의 파일 시스템을 바꾸는 레이어를 만들어요. `CMD` 같은 명령은 실행 설정을 기록해요. 입력이 같은 단계는 캐시를 쓸 수 있어요. `COPY`는 복사할 파일 내용도 입력이에요. 앞 단계가 바뀌면 뒤 단계도 캐시를 새로 판단해요.',
                               todo=[TODO_DOCKER_BEFORE + ' 두 번째 빌드 줄을 읽으세요.',
                                     '`COPY menu.txt .` 줄과 `RUN` 줄의 순서를 바꾸세요.',
                                     TODO_RUN_AFTER, TODO_SUBMIT],
                               entry_file='Dockerfile', files={'lab.sh': LAB4, 'compose.yaml': COMPOSE4, 'menu.txt': '우유\n'},
                               variations=[dict(files={'menu.txt': '커피\n차\n'},
                                                expected='첫 빌드: 준비 단계 실행\n메뉴만 바꾼 두 번째 빌드: 준비 단계 캐시 사용\n메뉴: 커피 차 빵')],
                               starter=S4_START, solution=S4_SOLUTION,
                               tests=[('', '첫 빌드: 준비 단계 실행\n메뉴만 바꾼 두 번째 빌드: 준비 단계 캐시 사용\n메뉴: 우유 빵')],
                               success='메뉴만 바뀐 두 번째 빌드는 준비 단계를 캐시로 건너뛰고, 이미지에는 새 메뉴가 들어 있어요.',
                               complexity=dict(prior='이미지에서 컨테이너를 만들어 봤어요.', new='레이어와 빌드 캐시',
                                               changed='COPY와 RUN의 순서', evidence='두 번째 빌드에서 준비 단계를 다시 했는지', lines=2),
                               narration=[
                                   ('say', '메뉴 한 줄만 바꿨는데 오래 걸리는 준비를 또 하는 문제예요.', 'text:실행하면 메뉴 한 줄만 바꾼 두 번째 빌드도 3초 걸리는 준비 단계를 다시 해요.'),
                                   ('run',),
                                   ('say', '두 번째 빌드도 준비 단계를 다시 실행했어요.', 'output'),
                                   ('say', '메뉴가 바뀌어 COPY 레이어가 달라졌어요. 그 뒤에 있는 RUN도 다시 만들어요.', 'code:COPY menu.txt .'),
                                   ('patch', *FIX4, '준비 단계를 먼저, 메뉴 복사를 뒤에 둬요.'),
                                   ('run',),
                                   ('say', '이제 두 번째 빌드는 준비 단계에 캐시를 써요. 메뉴는 우유 빵으로 새것이에요.', 'output'),
                                   ('say', '조심하세요. 파일이 필요한 RUN을 COPY 앞으로 옮기면 아직 그 파일이 없어요. 그 파일이 필요한 단계는 COPY 뒤에 둬요.', 'text:앞 단계가 바뀌면 뒤 단계도 캐시를 새로 판단해요.'),
                                   ('submit',)],
                               review={'조심하세요. 파일이 필요한 RUN을 COPY 앞으로 옮기면 아직 그 파일이 없어요. 그 파일이 필요한 단계는 COPY 뒤에 둬요.':
                                       '순서를 바꾸는 이 스텝에서 바로 생기는 다음 실수예요. RUN이 menu.txt를 쓰면 COPY 전이라 파일이 없어요. 이 RUN은 menu.txt를 쓰지 않아 순서를 바꿔도 돼요.'},
                               accepts=[([('COPY menu.txt .', 'COPY menu.txt /app/')], '절대 경로로 같은 곳에 복사해도 같아요.')],
                               rejects=[([('COPY menu.txt .', 'COPY menu.txt /tmp/')], '메뉴를 다른 곳에 복사하면 CMD가 /app/menu.txt를 찾지 못해요.')]),
                      ]),
             ]),
        dict(title='최종 도전: 다시 빌드해도 남는 메모', objectives=['코드는 이미지에, 데이터는 볼륨에 두는 구성을 처음 보는 앱에 적용해요.'],
             units=[
                 dict(title='코드는 이미지, 데이터는 볼륨', objectives=['이미지를 새로 빌드해 컨테이너를 바꿔도 데이터가 남게 구성해요.'],
                      premise='메모 앱 이미지는 add.sh(메모 더하기)와 show.sh(버전과 메모 보기)를 담아요. 실습 스크립트는 메모를 쓰고, show.sh를 v2로 고쳐 다시 빌드한 뒤, down 뒤에도 메모를 읽어요.',
                      steps=[
                          step(slug='final-memo-app', title='앱을 고쳐 다시 빌드해도 메모가 남게 하세요',
                               objectives=['앱이 데이터를 쓰는 경로를 코드에서 찾아 볼륨을 연결하고, 새 이미지와 남은 데이터를 함께 확인해요.'],
                               start=START_NEW,
                               intro=['실행하면 다시 빌드한 뒤 앱 버전은 v2로 바뀌는데 메모는 `(없음)`이에요. 앱을 고칠 때마다 메모가 사라지면 쓸 수 없어요.',
                                     'add.sh와 show.sh를 읽고, 메모가 실제로 어느 폴더에 저장되는지 찾으세요.'],
                               know='`up --build`는 이미지를 새로 만들고, 바뀐 이미지로 컨테이너를 새로 만들어요. 새 컨테이너는 새 쓰기 레이어에서 시작해요. 볼륨은 연결한 폴더의 데이터만 지켜요.',
                               todo=[TODO_DOCKER_BEFORE + ' 세 줄에서 메모와 버전을 비교하세요.',
                                     'add.sh가 메모를 쓰는 폴더를 찾으세요.',
                                     '`고칠 곳` 자리에 그 폴더에 이름 있는 볼륨을 연결하는 `volumes`를 쓰고, 파일 끝에 볼륨을 선언하세요.',
                                     TODO_RUN_AFTER, TODO_SUBMIT],
                               entry_file='compose.yaml',
                               files={'lab.sh': LAB5, 'Dockerfile': DOCKERFILE5, 'add.sh': ADD5, 'show.sh': SHOW5, 'memos.txt': '우유\n빵\n'},
                               variations=[dict(files={'memos.txt': '계란\n'},
                                                expected='처음: [v1] 계란\n앱을 고쳐 다시 빌드한 뒤: [v2] 계란\ndown 뒤: [v2] 계란')],
                               starter=S5_START, solution=S5_SOLUTION,
                               tests=[('', '처음: [v1] 우유 빵\n앱을 고쳐 다시 빌드한 뒤: [v2] 우유 빵\ndown 뒤: [v2] 우유 빵')],
                               success='다시 빌드한 뒤에는 v2가 보이고, 메모는 다시 빌드와 down 뒤에도 그대로 남아요.',
                               complexity=dict(prior='볼륨·공유·빌드 캐시를 각각 확인했어요.', new='', changed='앱의 데이터 폴더에 볼륨 연결',
                                               evidence='다시 빌드 전후와 down 뒤의 버전·메모', lines=3),
                               narration=[
                                   ('say', '앱을 고쳐 다시 빌드하면 메모가 사라지는 문제예요.', 'text:앱을 고칠 때마다 메모가 사라지면 쓸 수 없어요.'),
                                   ('run',),
                                   ('say', '처음엔 우유 빵이 있어요. 다시 빌드한 뒤에는 v2로 바뀌었지만 메모는 없음이에요.', 'output'),
                                   ('say', 'build 줄 때문에 up --build가 이미지를 새로 만들고, 그 이미지로 컨테이너도 새로 만들어요.', 'code:build: .'),
                                   ('say', 'add.sh는 메모를 /data/memo.txt에 써요. 이 폴더는 지금 쓰기 레이어에 있어요.', 'text:add.sh와 show.sh를 읽고, 메모가 실제로 어느 폴더에 저장되는지 찾으세요.'),
                                   ('patch', *FIX5, '/data에 memos 볼륨을 연결하고 선언해요.'),
                                   ('run',),
                                   ('say', '다시 빌드한 뒤에도 v2와 우유 빵이 함께 보여요. down 뒤에도 남아요.', 'output'),
                                   ('say', '이미지는 새것으로 바뀌었고, 메모는 볼륨에 있어서 그대로예요. 코드와 데이터가 다른 곳에 있어요.', 'text:볼륨은 연결한 폴더의 데이터만 지켜요.'),
                                   ('submit',)],
                               rejects=[([('      - memos:/data', '      - memos:/app')], '/app에 볼륨을 연결하면 메모는 여전히 쓰기 레이어에 있고, 볼륨이 앱 코드 폴더를 덮어 새 버전도 보이지 않아요.'),
                                        ([('      - memos:/data', '      - memos:/memo')], '앱이 쓰지 않는 폴더에 연결하면 메모는 지켜지지 않아요.')]),
                      ]),
             ]),
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
LESSON['reset'] = ['각 문제는 본문에서 알린 준비 상태로 시작해요. CLI 실습은 이 문제 소유 컨테이너만 되돌려요.',
    '대화형 실습 자원은 수업 동안 유지하고 수업을 나가면 정리해요. 제출 검사는 별도 공간에서 실행해요.',
    '기존 사용자의 컨테이너·볼륨과 학습 진도는 지우지 않아요.']
LESSON['chapters'][1]['units'][0]['steps'][0]['intro'].insert(0,
    '앞에서는 run에 이미지와 명령을 직접 썼어요. 이제 같은 실행 설정을 compose.yaml에 기록해요. services 아래에는 서비스 이름, image에는 이미지, command에는 실행할 명령을 써요. lab.sh가 그 파일로 docker compose up을 실행해요. 여러 실행 설정을 파일로 관리하는 단계예요.')
LESSON['chapters'][1]['units'][0]['steps'][0]['narration'].insert(0,
    ('say', '앞에서 쓴 run의 이미지와 실행 명령을 파일로 옮겨요. services 아래에 설정을 기록하고 Compose가 읽게 해요.',
     'text:앞에서는 run에 이미지와 명령을 직접 썼어요.'))
LESSON['chapters'][1]['units'][0]['steps'][0]['narration'].insert(1,
    ('say', 'image가 실행 재료이고 command가 시작할 명령이에요. Compose는 이 설정을 읽어 컨테이너를 만들어요.', 'code:services:'))
