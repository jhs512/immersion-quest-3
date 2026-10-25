"""Shared wording for the principle lessons. Learner-facing text follows docs/voice.md."""

START_NEW = '이 스텝은 제공된 준비 코드에서 시작해요.'
START_PREV = '이 스텝은 앞 스텝을 고친 상태의 코드에서 시작해요. 내가 앞에서 쓴 답이 아니라 정답 상태로 준비했어요.'

JAVA_GRADING = [
    '제출한 코드를 실제 JDK 25로 실행해 정답 출력과 비교해요.',
    '여러 입력으로 다시 실행해요. 한 입력의 출력만 맞춘 코드는 통과하지 못해요.',
    '시작 코드는 실패하고, 흔한 오해에 맞춘 답도 실패하는지 기록된 오답으로 확인해요.',
]
JAVA_RESET = ['스텝마다 제공된 준비 코드와 입력으로 돌아가요.', '해설은 내 코드를 따로 보관하고, 끝나면 되돌려요.']
JAVA_NARRATION = ['수정 전 실행 → 출력 읽기 → 고칠 한 곳 → 다시 실행해 비교해요.',
                  '「조심하세요」는 그 스텝에서 실제로 하기 쉬운 실수에만 써요.']
VERIFY = ['실제 MQ 채점기로 정답 통과·시작 코드 실패·기록된 오답 거절·다른 정답 허용을 확인해요(tests/lesson-cases).',
          '해설의 실행 결과는 실제 실행 기록과 비교해요. 앱 화면의 음성·강조 동기는 별도 확인이에요.']
STRATEGY = '각 스텝은 먼저 실행해 예상과 다른 결과를 봐요. 원인을 찾은 뒤 표시한 한 곳만 고치고 다시 실행해요. 해설은 내 코드를 보존한 채 따로 진행해요.'

TODO_RUN_BEFORE = '코드 실행 버튼을 눌러 고치기 전 결과를 확인하세요.'
TODO_RUN_AFTER = '코드 실행 버튼을 눌러 바뀐 결과를 확인하세요.'
TODO_SUBMIT = '고친 코드를 제출하세요.'


def java_lesson(**fields):
    fields.setdefault('grading', JAVA_GRADING)
    fields.setdefault('reset', JAVA_RESET)
    fields.setdefault('narration_policy', JAVA_NARRATION)
    fields.setdefault('verification', VERIFY)
    fields.setdefault('learning_strategy', STRATEGY)
    return fields
