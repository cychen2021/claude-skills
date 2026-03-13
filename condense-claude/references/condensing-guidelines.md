# CLAUDE.md Condensing Guidelines

## Core Principle

CLAUDE.md should be a concise reference that guides AI assistants efficiently. Information that's already documented elsewhere in `docs/` should be replaced with brief references. The goal is to reduce verbosity while maintaining all necessary context for effective assistance.

## What to Keep in CLAUDE.md

### Essential Content (Always Keep)

1. **Key Conventions** - Critical rules that apply across the codebase:
   - Rust code style conventions
   - Error handling patterns
   - Parser design patterns (nom-based)
   - Semantic analysis patterns
   - AST conventions
   - Type system conventions
   - Testing conventions
   - Git commit conventions

2. **Development Workflow Essentials**:
   - Prerequisites and version management
   - Build commands
   - Feature branch workflow
   - After-editing code routine (cargo fix/fmt)
   - Test commands
   - CLI installation

3. **Project Structure Overview**:
   - High-level repository structure (directories and their purpose)
   - Brief description of major components (runtime/, spot-rs/, docs/)
   - Documentation structure conventions

4. **Architecture at a Glance**:
   - Data flow diagrams (formula-only and program workflows)
   - Module responsibilities table
   - High-level architecture patterns

## What to Condense (Replace with References)

### Detailed Content (Condense to References)

1. **Complete API Documentation**:
   - Full function signatures
   - Detailed parameter descriptions
   - Return type explanations
   - Examples
   → Replace with: "See [docs/api.md](docs/api.md) for complete API reference"

2. **CLI Usage Details**:
   - Command syntax
   - Flag descriptions
   - Output format details
   - Examples
   → Replace with: "See [docs/cli.md](docs/cli.md) for CLI usage"

3. **Parser Grammar and Internals**:
   - Complete grammar rules
   - Operator precedence tables (keep summary, remove details)
   - Parser combinator details
   → Replace with: "See [docs/parser.md](docs/parser.md) for grammar and parser internals"

4. **Type System Details**:
   - Complete type enum structure with all variants
   - All helper methods
   - Detailed compatibility rules
   - Examples
   → Keep: High-level type system overview
   → Replace details with: "See [docs/semantic-analysis.md](docs/semantic-analysis.md) for complete type system"

5. **Runtime Documentation**:
   - Zig runtime architecture
   - Build system details
   - Component descriptions
   → Replace with: "See [docs/runtime.md](docs/runtime.md) for runtime documentation"

6. **Spot Wrapper Details**:
   - Architecture details
   - Build requirements
   - API details
   → Replace with: "See [docs/spot-rs.md](docs/spot-rs.md) for Spot wrapper documentation"

7. **Examples and Use Cases**:
   - Rhai predicate examples
   - C connector examples
   - CWE patterns
   → Replace with: "See [docs/examples.md](docs/examples.md) for usage examples"

8. **Common Tasks Recipes**:
   - Step-by-step instructions for adding operators, types, CLI options
   → Replace with: "See [docs/api.md](docs/api.md) for common development tasks"

9. **Dependencies Table**:
   - Full dependency list with versions and purposes
   → Replace with brief mention and reference to Cargo.toml

10. **Performance Characteristics**:
   - Detailed performance metrics
   → Remove or condense to one-liner if not essential

## Condensing Patterns

### Pattern 1: Section with Reference

**Before:**
```markdown
### Public API (`lib.rs`)

#### Original formula-only API

```rust
// Parse only — no validation
pub fn parse(input: &str) -> Result<Formula, String>

// Parse + Phase 1: arity consistency checking
pub fn parse_and_validate(input: &str) -> Result<(Formula, SignatureRegistry), String>

// Parse + Phase 2: full type checking against declared signatures
pub fn parse_and_type_check(input: &str, registry: TypeRegistry) -> Result<Formula, String>
```

#### Program API (with conditions and predicates)

```rust
// Parse and type-check a complete program (predicates + conditions)
pub fn check_program(input: &str) -> Result<Program, String>

// Lower a ParaLTL program to PLTL intermediate representation
pub fn lower_to_pltl(program: &Program) -> Result<PLTLProgram, LoweringError>
```
```

**After:**
```markdown
### Public API

The library provides functions for parsing, validating, and compiling LTL formulas. See [docs/api.md](docs/api.md) for complete API reference including all function signatures and examples.
```

### Pattern 2: Inline Reference

**Before:**
```markdown
### LTL Operator Precedence (highest to lowest)

1. Primary: atomic propositions, parenthesized expressions, `not`, `always` (G), `eventually` (F), `next` (X)
2. `until` (U), `release` (R) — left-associative
3. `and` — left-associative
4. `or` — left-associative
5. `implies` — right-associative
6. `iff` — left-associative
```

**After:**
```markdown
### Parser

Operators follow standard LTL precedence rules. See [docs/parser.md](docs/parser.md) for complete grammar, precedence table, and parser internals.
```

### Pattern 3: High-Level Summary + Reference

**Before:**
```markdown
### Type System

**Type Enum Structure:**

```rust
pub enum Type {
    // DSL core types (untagged)
    Integer, Boolean, String, Custom(String), Deferred,

    // Language-tagged types (for all language-specific types including C)
    LanguageTagged {
        language: MonitoredLanguage,
        descriptor: LanguageTypeDescriptor,
    }
}
```

**C Type Helper Methods:**

For convenience, helper methods create language-tagged C types:
```rust
Type::c_size_t()   // @foreignty<c> size_t
Type::c_int8()     // @foreignty<c> int8_t
...
```

[many more details]
```

**After:**
```markdown
### Type System

NRV uses a two-tier type system: DSL core types (int, bool, string) and language-tagged types (@foreignty<c>, @foreignty<py>) for foreign language interop. Language-tagged types enforce strict separation between DSL and monitored language types.

See [docs/semantic-analysis.md](docs/semantic-analysis.md) for complete type system documentation including all type variants, helper methods, and compatibility rules.
```

### Pattern 4: Component Mention + Reference

**Before:**
```markdown
### Runtime Directory

The `runtime/` directory contains the **Zig automaton runtime infrastructure** for LTL formula monitoring. This is stage 3 of the compilation implementation (see [docs/draft/impl-compilation.md](docs/draft/impl-compilation.md)).

**Purpose:** Table-driven execution of automata generated from LTL formulas (M_f and M_¬f) for runtime verification with finite-trace semantics (LTL_f).

**Status:** Infrastructure scaffold complete. Stage 4 will add Rust-side integration with Spot library for automaton generation and jump table codegen.

**Documentation:** See [docs/runtime.md](docs/runtime.md) for complete runtime documentation.

**Key Components:**
- `automaton.zig` - DFA data structures (states, transitions, jump tables)
- `executor.zig` - Dual automaton execution engine (runs M_f and M_¬f in parallel)
- `verdict.zig` - Verdict determination (satisfies/violates/inconclusive)
- `trace.zig` - Execution trace representation
- `root.zig` - Library API (exposed as `nrv-runtime` module)

**Build System:** Uses Zig's native build system (`build.zig`). The runtime is exposed as a library module for stage 4 integration.
```

**After:**
```markdown
### Runtime Directory

The `runtime/` directory contains Zig automaton runtime infrastructure for LTL formula monitoring (compilation stage 3). See [docs/runtime.md](docs/runtime.md) for architecture, components, and build details.
```

## Verification Checklist

After condensing, verify:

- [ ] All key conventions are preserved (Rust style, error handling, parser, semantic analysis, AST, types, testing, git)
- [ ] Essential workflow commands remain (build, test, install, feature branches)
- [ ] Repository structure overview is intact
- [ ] Module responsibilities are clear
- [ ] Architecture diagrams remain
- [ ] All detailed content has corresponding references to docs/
- [ ] References are accurate (files exist and contain the referenced information)
- [ ] The condensed version maintains context for effective AI assistance
- [ ] No critical information is lost (just moved to appropriate docs)
