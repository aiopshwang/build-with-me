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


class StartAndDecomposeTest(unittest.TestCase):
    text = property(lambda self: read("references/start-and-decompose.md"))

    def test_sections(self):
        for h in ("## 진입 6단계", "## 예시 폴백", "## 이어서 / 새로", "## 북극성", "## 범위 판별과 축소안",
                  "## 거꾸로 파기 (O/P/I)", "## 유도 규칙 6", "## 강도 다이얼"):
            self.assertIn(h, self.text)

    def test_first_screen_before_questions(self):
        t = self.text
        self.assertLess(t.index("임시 한 줄 페이지"), t.index("세 줄 되풀이"))
        self.assertIn("첫 화면 전 학습자에게 하는 질문은 최대 1개", t)

    def test_no_intensity_question_and_quiet_git(self):
        self.assertIn("강도는 묻지 않고 ②로 시작", self.text)
        self.assertIn("git init -q", self.text)

    def test_folder_step_and_handoff_format(self):
        self.assertIn("VS Code면 이 폴더를 열고", self.text)
        self.assertIn("끝나면 '됐어요'라고 해주세요", self.text)

    def test_scenarios_named_in_fallback(self):
        for s in ("재고표", "설문", "예약"):
            self.assertIn(s, self.text)


if __name__ == "__main__":
    unittest.main()
