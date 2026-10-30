"""engineer-os: the final challenge's code-reading fields -> a coding challenge (2026-10-30 user decision).

The challenge showed a SJF example program and asked for its average wait, FIFO page faults and the
deadlock condition by name. It now asks for the two computations in that program: the SJF order and the
FIFO eviction. Prepared cases rerun with other jobs, reference strings and frame counts, so a typed
answer, arrival order (FCFS) and evicting the newest page fail. The deadlock-condition term stays
practised by steps 11-13; the other steps (hand calculations and concepts) are unchanged."""
from _kit import Script, code_step

PRD_SCOPE = ['3챕터·3단원·14스텝으로 같은 상황을 점진적으로 바꿔요.',
             '대기·반환 시간과 페이지·교착은 문서·표·조건으로 판단해요. 마지막 도전은 SJF 순서와 FIFO 페이지 교체를 Python 코드로 직접 써서 실행해요.']
PRD_GRADING = ['선택형 정답·오답·빈 답안과 해설 뒤 답안 복귀를 확인해요.',
               '표와 수치가 있는 문제는 별도 계산이나 실제 도구로 답을 대조해요.',
               '마지막 도전: 시작 코드는 실패해야 해요. 실제 Python으로 실행하고 다른 작업·참조열·프레임 수로 다시 실행해, 도착 순서로 실행한 답·가장 최근 페이지를 뺀 답·결과를 적은 답을 거절해요.']

o15 = '''jobs = {"P1": 6, "P2": 2, "P3": 4}
refs = [1, 2, 3, 4, 1, 2]
frames = 3
# 1) 이 줄을 고쳐 실행시간이 짧은 작업부터 순서를 정하세요. 모두 시각 0에 도착하는 비선점 SJF예요.
order = list(jobs)
time = 0
waits = []
for name in order:
    waits.append(time)
    time += jobs[name]
print(" ".join(order))
print(round(sum(waits) / len(waits), 6))
memory = []
faults = 0
for page in refs:
    if page not in memory:
        faults += 1
        if len(memory) == frames:
            # 2) 이 줄을 고쳐 가장 먼저 들어온 페이지를 빼세요(FIFO).
            memory.pop()
        memory.append(page)
print(faults)
'''
o15_sol = (o15.replace('order = list(jobs)\n', '# 실행시간(jobs의 값)이 짧은 작업부터 정렬해요. 앞 작업의 실행시간이 뒤 작업의 대기가 돼요.\norder = sorted(jobs, key=jobs.get)\n')
           .replace('            memory.pop()\n', '            # 목록 앞이 가장 먼저 들어온 페이지예요. pop()은 맨 뒤, 가장 최근 페이지를 빼요.\n            memory.pop(0)\n'))
p15 = (Script(o15)
       .say('마지막 도전이에요. SJF 순서와 FIFO 교체를 코드로 직접 써서 대기시간과 페이지 부재를 구해요.', 'text:SJF 순서와 FIFO 페이지 교체를 코드로 직접 써서 대기시간과 페이지 부재를 구해요.')
       .run('print(" ".join(order))', 'print(faults)')
       .say('P1 P2 P3, 4.666667, 4예요. 도착 순서로 실행했고, 새 페이지가 올 때 가장 최근 페이지를 뺐어요.', 'output')
       .patch('order = list(jobs)\n', 'order = sorted(jobs, key=jobs.get)\n', 'jobs를 실행시간 기준으로 정렬해요.')
       .run('print(" ".join(order))', 'print(faults)')
       .say('P2 P3 P1과 2.666667이에요. 대기시간 0, 2, 6의 평균 8/3이에요.', 'output')
       .patch('            memory.pop()\n', '            memory.pop(0)\n', 'pop()을 pop(0)으로 바꿔 맨 앞 페이지를 빼요.')
       .run('print(" ".join(order))', 'print(faults)')
       .say('페이지 부재는 6이에요. 4가 1을, 1이 2를, 2가 3을 차례로 밀어내 참조마다 부재가 났어요.', 'output')
       .say('조심하세요. 들어온 순서는 목록 앞부터예요. pop()은 방금 넣은 페이지를 빼서 FIFO가 아니에요.', 'code:memory.pop(0)'))

SPECS = [
    code_step('stp_7890e0b4-4fbe-4227-8b8b-16a903154e97', 'SJF 순서와 FIFO 교체를 코드로 끝까지 추적하세요',
              'SJF 순서와 FIFO 페이지 교체를 코드로 직접 써서 대기시간과 페이지 부재를 구해요.',
              '처음 코드는 도착 순서와 최근 페이지 교체로 P1 P2 P3, 4.666667, 4다. sorted(jobs, key=jobs.get)와 memory.pop(0)으로 고쳐 P2 P3 P1, 2.666667, 6을 확인한다. 채점은 다른 작업·참조열·프레임 수로 실행한다.',
              'SJF 순서와 FIFO 페이지 교체를 코드로 직접 써서 대기시간과 페이지 부재를 구해요.\n\n'
              'P1·P2·P3은 모두 시각 0에 도착하고 실행시간은 jobs의 값이에요. 비선점 SJF는 실행시간이 짧은 작업부터 끝까지 실행해요. '
              '별도 메모리는 빈 프레임 frames개에서 참조열 refs를 처리해요. FIFO는 프레임이 가득 찼을 때 가장 먼저 들어온 페이지를 빼요. '
              '`sorted(jobs, key=jobs.get)`는 값이 작은 키부터 정렬하고, `memory.pop(0)`은 목록 맨 앞을 빼요.',
              '두 주석의 지시대로 고치세요. 채점은 다른 작업·참조열·프레임 수로도 실행해요.',
              ['코드 실행을 눌러 수정 전 결과를 확인하세요.', '`order = list(jobs)`를 `order = sorted(jobs, key=jobs.get)`로 고치세요.',
               '`memory.pop()`을 `memory.pop(0)`으로 고치세요.', '다시 실행해 결과를 확인하고 작성한 코드를 제출하세요.'],
              o15, o15_sol, p15, {p15.actions[-1]['text']: 'FIFO와 최근 페이지 교체의 실제 차이를 말해요.'},
              cases=[{'jobs': {'A': 3, 'B': 1, 'C': 2, 'D': 5}, 'refs': [7, 0, 1, 2, 0, 3, 0, 4], 'frames': 3},
                     {'jobs': {'X': 4, 'Y': 4}, 'refs': [1, 2, 1, 3, 1], 'frames': 2}],
              reject=[([['order = sorted(jobs, key=jobs.get)\n', 'order = list(jobs)\n']], 'Arrival order (FCFS)'),
                      ([['            memory.pop(0)\n', '            memory.pop()\n']], 'Evicting the newest page')],
              accept=[([['order = sorted(jobs, key=jobs.get)\n', 'order = sorted(jobs, key=lambda name: jobs[name])\n']], 'lambda key')]),
]
