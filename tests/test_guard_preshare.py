"""pre-share must catch secrets in files that are about to become public."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills/build-with-me/scripts"))
import guard  # noqa: E402

JWT = "eyJ" + "a" * 60 + ".payload.sig"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout


class PreShareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_clean_site_has_no_findings(self):
        self.write("index.html", "<h1>재고표</h1>")
        self.write("config.js", f"const SUPABASE_URL='https://x.supabase.co';\nconst SUPABASE_ANON_KEY='{JWT}';\n")
        self.assertEqual(guard.scan_dir(self.root), [])

    def test_service_role_anywhere_is_a_finding(self):
        self.write("index.html", "<script>const k='service_role'</script>")
        kinds = [f.kind for f in guard.scan_dir(self.root)]
        self.assertEqual(kinds, ["service_role"])

    def test_jwt_outside_config_is_a_finding(self):
        self.write("index.html", f"<script>const k='{JWT}'</script>")
        self.assertEqual([f.kind for f in guard.scan_dir(self.root)], ["jwt"])

    def test_second_jwt_in_config_is_a_finding(self):
        self.write("config.js", f"a='{JWT}';\nb='{JWT}';\n")
        self.assertEqual(len(guard.scan_dir(self.root)), 1)

    def test_openai_and_aws_and_password(self):
        self.write("app.js", "k='sk-" + "b" * 24 + "'\nid='AKIA" + "C" * 16 + "'\npassword = 'x'\n")
        self.assertEqual(sorted(f.kind for f in guard.scan_dir(self.root)), ["aws", "openai", "password"])

    def test_archive_is_scanned_when_it_would_ship(self):
        """archive/ is not special: outside a repo it ships with the folder, so it is scanned."""
        self.write(".git/config", "service_role")
        self.write("archive/2026/old.js", "service_role")
        findings = guard.scan_dir(self.root)
        self.assertEqual([f.kind for f in findings], ["service_role"])
        self.assertIn("old.js", findings[0].path)

    def test_dotenv_is_scanned(self):
        """.env has no scannable suffix, so it must be matched by name."""
        self.write(".env", "password=x\n")
        self.assertEqual([f.kind for f in guard.scan_dir(self.root)], ["password"])

    def test_git_repo_scans_only_shipped_files(self):
        """Inside a repo the answer is git's: ignored files never become public."""
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "t@t"); git(self.root, "config", "user.name", "t")
        self.write(".gitignore", "archive/\n")
        self.write("archive/old.js", "service_role")
        self.write("index.html", "<h1>hi</h1>")
        self.assertEqual(guard.scan_dir(self.root), [])
        self.write(".gitignore", "\n")
        self.assertEqual([f.kind for f in guard.scan_dir(self.root)], ["service_role"])

    def test_unreadable_file_is_reported_not_silent(self):
        self.write("app.js", "ok")
        seen = []
        real = Path.read_text

        def boom(self, *a, **kw):
            if self.name == "app.js":
                raise OSError("locked")
            return real(self, *a, **kw)
        Path.read_text = boom
        try:
            self.assertEqual(guard.scan_dir(self.root, unreadable=seen), [])
        finally:
            Path.read_text = real
        self.assertEqual([Path(s).name for s in seen], ["app.js"])

    def test_sample_is_masked(self):
        self.write("app.js", "k='sk-" + "b" * 24 + "'")
        self.assertNotIn("b" * 24, guard.scan_dir(self.root)[0].sample)


if __name__ == "__main__":
    unittest.main()
