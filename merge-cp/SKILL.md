---
name: merge-cp
description: Merge a checkpoint branch (checkpoints/cp-YYMMDD, made by make-cp and changed by revise) back into the default branch. Merges the default branch into the checkpoint branch first, applies the rules the review set to the code that landed in parallel, runs the checks, writes merge-notes.md, merges the branch into the default branch with a merge commit (no PR), brings any newer checkpoint branch up to date, and cleans up. Use when the user asks to merge a checkpoint, land a checkpoint, or reconcile a checkpoint branch with main.
---

# Merge Checkpoint Branch

While a checkpoint branch is in review, the default branch keeps moving. A plain merge joins the text but leaves the parallel work behind the rules that the review set (new names, new conventions, fixes to a pattern). This skill also applies those rules to the parallel work, so they hold everywhere.

All the work happens on the checkpoint branch, so the default branch is never broken.

## 1. Find the branches and the two sets of commits

The checkpoint branch is the current branch if it matches `checkpoints/cp-*`. Otherwise ask which one.

```bash
git fetch origin
fork=$(git merge-base <cp-branch> origin/<default>)
git log --oneline "$fork"..<cp-branch>         # the review's commits
git log --oneline "$fork"..origin/<default>    # the parallel commits
git diff --name-only "$fork"..origin/<default> # files to sweep in step 4
```

## 2. List the rules the review set

Read, in this order:

1. `checkpoints/cp-<date>/revision*.md`: the comments and what was done for each. This is the main source.
2. The diff of `CLAUDE.md` and `docs/` from `$fork` to the checkpoint branch: any new rule there holds everywhere from now on.
3. The code diff of the checkpoint branch, for changes the revision files do not explain.

Write each rule down before you change anything:

- **Rule**: before and after, exact enough to find elsewhere (for example "`foo_helper` is now `build_config`", or "Rust modules with children use `<name>/mod.rs`").
- **Why**: from the revision file.
- **Limit**: where it does not apply.

Rules are of two kinds. Mechanical ones (renames, layout, import style) you can find with a search. Fixes to a pattern (the same bug shape, the same duplicated logic) need you to read the parallel code and judge.

## 3. Merge the default branch into the checkpoint branch

```bash
git checkout <cp-branch>
git merge origin/<default>
```

Resolve conflicts by reading both sides and keeping the intent of both, never by taking one side blindly. Ask the user when a conflict is too unclear to resolve with confidence. Do not abort the merge unless the user asks.

## 4. Apply the rules to the parallel work

Go through the files from step 1, except the ones the checkpoint branch already fixed:

- Mechanical rules: search for the "before" form, change it to the "after" form, respecting the limit. Search the whole tree for old names after a rename.
- Pattern fixes: read the code, and fix it where the same shape occurs. Where a rule seems to apply but does not fit, leave the code and note why.

If no rule applies to any parallel file, say so explicitly.

## 5. Check

Run the project's gate (the commands in `CLAUDE.md`). Fix what fails, including what the sweep broke. Fix the sweep, do not undo it. Commit the sweep apart from the merge commit.

## 6. Write `checkpoints/cp-<date>/merge-notes.md`

- The parallel commits (hash and headline).
- Each rule from step 2, and the files it was applied to.
- Places where a rule seemed to apply but was left, and why.

Commit it with the sweep.

## 7. Land the branch

Merge the checkpoint branch into the default branch with a merge commit, so the history shows where the checkpoint came in:

```bash
git checkout <default>
git merge --no-ff <cp-branch>
```

Ask the user before pushing the default branch.

Do not open a PR. The review already happened in `review.md` and the revision files.

## 8. Bring a newer checkpoint up to date

If a newer `checkpoints/cp-*` branch exists, merge the updated default branch into it (the user means the default branch with this checkpoint already merged). Then refresh that checkpoint's `review.md` (or its guidelines, for an older checkpoint) for the new code: correct paths and names that changed, mark problems that are now fixed, and add problems that the merged work brings in. Commit and push.

## 9. Clean up

- Delete the merged branch, local and remote.
- Ask before removing the worktree `.worktrees/cp-<date>`. It holds the user's gitignored `x_*` files, such as `x_review_comments.md`, which a removal deletes. Offer to copy them first.
