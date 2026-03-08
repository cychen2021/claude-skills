---
name: finish-feature-impl
description: Complete a feature implementation in the verifuzz codebase with quality checks, testing, documentation updates, commits, and PR creation. Runs cargo fix/fmt, executes full test suite with fixes, updates relevant documentation, creates commits, pushes to remote, creates PR via gh CLI, and manages review workflow. AUTOMATICALLY use this skill when feature implementation work is complete and all todos in the feature checklist are finished, or when the user explicitly requests to "finish feature", "wrap up feature", "complete feature and create PR", or indicates the feature is ready for finalization.
---

# Finish Feature Impl

Complete a feature implementation with quality checks, testing, documentation, and PR workflow.

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
- [ ] If feature contains breaking changes:
  - [ ] Version was incremented in `Cargo.toml` (following semver)
  - [ ] "Current Version" in CLAUDE.md was updated
  - [ ] Breaking changes and version bump documented in checkpoint changelog
  - [ ] CLAUDE.md updated to reflect current state (no historical sections)
- [ ] If feature has NO breaking changes:
  - [ ] Version was NOT changed (per CLAUDE.md policy)
  - [ ] Feature documented in checkpoint changelog or commit messages

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
- [ ] New `Formula` variants are handled in both `SemanticAnalyzer` and `TypedSemanticAnalyzer`
- [ ] All public functions have `///` rustdoc comments with examples for non-trivial items
- [ ] All AST types derive `Debug` and `PartialEq`
- [ ] No `.unwrap()` or `.expect()` in library code (only in tests or bin/)
- [ ] Error messages include contextual information (predicate name, expected vs actual)

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

### 3. Documentation Updates

Analyze the changes made and identify which documentation needs updating:

1. **Find all documentation files:**
   ```bash
   find docs/ -name "*.md" -type f
   ls *.md
   ```

2. **Analyze changes to determine impact:**
   - Review `git diff` output from the commit process
   - Identify which areas were modified (API, CLI, parser, types, semantic analysis, etc.)

3. **Update relevant documentation:**

   **Common documentation areas:**
   - `docs/api.md` - Public API changes (new functions, changed signatures)
   - `docs/cli.md` - CLI arguments or output changes
   - `docs/parser.md` - Grammar, operators, or precedence changes
   - `docs/semantic-analysis.md` - Type system or validation rule changes
   - `docs/examples.md` - New use cases or examples
   - `README.md` - Major features or usage pattern changes
   - `CLAUDE.md` - Development workflow or convention changes
   - Any other `.md` files in `docs/` that are affected

4. **For each relevant documentation file:**
   - Read the current content
   - Update to reflect the changes made
   - Be thorough but concise
   - Ensure examples still work correctly

**Do not skip documentation updates** - even small changes may affect docs.

### 3.5. Checkpoint Changelog Maintenance

If this work is based on a checkpoint, update or create the checkpoint's changelog file:

1. **Check if work is checkpoint-based:**
   - Look for `x_required_code_changes.md` or references to `cp-YYMMDD` in planning documents
   - Check git branch name for checkpoint references
   - If found, note the checkpoint ID (e.g., `cp-260228`)

2. **Locate or create the changelog:**
   ```bash
   # Check if checkpoint directory exists
   ls -la checkpoints/cp-YYMMDD/

   # Check if changelog already exists
   ls checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md
   ```

3. **Update or create the changelog file:**

   **File path format:** `checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md`

   **If file exists:** Update it with the new changes

   **If file doesn't exist:** Create it following this format:
   ```markdown
   # Changelog After Checkpoint cp-YYMMDD

   This file documents all changes made to the verifuzz codebase after checkpoint cp-YYMMDD was created.

   ## YYYY-MM-DD: [Feature/Fix Name] ([version if applicable])

   ### Breaking Changes
   - List any breaking API or behavior changes

   ### New Features
   - List new functionality added

   ### Implementation Files
   - Key files modified with brief description

   ### Test Updates
   - Number of tests updated/added
   - Test coverage information

   ### Documentation Updates
   - List documentation files updated

   ### PR Information
   - **Branch**: feature/branch-name
   - **PR**: #XX (add after PR created)
   - **Merged**: YYYY-MM-DD (add after merge)
   - **Merge Commit**: xxxxxxx (add after merge)

   ### Verification
   - Test results
   - Build status
   - Clippy/lint status

   ### Review
   - Review comments summary
   - Issues addressed
   ```

4. **Content to include:**
   - Date and descriptive title
   - Breaking changes (if any) - **NOTE: Breaking changes are documented ONLY in checkpoint changelogs, never in CLAUDE.md**
   - Features/fixes implemented
   - Files modified with context
   - Test count and coverage
   - Documentation updates
   - PR and merge information (add PR number in step 6, merge info when merged)
   - Verification results

5. **When to update:**
   - **Now:** Create/update with implementation details before committing
   - **After PR creation:** Add PR number to the changelog
   - **After merge:** Add merge date and commit hash

**IMPORTANT:** This is required by CLAUDE.md's "Checkpoint-based changelog workflow". The checkpoint changelog is the single source of truth for all changes (including breaking changes) made after the checkpoint. CLAUDE.md reflects only the current state of the codebase without historical sections.

**If no checkpoint reference found:** Skip this step - not all features are checkpoint-based.

### 4. Git Commit

Create a commit following verifuzz conventions:

1. Invoke the `/commit` skill to create a commit with proper message format
2. The commit skill will:
   - Run `git status` and `git diff` to analyze changes
   - Draft a commit message following conventions (headline + body)
   - Create the commit with Co-Authored-By line
   - Verify with `git status`

**Important:** Do NOT squash commits unless explicitly requested. The `/squash` skill is available if needed, but default is to keep commits as-is.

### 5. Push to Remote

Push the feature branch to remote:

```bash
git push -u origin <branch-name>
```

If the branch already tracks a remote, use:

```bash
git push
```

### 6. Create Pull Request

Create a PR using GitHub CLI:

1. Draft PR title and body:
   - **Title:** Short (under 70 characters), descriptive
   - **Body format:**
     ```markdown
     ## Summary
     - Bullet point summary of changes (1-3 points)

     ## Changes Made
     - List key changes by area (parser, semantic, types, etc.)

     ## Test Plan
     - [ ] All tests pass (cargo test)
     - [ ] All tests pass with rhai feature (cargo test --features rhai)
     - [ ] Manual testing completed (if applicable)
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

   ## Test Plan
   - [x] All tests pass

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

3. Note the PR number from the output

4. **Update checkpoint changelog (if applicable):**
   - If you created/updated a checkpoint changelog in step 3.5, update it with the PR number
   - Edit `checkpoints/cp-YYMMDD/changelog-after-YYMMDD.md`
   - Add PR number to the "PR Information" section
   - Commit the update: `git commit -am "Update changelog with PR number"`
   - Push: `git push`

### 7. Request Review

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

### 8. Address Review Comments

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

### 9. Final Notification

Once all reviews are addressed and tests pass:

1. Comment on the PR to inform user to merge:
   ```bash
   gh pr comment <pr-number> --body "@cychen2021 All review comments have been addressed and all tests are passing. Please review and merge when ready! 🚀"
   ```

2. Notify the user in the conversation:
   - Provide the PR URL
   - Confirm all checks passed
   - Confirm PR comment was posted
   - Ask user to merge the PR

## Integration with Other Skills

This skill works with the verifuzz workflow:

- **Triggered after:** `/init-feature-impl` completes implementation
- **Uses internally:**
  - `/test` - Full test suite execution
  - `/debug-tests` - Fix test failures
  - `/commit` - Create commits following conventions
  - `/squash` - Optionally squash commits (if requested)

## Notes

- **Do not proceed** to PR creation if tests are failing
- **Always update documentation** - even small changes may affect docs
- **Checkpoint changelog maintenance** is required by CLAUDE.md for checkpoint-based work - see step 3.5
- **Manual code convention checks** are critical - automated tools don't catch everything
- The PR body format can be adjusted based on project needs
- GitHub CLI (`gh`) must be configured and authenticated
- Review workflow assumes use of GitHub's review features
- **GitHub Copilot code review** requires repository-level enablement - see: https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review
- **GitHub CLI documentation**: https://cli.github.com/manual/gh_pr for full reference on PR commands

## Exit Criteria

The skill completes when:
1. All tests pass
2. All documentation is updated
3. Checkpoint changelog is updated (if applicable)
4. Commits are created and pushed
5. PR is created and reviews are requested
6. Review comments (if any) are addressed
7. User is notified to merge
