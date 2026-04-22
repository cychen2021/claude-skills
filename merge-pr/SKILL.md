---
name: merge-pr
description: Merge pull requests into main branch using merge commits (no squash/rebase) with intelligent conflict resolution and comprehensive verification. Use when the user explicitly requests to merge a PR, complete a merge, or finish merging a branch. The skill handles PR numbers (#123), branch names (feature/my-branch), or auto-detects the current feature branch if no input provided. Resolves conflicts interactively by analyzing code and applying correct resolutions, runs the project's full verification suite (tests, build, and lint/type-check appropriate for the detected toolchain), and ensures code is properly formatted. Works for both Rust (Cargo) and Python (uv/Poetry/Hatch/pip) projects. Invoked manually only - never auto-trigger.
---

# Merge PR

Merge pull requests into the main branch using merge commits with intelligent conflict resolution and comprehensive post-merge verification.

## Overview

This skill handles the complete PR merge workflow:
1. Detect the project type (Rust / Python / mixed).
2. Parse PR number or branch name.
3. Fetch latest changes and merge with `--no-ff` (create merge commit).
4. Resolve conflicts interactively if they occur.
5. Format code with the toolchain-appropriate formatter.
6. Run comprehensive verification (tests, build where applicable, lint/type-check).
7. Fix any issues found during verification.
8. Update the checkpoint changelog **only if** the repo uses one.
9. Push, and optionally clean up the merged branch.

## Step 0: Detect the project type

Before running any tool, identify the project type from files at the repository root. Use this detection to pick the right commands in every later step.

- **Rust (Cargo)** — `Cargo.toml` at the repo root (or at a workspace root).
- **Python** — `pyproject.toml` at the repo root. Further distinguish the workflow:
  - **uv** — `[tool.uv]`, `uv.lock`, or `build-backend = "uv_build"`.
  - **Poetry** — `[tool.poetry]` or `poetry.lock`.
  - **Hatch** — `[tool.hatch]`.
  - **pip / PEP 621 plain** — none of the above; plain `[project]` or `requirements*.txt`.
- **Mixed / polyglot** — if both `Cargo.toml` and `pyproject.toml` exist, run the verification for both.

Prefer repo-provided wrapper scripts (`format.py`, `type_check.py`, `scripts/fmt.sh`, a `justfile`, a `Makefile` target) over raw tool invocations — they encode the project's authoritative configuration.

If detection is ambiguous, ask the user which toolchain to use before proceeding.

## Workflow

### Step 1: Parse Input and Prepare

Determine which branch to merge:

**If PR number provided** (e.g., `#123` or `123`):
```bash
# Get branch name from PR
gh pr view <NUMBER> --json headRefName -q .headRefName
```

**If branch name provided** (e.g., `feature/my-branch`):
Use the branch name directly.

**If no PR/branch provided**:
```bash
# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# If not on main, use the current branch
if [ "$CURRENT_BRANCH" != "main" ]; then
  # Try to find associated PR
  gh pr list --head "$CURRENT_BRANCH" --json number -q '.[0].number'
fi
```

Use the current branch as the merge source. If a PR exists for this branch, note the PR number for reference.

### Step 2: Fetch and Merge

```bash
# Fetch latest changes
git fetch origin

# Checkout main and ensure it's up to date
git checkout main
git pull origin main

# Merge with --no-ff to create merge commit
git merge --no-ff <BRANCH_NAME>
```

### Step 3: Resolve Conflicts (if any)

If conflicts occur, resolve them interactively:

1. **Identify conflicts**:
   ```bash
   git status
   ```

2. **For each conflicted file**:
   - Read the file to see conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
   - Understand both versions of the code
   - Analyze which version is correct or how to combine them
   - Apply the correct resolution using the Edit tool
   - Stage the resolved file: `git add <file>`

3. **Continue the merge**:
   ```bash
   git commit --no-edit
   ```

**Important**: Never blindly accept one side. Always analyze the conflict context to determine the correct resolution.

### Step 4: Format Code

Apply the project's standard formatter (picked from Step 0).

| Project type | Commands |
|---|---|
| Rust (Cargo) | `cargo fix --allow-dirty --allow-staged` then `cargo fmt` |
| Python (uv, repo has `format.py` / `type_check.py` scripts) | `uv run format.py` (or `uv run python format.py`). Run any other project-provided fix scripts the same way. |
| Python (uv, no wrapper script) | `uv run ruff format .` and `uv run ruff check --fix .` if `ruff` is a dependency; otherwise `uvx ruff format .` and `uvx ruff check --fix .` |
| Python (Poetry) | `poetry run ruff format .` and `poetry run ruff check --fix .` (or `black` / `isort` if the project uses them) |
| Python (Hatch) | `hatch run fmt` / `hatch run lint` if defined; otherwise `hatch run ruff format .` and `hatch run ruff check --fix .` |
| Python (pip) | `ruff format .` / `black .` / `isort .` — whichever is configured in `pyproject.toml` |

If the formatter/fixer makes changes, stage and commit them:
```bash
git add .
git commit -m "Apply formatter/linter suggestions after merge"
```

### Step 5: Run Comprehensive Verification

Run all verification checks. Skip rows that don't apply to the detected toolchain.

| Project type | Test | Build | Lint / type-check |
|---|---|---|---|
| Rust (Cargo) | `cargo test` (or `cargo test --workspace` / `cargo test --all-features` as appropriate) | `cargo build --release` | `cargo clippy --all-targets -- -D warnings` |
| Python (uv) | `uv run pytest` | *(usually N/A — skip unless the project has a build step)* | `uv run type_check.py` (or `uv run pyright` / `uv run mypy`) |
| Python (Poetry) | `poetry run pytest` | *(N/A)* | `poetry run pyright` / `poetry run mypy` |
| Python (Hatch) | `hatch run test` or `hatch run pytest` | *(N/A)* | `hatch run type-check` / `hatch run pyright` |
| Python (pip) | `pytest` | *(N/A)* | `pyright` / `mypy` |

If the repo provides an authoritative wrapper (`/test`, `make test`, `scripts/check.sh`), prefer it.

### Step 6: Fix Issues (if any)

If any verification step fails:

1. **Analyze the failure**: Read error messages and identify root cause.
2. **Fix the issue**: Use Edit tool to apply corrections.
3. **Re-run formatting**: use the Step 4 commands for the detected toolchain.
4. **Stage and commit**:
   ```bash
   git add .
   git commit -m "Fix <issue-description> after merge"
   ```
5. **Re-run verification**: Repeat Step 5 until all checks pass.

### Step 7: Update Checkpoint Changelog (only if the repo uses one)

**Short-circuit:** if there is no `checkpoints/` directory at the repository root, **skip this step entirely** — this project does not track merges via checkpoint changelogs.

```bash
# Short-circuit check
if [ ! -d checkpoints ]; then
  echo "No checkpoints/ directory — skipping changelog update."
fi
```

**If `checkpoints/` exists**, look for an active checkpoint and its changelog:

```bash
# Find the latest checkpoint
latest_checkpoint=$(ls -1d checkpoints/cp-* 2>/dev/null | sort -r | head -n1)

# Check if changelog exists
if [ -n "$latest_checkpoint" ]; then
  changelog_file="$latest_checkpoint/changelog-after-$(basename $latest_checkpoint | sed 's/cp-//').md"
  if [ -f "$changelog_file" ]; then
    echo "Found checkpoint changelog: $changelog_file"
  fi
fi
```

**If a checkpoint changelog exists:**

1. **Read the changelog** to understand the current format and existing entries.
2. **Add or update the PR entry** with merge information:
   - Update "**Merged**" date to today's date.
   - Add "**Merge Commit**" hash from the merge commit.
   - Verify all PR information is complete.

3. **Example update:**
   ```markdown
   ### PR Information

   - **Branch**: feature/branch-name
   - **PR**: #XX
   - **Merged**: 2026-03-10  # ← Add this
   - **Merge Commit**: abc1234  # ← Add this
   ```

4. **Commit the changelog update:**
   ```bash
   git add "$changelog_file"
   git commit -m "Update checkpoint changelog with PR #XX merge information"
   ```

**If `checkpoints/` exists but no active changelog is found:** skip, and mention to the user that no active checkpoint changelog was located.

**Note:** The checkpoint-based changelog workflow is a convention used by some projects (see their `CLAUDE.md`). Projects that don't keep a `checkpoints/` directory should rely on commit messages and/or a top-level `CHANGELOG.md` (update that file if present instead).

### Step 8: Push to Main

Once all verification passes and changelog is updated:

```bash
# Push to main
git push origin main
```

Inform the user that the PR has been successfully merged.

### Step 9: Branch Cleanup (Optional)

After a successful merge, ask the user if they want to delete the merged branch:

**Local branch deletion:**
```bash
# Delete local branch (if not currently on it)
git branch -d <BRANCH_NAME>
```

**Remote branch deletion:**
```bash
# Delete remote branch
git push origin --delete <BRANCH_NAME>
```

**Important considerations:**
- **Always ask the user first** - don't assume they want the branch deleted
- Some workflows keep feature branches for historical reference
- Some teams have automated branch cleanup policies
- If the user is unsure, recommend keeping the branch until later

**Example prompt to user:**
"The PR has been successfully merged to main. Would you like me to delete the `<BRANCH_NAME>` branch (both locally and from remote)? This can help keep the repository clean, but you can also keep it for reference."

## Error Handling

### Merge Conflicts

- Never use `git merge --abort` unless explicitly requested
- Always attempt interactive resolution first
- If conflicts are too complex, ask user for guidance

### Failed Tests

- Analyze test output carefully
- Fix issues in the merged code, not in the original branches
- Create separate commits for each logical fix

### Build / Lint / Type-check Failures

- Treat as blockers — do not complete the merge until resolved.
- Apply fixes and re-run verification.
- Ensure fixes don't introduce new issues.

## Best Practices

- Always use `--no-ff` to create explicit merge commits
- Write clear commit messages for conflict resolution and fixes
- Run full verification suite - don't skip any checks
- Keep the user informed about each step's progress
- If unsure about conflict resolution, ask the user

## Example Usage

**User: "Merge PR #456"** (Rust project)
- Parse PR #456 to get the branch name.
- Detect `Cargo.toml` → use Rust commands.
- Fetch and merge with `--no-ff`.
- Resolve any conflicts.
- Format with `cargo fix --allow-dirty --allow-staged && cargo fmt`.
- Run `cargo test`, `cargo build --release`, `cargo clippy -- -D warnings`.
- Update checkpoint changelog if `checkpoints/` exists.
- Push to main.

**User: "Merge PR #123"** (Python uv project)
- Parse PR #123 to get the branch name.
- Detect `pyproject.toml` + `uv.lock` → use uv commands.
- Fetch and merge with `--no-ff`.
- Resolve any conflicts.
- Format via repo wrapper (e.g. `uv run format.py`) or `uv run ruff format . && uv run ruff check --fix .`.
- Run `uv run pytest` and `uv run type_check.py` (or `pyright`/`mypy`).
- Skip checkpoint changelog step (no `checkpoints/` directory).
- Push to main.

**User: "Merge feature/add-monitors into main"**
- Use the branch name directly.
- Follow the same workflow, picking commands from the detected toolchain.

**User: "Merge this branch"** (while on `feature/my-feature`)
- Auto-detect current branch.
- Check if a PR exists for this branch.
- Follow the same workflow.
