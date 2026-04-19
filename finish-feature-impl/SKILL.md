---
name: finish-feature-impl
description: Complete a feature implementation with quality checks, testing, documentation updates, commits, and PR creation. Supports common Rust (Cargo) and Python projects (uv/Poetry/pip). Runs the appropriate formatter, linter, and test commands for the detected toolchain, updates relevant documentation, creates commits, pushes to remote, creates a PR via the `gh` CLI, and manages the review workflow. AUTOMATICALLY use this skill when feature implementation work is complete, or when the user explicitly requests to "finish feature", "wrap up feature", "complete feature and create PR", or indicates the feature is ready for finalization.
---

# Finish Feature Impl

Complete a feature implementation with quality checks, testing, documentation, and PR workflow across common Rust and Python project layouts.

## 0. Detect the project type

Before running any tool, identify the project type from files at the repository root. Use this detection to pick the right commands in every later step.

- **Rust (Cargo)** — `Cargo.toml` at the repo root (or at a workspace root).
- **Python** — a `pyproject.toml` at the repo root. Further distinguish the workflow by looking at the file:
  - **uv** — `[tool.uv]` section, or a `uv.lock` file, or a `[build-system]` `build-backend = "uv_build"`, or project scripts installed via `uv sync`.
  - **Poetry** — `[tool.poetry]` section, or a `poetry.lock` file.
  - **Hatch** — `[tool.hatch]` section.
  - **pip / setuptools / PEP 621 plain** — none of the above; a `requirements*.txt` or a plain `[project]` table.
- **Mixed / polyglot** — if both `Cargo.toml` and `pyproject.toml` exist (e.g. a PyO3 crate), run the checks for both.

If detection is ambiguous, ask the user which toolchain to use before proceeding.

The command tables below are keyed off this detection. Use the column that matches the detected type; skip the others.

## 1. Pre-commit Quality Checks

### 1a. Version verification (if versioned)

Check the project's declared version and keep it in sync with any documented "current version" in `CLAUDE.md` or `README.md`.

| Project type | Where the version lives | How to read it |
|---|---|---|
| Rust (Cargo) | `Cargo.toml` `[package] version` | `cargo metadata --format-version 1 \| jq -r '.packages[] \| select(.name == "<crate>") \| .version'` |
| Python       | `pyproject.toml` `[project] version` (PEP 621) or `[tool.poetry] version` | `grep '^version' pyproject.toml` (or `uv version` / `poetry version --short` if the tool is installed) |

Checklist (apply only if the project actually tracks a "current version" outside the manifest):

- [ ] Manifest version matches any "Current Version" line in `CLAUDE.md` / `README.md`.
- [ ] If the feature contains **breaking changes**:
  - [ ] Version bumped in the manifest following SemVer.
  - [ ] "Current Version" doc references updated.
  - [ ] Breaking changes documented in a changelog / release notes file (if the project keeps one).
- [ ] If the feature has **no breaking changes**:
  - [ ] Version was not changed (unless the project's policy says otherwise).
  - [ ] Feature summarized in changelog or commit messages.

If the project doesn't track a version anywhere other than the manifest, skip this sub-step.

### 1b. Automated formatting and fixes

Run the project's standard formatter and auto-fixer.

| Project type | Commands |
|---|---|
| Rust (Cargo) | `cargo fix --allow-dirty --allow-staged` then `cargo fmt` |
| Python (uv, repo has `format.py` / `type_check.py` scripts) | `uv run format.py` (and any project-provided fix script) |
| Python (uv, no wrapper script) | `uv run ruff format .` and `uv run ruff check --fix .` if `ruff` is a dependency; otherwise `uvx ruff format .` and `uvx ruff check --fix .` |
| Python (Poetry) | `poetry run ruff format .` and `poetry run ruff check --fix .` (or `black` / `isort` if the project uses them) |
| Python (pip) | `ruff format .` / `black .` / `isort .` — whichever is configured in `pyproject.toml` |

If the repository provides wrapper scripts (e.g. `format.py`, `scripts/fmt.sh`, a `justfile`, or a `Makefile` target), prefer those — they encode the project's authoritative configuration.

### 1c. Language-agnostic convention checklist

Verify manually — automated tools won't catch all of these:

- [ ] No stray debug prints / `dbg!` / `console.log` / `print(` additions in library or production code.
- [ ] Public items have docstrings/rustdoc with at least a one-line summary.
- [ ] Errors carry enough context for a caller to act on them (not bare `"error"`).
- [ ] No `unwrap`/`expect` (Rust) or broad `except:` catches (Python) in non-test code unless the invariant is documented.
- [ ] Imports/`use` statements follow the project's existing style (nesting depth, grouping, ordering).
- [ ] New public API items are referenced from somewhere — or deliberately left for a follow-up, with a TODO that says so.

If the project's `CLAUDE.md` lists additional conventions, fold them in here as well.

## 2. Testing

Run the project's full test suite and fix any failures before moving on. **Do not proceed until tests pass.**

| Project type | Commands |
|---|---|
| Rust (Cargo) | `cargo test` (and `cargo test --all-features` if features are in play). For workspaces, `cargo test --workspace`. |
| Python (uv) | `uv run pytest` (respecting any `pytest.ini` / `pyproject.toml` config). If the project pins a test script, use it. |
| Python (Poetry) | `poetry run pytest` |
| Python (pip) | `pytest` (inside the activated virtualenv) |

Additional language-level checks to run if configured:

- **Rust**: `cargo clippy --all-targets -- -D warnings`, and `cargo check` (workspace) if clippy isn't wired up.
- **Python**: type check via `uv run pyright` / `poetry run pyright` / `mypy .`, whichever the project uses. If the repo provides a `type_check.py` or similar wrapper, prefer that.

If a repo-wide wrapper like `/test` or a `make test` target exists, prefer it — it will encode the canonical sequence.

If tests fail, debug and fix until they pass; do not skip failing tests to get the PR out.

## 3. Documentation Updates

Identify documentation affected by the change and update it.

1. **Enumerate documentation files:**
   ```bash
   # common locations
   ls *.md
   find docs/ -name "*.md" -type f 2>/dev/null
   ```
2. **Look at your diff** (`git diff` / `git diff --stat`) to figure out which surfaces changed: public API, CLI, file formats, config schema, install steps, etc.
3. **Update the files that actually describe those surfaces.** Common candidates:
   - `README.md` — install / quickstart / usage examples
   - `CLAUDE.md` — development workflow, commands, conventions for AI assistants
   - `docs/api.md` (or `docs/<module>.md`) — public API
   - `docs/cli.md` — CLI arguments, subcommands, output
   - `docs/examples.md` / `examples/` — new use cases
   - `CHANGELOG.md` — if the project maintains one
   - Rust-specific: rustdoc comments in `src/lib.rs` or module roots that are rendered on docs.rs
   - Python-specific: Sphinx / MkDocs sources under `docs/`, if present

Be thorough but concise. If nothing surfaced in the diff touches user-visible docs, say so explicitly instead of padding edits.

## 4. Git Commit

Follow the project's commit conventions. Check `.vscode/general-commit.instructions.md`, `CONTRIBUTING.md`, or a commitlint config for project-specific rules, then fall back to:

- Imperative headline, capitalized verb, no trailing period.
- Headline short enough to read at a glance (typically ≤ 50–72 chars; some projects cap at "under 10 words").
- Blank line between headline and body.
- Body explains the *why*; the diff shows the *what*.
- Reference code items as `` `code_item` `` and paths as `` `path/to/file` ``.

If the repo exposes a `/commit` skill, prefer that — it will encode the conventions above.

Default: **create a new commit**; do not squash unless the user asks.

## 5. Push to Remote

```bash
# first push of a new branch
git push -u origin <branch-name>

# subsequent pushes
git push
```

## 6. Create Pull Request

Draft a PR with `gh pr create`. The body template below is generic; trim sections that don't apply.

```bash
gh pr create --title "<concise title, under 70 chars>" --body "$(cat <<'EOF'
## Summary
- 1–3 bullets describing the change at a glance.

## Changes
- Per-area bullets (e.g., "parser:", "CLI:", "docs:") describing what moved.

## Test plan
- [ ] All tests pass (`cargo test` / `uv run pytest` / …)
- [ ] Formatter / linter clean
- [ ] Type-check clean (if applicable)
- [ ] Manual testing steps, if relevant

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Record the PR number for later steps.

## 7. Request Review

**Human reviewers** (GitHub CLI works fine):

```bash
gh pr edit <pr-number> --add-reviewer "user1,user2"
gh pr edit <pr-number> --add-reviewer "org/team"
```

**GitHub Copilot code review** — as of this writing, there's no reliable CLI path. To add Copilot as an actual reviewer, the user must pick it from the Reviewers dropdown on the PR page in the web UI. (`gh pr edit --add-assignee "@copilot"` adds Copilot as an assignee, which is *not* the same as requesting review and will instead trigger Copilot to make changes — avoid unless that's what you want.)

**⚠️ Important:** When responding to Copilot review comments, do **not** @-mention "Copilot" or "@copilot" in your replies — mentions trigger Copilot to edit the PR rather than just review it.

Verify requests landed:

```bash
gh pr view <pr-number> --json reviewRequests
gh pr view <pr-number>
```

Then wait for the user to signal that reviews have come in.

## 8. Address Review Comments

When reviews arrive:

1. Read them:
   ```bash
   gh pr view <pr-number>
   gh api repos/:owner/:repo/pulls/<pr-number>/comments
   ```
2. For each actionable comment, make the change, re-run the quality/test steps from sections 1 and 2, and commit.
3. `git push`.
4. Repeat until all comments are addressed.

## 9. Final Notification

Once the PR is green and all review feedback is handled:

1. Leave a comment tagging the owner (substitute their handle):
   ```bash
   gh pr comment <pr-number> --body "All review comments have been addressed and all tests are passing. Ready for merge when you are."
   ```
2. In the conversation, give the user the PR URL, confirm the checks passed, and ask them to merge.

## Integration with Other Skills

- **Triggered after:** `/init-feature-impl` or any equivalent feature-branch setup.
- **Often uses internally:**
  - `/test` — if the project provides a canonical test sequence
  - `/debug-tests` — for fixing test failures
  - `/commit` — for commit-message conventions
  - `/squash` — optional, only if the user asks

## Notes

- Detect the toolchain *first*, then pick commands — don't run Cargo commands in a Python-only repo or vice versa.
- Prefer repo-provided wrapper scripts (`format.py`, `scripts/fmt.sh`, `just`, `make`) over raw tool invocations — they encode the project's authoritative configuration.
- If the repo keeps a CHANGELOG or release-notes file, update it; if it only relies on commit messages, trust the messages.
- `gh` must be authenticated (`gh auth status`).
- GitHub Copilot code review requires repository-level enablement. See: https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review
- `gh` reference: https://cli.github.com/manual/gh_pr

## Exit Criteria

Done when:
1. All tests / lints / type checks pass.
2. Documentation is updated (or explicitly confirmed N/A).
3. Commits are created and pushed.
4. PR is opened and reviewers are requested.
5. Review comments (if any) are addressed.
6. User is notified to merge.
