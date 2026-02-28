# Refactoring Workflow

This document describes the detailed refactoring workflow for verifuzz maintenance.

## Execution Flow

1. **Format code** (`cargo fmt`)
2. **Apply compiler fixes** (`cargo fix --allow-dirty`)
3. **Address clippy warnings** (`cargo clippy`)
4. **Check documentation** (`cargo doc`)
5. **Run tests** (`cargo test`)
6. **Handle structural issues** (manual review)

## Handling Different Issue Types

### Format Issues (Auto-fix)

**Detection**: `cargo fmt --check` shows diffs

**Action**: Run `cargo fmt` automatically

**Example**:
```
Diff in src/parser.rs at line 42
```

**Resolution**: Applied automatically by script

### Compiler Warnings (Auto-fix)

**Detection**: `cargo fix` suggests changes

**Action**: Apply `cargo fix --allow-dirty --allow-staged`

**Common fixes**:
- Unused imports
- Unused variables (prefix with `_`)
- Deprecated syntax

**Resolution**: Applied automatically by script

### Clippy Warnings (Review Required)

**Detection**: `cargo clippy` reports warnings

**Action**: Review each warning and decide:

1. **Apply safe fixes** - Simplifications, style improvements
2. **Skip false positives** - Add `#[allow(clippy::...)]` with justification
3. **Document intentional choices** - Explain why warning doesn't apply

**Common clippy warnings**:
- `needless_return` - Remove explicit return
- `redundant_pattern_matching` - Use `if let` instead of `match`
- `manual_map` - Replace manual `match` with `.map()`
- `single_match` - Replace `match` with `if let`

**Example decision tree**:
```
Clippy warning found
├─ Safe refactor (style/simplification)? → Apply immediately
├─ False positive? → Add #[allow(...)] with comment
└─ Complex change? → Report for manual review
```

### Documentation Issues (Review Required)

**Detection**: `cargo doc` shows warnings or missing docs

**Action**:
1. Check for missing `///` comments on public items
2. Verify examples compile (use `cargo test --doc`)
3. Update affected docs/ markdown files

**Priority**:
- Public API functions (required)
- Public structs/enums (required)
- Private items (optional, add if complex)

### Structural Refactoring (Manual)

These require human judgment and are NOT automated:

**Code duplication**:
- Search for similar patterns with Grep
- Consider extracting shared logic
- Balance DRY vs readability (3+ occurrences → consider extraction)

**Complex functions**:
- Functions over 50 lines → consider breaking down
- Deep nesting (4+ levels) → flatten with early returns
- Too many parameters (6+) → consider a struct

**Module organization**:
- Files over 500 lines → consider splitting
- Related functionality → group in submodules

## After Refactoring

Always run the full verification sequence:
```bash
# Option 1: Use the refactoring script (recommended)
python3 .claude/skills/refactor-codebase/scripts/refactor_check.py

# Option 2: Manual verification
cargo fmt
cargo fix --allow-dirty
cargo test
```

If creating a commit, follow conventions in CLAUDE.md.

## Common Patterns

### Extracting repetitive code

**Before**:
```rust
fn validate_a() -> Result<(), String> {
    // validation logic
}
fn validate_b() -> Result<(), String> {
    // same validation logic
}
```

**After**:
```rust
fn validate(input: Input) -> Result<(), String> {
    // shared validation logic
}
```

### Simplifying nested matches

**Before**:
```rust
match result {
    Ok(val) => {
        match val {
            Some(x) => process(x),
            None => default(),
        }
    }
    Err(e) => handle_error(e),
}
```

**After**:
```rust
match result {
    Ok(Some(x)) => process(x),
    Ok(None) => default(),
    Err(e) => handle_error(e),
}
```

### Using early returns

**Before**:
```rust
fn process(x: Option<i32>) -> i32 {
    if let Some(val) = x {
        val * 2
    } else {
        0
    }
}
```

**After**:
```rust
fn process(x: Option<i32>) -> i32 {
    let Some(val) = x else { return 0 };
    val * 2
}
```
