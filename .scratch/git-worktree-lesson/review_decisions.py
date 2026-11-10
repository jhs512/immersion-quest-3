"""Write the author's meaning review of every flagged narration sentence (docs/agents/narration.md).

Run from the repository root after author_lesson.py, then record it:
    python .scratch/git-worktree-lesson/review_decisions.py
    python tools/narration_review.py record .scratch/git-worktree-lesson/narration-review-decisions.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import narration_review  # noqa: E402

NOTES = {
    1: '실제 실수: 거절을 보고 switch -f로 넘기는 것. -f는 --discard-changes와 같아서 work의 커밋하지 않은 검색 안내를 지운다'
       '(git-switch 문서, tests/git_worktree.rs의 switch -f 오답이 작업 파일 검사로 실패). 행동(강제 옵션을 붙이지 않기)과 결과(검색 안내 삭제)를 말한다.',
    2: '실제 실수: 경로 ../hotfix를 hotfix로 줄여 쓰는 것. Git 2.56.0 실측에서 work 안에 hotfix 폴더가 생기고 status에 ?? hotfix/가 보였다. '
       '채점의 폴더 목록에서도 다른 자리로 실패한다. 결과를 구체적으로 말한다.',
    3: '실제 실수: cd ../hotfix를 빠뜨리고 echo·add·commit을 work에서 실행하는 것. 그러면 쓰던 검색 안내와 운영 시간 줄이 함께 main에 커밋된다'
       '(오답 사례로 main 기록 검사가 실패). 주어(다음 명령)와 결과(main에 커밋)를 밝힌다.',
    4: '실제 실수: 거절을 보고 add에 -f를 붙이는 것. 문서상 --force가 다른 워크트리에서 쓰는 브랜치 거절을 넘고, 실측에서 한쪽 커밋 뒤 '
       '다른 폴더의 status에 M  guide.txt가 생겼다(상태 어긋남). 채점도 같은 브랜치 두 폴더를 실패로 본다.',
    5: '실제 실수: 커밋하지 않은 변경이 있는 폴더를 remove로 지우려다 --force를 붙이는 것. 실측: 「contains modified or untracked files, '
       'use --force to delete it」 거절, --force는 그 폴더의 변경을 지운다(문서: remove는 깨끗한 워크트리만). 강조 문장(이번엔 변경이 없다)과 대비되는 조건을 말한다.',
    6: '실제 실수: 폴더를 rm -r로만 지우고 끝내는 것. 실측: worktree list에 prunable 기록이 남고 같은 경로의 add가 「missing but already '
       'registered worktree」로 거절된다. 채점도 남은 기록을 실패로 본다. 해결 행동(prune)까지 말한다.',
}


def main():
    authored = json.loads((ROOT / 'tools/redesigned_lessons/git_worktree/content.json').read_text(encoding='utf-8'))
    decisions = []
    for index, task in enumerate(authored['tasks'], 1):
        prompts = narration_review.prompts(task)
        if prompts and index not in NOTES:
            raise SystemExit(f'{index}: flagged sentences without a review note')
        decisions.append({'lesson': 'git-worktree', 'step': task['id'],
                          'checked': {prompt['text']: NOTES[index] for prompt in prompts},
                          'findings': [], 'reviewer': 'Claude Code(작성자 자체 검토, 사용자 검수 아님)'})
    path = ROOT / '.scratch/git-worktree-lesson/narration-review-decisions.json'
    path.write_text(json.dumps(decisions, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print('wrote', path.relative_to(ROOT), len(decisions))


if __name__ == '__main__':
    main()
