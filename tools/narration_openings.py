"""Compile orientation before authored detail, without changing executable actions.

Lesson introductions are hand-authored. Problem orientation comes from the exact
question, an existing problem-summary sentence, or the task's requested action.
The original, meaning-reviewed narration remains intact after this prefix.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / 'tools/redesigned_lessons/narration-openings.json'


def plain(text):
    return re.sub(r'\s+', ' ', re.sub(r'[`*]', '', text)).strip()


ENDINGS = {
    '맞추세요':'맞추는', '구하세요':'구하는', '적으세요':'적는',
    '덧붙이세요':'덧붙이는', '늘리세요':'늘리는', '꽂으세요':'꽂는', '던지세요':'던지는',
    '담으세요':'담는', '잡으세요':'잡는', '시키세요':'시키는', '마치세요':'마치는',
    '묶으세요':'묶는', '놓으세요':'놓는', '나누세요':'나누는', '놓아요':'놓는',
    '없애세요':'없애는', '멈추세요':'멈추는', '켜세요':'켜는', '지키세요':'지키는',
    '채워요':'채우는', '빼요':'빼는', '담아요':'담는', '합쳐요':'합치는',
    '돌려주세요':'돌려주는', '들어가세요':'들어가는', '나오세요':'나오는',
    '돌아오세요':'돌아오는', '가져오세요':'가져오는', '고르세요':'고르는',
    '만드세요':'만드는', '쓰세요':'쓰는', '읽으세요':'읽는', '넣으세요':'넣는',
    '찾으세요':'찾는', '막으세요':'막는', '고치세요':'고치는', '바꾸세요':'바꾸는',
    '남기세요':'남기는', '옮기세요':'옮기는', '두세요':'두는', '되돌리세요':'되돌리는',
    '세세요':'세는', '보세요':'보는', '모으세요':'모으는', '알리세요':'알리는',
    '지우세요':'지우는', '합치세요':'합치는', '보내세요':'보내는', '받으세요':'받는',
    '마세요':'않는', '하세요':'하는', '해요':'하는', '읽어요':'읽는', '나눠요':'나누는',
    '바꿔요':'바꾸는', '봐요':'보는', '골라요':'고르는', '찾아요':'찾는',
    '맞춰요':'맞추는', '남겨요':'남기는', '만들어요':'만드는', '모아요':'모으는',
    '적어요':'적는', '붙여요':'붙이는', '묶어요':'묶는', '줘요':'주는',
    '세어요':'세는', '배워요':'배우는', '가리켜요':'가리키는', '옮겨요':'옮기는',
    '써요':'쓰는', '넘겨요':'넘기는', '보내요':'보내는', '받아요':'받는',
    '넣어요':'넣는', '구해요':'구하는', '내세요':'내는',
    # Coding conversions (2026-10-29).
    '이으세요':'잇는', '끄세요':'끄는', '불러오세요':'불러오는','주세요':'주는', '매기세요':'매기는', '보이세요':'보이는', '정하세요':'정하는', '더하세요':'더하는',
    '부르세요':'부르는', '올리세요':'올리는', '붙이세요':'붙이는', '빼세요':'빼는', '세우세요':'세우는',
    '나타내세요':'나타내는', '그리세요':'그리는', '확인하세요':'확인하는', '맞히세요':'맞히는', '살리세요':'살리는',
    '숨기세요':'숨기는', '배우세요':'배우는', '드러내세요':'드러내는', '쓰세요':'쓰는', '넘기세요':'넘기는', '꺼내세요':'꺼내는', '줄이세요':'줄이는', '키우세요':'키우는', '섞으세요':'섞는',
    '기르세요':'기르는', '멈추게 하세요':'멈추게 하는', '고정하세요':'고정하는', '건네세요':'건네는', '거르세요':'거르는',
}


OVERVIEWS = {
    'stp_cb4ab2ac-d4b3-4bfe-8898-628a99e37a6c': 'statistics.mean 표기에서 mean이 어느 모듈의 기능인지 고르는 문제예요.',
    'stp_19a6791c-7c1a-426e-aedf-8f01dcbe45e4': '지역을 연결하면서 모든 배송 행을 남기는 결합 방법을 고르는 문제예요.',
    'stp_a09b00ec-aef9-4858-8da0-d5452ecd52e4': '범주별로 만든 표시 열에서 1과 0이 무엇을 뜻하는지 고르는 문제예요.',
    'stp_cc51dad9-21f5-4266-9f06-bc9efc70ac60': '배송 시간을 예측할 때 접수 시점에 아는 열만 입력으로 남기는 문제예요.',
    'stp_db7b18b4-f9b6-43ab-8866-6020301a260e': '맞혀야 할 배송 시간이 입력에 섞이면 무엇이 문제인지 고르는 문제예요.',
    'stp_08c238c2-b05f-4141-b396-b50dbb66d9c9': '예측 오차를 분 단위로 보고할 때 쓸 평가 지표를 고르는 문제예요.',
    'stp_42d6681d-b5bb-4ef3-bd4f-14ac71094689': '범주별 지표의 평균을 내는 방식에 따라 결과가 다른 이유를 고르는 문제예요.',
    'stp_49835fc1-36eb-4889-9ddb-1d9202724d2f': '교차 검증의 평균과 따로 남긴 최종 테스트 점수를 구별하는 문제예요.',
    'stp_d3301ce8-d065-4bed-85f5-b74781b6177a': '파이프라인 안에서 바꿀 설정이 어느 단계에 속하는지 이름으로 지정하는 문제예요.',
    'stp_c6f4dc1f-64dd-4e79-a180-537f51755d94': '음수도 가능한 값을 예측할 때 출력에 ReLU를 써도 되는지 판단하는 문제예요.',
    'stp_880b5026-588a-4edc-82bc-a538418dbe83': '수치 회귀 모델이 학습 중 줄여야 할 손실을 고르는 문제예요.',
    'stp_523413c5-c858-4ed3-825a-83e4d7231fd1': '모델 평가에서 출력된 손실과 지표가 무엇을 뜻하는지 구별하는 문제예요.',
    'stp_ee524730-dffa-42d4-bf7a-a4dd2f4c7fa0': '신경망 출력의 위치를 실제 범주 이름과 연결하는 문제예요.',
    'stp_b9326c99-7b82-4c59-9eea-97a24ee5dea9': '총 손실과 자료의 평균제곱오차가 다른 이유를 고르는 문제예요.',
    'stp_d4d10fdc-175c-443d-8bca-cd99110f47e9': '문자 배열에서 글자와 끝 표시를 읽은 결과를 고르는 문제예요.',
    'stp_9753c53b-dc61-4770-8590-4d509bff115f': '함수를 두 번 호출했을 때 남아 있는 값과 출력 결과를 구하는 문제예요.',
    'stp_e9d3e0ca-505d-48bb-99d5-a9eb64fc3187': '함수 호출 전후의 출력이 어떤 순서로 나오는지 고르는 문제예요.',
    'stp_53e610bf-edef-4a4c-b9b5-0df26de86266': '포인터를 가리키는 포인터에서 주소를 두 번 따라간 값을 구하는 문제예요.',
    'stp_be3ac498-bec9-4719-9bd5-acf535d126aa': '관련 값을 담은 구조체에서 두 필드를 읽은 결과를 고르는 문제예요.',
    'stp_7fcc7e79-fc73-4882-97aa-48fd684246dc': '구조체 배열의 두 번째 원소에서 count 값을 읽는 문제예요.',
    'stp_da803331-6926-4d74-a1d9-8f8500674931': '정수 두 개의 비트를 자리별로 비교해 공통 부분을 구하는 문제예요.',
    'stp_e89108e7-6f81-4a7f-984b-320d809b411b': '정수 나눗셈의 결과를 double 변수에 담으면 어떤 값이 되는지 고르는 문제예요.',
    'stp_932d8712-b8d0-4ceb-9b2d-a060b36aebe4': '상위 생성자가 메서드를 부를 때 하위 필드의 값을 구하는 문제예요.',
    'stp_47dd7547-9aae-4fca-a631-ca0efb834ae7': '객체 사이의 소유 관계와 일반 연관을 구별할 기준을 고르는 문제예요.',
    'stp_a421822e-5eb2-42b7-9ea9-68d19d6a733a': '모듈의 응집도와 결합도를 함께 보고 개선 방향을 고르는 문제예요.',
    'stp_8b12ce97-dad9-4b9d-966a-56f30b4661c9': '불러온 모듈의 별칭에 맞춰 사용하는 이름을 고치는 문제예요.',
    'stp_44f23f0c-39aa-4135-9a56-af6901ab9e8b': '새 배송을 추가하고 head로 조회한 뒤 원래 표의 크기를 구하는 문제예요.',
    'stp_af14310d-4f86-4286-9ebf-a1aa45a662c7': '시간이 모두 비어 있을 때 중앙값으로 채울 수 있는지 판단하는 문제예요.',
    'stp_c1a9c678-bb7c-402e-a934-c0fddc3169fc': '중복된 회원 번호를 가진 표와 결합하면 행 수가 어떻게 될지 판단하는 문제예요.',
    'stp_9c37861b-82de-44dd-99a7-ebd4e716e5ff': '산점도에서 보이는 점의 위치와 실제 배송 건수를 비교하는 문제예요.',
    'stp_2d3886de-c0ca-44f4-b427-480c7675db90': '그림에서 점을 숨겼을 때 원본 데이터도 바뀌는지 판단하는 문제예요.',
    'stp_27e5b09a-d74d-4f79-8a2a-bccb60f48a53': '일곱 행을 나눴을 때 훈련 자료와 평가 자료의 개수를 구하는 문제예요.',
    'stp_de190aec-5129-4fea-a670-f441d780e9f3': '자료를 섞지 않는 설정이 날짜순 정렬까지 해 주는지 판단하는 문제예요.',
    'stp_b90c45ec-26b6-4596-bf35-df47b960fa5f': '평가 자료를 변환할 때 훈련에서 정한 기준을 유지하는 방법을 고르는 문제예요.',
    'stp_90fdca82-9335-4dc0-830f-bc26f72bbe8c': '새 거리 하나를 예측기에 전달할 때 필요한 입력 모양을 고르는 문제예요.',
    'stp_d43879ba-684e-4a8b-90b2-d43e5cbffa5c': '학습 자료의 시간이 바뀌었을 때 새 거리의 예측값을 구하는 문제예요.',
    'stp_5145836d-ef50-4155-aafc-1818867327cf': '후보 모델 중 평균제곱오차가 가장 작은 모델을 고르는 문제예요.',
    'stp_7fe94b48-9022-43ef-9de9-00f1e0b51c86': '훈련 정답이 한 종류뿐일 때 분류기를 학습할 수 있는지 판단하는 문제예요.',
    'stp_6a8cf0fb-ad90-4692-aa43-1c7b308dd3ce': '연속적인 시간을 예측하는 목표에 맞는 포레스트 모델을 고르는 문제예요.',
    'stp_b3c38cb6-a565-4543-8567-d21d420235c3': '분류기가 돌려준 결정 점수를 확률로 읽어도 되는지 판단하는 문제예요.',
    'stp_ba77c57b-72f9-45b2-a941-33a009a25bd7': '특성 중요도가 크다는 결과로 무엇까지 말할 수 있는지 판단하는 문제예요.',
    'stp_5112d317-54df-45bd-a2ab-80ca1599b3e1': '평가 표만 전달했을 때 학습이 자동으로 멈추는지 판단하는 문제예요.',
    'stp_128934cb-29fd-4513-a801-9e632cf08e2b': '최종 평가 자료를 설정 선택에 반복 사용해도 되는지 판단하는 문제예요.',
    'stp_f6f4f1b8-055f-4426-b368-3ba57037145f': '학습 전에 나온 예측값으로 무엇을 확인할 수 있는지 판단하는 문제예요.',
    'stp_bb058cd6-2242-4058-915d-5205f3742be2': '함수에 전달한 값을 바꾼 뒤 원래 변수에 남는 값을 구하는 문제예요.',
    'stp_fe856be5-cb40-4e52-a93d-5ec90ccc6c6e': '함수 안팎에 이름이 같은 변수가 있을 때 각각의 값을 구하는 문제예요.',
    'stp_87c24da0-82fa-4aab-a0f1-140d46467d6d': '구조체를 복사하고 문자 배열을 바꿨을 때 두 구조체의 값을 구하는 문제예요.',
}


def overview_text(task):
    if task['id'] in OVERVIEWS:
        return OVERVIEWS[task['id']]
    # Existing summaries already name what the learner must solve. Speak them first.
    for action in task['narration'][:2]:
        if action['action'] != 'say':
            break
        for sentence in re.split(r'(?<=[.!?])\s+', action.get('text', '')):
            if sentence.endswith('문제예요.') and len(sentence) < 160:
                return sentence
    title = plain(task.get('question') or task['title']).rstrip('.')
    if title.endswith(('?', '까요', '나요')):
        return title.rstrip('?') + '?'
    for ending, replacement in sorted(ENDINGS.items(), key=lambda pair: -len(pair[0])):
        if title.endswith(ending):
            return title[:-len(ending)] + replacement + ' 문제예요.'
    raise ValueError(f'Author a problem overview for {task["id"]}: {title}')


def compile_openings(key, tasks):
    intros = json.loads(INTRO.read_text(encoding='utf-8'))
    introduction = intros[key]
    if not 2 <= len(introduction) <= 4 or any(not text.strip() for text in introduction):
        raise ValueError(f'{key}: introduce the learning goal and flow in 2–4 short passages')
    for index, task in enumerate(tasks):
        title = plain(task['title'])
        # #1 is explicit because several goals repeat the title in the action list.
        summary = overview_text(task)
        opening = [{'action': 'say', 'text': summary, 'target': f'text:{title}#1'}]
        # Move an existing summary to the front instead of saying it twice.
        detail = []
        for position, action in enumerate(task['narration']):
            if position < 2 and action['action'] == 'say':
                sentences = re.split(r'(?<=[.!?])\s+', action.get('text', ''))
                if summary in sentences:
                    remainder = ' '.join(sentence for sentence in sentences if sentence != summary)
                    if not remainder:
                        continue
                    action = {**action, 'text': remainder}
            detail.append(action)
        if index == 0:
            # Lesson-wide goals are not a fragment of this problem. No misleading spotlight.
            opening = [{'action': 'say', 'text': text} for text in introduction] + opening
        task['narration'] = opening + detail
