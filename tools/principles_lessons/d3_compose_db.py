"""Compose DB: address boundaries, durable storage, first-init versus migration — typed in the real terminal.

The learner edits compose.yaml (or migration.sql) in the editor and types docker compose and psql
commands in the real terminal. Grading reads the real PostgreSQL state with one SELECT in the db
container, the mounts and the Compose configuration (compose_terminal.py).
"""
from compose_terminal import TERMINAL, bash, compose_step, config, file_text, mount, patch, read, running, type_command
from docker_common import FOLDER, lesson, unit
from sql_lab import PG

BASE = f'''services:
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
FIX1 = ('"-h", "localhost"', '"-h", "db"')
SOLUTION1 = BASE.replace(*FIX1)
UP = 'docker compose up -d --wait db'
APP = 'docker compose run --rm app'
PSQL = 'docker compose exec db psql -U postgres -d lab'
SELECT_TITLE = ['psql', '-U', 'postgres', '-d', 'lab', '-X', '-qAt', '-c']

S1 = compose_step(
    slug='db-address', title='app이 db 서비스의 데이터베이스에 접속하게 하세요',
    objectives=['데이터베이스 연결 주소는 클라이언트가 실행되는 위치에 따라 달라져요.'],
    start='편집기의 compose.yaml에는 db(PostgreSQL)와 app(SQL 클라이언트) 서비스가 있어요. ' + FOLDER + ' 아직 이 문제의 컨테이너는 없어요.',
    intro=['db 컨테이너에 PostgreSQL이 있고 app 컨테이너에서 SQL 클라이언트를 실행해요. 사용자 PC의 DB는 사용하지 않아요.'],
    know='app의 localhost에는 PostgreSQL이 없어요. 같은 네트워크의 db 서비스 이름과 내부 포트를 사용하세요. 이 단계는 PC에 DB 포트를 공개하지 않아요. `docker compose run --rm app`은 app을 한 번 실행하고 지워요. 접속하지 못하면 psql이 실패해요.',
    images=[PG], editable=['compose.yaml'], files={'compose.yaml': BASE}, solution_files={'compose.yaml': SOLUTION1},
    commands=[UP, APP],
    todo=[type_command(UP, 'DB를 실행하고 건강해질 때까지 기다려요. 처음에는 이미지를 받느라 조금 걸릴 수 있어요.'),
          type_command(APP, 'app의 접속 결과를 읽으세요.'),
          '편집기의 compose.yaml에서 app이 접속하는 주소를 db 서비스로 고치세요.',
          type_command(UP, '고친 파일로 다시 실행해요.'),
          type_command(APP, '이번 결과를 읽으세요.')],
    checks=[running('db'), config('app이 db 서비스에 접속', {'services': {'app': {'command': ['-h', 'db']}}})],
    success='지금 compose.yaml의 app이 db 서비스로 접속했고, 터미널의 app 실행이 성공했어요.',
    complexity=dict(prior='Compose 서비스 이름으로 다른 컨테이너를 찾았어요.', new='데이터베이스 연결 주소는 클라이언트가 실행되는 위치에 따라 달라져요.',
                    changed='app의 접속 주소', evidence='터미널의 app 실행 결과', lines=1, services=1),
    narration=[
        ('say', 'DB는 건강한데 app이 접속하지 못하는 문제예요.', 'text:db 컨테이너에 PostgreSQL이 있고 app 컨테이너에서 SQL 클라이언트를 실행해요.'),
        bash(UP, 'DB를 실행하고 건강해질 때까지 기다릴게요.', wait=900),
        ('say', 'db가 Healthy예요. PostgreSQL은 준비됐어요.', TERMINAL),
        bash(APP, 'app에서 접속해 볼게요.', fails=True),
        ('say', 'localhost에 접속하지 못했다는 오류예요. app이 자기 localhost로 접속했어요.', TERMINAL),
        ('say', 'app 안의 localhost는 app 컨테이너 자신이에요. 거기에는 DB가 없어요.', 'code:"-h", "localhost"'),
        patch('compose.yaml', *FIX1, '접속 주소를 db 서비스 이름으로 바꿔요.'),
        bash(UP, '고친 파일로 다시 실행해요.'),
        ('say', 'db는 그대로 건강해요. 바뀐 것은 app의 설정이에요.', TERMINAL),
        bash(APP, '다시 접속해요.'),
        ('say', 'connected가 나왔어요. app이 db 서비스의 실제 PostgreSQL에 연결했어요.', TERMINAL),
        ('say', '조심하세요. PC에 이미 설치된 PostgreSQL을 찾는 과제가 아니에요. 준비된 실습 DB의 서비스 이름을 사용하세요.', 'text:사용자 PC의 DB는 사용하지 않아요.')],
    review={'조심하세요. PC에 이미 설치된 PostgreSQL을 찾는 과제가 아니에요. 준비된 실습 DB의 서비스 이름을 사용하세요.':
            'PC에 DB가 있으면 그쪽에 연결을 시도하기 쉬워요. 이 실습은 PC에 DB 포트를 공개하지 않아요.'})

WRONG = SOLUTION1.replace('    healthcheck:', '    volumes: ["data:/data"]\n    healthcheck:') + 'volumes:\n  data:\n'
FIX2 = ('data:/data', 'data:/var/lib/postgresql')
RIGHT = WRONG.replace(*FIX2)
CREATE = PSQL + ''' -c "CREATE TABLE IF NOT EXISTS memo(title TEXT); INSERT INTO memo VALUES('milk')"'''
SELECT = PSQL + ' -c "SELECT title FROM memo"'
S2 = compose_step(
    slug='db-volume', title='DB 컨테이너를 다시 만들어도 메모가 남게 하세요',
    objectives=['볼륨은 데이터베이스가 실제로 저장하는 경로에 연결해야 해요.'],
    start='새 compose.yaml로 시작해요. db에 이름 있는 볼륨 data가 붙어 있어요. 이 문제의 컨테이너는 아직 없어요.',
    intro=['볼륨 data가 있지만 /data에 붙어 있어요. 이 PostgreSQL 18 이미지가 저장하는 경로와 달라요.'],
    know='준비된 PostgreSQL 18 이미지는 /var/lib/postgresql 아래에 데이터를 저장해요. `docker compose down`은 컨테이너를 지워요. 다시 up 하면 이미지의 익명 볼륨이 아닌 새 저장소로 시작해요. 실제 저장 경로를 이름 있는 data 볼륨에 연결해 다시 만든 컨테이너도 같은 저장소를 쓰게 하세요.',
    images=[PG], editable=['compose.yaml'], files={'compose.yaml': WRONG}, solution_files={'compose.yaml': RIGHT},
    commands=[UP, CREATE, 'docker compose down', UP, SELECT],
    todo=[type_command(UP, 'DB를 실행해요.'),
          type_command(CREATE, 'memo 표에 milk를 저장해요.'),
          type_command('docker compose down', 'DB 컨테이너를 지워요.'),
          type_command(UP, 'DB를 다시 만들어요.'),
          type_command(SELECT, 'milk가 남았는지 읽으세요.'),
          '편집기의 compose.yaml에서 data 볼륨이 PostgreSQL의 실제 저장 경로에 연결되게 고치세요.',
          type_command(UP, '고친 파일로 DB를 다시 만들어요.'),
          type_command(CREATE, 'milk를 다시 저장해요.'),
          type_command('docker compose down', 'DB 컨테이너를 지워요.'),
          type_command(UP, 'DB를 다시 만들어요.'),
          type_command(SELECT, '이번에는 milk가 남았는지 읽으세요.')],
    checks=[running('db'), mount('db', '/var/lib/postgresql', 'data'),
            read('db의 memo 표', 'db', SELECT_TITLE + ['SELECT title FROM memo'], has=['milk'])],
    success='지금 compose.yaml로 다시 만든 db가 /var/lib/postgresql에 data 볼륨을 연결했고, down 전에 저장한 milk가 남아 있어요.',
    complexity=dict(prior='DB 서비스에 접속했어요.', new='볼륨은 데이터베이스가 실제로 저장하는 경로에 연결해야 해요.',
                    changed='data 볼륨의 연결 경로', evidence='down 뒤 터미널의 SELECT 결과와 실제 마운트', lines=1, services=1),
    narration=[
        ('say', '볼륨을 붙였는데도 DB를 다시 만들면 표가 사라지는 문제예요.', 'text:볼륨 data가 있지만 /data에 붙어 있어요.'),
        bash(UP, 'DB를 실행할게요.', wait=900),
        ('say', 'db가 Healthy예요.', TERMINAL),
        bash(CREATE, 'memo 표를 만들고 milk를 저장해요.'),
        ('say', 'CREATE TABLE과 INSERT가 성공했어요.', TERMINAL),
        bash('docker compose down', '이제 컨테이너를 지울게요.'),
        ('say', '컨테이너가 지워졌어요. 볼륨 data는 남아 있어요.', TERMINAL),
        bash(UP, 'DB를 다시 만들어요.', wait=300),
        ('say', '새 db 컨테이너가 Healthy가 됐어요.', TERMINAL),
        bash(SELECT, 'milk를 찾아볼게요.', fails=True),
        ('say', 'memo 표가 없다는 오류예요. 새 컨테이너는 빈 저장소에서 시작했어요.', TERMINAL),
        ('say', 'data 볼륨이 /data에 붙어 있어요. PostgreSQL은 그 폴더에 저장하지 않아요.', 'code:data:/data'),
        patch('compose.yaml', *FIX2, '볼륨을 PostgreSQL 18의 실제 저장 경로에 연결해요.'),
        bash(UP, '고친 파일로 DB를 다시 만들어요.', wait=300),
        ('say', 'db를 새로 만들고 Healthy가 됐어요.', TERMINAL),
        bash(CREATE, 'milk를 다시 저장해요.'),
        ('say', '이번에는 data 볼륨 안에 저장됐어요.', TERMINAL),
        bash('docker compose down', '컨테이너를 지워요.'),
        ('say', '컨테이너는 지워졌어요.', TERMINAL),
        bash(UP, 'DB를 다시 만들어요.', wait=300),
        ('say', '새 db 컨테이너가 같은 data 볼륨을 연결했어요.', TERMINAL),
        bash(SELECT, 'milk를 찾아볼게요.'),
        ('say', 'milk가 그대로 나와요. 컨테이너 수명과 데이터 수명이 분리됐어요.', TERMINAL),
        ('say', '조심하세요. 이미지 버전마다 데이터 경로가 같다고 가정하지 마세요. 이 과제는 명시한 PostgreSQL 18 이미지의 경로를 사용해요.', 'text:준비된 PostgreSQL 18 이미지는 /var/lib/postgresql 아래에 데이터를 저장해요.')],
    review={'조심하세요. 이미지 버전마다 데이터 경로가 같다고 가정하지 마세요. 이 과제는 명시한 PostgreSQL 18 이미지의 경로를 사용해요.':
            '이전 버전의 /var/lib/postgresql/data 경로를 그대로 쓰는 실수가 흔해요. 이 실습은 PostgreSQL 18 이미지의 경로로 실제 확인해요.'},
    rejects=[([('data:/var/lib/postgresql', 'data:/var/lib/postgresql-old')], '실제 저장 경로가 아닌 곳에 볼륨을 붙이면 down 뒤 표가 사라져요.')])

COMPOSE_INIT = RIGHT.replace('    volumes: ["data:/var/lib/postgresql"]',
    '    volumes:\n      - data:/var/lib/postgresql\n      - ./init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro')
INIT = "CREATE TABLE memo(id INT PRIMARY KEY,title TEXT); INSERT INTO memo VALUES(1,'milk');\n"
MIGRATION_START = '-- 기존 DB에 필요한 스키마 변경을 구현하세요.\n'
MIGRATION_FIX = (MIGRATION_START, '-- 기존 표에 열을 더해요. 기존 행은 기본값 1을 받아요.\nALTER TABLE memo ADD COLUMN IF NOT EXISTS version INT DEFAULT 1 NOT NULL;\n')
MIGRATION = MIGRATION_START.replace(*MIGRATION_FIX)
LIST = PSQL + ' -c "SELECT * FROM memo"'
MIGRATE = 'docker compose exec -T db psql -U postgres -d lab < migration.sql'
VERSION = PSQL + ' -c "SELECT title, version FROM memo"'
S3 = compose_step(
    slug='final-migration', title='기존 메모를 보존하며 새 열을 추가하세요',
    objectives=['최초 초기화 스크립트와 이미 존재하는 DB의 변경은 서로 다른 작업이에요.'],
    start='편집기에는 migration.sql이 있어요. 터미널 폴더의 compose.yaml은 data 볼륨과 init.sql을 db에 연결해요. init.sql은 memo 표와 milk 한 행을 만들어요.',
    intro=['init.sql은 볼륨이 비어 있는 첫 실행에서만 실행돼요. 이미 데이터가 있는 DB에 새 열이 필요하면 표를 지우지 않고 변경해야 해요.',
           '같은 마이그레이션을 다시 실행해도 실패하지 않도록 ADD COLUMN IF NOT EXISTS를 쓸 수 있어요. 같은 이름의 열이 있으면 추가를 생략할 뿐, 기존 열의 자료형과 제약까지 검사하지는 않아요.'],
    know='이미 데이터가 있는 볼륨이면 초기화 스크립트를 다시 실행하지 않아요. migration.sql에서 memo에 version INT DEFAULT 1 NOT NULL 열을 추가하세요. 기존 행과 새 열의 기본값을 함께 보존해야 해요. `< migration.sql`은 이 폴더의 파일 내용을 psql의 입력으로 보내요.',
    images=[PG], editable=['migration.sql'], files={'migration.sql': MIGRATION_START, 'compose.yaml': COMPOSE_INIT, 'init.sql': INIT},
    solution_files={'migration.sql': MIGRATION},
    setup=[UP], commands=[MIGRATE, VERSION], same_files=['migration.sql'],
    todo=[type_command(UP, 'DB를 처음 실행해요. 이때 init.sql이 실행돼요.'),
          type_command(LIST, '저장된 메모를 읽으세요.'),
          type_command(VERSION, 'version 열이 있는지 확인하세요.'),
          '편집기의 migration.sql에 memo 표에 `version INT DEFAULT 1 NOT NULL` 열을 추가하는 SQL을 쓰세요.',
          type_command(MIGRATE, 'migration.sql을 실제 DB에 실행해요.'),
          type_command(VERSION, '기존 메모와 새 열을 함께 읽으세요.')],
    checks=[running('db'),
            read('memo 표의 기존 행과 새 열', 'db', SELECT_TITLE + ["SELECT title||':'||version FROM memo ORDER BY id"], has=['milk:1']),
            read('version 열의 제약', 'db', SELECT_TITLE + ["SELECT is_nullable||':'||column_default FROM information_schema.columns WHERE table_name='memo' AND column_name='version'"], has=['NO:1']),
            file_text('migration.sql', has=['alter table'], lacks=['drop table', 'truncate', 'delete', 'insert'])],
    success='지금 migration.sql을 실행해 기존 milk 행을 지우지 않고 version 열(기본값 1, NOT NULL)을 더했어요.',
    complexity=dict(prior='DB 데이터를 볼륨에 남겼어요.', new='최초 초기화 스크립트와 이미 존재하는 DB의 변경은 서로 다른 작업이에요.',
                    changed='migration.sql의 ALTER TABLE', evidence='터미널의 SELECT 결과와 실제 열 정의', lines=1, services=1),
    narration=[
        ('say', '데이터가 있는 DB에 새 열을 더하는 문제예요.', 'text:이미 데이터가 있는 DB에 새 열이 필요하면 표를 지우지 않고 변경해야 해요.'),
        ('say', 'migration.sql은 이미 있는 DB에 보내는 변경이에요. 다시 실행해도 실패하지 않게 써야 해요.', 'text:같은 마이그레이션을 다시 실행해도 실패하지 않도록 ADD COLUMN IF NOT EXISTS를 쓸 수 있어요.'),
        bash(UP, 'DB를 처음 실행해요. 빈 볼륨이라 init.sql이 실행돼요.', wait=900),
        ('say', 'db가 Healthy예요.', TERMINAL),
        bash(LIST, '저장된 메모를 읽어요.'),
        ('say', 'id 1의 milk가 있어요. init.sql이 만든 행이에요.', TERMINAL),
        bash(VERSION, 'version 열을 읽어 볼게요.', fails=True),
        ('say', 'version 열이 없다는 오류예요. 아직 표를 바꾸지 않았어요.', TERMINAL),
        ('say', 'migration.sql은 아직 비어 있어요. 여기에 기존 표를 바꾸는 SQL을 써요.', 'code:-- 기존 DB에 필요한 스키마 변경을 구현하세요.'),
        patch('migration.sql', *MIGRATION_FIX, 'ALTER TABLE로 memo에 version 열을 더해요.'),
        bash(MIGRATE, 'migration.sql을 실제 DB에 실행해요.'),
        ('say', '오류 없이 끝났어요. 표를 지우지 않고 열만 더했어요.', TERMINAL),
        bash(VERSION, '다시 읽어요.'),
        ('say', 'milk와 version 1이 함께 나와요. 기존 행이 기본값 1을 받았어요.', TERMINAL),
        ('say', '조심하세요. 볼륨을 지우고 다시 초기화하면 새 열은 생겨도 기존 사용자 데이터가 사라져요. 지금 목표는 기존 행을 지키는 변경이에요.', 'text:이미 데이터가 있는 볼륨이면 초기화 스크립트를 다시 실행하지 않아요.')],
    review={'조심하세요. 볼륨을 지우고 다시 초기화하면 새 열은 생겨도 기존 사용자 데이터가 사라져요. 지금 목표는 기존 행을 지키는 변경이에요.':
            'init.sql을 고쳐 down -v로 다시 초기화하는 지름길이 흔해요. 기존 행 보존이 이 문제의 조건이에요.',
            'migration.sql은 이미 있는 DB에 보내는 변경이에요. 다시 실행해도 실패하지 않게 써야 해요.':
            '본문을 다시 읽지 않고 이미 데이터가 있는 DB에 보내는 변경이라는 조건을 먼저 말해요. IF NOT EXISTS의 범위는 본문이 설명해요.'},
    rejects=[([('ADD COLUMN IF NOT EXISTS version INT DEFAULT 1 NOT NULL', 'ADD COLUMN IF NOT EXISTS version INT')], '기본값이 없으면 기존 행의 version이 비어 있어 milk:1이 나오지 않아요.'),
             ([('ALTER TABLE memo ADD COLUMN IF NOT EXISTS version INT DEFAULT 1 NOT NULL;', "DROP TABLE memo; CREATE TABLE memo(id INT PRIMARY KEY,title TEXT,version INT DEFAULT 1 NOT NULL); INSERT INTO memo VALUES(1,'milk');")], '표를 지우고 다시 만들면 결과는 같아 보여도 기존 데이터를 보존하지 않아요.')])

LESSON = lesson(key='docker-compose-db', folder='docker_compose_db', pilot='콤',
    title='Compose·DB · 컨테이너를 바꿔도 데이터는 남겨요',
    objectives=['앱과 DB의 주소 경계를 연결해요.', '실제 저장 경로와 볼륨 수명을 확인해요.', '초기화와 기존 데이터의 스키마 변경을 구별해요.'],
    units=[unit('서로 다른 서비스', 'DB에 연결하는 위치를 구별해요.',
                'db 서비스에는 PostgreSQL이, app 서비스에는 SQL 클라이언트가 있어요. 터미널에서 docker compose로 실행하고 결과를 읽어요.', [S1]),
           unit('데이터의 수명', '컨테이너를 다시 만드는 상황을 직접 검사해요.',
                'memo 표를 저장한 뒤 DB 컨테이너를 지우고 다시 만들어 남는지 터미널에서 확인해요.', [S2]),
           unit('최종 배포 변경', '기존 데이터를 보존하며 스키마를 바꿔요.',
                'init.sql로 처음 만든 DB에 migration.sql로 새 열을 더해요.', [S3])],
    final_slug='final-migration')
LESSON['sources'].append(('https://hub.docker.com/_/postgres', 'PostgreSQL 18 데이터 경로와 최초 초기화 조건을 확인해요.', '실제 고정 이미지의 재생성 결과로 대조해요.'))
LESSON['revision'] = 5
LESSON['prerequisites'] = ['Docker 입문에서 이미지·컨테이너·볼륨·Compose를 관찰했어요.', 'SQL 기초에서 표 생성·행 추가·조회를 실행했어요.']
