# NPM Package Guide

## Publishing to NPM

### Prerequisites

1. **NPM Account**: Create an account at [npmjs.com](https://www.npmjs.com/)
2. **Organization Access**: Ensure you have access to `@kastalien-research` organization
3. **Login**: Run `npm login` to authenticate

### First Time Setup

```bash
# Install dependencies
npm install

# Test the CLI locally
npm link
rooskills --help

# Unlink when done testing
npm unlink -g @kastalien-research/rooskills
```

### Publishing

```bash
# 1. Update version in package.json (follow semver)
npm version patch  # or minor, or major

# 2. Publish to NPM
npm publish --access public

# 3. Commit and push the version bump
git add package.json
git commit -m "Bump version to x.x.x"
git push
git push --tags
```

## Usage for End Users

### Quick Start (npx - no installation)

```bash
# Initialize in current directory
npx @kastalien-research/rooskills init

# Initialize in specific directory
npx @kastalien-research/rooskills init -d /path/to/project

# Generate a new skill
npx @kastalien-research/rooskills generate https://docs.example.com skill-name

# List available skills
npx @kastalien-research/rooskills list
```

### Global Installation

```bash
# Install globally
npm install -g @kastalien-research/rooskills

# Use commands directly
rooskills init
rooskills generate https://docs.fastapi.tiangolo.com fastapi-expert
rooskills list
```

### Local Installation (in a project)

```bash
# Install as dev dependency
npm install --save-dev @kastalien-research/rooskills

# Use via npx
npx rooskills init

# Or add to package.json scripts
{
  "scripts": {
    "skills:init": "rooskills init",
    "skills:generate": "rooskills generate"
  }
}
```

## CLI Commands

### `rooskills init`

Initialize Roo Skills in your project.

**Options:**
- `-d, --dir <directory>` - Target directory (default: current directory)
- `--no-install` - Skip Python dependency installation
- `--skills <skills...>` - Install specific skills only

**Examples:**
```bash
rooskills init
rooskills init -d ./my-project
rooskills init --no-install
rooskills init --skills mcp-builder document-skills
```

### `rooskills generate <url> [skill-name]`

Generate a new skill from documentation URL.

**Arguments:**
- `url` - Documentation URL to process (required)
- `skill-name` - Skill identifier in kebab-case (optional)

**Options:**
- `--max-urls <number>` - Maximum URLs to process (default: 20)
- `--output-dir <directory>` - Custom output directory
- `--verbose` - Enable verbose logging

**Examples:**
```bash
rooskills generate https://fastapi.tiangolo.com
rooskills generate https://docs.stripe.com stripe-expert --max-urls 30
rooskills generate https://docs.anthropic.com --verbose
```

### `rooskills list`

List all available pre-built skills.

**Example:**
```bash
rooskills list
```

## What Gets Installed

When you run `rooskills init`, the following files are copied to your project:

```
your-project/
├── .roomodes                         # Roo Code mode configuration
├── .env.example                      # Environment variables template
├── agent_skills_spec.md              # Skills specification
└── .roo/
    ├── commands/                     # Slash commands for Roo Code
    │   ├── generate-skill.md         # /generate-skill command
    │   └── sequential-feynman.md     # /sequential-feynman command
    └── skills/                       # All skills and tools
        ├── mcp-builder/
        ├── document-skills/
        ├── lindy-expert/
        └── scripts/
            └── agent-skill-generator/
```

## Updating the Package

### Version Numbering (Semver)

- **Patch** (1.0.x): Bug fixes, minor changes
- **Minor** (1.x.0): New features, backward compatible
- **Major** (x.0.0): Breaking changes

```bash
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0
```

### Release Checklist

- [ ] Test CLI locally with `npm link`
- [ ] Update README.md if needed
- [ ] Update version with `npm version`
- [ ] Publish with `npm publish --access public`
- [ ] Push git tags
- [ ] Create GitHub release (optional)

## Troubleshooting

### "Command not found" after npx

Make sure you're using the full package name:
```bash
npx @kastalien-research/rooskills init
```

### Permission errors during publish

Ensure you're logged in and have access to the organization:
```bash
npm login
npm org ls @kastalien-research
```

### Python dependencies fail to install

Users can install manually:
```bash
pip install -r .roo/skills/scripts/agent-skill-generator/requirements.txt
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/Kastalien-Research/rooskills/issues
- NPM Package: https://www.npmjs.com/package/@kastalien-research/rooskills
