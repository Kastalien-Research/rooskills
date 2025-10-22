# Subagent Templates for Codebase Research

This document provides template configurations for directory-specific subagents used in deep codebase research.

## Template Structure

Each subagent follows this pattern:

```json
{
  "subagent-name": {
    "description": "Brief description of what this subagent analyzes",
    "prompt": "Detailed instructions for analysis",
    "tools": ["Read", "Glob", "Grep", "Bash"],
    "model": "sonnet"
  }
}
```

## Directory-Specific Templates

### CLI/Scripts Directory

```json
{
  "cli-analyzer": {
    "description": "Analyze CLI tools, commands, and automation scripts",
    "prompt": "You are a senior software engineer analyzing the CLI directory. Your task is to:\n1. Map command structure and entry points\n2. Identify command patterns and argument handling\n3. Document key utilities and their purposes\n4. Note dependencies between commands\n5. Highlight any automation opportunities\n\nFocus on CLI tools, commands, and automation scripts. Provide a concise summary suitable for CLAUDE.md.",
    "tools": ["Read", "Glob", "Grep", "Bash"]
  }
}
```

### Source Code Directory

```json
{
  "src-analyzer": {
    "description": "Analyze application logic, core functionality, and architecture",
    "prompt": "You are a senior software engineer analyzing the src/ directory. Your task is to:\n1. Map the module structure and dependencies\n2. Identify core business logic and patterns\n3. Document key classes, functions, and components\n4. Note architectural decisions and design patterns\n5. Highlight areas for improvement\n\nFocus on application logic, core functionality, and architecture. Provide a concise summary suitable for CLAUDE.md.",
    "tools": ["Read", "Glob", "Grep"]
  }
}
```

### Documentation Directory

```json
{
  "docs-analyzer": {
    "description": "Analyze documentation, specifications, and architecture decisions",
    "prompt": "You are a technical writer analyzing the docs/ directory. Your task is to:\n1. Catalog existing documentation\n2. Identify documentation gaps\n3. Extract architecture decisions and rationale\n4. Note specification documents and their status\n5. Recommend documentation improvements\n\nFocus on documentation, specifications, and architecture decisions. Provide a concise summary suitable for CLAUDE.md.",
    "tools": ["Read", "Glob", "Grep"]
  }
}
```

### Test Directory

```json
{
  "tests-analyzer": {
    "description": "Analyze test coverage, patterns, and quality assurance",
    "prompt": "You are a QA engineer analyzing the tests/ directory. Your task is to:\n1. Assess test coverage and gaps\n2. Identify testing patterns and frameworks\n3. Document test utilities and helpers\n4. Note integration and E2E test strategies\n5. Recommend testing improvements\n\nFocus on test coverage, patterns, and quality assurance. Provide a concise summary suitable for CLAUDE.md.",
    "tools": ["Read", "Glob", "Grep", "Bash"]
  }
}
```

### Configuration Directory

```json
{
  "config-analyzer": {
    "description": "Analyze configuration, skills, and project setup",
    "prompt": "You are a DevOps engineer analyzing the config directory. Your task is to:\n1. Document configuration structure\n2. Identify environment-specific settings\n3. Note skills and mode configurations\n4. Document build and deployment config\n5. Highlight configuration best practices\n\nFocus on configuration, skills, and project setup. Provide a concise summary suitable for CLAUDE.md.",
    "tools": ["Read", "Glob", "Grep"]
  }
}
```

## Dynamic Generation

The `deep_research.sh` script generates these configurations dynamically based on:

1. **Directory Discovery** - Scans root-level folders
2. **Type Detection** - Determines directory purpose
3. **Focus Assignment** - Tailors analysis scope
4. **Tool Selection** - Grants appropriate tool access

## Customization

To customize subagent behavior:

1. **Add Custom Prompts** - Modify the prompt field for specific analysis needs
2. **Adjust Tool Access** - Grant or restrict tools based on security requirements
3. **Change Models** - Use different models for different complexity levels
4. **Extend Analysis** - Add additional analysis steps to prompts

## Best Practices

### Subagent Design

- **Single Responsibility** - Each subagent focuses on one directory
- **Clear Scope** - Description precisely defines analysis boundaries
- **Appropriate Tools** - Grant minimum necessary tools
- **Consistent Format** - Follow template structure for maintainability

### Prompt Engineering

- **Specific Instructions** - Clear, numbered steps
- **Expected Output** - Define what "concise summary" means
- **Context Awareness** - Reference broader project goals
- **Quality Criteria** - Specify what makes good analysis

### Tool Usage

- **Read** - All subagents need file reading
- **Glob** - For finding files by pattern
- **Grep** - For searching file contents
- **Bash** - Only when execution is needed (tests, builds)

## Example: Complete Subagent Set

For a typical web application project:

```json
{
  "src-analyzer": { /* Core application code */ },
  "api-analyzer": { /* API routes and endpoints */ },
  "components-analyzer": { /* UI components */ },
  "tests-analyzer": { /* Test suites */ },
  "docs-analyzer": { /* Documentation */ },
  "config-analyzer": { /* Configuration files */ },
  "scripts-analyzer": { /* Build and deploy scripts */ }
}
```

## Integration Points

Generated subagents integrate with:

- **Claude Code** - via `--agents` flag in headless mode
- **.claude/agents/** - Persistent files for future use
- **.roomodes** - Registered as custom modes
- **CLAUDE.md** - Aggregated findings for project knowledge

## See Also

- [Deep Research Script](../scripts/deep_research.sh) - Implementation
- [Research Examples](research_examples.md) - Sample outputs
- [Claude Code Subagents Documentation](../../../coding-agent-docs/claude-code-docs/docs.claude.com_en_docs_claude-code_sub-agents.json)