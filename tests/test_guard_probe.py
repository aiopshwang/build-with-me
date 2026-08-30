"""probe checks the RLS story the agent told the learner against the real API."""
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills/build-with-me/scripts"))
import guard  # noqa: E402

RULES = {"version": 1, "tables": {"responses": {
    "anon": {"insert": True, "select": False, "delete": False},
    "probe_row": {"answer": "확인용"}}}}


class FakeSupabase:
    """Minimal PostgREST: policy dict says what anon may do; select under RLS returns []."""

    def __init__(self, insert=True, select=False, delete=False):
        self.policy = {"insert": insert, "select": select, "delete": delete}
        self.rows = {}
        self.calls = []

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url))
        assert headers["apikey"] == "anon" and headers["Authorization"] == "Bearer anon"
        if method == "POST":
            if not self.policy["insert"]:
                return 401, '{"message":"new row violates row-level security policy"}'
            rid = len(self.rows) + 1
            self.rows[rid] = json.loads(body)
            return 201, json.dumps([{"id": rid, **self.rows[rid]}])
        if method == "GET":
            return 200, json.dumps([{"id": k, **v} for k, v in self.rows.items()] if self.policy["select"] else [])
        if method == "DELETE":
            if not self.policy["delete"]:
                return 401, '{"message":"permission denied"}'
            rid = int(url.rsplit("id=eq.", 1)[1])
            self.rows.pop(rid, None)
            return 204, ""
        raise AssertionError(method)


class ProbeTest(unittest.TestCase):
    def test_rules_match_reality(self):
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=FakeSupabase())
        self.assertEqual([(r.action, r.ok) for r in results], [("insert", True), ("select", True), ("delete", True)])

    def test_select_leak_is_reported(self):
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=FakeSupabase(select=True))
        bad = [r for r in results if not r.ok]
        self.assertEqual([(r.action, r.observed) for r in bad], [("select", "allow")])

    def test_nothing_works_is_unknown_not_deny(self):
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=FakeSupabase(insert=False))
        self.assertTrue(all(r.observed == "unknown" for r in results))
        self.assertTrue(all(not r.ok for r in results))

    def test_probe_row_is_cleaned_up_when_delete_allowed(self):
        fake = FakeSupabase(delete=True)
        rules = json.loads(json.dumps(RULES)); rules["tables"]["responses"]["anon"]["delete"] = True
        guard.probe("https://x.supabase.co", "anon", rules, http=fake)
        self.assertEqual(fake.rows, {})

    def test_urls_and_headers(self):
        fake = FakeSupabase()
        guard.probe("https://x.supabase.co/", "anon", RULES, http=fake)
        self.assertEqual(fake.calls[0], ("POST", "https://x.supabase.co/rest/v1/responses"))
        self.assertTrue(fake.calls[1][1].startswith("https://x.supabase.co/rest/v1/responses?select=*"))


if __name__ == "__main__":
    unittest.main()
