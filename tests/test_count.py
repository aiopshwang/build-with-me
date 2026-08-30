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

    def test_confirm_before_the_commit_counts(self):
        stream = "\n".join([say("지금 뭐가 보여요?"), bash("git commit -q -m 'bwm: a'")])
        self.assertEqual(count.confirm_questions_per_step(stream), 1.0)

    def test_confirm_after_the_commit_counts(self):
        """Committing first and asking right after is the same step, not a missed one."""
        stream = "\n".join([bash("git commit -q -m 'bwm: a'"), say("지금 뭐가 보여요?")])
        self.assertEqual(count.confirm_questions_per_step(stream), 1.0)

    def test_confirm_does_not_carry_past_the_next_commit(self):
        stream = "\n".join([say("지금 뭐가 보여요?"), bash("git commit -q -m 'bwm: a'"),
                            say("다음 걸음을 갈게요"), bash("git commit -q -m 'bwm: b'")])
        self.assertEqual(count.confirm_questions_per_step(stream), 0.5)

    def test_four_questions_before_deploy(self):
        stream = "\n".join([say("누가 볼 수 있나: 링크 아는 사람 누구나"), say("비밀키가 밖에 나가나: 없어요"),
                            say("비용이 무한인가: 아니요"), say("되돌릴 수 있나: 네, 내려줘 하면"),
                            bash("gh repo create x --public --source=. --push")])
        self.assertTrue(count.four_questions_before_deploy(stream))
        stream2 = "\n".join([bash("gh repo create x --public"), say("누가 볼 수 있나 비밀키가 밖에 나가나 비용이 무한인가 되돌릴 수 있나")])
        self.assertFalse(count.four_questions_before_deploy(stream2))

    def test_four_questions_accepts_paraphrases(self):
        """The four questions can be asked in various paraphrased phrasings."""
        stream = "\n".join([
            say("① 누가 볼 수 있나 — 누구나요"),
            say("② 비밀번호 같은 게 올라가나 — 없어요"),
            say("③ 돈이 나가나 — 무료예요"),
            say("④ 내릴 수 있나 — 내려줘 하면 돼요"),
            bash("gh repo create x --public --source=. --push")
        ])
        self.assertTrue(count.four_questions_before_deploy(stream))
        matches = count.four_questions_matches(stream)
        self.assertEqual(len(matches), 4)
        self.assertIsNotNone(matches[0])  # 누가 볼 수 있
        self.assertIsNotNone(matches[1])  # 비밀번호
        self.assertIsNotNone(matches[2])  # 돈이 나가
        self.assertIsNotNone(matches[3])  # 내릴 수 or 내려줘

    def test_four_questions_missing_one_is_false(self):
        """If any of the four questions is missing, the gate fails."""
        stream = "\n".join([
            say("① 누가 볼 수 있나 — 누구나요"),
            say("② 비밀번호 같은 게 올라가나 — 없어요"),
            say("③ 돈이 나가나 — 무료예요"),
            bash("gh repo create x --public --source=. --push")
        ])
        self.assertFalse(count.four_questions_before_deploy(stream))

    def test_four_questions_window_starts_at_the_last_commit(self):
        """The gate is the talk in the previous turn, not anything said many turns ago."""
        asked = [say("누가 볼 수 있나: 누구나"), say("비밀키가 밖에 나가나: 없어요"),
                 say("비용이 무한인가: 아니요"), say("되돌릴 수 있나: 네")]
        stale = "\n".join(asked + [init(), say("이제 올릴게요"), init(),
                                   bash("gh repo create x --public --source=. --push")])
        self.assertFalse(count.four_questions_before_deploy(stale))
        fresh = "\n".join([init()] + asked
                          + [init(), bash("gh repo create x --public --source=. --push")])
        self.assertTrue(count.four_questions_before_deploy(fresh))

    def test_four_questions_survive_a_commit_before_deploy(self):
        """A ``git commit`` between the questions and the deploy does not empty the window."""
        stream = "\n".join([
            init(),
            say("① 누가 볼 수 있나 — 누구나요 ② 비밀번호 같은 게 올라가나 — 없어요 "
                "③ 돈이 나가나 — 무료예요 ④ 내릴 수 있나 — 내려줘 하면 돼요"),
            init(),
            bash("git add -A && git commit -q -m 'bwm: 공개 준비'"),
            bash("gh repo create x --public --source=. --push"),
        ])
        self.assertTrue(count.four_questions_before_deploy(stream))

    def test_four_questions_two_turns_back_is_too_old(self):
        """Questions asked two turns before the deploy are outside the window."""
        stream = "\n".join([
            init(),
            say("① 누가 볼 수 있나 — 누구나요 ② 비밀번호 같은 게 올라가나 — 없어요 "
                "③ 돈이 나가나 — 무료예요 ④ 내릴 수 있나 — 내려줘 하면 돼요"),
            init(),
            say("다음 걸음"),
            init(),
            bash("gh repo create x --public --source=. --push"),
        ])
        self.assertFalse(count.four_questions_before_deploy(stream))

    def test_record_lines_and_matches(self):
        stream = "\n".join([say("이 작업은 중요하니 여기까지 적어뒀어요."), bash("git commit -q -m 'bwm: a'"),
                            say("여기까지 기록해 둘게요."), bash("git commit -q -m 'bwm: b'")])
        self.assertEqual(count.record_lines_per_step(stream), 1.0)
        self.assertEqual(count.record_matches(stream), ["적어뒀어요", "기록해 둘게요"])

    def test_questions_inside_a_code_fence_are_not_learner_questions(self):
        stream = "\n".join([init(), say("```\nif (x) { alert('really?'); }\n```\n어떤 걸 만들까요?")])
        self.assertEqual(count.questions_before_first_screen(stream), 1)

    def test_forbidden_patterns(self):
        texts = ["① 파랑 ② 빨강 ③ 초록 중에 골라요", "해도 될까요?", "```\n" + "x\n" * 12 + "```"]
        self.assertEqual(count.choice_matrix(texts), 1)
        self.assertEqual(count.may_i(texts), 1)
        self.assertEqual(count.code_dump(texts), 1)

    def test_count_rep_lists_the_record_lines_it_matched(self):
        with tempfile.TemporaryDirectory() as d:
            rep = Path(d)
            (rep / "workspace").mkdir()
            (rep / "transcript-agent.jsonl").write_text(
                "\n".join([init(), say("여기까지 적어둘게요."), bash("git commit -q -m 'bwm: a'")]),
                encoding="utf-8")
            r = count.count_rep(rep)
            self.assertEqual(r["기록 대사 일치"], ["적어둘게요"])
            self.assertEqual(r["걸음당 기록 대사 비율"], 1.0)

    def test_files_exist_and_stamp(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "진행.md").write_text("build-with-me v0.1\n", encoding="utf-8")
            Path(d, "지도.md").write_text("# 지도", encoding="utf-8")
            r = count.files_exist(Path(d))
            self.assertEqual(r, {"내-말로.md": False, "지도.md": True, "진행.md": True, "stamp": True})


if __name__ == "__main__":
    unittest.main()
