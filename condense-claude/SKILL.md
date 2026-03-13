---
name: condense-claude
description: Condense CLAUDE.md by removing verbose content that duplicates information in docs/ and replacing it with concise references. Preserves key conventions, essential workflows, and architecture overview while maintaining context for effective AI assistance. Use when the user requests to "condense CLAUDE.md", "slim down CLAUDE.md", "reduce CLAUDE.md verbosity", or when CLAUDE.md has grown too long after multiple feature additions.
---

# Condense CLAUDE.md

This skill condenses CLAUDE.md by identifying content that duplicates information already in `docs/` and replacing verbose sections with concise references, while preserving all essential conventions and workflows.

## Workflow

### 1. Read Current CLAUDE.md and Documentation

Read CLAUDE.md and scan the docs/ directory to understand what documentation exists:

```bash
ls -la docs/
```

Read key documentation files that might contain duplicated content:
- docs/api.md - API reference
- docs/cli.md - CLI usage
- docs/parser.md - Parser internals
- docs/semantic-analysis.md - Type system and semantic analysis
- docs/runtime.md - Runtime documentation
- docs/spot-rs.md - Spot wrapper documentation
- docs/examples.md - Usage examples

### 2. Load Condensing Guidelines

Read the detailed condensing guidelines:

```
references/condensing-guidelines.md
```

This file contains:
- What to keep in CLAUDE.md (key conventions, essential workflows)
- What to condense (detailed content with doc references)
- Condensing patterns with before/after examples
- Verification checklist

### 3. Identify Sections to Condense

Systematically review CLAUDE.md section by section, identifying content that:

1. **Duplicates detailed documentation** - Full API signatures, CLI usage, parser grammar, type system details, runtime architecture
2. **Provides examples** - These belong in docs/examples.md
3. **Lists all variants/methods** - High-level summaries suffice in CLAUDE.md
4. **Describes implementation details** - Keep architecture, move details to docs/

Cross-reference with docs/ to ensure corresponding documentation exists before condensing.

### 4. Apply Condensing Patterns

For each section to condense, apply appropriate pattern from guidelines:

**Pattern 1: Section with Reference**
- Remove detailed content
- Replace with one-paragraph summary + doc reference

**Pattern 2: Inline Reference**
- Remove entire section
- Replace with single sentence + doc reference

**Pattern 3: High-Level Summary + Reference**
- Keep 2-3 sentence overview
- Remove all details
- Add doc reference

**Pattern 4: Component Mention + Reference**
- Keep one sentence about purpose
- Remove component lists and details
- Add doc reference

### 5. Preserve Essential Content

Ensure these sections remain intact or only lightly condensed:

- **Key Conventions** (Rust code style, error handling, parser patterns, semantic analysis, AST, types, testing, git commits)
- **Development Workflow** (prerequisites, version management, build, feature branches, after-editing routine, test commands)
- **Project Structure Overview** (repository structure, major components, documentation conventions)
- **Architecture at a Glance** (data flow diagrams, module responsibilities table)

### 6. Verify References Are Accurate

For each reference added, verify:
- The referenced file exists
- The file contains the referenced information
- The file path is correct relative to repository root

### 7. Run Verification Checklist

Use the checklist from condensing-guidelines.md to verify:

- [ ] All key conventions preserved
- [ ] Essential workflow commands remain
- [ ] Repository structure overview intact
- [ ] Module responsibilities clear
- [ ] Architecture diagrams remain
- [ ] All detailed content has doc references
- [ ] References are accurate
- [ ] Context maintained for AI assistance
- [ ] No critical information lost

### 8. Create Condensed Version

Use the Edit tool to update CLAUDE.md with the condensed version. Make targeted edits to each section that needs condensing rather than rewriting the entire file.

### 9. Review and Iterate

Review the condensed CLAUDE.md:
- Verify it's significantly shorter
- Ensure all essential information is either present or referenced
- Check that it remains useful for AI assistant guidance

If needed, iterate on specific sections that are still too verbose or missing essential context.

## Output

The condensed CLAUDE.md should:
- Be 30-50% shorter than the original
- Contain all key conventions and workflows
- Reference docs/ for detailed information
- Maintain clear context for AI assistance
- Preserve project structure and architecture overview
