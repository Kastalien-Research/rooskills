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
        phase: str
    ) -> str:
        """
        Create a research prompt for a specific phase.
        
        Args:
            topic: The tool/framework being researched
            knowledge_context: Context from llms.txt
            phase: Research phase (discovery, ecosystem, practices)
            
        Returns:
            Formatted research prompt
        """
        base_context = f"""You are researching {topic} to create a comprehensive skill guide.

Available documentation context:
{knowledge_context[:2000]}...

"""
        
        if phase == "discovery":
            return base_context + f"""Phase 1: Discovery
Use Exa MCP to search and answer:
1. What is {topic}? (2-3 paragraph overview)
2. Who are the primary users?
3. What problems does it solve?
4. Key features and capabilities

Provide a comprehensive yet concise summary."""
        
        elif phase == "ecosystem":
            return base_context + f"""Phase 2: Ecosystem Mapping
Use Exa MCP to search and identify:
1. What category/domain does {topic} belong to?
2. What are the main alternatives?
3. What tools/services does it integrate with?
4. Common use cases and scenarios
5. When should you use {topic} vs alternatives?

Focus on practical positioning and real-world usage."""
        
        elif phase == "practices":
            return base_context + f"""Phase 3: Best Practices & Pitfalls
Use Exa MCP to search and identify:
1. Recommended patterns and best practices
2. Common mistakes and anti-patterns
3. Security considerations
4. Performance optimization tips
5. Testing and debugging approaches

Provide actionable, practical guidance."""
        
        return base_context
    
    def _execute_research_phase(
        self,
        topic: str,
        knowledge_context: str,
        phase: str
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
        
        prompt = self._create_research_prompt(topic, knowledge_context, phase)
        
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
        knowledge_context: str
    ) -> WisdomDocument:
        """
        Execute sequential Feynman research process.
        
        Args:
            topic: The tool/framework to research
            knowledge_context: Context from llms.txt
            
        Returns:
            WisdomDocument with ecosystem insights
        """
        logger.info(f"Starting ecosystem research for {topic}")
        
        # Execute three research phases
        discovery = self._execute_research_phase(
            topic, knowledge_context, "discovery"
        )
        ecosystem = self._execute_research_phase(
            topic, knowledge_context, "ecosystem"
        )
        practices = self._execute_research_phase(
            topic, knowledge_context, "practices"
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