"""Build the existing Pages dashboard with direct course paths and a SPA fallback."""
import json
from pathlib import Path
import re
import shutil
import sys

root = Path(__file__).resolve().parents[1]
output = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'public'
for name in ['dashboard', 'open']:
    folder = output / name
    folder.mkdir(parents=True, exist_ok=True)
    for source in (root / 'site' / name).iterdir():
        if source.is_file():
            shutil.copyfile(source, folder / source.name)
html = (root / 'site/dashboard/index.html').read_text(encoding='utf-8')
# Known basic courses return HTTP 200. Other public courses use the same app at
# the original requested path via GitHub Pages' custom 404 document.
for manifest in (root / 'courses/redesigned-courses').glob('*.json'):
    repo = json.loads(manifest.read_text(encoding='utf-8'))['repository']
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo) or any(x in ['.', '..'] for x in repo.split('/')):
        raise ValueError('Invalid course repository')
    target = output / 'dashboard' / repo / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding='utf-8')
(output / '404.html').write_text(html, encoding='utf-8')
(output / 'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=dashboard/"><title>MQ</title><a href="dashboard/">Dashboard</a></html>', encoding='utf-8')
(output / '.nojekyll').touch()
print('Dashboard assets, direct course routes and fallback built')
