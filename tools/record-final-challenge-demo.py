"""Record real Python demo outputs; task grading expectations remain independently authored."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/final_challenges'))
python = ROOT / 'target/ml-env/Scripts/python.exe'
for key in sys.argv[1:]:
    path = ROOT / 'tools/final_challenges' / (key.replace('-', '_') + '.py')
    module_spec = importlib.util.spec_from_file_location(key, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    spec = module.SPEC
    snapshots = spec.get('_snapshots') or module.s.snapshots
    runs = [a for a in spec['task']['narration'] if a['action'] == 'run']
    recorded = []
    for source, run in zip(snapshots, runs, strict=True):
        with tempfile.TemporaryDirectory() as folder:
            for name, body in spec['task'].get('files', {}).items():
                target = Path(folder, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding='utf-8')
            Path(folder, 'main.py').write_text(source, encoding='utf-8')
            result = subprocess.run([str(python), '-X', 'utf8', 'main.py'], cwd=folder,
                capture_output=True, text=True, encoding='utf-8', timeout=180,
                env=dict(os.environ, MPLBACKEND='Agg', TF_CPP_MIN_LOG_LEVEL='3'))
        if result.returncode:
            error = run.get('expect_error')
            assert error and error in result.stderr, (key, result.stderr[-2000:])
            expected = dict(pattern=error)
        else:
            assert not run.get('expect_error'), key
            expected = result.stdout.strip()
        recorded.append(dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(), expected=expected))
    output = ROOT / 'tools/final_challenges/recorded' / f'{key}.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(recorded, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{key}: {len(recorded)} real demo outputs recorded', flush=True)
