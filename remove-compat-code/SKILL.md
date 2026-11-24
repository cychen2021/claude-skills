---
name: remove-compat-code
description: Find and remove defensive code that keeps old versions working (migrations of old config or data formats, aliases of renamed keys, flags and commands, fallbacks to old paths or names, cleanup of files that old versions left, shims for old protocol versions) in a project that promises no compatibility, for example an early 0.x project. Lists what it finds, removes it, runs the checks and commits. Use when the user asks to remove, trim or clean up compatibility, migration, legacy or defensive code, or says that the project needs no backward compatibility.
---

# Remove Compatibility Code

In a project that promises no compatibility (an early `0.x` version, an internal tool, a prototype), code that keeps old versions working costs more than it gives. Each user runs the current version, and an old file or setting is easy to fix by hand. Such code grows with each change, it hides the real format of the data, and it has bugs of its own that nobody sees, because nobody runs it.

Remove it. When the current version meets something old, it fails with a clear error, or it treats it like any other unknown input.

## 1. Check the policy

Read `CLAUDE.md`, the README and the docs for a rule about versions and compatibility.

- If they say that the project promises no compatibility, or the user says so, go on.
- If they promise compatibility (a stable `1.x` with semantic versioning, a published file format, a public API with users outside the project), stop. Tell the user which promise you found, and ask what to do.
- If they say nothing, ask the user before you go on, and offer to add the rule to `CLAUDE.md`.

## 2. Know the scope

- No argument: the whole repository.
- A branch or a base (for example `main`): only the code that the branch added or changed.
- A path: only that file or directory.

## 3. Find the code

Look for code that exists only because an older version of this project did something else. Search for words such as `old`, `legacy`, `deprecated`, `compat`, `migrate`, `migration`, `fallback`, `alias`, `previous`, `former`, `older versions`, `backward`, `v1`, `upgrade`, `.old`, `.bak` (in code, comments, docs and scripts), and read the history of renames (`git log --diff-filter=R`, commit messages with "rename" or "move"). The kinds:

- **Migration of data or settings**: reading an old file name, format or key and writing the new one; renaming the old file; version fields in files that only exist to pick a migration.
- **Aliases**: old names of settings, keys, flags, subcommands, environment variables, enum values or API items that still work next to the new ones; `#[serde(alias)]`, hidden CLI aliases, deprecated re-exports.
- **Fallbacks**: looking in an old directory, socket, registry key or path when the new one is missing; trying an old protocol or message form.
- **Cleanup of old installs**: install or uninstall steps that remove files, services, registrations, links or caches that only an older version made.
- **Messages about old versions**: warnings or errors that name a setting or format "of older versions", or tell the user how to upgrade from one.
- **Their tests, test data and docs**: tests of the migration, fixtures of the old format, doc sections about upgrading from an old version.

Do not remove these. They are not compatibility code:

- Checks at a trust boundary of the current version: validation of user input, of files the user edits, of network data.
- Handling of real conditions of the current version: a missing file at the first start, a lost connection, a full disk.
- A version check that refuses a mismatch (for example between a client and a server). It makes removing compatibility safe.
- Support for old versions of other software (an old OS, compiler or library) that the project states it supports.
- A warning about unknown settings in general. Keep it, but remove any words in it that blame older versions.

If you are not sure whether some code is for an old version, read the commit that added it (`git log -S`, `git blame`).

## 4. List and ask

Show a short list, grouped by file. Each line: what to remove, and the old version or format that it serves. Example:

```text
server/src/settings.rs
  remove  move_old_file + its test        settings.json of 0.1
  remove  serde alias "switch_key"        name of 0.1
scripts/install.py
  remove  delete ~/Library/Logs/Old.log   log path of 0.1
  keep    unknown-key warning (reword)    general check of user input
```

Always wait for the user's approval before you remove anything, also when the user already asked you to remove such code. The user can remove lines from the list.

## 5. Remove

- Remove the code, and everything that only it used: helpers, constants, imports, dependencies (a parser of the old format), tests, test data, doc sections and comments that mention the old version.
- Make the current path the only path. Do not leave a `TODO`, an empty branch or a comment that says something was removed.
- Do not change the current behavior or format. If removing a migration means that an old file is now ignored or rejected, that is the intended result. Make sure the error, if any, names the file.
- If the user's own data on this computer is in an old form, tell the user how to convert it by hand, or convert it for them if they ask. Do not keep code for it.

## 6. Check

Run the project's gate (the format, check and test commands in `CLAUDE.md`, or the usual tools of the language). All must pass. Then search once more for the words of step 3, and for the names of the removed items, so that nothing still refers to them.

## 7. Commit

Follow the project's commit rules for the message, for example "Remove the migration of `settings.json`". The body lists what was removed. Make one commit on the current branch unless the user asks for something else, and push it if the branch has a remote.

## 8. Report

List what was removed, what you kept on purpose (with the reason), and anything the user must do by hand (for example an old setting on their computer that is now ignored).
