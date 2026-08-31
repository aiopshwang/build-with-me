# Changelog

## 0.2.0 — 2026-08-31

- Record files renamed: `진행.md` → `PROGRESS.md`, `지도.md` → `MAP.md`, `내-말로.md` → `MY-WORDS.md` (Korean filenames caused encoding/tooling trouble; spoken names in conversation stay Korean). Template stamp is now `build-with-me v0.2`.
- On resume, the skill quietly renames old-named files to the new names, so existing folders keep working — records are never discarded.

## 0.1.0 — 2026-08-31

- Skeleton, validator with SKILL.md word budget.
- SKILL.md body: 514 tokens (limit 900) — router, 5 invariants, 7 rules, 하지 않는 것.
- First validation: 10 Claude runs (5 RED / 5 GREEN) + 1 called variant; see evals/results/…
- v0.1.1 content: rule 4 records the confirmed line at ②; no own servers / no foreground commands / stay on the stack.
- Start sheet split: `시작하기.md` (ko) + `GETTING-STARTED.md` (en).
