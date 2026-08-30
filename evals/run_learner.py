#!/usr/bin/env python3
"""Multi-turn run: a simulated learner (persona) talks to an agent that may or may not
have build-with-me loaded. Baseline and candidate differ only in --plugin-dir.

Nothing here scores anything. count.py reads the artefacts afterwards.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EVALS = Path(__file__).resolve().parent
REPO_ROOT = EVALS.parent
AGENT_TOOLS = "Bash,Read,Write,Edit,Glob,Grep,Skill"
END = "[끝]"


def launch_command(argv: list[str]) -> list[str]:
    resolved = shutil.which(argv[0])
    if resolved is None:
        return list(argv)
    if Path(resolved).suffix.lower() in {".cmd", ".bat"}:
        return ["cmd.exe", "/c", resolved, *argv[1:]]
    return [resolved, *argv[1:]]


def events(stream: str):
    for line in stream.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def final_response(stream: str) -> str:
    final = ""
    for ev in events(stream):
        if ev.get("type") == "result" and isinstance(ev.get("result"), str):
            final = ev["result"]
    return final


def session_id(stream: str) -> str | None:
    sid = None
    for ev in events(stream):
        if ev.get("session_id"):
            sid = ev["session_id"]
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                return sid
    return sid


def skill_invoked(stream: str) -> bool:
    for ev in events(stream):
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                if "build-with-me" in json.dumps(block.get("input", {})):
                    return True
    return False


def is_done(text: str) -> bool:
    return END in text


def read_scenario(name: str) -> tuple[dict, str]:
    text = (EVALS / "scenarios" / f"{name}.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    return meta, m.group(2).strip()


def learner_prompt(facts: str, history: list[tuple[str, str]]) -> str:
    lines = ["당신이 아는 사실:", facts, "", "지금까지의 대화:"]
    for learner, agent in history:
        lines += [f"나: {learner}", f"에이전트: {agent}", ""]
    lines += ["에이전트의 마지막 말에 대해 다음에 할 말을 한두 문장만 쓰세요. 설명이나 따옴표 없이 말 자체만.",
              f"링크를 받았거나 더 할 말이 없으면 {END} 만 쓰세요."]
    return "\n".join(lines)


def agent_argv(*, arm: str, model: str, resume: str | None) -> list[str]:
    argv = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--setting-sources", "",
            "--strict-mcp-config", "--permission-mode", "bypassPermissions", "--model", model,
            "--tools", AGENT_TOOLS]
    if arm == "candidate":
        argv += ["--plugin-dir", str(REPO_ROOT)]
    if resume:
        argv += ["--resume", resume]
    return argv


def run_proc(argv: list[str], *, cwd: Path, stdin: str, timeout: int, env: dict) -> tuple[str, str, int]:
    try:
        r = subprocess.run(launch_command(argv), cwd=cwd, input=stdin, text=True, encoding="utf-8",
                           errors="replace", capture_output=True, timeout=timeout, check=False, env=env)
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as exc:
        return (exc.stdout if isinstance(exc.stdout, str) else ""), "timeout", 124


def run_one(args: argparse.Namespace, rep: int) -> dict:
    meta, facts = read_scenario(args.scenario)
    persona = EVALS / "personas" / f"{args.persona}.md"
    rep_dir = args.output / args.scenario / args.persona / args.arm / f"rep-{rep}"
    workspace = rep_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, BWM_NO_OPEN="1")
    history: list[tuple[str, str]] = []
    learner_msg = meta["first_message"]
    sid = None
    invoked = False
    stream_all = []
    for turn in range(1, args.max_turns + 1):
        stream, err, rc = run_proc(agent_argv(arm=args.arm, model=args.model, resume=sid),
                                   cwd=workspace, stdin=learner_msg, timeout=args.timeout, env=env)
        stream_all.append(stream)
        sid = sid or session_id(stream)
        agent_msg = final_response(stream)
        invoked = invoked or skill_invoked(stream)
        history.append((learner_msg, agent_msg))
        with (rep_dir / "turns.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"turn": turn, "learner": learner_msg, "agent": agent_msg,
                                "session_id": sid, "rc": rc}, ensure_ascii=False) + "\n")
        if rc == 124 or not agent_msg.strip():
            break
        out, _, _ = run_proc(["claude", "-p", "--model", args.learner_model, "--setting-sources", "",
                              "--strict-mcp-config", "--tools", "", "--append-system-prompt",
                              persona.read_text(encoding="utf-8")],
                             cwd=workspace, stdin=learner_prompt(facts, history), timeout=180, env=env)
        learner_msg = out.strip()
        if is_done(learner_msg):
            break
    (rep_dir / "transcript-agent.jsonl").write_text("\n".join(stream_all), encoding="utf-8")
    record = {"scenario": args.scenario, "persona": args.persona, "arm": args.arm, "rep": rep,
              "turns": len(history), "skill_invoked": invoked if args.arm == "candidate" else False,
              "storage": meta.get("storage", "none")}
    (rep_dir / "run.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenario", required=True); p.add_argument("--persona", required=True)
    p.add_argument("--arm", choices=("baseline", "candidate"), required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--model", default="sonnet"); p.add_argument("--learner-model", default="sonnet")
    p.add_argument("--max-turns", type=int, default=15); p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--reps", type=int, default=1)
    args = p.parse_args(argv)
    for rep in range(1, args.reps + 1):
        print(json.dumps(run_one(args, rep), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
