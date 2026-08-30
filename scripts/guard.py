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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pre-share"); p.add_argument("dir"); p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_pre_share)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
