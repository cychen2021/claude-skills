#!/usr/bin/env python3
"""Read-only scanner for redaction candidates in a repository.

Reports several classes of findings, never modifies anything:

  AI         -- AI assistant artifacts (agent rule files, AI config dirs,
                AI-authored commit trailers, model/provider mentions).
  PERSONAL   -- personal information (author fields, home-dir paths with a
                username, email addresses, phone numbers, personal home page /
                social / academic profile URLs, embedded secrets/tokens,
                personal account names in remote URLs).
  IDENTIFIER -- caller-supplied personal identifiers (your name, username, or
                self-authored package/namespace names such as `phdkit`) found
                anywhere in the tree.
  SUBMODULE  -- git submodules and references to them; self-authored submodules
                often leak identity via their name, namespace, or remote URL.

Usage:
    scan.py [ROOT] [--json] [--full] [-i TERM ...]

  ROOT             repository root to scan (default: current directory).
  --json           emit machine-readable JSON instead of the grouped report.
  --full           do not truncate the per-pattern match list (default: 20).
  -i, --identifier personal identifier to flag everywhere (repeatable). Pass
                   your name, username, and any self-authored package/namespace
                   name. Matched case-insensitively on word-ish boundaries, so
                   `-i phdkit` also catches `phdkit.foo` and `import phdkit`.

The scanner respects .gitignore by scanning only git-tracked files when ROOT
is a git work tree; otherwise it walks the tree skipping common heavy dirs.
Binary files and very large files are skipped for content matching.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- name-based detection -------------------------------------------------

# Files whose *name* marks them as AI-assistant artifacts. Matched case-
# insensitively against the basename.
AI_FILE_NAMES = {
    "agents.md",
    "claude.md",
    "gemini.md",
    "qwen.md",
    "codex.md",
    ".cursorrules",
    ".windsurfrules",
    ".aider.conf.yml",
    ".aiderignore",
    "copilot-instructions.md",
    ".clinerules",
    ".goosehints",
}

# Directories that hold AI-assistant config/state. Matched against any path
# component.
AI_DIR_NAMES = {
    ".claude",
    ".cursor",
    ".aider",
    ".continue",
    ".codeium",
    ".windsurf",
    ".github/copilot",
    ".gemini",
    ".opencode",
    ".codex",
}

# glob suffixes that are AI artifacts regardless of directory
AI_FILE_GLOBS = (".aider*",)

# --- content-based detection ----------------------------------------------


@dataclass
class Pattern:
    name: str
    kind: str  # "AI" or "PERSONAL"
    regex: re.Pattern[str]
    note: str = ""


def _content_patterns(identifiers: list[str] | None = None) -> list[Pattern]:
    pats: list[Pattern] = []
    for term in identifiers or []:
        # word-ish boundary so `phdkit` also catches `phdkit.foo`, `import phdkit`,
        # `phdkit_utils`, but not `xphdkit`. Allow trailing _.- joins.
        esc = re.escape(term)
        pats.append(
            Pattern(
                f"identifier:{term}",
                "IDENTIFIER",
                re.compile(rf"(?i)(?<![A-Za-z0-9]){esc}(?![A-Za-z0-9])"),
                f"caller-supplied identifier '{term}' (name / username / self-authored package)",
            )
        )
    pats.extend([
        Pattern(
            "ai-commit-trailer",
            "AI",
            re.compile(
                r"(?i)(co-authored-by:\s*(claude|copilot|cursor|gpt|chatgpt|gemini|codex)"
                r"|generated with \[?claude code"
                r"|🤖 generated with"
                r"|with the help of (claude|chatgpt|copilot|an? (ai|llm)))"
            ),
            "AI authorship trailer / credit",
        ),
        Pattern(
            "ai-model-mention",
            "AI",
            re.compile(
                r"(?i)\b(anthropic|claude-(?:opus|sonnet|haiku|fable)|@anthropic-ai|"
                r"openai|gpt-4|gpt-3\.5|chatgpt|copilot|gemini-(?:pro|flash)|"
                r"us\.anthropic\.)\b"
            ),
            "AI provider / model reference (review: may be legitimate dependency)",
        ),
        Pattern(
            "email",
            "PERSONAL",
            re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            ),
            "email address (review: some may be upstream/library emails)",
        ),
        Pattern(
            "home-path",
            "PERSONAL",
            re.compile(r"(?:/home/|/Users/|C:\\\\Users\\\\)[A-Za-z0-9._-]+"),
            "absolute home path leaking a username",
        ),
        Pattern(
            "phone",
            "PERSONAL",
            # E.164 (+CC...) or grouped NANP-style numbers with separators;
            # require a separator or leading + so bare digit runs (years,
            # ids, ports) don't match.
            re.compile(
                r"(?<![\w.])(?:\+\d{1,3}[\s.-]?)?"
                r"(?:\(\d{2,4}\)[\s.-]?|\d{2,4}[\s.-])\d{2,4}[\s.-]\d{2,4}"
                r"(?:[\s.-]\d{2,4})?(?![\w.])"
            ),
            "phone number (review: may be a version range, id, or coordinate)",
        ),
        Pattern(
            "personal-url",
            "PERSONAL",
            # Personal home pages and social / academic profile links that
            # tie the repo to an individual. Generic project/dependency URLs
            # are NOT matched here (see ai-model-mention / submodule checks).
            re.compile(
                r"(?i)\b(?:"
                r"(?:https?://)?(?:www\.)?(?:"
                r"linkedin\.com/in/|twitter\.com/|x\.com/|"
                r"github\.com/|gitlab\.com/|bitbucket\.org/|"
                r"facebook\.com/|instagram\.com/|t\.me/|"
                r"mastodon\.[a-z]+/@|bsky\.app/profile/|"
                r"orcid\.org/|scholar\.google\.[a-z.]+/|"
                r"researchgate\.net/profile/|medium\.com/@|"
                r"dev\.to/|youtube\.com/@|youtube\.com/c/"
                r")[A-Za-z0-9._/-]+"
                r"|(?:https?://)?[A-Za-z0-9-]+\.(?:me|dev|io|page|blog|name|xyz)/?\b"
                r")"
            ),
            "personal home page / social or academic profile URL "
            "(review: project links may be legitimate)",
        ),
        Pattern(
            "secret",
            "PERSONAL",
            re.compile(
                r"(?i)(api[_-]?key|secret|token|password|passwd|access[_-]?key)\s*[:=]\s*"
                r"['\"]?[A-Za-z0-9_\-./+]{12,}"
                r"|gh[pousr]_[A-Za-z0-9]{20,}"
                r"|sk-[A-Za-z0-9]{20,}"
                r"|AKIA[0-9A-Z]{16}"
            ),
            "possible hardcoded secret / credential",
        ),
    ])
    return pats


# pyproject / package metadata author fields, checked separately so the
# finding can point at the specific key.
META_AUTHOR_RE = re.compile(
    r"(?im)^\s*(authors?|maintainers?|author_email|author-email)\b.*"
)

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".idea",
}

MAX_CONTENT_BYTES = 2_000_000


@dataclass
class Finding:
    pattern: str
    kind: str
    path: str
    line: int
    excerpt: str
    note: str = ""


@dataclass
class Submodule:
    name: str
    path: str
    url: str


@dataclass
class Report:
    ai_paths: list[str] = field(default_factory=list)  # name-based AI artifacts
    submodules: list[Submodule] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


def _parse_gitmodules(root: Path) -> list[Submodule]:
    gm = root / ".gitmodules"
    if not gm.is_file():
        return []
    try:
        text = gm.read_text("utf-8", "replace")
    except OSError:
        return []
    mods: list[Submodule] = []
    name = path = url = ""
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r'\[submodule "(.+?)"\]', s)
        if m:
            if name:
                mods.append(Submodule(name, path, url))
            name, path, url = m.group(1), "", ""
            continue
        if s.startswith("path"):
            path = s.split("=", 1)[1].strip() if "=" in s else ""
        elif s.startswith("url"):
            url = s.split("=", 1)[1].strip() if "=" in s else ""
    if name:
        mods.append(Submodule(name, path, url))
    return mods


def _git_tracked_files(root: Path) -> list[Path] | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    names = out.stdout.decode("utf-8", "replace").split("\0")
    return [root / n for n in names if n]


def _walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIR_NAMES for part in p.relative_to(root).parts):
            continue
        files.append(p)
    return files


def _is_binary(data: bytes) -> bool:
    return b"\0" in data[:8192]


def _name_is_ai(rel: Path) -> bool:
    name = rel.name.lower()
    if name in AI_FILE_NAMES:
        return True
    parts = [p.lower() for p in rel.parts]
    for d in AI_DIR_NAMES:
        segs = d.lower().split("/")
        for i in range(len(parts) - len(segs) + 1):
            if parts[i : i + len(segs)] == segs:
                return True
    for g in AI_FILE_GLOBS:
        if rel.match(g):
            return True
    return False


def scan(root: Path, full: bool, identifiers: list[str] | None = None) -> Report:
    report = Report()
    report.submodules = _parse_gitmodules(root)
    tracked = _git_tracked_files(root)
    files = tracked if tracked is not None else _walk_files(root)
    patterns = _content_patterns(identifiers)

    seen_ai_dirs: set[str] = set()
    for f in files:
        try:
            rel = f.relative_to(root)
        except ValueError:
            rel = f
        # name-based AI artifacts: collapse known AI dirs to the dir itself
        if _name_is_ai(rel):
            collapsed = None
            for d in AI_DIR_NAMES:
                segs = d.split("/")
                parts = list(rel.parts)
                for i in range(len(parts) - len(segs) + 1):
                    if [p.lower() for p in parts[i : i + len(segs)]] == [
                        s.lower() for s in segs
                    ]:
                        collapsed = str(Path(*parts[: i + len(segs)]))
                        break
                if collapsed:
                    break
            if collapsed:
                if collapsed not in seen_ai_dirs:
                    seen_ai_dirs.add(collapsed)
                    report.ai_paths.append(collapsed + "/")
            else:
                report.ai_paths.append(str(rel))

        # content matching
        if not f.is_file():
            continue
        try:
            if f.stat().st_size > MAX_CONTENT_BYTES:
                continue
            data = f.read_bytes()
        except OSError:
            continue
        if _is_binary(data):
            continue
        text = data.decode("utf-8", "replace")
        lines = text.splitlines()
        is_meta = rel.name in ("pyproject.toml", "package.json", "setup.py", "setup.cfg")
        for i, line in enumerate(lines, 1):
            for pat in patterns:
                m = pat.regex.search(line)
                if m:
                    report.findings.append(
                        Finding(
                            pattern=pat.name,
                            kind=pat.kind,
                            path=str(rel),
                            line=i,
                            excerpt=line.strip()[:160],
                            note=pat.note,
                        )
                    )
            if is_meta and META_AUTHOR_RE.match(line):
                report.findings.append(
                    Finding(
                        pattern="metadata-author",
                        kind="PERSONAL",
                        path=str(rel),
                        line=i,
                        excerpt=line.strip()[:160],
                        note="package metadata author/maintainer field",
                    )
                )
    return report


def _print_text(report: Report, full: bool) -> None:
    limit = None if full else 20
    print("=" * 70)
    print("REDACTION SCAN")
    print("=" * 70)

    print(f"\n## AI artifacts by name ({len(report.ai_paths)})")
    if report.ai_paths:
        for p in sorted(report.ai_paths):
            print(f"  [AI] {p}")
    else:
        print("  (none)")

    print(f"\n## Git submodules ({len(report.submodules)})")
    if report.submodules:
        print("  review each: self-authored submodules leak identity via name / url")
        for sm in report.submodules:
            print(f"  [SUBMODULE] {sm.path}  <-  {sm.url}")
    else:
        print("  (none)")

    by_pat: dict[str, list[Finding]] = {}
    for fnd in report.findings:
        by_pat.setdefault(fnd.pattern, []).append(fnd)

    print(f"\n## Content findings ({len(report.findings)})")
    if not report.findings:
        print("  (none)")
    for pat in sorted(by_pat):
        group = by_pat[pat]
        kind = group[0].kind
        note = group[0].note
        print(f"\n  [{kind}] {pat} — {note}  ({len(group)})")
        shown = group if limit is None else group[:limit]
        for fnd in shown:
            print(f"    {fnd.path}:{fnd.line}: {fnd.excerpt}")
        if limit is not None and len(group) > limit:
            print(f"    ... +{len(group) - limit} more (use --full)")

    print("\n" + "=" * 70)
    print("Findings are CANDIDATES. Apply judgment before deleting; record")
    print("anything you cannot safely remove in x_not_redacted.md.")
    print("=" * 70)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument(
        "-i",
        "--identifier",
        action="append",
        default=[],
        metavar="TERM",
        help="personal identifier to flag everywhere (repeatable): your name, "
        "username, or self-authored package/namespace name (e.g. -i phdkit)",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 2

    report = scan(root, args.full, args.identifier)

    if args.json:
        print(
            json.dumps(
                {
                    "ai_paths": report.ai_paths,
                    "submodules": [vars(s) for s in report.submodules],
                    "findings": [vars(f) for f in report.findings],
                },
                indent=2,
            )
        )
    else:
        _print_text(report, args.full)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
