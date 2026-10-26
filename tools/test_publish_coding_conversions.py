import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('coding_publisher',Path(__file__).with_name('publish-coding-conversions.py'))
publish=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class MergeTests(unittest.TestCase):
    def test_generated_history_uses_the_players_utc_seconds_contract(self):
        merged=publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')])
        self.assertTrue(merged['change_history'])
        for row in merged['change_history']:
            self.assertRegex(row['at'],r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

    def test_revision_numbers_cannot_reuse_or_go_back_to_published_versions(self):
        old=dict(id='lesson',revision='java-crud-5')
        for revision in ['java-crud-4','java-crud-5']:
            with self.assertRaises(ValueError):
                publish.check_transition('java-crud',old,dict(id='lesson',revision=revision))
        publish.check_transition('java-crud',old,dict(id='lesson',revision='java-crud-6'))

    def setUp(self):
        self.old={'id':'retained','repository':'jhs512/mq3-lesson-redesigned-java-values','revision':'old','sha256':'a'*64}
        self.new={**self.old,'revision':'new','sha256':'b'*64}
        self.remote={'id':'course','lessons':[self.old,{'id':'new-docker','repository':'another-new-lesson'}],
                     'categories':[{'id':'docker','title':'Docker'}], 'description':'concurrent description',
                     'scope_note':'Docker and DB are delivered; Spring remains planned',
                     'lesson_previews':{'new-docker':{'challenge':'keep this'}},'change_history':[]}
        self.prepared={'lesson_previews':{'retained':{'challenge':'code directly'}}}

    def test_new_docker_lessons_categories_and_other_changes_survive(self):
        old=copy.deepcopy(self.remote)
        merged=publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')])
        self.assertEqual(self.remote,old)
        self.assertEqual(merged['lessons'][0],self.new)
        self.assertEqual(merged['lessons'][1],old['lessons'][1])
        self.assertEqual(merged['categories'],old['categories'])
        self.assertEqual(merged['description'],old['description'])
        self.assertEqual(merged['scope_note'],old['scope_note'])
        self.assertEqual(merged['lesson_previews']['new-docker'],old['lesson_previews']['new-docker'])
        self.assertEqual(publish.merge(merged,self.prepared,[(self.old,self.new,b'')]),merged)

    def test_a_concurrent_revision_is_rejected(self):
        self.remote['lessons'][0]={**self.old,'revision':'someone-elses-newer-version'}
        with self.assertRaisesRegex(ValueError,'Concurrent course revision'):
            publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')])

    def test_concurrent_metadata_on_the_updated_lesson_is_kept(self):
        self.remote['lessons'][0].update(category='java',track='basic',prerequisites=['new-docker'])
        merged=publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')])
        self.assertEqual(merged['lessons'][0]['revision'],'new')
        self.assertEqual(merged['lessons'][0]['prerequisites'],['new-docker'])
        self.assertEqual(merged['lessons'][0]['track'],'basic')

    def test_second_batch_keeps_all_new_lessons_and_coding_history(self):
        self.remote['lessons']=[dict(id=key,repository='jhs512/mq3-lesson-redesigned-'+key,revision='old') for key in publish.SECOND_BATCH]+[{'id':'new-docker','repository':'another-new-lesson'}]
        self.remote['change_history']=[{'summary':'Java 12수업의 선택 문제를 직접 구현하는 문제로 바꿨어요.'}]
        rows=[(copy.deepcopy(row),{**row,'revision':'new'},b'') for row in self.remote['lessons'][:-1]]
        merged=publish.merge(self.remote,self.prepared,rows)
        self.assertEqual(len(merged['lessons']),10)
        self.assertEqual(merged['lessons'][-1],self.remote['lessons'][-1])
        self.assertEqual(len(merged['change_history']),2)
        self.assertIn('Java 5수업과 Git 4수업',merged['change_history'][0]['summary'])
        self.assertEqual(publish.merge(merged,self.prepared,rows),merged)

    def test_order_changes_preserve_newer_unrelated_content_and_track(self):
        self.remote['lessons'][1].update(revision='newer-remote',track='advanced',category='docker')
        self.prepared['lessons']=[
            {**self.remote['lessons'][1], 'revision':'older-local', 'prerequisites':[]},
            {**self.new, 'prerequisites':['new-docker']},
        ]
        merged=publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')],True)
        self.assertEqual([l['id'] for l in merged['lessons']],['new-docker','retained'])
        self.assertEqual(merged['lessons'][0]['revision'],'newer-remote')
        self.assertEqual(merged['lessons'][0]['track'],'advanced')
        self.assertEqual(merged['lessons'][1]['prerequisites'],['new-docker'])
        self.assertEqual(merged['scope_note'],self.remote['scope_note'])

    def test_order_changes_refuse_to_erase_a_concurrently_added_lesson(self):
        self.prepared['lessons']=[{**self.new,'prerequisites':[]}]
        with self.assertRaisesRegex(ValueError,'Concurrent course membership'):
            publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')],True)


if __name__=='__main__':unittest.main()
