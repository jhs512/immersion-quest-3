"""Entry briefs from approved objectives and the actual lesson hierarchy, with authored inquiry prompts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = {
 'aice-python-start': '같은 코드를 다른 값으로 실행하면 무엇이 달라질까요?',
 'aice-python-conditions': '조건에 맞지 않는 자료는 어디서 걸러야 할까요?',
 'aice-python-api': '기능을 불러오는 것과 그 기능을 실행하는 것은 어떻게 다를까요?',
 'aice-table-csv': '파일의 글자와 표의 값은 언제 같고 언제 달라질까요?',
 'aice-selection': '열을 고르는 것과 행을 거르는 것은 어떻게 다를까요?',
 'aice-quality': '빈값을 0으로 바꾸면 자료의 뜻도 그대로일까요?',
 'aice-join': '두 표의 줄 순서가 같으면 같은 배송이라고 봐도 될까요?',
 'aice-plots': '그림의 축을 잘못 고르면 어떤 관계를 놓칠까요?',
 'aice-features': '모델이 맞힐 정답과 맞힐 때 사용할 입력은 어떻게 나눌까요?',
 'aice-split': '자료를 나누면서 입력과 정답의 짝은 어떻게 지킬까요?',
 'aice-leakage': '미래에 알게 될 값을 학습에 쓰면 평가는 왜 좋아질까요?',
 'aice-scale': '새 자료가 들어올 때마다 평균을 다시 구해도 될까요?',
 'aice-regression': '복잡한 예측이 단순한 평균 예측보다 나은지 어떻게 알까요?',
 'aice-regression-metrics': '큰 오차 하나를 어떤 지표가 더 크게 반영할까요?',
 'aice-classification': '확률의 첫 번째 열이 항상 관심 범주일까요?',
 'aice-classification-metrics': '경보를 많이 울리면 놓친 사례와 잘못 울린 경보는 어떻게 달라질까요?',
 'aice-models': '훈련 결과만 보고 모델을 고르면 무엇을 놓칠까요?',
 'aice-boosting': '학습률과 반복 수는 예측을 어떻게 바꿀까요?',
 'aice-tuning': '설정 탐색에 쓴 자료로 마지막 성능까지 보고해도 될까요?',
 'aice-tensorflow': '자료의 행 수와 입력 특성 수는 어떻게 다른가요?',
 'aice-neural-regression': '숫자 예측에 출력 활성화와 손실을 어떻게 맞출까요?',
 'aice-neural-classification': '정답의 표현이 달라지면 손실 함수도 달라질까요?',
 'aice-training': '마지막으로 학습한 상태가 항상 가장 좋은 상태일까요?',
 'aice-integration': '새 자료에 처음 보는 범주가 있어도 같은 전처리 흐름을 쓸 수 있을까요?',
 'engineer-c-start': '변수가 바뀌면 앞서 복사한 값도 함께 바뀔까요?',
 'engineer-c-conditions': '딱 나누어떨어지는 경계는 어느 조건에 들어갈까요?',
 'engineer-c-arrays': '마지막 칸과 동점 위치를 빠짐없이 다루려면 무엇을 비교할까요?',
 'engineer-c-functions': '작은 호출이 반환한 뒤 원래 호출은 어느 줄에서 이어질까요?',
 'engineer-c-pointers': '주소를 옮기는 것과 그 주소의 값을 고치는 것은 어떻게 다를까요?',
 'engineer-c-double-pointers': '호출자의 포인터를 바꾸려면 어느 층에 써야 할까요?',
 'engineer-c-structures': '자료와 계산 규칙을 각각 바꿀 수 있게 연결하려면 어떻게 할까요?',
 'engineer-java-flow': '조건의 순서와 반복 종료 위치가 결과를 어떻게 바꿀까요?',
 'engineer-java-references': '새 객체를 만들면 전달한 배열까지 새로 복사될까요?',
 'engineer-java-static': '참조를 하나 더 만들면 객체 수도 늘어날까요?',
 'engineer-java-polymorphism': '필드 선택과 메서드 선택은 같은 기준을 따를까요?',
 'engineer-python-values': '바깥 목록만 복사하면 안쪽 자료도 독립적일까요?',
 'engineer-python-calls': '호출 사이에 남는 기본 인수는 어떤 문제를 만들까요?',
 'engineer-db-model': '값이 있다는 것과 올바른 관계를 가진다는 것은 어떻게 다를까요?',
 'engineer-sql-select': '연결할 상대가 없는 행은 언제 남고 언제 사라질까요?',
 'engineer-sql-group': '행을 거르는 조건과 그룹을 거르는 조건은 어디에 둘까요?',
 'engineer-sql-change': '같은 변경문도 실행 순서가 바뀌면 결과가 달라질까요?',
 'engineer-db-storage': '중복을 줄이는 설계와 조회를 빠르게 하는 방법은 같은가요?',
 'engineer-requirements': '요구가 바뀌었을 때 어느 시험을 함께 바꿔야 할까요?',
 'engineer-design': '무엇이 달라지는지를 먼저 보면 패턴 선택이 쉬워질까요?',
 'engineer-server': '같은 시간에 실행된다는 이유만으로 한 모듈에 묶어도 될까요?',
 'engineer-interfaces': '응답을 못 받았으면 상대가 처리하지 않았다고 봐도 될까요?',
 'engineer-ui': '오류를 본 사용자가 다음 행동을 바로 알 수 있을까요?',
 'engineer-test-cases': '정상 경계 바로 밖의 값도 검사했나요?',
 'engineer-test-integration': '모든 문장을 지나면 모든 분기도 검사한 걸까요?',
 'engineer-security': '로그인했으면 모든 자료를 읽어도 될까요?',
 'engineer-os': '실행 순서와 메모리 교체 규칙을 바꾸면 어떤 비용이 달라질까요?',
 'engineer-network': '같은 IP의 프리픽스가 달라지면 소속 네트워크도 달라질까요?',
 'engineer-build': '버전을 올리는 기준은 수정한 코드 양일까요, 호환성일까요?',
 'engineer-mixed': '각 문제에서 답을 정하는 근거가 코드·자료·요구 중 무엇인가요?',
}


def for_course(course, items):
    result = {}
    challenges = json.loads((ROOT / f'tools/redesigned_courses/{course}/lesson-challenges.json').read_text(encoding='utf-8'))['lessons']
    for item in items:
        prd = json.loads((ROOT / item['authoring_prd']).read_text(encoding='utf-8'))
        # Keep the visible journey tied to the authored hierarchy instead of inventing a generic sequence.
        units = [u for ch in prd['chapters'] for u in ch['units'] if u['title'] != '마지막 도전']
        stages = [u['title'] for u in units]
        if len(stages) > 6:
            stages = [ch['title'] for ch in prd['chapters']]
        assumptions = ('실제 Python과 준비된 소규모 배송 자료를 사용해요. 모델 점수는 이 연습 자료의 결과이며 실제 서비스 성능을 보장하지 않아요.'
                       if course == 'aice' else
                       '수업에 제시한 코드·표·명세 조건 안에서 판단해요. 코드는 실제 실행하고, 계산·설계 문제는 답안 칸에 직접 적어요. SQL은 SQLite 기준이에요.')
        result[item['id']] = dict(learn=prd['objectives'],
            challenge=challenges[item['key']]['title'] if item['key'] in challenges else '수업에서 배운 조건을 마지막 문제에 적용하세요.',
            scenario=stages, constraints=[assumptions], question=QUESTIONS[item['key']])
    return result
