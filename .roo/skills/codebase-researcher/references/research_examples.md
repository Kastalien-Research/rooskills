# Codebase Research Examples

This document provides example outputs and use cases for the codebase researcher skill.

## Example 1: NPM Package Analysis

### Input
```bash
/deep-research
```

### Detected Directories
- `cli/` - Command-line interface tools
- `scripts/` - Automation and generation scripts
- `.roo/` - Skills and configuration
- `specs/` - Technical specifications
- `coding-agent-docs/` - Documentation cache

### Generated Subagents
- `cli-analyzer` - Analyzes CLI structure and commands
- `scripts-analyzer` - Examines automation scripts
- `roo-analyzer` - Reviews skills ecosystem
- `specs-analyzer` - Processes technical specifications
- `coding-agent-docs-analyzer` - Catalogs documentation

### Sample Output (CLAUDE.md)

```markdown
# Rooskills Project Knowledge

## Project Overview

Rooskills is an NPM package that brings Anthropic's Agent Skills system to Roo Code users. It provides CLI tools for initializing skills and generating new skills from documentation URLs.

## Architecture

### Key Components

1. **CLI Layer** (`cli/`)
   - Entry point: `cli/index.js`
   - Commands: `init` and `generate`
   - Distribution: Published via NPM

2. **Skills Ecosystem** (`.roo/skills/`)
   - Pre-built skills: mcp-builder, lindy-expert, cursor-skills, etc.
   - Skill structure: SKILL.md + references/ + scripts/
   - Integration: Via `.roomodes` configuration

3. **Generation Pipeline** (`scripts/`)
   - Knowledge extraction (Firecrawl + OpenAI)
   - Ecosystem research (Claude + Exa)
   - Skill synthesis and validation
   
4. **Specifications** (`specs/`)
   - Enhanced skill generator pipeline
   - Cursor skills mapping
   - Architecture documentation

## Patterns and Conventions

- **Modularity**: Files kept under 500 lines
- **Environment Safety**: No hardcoded secrets
- **Progressive Disclosure**: SKILL.md → references/ → scripts/
- **Skill Format**: YAML frontmatter + Markdown body

## Getting Started

1. Install: `npm install -g @kastalien-research/rooskills`
2. Initialize: `npx rooskills init`
3. Generate skills: `npx rooskills generate <url> <skill-name>`
```

## Example 2: Monorepo Analysis

### Input
```bash
./.roo/skills/codebase-researcher/scripts/deep_research.sh --dirs "packages,apps,libs"
```

### Focused Analysis
Only analyzes specified directories for faster, targeted research.

### Output
Focused documentation on:
- Package boundaries
- Shared libraries
- Application architecture
- Inter-package dependencies

## Example 3: Documentation Update

### Scenario
Codebase has evolved significantly since last documentation.

### Input
```bash
/deep-research
```

### Process
1. Analyzes current state
2. Compares with existing CLAUDE.md
3. Identifies changes and updates
4. Generates fresh documentation

### Result
- Updated CLAUDE.md with current architecture
- New `.claude/agents/` files reflecting current structure
- Updated `.roomodes` with latest knowledge

## Example 4: Onboarding Aid

### Use Case
New team member needs to understand the project quickly.

### Workflow
```bash
# 1. Run deep research
/deep-research

# 2. Review CLAUDE.md
cat CLAUDE.md

# 3. Explore specific areas
claude --agents '{
  "feature-x-analyzer": {
    "description": "Deep dive into feature X implementation",
    "prompt": "Analyze feature X in detail, including data flow and integration points.",
    "tools": ["Read", "Glob", "Grep"]
  }
}'
```

### Benefit
Comprehensive understanding without extensive pair programming time.

## Example 5: Technical Debt Audit

### Goal
Identify areas needing refactoring or documentation.

### Input
```bash
/deep-research
```

### Analysis Focus
Each subagent identifies:
- Missing documentation
- Complex code requiring simplification
- Inconsistent patterns
- Technical debt items

### Output
Structured technical debt report in `references/technical_debt.md`.

## Common Research Scenarios

### New Project Setup
**Goal**: Create initial CLAUDE.md for AI-assisted development  
**Command**: `/deep-research`  
**Output**: Comprehensive project knowledge base

### Architecture Documentation
**Goal**: Document system architecture for team  
**Command**: `/deep-research --output ./docs`  
**Output**: Architecture diagrams and documentation

### Code Review Preparation
**Goal**: Understand codebase before major review  
**Command**: `/deep-research --dirs "src,tests"`  
**Output**: Focused analysis of code and test quality

### Migration Planning
**Goal**: Assess effort for technology migration  
**Command**: `/deep-research`  
**Output**: Dependency map and migration complexity assessment

### Knowledge Transfer
**Goal**: Capture departing team member's knowledge  
**Command**: `/deep-research`  
**Output**: Comprehensive codebase documentation

## Output Artifacts

### 1. CLAUDE.md
Primary knowledge base containing:
- Project overview
- Architecture summary
- Key components
- Patterns and conventions
- Getting started guide

### 2. .claude/agents/*.md
Persistent subagents for future use:
- One agent per analyzed directory
- Specialized knowledge and context
- Reusable for targeted analysis

### 3. .roomodes
Updated configuration:
- Codebase-researcher mode registered
- Skill reference configured
- Project-specific context loaded

### 4. references/
Supporting documentation:
- `codebase_structure.md` - Detailed directory analysis
- `patterns.md` - Code conventions and patterns
- `dependencies.md` - Dependency graph
- `technical_debt.md` - Issues and improvements

## Iteration and Refinement

### Initial Research
Broad analysis covering all important directories.

### Focused Deep Dives
Target specific areas for detailed investigation:
```bash
claude --agents '{
  "auth-analyzer": {
    "description": "Deep analysis of authentication system",
    "prompt": "Analyze authentication flows, security measures, and user management in detail.",
    "tools": ["Read", "Grep", "Bash"]
  }
}'
```

### Periodic Updates
Re-run research as codebase evolves to keep documentation current.

## Integration with Workflow

### 1. Project Initialization
```bash
git clone repo
cd repo
/deep-research
# Now have comprehensive understanding
```

### 2. Feature Development
```bash
# Research relevant areas
/deep-research --dirs "src/features,src/api"
# Develop with context
```

### 3. Code Review
```bash
# Understand changes
/deep-research --dirs "modified-directory"
# Review with full context
```

### 4. Refactoring
```bash
# Map current state
/deep-research
# Plan refactoring with architectural understanding
```

## Success Metrics

Good research output includes:
- ✅ Accurate reflection of codebase
- ✅ Clear architecture explanation
- ✅ Actionable insights and patterns
- ✅ Useful for both AI and humans
- ✅ Maintainable and updateable

## See Also

- [Subagent Templates](subagent_templates.md) - Template configurations
- [Deep Research Script](../scripts/deep_research.sh) - Implementation
- [SKILL.md](../SKILL.md) - Main skill documentation