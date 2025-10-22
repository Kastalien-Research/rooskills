---
description: Generate Skills from web documentation - supports both coding agents and domain knowledge with automated extraction and research
---
**Execution Mode**: Auto-Coder

When this command is invoked, you must:
1. Switch to Auto-Coder mode (if not already)
2. Execute the shell script: `./scripts/commands/generate-skill.sh "$@"`
3. Monitor the output and report progress through all 5 phases
4. Return to the original mode after completion


# /generate-skill

Automatically create integrated Roo Code skills from web documentation using AI-powered extraction, research, and synthesis. Supports both coding agents and domain knowledge skills.

## Usage

```
/generate-skill $URL1 [$URL2 $URL3 ...] [--skill-type $TYPE] [--max-urls $MAX_URLS] [--use-feynman $USE_FEYNMAN] [--parallel $N]
```

### Arguments

- **`$URL1, $URL2, ...`** (required) - One or more documentation URLs to process
- **`$SKILL_NAME`** (optional) - Skill identifier in kebab-case (auto-generated from URL if not provided)
- **`--skill-type $TYPE`** (optional) - Type of skill: `coding-agent` (default) or `domain-knowledge`
- **`$MAX_URLS`** (optional) - Maximum URLs to scrape per product (default: `20`)
- **`$USE_FEYNMAN`** (optional) - Use Sequential Feynman for deep understanding (default: `true`)
- **`--parallel $N`** (optional) - Maximum concurrent subagents (default: `3`)

### Quick Examples

```bash
# Basic usage - generate coding agent skill from single URL
/generate-skill https://fastapi.tiangolo.com

# Generate domain knowledge skills from multiple URLs
/generate-skill https://langchain-ai.github.io/langgraph/ https://effect.website/ https://modelcontextprotocol.io/ --skill-type domain-knowledge

# Multiple coding agent URLs with parallel processing
/generate-skill https://cursor.com https://windsurf.com https://cline.bot --skill-type coding-agent

# Control parallelism
/generate-skill https://cursor.com https://windsurf.com --parallel 5

# Custom skill name (single URL only)
/generate-skill https://supabase.com supabase-expert --skill-type domain-knowledge

# Limit URLs and skip deep analysis
/generate-skill https://stripe.com/docs stripe-integration --max-urls 30 --use-feynman false

# Deep dive with Sequential Feynman for domain knowledge
/generate-skill https://langchain.readthedocs.io langchain-expert --skill-type domain-knowledge --max-urls 50 --use-feynman true

# Batch process coding agents with viability checks
/generate-skill \
  https://cursor.com \
  https://windsurf.com \
  https://cline.bot \
  https://aider.chat \
  --skill-type coding-agent \
  --parallel 4 \
  --max-urls 20
```

### Multi-URL Processing

When multiple URLs are provided:
1. **One subagent per URL** - Each URL gets a dedicated Claude Agent SDK subagent
2. **Parallel execution** - Subagents run concurrently (up to `--parallel` limit)
3. **Independent pipelines** - Each subagent owns the complete Phase 0-7 pipeline
4. **Viability filtering** - Non-viable products get reports, viable ones get skills
5. **Aggregated results** - Summary shows all skills generated and reports created

**Performance:**
- 3 URLs with `--parallel 3`: ~5-10 minutes total (vs 15-30 minutes sequential)
- Respects rate limits through controlled concurrency
- Failed URLs don't block others

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

## Unix Composability

The enhanced pipeline follows Unix philosophy: atomic scripts that can be composed via stdin/stdout.

### Atomic Scripts

Each phase is implemented as a standalone script:

```bash
# Phase 0: Viability Evaluation
./scripts/agent-skill-generator/evaluate-viability.py <URL> > viability.json

# Phase 0b: Report Generation (for non-viable)
cat viability.json | ./scripts/agent-skill-generator/generate-report.py > report.md

# Phase 1-5: Skill Generation
cat viability.json | ./scripts/agent-skill-generator/generate-skill.py > skill-result.json

# Phase 6: Mapping Specification
./scripts/agent-skill-generator/generate-mapping-spec.py \
  --viability viability.json \
  --skill-dir ./skill-name \
  --output MAPPING.md
```

### Pipeline Composition Examples

**Example 1: Evaluate → Generate or Report**

```bash
# Evaluate viability first
./evaluate-viability.py https://cursor.com | tee viability.json

# If viable, generate skill; else generate report
if [ $(jq -r '.viable' viability.json) = "true" ]; then
  cat viability.json | ./generate-skill.py | tee skill-result.json
  cat skill-result.json | ./generate-mapping-spec.py > MAPPING.md
else
  cat viability.json | ./generate-report.py > cursor-report.md
fi
```

**Example 2: Batch Processing with Filtering**

```bash
# Process multiple URLs, filter for viable ones
cat urls.txt | \
  xargs -I {} ./evaluate-viability.py {} | \
  jq -r 'select(.viable==true) | .url' | \
  xargs -I {} ./generate-skill.py {}
```

**Example 3: Pure Unix Pipeline**

```bash
# One-liner: evaluate → generate (if viable) → map
./evaluate-viability.py https://cursor.com | \
  tee viability.json | \
  jq -r 'select(.viable==true)' | \
  ./generate-skill.py | \
  ./generate-mapping-spec.py
```

### Benefits of Composability

1. **Modularity** - Run phases independently for testing/debugging
2. **Reusability** - Combine scripts in different ways for different workflows
3. **Observability** - Pipe through `tee` or `jq` to inspect intermediate results
4. **Flexibility** - Easy to add custom processing between phases
5. **Testability** - Each script can be unit tested with sample JSON

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

### Phase 0: Viability Evaluation (Optional but Recommended)

**Objective:** Assess if the product has sufficient extensibility mechanisms before expensive scraping

```bash
echo "
═══════════════════════════════════════
Phase 0: Viability Evaluation
═══════════════════════════════════════
"

# Quick viability check using evaluate-viability.py
if [ -f "$AGENT_GEN_DIR/evaluate-viability.py" ]; then
  echo "🔍 Evaluating viability of $URL..."

  if python3 "$AGENT_GEN_DIR/evaluate-viability.py" "$URL" > "$TEMP_DIR/viability.json" 2>&1; then
    VIABLE=$(jq -r '.viable' "$TEMP_DIR/viability.json")
    CONFIDENCE=$(jq -r '.confidence' "$TEMP_DIR/viability.json")
    PRODUCT_NAME=$(jq -r '.product_name' "$TEMP_DIR/viability.json")

    echo "📊 Viability Assessment:"
    echo "   Product: $PRODUCT_NAME"
    echo "   Viable: $VIABLE"
    echo "   Confidence: $CONFIDENCE"

    if [ "$VIABLE" != "true" ]; then
      echo "❌ Product not viable for Skills mapping"
      echo "   Generating viability report instead..."

      cat "$TEMP_DIR/viability.json" | \
        python3 "$AGENT_GEN_DIR/generate-report.py" \
        > "$TEMP_DIR/${SKILL_NAME}-viability-report.md"

      echo "✅ Report generated: $TEMP_DIR/${SKILL_NAME}-viability-report.md"
      echo ""
      echo "This product lacks sufficient extensibility mechanisms."
      echo "See the report for details and recommendations."
      exit 0
    fi

    echo "✅ Viable for Skills mapping, proceeding with generation..."
  else
    echo "⚠️  Viability check failed, continuing with generation anyway..."
  fi
else
  echo "⚠️  evaluate-viability.py not found, skipping viability check"
fi
```

**What This Phase Does:**
1. Uses Exa API to quickly research product extensibility
2. Analyzes if product has plugin/extension/rule systems
3. Returns structured assessment with confidence score
4. If not viable: generates report and exits early
5. If viable: proceeds with normal skill generation

**Benefits:**
- Saves time by avoiding generation for non-viable products
- Produces actionable reports for products without extensibility
- Confidence score helps prioritize which products to tackle

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

### Phase 6: Mapping Specification Generation (Optional)

**Objective:** Generate mapping specification for products with extensibility mechanisms

```bash
echo "
═══════════════════════════════════════
Phase 6: Mapping Specification
═══════════════════════════════════════
"

# Check if viability assessment exists and product is viable
if [ -f "$TEMP_DIR/viability.json" ]; then
  MAPPING_STRATEGY=$(jq -r '.mapping_strategy // "n/a"' "$TEMP_DIR/viability.json")

  if [ "$MAPPING_STRATEGY" != "n/a" ] && [ "$MAPPING_STRATEGY" != "impossible" ]; then
    echo "🗺️  Generating mapping specification..."
    echo "   Strategy: $MAPPING_STRATEGY"

    # Generate mapping spec
    python3 "$AGENT_GEN_DIR/generate-mapping-spec.py" \
      --viability "$TEMP_DIR/viability.json" \
      --skill-dir "$SKILL_DIR" \
      --output "$SKILL_DIR/MAPPING.md" \
      2>&1 | tee -a "$LOG_FILE"

    if [ -f "$SKILL_DIR/MAPPING.md" ]; then
      echo "✅ Mapping specification created: $SKILL_DIR/MAPPING.md"
      echo ""
      echo "This spec documents how to map Claude Skills to this product's"
      echo "extensibility system with estimated ${MAPPING_STRATEGY} approach."
    else
      echo "⚠️  Mapping spec generation failed"
    fi
  else
    echo "ℹ️  No mapping strategy available, skipping mapping spec"
  fi
else
  echo "ℹ️  No viability assessment found, skipping mapping spec"
fi
```

**What This Phase Does:**
1. Checks if product has extensibility mechanisms (from Phase 0)
2. Generates detailed mapping specification (MAPPING.md)
3. Documents conversion strategy and requirements
4. Provides implementation plan and examples
5. Similar to the Cursor Skills mapping spec

**Output:**
- `MAPPING.md` - Comprehensive guide for converting Skills to product format
- Includes conversion scripts, validation approach, success metrics

### Phase 7: Validation and Output

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