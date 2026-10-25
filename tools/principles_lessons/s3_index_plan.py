"""Indexes as additional access paths, observed through real PostgreSQL JSON plans."""
from sql_lab import sql_step, sql_lesson, unit

SEED = """CREATE TABLE parcel(id INT PRIMARY KEY, code TEXT NOT NULL, city TEXT NOT NULL, state TEXT NOT NULL);
INSERT INTO parcel SELECT i,'BOX-'||i,CASE WHEN i%100=0 THEN 'busan' ELSE 'seoul' END,
CASE WHEN i%1000=0 THEN 'waiting' ELSE 'done' END FROM generate_series(1,50000) i;
ANALYZE parcel;
-- 제공 관찰 함수: 실제 EXPLAIN의 계획 노드 전체에서 인덱스 사용을 찾습니다.
CREATE FUNCTION uses_index(query TEXT) RETURNS BOOLEAN LANGUAGE plpgsql AS $$
DECLARE plan JSON; BEGIN
 EXECUTE 'EXPLAIN (FORMAT JSON) '||query INTO plan;
 RETURN jsonb_path_exists(plan::jsonb, '$.**."Index Name"');
END $$;
"""


def step(slug, title, concept, intro, know, starter, solution, after, first, result, caution, variants=None):
    return sql_step(slug=slug, title=title, concept=concept, intro=intro, know=know,
                    before=SEED, starter=starter, solution=solution, after=after,
                    expected='인덱스 경로:true\n일치:1', first_output=first, result=result,
                    caution=caution, variants=variants)


CHECK1 = "SELECT '인덱스 경로:'||uses_index('SELECT id FROM parcel WHERE code=''BOX-12345''');\nSELECT '일치:'||COUNT(*) FROM parcel WHERE code='BOX-12345';\n"
S1 = step('access-path', '송장 코드 조회용 인덱스를 만드세요', '인덱스는 정답을 바꾸지 않고 행을 찾는 경로를 추가해요.',
          '송장 5만 건에서 코드 하나를 찾아요. id에는 기본 키 인덱스가 있지만 code에는 없어요.',
          '제공 함수는 실제 EXPLAIN JSON을 검사해요. 실행 시간은 컴퓨터와 캐시마다 달라서 채점하지 않아요. code의 동등 조건에 맞는 인덱스를 추가하세요.',
          '-- code 조회 경로를 추가하세요.\n', 'CREATE INDEX parcel_code ON parcel(code);\n', CHECK1,
          '일치는 1이지만 인덱스 경로는 false예요. 답이 맞는 것과 찾는 방법은 별개예요.',
          '일치는 그대로 1이고 인덱스 경로가 true가 됐어요. 실제 계획이 추가 경로를 선택했어요.',
          '조심하세요. id 인덱스가 code 검색을 대신해 주지는 않아요. 조회 조건의 열을 확인하세요.',
          [dict(files={'after.sql': CHECK1.replace('12345','23456')}, expected='인덱스 경로:true\n일치:1')])

CHECK2 = "SELECT '인덱스 경로:'||uses_index('SELECT id FROM parcel WHERE lower(code)=''box-12345''');\nSELECT '일치:'||COUNT(*) FROM parcel WHERE lower(code)='box-12345';\n"
S2 = step('expression', '대소문자를 무시하는 검색 경로를 만드세요', '열 값과 그 값에 함수를 적용한 결과는 다른 검색 키예요.',
          '이번 검색은 lower(code)를 비교해요. code 인덱스를 만들었지만 계획은 여전히 전체 표를 읽어요.',
          '검색이 사용하는 표현식과 맞는 표현식 인덱스를 만드세요. 원본 코드와 소문자로 바꾼 코드는 서로 다른 키예요.',
          'CREATE INDEX parcel_code ON parcel(code);\n', 'CREATE INDEX parcel_lower ON parcel(lower(code));\n', CHECK2,
          '소문자 검색 결과는 한 건이지만 일반 code 인덱스 경로가 선택되지 않았어요.',
          'lower(code)로 만든 인덱스에서 같은 소문자 키를 찾아요. 실제 저장된 code를 소문자로 고치지는 않았어요.',
          '조심하세요. WHERE를 대소문자 구분 검색으로 바꿔 통과하려 하면 원래 검색 요구가 바뀌어요.')

CHECK3 = "SELECT '인덱스 경로:'||uses_index('SELECT id FROM parcel WHERE state=''waiting'' AND code=''BOX-12000''');\nSELECT '일치:'||COUNT(*) FROM parcel WHERE state='waiting' AND code='BOX-12000';\n"
S3 = step('partial', '대기 중인 송장만 담는 인덱스를 만드세요', '부분 인덱스는 행을 삭제하지 않고 색인할 행을 제한해요.',
          '5만 건 중 대기 송장은 50건이에요. 화면은 대기 상태의 코드 하나만 검색해요.',
          'WHERE state=\'waiting\'인 행의 code를 부분 인덱스에 담으세요. 표의 완료 행은 그대로 두어야 해요. 실제 검색 조건이 인덱스의 조건을 보장해야 쓸 수 있어요.',
          "CREATE INDEX parcel_waiting ON parcel(code) WHERE state='done';\n",
          "CREATE INDEX parcel_waiting ON parcel(code) WHERE state='waiting';\n", CHECK3,
          '완료 행만 담은 인덱스에서는 대기 송장을 찾을 수 없어요. 결과 한 건을 다른 경로로 찾았어요.',
          '대기 송장만 담은 경로가 선택됐어요. 전체 표의 행 수를 줄인 것은 아니에요.',
          '조심하세요. 부분 인덱스의 WHERE는 조회 결과를 거르는 WHERE와 달라요. 조회가 필요한 행을 인덱스가 빠뜨리면 쓸 수 없어요.')

START4 = "CREATE INDEX parcel_city ON parcel(city);\n"
FIX4 = "CREATE INDEX parcel_lookup ON parcel(city,lower(code)) WHERE state='waiting';\n"
CHECK4 = "SELECT '인덱스 경로:'||uses_index('SELECT id FROM parcel WHERE city=''busan'' AND state=''waiting'' AND lower(code)=''box-12000''');\nSELECT '일치:'||COUNT(*) FROM parcel WHERE city='busan' AND state='waiting' AND lower(code)='box-12000';\n"
S4 = step('final-lookup', '지역·상태·대소문자 조건을 함께 지원하세요', '조건과 데이터 분포에 맞는 검색 키를 직접 구성해요.',
          '지역별 대기 송장 화면을 만들어요. 코드의 대소문자를 무시하면서 지정한 지역의 송장 하나를 찾아야 해요.',
          '도시와 lower(code)를 키로 사용하고 대기 행만 담는 경로를 구현하세요. 별도의 코드로 SELECT 결과를 출력하지 말고 준비된 관찰 쿼리의 경로를 바꾸세요.',
          START4, FIX4, CHECK4,
          'city 인덱스도 일부 후보를 줄일 수 있어요. 이번 도전은 검색 조건 전체를 담는 색인 구조를 만드는 거예요.',
          '도시와 소문자 코드가 키가 되고 대기 행만 담겼어요. 같은 요구의 다른 코드도 같은 구조로 찾아요.',
          '조심하세요. 이 데이터에서 선택된 계획이 모든 데이터에 가장 빠르다는 뜻은 아니에요. 데이터가 달라지면 다시 EXPLAIN으로 확인하세요.',
          [dict(files={'after.sql': CHECK4.replace('12000','23000')}, expected='인덱스 경로:true\n일치:1')])
# The final also checks the index definition, rather than accepting an unrelated city-only path.
S4['files']['after.sql'] += "SELECT CASE WHEN EXISTS(SELECT 1 FROM pg_indexes WHERE tablename='parcel' AND indexdef LIKE '%lower(code)%' AND indexdef LIKE '%city%' AND indexdef LIKE '%waiting%') THEN '구조:true' ELSE '구조:false' END;\n"
S4['tests'] = [('', '인덱스 경로:true\n일치:1\n구조:true')]
S4['success'] = S4['tests'][0][1]
S4['variations'][0]['files']['after.sql'] += S4['files']['after.sql'].splitlines(True)[-1]
S4['variations'][0]['expected'] = S4['success']

LESSON = sql_lesson(key='sql-index-plan', folder='sql_index_plan', pilot='쥐',
                    title='인덱스 · 답은 같은데 찾는 경로가 달라요',
                    objectives=['조회 결과와 접근 경로를 구별해요.', '표현식과 부분 인덱스를 조건에 맞춰 만들어요.', '실제 실행 계획으로 가정을 확인해요.'],
                    units=[unit('정답과 경로', '데이터를 바꾸지 않고 검색 경로를 추가해요.', [S1,S2]),
                           unit('조건에 맞춘 색인', '어떤 행과 어떤 키를 색인할지 결정해요.', [S3,S4])],
                    final_slug='final-lookup', sources=[('https://www.postgresql.org/docs/18/indexes.html','표현식·부분·복합 인덱스의 전제를 확인해요.','실제 PostgreSQL 18 계획과 대조해요.')])
