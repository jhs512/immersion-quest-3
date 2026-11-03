"""Drives the real Mac report dialog of MQ.app: dialog -> capture helper -> MQ, then 다시 캡처.

MQ and `--report-dialog` both start through LaunchServices as MQ.app, so the dialog spawns
the capture helper exactly as it does for a student. System Events does not list the dialog's
window, so `mac_dialog_ui.swift` reads it with Vision and clicks with a CGEvent.

timeout: MQ is paused with SIGSTOP, so the helper times out and the dialog must say so.
retry: the dialog opens before MQ's window is on screen, so the first capture fails. Once the
window is up, 다시 캡처 must bring the dialog back with 캡처 확인 and a screen.png.
Each dialog is cancelled, so nothing is sent to GitHub.
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


def click(osascript, name):
    owner = next(pp for p, pp, _ in processes() if p == osascript)
    subprocess.run([str(UI), "activate", str(owner)], check=True)
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


def wait_shown(main, name):
    attempt = [0]

    def window_shown():
        attempt[0] += 1
        shot = DATA / "bug-reports" / f"{name}-ready-{attempt[0]}" / "screen.png"
        shot.parent.mkdir(parents=True)
        subprocess.run(["open", "-n", "-W", *env, str(APP), "--args", "--capture-report", str(main), str(shot)], check=True)
        return shot.exists() or time.sleep(2)

    wait_for(window_shown, 120, "MQ window on screen")


def start_mq(name, shown=True):
    before = {p for p, _, _ in processes()}
    subprocess.run(["open", "-n", *env, str(APP)], check=True)
    main = wait_for(lambda: next((p for p, _, c in processes() if p not in before and c.strip().endswith(str(EXECUTABLE))), None), 60, "MQ")
    wait_for(lambda: Path(os.environ.get("TMPDIR", "/tmp"), f"mq-report-capture-{main}.sock").exists(), 60, "MQ capture service")
    if shown:
        wait_shown(main, name)
    return main


def open_dialog(main, name):
    known = {p.name for p in (DATA / "bug-reports").iterdir()}
    opener = subprocess.Popen(["open", "-n", "-W", *env, str(APP), "--args", "--report-dialog", str(main), "bug"])
    osa = wait_for(dialog_pid, 60, "report dialog script")
    folder = wait_for(lambda: next((p for p in (DATA / "bug-reports").iterdir() if p.name not in known and (p / "draft.json").exists()), None), 30, "report folder")
    state = wait_for(lambda: dialog_state(osa), 40, "report dialog window")
    screenshot(f"{name}-dialog")
    status = folder / "capture-status.json"
    report[name] = {"dialog": state["text"], "status": json.loads(status.read_text()) if status.exists() else None,
                    "windows": json.loads(subprocess.run([str(UI), "read", str(WORK / "windows.png")], capture_output=True, text=True).stdout or "{}").get("windows")}
    return opener, osa, folder, state


def close(opener, osa, folder):
    click(osa, "취소")
    opener.wait(timeout=30)
    assert not (folder / "response.json").exists(), "cancel wrote a response"


mains = []
try:
    main = start_mq("timeout")
    mains.append(main)
    os.kill(main, signal.SIGSTOP)
    opener, osa, folder, state = open_dialog(main, "timeout")
    assert report["timeout"]["status"] == {"reason": "timeout"}, "the dialog did not time out its helper"
    assert "제때답하지" in state["text"].replace(" ", ""), f"timeout was not explained: {state['text']}"
    assert "다시캡처" in state["text"].replace(" ", ""), "no 다시 캡처 after a timeout"
    os.kill(main, signal.SIGCONT)
    close(opener, osa, folder)
    subprocess.run(["kill", str(main)])
    time.sleep(2)

    # MQ's capture service starts before its window is on screen: a report opened then fails.
    main = start_mq("retry", shown=False)
    mains.append(main)
    opener, osa, folder, state = open_dialog(main, "retry")
    assert report["retry"]["status"] and report["retry"]["status"]["reason"] == "failed", "the first capture did not fail before MQ's window was up"
    assert "다시캡처" in state["text"].replace(" ", ""), "no 다시 캡처 after a failed capture"
    wait_shown(main, "retry")
    click(osa, "다시 캡처")
    subprocess.run([str(UI), "activate", str(next(pp for p, pp, _ in processes() if p == osa))], check=True)
    after = wait_for(lambda: (s := dialog_state(osa)) and "캡처확인" in s["text"].replace(" ", "") and s, 30, "dialog after 다시 캡처")
    screenshot("retry-after")
    screen = folder / "screen.png"
    report["retry"].update(after=after["text"], screen_bytes=screen.stat().st_size if screen.exists() else 0)
    assert screen.exists() and screen.stat().st_size > 10_000, "다시 캡처 did not write the MQ window"
    close(opener, osa, folder)
except AssertionError:
    screenshot("failure")
    raise
finally:
    for main in mains:
        try:
            os.kill(main, signal.SIGCONT)
        except ProcessLookupError:
            pass
        subprocess.run(["kill", str(main)], capture_output=True)
    (WORK / "dialog.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "windows"} if isinstance(v, dict) else v for k, v in report.items()}, indent=2, ensure_ascii=False))
print("Report dialog explained a capture timeout, showed the failure detail, and 다시 캡처 captured MQ")
