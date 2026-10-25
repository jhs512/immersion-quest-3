"""The meaning-review gate: prompts are found deterministically, decisions are a reviewer's, and an old
review never covers changed text. Uses the real Bash step 9 (stp_30c10394) as the known-bad case."""
import copy
import json
import unittest
from pathlib import Path

import narration_review as review

BASH9 = 'stp_30c10394-2734-418f-b96a-d257e8b0d6ff'
BAD = '조심하세요. 이름이 같아도 지금 위치 notes 안에 만들어요. 바깥 memo.txt의 첫 메모는 그대로예요.'
NATURAL = '현재 위치가 notes 폴더이므로, 새 memo.txt는 이 폴더 안에 생겨요. 바깥 폴더의 memo.txt는 그대로 남아요.'


def bash9(text=BAD):
    _, _, authored, steps = review.load('bash-basics')
    step = next(step for step in steps if step['id'] == BASH9)
    task = copy.deepcopy(next(task for task in authored['tasks'] if task['id'] == BASH9))
    for action in task['narration']:
        if review.spoken(action) in (BAD, NATURAL):
            action['text'] = text
    return step, task


def reviewed(step, task, checked=None, findings=None):
    return {'lesson': 'bash-basics', 'state': 'reviewed', 'context_sha256': review.context_sha256(step, task),
            'checked': checked or {}, 'findings': findings or []}


class PromptTest(unittest.TestCase):
    def test_known_bad_bash9_sentence_is_a_prompt_for_both_reasons(self):
        step, task = bash9(BAD)
        prompt = next(p for p in review.prompts(task) if p['text'] == BAD)
        self.assertTrue(any(r.startswith('caution') for r in prompt['reasons']))
        self.assertTrue(any('같아도' in r for r in prompt['reasons']))

    def test_natural_sentence_is_not_forced_into_a_warning(self):
        step, task = bash9(NATURAL)
        self.assertNotIn(NATURAL, [p['text'] for p in review.prompts(task)])

    def test_prompts_are_not_verdicts(self):
        # A real warning with a concession is still only a prompt; keeping it with a note is allowed.
        task = {'narration': [{'action': 'say', 'text': '조심하세요. 파일이 있어도 >는 내용을 지우고 새로 써요.'}]}
        self.assertEqual(len(review.prompts(task)), 1)


class GateTest(unittest.TestCase):
    def test_unchanged_baseline_passes_and_changed_baseline_needs_review(self):
        step, task = bash9(BAD)
        entry = {'lesson': 'bash-basics', 'state': 'baseline', 'context_sha256': review.context_sha256(step, task)}
        self.assertEqual(review.problems('bash-basics', step, task, entry), [])
        step, changed = bash9(NATURAL)
        self.assertRegex(' '.join(review.problems('bash-basics', step, changed, entry)), '다시 검토')

    def test_review_of_old_text_does_not_cover_new_text(self):
        step, task = bash9(BAD)
        old = reviewed(step, task, checked={BAD: 'looked fine'})
        step, changed = bash9(NATURAL)
        self.assertRegex(' '.join(review.problems('bash-basics', step, changed, old)), '다시 검토')

    def test_every_prompt_must_be_covered(self):
        step, task = bash9(BAD)
        others = {p['text']: 'real mistake named' for p in review.prompts(task) if p['text'] != BAD}
        self.assertRegex(' '.join(review.problems('bash-basics', step, task, reviewed(step, task, checked=others))), '검토하지 않은')

    def test_open_finding_blocks_and_fixed_finding_must_be_present(self):
        step, task = bash9(BAD)
        finding = {'sentence': BAD, 'issue': 'concession without contrast', 'reason': 'same name ≠ same file', 'status': 'open'}
        self.assertRegex(' '.join(review.problems('bash-basics', step, task, reviewed(step, task, findings=[finding]))), '해결하지 않은')
        fixed = dict(finding, status='fixed', fix=NATURAL)
        self.assertRegex(' '.join(review.problems('bash-basics', step, task, reviewed(step, task, findings=[fixed]))), '현재 해설에 없어요')
        step, corrected = bash9(NATURAL)
        others = {p['text']: 'real mistake named' for p in review.prompts(corrected)}
        self.assertEqual(review.problems('bash-basics', step, corrected, reviewed(step, corrected, checked=others, findings=[fixed])), [])

    def test_kept_sentence_and_finding_need_reasons(self):
        step, task = bash9(BAD)
        entry = reviewed(step, task, checked={p['text']: '' for p in review.prompts(task)})
        self.assertRegex(' '.join(review.problems('bash-basics', step, task, entry)), '이유가 없어요')
        entry = reviewed(step, task, checked={p['text']: 'ok' for p in review.prompts(task)},
                         findings=[{'sentence': BAD, 'issue': '', 'reason': 'x', 'status': 'kept'}])
        self.assertRegex(' '.join(review.problems('bash-basics', step, task, entry)), 'issue')

    def test_record_replaces_only_spoken_text_and_never_commands(self):
        _, _, authored, _ = review.load('bash-basics')
        task = next(task for task in authored['tasks'] if task['id'] == BASH9)
        current = [review.spoken(a) for a in task['narration']]
        # Whichever text the source holds now, replace it with the other one (dry run only).
        before_text, after_text = (BAD, NATURAL) if BAD in current else (NATURAL, BAD)
        self.assertIn(before_text, current)
        ledger = {'steps': {}}
        others = {p['text']: 'real mistake named' for p in review.prompts(task) if p['text'] != before_text}
        if after_text == BAD:
            others[BAD] = 'reverse dry run'
        decision = {'lesson': 'bash-basics', 'step': BASH9, 'checked': others,
                    'findings': [{'sentence': before_text, 'issue': 'i', 'reason': 'r', 'fix': after_text, 'status': 'fixed'}]}
        before = Path(review.ROOT / 'tools/redesigned_lessons/bash_basics/content.json').read_bytes()
        self.assertEqual(review.record([decision], ledger, dry_run=True), ['bash-basics'])
        self.assertEqual(Path(review.ROOT / 'tools/redesigned_lessons/bash_basics/content.json').read_bytes(), before)
        self.assertEqual(ledger['steps'][BASH9]['state'], 'reviewed')

    def test_rerecording_keeps_earlier_fixes_and_accepts_a_fix_of_a_fix(self):
        # Pass 1 fixed A -> B; pass 2 removes B. The chain is valid; a new finding still has to match.
        A, B = '조심하세요. 영은 조건에서 빠져요.', '조심하세요. 0은 조건에서 빠져요.'
        step, task = bash9(NATURAL)
        first = {'sentence': A, 'issue': 'pronunciation-in-text', 'reason': 'r', 'fix': B, 'status': 'fixed'}
        second = {'sentence': B, 'issue': 'filler-caution', 'reason': 'r', 'fix': '', 'status': 'fixed'}
        others = {p['text']: 'real mistake named' for p in review.prompts(task)}
        self.assertEqual(review.problems('bash-basics', step, task, reviewed(step, task, checked=others, findings=[first, second])), [])
        # Without the later finding, the vanished fix B is still reported.
        self.assertRegex(' '.join(review.problems('bash-basics', step, task, reviewed(step, task, checked=others, findings=[first]))),
                         '현재 해설에 없어요')

    def test_record_refuses_a_new_finding_that_matches_nothing(self):
        ledger = {'steps': {}}
        decision = {'lesson': 'bash-basics', 'step': BASH9, 'checked': {},
                    'findings': [{'sentence': '없는 문장이에요.', 'issue': 'i', 'reason': 'r', 'fix': '', 'status': 'fixed'}]}
        with self.assertRaisesRegex(ValueError, '찾지 못했어요'):
            review.record([decision], ledger, dry_run=True)

    def test_whole_registry_is_covered_by_the_ledger(self):
        self.assertEqual(review.status(review.load_ledger())['uncovered'], 0)


if __name__ == '__main__':
    unittest.main()
