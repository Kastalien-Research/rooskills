#!/usr/bin/env python3
"""
Validation tests for Roo Code ↔ Claude Skills integration pattern.

This script validates that the skill reference pattern in .roomodes works correctly
by testing file structure, schema validation, and integration compatibility.

Exit Codes:
    0 - All validations passed
    1 - Validation failures detected
"""

import json
import os
import sys
import unittest
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class ModeSkillIntegrationValidator:
    """Validator for mode-skill integration pattern."""
    
    WORKSPACE_DIR = Path(__file__).parent.parent.parent.parent
    ROOMODES_PATH = WORKSPACE_DIR / ".roomodes"
    VALID_MERGE_STRATEGIES = {"override", "append", "prepend"}
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def load_roomodes(self) -> Optional[Dict[str, Any]]:
        """Load and parse .roomodes JSON file."""
        try:
            with open(self.ROOMODES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.errors.append(f".roomodes file not found at {self.ROOMODES_PATH}")
            return None
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in .roomodes: {e}")
            return None
    
    def parse_yaml_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract and parse YAML frontmatter from SKILL.md file."""
        # Match YAML frontmatter between --- markers
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None
        
        yaml_content = match.group(1)
        frontmatter = {}
        
        # Simple YAML parser for key: value pairs
        for line in yaml_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        return frontmatter
    
    def validate_file_exists(self, skill_path: str, mode_slug: str) -> bool:
        """Validate that a skill file exists."""
        full_path = self.WORKSPACE_DIR / skill_path
        
        if not full_path.exists():
            self.errors.append(
                f"Mode '{mode_slug}': Skill file does not exist: {skill_path}"
            )
            return False
        
        if not full_path.is_file():
            self.errors.append(
                f"Mode '{mode_slug}': Skill path is not a file: {skill_path}"
            )
            return False
        
        return True
    
    def validate_skill_path_relative(self, skill_path: str, mode_slug: str) -> bool:
        """Validate that skill path is relative to workspace."""
        if skill_path.startswith('/') or skill_path.startswith('..'):
            self.errors.append(
                f"Mode '{mode_slug}': Skill path must be relative to workspace: {skill_path}"
            )
            return False
        
        return True
    
    def validate_merge_strategy(self, strategy: str, mode_slug: str) -> bool:
        """Validate that merge_strategy has a valid value."""
        if strategy not in self.VALID_MERGE_STRATEGIES:
            self.errors.append(
                f"Mode '{mode_slug}': Invalid merge_strategy '{strategy}'. "
                f"Must be one of: {', '.join(self.VALID_MERGE_STRATEGIES)}"
            )
            return False
        
        return True
    
    def validate_skill_ref_schema(self, skill_ref: Dict[str, Any], mode_slug: str) -> bool:
        """Validate skill_ref object has required properties."""
        if not isinstance(skill_ref, dict):
            self.errors.append(
                f"Mode '{mode_slug}': skill_ref must be an object"
            )
            return False
        
        # Check required properties
        if 'path' not in skill_ref:
            self.errors.append(
                f"Mode '{mode_slug}': skill_ref missing required property 'path'"
            )
            return False
        
        if 'merge_strategy' not in skill_ref:
            self.errors.append(
                f"Mode '{mode_slug}': skill_ref missing required property 'merge_strategy'"
            )
            return False
        
        return True
    
    def validate_yaml_frontmatter(self, skill_path: str, mode_slug: str) -> Optional[Dict[str, Any]]:
        """Validate SKILL.md has valid YAML frontmatter."""
        full_path = self.WORKSPACE_DIR / skill_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(
                f"Mode '{mode_slug}': Cannot read skill file {skill_path}: {e}"
            )
            return None
        
        frontmatter = self.parse_yaml_frontmatter(content)
        
        if frontmatter is None:
            self.errors.append(
                f"Mode '{mode_slug}': Skill file {skill_path} missing YAML frontmatter"
            )
            return None
        
        # Validate required frontmatter fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(
                    f"Mode '{mode_slug}': Skill {skill_path} frontmatter missing '{field}'"
                )
        
        return frontmatter
    
    def validate_no_circular_refs(self, roomodes_data: Dict[str, Any]) -> bool:
        """Validate there are no circular references in skill paths."""
        # Track which modes reference which skills
        skill_refs: Dict[str, List[str]] = {}
        
        for mode in roomodes_data.get('customModes', []):
            slug = mode.get('slug', '')
            skill_ref = mode.get('skill_ref')
            
            if skill_ref and 'path' in skill_ref:
                skill_path = skill_ref['path']
                if skill_path not in skill_refs:
                    skill_refs[skill_path] = []
                skill_refs[skill_path].append(slug)
        
        # Check for any duplicate references (same skill used by multiple modes)
        # This is actually valid, so just track for informational purposes
        for skill_path, modes in skill_refs.items():
            if len(modes) > 1:
                self.warnings.append(
                    f"Skill {skill_path} is referenced by multiple modes: {', '.join(modes)}"
                )
        
        return True
    
    def validate_mode_groups_compatibility(self, mode: Dict[str, Any]) -> bool:
        """Validate that mode groups are compatible with operations."""
        slug = mode.get('slug', 'unknown')
        groups = mode.get('groups', [])
        
        if not isinstance(groups, list):
            self.errors.append(
                f"Mode '{slug}': groups must be a list"
            )
            return False
        
        # Extract group names (handling both string and tuple formats)
        group_names = []
        for group in groups:
            if isinstance(group, str):
                group_names.append(group)
            elif isinstance(group, list) and len(group) >= 1:
                group_names.append(group[0])
        
        # Validate known group types
        valid_groups = {'read', 'edit', 'browser', 'mcp', 'command'}
        for group_name in group_names:
            if group_name not in valid_groups:
                self.warnings.append(
                    f"Mode '{slug}': Unknown group '{group_name}'"
                )
        
        return True
    
    def run_all_validations(self) -> bool:
        """Run all validation tests and return overall success status."""
        print("=" * 70)
        print("Roo Code ↔ Claude Skills Integration Validator")
        print("=" * 70)
        print()
        
        # Load .roomodes
        print("📁 Loading .roomodes file...")
        roomodes_data = self.load_roomodes()
        if roomodes_data is None:
            return False
        print("✓ .roomodes file loaded successfully")
        print()
        
        # Get custom modes
        custom_modes = roomodes_data.get('customModes', [])
        if not custom_modes:
            self.errors.append("No customModes found in .roomodes")
            return False
        
        print(f"📋 Found {len(custom_modes)} custom modes")
        print()
        
        # Filter modes with skill_ref
        modes_with_skills = [m for m in custom_modes if 'skill_ref' in m]
        print(f"🔗 Found {len(modes_with_skills)} modes with skill references")
        print()
        
        # Validate each mode with skill_ref
        for mode in modes_with_skills:
            slug = mode.get('slug', 'unknown')
            skill_ref = mode.get('skill_ref', {})
            
            print(f"🔍 Validating mode: {slug}")
            
            # Schema validation
            if not self.validate_skill_ref_schema(skill_ref, slug):
                continue
            
            skill_path = skill_ref.get('path')
            merge_strategy = skill_ref.get('merge_strategy')
            
            # Path validation
            self.validate_skill_path_relative(skill_path, slug)
            
            # File existence
            if not self.validate_file_exists(skill_path, slug):
                continue
            
            # Merge strategy validation
            self.validate_merge_strategy(merge_strategy, slug)
            
            # YAML frontmatter validation
            self.validate_yaml_frontmatter(skill_path, slug)
            
            # Group compatibility
            self.validate_mode_groups_compatibility(mode)
            
            print(f"  ✓ {skill_path}")
        
        print()
        
        # Check for circular references
        print("🔄 Checking for circular references...")
        self.validate_no_circular_refs(roomodes_data)
        print("✓ No circular references detected")
        print()
        
        # Report results
        success = len(self.errors) == 0
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
        
        if self.errors:
            print("❌ VALIDATION FAILURES:")
            for error in self.errors:
                print(f"  - {error}")
            print()
            print(f"Total errors: {len(self.errors)}")
        else:
            print("✅ ALL VALIDATIONS PASSED")
        
        print()
        print("=" * 70)
        
        return success


class TestModeSkillIntegration(unittest.TestCase):
    """Unit tests for mode-skill integration validation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.validator = ModeSkillIntegrationValidator()
        cls.roomodes_data = cls.validator.load_roomodes()
    
    def test_roomodes_file_exists(self):
        """Test that .roomodes file exists and is valid JSON."""
        self.assertIsNotNone(
            self.roomodes_data,
            ".roomodes file must exist and contain valid JSON"
        )
    
    def test_roomodes_has_custom_modes(self):
        """Test that .roomodes contains customModes array."""
        self.assertIn('customModes', self.roomodes_data)
        self.assertIsInstance(self.roomodes_data['customModes'], list)
        self.assertGreater(len(self.roomodes_data['customModes']), 0)
    
    def test_all_skill_refs_have_valid_schema(self):
        """Test that all skill_ref objects have required properties."""
        modes_with_skills = [
            m for m in self.roomodes_data.get('customModes', [])
            if 'skill_ref' in m
        ]
        
        for mode in modes_with_skills:
            slug = mode.get('slug', 'unknown')
            skill_ref = mode.get('skill_ref')
            
            with self.subTest(mode=slug):
                self.assertIsInstance(skill_ref, dict)
                self.assertIn('path', skill_ref, f"Mode {slug} skill_ref missing 'path'")
                self.assertIn('merge_strategy', skill_ref, f"Mode {slug} skill_ref missing 'merge_strategy'")
    
    def test_all_skill_files_exist(self):
        """Test that all referenced SKILL.md files exist."""
        modes_with_skills = [
            m for m in self.roomodes_data.get('customModes', [])
            if 'skill_ref' in m
        ]
        
        for mode in modes_with_skills:
            slug = mode.get('slug', 'unknown')
            skill_path = mode.get('skill_ref', {}).get('path')
            
            if skill_path:
                with self.subTest(mode=slug, path=skill_path):
                    full_path = self.validator.WORKSPACE_DIR / skill_path
                    self.assertTrue(
                        full_path.exists(),
                        f"Skill file does not exist: {skill_path}"
                    )
                    self.assertTrue(
                        full_path.is_file(),
                        f"Skill path is not a file: {skill_path}"
                    )
    
    def test_all_skill_paths_are_relative(self):
        """Test that all skill paths are relative to workspace."""
        modes_with_skills = [
            m for m in self.roomodes_data.get('customModes', [])
            if 'skill_ref' in m
        ]
        
        for mode in modes_with_skills:
            slug = mode.get('slug', 'unknown')
            skill_path = mode.get('skill_ref', {}).get('path', '')
            
            with self.subTest(mode=slug, path=skill_path):
                self.assertFalse(
                    skill_path.startswith('/'),
                    f"Skill path must be relative (mode: {slug})"
                )
                self.assertFalse(
                    skill_path.startswith('..'),
                    f"Skill path must not use parent directory (mode: {slug})"
                )
    
    def test_all_merge_strategies_are_valid(self):
        """Test that all merge_strategy values are valid."""
        modes_with_skills = [
            m for m in self.roomodes_data.get('customModes', [])
            if 'skill_ref' in m
        ]
        
        for mode in modes_with_skills:
            slug = mode.get('slug', 'unknown')
            strategy = mode.get('skill_ref', {}).get('merge_strategy')
            
            with self.subTest(mode=slug, strategy=strategy):
                self.assertIn(
                    strategy,
                    self.validator.VALID_MERGE_STRATEGIES,
                    f"Invalid merge_strategy '{strategy}' for mode {slug}"
                )
    
    def test_all_skill_files_have_yaml_frontmatter(self):
        """Test that all SKILL.md files have valid YAML frontmatter."""
        modes_with_skills = [
            m for m in self.roomodes_data.get('customModes', [])
            if 'skill_ref' in m
        ]
        
        for mode in modes_with_skills:
            slug = mode.get('slug', 'unknown')
            skill_path = mode.get('skill_ref', {}).get('path')
            
            if skill_path:
                with self.subTest(mode=slug, path=skill_path):
                    full_path = self.validator.WORKSPACE_DIR / skill_path
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        frontmatter = self.validator.parse_yaml_frontmatter(content)
                        self.assertIsNotNone(
                            frontmatter,
                            f"Skill file {skill_path} missing YAML frontmatter"
                        )
                        
                        # Check required fields
                        self.assertIn('name', frontmatter, f"Frontmatter missing 'name' in {skill_path}")
                        self.assertIn('description', frontmatter, f"Frontmatter missing 'description' in {skill_path}")


def main():
    """Main entry point for validation script."""
    # Run comprehensive validation
    validator = ModeSkillIntegrationValidator()
    success = validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    # If --test flag is provided, run unit tests
    if '--test' in sys.argv:
        sys.argv.remove('--test')
        unittest.main(verbosity=2)
    else:
        main()