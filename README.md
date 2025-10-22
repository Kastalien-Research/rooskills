# Roo Code Skills Template

**Bring Anthropic's Agent Skills to Roo Code**

This repository is a template that enables Roo Code users to leverage [Anthropic's Agent Skills system](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - the same powerful capability available in Claude Code. It provides:

- **Skills Integration** - Use Anthropic's Agent Skills format in Roo Code through custom modes
- **Automated Generation** - Create new skills from any documentation URL
- **Pre-built Skills** - Ready-to-use skills for development, AI automation, and documentation

## What are Agent Skills?

Agent Skills are modular instruction sets that enhance Claude's capabilities for specific tasks. Originally developed for Claude Code, this template brings that same functionality to Roo Code by:

1. Converting Agent Skills into Roo Code custom modes via [`.roomodes`](.roomodes)
2. Organizing skills in [`.roo/skills/`](.roo/skills/) for clean project structure
3. Providing automated tools to generate new skills from documentation

This means Roo Code users get the same skill-based enhancements that Claude Code users enjoy.

## Features

### 🤖 Automated Skill Generator
The repository includes a powerful skill generation system that can automatically create comprehensive skills from documentation URLs using:
- **Firecrawl** for web scraping and content extraction
- **OpenAI GPT-4o-mini** for knowledge summarization
- **Claude Agent SDK (Anthropic)** for ecosystem research and best practices
- **Exa MCP** for supplementary research

### 📚 Pre-built Skills
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

## Using This Template

### For Roo Code Users

1. **Fork or Clone** this repository to your Roo Code workspace
2. **Copy `.env.example`** (if provided) to `.env` and add your API keys
3. **Import the `.roomodes` configuration** into your Roo Code settings
4. Skills in [`.roo/skills/`](.roo/skills/) will be available as custom modes

### For Claude Code Users

While this template is designed for Roo Code, the skills themselves are compatible with Claude Code's native Agent Skills system:

1. Skills can be used directly from [Anthropic's official skills repository](https://github.com/anthropics/skills)
2. Or you can copy individual skills from this template's `.roo/skills/` directory

## Quick Start

### Prerequisites

1. **Environment Variables** - Create a `.env` file in the project root:
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

2. **Python Dependencies** - Install required packages:
```bash
pip install -r .roo/skills/scripts/agent-skill-generator/requirements.txt
```

### Generating a New Skill

Use the skill generator to create a new skill from any documentation URL:

```bash
./.roo/skills/scripts/commands/generate-skill.sh "https://docs.example.com/" "skill-name" --max-urls 15
```

**Parameters:**
- `URL` - Documentation URL to process (required)
- `SKILL_NAME` - Skill identifier in kebab-case (optional, auto-generated from URL)
- `--max-urls N` - Maximum number of URLs to process (default: 20)
- `--output-dir DIR` - Output directory (default: .roo/skills/SKILL_NAME)
- `--verbose` - Enable verbose logging
- `--help` - Show help message

**Example:**
```bash
# Generate a FastAPI skill
./.roo/skills/scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" "fastapi-expert" --max-urls 30

# Generate with auto-detected name
./.roo/skills/scripts/commands/generate-skill.sh "https://docs.stripe.com/"
```

### Generation Process

The skill generator runs through 5 automated phases:

1. **Knowledge Extraction** - Scrapes and summarizes documentation using Firecrawl + OpenAI
2. **Ecosystem Research** - Analyzes positioning and best practices using Claude + Exa
3. **Skill Synthesis** - Generates structured SKILL.md with comprehensive guidance
4. **File Writing** - Creates all skill files and reference documentation
5. **Mode Registration** - Registers the skill as a mode in `.roomodes`

### Output Structure

Each generated skill includes:
```
.roo/skills/skill-name/
├── SKILL.md                          # Main skill file with YAML frontmatter
├── LICENSE.txt                       # License information
└── references/
    ├── api_documentation.md          # Complete API/documentation content
    └── documentation_index.md        # Curated index of key resources
```

## Using Skills in Roo Code

### Roo Code Plugin Marketplace
Register this repository as a plugin marketplace:
```bash
/plugin marketplace add username/rooskills
```

### Manual Skill Usage
Skills are automatically loaded from `.roomodes` and can be activated by:
1. Mentioning the skill name in your conversation
2. Switching to the skill's mode using the mode selector
3. Referencing skills in task delegation

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