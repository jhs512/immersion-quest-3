"""Independent foundations for the two certificates; no shared lesson identities."""
import json
from principles_course.common import code, java, lesson, python, task


def py(id,title,principle,goal,starter,before,after,*,caution,hints,scenarios=None,challenge=False):
    t=python(id,title,principle,goal,starter,before,after,[('','')],caution=caution,hints=hints,challenge=challenge)
    scenarios=scenarios or [{}]
    # Change only the first prepared assignment to each input name. Equivalent
    # solutions pass; a memorized print is rejected when the prepared values change.
    t['checker']=code('''
        import ast
        import contextlib
        import io
        import runpy
        import sys

        reference = REFERENCE
        cases = CASES
        source = open(sys.argv[1], encoding='utf8').read()
        class Inputs(ast.NodeTransformer):
            def __init__(self, values):
                self.values=values
                self.seen=set()
            def visit_Assign(self, node):
                if len(node.targets)==1 and isinstance(node.targets[0], ast.Name):
                    name=node.targets[0].id
                    if name in self.values and name not in self.seen:
                        self.seen.add(name)
                        node.value=ast.parse(repr(self.values[name]), mode='eval').body
                return node
        def execute(text, values):
            tree=ast.fix_missing_locations(Inputs(values).visit(ast.parse(text)))
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(compile(tree,'main.py','exec'),{'__name__':'__main__'})
            return output.getvalue().rstrip('\\n')
        for values in cases:
            expected=execute(reference,values)
            actual=execute(source,values)
            assert actual==expected, '준비 값이 바뀌었을 때도 같은 규칙으로 계산하세요.'
        print('코드의 실제 실행 결과를 확인했어요.')
    ''').replace('REFERENCE',repr(t['solution'])).replace('CASES',repr(scenarios))
    return t


def build():
    first=lesson('aice-python-first','분석을 시작하는 Python 첫 실행',
        'Python을 처음 봐도 괜찮아요. 글자·계산·이름을 작은 실험으로 익혀요.',
        ['https://aice.study/info/aice/asso'],[
      py('first-print','코드를 그대로 실행해 봐요',
        'Python 코드는 컴퓨터에게 할 일을 알려 줘요.\nprint는 괄호 안의 값을 화면에 보여 줘요.\n따옴표 안에 있는 것은 글자예요.',
        '먼저 코드 실행을 누르세요.\n출력된 글자를 확인하세요.\n따옴표 안을 분석 시작으로 바꾸세요.\n다시 실행해서 두 결과를 비교해요.',
        '# print의 괄호 안을 화면에서 확인해요.\nprint("자료 준비")',
        '"자료 준비"','"분석 시작"',caution='따옴표와 괄호는 그대로 두고 안의 글자만 바꿔요.',hints=['print("분석 시작")처럼 적어요.']),
      py('text-and-number','글자로 쓴 계산과 실제 계산',
        '앞 문제의 따옴표는 글자를 감쌌어요.\n숫자 계산은 따옴표 밖에 적어요.',
        '먼저 글자로 된 식을 출력해 보세요.\n식 양쪽의 따옴표만 지우세요.\n계산한 결과와 비교하세요.',
        '# 따옴표가 있으면 계산식도 글자예요.\nprint("6 + 4")',
        '"6 + 4"','6 + 4',caution='글자와 계산 결과는 화면에서 다르게 나와요.',hints=['print(6 + 4)로 바꿔요.']),
      py('group-calculation','괄호로 계산 순서를 바꿔요',
        '곱하기는 더하기보다 먼저 계산해요.\n괄호 안의 계산을 먼저 할 수 있어요.',
        '준비 코드를 먼저 실행하세요.\n2 + 3만 괄호로 묶어 보세요.\n숫자를 바꾸지 않고 결과를 바꿔요.',
        '# 곱하기와 더하기의 순서를 비교해요.\nprint(2 + 3 * 4)',
        '2 + 3 * 4','(2 + 3) * 4',caution='print의 괄호 안에 계산용 괄호를 더 넣어요.',hints=['print((2 + 3) * 4)로 묶어요.']),
      py('value-name','값에 붙인 이름을 써 봐요',
        'price = 6은 숫자 6을 price에 저장해요.\n이렇게 값을 저장하는 이름을 변수라고 해요.\n따옴표 없는 price는 저장한 값을 꺼내요.',
        '먼저 준비 코드를 실행하세요.\nprint 안의 price 양쪽 따옴표를 지우세요.\n이름과 그 이름에 저장한 값을 비교해요.',
        '# 오른쪽 값을 왼쪽 이름에 저장해요.\nprice = 6\n# 따옴표가 있으면 이름 자체를 출력해요.\nprint("price")',
        'print("price")','print(price)',scenarios=[{}, {'price':13},{'price':0}],caution='변수 이름을 글자로 감싸면 저장한 값을 꺼내지 않아요.',hints=['print(price)로 값을 꺼내요.']),
      py('update-value','한 이름의 값을 바꿀 수 있어요',
        '코드는 위에서 아래로 실행해요.\namount + 2를 계산한 뒤 다시 저장해요.\n=는 그 시점의 값을 저장하는 기호예요.',
        '지금은 숫자 6을 직접 출력하고 있어요.\n마지막 줄에서 amount의 값을 출력하세요.\n처음 값과 바뀐 값을 비교해요.',
        '# 처음 값을 저장해요.\namount = 6\n# 현재 값에 2를 더하고 다시 저장해요.\namount = amount + 2\n# 저장된 값을 꺼낼 자리를 찾아요.\nprint(6)',
        'print(6)','print(amount)',scenarios=[{}, {'amount':10},{'amount':-2}],caution='출력할 숫자를 직접 고치면 처음 값이 바뀔 때 틀려요.',hints=['마지막 줄은 print(amount)예요.']),
      py('read-order','바꾸기 전과 후를 모두 보세요',
        '출력은 그 줄이 실행될 때의 값을 보여 줘요.\n뒤에서 값을 바꿔도 앞의 출력은 바뀌지 않아요.',
        '준비 코드의 출력을 먼저 보세요.\n마지막 주석 아래에 print(amount)를 넣으세요.\n두 출력의 순서를 비교해요.',
        '# 첫 값을 출력해요.\namount = 6\nprint(amount)\n# 새로운 값을 저장해요.\namount = 9\n# 마지막 값도 확인해요.',
        '# 마지막 값도 확인해요.','# 마지막 값도 확인해요.\nprint(amount)',scenarios=[{}, {'amount':2},{'amount':12}],caution='뒤에서 저장한 값이 앞의 출력으로 거슬러 가지 않아요.',hints=['맨 아래에 print(amount)를 한 줄 넣어요.']),
      py('calculate-names','이름에 담긴 값끼리 계산해요',
        '계산식에는 숫자 대신 변수 이름을 넣을 수 있어요.\n가격과 개수를 곱하면 전체 금액을 구해요.',
        '더하기 기호 하나를 바꾸세요.\n가격에 개수를 곱해 전체 금액을 출력하세요.',
        '# 준비된 가격과 개수예요.\nprice = 6\ncount = 3\n# 두 이름의 값으로 전체 금액을 계산해요.\ntotal = price + count\nprint(total)',
        'price + count','price * count',scenarios=[{}, {'price':8,'count':2},{'price':3,'count':5}],caution='화면의 답을 직접 적는 대신 계산식을 고쳐요.',hints=['곱하기 기호는 *예요.']),
      py('new-name','보여 줄 값을 이름으로 골라요',
        '이름에는 글자도 숫자도 담을 수 있어요.\nprint에서 어떤 이름을 쓰는지 살펴봐요.',
        '지금은 분석 제목을 출력하고 있어요.\n방문 횟수가 나오게 이름 하나만 바꾸세요.',
        '# 글자와 숫자에 각각 이름을 붙여요.\nlabel = "방문 분석"\nvisits = 3\n# 필요한 이름을 골라 화면에 보여 줘요.\nprint(label)',
        'print(label)','print(visits)',scenarios=[{}, {'visits':7},{'visits':1}],caution='변수 이름과 따옴표 안의 글자를 구별해요.',hints=['print 안에 visits를 넣어요.']),
      py('discount-challenge','할인을 반영한 금액을 구해요',
        '배운 계산과 변수만 조합해 봐요.',
        '전체 금액에서 discount를 한 번 빼세요.\n준비된 숫자는 그대로 두세요.\n최종 금액을 계산하는 줄을 찾아 고쳐요.',
        '# 가격·개수·할인액을 준비했어요.\nprice = 6\ncount = 3\ndiscount = 2\n# 계산한 최종 금액을 저장해요.\ntotal = price * count\nprint(total)',
        'total = price * count','total = price * count - discount',scenarios=[{}, {'price':5,'count':4,'discount':3},{'price':8,'count':1,'discount':0}],challenge=True,
        caution='할인은 물건 하나마다가 아니라 전체 금액에서 한 번 빼요.',hints=['전체 금액을 구한 뒤 할인액을 빼요.', 'total에 저장하는 식을 고쳐요.']),
    ])
    values=lesson('aice-python-values','분석 코드의 값·목록·자리',
        '표 분석에 쓸 값과 목록을 익혀요. 작은 숫자와 짧은 목록으로 실행해요.',
        ['https://aice.study/info/aice/asso'],[
      py('decimal','나누었을 때 소수도 남아요','Python의 /는 소수 부분도 계산해요.\n//는 내림한 몫을 구해요.',
        '한 사람당 평균 방문 횟수를 구해요.\n//를 /로 바꾸고 차이를 확인하세요.',
        '# 전체 방문 수를 사람 수로 나눠요.\nvisits = 7\npeople = 2\n# 평균은 소수도 남겨야 해요.\nprint(visits // people)',
        'visits // people','visits / people',scenarios=[{}, {'visits':9,'people':4},{'visits':5,'people':2}],caution='평균을 정수로 잘라 버리면 정보가 사라져요.',hints=['나누기 기호 하나만 남겨요.']),
      py('number-conversion','숫자로 적힌 글자를 바꿔요','따옴표 안의 6은 글자예요.\nint는 정수로 적힌 글자를 숫자로 바꿔요.',
        '지금은 글자 뒤에 글자를 붙이고 있어요.\n글자를 정수로 바꾼 뒤 2를 더하세요.',
        '# 파일에서 글자로 읽은 횟수예요.\nraw = "6"\n# 숫자로 바꾸고 계산할 자리를 찾아요.\nprint(raw + "2")',
        'raw + "2"','int(raw) + 2',scenarios=[{}, {'raw':'13'},{'raw':'0'}],caution='숫자처럼 보여도 글자끼리의 +는 이어 붙이기예요.',hints=['int(raw)로 바꾼 다음 2를 더해요.']),
      py('list-first','여러 값을 목록에 담아요','대괄호 안의 값들을 쉼표로 나눠요.\n이런 순서 있는 목록을 리스트라고 해요.\n자리 번호는 0부터 세요.',
        '준비된 목록을 살펴봐요.\n[1]을 [0]으로 바꿔 첫 값을 꺼내세요.',
        '# 방문 횟수 세 개를 순서대로 담았어요.\nvisits = [2, 5, 3]\n# 대괄호 안의 자리 번호를 확인해요.\nprint(visits[1])',
        'visits[1]','visits[0]',scenarios=[{}, {'visits':[8,1,4]},{'visits':[7,6]}],caution='첫 값의 자리 번호는 1이 아니라 0이에요.',hints=['visits[0]을 출력해요.']),
      py('list-last','뒤에서 첫 값을 꺼내요','목록의 마지막 값은 [-1]로 꺼낼 수 있어요.\n목록 길이가 바뀌어도 마지막을 가리켜요.',
        '첫 값 대신 마지막 값을 꺼내세요.\n고정된 양수 자리 번호는 쓰지 마세요.',
        '# 목록의 길이는 자료에 따라 달라져요.\nvisits = [2, 5, 3]\n# 끝에서 고르는 자리를 써 봐요.\nprint(visits[0])',
        'visits[0]','visits[-1]',scenarios=[{}, {'visits':[8,1,4,6]},{'visits':[7,2]}],caution='[-1]은 마지막 값이에요. 숫자 1인 값을 찾는 기능은 아니에요.',hints=['끝에서 첫 번째 자리는 -1이에요.']),
      py('list-length','목록의 길이를 직접 세요','len은 목록에 값이 몇 개 있는지 알려 줘요.\n함수 이름 뒤 괄호 안에 목록을 넣어요.',
        '목록 자체 대신 목록 길이를 출력하세요.\nvisits를 len(visits)로 감싸 보세요.',
        '# 몇 개의 방문 기록인지 확인해요.\nvisits = [2, 5, 3]\n# 목록 전체와 길이를 비교해요.\nprint(visits)',
        'print(visits)','print(len(visits))',scenarios=[{}, {'visits':[8,1]},{'visits':[7,6,3,1]}],caution='값의 합계와 값의 개수는 달라요.',hints=['print(len(visits))로 개수를 구해요.']),
      py('dict-key','이름으로 값을 묶어 꺼내요','딕셔너리는 키와 값을 짝지어 저장해요.\n콜론 왼쪽은 키, 오른쪽은 값이에요.\nrecord[\'visits\']처럼 키로 꺼내요.',
        '접속 경로 대신 방문 횟수를 꺼내세요.\n대괄호 안의 키 이름만 바꾸세요.',
        '# 한 기록의 특성을 이름으로 묶었어요.\nrecord = {"channel": "web", "visits": 3}\n# 필요한 키를 골라 값을 꺼내요.\nprint(record["channel"])',
        'record["channel"]','record["visits"]',scenarios=[{}, {'record':{'channel':'app','visits':8}},{'record':{'channel':'web','visits':1}}],caution='키 이름은 준비된 딕셔너리와 같아야 해요.',hints=['키를 "visits"로 바꿔요.']),
      py('comparison','숫자를 비교하면 참·거짓이 나와요','>=는 왼쪽 값이 오른쪽 이상인지 비교해요.\n비교 결과는 True나 False로 나와요.',
        '방문 횟수가 4 이상인지 확인하세요.\n4도 포함하는 비교 기호로 바꾸세요.',
        '# 경계에 있는 값을 비교해요.\nvisits = 4\n# 비교는 숫자가 아닌 참·거짓을 만들어요.\nprint(visits > 4)',
        'visits > 4','visits >= 4',scenarios=[{}, {'visits':2},{'visits':7}],caution='이상과 초과는 경계값을 다르게 다뤄요.',hints=['4를 포함하는 기호는 >=예요.']),
      py('list-mean','합계와 개수를 조합해요','sum은 목록 값들을 모두 더해요.\n평균은 합계를 개수로 나눈 값이에요.',
        '방문 횟수의 합계를 먼저 확인하세요.\n그 합계를 목록 길이로 나누세요.',
        '# 비어 있지 않은 목록을 준비했어요.\nvisits = [2, 5, 3]\n# 합계에서 평균으로 계산을 바꿔요.\nprint(sum(visits))',
        'sum(visits)','sum(visits) / len(visits)',scenarios=[{}, {'visits':[8,4]},{'visits':[7,2,3,4]}],caution='자료 개수를 숫자 3으로 고정하지 마세요.',hints=['sum(visits)를 len(visits)로 나눠요.']),
      py('record-challenge','한 기록에서 계산을 완성해요','키로 꺼낸 값도 계산식에 쓸 수 있어요.',
        'record 안의 가격과 개수를 곱하세요.\n키 이름과 준비된 자료는 그대로 두세요.',
        '# 계산에 필요한 값을 한 기록에 묶었어요.\nrecord = {"price": 6, "count": 3}\n# 두 키의 값을 꺼내 전체 금액을 계산해요.\nprint(record["price"] + record["count"])',
        'record["price"] + record["count"]','record["price"] * record["count"]',scenarios=[{}, {'record':{'price':8,'count':2}},{'record':{'price':3,'count':5}}],challenge=True,
        caution='키 이름을 붙이는 계산이 아니라 저장한 숫자의 계산이에요.',hints=['딕셔너리에서 꺼낸 숫자를 곱해요.']),
    ])
    sources=['https://www.q-net.or.kr/pageLink.do?link=cst/cstReport&jmCd=1320&mcrtrNo=991']
    def j(id,title,principle,goal,body,before,after,caution,hints,challenge=False):
        source='class Main {\n    public static void main(String[] args) {\n'+''.join('        '+line+'\n' for line in code(body).splitlines())+'    }\n}\n'
        return task(id,title,principle,goal,source,before,after,language='java',tests=[('','')],caution=caution,hints=hints,challenge=challenge)
    engineer=lesson('engineer-program-first','출력·변수·대입을 처음 읽어요',
        '정보처리기사 코드 문제를 위한 출발점이에요. 긴 프로그램을 쓰지 않고 실행 순서부터 확인해요.',sources,[
      j('first-output','실행하면 어디에 무엇이 나올까요?',
        '프로그램은 적힌 명령을 실행해요.\n준비된 틀 안의 println이 값을 출력해요.\n처음에는 틀을 외워 쓸 필요가 없어요.',
        '준비 코드를 그대로 실행하세요.\n따옴표 안의 준비를 시작으로 바꾸세요.\n다시 실행하고 출력이 바뀌는지 보세요.',
        '// 따옴표 안의 글자를 화면에 보여 줘요.\nSystem.out.println("준비");','"준비"','"시작"','따옴표와 괄호는 그대로 두고 글자만 바꿔요.',['println 안의 글자를 "시작"으로 바꿔요.']),
      j('number-text','식처럼 보여도 글자일 수 있어요','따옴표 안은 글자 그대로예요.\n따옴표 밖의 숫자는 계산할 수 있어요.',
        '먼저 글자로 된 식을 출력하세요.\n6 + 4를 감싼 따옴표만 지우세요.',
        '// 글자 출력과 숫자 계산을 비교해요.\nSystem.out.println("6 + 4");','"6 + 4"','6 + 4','따옴표 안의 +는 계산하지 않아요.',['따옴표 없이 System.out.println(6 + 4);로 적어요.']),
      j('execution-order','위에서 아래로 출력해요','명령은 위에서 아래로 실행해요.\nprintln은 출력한 다음 줄을 바꿔요.',
        '준비 다음에 완료가 나오도록 고치세요.\n두 출력 줄의 순서를 바꿔 보세요.',
        '// 두 명령의 순서를 확인해요.\nSystem.out.println("완료");\nSystem.out.println("준비");',
        'System.out.println("완료");\n        System.out.println("준비");','System.out.println("준비");\n        System.out.println("완료");',
        '화면의 순서를 바꾸려면 명령의 순서를 바꿔요.',['준비를 출력하는 줄을 위로 옮겨요.']),
      j('named-number','정수에 이름을 붙여요','int는 정수를 담을 변수를 만들 때 써요.\nint score = 6은 6을 score에 저장해요.',
        'score라는 글자 대신 저장한 값을 출력하세요.\n출력 줄의 따옴표만 지우세요.',
        '// 정수를 담을 변수와 첫 값을 준비해요.\nint score = 6;\n// 이름과 이름에 저장된 값은 달라요.\nSystem.out.println("score");',
        '"score"','score','변수 이름을 따옴표로 감싸면 그냥 글자가 돼요.',['System.out.println(score);로 값을 꺼내요.']),
      j('assignment','대입은 값을 다시 저장해요','=는 오른쪽 값을 왼쪽 변수에 저장해요.\n다시 대입하면 그 변수의 현재 값이 바뀌어요.',
        '처음 값 대신 마지막 score를 출력하세요.\n위에서 아래로 값을 따라가 보세요.',
        '// 처음 저장한 값이에요.\nint score = 6;\n// 이 줄을 실행하면 현재 값이 바뀌어요.\nscore = 9;\nSystem.out.println(6);',
        'println(6)','println(score)','다시 저장한 값은 그다음 명령에서 사용돼요.',['마지막 줄에서 score를 출력해요.']),
      j('update','자기 값에 더한 뒤 다시 담아요','오른쪽의 score + 2를 먼저 계산해요.\n그 결과를 왼쪽 score에 다시 저장해요.',
        '덮어쓰는 코드와 더해 저장하는 코드를 비교해요.\nscore = 2를 score = score + 2로 바꾸세요.',
        '// 현재 값에서 계산을 시작해요.\nint score = 6;\n// 오른쪽을 먼저 계산하고 왼쪽에 저장해요.\nscore = 2;\nSystem.out.println(score);',
        'score = 2;','score = score + 2;','수학의 등식이 아니라 실행 순서가 있는 대입이에요.',['오른쪽에서 현재 score와 2를 더해요.']),
      j('two-variables','두 변수로 식을 만들어요','한 식에서 여러 변수의 값을 쓸 수 있어요.\n곱하기 기호는 *예요.',
        '가격과 개수를 곱해 전체 금액을 구하세요.\n준비된 변수의 값은 바꾸지 마세요.',
        '// 가격과 개수를 따로 저장해요.\nint price = 6;\nint count = 3;\n// 저장한 값으로 계산해요.\nSystem.out.println(price + count);',
        'price + count','price * count','답 숫자를 직접 적는 대신 계산식을 고쳐요.',['더하기를 곱하기로 바꿔요.']),
      j('before-after','바뀐 값이 앞의 출력도 바꿀까요?','출력은 그 명령이 실행될 때의 값이에요.\n나중의 대입은 이미 나온 출력을 바꾸지 않아요.',
        '마지막 주석 아래에 출력을 한 번 추가하세요.\n마지막에도 value를 출력해 보세요.\n두 숫자가 왜 다른지 생각해 보세요.',
        '// 바꾸기 전에 출력해요.\nint value = 6;\nSystem.out.println(value);\n// 새 값을 저장한 뒤에도 확인해요.\nvalue = 9;\n// 마지막 값을 출력해요.',
        '// 마지막 값을 출력해요.','// 마지막 값을 출력해요.\n        System.out.println(value);',
        '마지막 값 하나만 보고 앞의 출력까지 바꾸어 생각하지 마세요.',['마지막 줄에 System.out.println(value);를 넣어요.'],True),
    ])
    return [first,values,engineer]
