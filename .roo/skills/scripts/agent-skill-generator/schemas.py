"""
Data schemas for Agent Skill Generator.
Defines Pydantic models for data validation and type safety.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, HttpUrl


class KnowledgeBundle(BaseModel):
    """Structured documentation knowledge from website scraping."""
    
    llms_txt: str = Field(description="Index with summaries")
    llms_full_txt: str = Field(description="Complete content")
    source_url: str = Field(description="Original documentation URL")
    page_count: int = Field(description="Number of pages processed")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WisdomDocument(BaseModel):
    """Ecosystem research insights from Claude + Exa."""
    
    overview: str = Field(description="2-3 paragraph synthesis")
    ecosystem_position: Dict[str, List[str]] = Field(
        description="category, alternatives, complements"
    )
    use_cases: List[str] = Field(default_factory=list)
    integration_patterns: Dict[str, List[str]] = Field(default_factory=dict)
    best_practices: List[str] = Field(default_factory=list)
    common_pitfalls: List[str] = Field(default_factory=list)
    sources: List[str] = Field(
        default_factory=list,
        description="Research URLs"
    )


class SkillMetadata(BaseModel):
    """YAML frontmatter data for SKILL.md."""
    
    name: str = Field(description="Skill identifier (kebab-case)")
    description: str = Field(description="When to use this skill")
    license: str = Field(default="Complete terms in LICENSE.txt")
    source_url: Optional[str] = None
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    generator_version: str = Field(default="1.0.0")
    compatible_modes: List[str] = Field(default_factory=list)
    required_groups: List[str] = Field(default_factory=list)


class ReferenceFile(BaseModel):
    """Reference documentation file."""
    
    filename: str
    content: str
    description: Optional[str] = None


class AssetFile(BaseModel):
    """Asset file (templates, configs, etc.)."""
    
    filename: str
    content: bytes
    description: Optional[str] = None


class SkillBundle(BaseModel):
    """Complete skill package."""
    
    skill_md: str = Field(description="Main SKILL.md content")
    references: List[ReferenceFile] = Field(default_factory=list)
    assets: List[AssetFile] = Field(default_factory=list)
    metadata: SkillMetadata


class ValidationReport(BaseModel):
    """Validation check results."""
    
    all_checks_passed: bool
    checks: Dict[str, bool] = Field(description="check_name -> passed")
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ModeRegistrationResult(BaseModel):
    """Result of .roomodes integration."""
    
    success: bool
    slug: str
    validation_report: ValidationReport
    error: Optional[str] = None


class SkillGenerationResult(BaseModel):
    """Final result of complete skill generation."""
    
    success: bool
    skill_path: str
    mode_slug: str
    validation_report: ValidationReport
    knowledge_bundle: Optional[KnowledgeBundle] = None
    wisdom_document: Optional[WisdomDocument] = None
    error: Optional[str] = None


class ScrapedPage(BaseModel):
    """Single scraped page data."""
    
    url: str
    title: str
    description: str
    markdown: str
    index: int


class ResearchPhaseResult(BaseModel):
    """Result from a single research phase."""
    
    phase_name: str
    findings: str
    sources: List[str] = Field(default_factory=list)