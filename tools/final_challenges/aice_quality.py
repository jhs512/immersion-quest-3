"""aice-quality final challenge: drop only unmeasured times, keep each order's last revision, keep real zeros, then summarize."""
from _common import Script, todo, ids, next_revision

KEY = 'aice-quality'
UNIT, STEP = ids(KEY)
CLEAN_TODO = 'clean = df  # 시간이 있는 배송에서 주문별 마지막 수정본만 남기세요.'
STARTER = f'''# 표를 다룰 판다스를 불러와요.
import pandas as pd
# None은 측정하지 못한 시간이에요. 0은 실제 0분이에요. 같은 주문은 파일 아래쪽이 나중 수정본이에요.
data = {{"order_id": [101, 102, 103, 103, 104, 105], "minutes": [12, None, 30, 42, 0, 25], "note": [None, "ok", "ok", "ok", "ok", None]}}
df = pd.DataFrame(data)
{CLEAN_TODO}
print(clean["order_id"].tolist())
print(clean["minutes"].tolist())
# 남긴 건수와 평균 시간이에요.
print(len(clean), clean["minutes"].mean())
'''
CLEAN_WRONG = 'clean = df.dropna().drop_duplicates(subset=["order_id"], keep="last")'
CLEAN = '''# 빈 메모는 허용해요. 시간 열의 빈값만 기준으로 빼요.
clean = df.dropna(subset=["minutes"])
# 같은 주문은 마지막 수정본만 남겨요.
clean = clean.drop_duplicates(subset=["order_id"], keep="last")'''
SOLUTION = STARTER.replace(CLEAN_TODO, CLEAN)

s = Script(STARTER)
s.say('마지막 도전이에요. 시간을 측정하지 못한 배송만 빼고, 같은 주문은 마지막 수정본만 남긴 뒤 건수와 평균을 보고해요.',
      'text:0분은 실제 시간이라 남겨요.')
s.run()
s.say('여섯 행이 그대로예요. 빈 시간과 같은 주문 103이 두 번 있어요.', 'output')
s.patch(CLEAN_TODO, CLEAN_WRONG, '빈값을 dropna로 빼고 중복을 지워 볼게요.')
s.run()
s.say('103과 104만 남았어요. 메모가 빈 101과 105까지 사라졌어요.', 'output')
s.patch(CLEAN_WRONG, CLEAN, '빈값 검사를 시간 열로 좁혀요.')
s.run()
s.say('101, 103, 104, 105가 남고 103은 42분이에요. 0분인 104도 남아 4건, 평균 19.75예요.', 'output')
s.say('조심하세요. 0분을 빈값처럼 빼면 실제로 바로 끝난 배송이 사라져 평균이 커져요.', 'code:clean = df.dropna(subset=["minutes"])')

GOAL = ('자, 마지막 도전이에요. 배송 표 df에 측정하지 못한 시간(None)과 같은 주문의 수정본이 섞여 있어요.\n\n'
        '시간이 빈 배송만 빼요. 메모가 빈 것은 괜찮아요. 0분은 실제 시간이라 남겨요. 같은 주문은 파일 아래쪽의 마지막 수정본만 남겨요. '
        '그 결과를 clean으로 두면 주문 번호, 시간, 건수와 평균이 출력돼요. 지금 자료이면 `[101, 103, 104, 105]`, `[12.0, 42.0, 0.0, 25.0]`, `4 19.75`예요. '
        '채점은 다른 자료로도 실행해요.\n\n'
        + todo('코드 실행을 눌러 지금 출력을 확인하세요.',
               '시간이 빈 배송만 빼세요.',
               '같은 주문은 마지막 수정본만 남기세요.',
               '다시 실행해 0분과 메모 없는 배송이 남았는지 확인한 뒤 제출하세요.'))

SPEC = dict(
    key=KEY, course='aice', revision=next_revision(KEY, 'aice-quality-5'),
    reason='결측 검사 대상(시간 열)과 허용할 빈값의 구별, 실제 0의 보존, 중복의 기준과 남길 수정본을 한 처리 흐름에서 함께 정하는 마지막 도전이에요.',
    grading='실제 파이썬 출력과 다른 자료 세 가지로 채점해요. 모든 열 dropna, 첫 수정본, 0분 제거는 실패해요.',
    unit=dict(id=UNIT, title='마지막 도전', objectives=['빈값·0·중복을 각각 맞게 처리해요.'],
              premise='빈 시간과 수정본이 섞인 배송 표예요. 앞 스텝과 상관없이 바로 풀 수 있어요.'),
    step=dict(id=STEP, title='측정 못한 시간과 옛 수정본을 정리하세요',
              objectives=['시간 열의 빈값만 빼고 주문별 마지막 수정본을 남겨요.'],
              core_flow='준비 코드는 원래 표를 요약한다. 학생은 dropna(subset=["minutes"])와 drop_duplicates(subset=["order_id"], keep="last")를 쓴다. '
                        '해설은 모든 열 dropna로 메모 없는 배송이 사라지는 실제 결과를 보여 준다. 채점: 0분만 있는 자료, 수정본 세 개, 모두 측정된 자료.'),
    task=dict(id=STEP, title='측정 못한 시간과 옛 수정본을 정리하세요', language='python', goal=GOAL,
              starter_code=STARTER, solution=SOLUTION, required=True,
              tests=[dict(input='', expected='[101, 103, 104, 105]\n[12.0, 42.0, 0.0, 25.0]\n4 19.75')], narration=s.actions),
    prepared_cases=[dict(values=dict(data={'order_id': [1, 2], 'minutes': [0, None], 'note': [None, None]}), expected='[1]\n[0.0]\n1 0.0'),
                    dict(values=dict(data={'order_id': [7, 7, 7], 'minutes': [10, 20, 35], 'note': ['a', None, 'c']}), expected='[7]\n[35]\n1 35.0'),
                    dict(values=dict(data={'order_id': [3, 4, 3], 'minutes': [5, 15, None], 'note': [None, 'x', 'y']}), expected='[3, 4]\n[5.0, 15.0]\n2 10.0')],
    cases=dict(expected_outputs=['[101, 102, 103, 103, 104, 105]\n[12.0, nan, 30.0, 42.0, 0.0, 25.0]\n6 21.8',
                                 '[103, 104]\n[42.0, 0.0]\n2 21.0',
                                 '[101, 103, 104, 105]\n[12.0, 42.0, 0.0, 25.0]\n4 19.75'],
               reject=[([['clean = df.dropna(subset=["minutes"])', 'clean = df.dropna()']], 'An empty note is allowed'),
                       ([['keep="last"', 'keep="first"']], 'The last revision is the one to keep'),
                       ([['clean = df.dropna(subset=["minutes"])', 'clean = df.dropna(subset=["minutes"])\nclean = clean[clean["minutes"] > 0]']], 'Zero minutes is a real time')],
               accept=[([['clean = df.dropna(subset=["minutes"])', 'clean = df[df["minutes"].notna()]']], 'notna selects the same rows')]),
    review={'조심하세요. 0분을 빈값처럼 빼면 실제로 바로 끝난 배송이 사라져 평균이 커져요.':
            '이 수업 1번의 빈값과 0의 구별을 이 도전의 요약 결과로 말해요. 채점의 0분 사례가 잡아요.'},
)
