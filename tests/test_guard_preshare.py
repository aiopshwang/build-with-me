"""pre-share must catch secrets in files that are about to become public."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import guard  # noqa: E402

JWT = "eyJ" + "a" * 60 + ".payload.sig"


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

    def test_skips_git_and_archive(self):
        self.write(".git/config", "service_role")
        self.write("archive/2026/old.js", "service_role")
        self.assertEqual(guard.scan_dir(self.root), [])

    def test_sample_is_masked(self):
        self.write("app.js", "k='sk-" + "b" * 24 + "'")
        self.assertNotIn("b" * 24, guard.scan_dir(self.root)[0].sample)


if __name__ == "__main__":
    unittest.main()
