# Generate Skill Command - Usage Examples

This document provides practical examples for using the `generate-skill.sh` command wrapper.

## Prerequisites

Set up your environment variables first:

```bash
export FIRECRAWL_API_KEY="fc-your-key-here"
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Or create a `.env` file in the project root:

```bash
FIRECRAWL_API_KEY=fc-your-key-here
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Basic Examples

### Example 1: Auto-Generated Skill Name

Generate a skill with automatically detected name from URL:

```bash
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com"
```

Result:
- Skill name: `fastapi`
- Output directory: `./fastapi/`

### Example 2: Custom Skill Name

Specify a custom skill name:

```bash
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" "fastapi-developer"
```

Result:
- Skill name: `fastapi-developer`
- Output directory: `./fastapi-developer/`

### Example 3: Increased URL Limit

Process more documentation pages:

```bash
./scripts/commands/generate-skill.sh "https://pydantic-docs.helpmanual.io" --max-urls 50
```

Result:
- Scrapes up to 50 pages instead of default 20
- Auto-generated name: `pydantic-docs`

## Advanced Examples

### Example 4: Custom Output Directory

Save skill files to a specific location:

```bash
./scripts/commands/generate-skill.sh \
    "https://docs.python.org/3/library/asyncio.html" \
    "asyncio-expert" \
    --output-dir "./my-skills/asyncio"
```

Result:
- Skill files saved to: `./my-skills/asyncio/`
- SKILL.md path: `./my-skills/asyncio/SKILL.md`

### Example 5: Verbose Logging

Enable detailed logging for debugging:

```bash
./scripts/commands/generate-skill.sh \
    "https://flask.palletsprojects.com" \
    "flask-developer" \
    --max-urls 30 \
    --verbose
```

Result:
- Shows detailed progress for each phase
- Displays API calls and responses
- Useful for troubleshooting issues

### Example 6: Complete Configuration

Use all available options:

```bash
./scripts/commands/generate-skill.sh \
    "https://www.djangoproject.com/documentation" \
    "django-expert" \
    --output-dir "./professional-skills/django" \
    --max-urls 40 \
    --verbose
```

Result:
- Custom skill name: `django-expert`
- Custom output location: `./professional-skills/django/`
- Processes up to 40 pages
- Verbose logging enabled

## Domain-Specific Examples

### Example 7: API Documentation

Generate skill for API frameworks:

```bash
./scripts/commands/generate-skill.sh "https://docs.nestjs.com"
```

Auto-detected name: `docs-nestjs`

### Example 8: Database Documentation

Generate skill for database tools:

```bash
./scripts/commands/generate-skill.sh \
    "https://www.postgresql.org/docs/current" \
    "postgresql-admin" \
    --max-urls 60
```

### Example 9: Cloud Platform Documentation

Generate skill for cloud platforms:

```bash
./scripts/commands/generate-skill.sh \
    "https://cloud.google.com/firestore/docs" \
    "firestore-developer" \
    --output-dir "./cloud-skills/gcp"
```

### Example 10: Testing Framework

Generate skill for testing tools:

```bash
./scripts/commands/generate-skill.sh \
    "https://docs.pytest.org" \
    "pytest-expert"
```

## Troubleshooting Examples

### Example 11: Debug Failed Generation

If generation fails, use verbose mode:

```bash
./scripts/commands/generate-skill.sh \
    "https://problematic-site.com" \
    "debug-skill" \
    --max-urls 5 \
    --verbose
```

### Example 12: Rate Limit Testing

Test with minimal pages to avoid rate limits:

```bash
./scripts/commands/generate-skill.sh \
    "https://test-docs.example.com" \
    "test-skill" \
    --max-urls 3
```

## Batch Processing Examples

### Example 13: Generate Multiple Skills

Create a script to generate multiple skills:

```bash
#!/bin/bash

# Generate multiple framework skills
./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" "fastapi-dev" &
./scripts/commands/generate-skill.sh "https://flask.palletsprojects.com" "flask-dev" &
./scripts/commands/generate-skill.sh "https://docs.djangoproject.com" "django-dev" &

wait
echo "All skills generated!"
```

### Example 14: Organized Skill Library

Generate skills into organized directories:

```bash
# Backend frameworks
./scripts/commands/generate-skill.sh \
    "https://fastapi.tiangolo.com" \
    "fastapi" \
    --output-dir "./skills/backend/fastapi"

# Frontend frameworks  
./scripts/commands/generate-skill.sh \
    "https://react.dev" \
    "react" \
    --output-dir "./skills/frontend/react"

# Databases
./scripts/commands/generate-skill.sh \
    "https://www.postgresql.org/docs" \
    "postgresql" \
    --output-dir "./skills/databases/postgresql"
```

## Output Structure

After successful generation, you'll see:

```
skill-name/
├── SKILL.md                      # Main skill definition
├── LICENSE.txt                   # License information
└── references/                   # Supporting documentation
    ├── api_documentation.md      # Full API docs
    └── documentation_index.md    # Quick reference index
```

The skill is automatically registered in `.roomodes` and ready to use in Roo Code.

## Common Issues

### Issue: Missing Environment Variables

```bash
# Check if variables are set
echo $FIRECRAWL_API_KEY
echo $OPENAI_API_KEY  
echo $ANTHROPIC_API_KEY

# Set them if missing
export FIRECRAWL_API_KEY="your-key"
```

### Issue: Python Dependencies Missing

The script auto-installs dependencies, but you can manually install:

```bash
pip install -r scripts/agent-skill-generator/requirements.txt
```

### Issue: Permission Denied

Make sure the script is executable:

```bash
chmod +x scripts/commands/generate-skill.sh
```

## Next Steps

After generating a skill:

1. Review the generated `SKILL.md`
2. Test the skill in Roo Code
3. Customize as needed
4. Share with the community

For more information, see:
- [Command README](./README.md)
- [Python Orchestrator README](../agent-skill-generator/README.md)
- [Architecture Documentation](../../architecture/agent-skill-generator-architecture.md)