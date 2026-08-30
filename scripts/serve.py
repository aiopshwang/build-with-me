#!/usr/bin/env python3
"""Local preview for build-with-me: start / open / stop. Standard library only."""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STATE = ".bwm/serve.json"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start(root: Path) -> str:
    port = free_port()
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0x8)
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1",
                             "--directory", str(root)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
    state = root / STATE
    state.parent.mkdir(exist_ok=True)
    state.write_text(json.dumps({"port": port, "pid": proc.pid}), encoding="utf-8")
    return f"http://127.0.0.1:{port}/"


def stop(root: Path) -> bool:
    state = root / STATE
    if not state.is_file():
        return False
    pid = json.loads(state.read_text(encoding="utf-8"))["pid"]
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    state.unlink()
    return True


def open_url(url: str, env=None, platform: str = sys.platform, run=subprocess.run) -> str:
    env = os.environ if env is None else env
    if env.get("BWM_NO_OPEN") or env.get("CODEX_SANDBOX") or env.get("CODEX_THREAD_ID"):
        return f"HANDOFF {url}"
    if platform == "win32":
        attempts = [["powershell", "-NoProfile", "-Command", f"Start-Process '{url}'"],
                    ["rundll32", "url.dll,FileProtocolHandler", url]]
    elif platform == "darwin":
        attempts = [["open", url]]
    else:
        attempts = [["xdg-open", url]]
    for argv in attempts:
        try:
            if run(argv, capture_output=True, timeout=15).returncode == 0:
                return "OPENED"
        except (OSError, subprocess.SubprocessError):
            continue
    return f"HANDOFF {url}"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2 or argv[0] not in {"start", "open", "stop"}:
        print("usage: serve.py start <dir> | open <url> | stop <dir>")
        return 2
    if argv[0] == "start":
        print("URL", start(Path(argv[1]).resolve()))
    elif argv[0] == "open":
        print(open_url(argv[1]))
    else:
        print("STOPPED" if stop(Path(argv[1]).resolve()) else "NOT_RUNNING")
    return 0


if __name__ == "__main__":
    sys.exit(main())
