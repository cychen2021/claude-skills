# When a test is worth having

A test has a cost. It takes time on each run, it is code that people must read, and it must change each time the code that it tests changes. Keep a test only when it gives more than it costs. Other skills (`start-feature-work`, `finish-feature-work`, `make-cp`) use these rules too.

## Add a test when

At least one of these is true:

- **The logic is easy to get wrong, and the error is hard to see.** For example: parsing, escaping and encoding, merging, ordering and sorting, date and time arithmetic, state machines, retries and timeouts, concurrency.
- **Other people or programs depend on the behavior.** For example: a public API, a CLI, a config or file format, a wire protocol, a guarantee that the docs give.
- **The bug can come back.** The same mistake can happen again: in code that changes frequently, or in new code of the same kind (for example, each new optional setting can have the bug of the last one).
- **No other test goes through a main path.** One end-to-end test of each main flow is worth having, also when its parts have no tests of their own.

## Do not add a test when

- **It checks a library, the language or the framework**, not the code of the project. For example: that a serde rename gives the expected name, that a map keeps a value, that the type checker rejects a wrong type.
- **The code is trivial**: constructors, getters, constants, a `Display` or `to_string` of an enum, code that the compiler or type checker already checks.
- **Another test already goes through the same path with the same kind of input.** Add an assertion or a case to that test instead.
- **It checks an implementation detail**: a private helper, the order of internal calls, an internal data layout. A rewrite changes these without a change of behavior, and then the test must change for no reason.
- **The bug was a one-off**: a typo, a wrong constant, a missing line that nothing makes likely again. The fix is the check.
- **It needs so many mocks that it checks the mocks**, or the mock returns the value that the test expects.

## When you fix a bug

1. Decide with the two lists above if the bug deserves a test.
2. If it does, first add an assertion or a case to an existing test. Write a new test only if no existing test fits.
3. If it does not, add no test. If someone asked for the fix (a review comment, an issue), say in one line why there is no test.

## The form of a test

- One test for each behavior, with several cases (a table or a loop), is better than many tiny tests.
- Test through the public interface of the module, not its private helpers.
- Keep slow tests (network, other processes, large data, a real device) for the main paths only.
