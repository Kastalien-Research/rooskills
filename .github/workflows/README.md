# GitHub Actions Workflows

This directory contains CI/CD workflows for automated testing, validation, and publishing.

## Workflows

### 🔍 CI/CD (`ci.yml`)

**Triggers:** Push to `main` or `develop`, Pull Requests

**Jobs:**
1. **Security Check** - Validates security and package integrity
   - Scans git history for `.env` files
   - Verifies `.gitignore` patterns
   - Detects exposed API keys in code
   - Validates `package.json` structure
   - Tests package build for sensitive files
   - Checks CLI executability
   - Scans for Python cache files

2. **Test** - Runs test suite
   - Executes `npm test`
   - Tests CLI commands (`--help`, `--version`)

3. **Package Validation** - Validates npm package
   - Creates package tarball
   - Tests installation
   - Verifies package contents
   - Uploads package artifact (7-day retention)

### 📋 PR Checks (`pr-check.yml`)

**Triggers:** Pull Request opened, synchronized, or reopened

**Checks:**
- Sensitive file changes (`.env`, `__pycache__`, etc.)
- Package version changes
- Package size validation (warns if > 5MB)
- Lint checks (if configured)
- Generates PR summary with package stats

### 🚀 Publish (`publish.yml`)

**Triggers:** 
- GitHub Release published
- Manual workflow dispatch

**Features:**
- Pre-publish security checks
- Optional version bumping
- Automated npm publishing with provenance
- Git tag creation
- Package artifact upload (30-day retention)
- Post-publish summary

## Setup

### Required Secrets

Add these secrets to your GitHub repository:

1. **`NPM_TOKEN`** - npm authentication token
   - Go to https://www.npmjs.com/settings/YOUR_USERNAME/tokens
   - Create a new "Automation" token
   - Add to GitHub: Settings → Secrets → Actions → New repository secret

### Required Permissions

The publish workflow requires:
- `contents: write` - For creating tags
- `id-token: write` - For npm provenance

These are configured in the workflow file.

## Usage

### Running CI Checks Locally

```bash
# Security checks
git log --all --full-history -- .env
npm pack --dry-run | grep -E "\.env|\.pyc|__pycache__"

# Package validation
npm pack
tar -tzf kastalien-research-rooskills-*.tgz | head -20

# CLI tests
node cli/index.js --help
node cli/index.js --version
```

### Publishing a New Version

#### Option 1: GitHub Release (Recommended)
1. Create a new release on GitHub
2. Tag format: `v1.2.3`
3. Workflow automatically publishes to npm

#### Option 2: Manual Workflow Dispatch
1. Go to Actions → Publish to npm → Run workflow
2. Optionally specify version to bump
3. Workflow publishes to npm and creates tag

#### Option 3: Manual Publish
```bash
# Bump version
npm version patch  # or minor, major

# Publish
npm publish --access public --provenance

# Push changes and tag
git push && git push --tags
```

## Workflow Status Badges

Add to your README.md:

```markdown
[![CI/CD](https://github.com/Kastalien-Research/rooskills/actions/workflows/ci.yml/badge.svg)](https://github.com/Kastalien-Research/rooskills/actions/workflows/ci.yml)
[![Publish](https://github.com/Kastalien-Research/rooskills/actions/workflows/publish.yml/badge.svg)](https://github.com/Kastalien-Research/rooskills/actions/workflows/publish.yml)
```

## Security Checks Reference

### Files That Trigger Failures

- `.env` files (except `.env.example`)
- Python cache: `__pycache__/`, `*.pyc`, `*.pyo`
- API keys matching pattern: `sk-[a-zA-Z0-9-_]{20,}`
- MCP configs: `.roo/mcp.json`, `cc_mcp_config.json`

### Files That Trigger Warnings

- IDE configs: `.claude/`, `.refactoring-game/`
- Large package size (> 5MB)

## Troubleshooting

### CI Fails: "Sensitive files found in package"

Check your `.npmignore` and `package.json` files array:
```bash
npm pack --dry-run | grep -E "\.env|\.pyc|__pycache__"
```

### CI Fails: "Missing pattern in .gitignore"

Ensure `.gitignore` includes:
```
.env
__pycache__/
*.pyc
venv/
.claude/
.refactoring-game/
```

### Publish Fails: "NPM_TOKEN not found"

Add npm token to GitHub secrets:
1. Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `NPM_TOKEN`
4. Value: Your npm automation token

### Package Size Too Large

Optimize by excluding unnecessary files:
```bash
# Check what's included
npm pack --dry-run

# Update .npmignore or package.json files array
# Remove large documentation, examples, or test files
```

## Maintenance

### Updating Node Version

Edit all workflow files to update:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '18'  # Update this
```

### Adding New Security Checks

Edit `ci.yml` → `security-check` job → Add new step

### Modifying Package Validation

Edit `ci.yml` → `package-validation` job → Update validation logic

## Best Practices

1. **Always run security checks** before publishing
2. **Test package installation** locally before releasing
3. **Use semantic versioning** (major.minor.patch)
4. **Create GitHub releases** for version tracking
5. **Review workflow runs** after each push
6. **Keep secrets secure** - never commit tokens

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [npm Publishing Guide](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)
- [npm Provenance](https://docs.npmjs.com/generating-provenance-statements)
- [Semantic Versioning](https://semver.org/)
