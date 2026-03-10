---
name: revise
description: Apply post-checkpoint review feedback to codebase and documentation. Use this skill after the user has completed manual review of checkpoint guidelines and provided revision instructions. Trigger when the user says "revise based on checkpoint feedback", "apply review feedback", "implement checkpoint changes", "/revise", or indicates they've finished reviewing and want changes applied. The skill reads marked review guidelines, applies requested modifications, runs verification checks, creates a revision summary, and commits all changes.
---

# Revise

Apply post-checkpoint review feedback to update documentation and code based on user review.

## Overview

This skill is used after the user has completed manual review of checkpoint guidelines and provided specific revision instructions. It:

1. Reads completed review items from checkpoint review guidelines
2. Reads revision instructions from `x_review_comments.md`
3. Applies modifications to docs and code
4. Runs full verification (formatting, tests, build)
5. Creates a revision summary document
6. Commits all changes

## Workflow

### Step 1: Locate Checkpoint and Review Files

Find the latest checkpoint directory and review files:

```bash
# Find the latest checkpoint (format: cp-YYMMDD)
latest_checkpoint=$(ls -1d checkpoints/cp-* | sort -r | head -n1)
```

The required files:
- `$latest_checkpoint/code-review-guidelines.md` - Code review checklist with marked items
- `$latest_checkpoint/doc-review-guidelines.md` - Documentation review checklist with marked items
- `x_review_comments.md` (repo root) - Specific revision instructions from the user

### Step 2: Read Review Files

Read all three files to understand:
- What the user has reviewed and approved (checked items in guidelines)
- What specific changes are requested (`x_review_comments.md`)

### Step 3: Apply Modifications

Based on the user's instructions in `x_review_comments.md`, apply all requested changes:

**Documentation updates:**
- Fix typos, grammar, clarity issues
- Add missing examples or explanations
- Update outdated information
- Improve structure and organization

**Code modifications:**
- Refactor code (rename functions, restructure modules)
- Fix bugs or code quality issues
- Add missing documentation comments
- Improve naming or code clarity
- Extract helpers or remove duplication

Work through each item systematically, making the changes as specified by the user.

### Step 4: Run Verification Checks

After all modifications are complete, run the full verification sequence:

```bash
# Apply compiler-suggested fixes and format code
cargo fix --allow-dirty && cargo fmt

# Run the full test suite
cargo test

# Check for clippy warnings (optional but recommended)
cargo clippy -- -D warnings
```

If any checks fail:
- Fix the issues immediately
- Re-run the checks to ensure they pass
- Do not proceed until all verification passes

### Step 5: Create Revision Summary

Create a `revision.md` file in the latest checkpoint directory that documents:

1. **User's Comments** - Summary of what the user identified during review (from the marked items in review guidelines)
2. **Required Changes** - What the user requested to be modified (from `x_review_comments.md`)
3. **Modifications Made** - Detailed description of all changes applied, organized by:
   - Documentation changes (file-by-file)
   - Code changes (file-by-file or module-by-module)

**Format for `revision.md`:**

```markdown
# Revision Summary for Checkpoint cp-YYMMDD

**Date**: YYYY-MM-DD

## User's Review Comments

[Summarize what the user identified as needing attention from the review guidelines]

- Documentation issues: [list]
- Code issues: [list]

## Required Changes

[Summarize the specific changes requested in x_review_comments.md]

## Modifications Made

### Documentation Changes

#### `docs/file1.md`
- [Change 1]
- [Change 2]

#### `docs/file2.md`
- [Change 1]

### Code Changes

#### `src/module1.rs`
- [Change 1]
- [Change 2]

#### `src/module2.rs`
- [Change 1]

## Verification

- ✅ `cargo fix --allow-dirty` - passed
- ✅ `cargo fmt` - passed
- ✅ `cargo test` - all tests passed
- ✅ `cargo clippy` - no warnings

## Summary

[Brief overall summary of the revision process and outcomes]
```

Save this file as `$latest_checkpoint/revision.md`.

### Step 6: Commit Changes

Create commits for the changes:

**Commit 1: Code and documentation revisions**

```bash
# Stage all modified documentation and code files
git add docs/ src/ Cargo.toml  # Adjust as needed based on actual changes

# Create commit with descriptive message
git commit -m "$(cat <<'EOF'
Apply checkpoint cp-YYMMDD review feedback

- Fix [specific doc issues]
- Refactor [specific code changes]
- [Other major changes]

Addresses feedback from manual review of checkpoint cp-YYMMDD.
All verification checks passed (cargo fix, fmt, test, clippy).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**Commit 2: Revision summary**

```bash
# Stage the revision summary
git add checkpoints/cp-YYMMDD/revision.md

# Create commit
git commit -m "$(cat <<'EOF'
Add revision summary for checkpoint cp-YYMMDD

Documents user's review comments, required changes, and all
modifications made in response to checkpoint feedback.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 7: Create Empty Changelog File

Create an empty changelog file for future development work after this revision:

```bash
# Extract checkpoint date from latest_checkpoint
cp_date=$(basename "$latest_checkpoint" | sed 's/cp-//')

# Create empty changelog file
cat > "$latest_checkpoint/changelog-after-$cp_date.md" << 'EOF'
# Changelog After Checkpoint cp-YYMMDD

**Note:** Replace YYMMDD with the actual checkpoint date.

This file tracks all changes made after the checkpoint revision. Document changes as they happen:

## Features

-

## Bug Fixes

-

## Refactorings

-

## Documentation Updates

-

## Dependency Changes

-

## Breaking Changes

-
EOF
```

**Commit the empty changelog:**

```bash
# Stage the changelog file
git add "$latest_checkpoint/changelog-after-$cp_date.md"

# Create commit
git commit -m "$(cat <<'EOF'
Create empty changelog for post-revision development

This changelog will track all changes made after checkpoint cp-YYMMDD
revision until the next checkpoint is created.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 8: Report Completion

Provide a summary to the user:

```
✅ Revision complete for checkpoint cp-YYMMDD

Changes applied:
- [Summary of doc changes]
- [Summary of code changes]

Verification:
- ✅ cargo fix --allow-dirty
- ✅ cargo fmt
- ✅ cargo test (all passed)
- ✅ cargo clippy (no warnings)

Commits created:
- [commit hash] Apply checkpoint cp-YYMMDD review feedback
- [commit hash] Add revision summary for checkpoint cp-YYMMDD
- [commit hash] Create empty changelog for post-revision development

Files created:
- checkpoints/cp-YYMMDD/revision.md - Complete revision summary
- checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md - Empty changelog for future changes

📝 Next Steps:
As you continue development after this revision, document all changes in:
  checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md

This changelog should be updated as you make changes:
- New features implemented
- Bug fixes
- Refactorings
- Documentation updates
- Dependency changes
- Breaking changes

This changelog will be referenced when creating the next checkpoint.
```

## Important Notes

- **Always read all three files** before making changes (both review guidelines + x_review_comments.md)
- **Make all changes requested** - don't skip items unless explicitly told by the user
- **Run all verification checks** - do not commit if checks fail
- **Be thorough in the revision summary** - document every significant change made
- **Create three commits** - one for the actual changes, one for the revision summary document, one for the empty changelog
- **Create empty changelog** - always create the empty changelog file after revision to prepare for future development
- **Check for x_review_comments.md** - if this file doesn't exist, ask the user to create it with their revision instructions

## Error Handling

If any issues occur during the process:

- **Missing files**: Ask the user to provide the missing file(s)
- **Test failures**: Fix the issues and re-run tests before proceeding
- **Unclear instructions**: Ask the user for clarification before making changes
- **Conflicting changes**: Ask the user how to resolve conflicts

## Example Usage

**User**: "I've finished reviewing checkpoint cp-260218. Please revise the code and docs."

**Claude**:
1. Locates `checkpoints/cp-260218/`
2. Reads `code-review-guidelines.md` and `doc-review-guidelines.md`
3. Reads `x_review_comments.md` from repo root
4. Applies all requested modifications
5. Runs `cargo fix`, `cargo fmt`, `cargo test`, `cargo clippy`
6. Creates `checkpoints/cp-260218/revision.md`
7. Creates `checkpoints/cp-260218/changelog-after-260218.md` (empty template)
8. Creates three commits (changes, revision summary, empty changelog)
9. Reports completion with summary
