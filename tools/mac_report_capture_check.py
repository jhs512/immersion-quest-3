"""Checks the report screen capture of the real MQ.app on a Mac without a Screen Recording grant.

Both MQ and the report capture helper are started through LaunchServices (`open -n`), so each
runs as MQ.app itself, a fresh ad-hoc signed bundle that this Mac never granted Screen
Recording. That is a student's first report after installing or updating MQ. The CI shell
has its own grant, so a helper started from the shell would not show the failure.

The second round re-signs the bundle with a new build number, giving it a new code
signature as an update does, and captures again.
"""
import json
import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path

APP = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
EXECUTABLE = APP / "Contents/MacOS/molip-quest"


def preflight():
    probe = WORK / "preflight.swift"
    probe.write_text("import CoreGraphics\nprint(CGPreflightScreenCaptureAccess())\n")
    return subprocess.run(["swift", str(probe)], capture_output=True, text=True).stdout.strip()


def open_app(data, *args, wait=False):
    command = ["open", "-n"] + (["-W"] if wait else []) + ["--env", f"MOLIP_DATA_DIR={data}", str(APP)]
    if args:
        command += ["--args", *args]
    subprocess.run(command, check=True)


def main_pid():
    rows = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True).stdout
    found = [int(line.split(None, 1)[0]) for line in rows.splitlines()
             if line.strip().endswith(str(EXECUTABLE))]
    return found[-1] if found else None


def capture_round(name):
    data = WORK / name
    data.mkdir(parents=True)
    open_app(data)
    deadline = time.time() + 90
    pid = None
    attempt = 0
    result = {}
    while time.time() < deadline:
        pid = pid or main_pid()
        if pid is None:
            time.sleep(1)
            continue
        attempt += 1
        folder = data / "bug-reports" / f"check-{attempt}"
        folder.mkdir(parents=True)
        screen = folder / "screen.png"
        open_app(data, "--capture-report", str(pid), str(screen), wait=True)
        status = folder / "capture-status.json"
        result = {"attempt": attempt, "pid": pid,
                  "status": json.loads(status.read_text()) if status.exists() else None}
        if screen.exists():
            size = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(screen)],
                                  capture_output=True, text=True).stdout.split()
            result.update(screen=str(screen), bytes=screen.stat().st_size,
                          width=int(size[size.index("pixelWidth:") + 1]),
                          height=int(size[size.index("pixelHeight:") + 1]))
            break
        time.sleep(3)
    if pid:
        subprocess.run(["kill", str(pid)])
        time.sleep(2)
    return result


def resign_as_update():
    info = APP / "Contents/Info.plist"
    with info.open("rb") as handle:
        plist = plistlib.load(handle)
    before = subprocess.run(["codesign", "-dvvv", str(APP)], capture_output=True, text=True).stderr
    plist["CFBundleVersion"] = str(int(plist.get("CFBundleVersion", "0") or 0) + 1)
    with info.open("wb") as handle:
        plistlib.dump(plist, handle)
    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(APP)], check=True)
    after = subprocess.run(["codesign", "-dvvv", str(APP)], capture_output=True, text=True).stderr
    hash_of = lambda text: next((l for l in text.splitlines() if l.startswith("CDHash=")), "")
    return hash_of(before), hash_of(after)


WORK.mkdir(parents=True, exist_ok=True)
report = {"macos": subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True).stdout.strip(),
          "shell_screen_recording_grant": preflight(),
          "install": capture_round("install")}
report["update_cdhash"] = resign_as_update()
report["update"] = capture_round("update")
(WORK / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
failed = [name for name in ("install", "update")
          if report[name].get("width", 0) < 200 or report[name].get("height", 0) < 200]
assert report["update_cdhash"][0] != report["update_cdhash"][1], "update did not change the code signature"
assert not failed, f"MQ window was not captured after {', '.join(failed)}: " + json.dumps([report[n] for n in failed], ensure_ascii=False)
print("MQ window captured after install and after update, without a Screen Recording grant")
