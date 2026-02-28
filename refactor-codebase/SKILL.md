---
name: refactor-codebase
description: Comprehensive codebase refactoring for Rust projects with emphasis on structural improvements. Analyzes architecture, identifies code duplication, extracts helpers, improves module organization, then applies automated fixes (formatting, clippy, compiler suggestions). Use when the user explicitly requests refactoring, code cleanup, or maintenance tasks like '/refactor', 'clean up the codebase', 'run refactoring checks', or 'periodic maintenance'. Also use before major milestones or after significant feature development to ensure code quality.
---

# Refactor Codebase

Perform comprehensive codebase refactoring and maintenance for Rust projects with **primary focus on structural improvements**, followed by automated formatting, linting, and quality checks.

## Quick Start

Run the refactoring script to execute all automated checks:

```bash
# Cross-platform (Windows, Linux, macOS)
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py

# Or on Windows
python .claude/skills/refactor-codebase/scripts/refactor_check.py
```

The script will:
1. Format code with `cargo fmt`
2. Apply compiler-suggested fixes with `cargo fix`
3. Check for clippy warnings
4. Verify documentation completeness
5. Run all tests

## Refactoring Workflow

**IMPORTANT**: Structural refactoring is the primary focus. Always begin by analyzing the codebase architecture and identifying structural improvements before running automated tools.

### Phase 1: Structural Analysis & Refactoring (MOST IMPORTANT)

**This is the core of refactoring.** Scrutinize the codebase structure and architecture to identify improvements:

**Code duplication** (3+ similar blocks):
- Use Grep to find patterns across the codebase
- Extract shared logic into helper functions
- Balance DRY principle with code clarity
- Example: File reading logic repeated 5+ times → extract helper

**Complex functions** (over 50 lines, deep nesting):
- Break into smaller, focused functions
- Use early returns to reduce nesting
- Extract parameter structs for functions with 6+ parameters
- Split logic into meaningful sub-operations

**Module organization**:
- Split files over 500 lines
- Group related functionality into submodules
- Ensure clear separation of concerns
- Review module boundaries and responsibilities

**Architecture improvements**:
- Identify tight coupling that should be loosened
- Look for opportunities to reduce dependency chains
- Consider whether abstractions are at the right level
- Remove dead code and redundant checks

**See [workflow.md](references/workflow.md) for detailed patterns and examples.**

### Phase 2: Automated Fixes

After structural improvements, execute the refactoring script. It handles:

- **Code formatting** - Applies Rust style conventions automatically
- **Compiler fixes** - Removes unused imports, fixes deprecated syntax
- **Safe changes** - Low-risk improvements that don't alter behavior

The script will report warnings (applied automatically) and errors (require manual review).

### Phase 3: Review Clippy Warnings

If clippy warnings are found, review each one:

**For safe refactors** (style improvements, simplifications):
- Apply the suggested changes
- Example: `needless_return`, `redundant_pattern_matching`

**For false positives**:
- Add `#[allow(clippy::warning_name)]` with a comment explaining why
- Document the intentional choice

**For complex changes**:
- Read [workflow.md](references/workflow.md) for detailed decision guidance
- Consider impact on readability vs. correctness

### Phase 4: Documentation Review & Updates

**CRITICAL**: Documentation is a first-class deliverable. As projects evolve, documentation often expands alongside features. During refactoring, comprehensive documentation review is essential.

**Review all documentation for accuracy:**

1. **Check rustdoc comments** (`///` and `//!`):
   - Verify public API documentation is complete and accurate
   - Update function signatures, parameter descriptions, return values
   - Ensure code examples compile and demonstrate current API
   - Add missing documentation for new public items

2. **Review user-facing documentation** in `docs/`:
   - **IMPORTANT**: Check that all markdown files reflect current behavior
   - Update API references for signature changes
   - Verify CLI documentation matches current flags and output
   - Review examples for outdated patterns or removed features
   - Check that new features are documented appropriately
   - Ensure cross-references between docs remain valid

3. **Validate documentation:**
   - Run `cargo test --doc` to verify rustdoc examples compile
   - Manually review code examples in markdown files
   - Check that documentation reflects architectural changes made during refactoring

4. **Documentation priority:**
   - Public API documentation (highest priority)
   - User-facing guides and tutorials
   - Public structs, enums, and traits
   - Complex private implementations (if non-obvious)

**Why documentation review matters during refactoring:**
- Refactoring often reveals outdated documentation assumptions
- Documentation may have grown organically and needs consistency review
- Structural changes require documentation updates
- Examples may reference deprecated patterns

### Phase 5: Verification

Always run after refactoring:

```bash
cargo fmt
cargo fix --allow-dirty
cargo test
```

Ensure all tests pass before committing changes.

## When to Refactor

**Weekly/Monthly maintenance**: Run the refactoring script periodically to catch accumulating issues

**After feature implementation**: Clean up quick fixes and technical debt from development

**Before code review**: Proactively address mechanical issues

**Pre-commit**: Ensure code meets quality standards (though consider the `/test` skill for this)

## Detailed Reference

For comprehensive workflow guidance, decision trees, and refactoring patterns:
- [workflow.md](references/workflow.md) - Complete refactoring procedures and examples

## Integration with Other Skills

- Use `/test` skill for comprehensive post-edit verification
- Use `/debug-tests` skill if tests fail during refactoring
- Commit changes following conventions in CLAUDE.md
