import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('coding_publisher',Path(__file__).with_name('publish-coding-conversions.py'))
publish=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.old={'id':'retained','repository':'jhs512/mq3-lesson-redesigned-java-values','revision':'old','sha256':'a'*64}
        self.new={**self.old,'revision':'new','sha256':'b'*64}
        self.remote={'id':'course','lessons':[self.old,{'id':'new-docker','repository':'another-new-lesson'}],
                     'categories':[{'id':'docker','title':'Docker'}], 'description':'concurrent description',
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
        self.assertEqual(merged['lesson_previews']['new-docker'],old['lesson_previews']['new-docker'])
        self.assertEqual(publish.merge(merged,self.prepared,[(self.old,self.new,b'')]),merged)

    def test_a_concurrent_revision_is_rejected(self):
        self.remote['lessons'][0]={**self.old,'revision':'someone-elses-newer-version'}
        with self.assertRaisesRegex(ValueError,'Concurrent course revision'):
            publish.merge(self.remote,self.prepared,[(self.old,self.new,b'')])


if __name__=='__main__':unittest.main()
