---
name: make-cp
description: Make a review checkpoint after a period of development. Creates the branch checkpoints/cp-YYMMDD in its own worktree, studies what changed since the last checkpoint, checks it against the concerns the user raised in past reviews, and writes one review.md with the problems that need the user's decision, the minor problems it can fix after approval, and the few high-level matters the user must look at, plus an x_review_comments.md outline for the user's comments. Use when the user asks to make or create a checkpoint, or to start a periodic review.
---

# Make Checkpoint

A checkpoint starts a review cycle:

1. This skill makes the branch, the worktree and `checkpoints/cp-YYMMDD/review.md`. The commit that adds `review.md` goes on the default branch too, so that development can go on there after it while the review runs.
2. The user reads the code, asks questions, and writes comments in `x_review_comments.md` (gitignored), under headings such as `General Comments - Round 1`, `Comments on Minor Problems` or `Comments on Where to Look - 2`.
3. `/revise` applies one section of comments at a time.
4. `/merge-cp` brings the branch back into the default branch.

`review.md` is for a reviewer with little time. The user does not audit the code line by line. Do that work yourself, and give the user only:

- the problems that need their decision,
- a list of minor problems that you fix after one approval,
- the checks that you could not run yourself, with the steps to run them,
- the few high-level matters that only they can decide.

Leave out generic checklists, project overviews and anything `git log` already shows well.

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
- `checkpoints/cp-*/review-comments.md` (the user's own comments, archived at each merge)
- any `x_review_comments.md` still present in the repo or in `.worktrees/*/`
- the rules in `CLAUDE.md`

Reduce them to the 5 to 10 kinds of problem that come back. Typical ones are names that carry no information, terms used in different ways, files or modules that are too large or at the wrong level, tests that call private helpers or are named badly, docs that are out of date or in the wrong file, and text that breaks the project's writing rules. If the project has no review history, use `CLAUDE.md` and that typical list.

## 4. Study the change

- `git diff --stat "$start"..HEAD` and the commit list. Read in full the files that changed most and the files that are new.
- Run the project's gate (the check and test commands in `CLAUDE.md`) and note the result.
- Check each concern from step 3 against the new code and docs.
- Look for real defects in the new code: wrong behavior, missing error handling, docs that say something the code does not do, tests that would not fail if the code broke (the code under test is mocked, the mock returns the expected value, or nothing is asserted).
- Answer your own detail questions. A question such as "does this handler run twice when the event comes twice?" is your work, not the user's. Read the code and its callers, read the docs of the library or system it calls, compare with a reference implementation if the project names one, write a throwaway test or run the program. If the answer shows a defect, it is a problem (step 5). If it does not, drop the question. If you cannot settle it (it needs a platform, a device, an account or a service that you cannot use), it goes to "Needs your check" (step 5).
- Look for the high-level matters: the architecture and the split between components, public interfaces (wire protocol, CLI, config format, file locations), project layout, conventions that touch many files, a growing area with no clear owner or design, and plan items that the code now depends on. These go to "Where to look".

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

These need your decision.

F1. `path/to/file.rs:120`: what is wrong, why it matters. Options: (a) ..., (b) .... Recommended: (a), because ....
F2. ...

## Minor problems

I fix these after your approval ("approve all", or the numbers to skip or change).

- M1. `path/to/file.rs:40`: what is wrong. Fix: ....
- M2. ...

## Needs your check

I could not settle these. Each needs a run on your side.

C1. `path/to/file.rs:80`: what may be wrong, and why it matters if it is. Check: the exact steps (platform, commands, what to type or click). A problem if: the result that shows the defect. Then: what I would fix.
C2. ...

## Past concerns, checked again

- <concern>: what was found (as F, M or C numbers), or "none found".

## Where to look

### Where to Look - 1: <matter>

What: the decision or the direction in question, in two or three sentences.
Why now: what in this cycle makes it matter (growth, a new platform, a second copy of the same code, a plan item).
Options: the realistic choices, each with its cost. Recommended: one of them, and why.
Scope: the components or the number of files it touches. Entry points: `full/path/a.rs`, `docs/x.md`.

### Where to Look - 2: ...
```

Rules:

- **Problems found** and **Minor problems** hold only problems you checked against the code, each at a named place. A suspicion that you could not confirm and could not rule out goes to **Needs your check**, with steps that the user can follow without reading the code. A suspicion that you ruled out is not in the file. Leave out the section if it is empty.
- A problem is **minor** if it has one obvious fix and the fix changes no behavior that users see and no public interface: stale or wrong comments and docs, rule breaks (names, imports, writing rules), small bugs with a clear fix, duplicated code with one obvious home, missing tests for existing behavior. Write each in one line.
- A problem goes to **Problems found** if the fix changes what users see, changes a public interface (protocol, CLI, config keys, file locations), needs a choice between options, or is large. Give the options and recommend one.
- **Where to look** has 2 to 6 high-level matters, most important first. Each is something only the user can decide: technical (architecture, the split between components, a protocol or format, a dependency) or not (a convention or a layout that touches many files, naming across the project, what to do next). Never put line-level questions here. If there is nothing at this level, write "Nothing this cycle."
- The user refers to items by number ("F2", "M5", "C1", "Where to Look - 2"), so keep the numbering stable once written.
- Keep the whole file short enough to read in about ten minutes. The minor list can be long, because each item is one line.

## 6. Write the comment outline

If `x_review_comments.md` does not exist in the worktree, create it with an empty heading for each item of `review.md`. "Needs Your Check" comes before the problems, because the results of the checks can decide problems and minor problems (a check that shows a defect makes its fix a request):

```markdown
# Review on Checkpoint cp-<date>

## General Comments - Round 1

## Comments on Needs Your Check

## Comments on Problems Found

## Comments on Minor Problems

## Comments on Where to Look - 1
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

Tell the user the worktree path, the path of `review.md`, the problems found (one line each, with the recommended option), the number of minor problems, the checks that need a run on their side (one line each), and the "Where to look" matters (one line each). Say that `/revise` on "Comments on Minor Problems" fixes the minor problems after their approval.

## Older checkpoints

Checkpoints made before this format have `status-quo.md`, `diff-vs-*.md`, `*-guidelines.md` and `changelog-after-*.md` instead of `review.md`. Leave them as they are. Read them only for step 3. The range always comes from Git.
