# Claude Code Integration Guide

This document explains how the codebase-researcher skill integrates with Claude Code's native features for programmatic subagent creation and headless mode execution.

## Overview

The skill leverages Claude Code's advanced features:
- **`--agents` CLI flag** - Dynamic subagent definition
- **Headless mode** (`-p` flag) - Non-interactive execution
- **JSON output** - Structured result parsing
- **Permission modes** - Automated tool access

## Programmatic Subagent Creation

### Using the `--agents` Flag

Claude Code supports dynamically defining subagents via JSON:

```bash
claude --agents '{
  "directory-analyzer": {
    "description": "Analyze specific directory",
    "prompt": "Analysis instructions...",
    "tools": ["Read", "Grep", "Glob"],
    "model": "sonnet"
  }
}' -p "Research this directory"
```

### Benefits

1. **No File Creation** - Subagents exist only for the session
2. **Scriptable** - Easy to generate programmatically
3. **Composable** - Different configurations for different tasks
4. **Parallel Execution** - Multiple subagents work concurrently

## Headless Mode Integration

### Basic Headless Execution

```bash
claude -p "Analyze this codebase" \
  --permission-mode plan \
  --output-format json
```

### With Dynamic Subagents

```bash
claude --agents "$(./generate_agents.sh)" \
  -p "Research codebase with specialized subagents" \
  --output-format json \
  > research_results.json
```

### Parsing Results

```bash
# Extract findings from JSON output
cat research_results.json | jq -r '.result' > CLAUDE.md

# Check for errors
if [ $(cat research_results.json | jq -r '.is_error') = "true" ]; then
  echo "Research failed"
  exit 1
fi
```

## Permission Management

### Permission Modes

The skill uses `plan` mode for safe, read-only analysis:

```bash
claude --permission-mode plan \
  -p "Research codebase"
```

**Available modes:**
- `default` - Prompt for each tool use
- `acceptEdits` - Auto-accept file edits
- `plan` - Read-only (recommended for research)

### Tool Allowlisting

Pre-approve specific tools:

```bash
claude --allowedTools "Read,Glob,Grep,Bash(ls:*)" \
  --agents "$AGENTS_JSON" \
  -p "Research with pre-approved tools"
```

## Multi-Turn Conversations

### Session Persistence

```bash
# Start research session
SESSION_ID=$(claude -p "Begin codebase research" \
  --output-format json | jq -r '.session_id')

# Continue in multiple turns
claude --resume "$SESSION_ID" \
  -p "Now analyze the API layer"

claude --resume "$SESSION_ID" \
  -p "Document findings in CLAUDE.md"
```

### Benefits

- **Context Preservation** - Subagents remember previous findings
- **Incremental Analysis** - Build understanding progressively
- **Resource Efficiency** - Avoid re-analyzing already understood areas

## Agent Definition Format

### Required Fields

```json
{
  "agent-name": {
    "description": "When to invoke this agent",  // Required
    "prompt": "System prompt for the agent"       // Required
  }
}
```

### Optional Fields

```json
{
  "agent-name": {
    "description": "...",
    "prompt": "...",
    "tools": ["Read", "Edit", "Bash"],  // Optional: defaults to all tools
    "model": "sonnet"                   // Optional: sonnet, opus, haiku
  }
}
```

### Tool Specifications

Available tools for subagents:
- `Read` - Read file contents
- `Edit` - Make targeted edits
- `Write` - Create or overwrite files
- `Bash` - Execute shell commands
- `Glob` - Find files by pattern
- `Grep` - Search file contents
- `Task` - Invoke nested subagents
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web

## Automation Patterns

### Pattern 1: Directory-Per-Subagent

```bash
#!/bin/bash
# Generate one subagent per directory

DIRS=$(ls -d */ | sed 's|/||')
AGENTS_JSON="{"

for DIR in $DIRS; do
  AGENTS_JSON+="\"${DIR}-analyzer\":{"
  AGENTS_JSON+="\"description\":\"Analyze $DIR directory\","
  AGENTS_JSON+="\"prompt\":\"You analyze the $DIR directory...\","
  AGENTS_JSON+="\"tools\":[\"Read\",\"Grep\",\"Glob\"]"
  AGENTS_JSON+="},"
done

AGENTS_JSON="${AGENTS_JSON%,}}"  # Remove trailing comma
```

### Pattern 2: Parallel Processing

```bash
#!/bin/bash
# Process multiple directories in parallel

DIRS=("src" "tests" "docs")

for DIR in "${DIRS[@]}"; do
  claude --agents "{
    \"${DIR}-analyzer\": {
      \"description\": \"Analyze $DIR\",
      \"prompt\": \"Analyze the $DIR directory in detail.\"
    }
  }" -p "Research $DIR/" --output-format json > "${DIR}_results.json" &
done

wait  # Wait for all background processes
```

### Pattern 3: Incremental Research

```bash
#!/bin/bash
# Build understanding incrementally

# Phase 1: High-level overview
claude -p "Provide high-level codebase overview" \
  --output-format json > phase1.json

# Phase 2: Detailed analysis with subagents
SESSION_ID=$(cat phase1.json | jq -r '.session_id')

claude --resume "$SESSION_ID" \
  --agents "$(./generate_subagents.sh)" \
  -p "Now perform detailed directory-by-directory analysis"
```

## Error Handling

### Robust Script Design

```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Trap errors
trap 'echo "Error on line $LINENO"' ERR

# Validate prerequisites
command -v claude >/dev/null || {
  echo "Error: claude not found"
  exit 1
}

command -v jq >/dev/null || {
  echo "Error: jq not found (required for JSON parsing)"
  exit 1
}

# Execute with error checking
if ! RESULT=$(claude --agents "$AGENTS_JSON" -p "$PROMPT" 2>&1); then
  echo "Research failed: $RESULT"
  exit 1
fi
```

### Validation

```bash
# Validate subagents JSON before use
if ! echo "$AGENTS_JSON" | jq '.' >/dev/null 2>&1; then
  echo "Invalid JSON generated"
  exit 1
fi

# Check result format
if ! echo "$RESULT" | jq -e '.result' >/dev/null 2>&1; then
  echo "Unexpected output format"
  exit 1
fi
```

## Performance Optimization

### Parallel Subagent Execution

Claude Code automatically parallelizes subagent work when possible. To maximize performance:

1. **Independent Subagents** - Each analyzes separate directory
2. **Minimal Tool Sets** - Grant only necessary tools
3. **Focused Prompts** - Clear, specific instructions
4. **Output Limits** - Concise summaries, not full transcripts

### Caching Strategies

Use Claude's context caching for repeated analyses:

```bash
# First run builds cache
claude -p "Analyze codebase" > results1.json

# Subsequent runs benefit from cache
claude -c -p "Update analysis with recent changes" > results2.json
```

## Integration with CI/CD

### Automated Documentation

```yaml
# .github/workflows/docs.yml
name: Update Documentation

on:
  push:
    branches: [main]

jobs:
  research:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code
      - name: Run Deep Research
        run: |
          ./.roo/skills/codebase-researcher/scripts/deep_research.sh
      - name: Commit Documentation
        run: |
          git config user.name "AI Documentation Bot"
          git add CLAUDE.md .claude/agents/
          git commit -m "docs: Update AI-generated documentation"
          git push
```

## Security Considerations

### Safe Research Practices

1. **Read-Only by Default** - Use `plan` mode
2. **No Secret Exposure** - Filter sensitive files
3. **Validated Inputs** - Check directory paths
4. **Limited Scope** - Analyze only necessary areas

### Tool Restrictions

```bash
# Restrict to read-only tools
claude --agents "$AGENTS_JSON" \
  --allowedTools "Read,Glob,Grep" \
  -p "Research with restricted tools"
```

## Troubleshooting

### Common Issues

**Issue: Subagents not created**
```bash
# Check JSON validity
echo "$AGENTS_JSON" | jq '.'

# Verify format
# Should be: {"agent-name": {"description": "...", "prompt": "..."}}
```

**Issue: Research incomplete**
```bash
# Increase turn limit
claude --agents "$AGENTS_JSON" \
  --max-turns 20 \
  -p "Research codebase thoroughly"
```

**Issue: Output too large**
```bash
# Use focused prompts
# Ask for "concise summaries" not "detailed reports"
```

### Debug Mode

```bash
# Enable verbose logging
claude --verbose \
  --agents "$AGENTS_JSON" \
  -p "Research with debug output"
```

## Advanced Techniques

### Nested Subagents

Subagents can invoke other subagents:

```bash
claude --agents '{
  "meta-analyzer": {
    "description": "Coordinates other analyzers",
    "prompt": "Use Task tool to invoke directory-specific analyzers as needed.",
    "tools": ["Task", "Read"]
  },
  "src-analyzer": {
    "description": "Analyzes src/ directory",
    "prompt": "Detailed src/ analysis...",
    "tools": ["Read", "Grep"]
  }
}'
```

### Custom Output Formats

```bash
# Research to specific format
claude --agents "$AGENTS_JSON" \
  -p "Research and output as Markdown with mermaid diagrams" \
  --append-system-prompt "Format output as structured Markdown"
```

## See Also

- [Claude Code CLI Reference](../../../coding-agent-docs/claude-code-docs/docs.claude.com_en_docs_claude-code_cli-reference.json)
- [Subagents Documentation](../../../coding-agent-docs/claude-code-docs/docs.claude.com_en_docs_claude-code_sub-agents.json)
- [Headless Mode](../../../coding-agent-docs/claude-code-docs/docs.claude.com_en_docs_claude-code_headless.json)
- [Deep Research Script](../scripts/deep_research.sh)