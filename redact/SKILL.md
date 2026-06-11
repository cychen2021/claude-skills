---
name: redact
description: Redact personal information (author names, emails, home-dir paths, secrets), caller-supplied identifiers (your name, username, self-authored package/namespace names like phdkit), self-authored git submodules, and AI-assistant artifacts (AGENTS.md, CLAUDE.md, .cursorrules, agent config dirs, AI commit trailers, AI editor config) from a repository to prepare an anonymized paper-review / artifact submission. Anything that cannot be safely deleted yet — because it is still relied upon, needs a git-history rewrite, requires a package rename, or has ambiguous ownership — is logged to x_not_redacted.md for the human to handle. Use when the user asks to anonymize, redact, scrub, or de-identify a repo for double-blind review or artifact release.
---

# Redact

## Overview

Prepare a repository for anonymous review by removing two classes of identifying
content: **personal information** (author fields, emails, home-dir paths,
embedded secrets) and **AI-assistant artifacts** (agent rule files like
`AGENTS.md`/`CLAUDE.md`, AI config dirs, AI commit trailers, AI editor config).
Whatever cannot be safely removed now is recorded in `x_not_redacted.md` so the
human can finish the job.

This skill is general — it works on any repository, not just the one it ships in.

## Workflow

### 0. Ask for caller-supplied identifiers

Before scanning, ask the user for the identifiers the scanner cannot guess:

- their **name** and any handles,
- their **username(s)** (appear in home paths, remote URLs),
- names of **self-authored packages/namespaces** they reuse across projects
  (e.g. a personal `phdkit` library, often pulled in as a git submodule).

Pass each as `-i <term>`. These reuse across the user's projects, so always ask
even if this repo looks clean.

### 1. Scan

Run the read-only scanner from the repo root being redacted:

```bash
scripts/scan.py <repo-root> -i <name> -i <username> -i <package>   # add --json for tooling, --full for all matches
```

It reports name-based AI artifacts, git submodules (from `.gitmodules`), and
content findings grouped by pattern (including the `IDENTIFIER` hits for your
`-i` terms). It **never modifies anything** — every result is a candidate. The
scanner does not descend into submodule working trees; to redact a submodule's
own contents, run it again with that submodule dir as the root.

### 2. Triage each finding

Findings are deliberately broad; apply judgment. Read
[references/catalog.md](references/catalog.md) for the per-class rules. Key
heuristics:

- **AI library/model mentions are usually legitimate** (`anthropic>=0.52`,
  `import openai`, prose about models) — they describe the software, not your use
  of an assistant. Keep them. Redact only mentions that reveal *you used an
  assistant*: commit trailers, your editor's AI config, agent rule files.
- **Most `secret` hits are false positives** (`resolve_github_token()`,
  `secrets.token_hex(...)`, a var named `token`). A real leak is a long literal
  assigned to a key/password. Read the line before acting.
- **Emails / home paths** that are test fixtures (`dev@example.com`) or the
  standard container user (`/home/vscode`) are usually fine.
- **`IDENTIFIER` hits in a package name/namespace** (e.g. a `phdkit` dist name or
  `import phdkit`) mean a rename, which touches many files at once — sanitize them
  together for consistency, or defer the whole rename if invasive.
- **Submodules**: judge the remote URL, the name/path, *and* the submodule's own
  contents separately. See [references/catalog.md](references/catalog.md).

### 3. For each confirmed finding, choose one action

- **Delete** — file/dir is a pure artifact (`git rm` if tracked, else remove).
- **Sanitize** — file stays, replace the offending span with a neutral
  placeholder (e.g. author → `Anonymous <anon@example.com>`, home path → relative
  path, drop the AI editor-config keys).
- **Defer** — cannot act safely now. **Do not delete; record it** (step 4).

Default to **defer, not delete** whenever you are unsure, when the user still
relies on the item, or when ownership is ambiguous. The user explicitly handles
deferred items themselves later.

Always defer (never auto-act on) these unless the user says otherwise:
- `.claude/` and any agent config dir the user is actively using for assistance.
- `CLAUDE.md` / agent rule files the user still relies on.
- Anything needing **git history rewrite** (AI commit trailers, author identity
  in past commits) — out of scope for a working-tree edit.
- Anything **outside the working tree**: git remote URLs, LFS storage, CI secrets.
- **Git submodules** — removing/re-pointing one touches `.gitmodules`, `.git/config`,
  and the gitlink; let the human run `git submodule deinit` / `git rm` deliberately.
- **Large package renames** — renaming a self-authored package risks breaking
  imports; defer unless the user confirms the rename.

### 4. Record deferrals in x_not_redacted.md

Create or update `x_not_redacted.md` at the redacted repo's root. For every
deferred item, append a row to the table with a concrete reason and the suggested
action so the human can finish. Use this structure:

```markdown
# Not yet redacted

Items found during redaction that were **not** removed automatically. Review and
handle each before submitting for review.

| Item | Type | Reason deferred | Suggested action |
|------|------|-----------------|------------------|
| `.claude/` | AI config dir | Still used by Claude Code to assist the author | Delete manually before submission |
| `CLAUDE.md` | AI rule file | Still relied upon during development | Delete manually before submission |
| AI commit trailers in git log | AI metadata | Requires history rewrite | `git rebase`/`filter-repo` to strip `Co-Authored-By` lines |
| `phdkit` submodule (`.gitmodules`, URL `github.com/<you>/phdkit`) | Self-authored submodule | Personal account in URL; removal touches gitlink | Vendor contents + sanitize name, or `git submodule deinit` |
| `phdkit` package name + `import phdkit` (N files) | Self-authored namespace | Rename risks breaking imports | Rename package to neutral name in one pass |
```

Keep entries specific (name the file and line where useful). If the file already
exists, merge rather than overwrite.

### 5. Report

Summarize to the user: what was deleted, what was sanitized (with the replacement
used), and what was deferred to `x_not_redacted.md` and why. Do not claim the repo
is fully anonymized while deferred items remain — say what is left.

## Notes

- The scanner uses only the Python standard library; no install needed.
- It scans git-tracked files when run inside a git work tree (respecting
  `.gitignore`), otherwise walks the tree skipping heavy dirs.
- Run the scan again after sanitizing to confirm findings are resolved.
