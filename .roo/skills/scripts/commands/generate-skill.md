# Generate Skill Command Documentation

Comprehensive guide for the `/generate-skill` command that transforms web documentation into integrated Roo Code skills.

## Command Overview

The [`generate-skill.sh`](./generate-skill.sh) command is a shell wrapper that orchestrates an automated skill generation pipeline. It transforms any web documentation into a complete, production-ready Roo Code skill with structured guidance, references, and automatic mode registration.

### What It Does

- **Extracts Knowledge**: Scrapes and summarizes documentation using Firecrawl + OpenAI
- **Researches Ecosystem**: Analyzes positioning, alternatives, and best practices using Claude + Exa
- **Synthesizes Skills**: Generates [`SKILL.md`](../../template-skill/SKILL.md) with structured guidance and examples
- **Creates References**: Builds supporting documentation files for quick lookup
- **Registers Modes**: Automatically integrates skills into [`.roomodes`](../../.roomodes) configuration

### When to Use It

Use this command when you want to:
- Create a new Roo Code skill from API documentation
- Convert framework docs into an AI-friendly skill
- Build specialized knowledge bases from technical documentation
- Automate skill creation from any web-based documentation source

**Implementation**: See [`scripts/agent-skill-generator/orchestrator.py`](../agent-skill-generator/orchestrator.py) for the Python orchestration logic.

---

## Quick Start

### Minimal Example

Generate a skill with auto-detected name:

```bash
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com"
```

**Output**: Creates `./fastapi/` with SKILL.md, LICENSE.txt, and references/

### With Custom Name

Specify a custom skill identifier:

```bash
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" "fastapi-developer"
```

**Output**: Creates `./fastapi-developer/` directory

### With Options

Customize processing limits and logging:

```bash
./scripts/commands/generate-skill.sh \
    "https://fastapi.tiangolo.com" \
    "fastapi-dev" \
    --max-urls 30 \
    --verbose
```

**Output**: Processes up to 30 pages with detailed logging

---

## Full Usage Reference

### Syntax

```bash
./scripts/commands/generate-skill.sh <URL> [SKILL_NAME] [OPTIONS]
```

### Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `URL` | Yes | Documentation URL to process | `https://fastapi.tiangolo.com` |
| `SKILL_NAME` | No | Skill identifier in kebab-case (auto-generated if omitted) | `fastapi-developer` |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--max-urls N` | Integer | 20 | Maximum number of URLs to process |
| `--use-feynman` | Boolean | true | Enable Feynman technique for documentation |
| `--output-dir DIR` | Path | `SKILL_NAME` | Output directory for generated files |
| `--verbose` | Flag | false | Enable verbose logging for debugging |
| `--help` | Flag | - | Show help message and exit |

### Auto-Generated Skill Names

When `SKILL_NAME` is omitted, the command generates it from the URL:

| Input URL | Generated Name |
|-----------|----------------|
| `https://fastapi.tiangolo.com` | `fastapi` |
| `https://docs.nestjs.com` | `docs-nestjs` |
| `https://www.postgresql.org/docs` | `postgresql` |
| `https://api.example.com/docs` | `example` |

**Implementation**: See [`generate_skill_name_from_url()`](./generate-skill.sh:214-230) function.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - skill generated and registered |
| 1 | Missing arguments or environment variables |
| >1 | Python orchestrator failure (see logs) |

---

## Workflow Phases

The command orchestrates a 5-phase pipeline coordinated by [`orchestrator.py`](../agent-skill-generator/orchestrator.py).

### Phase 1: Knowledge Extraction

**Module**: [`llms_generator.py`](../agent-skill-generator/llms_generator.py)

**Process**:
1. Maps all URLs on the documentation site using Firecrawl
2. Scrapes content in batches (markdown format)
3. Generates titles and descriptions using OpenAI
4. Creates llms.txt (summary) and llms-full.txt (complete content)

**Duration**: 2-5 minutes depending on URL count

**Output**: `KnowledgeBundle` with structured documentation

**Example Output**:
```
Phase 1: Extracting documentation knowledge...
✓ Processed 23 pages
```

### Phase 2: Ecosystem Research

**Module**: [`ecosystem_researcher.py`](../agent-skill-generator/ecosystem_researcher.py)

**Process**:
1. Analyzes what the tool is and who uses it
2. Maps ecosystem positioning and alternatives
3. Identifies best practices and common pitfalls
4. Uses Claude Agent SDK with optional Exa MCP integration

**Duration**: 1-3 minutes

**Output**: `WisdomDocument` with strategic insights

**Example Output**:
```
Phase 2: Researching ecosystem and best practices...
✓ Research complete
```

### Phase 3: Skill Synthesis

**Module**: [`skill_creator.py`](../agent-skill-generator/skill_creator.py)

**Process**:
1. Combines knowledge bundle and wisdom document
2. Extracts core capabilities and use cases
3. Structures content into SKILL.md sections
4. Generates YAML frontmatter with metadata
5. Creates reference documentation files

**Duration**: 1-2 minutes

**Output**: `SkillBundle` with SKILL.md and references

**Example Output**:
```
Phase 3: Creating SKILL.md and references...
✓ Skill synthesized
```

### Phase 4: File Writing

**Module**: [`orchestrator.py:_write_skill_files()`](../agent-skill-generator/orchestrator.py:143-173)

**Process**:
1. Creates skill directory structure
2. Writes SKILL.md with complete content
3. Writes reference files to `references/` subdirectory
4. Generates LICENSE.txt file

**Duration**: <1 second

**Output Structure**:
```
skill-name/
├── SKILL.md                      # Main skill definition
├── LICENSE.txt                   # License information
└── references/                   # Supporting documentation
    ├── api_documentation.md      # Full API reference
    └── documentation_index.md    # Quick lookup index
```

**Example Output**:
```
Phase 4: Writing skill files...
✓ Files written to ./fastapi-developer
```

### Phase 5: Mode Registration

**Module**: [`mode_configurator.py`](../agent-skill-generator/mode_configurator.py)

**Process**:
1. Validates SKILL.md structure and frontmatter
2. Checks for duplicate mode slugs in [`.roomodes`](../../.roomodes)
3. Adds mode entry to configuration
4. Runs integration validation checks
5. Reports warnings or errors

**Duration**: <1 second

**Output**: `ModeRegistrationResult` with validation report

**Example Output**:
```
Phase 5: Registering mode in .roomodes...
✓ Mode registered successfully

Validation Results:
  ✓ YAML frontmatter valid
  ✓ Required fields present
  ✓ File patterns valid
  ✓ Mode slug unique
```

---

## Prerequisites

### Required API Keys

Set these environment variables before running the command:

```bash
export FIRECRAWL_API_KEY="fc-your-key-here"
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Where to Get Keys**:
- **Firecrawl**: https://firecrawl.dev (web scraping)
- **OpenAI**: https://platform.openai.com (summarization)
- **Anthropic**: https://console.anthropic.com (research & synthesis)

**Optional**: `EXA_API_KEY` for enhanced ecosystem research via Exa MCP

### Using .env Files

Create `.env` in project root:

```bash
# Required Keys
FIRECRAWL_API_KEY=fc-xxx...
OPENAI_API_KEY=sk-xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...

# Optional Keys
EXA_API_KEY=your-exa-key
```

**Security Note**: Add `.env` to [`.gitignore`](../../.gitignore) to prevent accidental commits.

### System Requirements

- **Bash**: 4.0 or higher
- **Python**: 3.10 or higher
- **Dependencies**: Auto-installed from [`requirements.txt`](../agent-skill-generator/requirements.txt)

### Verification

Check environment setup:

```bash
# Verify API keys are set
echo $FIRECRAWL_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Check Python version
python3 --version

# Test script execution
./scripts/commands/generate-skill.sh --help
```

---

## Common Use Cases

### API Framework Documentation

Generate skills for web frameworks:

```bash
# FastAPI
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com"

# NestJS
./scripts/commands/generate-skill.sh "https://docs.nestjs.com" "nestjs-developer"

# Django
./scripts/commands/generate-skill.sh \
    "https://docs.djangoproject.com" \
    "django-expert" \
    --max-urls 40
```

### Database Documentation

Create database administration skills:

```bash
# PostgreSQL
./scripts/commands/generate-skill.sh \
    "https://www.postgresql.org/docs/current" \
    "postgresql-admin" \
    --max-urls 60

# MongoDB
./scripts/commands/generate-skill.sh "https://docs.mongodb.com"
```

### Cloud Platform Documentation

Build cloud service skills:

```bash
# Google Cloud Firestore
./scripts/commands/generate-skill.sh \
    "https://cloud.google.com/firestore/docs" \
    "firestore-developer" \
    --output-dir "./cloud-skills/gcp"

# AWS Lambda
./scripts/commands/generate-skill.sh \
    "https://docs.aws.amazon.com/lambda" \
    "aws-lambda-expert"
```

### Testing Framework Documentation

Generate testing tool skills:

```bash
# pytest
./scripts/commands/generate-skill.sh "https://docs.pytest.org" "pytest-expert"

# Jest
./scripts/commands/generate-skill.sh "https://jestjs.io/docs" "jest-testing"
```

### Custom Output Organization

Organize skills into categorized directories:

```bash
# Backend skills
./scripts/commands/generate-skill.sh \
    "https://fastapi.tiangolo.com" \
    "fastapi" \
    --output-dir "./skills/backend/fastapi"

# Frontend skills
./scripts/commands/generate-skill.sh \
    "https://react.dev" \
    "react" \
    --output-dir "./skills/frontend/react"
```

### Batch Processing

Generate multiple skills in sequence:

```bash
#!/bin/bash
# batch-generate.sh

URLS=(
    "https://fastapi.tiangolo.com:fastapi-dev"
    "https://flask.palletsprojects.com:flask-dev"
    "https://docs.djangoproject.com:django-dev"
)

for entry in "${URLS[@]}"; do
    IFS=':' read -r url name <<< "$entry"
    ./scripts/commands/generate-skill.sh "$url" "$name"
done
```

---

## Troubleshooting

### Missing Environment Variables

**Error**:
```
✗ Error: Missing required environment variables:
  - FIRECRAWL_API_KEY
  - OPENAI_API_KEY
```

**Solution**:
```bash
# Set missing variables
export FIRECRAWL_API_KEY="fc-your-key"
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Or source from .env
set -a
source .env
set +a
```

### Python Dependencies Missing

**Error**:
```
⚠ Warning: Some Python dependencies are missing
```

**Solution**: Dependencies are auto-installed, but you can manually install:
```bash
pip install -r scripts/agent-skill-generator/requirements.txt
```

### Rate Limiting Issues

**Error**:
```
429 Too Many Requests
```

**Solution**: Reduce processing speed:
```bash
# Lower max URLs
./scripts/commands/generate-skill.sh "https://example.com" --max-urls 10

# Process in batches with delays
./scripts/commands/generate-skill.sh "https://site1.com" && sleep 60
./scripts/commands/generate-skill.sh "https://site2.com"
```

### Invalid SKILL.md Generated

**Error**:
```
Invalid or missing YAML frontmatter in SKILL.md
```

**Solution**: Validate and regenerate:
```bash
# Check validation
python -m scripts.agent-skill-generator.orchestrator validate \
    skill-name/SKILL.md

# Regenerate with verbose logging
./scripts/commands/generate-skill.sh \
    "https://example.com" \
    "skill-name" \
    --verbose
```

### Scraping Failures

**Error**:
```
Failed to scrape URL: Connection timeout
```

**Solution**:
1. Verify URL is accessible in browser
2. Check for rate limiting or geo-restrictions
3. Try with fewer pages: `--max-urls 5`
4. Enable verbose mode to see detailed errors: `--verbose`

### Permission Errors

**Error**:
```
Permission denied: ./scripts/commands/generate-skill.sh
```

**Solution**:
```bash
chmod +x scripts/commands/generate-skill.sh
```

### Enable Debug Logging

For detailed troubleshooting:

```bash
./scripts/commands/generate-skill.sh \
    "https://example.com" \
    "debug-skill" \
    --max-urls 5 \
    --verbose
```

This shows:
- API call details
- Phase-by-phase progress
- Error stack traces
- Validation results

---

## Integration with Roo Code

### Automatic Registration

Generated skills are automatically registered in [`.roomodes`](../../.roomodes):

```json
{
  "skill-name": {
    "slug": "skill-name",
    "name": "Skill Display Name",
    "roleDefinition": "Brief description...",
    "groups": ["read", "edit"],
    "skillPath": "skill-name/SKILL.md"
  }
}
```

### Using Generated Skills

After generation, activate the skill in Roo Code:

1. **Restart Roo Code** to load new mode
2. **Switch to mode**: `/mode skill-name`
3. **Verify activation**: Check mode indicator
4. **Test functionality**: Try example prompts from SKILL.md

### Skill Structure

Each generated skill follows this pattern:

```markdown
---
name: skill-name
description: When to use this skill
license: See LICENSE.txt
---

# Skill Name

## Core Capabilities
- Feature 1
- Feature 2

## When to Use This Skill
Use cases and scenarios

## Ecosystem & Alternatives
Positioning in the ecosystem

## Integration Patterns
How to integrate with other tools

## Best Practices
Recommended approaches

## References
- [API Documentation](references/api_documentation.md)
- [Quick Index](references/documentation_index.md)
```

### Validation

Validate skill integration:

```bash
python -m scripts.agent-skill-generator.orchestrator validate \
    skill-name/SKILL.md
```

**Checks**:
- ✓ YAML frontmatter valid
- ✓ Required fields present (name, description)
- ✓ File patterns valid (if specified)
- ✓ Mode slug unique in .roomodes

### Customization

Customize generated skills:

1. **Edit SKILL.md**: Add examples, refine guidance
2. **Update References**: Add custom documentation
3. **Modify .roomodes**: Adjust permissions or file patterns
4. **Test Changes**: Verify in Roo Code

### File Restrictions

Skills can specify which files modes can edit via [`file_globs`](../../.roomodes):

```json
{
  "skill-name": {
    "file_globs": ["*.py", "*.md"]
  }
}
```

See [`mode_configurator.py`](../agent-skill-generator/mode_configurator.py) for registration logic.

---

## Related Documentation

- [Shell Commands Overview](./README.md)
- [Usage Examples](./EXAMPLES.md)
- [Python Orchestrator](../agent-skill-generator/README.md)
- [System Guide](../agent-skill-generator/SYSTEM_GUIDE.md)
- [Architecture](../../architecture/agent-skill-generator-architecture.md)
- [Process Flow](../../architecture/agent-skill-generator-process.md)

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [existing examples](./EXAMPLES.md)
3. Run with `--verbose` for detailed logs
4. Validate with [`validate`](../agent-skill-generator/orchestrator.py:245-282) command