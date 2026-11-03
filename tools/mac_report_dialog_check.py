"""Drives the real Mac report dialog of MQ.app: dialog -> capture helper -> MQ, then 다시 캡처.

MQ and `--report-dialog` both start through LaunchServices as MQ.app, so the dialog spawns
the capture helper exactly as it does for a student. MQ is first paused with SIGSTOP so
the helper times out and the dialog offers 다시 캡처. MQ is then resumed and the button is
clicked with a CGEvent at the label Vision reads, because System Events does not list the
dialog's window. The dialog must come back with 캡처 확인 and a screen.png.
The dialog is cancelled at the end, so nothing is sent to GitHub.
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

APP = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
EXECUTABLE = APP / "Contents/MacOS/molip-quest"
DATA = WORK / "data"
UI = WORK / "dialog-ui"


def processes():
    rows = subprocess.run(["ps", "-axo", "pid=,ppid=,command="], capture_output=True, text=True).stdout
    return [(int(p), int(pp), c) for p, pp, c in (line.split(None, 2) for line in rows.splitlines() if line.strip())]


def wait_for(check, seconds, what):
    deadline = time.time() + seconds
    while time.time() < deadline:
        value = check()
        if value:
            return value
        time.sleep(0.5)
    raise AssertionError(f"timed out waiting for {what}")


def dialog_pid():
    found = [p for p, _, c in processes() if c.startswith("/usr/bin/osascript -l JavaScript") and "report.js" in c]
    return found[-1] if found else None


def dialog_state(_osascript):
    seen = json.loads(subprocess.run([str(UI), "read", str(WORK / "dialog-read.png")], capture_output=True, text=True).stdout or "{}")
    if not seen.get("dialog"):
        report["last_ui_windows"] = seen.get("windows")
        return None
    lines = seen["lines"]
    return {"bounds": seen["dialog"], "buttons": [l["text"] for l in lines], "text": " ".join(l["text"] for l in lines), "lines": lines}


def click(_osascript, name):
    state = wait_for(lambda: dialog_state(None), 10, f"dialog with {name}")
    # Exact label: the message sentence also contains "다시 캡처".
    line = next((l for l in state["lines"] if l["text"].replace(" ", "") == name.replace(" ", "")), None)
    assert line, f"no {name} on the dialog: {state['buttons']}"
    subprocess.run([str(UI), "click", str(line["x"]), str(line["y"])], check=True)


def screenshot(name):
    subprocess.run(["screencapture", "-x", str(WORK / f"{name}.png")])


WORK.mkdir(parents=True, exist_ok=True)
DATA.mkdir(exist_ok=True)
report = {}
subprocess.run(["swiftc", "-O", "-o", str(UI), str(Path(__file__).with_name("mac_dialog_ui.swift"))], check=True)
env = ["--env", f"MOLIP_DATA_DIR={DATA}"]
subprocess.run(["open", "-n", *env, str(APP)], check=True)
main = wait_for(lambda: next((p for p, _, c in processes() if c.strip().endswith(str(EXECUTABLE))), None), 60, "MQ")
socket = wait_for(lambda: next(Path(os.environ.get("TMPDIR", "/tmp")).glob(f"mq-report-capture-{main}.sock"), None)
                  or next(Path("/private/var/folders").glob(f"*/*/T/mq-report-capture-{main}.sock"), None), 60, "MQ capture service")
time.sleep(5)
report.update(main_pid=main, socket=str(socket))

os.kill(main, signal.SIGSTOP)
report["dialog_requested_at"] = time.time()
opener = subprocess.Popen(["open", "-n", "-W", *env, str(APP), "--args", "--report-dialog", str(main), "bug"])
try:
    osa = wait_for(dialog_pid, 60, "report dialog script")
    report["osascript_seen_at"] = time.time()
    helpers = [c for _, _, c in processes() if "--capture-report" in c]
    first = wait_for(lambda: dialog_state(osa), 30, "report dialog window")
    screenshot("dialog-timeout")
    report.update(dialog_osascript=osa, helper_commands_seen=helpers, while_mq_paused=first)
    assert "다시캡처" in first["text"].replace(" ", ""), f"no retry button while MQ was paused: {first}"
    assert "제때답하지" in first["text"].replace(" ", ""), f"timeout was not explained: {first}"

    folder = max((DATA / "bug-reports").iterdir(), key=lambda p: p.stat().st_mtime)
    status = folder / "capture-status.json"
    report["status_while_mq_paused"] = json.loads(status.read_text()) if status.exists() else None
    assert report["status_while_mq_paused"] == {"reason": "timeout"}, "the dialog did not time out its helper"
    os.kill(main, signal.SIGCONT)
    click(osa, "다시 캡처")
    after = wait_for(lambda: (s := dialog_state(osa)) and "캡처확인" in s["text"].replace(" ", "") and s, 30, "dialog after 다시 캡처")
    screenshot("dialog-after-retry")
    screen = folder / "screen.png"
    report.update(after_retry=after, screen=str(screen), screen_bytes=screen.stat().st_size if screen.exists() else 0,
                  status_after_retry=status.exists())
    assert screen.exists() and screen.stat().st_size > 10_000, "다시 캡처 did not write the MQ window"

    click(osa, "취소")
    opener.wait(timeout=30)
    report["dialog_closed"] = True
    assert not (folder / "response.json").exists(), "cancel wrote a response"
except AssertionError:
    screenshot("failure")
    probe = subprocess.run(["osascript", "-e", 'tell application "System Events" to get {name, unix id, count of windows} of every process whose background only is false'], capture_output=True, text=True)
    report["windows"] = probe.stdout.strip() or probe.stderr.strip()
    trusted = WORK / "trusted.swift"
    trusted.write_text("import ApplicationServices\nprint(AXIsProcessTrusted())\n")
    report["shell_accessibility_trusted"] = subprocess.run(["swift", str(trusted)], capture_output=True, text=True).stdout.strip()
    bugs = DATA / "bug-reports"
    report["mtimes"] = {str(p.relative_to(DATA)): p.stat().st_mtime for p in bugs.rglob("*")} if bugs.exists() else {}
    raise
finally:
    try:
        os.kill(main, signal.SIGCONT)
    except ProcessLookupError:
        pass
    (WORK / "dialog.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    subprocess.run(["kill", str(main)])
print("Report dialog spawned the capture helper, explained the timeout, and 다시 캡처 captured MQ")
