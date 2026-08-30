#!/usr/bin/env python3
"""build-with-me guard: pre-share / probe / human-edits. Standard library only.

Every message printed for a learner is plain Korean with no file names, function
names or library names. Exit codes: 0 clean, 1 findings, 2 error.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ANON_KEY_FILE = "config.js"
SKIP_DIRS = {".git", "node_modules", "archive", ".bwm", "__pycache__"}
SCAN_SUFFIXES = {".html", ".js", ".css", ".json", ".md", ".txt", ".sql", ".env"}
PATTERNS = {
    "openai": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "aws": re.compile(r"AKIA[0-9A-Z]{16}"),
    "service_role": re.compile(r"service_role"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{40,}\."),
    "password": re.compile(r"password\s*="),
}
PLAIN = {
    "openai": "AI 회사 비밀키처럼 보이는 글자",
    "aws": "클라우드 비밀키처럼 보이는 글자",
    "service_role": "저장소의 '전권' 키를 가리키는 말",
    "jwt": "공개용이 아닌 긴 열쇠 글자",
    "password": "비밀번호가 적힌 줄",
}


@dataclasses.dataclass
class Finding:
    path: str
    line: int
    kind: str
    sample: str


@dataclasses.dataclass
class ProbeResult:
    table: str
    action: str
    expected: str
    observed: str
    ok: bool
    note: str = ""


def _urllib_http(method: str, url: str, headers: dict[str, str], body: str | None) -> tuple[int, str]:
    data = body.encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def probe(url: str, key: str, rules: dict[str, Any], http=None) -> list[ProbeResult]:
    http = http or _urllib_http
    base = url.rstrip("/") + "/rest/v1/"
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
               "Prefer": "return=representation"}
    results: list[ProbeResult] = []
    for table, spec in rules.get("tables", {}).items():
        want = {a: ("allow" if spec["anon"].get(a) else "deny") for a in ("insert", "select", "delete")}
        row = spec.get("probe_row", {})
        observed: dict[str, str] = {}
        inserted_id = None
        status, text = http("POST", base + table, headers, json.dumps(row, ensure_ascii=False))
        observed["insert"] = "allow" if status in (200, 201) else "deny"
        if observed["insert"] == "allow":
            try:
                inserted_id = json.loads(text)[0].get("id")
            except (ValueError, IndexError, AttributeError):
                inserted_id = None
        status, text = http("GET", base + f"{table}?select=*&limit=5", headers, None)
        try:
            rows = json.loads(text) if status == 200 else []
        except ValueError:
            rows = []
        observed["select"] = "allow" if rows else "deny"
        if inserted_id is not None:
            status, _ = http("DELETE", base + f"{table}?id=eq.{inserted_id}", headers, None)
            observed["delete"] = "allow" if status in (200, 204) else "deny"
        else:
            observed["delete"] = "unknown"
        # Control: at least one action the rules allow must have been observed as allowed.
        control_ok = any(want[a] == "allow" and observed[a] == "allow" for a in want)
        for action in ("insert", "select", "delete"):
            obs = observed[action] if control_ok else "unknown"
            ok = control_ok and obs == want[action]
            note = "" if control_ok else "허용된 동작도 하나도 안 돼서, 막힌 건지 연결이 안 된 건지 알 수 없어요"
            if control_ok and action == "delete" and inserted_id is not None and observed["delete"] == "deny":
                note = "확인용 줄 하나가 저장소에 남았어요 — 나중에 대시보드에서 지우면 돼요"
            results.append(ProbeResult(table, action, want[action], obs, ok, note))
    return results


def _mask(s: str) -> str:
    return s[:6] + "…" if len(s) > 6 else s


def scan_dir(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        anon_budget = 1 if path.name == ANON_KEY_FILE else 0
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            for kind, rx in PATTERNS.items():
                for m in rx.finditer(line):
                    if kind == "jwt" and anon_budget > 0:
                        anon_budget -= 1
                        continue
                    findings.append(Finding(str(path.relative_to(root)), lineno, kind, _mask(m.group(0))))
    return findings


def cmd_pre_share(args: argparse.Namespace) -> int:
    root = Path(args.dir).resolve()
    if not root.is_dir():
        print("확인할 폴더를 찾지 못했어요.")
        return 2
    findings = scan_dir(root)
    if args.json:
        print(json.dumps([dataclasses.asdict(f) for f in findings], ensure_ascii=False))
    elif not findings:
        print("공개해도 되는 파일들이에요 — 비밀키처럼 보이는 글자가 없어요.")
    else:
        print("잠깐, 공개하기 전에 볼 게 있어요:")
        for f in findings:
            print(f"- {PLAIN[f.kind]}가 들어 있어요 (파일 {f.path}, {f.line}번째 줄, '{f.sample}')")
        print("이 줄들을 빼고 나서 다시 확인할게요.")
    return 1 if findings else 0


PLAIN_ACTION = {"insert": "적기", "select": "보기", "delete": "지우기"}


def cmd_probe(args: argparse.Namespace) -> int:
    rules = json.loads(Path(args.rules).read_text(encoding="utf-8"))
    results = probe(args.url, args.key, rules)
    OBS = {"allow": "됨", "deny": "막힘", "unknown": "알 수 없음"}
    if args.json:
        print(json.dumps([dataclasses.asdict(r) for r in results], ensure_ascii=False))
    else:
        for r in results:
            mark = "✓" if r.ok else "✗"
            print(f"{mark} '{r.table}' {PLAIN_ACTION[r.action]}: 약속은 {'허용' if r.expected == 'allow' else '금지'}, "
                  f"실제로는 {OBS[r.observed]}{(' — ' + r.note) if r.note else ''}")
        if all(r.ok for r in results):
            print("접근 규칙이 약속대로 동작해요.")
        else:
            print("약속과 다른 곳이 있어요. 고치고 다시 확인할게요.")
    return 0 if all(r.ok for r in results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pre-share"); p.add_argument("dir"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_pre_share)
    p = sub.add_parser("probe"); p.add_argument("url"); p.add_argument("key"); p.add_argument("rules")
    p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_probe)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
