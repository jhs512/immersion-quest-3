"""Protect course identities and publication boundaries while adding reviewed metadata."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('metadata_publisher', Path(__file__).with_name('publish-course-improvements.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicationBoundaries(unittest.TestCase):
    def setUp(self):
        self.remote = dict(id='course', lessons=[dict(id='one', revision='v1', sha256='abc', challenge_task='step', title='lesson')], description='keep', change_history=[])
        self.local = copy.deepcopy(self.remote)
        self.local['lessons'][0]['category'] = 'python'
        self.local['categories'] = [dict(id='python', title='Python')]
        self.local['lesson_previews'] = {'one': dict(learn=['values'], challenge='final', scenario=['read', 'change'], constraints=['local'], question='why?')}

    def test_only_authorized_metadata_changes(self):
        result = module.prepare('aice', self.remote, self.local)
        self.assertEqual(result['description'], 'keep')
        self.assertEqual(result['lessons'][0]['revision'], 'v1')
        self.assertEqual(result['lessons'][0]['category'], 'python')
        self.assertNotIn('category', self.remote['lessons'][0])

    def test_unpublished_pin_cannot_sneak_into_metadata_update(self):
        self.local['lessons'][0]['revision'] = 'v2'
        with self.assertRaises(ValueError):
            module.prepare('aice', self.remote, self.local)

    def test_identity_and_missing_briefs_are_refused(self):
        for mutate in [lambda x: x['lessons'][0].update(id='other'), lambda x: x['lesson_previews'].clear()]:
            local = copy.deepcopy(self.local)
            mutate(local)
            with self.assertRaises(ValueError):
                module.prepare('aice', self.remote, local)

    def test_partial_publication_does_not_claim_every_lesson_is_done(self):
        remote = dict(lessons=[dict(id='one', repository='repo/one', revision='v1', sha256='a'),
                               dict(id='two', repository='repo/two', revision='v1', sha256='b')], change_history=[])
        prepared = copy.deepcopy(remote)
        prepared['lessons'][0].update(revision='v2', sha256='c', challenge_task='step')
        rows = [('one', remote['lessons'][0], prepared['lessons'][0], b'')]
        partial = module.module.merge(remote, prepared, rows, 'aice')
        self.assertIn('1/2', partial['change_history'][0]['summary'])
        self.assertNotIn('모든', partial['change_history'][0]['summary'])


if __name__ == '__main__':
    unittest.main()
