"""Register the first cloud lesson in the Java course without changing existing lessons.

Idempotent. Existing lessons keep their ids, revisions, order and content. Adding a lesson changes the
course flow, so the canonical network previews' course_intent_sha256 (metadata) and their alignment
hashes are re-stamped; their learner-facing preview text is not touched.
Run from the repository root, before author_lesson.py.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
KEY = 'cloud-vpc-subnet-ec2'
LESSON_ID = 'lsn_9684d378-1491-4707-8911-20a7753501f9'
TITLE = '클라우드 · 주소 공간 안에 서버 한 대를 배치해요'
LAST = 'stp_6cb45d59-91d2-4bb7-b082-06523207af50'
PREREQUISITES = ['network-ip', 'network-endpoints', 'network-routing', 'network-http', 'docker-image-container', 'docker-network-ports']


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def save(path, value, indent=2):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8', newline='\n')


def main():
    catalog = load('tools/redesigned_courses/catalog.json')
    java = next(c for c in catalog['courses'] if c['key'] == 'java')
    if not any(item['key'] == KEY for item in java['lessons']):
        java['lessons'].append({
            'key': KEY, 'id': LESSON_ID, 'title': TITLE,
            'objectives': ['이미 아는 CIDR로 VPC와 서브넷의 포함 관계를 읽고 선언해요.',
                           '서버 한 대를 원하는 서브넷에 놓고, 받은 주소가 그 범위 안인지 확인해요.',
                           '같은 VPC 안의 다른 서버에서 그 주소로 HTTP 응답을 받아 배치를 확인해요.'],
            'authoring_prd': 'tools/redesigned_lessons/cloud_vpc_subnet_ec2/approved-prd.json',
            'revision': f'{KEY}-2', 'added_on': '2026-11-10',
            'origin': '2026-11-09 사용자가 승인한 Floci 클라우드 첫 수업 예고·PRD·대표 문제로 만든 자바 과정 후속 선택 수업.',
            'validation': {'pilot': '클', 'driver': 'code', 'label': TITLE},
            'required': False})
        save('tools/redesigned_courses/catalog.json', catalog)

    sequence = load('tools/redesigned_courses/backend-sequence.json')
    if KEY not in sequence['order']:
        sequence['order'].insert(sequence['order'].index('docker-compose-db') + 1, KEY)
    sequence['prerequisites'][KEY] = PREREQUISITES
    sequence['cloud_rationale'] = ('클라우드 첫 수업은 네트워크 기초와 Docker·Compose 뒤, 화면 확장 앞에 둔다. '
                                   'CIDR·주소·HTTP·컨테이너를 다시 가르치지 않고 VPC·서브넷·서버 배치에만 쓴다(2026-11-10). 기존 수업의 상대 순서는 유지한다.')
    save('tools/redesigned_courses/backend-sequence.json', sequence)

    challenges = load('tools/redesigned_courses/java/lesson-challenges.json')
    challenges['lessons'][KEY] = {'task_id': LAST, 'title': '자바 서버를 10.91.2.0/24에 배치하세요',
                                  'reason': '서브넷 범위·서버 자리·사설 주소 요청을 한 번에 조합하는 마지막 문제를 실제 API 상태와 채점기의 HTTP 요청으로 채점해요.'}
    save('tools/redesigned_courses/java/lesson-challenges.json', challenges)

    classes = load('tools/redesigned_courses/lesson-classification.json')
    lessons = classes['courses']['java']['lessons']
    if not any(c['id'] == 'cloud' for c in classes['courses']['java']['categories']):
        classes['courses']['java']['categories'].append({'id': 'cloud', 'title': '클라우드'})
    lessons[KEY] = {'category': 'cloud', 'track': None, 'status': 'approved', 'decided_by': '사용자(jhs512): 2026-11-10 「클라우드 새로 만들고」', 'decided_on': '2026-11-10', 'title': '클라우드 · 주소 공간 안에 서버 한 대를 배치해요', 'evidence': {'category': '사용자가 새 클라우드 분류를 지시했어요. VPC·서브넷·서버 배치와 이후 수명주기·S3 수업을 묶어요.', 'track': '새 트랙이나 진도 잠금은 만들지 않아요.'}}
    save('tools/redesigned_courses/lesson-classification.json', classes)

    release = load('tools/redesigned_courses/release.json')
    entry = {'at': '2026-11-10T12:00:00Z', 'summary': '클라우드 첫 수업을 추가했어요.',
             'reason': '사용자가 승인한 예고·PRD·대표 문제로 자바 과정의 후속 클라우드 수업을 만들었어요.',
             'details': ['VPC·서브넷·서버 배치를 로컬 실습 API로 다루는 선택 수업이에요. 실제 AWS 계정은 쓰지 않아요.',
                         '실제 API 상태와 채점기의 HTTP 요청으로 채점하는 터미널 실습 7개예요.',
                         '기존 수업의 순서·문제·학습 기록은 그대로예요. 새 수업은 Docker·Compose 수업 다음에 연결해요.',
                         'Docker Desktop Linux 엔진과 클라우드 실습을 지원하는 최신 MQ3 플레이어가 필요해요. AWS CLI는 따로 설치하지 않아요.']}
    if not any(item['summary'] == entry['summary'] for item in release['course_changes']['java']):
        release['course_changes']['java'].insert(0, entry)
    save('tools/redesigned_courses/release.json', release)

    pilot = ROOT / 'tests/fixtures/player-pilot/클/course.json'
    if not pilot.exists():
        template = load('tests/fixtures/player-pilot/이/course.json')
        template['title'] = '클라우드 실습 검증 코스'
        template['lessons'][0].update(id=LESSON_ID, title=TITLE, revision=f'{KEY}-1', sha256='0' * 64)
        pilot.parent.mkdir(parents=True, exist_ok=True)
        pilot.write_text(json.dumps(template, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

    # Course intent now covers the new flow: re-stamp the canonical network previews' metadata.
    from curriculum_authority import alignment_source, course_intent, digest
    intent = digest(course_intent(java))
    for item in java['lessons']:
        if not item['key'].startswith('network-'):
            continue
        folder = ROOT / Path(item['authoring_prd']).parent
        preview = json.loads((folder / 'lesson-preview.json').read_text(encoding='utf-8'))
        if preview['course_intent_sha256'] == intent:
            continue
        binding = json.loads((folder / 'preview-alignment.json').read_text(encoding='utf-8'))
        prd = json.loads((folder / 'approved-prd.json').read_text(encoding='utf-8'))
        authored = json.loads((folder / 'content.json').read_text(encoding='utf-8'))
        # Re-stamp only a binding that matched before: a pre-existing mismatch must stay visible.
        if binding['source_sha256'] != digest(alignment_source(preview, prd, authored)):
            raise SystemExit(f"{item['key']}: alignment was already stale before this change")
        preview['course_intent_sha256'] = intent
        (folder / 'lesson-preview.json').write_text(json.dumps(preview, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        binding['source_sha256'] = digest(alignment_source(preview, prd, authored))
        binding['intent_restamped'] = ('2026-11-10: 자바 과정 흐름에 cloud-vpc-subnet-ec2를 추가해 course_intent_sha256만 다시 찍었어요. '
                                       '이 수업의 예고·PRD·본편은 바뀌지 않아 기존 검토를 유지해요.')
        (folder / 'preview-alignment.json').write_text(json.dumps(binding, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('registered', KEY)


if __name__ == '__main__':
    main()
