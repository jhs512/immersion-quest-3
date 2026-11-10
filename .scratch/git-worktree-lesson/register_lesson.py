"""Register the Git worktree lesson in the Java course without changing existing lessons.

Idempotent. Existing lessons keep their ids, revisions, order and content. Adding a lesson changes the
course flow, so the canonical (network-, cloud-) previews' course_intent_sha256 (metadata) and their
alignment hashes are re-stamped; their learner-facing preview text is not touched.
Run from the repository root, before author_lesson.py.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
KEY = 'git-worktree'
LESSON_ID = 'lsn_411084da-1251-402b-accc-13a1a1c9e208'
TITLE = 'Git · 워크트리: 작업을 둔 채 다른 브랜치를 옆 폴더에서 다뤄요'
LAST = 'stp_766d9f5c-ed41-48c5-bd20-7cf8246b240d'
PILOT = '워'
PREREQUISITES = ['git-branch-advanced']
OBJECTIVES = ['커밋하지 않은 작업이 있을 때 브랜치 전환이 막히는 이유를 겪어요.',
              'git worktree로 다른 브랜치를 옆 폴더에 꺼내 커밋하고, 같은 저장소에 남는 것을 확인해요.',
              '한 브랜치는 한 폴더에만 꺼낸다는 규칙을 지키고, 다 쓴 폴더를 remove·prune으로 정리해요.']
APPROVAL = '사용자(jhs512): 2026-11-10 「깃 워크 트리 수업도 적절히 구성해서 추가해줘」, 「다 수락할게」'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def save(path, value, indent=2):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8', newline='\n')


def main():
    catalog = load('tools/redesigned_courses/catalog.json')
    java = next(c for c in catalog['courses'] if c['key'] == 'java')
    if not any(item['key'] == KEY for item in java['lessons']):
        at = next(i for i, item in enumerate(java['lessons']) if item['key'] == 'git-branch-advanced') + 1
        java['lessons'].insert(at, {
            'key': KEY, 'id': LESSON_ID, 'title': TITLE, 'objectives': OBJECTIVES,
            'authoring_prd': 'tools/redesigned_lessons/git_worktree/approved-prd.json',
            'continuing_situation': 'main에서 쓰던 안내를 커밋하지 않은 채, 동료의 hotfix 브랜치를 옆 폴더에 꺼내 급한 수정을 마치고 정리한다.',
            'revision': f'{KEY}-1', 'required': False, 'added_on': '2026-11-11',
            'origin': '2026-11-10 사용자가 요청하고 수락한 Git 워크트리 수업 계획(브랜치 심화 뒤, GitLab MR 앞)으로 만든 선택 수업.',
            'validation': {'pilot': PILOT, 'driver': 'native', 'label': KEY}})
        save('tools/redesigned_courses/catalog.json', catalog)

    sequence = load('tools/redesigned_courses/backend-sequence.json')
    if KEY not in sequence['order']:
        sequence['order'].insert(sequence['order'].index('git-branch-advanced') + 1, KEY)
    sequence['prerequisites'][KEY] = PREREQUISITES
    sequence['worktree_rationale'] = ('Git 워크트리 수업은 브랜치 심화 뒤, GitLab MR 앞에 둔다. 전환·커밋·show·log와 '
                                      'git-remote의 ../ 복제본 경험을 다시 가르치지 않고 워크트리에만 쓴다(2026-11-10 사용자 수락). '
                                      '기존 수업의 상대 순서와 선수 관계는 유지한다.')
    save('tools/redesigned_courses/backend-sequence.json', sequence)

    challenges = load('tools/redesigned_courses/java/lesson-challenges.json')
    challenges['lessons'][KEY] = {'task_id': LAST, 'title': '쓰던 변경을 지키며 급한 수정을 마치세요',
                                  'reason': '워크트리 추가·다른 폴더의 커밋·폴더 정리를 쓰던 변경을 지키며 한 번에 조합하는 마지막 문제를 실제 폴더 목록과 브랜치 기록으로 채점해요.'}
    save('tools/redesigned_courses/java/lesson-challenges.json', challenges)

    classes = load('tools/redesigned_courses/lesson-classification.json')
    classes['courses']['java']['lessons'][KEY] = {
        'category': 'git', 'track': None, 'status': 'approved', 'decided_by': APPROVAL, 'decided_on': '2026-11-10', 'title': TITLE,
        'evidence': {'category': '실제 Git 저장소의 워크트리를 다루는 Git 수업이에요.', 'track': '새 트랙이나 진도 잠금은 만들지 않아요.'}}
    save('tools/redesigned_courses/lesson-classification.json', classes)

    release = load('tools/redesigned_courses/release.json')
    entry = {'at': '2026-11-11T12:00:00Z', 'summary': 'Git 워크트리 수업을 추가했어요.',
             'reason': '사용자가 수락한 계획으로 브랜치 심화 뒤에 Git 워크트리 선택 수업을 만들었어요.',
             'details': ['쓰던 변경을 그대로 두고 다른 브랜치를 옆 폴더에 꺼내 커밋하고, 다 쓴 폴더를 정리하는 수업이에요.',
                         '실제 Git 저장소의 폴더 목록과 브랜치 기록으로 채점하는 터미널 실습 7개예요.',
                         '기존 수업의 순서·문제·학습 기록은 그대로예요. 새 수업은 Git 브랜치 심화 다음에 연결해요.',
                         '워크트리 채점을 지원하는 최신 MQ3 플레이어가 필요해요.']}
    if not any(item['summary'] == entry['summary'] for item in release['course_changes']['java']):
        release['course_changes']['java'].insert(0, entry)
    save('tools/redesigned_courses/release.json', release)

    pilot = ROOT / f'tests/fixtures/player-pilot/{PILOT}/course.json'
    if not pilot.exists():
        template = load('tests/fixtures/player-pilot/굳/course.json')
        template['lessons'][0].update(id=LESSON_ID, title=TITLE, revision=f'{KEY}-1', sha256='0' * 64)
        pilot.parent.mkdir(parents=True, exist_ok=True)
        pilot.write_text(json.dumps(template, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

    # Course intent now covers the new flow: re-stamp the canonical previews' metadata only.
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
        binding['intent_restamped'] = ('2026-11-11: 자바 과정 흐름에 git-worktree를 추가해 course_intent_sha256만 다시 찍었어요. '
                                       '이 수업의 예고·PRD·본편은 바뀌지 않아 기존 검토를 유지해요.')
        (folder / 'preview-alignment.json').write_text(json.dumps(binding, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('registered', KEY)


if __name__ == '__main__':
    main()
