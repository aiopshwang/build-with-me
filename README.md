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

Start here: [시작하기.md](시작하기.md) — the one-page start sheet, Korean then English.

The golden path, in one paragraph: a folder, one sentence, a 90-second placeholder screen so there is something on screen before any question is asked, a north star agreed in one line, a local page built one visible step at a time, one real feature working end to end, a GitHub account handed over when needed, four questions answered before anything goes public (who can see it, does a secret leave, is the cost unbounded, can it be undone), a deploy, a link — and Supabase brought in only if something needs to be saved. A real before/after transcript from an actual run will replace this paragraph once the first validation run is complete; nothing has been run yet.

## What is measured

Nothing here is a judged score. When this README or its evidence files quote a result, it is a deterministic count — a file that exists, a command that exited 0, a string that appears in an output, a line a test checked — never a model's opinion of how well a session went.

## Scope

Measured on Windows 11, with Claude Code and Codex as the calling agents. Hosting target: GitHub Pages. Storage target: Supabase. On macOS, only the browser-open command has been checked by inspection; a full macOS run has not been done.

## License

MIT. See [LICENSE](LICENSE).
