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

    def test_storage_moment_routes_to_reference(self):
        self.assertIn("저장'이라는 답이 나오는 순간", self.text)


class StorageTest(unittest.TestCase):
    text = property(lambda self: read("references/storage-questions-first.md"))

    def test_sections(self):
        for h in ("## 질문 먼저", "## 구조 도출", "## Worked Example 한 줄", "## 접근 규칙을 쉬운 말로",
                  "## SQL과 access-rules.json 같이 만들기", "## 손 넘기기: 저장소 계정 → SQL → 주소·공개키",
                  "## 설정 두 줄 같이 보기"):
            self.assertIn(h, self.text)

    def test_questions_before_tables(self):
        self.assertLess(self.text.index("## 질문 먼저"), self.text.index("## 구조 도출"))

    def test_plain_words_rule_and_config_lines(self):
        self.assertIn("누구나 적을 수 있고, 보는 건 당신뿐", self.text)
        self.assertIn("SUPABASE_URL", self.text)
        self.assertIn("SUPABASE_ANON_KEY", self.text)

    def test_sql_failure_path(self):
        self.assertIn("빨간 글자", self.text)
        self.assertIn("두 번 실패하면", self.text)


class PublishGateTest(unittest.TestCase):
    text = property(lambda self: read("references/publish-safety-gate.md"))

    def test_sections(self):
        for h in ("## 순서", "## 손 넘기기 세 번", "## 네 질문", "## 배포 한 줄", "## 배포 실패 경로",
                  "## 재배포 한 줄", "## 내리는 법", "## (선택) 한 번 더 보기"):
            self.assertIn(h, self.text)

    def test_gate_precedes_deploy(self):
        t = self.text
        self.assertLess(t.index("## 네 질문"), t.index("## 배포 한 줄"))
        self.assertIn("호스팅 계정 → 네 질문 → 배포 → 링크", t)

    def test_four_questions(self):
        for q in ("누가 볼 수 있나", "비밀키가 밖에 나가나", "비용이 무한인가", "되돌릴 수 있나"):
            self.assertIn(q, self.text)

    def test_measured_facts(self):
        self.assertIn("delete_repo", self.text)
        self.assertIn("3분", self.text)
        self.assertIn("Name already exists", self.text)
        self.assertIn("Bad credentials", self.text)


class CarryOnTest(unittest.TestCase):
    text = property(lambda self: read("references/carry-on.md"))

    def test_sections(self):
        for h in ("## 걸음 끝 두 줄, 보이게", "## 재개 (새 세션·맥락 정리 직후)", "## '안 돼요' 프로토콜",
                  "## 에러 번역 세 줄", "## 요구가 바뀌면", "## archive", "## 강사에게 보내기"):
            self.assertIn(h, self.text)

    def test_record_line_says_why(self):
        self.assertIn("여기까지 적어둘게요", self.text)
        self.assertIn("다음에 이어서 할 때 이걸 읽어요", self.text)

    def test_agent_looks_first(self):
        t = self.text
        self.assertLess(t.index("먼저 스스로 본다"), t.index("빨간 글자"))

    def test_three_line_error_format(self):
        for k in ("무슨 일", "왜", "뭘 할지"):
            self.assertIn(k, self.text)

    def test_carry_on_appends_my_words_line(self):
        self.assertIn("내-말로.md`에 이 걸음의 한 줄", self.text)


class SkillStructureTest(unittest.TestCase):
    text = property(lambda self: read("SKILL.md"))

    def test_router_and_invariants_come_first(self):
        t = self.text
        self.assertLess(t.index("## 언제 무엇을 읽나"), t.index("## 불변식 5"))
        self.assertLess(t.index("## 불변식 5"), t.index("## 규칙 7"))

    def test_router_points_to_all_four_references(self):
        for ref in ("references/start-and-decompose.md", "references/storage-questions-first.md",
                    "references/publish-safety-gate.md", "references/carry-on.md"):
            self.assertIn(ref, self.text)

    def test_description_has_beginner_phrases(self):
        head = self.text.split("\n---", 1)[0]
        for phrase in ("코딩", "처음", "만들고 싶", "어제 하던"):
            self.assertIn(phrase, head)

    def test_seven_rules_and_do_not_table(self):
        self.assertEqual(self.text.count("\n### 규칙 "), 7)
        self.assertIn("## 하지 않는 것", self.text)

    def test_rule4_records_at_intensity_two(self):
        self.assertIn("내-말로 파일에 바로 적는다", self.text)

    def test_do_not_run_own_server(self):
        self.assertIn("서버를 직접 띄우기", self.text)


class StartPaperTest(unittest.TestCase):
    text = property(lambda self: (SKILL.parents[1] / "시작하기.md").read_text(encoding="utf-8"))

    def test_order(self):
        t = self.text
        marks = ["폴더", "npx skills add aiopshwang/build-with-me", "이렇게 나오면 된 거예요", "코딩은 몰라요",
                 "재고표", "강사", "업데이트"]
        idx = [t.index(m) for m in marks]
        self.assertEqual(idx, sorted(idx))

    def test_five_examples(self):
        for s in ("우리 가게 지도", "재고표", "설문 페이지", "예약 신청", "견적 계산기"):
            self.assertIn(s, self.text)


if __name__ == "__main__":
    unittest.main()
