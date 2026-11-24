---
name: trim-tests
description: Remove and merge tests that cost more than they give (tests of libraries or trivial code, duplicates, tests of implementation details, one-off regression tests), by the rules in test-value.md. Lists what it wants to remove or merge, applies the list after the user approves it, runs the checks and commits. Use when the user asks to trim, prune, slim down or clean up the tests, or says that a project or a branch has too many tests. Other skills read test-value.md to decide when to add a test.
---

# Trim Tests

Remove the tests that cost more than they give, and merge the tests that check the same thing. `test-value.md` in this directory has the rules: what makes a test worth having. Read it first.

The aim is fewer tests with the same protection, not fewer tests at any cost. When you are not sure about a test, keep it.

## 1. Know the scope

- No argument: all tests of the repository.
- A branch or a base (for example `main`): only the tests that the branch added or changed (`git diff <base>...HEAD`). Use this after feature work.
- A path: only the tests in that file or directory.

## 2. List the tests

Find the tests by the conventions of the language and the project (`CLAUDE.md` can say where they are). For each test, note:

- its file and name,
- the behavior that it checks, in a few words,
- if it is slow or needs something outside the process (network, another program, a device, a large file). Run the suite once with timing if the runner can give it (for example `pytest --durations=20`, `cargo test` with the time of each test binary, `go test -v`).

For a large repository, do the list one module at a time.

## 3. Sort the tests

Put each test in one of three groups, by `test-value.md`:

- **Keep.**
- **Merge**: its cases go into another test that checks the same behavior. Name the target test.
- **Delete**: it gives nothing that the remaining tests do not give.

Give each merge and each delete a reason of one line that names the rule (for example "checks serde, not our code" or "same path as `round_trip`").

Never delete or merge these, also when they look small:

- the only test of a behavior that users or other programs depend on,
- tests that the project's docs or `CLAUDE.md` require (for example platform tests or a protocol test),
- tests that the user asked for or wrote.

Also look for helpers, fixtures, test data and dev dependencies that only the tests to delete use.

## 4. Ask the user

Show a short list, grouped by file: only the merges and the deletes, each with its reason. Give the number of tests that stay, but do not list them. Example:

```text
src/login.rs
  delete  provider_names            checks serde rename, not our code
  merge   decode_plus -> decode_query_values   same function, one more case
tests/server.rs
  (no change)

Delete 4, merge 3 into 2, keep 41.
```

Wait for approval. The user can approve all, or remove lines from the list.

## 5. Apply

- Delete the tests. Remove the helpers, fixtures, test data and dev dependencies that no test uses any more.
- For a merge, move each remaining useful case or assertion into the target test. Drop only the cases that the target test already has.
- Change no code that is not a test.

## 6. Check

- Run the project's gate (the format, check and test commands in `CLAUDE.md`, or the usual tools of the language). All must pass.
- Make sure that each behavior from step 3 that users depend on still has a test. If the project already has a coverage tool set up, compare the coverage of the code that is not tests before and after. A line that lost its only test must be one that you decided to leave without a test.

## 7. Commit

Follow the project's commit rules. If the current branch is the default branch, make a branch first. Make one commit, for example "Remove tests that check library behavior". The body lists the deleted tests and the merges. Push and open a pull request only as the project's workflow says.

## 8. Report

Say how many tests there were and are now, the run time before and after if you measured it, and the tests that you kept although they looked small (with the reason).
