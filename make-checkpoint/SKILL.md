---
name: make-checkpoint
description: Create periodic manual review checkpoints for the verifuzz codebase. Use this skill when the user explicitly requests to create a checkpoint, make a manual checkpoint, or initiate a code review checkpoint after extended development work. The skill generates a timestamped checkpoint folder containing status summary, diff from previous checkpoint, and tailored review guidelines for both documentation and code.
---

# Make Checkpoint

Create periodic manual review checkpoints to facilitate systematic code review after extended development sessions.

## Overview

This skill creates a timestamped checkpoint folder in `checkpoints/` containing:
1. Current codebase status summary
2. Diff comparison with previous checkpoint
3. Tailored documentation review guidelines
4. Tailored code review guidelines

Checkpoints help maintain code quality by providing structured review touchpoints after "vibe coding" sessions.

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

### Step 3: Create Checkpoint Directory

Create the new checkpoint folder:

```bash
mkdir -p checkpoints/cp-<timestamp>
```

### Step 4: Analyze Current Codebase State

Gather information about the current state:

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

### Step 5: Generate `status-quo.md`

Create a concise summary (200-400 words) covering:

```markdown
# Codebase Status Quo - <timestamp>

## Overview
[1-2 sentence project state summary]

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

### Step 6: Generate `diff-vs-<previous_cp_timestamp>.md`

If a previous checkpoint exists, create a comparison document:

**Load previous checkpoint data:**
- Read `checkpoints/cp-<previous_timestamp>/status-quo.md` for baseline state
- Check for `checkpoints/cp-<previous_timestamp>/changelog-after-<previous_timestamp>.md` (post-checkpoint changes)
  - If this changelog exists, incorporate its content into the diff to capture changes made after the previous checkpoint was revised

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

### Step 7: Generate `doc-review-guidelines.md`

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

### Step 8: Generate `code-review-guidelines.md`

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

## Completion

After generating all four files:

1. Confirm checkpoint created successfully:
   ```bash
   ls -lh checkpoints/cp-<timestamp>/
   ```

2. Inform user of next steps:
   - Review `status-quo.md` to understand current state
   - Review `diff-vs-<previous_cp>.md` to see what changed
   - Use `doc-review-guidelines.md` to review documentation
   - Use `code-review-guidelines.md` to review code
   - After applying revisions with `/revise`, create `changelog-after-<timestamp>.md` in the checkpoint directory to track subsequent changes

3. Remind user about the `.gitignore` convention:
   - Checkpoints folder should be added to `.gitignore` if they want these to remain local
   - Or commit them if they want to track review history in the repository

## Changelog Workflow

After checkpoint creation and subsequent revisions:

1. When the user runs `/revise` to apply review feedback, a `revision.md` is created
2. As development continues after the revision, maintain a running changelog: `checkpoints/cp-<timestamp>/changelog-after-<timestamp>.md`
3. This changelog documents all changes made after the checkpoint was revised:
   - New features implemented
   - Bug fixes
   - Refactorings
   - Documentation updates
   - Dependency changes
4. When creating the next checkpoint, this changelog is read and incorporated into the diff analysis to provide complete change tracking
