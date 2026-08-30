"""SKILL.md body must stay under the compaction re-injection window."""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import validate  # noqa: E402


class SkillBudgetTest(unittest.TestCase):
    def test_body_words_counts_after_frontmatter(self):
        text = "---\nname: x\ndescription: y\n---\n\n# T\n\none two three\n"
        self.assertEqual(validate.body_words(text), 5)

    def test_repo_skill_is_under_budget(self):
        path = REPO_ROOT / "skills/build-with-me/SKILL.md"
        self.assertLessEqual(validate.body_words(path.read_text(encoding="utf-8")), validate.BODY_WORD_LIMIT)


if __name__ == "__main__":
    unittest.main()
