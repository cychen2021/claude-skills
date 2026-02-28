---
name: merge-pr
description: Merge pull requests into main branch using merge commits (no squash/rebase) with intelligent conflict resolution and comprehensive verification. Use when the user explicitly requests to merge a PR, complete a merge, or finish merging a branch. The skill handles PR numbers (#123), branch names (feature/my-branch), or auto-detects the current feature branch if no input provided. Resolves conflicts interactively by analyzing code and applying correct resolutions, runs full verification suite (tests + build + clippy), and ensures code is properly formatted. Invoked manually only - never auto-trigger.
---

# Merge PR

Merge pull requests into the main branch using merge commits with intelligent conflict resolution and comprehensive post-merge verification.

## Overview

This skill handles the complete PR merge workflow:
1. Parse PR number or branch name
2. Fetch latest changes and merge with `--no-ff` (create merge commit)
3. Resolve conflicts interactively if they occur
4. Format code with `cargo fix --allow-dirty && cargo fmt`
5. Run comprehensive verification (tests, build, clippy)
6. Fix any issues found during verification
7. Complete the merge

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

Apply code formatting after merge:

```bash
cargo fix --allow-dirty && cargo fmt
```

If `cargo fix` makes changes, stage and commit them:
```bash
git add .
git commit -m "Apply cargo fix suggestions after merge"
```

### Step 5: Run Comprehensive Verification

Run all verification checks:

```bash
# Full test suite with rhai feature
cargo test --features rhai

# Build verification
cargo build --release

# Clippy checks
cargo clippy
```

### Step 6: Fix Issues (if any)

If any verification step fails:

1. **Analyze the failure**: Read error messages and identify root cause
2. **Fix the issue**: Use Edit tool to apply corrections
3. **Re-run formatting**: `cargo fix --allow-dirty && cargo fmt`
4. **Stage and commit**:
   ```bash
   git add .
   git commit -m "Fix <issue-description> after merge"
   ```
5. **Re-run verification**: Repeat Step 5 until all checks pass

### Step 7: Complete Merge

Once all verification passes:

```bash
# Push to main
git push origin main
```

Inform the user that the PR has been successfully merged.

### Step 8: Branch Cleanup (Optional)

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

### Build/Clippy Failures

- Treat as blockers - do not complete merge until resolved
- Apply fixes and re-run verification
- Ensure fixes don't introduce new issues

## Best Practices

- Always use `--no-ff` to create explicit merge commits
- Write clear commit messages for conflict resolution and fixes
- Run full verification suite - don't skip any checks
- Keep the user informed about each step's progress
- If unsure about conflict resolution, ask the user

## Example Usage

**User: "Merge PR #456"**
- Parse PR #456 to get branch name
- Fetch and merge with `--no-ff`
- Resolve any conflicts
- Format code
- Run tests, build, and clippy
- Push to main

**User: "Merge feature/add-monitors into main"**
- Use branch name directly
- Follow same workflow as above

**User: "Merge this branch" (while on feature/my-feature)**
- Auto-detect current branch (feature/my-feature)
- Check if PR exists for this branch
- Follow same workflow as above
