"""serve.py starts a local server the learner can see and knows when to hand the URL over."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills/build-with-me/scripts"))
import serve  # noqa: E402


def pid_alive(pid: int) -> bool:
    if sys.platform == "win32":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


class OpenUrlTest(unittest.TestCase):
    def test_codex_env_hands_off(self):
        self.assertEqual(serve.open_url("http://x/", env={"CODEX_SANDBOX": "1"}), "HANDOFF http://x/")

    def test_no_open_env_hands_off(self):
        self.assertEqual(serve.open_url("http://x/", env={"BWM_NO_OPEN": "1"}), "HANDOFF http://x/")

    def test_windows_uses_powershell_then_rundll32(self):
        calls = []

        def run(argv, **kw):
            calls.append(argv[0])
            class R: returncode = 1 if argv[0] == "powershell" else 0
            return R()
        self.assertEqual(serve.open_url("http://x/", env={}, platform="win32", run=run), "OPENED")
        self.assertEqual(calls, ["powershell", "rundll32"])

    def test_all_fail_hands_off(self):
        def run(argv, **kw):
            class R: returncode = 1
            return R()
        self.assertEqual(serve.open_url("http://x/", env={}, platform="win32", run=run), "HANDOFF http://x/")


class StartStopTest(unittest.TestCase):
    def test_start_serves_and_stop_kills(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "index.html").write_text("<h1>재고표</h1>", encoding="utf-8")
            out = subprocess.run([sys.executable, str(REPO_ROOT / "skills/build-with-me/scripts/serve.py"), "start", d],
                                 capture_output=True, text=True, encoding="utf-8", check=True).stdout
            url = out.split()[1]
            for _ in range(20):
                try:
                    body = urllib.request.urlopen(url, timeout=1).read().decode("utf-8"); break
                except Exception:
                    time.sleep(0.25)
            self.assertIn("재고표", body)
            state = json.loads(Path(d, ".bwm/serve.json").read_text(encoding="utf-8"))
            self.assertEqual(url, f"http://127.0.0.1:{state['port']}/")
            out = subprocess.run([sys.executable, str(REPO_ROOT / "skills/build-with-me/scripts/serve.py"), "stop", d],
                                 capture_output=True, text=True, encoding="utf-8").stdout
            self.assertIn("STOPPED", out)
            time.sleep(0.5)
            with self.assertRaises(Exception):
                urllib.request.urlopen(url, timeout=1)

    def test_start_twice_leaves_one_server(self):
        """A second start must not orphan the first server: start stops the old one."""
        with tempfile.TemporaryDirectory() as d:
            Path(d, "index.html").write_text("<h1>재고표</h1>", encoding="utf-8")
            root = Path(d)
            try:
                serve.start(root)
                pid1 = json.loads(Path(d, ".bwm/serve.json").read_text(encoding="utf-8"))["pid"]
                serve.start(root)
                pid2 = json.loads(Path(d, ".bwm/serve.json").read_text(encoding="utf-8"))["pid"]
                self.assertNotEqual(pid1, pid2)
                for _ in range(20):
                    if not pid_alive(pid1):
                        break
                    time.sleep(0.25)
                self.assertFalse(pid_alive(pid1), f"first server {pid1} is still running")
                self.assertTrue(pid_alive(pid2))
            finally:
                serve.stop(root)

    def test_stop_handles_garbage_state(self):
        """A truncated or hand-edited state file must not raise a traceback at the learner."""
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, ".bwm"); state.mkdir()
            (state / "serve.json").write_text("not json", encoding="utf-8")
            out = subprocess.run([sys.executable, str(REPO_ROOT / "skills/build-with-me/scripts/serve.py"),
                                  "stop", d], capture_output=True, text=True, encoding="utf-8")
            self.assertNotIn("Traceback", out.stderr)
            self.assertTrue("NOT_RUNNING" in out.stdout or "STOPPED" in out.stdout, out.stdout)
            self.assertFalse((state / "serve.json").exists())

    def test_stop_accepts_bom_state_file_from_powershell(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, ".bwm"); state.mkdir()
            # a PID that does not exist: stop must still parse the file and remove it
            (state / "serve.json").write_text(json.dumps({"port": 1, "pid": 999999}), encoding="utf-8-sig")
            out = subprocess.run([sys.executable, str(REPO_ROOT / "skills/build-with-me/scripts/serve.py"), "stop", d],
                                 capture_output=True, text=True, encoding="utf-8").stdout
            self.assertIn("STOPPED", out)
            self.assertFalse((state / "serve.json").exists())


if __name__ == "__main__":
    unittest.main()
