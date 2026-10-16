"""aice-python-tools: call functions with arguments, use returned values, import modules, read errors.

Exam code calls library functions with positional and named arguments and keeps what they return.
Each task changes one small place in prepared code and compares the runs; changed scenarios make
memorized output fail, and the listed mistakes are realistic beginner slips proven to fail.
"""
from certification_course.kit import py_task
from principles_course.common import lesson

SOURCES = ['https://aice.study/info/aice/asso', 'https://docs.python.org/3/library/functions.html',
           'https://docs.python.org/3/library/stdtypes.html#string-methods']


def build():
    return lesson('aice-python-tools', '분석 코드를 읽고 이어 쓰기',
        '시험 코드는 함수에 인자를 넣고 돌려받은 값을 써요. '
        '그 모양과 오류 읽기를 작은 실험으로 익혀요. 필수 문제 8개와 선택 도전 2개예요.',
        SOURCES, [
        py_task('round-digits', '함수에 값을 넣어 불러요',
            'round는 숫자를 반올림해 돌려주는 함수예요.\n'
            '함수 이름 뒤 괄호에 넣는 값을 인자라고 해요.\n'
            '인자가 둘이면 쉼표로 나눠요. `round(값, 자리 수)` 순서예요.',
            '먼저 실행해서 정수로 반올림된 평균을 보세요.\n'
            'round 괄호 안 average 뒤에 `, 1`을 넣으세요.\n'
            '다시 실행해서 소수 첫째 자리까지 나오는지 비교해요.',
            '''
            # 고객 세 명의 이용 시간(분)이에요.
            minutes = [12, 16, 9]
            # 합계를 개수로 나눠 평균을 구해요.
            average = sum(minutes) / len(minutes)
            # round가 돌려준 값을 화면에 보여 줘요.
            print(round(average))
            ''',
            'round(average)', 'round(average, 1)',
            scenarios=[{'minutes': [20, 7, 14]}, {'minutes': [31, 26, 40, 8, 15, 4]}],
            wrong=[('round(average)', 'round(average), 1'), ('round(average)', 'round(1, average)')],
            caution='1을 round 괄호 밖에 쓰면 print가 따로 출력해요.',
            hints=['`print(round(average, 1))`처럼 적어요.']),
        py_task('named-argument', '이름 붙은 인자로 방향을 바꿔요',
            'sorted는 목록을 작은 값부터 정렬한 새 목록을 돌려줘요.\n'
            '`reverse=True`처럼 이름=값 모양으로 넣는 인자도 있어요.\n'
            '`test_size=0.2`도 같은 모양이에요. 모델을 만드는 수업에서 만나요.',
            '먼저 실행해서 정렬 순서와 첫 값을 보세요.\n'
            'sorted 괄호 안 visits 뒤에 `, reverse=True`를 넣으세요.\n'
            '큰 값부터 정렬되고 첫 값이 바뀌는지 비교해요.',
            '''
            # 매장 네 곳의 방문 수예요.
            visits = [42, 17, 58, 33]
            # 정렬한 새 목록을 ranked에 받아요.
            ranked = sorted(visits)
            # 정렬한 목록과 그 첫 값을 확인해요.
            print(ranked)
            print(ranked[0])
            ''',
            'sorted(visits)', 'sorted(visits, reverse=True)',
            scenarios=[{'visits': [5, 91, 23]}, {'visits': [60, 60, 12, 75, 3]}], compare=('ranked',),
            wrong=[('sorted(visits)', 'sorted(visits, True)'), ('sorted(visits)', 'sorted(visits, Reverse=True)')],
            caution='이름 없이 True만 넣으면 TypeError가 나요.',
            hints=['`sorted(visits, reverse=True)`로 바꿔요.']),
        py_task('return-value', '직접 만든 함수가 값을 돌려줘요',
            '`def 이름(받을 값):`으로 함수를 직접 만들어요. 안쪽 줄은 네 칸 들여 써요.\n'
            '`return 값`은 그 값을 함수를 부른 줄로 돌려줘요. `result = to_hours(total)`이면 result에 담기죠.\n'
            'return이 없으면 값이 없다는 뜻의 None을 돌려줘요.',
            '먼저 실행해서 result에 무엇이 담겼는지 보세요.\n'
            '돌려줄 자리 주석 아래에 `return hours`를 hours 줄처럼 네 칸 들여 넣으세요.\n'
            '안 들여 쓰면 함수 밖의 return이라는 SyntaxError가 나요.\n'
            '다시 실행해서 시간 값이 나오는지 비교해요.',
            '''
            # 분을 시간으로 바꾸는 함수를 만들어요.
            def to_hours(minutes):
                # 받은 분을 60으로 나눠요.
                hours = minutes / 60
                # 계산한 값을 돌려줄 자리예요.

            # 이번 달 전체 이용 시간(분)이에요.
            total = 150
            # 함수에 total을 넣고 돌려준 값을 받아요.
            result = to_hours(total)
            print(result)
            ''',
            '    # 계산한 값을 돌려줄 자리예요.', '    # 계산한 값을 돌려줄 자리예요.\n    return hours',
            scenarios=[{'total': 90}, {'total': 45}], compare=('result',),
            wrong=[('    # 계산한 값을 돌려줄 자리예요.', '    # 계산한 값을 돌려줄 자리예요.\n    print(hours)'),
                   ('    # 계산한 값을 돌려줄 자리예요.', '    # 계산한 값을 돌려줄 자리예요.\nreturn hours')],
            caution='함수 안에서 print만 하면 result에는 None이 담겨요.',
            hints=['`return hours`를 hours 줄과 같은 깊이로 들여 써요.']),
        py_task('import-module', '모듈을 불러온 뒤에 써요',
            'math는 계산 함수를 모아 둔 모듈이에요. `math.sqrt`는 제곱근을 구해요.\n'
            '모듈은 `import math`로 먼저 불러와야 쓸 수 있어요.\n'
            '오류가 나면 마지막 줄의 오류 이름과 설명부터 읽어요.',
            '먼저 실행해서 마지막 줄의 NameError를 읽어 보세요.\n'
            '`is not defined`는 그 이름을 모른다는 뜻이에요. 뒤 물음은 import를 잊었냐는 말이고요.\n'
            '맨 위 주석 바로 아래 빈 줄에 `import math`를 적으세요.\n'
            '다시 실행해서 한 변의 길이를 확인해요.',
            '''
            # 쓸 모듈은 맨 위에서 불러와요.

            # 정사각형 매장의 넓이(제곱미터)예요.
            area = 49
            # 넓이의 제곱근이 한 변의 길이예요.
            side = math.sqrt(area)
            print(side)
            ''',
            '# 쓸 모듈은 맨 위에서 불러와요.', '# 쓸 모듈은 맨 위에서 불러와요.\nimport math',
            scenarios=[{'area': 81}, {'area': 2}], compare=('side',),
            wrong=[('print(side)', 'print(side)\nimport math'),
                   ('# 쓸 모듈은 맨 위에서 불러와요.', '# 쓸 모듈은 맨 위에서 불러와요.\nimport Math')],
            caution='import 줄을 쓰는 줄보다 아래에 두면 같은 오류가 나요.',
            hints=['첫 주석 바로 아래 빈 줄에 `import math`를 적어요.']),
        py_task('import-alias', '별명을 붙였으면 별명으로 불러요',
            '`import statistics as st`는 모듈에 st라는 별명을 붙여요.\n'
            '그다음부터는 `st.median`처럼 별명으로 불러요.\n'
            '`import pandas as pd` 뒤에 `pd.read_csv`를 쓴 것과 같아요.',
            '먼저 실행해서 NameError가 어떤 이름을 말하는지 보세요.\n'
            'import를 권하는 안내가 붙어도 import는 더 넣지 마세요.\n'
            '`statistics.median`을 별명을 쓴 모양으로 고치세요.\n'
            '다시 실행해서 크기순 가운데 값인 중앙값을 확인해요.',
            '''
            # 통계 모듈을 불러오고 st라는 별명을 붙여요.
            import statistics as st

            # 주문 금액이에요. 하나만 유난히 커요.
            orders = [12000, 9000, 15000, 98000, 11000]
            # 크기순으로 놓았을 때 가운데 값을 구해요.
            middle = statistics.median(orders)
            print(middle)
            ''',
            'statistics.median(orders)', 'st.median(orders)',
            scenarios=[{'orders': [5000, 7000, 64000]}, {'orders': [4000, 9000, 6000, 30000]}], compare=('middle',),
            wrong=[('statistics.median(orders)', 'st.median'), ('statistics.median(orders)', 'st.mean(orders)')],
            caution='괄호를 빼고 `st.median`만 쓰면 함수 자체가 출력돼요.',
            hints=['`st.median(orders)`로 고쳐요.']),
        py_task('type-error', '오류의 마지막 줄을 읽어요',
            '글자와 숫자를 +로 바로 이으면 TypeError가 나요.\n'
            '오류의 마지막 줄에 오류 이름과 이유가 나와요.\n'
            '`str(값)`은 값을 글자로 바꿔 돌려줘요.',
            '먼저 실행해서 마지막 줄의 TypeError를 읽어 보세요.\n'
            '이유에 나온 str은 글자, int는 정수예요. 글자엔 글자만 이을 수 있다는 말이죠.\n'
            'message 줄의 visits를 `str(visits)`로 감싸세요.\n'
            '다시 실행해서 안내 문장을 확인해요.',
            '''
            # 이번 주 방문 수예요.
            visits = 37
            # 안내 문장에 방문 수를 이어 붙여요.
            message = "이번 주 방문 " + visits + "회"
            print(message)
            ''',
            '+ visits +', '+ str(visits) +',
            scenarios=[{'visits': 5}, {'visits': 120}], compare=('message',),
            wrong=[('+ visits +', '+ "visits" +'), ('+ visits +', '+ int(visits) +')],
            caution='visits를 따옴표로 감싸면 숫자 대신 이름 글자가 붙어요.',
            hints=['`"이번 주 방문 " + str(visits) + "회"`처럼 적어요.']),
        py_task('string-methods', '글자를 정리하는 메서드',
            '값 뒤에 점을 찍고 부르는 함수를 메서드라고 해요.\n'
            '`strip()`은 앞뒤 공백을 지우고 `lower()`는 소문자로 바꿔요. 괄호가 빈 건 넣을 값이 없어서예요.\n'
            '둘 다 새 글자를 돌려줘요. 그래서 이어서 부를 수 있어요.',
            '먼저 실행해서 공백은 사라졌지만 대문자가 남은 걸 보세요.\n'
            '`strip()` 뒤에 `.lower()`를 이어 붙이세요.\n'
            '다시 실행해서 대괄호 안의 글자를 비교해요.',
            '''
            # 손으로 입력한 접속 경로예요. 공백과 대문자가 섞였어요.
            channel = " Web "
            # 정리한 새 글자를 clean에 담아요.
            clean = channel.strip()
            # 대괄호로 감싸면 남은 공백이 눈에 보여요.
            print("[" + clean + "]")
            ''',
            'clean = channel.strip()', 'clean = channel.strip().lower()',
            scenarios=[{'channel': ' APP'}, {'channel': 'Mobile Web '}], compare=('clean',),
            wrong=[('clean = channel.strip()', 'channel.lower()\nclean = channel.strip()'),
                   ('clean = channel.strip()', 'clean = channel.strip().lower')],
            caution='`channel.lower()`만 따로 적으면 channel은 그대로예요.',
            hints=['`clean = channel.strip().lower()`로 바꿔요.']),
        py_task('comma-number', '쉼표가 든 글자를 숫자로 바꿔요',
            '`int`는 쉼표가 섞인 글자를 못 바꿔서 ValueError를 내요.\n'
            '`replace(",", "")`는 모든 쉼표를 빈 글자로 바꾼 새 글자를 돌려줘요.\n'
            '쉼표를 지운 글자는 `int`로 바꿀 수 있어요.',
            '먼저 실행해서 마지막 줄의 ValueError를 읽어 보세요.\n'
            '`invalid literal`은 int가 못 바꾸는 글자라는 뜻이에요. 맨 끝에 그 글자가 보여요.\n'
            'int 괄호 안을 `price_text.replace(",", "")`로 바꾸세요.\n'
            '다시 실행해서 세 개를 산 금액을 확인해요.',
            '''
            # 표에서 복사한 가격이에요. 천 단위 쉼표가 있어요.
            price_text = "1,200"
            # 글자를 정수로 바꿔 계산에 써요.
            price = int(price_text)
            # 세 개를 산 금액이에요.
            print(price * 3)
            ''',
            'int(price_text)', 'int(price_text.replace(",", ""))',
            scenarios=[{'price_text': '15,000'}, {'price_text': '2,345,000'}, {'price_text': '980'}],
            compare=('price',),
            wrong=[('price = int(price_text)', 'price = price_text.replace(",", "")'),
                   ('price = int(price_text)', 'price_text.replace(",", "")\nprice = int(price_text)')],
            caution='replace만 하고 int를 빼면 글자가 세 번 이어 붙어요.',
            hints=['`int(price_text.replace(",", ""))`처럼 감싸요.']),
        py_task('argument-order', '도전 · 인자 순서를 맞춰요',
            '`round(값, 자리 수)`처럼 인자는 넣은 순서대로 짝지어요.\n'
            '직접 만든 함수도 def 줄의 순서대로 값을 받아요.',
            '방문 한 번당 이용 시간이 너무 작게 나와요.\n'
            '함수가 무엇을 무엇으로 나누는지 읽어 보세요.\n'
            '함수는 그대로 두고 원인을 찾아 고치세요.',
            '''
            # 방문 한 번당 이용 시간(분)을 구하는 함수예요.
            def per_visit(minutes, visits):
                # 첫째 인자를 둘째 인자로 나눠 돌려줘요.
                return minutes / visits

            # 한 고객의 전체 이용 시간과 방문 수예요.
            minutes = 90
            visits = 6
            # 두 값을 넣고 돌려준 값을 받아요.
            result = per_visit(visits, minutes)
            print(result)
            ''',
            'per_visit(visits, minutes)', 'per_visit(minutes, visits)',
            scenarios=[{'minutes': 50, 'visits': 4}, {'minutes': 84, 'visits': 12}], compare=('result',),
            wrong=[('per_visit(visits, minutes)', 'per_visit(visits, minutes=minutes)'),
                   ('result = per_visit(visits, minutes)', 'result = 15.0')],
            challenge=True,
            caution='`per_visit(visits, minutes=minutes)`는 minutes를 두 번 받아 TypeError가 나요.',
            hints=['def 줄의 괄호 순서와 부르는 줄의 순서를 비교해요.',
                   '부르는 줄의 두 인자를 def 줄과 같은 순서로 바꿔 적어요.']),
        py_task('clean-function', '도전 · 정리 함수가 값을 돌려주게',
            '앞에서 배운 쉼표 정리를 함수로 묶었어요.\n'
            '오류에 나오는 NoneType은 None 값의 종류 이름이에요.\n'
            '`unsupported operand`는 +로 계산할 수 없는 값이라는 뜻이에요.',
            '첫 달과 마지막 달의 매출을 더하려고 해요.\n'
            '오류가 난 줄과 원인이 있는 줄이 달라요.\n'
            '마지막 줄을 읽고 원인을 찾아 고치세요.',
            '''
            # 쉼표가 섞인 금액 글자를 정수로 바꾸는 함수예요.
            def to_number(text):
                # 쉼표를 지운 뒤 정수로 바꿔요.
                number = int(text.replace(",", ""))

            # 월별 매출 글자예요.
            sales = ["1,200", "950", "3,400"]
            # 첫 달과 마지막 달 매출을 더해요.
            total = to_number(sales[0]) + to_number(sales[-1])
            print(total)
            ''',
            '    number = int(text.replace(",", ""))', '    number = int(text.replace(",", ""))\n    return number',
            scenarios=[{'sales': ['2,500', '700']}, {'sales': ['12,000', '3,000', '800', '1,050']}],
            compare=('total',),
            wrong=[('    number = int(text.replace(",", ""))', '    number = int(text.replace(",", ""))\n    print(number)'),
                   ('    number = int(text.replace(",", ""))', '    number = int(text.replace(",", ""))\nreturn number')],
            challenge=True,
            caution='함수 안에서 print만 하면 더하는 줄에서 같은 오류가 나요.',
            hints=['None은 함수가 돌려준 값이 없을 때 나와요.', 'to_number 안에서 number를 돌려줘요.']),
    ])
