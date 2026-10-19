---
name: finish-feature-remove
description: Complete a feature removal with quality checks, testing, orphaned-reference verification, documentation updates, commits, and PR creation. Supports common Rust (Cargo) and Python projects (uv / Poetry / Hatch / pip). Runs the appropriate formatter, linter, and test commands for the detected toolchain, verifies no orphaned references remain, updates relevant documentation, splits large changes into several commits, pushes to remote, marks the draft PR (opened by `init-feature-remove`) ready or creates one via the `gh` CLI, and manages the review workflow. AUTOMATICALLY use this skill when feature removal work is complete and the removal checklist is finished, or when the user explicitly requests to "finish removal", "wrap up removal", "complete removal and create PR", or indicates the removal is ready for finalization.
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

Default: **create new commits**; do not squash unless the user asks.

**Split large changes into several commits, one per concern**, so each can be read, reverted and bisected on its own. Split when the change does more than one thing, or when it is large (as a rough guide, more than about 300 changed lines or 10 files): then look for the seams. Typical seams:
  - removing the uses of the feature (callers, CLI wiring, config keys), before removing its definitions;
  - removing the feature's own code, together with the tests that covered it;
  - each independent part of a larger removal (one command, one module, one schema field), on its own;
  - documentation and the changelog's breaking change notice, last.

Rules for splitting:
- Keep tests in the same commit as the code they test, and generated files in the same commit as the source change that produced them.
- Order commits so each one builds: no commit deletes a definition that code left in place by that commit still uses. The full test suite runs once on the final state (sections 2 and 3), not once per commit.
- Stage each group by path (`git add <paths>`). When one file holds hunks of two concerns, stage one concern's hunks with a filtered patch (`git diff <file>` into a temporary file, delete the other hunks, then `git apply --cached` it), since interactive `git add -p` is not available. If a file does not split cleanly, keep it whole in one commit rather than forcing it.
- Commits already made during the work count: split only what is still uncommitted, and never rewrite commits that are already pushed.
- Do not split a small, single-purpose change just to have more commits.
- Afterwards, check `git log --stat <base>..HEAD`: each headline describes only its own commit's content.

## 6. Push to Remote

The branch normally tracks its remote already, since `/init-feature-remove` pushed it when it opened the draft PR:

```bash
git push

# only if the branch was never pushed
git push -u origin <branch-name>
```

## 7. Mark the Pull Request Ready

`/init-feature-remove` opened a draft PR when the work started. Find it:

```bash
gh pr view --json number,url,isDraft,title
```

**If the PR exists**, rewrite its title and description for the finished work with the template below (it replaces the draft's plan and status sections), then mark it ready for review:

```bash
gh pr edit <pr-number> --title "<concise title, under 70 chars>" --body "<the template below>"
gh pr ready <pr-number>
```

Mark it ready **before** requesting review in section 8: a draft can be skipped by reviewers and by Codex's automatic reviews.

**If there is no PR** (the branch was started without `/init-feature-remove`), create one, not as a draft. Call out breaking changes prominently so reviewers and downstream consumers see them. Trim sections that don't apply.

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

**Codex code review**: request it **by default**, unless the user explicitly asked you not to. Do **not** request GitHub Copilot's review (its credits are kept for other work). Codex is the ChatGPT Codex Connector GitHub app, which reviews a PR when someone comments `@codex review` on it. Request it **once per PR**: never re-request it after pushing fixes, because each new review brings new comments and the review–fix cycle would not end. A further review is the user's call.

```bash
gh pr comment <pr-number> --body "@codex review"
```

Do **not** substitute a local `codex review` run for this: the user wants the review on the PR, where it is visible and threaded.

Codex answers as the bot `chatgpt-codex-connector[bot]`. Within a few seconds it adds an 👀 reaction and posts a placeholder comment marked `<!-- codex-pull-request-review-summary -->`. That placeholder is **not** the review. The review itself comes later, in one of two forms:

- **Findings**: a pull request review (`state` `COMMENTED`) whose body starts with `<!-- codex-review-receipt:v1 -->` and "Codex Review", with the findings as inline comments.
- **Nothing found**: a plain PR comment starting with `<!-- codex-review-receipt:v1 -->` that says "Codex Review: Didn't find any major issues", plus a 👍 reaction on the PR.

If no 👀 reaction or placeholder appears within a couple of minutes, the Codex app is probably not installed on the repository (or Codex is not set up for it at chatgpt.com/codex). Tell the user rather than waiting an hour for nothing.

**⚠️ Important:** When replying to Codex's review comments, do **not** write `@codex` in your replies: a mention is a new instruction to Codex (another review, or a task to change the PR), not a reply.

## 9. Wait for the Review, Polling Automatically in the Background

Codex's review usually lands within a few minutes but can take longer. **Start waiting for it yourself, immediately after requesting it, and do not hand the waiting back to the user.** A foreground poll with a short cap gives up too early; poll from a background shell instead, so you are re-invoked the moment the review lands, even after your turn has ended.

Right after the request in section 8, record the time and start this loop with the Bash tool's `run_in_background: true`. It watches both places the review can land (a pull request review, or a plain PR comment when nothing was found), and only counts entries carrying the `codex-review-receipt` marker, so the early placeholder comment is not mistaken for the review:

```bash
since=$(date -u +%Y-%m-%dT%H:%M:%SZ)
bot='chatgpt-codex-connector[bot]'
for i in $(seq 120); do                     # every 30 s, for up to an hour
  r=$(gh api repos/:owner/:repo/pulls/<pr-number>/reviews \
        --jq "[.[] | select(.user.login == \"$bot\" and .submitted_at >= \"$since\")] | length")
  c=$(gh api repos/:owner/:repo/issues/<pr-number>/comments \
        --jq "[.[] | select(.user.login == \"$bot\" and .created_at >= \"$since\" and (.body | contains(\"codex-review-receipt\")))] | length")
  [ "${r:-0}" -gt 0 ] && { echo "codex review arrived with findings"; exit 0; }
  [ "${c:-0}" -gt 0 ] && { echo "codex review arrived: no major issues"; exit 0; }
  sleep 30
done
echo "no codex review after 60 minutes"; exit 1
```

Counting only entries made after `since` keeps an older review, from before this skill ran, from being mistaken for the new one. Tell the user in one line that the PR is up and you are waiting for Codex's review, then stop; do not also poll in the foreground.

When the background task reports a review with findings, **continue straight to section 10 without asking**: fetch both halves of the review (they live at different endpoints, and `gh pr view` shows neither reliably) and address them.

```bash
# inline, line-anchored comments: the actionable findings
gh api repos/:owner/:repo/pulls/<pr-number>/comments \
  --jq '.[] | {id, path, line, body}'
# the review's own summary body, which can list further findings without inline comments
gh api repos/:owner/:repo/pulls/<pr-number>/reviews --jq '.[] | {user: .user.login, state, body}'
```

When it reports "no major issues", Codex found nothing actionable. Say so and move to section 11.

If the loop gives up after an hour, check whether Codex picked the request up at all: look for its 👀 reaction on your `@codex review` comment or its placeholder comment (`gh api repos/:owner/:repo/issues/<pr-number>/comments --jq '.[] | select(.user.login == "chatgpt-codex-connector[bot]") | {created_at, body: .body[0:120]}'`). Then tell the user what you found, so they can decide whether to wait longer or merge without it. Do not claim a review came back empty when it simply never arrived: those are different outcomes.

Human reviewers are the exception: do not poll for them on a timer. Tell the user the PR is ready and let them signal when human feedback is in.

## 10. Address Review Comments

When reviews arrive:

1. Read every inline comment and the summary body (see the commands above).
2. **Judge each comment before acting on it.** Reviewers, automated ones especially, produce both real defects and confident-sounding false positives. On a removal PR the most valuable findings are orphaned references the sweep missed, and the most common false positives are objections to deletions that were the point of the PR. Verify each claim against the code before touching anything, and if a comment is wrong or does not apply, leave the code alone and say why in your reply.
3. For each comment that *is* real, make the change, re-run the quality/test/orphaned-reference steps from sections 1–3.
4. Commit. Reference the review in the body (e.g. "From Codex review on #<pr-number>") so the reason for the change is recoverable later.
5. `git push`.
6. Do **not** comment `@codex review` again after the push, and do not wait for another review: the one review requested in section 8 is the only one this skill acts on. If a later review arrives anyway (Codex's automatic reviews, if turned on for the repository, can trigger one on push), tell the user it is there and leave it for them to decide on, rather than starting another round of fixes.
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
- Codex code review is requested by default (`gh pr comment <n> --body "@codex review"`) and requires the ChatGPT Codex Connector GitHub app on the repository. See: https://developers.openai.com/codex/integrations/github
- GitHub Copilot's review is not requested: its credits are kept for other work. Use it only if the user asks for it by name.
- Codex is requested once per PR, never again after fixes, so reviewing and fixing cannot loop. Its review is waited for automatically, by a background poll started right after the request (section 9), and its comments are addressed as soon as it lands, without asking. Its first comment is a placeholder: wait for the `codex-review-receipt` marker before treating the review as done.
- `gh` reference: https://cli.github.com/manual/gh_pr

## Exit Criteria

Done when:
1. All tests / lints / type checks pass.
2. No orphaned references remain.
3. Documentation is updated (or explicitly confirmed N/A).
4. Commits are created (a large change split into one commit per concern) and pushed.
5. The PR is marked ready for review (no longer a draft) and the review requests are verified as landed (Codex reacted to `@codex review`).
6. Codex's review has been waited for in the background and either arrived and been addressed, or not arrived within the hour (the difference stated plainly).
7. Review comments (if any) are addressed, and any judged to be false positives are answered with a reason.
8. User is notified to merge.
