"""Check required release containers. Does not certify code signing, notarization or runtime."""
import sys
import zipfile
from pathlib import Path


def verify(root, windows_only=False, desktop=False):
    windows = root / ('molip-quest-3-windows-x64-setup.exe' if windows_only or desktop else 'molip-quest-windows-x64-setup.exe')
    macos = root / 'molip-quest-macos-arm64.dmg'
    android = root / 'molip-quest-android.apk'
    macs = tuple(root / f'molip-quest-3-macos-{arch}.dmg' for arch in ('arm64','x86_64')) if desktop else (macos,)
    for path in ((windows,) if windows_only else (windows, *macs) if desktop else (windows, macos, android)):
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f'Missing installer: {path.name}')
    with windows.open('rb') as stream:
        if stream.read(2) != b'MZ':
            raise ValueError('Windows installer is not an executable')
        if windows_only or desktop:
            stream.seek(0x3c)
            offset = int.from_bytes(stream.read(4), 'little')
            stream.seek(offset)
            if stream.read(4) != b'PE\x00\x00' or windows.stat().st_size < 1_000_000:
                raise ValueError('Windows installer is incomplete or not a PE executable')
    if windows_only:
        return
    for image in macs:
        with image.open('rb') as stream:
            # A UDIF disk image ends with a 512-byte 'koly' trailer.
            stream.seek(-512, 2)
            if stream.read(4) != b'koly':
                raise ValueError('macOS disk image has no UDIF trailer')
    if desktop:
        return
    with zipfile.ZipFile(android) as apk:
        names = apk.namelist()
        if 'AndroidManifest.xml' not in names:
            raise ValueError('APK has no Android manifest')
        if not any(name.startswith('lib/arm64-v8a/') and name.endswith('.so') for name in names):
            raise ValueError('APK has no arm64 native library')


if __name__ == '__main__':
    verify(Path(sys.argv[1]), windows_only='--windows-only' in sys.argv, desktop='--desktop' in sys.argv)
    print('Required installer containers are present. Signing and device testing are separate release requirements.')
