"""
Orchestrator - Main CLI entry point for Agent Skill Generator.
Coordinates all modules to generate complete skills from documentation URLs.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import get_settings
from .schemas import SkillGenerationResult
from .llms_generator import LLMSGenerator
from .ecosystem_researcher import EcosystemResearcher
from .skill_creator import SkillCreator
from .mode_configurator import ModeConfigurator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create CLI app
app = typer.Typer(
    name="agent-skill-generator",
    help="Generate Roo Code skills from documentation URLs"
)
console = Console()


class SkillOrchestrator:
    """Main orchestrator for skill generation pipeline."""
    
    def __init__(self):
        """Initialize orchestrator with settings and modules."""
        self.settings = get_settings()
        self.llms_generator = LLMSGenerator(self.settings)
        self.ecosystem_researcher = EcosystemResearcher(self.settings)
        self.skill_creator = SkillCreator()
        self.mode_configurator = ModeConfigurator()
    
    def generate_skill(
        self,
        url: str,
        skill_name: str,
        max_pages: int = 50,
        output_dir: Optional[Path] = None,
        groups: list[str] = None,
        skill_type: str = "coding-agent"
    ) -> SkillGenerationResult:
        """
        Orchestrate complete skill generation.

        Args:
            url: Documentation URL to process
            skill_name: Skill identifier (kebab-case)
            max_pages: Maximum pages to scrape
            output_dir: Output directory for skill files
            groups: Permission groups for mode
            skill_type: Type of skill - "coding-agent" or "domain-knowledge"

        Returns:
            SkillGenerationResult with paths and validation status
        """
        if groups is None:
            groups = ["read", "edit"]
        
        if output_dir is None:
            output_dir = Path(self.settings.output_dir) / skill_name
        
        try:
            console.print(f"\n[bold cyan]🚀 Starting skill generation for {skill_name}[/bold cyan]\n")
            
            # Phase 1: Knowledge Extraction
            console.print("[bold]Phase 1:[/bold] Extracting documentation knowledge...")
            knowledge_bundle = self.llms_generator.extract_knowledge(url, max_pages)
            console.print(f"✓ Processed {knowledge_bundle.page_count} pages\n")
            
            # Phase 2: Ecosystem Research
            console.print("[bold]Phase 2:[/bold] Researching ecosystem and best practices...")
            wisdom_document = self.ecosystem_researcher.research_ecosystem(
                skill_name,
                knowledge_bundle.llms_txt[:2000],  # Provide context
                skill_type=skill_type
            )
            console.print("✓ Research complete\n")

            # Phase 3: Skill Synthesis
            console.print("[bold]Phase 3:[/bold] Creating SKILL.md and references...")
            skill_bundle = self.skill_creator.create_skill(
                skill_name,
                knowledge_bundle,
                wisdom_document,
                compatible_modes=groups,
                skill_type=skill_type
            )
            console.print("✓ Skill synthesized\n")
            
            # Phase 4: Write Files
            console.print("[bold]Phase 4:[/bold] Writing skill files...")
            self._write_skill_files(output_dir, skill_bundle)
            console.print(f"✓ Files written to {output_dir}\n")
            
            # Phase 5: Register Mode
            console.print("[bold]Phase 5:[/bold] Registering mode in .roomodes...")
            skill_path = output_dir / "SKILL.md"
            role_definition = wisdom_document.overview[:200]
            
            registration = self.mode_configurator.register_mode(
                skill_name,
                str(skill_path),
                role_definition,
                groups
            )
            
            if registration.success:
                console.print("✓ Mode registered successfully\n")
            else:
                console.print(f"⚠ Mode registration had issues: {registration.error}\n")
            
            # Return result
            return SkillGenerationResult(
                success=True,
                skill_path=str(skill_path),
                mode_slug=skill_name,
                validation_report=registration.validation_report,
                knowledge_bundle=knowledge_bundle,
                wisdom_document=wisdom_document
            )
        
        except Exception as e:
            logger.error(f"Skill generation failed: {e}", exc_info=True)
            return SkillGenerationResult(
                success=False,
                skill_path="",
                mode_slug=skill_name,
                validation_report=None,
                error=str(e)
            )
    
    def _write_skill_files(self, output_dir: Path, skill_bundle) -> None:
        """
        Write all skill files to disk.
        
        Args:
            output_dir: Output directory
            skill_bundle: SkillBundle with all content
        """
        # Create directories
        output_dir.mkdir(parents=True, exist_ok=True)
        references_dir = output_dir / "references"
        references_dir.mkdir(exist_ok=True)
        
        # Write SKILL.md
        skill_path = output_dir / "SKILL.md"
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(skill_bundle.skill_md)
        logger.info(f"Wrote {skill_path}")
        
        # Write reference files
        for ref_file in skill_bundle.references:
            ref_path = references_dir / ref_file.filename
            with open(ref_path, 'w', encoding='utf-8') as f:
                f.write(ref_file.content)
            logger.info(f"Wrote {ref_path}")
        
        # Write LICENSE.txt
        license_path = output_dir / "LICENSE.txt"
        with open(license_path, 'w', encoding='utf-8') as f:
            f.write("MIT License\n\nComplete license terms here.\n")
        logger.info(f"Wrote {license_path}")


@app.command()
def generate(
    url: str = typer.Argument(..., help="Documentation URL to process"),
    skill_name: str = typer.Argument(..., help="Skill name in kebab-case"),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory (default: skill-name)"
    ),
    skill_type: str = typer.Option(
        "coding-agent",
        "--skill-type",
        "-t",
        help="Type of skill: coding-agent or domain-knowledge"
    ),
    max_urls: int = typer.Option(
        20,
        "--max-urls",
        "-m",
        help="Maximum number of URLs to process"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
):
    """
    Generate a Skill from documentation URL.

    Examples:
        # Generate coding agent skill
        python -m scripts.agent-skill-generator.orchestrator generate \\
            "https://cursor.com" \\
            "cursor-agent" \\
            --skill-type coding-agent \\
            --max-urls 50

        # Generate domain knowledge skill
        python -m scripts.agent-skill-generator.orchestrator generate \\
            "https://langchain-ai.github.io/langgraph/" \\
            "langgraph-expert" \\
            --skill-type domain-knowledge \\
            --max-urls 30
    """
    # Set logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate skill type
    if skill_type not in ["coding-agent", "domain-knowledge"]:
        console.print(f"[red]Error: Invalid skill type '{skill_type}'. Must be 'coding-agent' or 'domain-knowledge'[/red]")
        sys.exit(1)

    # Create orchestrator and generate skill
    orchestrator = SkillOrchestrator()

    result = orchestrator.generate_skill(
        url=url,
        skill_name=skill_name,
        max_pages=max_urls,
        output_dir=output_dir,
        skill_type=skill_type
    )
    
    # Display results
    if result.success:
        console.print("\n[bold green]✨ Skill generation complete![/bold green]\n")
        console.print(f"Skill path: [cyan]{result.skill_path}[/cyan]")
        console.print(f"Mode slug: [cyan]{result.mode_slug}[/cyan]")
        
        if result.validation_report:
            console.print("\n[bold]Validation Results:[/bold]")
            for check, passed in result.validation_report.checks.items():
                status = "✓" if passed else "✗"
                console.print(f"  {status} {check}")
            
            if result.validation_report.warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result.validation_report.warnings:
                    console.print(f"  ⚠ {warning}")
        
        sys.exit(0)
    else:
        console.print(f"\n[bold red]❌ Skill generation failed:[/bold red] {result.error}\n")
        sys.exit(1)


@app.command()
def validate(
    skill_path: Path = typer.Argument(..., help="Path to SKILL.md file")
):
    """
    Validate an existing skill integration.
    
    Example:
        python -m scripts.agent-skill-generator.orchestrator validate \\
            fastapi-developer/SKILL.md
    """
    configurator = ModeConfigurator()
    skill_name = skill_path.parent.name
    
    validation = configurator.validate_integration(skill_name, str(skill_path))
    
    console.print("\n[bold]Validation Results:[/bold]")
    for check, passed in validation.checks.items():
        status = "✓" if passed else "✗"
        color = "green" if passed else "red"
        console.print(f"  [{color}]{status} {check}[/{color}]")
    
    if validation.warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in validation.warnings:
            console.print(f"  ⚠ {warning}")
    
    if validation.errors:
        console.print("\n[red]Errors:[/red]")
        for error in validation.errors:
            console.print(f"  ✗ {error}")
    
    if validation.all_checks_passed:
        console.print("\n[bold green]✨ All checks passed![/bold green]\n")
        sys.exit(0)
    else:
        console.print("\n[bold red]❌ Validation failed[/bold red]\n")
        sys.exit(1)


if __name__ == "__main__":
    app()