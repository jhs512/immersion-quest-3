from _python_final import make

START = '''def add(value, *, prefix, history=[]):
    history.append(prefix + str(value))
    return history[:]

first = add(1, prefix="A")
second = add(2, prefix="B")
given = ["start"]
third = add(3, prefix="C", history=given)
print(first)
print(second)
print(third, given is third)
'''
SPEC = make('engineer-python-calls', '생략한 기록 목록은 호출마다 새로 만드세요',
    'history를 생략한 두 호출은 별도 목록이어야 해요. 명시적으로 넘긴 given은 그대로 수정하고 반환하세요. prefix는 키워드 인수예요.',
    '가변 기본 인수의 공유를 없애면서 명시적으로 전달한 목록의 참조는 유지해요.', START,
    [('def add(value, *, prefix, history=[]):\n    history.append', 'def add(value, *, prefix, history=None):\n    if history is None:\n        history = []\n    history.append', '기본값을 None으로 바꾸고 None일 때만 새 목록을 만든 뒤 항목을 추가하세요.'),
     ('return history[:]', 'return history', '복사본 대신 항목을 추가한 바로 그 목록을 반환하세요.')],
    "['A1']\n['B2']\n['start', 'C3'] True", [],
    [([['if history is None:', 'if True:']], '직접 넘긴 목록은 새 것으로 바꾸면 안 돼요.')],
    [([['history is None', 'None is history']], 'None 동일성 비교의 양쪽 순서는 바꿔도 돼요.')],
    '두 번째 결과에 앞 호출의 A1이 섞이고 반환 목록도 given과 다른 객체예요.', '생략한 목록은 독립적이에요. 아직 세 번째 반환값은 given의 복사본이에요.',
    '첫 두 호출은 독립적이고 세 번째 호출은 넘겨준 given에 C3를 붙였어요.',
    '조심하세요. 매번 새 목록으로 덮어쓰면 호출자가 넘긴 given을 수정할 수 없어요.',
    first_error=None,
    probe='assert first is not second\nassert third is given\nassert len(first) == 1 and len(second) == 1')
SPEC['course'] = 'engineer'
