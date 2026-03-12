---
name: test
description: Run the full post-edit verification sequence for nrv. Use when code changes are complete and need verification, or when the user requests to run tests or verify changes.
---

Run the full post-edit verification sequence required by this project, in order:

1. `cargo fix --allow-dirty` — apply compiler-suggested fixes
2. `cargo fmt` — format code to Rust style conventions
3. `cargo test` — run all tests (298 unit tests + 18 integration tests)

Stop immediately if any step fails and show the exact error output. Do not proceed to the next step after a failure. Report a clear pass/fail summary when done.
