"""Compatibility entry point for the first approved Git lesson."""
import runpy
import sys
from pathlib import Path

sys.argv.extend(['--lesson', 'git-first'])
runpy.run_path(str(Path(__file__).with_name('build-redesigned-git.py')), run_name='__main__')
