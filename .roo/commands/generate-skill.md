---
description: Generate Agent Skills from web documentation with automated knowledge extraction and ecosystem research
---
**Execution Mode**: Auto-Coder

When this command is invoked, you must:
1. Switch to Auto-Coder mode (if not already)
2. Execute the shell script: `./scripts/commands/generate-skill.sh "$@"`
3. Monitor the output and report progress through all 5 phases
4. Return to the original mode after completion


# /generate-skill

Automatically create integrated Roo Code skills from web documentation using AI-powered extraction, research, and synthesis.

## Usage

```
/generate-skill $URL [$SKILL_NAME] [--max-urls $MAX_URLS] [--use-feynman $USE_FEYNMAN]
```

### Arguments

- **`$URL`** (required) - Documentation URL to process (e.g., `https://fastapi.tiangolo.com`)
- **`$SKILL_NAME`** (optional) - Skill identifier in kebab-case (auto-generated from URL if not provided)
- **`$MAX_URLS`** (optional) - Maximum URLs to scrape (default: `20`)
- **`$USE_FEYNMAN`** (optional) - Use Sequential Feynman for deep understanding (default: `true`)

### Quick Examples

```bash
# Basic usage - generate skill from FastAPI docs
/generate-skill https://fastapi.tiangolo.com

# Custom skill name
/generate-skill https://supabase.com supabase-expert

# Limit URLs and skip deep analysis
/generate-skill https://stripe.com/docs stripe-integration --max-urls 30 --use-feynman false

# Deep dive with Sequential Feynman
/generate-skill https://langchain.readthedocs.io langchain-agent --max-urls 50 --use-feynman true
```

---

## Prerequisites Check

Before executing, verify these environment variables are set:

```bash
# Required API Keys
echo "Checking environment..."
[ -z "$FIRECRAWL_API_KEY" ] && echo "❌ Missing FIRECRAWL_API_KEY" || echo "✅ Firecrawl configured"
[ -z "$OPENAI_API_KEY" ] && echo "❌ Missing OPENAI_API_KEY" || echo "✅ OpenAI configured"
[ -z "$ANTHROPIC_API_KEY" ] && echo "❌ Missing ANTHROPIC_API_KEY" || echo "✅ Anthropic configured"

# Optional - Enhanced research
[ -z "$EXA_API_KEY" ] && echo "⚠️  EXA_API_KEY not set (ecosystem research will be limited)" || echo "✅ Exa MCP configured"
```

If any required keys are missing, stop execution and prompt user to configure them.

---

## Execution Workflow

### Variables Setup

```bash
# Extract and normalize inputs
URL="$1"
SKILL_NAME="${2:-$(echo "$URL" | sed 's|https\?://||' | sed 's|/.*||' | tr '.' '-' | tr '[:upper:]' '[:lower:]')}"
MAX_URLS="${3:-20}"
USE_FEYNMAN="${4:-true}"

# Define paths
SKILL_DIR="./${SKILL_NAME}"
TEMP_DIR=".skill-gen-temp/${SKILL_NAME}"
LOG_FILE="${TEMP_DIR}/generation.log"

echo "🎯 Generating skill: $SKILL_NAME"
echo "📚 Source: $URL"
echo "🔢 Max URLs: $MAX_URLS"
echo "🧠 Use Feynman: $USE_FEYNMAN"
```

### Phase 1: Environment Validation

```bash
echo "
═══════════════════════════════════════
Phase 1: Environment Validation
═══════════════════════════════════════
"

# Create working directories
mkdir -p "$TEMP_DIR"
mkdir -p "$SKILL_DIR/references"

# Validate URL format
if ! echo "$URL" | grep -qE '^https?://'; then
  echo "❌ Invalid URL format: $URL"
  echo "   Expected: https://example.com or http://example.com"
  exit 1
fi

# Check for existing skill
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  echo "⚠️  Skill already exists at $SKILL_DIR/SKILL.md"
  read -p "   Overwrite? (y/N): " confirm
  [[ ! "$confirm" =~ ^[Yy]$ ]] && exit 0
fi

echo "✅ Environment validated"
```

### Phase 2: Knowledge Extraction

**Objective:** Generate [`llms.txt`](https://llmstxt.org) from documentation using Firecrawl + OpenAI

```bash
echo "
═══════════════════════════════════════
Phase 2: Knowledge Extraction
═══════════════════════════════════════
"

echo "📡 Mapping documentation site..."
echo "   URL: $URL"
echo "   Max pages: $MAX_URLS"

# Execute llms.txt generation
python -m scripts.agent-skill-generator.llms_generator \
  --url "$URL" \
  --max-urls "$MAX_URLS" \
  --output "$TEMP_DIR/knowledge" \
  2>&1 | tee -a "$LOG_FILE"

if [ ! -f "$TEMP_DIR/knowledge/llms.txt" ]; then
  echo "❌ Knowledge extraction failed. Check $LOG_FILE"
  exit 1
fi

echo "✅ Knowledge extracted:"
echo "   - llms.txt: $(wc -l < "$TEMP_DIR/knowledge/llms.txt") lines"
echo "   - llms-full.txt: $(wc -l < "$TEMP_DIR/knowledge/llms-full.txt") lines"
```

**Outputs:**
- `llms.txt` - Concise documentation summary (< 50KB)
- `llms-full.txt` - Complete documentation content
- `documentation_index.md` - URL mapping and titles

### Phase 3: Ecosystem Research

**Objective:** Understand positioning, alternatives, and best practices using Claude + Exa MCP

```bash
echo "
═══════════════════════════════════════
Phase 3: Ecosystem Research
═══════════════════════════════════════
"

if [ "$USE_FEYNMAN" = "true" ]; then
  echo "🧠 Deep analysis with Sequential Feynman..."
  
  # Option 1: Use Sequential Feynman command
  /sequential-feynman "$SKILL_NAME from $URL" \
    --notebook-path "$TEMP_DIR/feynman-notebook.ipynb" \
    2>&1 | tee -a "$LOG_FILE"
  
  WISDOM_INPUT="$TEMP_DIR/feynman-notebook.ipynb"
else
  echo "🔍 Standard ecosystem research..."
  WISDOM_INPUT="$TEMP_DIR/knowledge/llms.txt"
fi

# Run ecosystem researcher
python -m scripts.agent-skill-generator.ecosystem_researcher \
  --knowledge "$TEMP_DIR/knowledge/llms.txt" \
  --context "$WISDOM_INPUT" \
  --output "$TEMP_DIR/wisdom.json" \
  2>&1 | tee -a "$LOG_FILE"

if [ ! -f "$TEMP_DIR/wisdom.json" ]; then
  echo "❌ Ecosystem research failed. Check $LOG_FILE"
  exit 1
fi

echo "✅ Ecosystem research complete"
```

**Research Questions:**
- What is this tool/framework?
- Who uses it and why?
- What are the alternatives?
- What are common pitfalls?
- What are best practices?
- How does it integrate with other tools?

### Phase 4: Skill Synthesis

**Objective:** Combine knowledge and wisdom into structured [`SKILL.md`](../../../template-skill/SKILL.md)

```bash
echo "
═══════════════════════════════════════
Phase 4: Skill Synthesis
═══════════════════════════════════════
"

echo "🔨 Synthesizing SKILL.md..."

# Generate skill file
python -m scripts.agent-skill-generator.skill_creator \
  --knowledge "$TEMP_DIR/knowledge" \
  --wisdom "$TEMP_DIR/wisdom.json" \
  --skill-name "$SKILL_NAME" \
  --output "$SKILL_DIR" \
  2>&1 | tee -a "$LOG_FILE"

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "❌ Skill synthesis failed. Check $LOG_FILE"
  exit 1
fi

echo "✅ SKILL.md created:"
echo "   - Path: $SKILL_DIR/SKILL.md"
echo "   - Size: $(wc -l < "$SKILL_DIR/SKILL.md") lines"
echo "   - References: $(ls -1 "$SKILL_DIR/references" | wc -l) files"
```

**SKILL.md Structure:**
```markdown
---
name: skill-name
description: When to use this skill
license: Complete terms in LICENSE.txt
---

# Skill Title

## Core Capabilities
## When to Use This Skill
## Ecosystem & Alternatives
## Integration Patterns
## Best Practices
## References
```

### Phase 5: Mode Configuration

**Objective:** Register skill in [`.roomodes`](../../../.roomodes) configuration

```bash
echo "
═══════════════════════════════════════
Phase 5: Mode Configuration
═══════════════════════════════════════
"

echo "📝 Registering mode in .roomodes..."

# Register mode
python -m scripts.agent-skill-generator.mode_configurator \
  --skill-path "$SKILL_DIR/SKILL.md" \
  --roomodes-path ".roomodes" \
  2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
  echo "⚠️  Mode registration failed - manual registration required"
  echo "   Add this to .roomodes:"
  echo ""
  cat "$TEMP_DIR/mode-entry.json" 2>/dev/null || echo "   (See $SKILL_DIR/SKILL.md for details)"
  echo ""
fi

echo "✅ Mode configuration updated"
```

**Validation Checks:**
- YAML frontmatter present and valid
- Required fields: `name`, `description`
- No duplicate slugs in `.roomodes`
- Skill file under 500 lines
- Valid markdown structure

### Phase 6: Validation and Output

```bash
echo "
═══════════════════════════════════════
Phase 6: Validation & Summary
═══════════════════════════════════════
"

# Run validation
python -m scripts.agent-skill-generator.orchestrator validate \
  "$SKILL_DIR/SKILL.md" \
  2>&1 | tee -a "$LOG_FILE"

# Generate summary
cat > "$SKILL_DIR/README.md" << EOF
# ${SKILL_NAME}

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Source:** $URL
**Documentation Pages:** $(grep -c "^# " "$TEMP_DIR/knowledge/llms.txt")

## Quick Start

See [SKILL.md](./SKILL.md) for complete documentation.

## Generation Log

Full generation log: [\`generation.log\`]($LOG_FILE)
EOF

echo "
✅ SKILL GENERATION COMPLETE
══════════════════════════════════════════

📁 Skill Directory: $SKILL_DIR
📄 Main File: $SKILL_DIR/SKILL.md
📚 References: $SKILL_DIR/references/
🔧 Mode Slug: $SKILL_NAME

Next Steps:
1. Review $SKILL_DIR/SKILL.md
2. Test the mode: /mode $SKILL_NAME
3. Refine if needed
4. Commit to repository

Generation artifacts preserved in: $TEMP_DIR
"

# Archive logs
cp "$LOG_FILE" "$SKILL_DIR/generation.log"

# Optional cleanup
read -p "Remove temporary files? (y/N): " cleanup
if [[ "$cleanup" =~ ^[Yy]$ ]]; then
  rm -rf ".skill-gen-temp/${SKILL_NAME}"
  echo "🧹 Temporary files cleaned"
fi
```

---

## Expected Output

After successful execution, you'll have:

```
skill-name/
├── SKILL.md                      # Main skill definition
├── LICENSE.txt                   # License file
├── README.md                     # Generation summary
├── generation.log                # Complete generation log
└── references/
    ├── api_documentation.md      # Full documentation
    └── documentation_index.md    # URL index
```

### Integration Verification

```bash
# Verify mode is registered
grep "$SKILL_NAME" .roomodes

# Test the mode
/mode $SKILL_NAME
# Try a simple task to verify skill works
```

---

## Troubleshooting

### Missing API Keys

**Symptom:**
```
ValueError: Missing required environment variables: FIRECRAWL_API_KEY
```

**Solution:**
```bash
# Set in .env file
echo "FIRECRAWL_API_KEY=fc-xxx" >> .env
echo "OPENAI_API_KEY=sk-xxx" >> .env
echo "ANTHROPIC_API_KEY=sk-ant-xxx" >> .env

# Or export directly
export FIRECRAWL_API_KEY="fc-xxx"
export OPENAI_API_KEY="sk-xxx"
export ANTHROPIC_API_KEY="sk-ant-xxx"
```

### Invalid URL or 404 Errors

**Symptom:**
```
❌ Firecrawl failed to map URL: 404 Not Found
```

**Solution:**
- Verify URL is accessible in browser
- Check for redirects (use final URL)
- Try with/without trailing slash
- Ensure documentation is publicly accessible

### Rate Limiting

**Symptom:**
```
429 Too Many Requests - Rate limit exceeded
```

**Solution:**
```bash
# Reduce batch size
export BATCH_SIZE=5
export MAX_WORKERS=2

# Or reduce max URLs
/generate-skill https://example.com my-skill --max-urls 10
```

### Incomplete Knowledge Extraction

**Symptom:**
```
⚠️  Only 5 pages scraped, expected 20+
```

**Solution:**
- Check Firecrawl API quota
- Increase timeout values
- Verify site allows scraping (check robots.txt)
- Try smaller `--max-urls` value first

### Mode Registration Failed

**Symptom:**
```
⚠️  Mode registration failed - manual registration required
```

**Solution:**
1. Check [`SKILL.md`](../../../template-skill/SKILL.md) has valid YAML frontmatter
2. Verify no duplicate slug in [`.roomodes`](../../../.roomodes)
3. Manually add mode entry:

```json
{
  "slug": "skill-name",
  "name": "Skill Display Name",
  "roleDefinition": "You are an expert in...",
  "groups": ["skills"],
  "source": "skill-name/SKILL.md"
}
```

### Sequential Feynman Timeout

**Symptom:**
```
⏱️  Sequential Feynman taking too long...
```

**Solution:**
```bash
# Skip deep analysis for faster generation
/generate-skill https://example.com my-skill --use-feynman false

# Or run Feynman separately after generation
/sequential-feynman "skill-name from example.com"
```

---

## Advanced Usage

### Custom Output Directory

```bash
# Generate in specific location
SKILL_DIR="./custom/path/skill-name"
/generate-skill https://example.com skill-name
```

### Batch Generation

```bash
# Generate multiple skills
for url in $(cat urls.txt); do
  skill=$(echo "$url" | sed 's|https://||' | cut -d'/' -f1 | tr '.' '-')
  /generate-skill "$url" "$skill" --max-urls 15
  sleep 60  # Rate limiting
done
```

### Re-generation with Updates

```bash
# Update existing skill with new documentation
/generate-skill https://example.com existing-skill --max-urls 30

# System will prompt to overwrite
```

---

## Meta-Learning

Each skill generation creates detailed logs for continuous improvement:

**Logs Location:** `.skill-gen-temp/skill-name/generation.log`

**Archive Pattern:**
```bash
logs/skill-generations/
└── YYYY-MM-DD_HH-MM-SS/
    ├── skill-name/
    ├── generation.log
    └── metadata.json
```

**Analytics:**
- Success rate per documentation source
- Average pages per skill
- Time to generate
- Validation pass/fail patterns

---

## Success Criteria

Skill generation succeeds when:

- [x] All prerequisite API keys validated
- [x] Documentation mapped and scraped successfully
- [x] Knowledge extracted into llms.txt
- [x] Ecosystem research completed (with or without Feynman)
- [x] SKILL.md generated with valid structure
- [x] Mode registered in .roomodes
- [x] Validation passes all checks
- [x] References created in references/
- [x] README.md generated
- [x] No critical errors in generation.log

---

## Related Commands

- [`/sequential-feynman`](./sequential-feynman.md) - Deep learning validation
- [`/refactoring-game`](./refactoring-game.md) - Iterative code improvement

---

## Quick Reference

**Command:** `/generate-skill $URL [$SKILL_NAME] [options]`

**Time Investment:** 5-15 minutes (30-60 min with Sequential Feynman)

**Outputs:**
- `SKILL.md` - Production-ready skill definition
- `references/` - Full documentation reference
- `generation.log` - Audit trail

**Best For:**
- Adding new framework/library skills
- Documenting third-party APIs
- Creating domain expertise modes
- Building specialized development skills
---
description: Transform web documentation into integrated Roo Code skills with automated knowledge extraction, ecosystem research, and mode registration
---

# /generate-skill - Automated Skill Generation

Transform any web documentation into a complete, production-ready Roo Code skill with structured guidance, references, and automatic mode registration.

**Shell Script**: [`scripts/commands/generate-skill.sh`](../../scripts/commands/generate-skill.sh)

---

## Usage

```bash
/generate-skill <URL> [SKILL_NAME] [OPTIONS]
```

### Quick Examples

```bash
# Auto-detect skill name from URL
/generate-skill "https://fastapi.tiangolo.com"

# Specify custom skill name
/generate-skill "https://fastapi.tiangolo.com" "fastapi-developer"

# With custom options
/generate-skill "https://fastapi.tiangolo.com" "fastapi-dev" --max-urls 30 --verbose

# With custom output directory
/generate-skill "https://fastapi.tiangolo.com" --output-dir "./skills/backend/fastapi"
```

---

## Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `URL` | Yes | Documentation URL to process | `https://fastapi.tiangolo.com` |
| `SKILL_NAME` | No | Skill identifier in kebab-case (auto-generated if omitted) | `fastapi-developer` |

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--max-urls N` | Integer | 20 | Maximum number of URLs to process |
| `--use-feynman` | Boolean | true | Enable Feynman technique for documentation |
| `--output-dir DIR` | Path | `SKILL_NAME` | Output directory for generated files |
| `--verbose` | Flag | false | Enable verbose logging for debugging |
| `--help` | Flag | - | Show help message and exit |

---

## Prerequisites

### Required Environment Variables

The command requires three API keys to be set in your environment:

```bash
export FIRECRAWL_API_KEY="fc-your-key-here"
export OPENAI_API_KEY="sk-your-key-here"  
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Where to Get Keys**:
- **Firecrawl**: https://firecrawl.dev (web scraping and content extraction)
- **OpenAI**: https://platform.openai.com (content summarization)
- **Anthropic**: https://console.anthropic.com (research and skill synthesis)

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

**Security**: Add `.env` to `.gitignore` to prevent accidental commits.

### System Requirements

- **Bash**: 4.0 or higher
- **Python**: 3.10 or higher
- **Dependencies**: Auto-installed from requirements.txt

### Verification

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

## Workflow Phases

The command orchestrates a 5-phase pipeline coordinated by [`orchestrator.py`](../../scripts/agent-skill-generator/orchestrator.py).

### Phase 1: Knowledge Extraction

**Module**: [`llms_generator.py`](../../scripts/agent-skill-generator/llms_generator.py)

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
✓ Mapped 47 URLs
✓ Processed 23 pages
✓ Generated summaries
```

### Phase 2: Ecosystem Research

**Module**: [`ecosystem_researcher.py`](../../scripts/agent-skill-generator/ecosystem_researcher.py)

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
✓ Analyzed positioning
✓ Identified alternatives
✓ Extracted best practices
```

### Phase 3: Skill Synthesis

**Module**: [`skill_creator.py`](../../scripts/agent-skill-generator/skill_creator.py)

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
✓ Synthesized skill structure
✓ Generated YAML frontmatter
✓ Created reference files
```

### Phase 4: File Writing

**Module**: [`orchestrator.py:_write_skill_files()`](../../scripts/agent-skill-generator/orchestrator.py)

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
✓ Created directory structure
✓ Wrote SKILL.md (12,456 bytes)
✓ Wrote 2 reference files
✓ Generated LICENSE.txt
```

### Phase 5: Mode Registration

**Module**: [`mode_configurator.py`](../../scripts/agent-skill-generator/mode_configurator.py)

**Process**:
1. Validates SKILL.md structure and frontmatter
2. Checks for duplicate mode slugs in `.roomodes`
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

## Common Use Cases

### API Framework Documentation

Generate skills for web frameworks:

```bash
# FastAPI
/generate-skill "https://fastapi.tiangolo.com"

# NestJS  
/generate-skill "https://docs.nestjs.com" "nestjs-developer"

# Django
/generate-skill "https://docs.djangoproject.com" "django-expert" --max-urls 40
```

### Database Documentation

Create database administration skills:

```bash
# PostgreSQL
/generate-skill "https://www.postgresql.org/docs/current" "postgresql-admin" --max-urls 60

# MongoDB
/generate-skill "https://docs.mongodb.com"
```

### Cloud Platform Documentation

Build cloud service skills:

```bash
# Google Cloud Firestore
/generate-skill "https://cloud.google.com/firestore/docs" "firestore-developer" --output-dir "./cloud-skills/gcp"

# AWS Lambda
/generate-skill "https://docs.aws.amazon.com/lambda" "aws-lambda-expert"
```

### Testing Framework Documentation

Generate testing tool skills:

```bash
# pytest
/generate-skill "https://docs.pytest.org" "pytest-expert"

# Jest
/generate-skill "https://jestjs.io/docs" "jest-testing"
```

### Batch Processing Multiple Skills

```bash
#!/bin/bash
# batch-generate.sh - Generate multiple skills in sequence

URLS=(
    "https://fastapi.tiangolo.com:fastapi-dev"
    "https://flask.palletsprojects.com:flask-dev"
    "https://docs.djangoproject.com:django-dev"
)

for entry in "${URLS[@]}"; do
    IFS=':' read -r url name <<< "$entry"
    /generate-skill "$url" "$name"
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
/generate-skill "https://example.com" --max-urls 10

# Process in batches with delays
/generate-skill "https://site1.com" && sleep 60
/generate-skill "https://site2.com"
```

### Invalid SKILL.md Generated

**Error**:
```
Invalid or missing YAML frontmatter in SKILL.md
```

**Solution**: Validate and regenerate:
```bash
# Check validation
python -m scripts.agent-skill-generator.orchestrator validate skill-name/SKILL.md

# Regenerate with verbose logging
/generate-skill "https://example.com" "skill-name" --verbose
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

For detailed troubleshooting, enable verbose mode:

```bash
/generate-skill "https://example.com" --verbose
```

This will show:
- Detailed API calls and responses
- File operations and validations
- Internal processing steps
- Error stack traces

---

## Output Artifacts

After successful execution, you'll have:

### 1. Skill Directory

```
skill-name/
├── SKILL.md                      # Main skill definition
├── LICENSE.txt                   # MIT license
└── references/                   # Supporting documentation
    ├── api_documentation.md      # Full API reference
    ├── documentation_index.md    # Quick lookup index
    └── best_practices.md         # Common patterns and anti-patterns
```

### 2. Mode Registration

The skill is automatically registered in `.roomodes`:

```json
{
  "slug": "skill-name",
  "name": "Skill Display Name",
  "icon": "📘",
  "description": "Generated description",
  "roleDefinition": "You are an expert in...",
  "customInstructions": "Detailed guidance...",
  "systemPromptFile": "skill-name/SKILL.md"
}
```

### 3. Validation Report

A validation report confirms:
- ✓ YAML frontmatter is valid
- ✓ All required fields are present
- ✓ File patterns are correctly formatted
- ✓ Mode slug is unique
- ✓ Integration passes all checks

---

## Best Practices

### URL Selection

Choose documentation URLs that:
- Have comprehensive, well-organized content
- Include API references and examples
- Are actively maintained
- Cover common use cases

**Good Examples**:
- `https://fastapi.tiangolo.com` (complete framework docs)
- `https://docs.pytest.org` (testing framework)
- `https://www.postgresql.org/docs` (database docs)

**Avoid**:
- Blog posts or tutorials (not comprehensive)
- Outdated documentation
- Sites with heavy JavaScript (hard to scrape)

### Processing Limits

**Default (20 URLs)**: Good for most documentation sites
**Small Sites (5-10 URLs)**: Quick skills for focused tools
**Large Sites (30-50 URLs)**: Comprehensive frameworks requiring detailed coverage

**Warning**: Processing >50 URLs may hit rate limits or timeout

### Customization

After generation, you can:
1. Edit `SKILL.md` to refine guidance
2. Add more reference files
3. Update YAML frontmatter
4. Modify custom instructions

**Tip**: Run validation after edits:
```bash
python -m scripts.agent-skill-generator.orchestrator validate skill-name/SKILL.md
```

---

## Integration with Roo Code

### Using Generated Skills

Once generated and registered, use the skill in Roo Code:

1. **Switch to Mode**: `/mode skill-name`
2. **View Capabilities**: Check the SKILL.md for available commands
3. **Access References**: Reference files are auto-loaded as context

### Skill Structure

Each generated skill follows SPARC principles:

- **S**pecification: Clear role definition and capabilities
- **P**seudocode: Step-by-step workflow guidance
- **A**rchitecture: Modular structure with references
- **R**efinement: Iterative improvement through validation
- **C**ompletion: Production-ready with no hardcoded secrets

### File Restrictions

Generated skills respect mode-specific file restrictions:
- Documentation skills: Can edit `.md` files only
- Developer skills: Can edit relevant code files
- Admin skills: Can edit configuration files

Restrictions are defined in the YAML frontmatter's `allowedFilePatterns`.

---

## Related Documentation

- **Implementation Guide**: [`scripts/agent-skill-generator/README.md`](../../scripts/agent-skill-generator/README.md)
- **System Guide**: [`scripts/agent-skill-generator/SYSTEM_GUIDE.md`](../../scripts/agent-skill-generator/SYSTEM_GUIDE.md)
- **Architecture**: [`architecture/agent-skill-generator-architecture.md`](../../architecture/agent-skill-generator-architecture.md)
- **Process Flow**: [`architecture/agent-skill-generator-process.md`](../../architecture/agent-skill-generator-process.md)
- **Shell Script**: [`scripts/commands/generate-skill.sh`](../../scripts/commands/generate-skill.sh)
- **Full Documentation**: [`scripts/commands/generate-skill.md`](../../scripts/commands/generate-skill.md)

---

## What This Command Does

1. **Extracts Knowledge**: Scrapes and summarizes documentation using Firecrawl + OpenAI
2. **Researches Ecosystem**: Analyzes positioning, alternatives, and best practices using Claude + Exa
3. **Synthesizes Skills**: Generates SKILL.md with structured guidance and examples
4. **Creates References**: Builds supporting documentation files for quick lookup
5. **Registers Modes**: Automatically integrates skills into `.roomodes` configuration

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - skill generated and registered |
| 1 | Missing arguments or environment variables |
| >1 | Python orchestrator failure (see logs with `--verbose`) |

---

## Success Criteria

You've successfully generated a skill when:

- [ ] All 5 phases complete without errors
- [ ] SKILL.md file is created with valid YAML frontmatter
- [ ] Reference files are generated in `references/` directory
- [ ] LICENSE.txt is present
- [ ] Mode is registered in `.roomodes`
- [ ] Validation passes all checks
- [ ] Skill can be activated in Roo Code via `/mode skill-name`

---

## Quick Reference

**Command**: `/generate-skill <URL> [SKILL_NAME] [OPTIONS]`

**Purpose**: Transform web documentation into integrated Roo Code skills

**Time Investment**: 5-10 minutes per skill (automated)

**Payoff**: Production-ready, validated skill with automatic mode registration

**Best For**: API frameworks, databases, cloud platforms, testing tools

**Artifacts Created**:
- `$SKILL_NAME/SKILL.md` - Main skill definition
- `$SKILL_NAME/references/` - Supporting documentation
- `.roomodes` entry - Mode registration