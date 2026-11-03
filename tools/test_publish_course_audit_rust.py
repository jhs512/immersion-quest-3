import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('audit_release', Path(__file__).with_name('publish-course-audit-rust.py'))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def row(key, revision=1):
    return {'id': key, 'repository': 'jhs512/mq3-lesson-redesigned-' + key,
            'revision': f'{key}-{revision}', 'sha256': f'{key}:{revision}', 'title': key,
            'required': False, 'prerequisites': []}


class PublicationMerge(unittest.TestCase):
    def setUp(self):
        self.old = row('java-conditions')
        self.new = row('java-conditions', 2)
        self.rust = [row(key) for key in release.RUST]
        self.remote = {'id': 'course', 'title': 'Remote edited title',
                       'lessons': [row('java-launch'), self.old, row('web-todo-dom'), row('react-todo')],
                       'change_history': [{'summary': 'Remote history'}], 'custom': {'keep': True}}
        self.prepared = {'lessons': [row('java-launch'), *self.rust, self.new],
                         'categories': [{'id': 'rust', 'title': 'Rust'}],
                         'lesson_previews': {item['id']: {'summary': item['title']} for item in self.rust}}

    def test_existing_revision_preserves_remote_metadata_and_unrelated_lessons(self):
        self.remote['lessons'][1] = dict(self.old, title='Remote lesson title', required=True)
        before = copy.deepcopy(self.remote)
        result = release.merge_course(self.remote, self.prepared, [(self.old, self.new, b'')])
        self.assertEqual(self.remote, before)
        self.assertEqual(result['lessons'][1], dict(before['lessons'][1], revision=self.new['revision'], sha256=self.new['sha256']))
        self.assertEqual(result['lessons'][2:], before['lessons'][2:])
        self.assertEqual(result['title'], before['title'])
        self.assertEqual(result['custom'], before['custom'])
        self.assertEqual(result['change_history'], before['change_history'])

    def test_new_rust_lessons_follow_java_launch_without_removing_remote_extras(self):
        rows = [(None, item, b'') for item in self.rust]
        result = release.merge_course(self.remote, self.prepared, rows)
        self.assertEqual([item['id'] for item in result['lessons']],
                         ['java-launch', *release.RUST, 'java-conditions', 'web-todo-dom', 'react-todo'])
        self.assertEqual(result['categories'], [{'id': 'rust', 'title': 'Rust'}])
        self.assertEqual(release.merge_course(result, self.prepared, rows), result)

    def test_concurrent_revision_is_rejected(self):
        self.remote['lessons'][1] = row('java-conditions', 3)
        with self.assertRaisesRegex(ValueError, 'Concurrent'):
            release.merge_course(self.remote, self.prepared, [(self.old, self.new, b'')])

    def test_removed_existing_lesson_is_not_restored_silently(self):
        self.remote['lessons'].pop(1)
        with self.assertRaisesRegex(ValueError, 'removed concurrently'):
            release.merge_course(self.remote, self.prepared, [(self.old, self.new, b'')])

    def test_rust_category_conflict_is_rejected(self):
        self.remote['categories'] = [{'id': 'rust', 'title': 'Someone else changed this'}]
        with self.assertRaisesRegex(ValueError, 'category'):
            release.merge_course(self.remote, self.prepared, [(None, item, b'') for item in self.rust])


if __name__ == '__main__':
    unittest.main()
