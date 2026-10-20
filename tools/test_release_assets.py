import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('release_assets',Path(__file__).with_name('verify-release-assets.py'))
assets=importlib.util.module_from_spec(spec);spec.loader.exec_module(assets)

class DesktopReleaseTests(unittest.TestCase):
    def test_windows_and_apple_silicon_release_does_not_require_intel(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with (root/'molip-quest-3-windows-x64-setup.exe').open('wb') as stream:
                stream.write(b'MZ');stream.seek(0x3c);stream.write((128).to_bytes(4,'little'))
                stream.seek(128);stream.write(b'PE\x00\x00');stream.truncate(1_000_001)
            # Minimal containers exercise the completeness gate, not DMG signing.
            arm=root/'molip-quest-3-macos-arm64.dmg';arm.write_bytes(b'koly'+b'\0'*508)
            assets.verify(root,desktop=True)
            arm.unlink()
            with self.assertRaisesRegex(ValueError,'arm64'):
                assets.verify(root,desktop=True)

if __name__=='__main__':unittest.main()
