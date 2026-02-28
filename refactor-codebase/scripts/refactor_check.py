#!/usr/bin/env python3
"""
Refactoring check script for Rust projects
Runs formatting, linting, and validation checks
Cross-platform: Works on Windows, Linux, and macOS
"""

import subprocess
import sys
from pathlib import Path

# ANSI color codes (work on most terminals, including Windows 10+)
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Track overall status
warnings = 0
errors = 0


def run_command(cmd, description, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result
    except Exception as e:
        print(f"{RED}✗ Error running {description}: {e}{NC}")
        return None


def check_formatting():
    """Check and apply code formatting."""
    global warnings
    print(f"{BLUE}[1/5] Running cargo fmt...{NC}")

    # Check if formatting is needed
    result = run_command("cargo fmt -- --check", "cargo fmt --check")
    if result and result.returncode != 0:
        print(f"{YELLOW}⚠ Code formatting needed. Applying...{NC}")
        run_command("cargo fmt", "cargo fmt", capture_output=False)
        print(f"{GREEN}✓ Code formatted{NC}")
        warnings += 1
    else:
        print(f"{GREEN}✓ Code already formatted{NC}")
    print()


def apply_compiler_fixes():
    """Apply compiler-suggested fixes."""
    global warnings
    print(f"{BLUE}[2/5] Running cargo fix...{NC}")

    result = run_command("cargo fix --allow-dirty --allow-staged", "cargo fix")
    if result and "Fixed" in result.stderr:
        print(f"{YELLOW}⚠ Compiler fixes applied{NC}")
        # Print fixed items
        for line in result.stderr.split('\n'):
            if "Fixed" in line:
                print(f"  {line}")
        warnings += 1
    else:
        print(f"{GREEN}✓ No compiler fixes needed{NC}")
    print()


def check_clippy():
    """Run clippy linting."""
    global errors
    print(f"{BLUE}[3/5] Running cargo clippy...{NC}")

    result = run_command(
        "cargo clippy --all-targets --all-features -- -D warnings",
        "cargo clippy",
        capture_output=False
    )
    if result and result.returncode == 0:
        print(f"{GREEN}✓ No clippy warnings{NC}")
    else:
        print(f"{RED}✗ Clippy warnings found{NC}")
        errors += 1
    print()


def check_documentation():
    """Check documentation completeness."""
    global warnings
    print(f"{BLUE}[4/5] Checking documentation...{NC}")

    result = run_command(
        "cargo doc --no-deps --document-private-items",
        "cargo doc"
    )
    if result and "warning" in result.stderr.lower():
        print(f"{YELLOW}⚠ Documentation warnings found{NC}")
        for line in result.stderr.split('\n'):
            if "warning" in line.lower():
                print(f"  {line}")
        warnings += 1
    else:
        print(f"{GREEN}✓ Documentation complete{NC}")
    print()


def run_tests():
    """Run all tests."""
    global errors
    print(f"{BLUE}[5/5] Running tests...{NC}")

    result = run_command("cargo test", "cargo test")
    if result and result.returncode == 0:
        # Extract passed test count
        for line in result.stdout.split('\n'):
            if "passed" in line:
                print(f"{GREEN}✓ All tests passed{NC}")
                print(f"  {line.strip()}")
                break
    else:
        print(f"{RED}✗ Tests failed{NC}")
        errors += 1
    print()


def print_summary():
    """Print summary of results."""
    print(f"{BLUE}=== Summary ==={NC}")
    print(f"Warnings: {YELLOW}{warnings}{NC}")
    print(f"Errors: {RED}{errors}{NC}")
    print()

    if errors == 0:
        print(f"{GREEN}✓ Refactoring check complete!{NC}")
        return 0
    else:
        print(f"{RED}✗ Refactoring check found errors{NC}")
        return 1


def main():
    """Main entry point."""
    print(f"{BLUE}=== Verifuzz Refactoring Check ==={NC}\n")

    # Run all checks
    check_formatting()
    apply_compiler_fixes()
    check_clippy()
    check_documentation()
    run_tests()

    # Print summary and exit with appropriate code
    exit_code = print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
