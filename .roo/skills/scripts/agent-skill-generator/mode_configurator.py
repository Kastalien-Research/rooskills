"""
Mode Configurator Module - Manages .roomodes integration and validation.
Registers skills as modes in the .roomodes configuration file.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .schemas import (
    ModeRegistrationResult,
    ValidationReport,
    SkillMetadata
)

logger = logging.getLogger(__name__)


class ModeConfigurator:
    """
    Manages .roomodes integration and validation.
    
    Handles reading, updating, and validating the .roomodes JSON file
    to register new skills as modes.
    """
    
    def __init__(self, roomodes_path: str = ".roomodes"):
        """
        Initialize configurator.
        
        Args:
            roomodes_path: Path to .roomodes file
        """
        self.roomodes_path = Path(roomodes_path)
    
    def _read_roomodes(self) -> Dict[str, Any]:
        """
        Read current .roomodes configuration.
        
        Returns:
            Parsed .roomodes JSON
            
        Raises:
            FileNotFoundError: If .roomodes doesn't exist
            json.JSONDecodeError: If .roomodes is invalid JSON
        """
        if not self.roomodes_path.exists():
            raise FileNotFoundError(f".roomodes file not found at {self.roomodes_path}")
        
        with open(self.roomodes_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_roomodes(self, config: Dict[str, Any]) -> None:
        """
        Write updated .roomodes configuration.
        
        Args:
            config: Complete .roomodes configuration
        """
        with open(self.roomodes_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated {self.roomodes_path}")
    
    def _check_duplicate_slug(self, config: Dict[str, Any], slug: str) -> bool:
        """
        Check if slug already exists in configuration.
        
        Args:
            config: Current .roomodes configuration
            slug: Proposed mode slug
            
        Returns:
            True if duplicate exists, False otherwise
        """
        custom_modes = config.get("customModes", [])
        return any(mode.get("slug") == slug for mode in custom_modes)
    
    def _validate_yaml_frontmatter(self, skill_path: str) -> bool:
        """
        Validate SKILL.md frontmatter exists and is valid.
        
        Args:
            skill_path: Path to SKILL.md file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            if not content.startswith('---'):
                return False
            
            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return False
            
            frontmatter = parts[1]
            
            # Check for required fields
            required_fields = ['name:', 'description:']
            return all(field in frontmatter for field in required_fields)
        
        except Exception as e:
            logger.error(f"Error validating frontmatter: {e}")
            return False
    
    def _check_file_size(self, skill_path: str, max_lines: int = 500) -> bool:
        """
        Check if SKILL.md file size is within limits.
        
        Args:
            skill_path: Path to SKILL.md file
            max_lines: Maximum allowed lines
            
        Returns:
            True if within limits, False otherwise
        """
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            
            return line_count <= max_lines
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            return False
    
    def validate_integration(
        self,
        skill_name: str,
        skill_path: str
    ) -> ValidationReport:
        """
        Run comprehensive validation checks.
        
        Checks:
        - SKILL.md exists at path
        - YAML frontmatter valid
        - No duplicate slugs
        - File size < 500 lines
        
        Args:
            skill_name: Skill name/slug
            skill_path: Path to SKILL.md
            
        Returns:
            ValidationReport with all check results
        """
        logger.info(f"Validating integration for {skill_name}")
        
        checks = {}
        warnings = []
        errors = []
        
        # Check if SKILL.md exists
        skill_file = Path(skill_path)
        checks["skill_file_exists"] = skill_file.exists()
        if not checks["skill_file_exists"]:
            errors.append(f"SKILL.md not found at {skill_path}")
        
        # Check YAML frontmatter
        if checks["skill_file_exists"]:
            checks["valid_frontmatter"] = self._validate_yaml_frontmatter(skill_path)
            if not checks["valid_frontmatter"]:
                errors.append("Invalid or missing YAML frontmatter in SKILL.md")
        
        # Check for duplicate slug
        try:
            config = self._read_roomodes()
            checks["no_duplicate_slug"] = not self._check_duplicate_slug(
                config, skill_name
            )
            if not checks["no_duplicate_slug"]:
                errors.append(f"Slug '{skill_name}' already exists in .roomodes")
        except Exception as e:
            checks["no_duplicate_slug"] = False
            errors.append(f"Failed to read .roomodes: {e}")
        
        # Check file size
        if checks["skill_file_exists"]:
            checks["file_size_ok"] = self._check_file_size(skill_path)
            if not checks["file_size_ok"]:
                warnings.append("SKILL.md exceeds 500 lines - consider moving content to references/")
        
        all_checks_passed = all(checks.values()) and len(errors) == 0
        
        return ValidationReport(
            all_checks_passed=all_checks_passed,
            checks=checks,
            warnings=warnings,
            errors=errors
        )
    
    def register_mode(
        self,
        skill_name: str,
        skill_path: str,
        role_definition: str,
        groups: List[str],
        custom_instructions: Optional[str] = None
    ) -> ModeRegistrationResult:
        """
        Add mode entry to .roomodes.
        
        Args:
            skill_name: Mode slug (kebab-case)
            skill_path: Path to SKILL.md (relative to project root)
            role_definition: Brief role description
            groups: List of permission groups (e.g., ["read", "edit"])
            custom_instructions: Optional custom instructions
            
        Returns:
            ModeRegistrationResult with validation status
        """
        logger.info(f"Registering mode: {skill_name}")
        
        # Validate before registration
        validation = self.validate_integration(skill_name, skill_path)
        
        if not validation.all_checks_passed:
            return ModeRegistrationResult(
                success=False,
                slug=skill_name,
                validation_report=validation,
                error="Validation failed - see validation report"
            )
        
        try:
            # Read current configuration
            config = self._read_roomodes()
            
            # Create new mode entry
            new_mode = {
                "slug": skill_name,
                "name": f"🎯 {skill_name.replace('-', ' ').title()}",
                "roleDefinition": role_definition,
                "skill_ref": {
                    "path": skill_path,
                    "merge_strategy": "override"
                },
                "groups": groups,
                "source": "project"
            }
            
            # Add custom instructions if provided
            if custom_instructions:
                new_mode["customInstructions"] = custom_instructions
            
            # Add to custom modes
            if "customModes" not in config:
                config["customModes"] = []
            
            config["customModes"].append(new_mode)
            
            # Write updated configuration
            self._write_roomodes(config)
            
            return ModeRegistrationResult(
                success=True,
                slug=skill_name,
                validation_report=validation
            )
        
        except Exception as e:
            logger.error(f"Failed to register mode: {e}")
            return ModeRegistrationResult(
                success=False,
                slug=skill_name,
                validation_report=validation,
                error=str(e)
            )