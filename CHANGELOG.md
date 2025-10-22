# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- **1.2.1** - Fix npm README display (republish)
- **1.2.0** - Sequential Feynman Batch Executor + Enhanced skill generation
- **1.1.4** - CI/CD and security improvements
- **1.1.3** - Initial npm package release

[1.2.1]: https://github.com/Kastalien-Research/rooskills/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/Kastalien-Research/rooskills/compare/v1.1.4...v1.2.0
[1.1.4]: https://github.com/Kastalien-Research/rooskills/compare/v1.1.3...v1.1.4
[1.1.3]: https://github.com/Kastalien-Research/rooskills/releases/tag/v1.1.3
