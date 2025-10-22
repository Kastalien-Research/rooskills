# Sequential Feynman Batch Executor

Automate multiple runs of the `/sequential-feynman` workflow to produce validated research notebooks and comprehensive reports.

## Quick Start

```bash
# Basic usage - single iteration
./scripts/feynman-batch.sh "distributed tracing systems"

# Multiple iterations
./scripts/feynman-batch.sh "React Server Components" 3

# Parallel execution
./scripts/feynman-batch.sh "MCP architecture" 5 --parallel 2

# Custom output directory
./scripts/feynman-batch.sh "WebAssembly optimization" 3 --output ./research
```

## Features

✅ **Non-blocking execution** - Run in background while agent works on other tasks  
✅ **Parallel processing** - Execute multiple iterations concurrently  
✅ **Automatic retry** - Handles failures with configurable retry logic  
✅ **Artifact collection** - Gathers notebooks, skills, and outputs  
✅ **Progress tracking** - JSON status file for monitoring  
✅ **Summary reports** - Markdown report with comparison analysis  

## Usage

```bash
./scripts/feynman-batch.sh <topic> [iterations] [options]
```

### Arguments

- **topic** (required) - Topic to research
- **iterations** (optional) - Number of iterations to run (default: 1)

### Options

- `--parallel N` - Run N iterations in parallel (default: 1)
- `--output DIR` - Output directory (default: feynman-batch-outputs)
- `--timeout SEC` - Timeout per iteration in seconds (default: 14400 = 4 hours)
- `--retries N` - Max retries per iteration (default: 3)
- `--help` - Show help message

## Examples

### Example 1: Single Deep Research

```bash
./scripts/feynman-batch.sh "distributed consensus algorithms"
```

**Output:**
```
feynman-batch-outputs/
  20251022-053000-distributed-consensus-algorithms/
    iteration-1/
      output.json
      execution.log
      artifacts/
        feynman-distributed-consensus-algorithms.ipynb
        distributed-consensus-algorithms/
          SKILL.md
        metadata.json
    STATUS.json
    REPORT.md
```

### Example 2: Comparative Analysis (3 Iterations)

```bash
./scripts/feynman-batch.sh "React Server Components" 3
```

Runs 3 sequential iterations to:
- Explore different perspectives
- Validate consistency across runs
- Compare depth and coverage
- Identify common patterns

### Example 3: Parallel Research (5 Topics, 2 Concurrent)

```bash
./scripts/feynman-batch.sh "microservices patterns" 5 --parallel 2
```

Executes 5 iterations with max 2 running concurrently:
- Faster completion (2.5x speedup)
- Controlled resource usage
- Automatic queue management

### Example 4: Background Execution

```bash
# Start in background
nohup ./scripts/feynman-batch.sh "Rust async runtime" 3 > batch.log 2>&1 &

# Check status
cat feynman-batch-outputs/*/STATUS.json | jq '.progress'

# Monitor progress
tail -f batch.log
```

## Output Structure

```
feynman-batch-outputs/
  [run-id]/
    iteration-1/
      output.json          # Claude's full output
      execution.log        # Execution logs
      artifacts/
        *.ipynb           # Feynman notebooks
        */SKILL.md        # Generated skills
        metadata.json     # Artifact metadata
    iteration-2/
      ...
    STATUS.json           # Real-time status
    REPORT.md            # Summary report
```

## Status Monitoring

The `STATUS.json` file tracks execution in real-time:

```json
{
  "run_id": "20251022-053000-distributed-tracing",
  "topic": "distributed tracing systems",
  "iterations": 3,
  "status": "running",
  "progress": {
    "completed": 1,
    "failed": 0,
    "running": 1,
    "total": 3
  },
  "iterations_status": [
    {
      "iteration": 1,
      "status": "completed",
      "message": "Success",
      "timestamp": "2025-10-22T10:30:00Z"
    }
  ]
}
```

## Summary Report

Each run generates a `REPORT.md` with:

- **Summary** - Completion stats, duration, timestamps
- **Execution Status** - Per-iteration results table
- **Artifacts** - List of generated notebooks and skills
- **Next Steps** - Recommended actions

## Integration with Agents

Agents can use this script as a background tool:

```typescript
// Pseudo-code for agent tool
async function delegateResearch(topic: string, iterations: number) {
  // Start batch in background
  spawn('./scripts/feynman-batch.sh', [topic, iterations.toString()], {
    detached: true,
    stdio: 'ignore'
  });
  
  // Agent continues other work...
  
  // Check status later
  const status = JSON.parse(
    fs.readFileSync('feynman-batch-outputs/*/STATUS.json')
  );
  
  if (status.status === 'completed') {
    // Process results
    const report = fs.readFileSync(
      `${status.run_id}/REPORT.md`, 'utf8'
    );
  }
}
```

## Requirements

- **Claude Code CLI** - `claude` command must be available
- **jq** - For JSON processing (install: `brew install jq`)
- **Bash 4+** - Modern bash features
- **API Key** - Set `CLAUDE_API_KEY` environment variable

## Performance

**Per Iteration:**
- Time: 2-4 hours (depends on topic complexity)
- API Cost: ~$2-5 (depends on model and usage)
- Storage: ~50MB (notebooks + skills)

**Parallel Execution:**
- 2x concurrency = ~2x speedup
- 3x concurrency = ~2.5x speedup (diminishing returns)
- Recommended: 2-3 concurrent for optimal balance

## Troubleshooting

### Script not found
```bash
# Make executable
chmod +x scripts/feynman-batch.sh

# Run from project root
./scripts/feynman-batch.sh "topic"
```

### jq not found
```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq
```

### Timeout issues
```bash
# Increase timeout to 6 hours
./scripts/feynman-batch.sh "complex topic" 1 --timeout 21600
```

### API rate limits
```bash
# Reduce concurrency
./scripts/feynman-batch.sh "topic" 5 --parallel 1
```

## Advanced Usage

### Custom Tool Restrictions

Edit the script to modify allowed tools:

```bash
# Line ~200 in feynman-batch.sh
claude -p "/sequential-feynman $TOPIC" \
  --allowedTools "Read,Write,Grep,WebSearch" \  # Customize here
  --permission-mode acceptEdits
```

### Integration with CI/CD

```yaml
# .github/workflows/research.yml
name: Automated Research
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  research:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run batch research
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        run: |
          ./scripts/feynman-batch.sh "weekly topic" 2
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: research-outputs
          path: feynman-batch-outputs/
```

## Related Documentation

- [Specification](../specs/feynman-batch-executor.md) - Full technical spec
- [Sequential Feynman Command](../.claude/commands/sequential-feynman.md) - Base workflow
- [Claude Code Headless Mode](https://docs.claude.com/en/docs/claude-code/headless) - CLI reference

## License

Same as parent project.
