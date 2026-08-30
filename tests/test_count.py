"""count.py turns run artefacts into the numbers the success table asks for."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "evals"))
import count  # noqa: E402


def bash(cmd):
    return json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}})


def say(text):
    return json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}})


def init():
    return json.dumps({"type": "system", "subtype": "init", "session_id": "s"})


class CountTest(unittest.TestCase):
    def test_first_screen_from_agent_stream(self):
        stream = "\n".join([
            init(),
            say("잘 오셨어요. 뭘 만들고 싶어요?"),
            bash("python skills/build-with-me/scripts/serve.py start ."),
            say("이건 자리만 잡은 거예요. 맞아요?"),
            init(),
            say("지금 뭐가 보여요?"),
        ])
        self.assertEqual(count.first_screen_turn(stream), 1)
        self.assertEqual(count.questions_before_first_screen(stream), 1)

        stream2 = "\n".join([init(), say("주소예요: http://127.0.0.1:5000/")])
        self.assertEqual(count.first_screen_turn(stream2), 1)

    def test_first_screen_none(self):
        stream = "\n".join([init(), say("a?"), init(), say("b? c?")])
        self.assertIsNone(count.first_screen_turn(stream))
        self.assertEqual(count.questions_before_first_screen(stream), 3)

    def test_identifier_mentions(self):
        hits = count.identifier_mentions(["index.html을 고쳤어요", "getItems 함수", "config.js 두 줄", "화면이 떴어요"],
                                         ["index.html", "config.js"])
        self.assertEqual(sorted(hits), ["getItems", "index.html"])

    def test_identifier_mentions_ascii_boundary(self):
        # \b breaks next to Hangul (Hangul is \w in Python's Unicode regex), so the
        # identifier patterns must use ASCII-only lookaround boundaries instead.
        hits = count.identifier_mentions(
            ["config.js가 있어요", "index.html을 열어보세요", "getItems를 호출했어요", "user_id를 확인했어요"], [])
        self.assertEqual(sorted(hits), ["getItems", "index.html", "user_id"])

    def test_identifier_mentions_korean_only(self):
        self.assertEqual(count.identifier_mentions(["화면이 떴어요. 재고표가 보여요"], []), [])

    def test_step_boundaries_and_confirm_ratio(self):
        stream = "\n".join([say("지금 뭐가 보여요?"), bash("git commit -q -m 'bwm: a'"),
                            say("다음 걸음"), bash("git commit -q -m 'bwm: b'")])
        self.assertEqual(count.step_boundaries(stream), 2)
        self.assertEqual(count.confirm_questions_per_step(stream), 0.5)

    def test_four_questions_before_deploy(self):
        stream = "\n".join([say("누가 볼 수 있나: 링크 아는 사람 누구나"), say("비밀키가 밖에 나가나: 없어요"),
                            say("비용이 무한인가: 아니요"), say("되돌릴 수 있나: 네, 내려줘 하면"),
                            bash("gh repo create x --public --source=. --push")])
        self.assertTrue(count.four_questions_before_deploy(stream))
        stream2 = "\n".join([bash("gh repo create x --public"), say("누가 볼 수 있나 비밀키가 밖에 나가나 비용이 무한인가 되돌릴 수 있나")])
        self.assertFalse(count.four_questions_before_deploy(stream2))

    def test_forbidden_patterns(self):
        texts = ["① 파랑 ② 빨강 ③ 초록 중에 골라요", "해도 될까요?", "```\n" + "x\n" * 12 + "```"]
        self.assertEqual(count.choice_matrix(texts), 1)
        self.assertEqual(count.may_i(texts), 1)
        self.assertEqual(count.code_dump(texts), 1)

    def test_files_exist_and_stamp(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "진행.md").write_text("build-with-me v0.1\n", encoding="utf-8")
            Path(d, "지도.md").write_text("# 지도", encoding="utf-8")
            r = count.files_exist(Path(d))
            self.assertEqual(r, {"내-말로.md": False, "지도.md": True, "진행.md": True, "stamp": True})


if __name__ == "__main__":
    unittest.main()
