# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-01-22

### Added

#### Security Framework
- **Input Validation System** - Comprehensive validation for all user inputs
  - URL validation with protocol whitelist (http/https only)
  - Skill name validation (alphanumeric + hyphens/underscores)
  - Path validation to prevent traversal attacks
  - Parameter sanitization for safe command execution
- **Environment Validation** - Required configuration checking on startup
  - Type validation for all environment variables
  - Format validation (API keys, timeouts, etc.)
  - Clear error messages with troubleshooting tips
- **Security Documentation**
  - `SECURITY.md` - Complete security guide with best practices
  - `CODE_REVIEW.md` - Detailed vulnerability analysis (21 issues documented)
  - Security checklist for contributors

#### New Utilities
- `cli/utils/security.js` - JavaScript validation functions (460+ lines)
- `cli/utils/config-validator.js` - Environment variable validator (240+ lines)
- `scripts/feynman-batch-sdk/src/validators.ts` - TypeScript validators (270+ lines)
- `scripts/feynman-batch-sdk/src/constants.ts` - Security constants (290+ lines)

### Changed
- **Enhanced .env.example** - Comprehensive configuration documentation with examples
- **Strict TypeScript Mode** - Enabled full strict checking in tsconfig.json
- **Command Execution** - All CLI commands now use safe execution patterns
- **API Calls** - Added timeout protection for Python Thoughtbox client

### Security
- **Fixed command injection vulnerabilities** (CRITICAL) in `cli/commands/generate.js` and `cli/commands/init.js`
- **Replaced `execSync` with `execFileSync`** - Prevents shell interpretation and command injection
- **Added timeout protection** - All operations have configurable timeouts (default: 30s)
- **Implemented input validation** - All user inputs validated before processing
- **Added path validation** - Prevents path traversal attacks (../, ~, etc.)
- **Safe error messages** - Production errors don't expose sensitive data
- **Environment variable validation** - Required keys checked on startup

### Fixed
- Command injection vulnerability in skill generation (CRITICAL)
- Command injection vulnerability in initialization (CRITICAL)
- Missing input validation across all user inputs (CRITICAL)
- Unprotected environment variables (HIGH)
- Unsafe file operations (HIGH)
- Missing API timeouts in Python client (HIGH)
- Magic numbers extracted to constants (MEDIUM)

## [1.2.1] - 2025-10-22

### Fixed
- Republish to ensure README displays correctly on npm registry
- No functional changes from v1.2.0

## [1.2.0] - 2025-10-22

### Added

#### Sequential Feynman Batch Executor
- **New automation script** (`scripts/feynman-batch.sh`) for running multiple `/sequential-feynman` iterations
- Supports parallel and sequential execution modes
- Automatic retry logic with configurable attempts
- Artifact collection (notebooks, skills, outputs)
- Real-time progress tracking via STATUS.json
- Comprehensive summary report generation
- Background execution support for non-blocking research
- Full technical specification in `specs/feynman-batch-executor.md`
- Usage documentation in `scripts/README-feynman-batch.md`

#### Enhanced Skill Generation
- Updated skill generator to include user codebase context
- Integration with domain knowledge from coding-agent-docs
- Improved ecosystem research capabilities
- Better skill quality through contextual awareness

#### Documentation
- Added comprehensive coding agent documentation (Claude Code, Roo Code, Cursor)
- New specification documents for architecture and workflows
- Enhanced README with automation examples

### Changed
- Updated package description to reflect automation capabilities
- Expanded `files` array in package.json to include new scripts
- Improved .npmignore to properly exclude development files while including scripts

### Fixed
- Better handling of Python dependencies in skill generation
- Improved error messages with actionable commands

## [1.1.4] - 2025-10-21

### Added
- CI/CD workflows with security checks
- Comprehensive security documentation
- NPM keywords for better discoverability

### Changed
- Enhanced .gitignore patterns
- Updated .npmignore to exclude sensitive configs

### Fixed
- Removed Python cache files from repository
- Improved error handling in CLI

## [1.1.3] - 2025-10-20

### Added
- Initial npm package structure
- CLI tool for skill installation
- Core agent skills collection
- Basic documentation

### Changed
- Reorganized project structure
- Improved README documentation

## [Unreleased]

### Planned
- TypeScript SDK for programmatic batch execution
- Python SDK for data science workflows
- MCP server wrapper for agent tool integration
- Web UI for visual progress monitoring
- Distributed worker support
- Semantic comparison of research iterations

---

## Version History

- **1.3.0** - Security framework and comprehensive hardening
- **1.2.1** - Fix npm README display (republish)
- **1.2.0** - Sequential Feynman Batch Executor + Enhanced skill generation
- **1.1.4** - CI/CD and security improvements
- **1.1.3** - Initial npm package release

[1.3.0]: https://github.com/Kastalien-Research/rooskills/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/Kastalien-Research/rooskills/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/Kastalien-Research/rooskills/compare/v1.1.4...v1.2.0
[1.1.4]: https://github.com/Kastalien-Research/rooskills/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/Kastalien-Research/rooskills/releases/tag/v1.1.3
