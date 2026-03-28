---
name: thorough-test
description: Make all tests pass and maximize code coverage using cargo llvm-cov. Use when the user asks to improve test coverage, fix failing tests, run thorough testing, or when coverage is below target. Handles unit tests, integration tests, and snapshot tests (insta). Covers the vischat Rust project.
---

# Thorough Test

Make all tests pass, then maximize coverage using `cargo llvm-cov`.

## Step 1: Ensure all tests pass

```
cargo fix --allow-dirty
cargo fmt
cargo test
```

If any tests fail, fix them before proceeding. For snapshot failures, run `cargo insta review` to accept or update snapshots.

## Step 2: Measure baseline coverage

Choose the right flag for the project type:

- **Bin-only crate** (e.g. `src/main.rs`, no `src/lib.rs`): use the plain command — `--lib` instruments only library targets and will show 0% for a binary-only project.
  ```
  cargo llvm-cov
  ```
- **Lib crate or workspace with a lib target**: `--lib` limits measurement to the library, excluding integration tests and the binary entry point.
  ```
  cargo llvm-cov --lib
  ```

When in doubt, check `Cargo.toml` for `[lib]` vs `[[bin]]` sections.

Note the coverage percentage per file. Focus effort on files below 95%.

Example output format:
```
Filename          Regions  Missed  Cover    Functions  Missed  Exec     Lines  Missed  Cover
app.rs                410       0  100.00%         43       0  100.00%    266       0  100.00%
ui.rs                 399     399    0.00%         10      10    0.00%    196     196    0.00%
```

## Step 3: Increase coverage — per-file strategy

Read each under-covered file. Identify which functions/branches are not exercised, then write targeted tests.

### ui.rs (typically 0% — hardest)

`ui.rs` renders ratatui widgets. Use `TestBackend` to test rendering without a real terminal:

```rust
use ratatui::{Terminal, backend::TestBackend};

let backend = TestBackend::new(80, 24);
let mut terminal = Terminal::new(backend).unwrap();
terminal.draw(|f| {
    // call the render function under test, e.g.:
    crate::ui::draw(f, &app);
}).unwrap();
let buf = terminal.backend().buffer().clone();
// Assert specific cells or use insta snapshot:
insta::assert_debug_snapshot!(buf);
```

Tests for `ui.rs` go in `src/ui.rs` inside a `#[cfg(test)]` module. Add `use ratatui::{Terminal, backend::TestBackend};` at the top.

### message.rs / parser.rs / navigation.rs (partial coverage)

These are pure logic modules. Run `cargo llvm-cov` and examine the "Missed Lines" count. Common gaps:
- Error/edge-case branches (empty input, malformed JSON, missing fields)
- Less-used enum variants in `Display` or `From` impls
- Functions called only from `main.rs` (not reachable via `--lib`)

Write small unit tests in `#[cfg(test)]` blocks at the bottom of each file to hit the missing branches.

## Step 4: Iterate

After adding tests:
```
cargo test
cargo llvm-cov
```

Repeat Step 3 until coverage plateaus or reaches the target (aim for >90% total, >80% per file).

## Step 5: Snapshot tests

If new rendering tests produce snapshot output, run:
```
cargo insta test
cargo insta review
```

Accept correct snapshots. If an existing snapshot is stale after a legitimate UI change, update it with `cargo insta review`.

## Key facts about this codebase

- `main.rs` is the binary entry point and its coverage is typically minimal/excluded.
- Snapshot test fixtures live in `src/snapshots/`.
- Test data fixture: `example-history.jsonl` in the project root.
- `insta` is the snapshot testing library (`dev-dependency`).
- `ratatui`'s `TestBackend` is available without extra dependencies.
