"""Original pilot lessons. Official sources define scope, never copied questions."""
import hashlib
import json
from pathlib import Path
import sys

from principles_course.common import LESSONS, ROOT, code, java, lesson, python, compile_narration

OUT = ROOT / 'target/certification-pilots'
DATA = 'channel,visits,minutes,bought\nweb,2,10,0\napp,5,20,1\nweb,3,,1\napp,8,40,1\nweb,1,5,0\napp,4,15,0\n'
OTHER = 'channel,visits,minutes,bought\napp,9,12,1\nweb,4,,0\napp,1,30,0\nweb,6,18,1\nweb,2,6,0\n'
THIRD = 'channel,visits,minutes,bought\nweb,7,8,1\napp,2,,0\napp,3,22,1\nweb,1,14,0\n'


def analysis(id, title, principle, goal, before, after, expected, *, challenge=False, caution, hints):
    starter = '''
        import pandas as pd

        # 직접 만든 방문 자료예요. 실제 고객 자료가 아니에요.
        df = pd.read_csv('data/visits.csv')
        # result는 화면에 보여 줄 값의 이름이에요.
        result = EXPRESSION
        # 계산한 값을 눈으로 확인해요.
        print(result)
    '''.replace('EXPRESSION', before)
    t = python(id, title, principle, goal, starter, 'result = '+before, 'result = '+after,
               [('', expected)], files={'data/visits.csv': DATA}, challenge=challenge,
               caution=caution, hints=hints)
    # Compare real objects on three distinct datasets; memorized output cannot pass.
    t['checker'] = code('''
        import builtins
        import contextlib
        import io
        from pathlib import Path
        import runpy
        import sys
        import pandas as pd

        builtins.display = lambda *args: None
        for csv in DATASETS:
            Path('data/visits.csv').write_text(csv, encoding='utf8')
            df = pd.read_csv(io.StringIO(csv))
            expected = EXPECTED
            with contextlib.redirect_stdout(io.StringIO()):
                scope = runpy.run_path(sys.argv[1], run_name='__main__')
            assert 'result' in scope, 'result에 계산 결과를 담아 주세요.'
            actual = scope['result']
            if isinstance(expected, pd.DataFrame):
                pd.testing.assert_frame_equal(actual, expected)
            elif isinstance(expected, pd.Series):
                pd.testing.assert_series_equal(actual, expected)
            else:
                assert actual == expected, '다른 자료에서도 같은 원리가 맞아야 해요.'
        print('서로 다른 자료 3개를 모두 통과했어요.')
    ''').replace('DATASETS', repr([DATA, OTHER, THIRD])).replace('EXPECTED', after)
    return t


def build():
    aice = lesson('aice-data-first', '처음 만나는 코드와 데이터 표',
        '실행부터 시작해요. 표를 보고 행과 열을 골라요. 필수 문제 8개와 선택 도전 2개예요.',
        ['https://aice.study/info/aice/asso', 'https://aice.study/certi/examGuide'], [
        analysis('meet-table', '그대로 실행하고 표를 만나봐요',
            '아래는 방문 자료의 앞부분이에요.\n한 행은 방문 기록 하나예요.\n열은 같은 종류의 값을 세로로 모아요.\n\n'
            '| 접속 경로 | 방문 횟수 | 시간(분) | 구매(1)/미구매(0) |\n| --- | --- | --- | --- |\n'
            '| web | 2 | 10 | 0 |\n| app | 5 | 20 | 1 |\n| web | 3 | 빈칸 | 1 |\n\n'
            '준비 코드가 전체 표를 읽어 df에 담아요.\ndf는 표에 붙인 이름이에요.\n'
            'result는 보여 줄 값의 이름이고요.\nprint는 괄호 안의 값을 화면에 보여 줘요.',
            '① 코드를 고치지 말고 코드 실행을 누르세요.\n② 출력된 글자를 확인하세요.\n'
            '③ result 줄의 `\'방문 자료\'`를 `df`로 바꾸세요.\n④ 다시 실행해서 전체 표를 보세요.\n'
            '윗부분의 표 준비 코드는 그대로 두세요.\n표가 보이면 제출해 보세요.',
            "'방문 자료'", 'df', 'AUTO', caution='따옴표 안은 글자예요. df에는 따옴표를 붙이지 않아요.',
            hints=['result = df로 바꿔요. 아래 print는 그대로 둬요.']),
        analysis('preview', '보여 줄 행 수만 바꿔 봐요',
            '아까 df에는 전체 표가 들어 있었죠?\nhead는 표의 앞부분을 보여 줘요.\nhead(1)은 앞의 한 행을 골라요.',
            '먼저 실행해서 한 행을 확인하세요.\n괄호 안의 1만 3으로 바꾸세요.\n다시 실행해서 앞의 세 행을 비교해요.',
            'df.head(1)', 'df.head(3)', 'AUTO', caution='head는 보여 줄 앞부분을 골라요. 원본 행을 삭제하지 않아요.', hints=['df.head(3)으로 바꿔요.']),
        analysis('column', '방문 횟수만 세로로 꺼내요',
            '이번에는 행 대신 열을 골라요.\ndf[\'channel\']은 접속 경로 열을 꺼내요.\n대괄호 안에 열 이름을 글자로 넣어요.',
            '먼저 접속 경로를 출력해 보세요.\nchannel을 visits로 바꾸세요.\n방문 횟수만 나오는지 확인하세요.',
            "df['channel']", "df['visits']", 'AUTO', caution='열 이름은 실제 표와 철자가 같아야 해요.', hints=['대괄호 안을 \'visits\'로 바꿔요.']),
        analysis('minutes', '이용 시간 열도 꺼내 봐요',
            '같은 방법으로 다른 열도 꺼낼 수 있어요.\nminutes는 이용 시간이에요.\nNaN은 아직 값이 없는 칸을 나타내요.',
            '이번에는 이용 시간 열을 꺼내세요.\n어느 기록의 시간이 비어 있는지 보세요.\n빈칸을 채우는 방법은 뒤에서 배워요.',
            "df['visits']", "df['minutes']", 'AUTO', caution='빈칸과 숫자 0은 뜻이 달라요.', hints=['열 이름을 minutes로 바꿔요.']),
        analysis('two-columns', '두 열을 작은 표로 골라요',
            '여러 열은 이름을 목록으로 묶어 골라요.\n[\'channel\', \'visits\']처럼 쉼표로 나눠요.\n바깥 대괄호는 표에서 고르는 역할이에요.',
            'channel 대신 minutes를 골라 보세요.\n방문 횟수와 이용 시간만 남기세요.\n열 순서는 visits, minutes 순서예요.',
            "df[['visits', 'channel']]", "df[['visits', 'minutes']]", 'AUTO', caution='두 열의 이름을 한 글자로 합치지 않아요.', hints=["df[['visits', 'minutes']]로 골라요."]),
        analysis('size-pair', '표의 크기를 한 쌍으로 봐요',
            '지금까지 표의 일부를 꺼내 봤어요.\nshape는 전체 표의 크기를 알려 줘요.\n(행 수, 열 수) 순서의 한 쌍이에요.',
            'result 줄의 df.head(3)을 df.shape로 바꾸세요.\n두 숫자를 표와 비교해 보세요.\nshape 뒤에는 괄호를 붙이지 않아요.',
            'df.head(3)', 'df.shape', 'AUTO', caution='shape의 앞은 행 수, 뒤는 열 수예요.', hints=['result = df.shape로 바꿔요.']),
        analysis('rows', '한 쌍에서 행 수만 꺼내요',
            '앞에서 크기는 (행 수, 열 수)였어요.\n한 쌍의 자리는 0부터 세요.\n[0]은 첫 값, [1]은 두 번째 값이에요.',
            '먼저 실행해서 열 수를 확인하세요.\n[1]을 [0]으로 바꿔 행 수를 꺼내세요.\n방문 기록 하나가 한 행이라는 점을 떠올려요.',
            'df.shape[1]', 'df.shape[0]', 'AUTO', caution='첫 번째 값의 자리는 1이 아니라 0이에요.', hints=['df.shape[0]으로 바꿔요.']),
        analysis('columns-count', '이번에는 열 수를 꺼내요',
            '같은 크기 쌍에서 다른 값을 골라 봐요.\n열은 방문 기록의 특성을 담고 있어요.',
            '행 수 대신 전체 열 수를 출력하세요.\n자리 번호 하나만 바꾸면 돼요.',
            'df.shape[0]', 'df.shape[1]', 'AUTO', caution='행 수와 열 수가 같아도 자리의 의미는 달라요.', hints=['두 번째 값은 [1]로 꺼내요.']),
        analysis('preview-column', '앞의 세 기록에서 방문 횟수만',
            '앞에서 배운 행 선택과 열 선택을 조합해요.',
            '앞의 세 기록에서 visits 열만 꺼내세요.\n전체 기록을 출력하지 않게 해 보세요.',
            "df['visits']", "df.head(3)['visits']", 'AUTO', challenge=True,
            caution='전체 열을 꺼낸 것과 앞의 세 기록만 꺼낸 것을 비교해요.', hints=['앞부분을 고른 뒤 열을 꺼내 보세요.', "df.head(3)['visits']처럼 이어 써요."]),
        analysis('selected-size', '두 열만 고른 표에는 몇 열이 있을까요?',
            '표를 고른 다음 크기를 확인해요.\n원본 표의 크기와 구별해 보세요.',
            'visits와 minutes만 고른 표가 있어요.\n이 작은 표의 열 수만 출력하세요.\n배운 코드들을 조합해 보세요.',
            "df[['visits', 'minutes']]", "df[['visits', 'minutes']].shape[1]", 'AUTO', challenge=True,
            caution='원본 df의 크기를 구하면 질문이 달라져요.', hints=['선택한 표 뒤에 shape를 붙여요.', '크기 쌍에서 열 수의 자리는 [1]이에요.']),
    ])
    aice['revision']='v1.1.0'
    # The first sample output is generated by actual execution below.
    from principles_course.common import execute
    for t in aice['tasks']:
        t['tests'][0]['expected'] = execute(t, t['solution']).stdout.strip()

    engineer = lesson('engineer-java-state', '자바 실행 원리를 작은 변화로 확인해요',
        '실기 대비 코드 이해 연습이에요. 필수 문제 5개와 선택 도전 1개예요.',
        ['https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991'], [
        java('loop', '반복이 한 번 더 돌면', '반복 조건의 경계가 더하는 값을 바꿔요.',
            '1부터 n까지 더하도록 조건만 고치세요.\n작은 n으로 중간 값을 생각한 뒤 실행해요.',
            'static int solve(int n)', '// 합계는 0에서 시작해요.\nint sum=0;\n// 마지막 n도 포함해야 해요.\nfor(int i=1;i<n;i++) sum+=i;\nreturn sum;',
            'i<n', 'i<=n', 'Exercise.solve(in.nextInt())', [('4','10'),('1','1'),('6','21')], hints=['마지막 n도 포함하는 조건을 골라요.'], caution='미만은 마지막 n을 제외해요.'),
        java('alias', '두 이름이 같은 배열을 가리켜요', '배열을 대입하면 같은 배열을 함께 가리켜요.',
            'b를 바꿔도 a가 유지되게 고치세요.\n출력은 a의 첫 값이에요.',
            'static int solve(int value)', '// 원본과 별도 배열이 필요한 상황이에요.\nint[] a={value,2};\n// 대입과 복사의 차이를 확인해요.\nint[] b=a;\nb[0]=99;\nreturn a[0];',
            'int[] b=a;', 'int[] b=a.clone();', 'Exercise.solve(in.nextInt())', [('3','3'),('7','7')], hints=['새 배열을 만드는 clone을 써 보세요.'], caution='배열 이름을 대입해도 내용이 복사되지는 않아요.'),
        java('division', '자료형 변환은 언제 해야 할까요?', '정수 나눗셈 뒤에는 소수 부분이 이미 사라져요.',
            '나누기 전에 실수로 바꾸세요.\n정수 나눗셈 뒤 변환한 값과 비교해요.',
            'static double solve(int a,int b)', '// 먼저 계산한 값이 무엇인지 살펴봐요.\nreturn (double)(a/b);',
            '(double)(a/b)', '(double)a/b', 'Exercise.solve(in.nextInt(),in.nextInt())', [('7 2','3.5'),('9 4','2.25')], hints=['a만 먼저 double로 바꾸세요.'], caution='계산 뒤 변환해도 버린 소수 부분은 돌아오지 않아요.'),
        java('string', '문자열의 내용이 같은지 확인해요', '같은 내용과 같은 객체는 다른 조건이에요.',
            '문자열의 내용으로 비교하세요.\n새 객체 두 개를 비교하는 코드예요.',
            'static boolean solve(String word)', '// 내용은 같아도 별도 객체일 수 있어요.\nString a=new String(word);\nString b=new String(word);\n// 내용 비교를 할 자리를 찾아요.\nreturn a==b;',
            'return a==b;', 'return a.equals(b);', 'Exercise.solve(in.next())', [('java','true'),('code','true')], hints=['문자열 내용 비교는 equals를 써요.'], caution='==는 두 객체의 내용 비교가 아니에요.'),
        java('recursion', '호출이 끝나야 더할 수 있어요', '재귀 호출은 종료 조건에서 돌아오기 시작해요.',
            '1부터 n까지 더하는 재귀를 완성하세요.\nn이 3일 때 호출 순서를 생각해요.',
            'static int solve(int n)', '// 0에 도달하면 호출을 멈춰요.\nif(n==0) return 0;\n// 돌아온 값에 현재 n을 더해요.\nreturn solve(n-1);',
            'return solve(n-1);', 'return n+solve(n-1);', 'Exercise.solve(in.nextInt())', [('3','6'),('0','0'),('5','15')], hints=['아래 호출의 합계에 현재 n을 더해요.'], caution='종료 조건이 없으면 호출이 계속 쌓여요.'),
        java('challenge', '도전 · 선택한 값만 더해요', '조건과 누적을 조합해 새로운 규칙을 만들어요.',
            '1부터 n까지 짝수만 더하세요.\n홀수 n과 짝수 n을 모두 확인하세요.',
            'static int solve(int n)', '// 모든 수가 아닌 필요한 수만 더해요.\nint sum=0;\nfor(int i=1;i<=n;i++) {\n    // 조건을 만족할 때만 누적해요.\n    sum+=i;\n}\nreturn sum;',
            'sum+=i;', 'if(i%2==0) sum+=i;', 'Exercise.solve(in.nextInt())', [('6','12'),('5','6'),('1','0')], challenge=True, hints=['2로 나눈 나머지를 이용해요.', '나머지가 0일 때만 합계에 더해요.'], caution='합계를 나중에 나누는 것과 짝수만 더하는 것은 달라요.'),
    ])
    for course_id, title, description, item in [
        ('aice-associate', '에이스 Associate · 작은 실험으로 분석하기', '공식 범위를 참고한 자체 제작 첫 수업이에요. 전체 시험 대비 과정은 이어서 보강해요.', aice),
        ('engineer-practical', '정보처리기사 실기 · 원리부터 풀기', '자바 코드 이해부터 시작하는 자체 제작 첫 수업이에요. 전체 출제 범위는 이어서 보강해요.', engineer),
    ]:
        for t in item['tasks']:
            compile_narration(item, t)
        folder=OUT/course_id
        folder.mkdir(parents=True, exist_ok=True)
        raw=json.dumps(item,ensure_ascii=False,indent=2)+'\n'
        (folder/'lesson.json').write_text(raw,encoding='utf8',newline='\n')
        manifest=dict(schema_version=1,id=course_id,title=title,description=description,
            repository='jhs512/mq3-course-'+course_id,lessons=[dict(id=item['id'],title=item['title'],
            repository='jhs512/mq3-lesson-'+item['id'],revision=item['revision'],sha256=hashlib.sha256(raw.encode()).hexdigest(),
            prerequisites=[],required=True,review_enabled=False)])
        (folder/'course.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        print(f"BUILT {title}: {len(item['tasks'])} tasks",flush=True)


if __name__=='__main__':
    build()
