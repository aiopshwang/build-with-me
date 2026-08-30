"""Pure parts of the multi-turn runner."""
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "evals"))
import run_learner  # noqa: E402


class ParseTest(unittest.TestCase):
    def test_session_id_from_init_event(self):
        stream = json.dumps({"type": "system", "subtype": "init", "session_id": "abc"}) + "\n"
        self.assertEqual(run_learner.session_id(stream), "abc")

    def test_session_id_falls_back_to_result(self):
        stream = json.dumps({"type": "result", "result": "hi", "session_id": "xyz"}) + "\n"
        self.assertEqual(run_learner.session_id(stream), "xyz")

    def test_done_when_learner_ends(self):
        self.assertTrue(run_learner.is_done("[끝]"))
        self.assertTrue(run_learner.is_done("네 됐어요 [끝]"))
        self.assertFalse(run_learner.is_done("됐어요"))

    def test_learner_prompt_contains_facts_and_history(self):
        p = run_learner.learner_prompt("품목 12개", [("코딩 몰라요", "화면을 열었어요")])
        self.assertIn("품목 12개", p)
        self.assertIn("화면을 열었어요", p)
        self.assertIn("[끝]", p)

    def test_skill_invoked_matches_this_skill(self):
        ev = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill",
                                                            "input": {"skill": "build-with-me"}}]}}
        self.assertTrue(run_learner.skill_invoked(json.dumps(ev)))

    def test_stop_preview_removes_state_file(self):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as d:
            state = Path(d, ".bwm"); state.mkdir()
            (state / "serve.json").write_text(json.dumps({"port": 1, "pid": 999999}), encoding="utf-8")
            run_learner.stop_preview(Path(d))
            self.assertFalse((state / "serve.json").exists())

    def test_storage_facts_empty_for_none(self):
        self.assertEqual(run_learner.storage_facts({"storage": "none"}, {}), "")

    def test_storage_facts_includes_url_and_key(self):
        env = {"BWM_EVAL_SUPABASE_URL": "https://x.supabase.co", "BWM_EVAL_SUPABASE_KEY": "k"}
        facts = run_learner.storage_facts({"storage": "supabase"}, env)
        self.assertIn("주소: https://x.supabase.co", facts)
        self.assertIn("공개 키: k", facts)
        self.assertIn("됐어요", facts)

    def test_storage_facts_missing_env_exits_2(self):
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit) as ctx:
                run_learner.storage_facts({"storage": "supabase"}, {})
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("BWM_EVAL_SUPABASE_URL", buf.getvalue())
        self.assertIn("BWM_EVAL_SUPABASE_KEY", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
