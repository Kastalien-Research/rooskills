# Mode-Skill Integration Validator

## Overview

This validation script ensures the Roo Code ↔ Claude Skills integration pattern in [`.roomodes`](../.roomodes) works correctly by validating file structure, schema compliance, and integration compatibility.

## Usage

### Run Full Validation

```bash
python3 scripts/validate_mode_skill_integration.py
```

This performs comprehensive validation and outputs a detailed report:
- ✓ File structure validation
- ✓ Schema validation
- ✓ YAML frontmatter validation
- ✓ Circular reference detection
- ✓ Mode group compatibility

**Exit Codes:**
- `0` - All validations passed
- `1` - Validation failures detected

### Run Unit Tests

```bash
python3 scripts/validate_mode_skill_integration.py --test
```

Runs the complete unit test suite using Python's unittest framework with verbose output.

## What It Validates

### 1. File Structure Validation

**Tests:**
- All referenced SKILL.md files exist
- Skill paths are valid files (not directories)
- Paths are relative to workspace root
- No absolute paths or parent directory references

**Example Error:**
```
Mode 'algorithmic-art': Skill file does not exist: algorithmic-art/SKILL.md
```

### 2. Schema Validation

**Tests:**
- `skill_ref` objects have required properties: `path` and `merge_strategy`
- `merge_strategy` values are valid: `"override"`, `"append"`, or `"prepend"`
- `.roomodes` file is valid JSON
- `customModes` array exists and contains modes

**Example Error:**
```
Mode 'mcp-builder': skill_ref missing required property 'path'
Mode 'canvas-design': Invalid merge_strategy 'replace'. Must be one of: override, append, prepend
```

### 3. YAML Frontmatter Validation

**Tests:**
- All SKILL.md files have valid YAML frontmatter between `---` markers
- Required fields present: `name`, `description`
- Frontmatter is properly formatted

**Example Error:**
```
Mode 'algorithmic-art': Skill file algorithmic-art/SKILL.md missing YAML frontmatter
Mode 'mcp-builder': Skill mcp-builder/SKILL.md frontmatter missing 'description'
```

### 4. Integration Validation

**Tests:**
- No circular skill references
- Mode groups are valid and compatible
- Skill files can be loaded and parsed

**Example Warning:**
```
Skill algorithmic-art/SKILL.md is referenced by multiple modes: algorithmic-art, art-v2
Mode 'debug': Unknown group 'experimental'
```

## Integration Pattern

The validator checks the integration pattern defined in `.roomodes`:

```json
{
  "slug": "mode-name",
  "name": "🎨 Display Name",
  "roleDefinition": "Mode purpose...",
  "skill_ref": {
    "path": "path/to/SKILL.md",
    "merge_strategy": "override"
  },
  "groups": ["read", "edit", "browser"]
}
```

### Required SKILL.md Format

```markdown
---
name: skill-name
description: Skill description text
license: Complete terms in LICENSE.txt
---

# Skill Content

Instructions and documentation for the skill...
```

## Valid Merge Strategies

- **`override`**: Skill content replaces mode instructions entirely
- **`append`**: Skill content is added after mode instructions
- **`prepend`**: Skill content is added before mode instructions

## Continuous Integration

Add this to CI/CD pipelines to validate integration on every commit:

```yaml
# .github/workflows/validate.yml
- name: Validate Mode-Skill Integration
  run: |
    python3 scripts/validate_mode_skill_integration.py
    if [ $? -ne 0 ]; then
      echo "❌ Mode-skill integration validation failed"
      exit 1
    fi
```

## Test Coverage

The validator includes comprehensive unit tests covering:

1. **`test_roomodes_file_exists`** - .roomodes file presence and JSON validity
2. **`test_roomodes_has_custom_modes`** - customModes array structure
3. **`test_all_skill_refs_have_valid_schema`** - Schema compliance for all skill_ref objects
4. **`test_all_skill_files_exist`** - Referenced files exist and are accessible
5. **`test_all_skill_paths_are_relative`** - Path format validation
6. **`test_all_merge_strategies_are_valid`** - Merge strategy enumeration
7. **`test_all_skill_files_have_yaml_frontmatter`** - YAML frontmatter presence and structure

## Example Output

### Success

```
======================================================================
Roo Code ↔ Claude Skills Integration Validator
======================================================================

📁 Loading .roomodes file...
✓ .roomodes file loaded successfully

📋 Found 19 custom modes

🔗 Found 3 modes with skill references

🔍 Validating mode: algorithmic-art
  ✓ algorithmic-art/SKILL.md
🔍 Validating mode: mcp-builder
  ✓ mcp-builder/SKILL.md
🔍 Validating mode: canvas-design
  ✓ canvas-design/SKILL.md

🔄 Checking for circular references...
✓ No circular references detected

✅ ALL VALIDATIONS PASSED

======================================================================
```

### Failure

```
======================================================================
Roo Code ↔ Claude Skills Integration Validator
======================================================================

📁 Loading .roomodes file...
✓ .roomodes file loaded successfully

📋 Found 19 custom modes

🔗 Found 3 modes with skill references

🔍 Validating mode: new-mode
  ✗ Validation errors detected

❌ VALIDATION FAILURES:
  - Mode 'new-mode': skill_ref missing required property 'merge_strategy'
  - Mode 'new-mode': Skill file does not exist: nonexistent/SKILL.md

Total errors: 2

======================================================================
```

## Maintenance

When adding new modes with skill references:

1. Create the SKILL.md file with proper YAML frontmatter
2. Add skill_ref to the mode in .roomodes
3. Run the validator to ensure integration is correct
4. Fix any reported errors before committing

## Dependencies

- Python 3.6+
- Standard library only (no external dependencies)

## File Size

- Script: 463 lines (within 500-line limit)
- Modular design with separate validator class and test suite
- Well-documented with comprehensive error messages