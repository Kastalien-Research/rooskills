# Cursor Skills Mapping Analysis

## Executive Summary

**Status:** ✅ **VIABLE** - Cursor has multiple extensibility mechanisms that can accommodate Agent Skills mapping

**Primary Solution:** Leverage Cursor's **Rules** system (`.cursor/rules/*.mdc`) as the direct equivalent to Claude Code Skills

**Alternative Solutions:** Cursor **Commands** (`.cursor/commands/*.md`) and **AGENTS.md** provide complementary approaches for different use cases

## Current State Analysis

### Claude Code Skills Architecture

Claude Code uses a three-level progressive disclosure system:

```
~/.claude/skills/skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description, allowed-tools)
│   └── Markdown instructions
├── scripts/          # Executable utilities
├── references/       # Documentation loaded as needed
└── assets/           # Templates and output files
```

**Key Characteristics:**
- **Model-invoked**: Claude autonomously decides when to use skills based on description
- **Progressive loading**: Metadata → SKILL.md → bundled resources (as needed)
- **Scoped by location**: Personal (`~/.claude/skills/`) vs Project (`.claude/skills/`)
- **Tool permissions**: `allowed-tools` frontmatter restricts tool access when skill is active

### Roo Code Modes (Existing Implementation)

Roo Code's modes have been successfully mapped to Skills:

```
.roo/skills/cursor-skills/
├── SKILL.md               # Mode description and when to use
├── references/
│   ├── api_documentation.md      # Complete Cursor docs
│   └── documentation_index.md    # llms.txt format index
└── LICENSE.txt
```

**Success factors:**
- Single skill encapsulates Cursor platform knowledge
- References contain comprehensive documentation
- Works as reference material for implementing Cursor-specific workflows

### Cursor Extensibility Mechanisms

Cursor provides **three distinct extensibility patterns**, each with different characteristics:

#### 1. Rules System (`.cursor/rules/*.mdc`)

**Format:**
```mdc
---
description: RPC Service boilerplate
globs: ["**/*.ts", "**/*.tsx"]
alwaysApply: false
---

- Use our internal RPC pattern when defining services
- Always use snake_case for service names.

@service-template.ts
```

**Characteristics:**
- **Location**: Project (`.cursor/rules/`), User (global settings), Team (dashboard)
- **File format**: MDC (Markdown with frontmatter)
- **Invocation types**:
  - `Always` rules: Always in context (alwaysApply: true)
  - `Auto Attached` rules: Triggered by glob patterns
  - `Manual` rules: Explicitly referenced via `@ruleName`
- **Scope**: Applies to Agent (Chat) and Inline Edit
- **Nested support**: Can nest `.cursor/rules/` in subdirectories
- **Precedence**: Team Rules → Project Rules → User Rules

#### 2. Commands System (`.cursor/commands/*.md`)

**Format:**
```markdown
# Review Code

Perform a thorough code review checking for:
- Security vulnerabilities
- Performance issues
- Best practices adherence
```

**Characteristics:**
- **Location**: Project (`.cursor/commands/`), Global (`~/.cursor/commands/`), Team (dashboard)
- **File format**: Plain Markdown (no frontmatter)
- **Invocation**: User-invoked via `/command-name` in chat
- **Parameters**: Can accept additional context after command name
- **Scope**: Agent Chat only
- **No auto-triggering**: Always requires explicit user invocation

#### 3. AGENTS.md (Simple Alternative)

**Format:**
```markdown
# Project Instructions

## Code Style
- Use TypeScript for all new files
- Prefer functional components in React

## Architecture
- Follow the repository pattern
```

**Characteristics:**
- **Location**: Project root or subdirectories
- **File format**: Plain Markdown
- **Invocation**: Always active (similar to "Always" rules)
- **Scope**: Agent and Inline Edit
- **Simplicity**: No metadata, glob patterns, or complex configuration
- **Legacy replacement**: Replaces deprecated `.cursorrules` file

## Problem Space Analysis

### Core Challenge: Model-Invoked vs User-Invoked

**Claude Code Skills:** Model autonomously decides when to use skills based on `description` field
**Cursor Commands:** User must explicitly invoke with `/command` prefix

This creates a fundamental mismatch for workflow-type skills that should trigger automatically.

### Mapping Complexity Matrix

| Skill Type | Claude Code Behavior | Cursor Equivalent | Complexity |
|------------|---------------------|-------------------|------------|
| Domain Knowledge | Progressive disclosure from references/ | Rules (Auto Attached) or AGENTS.md with nested structure | Low |
| Workflow Automation | Model-invoked based on description | Rules (Manual) + Commands (requires user invoke) | Medium |
| Tool Integration | Scripts + allowed-tools restrictions | Rules (no tool restrictions) + Extensions/MCP | High |
| Templates | Assets folder with boilerplate | Rules with file references or Commands | Low |

## Proposed Solution: Hybrid Mapping Strategy

### Architecture Overview

```
.cursor/
├── rules/                          # Model-invoked skills
│   ├── skill-name.mdc             # Auto-attached by glob or always active
│   └── nested-context/
│       └── rules/
│           └── specific-skill.mdc
├── commands/                       # User-invoked workflows
│   └── skill-workflow.md          # Explicit /command invocation
└── skills/                         # NEW: Mirrored Skills structure
    └── skill-name/
        ├── SKILL.md → ../rules/skill-name.mdc (symlink)
        ├── references/
        ├── scripts/
        └── assets/
```

### Mapping Strategy by Skill Type

#### Type 1: Knowledge/Reference Skills (High Fidelity)

**Example:** `cursor-skills`, `lindy-expert`, `mcp-builder`

**Mapping:**
```
Claude: .claude/skills/cursor-skills/SKILL.md
          └── references/api_documentation.md

Cursor: .cursor/rules/cursor-skills.mdc (Auto Attached)
          └── @references/cursor-api.md
```

**Implementation:**
1. Convert `SKILL.md` frontmatter → MDC frontmatter
2. Map `description` → `description` field
3. Convert references to separate files referenced via `@file` syntax
4. Use `globs` to auto-attach when relevant files are opened
5. Set `alwaysApply: false` for manual/auto-attached behavior

**Fidelity:** 95% - Near-perfect mapping

#### Type 2: Workflow Skills (Medium Fidelity)

**Example:** `skill-creator`, `document-skills`

**Mapping (Hybrid):**
```
Claude: .claude/skills/skill-creator/SKILL.md

Cursor: .cursor/rules/skill-creator.mdc (Manual rule)
        + .cursor/commands/create-skill.md (User command)
```

**Implementation:**
1. Create **Manual Rule** for procedural knowledge
2. Create **Command** for explicit workflow invocation
3. Rule provides context when Command is used
4. Command becomes the "entry point" user must invoke

**Tradeoff:** Loses autonomous invocation, gains explicit control

**Fidelity:** 70% - Core functionality preserved, invocation model changes

#### Type 3: Script-Heavy Skills (Low Fidelity)

**Example:** Skills with `scripts/` containing Python/Bash utilities

**Mapping (Workaround):**
```
Claude: .claude/skills/pdf-processor/
          ├── SKILL.md
          └── scripts/rotate_pdf.py

Cursor: .cursor/rules/pdf-processor.mdc
          └── Describes script usage, but scripts stored separately
        + scripts/rotate_pdf.py (project scripts/)
```

**Limitations:**
- Cursor Rules cannot execute or bundle scripts directly
- Scripts must be referenced externally
- No `allowed-tools` equivalent to restrict capabilities
- User must ensure scripts are available in project

**Fidelity:** 40% - Significant functionality gap

### Implementation Process

#### Phase 1: Directory Structure Setup

```bash
# Create Cursor extensibility directories
mkdir -p .cursor/rules
mkdir -p .cursor/commands
mkdir -p .cursor/skills

# Optional: Create symlink structure for parallel management
# This maintains compatibility with both systems
```

#### Phase 2: Conversion Utilities

Create conversion scripts:

```bash
scripts/
├── convert_skill_to_rule.py      # SKILL.md → .mdc with frontmatter
├── convert_skill_to_command.py   # SKILL.md → command .md
└── sync_skills_to_cursor.py      # Batch conversion tool
```

**Conversion Logic:**

```python
# Pseudo-code for SKILL.md → Rule conversion
def convert_to_rule(skill_path):
    skill_md = parse_skill_md(skill_path / "SKILL.md")

    mdc_content = {
        "frontmatter": {
            "description": skill_md.description,
            "globs": infer_globs(skill_md.description),  # Smart inference
            "alwaysApply": should_always_apply(skill_md)
        },
        "content": convert_markdown_body(skill_md.content)
    }

    # Handle references
    for ref_file in (skill_path / "references").glob("*.md"):
        create_reference_file(ref_file, ".cursor/rules/references/")

    write_mdc(".cursor/rules/{name}.mdc", mdc_content)
```

#### Phase 3: Smart Glob Inference

Auto-generate glob patterns from skill descriptions:

```python
# Example inference rules
DESCRIPTION_PATTERNS = {
    "PDF": ["**/*.pdf"],
    "TypeScript": ["**/*.ts", "**/*.tsx"],
    "React": ["**/*.jsx", "**/*.tsx", "**/components/**"],
    "API": ["**/api/**", "**/routes/**"],
    "database": ["**/models/**", "**/schema/**", "**/*.sql"],
}

def infer_globs(description: str) -> list[str]:
    globs = []
    for keyword, patterns in DESCRIPTION_PATTERNS.items():
        if keyword.lower() in description.lower():
            globs.extend(patterns)
    return globs or ["**/*"]  # Default to all files
```

#### Phase 4: Dual-Mode Operation

Support both systems simultaneously:

```
.claude/skills/    ← Original Skills (Claude Code)
.cursor/rules/     ← Converted Rules (Cursor)
.cursor/commands/  ← Workflow Commands (Cursor)

# Automated sync via pre-commit hook
.git/hooks/pre-commit → scripts/sync_skills_to_cursor.py
```

## Target State Specification

### Directory Structure

```
rooskills/
├── .claude/
│   └── skills/                    # Claude Code Skills (source of truth)
│       ├── architecture/
│       ├── create-llmstxt-py/
│       ├── document-skills/
│       ├── lindy-expert/
│       ├── mcp-builder/
│       ├── model-enhancement-mcp/
│       ├── scripts/
│       ├── skill-creator/
│       └── template-skill/
│
├── .cursor/
│   ├── rules/                     # Auto-generated from skills
│   │   ├── architecture.mdc
│   │   ├── create-llmstxt-py.mdc
│   │   ├── document-skills.mdc
│   │   ├── lindy-expert.mdc
│   │   ├── mcp-builder.mdc
│   │   ├── model-enhancement-mcp.mdc
│   │   ├── skill-creator.mdc
│   │   └── references/            # Extracted reference files
│   │       ├── lindy-api.md
│   │       ├── mcp-spec.md
│   │       └── skill-patterns.md
│   │
│   └── commands/                  # Workflow entry points
│       ├── create-skill.md        # From skill-creator
│       ├── document-skill.md      # From document-skills
│       ├── create-llmstxt.md      # From create-llmstxt-py
│       └── architecture-review.md # From architecture
│
├── .roo/
│   └── skills/
│       └── cursor-skills/         # Roo Mode for Cursor knowledge
│
├── scripts/
│   ├── convert_skill_to_rule.py
│   ├── convert_skill_to_command.py
│   ├── sync_skills_to_cursor.py
│   └── validate_cursor_mapping.py
│
├── specs/
│   └── cursor-skills-mapping.md   # This document
│
└── README.md
```

### Conversion Examples

#### Example 1: Knowledge Skill (skill-creator)

**Input:** `.claude/skills/skill-creator/SKILL.md`
```yaml
---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill...
---

# Skill Creator
...
```

**Output:** `.cursor/rules/skill-creator.mdc`
```mdc
---
description: Guide for creating effective skills. Use when creating or updating skills that extend capabilities.
globs: ["**/.claude/skills/**", "**/SKILL.md"]
alwaysApply: false
---

# Skill Creator

This rule provides guidance for creating effective skills.

For detailed patterns, see @references/skill-patterns.md

...
```

**Output:** `.cursor/commands/create-skill.md`
```markdown
# Create New Skill

Follow the skill creation process to build a new skill:

1. Understand concrete usage examples
2. Plan reusable skill contents
3. Initialize using init_skill.py
4. Edit SKILL.md and resources
5. Package and test

See @skill-creator rule for detailed guidance.
```

#### Example 2: API Knowledge Skill (lindy-expert)

**Input:** `.claude/skills/lindy-expert/SKILL.md`

**Output:** `.cursor/rules/lindy-expert.mdc`
```mdc
---
description: Lindy AI agent platform expertise. Use when working with Lindy integrations, agent creation, or automation workflows.
globs: ["**/lindy/**", "**/*lindy*"]
alwaysApply: false
---

# Lindy Expert

Lindy is an AI agent creation platform for business process automation.

For complete API documentation, see @references/lindy-api.md

## Core Capabilities
...
```

### Automation Workflow

```bash
# Manual conversion workflow
./scripts/convert_skill_to_rule.py .claude/skills/skill-name
./scripts/convert_skill_to_command.py .claude/skills/skill-name

# Automated sync (triggered on file changes)
./scripts/sync_skills_to_cursor.py --watch

# Validation
./scripts/validate_cursor_mapping.py
```

### Validation Criteria

The validation script ensures:

1. ✅ Every `.claude/skills/*/SKILL.md` has corresponding `.cursor/rules/*.mdc`
2. ✅ Workflow skills have corresponding `.cursor/commands/*.md`
3. ✅ All `references/` files are extracted and referenced
4. ✅ MDC frontmatter is valid
5. ✅ Glob patterns are sensible
6. ✅ No duplicate descriptions between rules
7. ⚠️ Warning for skills with `scripts/` (manual review needed)
8. ⚠️ Warning for skills with `allowed-tools` (no Cursor equivalent)

## Limitations and Gaps

### Critical Limitations

1. **No Tool Restrictions**: Claude's `allowed-tools` has no Cursor equivalent
   - **Impact:** Cannot create "safe" rules that restrict capabilities
   - **Workaround:** Document expectations in rule content, rely on user oversight

2. **No Script Execution**: Cursor Rules cannot bundle/execute scripts
   - **Impact:** Skills with `scripts/` lose deterministic execution
   - **Workaround:** Store scripts separately, document in rules, user must manage

3. **Manual Command Invocation**: Commands are user-invoked, not model-invoked
   - **Impact:** Loses autonomous skill discovery for workflows
   - **Workaround:** Hybrid approach (Rule provides context, Command is entry point)

### Minor Limitations

4. **No Progressive Disclosure Control**: Rules are either in context or not
   - **Impact:** Cannot precisely control when large reference files load
   - **Mitigation:** Use Manual rules with `@file` references

5. **Different Frontmatter Format**: MDC vs YAML
   - **Impact:** Requires conversion tooling
   - **Mitigation:** Automated conversion scripts

6. **No Native Skill Bundling**: No equivalent to Skills' unified directory structure
   - **Impact:** Rules, Commands, and references are separate
   - **Mitigation:** Maintain parallel `.cursor/skills/` for organization

## Success Metrics

### Definition of Success

The mapping is successful if:

1. ✅ 90%+ of existing Claude Skills can be represented in Cursor
2. ✅ Knowledge/reference skills work with high fidelity (>90%)
3. ✅ Workflow skills are accessible with acceptable UX (70%+ fidelity)
4. ✅ Automated conversion requires minimal manual intervention (<10% skills)
5. ✅ Both systems can coexist in same repository
6. ✅ Team can contribute to either system with auto-sync

### Measurement Plan

Track conversion metrics:

```python
{
    "total_skills": 10,
    "high_fidelity": 7,      # Knowledge skills
    "medium_fidelity": 2,    # Workflow skills
    "low_fidelity": 1,       # Script-heavy skills
    "automated": 9,          # Converted without manual edits
    "manual_review": 1       # Required manual adjustment
}
```

## Alternative Approaches Considered

### Alternative 1: Commands-Only Approach

**Rejected because:** Commands are user-invoked, losing the core "model-invoked" nature of Skills

### Alternative 2: MCP Server for Skills

Create an MCP (Model Context Protocol) server that dynamically loads Skills

**Pros:**
- Could preserve exact Skills semantics
- Works across multiple agents (Cursor, Claude Code, etc.)

**Cons:**
- Significant implementation complexity
- Requires MCP server development and maintenance
- Overkill for simple skill mapping
- Still subject to Cursor's MCP integration limitations

**Verdict:** Over-engineered for current needs, consider for v2

### Alternative 3: AGENTS.md Only

Use simple `AGENTS.md` files instead of Rules

**Pros:**
- Simplest approach
- No conversion needed

**Cons:**
- No scoping (always active)
- No references to external files
- No organization (single file)
- Cannot represent complex skills

**Verdict:** Too limited for comprehensive skill mapping

### Alternative 4: Cursor Extension

Build a Cursor extension that understands Skills natively

**Pros:**
- Could implement exact Skills semantics
- Full control over behavior

**Cons:**
- Requires VS Code extension development expertise
- Maintenance burden
- Not portable to other agents
- Still constrained by Cursor's extension API

**Verdict:** Interesting long-term option, impractical short-term

## Implementation Recommendations

### Phase 1: Proof of Concept (Week 1)

1. Convert 2-3 representative skills manually
   - 1 knowledge skill (high fidelity)
   - 1 workflow skill (medium fidelity)
   - 1 script-heavy skill (low fidelity)
2. Test in real Cursor usage
3. Document pain points and adjustments needed

### Phase 2: Automation (Week 2)

1. Build `convert_skill_to_rule.py`
2. Build `convert_skill_to_command.py`
3. Build `sync_skills_to_cursor.py` with watch mode
4. Add validation script
5. Test on all existing skills

### Phase 3: Integration (Week 3)

1. Set up git hooks for auto-sync
2. Document usage for team
3. Create contribution guidelines
4. Add CI validation

### Phase 4: Refinement (Ongoing)

1. Collect user feedback
2. Adjust glob patterns based on usage
3. Improve conversion heuristics
4. Consider MCP server for v2

## Conclusion

### Verdict: VIABLE with Acceptable Tradeoffs

Cursor provides sufficient extensibility through its **Rules** and **Commands** systems to accommodate the majority of Agent Skills use cases. While not a perfect 1:1 mapping, the hybrid approach (Rules for knowledge, Commands for workflows) achieves 70-95% fidelity depending on skill type.

### Key Success Factors

1. ✅ **Rules system is mature and powerful** - MDC format, glob patterns, nested support
2. ✅ **Commands provide workflow entry points** - User-invoked alternative to model-invoked
3. ✅ **Both systems can coexist** - Automated sync allows parallel maintenance
4. ✅ **90%+ skills can be represented** - Only script-heavy skills face major limitations

### Primary Gaps

1. ❌ **No tool restrictions** - `allowed-tools` has no equivalent
2. ❌ **No script bundling** - Scripts must be managed separately
3. ⚠️ **User invocation required for workflows** - Loses autonomous discovery

### Recommended Path Forward

1. **Adopt Hybrid Strategy**: Rules for knowledge, Commands for workflows
2. **Build Automation**: Convert and sync tools for maintainability
3. **Accept Limitations**: Document script and tool restriction gaps
4. **Monitor Usage**: Collect feedback to refine approach
5. **Consider MCP v2**: If limitations become blocking, explore MCP server approach

This mapping establishes a viable pattern for bringing Agent Skills to Cursor and potentially other coding agents with similar extensibility mechanisms.
