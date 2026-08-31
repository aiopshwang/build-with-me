# Build With Me

*You cannot code. That is the starting condition, not a problem to fix first.*

[![Validate](https://img.shields.io/github/actions/workflow/status/aiopshwang/build-with-me/validate.yml?branch=main&label=validate)](https://github.com/aiopshwang/build-with-me/actions/workflows/validate.yml)
[![Version](https://img.shields.io/github/v/release/aiopshwang/build-with-me?label=version)](https://github.com/aiopshwang/build-with-me/releases)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[한국어](README.ko.md)

**First time?** Read the one-page start sheet: [GETTING-STARTED.md](GETTING-STARTED.md) (한국어: [시작하기.md](시작하기.md)). This README is for the instructor or developer deciding whether to install it.

Build With Me is an Agent Skill that takes someone who cannot code from one sentence to a local page in minutes, then to a shareable link — teaching only at the moments where something would otherwise break.

- [Who it's for](#who-its-for)
- [Install and call it](#install-and-call-it)
- [What happens](#what-happens)
- [Before and after](#before-and-after)
- [What ends up in your folder](#what-ends-up-in-your-folder)
- [Picking up where you left off](#picking-up-where-you-left-off)
- [Before anything goes public](#before-anything-goes-public)
- [Requirements](#requirements)
- [On Codex](#on-codex)
- [When it gets stuck](#when-it-gets-stuck)
- [Evidence and how to reproduce](#evidence-and-how-to-reproduce)
- [Scope, versioning, feedback, license](#scope-versioning-feedback-license)

## Who it's for

**For:** someone who says they cannot code, someone doing this for the first time, someone who wants to build something to show people, and someone coming back to continue what they did last time.

**Not for:** developers who want code explained line by line, and not for code review.

## Install and call it

```bash
npx skills add aiopshwang/build-with-me
```

You know it worked when the last line is a green `Done!`, with build-with-me listed just above it. Silence after that is normal — the skill sits still until you call it.

Then start `claude` or `codex` in that folder and type:

```text
I can't code. I want to build something.
```

(fallback: `use the build-with-me skill`)

## What happens

The golden path, one line per step:

1. **A folder of its own.** If the current folder is not empty or is already a repository, the agent proposes `문서/내앱/<name>` and hands the move to you. You see: an empty folder that belongs to this project only.
2. **One sentence from you.** The opening line is reassurance, not a form; if you have no idea, it offers examples instead of a question. You see: exactly one question asked before anything appears on screen.
3. **A placeholder screen in 90 seconds.** The moment it hears your sentence it writes a single `index.html`, starts the preview server, and opens it. You see: a page in your browser with your title on it and the line "this is just holding the spot".
4. **A north star in one line.** The agent writes the line first — who opens it, what they see, what happens when they do something — and you only correct the wrong parts. You see: one sentence describing your app that you agreed to.
5. **A map of steps.** It works backwards from the result to the input, then flips the order; anything out of range is written down under "that's part 2" instead of being argued about. You see: a checklist in `MAP.md`.
6. **One visible step at a time.** A step is not finished until something new is on the screen, and it does not move on before you see it. You see: one new thing on the page after every step.
7. **One real feature, end to end.** Storage (Supabase) is brought in only when the answer to "where does what I typed have to stay?" is that it must be saved; the access rule is agreed in plain words first. You see: your own data on your own page.
8. **The gate, then the link.** A GitHub account is handed to you only when it is needed, the four questions are answered, then it deploys. You see: a public address that did not exist before those four answers.

Sources: [`SKILL.md`](skills/build-with-me/SKILL.md), [`start-and-decompose.md`](skills/build-with-me/references/start-and-decompose.md), [`storage-questions-first.md`](skills/build-with-me/references/storage-questions-first.md).

## Before and after

Both transcripts below are from real runs of the same request ("an app that shows my Excel inventory sheet on screen"), turn 1, verbatim — the sessions were conducted in Korean, so the quotes are Korean:

**No skill — agent's turn-1 reply:**

> 현재 폴더가 비어 있네요. 몇 가지 여쭤볼게요.
>
> **엑셀 재고 파일을 화면으로 보여주는 앱을 만들어 드릴 수 있어요.** 시작하기 전에 몇 가지만 알려주세요.
>
> **1. 엑셀 파일은 어떻게 생겼나요?**
>
> - 품목명, 수량, 단위, 날짜 같은 항목이 있나요?
> - 컬럼(열) 이름들을 알려주실 수 있나요?
>
> (more questions follow — still no screen)

**build-with-me on — same scenario, agent's turn-1 reply:**

> 이 작업은 중요하니 여기까지 적어둘게요 — 다음에 이어서 할 때 이걸 읽어요.
>
> 화면이 뜨면, 제가 생각한 걸 한 줄로 말해볼게요. 틀린 부분만 고쳐주시면 돼요:
>
> **"열면 내가 매주 보는 재고 목록이 한눈에 보이는 화면"**
>
> 맞아요?

Across the first validation's 10 runs (Claude, RED 5 / GREEN 5), the 5 runs with the skill on opened a screen on turn 1 in 5 of 5; the 5 runs without the skill did so in 0 of 5. Counting method and the other scenarios: [evals/results/2026-08-30-first-validation.md](evals/results/2026-08-30-first-validation.md).

## What ends up in your folder

| What | Why it is there |
| --- | --- |
| `PROGRESS.md` | Progress. Two lines at the end of every step: what is done, what is next. This is the file read first when work resumes. |
| `MAP.md` | The map: the north star, the list of steps with checkmarks, "that's part 2", and the spots where you got stuck twice. |
| `MY-WORDS.md` | One sentence per step in the learner's own words. No step is left blank — it is what you read later to explain the app to someone else. |
| `index.html` | The page itself. `config.js` and `access-rules.json` appear beside it only when something has to be saved. |
| `.bwm/` | Preview-server state (the port it is listening on). Git-ignored, along with `archive/` and `.env` files. |
| `CLAUDE.md` / `AGENTS.md` | One appended line telling the next session to read `PROGRESS.md` first and say where you left off. |

`PROGRESS.md`, `MAP.md` and `MY-WORDS.md` contain no keys — that is why the start sheet tells a stuck learner to send the first two straight to an instructor. Templates: [`assets/`](skills/build-with-me/assets/).

## Picking up where you left off

The method is that the recording is made **visible**. At the end of every step the agent writes the two lines and says out loud why it is writing them ("this matters, so I am noting where we got to — next time I read this first"). Git commits stay invisible; the record does not.

At a new session, and immediately after the agent's context is compacted, its first action is to read `PROGRESS.md` and say "last time we got to …, next is …". The one line appended to `CLAUDE.md` / `AGENTS.md` is what makes it do that, so the learner never has to notice that context was lost.

When stuck, sending `PROGRESS.md` and `MAP.md` to an instructor is the escape hatch — the same two files `guard.py pre-share` scans. Source: [`carry-on.md`](skills/build-with-me/references/carry-on.md).

## Before anything goes public

The order is fixed: **hosting account → four questions → deploy → link.** No public address exists before the gate passes. First publish answers all four; a redeploy is one line unless the change touches one of them.

1. **Who can see it?** Anyone with the link. The agent states the storage rule in one plain sentence and pastes what `guard.py probe` just observed against the real API. If what people submit carries names or contact details, visibility is locked to you alone — not offered as a choice.
2. **Does a secret leave?** `guard.py pre-share .` scans the folder and its answer is read out as it is, warning lines included.
3. **Is the cost unbounded?** With no store, it passes. With a store, one line confirms the free plan — a free store stops at its limit rather than billing you.
4. **Can it be undone?** Taking it down is one sentence to the agent, and the address stops answering a few minutes later.

**What it never does:** write a secret key into the chat; run a server of its own (preview happens only through the skill's serve command); leave the fixed stack of one HTML file plus one store; or ask permission for anything except money, accounts, deletion and publishing. Source: [`publish-safety-gate.md`](skills/build-with-me/references/publish-safety-gate.md), [`guard.py`](skills/build-with-me/scripts/guard.py).

## Requirements

- **Claude Code or Codex** as the calling agent.
- **Node.js**, for the `npx` install command.
- **Python 3**, for the preview server and `guard.py`. If Python is absent, [`serve.ps1`](skills/build-with-me/scripts/serve.ps1) does the same job on Windows PowerShell.
- **Git, GitHub CLI (`gh`) and a GitHub account** — only at the publish step. The agent runs `winget install GitHub.cli` itself and hands you the sign-up and the eight-character device-code login.
- **A Supabase account** — only if something has to be saved. Skipped entirely otherwise.
- Measured on **Windows 11**.

## On Codex

Codex reads the project's `AGENTS.md`, which is why the resume line is written to both `CLAUDE.md` and `AGENTS.md`. The installer puts the skill at `.agents/skills/build-with-me/` in the project folder, with Claude Code getting a link to that same place, and [`agents/openai.yaml`](skills/build-with-me/agents/openai.yaml) supplies the name Codex displays plus its default prompt, `$build-with-me: I can't code. Help me build something I can show people.`

Opening a browser is blocked inside the Codex sandbox, so the skill detects that and hands the step to the human: it prints the address and asks you to paste it into the address bar. The `workspace-write` sandbox also blocks outbound network, which the publish step needs — see [evals/README.md](evals/README.md) for the flag the eval runner uses.

## When it gets stuck

**The install printed `Done!` and then nothing happened.** That is the expected state. The skill does nothing until you start `claude` or `codex` and say the call sentence.

**It did not trigger.** Mention the skill by name in any phrasing (`build with me 기반으로 개발 시작하자` works), or say the fallback line: `use the build-with-me skill`. In the first validation, 4 of the 5 scenarios triggered on the first message alone; all 5 triggered once the fallback line was added.

**The browser did not open.** The agent prints the address instead and asks you to open it — `http://127.0.0.1:<port>`, where the port is recorded in `.bwm/serve.json`.

**The deploy failed.** The agent retries once silently, then explains in three lines: what happened, why, what it will do. After a second failure it closes the session with "let's finish the version that works on my computer today" and writes the retry point into `PROGRESS.md`.

**Take the link down.** Say `내려줘` / "take it down". The agent deletes or unpublishes the repository and the address stops answering a few minutes later.

**Start over, or remove the skill.** Saying `새로 시작` moves only the files the skill made into `archive/<date>/` — nothing is deleted and your own files are not touched. To uninstall, delete `.agents/skills/build-with-me/` (and the `.claude/skills/build-with-me` link if it is there); to update, run the install command again.

## Evidence and how to reproduce

Nothing here is a judged score. When this README or its evidence files quote a result, it is a deterministic count — a file that exists, a command that exited 0, a string that appears in an output, a line a test checked — never a model's opinion of how well a session went.

```bash
python evals/run_learner.py --scenario <s> --persona <p> --arm baseline|candidate [--host claude|codex] --output <dir>
python evals/count.py <rep-dir>
```

The matrix is 12 runs: 10 on Claude (five scenario × persona pairs, each run once RED with the skill off and once GREEN with it on) plus 2 GREEN-only runs on Codex, reported separately and never mixed into the Claude ten.

- Claude 10: [evals/results/2026-08-30-first-validation.md](evals/results/2026-08-30-first-validation.md)
- Codex 2: [evals/results/2026-08-30-codex.md](evals/results/2026-08-30-codex.md)
- Name-mention trigger (v0.2.0): [evals/results/2026-08-31-name-trigger.md](evals/results/2026-08-31-name-trigger.md)
- Rows and thresholds, counts only: [evals/rubric.json](evals/rubric.json) · fixtures and matrix: [evals/README.md](evals/README.md)

## Scope, versioning, feedback, license

Measured on Windows 11, with Claude Code and Codex as the calling agents. Hosting target: GitHub Pages. Storage target: Supabase. On macOS, only the browser-open command has been checked by inspection; a full macOS run has not been done.

**Versioning.** Current version 0.2.0; what changed is in [CHANGELOG.md](CHANGELOG.md).

**Feedback.** Open an issue: <https://github.com/aiopshwang/build-with-me/issues>

**License.** MIT. See [LICENSE](LICENSE).
