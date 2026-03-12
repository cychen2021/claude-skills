---
name: init-feature-remove
description: Initialize feature removal for the nrv codebase. Creates a removal branch with proper naming convention, analyzes dependencies, checks for breaking changes, and creates a removal plan. AUTOMATICALLY use this skill when the user explicitly requests to remove a feature with phrases like "Remove feature X", "Delete the Y functionality", "Deprecate Z", "Get rid of [feature]", or any clear request to remove existing functionality from the codebase.
---

# Init Feature Remove

Initialize feature removal with proper branch setup, dependency analysis, and planning.

## Workflow

### 1. Clarify Requirements

If the removal request is ambiguous or lacks details, ask clarifying questions using the `AskUserQuestion` tool:

- What specific feature or functionality should be removed?
- Are there any parts that should be kept or replaced?
- Is there a deprecation period needed, or immediate removal?
- Are there known dependencies on this feature?
- Should related tests and documentation be removed as well?

### 2. Create Removal Branch

Create a removal branch following the nrv naming convention:

```bash
git checkout -b remove/<descriptive-name>
```

Or with username prefix if working in a team:

```bash
git checkout -b <username>/remove/<descriptive-name>
```

**Branch naming guidelines:**
- Use kebab-case for multi-word descriptions
- Be descriptive about what's being removed
- Examples: `remove/bounded-temporal-ops`, `remove/legacy-parser`

### 3. Analyze Dependencies

Thoroughly search the codebase to identify all code, tests, and documentation related to the feature being removed:

**Search for code references:**
```bash
# Search for the feature name/identifier
rg "<feature-name>" --type rust

# Search for related types, functions, modules
rg "<FeatureType>" --type rust
rg "fn <feature_function>" --type rust

# Check AST and parser for enum variants
rg "enum Formula" src/ast.rs
rg "Formula::<Variant>" src/
```

**Search for tests:**
```bash
# Find test modules and functions
rg "test.*<feature>" --type rust
rg "#\[test\]" -A 5 | rg "<feature>"
```

**Search for documentation:**
```bash
# Search markdown files
rg "<feature>" docs/
rg "<feature>" *.md

# Check for examples
rg "<feature>" docs/examples.md
```

**Check CLI integration:**
```bash
# Search for CLI arguments or subcommands
rg "<feature>" src/bin/nrv.rs
```

Document all findings for the removal plan.

### 4. Check for Breaking Changes

Determine if the removal constitutes a breaking change:

**Breaking change indicators:**
- Removing a public API function or type
- Removing CLI arguments or subcommands
- Removing supported syntax or operators
- Changing behavior of existing features

**If breaking:**
- Plan to update `CHANGELOG.md` with breaking change notice
- Consider if version bump is needed (major version for semver)
- Determine if a deprecation period is appropriate instead of immediate removal

**If non-breaking:**
- Feature is internal-only, or
- Feature was never documented/exposed, or
- Feature is being replaced with equivalent functionality

### 5. Create Removal Plan

Use the `EnterPlanMode` tool to enter planning mode and create a detailed removal plan:

1. **Files to modify:**
   - List all files where code will be removed
   - Identify specific functions, types, or modules to delete

2. **Tests to remove or update:**
   - List test functions that will be deleted
   - Identify tests that need updates (removing assertions for removed features)

3. **Documentation to update:**
   - `docs/api.md` - Remove API references
   - `docs/cli.md` - Remove CLI documentation
   - `docs/parser.md` - Remove grammar/operator documentation
   - `docs/semantic-analysis.md` - Remove type/validation documentation
   - `docs/examples.md` - Remove or update examples
   - `README.md` - Update if feature was mentioned
   - `CLAUDE.md` - Update development conventions if needed
   - `CHANGELOG.md` - Add breaking change notice if applicable

4. **Order of operations:**
   - Remove tests first (so they don't fail during removal)
   - Remove implementation code
   - Update documentation
   - Run full test suite to verify nothing broke

5. **Breaking change handling:**
   - If breaking: note required CHANGELOG and version updates
   - If non-breaking: note that existing API surface is preserved

Present the plan using `ExitPlanMode` tool.

### 6. Wait for Go-Ahead

After presenting the plan, **wait for the user's explicit instruction to begin removal**. Do not start removing code until the user approves.

Examples of go-ahead signals:
- "Looks good, proceed with removal"
- "Start removing"
- "Let's do it"
- "Go ahead"

### 7. Begin Removal

Once approved:

1. Use `TodoWrite` tool to create a task list for the removal based on the plan
2. Start removing code following the approved plan
3. Mark todos as `in_progress` and `completed` as work progresses
4. Follow the order of operations from the plan:
   - Remove tests first
   - Remove implementation code
   - Update documentation
   - Verify tests pass

5. Follow nrv code conventions (see CLAUDE.md):
   - If removing a `Formula` variant, update both `SemanticAnalyzer` and `TypedSemanticAnalyzer`
   - Keep commits focused and atomic
   - Run `cargo fix --allow-dirty` and `cargo fmt` after changes
   - Ensure no orphaned imports or dead code remains

## Integration with Other Skills

This skill is designed to work with the full nrv workflow:

- **After removal:** Use `/finish-feature-remove` to complete the removal with testing, docs verification, and PR creation
- **During removal:** Use `/test` to verify changes, `/debug-tests` to fix failures
- **For commits:** Use `/commit` to follow nrv commit conventions

## Notes

- This skill focuses on initialization and planning—actual removal happens after user approval
- Always check `CLAUDE.md` for the latest development workflow and conventions
- Removal branches keep main stable and allow for easier review
- Be thorough in dependency analysis—missed references can break the build
- Breaking changes require careful documentation and version management
