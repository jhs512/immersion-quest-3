"""Shared real-engine SQL exercises; no simulated query results."""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT

PG = 'postgres:18-alpine@sha256:898c60cb390d1085bc97bdd6a1ae968757421df394b071848b52b1c09c89d6a5'
MYSQL = 'mysql:8.4@sha256:76f0358884cb92d9a086d24e5671c38048d3fef40f2588703d73eb55392d6b69'


def compose(engine):
    if engine == 'mysql':
        return f'''services:
  db:
    image: {MYSQL}
    environment: {{MYSQL_ROOT_PASSWORD: lab, MYSQL_DATABASE: lab}}
    tmpfs: [/var/lib/mysql]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "127.0.0.1", "-uroot", "-plab"]
      interval: 1s
      timeout: 3s
      retries: 60
'''
    return f'''services:
  db:
    image: {PG}
    environment: {{POSTGRES_PASSWORD: lab, POSTGRES_DB: lab}}
    tmpfs: [/var/lib/postgresql]
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres", "-h", "127.0.0.1"]
      interval: 1s
      timeout: 3s
      retries: 60
'''


def lab(engine):
    command = ('docker compose exec -T -e MYSQL_PWD=lab db mysql -uroot --default-character-set=utf8mb4 --batch --skip-column-names --force lab'
               if engine == 'mysql' else 'docker compose exec -T db psql -U postgres -d lab -X -q -A -t -v ON_ERROR_STOP=0')
    return f'''# 제공 실습: 실제 DB를 준비하고 학습자가 쓴 SQL을 실행해요.
set -e
docker compose up -d --wait db >/dev/null 2>&1
# 오류가 나도 다음 SQL을 실행해요. DB가 거절한 행과 남은 행을 비교하기 위해서예요.
# 오류는 stderr에 그대로 남고, 표의 실제 조회 결과만 stdout으로 나와요.
cat before.sql lesson.sql after.sql | {command}
'''


def sql_step(*, slug, title, concept, intro, know, before='', starter, solution,
             after='', expected, first_output, result, caution, engine='postgres',
             tests=None, variants=None, accepts=None, rejects=None):
    return dict(slug=slug, title=title, language='docker',
                docker_images=[MYSQL if engine == 'mysql' else PG], entry_file='lesson.sql',
                files={'compose.yaml': compose(engine), 'lab.sh': lab(engine),
                       'before.sql': before, 'after.sql': after},
                start=START_NEW, intro=[intro], know=know,
                todo=[TODO_RUN_BEFORE, 'lesson.sql에서 다음 요구를 구현하세요. ' + title,
                      '오류가 난 문장과 그 뒤 조회 결과를 함께 읽으세요.', TODO_RUN_AFTER, TODO_SUBMIT],
                objectives=[concept], starter=starter, solution=solution,
                tests=tests or [('', expected)], variations=variants or [],
                success=expected,
                complexity=dict(prior='SELECT·INSERT와 표의 기본 의미를 알아요.', new=concept,
                                changed=title, evidence='실제 SQL 오류와 저장된 행의 조회 결과', lines=3, services=0),
                narration=[('say', intro, 'text:' + intro), ('run',), ('say', first_output, 'output'),
                           ('say', concept, 'code:' + starter.splitlines()[0]),
                           ('patch', starter, solution, title), ('run',), ('say', result, 'output'),
                           ('say', caution, 'text:' + know), ('submit',)],
                review={intro: '준비 SQL에서 실제로 시작하는 상태를 말해요.',
                        title: '현재 스텝의 SQL 수정 목표예요. 준비된 관계와 수정 후 조회 결과로 달성 여부를 확인해요.',
                        concept: '수정할 SQL 구문을 강조하며 이 스텝에서 관찰할 원리를 설명해요.',
                        first_output: '수정 전 실제 조회 결과와 원인을 연결해요.',
                        result: '수정 후 DB에 남는 행을 말해요. SQL 오류와 행 수를 같은 것으로 취급하지 않아요.',
                        caution: '이 스텝의 구체적인 오해를 지적해요. 표시된 DB 규칙과 실제 실행을 비교해요.'},
                accepts=accepts or [], rejects=rejects or [([(solution, starter)], '해결 전 SQL로 되돌리면 DB가 요구한 상태가 되지 않아요.')])


def sql_lesson(*, key, folder, pilot, title, objectives, units, final_slug, engine='postgres', sources=None):
    return dict(key=key, folder=folder, pilot=pilot, revision=1, title=title,
                category='db', category_title='DB', track=None,
                category_evidence='실제 DB 엔진에서 SQL을 실행하고 저장된 상태를 확인해요.',
                track_evidence='새 수업의 트랙은 임의 확정하지 않아요.',
                audience='SQL 결과가 왜 그렇게 나오는지 이해하고 싶은 학습자',
                prerequisites=['터미널에서 명령을 실행할 수 있어요.', 'SELECT·INSERT의 기본 의미를 알아요.', 'Docker Desktop을 설치하고 켤 수 있어요.'],
                objectives=objectives, scope=objectives,
                out_of_scope=['운영 DB 접속과 데이터 변경', '엔진 내부 구현 전체', 'Supabase·RLS·트리거'],
                sources=sources or [('https://www.postgresql.org/docs/current/tutorial.html', '관계·제약·조회·트랜잭션의 의미를 확인해요.', '공식 문서와 실제 엔진 출력을 대조해요.')],
                description='작은 표에서 조건 하나를 바꿔 실제 저장 결과를 비교해요.',
                brief=(' / '.join(objectives), '마지막 도전에서 여러 입력에도 데이터의 규칙을 지키세요.',
                       [u['title'] for u in units], f'실제 {"MySQL 8.4" if engine == "mysql" else "PostgreSQL 18"}를 사용해요. 문제 진입 시 준비 SQL을 넣어요. 같은 문제를 다시 실행하면 변경 상태가 이어져요. 제출 검사는 별도 준비 DB에서 해요.',
                       '쿼리가 실행됐다는 것과 데이터가 올바르다는 것은 어떻게 다를까요?'),
                representative=dict(slug=final_slug, expected_action='최종 도전의 SQL을 직접 구현해요.',
                                    acceptance='실제 DB의 결과가 모든 검사와 변형 조건을 만족해요.', reset='앱 소유의 새 실습 DB에서 시작해요.',
                                    narration='실패 결과를 읽고 SQL을 고쳐 실제 저장 결과를 비교해요.'),
                grading=['실제 DB와 앱 채점기로 정답·준비 코드·오답을 실행해요.', 'SQL 오류는 숨기지 않고 남은 데이터와 함께 보여 줘요.',
                         '다른 입력과 동등한 SQL 풀이를 비교해요.'],
                reset=['문제에 처음 진입할 때 준비 SQL을 적용해요. 같은 문제의 실행 버튼을 다시 누르면 변경 상태가 이어져요.',
                       '문제를 바꾸거나 초기화를 요청하면 해당 실습의 준비 상태로 돌아가요. 제출 검사에는 별도 DB를 사용해요.',
                       '수업을 나갈 때 앱 소유 컨테이너를 정리해요. 사용자의 기존 DB·컨테이너와 학습 진도는 지우지 않아요.'],
                narration_policy=['수정 전 SQL 실행·결과 읽기·SQL 수정·다시 실행 순서예요.', '이 스텝에서 혼동할 부분만 구체적으로 경고해요.'],
                verification=['실제 엔진의 저장 상태와 오류를 확인해요.', '준비 코드 실패·정답 통과·오답 거부를 확인해요.'],
                learning_strategy='먼저 실제 SQL 결과를 보고, 원인을 설명한 뒤 직접 SQL을 고쳐요.',
                chapters=[dict(title=title, objectives=objectives, units=units)])


def unit(title, objective, steps):
    return dict(title=title, objectives=[objective], premise='제공 SQL로 작은 실습 DB를 준비해요. 실제 사용자 데이터는 없어요.', steps=steps)
