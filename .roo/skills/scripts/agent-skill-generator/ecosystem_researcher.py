"""
Ecosystem Researcher Module - Deep research using Claude + Exa MCP.
Uses Claude Agent SDK with Exa MCP server for comprehensive ecosystem analysis.
"""

import logging
from typing import List, Dict

from anthropic import Anthropic

from .config import Settings
from .schemas import WisdomDocument, ResearchPhaseResult

logger = logging.getLogger(__name__)


class EcosystemResearcher:
    """
    Uses Claude Agent SDK + Exa MCP for ecosystem research.
    
    Executes a sequential research process to understand:
    - What the tool is and who uses it
    - Ecosystem positioning and alternatives
    - Best practices and common pitfalls
    """
    
    def __init__(self, settings: Settings):
        """Initialize with settings containing API keys."""
        self.settings = settings
        self.client = Anthropic(api_key=settings.anthropic_api_key)
    
    def _create_research_prompt(
        self,
        topic: str,
        knowledge_context: str,
        phase: str,
        skill_type: str = "coding-agent"
    ) -> str:
        """
        Create a research prompt for a specific phase.

        Args:
            topic: The tool/framework being researched
            knowledge_context: Context from llms.txt
            phase: Research phase (discovery, ecosystem, practices)
            skill_type: Type of skill being created

        Returns:
            Formatted research prompt
        """
        # Customize context based on skill type
        if skill_type == "domain-knowledge":
            purpose = f"to create a comprehensive domain knowledge skill for {topic}"
            focus = "learning, understanding, and applying"
        else:
            purpose = f"to create a coding agent skill for {topic}"
            focus = "integration, automation, and extensibility"

        base_context = f"""You are researching {topic} {purpose}.

Available documentation context:
{knowledge_context[:2000]}...

"""
        
        if phase == "discovery":
            if skill_type == "domain-knowledge":
                return base_context + f"""Phase 1: Discovery
Use Exa MCP to search and answer:
1. What is {topic}? (2-3 paragraph overview)
2. Who are the primary users and learners?
3. What concepts and problems does it address?
4. Key features, principles, and capabilities
5. Learning curve and prerequisites

Focus on understanding and knowledge acquisition."""
            else:
                return base_context + f"""Phase 1: Discovery
Use Exa MCP to search and answer:
1. What is {topic}? (2-3 paragraph overview)
2. Who are the primary users?
3. What problems does it solve?
4. Key features and capabilities
5. Extensibility and automation potential

Focus on integration and automation capabilities."""

        elif phase == "ecosystem":
            if skill_type == "domain-knowledge":
                return base_context + f"""Phase 2: Ecosystem Mapping
Use Exa MCP to search and identify:
1. What category/domain does {topic} belong to?
2. What are the main alternatives and related technologies?
3. What tools/frameworks does it work with?
4. Common learning paths and use cases
5. When should you learn {topic} vs alternatives?

Focus on educational positioning and knowledge building."""
            else:
                return base_context + f"""Phase 2: Ecosystem Mapping
Use Exa MCP to search and identify:
1. What category/domain does {topic} belong to?
2. What are the main alternatives?
3. What tools/services does it integrate with?
4. Common automation and integration scenarios
5. When should you use {topic} vs alternatives?

Focus on practical positioning and integration opportunities."""

        elif phase == "practices":
            if skill_type == "domain-knowledge":
                return base_context + f"""Phase 3: Best Practices & Learning
Use Exa MCP to search and identify:
1. Recommended learning patterns and approaches
2. Common misconceptions and learning pitfalls
3. Key concepts to master first
4. Practical application strategies
5. Advanced techniques and patterns

Focus on effective learning and application."""
            else:
                return base_context + f"""Phase 3: Best Practices & Pitfalls
Use Exa MCP to search and identify:
1. Recommended integration patterns and best practices
2. Common mistakes and anti-patterns
3. Security considerations
4. Performance optimization tips
5. Testing and debugging approaches

Focus on practical implementation guidance."""
        
        return base_context
    
    def _execute_research_phase(
        self,
        topic: str,
        knowledge_context: str,
        phase: str,
        skill_type: str = "coding-agent"
    ) -> ResearchPhaseResult:
        """
        Execute a single research phase using Claude + Exa.
        
        This is a simplified implementation. In production, this would:
        1. Create an MCP client for Exa
        2. Use Claude Agent SDK to interact with Exa MCP
        3. Execute multiple searches
        4. Synthesize findings
        
        Args:
            topic: Tool/framework name
            knowledge_context: Documentation context
            phase: Research phase name
            
        Returns:
            ResearchPhaseResult with findings
        """
        logger.info(f"Executing research phase: {phase}")
        
        prompt = self._create_research_prompt(topic, knowledge_context, phase, skill_type)
        
        # Note: This is a simplified version without actual MCP integration
        # In production, you would use the Exa MCP server here
        # For now, we'll use Claude's knowledge with a research-focused prompt
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        findings = response.content[0].text
        
        return ResearchPhaseResult(
            phase_name=phase,
            findings=findings,
            sources=[]  # Would be populated from Exa search results
        )
    
    def research_ecosystem(
        self,
        topic: str,
        knowledge_context: str,
        skill_type: str = "coding-agent"
    ) -> WisdomDocument:
        """
        Execute sequential Feynman research process.

        Args:
            topic: The tool/framework to research
            knowledge_context: Context from llms.txt
            skill_type: Type of skill - "coding-agent" or "domain-knowledge"

        Returns:
            WisdomDocument with ecosystem insights
        """
        logger.info(f"Starting ecosystem research for {topic}")
        
        # Execute three research phases
        discovery = self._execute_research_phase(
            topic, knowledge_context, "discovery", skill_type
        )
        ecosystem = self._execute_research_phase(
            topic, knowledge_context, "ecosystem", skill_type
        )
        practices = self._execute_research_phase(
            topic, knowledge_context, "practices", skill_type
        )
        
        # Synthesize findings into structured wisdom document
        synthesis_prompt = f"""Synthesize the following research into a structured wisdom document for {topic}:

DISCOVERY PHASE:
{discovery.findings}

ECOSYSTEM PHASE:
{ecosystem.findings}

BEST PRACTICES PHASE:
{practices.findings}

Create a JSON response with this structure:
{{
    "overview": "2-3 paragraph synthesis",
    "ecosystem_position": {{
        "category": ["list of categories"],
        "alternatives": ["list of alternatives"],
        "complements": ["list of complementary tools"]
    }},
    "use_cases": ["list of use cases"],
    "integration_patterns": {{
        "common": ["list of common patterns"],
        "advanced": ["list of advanced patterns"]
    }},
    "best_practices": ["list of best practices"],
    "common_pitfalls": ["list of common pitfalls"]
}}"""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": synthesis_prompt
            }]
        )
        
        # Parse the synthesis
        import json
        synthesis = json.loads(response.content[0].text)
        
        return WisdomDocument(
            overview=synthesis.get("overview", ""),
            ecosystem_position=synthesis.get("ecosystem_position", {}),
            use_cases=synthesis.get("use_cases", []),
            integration_patterns=synthesis.get("integration_patterns", {}),
            best_practices=synthesis.get("best_practices", []),
            common_pitfalls=synthesis.get("common_pitfalls", []),
            sources=[]  # Would include Exa search URLs
        )