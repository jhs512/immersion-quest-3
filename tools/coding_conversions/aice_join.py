"""aice-join: 7 answer-picking steps -> coding steps (2026-10-29).

The JSON step is graded by rewriting regions.json with other files; the others vary the prepared
orders/lookup data through prepared cases (other row orders, missing and repeated members), so a pick by
row position, a typed list or the wrong join fail."""
from _kit import Script, code_step, file_variants_checker

OPENING = ['이 수업에서는 표를 이어 붙이는 일과 키로 연결하는 일을 직접 코드로 구별해요. 원본 행이 어떻게 남는지도 확인해요.',
           'JSON과 월별 배송 표를 읽고 합쳐요. 중복 키와 자료형, 결측 키도 직접 고쳐 점검해요.']
PRD_SCOPE = ['두 챕터·두 단원·아홉 스텝으로 같은 배송과 회원 조회를 연결해요.',
             'read_json·concat·merge(on·how)·결합 행 수·자료형 맞추기·결측 키 제외를 한 곳씩 직접 고쳐 쓰고 최종 분석에서 관측을 잃거나 늘리지 않게 해요.']
PRD_GRADING = ['직접 고친 코드를 실제 파이썬·판다스로 실행해 판정해요. 실행·해설만으로 성공시키지 않아요.',
               '다른 원본 행과 조회 누락·중복 자료에서 실제 merge 결과를 검사해요. 준비 자료나 JSON 파일을 바꿔 다시 실행해 기준 풀이와 비교하고, 행 위치로 붙인 답·글자로 적은 결과는 거절해요.',
               '마지막 도전(stp_b05f4187-a8de-4b39-9235-d20c619977f6): 실제 파이썬 출력과 다른 배송·조회 자료 세 가지로 채점해요. inner 결합, 한 달만 사용, 빈 지역을 세지 않기는 실패해요.']
PRD_NARRATION = ['같은 배송·회원의 관계를 유지하고 문제 조건 한 개씩 고쳐요.',
                 '행추가와결합·행위치·행손실·중복확장·형변환의미·결측매칭을 조심할 지점으로 짚어요.']

SUBMIT = '수정한 코드를 제출하세요.'
W = '실제 판다스 동작을 정확히 말해요.'

JSON = '[{"member_id":1,"zone":"north"},{"member_id":2,"zone":"south"}]\n'
OTHER_JSON = [{'regions.json': '[{"member_id":7,"zone":"west"}]\n'},
              {'regions.json': '[{"zone":"east","member_id":3},{"zone":"north","member_id":9},{"zone":"south","member_id":4}]\n'}]
s1 = ('import pandas as pd\n\n# 제공된 파일의 객체 한 개가 회원 한 행이에요.\n# 이 줄을 고쳐 JSON 파일을 JSON 읽기 기능으로 읽으세요.\n'
      'regions = pd.read_csv("regions.json")\nprint(regions.columns.tolist())\nprint(regions["zone"].tolist())\n')
s1_sol = s1.replace('regions = pd.read_csv("regions.json")', '# read_json은 객체 목록의 키를 열로, 객체 하나를 행 하나로 읽어요.\nregions = pd.read_json("regions.json", orient="records")')
n1 = (Script(s1)
      .say('regions.json은 회원 객체 두 개의 목록이에요. CSV 읽기 줄을 JSON 읽기로 고쳐야 해요.', 'text:regions 줄을 고쳐 JSON 파일을 JSON 읽기 기능으로 읽으세요.')
      .run('print(regions.columns', 'print(regions["zone"]', error='KeyError')
      .say('열 이름이 JSON 글자 조각으로 잘렸고 zone 열이 없어 KeyError예요. 쉼표로 나눠 읽었어요.', 'output')
      .patch('regions = pd.read_csv("regions.json")', 'regions = pd.read_json("regions.json", orient="records")', 'pd.read_json으로 바꾸고 orient="records"를 줘요.')
      .run('print(regions.columns', 'print(regions["zone"]')
      .say("['member_id', 'zone']과 ['north', 'south']예요. 두 열과 회원 두 행이에요.", 'output')
      .say('조심하세요. 파일 이름의 확장자보다 내용의 형식에 맞는 읽기 기능을 골라요.', 'code:pd.read_json'))

s2 = ('import pandas as pd\n\n# 같은 열의 다음 달 배송이에요.\nfirst_ids = [101, 102]\nsecond_ids = [103]\nfirst = pd.DataFrame({"order_id": first_ids})\nsecond = pd.DataFrame({"order_id": second_ids})\n'
      '# 이 줄을 고쳐 다음 달 배송을 아래에 이어 붙이고 행 번호를 새로 매기세요.\ncombined = first.merge(second, on="order_id", how="left")\n'
      'print(combined["order_id"].tolist())\nprint(combined.index.tolist())\n')
s2_sol = s2.replace('combined = first.merge(second, on="order_id", how="left")',
                    '# concat은 같은 열의 표를 아래로 쌓아요. ignore_index=True는 행 번호를 0부터 새로 매겨요.\ncombined = pd.concat([first, second], ignore_index=True)')
n2 = (Script(s2)
      .say('같은 열의 다음 달 배송을 아래에 이어 붙이려 해요. 키로 연결하는 merge 줄을 행을 쌓는 concat으로 고쳐야 해요.', 'text:combined 줄을 고쳐 다음 달 배송을 아래에 이어 붙이고 행 번호를 새로 매기세요.')
      .run('print(combined["order_id"]', 'print(combined.index')
      .say('[101, 102]와 [0, 1]이에요. merge는 첫 달 행에 맞는 키를 찾았을 뿐 103을 붙이지 않았어요.', 'output')
      .patch('combined = first.merge(second, on="order_id", how="left")', 'combined = pd.concat([first, second], ignore_index=True)', 'pd.concat([first, second], ignore_index=True)로 바꿔요.')
      .run('print(combined["order_id"]', 'print(combined.index')
      .say('[101, 102, 103]과 [0, 1, 2]예요. 두 달 배송이 한 표에 쌓였어요.', 'output')
      .say('조심하세요. ignore_index를 빼면 둘째 표의 행 번호 0이 그대로 남아 번호가 겹쳐요.', 'code:ignore_index=True'))

LOOK = ('import pandas as pd\n\n# 배송과 회원 조회는 행 순서가 서로 달라요.\norder_data = {"order_id": [101, 102, 103], "member_id": [2, 1, 3]}\n'
        'region_data = {"member_id": [1, 2], "zone": ["north", "south"]}\norders = pd.DataFrame(order_data)\nregions = pd.DataFrame(region_data)\n')
SHOW = 'print(joined["order_id"].tolist())\n# 표시용: 지역을 찾지 못한 칸은 unknown으로 보여요.\nprint(joined["zone"].fillna("unknown").tolist())\n'
LOOK_CASES = [{'order_data': {'order_id': [301, 302, 303, 304], 'member_id': [5, 5, 4, 6]}, 'region_data': {'member_id': [6, 4], 'zone': ['west', 'east']}},
              {'order_data': {'order_id': [401, 402], 'member_id': [1, 2]}, 'region_data': {'member_id': [2, 1, 3], 'zone': ['south', 'north', 'west']}}]
s3 = LOOK + '# 이 줄을 고쳐 행 위치가 아니라 member_id가 같은 회원의 지역을 붙이세요. 배송은 모두 남겨요.\njoined = orders.assign(zone=regions["zone"])\n' + SHOW
s3_sol = s3.replace('joined = orders.assign(zone=regions["zone"])', '# merge는 on에 적은 열의 값이 같은 행끼리 짝지어요. how="left"는 배송을 모두 남겨요.\njoined = orders.merge(regions, on="member_id", how="left")')
n3 = (Script(s3)
      .say('조회 표는 회원 1부터지만 첫 배송은 회원 2예요. 행 위치로 붙이는 줄을 같은 회원끼리 짝짓도록 고쳐야 해요.', 'text:joined 줄을 고쳐 행 위치가 아니라 member_id가 같은 회원의 지역을 붙이세요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('지역이 north, south, unknown이에요. 회원 2의 첫 배송에 조회 첫 행 north가 붙었어요.', 'output')
      .patch('joined = orders.assign(zone=regions["zone"])', 'joined = orders.merge(regions, on="member_id", how="left")', 'orders.merge(regions, on="member_id", how="left")로 바꿔요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('south, north, unknown이에요. 회원 2는 south, 회원 1은 north이고 회원 3은 조회에 없어요.', 'output')
      .say('조심하세요. 두 표의 행 순서는 보통 달라요. 같은 줄에 있다고 같은 회원이 아니에요.', 'code:on="member_id"'))

s4 = LOOK + '# 이 줄의 how를 고쳐 조회에 회원이 있는 배송만 남기세요.\njoined = orders.merge(regions, on="member_id", how="left")\n' + SHOW
s4_sol = s4.replace('joined = orders.merge(regions, on="member_id", how="left")', '# inner는 양쪽에 다 있는 키의 행만 남겨요.\njoined = orders.merge(regions, on="member_id", how="inner")')
n4 = (Script(s4)
      .say('조회에 회원 3이 없어요. 조회에 있는 회원의 배송만 남기도록 how를 고쳐야 해요.', 'text:joined 줄의 how를 고쳐 조회에 회원이 있는 배송만 남기세요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('배송 세 건이 남고 103의 지역은 unknown이에요. left는 왼쪽 배송을 모두 남겨요.', 'output')
      .patch('how="left"', 'how="inner"', 'how를 "inner"로 바꿔요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('[101, 102]와 south, north예요. 회원 3의 배송 103은 빠졌어요.', 'output')
      .say('조심하세요. inner는 짝이 없는 배송을 조용히 버려요. 결과 행 수를 원본과 비교해요.', 'code:how="inner"'))

DUP = LOOK.replace('region_data = {"member_id": [1, 2], "zone": ["north", "south"]}', 'region_data = {"member_id": [1, 1, 2], "zone": ["north", "west", "south"]}') \
    .replace('# 배송과 회원 조회는 행 순서가 서로 달라요.', '# 회원 1이 조회 표에 두 번 있어요.')
s5 = (DUP + 'joined = orders.merge(regions, on="member_id", how="left", sort=False)\nprint(len(orders))\n'
      '# 이 줄을 고쳐 원본 배송 수가 아니라 결합한 표의 행 수를 rows에 담으세요.\nrows = len(orders)\nprint(rows)\n')
s5_sol = s5.replace('rows = len(orders)\n', '# 조회 키가 겹치면 배송 한 건이 조회 두 행과 붙어 행이 늘 수 있어요.\nrows = len(joined)\n')
n5 = (Script(s5)
      .say('회원 1이 조회 표에 두 번 있어요. 결합한 표의 행 수를 rows에 담아 원본과 비교해야 해요.', 'text:rows 줄을 고쳐 원본 배송 수가 아니라 결합한 표의 행 수를 rows에 담으세요.')
      .run('print(len(orders))', 'print(rows)')
      .say('두 줄 모두 3이에요. 아직 원본 배송 수를 두 번 셌어요.', 'output')
      .patch('rows = len(orders)\n', 'rows = len(joined)\n', 'len(joined)로 결합한 표를 세요.')
      .run('print(len(orders))', 'print(rows)')
      .say('3과 4예요. 회원 1의 배송 102가 north와 west 두 행에 붙어 한 행이 늘었어요.', 'output')
      .say('조심하세요. left도 행 수가 같다고 보장하지 않아요. 조회 키가 한 번씩인지 validate="many_to_one"으로 검사할 수 있어요.', 'code:rows = len(joined)'))
DUP_CASES = [{'order_data': {'order_id': [301, 302], 'member_id': [4, 4]}, 'region_data': {'member_id': [4, 4, 4], 'zone': ['a', 'b', 'c']}},
             {'order_data': {'order_id': [401, 402, 403], 'member_id': [1, 2, 3]}, 'region_data': {'member_id': [1, 2, 3], 'zone': ['n', 's', 'w']}}]

TYPE = LOOK.replace('region_data = {"member_id": [1, 2], "zone": ["north", "south"]}', 'region_data = {"member_id": ["1", "2"], "zone": ["north", "south"]}') \
    .replace('# 배송과 회원 조회는 행 순서가 서로 달라요.', '# 배송 키는 정수, 조회 키는 문자예요. 이 실습의 회원번호는 앞자리 영 없이 같은 정수를 뜻해요.')
s6 = TYPE + '# 이 줄을 고쳐 조회 키를 배송 키와 같은 정수로 바꾸세요.\nregions["member_id"] = regions["member_id"]\njoined = orders.merge(regions, on="member_id", how="left", validate="many_to_one", sort=False)\n' + SHOW
s6_sol = s6.replace('regions["member_id"] = regions["member_id"]\n', '# 같은 번호라는 약속을 확인했으니 astype(int)로 자료형을 맞춰요.\nregions["member_id"] = regions["member_id"].astype(int)\n')
n6 = (Script(s6)
      .say('배송 키는 정수, 조회 키는 문자예요. 같은 번호라는 약속을 확인했으니 조회 키를 정수로 맞춰야 해요.', 'text:regions["member_id"] 줄을 고쳐 조회 키를 배송 키와 같은 정수로 바꾸세요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]', error='ValueError')
      .say('ValueError예요. 정수 열과 문자 열은 merge 키로 맞추지 않아요.', 'output')
      .patch('regions["member_id"] = regions["member_id"]\n', 'regions["member_id"] = regions["member_id"].astype(int)\n', '뒤에 .astype(int)를 붙여요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('south, north, unknown이에요. 문자 "2"가 정수 2로 바뀌어 회원 2와 짝지어졌어요.', 'output')
      .say('조심하세요. "01"처럼 앞자리 영이 뜻을 가진 번호라면 정수로 바꾸면 안 돼요. 키의 약속을 먼저 확인해요.', 'code:.astype(int)'))
TYPE_CASES = [{'order_data': {'order_id': [301, 302, 303], 'member_id': [7, 8, 7]}, 'region_data': {'member_id': ['8', '7'], 'zone': ['east', 'west']}},
              {'order_data': {'order_id': [401], 'member_id': [5]}, 'region_data': {'member_id': ['6'], 'zone': ['south']}}]

s7 = ('import pandas as pd\n\n# 양쪽에서 회원을 알 수 없는 키가 나타났어요.\norder_data = {"member_id": [None, 2], "order_id": [101, 102]}\n'
      'region_data = {"member_id": [None, 2], "zone": ["unverified", "south"]}\norders = pd.DataFrame(order_data)\nregions = pd.DataFrame(region_data)\n'
      '# 이 줄을 고쳐 회원 키가 비어 있는 조회 행은 빼고 연결하세요.\nlookup = regions\njoined = orders.merge(lookup, on="member_id", how="left")\n'
      'print(joined["order_id"].tolist())\nprint(joined["zone"].fillna("unknown").tolist())\n')
s7_sol = s7.replace('lookup = regions\n', '# 빈 키끼리 붙은 것은 같은 회원이라는 확인이 아니에요. 빈 키 행은 조회에서 빼요.\nlookup = regions.dropna(subset=["member_id"])\n')
n7 = (Script(s7)
      .say('판다스는 양쪽의 빈 회원 키를 서로 붙여요. 빈 키 조회 행은 빼고 연결하도록 lookup 줄을 고쳐야 해요.', 'text:lookup 줄을 고쳐 회원 키가 비어 있는 조회 행은 빼고 연결하세요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('배송 101의 지역이 unverified예요. 빈 키끼리 짝지어졌어요.', 'output')
      .patch('lookup = regions\n', 'lookup = regions.dropna(subset=["member_id"])\n', 'regions.dropna(subset=["member_id"])로 빈 키 행을 빼요.')
      .run('print(joined["order_id"]', 'print(joined["zone"]')
      .say('101은 unknown, 102는 south예요. 배송은 모두 남고 확인된 회원만 지역이 붙었어요.', 'output')
      .say('조심하세요. 빈 키가 붙었다고 같은 회원임이 확인된 게 아니에요. 결측 키는 따로 검토해요.', 'code:dropna(subset=["member_id"])'))
NULL_CASES = [{'order_data': {'member_id': [3, None, None], 'order_id': [201, 202, 203]}, 'region_data': {'member_id': [None, 3], 'zone': ['guess', 'west']}},
              {'order_data': {'member_id': [None], 'order_id': [301]}, 'region_data': {'member_id': [None, None], 'zone': ['a', 'b']}}]

SPECS = [
    code_step('stp_b015b8bc-0755-4719-a9e6-1c0a3a8f93b0', 'read_json으로 JSON 회원 파일을 표로 읽으세요', 'JSON 객체 목록을 행과 열이 있는 표로 읽어요.',
              'read_csv로 읽은 regions.json은 열이 JSON 조각으로 잘리고 zone이 없다. pd.read_json(orient="records")로 고쳐 member_id·zone 두 열을 확인한다. 채점은 regions.json을 다른 파일로 바꿔 기준 풀이와 비교한다.',
              'regions.json은 회원 객체의 목록이에요. 객체 하나가 회원 한 행이고 객체의 키가 열 이름이에요. `pd.read_json(파일, orient="records")`가 이런 목록을 표로 읽어요.',
              'regions 줄을 고쳐 JSON 파일을 JSON 읽기 기능으로 읽으세요. 채점은 regions.json의 내용을 바꿔서도 실행해요.',
              ['코드 실행을 눌러 KeyError가 나오는지 확인하세요.', '`pd.read_csv("regions.json")`을 `pd.read_json("regions.json", orient="records")`로 고치세요.', '코드 실행을 눌러 두 열과 지역 목록을 확인하세요.', SUBMIT],
              s1, s1_sol, n1, {n1.actions[-1]['text']: '실제 읽기 기능 선택 기준을 정확히 말해요.', n1.actions[2]['text']: '실제 read_csv 결과(조각난 열·KeyError)를 정확히 말해요.'},
              files={'regions.json': JSON}, checker=file_variants_checker(s1_sol, OTHER_JSON, '다른 JSON 파일에서도 같은 원리로 맞는 결과가 나와야 해요.'),
              reject=[([['print(regions["zone"].tolist())', "print(['north', 'south'])"]], 'Typing the zones')],
              accept=[([['regions = pd.read_json("regions.json", orient="records")', 'import json\nregions = pd.DataFrame(json.load(open("regions.json", encoding="utf-8")))']], 'json module and DataFrame')]),
    code_step('stp_1591fd5e-cdc1-4f7b-bfa5-6e6a6d43504f', 'concat으로 다음 달 배송을 아래에 이어 붙이세요', '같은 열의 표를 행 방향으로 쌓아요.',
              'merge는 키를 찾을 뿐 103을 붙이지 않아 [101, 102]다. pd.concat([first, second], ignore_index=True)로 고쳐 [101, 102, 103]과 [0, 1, 2]를 확인한다. 채점은 다른 두 달 자료로 실행한다.',
              '같은 열의 다음 달 배송을 아래에 이어 붙여요. `pd.concat([표1, 표2])`는 같은 열의 표를 아래로 쌓고, `merge`는 키 값으로 다른 표의 열을 옆에 붙여요. `ignore_index=True`는 행 번호를 새로 매겨요.',
              'combined 줄을 고쳐 다음 달 배송을 아래에 이어 붙이고 행 번호를 새로 매기세요. 채점은 다른 두 달 자료로도 실행해요.',
              ['코드 실행을 눌러 103이 빠졌는지 확인하세요.', '`first.merge(...)`를 `pd.concat([first, second], ignore_index=True)`로 고치세요.', '코드 실행을 눌러 세 건과 새 행 번호를 확인하세요.', SUBMIT],
              s2, s2_sol, n2, {n2.actions[-1]['text']: W}, cases=[{'first_ids': [201], 'second_ids': [202, 203, 204]}, {'first_ids': [5, 6, 7], 'second_ids': [8, 9]}],
              reject=[([['combined = pd.concat([first, second], ignore_index=True)', 'combined = pd.concat([first, second])']], 'Overlapping row numbers'),
                      ([['combined = pd.concat([first, second], ignore_index=True)', 'combined = pd.concat([second, first], ignore_index=True)']], 'Next month on top')],
              accept=[([['combined = pd.concat([first, second], ignore_index=True)', 'combined = pd.concat([first, second]).reset_index(drop=True)']], 'reset_index after concat')]),
    code_step('stp_d49ec054-3c11-4d99-bb8a-0bcf4479901a', 'merge(on="member_id")로 같은 회원의 지역을 붙이세요', '행 위치가 아니라 키 값이 같은 행끼리 연결해요.',
              'assign으로 붙인 지역은 행 위치로 붙어 회원 2에 north가 붙는다. orders.merge(regions, on="member_id", how="left")로 고쳐 south, north, unknown을 확인한다. 채점은 행 순서가 다른 자료로 실행한다.',
              '조회 표는 회원 1부터지만 첫 배송은 회원 2예요. `merge(조회, on="member_id")`는 member_id 값이 같은 행끼리 짝지어 열을 붙이고, `how="left"`는 왼쪽 배송을 모두 남겨요.',
              'joined 줄을 고쳐 행 위치가 아니라 member_id가 같은 회원의 지역을 붙이세요. 배송은 모두 남겨요. 채점은 행 순서가 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 첫 배송의 지역을 확인하세요.', '`orders.assign(zone=regions["zone"])`를 `orders.merge(regions, on="member_id", how="left")`로 고치세요.', '코드 실행을 눌러 회원별 지역이 맞는지 확인하세요.', SUBMIT],
              s3, s3_sol, n3, {n3.actions[-1]['text']: W}, cases=LOOK_CASES,
              reject=[([['joined = orders.merge(regions, on="member_id", how="left")', 'joined = orders.assign(zone=regions["zone"])']], 'By row position'),
                      ([['how="left")', 'how="inner")']], 'Dropping orders without a member')],
              accept=[([['joined = orders.merge(regions, on="member_id", how="left")', 'joined = orders.assign(zone=orders["member_id"].map(regions.set_index("member_id")["zone"]))']], 'map through a lookup Series')]),
    code_step('stp_7a3fb796-be6a-4a62-b9b6-354d2d8d8a53', 'how="inner"로 조회에 있는 회원의 배송만 남기세요', 'how에 따라 짝이 없는 행이 남는지 빠지는지 확인해요.',
              'how="left"는 배송 세 건을 남기고 103의 지역은 비어 있다. how="inner"로 고쳐 103이 빠진 [101, 102]를 확인한다. 채점은 다른 자료로 실행한다.',
              '조회에 회원 3이 없어요. `how`는 짝을 못 찾은 행을 어떻게 할지 정해요. `left`는 왼쪽 표(orders)의 행을 모두 남기고, `inner`는 양쪽에 다 있는 키의 행만 남겨요.',
              'joined 줄의 how를 고쳐 조회에 회원이 있는 배송만 남기세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 배송 세 건이 남는지 확인하세요.', '`how="left"`를 `how="inner"`로 고치세요.', '코드 실행을 눌러 103이 빠졌는지 확인하세요.', SUBMIT],
              s4, s4_sol, n4, {n4.actions[-1]['text']: '실제 inner 동작과 점검 습관을 정확히 말해요.'}, cases=LOOK_CASES,
              reject=[([['how="inner")', 'how="left")']], 'Keeping every order'),
                      ([['print(joined["order_id"].tolist())', 'print([101, 102])']], 'Typing the orders')],
              accept=[([['joined = orders.merge(regions, on="member_id", how="inner")', 'joined = orders.merge(regions, on="member_id")']], 'inner is the default')]),
    code_step('stp_c1a9c678-bb7c-402e-a934-c0fddc3169fc', 'len(joined)로 결합 뒤 늘어난 행을 세세요', '조회의 중복 키가 결합 행을 늘릴 수 있음을 세어 확인해요.',
              '회원 1이 조회에 두 번 있다. rows = len(orders)는 3이다. len(joined)로 고쳐 4를 확인한다. 채점은 중복 정도가 다른 자료로 실행한다.',
              '회원 1이 조회 표에 두 번 있어요. 배송 한 건의 키가 조회 두 행과 맞으면 두 행으로 붙어요. `sort=False`는 결과를 배송 순서대로 둬요.',
              'rows 줄을 고쳐 원본 배송 수가 아니라 결합한 표의 행 수를 rows에 담으세요. 채점은 중복이 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 두 수가 같은지 확인하세요.', '`rows = len(orders)`를 `rows = len(joined)`로 고치세요.', '코드 실행을 눌러 원본과 결합 행 수를 비교하세요.', SUBMIT],
              s5, s5_sol, n5, {n5.actions[-1]['text']: '실제 판다스 merge 검사 옵션을 정확히 말해요.'}, cases=DUP_CASES,
              reject=[([['rows = len(joined)\n', 'rows = len(orders)\n']], 'Original order count'),
                      ([['rows = len(joined)\n', 'rows = 4\n']], 'Typing the count')],
              accept=[([['rows = len(joined)\n', 'rows = joined.shape[0]\n']], 'shape[0]')]),
    code_step('stp_7b18e674-b85c-4a9e-881d-b0f2f3015164', 'astype(int)로 조회 키의 자료형을 맞추세요', '키의 뜻을 확인한 뒤 두 표의 키 자료형을 같게 맞춰요.',
              '정수 키와 문자 키를 merge하면 ValueError다. regions["member_id"].astype(int)로 고쳐 south, north, unknown을 확인한다. 채점은 다른 문자 키 자료로 실행한다.',
              '배송 키는 정수, 조회 키는 문자예요. 이 실습의 회원번호는 앞자리 영 없이 같은 정수를 뜻해요. 판다스는 1과 "1"을 같은 키로 맞춰 주지 않아요. `astype(int)`는 열을 정수로 바꿔요.',
              'regions["member_id"] 줄을 고쳐 조회 키를 배송 키와 같은 정수로 바꾸세요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 ValueError가 나오는지 확인하세요.', '오른쪽의 `regions["member_id"]` 뒤에 `.astype(int)`를 붙이세요.', '코드 실행을 눌러 회원별 지역을 확인하세요.', SUBMIT],
              s6, s6_sol, n6, {n6.actions[-1]['text']: '실제 키 자료형 판단 기준을 정확히 말해요.', n6.actions[2]['text']: '실제 판다스 오류(int64와 object 키 merge)를 정확히 말해요.'}, cases=TYPE_CASES,
              reject=[([['regions["member_id"] = regions["member_id"].astype(int)\n', 'regions["member_id"] = regions["member_id"]\norders["member_id"] = orders["member_id"].astype(str).str.zfill(2)\n']], 'Padding the other side so nothing matches'),
                      ([['print(joined["zone"].fillna("unknown").tolist())', "print(['south', 'north', 'unknown'])"]], 'Typing the zones')],
              accept=[([['regions["member_id"] = regions["member_id"].astype(int)\n', 'regions["member_id"] = pd.to_numeric(regions["member_id"])\n']], 'to_numeric')]),
    code_step('stp_614ada92-b83f-4718-90ec-e1d815dcdab9', 'dropna로 빈 회원 키는 빼고 연결하세요', '결측 키끼리 붙는 것과 같은 회원 확인을 구별해요.',
              '빈 키끼리 붙어 배송 101에 unverified가 붙는다. 조회에서 dropna(subset=["member_id"])로 빈 키 행을 빼고 연결해 101은 unknown, 102는 south를 확인한다. 채점은 다른 자료로 실행한다.',
              '양쪽에 회원을 알 수 없는 빈 키가 있어요. 판다스 merge는 양쪽의 빈 키도 서로 붙여요. `dropna(subset=["member_id"])`는 그 열이 비어 있는 행을 빼요.',
              'lookup 줄을 고쳐 회원 키가 비어 있는 조회 행은 빼고 연결하세요. 배송은 모두 남겨요. 채점은 다른 자료로도 실행해요.',
              ['코드 실행을 눌러 배송 101의 지역을 확인하세요.', '`lookup = regions`를 `lookup = regions.dropna(subset=["member_id"])`로 고치세요.', '코드 실행을 눌러 101이 unknown인지 확인하세요.', SUBMIT],
              s7, s7_sol, n7, {n7.actions[-1]['text']: '실제 판다스 결측 키 동작과 검토 습관을 정확히 말해요.'}, cases=NULL_CASES,
              reject=[([['lookup = regions.dropna(subset=["member_id"])\n', 'lookup = regions\n']], 'Empty keys still match'),
                      ([['joined = orders.merge(lookup, on="member_id", how="left")', 'joined = orders.dropna(subset=["member_id"]).merge(lookup, on="member_id", how="left")']], 'Dropping the orders too')],
              accept=[([['lookup = regions.dropna(subset=["member_id"])\n', 'lookup = regions[regions["member_id"].notna()]\n']], 'notna filter')]),
]
