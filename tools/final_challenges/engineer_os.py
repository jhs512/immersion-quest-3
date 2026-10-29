from _engineer_final import fields

EXAMPLE = '''jobs = {"P1": 6, "P2": 2, "P3": 4}
order = sorted(jobs, key=jobs.get)
time = 0
waits = []
for name in order:
    waits.append(time)
    time += jobs[name]
print(" ".join(order))
print(waits)
'''
SPEC = fields('engineer-os', '작업 대기와 페이지 교체를 끝까지 추적하세요',
    'SJF 대기시간과 FIFO 페이지 부재를 계산하고 교착 예방 조건을 연결해요.',
    'P1·P2·P3은 모두 시각 0에 도착하고 실행시간은 6·2·4예요. 비선점 SJF로 실행하며 문맥 교환 비용은 0이에요. 별도 메모리는 빈 프레임 3개에서 참조열 1,2,3,1,4,2를 FIFO로 처리해요. 또 모든 작업이 자원을 같은 전역 순서로만 요청하게 바꿨어요.',
    [('wait', 'SJF의 평균 대기시간(소수 여섯째 자리로 반올림하거나 분수로)은?', ['2.666667', '8/3', '2.6666666666666665']),
     ('faults', '주어진 FIFO 참조열의 페이지 부재 횟수는?', ['4']),
     ('deadlock', '자원 요청 순서를 통일해 끊으려는 교착 상태 조건은?', ['순환 대기', '순환대기', 'circular wait'])],
    ['SJF 순서는 P2·P3·P1이고 대기시간은 0·2·6이에요. 평균은 8 나누기 3이에요.',
     '1·2·3에서 부재가 세 번, 다시 1은 적중해요. 4가 들어올 때 가장 먼저 들어온 1을 교체해 네 번째 부재예요. 마지막 2는 남아 있어 적중해요.',
     '모든 작업이 같은 순서로 자원을 요청하면 서로의 자원을 원으로 기다리는 순환 대기를 끊을 수 있어요.'],
    example=EXAMPLE, output='P2 P3 P1\n[0, 2, 6]')
