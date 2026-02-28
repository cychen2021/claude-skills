---
name: commit
description: Create a git commit following project commit message conventions, with full support for repositories using git submodules. Handles submodule changes before parent repository commits. Use when the user requests to commit changes, create a commit, or save work to git.
---

Create a git commit following this project's conventions. Handles both regular repositories and repositories with git submodules.

## Steps

### 1. Check for submodules

First, check if the repository has submodules by running:
```bash
test -f .gitmodules && cat .gitmodules || echo "No submodules"
```

If `.gitmodules` exists, check each submodule for uncommitted changes:

For each submodule path listed in `.gitmodules`:
- Run `cd <submodule-path> && git status --short && cd -`
- If output is non-empty, the submodule has uncommitted changes

If submodules are detected with changes:
- Show the user which submodules have changes
- For each submodule with changes:
  - `cd` into the submodule directory
  - Run `git status` to show the changes
  - Ask if the user wants to commit those changes now
  - If yes, follow steps 2-4 below **within the submodule**
  - Return to the parent directory with `cd -`
- After handling all submodule commits, continue to step 2 for the parent repository

### 2. Review staged changes

Run `git diff --staged` to review what is staged. If nothing is staged, run `git status` and ask which changes to include before proceeding.

**Note**: After committing in submodules, the parent repository will show the submodule path as a staged change (the new commit hash). This is expected and should be included in the parent commit.

### 3. Draft commit message

Draft a commit message using the rules below.

### 4. Confirm and commit

Show the draft to the user and ask for confirmation before committing.

### 5. Execute commit

Run `git commit` using a heredoc to preserve formatting.

## Commit message rules

**Headline** (required):
- Fewer than 10 words
- Starts with a capitalized verb (Add, Fix, Remove, Move, Rename, Update, Extract, ...)
- No trailing period
- Avoid vague verbs: do not use "refactor", "enhance", or "improve" unless nothing more precise fits

**Body** (when changes need explanation):
- One blank line after the headline
- Bullet points only — each is either a complete sentence or matches the grammatical structure of the headline
- Most important information first
- Wrap code names in backticks: `` `TypeRegistry` ``, `` `src/types.rs` ``
- For moves/renames be precise: say "move X from A to B", not "delete X from A, add X to B"

**Minor changes**: a one-line headline is sufficient; no body needed.

**Submodule updates**: When committing submodule pointer updates in the parent repository, mention what changed in the submodule:
- Good: `Update vendor/lib submodule with security fixes`
- Good: `Update third-party/parser submodule to v2.1.0`
- Avoid: `Update submodule` (too vague)

## Examples

```
Add `TypedSemanticAnalyzer` for Phase 2 type checking

- Introduce `TypedSemanticAnalyzer` in `src/semantic.rs`
- Add `parse_and_type_check` to the public API in `src/lib.rs`
- Cover all new code paths with unit tests
```

```
Fix arity mismatch error message to include predicate name
```

**Submodule update example:**

```
Update vendor/ui-lib submodule to v3.2.1

- Includes new Button component variants
- Fixes accessibility issues in Modal component
- Updates TypeScript definitions
```
