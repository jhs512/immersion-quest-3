import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('course_copy', Path(__file__).with_name('publish-course-copy.py'))
course_copy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(course_copy)


def lesson():
    return {'revision': 'engineer-design-6-spacing-20261103', 'tasks': [{
        'goal': '어떤 관점일까요?\n\n**할 일**\n\n1. 선택한 보기를 제출하세요.',
        'solution': 'structure', 'interaction': {'kind': 'choice', 'answer': 'structure'},
        'narration': [{'action': 'say', 'text': '조심하세요. 모호한 경고예요.'},
                      {'action': 'choose_answer', 'id': 'structure'}]}]}


def row(key, revision, sha):
    return {'id': 'lsn_' + key, 'repository': 'jhs512/mq3-lesson-redesigned-' + key, 'revision': revision, 'sha256': sha}


class ReviewedPayload(unittest.TestCase):
    def test_default_suffix_keeps_spacing_revision_names(self):
        original = dict(lesson(), revision='engineer-design-6')
        self.assertEqual(course_copy.reviewed_payload(original, [])['revision'], 'engineer-design-6-spacing-20261103')

    def test_suffix_names_a_new_revision_on_top_of_the_live_one(self):
        edit = {'path': ['tasks', 0, 'goal'], 'old': lesson()['tasks'][0]['goal'], 'new': '어떤 관점일까요?'}
        result = course_copy.reviewed_payload(lesson(), [edit], 'todo-20261103')
        self.assertEqual(result['revision'], 'engineer-design-6-spacing-20261103-todo-20261103')
        self.assertEqual(result['tasks'][0]['goal'], '어떤 관점일까요?')
        self.assertEqual(result['tasks'][0]['interaction'], lesson()['tasks'][0]['interaction'])

    def test_grading_fields_and_stale_baselines_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'grading'):
            course_copy.reviewed_payload(lesson(), [{'path': ['tasks', 0, 'solution'], 'old': 'structure', 'new': 'time'}])
        with self.assertRaisesRegex(ValueError, 'baseline'):
            course_copy.reviewed_payload(lesson(), [{'path': ['tasks', 0, 'goal'], 'old': 'older text', 'new': 'x'}])

    def test_narration_list_may_change_only_spoken_prose(self):
        old = lesson()['tasks'][0]['narration']
        fixed = copy.deepcopy(old)
        fixed[0] = {'action': 'say', 'text': '조심하세요. time을 고르면 순서만 보여요.', 'target': 'answer:time'}
        result = course_copy.reviewed_payload(lesson(), [{'path': ['tasks', 0, 'narration'], 'old': old, 'new': fixed}])
        self.assertEqual(result['tasks'][0]['narration'], fixed)
        demo = copy.deepcopy(old)
        demo[1]['id'] = 'time'
        with self.assertRaisesRegex(ValueError, 'demo'):
            course_copy.reviewed_payload(lesson(), [{'path': ['tasks', 0, 'narration'], 'old': old, 'new': demo}])
        editor = copy.deepcopy(old)
        editor[0]['target'] = 'editor'
        with self.assertRaisesRegex(ValueError, 'prose'):
            course_copy.reviewed_payload(lesson(), [{'path': ['tasks', 0, 'narration'], 'old': old, 'new': editor}])


class CourseMerge(unittest.TestCase):
    def setUp(self):
        self.before = row('engineer-design', 'engineer-design-6-spacing-20261103', 'a' * 64)
        self.after = dict(self.before, revision='engineer-design-6-spacing-20261103-todo-20261103', sha256='b' * 64)
        self.current = {'categories': [{'id': 'design'}], 'learning_sequence': ['x'], 'change_history': [{'summary': 'old'}],
                        'lessons': [row('engineer-python-basics', 'engineer-python-basics-1', 'c' * 64),
                                    dict(self.before, prerequisites=['lsn_engineer-python-basics'], category='design')]}

    def test_only_reviewed_rows_change_and_remote_metadata_survives(self):
        merged = course_copy.merge_rows(self.current, [(self.before['id'], self.before, self.after)], {'summary': 'new'})
        self.assertEqual(merged['lessons'][0], self.current['lessons'][0])
        self.assertEqual(merged['lessons'][1], dict(self.current['lessons'][1], revision=self.after['revision'], sha256=self.after['sha256']))
        self.assertEqual({k: merged[k] for k in ('categories', 'learning_sequence')}, {k: self.current[k] for k in ('categories', 'learning_sequence')})
        self.assertEqual(merged['change_history'], [{'summary': 'new'}, {'summary': 'old'}])

    def test_rerun_after_publication_adds_nothing(self):
        published = course_copy.merge_rows(self.current, [(self.before['id'], self.before, self.after)], {'summary': 'new'})
        self.assertEqual(course_copy.merge_rows(published, [(self.before['id'], self.before, self.after)], {'summary': 'again'}), published)

    def test_a_concurrent_revision_is_not_overwritten(self):
        self.current['lessons'][1]['revision'] = 'engineer-design-7'
        with self.assertRaisesRegex(ValueError, 'concurrently'):
            course_copy.merge_rows(self.current, [(self.before['id'], self.before, self.after)], {'summary': 'new'})


if __name__ == '__main__':
    unittest.main()
