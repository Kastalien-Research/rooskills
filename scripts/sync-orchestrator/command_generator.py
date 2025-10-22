#!/usr/bin/env python3
"""
Command Generator - Generate slash commands from skills using Thoughtbox intent.

This module creates concise, actionable command documentation from skill definitions.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict
from dataclasses import dataclass


def generate_command_from_skill(
    skill_path: str,
    intent_data: Dict,
    output_path: str,
    verbose: bool = False
) -> bool:
    """
    Generate a command markdown file from a skill using Thoughtbox intent.

    Args:
        skill_path: Path to the skill SKILL.md file
        intent_data: Intent analysis from Thoughtbox
        output_path: Where to write the generated command
        verbose: Enable detailed logging

    Returns:
        True if successful, False otherwise
    """
    skill_name = intent_data.get("name", os.path.basename(os.path.dirname(skill_path)))

    # Read skill content for context
    with open(skill_path, 'r') as f:
        skill_content = f.read()

    # Extract YAML frontmatter description if present
    import re
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', skill_content, re.DOTALL)
    description = ""
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        desc_match = re.search(r'description:\s*(.+?)(?:\n|$)', fm)
        if desc_match:
            description = desc_match.group(1).strip()

    # If no description in frontmatter, use intent purpose
    if not description:
        description = intent_data.get("purpose", f"Execute {skill_name} workflow")

    # Generate command markdown
    command_md = f"""---
description: {description}
---

**Execution Mode**: Auto-Coder

When this command is invoked, you must:
1. Switch to Auto-Coder mode (if not already)
2. Load the skill context from `.claude/skills/{skill_name}/SKILL.md`
3. Execute the workflow defined in the skill
4. Return to the original mode after completion

# /{skill_name}

{intent_data.get("purpose", "Execute the workflow for this skill")}

## Purpose

"""

    # Add use cases
    use_cases = intent_data.get("use_cases", [])
    if use_cases:
        command_md += "This command is useful when:\n"
        for use_case in use_cases:
            command_md += f"- {use_case}\n"
        command_md += "\n"

    command_md += "## Usage\n\n```\n"

    # Determine if command takes arguments based on workflow
    workflow_steps = intent_data.get("workflow_steps", [])
    if workflow_steps and any(keyword in str(workflow_steps).lower() for keyword in ['argument', 'parameter', 'input', 'specify']):
        command_md += f"/{skill_name} <arguments>\n"
    else:
        command_md += f"/{skill_name}\n"

    command_md += "```\n\n"

    # Add key concepts if they exist
    key_concepts = intent_data.get("key_concepts", [])
    if key_concepts:
        command_md += "## Key Concepts\n\n"
        for concept in key_concepts:
            command_md += f"- **{concept}**\n"
        command_md += "\n"

    # Add workflow steps if they exist
    if workflow_steps:
        command_md += "## Workflow\n\n"
        for i, step in enumerate(workflow_steps, 1):
            command_md += f"{i}. {step}\n"
        command_md += "\n"

    # Add dependencies if they exist
    dependencies = intent_data.get("dependencies", [])
    if dependencies:
        command_md += "## Dependencies\n\n"
        for dep in dependencies:
            command_md += f"- {dep}\n"
        command_md += "\n"

    # Add reference to full skill
    command_md += f"""## Related Documentation

For complete details, see the full skill documentation:
- [Skill Documentation](.claude/skills/{skill_name}/SKILL.md)

## Quick Reference

**Command:** `/{skill_name}`

**Skill Source:** `.claude/skills/{skill_name}/SKILL.md`

**Purpose:** {intent_data.get("purpose", "Execute skill workflow")}
"""

    # Write the command file
    try:
        with open(output_path, 'w') as f:
            f.write(command_md)

        if verbose:
            print(f"✅ Generated command: {output_path}")

        return True

    except Exception as e:
        if verbose:
            print(f"❌ Failed to generate command: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate command from skill using Thoughtbox intent"
    )
    parser.add_argument(
        "--skill",
        required=True,
        help="Path to skill SKILL.md file"
    )
    parser.add_argument(
        "--intent",
        required=True,
        help="Path to Thoughtbox intent JSON file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for generated command .md file"
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

    # Generate command
    success = generate_command_from_skill(
        args.skill,
        intent_data,
        args.output,
        args.verbose
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
