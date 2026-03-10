---
name: finish-feature-remove
description: Complete a feature removal in the verifuzz codebase with quality checks, testing, orphaned reference verification, documentation updates, commits, and PR creation. Runs cargo fix/fmt, executes full test suite with fixes, verifies no orphaned references remain, updates relevant documentation, creates commits, pushes to remote, creates PR via gh CLI, and manages review workflow. AUTOMATICALLY use this skill when feature removal work is complete and all todos in the removal checklist are finished, or when the user explicitly requests to "finish removal", "wrap up removal", "complete removal and create PR", or indicates the removal is ready for finalization.
---

# Finish Feature Remove

Complete a feature removal with quality checks, testing, orphaned reference verification, documentation updates, and PR workflow.

## Workflow

### 1. Pre-commit Quality Checks

**Version Verification:**

Check that version numbers are synchronized across the codebase:

```bash
# Check current version in Cargo.toml
CARGO_VERSION=$(cargo metadata --format-version 1 | jq -r '.packages[] | select(.name == "verifuzz") | .version')
echo "Cargo.toml version: $CARGO_VERSION"

# Check version in CLAUDE.md
grep -A1 "Current Version:" CLAUDE.md
```

Verify synchronization:
- [ ] Version in `Cargo.toml` matches "Current Version" in CLAUDE.md
- [ ] If removal contains breaking changes (most removals are breaking):
  - [ ] Version was incremented in `Cargo.toml` (following semver MAJOR bump)
  - [ ] "Current Version" in CLAUDE.md was updated
  - [ ] Breaking changes and version bump documented in checkpoint changelog
  - [ ] CLAUDE.md updated to reflect current state (no historical sections)
- [ ] If removal has NO breaking changes (rare - internal-only removal):
  - [ ] Version was NOT changed (per CLAUDE.md policy)
  - [ ] Removal documented in checkpoint changelog or commit messages

Run automated formatting and fixes:

```bash
cargo fix --allow-dirty
cargo fmt
```

**Manual Code Convention Checklist:**

After automated fixes, manually verify the following verifuzz conventions:

- [ ] `use` statements are at most one nested layer deep
  - Good: `use std::fs::{File, OpenOptions}`
  - Bad: `use std::{fs::File, io::Write}`
- [ ] If a `Formula` variant was removed, both `SemanticAnalyzer` and `TypedSemanticAnalyzer` were updated
- [ ] All public functions have `///` rustdoc comments with examples for non-trivial items
- [ ] All AST types derive `Debug` and `PartialEq`
- [ ] No `.unwrap()` or `.expect()` in library code (only in tests or bin/)
- [ ] No orphaned imports or unused code remains

If any manual fixes are needed, make them now.

### 2. Testing

Run the full test suite and fix any failures:

1. Invoke the `/test` skill to run the complete post-edit verification sequence
2. If tests fail:
   - Invoke `/debug-tests` skill to debug and fix failures
   - Repeat until all tests pass
3. For Rhai feature testing, ensure both runs pass:
   - `cargo test` (without rhai feature, 28 tests)
   - `cargo test --features rhai` (with rhai feature, 32 tests)

**Do not proceed until all tests pass.**

### 3. Verify No Orphaned References

Search the codebase to ensure no references to the removed feature remain:

**Search for code references:**
```bash
# Search for the removed feature name/identifier
rg "<removed-feature-name>" --type rust

# Search for removed types, functions (expect no results)
rg "<RemovedType>" --type rust
rg "fn <removed_function>" --type rust

# Check for commented-out code or TODOs referencing removal
rg "TODO.*<removed-feature>" --type rust
rg "FIXME.*<removed-feature>" --type rust
```

**Search documentation:**
```bash
# Search markdown files for lingering references
rg "<removed-feature>" docs/
rg "<removed-feature>" *.md
```

**Expected results:**
- No references to removed types, functions, or modules
- No broken imports or dead code
- No lingering documentation references

**If orphaned references found:**
- Remove or update them now
- Re-run quality checks (cargo fix, cargo fmt)
- Re-run tests

### 4. Documentation Updates

Analyze the changes made and identify which documentation needs updating:

1. **Find all documentation files:**
   ```bash
   find docs/ -name "*.md" -type f
   ls *.md
   ```

2. **Analyze changes to determine impact:**
   - Review `git diff` output to see what was removed
   - Identify which documentation areas were affected

3. **Update relevant documentation:**

   **Common documentation areas for removals:**
   - `docs/api.md` - Remove API references for deleted public functions/types
   - `docs/cli.md` - Remove CLI documentation for deleted arguments/subcommands
   - `docs/parser.md` - Remove grammar/operator documentation for deleted syntax
   - `docs/semantic-analysis.md` - Remove type system documentation for deleted types/rules
   - `docs/examples.md` - Remove or update examples using removed features
   - `README.md` - Update if feature was mentioned in overview or examples
   - `CLAUDE.md` - Add breaking changes section if removal is breaking
   - Any other `.md` files in `docs/` that referenced the removed feature

4. **For each relevant documentation file:**
   - Read the current content
   - Remove or update references to the removed feature
   - Ensure examples still work correctly
   - Be thorough but concise

**Do not skip documentation updates** - orphaned documentation can confuse users.

### 5. Checkpoint Changelog Maintenance

If this removal work is based on a checkpoint, update or create the checkpoint's changelog file:

1. **Check if work is checkpoint-based:**
   - Look for checkpoint references in branch name or planning documents
   - Check for `cp-YYMMDD` directory in `checkpoints/`
   - If found, note the checkpoint ID

2. **Locate or create the changelog:**
   ```bash
   # Find the latest checkpoint
   ls -la checkpoints/

   # Check if changelog exists
   ls checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md
   ```

3. **Update or create the changelog file:**

   **File path format:** `checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md`

   **If file exists:** Add a new dated section for this removal

   **If file doesn't exist:** Create it following this format:
   ```markdown
   # Changelog After Checkpoint cp-YYMMDD

   This file documents all changes made to the verifuzz codebase after checkpoint cp-YYMMDD was created.

   ## YYYY-MM-DD: [Removal Description] ([version if applicable])

   ### Breaking Changes
   - List what was removed from public API
   - Note any behavior changes

   ### Implementation Files
   - Files modified with brief description

   ### Test Updates
   - Number of tests updated/removed
   - Test pass status

   ### Documentation Updates
   - List documentation files updated

   ### PR Information
   - **Branch**: remove/branch-name
   - **PR**: #XX (add after PR created)
   - **Status**: Open/Merged

   ### Verification
   - Test results
   - Build status

   ### Statistics
   - Occurrences removed
   - Lines changed

   ### Review
   - Review status
   ```

4. **Content to include:**
   - Date and descriptive title
   - Breaking changes (what was removed, migration path) - **NOTE: Breaking changes are documented ONLY in checkpoint changelogs, never in CLAUDE.md**
   - Files modified with context
   - Test updates
   - Documentation updates
   - PR information (add PR number after creation)
   - Verification results
   - Statistics (lines changed, occurrences removed)

5. **When to update:**
   - **Now:** Create/update with removal details before committing
   - **After PR creation:** Add PR number to the changelog
   - **After merge:** Add merge status

**IMPORTANT:** This is required by CLAUDE.md's "Checkpoint-based changelog workflow". The checkpoint changelog is the single source of truth for all changes (including breaking changes) made after the checkpoint. CLAUDE.md reflects only the current state of the codebase without historical sections.

**If no checkpoint reference found:** Skip this step - not all removals are checkpoint-based.

### 6. Git Commit

Create a commit following verifuzz conventions:

1. Invoke the `/commit` skill to create a commit with proper message format
2. The commit skill will:
   - Run `git status` and `git diff` to analyze changes
   - Draft a commit message following conventions (headline + body)
   - Create the commit with Co-Authored-By line
   - Verify with `git status`

**Important:** Do NOT squash commits unless explicitly requested. The `/squash` skill is available if needed, but default is to keep commits as-is.

### 7. Push to Remote

Push the removal branch to remote:

```bash
git push -u origin <branch-name>
```

If the branch already tracks a remote, use:

```bash
git push
```

### 8. Create Pull Request

Create a PR using GitHub CLI:

1. Draft PR title and body:
   - **Title:** Short (under 70 characters), descriptive
     - Example: "Remove bounded temporal operators"
     - Example: "Remove legacy parser implementation"
   - **Body format:**
     ```markdown
     ## Summary
     - Bullet point summary of what was removed (1-3 points)
     - Note if this is a breaking change

     ## Changes Made
     - List what was removed by area (parser, semantic, types, etc.)
     - List files deleted or modified

     ## Breaking Changes
     [If applicable]
     - Describe the breaking change
     - Provide migration guidance

     ## Test Plan
     - [ ] All tests pass (cargo test)
     - [ ] All tests pass with rhai feature (cargo test --features rhai)
     - [ ] No orphaned references found
     - [ ] Documentation updated

     🤖 Generated with [Claude Code](https://claude.com/claude-code)
     ```

2. Create the PR:
   ```bash
   gh pr create --title "PR title" --body "$(cat <<'EOF'
   ## Summary
   - ...

   ## Changes Made
   - ...

   ## Breaking Changes
   [If applicable]
   - ...

   ## Test Plan
   - [x] All tests pass
   - [x] No orphaned references

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

3. Note the PR number from the output

4. **Update checkpoint changelog (if applicable):**
   - If you created/updated a checkpoint changelog in step 5, update it with the PR number
   - Edit `checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md`
   - Add PR number to the "PR Information" section
   - Commit the update: `git commit -am "Update changelog with PR #<number>"`
   - Push: `git push`

### 9. Request Review

Request review from GitHub Copilot or other reviewers:

**For Human Reviewers (Using GitHub CLI):**

```bash
# Request review from specific users
gh pr edit <pr-number> --add-reviewer "username1,username2"

# Request review from team
gh pr edit <pr-number> --add-reviewer "org-name/team-name"
```

**For GitHub Copilot Code Review:**

**IMPORTANT:** There is no working CLI command to request Copilot as a reviewer. The user must manually assign Copilot through the GitHub web interface.

1. You can optionally add Copilot as an assignee (this is NOT the same as requesting review):
   ```bash
   gh pr edit <pr-number> --add-assignee "@copilot"
   ```
   This will show Copilot in the "Assignees" section but does NOT trigger a code review.

2. Inform the user that they need to manually request Copilot review:
   - Open the PR on GitHub.com: `https://github.com/<owner>/<repo>/pull/<pr-number>`
   - Click the **Reviewers** section in the right sidebar
   - Select **Copilot** from the dropdown to request an actual code review

**⚠️ CRITICAL WARNING:** When addressing Copilot review comments, **DO NOT** mention "Copilot" or "@copilot" in your PR comments. Mentioning Copilot will trigger it to actively work on the PR (make changes), not just review it. This can lead to unintended modifications. Simply address the feedback without mentioning Copilot by name.

**Verify review request:**

```bash
# Check if human reviewers were added
gh pr view <pr-number> --json reviewRequests

# View full PR details
gh pr view <pr-number>
```

**Note:** GitHub Copilot code review requires Copilot Business or Enterprise subscription and must be enabled for the repository. See: https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review

**Wait for user to notify when reviews are received.**

### 10. Address Review Comments

Once reviews are received:

1. Read review comments:
   ```bash
   gh pr view <pr-number>
   gh api repos/:owner/:repo/pulls/<pr-number>/comments
   ```

2. For each comment:
   - Make the requested changes
   - Run quality checks again (cargo fix, cargo fmt)
   - Re-run tests with `/test` skill
   - Commit fixes with `/commit` skill

3. Push updates:
   ```bash
   git push
   ```

4. Repeat until all review comments are resolved

### 11. Final Notification

Once all reviews are addressed and tests pass:

1. Comment on the PR to inform user to merge:
   ```bash
   gh pr comment <pr-number> --body "@cychen2021 All review comments have been addressed and all tests are passing. Removal is complete and ready to merge! 🚀"
   ```

2. Notify the user in the conversation:
   - Provide the PR URL
   - Confirm all checks passed
   - Confirm PR comment was posted
   - Ask user to merge the PR

## Integration with Other Skills

This skill works with the verifuzz workflow:

- **Triggered after:** `/init-feature-remove` completes removal
- **Uses internally:**
  - `/test` - Full test suite execution
  - `/debug-tests` - Fix test failures
  - `/commit` - Create commits following conventions
  - `/squash` - Optionally squash commits (if requested)

## Notes

- **Do not proceed** to PR creation if tests are failing
- **Always verify no orphaned references** - grep for removed feature names
- **Always update documentation** - remove all references to deleted features
- **Breaking changes require special attention** - CHANGELOG, version, migration guide
- **Manual code convention checks** are critical - automated tools don't catch everything
- The PR body format can be adjusted based on project needs
- GitHub CLI (`gh`) must be configured and authenticated
- Review workflow assumes use of GitHub's review features
- **GitHub Copilot code review** requires repository-level enablement - see: https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review
- **GitHub CLI documentation**: https://cli.github.com/manual/gh_pr for full reference on PR commands

## Exit Criteria

The skill completes when:
1. All tests pass
2. No orphaned references remain
3. All documentation is updated
4. Checkpoint changelog updated (if applicable)
5. Commits are created and pushed
6. PR is created and reviews are requested
7. Review comments (if any) are addressed
8. User is notified to merge
