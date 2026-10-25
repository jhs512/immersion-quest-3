"""Compose DB: address boundaries, durable storage, first-init versus migration."""
from docker_common import step, lesson
from sql_lab import PG, unit

BASE=f'''services:
  db:
    image: {PG}
    environment:
      POSTGRES_PASSWORD: lab
      POSTGRES_DB: lab
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "lab"]
      interval: 1s
      timeout: 1s
      retries: 60
  app:
    image: {PG}
    environment:
      PGPASSWORD: lab
    command: ["psql", "-h", "localhost", "-U", "postgres", "-d", "lab", "-X", "-qAt", "-c", "SELECT 'connected'"]
'''
FIX1=BASE.replace('"localhost"','"db"')
LAB1='''set -e
docker compose up -d --wait db >/dev/null 2>&1
if result=$(docker compose run --rm -T app 2>/dev/null); then echo "$result"; else echo 'connection failed'; fi
'''
S1=step(slug='db-address',title='app이 db 서비스의 데이터베이스에 접속하게 하세요',
    concept='데이터베이스 연결 주소는 클라이언트가 실행되는 위치에 따라 달라져요.',
    intro='db 컨테이너에 PostgreSQL이 있고 app 컨테이너에서 SQL 클라이언트를 실행해요. 사용자 PC의 DB는 사용하지 않아요.',
    know='app의 localhost에는 PostgreSQL이 없어요. 같은 네트워크의 db 서비스 이름과 내부 포트를 사용하세요. 이 단계는 PC에 DB 포트를 공개하지 않아요.',
    starter=BASE,solution=FIX1,script=LAB1,images=[PG],expected='connected',
    first='DB의 건강 검사는 통과했지만 app의 연결은 실패했어요. app이 자기 localhost로 접속했어요.',
    result='app이 db 서비스에 연결해 실제 SQL 응답 connected를 받았어요.',
    caution='조심하세요. PC에 이미 설치된 PostgreSQL을 찾는 과제가 아니에요. 준비된 실습 DB의 서비스 이름을 사용하세요.')

WRONG=FIX1.replace('    healthcheck:', '    volumes: ["data:/data"]\n    healthcheck:')+'volumes:\n  data:\n'
RIGHT=WRONG.replace('data:/data','data:/var/lib/postgresql')
LAB2='''set -e
sql() { docker compose exec -T db psql -U postgres -d lab -X -qAt -v ON_ERROR_STOP=1 -c "$1" </dev/null; }
read_count() { sql 'SELECT count(*) FROM memo' 2>/dev/null || echo '표 없음'; }
docker compose up -d --wait db >/dev/null 2>&1
sql 'CREATE TABLE memo(title TEXT); INSERT INTO memo VALUES(\'milk\')'
echo "처음:$(read_count)"
docker compose restart -t 1 db >/dev/null 2>&1
docker compose up -d --wait db >/dev/null 2>&1
echo "재시작:$(read_count)"
docker compose up -d --force-recreate --wait -t 1 db >/dev/null 2>&1
echo "재생성:$(read_count)"
docker compose down -t 1 >/dev/null 2>&1
docker compose up -d --wait db >/dev/null 2>&1
echo "down:$(read_count)"
'''
# Use a double-quoted shell SQL argument so its SQL quotes survive unchanged.
LAB2=LAB2.replace("sql 'CREATE TABLE memo(title TEXT); INSERT INTO memo VALUES('milk')'", 'sql "CREATE TABLE memo(title TEXT); INSERT INTO memo VALUES(\'milk\')"')
S2=step(slug='db-volume',title='DB 컨테이너를 다시 만들어도 메모가 남게 하세요',
    concept='볼륨은 데이터베이스가 실제로 저장하는 경로에 연결해야 해요.',
    intro='볼륨 data가 있지만 /data에 붙어 있어요. 이 PostgreSQL 18 이미지가 저장하는 경로와 달라요.',
    know='준비된 PostgreSQL 18 이미지는 /var/lib/postgresql 아래에 데이터를 저장해요. 이미지의 기본 익명 볼륨은 재생성 때 이어질 수도 있지만 down 뒤 새 실행에서 같은 저장소로 다시 연결되지는 않아요. 실제 저장 경로를 이름 있는 data 볼륨에 연결해 식별자를 유지하세요.',
    starter=WRONG,solution=RIGHT,script=LAB2,images=[PG],
    expected='처음:1\n재시작:1\n재생성:1\ndown:1',
    first='재시작과 재생성에서는 메모가 남아 보일 수 있어요. 하지만 down 뒤에는 같은 익명 볼륨을 다시 찾지 않아 표가 사라져요. 이름 있는 data 볼륨은 엉뚱한 경로에 붙어 있었어요.',
    result='재생성과 down 뒤에도 실제 memo 표의 한 행이 남아 있어요. 컨테이너 수명과 데이터 수명이 분리됐어요.',
    caution='조심하세요. 이미지 버전마다 데이터 경로가 같다고 가정하지 마세요. 이 과제는 명시한 PostgreSQL 18 이미지의 경로를 사용해요.')

COMPOSE_INIT=RIGHT.replace('    volumes: ["data:/var/lib/postgresql"]',
    '    volumes:\n      - data:/var/lib/postgresql\n      - ./init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro')
INIT="CREATE TABLE memo(id INT PRIMARY KEY,title TEXT); INSERT INTO memo VALUES(1,'milk');\n"
LAB3='''set -e
docker compose up -d --wait db >/dev/null 2>&1
# 첫 초기화 뒤 배포 파일이 새 버전으로 바뀐 상황을 재현해요.
printf "CREATE TABLE memo(id INT PRIMARY KEY,title TEXT,version INT DEFAULT 1);\\n" > init.sql
docker compose up -d --force-recreate --wait -t 1 db >/dev/null 2>&1
cat migration.sql | docker compose exec -T db psql -U postgres -d lab -X -qAt -v ON_ERROR_STOP=1
docker compose exec -T db psql -U postgres -d lab -X -qAt -v ON_ERROR_STOP=1 -c "SELECT title||':'||version FROM memo ORDER BY id" </dev/null
'''
S3=step(slug='final-migration',title='기존 메모를 보존하며 새 열을 추가하세요',
    concept='최초 초기화 스크립트와 이미 존재하는 DB의 변경은 서로 다른 작업이에요.',
    intro='첫 실행에서 milk 메모를 저장했어요. init.sql을 새 표 정의로 바꿔 컨테이너를 다시 만들어도 기존 DB의 표는 바뀌지 않아요.',
    know='이미 데이터가 있는 볼륨이면 초기화 스크립트를 다시 실행하지 않아요. migration.sql에서 memo에 version INT DEFAULT 1 NOT NULL 열을 추가하세요. 기존 행과 새 열의 기본값을 함께 보존해야 해요.',
    starter='-- 기존 DB에 필요한 스키마 변경을 구현하세요.\n',
    solution='ALTER TABLE memo ADD COLUMN version INT DEFAULT 1 NOT NULL;\n',script=LAB3,
    images=[PG],files={'init.sql':INIT},expected='milk:1',
    first='마지막 조회에서 version 열이 없다는 오류가 나요. 새 초기화 파일은 이미 존재하는 DB를 변경하지 않았어요.',
    result='실제 기존 행 milk와 새 version 값 1이 함께 나와요. DB를 지우지 않고 스키마를 변경했어요.',
    caution='조심하세요. 볼륨을 지우고 다시 초기화하면 새 열은 생겨도 기존 사용자 데이터가 사라져요. 지금 목표는 기존 행을 지키는 변경이에요.',
    variants=[dict(files={'init.sql':INIT.replace("'milk'","'bread'")},expected='bread:1')])
# Only the learner's migration is editable here; the Compose environment is provided.
S3['entry_file']='migration.sql'
S3['files']['compose.yaml']=COMPOSE_INIT
# The first observation deliberately fails at the provided SELECT, after the
# student's empty migration. Mark that execution as the expected SQL failure.
S3['narration'][1]=('run',None,'version')

LESSON=lesson(key='docker-compose-db',folder='docker_compose_db',pilot='콤',
    title='Compose·DB · 컨테이너를 바꿔도 데이터는 남겨요',
    objectives=['앱과 DB의 주소 경계를 연결해요.', '실제 저장 경로와 볼륨 수명을 확인해요.', '초기화와 기존 데이터의 스키마 변경을 구별해요.'],
    units=[unit('서로 다른 서비스','DB에 연결하는 위치를 구별해요.',[S1]),
           unit('데이터의 수명','컨테이너를 다시 만드는 상황을 직접 검사해요.',[S2]),
           unit('최종 배포 변경','기존 데이터를 보존하며 스키마를 바꿔요.',[S3])],final_slug='final-migration')
LESSON['sources'].append(('https://hub.docker.com/_/postgres','PostgreSQL 18 데이터 경로와 최초 초기화 조건을 확인해요.','실제 고정 이미지의 재생성 결과로 대조해요.'))
