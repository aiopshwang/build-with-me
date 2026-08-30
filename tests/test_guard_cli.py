"""CLI layer tests for the pre-share command."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class GuardCLITest(unittest.TestCase):
    """Test guard.py CLI entry points with subprocess."""

    def run_guard(self, *args):
        """Run guard.py with the given arguments, return (returncode, stdout, stderr)."""
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/guard.py", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(REPO_ROOT),
            env=env
        )
        return result.returncode, result.stdout, result.stderr

    def test_clean_dir_exits_0(self):
        """pre-share with clean directory returns 0 and suitable message."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "index.html").write_text("<h1>재고표</h1>", encoding="utf-8")
            returncode, stdout, _ = self.run_guard("pre-share", str(tmp_path))
            self.assertEqual(returncode, 0)
            self.assertIn("공개해도 되는 파일들이에요", stdout)

    def test_findings_exit_1_and_json(self):
        """pre-share with findings returns 1 and with --json outputs JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "app.js").write_text("k='service_role'", encoding="utf-8")
            returncode, stdout, _ = self.run_guard("pre-share", str(tmp_path))
            self.assertEqual(returncode, 1)

            # Test with --json
            returncode, stdout, _ = self.run_guard("pre-share", str(tmp_path), "--json")
            self.assertEqual(returncode, 1)
            findings = json.loads(stdout)
            self.assertIsInstance(findings, list)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["kind"], "service_role")

    def test_missing_dir_exits_2(self):
        """pre-share with missing directory returns 2 with error message."""
        returncode, stdout, _ = self.run_guard("pre-share", "/nonexistent/path/xyz")
        self.assertEqual(returncode, 2)
        self.assertIn("확인할 폴더를 찾지 못했어요", stdout)


if __name__ == "__main__":
    unittest.main()
