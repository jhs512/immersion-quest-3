from _python_final import make

START = '''rows = [[1, 2], [3, 4]]
default = 0
# 안쪽 목록까지 독립적으로 복사하세요.
copied = rows[:]
copied[0][0] = 9
counts = {"done": 2}
# 없는 키는 default로 읽고 사전에는 추가하지 마세요.
pending = counts.get("pending", 1)
print(rows[0][0], copied[0][0])
print(pending, "pending" in counts)
'''
SPEC = make('engineer-python-values', '중첩 목록을 독립적으로 고치고 없는 키를 읽으세요',
    'copied의 첫 칸만 9로 고치고 rows는 보존하세요. pending 키가 없으면 default를 읽되 counts에 새 키를 만들지 마세요. 지금 출력은 1 9와 0 False예요.',
    '얕은 복사의 내부 공유와 사전 기본값 조회를 함께 판단해요.', START,
    [('copied = rows[:]', 'copied = [row[:] for row in rows]', '각 안쪽 목록도 복사해 copied를 만드세요.'),
     ('counts.get("pending", 1)', 'counts.get("pending", default)', '없는 키의 기본값으로 default를 사용하세요.')],
    '1 9\n0 False',
    [dict(values=dict(rows=[[5, 6], [7, 8]], default=4), expected='5 9\n4 False')],
    [([['[row[:] for row in rows]', 'rows[:]']], '바깥 목록만 복사하면 내부 자료를 공유해요.'),
     ([['counts.get("pending", default)', 'counts.setdefault("pending", default)']], '조회가 사전에 새 키를 만들면 안 돼요.')],
    [([['[row[:] for row in rows]', '[list(row) for row in rows]']], '각 내부 목록을 새 list로 만들어도 돼요.')],
    'copied를 바꿨는데 원본도 9가 됐고 기본값도 1로 잘못 읽었어요.', '내부 목록을 복사해 원본을 보존했어요. 기본값 조회는 아직 고쳐야 해요.',
    '원본은 1이고 복사본만 9예요. 없는 키는 0으로 읽었고 새 키는 생기지 않았어요.',
    '조심하세요. get과 setdefault는 없는 키를 사전에 추가하는지에서 달라요.',
    probe='assert rows[0][0] != copied[0][0]\nassert "pending" not in counts')
SPEC['course'] = 'engineer'
