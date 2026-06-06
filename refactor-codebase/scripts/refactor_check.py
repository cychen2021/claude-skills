#!/usr/bin/env python3
"""
Refactoring check script.

Detects the project's toolchain (Rust, Python, ...) and runs the matching
formatting, linting, type-checking, and test steps. Cross-platform: works on
Windows, Linux, and macOS.

Detection is based on marker files in the project root (or a directory passed
as the first CLI argument):

  - Rust:   Cargo.toml
  - Python: pyproject.toml / setup.py / setup.cfg

If both are present, every detected toolchain runs in turn. Use --lang to force
a single toolchain (e.g. --lang python).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# ANSI color codes (work on most terminals, including Windows 10+)
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

# Track overall status
warnings = 0
errors = 0


def run_command(cmd, description, cwd=None, capture_output=True):
    """Run a command and return the CompletedProcess (or None on failure)."""
    try:
        return subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=False,
            cwd=cwd,
        )
    except Exception as e:  # pragma: no cover - defensive
        print(f"{RED}✗ Error running {description}: {e}{NC}")
        return None


def have(tool):
    """Return True if an executable is on PATH."""
    return shutil.which(tool) is not None


# --------------------------------------------------------------------------- #
# Step helpers — each takes the resolved command string and a human label.
# --------------------------------------------------------------------------- #


def step_format(check_cmd, fix_cmd, label, cwd):
    """Check formatting and apply the fixer if needed."""
    global warnings
    print(f"{BLUE}Formatting ({label})...{NC}")
    result = run_command(check_cmd, label, cwd=cwd)
    if result and result.returncode != 0:
        print(f"{YELLOW}⚠ Formatting needed. Applying...{NC}")
        run_command(fix_cmd, label, cwd=cwd, capture_output=False)
        print(f"{GREEN}✓ Code formatted{NC}")
        warnings += 1
    else:
        print(f"{GREEN}✓ Code already formatted{NC}")
    print()


def step_lint(cmd, label, cwd):
    """Run a linter / type-checker; non-zero exit is an error."""
    global errors
    print(f"{BLUE}Linting ({label})...{NC}")
    result = run_command(cmd, label, cwd=cwd, capture_output=False)
    if result and result.returncode == 0:
        print(f"{GREEN}✓ No {label} issues{NC}")
    else:
        print(f"{RED}✗ {label} issues found{NC}")
        errors += 1
    print()


def step_tests(cmd, label, cwd):
    """Run the test suite; non-zero exit is an error."""
    global errors
    print(f"{BLUE}Tests ({label})...{NC}")
    result = run_command(cmd, label, cwd=cwd, capture_output=False)
    if result and result.returncode == 0:
        print(f"{GREEN}✓ All tests passed{NC}")
    else:
        print(f"{RED}✗ Tests failed{NC}")
        errors += 1
    print()


# --------------------------------------------------------------------------- #
# Toolchains
# --------------------------------------------------------------------------- #


def run_rust(root):
    """Format, compiler-fix, clippy, doc, test for a Cargo project."""
    global warnings
    print(f"{BLUE}=== Rust toolchain ==={NC}\n")

    step_format("cargo fmt -- --check", "cargo fmt", "cargo fmt", root)

    # Compiler-suggested fixes (unused imports, deprecated syntax, ...).
    print(f"{BLUE}Compiler fixes (cargo fix)...{NC}")
    result = run_command("cargo fix --allow-dirty --allow-staged", "cargo fix", cwd=root)
    if result and "Fixed" in (result.stderr or ""):
        print(f"{YELLOW}⚠ Compiler fixes applied{NC}")
        for line in result.stderr.split("\n"):
            if "Fixed" in line:
                print(f"  {line}")
        warnings += 1
    else:
        print(f"{GREEN}✓ No compiler fixes needed{NC}")
    print()

    step_lint(
        "cargo clippy --all-targets --all-features -- -D warnings", "clippy", root
    )

    # Documentation build (warnings are non-fatal).
    print(f"{BLUE}Documentation (cargo doc)...{NC}")
    result = run_command("cargo doc --no-deps --document-private-items", "cargo doc", cwd=root)
    if result and "warning" in (result.stderr or "").lower():
        print(f"{YELLOW}⚠ Documentation warnings found{NC}")
        for line in result.stderr.split("\n"):
            if "warning" in line.lower():
                print(f"  {line}")
        warnings += 1
    else:
        print(f"{GREEN}✓ Documentation complete{NC}")
    print()

    step_tests("cargo test", "cargo test", root)


def run_python(root):
    """Format (ruff), type-check (pyright/mypy), test (pytest) for Python.

    Prefers project helper scripts when present (e.g. this repo's
    `format.py` / `type_check.py`), then falls back to direct tooling.
    Uses `uv run` when a uv project is detected, else bare commands.
    """
    print(f"{BLUE}=== Python toolchain ==={NC}\n")

    uv = have("uv") and (root / "uv.lock").exists()
    runner = "uv run " if uv else ""

    # Formatting: project helper > ruff. The helper (e.g. this repo's
    # format.py) formats in place, so check with ruff and fix with the helper.
    if (root / "format.py").exists():
        step_format(
            f"{runner}ruff format --check .",
            f"{runner}format.py",
            "format.py",
            root,
        )
    elif have("ruff") or uv:
        ruff = f"{runner}ruff" if uv else "ruff"
        step_format(f"{ruff} format --check .", f"{ruff} format .", "ruff format", root)
    else:
        print(f"{YELLOW}⚠ No Python formatter found (install ruff){NC}\n")

    # Lint: ruff check (autofix safe issues).
    if have("ruff") or uv:
        ruff = f"{runner}ruff" if uv else "ruff"
        run_command(f"{ruff} check --fix .", "ruff check --fix", cwd=root, capture_output=False)
        step_lint(f"{ruff} check .", "ruff check", root)

    # Type check: project helper > pyright > mypy.
    if (root / "type_check.py").exists():
        step_lint(f"{runner}type_check.py", "type_check.py", root)
    elif have("pyright") or uv:
        pyright = f"{runner}pyright" if uv else "pyright"
        step_lint(pyright, "pyright", root)
    elif have("mypy"):
        step_lint("mypy .", "mypy", root)

    # Tests: pytest.
    if have("pytest") or uv:
        step_tests(f"{runner}pytest", "pytest", root)


TOOLCHAINS = {
    "rust": (lambda root: (root / "Cargo.toml").exists(), run_rust),
    "python": (
        lambda root: any(
            (root / m).exists() for m in ("pyproject.toml", "setup.py", "setup.cfg")
        ),
        run_python,
    ),
}


def print_summary():
    """Print summary of results and return an exit code."""
    print(f"{BLUE}=== Summary ==={NC}")
    print(f"Warnings: {YELLOW}{warnings}{NC}")
    print(f"Errors: {RED}{errors}{NC}")
    print()
    if errors == 0:
        print(f"{GREEN}✓ Refactoring check complete!{NC}")
        return 0
    print(f"{RED}✗ Refactoring check found errors{NC}")
    return 1


def main():
    parser = argparse.ArgumentParser(description="Run refactoring checks for the detected toolchain(s).")
    parser.add_argument("path", nargs="?", default=".", help="Project root (default: cwd)")
    parser.add_argument(
        "--lang",
        choices=sorted(TOOLCHAINS),
        help="Force a single toolchain instead of auto-detecting.",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    print(f"{BLUE}=== Refactoring Check: {root} ==={NC}\n")

    if args.lang:
        selected = [args.lang]
    else:
        selected = [name for name, (detect, _) in TOOLCHAINS.items() if detect(root)]

    if not selected:
        print(
            f"{YELLOW}⚠ No supported toolchain detected in {root}.{NC}\n"
            f"  Looked for: Cargo.toml (Rust), pyproject.toml/setup.py (Python).\n"
            f"  Use --lang to force one, or run the structural-refactoring phase manually."
        )
        sys.exit(0)

    for name in selected:
        TOOLCHAINS[name][1](root)

    sys.exit(print_summary())


if __name__ == "__main__":
    main()
