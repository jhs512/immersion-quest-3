"""Scope/concurrency properties of the network-only deployment merge; no API calls."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('network_publish',ROOT/'tools/publish-network-foundations.py')
publish=importlib.util.module_from_spec(spec);spec.loader.exec_module(publish)


class NetworkPublication(unittest.TestCase):
    def setUp(self):
        self.local,_=publish.prepared();self.remote=copy.deepcopy(self.local)
        ids={r['id'] for r in self.remote['lessons'] if r['repository'] in {publish.PREFIX+k for k in publish.KEYS}}
        self.remote['lessons']=[r for r in self.remote['lessons'] if r['id'] not in ids]
        for r in self.remote['lessons']:r['prerequisites']=[i for i in r.get('prerequisites',[]) if i not in ids]
        for i in ids:self.remote['lesson_previews'].pop(i,None)

    def test_live_only_lessons_order_and_newer_metadata_survive(self):
        foreign=dict(id='lsn_c2c9e367-d629-490b-9807-c6606ad864ac',title='Fresh live lesson',repository='jhs512/live-only-web',revision='fresh-1',sha256='a'*64)
        self.remote['lessons'].append(foreign);self.remote['title']='Newer live title';self.remote['live_only']={'preserve':True}
        untouched=copy.deepcopy(self.remote)
        result=publish.merge_course(self.remote,self.local)
        repositories={publish.PREFIX+k for k in publish.KEYS}
        before=[r['repository'] for r in self.remote['lessons']]
        after=[r['repository'] for r in result['lessons'] if r['repository'] not in repositories]
        self.assertEqual(before,after);self.assertIn(foreign,result['lessons'])
        self.assertEqual(result['title'],'Newer live title');self.assertEqual(result['live_only'],{'preserve':True})
        self.assertEqual(len(result['lessons']),len(before)+8)
        self.assertEqual(self.remote['lessons'][-1],foreign) # input not mutated
        self.assertEqual(self.remote,untouched)

    def test_replay_is_idempotent(self):
        result=publish.merge_course(self.remote,self.local)
        self.assertEqual(publish.merge_course(result,self.local),result)

    def test_concurrent_network_change_is_not_overwritten(self):
        result=publish.merge_course(self.remote,self.local)
        next(r for r in result['lessons'] if r['repository']==publish.PREFIX+'network-ip')['revision']='someone-else-3'
        with self.assertRaises(ValueError):publish.merge_course(result,self.local)

    def test_wrong_course_identity_is_rejected(self):
        self.remote['id']='another-course'
        with self.assertRaises(ValueError):publish.merge_course(self.remote,self.local)


if __name__=='__main__':unittest.main()
