---
name: condense-claude
description: Make a long CLAUDE.md shorter. Moves details that docs/ already holds (or should hold) out of CLAUDE.md and leaves short links in their place, while keeping the rules, commands and layout an agent needs in every session. Use when the user asks to condense, shorten or slim down CLAUDE.md, or when CLAUDE.md has grown long after many changes.
---

# Condense CLAUDE.md

`CLAUDE.md` is read at the start of every session, so each line costs something every time. It should hold what an agent needs in almost every task, and point to `docs/` for the rest.

## Keep in CLAUDE.md

- What the project is, in a few sentences.
- The layout: top-level directories and subprojects, one line each.
- Rules that apply across the code: code style, naming and writing rules, error handling, test placement, commit format, doc language.
- The commands: build, format, check, test, run one test.
- Things that must not be changed (fixed ids, pinned versions) and decisions not yet made.

## Move out of CLAUDE.md

- Full API, CLI, config or file format descriptions.
- Step-by-step guides and long examples.
- Design explanations, history, and plans that are done or no longer valid.
- Anything that repeats a file in `docs/`.

## Steps

1. Read `CLAUDE.md` and every file in `docs/`.
2. For each section of `CLAUDE.md`, decide: keep, shorten, or move.
3. Before you remove a detail, make sure `docs/` holds it. If it does not, move the text into the right doc (or a new one) first. Never drop information that exists nowhere else.
4. Replace the moved text with one sentence and a link. Follow the project's link rules (some projects link only to `docs/index.md`).
5. Remove what is wrong or out of date. Check claims against the code. Do not move stale text into `docs/`.
6. Check that every link points to a file that exists and holds what the sentence says.
7. Tell the user what moved where, what was deleted as out of date, and the line count before and after.
