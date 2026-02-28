---
name: commit
description: Create a git commit following verifuzz commit message conventions. Use when the user requests to commit changes, create a commit, or save work to git.
---

Create a git commit following this project's conventions.

## Steps

1. Run `git diff --staged` to review what is staged. If nothing is staged, run `git status` and ask which changes to include before proceeding.
2. Draft a commit message using the rules below.
3. Show the draft to the user and ask for confirmation before committing.
4. Run `git commit` using a heredoc to preserve formatting.

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
