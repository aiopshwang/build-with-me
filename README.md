# Build With Me

*You cannot code. That is the starting condition, not a problem to fix first.*

[한국어](README.ko.md)

Build With Me is an Agent Skill that takes someone who cannot code from one sentence to a local page in minutes, then to a shareable link — teaching only at the moments where something would otherwise break.

```bash
npx skills add aiopshwang/build-with-me
```

Then, in that folder's terminal:

```text
I can't code. I want to build something.
```

(fallback: `use the build-with-me skill`)

## See it

Start here: [GETTING-STARTED.md](GETTING-STARTED.md) — the one-page start sheet. (Korean version: [시작하기.md](시작하기.md).)

The golden path, in one paragraph: a folder, one sentence, a 90-second placeholder screen so there is something on screen before any question is asked, a north star agreed in one line, a local page built one visible step at a time, one real feature working end to end, a GitHub account handed over when needed, four questions answered before anything goes public (who can see it, does a secret leave, is the cost unbounded, can it be undone), a deploy, a link — and Supabase brought in only if something needs to be saved.

Both transcripts below are from real runs of the same request ("an app that shows my Excel inventory sheet on screen"), turn 1, verbatim — the sessions were conducted in Korean, so the quotes are Korean:

**No skill — agent's turn-1 reply:**

> 현재 폴더가 비어 있네요. 몇 가지 여쭤볼게요.
>
> **엑셀 재고 파일을 화면으로 보여주는 앱을 만들어 드릴 수 있어요.** 시작하기 전에 몇 가지만 알려주세요.
>
> **1. 엑셀 파일은 어떻게 생겼나요?**
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

## What is measured

Nothing here is a judged score. When this README or its evidence files quote a result, it is a deterministic count — a file that exists, a command that exited 0, a string that appears in an output, a line a test checked — never a model's opinion of how well a session went.

## Scope

Measured on Windows 11, with Claude Code and Codex as the calling agents. Hosting target: GitHub Pages. Storage target: Supabase. On macOS, only the browser-open command has been checked by inspection; a full macOS run has not been done.

## License

MIT. See [LICENSE](LICENSE).
