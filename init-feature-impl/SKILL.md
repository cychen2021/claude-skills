---
name: init-feature-impl
description: Initialize a new feature implementation for common Rust (Cargo) or Python (uv / Poetry / Hatch / pip) projects. Creates a feature branch with a sensible naming convention, optionally designs an implementation plan, and prepares for implementation. AUTOMATICALLY use this skill when the user explicitly requests a new feature with phrases like "I want a new feature", "Let's add [feature]", "Start implementing [feature]", "Begin new feature [description]", or any clear request to start feature development work.
---

# Init Feature Impl

Initialize a new feature implementation with proper branch setup and planning. Works for common Rust (Cargo) and Python (uv / Poetry / pip) projects.

## 0. Detect the project type

Before branching, identify the project's toolchain so the plan and implementation reference the right commands:

- **Rust (Cargo)** — `Cargo.toml` at the repo root or a workspace root.
- **Python** — `pyproject.toml` at the repo root. Further distinguish:
  - **uv** — `[tool.uv]`, a `uv.lock`, or `build-backend = "uv_build"`.
  - **Poetry** — `[tool.poetry]` or a `poetry.lock`.
  - **Hatch** — `[tool.hatch]`.
  - **pip / PEP 621 plain** — none of the above; plain `[project]` table or `requirements*.txt`.
- **Mixed / polyglot** — both `Cargo.toml` and `pyproject.toml` (e.g. a PyO3 crate).

Note the detected type — later sections refer back to it.

## 1. Clarify Requirements

If the feature request is ambiguous, use the `AskUserQuestion` tool to clarify:

- What is the expected behavior or outcome?
- Are there specific constraints or requirements?
- Which parts of the codebase will be affected?
- Are there examples or use cases to consider?

## 2. Create Feature Branch

Use a descriptive, kebab-case branch name. Prefer the project's existing convention (sample recent branches with `git for-each-ref --sort=-committerdate --format='%(refname:short)' refs/heads refs/remotes | head -20`) before applying the defaults below.

```bash
git checkout -b feature/<descriptive-name>
```

Team conventions sometimes prefix with a username:

```bash
git checkout -b <username>/feature/<descriptive-name>
```

**Branch naming guidelines:**
- Kebab-case for multi-word descriptions.
- Descriptive but concise.
- Examples: `feature/add-retry-middleware`, `feature/improve-type-inference`, `feature/exp-command-group`.

## 3. Planning Phase (Optional)

**Default:** plan non-trivial features before coding.

**Skip when:** the user passes `--skip-plan`, or the change is a trivial one-liner.

**Planning is worth it for:**
- New public API surface or CLI commands.
- Multi-file or cross-module changes.
- Architectural decisions with multiple valid approaches.
- Unclear scope that requires codebase exploration first.

**How to plan:**

1. Explore with `Glob` / `Grep` / `Read` (or an Explore subagent for larger scopes) to understand:
   - Existing patterns and architecture in the detected toolchain.
   - Related code that will be affected.
   - Testing patterns (where `tests/` live, how fixtures work).
   - Documentation the change will impact.
2. Design the implementation, covering:
   - Specific files and functions to touch.
   - How the feature integrates with existing code.
   - What tests are needed and where they go.
   - What documentation needs updating.
3. Present the plan to the user in a message for approval.

**If planning is skipped:** sketch the approach in a short message before coding.

## 4. Wait for Go-Ahead

Unless the user passed `--skip-plan` (see **Arguments** below), **wait for explicit user approval** after presenting the plan before writing code.

Go-ahead signals include: "Looks good, go ahead", "Start implementing", "Proceed", "Let's do it".

When `--skip-plan` is used, the flag itself counts as the go-ahead — proceed directly to step 5 (the draft PR) without a separate approval gate. Still sketch the intended approach in a short message first, so the user can course-correct if needed.

## 5. Open a Draft PR

Once the user has approved the plan (or, with `--skip-plan`, right after the sketch), open the PR now, as a **draft**, before changing any code. An open draft PR shows the work's progress as commits land, runs CI on each push so a break shows up early, and gives the plan a home that outlives the session. `/finish-feature-impl` later rewrites its description for the finished work and marks it ready for review.

Skip this step only when the project's own instructions say small changes go straight to the default branch without a PR, and this change is one of those.

GitHub cannot open a PR for a branch with no commits beyond its base, so start the branch with an empty commit that records the plan (follow the project's commit conventions for its wording):

```bash
git commit --allow-empty -m "Start <feature name>" -m "<the approved plan, or the sketch, as short bullets>"
git push -u origin <branch-name>
gh pr create --draft --title "<concise title, under 70 chars>" --body "$(cat <<'EOF'
## Summary
- 1–3 bullets on what the feature will do.

## Plan
- The approved plan, as bullets.

## Status
Draft: work in progress. It will be marked ready for review when done.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Do **not** request a review on the draft (no `@codex review` comment, no reviewers): `/finish-feature-impl` requests the one Codex review when the work is done. Record the PR number and give the user the link in one line.

## 6. Begin Implementation

Once approved:

1. Create a task list with `TodoWrite` tracking the implementation steps.
2. Implement following the approved plan. Mark tasks `in_progress` → `completed` as you go.
3. Follow language-appropriate conventions:
   - **Rust**: derive standard traits (`Debug`, `PartialEq`) on data types where sensible; avoid `unwrap`/`expect` in library code; keep `use` nesting shallow and consistent with the existing code.
   - **Python**: type hints on public functions; docstrings on public classes/functions; prefer the project's existing import style (absolute vs. relative); avoid bare `except`.
4. Add tests alongside new behavior (`src/**/mod tests` or `tests/` for Rust; `tests/` or `test_*.py` for Python).
5. Always read the project's `CLAUDE.md` / `CONTRIBUTING.md` for conventions that override these defaults.
6. **Commit verified work promptly — never leave it uncommitted across a session boundary.** Once a coherent unit of work passes the formatter, type-check, and tests, commit it and `git push`, so the draft PR shows the progress. Uncommitted changes are the only git state that does not survive a branch switch, `git clean`, or a new session — work left uncommitted has been silently lost and had to be redone from scratch. If you cannot commit yet (e.g. still mid-feature), `git stash` so it stays recoverable.
7. **One commit per concern.** A large feature lands as several commits, not one: for example a preparatory rename or extraction that changes no behaviour, then each independent piece of the feature with its own tests, then documentation that spans them. Keep tests with the code they test, and order commits so each one builds. `/finish-feature-impl` has the full splitting rules.

## Arguments

**`--skip-plan`**: Skip the planning phase *and* the separate approval gate for simple features where the implementation is straightforward. The user supplying `--skip-plan` is itself the approval signal.

Example:
- User: "I want a new feature to add support for X --skip-plan"
- Sketch the approach in a brief message, then go directly from step 2 (branch creation) to step 5 (the draft PR) and then step 6 (implementation) — no plan document, no separate approval gate.

## Integration with Other Skills

- **After implementation:** `/finish-feature-impl` to run quality checks, update docs, commit, push, and mark the draft PR ready for review. It requests a Codex code review (an `@codex review` comment) by default, waits for it with a background poll, and addresses the comments when they land, rather than handing back to the user to wait — if the user doesn't want Codex reviewing this feature, say so when handing off.
- **During implementation:** `/test` / `/debug-tests` if the project provides them.
- **For commits:** `/commit` if the project provides it; otherwise follow conventions from `.vscode/general-commit.instructions.md` if present, or fall back to `CONTRIBUTING.md`, commitlint configuration, or recent `git log` examples.

## Notes

- This skill focuses on initialization and planning — implementation only begins after user approval. It opens a draft PR before the first code change, so the work is visible from its first commit.
- Always consult `CLAUDE.md` for the project's current workflow and conventions before committing to a plan.
- Feature branches keep the default branch stable and make review easier.
- Never end a session with completed work uncommitted — commit it (or `git stash`) first; uncommitted changes do not survive a branch switch, `git clean`, or a new session. At session start, check `git log` / `git reflog`: a branch whose only reflog entry is "Created from HEAD" never had its work committed.
