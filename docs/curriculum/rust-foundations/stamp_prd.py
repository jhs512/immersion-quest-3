"""Snapshot the current policy into a Rust lesson PRD, record the user's approval and render the Markdown.

The approval is the user's 2026-11-02 answer relayed by Codex (README.md, "승인 기록"). Run it again
after editing the PRD inside the approved scope; a goal or teaching-method change needs a new approval.

    python docs/curriculum/rust-foundations/stamp_prd.py rust_values [...]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from lesson_prd import approve, policy_revision, render  # noqa: E402

POLICY_FILES = ('docs/content-rules.md', 'docs/voice.md', 'docs/agents/narration.md')
RUST_RULES = [
    'Rust 코드는 실제 rustc --edition=2024로 컴파일·실행해 판정한다. 다른 언어로 위장해 등록하지 않는다.',
    '컴파일 실패는 프로그램이 실행되지 않은 결과다. 실행되지 않은 줄의 값 변화나 소유권 상태를 그리지 않는다.',
    'Rust 코드 흐름 보기는 지원이 입증되기 전까지 해설에 쓰지 않는다. 진단과 실제 출력으로 설명한다.',
]
BY = '사용자 / user · Codex 경유 2026-11-02'
EVIDENCE = ('2026-11-02 사용자가 Rust 기초 네 수업의 구체 PRD와 대표 문제 승인 질문에 「이 구성으로 제작」이라고 답했어요(Codex 경유). '
            '승인 범위: Java 실행 수업 직후 Rust 네 수업 연속 배치. ①값·타입·mut·출력 ②조건·반복·함수 '
            '③소유권·move·clone·빌림·&mut ④struct·Vec·Option·Result·match. 초안의 41스텝은 수량 강제가 아니에요. '
            '근거 초안: commit 83e96b45 docs/curriculum/rust-foundations/. 승인 범위 안의 스텝 조정은 README.md 「정식 제작 변경 기록」에 남겨요.')


def course_rules():
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    java = next(course for course in catalog['courses'] if course['key'] == 'java')
    return java['policy_snapshot']['rules']


def stamp(folder):
    path = ROOT / 'tools/redesigned_lessons' / folder / 'approved-prd.json'
    document = json.loads(path.read_text(encoding='utf-8'))
    document['approval'] = {'status': 'draft'}
    artifacts = [{'path': name, 'text': (ROOT / name).read_text(encoding='utf-8').replace('\r\n', '\n')} for name in POLICY_FILES]
    document['policy_snapshot'] = {'revision': policy_revision(artifacts), 'artifacts': artifacts,
                                   'rules': course_rules() + RUST_RULES}
    approved = approve(document, BY, EVIDENCE)
    path.write_text(json.dumps(approved, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    path.with_suffix('.md').write_text(render(approved) + '\n', encoding='utf-8', newline='\n')
    print(f"{folder}: approved {approved['approval']['content_sha256'][:12]}")


if __name__ == '__main__':
    for name in sys.argv[1:]:
        stamp(name)
