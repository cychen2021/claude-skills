---
name: debug-tests
description: Debug and fix failing unit tests in nrv. Use when `cargo test` reports failures.
---

Debug and fix all failing tests. Work through failures one at a time.

## For each failing test

### 1. Locate the failure

Read the `cargo test` output carefully:
- Which test function failed?
- What module is it in (`parser::`, `semantic::`, `types::`, etc.)?
- What was the assertion — expected value vs. actual value?

### 2. Reason about the root cause (do this thoroughly before touching any code)

Find the failing test with Grep, then read both the test and the source code it exercises. Ask:

- **What does the test assert?** Read the exact expected value — AST structure, error message substring, return type.
- **What does the code actually produce?** Trace the execution path: parser combinator → AST node → semantic pass.
- **Where does the divergence happen?** Identify the precise line where actual behavior stops matching the expectation.
- **Why does the divergence exist?** Common causes in this codebase:
  - A `Formula` variant was added to `ast.rs` but not handled in `SemanticAnalyzer`, `TypedSemanticAnalyzer`, or the parser — causing a `match` arm to be missing or a default arm to fire.
  - An operator precedence rule changed in `parser.rs`, restructuring the AST in a way tests didn't anticipate.
  - An error message was reworded, breaking tests that assert on message substrings.
  - A type compatibility rule changed in `types.rs`, altering what `is_compatible_with()` returns.
- **Is the source wrong, or is the test expectation stale?** Fix the source unless the test itself encodes an incorrect assumption about intended behavior.

Only move to the next step once the root cause is clear and confirmed.

### 3. Fix

Apply the minimal change that corrects the root cause. Do not clean up surrounding code or fix unrelated issues.

If the root cause is a missing `Formula` variant handler, remember to update **both** `SemanticAnalyzer::analyze` and `TypedSemanticAnalyzer::check` in `src/semantic.rs`.

### 4. Verify

Run `cargo test` again. If the previously failing test now passes but new failures appear, treat each new failure as a separate case and repeat from step 1.

Once all tests pass, report which tests were fixed and what the root cause of each was.
