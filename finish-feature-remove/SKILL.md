---
name: finish-feature-remove
description: Complete a feature removal with quality checks, testing, orphaned-reference verification, documentation updates, commits, and PR creation. Supports common Rust (Cargo) and Python projects (uv / Poetry / Hatch / pip). Runs the appropriate formatter, linter, and test commands for the detected toolchain, verifies no orphaned references remain, updates relevant documentation, creates commits, pushes to remote, creates a PR via the `gh` CLI, and manages the review workflow. AUTOMATICALLY use this skill when feature removal work is complete and the removal checklist is finished, or when the user explicitly requests to "finish removal", "wrap up removal", "complete removal and create PR", or indicates the removal is ready for finalization.
---

# Finish Feature Remove

Complete a feature removal with quality checks, testing, orphaned-reference verification, documentation updates, and PR workflow across common Rust and Python project layouts.

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

Removals are frequently breaking. Check the project's declared version and keep it in sync with any documented "current version" in `CLAUDE.md` or `README.md`.

| Project type | Where the version lives | How to read it |
|---|---|---|
| Rust (Cargo) | `Cargo.toml` `[package] version` | `cargo metadata --format-version 1 \| jq -r '.packages[] \| select(.name == "<crate>") \| .version'` |
| Python       | `pyproject.toml` `[project] version` (PEP 621) or `[tool.poetry] version` | `grep '^version' pyproject.toml` (or `uv version` / `poetry version --short` if the tool is installed) |

Checklist (apply only if the project actually tracks a "current version" outside the manifest):

- [ ] Manifest version matches any "Current Version" line in `CLAUDE.md` / `README.md`.
- [ ] If the removal contains **breaking changes** (most public-API removals are):
  - [ ] Version bumped in the manifest following SemVer (MAJOR bump for breaking public API changes on a 1.x+ project).
  - [ ] "Current Version" doc references updated.
  - [ ] Breaking changes and migration notes documented in the project's changelog or release-notes file (if one exists).
- [ ] If the removal has **no breaking changes** (internal-only removal, never-exposed API, or equivalent replacement):
  - [ ] Version was not changed (unless the project's policy says otherwise).
  - [ ] Removal summarized in changelog or commit messages.

If the project doesn't track a version anywhere other than the manifest, skip this sub-step.

### 1b. Automated formatting and fixes

Run the project's standard formatter and auto-fixer — removals often leave unused imports or dead code that these catch.

| Project type | Commands |
|---|---|
| Rust (Cargo) | `cargo fix --allow-dirty --allow-staged` then `cargo fmt` |
| Python (uv, repo has `format.py` / `type_check.py` scripts) | `uv run python format.py` (and `uv run python <script>.py` for other project-provided Python fix scripts). If the script is already executable (`chmod +x` with a PEP 723 shebang), `uv run format.py` also works. |
| Python (uv, no wrapper script) | `uv run ruff format .` and `uv run ruff check --fix .` if `ruff` is a dependency; otherwise `uvx ruff format .` and `uvx ruff check --fix .` |
| Python (Poetry) | `poetry run ruff format .` and `poetry run ruff check --fix .` (or `black` / `isort` if the project uses them) |
| Python (Hatch) | `hatch run fmt` / `hatch run lint` if scripts are defined in `[tool.hatch.envs.*.scripts]`; otherwise `hatch run ruff format .` and `hatch run ruff check --fix .` |
| Python (pip) | `ruff format .` / `black .` / `isort .` — whichever is configured in `pyproject.toml` |

If the repository provides wrapper scripts (e.g. `format.py`, `scripts/fmt.sh`, a `justfile`, or a `Makefile` target), prefer those — they encode the project's authoritative configuration.

Also consider removing newly unused dependencies that only the deleted feature needed:

| Project type | Command |
|---|---|
| Rust (Cargo) | `cargo remove <crate>` (or edit `[dependencies]` and run `cargo update`) |
| Python (uv) | `uv remove <pkg>` |
| Python (Poetry) | `poetry remove <pkg>` |
| Python (Hatch / pip) | edit `pyproject.toml` `dependencies` by hand, then re-lock/reinstall |

### 1c. Language-agnostic convention checklist

Verify manually — automated tools won't catch all of these:

- [ ] No orphaned imports, unused items, or dead code left behind by the removal.
- [ ] No commented-out blocks of "the old code" — delete cleanly.
- [ ] No stray `TODO` / `FIXME` comments referencing the removed feature.
- [ ] Errors and docstrings that mentioned the removed feature are updated.
- [ ] Imports/`use` statements still follow the project's existing style (nesting depth, grouping, ordering).
- [ ] If the removal touched a type or trait hierarchy, every sibling implementation that needed updating was updated (e.g., pattern matches on an enum after dropping a variant, visitor methods after dropping a node).

If the project's `CLAUDE.md` lists additional conventions, fold them in here as well.

## 2. Testing

Run the project's full test suite and fix any failures before moving on. **Do not proceed until tests pass.**

| Project type | Commands |
|---|---|
| Rust (Cargo) | `cargo test` (and `cargo test --all-features` if features are in play). For workspaces, `cargo test --workspace`. |
| Python (uv) | `uv run pytest` (respecting any `pytest.ini` / `pyproject.toml` config). If the project pins a test script, use it. |
| Python (Poetry) | `poetry run pytest` |
| Python (Hatch) | `hatch run test` if defined, otherwise `hatch run pytest` |
| Python (pip) | `pytest` (inside the activated virtualenv) |

If the project uses Cargo features or optional Python extras that the removed feature intersected with, run the matrix — not just the default configuration.

Additional language-level checks to run if configured:

- **Rust**: `cargo clippy --all-targets -- -D warnings`, and `cargo check` (workspace) if clippy isn't wired up.
- **Python**: type check via `uv run pyright` / `poetry run pyright` / `mypy .`, whichever the project uses. If the repo provides a `type_check.py` or similar wrapper, prefer that.

If a repo-wide wrapper like `/test` or a `make test` target exists, prefer it — it will encode the canonical sequence.

If tests fail, debug and fix until they pass; do not skip failing tests to get the PR out.

## 3. Verify No Orphaned References

This step is specific to removals. After quality checks and tests pass, search the codebase to ensure no references to the removed feature remain anywhere — code, tests, docs, or config.

```bash
# Replace <feature> with the removed identifier, file name, module, flag, etc.
# Run a few variants to cover different surface forms.
rg -i '<feature>'
rg '<RemovedType>|<removed_function>|<removed_module>'
rg 'TODO.*<feature>|FIXME.*<feature>'
```

Also check dependency manifests and lockfiles for now-unused third-party packages pulled in only by the removed feature (and remove them via the command in §1b if so).

**Expected results:**
- No references to removed types, functions, modules, CLI flags, or config keys.
- No broken imports, dead code, or unreachable branches.
- No lingering documentation, examples, or fixtures.

**If orphaned references are found:**
- Remove or update them now.
- Re-run §1b (formatter / auto-fix) and §2 (tests) to confirm the codebase still builds clean.

## 4. Documentation Updates

Identify documentation affected by the removal and update it. Orphaned docs are worse than missing docs — they mislead users into calling things that no longer exist.

1. **Enumerate documentation files:**
   ```bash
   ls *.md
   find docs/ -name "*.md" -type f 2>/dev/null
   ```
2. **Look at your diff** (`git diff` / `git diff --stat`) to figure out which surfaces went away: public API, CLI, file formats, config schema, install steps, etc.
3. **Remove or rewrite the sections that described those surfaces.** Common candidates:
   - `README.md` — overview, quickstart, usage examples, feature lists
   - `CLAUDE.md` — development workflow, commands, conventions for AI assistants
   - `docs/api.md` (or `docs/<module>.md`) — public API
   - `docs/cli.md` — CLI arguments, subcommands, output
   - `docs/examples.md` / `examples/` — examples using the removed feature
   - `CHANGELOG.md` — add a breaking-change notice if the project maintains one
   - Rust-specific: rustdoc comments in `src/lib.rs` or module roots that are rendered on docs.rs
   - Python-specific: Sphinx / MkDocs sources under `docs/`, if present

Prefer deleting whole sections cleanly over leaving "previously this did X" notes, unless the project maintains historical docs intentionally.

Be thorough but concise. If nothing surfaced in the diff touches user-visible docs, say so explicitly instead of padding edits.

## 5. Git Commit

Follow the project's commit conventions. Check `.vscode/general-commit.instructions.md` if present, `CONTRIBUTING.md` if present, or a commitlint config if present for project-specific rules, then fall back to:

- Imperative headline, capitalized verb, no trailing period.
- Headline short enough to read at a glance (typically ≤ 50–72 chars; some projects cap at "under 10 words").
- Blank line between headline and body.
- Body explains the *why* (removal motivation, breaking-change notice); the diff shows the *what*.
- Reference code items as `` `code_item` `` and paths as `` `path/to/file` ``.
- Prefer phrasing like "Removed `X`", "Dropped support for `Y`" over vague "Cleaned up".

If the repo exposes a `/commit` skill, prefer that — it will encode the conventions above.

Default: **create a new commit**; do not squash unless the user asks.

## 6. Push to Remote

```bash
# first push of a new branch
git push -u origin <branch-name>

# subsequent pushes
git push
```

## 7. Create Pull Request

Draft a PR with `gh pr create`. Call out breaking changes prominently so reviewers and downstream consumers see them. Trim sections that don't apply.

```bash
gh pr create --title "<concise title, under 70 chars>" --body "$(cat <<'EOF'
## Summary
- 1–3 bullets naming what was removed and why.
- Note whether this is a breaking change.

## Changes
- Per-area bullets (e.g., "parser:", "CLI:", "docs:") describing what went away.

## Breaking changes
<!-- Omit this section if the removal is not breaking. -->
- Describe the user-visible break.
- Provide migration guidance: what to use instead, or how to adapt.

## Test plan
- [ ] All tests pass (`cargo test` / `uv run pytest` / …)
- [ ] Formatter / linter clean
- [ ] Type-check clean (if applicable)
- [ ] No orphaned references (`rg` of removed identifiers returns nothing)
- [ ] Documentation updated

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Record the PR number for later steps.

## 8. Request Review

**Human reviewers** (GitHub CLI works fine):

```bash
gh pr edit <pr-number> --add-reviewer "user1,user2"
gh pr edit <pr-number> --add-reviewer "org/team"
```

**GitHub Copilot code review** — request it **by default**, via the CLI, unless the user explicitly asked you not to. Request it **once per PR**: never re-request it after pushing fixes, because each new review brings new comments and the review–fix cycle would not end. A further review is the user's call.

```bash
gh pr edit <pr-number> --add-reviewer "@copilot"
```

`gh` supports the `@copilot` special value on `--add-reviewer` (`gh` ≥ 2.76; not on GitHub Enterprise Server). If the CLI rejects it as an unsupported value, fall back to the Reviewers dropdown on the PR page in the web UI. `--reviewer` on `gh pr create` does **not** accept `@copilot`, so request Copilot in a follow-up `gh pr edit`.

Do **not** use `gh pr edit --add-assignee "@copilot"` as a substitute — assigning Copilot is not a review request and instead makes it edit the PR.

**⚠️ Important:** When responding to Copilot review comments, do **not** @-mention "Copilot" or "@copilot" in your replies — mentions trigger Copilot to edit the PR rather than just review it.

Verify requests landed — and do not trust the exit code alone. `gh pr edit --add-reviewer "@copilot"` can exit 0 while the request never lands, and `gh pr view --json reviewRequests` does not list bot reviewers, so it reads `[]` even on success. Check the REST endpoint, which does list them:

```bash
gh api repos/:owner/:repo/pulls/<pr-number>/requested_reviewers --jq '.users[].login'
```

If Copilot is absent from that output, request it directly by its bot login before moving on:

```bash
gh api -X POST repos/:owner/:repo/pulls/<pr-number>/requested_reviewers \
  -f 'reviewers[]=copilot-pull-request-reviewer[bot]'
```

**Fallback: Codex cloud review when Copilot is out of credits.** If Copilot cannot review because its premium-request quota or credits are exhausted (the user says so, or Copilot's request or review reports a quota or credit error), ask Codex to review the PR on its cloud instead, by mentioning it in a PR comment:

```bash
gh pr comment <pr-number> --body "@codex review"
```

This needs the repository connected to Codex cloud (the ChatGPT Codex Connector GitHub app); Codex then posts a regular PR review with inline comments as `chatgpt-codex-connector[bot]`. The Copilot rules carry over unchanged: request it **once per PR**, never again after fixes, and do **not** @-mention `@codex` in replies to its review threads, since each mention starts a new Codex task. Do **not** substitute a local `codex review` run for the cloud review: the user wants the review on the PR, where it is visible and threaded. Wait for it with the same background poll below, setting `bot` to Codex's login.

## 9. Wait for the Review, Polling Automatically in the Background

Copilot's review can take anywhere from a minute to half an hour. **Start waiting for it yourself, immediately after requesting it, and do not hand the waiting back to the user.** A foreground poll with a short cap gives up too early; poll from a background shell instead, so you are re-invoked the moment the review lands, even after your turn has ended.

Right after the request in section 8, record the time and start this loop with the Bash tool's `run_in_background: true`:

```bash
bot="copilot-pull-request-reviewer[bot]"   # or "chatgpt-codex-connector[bot]" for the Codex fallback
since=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for i in $(seq 120); do                     # every 30 s, for up to an hour
  n=$(gh api repos/:owner/:repo/pulls/<pr-number>/reviews \
        --jq "[.[] | select(.user.login == \"$bot\" and .submitted_at >= \"$since\")] | length")
  [ "${n:-0}" -gt 0 ] && { echo "$bot review arrived"; exit 0; }
  sleep 30
done
echo "no $bot review after 60 minutes"; exit 1
```

Counting only reviews submitted after `since` keeps an older review, from before this skill ran, from being mistaken for the new one. Tell the user in one line that the PR is up and you are waiting for the review (Copilot's, or Codex's if it took over), then stop; do not also poll in the foreground.

When the background task reports that the review arrived, **continue straight to section 10 without asking**: fetch both halves of the review — they live at different endpoints, and `gh pr view` shows neither reliably — and address them.

```bash
# inline, line-anchored comments: the actionable findings
gh api repos/:owner/:repo/pulls/<pr-number>/comments \
  --jq '.[] | {id, path, line, body}'
# the review's own summary body, which can list further findings without inline comments
gh api repos/:owner/:repo/pulls/<pr-number>/reviews --jq '.[] | {user: .user.login, state, body}'
```

A review whose `state` is `COMMENTED` with zero inline comments and no findings in its body means Copilot found nothing actionable. Say so and move to section 11.

If the loop gives up after an hour, check that the request landed at all: `requested_reviewers` often reads empty for a bot even when it did, so look for the `review_requested` event on the timeline (`gh api repos/:owner/:repo/issues/<pr-number>/timeline --jq '.[] | select(.event == "review_requested")'`). Then tell the user the request is in but no review has landed, so they can decide whether to wait longer or merge without it. Do not claim a review came back empty when it simply never arrived — those are different outcomes.

Human reviewers are the exception: do not poll for them on a timer. Tell the user the PR is ready and let them signal when human feedback is in.

## 10. Address Review Comments

When reviews arrive:

1. Read every inline comment and the summary body (see the commands above).
2. **Judge each comment before acting on it.** Reviewers, Copilot especially, produce both real defects and confident-sounding false positives. On a removal PR the most valuable findings are orphaned references the sweep missed, and the most common false positives are objections to deletions that were the point of the PR. Verify each claim against the code before touching anything, and if a comment is wrong or does not apply, leave the code alone and say why in your reply.
3. For each comment that *is* real, make the change, re-run the quality/test/orphaned-reference steps from sections 1–3.
4. Commit. Reference the review in the body (e.g. "From Copilot review on #<pr-number>" or "From Codex review on #<pr-number>") so the reason for the change is recoverable later.
5. `git push`.
6. Do **not** request another Copilot review after the push, and do not wait for one: the one review requested in section 8 is the only one this skill acts on. If a later review arrives anyway (a repository setting can trigger one on push), tell the user it is there and leave it for them to decide on, rather than starting another round of fixes.
7. Once every comment of that review is either fixed or explicitly answered, move on.

## 11. Final Notification

Once the PR is green and all review feedback is handled:

1. Leave a comment on the PR (the owner's handle, if one should be tagged, can be looked up from `gh repo view --json owner`):
   ```bash
   gh pr comment <pr-number> --body "All review comments have been addressed and all tests are passing. Ready for merge when you are."
   ```
2. In the conversation, give the user the PR URL, confirm the checks passed, and ask them to merge.

## Integration with Other Skills

- **Triggered after:** `/init-feature-remove` or any equivalent removal-branch setup.
- **Often uses internally:**
  - `/test` — if the project provides a canonical test sequence
  - `/debug-tests` — for fixing test failures
  - `/commit` — for commit-message conventions
  - `/squash` — optional, only if the user asks

## Notes

- Detect the toolchain *first*, then pick commands — don't run Cargo commands in a Python-only repo or vice versa.
- Prefer repo-provided wrapper scripts (`format.py`, `scripts/fmt.sh`, `just`, `make`) over raw tool invocations — they encode the project's authoritative configuration.
- **Always verify no orphaned references** — the single biggest failure mode of a removal PR is a missed import or a doc section pointing at something that no longer exists.
- **Breaking changes deserve extra care** — version bump, changelog entry, migration guidance in the PR body.
- If the repo keeps a CHANGELOG or release-notes file, update it; if it only relies on commit messages, trust the messages.
- `gh` must be authenticated (`gh auth status`).
- GitHub Copilot code review is requested by default (`gh pr edit <n> --add-reviewer "@copilot"`) and requires repository-level enablement. See: https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review
- When Copilot is out of credits, Codex reviews the PR on its cloud instead: comment `@codex review` on the PR (section on requesting review). The same once-per-PR rule applies, and its review is polled for as `chatgpt-codex-connector[bot]`.
- Copilot is requested once per PR, never again after fixes, so reviewing and fixing cannot loop. Its review is waited for automatically, by a background poll started right after the request (section 9), and its comments are addressed as soon as it lands, without asking. `gh pr view --json reviewRequests` omits bot reviewers, so verify via `gh api .../requested_reviewers`, or the timeline's `review_requested` event, instead of assuming the request failed.
- `gh` reference: https://cli.github.com/manual/gh_pr

## Exit Criteria

Done when:
1. All tests / lints / type checks pass.
2. No orphaned references remain.
3. Documentation is updated (or explicitly confirmed N/A).
4. Commits are created and pushed.
5. PR is opened and the reviewer requests are verified as landed.
6. Copilot's review (or Codex's cloud review, when Copilot is out of credits) has been waited for in the background and either arrived and been addressed, or not arrived within the hour (the difference stated plainly).
7. Review comments (if any) are addressed, and any judged to be false positives are answered with a reason.
8. User is notified to merge.
