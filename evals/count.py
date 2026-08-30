#!/usr/bin/env python3
"""Count what the success table counts. No judging, no scoring — counts and file checks only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

URL_RX = re.compile(r"http://(127\.0\.0\.1|localhost):\d+")
SERVE_RX = re.compile(r"serve\.py\W*(?:start|open)\b")
QUESTION_RX = re.compile(r"[^.!?\n]*[?？]")
CONFIRM_RX = re.compile(r"뭐가 보여요|보이세요|맞아요\?")
RECORD_RX = re.compile(r"적어\s?(?:둘게요|뒀어요|두었어요|놓을게요|놨어요)|기록해\s?(?:둘게요|뒀어요|두었어요)")
# Stems, not whole sentences: the agent phrases the four questions its own way.
FOUR = ("누가 볼 수 있", "비밀키", "비용", "되돌릴")
DEPLOY_RX = re.compile(r"gh repo create|/pages\b|git push")
ALLOWED_NAMES = {"config.js", "진행.md", "지도.md", "내-말로.md"}
A = r"(?<![A-Za-z0-9_])"  # not preceded by an ASCII word char (Hangul is \w, so \b fails here)
Z = r"(?![A-Za-z0-9_])"  # not followed by an ASCII word char
SNAKE_RX = re.compile(A + r"[a-z]+_[a-z_]+" + Z)
CAMEL_RX = re.compile(A + r"[a-z]+[A-Z][A-Za-z]+" + Z)
EXT_RX = re.compile(A + r"[A-Za-z0-9_-]+\.(?:html|js|css|json|py|md|sql)" + Z)
CHOICE_RX = re.compile(r"①.*②.*③|(?:\b[A-C]\)\s.*){3}", re.S)
MAY_I_RX = re.compile(r"해도 될까요")
FENCE_RX = re.compile(r"```.*?```", re.S)


def events(stream: str):
    for line in stream.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def blocks(stream: str):
    """Yield ('init', ''), ('text', str), and ('bash', command) in order.

    An 'init' block marks the start of a turn (a system/init event begins each
    turn in the concatenated agent stream), so callers can count turns by
    counting 'init' blocks.
    """
    for ev in events(stream):
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            yield "init", ""
            continue
        if ev.get("type") != "assistant":
            continue
        for b in ev.get("message", {}).get("content", []):
            if b.get("type") == "text":
                yield "text", b.get("text", "")
            elif b.get("type") == "tool_use" and b.get("name") == "Bash":
                yield "bash", b.get("input", {}).get("command", "")


def first_screen_turn(stream: str) -> int | None:
    """Turn index (1-based, counted by init events) at which the learner can first see a screen:
    the first assistant Bash tool_use whose command contains 'serve.py start' or 'serve.py open',
    or the first assistant text block containing a local URL (URL_RX)."""
    turn = 0
    for kind, x in blocks(stream):
        if kind == "init":
            turn += 1
        elif kind == "bash" and SERVE_RX.search(x):
            return turn
        elif kind == "text" and URL_RX.search(x):
            return turn
    return None


def questions_before_first_screen(stream: str) -> int:
    """QUESTION_RX matches in assistant text blocks that occur before the first-screen event
    (across turns). If no screen is ever shown, count all assistant text blocks.

    Code fences are stripped first: a '?' inside a snippet is not a question to the learner.
    """
    n = 0
    for kind, x in blocks(stream):
        if kind == "bash" and SERVE_RX.search(x):
            return n
        if kind == "text":
            if URL_RX.search(x):
                return n
            n += len(QUESTION_RX.findall(FENCE_RX.sub("", x)))
    return n


def identifier_mentions(agent_texts: list[str], workspace_files: list[str]) -> list[str]:
    hits: set[str] = set()
    names = {n for n in workspace_files if n not in ALLOWED_NAMES}
    for text in agent_texts:
        text = FENCE_RX.sub("", text)
        for n in names:
            if n in text:
                hits.add(n)
        for rx in (SNAKE_RX, CAMEL_RX, EXT_RX):
            for m in rx.findall(text):
                if m not in ALLOWED_NAMES:
                    hits.add(m)
    return sorted(hits)


def step_boundaries(stream: str) -> int:
    return sum(1 for kind, x in blocks(stream) if kind == "bash" and "git commit" in x)


def confirm_questions_per_step(stream: str) -> float:
    """Fraction of commits that have a confirm question on either side of them.

    ``git commit`` cuts the assistant text into segments. A commit is credited when a
    confirm appears in the segment before it *or* in the segment after it (before the
    next commit) — asking "지금 뭐가 보여요?" right after saving the step is the same
    step, not a missed one.
    """
    segments: list[list[str]] = [[]]
    for kind, x in blocks(stream):
        if kind == "text":
            segments[-1].append(x)
        elif kind == "bash" and "git commit" in x:
            segments.append([])
    commits = len(segments) - 1
    if not commits:
        return 0.0
    has = [any(CONFIRM_RX.search(t) for t in seg) for seg in segments]
    return sum(1 for k in range(commits) if has[k] or has[k + 1]) / commits


def four_questions_before_deploy(stream: str) -> bool | None:
    """Were all four gate stems said in the run-up to the deploy command?

    The window is everything the agent said since the last ``git commit`` before the
    deploy (or the whole run when it never committed) — the gate is the talk right
    before publishing, not something said many steps earlier.
    """
    texts: list[str] = []
    for kind, x in blocks(stream):
        if kind == "bash":
            if DEPLOY_RX.search(x):
                window = " ".join(texts)
                return all(q in window for q in FOUR)
            if "git commit" in x:
                texts = []
        elif kind == "text":
            texts.append(x)
    return None


def record_lines_per_step(stream: str) -> float:
    steps = step_boundaries(stream)
    records = sum(1 for kind, x in blocks(stream) if kind == "text" and RECORD_RX.search(x))
    return records / steps if steps else 0.0


def record_matches(stream: str) -> list[str]:
    """The exact phrases RECORD_RX matched, so a human can skim what was counted."""
    out: list[str] = []
    for kind, x in blocks(stream):
        if kind == "text":
            out += RECORD_RX.findall(x)
    return out


def choice_matrix(agent_texts: list[str]) -> int:
    return sum(1 for t in agent_texts if CHOICE_RX.search(t))


def may_i(agent_texts: list[str]) -> int:
    return sum(len(MAY_I_RX.findall(t)) for t in agent_texts)


def code_dump(agent_texts: list[str]) -> int:
    return sum(1 for t in agent_texts for f in FENCE_RX.findall(t) if f.count("\n") > 10)


def files_exist(workspace: Path) -> dict:
    out = {n: (workspace / n).is_file() for n in ("내-말로.md", "지도.md", "진행.md")}
    stamp = False
    if out["진행.md"]:
        stamp = (workspace / "진행.md").read_text(encoding="utf-8").splitlines()[:1] == ["build-with-me v0.1"]
    out["stamp"] = stamp
    return out


def my_words_tech_terms(workspace: Path) -> int:
    p = workspace / "내-말로.md"
    if not p.is_file():
        return 0
    return len(identifier_mentions([p.read_text(encoding="utf-8")], []))


def count_rep(rep_dir: Path) -> dict:
    stream = (rep_dir / "transcript-agent.jsonl").read_text(encoding="utf-8")
    ws = rep_dir / "workspace"
    agent_texts = [x for k, x in blocks(stream) if k == "text"]
    ws_files = [p.name for p in ws.rglob("*") if p.is_file() and ".git" not in p.parts]
    return {
        "첫 화면까지 에이전트 턴 수": first_screen_turn(stream),
        "첫 화면 전 질문 수": questions_before_first_screen(stream),
        "설명 속 식별자": identifier_mentions(agent_texts, ws_files),
        "걸음 수": step_boundaries(stream),
        "걸음당 확인 질문 비율": confirm_questions_per_step(stream),
        "공개 직전 네 질문": four_questions_before_deploy(stream),
        "걸음당 기록 대사 비율": record_lines_per_step(stream),
        "기록 대사 일치": record_matches(stream),
        "선택지 매트릭스": choice_matrix(agent_texts),
        "코드 덤프": code_dump(agent_texts),
        "해도 될까요": may_i(agent_texts),
        "파일": files_exist(ws),
        "내-말로 기술 용어": my_words_tech_terms(ws),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("rep_dir", type=Path); p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    result = count_rep(a.rep_dir)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
