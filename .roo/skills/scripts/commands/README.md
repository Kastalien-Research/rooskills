# Shell Command Wrappers

This directory contains shell command wrappers that provide convenient CLI interfaces for various automation tasks in the Roo Skills project.

## Available Commands

### `generate-skill.sh`

Shell wrapper for the Agent Skill Generator that transforms web documentation into integrated Roo Code skills.

**Location:** [`scripts/commands/generate-skill.sh`](./generate-skill.sh)

**Purpose:** Provides a user-friendly command-line interface with:
- Environment validation
- Argument parsing with sensible defaults
- Visual progress indicators
- Comprehensive error handling
- Auto-generated skill names from URLs

**Quick Start:**

```bash
# Basic usage with auto-generated skill name
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com"

# With custom skill name
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" "fastapi-dev"

# With options
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" --max-urls 30 --verbose
```

**Required Environment Variables:**

```bash
export FIRECRAWL_API_KEY="fc-xxx..."
export OPENAI_API_KEY="sk-xxx..."
export ANTHROPIC_API_KEY="sk-ant-xxx..."
```

**Arguments:**

- `URL` - Documentation URL to process (required)
- `SKILL_NAME` - Skill identifier in kebab-case (optional, auto-generated from URL)

**Options:**

- `--max-urls N` - Maximum number of URLs to process (default: 20)
- `--use-feynman` - Enable Feynman technique for documentation (default: true)
- `--output-dir DIR` - Output directory (default: SKILL_NAME)
- `--verbose` - Enable verbose logging
- `--help` - Show help message

**Features:**

1. **Environment Validation**
   - Checks for all required API keys
   - Validates Python installation
   - Verifies Python dependencies

2. **Auto-Generated Skill Names**
   - Extracts domain from URL
   - Converts to kebab-case format
   - Removes common prefixes (www, docs, api)

3. **Visual Feedback**
   - Color-coded status messages
   - Clear section headers
   - Progress indicators
   - Error and warning highlights

4. **Error Handling**
   - Validates all inputs before execution
   - Provides helpful error messages
   - Suggests troubleshooting steps
   - Exits with appropriate status codes

**Examples:**

```bash
# Generate FastAPI skill
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com"

# Generate with custom name and increased URL limit
./scripts/commands/generate-skill.sh \
    "https://pydantic-docs.helpmanual.io" \
    "pydantic-expert" \
    --max-urls 40

# Generate with custom output directory
./scripts/commands/generate-skill.sh \
    "https://docs.python.org/3/library/asyncio.html" \
    --output-dir "./my-skills/asyncio" \
    --verbose
```

**Workflow Phases:**

The script coordinates 5 phases through the Python orchestrator:

1. **Phase 1: Knowledge Extraction** - Scrapes and summarizes documentation
2. **Phase 2: Ecosystem Research** - Analyzes positioning and best practices
3. **Phase 3: Skill Synthesis** - Generates SKILL.md with structured guidance
4. **Phase 4: File Writing** - Writes all skill files to disk
5. **Phase 5: Mode Registration** - Registers skill in .roomodes configuration

**Exit Codes:**

- `0` - Success
- `1` - Missing required arguments or environment variables
- `>1` - Python orchestrator failure

**Dependencies:**

- Bash 4.0+
- Python 3.10+
- Python packages (auto-installed):
  - typer
  - rich
  - pydantic-settings
  - anthropic
  - openai
  - firecrawl-py

**Troubleshooting:**

If the script fails, try these steps:

1. Run with `--verbose` flag for detailed logs
2. Verify all environment variables are set: `echo $FIRECRAWL_API_KEY`
3. Check Python version: `python3 --version`
4. Manually install dependencies: `pip install -r scripts/agent-skill-generator/requirements.txt`
5. Verify URL is accessible in a browser

**Architecture:**

The wrapper script delegates actual skill generation to the Python orchestrator:

```
generate-skill.sh (this script)
    ↓
    Validates environment
    ↓
    Parses arguments
    ↓
    Calls Python orchestrator
    ↓
scripts.agent-skill-generator.orchestrator
    ↓
    Executes 5-phase workflow
```

**Related Documentation:**

- [Agent Skill Generator Architecture](../../architecture/agent-skill-generator-architecture.md)
- [Agent Skill Generator Process](../../architecture/agent-skill-generator-process.md)
- [Python Orchestrator README](../agent-skill-generator/README.md)

## Adding New Commands

To add a new shell command wrapper:

1. Create a new `.sh` file in this directory
2. Make it executable: `chmod +x scripts/commands/your-command.sh`
3. Follow the same structure as `generate-skill.sh`:
   - Environment validation
   - Argument parsing
   - Visual feedback
   - Error handling
   - Clear help text
4. Document it in this README
5. No hardcoded secrets - use environment variables

## Best Practices

- **Environment Variables**: Always use environment variables for sensitive data
- **Error Messages**: Provide clear, actionable error messages
- **Help Text**: Include comprehensive `--help` output
- **Exit Codes**: Use standard exit codes (0 = success, 1+ = failure)
- **Visual Feedback**: Use color-coded messages for better UX
- **Validation**: Validate all inputs before executing operations
- **Documentation**: Keep this README updated with new commands