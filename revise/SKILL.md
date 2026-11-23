---
name: revise
description: Apply the user's checkpoint review comments from x_review_comments.md, one section at a time (for example "General Comments - Round 2" or "Comments on Tests"). Answers the questions in the comments, makes the requested changes across the whole codebase, runs the checks, records what was done in checkpoints/cp-YYMMDD/revision-<section>.md, updates review.md and marks the section done. Use when the user says "/revise", "revise according to ...", "apply the review comments" or similar on a checkpoint branch.
---

# Revise

Apply one section (or several) of the user's review comments on a checkpoint made by `/make-cp`.

## 1. Find the checkpoint and the comments

- Checkpoint: from the branch name `checkpoints/cp-<date>`, or else the newest `checkpoints/cp-*/`. Work in that branch's worktree (`.worktrees/cp-<date>`) if there is one.
- Comments: `x_review_comments.md` at the root of the worktree. If it is missing, ask the user where the comments are.
- Sections to do: the ones the user names. If the user names none, do every section that is not empty and not marked `[DONE]`. Ignore the rest of the file, including text the user adds while you work, unless they ask you to read it.
- References such as "Priority 3", "Tests - Priority 3" or "F2" point into `checkpoints/cp-<date>/review.md`. In checkpoints made before `review.md` existed, they point into `code-review-guidelines.md`, `doc-review-guidelines.md` or `test-audit-guidelines.md`.
- A comment may point to another file, such as an `x_*.md` plan or a paper. Read it. It is part of the comment.

## 2. Sort the comments

Put each comment into one of three groups:

- **Requests**: clear changes. Do them.
- **Questions** ("Why is X named like this?", "What does Y do now?", "Is Z still used?"): answer them from the code. If the answer shows a change the user would clearly want, propose it. Make it only if the comment also asks for it ("... If not, delete it").
- **Unclear**: a comment with more than one sensible reading, or two targets that collide (for example two files renamed to the same name). Ask with `AskUserQuestion` before changing anything that depends on it.

If the section is large (for example a rename list or a restructure), write the plan in the revision file first (step 3) and tell the user in a few lines what you will do. Wait only if something is unclear.

## 3. Start the revision file

Create `checkpoints/cp-<date>/revision-<section>.md`, named after the section: `revision-general-r1.md`, `revision-tests.md`, `revision-code.md` and so on. If that name exists from an earlier round, add `-r2`, `-r3`.

```markdown
# Revision of cp-<date>: <section heading>

Date: YYYY-MM-DD

## Comments

The user's comments in short, each with the priority or F number it refers to.

## Answers

Answers to the questions, each with the evidence (paths, lines, commands run).

## To do

- [ ] One line for each change, with the paths.

## Done

Filled in as the work goes on: what changed, by file or by group, with commit hashes.

## Not as asked

Anything done differently from the comment, and why. Write "None" if there is nothing.

## Checks

The gate commands and their results.
```

Write it before the first change and keep it current. It is the record that survives a lost session.

## 4. Make the changes

- Follow `CLAUDE.md` and the project's writing rules for every name, message and doc you touch.
- A rename or a change of term applies everywhere: code, tests, test file names, fixtures, docs, CLI help and messages, config keys, comments and `CLAUDE.md`. Search the old term in all its forms (`rg -i`) when done. Leave a hit only when it means something else, and say so in "Not as asked".
- When a comment sets a rule ("tests must not call private helpers", "name files by what they do"), apply it to the whole codebase, not only to the place the comment names.
- One commit per concern, each one building. Push after each commit.
- Tick the to-do item and fill in "Done" as each change lands.

## 5. Check

Run the project's gate (the check and test commands in `CLAUDE.md`). Fix what fails. Do not weaken or delete a test to make it pass unless a comment asks for that. Write the results under "Checks".

## 6. Close the section

- Update `checkpoints/cp-<date>/review.md`: mark each problem and priority that this revision settled, for example `(done, see revision-tests.md)`. If the revision changed something that `review.md` describes (a path, a name, a claim), correct it.
- Add `[DONE]` to the end of each finished section heading in `x_review_comments.md`.
- Commit the revision file and `review.md` with the last change, or in their own commit, and push.
- Tell the user: the answers to their questions (in full, not only in the file), what changed, anything not done as asked, and the check results.
