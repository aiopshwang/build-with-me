"""probe checks the RLS story the agent told the learner against the real API."""
import json
import sys
import unittest
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "skills/build-with-me/scripts"))
import guard  # noqa: E402

RULES = {"version": 1, "tables": {"responses": {
    "anon": {"insert": True, "select": False, "delete": False},
    "probe_row": {"answer": "확인용"}}}}


class FakeSupabase:
    """PostgREST semantics: a row the caller may not SELECT is invisible in every response.

    * ``POST`` with ``Prefer: return=minimal`` answers 201 and an *empty body* — the
      insert-only policy of v0.1 gives no representation back.
    * ``GET`` answers ``[]`` unless the select policy exists.
    * ``DELETE`` with ``Prefer: return=representation`` answers 204 and ``[]`` when no
      delete policy exists (PostgREST reports "nothing was deleted", not 401), and 200
      with the deleted rows when the policy allows it.
    """

    def __init__(self, insert=True, select=False, delete=False):
        self.policy = {"insert": insert, "select": select, "delete": delete}
        self.rows = {}
        self.calls = []

    def _filters(self, url):
        query = urllib.parse.urlparse(url).query
        return {k: v[0][len("eq."):] for k, v in urllib.parse.parse_qs(query).items()
                if v[0].startswith("eq.")}

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url, headers.get("Prefer")))
        assert headers["apikey"] == "anon" and headers["Authorization"] == "Bearer anon"
        if method == "POST":
            assert headers.get("Prefer") == "return=minimal", headers
            if not self.policy["insert"]:
                return 401, '{"message":"new row violates row-level security policy"}'
            rid = len(self.rows) + 1
            self.rows[rid] = json.loads(body)
            return 201, ""
        if method == "GET":
            return 200, json.dumps([{"id": k, **v} for k, v in self.rows.items()] if self.policy["select"] else [])
        if method == "DELETE":
            assert headers.get("Prefer") == "return=representation", headers
            if not self.policy["delete"]:
                return 204, "[]"
            want = self._filters(url)
            hit = [k for k, v in self.rows.items()
                   if all(str(v.get(c)) == val for c, val in want.items())]
            removed = [{"id": k, **self.rows.pop(k)} for k in hit]
            return 200, json.dumps(removed, ensure_ascii=False)
        raise AssertionError(method)


class ProbeTest(unittest.TestCase):
    def test_rules_match_reality(self):
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=FakeSupabase())
        self.assertEqual([(r.action, r.ok) for r in results], [("insert", True), ("select", True), ("delete", True)])

    def test_insert_only_policy_passes(self):
        """The v0.1 policy: anon may insert and nothing else. No leftover 'unknown'."""
        fake = FakeSupabase(insert=True, select=False, delete=False)
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=fake)
        self.assertEqual([(r.action, r.observed, r.ok) for r in results],
                         [("insert", "allow", True), ("select", "deny", True), ("delete", "deny", True)])

    def test_select_leak_is_reported(self):
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=FakeSupabase(select=True))
        bad = [r for r in results if not r.ok]
        self.assertEqual([(r.action, r.observed) for r in bad], [("select", "allow")])

    def test_delete_leak_is_reported(self):
        """The rules promise delete is blocked but the table really lets anon delete."""
        results = guard.probe("https://x.supabase.co", "anon", RULES, http=FakeSupabase(delete=True))
        bad = [r for r in results if not r.ok]
        self.assertEqual([(r.action, r.observed) for r in bad], [("delete", "allow")])

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
        self.assertEqual(fake.calls[0], ("POST", "https://x.supabase.co/rest/v1/responses", "return=minimal"))
        self.assertTrue(fake.calls[1][1].startswith("https://x.supabase.co/rest/v1/responses?select=*"))
        # the delete filter names every probe_row column, url-encoded
        self.assertEqual(fake.calls[2][0], "DELETE")
        self.assertIn("answer=eq." + urllib.parse.quote("확인용"), fake.calls[2][1])

    def test_public_list_variant_passes(self):
        """'누구나 볼 수 있고, 적는 건 당신뿐' — insert denied, select allowed, delete denied.

        With insert blocked the probe can never create its own row, so delete is
        genuinely unverifiable. The control action (select) succeeded, so this must
        read as consistent with the rules, not as a mismatch to report.
        """
        rules = {"version": 1, "tables": {"items": {
            "anon": {"insert": False, "select": True, "delete": False},
            "probe_row": {"answer": "확인용"}}}}
        fake = FakeSupabase(insert=False, select=True, delete=False)
        fake.rows[1] = {"answer": "이미 있음"}
        results = guard.probe("https://x.supabase.co", "anon", rules, http=fake)
        self.assertEqual([(r.action, r.ok) for r in results],
                         [("insert", True), ("select", True), ("delete", True)])
        delete_result = next(r for r in results if r.action == "delete")
        self.assertEqual(delete_result.observed, "unknown")
        self.assertIn("지울 줄이 없어서", delete_result.note)

    def test_unverifiable_allowed_delete_still_fails(self):
        """Rules claiming delete is allowed still can't be waved through unverified."""
        rules = {"version": 1, "tables": {"items": {
            "anon": {"insert": False, "select": True, "delete": True},
            "probe_row": {"answer": "확인용"}}}}
        fake = FakeSupabase(insert=False, select=True, delete=False)
        fake.rows[1] = {"answer": "이미 있음"}
        results = guard.probe("https://x.supabase.co", "anon", rules, http=fake)
        delete_result = next(r for r in results if r.action == "delete")
        self.assertFalse(delete_result.ok)


if __name__ == "__main__":
    unittest.main()
