"""Shared metadata for real-engine Docker exercises; scripts remain lesson-specific."""
from common import START_NEW, TODO_RUN_BEFORE, TODO_RUN_AFTER, TODO_SUBMIT
from d1_image_container import BUSYBOX
from sql_lab import sql_lesson


def step(*, slug, title, concept, intro, know, starter, solution, script, expected,
         first, result, caution, files=None, images=None, variants=None, accepts=None, rejects=None):
    return dict(slug=slug, title=title, language='docker', docker_images=images or [BUSYBOX],
                entry_file='compose.yaml', files={'lab.sh': script, **(files or {})},
                start=START_NEW, objectives=[concept], intro=[intro], know=know,
                todo=[TODO_RUN_BEFORE, title, TODO_RUN_AFTER, TODO_SUBMIT],
                starter=starter, solution=solution, tests=[('', expected)], success=expected,
                variations=variants or [], complexity=dict(prior='컨테이너가 프로세스라는 것을 알아요.',
                    new=concept, changed=title, evidence='Docker 엔진이 실제로 연결하고 읽은 결과', lines=3, services=0),
                narration=[('say',intro,'text:'+intro), ('run',), ('say',first,'output'),
                    ('say',concept,'code:'+next(l for l in starter.splitlines() if l.strip() and not l.startswith('#'))),
                    ('patch',starter,solution,title), ('run',), ('say',result,'output'),
                    ('say',caution,'text:'+know), ('submit',)],
                review={intro:'준비된 컨테이너·네트워크의 시작 상태를 말해요.',
                    first:'실제 실행에서 관찰할 수정 전 상태와 원인을 연결해요.',
                    concept:'수정할 구성과 학습 개념의 관계를 짚어요.',
                    title:'목표에 맞는 구성 변경을 요구해요.', result:'수정 후 관찰 결과의 의미를 설명해요.',
                    caution:'이 스텝에서 잘못 적용하기 쉬운 경계를 구체적으로 설명해요.'},
                accepts=accepts or [], rejects=rejects or [([(solution,starter)],'수정 전 구성은 요구한 연결·보존 조건을 충족하지 못해요.')])


def lesson(*, key, folder, pilot, title, objectives, units, final_slug):
    value=sql_lesson(key=key, folder=folder, pilot=pilot, title=title,
                     objectives=objectives, units=units, final_slug=final_slug,
                     sources=[('https://docs.docker.com/compose/how-tos/networking/',
                         '서비스 이름·내부 포트·네트워크 범위를 확인해요.', '실제 Compose 환경에서 결과를 비교해요.')])
    value.update(category='docker', category_title='Docker',
                 category_evidence='실제 Docker·Compose 서비스의 연결과 수명을 다뤄요.',
                 prerequisites=['컨테이너·이미지·볼륨의 차이를 알아요.', 'Docker Desktop을 실행할 수 있어요.'],
                 description='실제 컨테이너를 연결하고 경계 하나를 바꿔 실패 원인을 확인해요.')
    value['brief']=(objectives[0], '마지막 도전에서 연결과 데이터 보존을 함께 지키세요.',
        [u['title'] for u in units], '실제 Docker Desktop을 사용해요. 호스트 포트는 필요할 때 127.0.0.1의 빈 포트만 자동 배정해요.',
        '내 컴퓨터에서 연결된다고 다른 컨테이너에서도 같은 주소를 쓸 수 있을까요?')
    value['representative']['expected_action']='최종 도전의 compose.yaml을 직접 구현해요.'
    return value
