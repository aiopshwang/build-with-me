"""human-edits lists files a person touched since the agent's last commit."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills/build-with-me/scripts"))
import guard  # noqa: E402


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout


class HumanEditsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@t"); git(self.repo, "config", "user.name", "t")
        (self.repo / "index.html").write_text("a", encoding="utf-8")
        git(self.repo, "add", "."); git(self.repo, "commit", "-q", "-m", "bwm: first screen")

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_is_empty(self):
        self.assertEqual(guard.human_edits(self.repo), [])

    def test_uncommitted_change_is_listed(self):
        (self.repo / "index.html").write_text("b", encoding="utf-8")
        self.assertEqual(guard.human_edits(self.repo), ["index.html"])

    def test_human_commit_after_agent_commit_is_listed(self):
        (self.repo / "style.css").write_text("x", encoding="utf-8")
        git(self.repo, "add", "."); git(self.repo, "commit", "-q", "-m", "changed colour")
        self.assertEqual(guard.human_edits(self.repo), ["style.css"])

    def test_agent_commit_resets(self):
        (self.repo / "style.css").write_text("x", encoding="utf-8")
        git(self.repo, "add", "."); git(self.repo, "commit", "-q", "-m", "bwm: colour step")
        self.assertEqual(guard.human_edits(self.repo), [])

    def test_renamed_to_quoted_name_is_clean(self):
        git(self.repo, "mv", "index.html", "index (renamed).html")
        self.assertEqual(guard.human_edits(self.repo), ["index (renamed).html"])

    def test_non_repo_is_reported_not_empty(self):
        """"cannot look" and "nothing was edited" are different answers; [] means the second."""
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(guard.human_edits(Path(d)))


if __name__ == "__main__":
    unittest.main()
