import copy
import unittest

from publish_engineer_bottom_up import COURSE, merge


class LiveCourseMergeTests(unittest.TestCase):
    def setUp(self):
        self.foundation = dict(id='foundation', repository='jhs512/mq3-lesson-redesigned-foundation', revision='newer-live-revision')
        self.addition = dict(id='addition', repository='jhs512/mq3-lesson-redesigned-extension', revision='extension-1')
        self.remote = dict(id='course', repository=COURSE, title='Live title', categories=[{'id': 'keep'}],
                           lessons=[self.foundation, dict(id='other', repository='teacher/extra', revision='1')],
                           change_history=[dict(summary='A concurrent author update')])
        self.prepared = dict(id='course', lessons=[self.addition], change_history=[dict(summary='보강 수업 32개')])
        self.additions = [dict(key='extension', after='foundation')]

    def test_new_content_keeps_live_old_revisions_metadata_and_unrelated_lessons(self):
        before = copy.deepcopy(self.remote)
        actual = merge(self.remote, self.prepared, self.additions)
        self.assertEqual(actual['lessons'], [self.foundation, self.addition, before['lessons'][1]])
        self.assertEqual(actual['title'], before['title'])
        self.assertEqual(actual['categories'], before['categories'])
        self.assertEqual(actual['change_history'][1], before['change_history'][0])
        self.assertEqual(self.remote, before)

    def test_retry_is_idempotent(self):
        first = merge(self.remote, self.prepared, self.additions)
        self.assertEqual(merge(first, self.prepared, self.additions), first)

    def test_conflicting_remote_addition_is_never_overwritten(self):
        first = merge(self.remote, self.prepared, self.additions)
        first['lessons'][1]['revision'] = 'another-author-revision'
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            merge(first, self.prepared, self.additions)


if __name__ == '__main__':
    unittest.main()
