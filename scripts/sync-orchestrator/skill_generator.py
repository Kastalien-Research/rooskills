#!/usr/bin/env python3
"""
Skill Generator - Generate skills from commands using Thoughtbox intent.

This module creates comprehensive SKILL.md files from command definitions.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict


def generate_skill_from_command(
    command_path: str,
    intent_data: Dict,
    output_dir: str,
    verbose: bool = False
) -> bool:
    """
    Generate a SKILL.md file from a command using Thoughtbox intent.

    Args:
        command_path: Path to the command .md file
        intent_data: Intent analysis from Thoughtbox
        output_dir: Directory where skill folder will be created
        verbose: Enable detailed logging

    Returns:
        True if successful, False otherwise
    """
    command_name = intent_data.get("name", Path(command_path).stem)

    # Read command content for context
    with open(command_path, 'r') as f:
        command_content = f.read()

    # Extract description from frontmatter
    import re
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', command_content, re.DOTALL)
    description = ""
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        desc_match = re.search(r'description:\s*(.+?)(?:\n|$)', fm)
        if desc_match:
            description = desc_match.group(1).strip()

    # If no description, use intent purpose
    if not description:
        description = intent_data.get("purpose", f"Skill for /{command_name} command")

    # Generate SKILL.md content
    skill_md = f"""---
name: {command_name}
description: {description}
license: MIT
---

# {command_name.replace('-', ' ').title()} Skill

## Overview

{intent_data.get("purpose", "This skill provides capabilities for the corresponding slash command.")}

**When to use this skill:**
"""

    # Add use cases
    use_cases = intent_data.get("use_cases", [])
    if use_cases:
        for use_case in use_cases:
            skill_md += f"- {use_case}\n"
    else:
        skill_md += f"- When you need to execute the `/{command_name}` workflow\n"

    skill_md += "\n---\n\n# Process\n\n"

    # Add workflow steps
    workflow_steps = intent_data.get("workflow_steps", [])
    if workflow_steps:
        skill_md += "## High-Level Workflow\n\n"
        for i, step in enumerate(workflow_steps, 1):
            skill_md += f"### Step {i}: {step}\n\n"

            # Add placeholder for step details
            skill_md += f"Execute: {step}\n\n"
    else:
        skill_md += """## High-Level Workflow

### Step 1: Preparation

Gather necessary inputs and context.

### Step 2: Execution

Execute the main workflow.

### Step 3: Validation

Verify results and provide feedback.

"""

    # Add key concepts section
    key_concepts = intent_data.get("key_concepts", [])
    if key_concepts:
        skill_md += "## Key Concepts\n\n"
        for concept in key_concepts:
            skill_md += f"### {concept}\n\n"
            skill_md += f"{concept} is an important aspect of this workflow.\n\n"

    # Add dependencies section
    dependencies = intent_data.get("dependencies", [])
    if dependencies:
        skill_md += "## Dependencies\n\n"
        for dep in dependencies:
            skill_md += f"- **{dep}**\n"
        skill_md += "\n"

    # Add best practices
    skill_md += """## Best Practices

### Do's
- Follow the workflow steps in order
- Validate inputs before processing
- Provide clear feedback on results

### Don'ts
- Skip validation steps
- Ignore error conditions
- Assume implicit context

"""

    # Add troubleshooting section
    skill_md += """## Troubleshooting

### Common Issues

**Issue: Workflow fails to execute**
- Verify all dependencies are available
- Check input parameters are valid
- Review error messages for specific guidance

**Issue: Unexpected results**
- Validate input data format
- Check for conflicting configurations
- Review workflow logs for details

"""

    # Add related resources
    skill_md += f"""## Related Resources

### Slash Command

This skill corresponds to the `/{command_name}` slash command.

**Command Documentation:** [.claude/commands/{command_name}.md](.claude/commands/{command_name}.md)

### Additional Documentation

For more information, consult:
- Skill source: `.claude/skills/{command_name}/SKILL.md`
- Command source: `.claude/commands/{command_name}.md`

---

## Success Criteria

You've successfully used this skill when:

- [ ] All workflow steps completed without errors
- [ ] Results meet expected quality standards
- [ ] Validation checks pass
- [ ] Output is properly formatted and actionable

---

**Note:** This skill was auto-generated from the `/{command_name}` command using Thoughtbox reasoning.
Review and refine as needed for your specific use case.
"""

    # Create skill directory
    skill_dir = Path(output_dir) / command_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    skill_file = skill_dir / "SKILL.md"

    try:
        with open(skill_file, 'w') as f:
            f.write(skill_md)

        if verbose:
            print(f"✅ Generated skill: {skill_file}")

        return True

    except Exception as e:
        if verbose:
            print(f"❌ Failed to generate skill: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate skill from command using Thoughtbox intent"
    )
    parser.add_argument(
        "--command",
        required=True,
        help="Path to command .md file"
    )
    parser.add_argument(
        "--intent",
        required=True,
        help="Path to Thoughtbox intent JSON file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for generated skill"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Load intent data
    with open(args.intent, 'r') as f:
        intent_data = json.load(f)

    # Generate skill
    success = generate_skill_from_command(
        args.command,
        intent_data,
        args.output_dir,
        args.verbose
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
