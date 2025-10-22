#!/usr/bin/env python3
"""
Discovery Module - Scan commands and skills directories to identify synchronization gaps.

This module identifies:
- Commands without corresponding skills
- Skills without corresponding commands
- Total synchronization work needed
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Set, Dict
from dataclasses import dataclass, asdict


@dataclass
class SyncDiscovery:
    """Results of discovery phase."""
    commands: List[str]
    skills: List[str]
    commands_without_skills: List[str]
    skills_without_commands: List[str]
    total_gaps: int


def discover_commands(commands_dir: Path) -> Set[str]:
    """
    Scan commands directory for .md files.

    Args:
        commands_dir: Path to commands directory (e.g., .claude/commands/)

    Returns:
        Set of command names (without .md extension)
    """
    commands = set()

    if not commands_dir.exists():
        return commands

    for file_path in commands_dir.glob("*.md"):
        command_name = file_path.stem  # Remove .md extension
        commands.add(command_name)

    return commands


def discover_skills(skills_dir: Path) -> Set[str]:
    """
    Scan skills directory for SKILL.md files.

    Args:
        skills_dir: Path to skills directory (e.g., .claude/skills/)

    Returns:
        Set of skill names (directory names containing SKILL.md)
    """
    skills = set()

    if not skills_dir.exists():
        return skills

    # Find all SKILL.md files
    for skill_file in skills_dir.glob("*/SKILL.md"):
        skill_name = skill_file.parent.name
        # Exclude template and special directories
        if skill_name not in ["template-skill", "scripts", "architecture"]:
            skills.add(skill_name)

    return skills


def compute_gaps(commands: Set[str], skills: Set[str]) -> SyncDiscovery:
    """
    Compute synchronization gaps between commands and skills.

    Args:
        commands: Set of command names
        skills: Set of skill names

    Returns:
        SyncDiscovery with gap analysis
    """
    commands_without_skills = sorted(commands - skills)
    skills_without_commands = sorted(skills - commands)
    total_gaps = len(commands_without_skills) + len(skills_without_commands)

    return SyncDiscovery(
        commands=sorted(commands),
        skills=sorted(skills),
        commands_without_skills=commands_without_skills,
        skills_without_commands=skills_without_commands,
        total_gaps=total_gaps
    )


def discover(commands_dir: str, skills_dir: str) -> SyncDiscovery:
    """
    Discover synchronization gaps between commands and skills.

    Args:
        commands_dir: Path to commands directory
        skills_dir: Path to skills directory

    Returns:
        SyncDiscovery with complete gap analysis
    """
    commands_path = Path(commands_dir)
    skills_path = Path(skills_dir)

    # Discover what exists
    commands = discover_commands(commands_path)
    skills = discover_skills(skills_path)

    # Compute gaps
    discovery = compute_gaps(commands, skills)

    return discovery


def main():
    parser = argparse.ArgumentParser(
        description="Discover synchronization gaps between commands and skills"
    )
    parser.add_argument(
        "--commands",
        default=".claude/commands",
        help="Path to commands directory (default: .claude/commands)"
    )
    parser.add_argument(
        "--skills",
        default=".claude/skills",
        help="Path to skills directory (default: .claude/skills)"
    )
    parser.add_argument(
        "--output",
        help="Output file for JSON results (default: stdout)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Run discovery
    discovery = discover(args.commands, args.skills)

    # Convert to JSON
    result_json = json.dumps(asdict(discovery), indent=2)

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result_json)
        if args.verbose:
            print(f"✅ Discovery results written to {args.output}")
    else:
        print(result_json)

    # Verbose summary
    if args.verbose:
        print("\n📊 Discovery Summary:")
        print(f"   Commands found: {len(discovery.commands)}")
        print(f"   Skills found: {len(discovery.skills)}")
        print(f"   Commands without skills: {len(discovery.commands_without_skills)}")
        print(f"   Skills without commands: {len(discovery.skills_without_commands)}")
        print(f"   Total gaps: {discovery.total_gaps}")

        if discovery.commands_without_skills:
            print(f"\n   Commands needing skills:")
            for cmd in discovery.commands_without_skills:
                print(f"      - {cmd}")

        if discovery.skills_without_commands:
            print(f"\n   Skills needing commands:")
            for skill in discovery.skills_without_commands:
                print(f"      - {skill}")


if __name__ == "__main__":
    main()
