# Copilot Instructions Migration Guide

This guide explains how to handle migration of a `copilot-instructions` git submodule when setting up Claude Code.

## Background

Some repositories use a `copilot-instructions` git submodule to store GitHub Copilot instructions. When migrating to Claude Code, these instructions should be:
1. Migrated to appropriate locations in the main repository
2. Configured properly for continued Copilot usage
3. The submodule should be removed

## Migration Strategy

### 1. Detect Copilot Instructions Submodule

Check for the submodule:
```bash
git submodule status
cat .gitmodules
```

Look for entries referencing `copilot-instructions`.

### 2. Review Submodule Content

Read the content in the submodule directory to understand:
- What instructions exist
- Whether they're project-specific or general guidelines
- Which parts are relevant to migrate

Common organizational patterns:

**Domain-based structure** (typical for reusable instructions):
```
copilot-instructions/
├── codegen/              # Code generation instructions
│   ├── codegen-general.instructions.md
│   ├── codegen-python.instructions.md
│   ├── codegen-rust.instructions.md
│   └── ...
├── commit/               # Commit message conventions
│   └── commit-general.instructions.md
├── prompts/              # Reusable prompt templates
│   └── ...
└── .vscode/              # VS Code configurations
```

**Monolithic structure** (typical for project-specific instructions):
```
copilot-instructions/
├── README.md
├── instructions.md       # Main instructions file
└── commit.instructions.md
```

### 3. Determine Migration Destinations

The migration strategy depends on whether instructions are project-specific or reusable:

#### A. Domain-Based Structure (Reusable Instructions Repository)

When the submodule is a **shared repository** with domain-based organization:

**codegen/** directory:
- **codegen-general.instructions.md**: Migrate relevant project-specific guidelines to `CLAUDE.md` → "Key Conventions" section
- **codegen-{language}.instructions.md**:
  - If project uses that language: Migrate to `CLAUDE.md` → "Key Conventions" → "{Language} Code Style"
  - Keep language-agnostic principles in `.vscode/copilot-instructions.md` for Copilot

**commit/** directory:
- **commit-*.instructions.md**: Migrate to both:
  - `CLAUDE.md` → "Git Commit Conventions" section (for Claude Code)
  - `.vscode/commit.instructions.md` (for GitHub Copilot)

**prompts/** directory:
- Review each prompt file for project relevance
- Generally these are workflow templates—not needed in Claude Code's instruction files
- Archive or document in project docs if valuable

**Strategy**: Be selective. Only migrate instructions **directly relevant to the project's codebase**. Generic coding advice should stay as Copilot-specific configuration.

#### B. Monolithic Structure (Project-Specific Instructions)

When the submodule is **project-specific**:

**Main instructions file (instructions.md, README.md, etc.)**:
- Migrate comprehensive content to `CLAUDE.md`
- Copy language-specific coding conventions to `.vscode/copilot-instructions.md` for Copilot

**Commit conventions**:
- Migrate to both `CLAUDE.md` and `.vscode/commit.instructions.md`

**Strategy**: Most content belongs in `CLAUDE.md` since it's project-specific. Duplicate only what's useful for Copilot's code generation.

### 4. Configure Settings

Update `.vscode/settings.json` to point to the migrated instruction files:

**If keeping Copilot alongside Claude Code:**

```json
{
  // Claude Code configuration
  "claude-code.permissionMode": "ask",
  "claude-code.autoResumeEnabled": true,

  // GitHub Copilot configuration
  "github.copilot.enable": {
    "*": true
  },

  // Point Copilot to migrated instructions
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".vscode/copilot-instructions.md"
    }
  ],
  "github.copilot.chat.commitMessageGeneration.instructions": [
    {
      "file": ".vscode/commit.instructions.md"
    }
  ]
}
```

**If using only Claude Code:**

```json
{
  "claude-code.permissionMode": "ask",
  "claude-code.autoResumeEnabled": true
}
```

Instructions go entirely in `CLAUDE.md` and `.vscode/` files can be omitted.

### 5. Remove Submodule

After migrating content:
```bash
# Remove submodule from .gitmodules and .git/config
git submodule deinit copilot-instructions

# Remove the submodule directory from git tracking
git rm copilot-instructions

# Remove the submodule directory from .git/modules
rm -rf .git/modules/copilot-instructions

# Commit the removal
git commit -m "Remove copilot-instructions submodule after migration"
```

## Content Categories

### Instructions to Migrate to CLAUDE.md

- Project architecture and structure
- Development workflow and conventions
- Code style guidelines
- Testing requirements
- Build and deployment procedures
- Domain-specific knowledge
- Project-specific patterns

### Instructions to Keep for Copilot Only

- General coding principles (if not in CLAUDE.md)
- Language-agnostic best practices
- Copilot-specific generation preferences
- Output format preferences

### Instructions to Duplicate

Some instructions may be relevant to both:
- Commit message conventions (both CLAUDE.md and .vscode/)
- Code review guidelines
- Security requirements

## Example Migrations

### Example 1: Domain-Based Structure (Reusable Instructions)

**Before (in copilot-instructions/):**
```
copilot-instructions/
├── codegen/
│   ├── codegen-general.instructions.md
│   ├── codegen-python.instructions.md
│   └── codegen-rust.instructions.md
├── commit/
│   └── commit-general.instructions.md
└── prompts/
    └── evolve-doc.prompt.md
```

**After migration for a Rust project:**

*CLAUDE.md:*
```markdown
## Git Commit Conventions

[Content from commit/commit-general.instructions.md]
- Use conventional commits format
- Start with imperative verb
- Keep headline under 50 characters

## Key Conventions

### Rust Code Style

[Relevant sections from codegen/codegen-rust.instructions.md]
- Use `rustfmt` for formatting
- Follow Rust API guidelines
- Prefer `&T` over cloning
```

*.vscode/copilot-instructions.md:*
```markdown
# Copilot Code Generation Instructions

[Language-agnostic sections from codegen/codegen-general.instructions.md]
- Write clear, descriptive variable names
- Prefer composition over inheritance
- Document complex logic
```

*.vscode/commit.instructions.md:*
```markdown
[Content from commit/commit-general.instructions.md]
Use conventional commits format:
- feat: new features
- fix: bug fixes
- docs: documentation changes
```

**Files NOT migrated:**
- `prompts/evolve-doc.prompt.md` - Not relevant to codebase conventions

### Example 2: Monolithic Structure (Project-Specific)

**Before (in copilot-instructions/):**
```markdown
# Project Instructions

## Architecture
This is a microservices project using Node.js and TypeScript...

## Commit Messages
Use conventional commits format...

## Code Style
- Always use TypeScript strict mode
- Prefer async/await over callbacks
- Use named exports
```

**After:**

*CLAUDE.md:*
```markdown
## Project Overview

This is a microservices project using Node.js and TypeScript...

## Architecture
[Details about microservices structure]

## Git Commit Conventions
Use conventional commits format...

## Key Conventions

### TypeScript Code Style
- Always use TypeScript strict mode
- Prefer async/await over callbacks
- Use named exports
```

*.vscode/copilot-instructions.md:*
```markdown
# Copilot Instructions

## TypeScript Code Generation
- Use TypeScript strict mode
- Prefer async/await over callbacks
- Use named exports
```

*.vscode/commit.instructions.md:*
```markdown
Use conventional commits format...
```
