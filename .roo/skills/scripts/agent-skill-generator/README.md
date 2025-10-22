# Agent Skill Generator

Automated skill generation system that transforms web documentation into integrated Roo Code skills using AI-powered extraction, research, and synthesis.

## Overview

The Agent Skill Generator orchestrates multiple AI services (Firecrawl, OpenAI, Claude, Exa MCP) to:

1. **Extract Knowledge** - Scrape and summarize documentation using Firecrawl + OpenAI
2. **Research Ecosystem** - Analyze positioning and best practices using Claude + Exa
3. **Synthesize Skills** - Generate SKILL.md with structured guidance
4. **Integrate Modes** - Register skills in `.roomodes` configuration

## Architecture

```
scripts/agent-skill-generator/
├── __init__.py              # Package initialization
├── orchestrator.py          # Main CLI entry point
├── llms_generator.py        # Firecrawl + OpenAI integration
├── ecosystem_researcher.py  # Claude Agent SDK + Exa MCP
├── skill_creator.py         # SKILL.md synthesis
├── mode_configurator.py     # .roomodes updates
├── config.py                # Configuration management
├── schemas.py               # Data models (Pydantic)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Module Responsibilities

- **`orchestrator.py`** - Coordinates the complete workflow, provides CLI interface
- **`llms_generator.py`** - Maps websites and scrapes content via Firecrawl, generates summaries via OpenAI
- **`ecosystem_researcher.py`** - Conducts deep research using Claude with optional Exa MCP integration
- **`skill_creator.py`** - Synthesizes knowledge and wisdom into structured SKILL.md files
- **`mode_configurator.py`** - Manages `.roomodes` integration and validation
- **`config.py`** - Handles environment variables and settings validation
- **`schemas.py`** - Defines Pydantic models for type safety and data validation

## Installation

### Prerequisites

- Python 3.10 or higher
- API keys for: Firecrawl, OpenAI, Anthropic (Claude)
- Optional: Exa API key for enhanced ecosystem research

### Install Dependencies

```bash
# Navigate to the script directory
cd scripts/agent-skill-generator

# Install required packages
pip install -r requirements.txt
```

## Configuration

### Required Environment Variables

Create a `.env` file in your project root or set environment variables:

```bash
# Required API Keys
FIRECRAWL_API_KEY=fc-xxx...
OPENAI_API_KEY=sk-xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...

# Optional: Enhanced research via Exa MCP
EXA_API_KEY=your-exa-key
```

### Optional Configuration

```bash
# Processing limits
MAX_URLS=20                  # Maximum URLs to scrape (default: 20)
BATCH_SIZE=10                # Batch size for concurrent processing
MAX_WORKERS=5                # Thread pool workers

# Retry configuration
API_RETRY_ATTEMPTS=3         # Number of retry attempts
API_RETRY_BACKOFF=2.0        # Exponential backoff multiplier

# Rate limiting (requests per minute)
FIRECRAWL_RATE_LIMIT=10
OPENAI_RATE_LIMIT=60
```

### Security Notes

⚠️ **NEVER** hardcode API keys in code files
✅ **ALWAYS** use environment variables or `.env` files
✅ Add `.env` to `.gitignore` to prevent accidental commits

## Usage

### Basic Usage

```bash
# Generate skill from documentation URL
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://fastapi.tiangolo.com" \
    "fastapi-developer"
```

### Advanced Usage

```bash
# Generate with custom options
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://fastapi.tiangolo.com" \
    "fastapi-developer" \
    --output-dir "./my-skills/fastapi" \
    --max-urls 50 \
    --verbose
```

### Validation Only

```bash
# Validate an existing skill
python -m scripts.agent-skill-generator.orchestrator validate \
    fastapi-developer/SKILL.md
```

### Command Reference

#### `generate`

Generate a new skill from documentation URL.

**Arguments:**
- `url` - Documentation URL to process (required)
- `skill_name` - Skill identifier in kebab-case (required)

**Options:**
- `--output-dir, -o` - Output directory (default: skill-name)
- `--max-urls, -m` - Maximum URLs to process (default: 20)
- `--verbose, -v` - Enable verbose logging

#### `validate`

Validate an existing skill integration.

**Arguments:**
- `skill_path` - Path to SKILL.md file (required)

## Generated Output Structure

```
skill-name/
├── SKILL.md                 # Main skill definition
├── LICENSE.txt              # License file
└── references/              # Reference documentation
    ├── api_documentation.md # Full documentation content
    └── documentation_index.md # Quick reference index
```

### SKILL.md Structure

Generated SKILL.md files follow this pattern:

```markdown
---
name: skill-name
description: Brief description of when to use this skill
license: Complete terms in LICENSE.txt
---

# Skill Name

## Core Capabilities
## When to Use This Skill
## Ecosystem & Alternatives
## Integration Patterns
## Best Practices
## References
```

## Workflow Phases

### Phase 1: Knowledge Extraction

Uses Firecrawl to:
1. Map all URLs on the documentation site
2. Scrape content in batches (markdown format)
3. Generate titles and descriptions using OpenAI

**Output:** `KnowledgeBundle` with llms.txt and llms-full.txt

### Phase 2: Ecosystem Research

Uses Claude Agent SDK to:
1. Discover what the tool is and who uses it
2. Map ecosystem positioning and alternatives
3. Identify best practices and common pitfalls

**Output:** `WisdomDocument` with structured insights

### Phase 3: Skill Synthesis

Combines knowledge and wisdom to:
1. Extract core capabilities
2. Structure content into sections
3. Generate YAML frontmatter
4. Create reference files

**Output:** `SkillBundle` with SKILL.md and references

### Phase 4: Mode Integration

Registers the skill in `.roomodes`:
1. Validates SKILL.md structure
2. Checks for duplicate slugs
3. Adds mode entry to configuration
4. Runs validation checks

**Output:** `ModeRegistrationResult` with validation report

## Error Handling

The system includes comprehensive error handling:

- **Retry Logic** - Automatic retries with exponential backoff for API failures
- **Graceful Degradation** - Continues processing even if some pages fail
- **Validation** - Pre-flight checks before mode registration
- **Detailed Logging** - Structured logs for debugging

### Common Issues

**Missing API Keys**
```
ValueError: Missing required environment variables: FIRECRAWL_API_KEY
```
**Solution:** Set all required environment variables

**Rate Limiting**
```
429 Too Many Requests
```
**Solution:** Reduce `BATCH_SIZE` or `MAX_WORKERS`, increase delays

**Invalid SKILL.md**
```
Invalid or missing YAML frontmatter in SKILL.md
```
**Solution:** Ensure SKILL.md has valid YAML frontmatter with `name:` and `description:`

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with verbose logging
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://example.com" \
    "test-skill" \
    --verbose
```

### Code Quality Standards

- **File Size:** All modules < 500 lines
- **Type Safety:** Full type hints with Pydantic models
- **Security:** No hardcoded secrets, environment variables only
- **Error Handling:** Retry logic with exponential backoff
- **Async:** Use async/await for I/O operations where applicable

## Examples

### Generate FastAPI Skill

```bash
export FIRECRAWL_API_KEY="fc-xxx"
export OPENAI_API_KEY="sk-xxx"
export ANTHROPIC_API_KEY="sk-ant-xxx"

python -m scripts.agent-skill-generator.orchestrator generate \
    "https://fastapi.tiangolo.com" \
    "fastapi-developer" \
    --max-urls 30
```

### Generate with Custom Output Directory

```bash
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://pydantic-docs.helpmanual.io" \
    "pydantic-expert" \
    --output-dir "./custom-skills/pydantic" \
    --max-urls 40
```

## Troubleshooting

### Enable Debug Logging

```bash
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://example.com" \
    "skill-name" \
    --verbose
```

### Check Validation Status

```bash
python -m scripts.agent-skill-generator.orchestrator validate \
    skill-name/SKILL.md
```

### Verify Environment Variables

```bash
# Check if variables are set
echo $FIRECRAWL_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

## Contributing

When extending this system:

1. **Maintain modularity** - Keep files under 500 lines
2. **Use type hints** - Add Pydantic models for new data structures
3. **Handle errors** - Add retry logic for external API calls
4. **Update schemas** - Add new data models to `schemas.py`
5. **Document changes** - Update this README with new features

## License

See individual skill LICENSE.txt files for specific licensing terms.

## Architecture Reference

For detailed architecture documentation, see:
- [`architecture/agent-skill-generator-architecture.md`](../../architecture/agent-skill-generator-architecture.md)
- [`architecture/agent-skill-generator-process.md`](../../architecture/agent-skill-generator-process.md)