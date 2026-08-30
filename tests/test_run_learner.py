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

    def test_final_response_prefers_result(self):
        stream = "\n".join([
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "text", "text": "지금 뭐가 보여요?"}]}}),
            json.dumps({"type": "result", "result": "끝"}),
        ])
        self.assertEqual(run_learner.final_response(stream), "끝")

    def test_final_response_falls_back_to_text_blocks(self):
        stream = "\n".join([
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "text", "text": "브라우저에서 새로고침해보세요 … 지금 뭐가 보여요?"}]}}),
            json.dumps({"type": "result", "result": ""}),
        ])
        self.assertEqual(run_learner.final_response(stream), "브라우저에서 새로고침해보세요 … 지금 뭐가 보여요?")

    def test_final_response_codex_from_agent_message(self):
        # Real event captured from a spike run of `codex exec --json --skip-git-repo-check
        # -C <dir> "안녕, 한 줄만 답해줘"` (codex-cli 0.150.0, Windows).
        stream = "\n".join([
            json.dumps({"type": "thread.started", "thread_id": "01a051e5-8b24-78b3-90fb-807b6acf6b83"}),
            json.dumps({"type": "turn.started"}),
            json.dumps({"type": "item.completed", "item": {"id": "item_0", "type": "agent_message",
                                                            "text": "안녕하세요! 무엇을 도와드릴까요?"}}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 14668, "output_tokens": 15}}),
        ])
        self.assertEqual(run_learner.final_response_codex(stream), "안녕하세요! 무엇을 도와드릴까요?")

    def test_final_response_codex_uses_the_last_agent_message(self):
        stream = "\n".join([
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "먼저 확인할게요."}}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution",
                                                            "command": "dir"}}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "됐어요."}}),
        ])
        self.assertEqual(run_learner.final_response_codex(stream), "됐어요.")

    def test_final_response_codex_empty_when_no_agent_message(self):
        stream = json.dumps({"type": "turn.failed", "error": {"message": "x"}})
        self.assertEqual(run_learner.final_response_codex(stream), "")

    def test_session_id_codex_from_thread_started(self):
        stream = json.dumps({"type": "thread.started", "thread_id": "01a051e5-8b24"}) + "\n"
        self.assertEqual(run_learner.session_id_codex(stream), "01a051e5-8b24")

    def test_session_id_codex_none_when_absent(self):
        self.assertIsNone(run_learner.session_id_codex(json.dumps({"type": "turn.started"})))

    def test_skill_invoked_codex_true_when_skillmd_read(self):
        # Real command captured from a spike run with the skill copied to
        # workspace/.agents/skills/build-with-me/.
        ev = {"type": "item.completed", "item": {"id": "item_1", "type": "command_execution",
              "command": "\"powershell.exe\" -Command \"Get-Content -Raw "
                         "'C:\\\\tmp\\\\bwm-codex-spike2\\\\.agents\\\\skills\\\\build-with-me\\\\SKILL.md'\""}}
        self.assertTrue(run_learner.skill_invoked_codex(json.dumps(ev)))

    def test_skill_invoked_codex_false_when_no_match(self):
        ev = {"type": "item.completed", "item": {"type": "command_execution", "command": "dir"}}
        self.assertFalse(run_learner.skill_invoked_codex(json.dumps(ev)))

    def test_agent_argv_codex_first_turn(self):
        argv = run_learner.agent_argv(host="codex", arm="candidate", model="sonnet", resume=None,
                                       workspace=Path("/tmp/ws"), sandbox="danger-full-access", msg="안녕")
        self.assertEqual(argv, ["codex", "exec", "--json", "--skip-git-repo-check", "-C",
                                str(Path("/tmp/ws")), "-s", "danger-full-access", "안녕"])

    def test_agent_argv_codex_resume_turn(self):
        argv = run_learner.agent_argv(host="codex", arm="candidate", model="sonnet", resume="01a051e5",
                                       workspace=Path("/tmp/ws"), sandbox="danger-full-access", msg="다음")
        self.assertEqual(argv, ["codex", "exec", "resume", "--last", "--json", "--skip-git-repo-check",
                                "-s", "danger-full-access", "다음"])

    def test_agent_argv_codex_ignores_plugin_dir(self):
        argv = run_learner.agent_argv(host="codex", arm="candidate", model="sonnet", resume=None,
                                       workspace=Path("/tmp/ws"), sandbox="danger-full-access", msg="hi")
        self.assertNotIn("--plugin-dir", argv)

    def test_agent_argv_claude_unaffected_by_new_kwargs(self):
        argv = run_learner.agent_argv(host="claude", arm="baseline", model="sonnet", resume=None,
                                       workspace=Path("/tmp/ws"), sandbox="danger-full-access", msg="hi")
        self.assertEqual(argv[0], "claude")
        self.assertNotIn("--plugin-dir", argv)

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
