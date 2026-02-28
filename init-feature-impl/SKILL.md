---
name: init-feature-impl
description: Initialize a new feature implementation for the verifuzz codebase. Creates a feature branch with proper naming convention, optionally designs an implementation plan, and prepares for implementation. AUTOMATICALLY use this skill when the user explicitly requests a new feature with phrases like "I want a new feature", "Let's add [feature]", "Start implementing [feature]", "Begin new feature [description]", or any clear request to start feature development work.
---

# Init Feature Impl

Initialize a new feature implementation with proper branch setup and planning.

## Workflow

### 1. Clarify Requirements

If the feature request is ambiguous or lacks details, ask clarifying questions using the `AskUserQuestion` tool:

- What is the expected behavior or outcome?
- Are there specific constraints or requirements?
- Which parts of the codebase will be affected?
- Are there examples or use cases to consider?

### 2. Create Feature Branch

Create a feature branch following the verifuzz naming convention:

```bash
git checkout -b feature/<descriptive-name>
```

Or with username prefix if working in a team:

```bash
git checkout -b <username>/feature/<descriptive-name>
```

**Branch naming guidelines:**
- Use kebab-case for multi-word descriptions
- Be descriptive but concise
- Examples: `feature/add-bounded-temporal-ops`, `feature/improve-type-inference`

### 3. Planning Phase (Optional)

**Default behavior:** Enter plan mode for non-trivial features.

**Skip if:** The user provides the `--skip-plan` argument, or the feature is extremely simple (single-line fix, trivial addition).

**When planning is needed:**
- New operator or type additions
- Multi-file changes
- Architectural decisions required
- Multiple valid implementation approaches
- Unclear scope requiring codebase exploration

**How to plan:**

1. Use `EnterPlanMode` tool to enter planning mode
2. Explore the codebase using `Glob`, `Grep`, and `Read` tools to understand:
   - Existing patterns and architecture
   - Related code that might be affected
   - Testing patterns to follow
   - Documentation that needs updating
3. Design the implementation approach considering:
   - Where changes will be made (specific files and functions)
   - How the feature integrates with existing code
   - What tests are needed
   - What documentation needs updating
4. Use `ExitPlanMode` tool to present the plan to the user

**If plan mode is skipped:** Briefly outline the implementation approach in a message to the user.

### 4. Wait for Go-Ahead

After presenting the plan (or skip-plan outline), **wait for the user's explicit instruction to begin implementation**. Do not start coding until the user approves.

Examples of go-ahead signals:
- "Looks good, go ahead"
- "Start implementing"
- "Let's do it"
- "Proceed"

### 5. Begin Implementation

Once approved:

1. Use `TodoWrite` tool to create a task list for the implementation
2. Start implementing following the approved plan
3. Mark todos as `in_progress` and `completed` as work progresses
4. Follow verifuzz code conventions (see CLAUDE.md):
   - Update both `SemanticAnalyzer` and `TypedSemanticAnalyzer` for AST changes
   - Add tests for all new code paths
   - Keep `use` statements at most one level deep
   - Derive `Debug` and `PartialEq` on AST types

## Arguments

**`--skip-plan`**: Skip the planning phase for simple features where the implementation is straightforward.

Example:
- User: "I want a new feature to add support for X --skip-plan"
- Skip directly to step 4 after creating the branch

## Integration with Other Skills

This skill is designed to work with the full verifuzz workflow:

- **After implementation:** Use `/finish-feature-impl` to complete the feature with testing, docs, and PR creation
- **During implementation:** Use `/test` to verify changes, `/debug-tests` to fix failures
- **For commits:** Use `/commit` to follow verifuzz commit conventions

## Notes

- This skill focuses on initialization and planning—actual implementation happens after user approval
- Always check `CLAUDE.md` for the latest development workflow and conventions
- Feature branches keep main stable and allow for easier review
