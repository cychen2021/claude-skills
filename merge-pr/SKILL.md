---
name: merge-pr
description: Merge a pull request into the default branch with a merge commit (no squash, no rebase). Accepts a PR number, a branch name, or the current branch. Brings the default branch into the PR branch first, resolves conflicts, runs the project's checks, fixes what fails, merges through GitHub and deletes the merged branch. Use only when the user asks to merge a PR or a branch. Never start it on your own.
---

# Merge PR

## 1. Find the PR

- A number (`#123`): `gh pr view 123 --json number,headRefName,baseRefName,state,isDraft`.
- A branch name: `gh pr list --head <branch> --json number`.
- Nothing: the current branch and its PR.

If there is no PR (for example a repo without a GitHub remote), merge locally as in step 5. If the PR is a draft or its checks are failing, tell the user and ask before going on.

## 2. Bring the default branch into the PR branch

```bash
git fetch origin
git checkout <branch> && git pull
git merge origin/<default>
```

Resolve each conflict by reading both sides and keeping the intent of both. Never take one side blindly, and never abort the merge unless the user asks. Ask the user when a conflict is too unclear to resolve with confidence.

## 3. Check

Run the project's gate: the format, check and test commands its `CLAUDE.md` names (for example `format.py`, `type_check.py`, `runtest.py`). If it names none, use the usual formatter, linter, type checker and test runner of the language. Fix what fails, in the merged code, one commit per fix, and run the gate again until it passes. Push the branch.

## 4. Merge

```bash
gh pr merge <number> --merge --delete-branch
git checkout <default> && git pull
git branch -d <branch> 2>/dev/null
```

If branch protection blocks the merge, tell the user. Do not use `--admin` unless they say so. If the PR has a Codex review still running after 30 minutes, do not wait for it.

## 5. Without a PR

```bash
git checkout <default> && git pull
git merge --no-ff <branch>
```

Run the gate as in step 3, then ask before pushing the default branch. Delete the merged branch locally and on the remote after the push.

## 6. Report

Say what was merged (PR number and merge commit), the conflicts and how they were resolved, the fixes made after the merge, and the gate results.
