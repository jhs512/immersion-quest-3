"""Drives the real Mac report dialog of MQ.app: dialog -> capture helper -> MQ, then 다시 캡처.

MQ and `--report-dialog` both start through LaunchServices as MQ.app, so the dialog spawns
the capture helper exactly as it does for a student. System Events does not list the dialog's
window, so `mac_dialog_ui.swift` reads it with Vision and clicks with a CGEvent.

timeout: MQ is paused with SIGSTOP, so the helper times out and the dialog must say so.
retry: the capture socket is temporarily unavailable, so the first capture fails. Once the
socket is restored, 다시 캡처 must bring the dialog back with 캡처 확인 and a screen.png.
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


def dialog_state(osascript):
    if osascript:
        owner = next((pp for p, pp, _ in processes() if p == osascript), None)
        if owner is None:
            return None
        activation = subprocess.run([str(UI), "activate", str(osascript), str(owner)], capture_output=True, text=True)
        report.setdefault("activations", []).append(activation.stdout.strip())
        time.sleep(0.25)
    seen = json.loads(subprocess.run([str(UI), "read", str(WORK / "dialog-read.png")], capture_output=True, text=True).stdout or "{}")
    if not seen.get("dialog"):
        report["last_ui_windows"] = seen.get("windows")
        return None
    lines = seen["lines"]
    return {"bounds": seen["dialog"], "buttons": [l["text"] for l in lines], "text": " ".join(l["text"] for l in lines), "lines": lines, "windows": seen["windows"]}


def click(osascript, name, before_click=None):
    state = wait_for(lambda: dialog_state(osascript), 10, f"dialog with {name}")
    if before_click:
        state = before_click(state)
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
        launch = subprocess.run(["open", "-n", "-W", *env, str(APP), "--args", "--capture-report", str(main), str(shot)], capture_output=True, text=True, timeout=15)
        screen_bytes = shot.stat().st_size if shot.exists() else 0
        report.setdefault("readiness", []).append({"main": main, "attempt": attempt[0], "launcher_returncode": launch.returncode, "launcher_stderr": launch.stderr, "screen_bytes": screen_bytes})
        return screen_bytes > 10_000 or time.sleep(2)

    wait_for(window_shown, 120, "MQ window on screen")


def start_mq(name, shown=True):
    before = {p for p, _, _ in processes()}
    subprocess.run(["open", "-n", *env, str(APP)], check=True)
    main = wait_for(lambda: next((p for p, _, c in processes() if p not in before and c.strip().endswith(str(EXECUTABLE))), None), 60, "MQ")
    mains.append(main)
    wait_for(lambda: Path(os.environ.get("TMPDIR", "/tmp"), f"mq-report-capture-{main}.sock").exists(), 60, "MQ capture service")
    if shown:
        wait_shown(main, name)
    return main


def open_dialog(main, name):
    known = {p.name for p in (DATA / "bug-reports").iterdir()}
    opener = subprocess.Popen(["open", "-n", "-W", *env, str(APP), "--args", "--report-dialog", str(main), "bug"])
    osa = wait_for(dialog_pid, 60, "report dialog script")
    folder = wait_for(lambda: next((p for p in (DATA / "bug-reports").iterdir() if p.name not in known and (p / "draft.json").exists()), None), 30, "report folder")
    state = wait_for(lambda: dialog_state(None), 40, "report dialog window without external activation")
    screenshot(f"{name}-dialog")
    status = folder / "capture-status.json"
    report[name] = {"dialog": state["text"], "status": json.loads(status.read_text()) if status.exists() else None,
                    "windows": json.loads(subprocess.run([str(UI), "read", str(WORK / "windows.png")], capture_output=True, text=True).stdout or "{}").get("windows")}
    return opener, osa, folder, state


def close(opener, osa, folder):
    owner = next(pp for p, pp, _ in processes() if p == osa)
    click(osa, "취소")
    wait_for(lambda: not any(p in (osa, owner) for p, _, _ in processes()), 30, "cancel closes the report script and helper")
    report.setdefault("cancellations", []).append({"script": osa, "helper": owner, "exited": True, "launcher_returncode": opener.poll()})
    if opener.poll() is None:
        opener.terminate()
    opener.wait(timeout=5)
    assert not (folder / "response.json").exists(), "cancel wrote a response"


mains = []
try:
    main = start_mq("timeout")
    os.kill(main, signal.SIGSTOP)
    opener, osa, folder, state = open_dialog(main, "timeout")
    assert report["timeout"]["status"] == {"reason": "timeout"}, "the dialog did not time out its helper"
    assert "제때답하지" in state["text"].replace(" ", ""), f"timeout was not explained: {state['text']}"
    assert "다시캡처" in state["text"].replace(" ", ""), "no 다시 캡처 after a timeout"
    os.kill(main, signal.SIGCONT)
    close(opener, osa, folder)
    subprocess.run(["kill", str(main)])
    time.sleep(2)

    main = start_mq("retry")
    socket = Path(os.environ.get("TMPDIR", "/tmp"), f"mq-report-capture-{main}.sock")
    offline = socket.with_suffix(".offline")
    socket.rename(offline)
    try:
        opener, osa, folder, state = open_dialog(main, "retry")
    finally:
        offline.rename(socket)
    assert report["retry"]["status"] and report["retry"]["status"]["reason"] == "failed", "the first capture did not fail with its socket unavailable"
    assert "capture service unavailable" in report["retry"]["status"].get("detail", ""), "the failure did not come from the capture service connection"
    assert "다시캡처" in state["text"].replace(" ", ""), "no 다시 캡처 after a failed capture"
    marker = f"MQREPORTFRESH{main}"
    subprocess.run([str(UI), "type", str(main), f"echo {marker}"], check=True)
    screenshot("marker-input")
    marker_input = json.loads(subprocess.run([str(UI), "ocr", str(WORK / "marker-input.png")], capture_output=True, text=True, check=True).stdout)
    marker_input_text = " ".join(line["text"] for line in marker_input["lines"])
    report["retry"]["marker_input_text"] = marker_input_text
    assert marker in marker_input_text, f"marker input did not reach the actual main terminal: {marker_input_text}"

    def record_capture_target(state):
        targets = [w for w in state["windows"] if w["pid"] == main and w["title"] == "MQ"]
        assert targets, "the main process has no MQ window before retry"
        target = max(targets, key=lambda w: w["bounds"][2] * w["bounds"][3])
        if target["onscreen"]:
            subprocess.run([str(UI), "hide", str(main)], check=True)
            state = wait_for(lambda: dialog_state(osa), 10, "report remains visible after hiding MQ")
            target = next(w for w in state["windows"] if w["id"] == target["id"] and w["pid"] == main)
            report["retry"]["offscreen_trigger"] = "controlled NSRunningApplication.hide after marker input"
        else:
            report["retry"]["offscreen_trigger"] = "main fullscreen window in another Space"
        report["retry"]["target_before_retry"] = target
        assert not target["onscreen"], f"the actual MQ capture target is on-screen before retry: {target}"
        return state

    click(osa, "다시 캡처", before_click=record_capture_target)
    after = wait_for(lambda: (s := dialog_state(osa)) and "캡처확인" in s["text"].replace(" ", "") and s, 30, "dialog after 다시 캡처")
    screenshot("retry-after")
    screen = folder / "screen.png"
    report["retry"].update(after=after["text"], screen_bytes=screen.stat().st_size if screen.exists() else 0)
    assert screen.exists() and screen.stat().st_size > 10_000, "다시 캡처 did not write the MQ window"
    captured = json.loads(subprocess.run([str(UI), "ocr", str(screen)], capture_output=True, text=True, check=True).stdout)
    captured_text = " ".join(line["text"] for line in captured["lines"])
    report["retry"].update(captured_text=captured_text, marker=marker)
    assert marker in captured_text, f"retry did not capture the newly written terminal marker: {captured_text}"
    state_after_capture = json.loads(subprocess.run([str(UI), "read", str(WORK / "retry-captured-dialog.png")], capture_output=True, text=True, check=True).stdout)
    report["retry"]["capture_windows"] = state_after_capture["windows"]
    target_id = report["retry"]["target_before_retry"]["id"]
    assert any(w["id"] == target_id and w["pid"] == main and w["title"] == "MQ" and not w["onscreen"] for w in state_after_capture["windows"]), "the same MQ capture target is not off-Space after retry"
    close(opener, osa, folder)
except (AssertionError, subprocess.SubprocessError):
    screenshot("failure")
    raise
finally:
    report["final_processes"] = [{"pid": p, "parent": pp, "command": c} for p, pp, c in processes() if "MQ.app" in c or "osascript" in c]
    final_ui = subprocess.run([str(UI), "read", str(WORK / "final-dialog.png")], capture_output=True, text=True)
    report["final_windows"] = json.loads(final_ui.stdout or "{}") if final_ui.returncode == 0 else {"error": final_ui.stderr}
    for main in mains:
        try:
            os.kill(main, signal.SIGCONT)
        except ProcessLookupError:
            pass
        subprocess.run(["kill", str(main)], capture_output=True)
    (WORK / "dialog.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "windows"} if isinstance(v, dict) else v for k, v in report.items()}, indent=2, ensure_ascii=False))
print("Report dialog explained a capture timeout, showed the failure detail, and 다시 캡처 captured MQ")
