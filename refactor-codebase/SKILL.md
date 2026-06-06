---
name: refactor-codebase
description: Comprehensive codebase refactoring with emphasis on structural improvements, for any language (Rust, Python, ...). Analyzes architecture, identifies code duplication, extracts helpers, improves module organization, then applies automated fixes (formatting, linting, type-checking, compiler suggestions) using the project's detected toolchain. Use when the user explicitly requests refactoring, code cleanup, or maintenance tasks like '/refactor', 'clean up the codebase', 'run refactoring checks', or 'periodic maintenance'. Also use before major milestones or after significant feature development to ensure code quality.
---

# Refactor Codebase

Perform comprehensive codebase refactoring and maintenance with **primary focus on structural improvements**, followed by automated formatting, linting, type-checking, and quality checks.

The skill is **language-agnostic**: the automated checks detect the project's toolchain and run the matching tools. Currently supported:

| Language | Detected by | Format | Lint / type-check | Test |
| --- | --- | --- | --- | --- |
| Rust | `Cargo.toml` | `cargo fmt` | `cargo clippy`, `cargo doc` | `cargo test` |
| Python | `pyproject.toml` / `setup.py` | `ruff format` (or project `format.py`) | `ruff check`, `pyright`/`mypy` (or project `type_check.py`) | `pytest` |

When a project ships its own quality helpers (e.g. this repo's `format.py` and `type_check.py`, run via `uv run`), the script prefers them. Always honor any toolchain commands documented in the project's `CLAUDE.md`.

## Quick Start

Run the refactoring script to execute all automated checks for the detected toolchain(s):

```bash
# Auto-detect Rust / Python in the current directory
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py

# Force one toolchain, or point at another directory
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py --lang python
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py /path/to/project

# On Windows, use `python` instead of `python3`
```

The script will, per detected toolchain:
1. Check & apply code **formatting**
2. Apply **compiler / linter autofixes** (e.g. `cargo fix`, `ruff check --fix`)
3. Run the **linter** (clippy / ruff) and report issues
4. Run the **type-checker** (Python: pyright/mypy) and **docs** (Rust: cargo doc)
5. Run the **tests**

## Refactoring Workflow

**IMPORTANT**: Structural refactoring is the primary focus and is language-independent. Always begin by analyzing the codebase architecture and identifying structural improvements before running automated tools.

### Phase 1: Structural Analysis & Refactoring (MOST IMPORTANT)

**This is the core of refactoring.** Scrutinize the codebase structure and architecture to identify improvements. These apply to any language:

**Code duplication** (3+ similar blocks):
- Use Grep to find patterns across the codebase
- Extract shared logic into helper functions/modules
- Balance DRY principle with code clarity
- Example: file-reading logic repeated 5+ times → extract a helper

**Complex functions** (over ~50 lines, deep nesting):
- Break into smaller, focused functions
- Use early returns / guard clauses to reduce nesting
- Extract a parameter object/struct/dataclass for functions with 6+ parameters
- Split logic into meaningful sub-operations

**Module organization**:
- Split files over ~500 lines
- Group related functionality into submodules / packages
- Ensure clear separation of concerns
- Review module boundaries and responsibilities

**Architecture improvements**:
- Identify tight coupling that should be loosened
- Look for opportunities to reduce dependency chains
- Consider whether abstractions are at the right level
- Remove dead code and redundant checks

**See [workflow.md](references/workflow.md) for detailed patterns and per-language examples.**

### Phase 2: Automated Fixes

After structural improvements, execute the refactoring script. It detects the toolchain and handles:

- **Code formatting** — applies the language's style conventions automatically
- **Autofixes** — removes unused imports, fixes deprecated syntax, applies safe lint fixes (`cargo fix`, `ruff check --fix`)
- **Safe changes** — low-risk improvements that don't alter behavior

The script reports warnings (applied automatically) and errors (require manual review).

### Phase 3: Review Linter Warnings

If the linter (clippy for Rust, ruff for Python) reports remaining warnings, review each one:

**For safe refactors** (style improvements, simplifications):
- Apply the suggested change
- Rust examples: `needless_return`, `redundant_pattern_matching`
- Python examples: unused variable, mutable default arg, simplifiable comprehension

**For false positives**:
- Suppress narrowly with a justifying comment:
  - Rust: `#[allow(clippy::warning_name)]`
  - Python (ruff): `# noqa: <RULE>`; type errors: `# type: ignore[<code>]` (per CLAUDE.md)
- Document the intentional choice

**For complex changes**:
- Read [workflow.md](references/workflow.md) for detailed decision guidance
- Consider impact on readability vs. correctness

### Phase 4: Documentation Review & Updates

**CRITICAL**: Documentation is a first-class deliverable. As projects evolve, documentation often expands alongside features. During refactoring, comprehensive documentation review is essential.

**Review all documentation for accuracy:**

1. **Check in-code API docs**:
   - Rust: rustdoc comments (`///`, `//!`)
   - Python: module/class/function docstrings
   - Verify public API docs are complete and accurate; update signatures, parameter descriptions, return values
   - Ensure code examples reflect the current API

2. **Review user-facing documentation** in `docs/` (and `README`):
   - **IMPORTANT**: Check that markdown files reflect current behavior
   - Update API references for signature changes
   - Verify CLI documentation matches current flags and output
   - Review examples for outdated patterns or removed features
   - Ensure cross-references between docs remain valid

3. **Validate documentation:**
   - Rust: `cargo test --doc` verifies rustdoc examples compile
   - Python: ensure docstring examples are correct (run doctests with `pytest --doctest-modules` if the project uses them)
   - Manually review code examples in markdown files

4. **Documentation priority:**
   - Public API documentation (highest priority)
   - User-facing guides and tutorials
   - Public types/classes/traits
   - Complex private implementations (if non-obvious)

### Phase 5: Verification

Always run the full verification sequence after refactoring. Re-running the script is the simplest option:

```bash
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py
```

Or run the tools manually for your toolchain:

```bash
# Rust
cargo fmt && cargo fix --allow-dirty && cargo test

# Python (this repo: prefer the project helpers)
uv run format.py && uv run type_check.py && uv run pytest
```

Ensure all tests pass before committing changes.

## When to Refactor

**Weekly/Monthly maintenance**: Run the refactoring script periodically to catch accumulating issues

**After feature implementation**: Clean up quick fixes and technical debt from development

**Before code review**: Proactively address mechanical issues

**Pre-commit**: Ensure code meets quality standards (though consider the `/test` skill for this)

## Detailed Reference

For comprehensive workflow guidance, decision trees, and refactoring patterns:
- [workflow.md](references/workflow.md) — complete refactoring procedures and per-language examples

## Integration with Other Skills

- Use `/test` skill for comprehensive post-edit verification
- Use `/debug-tests` skill if tests fail during refactoring
- Commit changes following conventions in CLAUDE.md
