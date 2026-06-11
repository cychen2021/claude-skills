# Redaction catalog

Reference for what counts as redactable, how to judge each class, and how to
handle it. Loaded on demand — `scan.py` flags candidates; this file explains
the judgment calls.

## Table of contents

- [AI assistant artifacts](#ai-assistant-artifacts)
- [Personal information](#personal-information)
- [Caller-supplied identifiers](#caller-supplied-identifiers)
- [Self-authored git submodules](#self-authored-git-submodules)
- [Distinguishing real findings from noise](#distinguishing-real-findings-from-noise)
- [Handling decisions: delete / sanitize / defer](#handling-decisions-delete--sanitize--defer)
- [Things that look redactable but usually are not](#things-that-look-redactable-but-usually-are-not)

## AI assistant artifacts

These reveal that an AI coding agent was used, which a double-blind paper
review may require hiding.

| Class | Examples | Default action |
|---|---|---|
| Agent rule files | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.windsurfrules`, `copilot-instructions.md`, `.clinerules`, `.aider.conf.yml` | Delete (or defer if you still rely on it — e.g. `CLAUDE.md`) |
| Agent config/state dirs | `.claude/`, `.cursor/`, `.aider*`, `.continue/`, `.codeium/`, `.github/copilot/` | Usually **defer** — needed for ongoing assistance |
| Symlinks to rule files | `AGENTS.md -> CLAUDE.md` | Delete the symlink; deciding on the target separately |
| AI commit trailers | `Co-Authored-By: Claude`, `🤖 Generated with Claude Code` | History rewrite — **defer**, record in report |
| Editor AI integration | `.vscode/settings.json` keys like `github.copilot.*`, recommended-extensions referencing `anthropic.claude-code` | Sanitize (remove those keys) or defer |
| AI tooling in build | `npm install -g @anthropic-ai/claude-code` lines in a `Dockerfile`/devcontainer | Sanitize if the image is published with the paper artifact |

## Personal information

| Class | Examples | Default action |
|---|---|---|
| Package metadata authors | `authors = [{ name = "...", email = "..." }]` in `pyproject.toml`; `author`/`contributors` in `package.json` | Sanitize to a neutral placeholder (e.g. `Anonymous <anon@example.com>`) |
| Email addresses | personal addresses in docs, configs, comments | Sanitize / remove |
| Home-dir paths | `/home/<user>/...`, `/Users/<user>/...`, `C:\Users\<user>\...` | Sanitize to a relative path or generic placeholder |
| Embedded secrets | API keys, tokens (`ghp_…`, `sk-…`, `AKIA…`), passwords | **Remove immediately**; rotate the credential |
| Remote URLs with account | `github.com/<personal-account>/...` in `.gitmodules`, README badges | Sanitize to a neutral org or note in report |
| Dotfiles with identity | shell prompts, git config embedded in `.devcontainer/dotfiles/` | Review; usually template content, sanitize only real identity |

## Caller-supplied identifiers

The user knows identifiers the scanner cannot guess: their **name**, **username**,
and the names of **self-authored packages/namespaces** they reuse across projects
(e.g. a personal `phdkit` library). Always ask for these up front and pass them
via `scan.py -i <term>` (repeatable). The `-i` matcher is case-insensitive and
fires on word-ish boundaries, so `-i phdkit` also flags `phdkit.foo`,
`import phdkit`, and `phdkit_utils`.

| Where the identifier hides | Examples | Default action |
|---|---|---|
| Package/dist name | `name = "phdkit"`, `phdkit/` source dir | Rename to a neutral package + update all imports, or defer if invasive |
| Import / namespace refs | `import phdkit`, `from phdkit.x import y` | Rename together with the package (consistency matters) |
| Dependency declarations | `phdkit @ git+https://github.com/<you>/phdkit` in `pyproject.toml`/`requirements.txt` | Sanitize URL + name, or vendor the dep |
| Prose / comments / docstrings | "built on my phdkit helpers" | Sanitize wording |

Renaming a package touches many files at once. If the rename is large or risky,
**defer** it (record in `x_not_redacted.md`) rather than half-renaming and breaking
imports.

## Self-authored git submodules

`scan.py` parses `.gitmodules` and lists every submodule with its URL. A submodule
leaks identity in three places, each needing its own decision:

1. **The remote URL** — `github.com/<your-account>/<repo>` names you directly.
2. **The submodule name / path** — may embed a personal package name.
3. **The submodule's *contents*** — its own files may carry your name, emails, or
   AI artifacts. The scanner does **not** descend into submodule working trees;
   to redact those, run `scan.py` again with the submodule dir as `ROOT`.

| Situation | Default action |
|---|---|
| Submodule is a self-authored package (e.g. `phdkit`) needed to build | Vendor it (copy contents in, drop the submodule) and sanitize names, or defer |
| Submodule is dev-only tooling not needed by reviewers (e.g. a skills repo) | Remove the submodule entry, or defer if still in use |
| Submodule is a legitimate third-party dependency | Keep; note only if its URL form reveals a fork under your account |

Removing/altering submodules touches `.gitmodules`, `.git/config`, and the gitlink
entry — often better to **defer** and let the human run `git submodule deinit` /
`git rm` deliberately. Always at least record the submodule URL in the report.

## Distinguishing real findings from noise

The scanner is deliberately broad. Apply these rules before acting:

- **`ai-model-mention` on dependencies is usually legitimate.** `anthropic>=0.52`
  / `openai>=1.70` in `pyproject.toml`, or `from anthropic import ...` in `src/`,
  describe what the *software* does — not who built it. For a paper whose subject
  *is* AI agents, these mentions are expected content, **not** a reviewer-identity
  leak. Keep them. Only redact mentions that reveal *your* use of an assistant
  (commit trailers, your editor config, agent rule files).
- **`secret` matches are often false positives.** `resolve_github_token(...)`,
  `secrets.token_hex(4)`, or a variable named `token` are code, not leaked
  credentials. A real finding is a long literal string assigned to a
  key/token/password. Verify by reading the line.
- **`email` may be upstream.** `dev@example.com` test fixtures or library author
  emails are fine; your own address is not.
- **Home paths in generated docs** (e.g. checkpoint files, logs) leak a username
  but may be in throwaway artifacts you will delete wholesale anyway.

## Handling decisions: delete / sanitize / defer

For each confirmed finding choose one:

1. **Delete** — the whole file/dir is an artifact with no other value
   (e.g. `AGENTS.md`, a stray `.cursorrules`). Use `git rm` if tracked.
2. **Sanitize** — the file must stay but a span must change (author field,
   home path, editor config key). Edit in place with a neutral placeholder.
3. **Defer** — cannot safely act now. Record in `x_not_redacted.md` with the
   reason. Reasons that warrant deferral:
   - You rely on it for ongoing work (`.claude/`, `CLAUDE.md`).
   - It requires git history rewrite (commit trailers, author in past commits).
   - It is outside the working tree (git remote config, LFS storage, CI secrets).
   - Ambiguous ownership — let the human decide.

## Things that look redactable but usually are not

- Names of AI libraries the project legitimately depends on or studies.
- `example.com` / `localhost` / placeholder credentials in tests and `*.example` files.
- `vscode` as a username inside a devcontainer image (it is the standard
  container user, not your identity) — though still worth a note if the image
  ships with the artifact.
- License files naming an institution (that is intended attribution; redact only
  if the venue requires anonymizing it).
