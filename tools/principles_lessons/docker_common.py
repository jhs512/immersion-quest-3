"""Shared metadata for the Docker network and Compose·DB lessons.

Their steps are Compose terminal steps (compose_terminal.py): the learner edits files in the editor
and types `docker compose …` in the real terminal. Grading reads the commands and the real engine.
"""
from d1_image_container import BUSYBOX, DOCKER_GRADING, DOCKER_NARRATION, DOCKER_RESET, DOCKER_VERIFY, FOLDER
from sql_lab import sql_lesson


def unit(title, objective, premise, steps):
    return dict(title=title, objectives=[objective], premise=premise, steps=steps)


def lesson(*, key, folder, pilot, title, objectives, units, final_slug):
    value = sql_lesson(key=key, folder=folder, pilot=pilot, title=title,
                       objectives=objectives, units=units, final_slug=final_slug,
                       sources=[('https://docs.docker.com/compose/how-tos/networking/',
                                 '서비스 이름·내부 포트·네트워크 범위를 확인해요.', '실제 Compose 환경에서 결과를 비교해요.')])
    value.update(category='docker', category_title='Docker',
                 category_evidence='실제 Docker·Compose 서비스의 연결과 수명을 다뤄요.',
                 prerequisites=['컨테이너·이미지·볼륨의 차이를 알아요.', 'Docker Desktop을 실행할 수 있어요.'],
                 description='실제 컨테이너를 연결하고 경계 하나를 바꿔 실패 원인을 확인해요.',
                 grading=list(DOCKER_GRADING), reset=list(DOCKER_RESET), narration_policy=list(DOCKER_NARRATION),
                 verification=list(DOCKER_VERIFY),
                 learning_strategy='먼저 터미널에서 docker compose 명령을 입력해 실제 결과를 봐요. 원인을 설명한 뒤 편집기에서 한 곳만 고치고 같은 명령으로 다시 확인해요.')
    value['brief'] = (objectives[0], '마지막 도전에서 연결과 데이터 보존을 함께 지키세요.',
        [u['title'] for u in units], '실제 Docker Desktop을 사용해요. 명령은 터미널에서 직접 입력해요. 호스트 포트는 필요할 때 127.0.0.1의 빈 포트만 자동 배정해요.',
        '내 컴퓨터에서 연결된다고 다른 컨테이너에서도 같은 주소를 쓸 수 있을까요?')
    value['representative'].update(expected_action='최종 도전의 파일을 편집기에서 고치고 터미널에서 docker compose로 확인해요.',
                                   acceptance='지금 파일로 실행한 명령과 실제 Docker 상태가 모든 검사를 만족해요.',
                                   reset='이 문제의 시작 파일로 돌아가고 이 문제가 만든 Docker 자원만 지워요.',
                                   narration='실패 결과를 터미널에서 읽고 파일 한 곳을 고친 뒤 같은 명령으로 다시 비교해요.')
    return value
