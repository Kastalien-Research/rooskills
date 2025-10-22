"""
Skill Creator Module - Synthesizes SKILL.md from knowledge and wisdom.
Creates structured markdown with YAML frontmatter following Roo Code patterns.
"""

import logging
from typing import List, Optional
from datetime import datetime

from .schemas import (
    KnowledgeBundle,
    WisdomDocument,
    SkillBundle,
    SkillMetadata,
    ReferenceFile
)

logger = logging.getLogger(__name__)


class SkillCreator:
    """
    Creates SKILL.md files from knowledge and wisdom.
    
    Synthesizes documentation content with ecosystem insights to produce
    comprehensive skill definitions following Roo Code patterns.
    """
    
    def __init__(self):
        """Initialize skill creator."""
        pass
    
    def _generate_yaml_frontmatter(self, metadata: SkillMetadata) -> str:
        """
        Generate YAML frontmatter for SKILL.md.
        
        Args:
            metadata: Skill metadata
            
        Returns:
            YAML frontmatter string
        """
        return f"""---
name: {metadata.name}
description: {metadata.description}
license: {metadata.license}
---
"""
    
    def _generate_overview_section(
        self,
        skill_name: str,
        wisdom: WisdomDocument,
        skill_type: str = "coding-agent"
    ) -> str:
        """Generate the overview section."""
        if skill_type == "domain-knowledge":
            when_to_use = f"""Use this skill when:
- You need to learn or understand {skill_name.replace('-', ' ')}
- You're working on projects that involve these concepts
- You need guidance on best practices and patterns
- You want to apply these techniques effectively"""
        else:
            when_to_use = f"""Use this skill when:
- You need to work with {skill_name.replace('-', ' ')}
- You're implementing features that involve these use cases
- You need guidance on integration and automation
- You want to extend or customize the tool"""

        return f"""# {skill_name.replace('-', ' ').title()}

{wisdom.overview}

## Core Capabilities

This skill provides specialized knowledge and workflows for:

{self._format_list(wisdom.use_cases)}

## When to Use This Skill

{when_to_use}
"""
    
    def _generate_ecosystem_section(self, wisdom: WisdomDocument, skill_type: str = "coding-agent") -> str:
        """Generate ecosystem positioning section."""
        position = wisdom.ecosystem_position
        
        section = "## Ecosystem & Alternatives\n\n"
        
        if position.get("category"):
            section += f"**Category**: {', '.join(position['category'])}\n\n"
        
        if position.get("alternatives"):
            section += "**Alternatives**:\n"
            section += self._format_list(position["alternatives"]) + "\n"
        
        if position.get("complements"):
            section += "**Works well with**:\n"
            section += self._format_list(position["complements"]) + "\n"
        
        return section
    
    def _generate_integration_section(self, wisdom: WisdomDocument, skill_type: str = "coding-agent") -> str:
        """Generate integration patterns section."""
        patterns = wisdom.integration_patterns

        if skill_type == "domain-knowledge":
            section = "## Application Patterns\n\n"
            section += "### Learning and Implementation\n\n"
        else:
            section = "## Integration Patterns\n\n"
            section += "### Common Patterns\n\n"

        if patterns.get("common"):
            section += self._format_list(patterns["common"]) + "\n"

        if patterns.get("advanced"):
            if skill_type == "domain-knowledge":
                section += "### Advanced Techniques\n\n"
            else:
                section += "### Advanced Patterns\n\n"
            section += self._format_list(patterns["advanced"]) + "\n"

        return section
    
    def _generate_best_practices_section(self, wisdom: WisdomDocument, skill_type: str = "coding-agent") -> str:
        """Generate best practices section."""
        section = "## Best Practices\n\n"
        
        if wisdom.best_practices:
            section += self._format_list(wisdom.best_practices) + "\n"
        
        if wisdom.common_pitfalls:
            section += "\n### Common Pitfalls to Avoid\n\n"
            section += self._format_list(wisdom.common_pitfalls) + "\n"
        
        return section
    
    def _generate_reference_section(
        self,
        knowledge: KnowledgeBundle,
        wisdom: WisdomDocument
    ) -> str:
        """Generate references section."""
        section = "## References\n\n"
        section += f"- [Official Documentation]({knowledge.source_url})\n"
        
        if wisdom.sources:
            section += "\n### Additional Resources\n\n"
            for source in wisdom.sources:
                section += f"- {source}\n"
        
        section += "\n### Reference Files\n\n"
        section += "See the `references/` directory for:\n"
        section += "- Complete API documentation\n"
        section += "- Detailed examples\n"
        section += "- Configuration guides\n"
        
        return section
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items as markdown bullets."""
        if not items:
            return "- None specified\n"
        return "\n".join(f"- {item}" for item in items)
    
    def _extract_references(
        self,
        knowledge: KnowledgeBundle
    ) -> List[ReferenceFile]:
        """
        Extract large documentation into reference files.
        
        Args:
            knowledge: Knowledge bundle with full documentation
            
        Returns:
            List of reference files
        """
        references = []
        
        # Create a reference file for the complete documentation
        if knowledge.llms_full_txt:
            references.append(ReferenceFile(
                filename="api_documentation.md",
                content=knowledge.llms_full_txt,
                description="Complete API documentation from official sources"
            ))
        
        # Create an index reference
        if knowledge.llms_txt:
            references.append(ReferenceFile(
                filename="documentation_index.md",
                content=knowledge.llms_txt,
                description="Quick reference index of all documentation pages"
            ))
        
        return references
    
    def create_skill(
        self,
        skill_name: str,
        knowledge: KnowledgeBundle,
        wisdom: WisdomDocument,
        compatible_modes: Optional[List[str]] = None,
        skill_type: str = "coding-agent"
    ) -> SkillBundle:
        """
        Generate SKILL.md with YAML frontmatter and content.

        Args:
            skill_name: Skill identifier (kebab-case)
            knowledge: Documentation knowledge bundle
            wisdom: Ecosystem research wisdom
            compatible_modes: List of compatible mode slugs
            skill_type: Type of skill - "coding-agent" or "domain-knowledge"

        Returns:
            SkillBundle with skill_md, references, and metadata
        """
        logger.info(f"Creating skill: {skill_name}")
        
        # Create metadata
        metadata = SkillMetadata(
            name=skill_name,
            description=wisdom.overview[:200] + "...",
            source_url=knowledge.source_url,
            compatible_modes=compatible_modes or ["read", "edit"],
            required_groups=["read", "edit"]
        )
        
        # Generate SKILL.md content
        sections = [
            self._generate_yaml_frontmatter(metadata),
            self._generate_overview_section(skill_name, wisdom, skill_type),
            self._generate_ecosystem_section(wisdom, skill_type),
            self._generate_integration_section(wisdom, skill_type),
            self._generate_best_practices_section(wisdom, skill_type),
            self._generate_reference_section(knowledge, wisdom)
        ]
        
        skill_md = "\n".join(sections)
        
        # Extract references
        references = self._extract_references(knowledge)
        
        return SkillBundle(
            skill_md=skill_md,
            references=references,
            assets=[],
            metadata=metadata
        )