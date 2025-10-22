# Agent Skill Generator - Integration Guide

Comprehensive guide explaining how the [`/generate-skill`](./.roo/commands/generate-skill.md) command integrates with the Roo Code ecosystem.

## Overview

### What It Does

The Agent Skill Generator is an automated pipeline that transforms web documentation into production-ready Roo Code skills. It orchestrates multiple AI services to:

- **Extract** documentation knowledge using Firecrawl + OpenAI
- **Research** ecosystem positioning using Claude + Exa MCP
- **Synthesize** structured SKILL.md files with best practices
- **Integrate** automatically into [`.roomodes`](../../.roomodes) configuration

### Why It Exists

Creating high-quality Roo Code skills manually requires:
- Reading extensive documentation
- Understanding ecosystem positioning
- Structuring knowledge for AI consumption
- Following Roo Code conventions and patterns

This system automates the entire workflow, reducing skill creation from hours to minutes while maintaining quality and consistency.

### Key Benefits

- **Speed**: Generate skills in 5-10 minutes vs. hours of manual work
- **Consistency**: Follow Roo Code patterns and conventions automatically
- **Comprehensiveness**: Include documentation, best practices, and ecosystem context
- **Integration**: Automatic `.roomodes` registration with validation

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Shell Command Wrapper                    │
│              scripts/commands/generate-skill.sh             │
│         (Environment validation, argument parsing)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Python Orchestrator                       │
│        scripts/agent-skill-generator/orchestrator.py        │
│         (Coordinates 5-phase pipeline workflow)             │
└────────┬────────────────┬──────────────┬───────────┬────────┘
         │                │              │           │
    Phase 1          Phase 2        Phase 3     Phase 4+5
         │                │              │           │
         ▼                ▼              ▼           ▼
┌────────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐
│ llms_generator │ │ ecosystem_  │ │  skill_  │ │  mode_   │
│      .py       │ │ researcher  │ │ creator  │ │configurar│
│                │ │    .py      │ │   .py    │ │   .py    │
└────────────────┘ └─────────────┘ └──────────┘ └──────────┘
```

### Module Responsibilities

**[`generate-skill.sh`](./generate-skill.sh)**
- Environment variable validation
- Command-line argument parsing
- User-friendly progress reporting
- Error handling and recovery guidance

**[`orchestrator.py`](../agent-skill-generator/orchestrator.py)**
- Coordinates all pipeline phases
- Manages data flow between modules
- Provides CLI interface via Typer
- Handles errors and rollbacks

**[`llms_generator.py`](../agent-skill-generator/llms_generator.py)**
- Maps documentation sites via Firecrawl
- Scrapes pages in parallel batches
- Generates summaries via OpenAI
- Produces llms.txt and llms-full.txt

**[`ecosystem_researcher.py`](../agent-skill-generator/ecosystem_researcher.py)**
- Conducts strategic research via Claude
- Optionally uses Exa MCP for enhanced search
- Identifies positioning and best practices
- Returns structured [`WisdomDocument`](../agent-skill-generator/schemas.py:21-36)

**[`skill_creator.py`](../agent-skill-generator/skill_creator.py)**
- Synthesizes knowledge + wisdom
- Generates YAML frontmatter
- Structures SKILL.md sections
- Creates reference documentation

**[`mode_configurator.py`](../agent-skill-generator/mode_configurator.py)**
- Validates SKILL.md structure
- Checks for duplicate slugs
- Registers in `.roomodes`
- Runs integration validation

**[`config.py`](../agent-skill-generator/config.py)** & **[`schemas.py`](../agent-skill-generator/schemas.py)**
- Environment configuration management
- Pydantic models for type safety
- Data validation and serialization

### Data Flow

```
URL → [Firecrawl] → Scraped Pages → [OpenAI] → KnowledgeBundle
                                                        │
                                                        ▼
                                              [Claude + Exa MCP]
                                                        │
                                                        ▼
                                                 WisdomDocument
                                                        │
                                                        ▼
                                              [Skill Creator]
                                                        │
                                                        ▼
                                                  SkillBundle
                                                        │
                                                        ▼
                                            [Write + Register]
                                                        │
                                                        ▼
                                            skill-name/SKILL.md
                                            + .roomodes entry
```

---

## Installation & Setup

### Prerequisites

- **Python 3.10+** - Runtime environment
- **Bash 4.0+** - Shell script execution
- **API Keys** - Firecrawl, OpenAI, Anthropic

### Step 1: Install Python Dependencies

```bash
cd scripts/agent-skill-generator
pip install -r requirements.txt
```

**Required packages:**
- `typer` - CLI framework
- `rich` - Terminal formatting
- `pydantic-settings` - Configuration management
- `openai` - OpenAI API client
- `anthropic` - Claude API client
- `requests` - HTTP requests
- `tenacity` - Retry logic

### Step 2: Configure API Keys

Create `.env` in project root:

```bash
# Required API Keys
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Optional - Enhanced Research
EXA_API_KEY=your-exa-key-here
```

**Security:** Ensure `.env` is in [`.gitignore`](../../.gitignore)

### Step 3: Validate Installation

```bash
# Test shell script
./scripts/commands/generate-skill.sh --help

# Test Python module
python -m scripts.agent-skill-generator.orchestrator --help

# Verify API keys
python -c "from scripts.agent_skill_generator.config import get_settings; get_settings()"
```

---

## Usage Workflows

### Workflow 1: Slash Command (Recommended)

```bash
/generate-skill https://fastapi.tiangolo.com
```

**What happens:**
1. Roo Code parses the slash command
2. Executes [`/generate-skill.sh`](./generate-skill.sh)
3. Shows progress with rich formatting
4. Registers mode automatically
5. Returns success confirmation

**Use when:** Working within Roo Code environment

### Workflow 2: Shell Script

```bash
./scripts/commands/generate-skill.sh \
    "https://fastapi.tiangolo.com" \
    "fastapi-developer" \
    --max-urls 30 \
    --verbose
```

**What happens:**
1. Validates environment variables
2. Parses arguments and options
3. Executes Python orchestrator
4. Displays phase-by-phase progress
5. Provides next steps guidance

**Use when:** Command-line automation or scripting

### Workflow 3: Python Module Direct

```bash
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://fastapi.tiangolo.com" \
    "fastapi-developer" \
    --output-dir "./custom/path" \
    --max-urls 50
```

**What happens:**
1. Runs orchestrator directly
2. Skips shell wrapper validation
3. Uses Python CLI interface
4. Returns structured results

**Use when:** Integration with other Python tools or debugging

### Workflow 4: Validation Only

```bash
python -m scripts.agent-skill-generator.orchestrator validate \
    fastapi-developer/SKILL.md
```

**What happens:**
1. Loads existing SKILL.md
2. Validates YAML frontmatter
3. Checks `.roomodes` integration
4. Reports validation status

**Use when:** Verifying manually created or edited skills

---

## Integration Points

### 1. `.roomodes` Configuration

**Location:** [`.roomodes`](../../.roomodes) in project root

**Integration:**
```json
{
  "slug": "fastapi-developer",
  "name": "FastAPI Developer",
  "roleDefinition": "You are an expert in...",
  "groups": ["read", "edit"],
  "source": "fastapi-developer/SKILL.md"
}
```

**Validation:**
- Checks for duplicate slugs
- Validates JSON structure
- Ensures SKILL.md exists
- Verifies frontmatter matches

### 2. Skill Directory Structure

**Pattern:** `skill-name/` in project root

**Structure:**
```
fastapi-developer/
├── SKILL.md              # Main skill definition
├── LICENSE.txt           # License information
└── references/           # Supporting docs
    ├── api_docs.md       # Full API reference
    └── doc_index.md      # Quick lookup
```

### 3. MCP Server Integration

**Exa MCP (Optional):**
- Enhanced ecosystem research
- Real-time web search
- Positioning analysis
- Alternative discovery

**Configuration:** Detected automatically if `EXA_API_KEY` is set

**MCP Settings:** [`mcp_settings.json`](../../cc_mcp_config.json)

### 4. Sequential Feynman (Future)

**Workflow:**
```bash
/generate-skill https://example.com skill-name --use-feynman true
```

**Integration:**
- Deep documentation analysis
- Iterative understanding
- Enhanced wisdom generation
- Notebook artifacts

**Status:** Planned for future integration

---

## File Structure Reference

### Generated Skill Directory

```
skill-name/
├── SKILL.md                      # 300-500 lines
│   ├── YAML frontmatter
│   ├── Overview
│   ├── Core Capabilities
│   ├── When to Use
│   ├── Ecosystem & Alternatives
│   ├── Integration Patterns
│   ├── Best Practices
│   └── References
│
├── LICENSE.txt                   # License terms
│
└── references/
    ├── api_documentation.md      # Complete API docs
    └── documentation_index.md    # URL index + titles
```

### Pipeline Artifacts

The orchestrator creates these data structures:

- **[`KnowledgeBundle`](../agent-skill-generator/schemas.py:11-19)** - Scraped documentation
- **[`WisdomDocument`](../agent-skill-generator/schemas.py:21-36)** - Research insights
- **[`SkillBundle`](../agent-skill-generator/schemas.py:67-74)** - Complete skill package
- **[`ValidationReport`](../agent-skill-generator/schemas.py:76-83)** - Integration checks

---

## Extension Points

### Adding Research Sources

**File:** [`ecosystem_researcher.py`](../agent-skill-generator/ecosystem_researcher.py)

```python
def research_ecosystem(self, skill_name: str, context: str) -> WisdomDocument:
    # Add custom research logic here
    custom_insights = self._query_custom_source(skill_name)
    # Merge with existing research
```

### Customizing SKILL.md Templates

**File:** [`skill_creator.py`](../agent-skill-generator/skill_creator.py)

```python
def _generate_custom_section(self, data: Dict) -> str:
    # Add new sections to SKILL.md
    return f"## Custom Section\n\n{data['content']}"
```

### Adding Validation Rules

**File:** [`mode_configurator.py`](../agent-skill-generator/mode_configurator.py)

```python
def _custom_validation(self, skill_path: str) -> bool:
    # Add custom validation logic
    return check_custom_requirement(skill_path)
```

### Processing Hooks

**Extend orchestrator** with custom phases:

```python
# Phase 6: Custom Processing
custom_result = self.custom_processor.process(skill_bundle)
```

---

## Best Practices

### URL Selection

- Use root documentation URLs (e.g., `https://fastapi.tiangolo.com`)
- Avoid versioned URLs unless necessary
- Verify public accessibility
- Check robots.txt compliance

### Processing Limits

- Start with `--max-urls 20` for initial testing
- Increase to 30-50 for comprehensive coverage
- Monitor API rate limits
- Consider documentation site size

### Skill Naming

- Use kebab-case: `fastapi-developer`
- Be descriptive but concise
- Avoid redundant terms
- Match domain/tool name

### Environment Management

- Store API keys in `.env` files
- Never commit secrets to git
- Use different keys for dev/prod
- Rotate keys periodically

### Quality Assurance

1. Review generated SKILL.md
2. Test mode in Roo Code
3. Verify reference accuracy
4. Check integration validation

---

## Troubleshooting

### API Key Errors

```
ValueError: Missing required environment variables
```

**Solution:** Export all required keys or use `.env` file

### Rate Limiting

```
429 Too Many Requests
```

**Solution:** Reduce `--max-urls` or add delays between generations

### Invalid SKILL.md

```
Invalid YAML frontmatter
```

**Solution:** Run validation and check frontmatter structure

### Mode Registration Failed

```
Duplicate slug in .roomodes
```

**Solution:** Choose unique slug or remove existing entry

### Connection Timeouts

**Solution:** Check network, verify URL accessibility, retry with `--verbose`

---

## Quick Reference

**Generate skill:**
```bash
/generate-skill https://docs.example.com skill-name
```

**Validate skill:**
```bash
python -m scripts.agent-skill-generator.orchestrator validate skill-name/SKILL.md
```

**Debug mode:**
```bash
./scripts/commands/generate-skill.sh "https://example.com" skill --verbose
```

**Documentation:**
- [Shell Command](./generate-skill.md)
- [Slash Command](../../.roo/commands/generate-skill.md)
- [Module README](../agent-skill-generator/README.md)
- [Architecture](../../architecture/agent-skill-generator-architecture.md)