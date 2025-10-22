# Roo Skills

**Bring Anthropic's Agent Skills to Roo Code**

An NPM package and template that enables Roo Code users to leverage [Anthropic's Agent Skills system](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - the same powerful capability available in Claude Code.

[![npm version](https://badge.fury.io/js/@kastalien-research%2Frooskills.svg)](https://www.npmjs.com/package/@kastalien-research/rooskills)
[![npm downloads](https://img.shields.io/npm/dm/@kastalien-research/rooskills.svg)](https://www.npmjs.com/package/@kastalien-research/rooskills)

## Features

- **🚀 One-Command Setup** - Install skills in any project with `npx @kastalien-research/rooskills init`
- **🤖 Automated Generation** - Create new skills from any documentation URL
- **📚 Pre-built Skills** - Ready-to-use skills for development, AI automation, and documentation
- **🔧 CLI Tools** - Simple commands for initialization and skill generation

## Quick Start

### Installation (Recommended)

Install skills in your Roo Code project with a single command:

```bash
npx @kastalien-research/rooskills init
```

This will:
- Copy all pre-built skills to `.roo/skills/`
- Add `.roomodes` configuration for Roo Code
- Create `.env.example` with required API keys
- Optionally install Python dependencies

### Generate a New Skill

Create a custom skill from any documentation URL:

```bash
npx @kastalien-research/rooskills generate https://docs.example.com skill-name --max-urls 20
```

### List Available Skills

```bash
npx @kastalien-research/rooskills list
```

## What are Agent Skills?

Agent Skills are modular instruction sets that enhance Claude's capabilities for specific tasks. Originally developed for Claude Code, this package brings that same functionality to Roo Code by:

1. Converting Agent Skills into Roo Code custom modes via [`.roomodes`](.roomodes)
2. Organizing skills in [`.roo/skills/`](.roo/skills/) for clean project structure
3. Providing automated tools to generate new skills from documentation

## Pre-built Skills

All skills are located in [`.roo/skills/`](.roo/skills/) and registered as custom modes in [`.roomodes`](.roomodes):

#### Development & Technical
- **mcp-builder** - Create high-quality MCP (Model Context Protocol) servers for integrating external services
- **model-enhancement-mcp** - Advanced MCP server examples including analogical reasoning and sequential thinking
- **document-skills** - Comprehensive document creation and manipulation (DOCX, PDF, PPTX, XLSX)

#### AI & Automation
- **lindy-expert** - Expertise in Lindy AI agent creation and management platform for business process automation

#### Development Tools
- **create-llmstxt-py** - Python tool for generating llms.txt documentation from websites
- **skill-creator** - Meta-skill for creating new effective skills with best practices
- **template-skill** - Basic template for starting new skills

#### Documentation
- **architecture** - Architecture documentation for the skill generation system

## Advanced Usage

### Environment Variables

After initialization, create a `.env` file in your project root:

```bash
# Firecrawl API Key (get from https://firecrawl.dev)
FIRECRAWL_API_KEY=your_key_here

# OpenAI API Key (get from https://platform.openai.com)
OPENAI_API_KEY=your_key_here

# Anthropic API Key (get from https://console.anthropic.com)
ANTHROPIC_API_KEY=your_key_here

# Optional: Exa API Key for enhanced research
EXA_API_KEY=your_key_here
```

### Skill Generation Process

The skill generator runs through 5 automated phases:

1. **Knowledge Extraction** - Scrapes and summarizes documentation using Firecrawl + OpenAI
2. **Ecosystem Research** - Analyzes positioning and best practices using Claude + Exa
3. **Skill Synthesis** - Generates structured SKILL.md with comprehensive guidance
4. **File Writing** - Creates all skill files and reference documentation
5. **Mode Registration** - Registers the skill as a mode in `.roomodes`

### Generated Skill Structure

Each generated skill includes:
```
.roo/skills/skill-name/
├── SKILL.md                          # Main skill file with YAML frontmatter
├── LICENSE.txt                       # License information
└── references/
    ├── api_documentation.md          # Complete API/documentation content
    └── documentation_index.md        # Curated index of key resources
```

### Manual Installation (Alternative)

If you prefer not to use the NPM package:

1. **Fork or Clone** this repository to your Roo Code workspace
2. **Copy `.env.example`** to `.env` and add your API keys
3. **Import the `.roomodes` configuration** into your Roo Code settings
4. Skills in [`.roo/skills/`](.roo/skills/) will be available as custom modes

### For Claude Code Users

While this package is designed for Roo Code, the skills themselves are compatible with Claude Code's native Agent Skills system:

1. Skills can be used directly from [Anthropic's official skills repository](https://github.com/anthropics/skills)
2. Or you can copy individual skills from this template's `.roo/skills/` directory

## Using Skills in Roo Code

Skills are automatically loaded from `.roomodes` and can be activated by:
1. Mentioning the skill name in your conversation
2. Switching to the skill's mode using the mode selector
3. Referencing skills in task delegation

## CLI Reference

### `rooskills init`

Initialize Roo Skills in your project.

**Options:**
- `-d, --dir <directory>` - Target directory (default: current directory)
- `--no-install` - Skip Python dependency installation
- `--skills <skills...>` - Install specific skills only

**Examples:**
```bash
rooskills init
rooskills init -d ./my-project
rooskills init --no-install
```

### `rooskills generate <url> [skill-name]`

Generate a new skill from documentation URL.

**Arguments:**
- `url` - Documentation URL to process (required)
- `skill-name` - Skill identifier in kebab-case (optional)

**Options:**
- `--max-urls <number>` - Maximum URLs to process (default: 20)
- `--output-dir <directory>` - Custom output directory
- `--verbose` - Enable verbose logging

**Examples:**
```bash
rooskills generate https://fastapi.tiangolo.com
rooskills generate https://docs.stripe.com stripe-expert --max-urls 30
```

### `rooskills list`

List all available pre-built skills.

## Validation

Validate skill integration:
```bash
python .roo/skills/scripts/validate_mode_skill_integration.py
```

This checks:
- SKILL.md file exists and is properly formatted
- YAML frontmatter is valid
- No duplicate slugs in `.roomodes`
- File sizes are within limits (<500 lines)
- Skills are properly registered

## Project Structure

```
rooskills/
├── .env                              # Environment variables (git-ignored)
├── .roomodes                         # Mode configuration file
├── README.md                         # This file
├── agent_skills_spec.md              # Skills specification
└── .roo/
    └── skills/                       # All skills directory
        ├── architecture/             # Architecture documentation
        ├── create-llmstxt-py/        # Python tool for llms.txt generation
        ├── document-skills/          # Document creation (DOCX, PDF, PPTX, XLSX)
        ├── lindy-expert/             # Lindy AI automation platform skill
        ├── mcp-builder/              # MCP server creation skill
        ├── model-enhancement-mcp/    # Advanced MCP examples
        ├── skill-creator/            # Meta-skill for creating skills
        ├── template-skill/           # Basic skill template
        └── scripts/                  # Skill generation scripts
            ├── agent-skill-generator/
            │   ├── config.py         # Configuration management
            │   ├── orchestrator.py   # Main CLI entry point
            │   ├── llms_generator.py # Knowledge extraction
            │   ├── ecosystem_researcher.py
            │   ├── skill_creator.py  # Skill synthesis
            │   └── mode_configurator.py
            ├── commands/
            │   └── generate-skill.sh # Shell wrapper
            └── validate_mode_skill_integration.py
```

## Architecture

The skill generator follows a modular, pipeline-based architecture:

- **Configuration** - Environment-based settings (never hardcoded secrets)
- **Knowledge Extraction** - Firecrawl + OpenAI for documentation processing
- **Research** - Claude + Exa for ecosystem analysis
- **Synthesis** - Structured skill creation with best practices
- **Validation** - Comprehensive integration checks

See [`architecture/`](architecture/) for detailed documentation.

## Best Practices

### When Creating Skills
- Keep SKILL.md under 500 lines - move detailed content to references/
- Use clear, descriptive frontmatter (name, description)
- Provide specific examples and guidelines
- Include integration patterns and common pitfalls
- Never hardcode secrets or environment-specific values

### When Generating Skills
- Start with smaller `--max-urls` values (10-15) for faster results
- Review generated content before committing
- Customize the SKILL.md to add organization-specific knowledge
- Test the skill thoroughly before deploying

## Contributing

Skills in this repository use modular architecture principles:
- Files should be < 500 lines
- Use environment variables for configuration
- Follow clean architecture patterns
- Document all functionality clearly

## License

See individual skill directories for licensing information. Most skills use MIT License unless otherwise specified.

## Resources & References

### Anthropic's Agent Skills
- [Official Agent Skills Repository](https://github.com/anthropics/skills) - Original skills for Claude Code
- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills) - Understanding the skills system
- [Equipping Agents for the Real World](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - Engineering blog post
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) - Official guide

### This Template
- [Architecture Documentation](architecture/) - Skill generation system design
- [Validation Scripts](.roo/skills/scripts/) - Testing and validation tools
- [Skill Creator Skill](.roo/skills/skill-creator/) - Meta-skill for creating new skills

## Compatibility

### Agent Skills Format
This template uses Anthropic's Agent Skills format (YAML frontmatter + Markdown instructions), ensuring skills are:
- **Portable** - Work in both Roo Code and Claude Code (with appropriate configuration)
- **Standard** - Follow Anthropic's established patterns and best practices
- **Maintainable** - Compatible with future skill format updates

### Roo Code Integration
Skills integrate with Roo Code through:
- **Custom Modes** - Each skill becomes a mode in [`.roomodes`](.roomodes)
- **Skill References** - Skills are loaded dynamically via `skill_ref` paths
- **Override Strategy** - Skill content overrides default mode instructions

## Support

For issues, questions, or contributions:
1. Check existing [documentation](architecture/)
2. Review [validation scripts](.roo/skills/scripts/)
3. Consult the [skill creator skill](.roo/skills/skill-creator/)
4. Reference [Anthropic's official skills documentation](https://github.com/anthropics/skills)

---

**Note:** This is a template repository that bridges Anthropic's Agent Skills system with Roo Code. Skills are compatible with the official Agent Skills format and can be shared between Claude Code and Roo Code environments.