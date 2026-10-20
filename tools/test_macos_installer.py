"""Exercise installer CPU selection without touching apps, network or Python envs."""
from pathlib import Path
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = r"C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")

class MacInstallerTests(unittest.TestCase):
    def test_scripts_have_valid_bash_syntax(self):
        for script in ("install.sh", "bundle.sh"):
            subprocess.run([BASH, "-n", (ROOT / "packaging/macos" / script).as_posix()], check=True)

    def select(self, cpu, translated="0"):
        # Stop before the first filesystem mutation. Only uname/sysctl are mocked.
        source = (ROOT / "packaging/macos/install.sh").read_text(encoding="utf-8").split("\ndest=/Applications", 1)[0]
        mocks = f'''uname() {{ if [ "$1" = -s ]; then echo Darwin; else echo {cpu}; fi; }}
sysctl() {{ echo {translated}; }}
'''
        return subprocess.run([BASH, "-c", mocks + source + '\nprintf "%s|%s" "$arch" "$python_version"'], text=True, capture_output=True, encoding="utf-8")

    def test_native_cpus_select_matching_app_and_python(self):
        for cpu, python in (("arm64", "3.13"), ("x86_64", "3.12")):
            result = self.select(cpu)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"{cpu}|{python}")

    def test_rosetta_cannot_install_the_intel_stack_on_apple_silicon(self):
        result = self.select("x86_64", "1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Rosetta", result.stdout)

if __name__ == "__main__":
    unittest.main()
