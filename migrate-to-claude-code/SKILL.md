---
name: migrate-to-claude-code
description: Migrate an existing repository to adopt Claude Code workflow and conventions, including creating docs/ and checkpoints/ directories, setting up CLAUDE.md instructions, configuring .vscode settings, and handling copilot-instructions git submodule migration. Use when the user requests to "migrate to Claude Code", "set up Claude Code", "initialize Claude Code", "adopt Claude Code conventions", or similar requests to adopt Claude Code in an existing project.
---

# Migrate Repository to Claude Code

Migrate an existing repository to adopt Claude Code workflow conventions with structured documentation, checkpoint system, and optional migration from copilot-instructions submodule.

## Migration Workflow

Follow these steps in order:

### 1. Check Current State

Verify the repository's current structure:

```bash
# Check for CLAUDE.md
ls -la CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"

# Check for docs/ and checkpoints/ directories
ls -la docs/ 2>/dev/null || echo "No docs/ directory"
ls -la checkpoints/ 2>/dev/null || echo "No checkpoints/ directory"

# Check for copilot-instructions submodule
git submodule status
cat .gitmodules 2>/dev/null || echo "No .gitmodules found"
```

### 2. Create Documentation and Checkpoint Directories

Create the structured documentation and checkpoint directories:

```bash
mkdir -p docs/draft
mkdir -p checkpoints
```

**Directory purposes:**
- `docs/` - Comprehensive project documentation (API, CLI, architecture, examples, etc.)
- `docs/draft/` - Work-in-progress documentation
- `checkpoints/` - Periodic manual review checkpoints (timestamped: cp-YYMMDD)

**Documentation structure pattern** (adapt to project needs):
- `docs/readme.md` - Documentation index and quick reference
- `docs/api.md` - API reference
- `docs/cli.md` - CLI usage (if applicable)
- `docs/examples.md` - Usage examples
- `docs/[module].md` - Module-specific documentation as needed

### 3. Handle Copilot Instructions Migration (if applicable)

**If a `copilot-instructions` submodule exists**, follow the migration process detailed in [references/copilot-migration-guide.md](references/copilot-migration-guide.md):

**Key steps:**

a. **Review submodule content:**
   - Read the content in the copilot-instructions directory
   - Identify project-specific instructions vs. general guidelines

b. **Migrate content appropriately:**
   - **To CLAUDE.md**: Project architecture, development workflow, conventions, testing requirements, domain knowledge
   - **To .vscode/copilot-instructions.md**: General coding principles, Copilot-specific preferences (if user still uses Copilot)
   - **To .vscode/commit.instructions.md**: Commit message conventions (for Copilot)

c. **Configure settings** (see step 5 below)

d. **Remove the submodule:**
   ```bash
   # Deinitialize and remove
   git submodule deinit copilot-instructions
   git rm copilot-instructions
   rm -rf .git/modules/copilot-instructions
   ```

**If no submodule exists**, skip to step 4.

### 4. Create CLAUDE.md

Use the template from [assets/CLAUDE.md.template](assets/CLAUDE.md.template) to create `CLAUDE.md` at the repository root.

**Customization approach:**

1. **Analyze the repository** to understand:
   - Project purpose and main functionality
   - Technology stack and dependencies
   - Directory structure
   - Build/test/development commands
   - Existing code style (check for formatters, linters, style guides)
   - Existing documentation (README.md, CONTRIBUTING.md, etc.)

2. **Fill in template sections** based on analysis:
   - Replace `[PROJECT_NAME]` with the actual project name
   - Write concise, actionable instructions
   - Include actual commands that work in this repository
   - Document existing conventions found in the codebase
   - Migrate relevant content from copilot-instructions if applicable

3. **Keep it concise:**
   - Focus on information Claude wouldn't know from examining code alone
   - Avoid redundancy with existing documentation
   - Use bullet points and code blocks for readability

**Example sections to prioritize:**
- Project overview (what it does, why it exists)
- Repository structure (key directories)
- Development workflow (build, test, lint commands)
- Commit conventions (if they exist)
- Code style conventions
- Common tasks with step-by-step instructions

### 5. Configure .vscode/settings.json

Create or update `.vscode/settings.json` using [assets/settings.json.template](assets/settings.json.template):

**Essential settings:**
```json
{
  "claude-code.permissionMode": "ask",
  "claude-code.autoResumeEnabled": true
}
```

**If user still uses GitHub Copilot**, add Copilot configuration:

```json
{
  "github.copilot.enable": {
    "*": true
  },
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

**If updating an existing file**, merge with existing settings rather than replacing.

### 6. Create Initial Documentation

Create essential documentation files in `docs/`:

**docs/readme.md** - Documentation index:
```markdown
# Documentation

Quick reference and documentation index for [PROJECT_NAME].

## Documentation Files

- [api.md](api.md) - API reference
- [cli.md](cli.md) - CLI usage guide (if applicable)
- [examples.md](examples.md) - Usage examples
- [CLAUDE.md](../CLAUDE.md) - AI assistant instructions

## Quick Start

[Brief getting started guide]

## Architecture Overview

[High-level architecture description]
```

**Additional documentation files** (create as needed):
- `docs/api.md` - Complete API reference
- `docs/cli.md` - CLI tool documentation
- `docs/examples.md` - Usage examples and patterns
- Module-specific docs as needed

### 7. Update .gitignore

Ensure `.gitignore` excludes temporary files while preserving documentation:

```gitignore
# Temporary files and directories (user-defined convention)
tmp/
x_*

# Keep these in version control:
# docs/
# checkpoints/
# CLAUDE.md
```

**If .gitignore already exists**, append these entries if not already present.

### 8. Commit Changes

After migration is complete, commit the changes:

```bash
git add docs/ checkpoints/ CLAUDE.md .vscode/settings.json .gitignore
git commit -m "Adopt Claude Code workflow and conventions

- Create docs/ directory with documentation structure
- Create checkpoints/ directory for manual review checkpoints
- Add CLAUDE.md with project instructions
- Configure .vscode/settings.json for Claude Code
[- Migrate copilot-instructions to .vscode/ and CLAUDE.md]
[- Remove copilot-instructions submodule]"
```

Adjust the commit message based on what was actually done (include copilot-instructions lines only if applicable).

## Post-Migration Verification

Verify the migration was successful:

```bash
# Check directory structure
ls -la docs/
ls -la checkpoints/

# Check files exist
test -f CLAUDE.md && echo "✓ CLAUDE.md exists"
test -f docs/readme.md && echo "✓ docs/readme.md exists"
test -f .vscode/settings.json && echo "✓ .vscode/settings.json exists"
test -d docs/draft && echo "✓ docs/draft/ exists"

# Verify submodule removal (if applicable)
git submodule status | grep copilot-instructions || echo "✓ copilot-instructions submodule removed"
```

## Special Cases

### Monorepo Migration

For monorepos with multiple projects:
- Create a unified `CLAUDE.md` with clear sections for each sub-project
- Organize `docs/` by sub-project: `docs/project1/`, `docs/project2/`
- Use shared `checkpoints/` for cross-cutting reviews
- Ask the user which approach they prefer

### Existing docs/ or checkpoints/ Directory

If directories already exist:
- Preserve existing content
- Fill in missing files following the documentation pattern
- Ask before overwriting any existing files

### No Git Repository

If the directory is not a git repository:
- Skip submodule checks and git commit steps
- Proceed with file creation only
- Suggest initializing git if the user wants version control

## Reference Materials

- **Copilot Migration Details**: See [references/copilot-migration-guide.md](references/copilot-migration-guide.md) for comprehensive submodule migration guidance
- **CLAUDE.md Template**: [assets/CLAUDE.md.template](assets/CLAUDE.md.template)
- **Settings Template**: [assets/settings.json.template](assets/settings.json.template)
