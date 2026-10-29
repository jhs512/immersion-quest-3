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
        'java-files', 'java-testing', 'git-branch', 'git-remote', 'git-branch-advanced', 'github-pr', 'java-rq', 'java-calculator', 'java-crud']


def count(value):
    return len(value) if isinstance(value, list) else value


def main():
    rows = []
    for key in KEYS:
        lesson = ROOT / f'courses/redesigned/{key}.json'
        current = hashlib.sha256(lesson.read_bytes()).hexdigest()
        content = json.loads(lesson.read_text(encoding='utf-8'))
        step = content['tasks'][-1]
        path = ROOT / f'target/final-challenges/{key}.json'
        evidence = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        fresh = evidence.get('passed') is True and evidence.get('lesson_sha256') == current
        runtime = evidence.get('runtime') or ('real JDK (validate_redesigned_lesson)' if key.startswith('java-') else '')
        state = '통과·해시 일치' if fresh else ('증거 없음' if not evidence else '낡음 또는 실패')
        rejected = count(evidence.get('rejected_answers', evidence.get('early_stops_rejected', '')))
        accepted = count(evidence.get('accepted_answers', ''))
        rows.append(f"| {key} | {content['revision']} | `{step['id']}` | {step['title']} | {runtime} | {accepted} | {rejected} | {state} | `{current[:16]}` |")
    text = ('# 마지막 도전 실제 채점 증거 (백엔드 24수업)\n\n'
            '`python tools/final_challenges/_evidence_summary.py`가 `target/final-challenges/<키>.json`과 지금 수업 바이트를 비교해 만든 표예요. '
            '자바 코드 수업은 `cargo run --example validate_redesigned_lesson -- tests/lesson-cases/<키>.json target/final-challenges/<키>.json`, '
            '터미널 수업은 `cargo test --test final_terminal_challenges`, GitHub 수업은 `cargo test --test github_pr real_github_final_challenge -- --ignored`가 증거를 써요. '
            '자바 코드 수업의 동등/거절 수는 수업 전체 사례 수이고, 터미널 수업은 도전 하나의 사례 수예요.\n\n'
            '| 수업 | 버전 | 도전 스텝 | 제목 | 실행 | 동등 풀이 통과 | 오답·우회 거절 | 상태 | 수업 sha256 앞 16자 |\n'
            '| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n' + '\n'.join(rows) + '\n')
    (ROOT / 'docs/curriculum/final-challenges-evidence.md').write_text(text, encoding='utf-8', newline='\n')
    print(text)


if __name__ == '__main__':
    main()
