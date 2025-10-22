# Codebase Researcher Skill

A systematic deep research skill for analyzing codebases from the top level down, generating comprehensive knowledge about project structure, architecture, and implementation patterns.

## Overview

This skill enables Claude to perform systematic, hierarchical analysis of codebases by:
- Spawning specialized subagents for each important root-level directory
- Conducting parallel, deep analysis across the codebase
- Aggregating findings into cohesive documentation
- Generating knowledge artifacts (SKILL.md, CLAUDE.md, references/)

## Quick Start

### Using the Slash Command

The easiest way to use this skill is through the `/deep-research` slash command:

```
/deep-research
```

This will automatically:
1. Scan your project for important directories
2. Generate and execute specialized subagents
3. Create comprehensive documentation in `.claude/` and project root
4. Update your `.roomodes` configuration

### Manual Usage

You can also invoke the research process manually:

```bash
.roo/skills/codebase-researcher/scripts/deep_research.sh
```

#### Options

- `--dirs "dir1,dir2,dir3"` - Specify which directories to research
- `--output "path/to/output"` - Set custom output location
- `--dry-run` - Preview the research plan without execution
- `--format json|markdown` - Choose output format (default: markdown)

#### Examples

Research specific directories:
```bash
./deep_research.sh --dirs "src,lib,api"
```

Preview research plan:
```bash
./deep_research.sh --dry-run
```

Custom output location:
```bash
./deep_research.sh --output ".docs/research"
```

## Features

### Automatic Directory Detection

The skill intelligently identifies important directories while excluding:
- Dependencies (`node_modules/`, `venv/`, etc.)
- Build artifacts (`dist/`, `build/`, `out/`, etc.)
- Version control (`.git/`, `.svn/`, etc.)
- Cache directories (`__pycache__`, `*.egg-info`, etc.)

### Specialized Subagents

Each directory gets a subagent configured with:
- Directory-specific context and focus
- Appropriate read-only tools
- Targeted research objectives
- Quality criteria for findings

### Comprehensive Output

The skill generates multiple artifacts:

1. **CLAUDE.md** - Global codebase knowledge in project root
2. **.claude/agents/*.md** - Persistent subagent configurations
3. **references/** - Supporting documentation, diagrams, examples
4. **.roomodes** - Updated with new research knowledge

## Structure

```
codebase-researcher/
├── SKILL.md                    # Main skill definition
├── README.md                   # This file
├── LICENSE.txt                 # MIT License
├── scripts/
│   └── deep_research.sh        # Research automation script
└── references/
    ├── subagent_templates.md   # Subagent configuration templates
    ├── research_examples.md    # Usage examples and outputs
    └── claude_code_integration.md  # Technical integration guide
```

## Integration

### Roo Code

The skill integrates with Roo Code through:
- `.roomodes` updates with research findings
- Custom modes for specialized analysis
- Slash command integration

### Claude Code

The skill leverages Claude Code's:
- `--agents` flag for programmatic subagent creation
- Headless mode (`-p`) for non-interactive execution
- Permission modes for safe, read-only analysis
- Persistent `.claude/agents/` configurations

## Requirements

- Bash shell (macOS, Linux, or WSL on Windows)
- Claude Code CLI installed and configured
- `jq` for JSON processing (optional but recommended)
- Python 3 for `.roomodes` updates (optional)

## Best Practices

### When to Use

✅ Starting work on a new codebase
✅ Documenting existing architecture
✅ Creating CLAUDE.md or SKILL.md files
✅ Performing comprehensive code audits
✅ Building team knowledge bases
✅ Onboarding new developers

### When NOT to Use

❌ Quick file searches (use `search_files` instead)
❌ Single-file analysis (use `read_file` instead)
❌ Real-time debugging (use `debug` mode instead)
❌ Small scripts or utilities (overkill for simple codebases)

### Quality Criteria

Good research should:
- Document architecture and key patterns
- Identify important dependencies and relationships
- Note conventions and coding standards
- Highlight potential issues or technical debt
- Provide actionable insights for developers

## Troubleshooting

### Script won't execute

Make the script executable:
```bash
chmod +x .roo/skills/codebase-researcher/scripts/deep_research.sh
```

### No directories found

Check your ignore patterns or specify directories manually:
```bash
./deep_research.sh --dirs "src,lib"
```

### Subagents fail to generate

Ensure Claude Code is properly configured:
```bash
claude --version
claude --help
```

### Output not generated

Check permissions and disk space:
```bash
ls -la .claude/
df -h
```

## Examples

### Full Project Analysis

Research an entire project:
```bash
/deep-research
```

Expected output:
- `CLAUDE.md` in project root
- `.claude/agents/src.md`, `.claude/agents/lib.md`, etc.
- Updated `.roomodes` with new knowledge
- `references/` directory with supporting docs

### Targeted Research

Focus on specific directories:
```bash
.roo/skills/codebase-researcher/scripts/deep_research.sh --dirs "api,db"
```

### Documentation Generation

Generate docs for onboarding:
```bash
./deep_research.sh --format markdown --output ".docs/onboarding"
```

## Contributing

To enhance this skill:

1. Review the [Agent Skills Spec](../../../agent_skills_spec.md)
2. Follow the existing structure and conventions
3. Test changes with both Roo Code and Claude Code
4. Update documentation to reflect changes

## License

MIT License - See [LICENSE.txt](LICENSE.txt) for details

## Support

For issues or questions:
- Check the [troubleshooting section](#troubleshooting)
- Review [references/claude_code_integration.md](references/claude_code_integration.md)
- Consult the main [rooskills README](../../../README.md)

## Version History

- **1.0.0** (2025-10-22) - Initial release
  - Deep research algorithm implementation
  - Slash command integration
  - Automated subagent generation
  - Comprehensive documentation and examples