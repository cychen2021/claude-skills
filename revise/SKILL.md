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
3. **Creates `revision.md` with complete TODO checklist BEFORE applying changes**
4. Applies modifications to docs and code **one item at a time**, checking off each TODO item as it's completed
5. Runs full verification (formatting, tests, build)
6. Finalizes revision summary with verification results and overall summary
7. Commits all changes (code/docs + revision.md in one commit, changelog in another)

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

### Step 3: Create `revision.md` with TODO Checklist

**IMPORTANT:** Before applying any changes, create the `revision.md` file with a complete TODO checklist.

Parse the user's review comments from `x_review_comments.md` and create a structured TODO checklist:

```markdown
# Revision Summary for Checkpoint cp-YYMMDD

**Date**: YYYY-MM-DD

## User's Review Comments

[Summarize what the user identified as needing attention from the review guidelines]

- Documentation issues: [list]
- Code issues: [list]

## Required Changes

[Summarize the specific changes requested in x_review_comments.md]

## TODO Checklist

### Documentation Changes

- [ ] `docs/file1.md` - Fix [specific issue]
- [ ] `docs/file1.md` - Add [specific content]
- [ ] `docs/file2.md` - Update [specific section]

### Code Changes

- [ ] `src/module1.rs` - Refactor [specific function/code]
- [ ] `src/module1.rs` - Fix [specific bug]
- [ ] `src/module2.rs` - Improve [specific aspect]

## Modifications Made

(This section will be populated as changes are applied)

## Verification

(This section will be populated after verification checks)

## Summary

(This section will be populated after all changes are complete)
```

**Key requirements:**
- Parse each change request from `x_review_comments.md` into individual TODO items
- Use `[ ]` for unchecked items
- Group by documentation vs. code changes
- Include file path and specific change description for each item
- Keep items actionable and specific

Save this file as `$latest_checkpoint/revision.md` before proceeding to Step 4.

### Step 4: Apply Modifications with Progress Tracking

Based on the user's instructions in `x_review_comments.md`, apply all requested changes **one item at a time**, checking off each TODO item as it is completed.

**For each TODO item:**

1. Make the specific change requested
2. Update `revision.md` to mark the item as complete: change `[ ]` to `[x]`
3. Add a detailed entry under "Modifications Made" section

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

**Note:** For structural refactoring requests (code duplication, complex functions, module organization, architecture improvements), leverage the techniques and patterns documented in the `refactor-codebase` skill. While `revise` is prescriptive (follow user instructions), you can apply refactoring best practices when the user requests structural improvements.

**Progress tracking pattern:**

```bash
# After completing each change, update revision.md:
# 1. Mark TODO item as complete: [ ] → [x]
# 2. Add entry under "Modifications Made" section

# Example entry in "Modifications Made":
## Modifications Made

### Documentation Changes

#### `docs/file1.md`
- Fixed typo in section 2.3: "paramter" → "parameter"
- Added example for edge case handling in section 4.1

### Code Changes

#### `src/module1.rs`
- Refactored `process_data()` to extract helper function `validate_input()`
- Improved error messages to include context information
```

Work through each item systematically, making the changes as specified by the user and updating `revision.md` after each completion.

### Step 5: Run Verification Checks

After all modifications are complete and all TODO items are checked off, run the full verification sequence:

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

**Update `revision.md` with verification results:**

```markdown
## Verification

- ✅ `cargo fix --allow-dirty` - passed
- ✅ `cargo fmt` - passed
- ✅ `cargo test` - all tests passed (X tests, Y ignored)
- ✅ `cargo clippy` - no warnings
```

### Step 6: Finalize Revision Summary

Update the `revision.md` file (created in Step 3) with the final summary section.

At this point, the file should already contain:
- User's Review Comments (from Step 3)
- Required Changes (from Step 3)
- TODO Checklist with all items checked off (from Step 4)
- Modifications Made (populated during Step 4)
- Verification results (from Step 5)

Add the final summary section:

```markdown
## Summary

[Brief overall summary of the revision process and outcomes]

**Key accomplishments:**
- [X] items completed from TODO checklist
- All documentation updated and clarified
- All code issues addressed
- All tests passing
- No clippy warnings

**Files modified:**
- Documentation: [count] files
- Code: [count] files

The codebase is now updated based on checkpoint cp-YYMMDD review feedback.
```

### Step 7: Commit Changes

Create commits for the changes:

**Commit 1: Revision summary and changes together**

Since `revision.md` was created at the beginning and updated throughout the process, commit it together with all the code and documentation changes:

```bash
# Stage all modified files including revision.md
git add docs/ src/ Cargo.toml checkpoints/cp-YYMMDD/revision.md  # Adjust as needed based on actual changes

# Create commit with descriptive message
git commit -m "$(cat <<'EOF'
Apply checkpoint cp-YYMMDD review feedback

- Fix [specific doc issues]
- Refactor [specific code changes]
- [Other major changes]

Addresses feedback from manual review of checkpoint cp-YYMMDD.
All verification checks passed (cargo fix, fmt, test, clippy).

See checkpoints/cp-YYMMDD/revision.md for complete change log
with TODO checklist and detailed modifications.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 8: Create Empty Changelog File

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

### Step 9: Report Completion

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
  (includes code/doc changes + revision.md with complete TODO checklist)
- [commit hash] Create empty changelog for post-revision development

Files created/updated:
- checkpoints/cp-YYMMDD/revision.md - Complete revision summary with TODO checklist
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
- **Create revision.md FIRST** - before applying any changes, create the revision.md file with complete TODO checklist
- **Track progress in real-time** - update revision.md as each TODO item is completed, marking `[ ]` → `[x]`
- **Make all changes requested** - don't skip items unless explicitly told by the user
- **Run all verification checks** - do not commit if checks fail
- **Be thorough in the revision summary** - document every significant change made in the "Modifications Made" section
- **Create two commits** - one for the actual changes + revision.md (which was being updated throughout), one for the empty changelog
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
4. **Creates `checkpoints/cp-260218/revision.md` with complete TODO checklist** (all items unchecked `[ ]`)
5. Applies requested modifications one by one, updating `revision.md` after each:
   - Marks TODO item as complete: `[ ]` → `[x]`
   - Adds detailed entry to "Modifications Made" section
6. Runs `cargo fix`, `cargo fmt`, `cargo test`, `cargo clippy`
7. Updates `revision.md` with verification results and final summary
8. Creates `checkpoints/cp-260218/changelog-after-260218.md` (empty template)
9. Creates two commits (changes + revision.md, then empty changelog)
10. Reports completion with summary
