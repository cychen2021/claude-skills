---
name: make-checkpoint
description: Create periodic manual review checkpoints for the codebase. Use this skill when the user explicitly requests to create a checkpoint, make a manual checkpoint, or initiate a code review checkpoint after extended development work. The skill generates a timestamped checkpoint folder containing status summary, diff from previous checkpoint, and tailored review guidelines for both documentation and code.
---

# Make Checkpoint

Create periodic manual review checkpoints to facilitate systematic code review after extended development sessions.

## Overview

This skill creates a timestamped checkpoint folder in `checkpoints/` containing:
1. Current codebase status summary
2. Diff comparison with previous checkpoint
3. Tailored documentation review guidelines
4. Tailored code review guidelines
5. Tailored test-correctness audit guidelines (vibe-code-specific)
6. An empty changelog file to track development that happens after this checkpoint

Checkpoints help maintain code quality by providing structured review touchpoints after "vibe coding" sessions. The test-audit guideline is separate from the code review because passing tests in vibe-coded projects do **not** imply correct tests — circular mocks, mocked-out SUTs, and assertion-free smoke tests are common failure modes that the standard code review tends to skim over.

## Workflow

### Step 1: Calculate Timestamp

Calculate the checkpoint timestamp in YYMMDD format:
- Format: 2-digit year + 2-digit month + 2-digit day
- Example: February 18, 2026 → `260218`
- Use the current date unless user specifies otherwise

### Step 2: Find Previous Checkpoint

Check if previous checkpoints exist:

```bash
ls -t checkpoints/cp-*/status-quo.md 2>/dev/null | head -1
```

If found, extract the timestamp from the directory name (e.g., `checkpoints/cp-250115/` → `250115`).

**Check for a `changelog-after-<prev_timestamp>.md` file in that previous checkpoint's directory before doing anything else.** If a checkpoint was created on a branch that later diverged from (or was merged back into) `main`, this file is the authoritative, already-researched record of everything that landed on `main` in parallel while that checkpoint was in review — do not re-derive this from scratch, and do not assume the checkpoint branch stayed isolated. Cross-check it against the actual current `HEAD`:

```bash
git log --oneline --graph --all | head -40
git merge-base --is-ancestor <prev-checkpoint-commit> HEAD && echo "prev checkpoint is an ancestor of HEAD"
```

If `HEAD` is a descendant of a merge that brought the checkpoint branch back into `main` (or vice versa), the current codebase almost certainly **contains** the parallel work the changelog describes — treat status-quo.md, the diff, and the review guidelines as covering the *merged* reality, not a still-diverged branch. Getting this wrong produces a checkpoint that claims features are absent when they're actually sitting in the working tree (verify with `ls src/`, `grep <dep> Cargo.toml`, etc.), which misleads every reviewer who reads it.

### Step 3: Create Checkpoint Directory

Create the new checkpoint folder:

```bash
mkdir -p checkpoints/cp-<timestamp>
```

### Step 4: Create Empty Changelog File

Create the changelog that will track development work happening *after* this
checkpoint, so it exists from the moment the checkpoint is created rather
than being created later (this used to be the `revise` skill's job — it no
longer creates this file):

```bash
cat > checkpoints/cp-<timestamp>/changelog-after-<timestamp>.md << 'EOF'
# Changelog After Checkpoint cp-<timestamp>

This file tracks all changes made after this checkpoint. Document changes as they happen:

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

This file stays empty at checkpoint-creation time — it's populated during
the development cycle that follows, and gets read back in as an input to
**Step 6** (diff generation) of the *next* checkpoint.

### Step 5: Analyze Current Codebase State

Gather information about the current state:

**Version verification:**
- Check current version: `cargo metadata --format-version 1 | jq -r '.packages[] | select(.name == "nrv") | .version'`
- Verify version in Cargo.toml matches "Current Version" in CLAUDE.md
- If versions are out of sync, note this as a critical issue in status-quo.md
- Record the current version in the checkpoint's status-quo.md

**Repository state:**
- Run `git status` to see modified/untracked files
- Run `git log --oneline -20` to see recent commits
- Run `git diff --stat main` if on a feature branch

**Code structure:**
- Check module organization in `src/`
- Identify any new modules or significant refactoring
- Note changes to public API in `lib.rs`

**Documentation state:**
- Check `docs/` directory for new or modified files
- Review `CLAUDE.md` for updated conventions
- Check `README.md` for alignment with current features

**Test coverage:**
- Run `cargo test 2>&1 | grep -E "test result|running"` for test count
- Identify areas with new tests or gaps

**Dependencies:**
- Check `Cargo.toml` for new or updated dependencies

### Step 6: Generate `status-quo.md`

Create a concise summary (200-400 words) covering:

```markdown
# Codebase Status Quo - <timestamp>

## Overview
[1-2 sentence project state summary]

**Version:** [version from Cargo.toml]

## Architecture
- Core modules: [list key src/ modules]
- Recent structural changes: [any refactoring, new modules]
- Public API surface: [key functions in lib.rs]

## Features
- Implemented: [major features working]
- In progress: [current feature branch if applicable]
- Planned: [known TODOs or future work]

## Code Quality
- Test count: [number from cargo test]
- Coverage gaps: [areas needing tests]
- Technical debt: [known issues, TODOs]

## Documentation
- Up-to-date docs: [which docs/* files are current]
- Documentation gaps: [missing or outdated docs]
- Examples: [state of docs/examples.md]

## Dependencies
- Core deps: [list from Cargo.toml]
- Recent changes: [any new or updated deps]

## Git State
- Current branch: [branch name]
- Recent commits: [last 5-10 commit summaries]
- Uncommitted changes: [if any]
```

### Step 7: Generate `diff-vs-<previous_cp_timestamp>.md`

If a previous checkpoint exists, create a comparison document:

**Load previous checkpoint:**
Read `checkpoints/cp-<previous_timestamp>/status-quo.md` and, if present,
`checkpoints/cp-<previous_timestamp>/changelog-after-<previous_timestamp>.md`
(populated during the intervening development cycle) as inputs.

**Don't assume a minimal cycle.** A previous checkpoint may have been created
on its own review branch while `main` kept moving in parallel — the commit
that merges that branch back into `main` is not the same thing as "only the
commits on that merge commit are new." Diff against the actual point where
the previous checkpoint's branch diverged from `main`
(`git merge-base <previous-checkpoint-commit> <main-at-that-time>`), not just
against the merge commit, so the diff reflects everything that landed on
`main` during the gap — not just what changed after the merge.

**Generate diff covering:**

```markdown
# Changes Since Checkpoint <previous_timestamp>

## Summary
[2-3 sentence overview of what changed]

## Architecture Changes
- New modules: [list any new src/ files]
- Refactored modules: [significant restructuring]
- API changes: [additions/removals in lib.rs]

## Feature Development
- Completed features: [features finished since last checkpoint]
- New features started: [features begun since last checkpoint]
- Bug fixes: [significant bugs fixed]

## Code Quality Changes
- Test additions: [new test coverage]
- Code cleanup: [refactoring, cargo fmt/clippy fixes]
- Technical debt addressed: [what was fixed]
- Technical debt added: [new TODOs or known issues]

## Documentation Updates
- New documentation: [new docs/* files]
- Updated documentation: [modified docs]
- Documentation gaps: [new gaps or resolved gaps]

## Dependency Changes
- Added: [new dependencies]
- Updated: [version bumps]
- Removed: [removed dependencies]

## Commit Activity
- Commits since last checkpoint: [count and key commits]
- Lines changed: [rough estimate from git diff --stat]
```

If no previous checkpoint exists, write:

```markdown
# First Checkpoint

This is the first checkpoint for the project. No previous checkpoint exists for comparison.
```

In this case, `<previous_cp_timestamp>` will be `none`.

### Step 8: Generate `doc-review-guidelines.md`

> **Path naming convention:** Always use full paths (e.g. `ltrn-mapper/src/app.rs`,
> `docs/draft/chiscript-plan.md`) when referencing files in the review guidelines.
> Avoid ambiguous short names like `app.rs` or `editor.rs` that could refer to
> multiple files in the workspace.

Create tailored documentation review guidelines:

```markdown
# Documentation Review Guidelines - Checkpoint <timestamp>

## Purpose
These guidelines help you systematically review documentation for accuracy, completeness, and alignment with the current codebase state.

## Review Priorities

[Based on status-quo.md and diff, identify top 3-5 review priorities]

### Priority 1: [Most important area]
**Why:** [Reason based on recent changes]
**Focus on:** [Specific docs to review]
**Check for:** [Specific issues to look for]

### Priority 2: [Second priority]
...

## Documentation Checklist

### Core Documentation (docs/)

**docs/readme.md:**
- [ ] Index is complete and accurate
- [ ] Quick reference matches current API
- [ ] Links to other docs work

**docs/api.md:**
- [ ] All public functions in lib.rs are documented
- [ ] Function signatures match current code
- [ ] Examples are runnable and correct
- [ ] [Add specific checks based on recent API changes]

**docs/cli.md:**
- [ ] CLI flags match current implementation
- [ ] Examples reflect current behavior
- [ ] Exit codes are documented correctly
- [ ] [Add specific checks based on recent CLI changes]

**docs/examples.md:**
- [ ] All examples are valid and parseable
- [ ] Examples demonstrate current features
- [ ] New features have examples
- [ ] [Add specific checks based on new features]

**docs/parser.md:**
- [ ] Grammar reflects current parser rules
- [ ] Operator precedence is accurate
- [ ] [Add specific checks based on parser changes]

**docs/semantic-analysis.md:**
- [ ] Type system rules are current
- [ ] Phase 1 and Phase 2 are accurate
- [ ] [Add specific checks based on type system changes]

### Project Documentation

**README.md:**
- [ ] Feature list is complete
- [ ] Installation instructions work
- [ ] Quick start example is current
- [ ] [Add specific checks based on changes]

**CLAUDE.md:**
- [ ] Architecture diagram matches current structure
- [ ] Module responsibilities are accurate
- [ ] Workflow examples reflect current process
- [ ] Git conventions are followed in recent commits
- [ ] [Add specific checks based on workflow changes]

## Review Process

1. **Read status-quo.md and diff** to understand what changed
2. **Start with priorities** identified above
3. **Work through checklist** systematically
4. **Take notes** on issues found
5. **Update docs** as you find issues OR create a list for batch updates

## Common Documentation Issues

[Based on the project and recent changes, list common issues to watch for:]
- Outdated code examples
- Missing documentation for new features
- Broken internal links
- Inconsistent terminology
- Examples that don't match current syntax
- [Add project-specific issues based on recent changes]

## Notes
- Focus on accuracy over perfection
- Small issues can accumulate, so address them now
- When in doubt, verify against actual code
</markdown>

### Step 9: Generate `code-review-guidelines.md`

> **Path naming convention:** Always use full paths (e.g. `ltrn-mapper/src/app.rs`,
> `ltrn/src/game/loader.rs`) when referencing files in the review guidelines.
> Avoid ambiguous short names like `app.rs` that could refer to multiple files.

Create tailored code review guidelines:

```markdown
# Code Review Guidelines - Checkpoint <timestamp>

## Purpose
These guidelines help you systematically review code for quality, consistency, and adherence to project conventions after extended development work.

## Review Priorities

[Based on status-quo.md and diff, identify top 3-5 review priorities]

### Priority 1: [Most important area]
**Why:** [Reason based on recent changes]
**Focus on:** [Specific modules to review]
**Check for:** [Specific issues to look for]

### Priority 2: [Second priority]
...

## Code Quality Checklist

### Architecture & Structure

**Module organization (src/):**
- [ ] Each module has clear, single responsibility
- [ ] Module boundaries are well-defined
- [ ] No circular dependencies
- [ ] [Add specific checks based on recent refactoring]

**Public API (lib.rs):**
- [ ] All public functions have rustdoc comments
- [ ] API is consistent and intuitive
- [ ] Error types are appropriate
- [ ] [Add specific checks based on API changes]

### Code Quality

**Error handling:**
- [ ] All public functions return `Result<T, String>`
- [ ] Error messages include context
- [ ] No unwrap() or expect() in library code
- [ ] [Add specific checks based on recent error handling]

**Documentation:**
- [ ] All public items have /// comments
- [ ] Complex functions have # Examples
- [ ] Module-level //! comments explain purpose
- [ ] [Add specific checks based on new code]

**Idiomatic Rust:**
- [ ] Uses &T/&mut T over cloning appropriately
- [ ] Iterator adapters used where readable
- [ ] Match used for complex control flow
- [ ] [Add specific checks based on recent code patterns]

**Testing:**
- [ ] All public functions have tests
- [ ] Error paths are tested
- [ ] Tests use inline strings, not fixture files
- [ ] [Add specific checks based on new features]

### Module-Specific Reviews

[For each module with significant changes, add specific review points]

**src/parser.rs:**
- [ ] All grammar rules have corresponding functions
- [ ] Whitespace handling is consistent (ws wrapper)
- [ ] No panic!() in parser code
- [ ] New operators respect precedence
- [ ] [Add specific checks based on recent parser changes]

**src/semantic.rs:**
- [ ] SemanticAnalyzer and TypedSemanticAnalyzer are structurally consistent
- [ ] Both handle all Formula variants
- [ ] VariableEnv tracking is correct
- [ ] [Add specific checks based on recent semantic changes]

**src/types.rs:**
- [ ] Type compatibility logic is symmetric
- [ ] New types update is_compatible_with()
- [ ] Display impl covers all variants
- [ ] [Add specific checks based on type system changes]

**src/ast.rs:**
- [ ] All types derive Debug and PartialEq
- [ ] New Formula variants added correctly
- [ ] [Add specific checks based on AST changes]

**src/eval.rs:**
- [ ] Rhai integration is secure
- [ ] Trace handling is robust
- [ ] [Add specific checks based on eval changes]

**src/connector.rs:**
- [ ] Trait definitions are clear
- [ ] Annotation handling is correct
- [ ] [Add specific checks based on connector changes]

## Convention Compliance

**CLAUDE.md conventions:**
- [ ] Commit messages follow format (verb, bullets, backticks)
- [ ] Error handling uses Result<_, String>
- [ ] use statements have max one nested layer
- [ ] [Add specific convention checks]

**Rust style:**
- [ ] cargo fmt has been run
- [ ] cargo clippy warnings addressed
- [ ] [Add specific style checks]

## Review Process

1. **Read status-quo.md and diff** to understand scope of changes
2. **Start with priorities** identified above
3. **Run automated checks:**
   ```bash
   cargo build
   cargo test
   cargo clippy
   cargo fmt --check
   ```
4. **Review high-churn areas** (files with most changes)
5. **Work through module-specific checklists**
6. **Check convention compliance**
7. **Document findings** and create fix list

## Common Code Quality Issues

[Based on the project and recent changes, list common issues to watch for:]
- Missing tests for new functionality
- Inconsistent error messages
- Outdated comments
- Unnecessary cloning
- Missing rustdoc examples
- [Add project-specific issues based on recent changes]

## Red Flags

[Issues that require immediate attention:]
- Tests failing
- Clippy errors (not just warnings)
- Public functions without documentation
- unwrap() in library code
- [Add project-specific red flags]

## Notes
- Focus on high-impact issues first
- Small consistency issues matter over time
- When in doubt, check CLAUDE.md conventions
- Balance idealism with pragmatism
```

### Step 10: Generate `test-audit-guidelines.md`

> **Path naming convention:** Always use full paths (e.g.
> `src/buckai_dojo/aws/sweep.py`, `tests/test_aws_sweep.py`) when referencing
> files. Avoid ambiguous short names that could refer to multiple files.

This file is specifically focused on the **correctness of the tests themselves**,
not the code under test. Vibe-coded projects routinely accumulate tests that
pass but assert nothing meaningful — the standard code review tends to skim
past green-bar tests, so this audit makes test correctness a first-class
review pass.

The goal is **not** to expand coverage. The goal is to confirm that the
existing tests would actually fail if the system under test (SUT) regressed.

```markdown
# Test Audit Guidelines - Checkpoint <timestamp>

## Purpose

Audit the **correctness of tests themselves**, not the code they cover. In
vibe-coded projects, a passing test suite is weaker evidence than it looks:
LLM-authored tests frequently mock out the very function they claim to test,
duplicate the SUT's logic inside the mock, or assert only that no exception
was raised. This audit is the deliberate counter-pressure against that drift.

Coverage expansion is **out of scope** here — that belongs in a separate task.
Here we ask: of the tests that already exist, which ones would actually catch
a regression?

## Audit Priorities

[Based on status-quo.md and diff, identify the 3-5 highest-risk test files —
typically the ones covering the highest-churn or highest-stakes modules.]

### Priority 1: [test file for the highest-stakes module]
**Why:** [Reason — e.g. covers the AWS sweep path, real-money blast radius]
**Focus on:** [specific test file paths]
**Audit for:** [the specific anti-patterns most likely here]

### Priority 2: ...

## Vibe-Code Test Anti-Patterns

For each test file under audit, check for:

### Mocked-out SUT
- [ ] The function under test is **not** itself mocked or patched.
- [ ] `patch.object(module, "func_under_test", ...)` does NOT replace the SUT.
- [ ] When the SUT is a method on a class, the class isn't replaced wholesale
      with a `MagicMock`.

### Circular / tautological mocks
- [ ] The test does not configure a mock to return value `X` and then assert
      the SUT returned `X` — that asserts the mock, not the SUT.
- [ ] Mock return values are realistic shapes the *real* dependency would
      return, not values hand-picked to make the assertion pass.
- [ ] No mocks duplicate the SUT's logic inside `side_effect=` so the test
      passes regardless of what the SUT does.

### Assertion-free smoke tests
- [ ] Every test has at least one meaningful `assert` (not just
      `assert result is not None` on a function that can never return None).
- [ ] "Did not raise" is justified — if the only assertion is
      implicit-no-exception, the test name says so AND raising is a real risk.
- [ ] No tests end with `mock.assert_called()` as the *only* assertion when
      the call is a precondition for any code reaching the assertion line.

### Over-mocking the boundary
- [ ] External I/O (`subprocess.run`, `urllib.request.urlopen`, sockets, boto3)
      is mocked at the **boundary**, not deeper. Mocking the SUT's internal
      helpers hides bugs in those helpers.
- [ ] Where a fake/stub would be clearer than a `MagicMock`, prefer the fake.

### Frozen-in-amber expectations
- [ ] Hardcoded expected values (ARNs, image URIs, ports, JSON blobs) match
      what the SUT actually produces today, not a stale snapshot.
- [ ] Snapshot/golden-file tests have been re-checked, not blindly regenerated.

### Setup-driven false positives
- [ ] `setUp` / fixtures don't quietly construct the answer the test then
      "discovers" — i.e. the fixture isn't doing the SUT's job.
- [ ] Parametrized tests don't all pass via the same trivial branch; spot-check
      one boundary case per parametrize block.

### Error-path coverage that doesn't actually exercise the error
- [ ] Tests for failure modes raise the failure where the SUT will *see* it,
      not at a point the SUT short-circuits before reaching.
- [ ] `pytest.raises(SomeError)` is paired with a `match=` or message check
      when multiple call sites can raise the same error type.

### Async / threading / subprocess hazards
- [ ] Tests that spawn threads, asyncio tasks, or subprocesses join/await
      them; no fire-and-forget that could mask a silent failure.
- [ ] Time-sensitive tests use injected clocks or fixtures, not `sleep`.

### Test isolation
- [ ] No test depends on another test having run first (suite ordering).
- [ ] Tests don't leave behind temp files, env vars, or global state.
- [ ] Module-level singletons / caches are reset per-test where relevant.

## Module-Specific Audit

[For each test file under audit, list the specific concrete anti-patterns
most likely present, given what the corresponding SUT does.]

### tests/test_<module>.py
- [ ] [specific check tied to that SUT's behavior]
- [ ] [specific check tied to that SUT's behavior]

## Cross-Cutting Checks

- [ ] Skipped tests (`pytest.skip`, `xfail`) are still justified — none have
      become silently dead with the recent refactors.
- [ ] No `if False:` / commented-out test bodies.
- [ ] Test names describe the *behavior under test*, not the implementation
      (`test_returns_none_when_input_empty`, not `test_calls_strip_then_split`).
- [ ] Coverage gaps in the per-file `term-missing` report flag genuinely
      untested *behavior*, not just untested *lines* (some untested lines are
      defensible defensive code).

## Audit Process

1. **Pick the highest-stakes test file from Priority 1.** Open the test file
   and the SUT side-by-side.
2. **For each test in that file, mutation-check it mentally:** if I broke the
   SUT's logic in the obvious way, would this test fail? If "no" or "unsure",
   flag it.
3. **Sample-mutate one or two tests for real** if the file is high-stakes —
   change a constant in the SUT, run that test, confirm red.
4. **Walk Priority 2-N** the same way.
5. **Run the cross-cutting checks** across the full `tests/` tree.
6. **Document findings** as a fix list — bad tests should be rewritten or
   deleted, not patched. A deleted misleading test is better than a kept one.

## Deliverable

A list of tests in one of three buckets:
- **Delete:** the test asserts nothing useful and rewriting it is not worth
  it.
- **Rewrite:** the test covers behavior worth covering but does it wrong
  (mocked-out SUT, tautology, etc.).
- **Keep:** the test would catch a regression. No action.

## Notes

- A failing audit is *good news* — it means you found tests that were lying
  to you. Treat them as bugs.
- Don't expand coverage during the audit. Note gaps; address them in a later
  pass.
- When deleting a test, leave a note in the commit message naming the
  anti-pattern, so future authors learn the failure mode.
```

## Completion

After generating all six files:

1. Confirm checkpoint created successfully:
   ```bash
   ls -lh checkpoints/cp-<timestamp>/
   ```

2. Inform user of next steps:
   - Review `status-quo.md` to understand current state
   - Review `diff-vs-<previous_cp>.md` to see what changed
   - Use `doc-review-guidelines.md` to review documentation
   - Use `code-review-guidelines.md` to review code
   - Use `test-audit-guidelines.md` to audit test correctness
   - Log ongoing work in `changelog-after-<timestamp>.md` as it happens, ready for the next checkpoint's diff step

3. Remind user about git workflow:
   - Checkpoints are meant to be committed to track review history in the repository
   - This provides a historical record of manual review touchpoints
   - Each checkpoint documents the state at a specific point in time
