---
name: squash
description: Squash a range of commits into one with a freshly drafted commit message. Use when the user requests to squash commits, combine commits, clean up commit history, or consolidate multiple commits. Accepts a range description like "all commits since I started feature X" or "last 5 commits".
---

Squash the commits described by: $ARGUMENTS

## Important Guidelines

**Default policy: Only squash local commits**

- By default, only squash commits that have NOT been pushed to the remote
- Check remote status with `git status -sb` or `git log origin/main..HEAD`
- If any commits in the range have been pushed to remote, STOP and ask the user to confirm before proceeding
- Only proceed with squashing remote commits if the user explicitly instructs you to do so
- This prevents accidentally rewriting shared history

## Steps

### 1. Resolve the base commit

Interpret `$ARGUMENTS` as a natural-language range description. Map it to a concrete git ref:
- If it mentions a branch name, use `git merge-base HEAD <branch>` to find the fork point
- If it mentions a commit message keyword, use `git log --oneline` to find the matching commit and take its parent
- If ambiguous, show the candidates and ask the user to confirm before proceeding

**Check if commits have been pushed:**
- Run `git log origin/HEAD..<base>..HEAD` (or appropriate remote branch) to check if any commits in the range exist on remote
- If any commits are already on remote, STOP and ask user: "Some of these commits have been pushed to remote. Squashing will require force push. Do you want to proceed?"
- Only continue if user explicitly confirms

### 2. Show what will be squashed

Run:
```
git log <base>..HEAD --oneline
git diff <base>..HEAD --stat
```

Display both so the user can see exactly which commits and which files are affected.

### 3. Draft a commit message

Read `git diff <base>..HEAD` (full diff) and the individual commit messages (`git log <base>..HEAD --format="%s%n%b"`). Draft a single commit message following the project conventions:

- **Headline**: fewer than 10 words, starts with a capitalized verb, no trailing period
- **Body**: one blank line after the headline, then bullet points for additional detail
- Wrap code names in backticks: `` `TypeRegistry` ``, `` `src/types.rs` ``
- Most important information first
- Avoid vague verbs: do not use "refactor", "enhance", or "improve" unless nothing more precise fits

### 4. Confirm before acting

Present:
1. The list of commits to be squashed (from step 2)
2. The drafted commit message

Ask the user to approve or edit the message. Do not proceed until confirmed.

### 5. Squash

```
git reset --soft <base>
git commit -m "<confirmed message>"
```

Use a heredoc to preserve formatting in the commit message.

### 6. Warn about force push if needed

Check whether the current branch tracks a remote (`git status -sb`). If it does, warn:
> This branch has already been pushed. You will need `git push --force` to update the remote. Confirm before pushing.
