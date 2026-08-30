"""Reference and asset files carry the fixed lines the skill promises."""
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills/build-with-me"


def read(rel):
    return (SKILL / rel).read_text(encoding="utf-8")


class AssetsTest(unittest.TestCase):
    def test_progress_stamp_is_first_line(self):
        self.assertEqual(read("assets/진행.md").splitlines()[0], "build-with-me v0.1")

    def test_map_has_three_boxes(self):
        text = read("assets/지도.md")
        for box in ("## 북극성", "## 걸음", "## 그건 2탄", "## 막힌 곳"):
            self.assertIn(box, text)

    def test_project_note_is_one_line_and_names_progress_file(self):
        lines = [l for l in read("assets/project-note.md").splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("진행.md", lines[0])
        self.assertIn("build-with-me", lines[0])


if __name__ == "__main__":
    unittest.main()
