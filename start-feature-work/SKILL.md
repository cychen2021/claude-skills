---
name: start-feature-work
description: Start work on a feature, which means adding a new feature, changing an existing one, or removing one. Creates a branch, plans the work, opens a draft PR and then begins the work. Use when the user asks to add, change, extend, rework, deprecate or remove a feature, for example "Let's add X", "Change how Y works", "Remove Z", or "Start work on ...".
---

# Start Feature Work

Start one piece of feature work: add a feature, change one, or remove one. `/finish-feature-work` ends it.

## 1. Know the kind of work

Decide from the request which kind it is, and ask only if the request does not say:

- **Add**: new behavior.
- **Change**: existing behavior works differently, is extended, renamed or reorganized.
- **Remove**: a feature, or part of one, goes away.

Ask about real gaps in the request (expected behavior, limits, what must stay) with `AskUserQuestion`. Do not ask about things the code or `CLAUDE.md` answers.

## 2. Create the branch

Use the project's branch convention if it has one (look at `git branch -a`). Otherwise use `feature/<short-kebab-name>`, for all three kinds. Branch from an up-to-date default branch.

## 3. Plan

Plan unless the user passed `--skip-plan` or the work is a few lines.

1. Read the code the work touches, and the project's `CLAUDE.md` and `docs/`.
2. For **change** and **remove**, find every use of what changes or goes away: code, tests, docs, config, CLI help, examples and fixtures. Search for each name in all its forms (type, function, CLI flag, config key, file name). The list of places is part of the plan.
3. Say if the work breaks something users depend on (public API, CLI, config or file format). If it does, say what users must do instead.
4. Write the plan as a short message: the files to change, the tests to add or change, the docs to update, and the order of the commits.
5. Decide if the work is one PR or a stack of PRs, and say which in the plan. Use a stack (the `gh-stack` skill) when the work is large (roughly over 800 changed lines), or when it has parts that a reviewer can read and merge one at a time, for example a preparatory change that other parts use, or a second feature that builds on the first. Each PR of the stack is one part that builds and passes the checks alone. Put each part in the order of its dependencies, the base first. Use one PR when the parts make sense only together.

Wait for the user's approval before changing code. `--skip-plan` counts as approval: give a short sketch of the approach and go on.

## 4. Open a draft PR

For a stack, open the draft PR of the first part now, and add each next part with `gh stack add <name>` when you start it (the `gh-stack` skill). Each part gets its own draft PR, with the plan of that part. Link the PRs into a stack (`gh stack submit --auto --draft`, or `gh stack link` for branches made with plain git).

Open the PR as a draft before the first code change, so CI runs on each push and the plan stays on record. Skip this only if the project says small changes go straight to the default branch and this is one of them.

```bash
git commit --allow-empty -m "Start <work name>" -m "<the plan as short bullets>"
git push -u origin <branch>
gh pr create --draft --title "<title under 70 chars>" --body "$(cat <<'EOF'
## Summary
- 1 to 3 bullets on what the work does. For a removal, say whether it breaks users.

## Plan
- The approved plan as bullets.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Do not request a review on the draft (no `@codex review`, no reviewers). `/finish-feature-work` requests it once the work is done. Give the user the PR link in one line.

## 5. Do the work

- Follow the project's `CLAUDE.md`. It overrides anything here.
- Add or update tests together with the code they test. Add a test only when it is worth its cost by `../trim-tests/test-value.md` (the `trim-tests` skill). Change or extend an existing test before you write a new one.
- For **remove**: delete cleanly. Leave no commented-out old code, no TODO that names the removed feature, and no dependency that only the removed code used.
- In a stack, a change to a lower part goes on the branch of that part. Then rebase the parts above it (`gh stack rebase --upstack`) and push.
- One commit per concern. A large change is several commits, for example a preparatory rename that changes no behavior, then each part with its tests, then docs that span them. Each commit must build.
- Commit and push each unit of work as soon as it passes the project's checks. Do not leave finished work uncommitted at the end of a session: uncommitted changes are lost on a branch switch, `git clean` or a new session. If the work is not ready to commit, `git stash` it.

When the work is done, use `/finish-feature-work`.
