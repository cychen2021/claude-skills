---
name: finish-feature-work
description: Finish feature work (an added, changed or removed feature) started with start-feature-work. Runs the project's checks and tests, checks that nothing still uses removed or renamed items, updates the docs, splits the work into commits, pushes, marks the draft PR ready, requests one Codex review, waits for it in the background and handles its comments. Use when the feature work is done, or when the user says "finish the feature", "wrap up", "make the PR ready" or similar.
---

# Finish Feature Work

Finish the work that `/start-feature-work` started.

## 1. Checks and tests

Run the project's own gate: the commands its `CLAUDE.md` names (for example `format.py`, `type_check.py`, `runtest.py`, a `justfile` or a `Makefile` target). If it names none, use the usual formatter, linter, type checker and test runner of the language. Fix every failure. Do not skip or weaken a failing test to get the PR out.

Then read your own diff (`git diff <base>...HEAD` plus uncommitted changes) for what tools do not catch: debug prints, missing doc comments on public items, error messages without context, and code that breaks a `CLAUDE.md` rule.

## 2. Leftover references (change and remove only)

When the work renamed, moved or removed anything, search the whole repo for each old name in all its forms (type, function, module, file, CLI flag, config key):

```bash
rg -i '<old name>'
```

Every hit must be updated or deleted: code, tests, docs, examples, fixtures, CLI help and config samples. Also remove any dependency that only the removed code used. Run the checks again after the cleanup.

## 3. Docs

From the diff, find what users or developers see that changed (API, CLI, config, file formats, setup steps, layout) and update the docs that describe it: `README` files, `CLAUDE.md`, `docs/`. For a removal, delete the old sections. Do not leave "this used to do X" notes. If no docs need a change, say so.

If the work breaks something users depend on and the project keeps a version or a changelog, update them.

## 4. Commit

Follow the commit rules in the project's `CLAUDE.md`. Commits made during the work stay. Split what is still uncommitted into one commit per concern when it does more than one thing or is large (roughly over 300 lines or 10 files):

- a preparatory move, rename or extraction that changes no behavior, first
- each independent part, with its own tests
- for a removal, removing the uses before removing the definitions
- docs that span several parts, last

Keep tests with the code they test, and generated files with their source. Each commit must build. Stage by path. When one file holds two concerns, stage one concern's hunks with a filtered patch (`git diff <file>` into a temporary file, delete the other hunks, `git apply --cached`), because `git add -p` is not available. Never rewrite pushed commits. After committing, check `git log --stat <base>..HEAD`: each headline describes only its own commit, and no commit is empty by mistake.

## 5. Push and mark the PR ready

```bash
git push
gh pr view --json number,url,isDraft
```

If a draft PR exists, rewrite its title and body for the finished work, then mark it ready (before the review request, because Codex can skip drafts):

```bash
gh pr edit <pr> --title "<title under 70 chars>" --body "<body>"
gh pr ready <pr>
```

If there is no PR, create one (not a draft). Body:

```markdown
## Summary
- 1 to 3 bullets on what changed.

## Changes
- One bullet for each area.

## Breaking changes
- Only if users must act. Say what to do instead.

## Test plan
- [x] Project checks and tests pass
- [ ] Manual steps, if any

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## 6. Request one Codex review

Request Codex's review unless the user said not to. Do not request GitHub Copilot's review (its credits are kept for other work). Do not run a local `codex review` in its place.

```bash
gh pr comment <pr> --body "@codex review"
```

Request it once per PR. Never request it again after pushing fixes, or the review and fix cycle never ends. A second review is the user's decision. Never write `@codex` in a reply to its comments: a mention is a new instruction to Codex.

Codex answers as `chatgpt-codex-connector[bot]`. Within seconds it adds a 👀 reaction and posts a placeholder comment. The placeholder is not the review. The review is one of:

- a PR review (`state` `COMMENTED`) whose body starts with `<!-- codex-review-receipt:v1 -->`, with inline comments, or
- a plain PR comment with that marker saying "Didn't find any major issues".

If no 👀 or placeholder appears within a few minutes, the Codex app is probably not installed on the repo. Tell the user.

## 7. Wait in the background

Start this right after the request, with the Bash tool's `run_in_background: true`, tell the user in one line that you are waiting, and stop. Do not poll in the foreground.

```bash
since=$(date -u +%Y-%m-%dT%H:%M:%SZ)
bot='chatgpt-codex-connector[bot]'
for i in $(seq 60); do                      # every 30 s, for up to 30 minutes
  r=$(gh api repos/:owner/:repo/pulls/<pr>/reviews \
        --jq "[.[] | select(.user.login == \"$bot\" and .submitted_at >= \"$since\")] | length")
  c=$(gh api repos/:owner/:repo/issues/<pr>/comments \
        --jq "[.[] | select(.user.login == \"$bot\" and .created_at >= \"$since\" and (.body | contains(\"codex-review-receipt\")))] | length")
  [ "${r:-0}" -gt 0 ] && { echo "codex review arrived with findings"; exit 0; }
  [ "${c:-0}" -gt 0 ] && { echo "codex review arrived: no major issues"; exit 0; }
  sleep 30
done
echo "no codex review after 30 minutes"; exit 1
```

- **Findings**: go on to step 8 without asking.
- **No major issues**: say so and go to step 9.
- **Nothing after 30 minutes**: stop waiting and go on without it. Tell the user the review did not arrive. Do not say it came back empty.

Do not poll for human reviewers. Tell the user the PR is ready and let them say when their feedback is in.

## 8. Handle the review comments

Fetch both parts of the review:

```bash
gh api repos/:owner/:repo/pulls/<pr>/comments --jq '.[] | {id, path, line, body}'
gh api repos/:owner/:repo/pulls/<pr>/reviews --jq '.[] | {user: .user.login, state, body}'
```

For each comment:

1. Check the claim against the code before acting. Automated reviews make confident false claims. If it is wrong, change nothing and say why.
2. If it is real, fix it and run the checks again. Add a test only if the bug deserves one by `../trim-tests/test-value.md` (the `trim-tests` skill), and then first try to add a case to an existing test.
3. Commit (mention "From Codex review on #<pr>" in the body) and push.
4. Reply on the thread (what changed, or why it does not apply), then resolve the thread. Resolve only threads you acted on:

```bash
owner=$(gh repo view --json owner --jq .owner.login)
repo=$(gh repo view --json name --jq .name)
gh api graphql -f query='
  query($owner:String!,$repo:String!,$pr:Int!){
    repository(owner:$owner,name:$repo){ pullRequest(number:$pr){
      reviewThreads(first:100){ nodes{ id isResolved
        comments(first:1){ nodes{ path line body } } } } } } }' \
  -f owner="$owner" -f repo="$repo" -F pr=<pr>
gh api graphql -f query='
  mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ id isResolved } } }' \
  -f id=<thread-id>
```

If another Codex review arrives after your push (for example an automatic one), tell the user and leave it to them.

## 9. Hand over

When the checks pass and every comment is fixed or answered, give the user the PR link, say what the checks and the review found, and ask them to merge (or use `/merge-pr`).
