---
name: make-cp
description: Make a review checkpoint after a period of development. Creates the branch checkpoints/cp-YYMMDD in its own worktree, studies what changed since the last checkpoint, checks it against the concerns the user raised in past reviews, and writes one review.md with the problems found and numbered places to look, plus an x_review_comments.md outline for the user's comments. Use when the user asks to make or create a checkpoint, or to start a periodic review.
---

# Make Checkpoint

A checkpoint starts a review cycle:

1. This skill makes the branch, the worktree and `checkpoints/cp-YYMMDD/review.md`. The commit that adds `review.md` goes on the default branch too, so that development can go on there after it while the review runs.
2. The user reads the code, asks questions, and writes comments in `x_review_comments.md` (gitignored), under headings such as `General Comments - Round 1` or `Comments on Tests - Priority 3`.
3. `/revise` applies one section of comments at a time.
4. `/merge-cp` brings the branch back into the default branch.

`review.md` is a guide for a human reviewer. Write it for that reader: what to look at and why. Leave out generic checklists, project overviews and anything `git log` already shows well.

## 1. Find the range

- Date: `YYMMDD` of today, unless the user gives one. If `checkpoints/cp-<date>/` or the branch already exists, ask.
- Previous checkpoint: the newest `checkpoints/cp-*/` on the default branch. The commit that added it is the start of the range:

  ```bash
  prev=$(ls -d checkpoints/cp-* 2>/dev/null | sort | tail -1)
  start=$(git log --diff-filter=A --format=%H -- "$prev" | tail -1)
  git log --oneline "$start"..<default-branch>
  ```

  Commits in that range that came from the previous checkpoint branch (its revisions and its merge) were already reviewed. List them apart from the new work.
- No previous checkpoint: the range is the whole history.
- If an older `checkpoints/cp-*` branch is not merged yet (`git branch -a --no-merged <default-branch>`), tell the user and ask whether to go on.

## 2. Make the branch and the worktree

```bash
git fetch origin
git worktree add .worktrees/cp-<date> -b checkpoints/cp-<date> origin/<default-branch>
cd .worktrees/cp-<date> && git submodule update --init
```

If `.worktrees/` or `x_*` is not in `.gitignore`, add it in the checkpoint commit. Do all later steps inside the worktree.

## 3. Learn what this user flags

Read what the user asked for in earlier reviews of this project:

- `checkpoints/cp-*/revision*.md` (the "comments" part of each)
- `checkpoints/cp-*/merge-notes.md` (the rules that were swept across the code)
- any `x_review_comments.md` still present in the repo or in `.worktrees/*/`
- the rules in `CLAUDE.md`

Reduce them to the 5 to 10 kinds of problem that come back. Typical ones are names that carry no information, terms used in different ways, files or modules that are too large or at the wrong level, tests that call private helpers or are named badly, docs that are out of date or in the wrong file, and text that breaks the project's writing rules. If the project has no review history, use `CLAUDE.md` and that typical list.

## 4. Study the change

- `git diff --stat "$start"..HEAD` and the commit list. Read in full the files that changed most and the files that are new.
- Run the project's gate (the check and test commands in `CLAUDE.md`) and note the result.
- Check each concern from step 3 against the new code and docs.
- Look for real defects in the new code: wrong behavior, missing error handling, docs that say something the code does not do, tests that would not fail if the code broke (the code under test is mocked, the mock returns the expected value, or nothing is asserted).

Do not fix anything at this step. The user decides what gets fixed.

## 5. Write `checkpoints/cp-<date>/review.md`

Use this layout. Always use full paths from the repo root, never a bare file name.

```markdown
# Checkpoint cp-<date>

Range: `<start-short>..<head-short>` (<n> commits, <m> files). Previous: cp-<prev>.
Checks: <gate commands> pass | <what fails>.

## What changed

5 to 10 bullets, one for each area of work, with PR numbers where there are some.
Then one line for the already-reviewed revisions of cp-<prev>, if any.

## Problems found

F1. `path/to/file.rs:120`: what is wrong, why it matters, suggested fix.
F2. ...

## Past concerns, checked again

- <concern>: what was found, with paths, or "none found".

## Where to look

### Code - Priority 1: <area>

Why: <the risk, from this cycle's changes>.
Files: `full/path/a.rs`, `full/path/b.rs`.
Questions: 2 to 4 specific questions a reader should be able to answer after reading these files.

### Code - Priority 2: ...

### Docs - Priority 1: ...

### Tests - Priority 1: ...
```

Rules:

- **Problems found** holds only problems you checked against the code. Each names a place, says what is wrong and suggests a fix. A suspicion that you could not confirm is a question under a priority, not a problem.
- At most 5 priorities for each of Code, Docs and Tests, highest risk first. Leave out an area that has nothing worth reading. The user refers to them by these exact headings ("Tests - Priority 3"), so keep the numbering stable once written.
- Questions are specific to this code ("Does `Session::reset` drop the preedit before the commit text is sent?"), never generic ("Is error handling adequate?").
- Keep the whole file short enough to read in about ten minutes.

## 6. Write the comment outline

If `x_review_comments.md` does not exist in the worktree, create it with an empty heading for each item of `review.md`:

```markdown
# Review on Checkpoint cp-<date>

## General Comments - Round 1

## Comments on Problems Found

## Comments on Code - Priority 1
...
## Comments on Docs - Priority 1
...
## Comments on Tests - Priority 1
...
```

Do not commit it. It is the user's file.

## 7. Commit, push and report

```bash
git add checkpoints/cp-<date>/review.md .gitignore
git commit -m "Add checkpoint cp-<date>"
git fetch origin
```

The checkpoint commit is the first commit of the branch and also goes on the default branch. The next checkpoint finds its range from this commit (step 1), and `/merge-cp` finds the parallel work from it.

- If `origin/<default-branch>` did not move since step 2, the push below is a fast-forward.
- If it moved, run `git rebase origin/<default-branch>` (the branch has only this one commit, and it is not pushed yet). The new commits on the default branch were not studied. Extend the `Range:` line of `review.md` to the new head, list those commits under "What changed" as "landed during the review, not studied", amend the commit, and tell the user.

```bash
git push origin HEAD:<default-branch>       # fast-forward only, never --force
git push -u origin checkpoints/cp-<date>
git -C <main checkout> merge --ff-only origin/<default-branch>   # skip if it has local changes or another branch
```

If the push to the default branch fails because the branch moved again, fetch and rebase again. Never merge the default branch into the checkpoint branch at this step.

Tell the user the worktree path, the path of `review.md`, the problems found (one line each), and the priority headings.

## Older checkpoints

Checkpoints made before this format have `status-quo.md`, `diff-vs-*.md`, `*-guidelines.md` and `changelog-after-*.md` instead of `review.md`. Leave them as they are. Read them only for step 3. The range always comes from Git.
