#!/usr/bin/env python3
"""
Sync Orchestrator - Main coordinator for bidirectional command-skill synchronization.

This module orchestrates all phases:
- Phase 0: Discovery
- Phase 1: Thoughtbox reasoning
- Phase 2: Parallel generation
- Phase 3: Validation
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict

# Import our modules
from discovery import discover, SyncDiscovery
from thoughtbox_client import ThoughtboxClient, Intent
from command_generator import generate_command_from_skill
from skill_generator import generate_skill_from_command


@dataclass
class SyncResult:
    """Results of synchronization."""
    skills_created: int
    commands_created: int
    total_synced: int
    errors: List[str]
    success: bool


class SyncOrchestrator:
    """Orchestrates the complete sync workflow."""

    def __init__(
        self,
        commands_dir: str = ".claude/commands",
        skills_dir: str = ".claude/skills",
        parallel: int = 3,
        dry_run: bool = False,
        verbose: bool = False
    ):
        """
        Initialize orchestrator.

        Args:
            commands_dir: Path to commands directory
            skills_dir: Path to skills directory
            parallel: Maximum concurrent subagents
            dry_run: If True, don't create files
            verbose: Enable detailed logging
        """
        self.commands_dir = commands_dir
        self.skills_dir = skills_dir
        self.parallel = parallel
        self.dry_run = dry_run
        self.verbose = verbose

        # Try to initialize Thoughtbox, but don't fail if unavailable
        try:
            self.thoughtbox = ThoughtboxClient()
            self.use_thoughtbox = True
        except Exception as e:
            self.log(f"⚠️  Thoughtbox not available: {e}")
            self.log("   Using fallback template-based generation")
            self.thoughtbox = None
            self.use_thoughtbox = False

        self.temp_dir = Path(".sync-temp")

    def log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)

    async def phase_0_discovery(self) -> SyncDiscovery:
        """
        Phase 0: Discover synchronization gaps.

        Returns:
            SyncDiscovery with gap analysis
        """
        print("\n═══════════════════════════════════════")
        print("Phase 0: Discovery")
        print("═══════════════════════════════════════\n")

        discovery = discover(self.commands_dir, self.skills_dir)

        print("📊 Discovery Results:")
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

        return discovery

    async def phase_1_reasoning(self, discovery: SyncDiscovery) -> Dict[str, Intent]:
        """
        Phase 1: Use Thoughtbox to analyze intent.

        Args:
            discovery: Gap analysis from Phase 0

        Returns:
            Dictionary mapping names to Intent objects
        """
        print("\n═══════════════════════════════════════")
        print("Phase 1: Thoughtbox Reasoning")
        print("═══════════════════════════════════════\n")

        intents = {}
        self.temp_dir.mkdir(exist_ok=True)
        intents_dir = self.temp_dir / "intents"
        intents_dir.mkdir(exist_ok=True)

        # Analyze commands
        for cmd in discovery.commands_without_skills:
            print(f"🧠 Analyzing command: {cmd}")
            cmd_path = Path(self.commands_dir) / f"{cmd}.md"

            try:
                with open(cmd_path, 'r') as f:
                    content = f.read()

                intent = await self.thoughtbox.analyze_command(content, cmd)
                intents[cmd] = intent

                # Save intent
                intent_file = intents_dir / f"{cmd}-intent.json"
                with open(intent_file, 'w') as f:
                    json.dump(asdict(intent), f, indent=2)

                self.log(f"   ✓ Intent saved: {intent_file}")

            except Exception as e:
                print(f"   ⚠️  Failed to analyze {cmd}: {e}")
                # Create fallback intent
                intents[cmd] = Intent(
                    name=cmd,
                    type="command",
                    purpose=f"Execute {cmd} workflow",
                    use_cases=[f"When using /{cmd} command"],
                    key_concepts=[],
                    workflow_steps=[],
                    dependencies=[],
                    suggested_structure={}
                )

        # Analyze skills
        for skill in discovery.skills_without_commands:
            print(f"🧠 Analyzing skill: {skill}")
            skill_path = Path(self.skills_dir) / skill / "SKILL.md"

            try:
                with open(skill_path, 'r') as f:
                    content = f.read()

                intent = await self.thoughtbox.analyze_skill(content, skill)
                intents[skill] = intent

                # Save intent
                intent_file = intents_dir / f"{skill}-intent.json"
                with open(intent_file, 'w') as f:
                    json.dump(asdict(intent), f, indent=2)

                self.log(f"   ✓ Intent saved: {intent_file}")

            except Exception as e:
                print(f"   ⚠️  Failed to analyze {skill}: {e}")
                # Create fallback intent
                intents[skill] = Intent(
                    name=skill,
                    type="skill",
                    purpose=f"Skill for {skill}",
                    use_cases=[f"When working with {skill}"],
                    key_concepts=[],
                    workflow_steps=[],
                    dependencies=[],
                    suggested_structure={}
                )

        print(f"\n✅ Thoughtbox reasoning complete for {len(intents)} items")
        return intents

    async def phase_2_generation(
        self,
        discovery: SyncDiscovery,
        intents: Dict[str, Intent]
    ) -> SyncResult:
        """
        Phase 2: Generate missing items with parallel subagents.

        Args:
            discovery: Gap analysis
            intents: Intent analysis for each item

        Returns:
            SyncResult with generation statistics
        """
        print("\n═══════════════════════════════════════")
        print("Phase 2: Parallel Generation")
        print("═══════════════════════════════════════\n")

        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be created\n")

        skills_created = 0
        commands_created = 0
        errors = []

        # Generate skills from commands
        print(f"🚀 Generating {len(discovery.commands_without_skills)} skills...")

        for cmd in discovery.commands_without_skills:
            print(f"   Generating skill for: {cmd}")

            if self.dry_run:
                print(f"      [DRY RUN] Would create: .claude/skills/{cmd}/SKILL.md")
                skills_created += 1
                continue

            try:
                cmd_path = Path(self.commands_dir) / f"{cmd}.md"
                intent = intents.get(cmd)
                intent_data = asdict(intent) if intent else {}

                success = generate_skill_from_command(
                    str(cmd_path),
                    intent_data,
                    self.skills_dir,
                    self.verbose
                )

                if success:
                    skills_created += 1
                    print(f"      ✅ Created: .claude/skills/{cmd}/SKILL.md")
                else:
                    errors.append(f"Failed to create skill for {cmd}")
                    print(f"      ❌ Failed")

            except Exception as e:
                errors.append(f"Error creating skill for {cmd}: {e}")
                print(f"      ❌ Error: {e}")

        # Generate commands from skills
        print(f"\n🚀 Generating {len(discovery.skills_without_commands)} commands...")

        for skill in discovery.skills_without_commands:
            print(f"   Generating command for: {skill}")

            if self.dry_run:
                print(f"      [DRY RUN] Would create: .claude/commands/{skill}.md")
                commands_created += 1
                continue

            try:
                skill_path = Path(self.skills_dir) / skill / "SKILL.md"
                cmd_output = Path(self.commands_dir) / f"{skill}.md"
                intent = intents.get(skill)
                intent_data = asdict(intent) if intent else {}

                success = generate_command_from_skill(
                    str(skill_path),
                    intent_data,
                    str(cmd_output),
                    self.verbose
                )

                if success:
                    commands_created += 1
                    print(f"      ✅ Created: .claude/commands/{skill}.md")
                else:
                    errors.append(f"Failed to create command for {skill}")
                    print(f"      ❌ Failed")

            except Exception as e:
                errors.append(f"Error creating command for {skill}: {e}")
                print(f"      ❌ Error: {e}")

        print(f"\n✅ Generation complete")
        print(f"   Skills created: {skills_created}")
        print(f"   Commands created: {commands_created}")

        return SyncResult(
            skills_created=skills_created,
            commands_created=commands_created,
            total_synced=skills_created + commands_created,
            errors=errors,
            success=len(errors) == 0
        )

    async def phase_3_validation(self, result: SyncResult):
        """
        Phase 3: Validate synchronization results.

        Args:
            result: Generation results to validate
        """
        print("\n═══════════════════════════════════════")
        print("Phase 3: Validation")
        print("═══════════════════════════════════════\n")

        if self.dry_run:
            print("🔍 DRY RUN - Skipping validation\n")
            return

        # Re-discover to verify gaps are filled
        discovery_after = discover(self.commands_dir, self.skills_dir)

        print("🔍 Validating sync results...")
        print(f"   Commands after: {len(discovery_after.commands)}")
        print(f"   Skills after: {len(discovery_after.skills)}")
        print(f"   Remaining gaps: {discovery_after.total_gaps}")

        # Validate generated files
        validation_errors = []

        for skill_dir in Path(self.skills_dir).iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skill_file = skill_dir / "SKILL.md"
                try:
                    with open(skill_file, 'r') as f:
                        content = f.read()

                    # Basic validation: check for YAML frontmatter
                    import re
                    if not re.match(r'^---\s*\n', content):
                        validation_errors.append(f"Missing frontmatter: {skill_file}")

                except Exception as e:
                    validation_errors.append(f"Error reading {skill_file}: {e}")

        if validation_errors:
            print(f"\n⚠️  Validation warnings ({len(validation_errors)}):")
            for error in validation_errors:
                print(f"   - {error}")
        else:
            print("\n✅ All validations passed")

    async def run(self) -> SyncResult:
        """
        Execute complete synchronization workflow.

        Returns:
            SyncResult with final statistics
        """
        print("\n🎯 Starting Command-Skill Synchronization")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"   Parallelism: {self.parallel}")

        # Phase 0: Discovery
        discovery = await self.phase_0_discovery()

        if discovery.total_gaps == 0:
            print("\n✅ Already synchronized - no gaps found!")
            return SyncResult(
                skills_created=0,
                commands_created=0,
                total_synced=0,
                errors=[],
                success=True
            )

        # Phase 1: Reasoning
        intents = await self.phase_1_reasoning(discovery)

        # Phase 2: Generation
        result = await self.phase_2_generation(discovery, intents)

        # Phase 3: Validation
        await self.phase_3_validation(result)

        # Final summary
        print("\n" + "="*50)
        print("✅ SYNC COMPLETE")
        print("="*50)
        print(f"\n📊 Results:")
        print(f"   Skills created: {result.skills_created}")
        print(f"   Commands created: {result.commands_created}")
        print(f"   Total synced: {result.total_synced}")

        if result.errors:
            print(f"\n⚠️  Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"   - {error}")

        print(f"\n📁 Locations:")
        print(f"   Commands: {self.commands_dir}/")
        print(f"   Skills: {self.skills_dir}/")

        if not self.dry_run:
            print(f"\n🧹 Cleanup:")
            print(f"   Temporary files: .sync-temp/ (run 'rm -rf .sync-temp' to clean)")

        return result


async def main_async(args):
    """Async main function."""
    orchestrator = SyncOrchestrator(
        commands_dir=args.commands,
        skills_dir=args.skills,
        parallel=args.parallel,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    result = await orchestrator.run()
    return 0 if result.success else 1


def main():
    parser = argparse.ArgumentParser(
        description="Synchronize commands and skills bidirectionally"
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
        "--parallel",
        type=int,
        default=3,
        help="Maximum concurrent subagents (default: 3)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
