---
name: merge-cp
description: Merge a checkpoint branch (created by the make-checkpoint skill and possibly revised by the revise skill, e.g. checkpoints/cp-YYMMDD) back into main. Resolves merge conflicts, then forward-applies any new coding convention or optimization the checkpoint branch introduced to the commits that landed on main in parallel while the checkpoint branch was in review, so the merged codebase is consistent everywhere instead of only on the files the checkpoint branch happened to touch. Use when the user asks to merge a checkpoint branch, merge a checkpoint back to main, reconcile a checkpoint branch with main, or land checkpoint review feedback into main.
---

# Merge Checkpoint Branch

Merge a `checkpoints/cp-*` branch into `main`, then retroactively sweep the checkpoint's conventions and optimizations across whatever else landed on `main` while the checkpoint was in review.

## Why this differs from `merge-pr`

`merge-pr` merges an ordinary feature branch and assumes both sides are otherwise compatible — it resolves textual conflicts and stops. A checkpoint branch is different: it exists purely for manual review, and while it sits in review, `main` keeps moving via unrelated PRs that never saw whatever conventions or fixes the checkpoint's `revise` cycle established. A plain `git merge` reconciles text but leaves those parallel commits stylistically and structurally behind. `merge-cp` treats the checkpoint branch as the source of a **convention/optimization delta** that must be swept across the *entire* post-fork history of `main`, not just the files the checkpoint branch itself edited.

Conflict resolution and the format/test/lint verification loop below are mechanically the same as in `merge-pr` — read that skill's Steps 3–5 for the full walkthrough if a conflict or a failing check needs more detail than is repeated here.

## Step 0: Detect project type and tooling

Same detection as `merge-pr`: `Cargo.toml` → Rust, `pyproject.toml` → Python (uv/Poetry/Hatch/pip by lockfile/config), both → mixed. Prefer repo-provided wrapper scripts (`format.py`, `type_check.py`, `runtest.py`, a `justfile`, a `Makefile` target) over raw tool invocations — they encode the project's authoritative gate. If this repo's `CLAUDE.md` documents the toolchain, that documentation wins over guessing from files.

## Step 1: Identify the checkpoint branch, fork point, and the two commit sets

Resolve the checkpoint branch: the current branch if it matches `checkpoints/cp-*`, otherwise ask which one.

```bash
git fetch origin
fork=$(git merge-base <checkpoint-branch> main)
git log --oneline "$fork"..<checkpoint-branch>   # cp_commits: what the checkpoint branch did
git log --oneline "$fork"..main                  # main_commits: what landed on main in parallel
```

If `main_commits` is empty, there is nothing to forward-apply — skip straight to Step 3 (merge) and Step 5 (verify); Step 4's sweep has no target.

If `main_commits` is non-empty, note every file it touches — that's the sweep surface for Step 4:

```bash
git diff --name-only "$fork"..main
```

## Step 2: Extract the convention/optimization delta from the checkpoint branch

Read, in priority order, to build a concrete list of rules:

1. **`checkpoints/cp-*/revision.md` on the checkpoint branch.** This is the authoritative, purpose-written record — `revise` populates it with exactly which convention was applied, why, and to which files. Trust it over re-deriving from the raw diff.
2. **Diff of `CLAUDE.md` / `docs/*.md` between `$fork` and the checkpoint tip.** Any new bullet or rule here is a convention that should hold everywhere from this point on, including files the checkpoint branch never touched.
3. **Diff of source files between `$fork` and the checkpoint tip, for hunks `revision.md` doesn't already explain.** Distinguish two kinds:
   - **Convention (mechanical/style) deltas** — the same small transformation repeated across otherwise-unrelated files (import grouping, renaming a helper, adopting a new error-handling idiom). These are grep-able: you can state a before/after pattern precisely.
   - **Optimization/fix deltas** — a localized logic change that does the same job faster, more correctly, or more idiomatically in one place. These require reading the new code on `main`'s side and judging whether the same shape recurs there, not pattern-matching text.

For each extracted rule, write down three things before touching any file:
- **Rule**: before pattern → after pattern, stated concretely enough to recognize elsewhere (e.g. "multiple single-item `use` statements from the same module at one brace level → merged into one `use module::{a, b};`").
- **Why**: quote the `revision.md` rationale if there is one.
- **Boundary**: the condition under which the rule does *not* apply (e.g. "unless merging would nest a path of 2+ segments inside the braces").

This checklist is the input to Step 4 — nothing gets applied yet.

## Step 3: Merge

```bash
git checkout main
git pull origin main
git merge --no-ff <checkpoint-branch>
```

If conflicts occur, resolve them the same way as `merge-pr` Step 3: read the conflict markers, understand both sides, apply the correct resolution with Edit (never blindly accept one side), `git add`, `git commit --no-edit`. Never `git merge --abort` unless explicitly asked.

## Step 4: Sweep `main_commits`' files for the convention/optimization delta

This is the step `merge-pr` doesn't have. Work from the file list gathered in Step 1, minus any file the checkpoint branch's own commits already fixed (those are already consistent post-merge).

**For convention deltas:** grep each candidate file for the "before" pattern from Step 2 and apply the "after" pattern with Edit, respecting the boundary condition. Because these rules are mechanical, batch them — don't re-derive the rule per file.

**For optimization/fix deltas:** read each remaining file's relevant section and judge whether it reproduces the shape the checkpoint fixed (duplicated algorithm, same bug pattern, same avoidable allocation/clone). Apply the equivalent fix. If a file's logic is different enough that the fix doesn't obviously transfer, leave it and note why in the merge notes (Step 6) rather than forcing a fit.

If Step 2 found no rules that apply to any file in the sweep surface (the checkpoint's changes were purely local to files it already touched), say so explicitly rather than silently skipping — this step should always produce either applied fixes or a stated reason there was nothing to apply.

## Step 5: Format and verify

Run the repo's formatter, then its full test/build/lint suite (same tables as `merge-pr` Steps 4–5: `cargo fmt`/`cargo test`/`cargo clippy` for Rust, the repo's wrapper scripts or `ruff`/`pytest`/`pyright` for Python, both for mixed). Fix anything that breaks — including anything broken by Step 4's sweep — and re-run until clean. Commit fixes separately from the merge commit.

## Step 6: Record what was forward-applied

If the repo has a `checkpoints/` directory, write (or append to) `checkpoints/cp-<timestamp>/merge-notes.md` documenting:
- Which commits from `main_commits` existed in parallel (list, with hashes).
- Each convention/optimization rule extracted in Step 2, and which of those parallel files it was applied to.
- Any file where a rule plausibly applied but wasn't forward-ported, and why.

This is the audit trail for a judgment call, not a mechanical merge — without it, a future reviewer can't tell whether inconsistency was intentional or missed. Commit this file together with the sweep's fixes.

If the repo also uses per-checkpoint changelogs (`checkpoints/cp-*/changelog-after-*.md`, see `make-checkpoint`), leave those alone — they track work *after* a checkpoint, not the reconciliation this skill performs.

## Step 7: Push

```bash
git push origin main
```

Confirm with the user before pushing, as with any push to a shared branch.

## Step 8: Branch cleanup (optional)

Ask before deleting the checkpoint branch locally and/or on the remote — checkpoint branches are sometimes kept for historical review reference. Don't assume.

## Error handling

- **Merge conflicts too complex to resolve confidently**: ask the user rather than guessing.
- **A convention rule from Step 2 is ambiguous** (e.g. `revision.md` names a pattern but the boundary condition is unclear from a single example): apply it to the unambiguous cases, flag the ambiguous ones in the merge notes instead of guessing.
- **Verification fails after the sweep**: fix in the code, not by reverting the sweep — a broken forward-applied fix is a bug in the fix, not a reason to skip consistency.
- **No previous checkpoint / first checkpoint on this branch**: `main_commits` is just "everything on main since the checkpoint branch was created" — same procedure, no special case.

## Example

Checkpoint branch `checkpoints/cp-260714` forked from `main` at commit `F`. While it sat in review, `revise` landed one commit on the checkpoint branch establishing a new `use`-import-merging convention (documented in `CLAUDE.md` and applied to the handful of files the checkpoint branch touched), and separately six unrelated PRs merged into `main` adding several new Rust modules that never saw that convention. `merge-cp` merges the checkpoint branch into `main`, then greps the six PRs' new files for the same same-module multi-`use` pattern the convention describes and merges those too — so the convention holds across the whole codebase, not just the files the checkpoint branch happened to edit — and records exactly which files were swept in `checkpoints/cp-260714/merge-notes.md`.
