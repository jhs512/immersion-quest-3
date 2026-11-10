"""Regression checks for orientation, highlights and unchanged executable lessons."""
import copy
import json
from pathlib import Path
import unittest

from lesson_registry import load_registry
from narration_openings import INTRO, compile_openings, overview_text, plain

ROOT = Path(__file__).resolve().parents[1]


def actions(narration):
    """Everything the narration does besides speaking: commands, edits, runs, in order."""
    return [a for a in narration if a['action'] != 'say']


class OpeningTests(unittest.TestCase):
    def test_all_published_lessons_start_with_goals_then_problem(self):
        introductions = json.loads(INTRO.read_text(encoding='utf-8'))
        rows = load_registry()
        self.assertEqual(set(introductions), {row['key'] for row in rows})
        total = 0
        for row in rows:
            key = row['key']
            with self.subTest(lesson=key):
                path = f'courses/redesigned/{key}.json'
                lesson = json.loads((ROOT / path).read_text(encoding='utf-8'))
                source = json.loads((ROOT / 'tools/redesigned_lessons' / row['folder'] / 'content.json').read_text(encoding='utf-8'))
                # Openings only prepend speech: every authored field, grader and action is published as written.
                self.assertEqual([t['id'] for t in lesson['tasks']], [t['id'] for t in source['tasks']])
                for task, authored in zip(lesson['tasks'], source['tasks']):
                    for field, value in authored.items():
                        if field != 'narration':
                            self.assertEqual(task[field], value, f"{task['id']} {field}: grading and task content must not change")
                    self.assertEqual(actions(task['narration']), actions(authored['narration']), f"{task['id']}: actions must not change")
                expected = copy.deepcopy(source['tasks'])
                compile_openings(key, expected)
                for index, (task, authored, compiled) in enumerate(zip(lesson['tasks'], source['tasks'], expected)):
                    total += 1
                    self.assertEqual(task['narration'], compiled['narration'])
                    offset = len(introductions[key]) if index == 0 else 0
                    if index == 0:
                        self.assertEqual([a['text'] for a in task['narration'][:offset]], introductions[key])
                        self.assertTrue(all(a['action'] == 'say' and 'target' not in a for a in task['narration'][:offset]))
                    overview = task['narration'][offset]
                    self.assertEqual(overview['action'], 'say')
                    self.assertEqual(overview['text'], overview_text(authored))
                    self.assertEqual(overview['target'], f'text:{plain(task["title"])}#1')
                    self.assertLessEqual(len(overview['text']), 160)
        self.assertEqual(total, 1125)

    def test_preserve_code_names(self):
        self.assertEqual(plain('`fit_transform` 값을 확인해요'), 'fit_transform 값을 확인해요')

    def test_move_summary_without_repeating_or_losing_actions(self):
        tasks = [dict(id='test', title='파일을 읽으세요', narration=[
            dict(action='say', text='먼저 파일이 있어요. 파일을 읽는 문제예요.', target='text:파일#1'),
            dict(action='bash_command', command='cat memo.txt'),
            dict(action='say', text='내용이 보여요.')])]
        compile_openings('bash-basics', tasks)
        narration = tasks[0]['narration']
        self.assertEqual(sum(a.get('text', '').count('파일을 읽는 문제예요.') for a in narration), 1)
        self.assertIn(dict(action='say', text='먼저 파일이 있어요.', target='text:파일#1'), narration)
        self.assertIn(dict(action='bash_command', command='cat memo.txt'), narration)

    def test_unrecognized_problem_fails_instead_of_generic_intro(self):
        with self.assertRaises(ValueError):
            overview_text(dict(id='unknown', title='제목만 있어요', narration=[]))


if __name__ == '__main__':
    unittest.main()
