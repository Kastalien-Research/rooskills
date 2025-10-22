# Agent Skill Generator System Guide

## Overview

### What It Does

The Agent Skill Generator automatically transforms web documentation into integrated Roo Code skills. It combines AI-powered knowledge extraction with ecosystem research to create production-ready Agent Skills that extend Roo Code's capabilities.

**Core Process:**
1. **Extract** - Scrape documentation using Firecrawl + OpenAI
2. **Research** - Analyze ecosystem with Claude + Exa MCP
3. **Synthesize** - Generate [`SKILL.md`](../../skill-creator/SKILL.md) files
4. **Integrate** - Register in [`.roomodes`](../../.roomodes)

### Why It Exists

**Problem:** Manually creating Agent Skills is time-consuming and requires deep expertise in both the target technology and Roo Code's skill system.

**Solution:** Autonomous skill generation that enables Roo Code to learn new tools by reading their documentation, just like developers do.

### Key Benefits

- **Automated Knowledge Extraction** - Scrape and structure docs in minutes
- **Ecosystem Understanding** - AI research reveals positioning, alternatives, best practices
- **Seamless Integration** - Auto-configure modes with proper permissions
- **Reproducible** - Same URL always generates consistent skills

---

## Quick Start

```bash
# 1. Install dependencies
cd scripts/agent-skill-generator
pip install -r requirements.txt

# 2. Set environment variables
export FIRECRAWL_API_KEY="fc-..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Generate your first skill
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://fastapi.tiangolo.com" \
    "fastapi-developer"
```

**Using Slash Command:**
```bash
/generate-skill https://fastapi.tiangolo.com fastapi-developer
```

---

## System Architecture

### High-Level Flow

```
Documentation URL
    ↓
[Firecrawl + OpenAI] → Knowledge (llms.txt)
    ↓
[Claude + Exa MCP] → Wisdom (ecosystem context)
    ↓
[Skill Creator] → SKILL.md + references/
    ↓
[Mode Configurator] → .roomodes integration
```

### Architecture Documentation

For detailed architecture, see:
- [System Architecture](../../architecture/agent-skill-generator-architecture.md) - Components, data flow, module boundaries
- [Process Documentation](../../architecture/agent-skill-generator-process.md) - Detailed workflow phases
- [Slash Command](../../.roo/commands/generate-skill.md) - CLI interface

### Component Overview

| Module | Purpose | External Services |
|--------|---------|------------------|
| [`orchestrator.py`](orchestrator.py) | CLI & workflow coordination | None |
| [`llms_generator.py`](llms_generator.py) | Knowledge extraction | Firecrawl, OpenAI |
| [`ecosystem_researcher.py`](ecosystem_researcher.py) | Ecosystem research | Claude, Exa MCP |
| [`skill_creator.py`](skill_creator.py) | SKILL.md synthesis | None |
| [`mode_configurator.py`](mode_configurator.py) | .roomodes integration | None |
| [`config.py`](config.py) | Environment management | None |
| [`schemas.py`](schemas.py) | Data validation | None |

---

## Components Deep Dive

### Configuration (`config.py`)

**Responsibilities:**
- Load environment variables
- Validate API keys
- Manage default settings

**Key Settings:**
```python
FIRECRAWL_API_KEY    # Required: Firecrawl access
OPENAI_API_KEY       # Required: Summarization
ANTHROPIC_API_KEY    # Required: Research
EXA_API_KEY          # Optional: Enhanced research
MAX_URLS = 20        # Default scraping limit
```

### LLMS Generator (`llms_generator.py`)

**Process:**
1. **Map** - Firecrawl `/map` discovers all URLs
2. **Scrape** - Firecrawl `/scrape` extracts markdown
3. **Summarize** - OpenAI generates titles (3-4 words) + descriptions (9-10 words)
4. **Output** - Creates `llms.txt` (index) + `llms-full.txt` (complete content)

**Output Format:**
```markdown
# https://docs.example.com llms.txt

- [Getting Started](url): Quick setup guide for installation
- [API Reference](url): Complete API with endpoints and auth
```

### Ecosystem Researcher (`ecosystem_researcher.py`)

**Sequential Feynman Process:**
1. **Discovery** - "What is [tool]? Who uses it?"
2. **Mapping** - "Integrations, alternatives, use cases"
3. **Practices** - "Patterns, anti-patterns, security"

**Uses:**
- Claude Agent SDK for orchestration
- Exa MCP for intelligent web search
- Optional Sequential Feynman for deep analysis

**Output:** [`WisdomDocument`](schemas.py) with ecosystem insights

### Skill Creator (`skill_creator.py`)

**Synthesis:**
1. Extracts capabilities from `llms.txt`
2. Combines with ecosystem wisdom
3. Generates YAML frontmatter
4. Structures markdown content
5. Extracts large docs to `references/`

**SKILL.md Template:**
```markdown
---
name: skill-name
description: When to use this skill...
license: LICENSE.txt
---

# Skill Name

## Core Capabilities
## When to Use This Skill
## Ecosystem & Alternatives
## Integration Patterns
## Best Practices
## References
```

### Mode Configurator (`mode_configurator.py`)

**Operations:**
1. Validates SKILL.md structure
2. Checks for duplicate slugs
3. Adds mode entry to `.roomodes`
4. Runs integration checks

**Validation Criteria:**
- SKILL.md exists at path
- Valid YAML frontmatter
- No slug conflicts
- File < 500 lines
- Groups alignment

---

## Usage Examples

### Example 1: Basic Generation

```bash
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://supabase.com/docs" \
    "supabase-admin"
```

**Output:**
```
supabase-admin/
├── SKILL.md
├── LICENSE.txt
└── references/
    ├── api_documentation.md
    └── documentation_index.md
```

### Example 2: Custom Configuration

```bash
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://stripe.com/docs" \
    "stripe-integration" \
    --max-urls 50 \
    --output-dir "./custom-skills/stripe" \
    --verbose
```

### Example 3: Validation Only

```bash
python -m scripts.agent-skill-generator.orchestrator validate \
    fastapi-developer/SKILL.md
```

---

## Workflow Phases

### Phase 1: Environment Validation

**Checks:**
- API keys present
- Dependencies installed
- URL format valid
- No duplicate skill names

### Phase 2: Knowledge Extraction

**Actions:**
1. Firecrawl maps website → URL list
2. Scrapes content in batches → markdown
3. OpenAI generates summaries → titles/descriptions
4. Writes `llms.txt` + `llms-full.txt`

**Time:** 2-5 minutes (depends on site size)

### Phase 3: Ecosystem Research

**Actions:**
1. Claude Agent SDK initializes with Exa MCP
2. Sequential searches for discovery, mapping, practices
3. Synthesizes findings into [`WisdomDocument`](schemas.py)

**Time:** 3-7 minutes (add 20-40 min if using Sequential Feynman)

### Phase 4: Skill Synthesis

**Actions:**
1. Extract capabilities from knowledge
2. Enrich with ecosystem wisdom
3. Generate YAML frontmatter
4. Create directory structure
5. Write reference files

**Time:** 1-2 minutes

### Phase 5: Mode Configuration

**Actions:**
1. Validate SKILL.md format
2. Check `.roomodes` for conflicts
3. Add mode entry with skill_ref
4. Run integration checks

**Time:** < 1 minute

### Phase 6: Validation

**Checks:**
- SKILL.md format valid
- Mode registered correctly
- Permissions aligned
- File sizes under limits

---

## Configuration Reference

### Required Environment Variables

```bash
# Firecrawl API (documentation scraping)
FIRECRAWL_API_KEY=fc-your-key-here

# OpenAI API (summarization)
OPENAI_API_KEY=sk-your-key-here

# Anthropic API (ecosystem research)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Optional Settings

```bash
# Processing Limits
MAX_URLS=20              # Maximum pages to scrape
BATCH_SIZE=10            # Concurrent processing batch size
MAX_WORKERS=5            # Thread pool size

# Rate Limiting (requests per minute)
FIRECRAWL_RATE_LIMIT=10
OPENAI_RATE_LIMIT=60

# Retry Configuration
API_RETRY_ATTEMPTS=3
API_RETRY_BACKOFF=2.0    # Exponential backoff multiplier

# Enhanced Research (optional)
EXA_API_KEY=your-exa-key # For Exa MCP integration
```

### Configuration File (`.env`)

```bash
# Create .env file in project root
cat > .env << 'EOF'
FIRECRAWL_API_KEY=fc-xxx
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
MAX_URLS=30
EOF
```

---

## Troubleshooting

### Missing API Keys

**Error:**
```
ValueError: Missing required environment variables: FIRECRAWL_API_KEY
```

**Solution:**
```bash
# Verify variables are set
echo $FIRECRAWL_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Set if missing
export FIRECRAWL_API_KEY="fc-..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Rate Limiting

**Error:**
```
429 Too Many Requests - Rate limit exceeded
```

**Solution:**
```bash
# Reduce batch size and workers
export BATCH_SIZE=5
export MAX_WORKERS=2

# Or reduce max URLs
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://example.com" \
    "skill-name" \
    --max-urls 10
```

### Invalid URLs

**Error:**
```
❌ Firecrawl failed to map URL: 404 Not Found
```

**Solution:**
- Verify URL is accessible in browser
- Check for redirects (use final URL)
- Try with/without trailing slash
- Ensure documentation is publicly accessible
- Check `robots.txt` for scraping restrictions

### Malformed Output

**Error:**
```
Invalid or missing YAML frontmatter in SKILL.md
```

**Solution:**
```bash
# Enable verbose logging to debug
python -m scripts.agent-skill-generator.orchestrator generate \
    "https://example.com" \
    "skill-name" \
    --verbose

# Check API responses in logs
# Validate SKILL.md manually
```

### Mode Registration Failure

**Error:**
```
⚠️ Mode registration failed - manual registration required
```

**Solution:**
1. Check SKILL.md has valid YAML frontmatter
2. Verify no duplicate slug in `.roomodes`
3. Manually add mode entry:

```json
{
  "slug": "skill-name",
  "name": "🔧 Skill Name",
  "roleDefinition": "You are an expert in...",
  "skill_ref": {
    "path": "skill-name/SKILL.md",
    "merge_strategy": "override"
  },
  "groups": ["read", "edit"],
  "source": "project"
}
```

---

## Extension Guide

### Adding New Research Sources

Extend [`EcosystemResearcher`](ecosystem_researcher.py) to integrate additional MCP servers:

```python
class EcosystemResearcher:
    def _research_with_custom_mcp(self, topic: str):
        # Add custom MCP server integration
        custom_results = await self.custom_mcp.search(topic)
        return self._synthesize(custom_results)
```

### Custom Skill Templates

Modify [`SkillCreator`](skill_creator.py) templates:

```python
class SkillCreator:
    def _custom_section_template(self, data):
        # Add domain-specific sections
        return f"## Custom Section\n{data}"
```

### Alternative Scrapers

Replace Firecrawl with custom scraping:

```python
class CustomLLMSGenerator:
    def _scrape_with_playwright(self, urls):
        # Implement custom scraping logic
        pass
```

---

## Best Practices

### API Key Security

✅ **DO:**
- Use environment variables
- Store in `.env` files (add to `.gitignore`)
- Rotate keys regularly
- Use different keys for dev/prod

❌ **DON'T:**
- Hardcode in source files
- Commit to version control
- Share in public channels
- Reuse across projects

### Resource Management

- **Monitor API usage** - Check Firecrawl/OpenAI quotas
- **Set appropriate limits** - Use `MAX_URLS` to control costs
- **Batch operations** - Process multiple skills off-peak
- **Cache results** - Save `llms.txt` for re-generation

### Quality Assurance

1. **Review generated skills** - Verify accuracy before use
2. **Test mode integration** - Try `/mode skill-name` to confirm
3. **Validate permissions** - Ensure groups match skill needs
4. **Check references** - Verify links work and docs are complete

### Maintenance

- **Update dependencies** - Run `pip install -U -r requirements.txt`
- **Monitor API changes** - Watch for Firecrawl/OpenAI updates
- **Archive old skills** - Keep generated skills in version control
- **Document customizations** - Note any manual edits to SKILL.md

---

## References

### Documentation

- [Process Documentation](../../architecture/agent-skill-generator-process.md) - Detailed workflow
- [Architecture Documentation](../../architecture/agent-skill-generator-architecture.md) - System design
- [Slash Command Reference](../../.roo/commands/generate-skill.md) - CLI usage
- [Skill Creator Guidelines](../../skill-creator/SKILL.md) - Skill format
- [MCP Builder Example](../../mcp-builder/SKILL.md) - Advanced integration

### API Documentation

- [Firecrawl API](https://firecrawl.dev) - Web scraping
- [OpenAI API](https://platform.openai.com/docs) - Summarization
- [Claude API](https://docs.anthropic.com) - Research
- [Exa MCP](https://docs.exa.ai) - Enhanced search

### Related Tools

- [`create-llmstxt-py`](../../create-llmstxt-py) - Standalone llms.txt generator
- [`skill-creator`](../../skill-creator) - Manual skill creation tools
- [`mcp-builder`](../../mcp-builder) - MCP server development

---

## Summary

The Agent Skill Generator automates the creation of high-quality Roo Code skills from web documentation. It orchestrates multiple AI services to extract knowledge, research ecosystems, and synthesize comprehensive SKILL.md files with proper mode integration.

**Key Takeaways:**
- Requires Firecrawl, OpenAI, and Anthropic API keys
- Generates skills in 5-15 minutes (add 20-40 min for deep analysis)
- Creates SKILL.md + references + .roomodes integration
- Extensible architecture for custom research and templates
- Production-ready output with validation and error handling

**Next Steps:**
1. Set up environment variables
2. Generate your first skill
3. Review and test the generated mode
4. Extend with custom research sources as needed