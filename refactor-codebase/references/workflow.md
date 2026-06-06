# Refactoring Workflow

This document describes the detailed refactoring workflow. It is **language-agnostic**: the automated steps are the same regardless of language, only the underlying tool differs. The script (`scripts/refactor_check.py`) detects the toolchain; the table below maps each step to the tool it runs.

## Toolchain Reference

| Step | Rust | Python |
| --- | --- | --- |
| Format (check) | `cargo fmt -- --check` | `ruff format --check .` |
| Format (apply) | `cargo fmt` | `ruff format .` (or project `format.py`) |
| Autofix | `cargo fix --allow-dirty --allow-staged` | `ruff check --fix .` |
| Lint | `cargo clippy --all-targets --all-features -- -D warnings` | `ruff check .` |
| Type-check | (n/a — compiler) | `pyright` / `mypy` (or project `type_check.py`) |
| Docs | `cargo doc --no-deps --document-private-items` | docstrings; `pytest --doctest-modules` if used |
| Tests | `cargo test` | `pytest` |

When the project uses `uv` (a `uv.lock` is present), Python commands run under `uv run`. Project helper scripts (`format.py`, `type_check.py`) are preferred when present. Always defer to commands documented in the project's `CLAUDE.md`.

## Execution Flow

1. **Format code**
2. **Apply autofixes** (compiler/linter safe fixes)
3. **Address lint warnings** (clippy / ruff)
4. **Type-check** (Python) / **check docs** (Rust)
5. **Run tests**
6. **Handle structural issues** (manual review)

## Handling Different Issue Types

### Format Issues (Auto-fix)

**Detection**: the format-check command shows diffs.

**Action**: run the formatter automatically (applied by the script).

### Autofixable Warnings (Auto-fix)

**Detection**: `cargo fix` / `ruff check --fix` suggests changes.

**Common fixes**:
- Unused imports
- Unused variables
- Deprecated syntax
- Simplifiable expressions (ruff)

**Resolution**: applied automatically by the script.

### Lint Warnings (Review Required)

**Detection**: `cargo clippy` / `ruff check` reports remaining warnings.

**Action**: review each warning and decide:

1. **Apply safe fixes** — simplifications, style improvements
2. **Skip false positives** — suppress narrowly with justification
3. **Document intentional choices** — explain why the warning doesn't apply

**Suppression syntax**:
- Rust: `#[allow(clippy::warning_name)]` with a comment
- Python (ruff): `# noqa: <RULE>` with a comment
- Python (type errors): `# type: ignore[<code>]` (see CLAUDE.md)

**Common Rust clippy warnings**: `needless_return`, `redundant_pattern_matching`, `manual_map`, `single_match`.

**Common Python ruff warnings**: unused import (`F401`), unused variable (`F841`), mutable default argument (`B006`), unnecessary comprehension (`C4xx`), un-pythonic comparison (`E711`/`E712`).

**Example decision tree**:
```
Lint warning found
├─ Safe refactor (style/simplification)? → Apply immediately
├─ False positive? → Suppress narrowly with a justifying comment
└─ Complex change? → Report for manual review
```

### Documentation / Type Issues (Review Required)

**Rust** — `cargo doc` shows warnings or missing docs:
1. Add missing `///` comments on public items
2. Verify examples compile (`cargo test --doc`)

**Python** — `pyright`/`mypy` reports type issues:
1. Fix genuine type errors
2. Add precise annotations where inference fails
3. Suppress unfixable third-party issues with `# type: ignore[<code>]` and a comment

**Priority** (both): public API > public types/classes > complex private items.

### Structural Refactoring (Manual)

These require human judgment and are NOT automated. They apply identically across languages:

**Code duplication**:
- Search for similar patterns with Grep
- Consider extracting shared logic (3+ occurrences → consider extraction)
- Balance DRY vs readability

**Complex functions**:
- Functions over ~50 lines → consider breaking down
- Deep nesting (4+ levels) → flatten with early returns / guard clauses
- Too many parameters (6+) → consider a struct / dataclass / parameter object

**Module organization**:
- Files over ~500 lines → consider splitting
- Related functionality → group in submodules / packages

## After Refactoring

Always run the full verification sequence:
```bash
# Option 1: use the refactoring script (recommended — auto-detects toolchain)
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py

# Option 2: manual verification
#   Rust:
cargo fmt && cargo fix --allow-dirty && cargo test
#   Python (this repo):
uv run format.py && uv run type_check.py && uv run pytest
```

If creating a commit, follow conventions in CLAUDE.md.

## Common Patterns

### Extracting repetitive code

**Rust — before**:
```rust
fn validate_a() -> Result<(), String> { /* validation logic */ }
fn validate_b() -> Result<(), String> { /* same validation logic */ }
```

**Rust — after**:
```rust
fn validate(input: Input) -> Result<(), String> { /* shared validation logic */ }
```

**Python — before**:
```python
def validate_a(x): ...  # validation logic
def validate_b(x): ...  # same validation logic
```

**Python — after**:
```python
def validate(x):  # shared validation logic
    ...
```

### Simplifying nested conditionals

**Rust — before**:
```rust
match result {
    Ok(val) => match val {
        Some(x) => process(x),
        None => default(),
    },
    Err(e) => handle_error(e),
}
```

**Rust — after**:
```rust
match result {
    Ok(Some(x)) => process(x),
    Ok(None) => default(),
    Err(e) => handle_error(e),
}
```

### Using early returns / guard clauses

**Rust — before**:
```rust
fn process(x: Option<i32>) -> i32 {
    if let Some(val) = x { val * 2 } else { 0 }
}
```

**Rust — after**:
```rust
fn process(x: Option<i32>) -> i32 {
    let Some(val) = x else { return 0 };
    val * 2
}
```

**Python — before**:
```python
def process(items):
    if items:
        result = []
        for item in items:
            if item.is_valid():
                result.append(transform(item))
        return result
    return []
```

**Python — after**:
```python
def process(items):
    if not items:
        return []
    return [transform(item) for item in items if item.is_valid()]
```
