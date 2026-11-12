"""Register the second cloud lesson right after the first one in the Java course.

Idempotent. Existing lessons keep their ids, revisions, order and content. Adding a lesson changes the
course flow, so the canonical previews' course_intent_sha256 (metadata) and their alignment hashes are
re-stamped; their learner-facing preview text is not touched.
Run from the repository root, before author_lesson.py.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
KEY = 'cloud-ec2-lifecycle'
AFTER = 'cloud-vpc-subnet-ec2'
LESSON_ID = 'lsn_81d67284-bfe0-49b9-ac29-33f9aea19c00'
TITLE = '클라우드 · 서버를 멈추고 다시 켜고 없애요'
LAST = 'stp_eb061d59-86eb-4cd6-a985-e05e8e9389d6'
PILOT = '멈'
PREREQUISITES = [AFTER, 'docker-image-container']


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def save(path, value, indent=2):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8', newline='\n')


def main():
    catalog = load('tools/redesigned_courses/catalog.json')
    java = next(c for c in catalog['courses'] if c['key'] == 'java')
    if not any(item['key'] == KEY for item in java['lessons']):
        at = next(i for i, item in enumerate(java['lessons']) if item['key'] == AFTER) + 1
        java['lessons'].insert(at, {
            'key': KEY, 'id': LESSON_ID, 'title': TITLE,
            'objectives': ['서버를 멈추고 다시 켜면 무엇이 남고 무엇이 사라지는지 실제 상태로 확인해요.',
                           '상태가 바로 바뀌지 않는 것을 보고, 다음 명령 전에 원하는 상태가 됐는지 확인해요.',
                           '자원을 지우는 순서를 거절 메시지로 찾아요. 서버 → 서브넷 → VPC 순서예요.'],
            'authoring_prd': 'tools/redesigned_lessons/cloud_ec2_lifecycle/approved-prd.json',
            'revision': f'{KEY}-1', 'added_on': '2026-11-12',
            'origin': '2026-11-12 사용자가 승인한 클라우드 두 번째 수업(서버 수명주기·삭제 순서) 예고·PRD·대표 문제로 만든 자바 과정 후속 선택 수업.',
            'validation': {'pilot': PILOT, 'driver': 'code', 'label': TITLE},
            'required': False})
        save('tools/redesigned_courses/catalog.json', catalog)

    sequence = load('tools/redesigned_courses/backend-sequence.json')
    if KEY not in sequence['order']:
        sequence['order'].insert(sequence['order'].index(AFTER) + 1, KEY)
    sequence['prerequisites'][KEY] = PREREQUISITES
    save('tools/redesigned_courses/backend-sequence.json', sequence)

    challenges = load('tools/redesigned_courses/java/lesson-challenges.json')
    challenges['lessons'][KEY] = {'task_id': LAST, 'title': '실습 VPC를 모두 정리하세요',
                                  'reason': '종료와 삭제 의존성을 조합해 VPC 하나를 안쪽부터 정리하는 마지막 문제를 실제 API 상태로 채점해요.'}
    save('tools/redesigned_courses/java/lesson-challenges.json', challenges)

    classes = load('tools/redesigned_courses/lesson-classification.json')
    classes['courses']['java']['lessons'][KEY] = {
        'category': 'cloud', 'track': None, 'status': 'approved', 'decided_by': '사용자(jhs512): 2026-11-10 「클라우드 새로 만들고」',
        'decided_on': '2026-11-12', 'title': TITLE,
        'evidence': {'category': '클라우드 분류는 VPC·서브넷·서버 배치와 이후 수명주기·S3 수업을 묶어요(2026-11-10 사용자 결정).',
                     'track': '새 트랙이나 진도 잠금은 만들지 않아요.'}}
    save('tools/redesigned_courses/lesson-classification.json', classes)

    release = load('tools/redesigned_courses/release.json')
    entry = {'at': '2026-11-12T12:00:00Z', 'summary': '클라우드 두 번째 수업을 추가했어요.',
             'reason': '사용자가 승인한 예고·PRD·대표 문제로 서버 수명주기와 자원 삭제 순서를 다루는 수업을 만들었어요.',
             'details': ['서버를 멈추고 다시 켜고 종료하며 남는 것을 확인하는 선택 수업이에요. 실제 AWS 계정은 쓰지 않아요.',
                         '서버 → 서브넷 → VPC 순서로 자원을 지우는 터미널 실습까지 6개예요. 실제 API 상태로 채점해요.',
                         '기존 수업의 순서·문제·학습 기록은 그대로예요. 새 수업은 첫 클라우드 수업 다음에 연결해요.',
                         'Docker Desktop Linux 엔진과 이 수업을 지원하는 최신 MQ3 플레이어가 필요해요.']}
    if not any(item['summary'] == entry['summary'] for item in release['course_changes']['java']):
        release['course_changes']['java'].insert(0, entry)
    save('tools/redesigned_courses/release.json', release)

    pilot = ROOT / f'tests/fixtures/player-pilot/{PILOT}/course.json'
    if not pilot.exists():
        template = load('tests/fixtures/player-pilot/클/course.json')
        template['title'] = '클라우드 수명주기 실습 검증 코스'
        template['lessons'][0].update(id=LESSON_ID, title=TITLE, revision=f'{KEY}-1', sha256='0' * 64)
        pilot.parent.mkdir(parents=True, exist_ok=True)
        pilot.write_text(json.dumps(template, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

    # Course intent now covers the new flow: re-stamp the other canonical previews' metadata.
    from curriculum_authority import CANONICAL_PREVIEW_PREFIXES, alignment_source, course_intent, digest
    intent = digest(course_intent(java))
    for item in java['lessons']:
        if item['key'] == KEY or not item['key'].startswith(CANONICAL_PREVIEW_PREFIXES):
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
        binding['intent_restamped'] = (f'2026-11-12: 자바 과정 흐름에 {KEY}를 추가해 course_intent_sha256만 다시 찍었어요. '
                                       '이 수업의 예고·PRD·본편은 바뀌지 않아 기존 검토를 유지해요.')
        (folder / 'preview-alignment.json').write_text(json.dumps(binding, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('registered', KEY)


if __name__ == '__main__':
    main()
