"""Exercise MQ's actual build.rs with Cargo, using synthetic public inputs only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='mq-build-inputs-') as directory:
        root = Path(directory)
        (root / 'src').mkdir()
        (root / 'courses').mkdir()
        (root / 'site').mkdir()
        (root / 'tools/redesigned_courses').mkdir(parents=True)
        (root / 'assets/icon').mkdir(parents=True)
        shutil.copyfile(ROOT / 'build.rs', root / 'build.rs')
        shutil.copyfile(ROOT / 'assets/icon/icon.ico', root / 'assets/icon/icon.ico')
        (root / 'tools/redesigned_courses/catalog.json').write_text('{"courses": []}')
        (root / 'src/main.rs').write_text('fn main() {}')
        (root / 'Cargo.toml').write_text('''[package]
name = "mq-build-input-check"
version = "0.0.0"
edition = "2021"
[build-dependencies]
serde_json = "1"
[target.'cfg(windows)'.build-dependencies]
winresource = "0.1"
''')
        env = dict(os.environ)
        # Never borrow another checkout's Cargo artifacts or expose local instructor data.
        env['CARGO_TARGET_DIR'] = str(root / 'target')
        env['CARGO_LOG'] = 'cargo::core::compiler::fingerprint=info'
        measurements = []

        def build(label, changed):
            start = time.perf_counter()
            result = subprocess.run(['cargo', 'check', '--offline', '-vv'], cwd=root,
                                    env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
            elapsed = round(time.perf_counter() - start, 3)
            if result.returncode:
                raise AssertionError(result.stderr[-4000:])
            # Cargo may say Checking rather than Compiling for the root target on
            # macOS. Observe execution of the build script, not that status label.
            rebuilt = any('Running ' in line and 'build-script-build' in line
                          for line in result.stderr.splitlines())
            measurements.append({'case': label, 'seconds': elapsed, 'rebuilt': rebuilt})
            print(json.dumps(measurements[-1]), flush=True)
            assert rebuilt == changed, '\n'.join(line for line in result.stderr.splitlines()
                                                 if 'Dirty' in line or 'missing' in line or 'Fresh mq-' in line)
            return next((root / 'target/debug/build').glob('mq-build-input-check-*/out'))

        build('initial absent inputs', True)
        build('unchanged absent inputs', False)
        for source, output in [('courses/kpc-solutions.json', 'private-solutions.json'),
                               ('site/data/instructor.json', 'private-instructor.json')]:
            path = root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{"synthetic": 1}')
            out = build(source + ': created', True)
            assert json.loads((out / output).read_text()) == {'synthetic': 1}
            build(source + ': unchanged', False)
            # Force a distinct mtime even on coarse timestamp filesystems.
            time.sleep(1.05)
            path.write_text('{"synthetic": 2}')
            out = build(source + ': changed', True)
            assert json.loads((out / output).read_text()) == {'synthetic': 2}
            build(source + ': unchanged again', False)
            path.unlink()
            out = build(source + ': deleted', True)
            assert json.loads((out / output).read_text()) == {}
            build(source + ': still absent', False)
        print('PASS: optional input creation, edits, deletion and idle builds')


if __name__ == '__main__':
    main()
