"""Write docs/curriculum/final-challenges-evidence.md from target/final-challenges/<key>.json and the current lesson bytes.

A row is "passed" only when the saved evidence passed and its lesson hash equals the current courses/redesigned/<key>.json.
    python tools/final_challenges/_evidence_summary.py
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEYS = ['bash-basics', 'java-values', 'vim-basics', 'java-launch', 'java-conditions', 'java-arrays', 'java-methods', 'java-arguments',
        'git-first', 'java-references', 'java-static', 'java-roles', 'java-collections', 'java-inheritance-composition', 'java-streams',
        'java-files', 'java-testing', 'git-branch', 'git-remote', 'git-branch-advanced', 'java-rq', 'java-calculator', 'java-crud']


def count(value):
    return len(value) if isinstance(value, list) else value


def main():
    rows = []
    catalog = json.loads((ROOT / 'tools/redesigned_courses/catalog.json').read_text(encoding='utf-8'))
    keys = KEYS + [l['key'] for c in catalog['courses'] if c['key'] in ('aice', 'engineer') for l in c['lessons']]
    for key in keys:
        lesson = ROOT / f'courses/redesigned/{key}.json'
        current = hashlib.sha256(lesson.read_bytes()).hexdigest()
        content = json.loads(lesson.read_text(encoding='utf-8'))
        step = content['tasks'][-1]
        path = ROOT / f'target/final-challenges/{key}.json'
        evidence = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        fresh = evidence.get('passed') is True and evidence.get('lesson_sha256') == current
        language = step.get('language') or step.get('language_id')
        runtime = evidence.get('runtime') or (('실행 예제 + 직접 답 입력' if step.get('example_code') else '사례별 직접 답 입력') if step.get('interaction') else
                  {'java':'실제 JDK', 'python':'실제 Python', 'c':'실제 C', 'sql':'실제 SQLite'}.get(language, '실제 채점기'))
        state = '통과·해시 일치' if fresh else ('증거 없음' if not evidence else '낡음 또는 실패')
        rejected = count(evidence.get('rejected_answers', evidence.get('early_stops_rejected', '')))
        accepted = count(evidence.get('accepted_answers', ''))
        rows.append(f"| {key} | {content['revision']} | `{step['id']}` | {step['title']} | {runtime} | {accepted} | {rejected} | {state} | `{current[:16]}` |")
    text = ('# 마지막 도전 실제 채점 증거 (이번 변경 77수업)\n\n'
            '`python tools/final_challenges/_evidence_summary.py`가 `target/final-challenges/<키>.json`과 지금 수업 바이트를 비교해 만든 표예요. '
            '자바 코드 수업은 `cargo run --example validate_redesigned_lesson -- tests/lesson-cases/<키>.json target/final-challenges/<키>.json`, '
            '터미널 수업은 `cargo test --test final_terminal_challenges`, GitHub 수업은 `cargo test --test github_pr real_github_final_challenge -- --ignored`가 증거를 써요. '
            '기존 백엔드 코드 증거는 수업 전체 사례, 터미널 및 새 두 과정 증거는 도전 하나의 사례를 셀 수 있어요. '
            '새 두 과정의 기존 문제는 게시 도구가 공개 버전과 바이트 단위로 동일한지 검사해요. '
            '이 표는 실제 음성을 들었다거나 화면 검수를 끝냈다는 뜻이 아니에요.\n\n'
            '| 수업 | 버전 | 도전 스텝 | 제목 | 실행 | 동등 풀이 통과 | 오답·우회 거절 | 상태 | 수업 sha256 앞 16자 |\n'
            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n' + '\n'.join(rows) + '\n')
    (ROOT / 'docs/curriculum/final-challenges-evidence.md').write_text(text, encoding='utf-8', newline='\n')
    print('docs/curriculum/final-challenges-evidence.md: 현재 수업 해시와 실제 실행 증거를 비교한 원장')


if __name__ == '__main__':
    main()
