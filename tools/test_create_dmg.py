import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('create_dmg',Path(__file__).resolve().parents[1]/'packaging/macos/create_dmg.py')
create_dmg=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(create_dmg)


class DiskImageCreationTest(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'Directory symlink creation requires Windows privileges')
    def test_applications_link_does_not_count_the_linked_directory_contents(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'source'
            source.mkdir()
            outside = root / 'Applications'
            outside.mkdir()
            with (outside / 'unrelated').open('wb') as file:
                file.truncate(1024 * 1024 * 1024)
            (source / 'Applications').symlink_to(outside, target_is_directory=True)
            (source / 'app').write_bytes(b'app')
            expected = 3 + (source / 'Applications').lstat().st_size
            self.assertEqual(create_dmg.source_bytes(source), expected)

    def test_hdiutil_failure_is_not_reported_as_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'source'
            source.mkdir()
            def execute(argv, **kwargs):
                raise subprocess.CalledProcessError(1, argv)
            with self.assertRaises(subprocess.CalledProcessError):
                create_dmg.create_image(source, Path(temporary) / 'out.dmg', 'image', execute=execute)

    def test_real_image_command_reserves_room_for_the_observed_intel_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            source=root/'한글 image';source.mkdir()
            with (source/'molip-quest').open('wb') as file:
                file.truncate(87320848)
            destination=root/'release image.dmg'
            calls=[]
            def execute(argv,**kwargs):
                calls.append(argv)
                return subprocess.CompletedProcess(argv,0)
            result=create_dmg.create_image(source,destination,'image',execute=execute)
            self.assertEqual(result['source_bytes'],87320848)
            args=calls[0]
            size=int(args[args.index('-size')+1].removesuffix('m'))*1024*1024
            self.assertGreaterEqual(size,87320848+64*1024*1024)
            self.assertLess(size,256*1024*1024)
            self.assertEqual(args[args.index('-srcfolder')+1],str(source.resolve()))
            self.assertEqual(args[-1],str(destination.resolve()))


if __name__=='__main__':
    unittest.main()
