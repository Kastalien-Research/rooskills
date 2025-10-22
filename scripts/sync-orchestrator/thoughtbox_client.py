#!/usr/bin/env python3
"""
Thoughtbox Client - MCP integration with Clear Thought 2.0 reasoning server.

This module provides deep reasoning capabilities for understanding the intent
behind commands and skills using the Thoughtbox MCP server.
"""

import os
import json
import argparse
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlencode


# Try to import MCP client
try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  Warning: MCP client not available. Install with: pip install mcp[cli]")


@dataclass
class Intent:
    """Analyzed intent from Thoughtbox reasoning."""
    name: str
    type: str  # "command" or "skill"
    purpose: str
    use_cases: list[str]
    key_concepts: list[str]
    workflow_steps: list[str]
    dependencies: list[str]
    suggested_structure: Dict[str, any]


class ThoughtboxClient:
    """Client for interacting with Thoughtbox MCP server."""

    def __init__(
        self,
        base_url: str = "https://server.smithery.ai/@Kastalien-Research/clear-thought-two/mcp",
        api_key: str = "fe556de3-a658-4330-a3e7-563cf6a91972",
        profile: str = "operational-bedbug-smw1eB",
        timeout: float = 30.0,
        connect_timeout: float = 10.0
    ):
        """
        Initialize Thoughtbox client.

        Args:
            base_url: Base URL for Thoughtbox MCP server
            api_key: API key for authentication
            profile: Profile identifier
            timeout: Request timeout in seconds (default: 30.0)
            connect_timeout: Connection timeout in seconds (default: 10.0)
        """
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP client not available. Install with: pip install mcp[cli]")

        params = {"api_key": api_key, "profile": profile}
        self.url = f"{base_url}?{urlencode(params)}"
        self.timeout = timeout
        self.connect_timeout = connect_timeout

    async def reason(self, prompt: str) -> str:
        """
        Use Thoughtbox to reason about a prompt.

        Args:
            prompt: The reasoning prompt

        Returns:
            Thoughtbox's reasoning response
            
        Raises:
            asyncio.TimeoutError: If request times out
            RuntimeError: If no tools are available or connection fails
        """
        try:
            # Apply timeout to entire operation
            async with asyncio.timeout(self.timeout):
                async with streamablehttp_client(self.url) as (read, write, _):
                    async with ClientSession(read, write) as session:
                        # Initialize connection with timeout
                        await asyncio.wait_for(
                            session.initialize(),
                            timeout=self.connect_timeout
                        )

                        # List available tools
                        tools_result = await asyncio.wait_for(
                            session.list_tools(),
                            timeout=self.connect_timeout
                        )
                        available_tools = [t.name for t in tools_result.tools]

                        # Use clear_thought tool if available
                        if "clear_thought" in available_tools:
                            result = await asyncio.wait_for(
                                session.call_tool(
                                    "clear_thought",
                                    arguments={"thought": prompt}
                                ),
                                timeout=self.timeout
                            )
                            return result.content[0].text
                        else:
                            # Fallback: use first available tool
                            if available_tools:
                                result = await asyncio.wait_for(
                                    session.call_tool(
                                        available_tools[0],
                                        arguments={"prompt": prompt}
                                    ),
                                    timeout=self.timeout
                                )
                                return result.content[0].text
                            else:
                                raise RuntimeError("No tools available in Thoughtbox MCP")
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(
                f"Request timed out after {self.timeout} seconds"
            )

    async def analyze_command(self, command_content: str, command_name: str) -> Intent:
        """
        Analyze a command using Thoughtbox reasoning.

        Args:
            command_content: Full markdown content of the command
            command_name: Name of the command

        Returns:
            Intent with deep understanding of the command
        """
        # Note: Content truncated to 2000 chars for context window
        prompt = f"""
Analyze this slash command and deeply understand its intent:

Command: /{command_name}

Content:
{command_content[:2000]}

Your task:
1. What is the core PURPOSE of this command?
2. What USE CASES does it serve?
3. What are the KEY CONCEPTS the user needs to understand?
4. What are the WORKFLOW STEPS when using this command?
5. What DEPENDENCIES does it have (tools, APIs, knowledge)?
6. How should the corresponding SKILL be structured?

Think deeply about the "why" behind this command, not just the "what".
Output your analysis as structured JSON with these keys:
- purpose: string
- use_cases: array of strings
- key_concepts: array of strings
- workflow_steps: array of strings
- dependencies: array of strings
- suggested_structure: object with title, sections, examples

Be concise but thorough. Focus on enabling skill generation.
"""

        reasoning = await self.reason(prompt)

        # Parse JSON from reasoning (Thoughtbox should return structured output)
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', reasoning)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback: construct intent from text
                data = {
                    "purpose": "Extracted from command documentation",
                    "use_cases": ["General command usage"],
                    "key_concepts": [],
                    "workflow_steps": [],
                    "dependencies": [],
                    "suggested_structure": {}
                }

            return Intent(
                name=command_name,
                type="command",
                purpose=data.get("purpose", ""),
                use_cases=data.get("use_cases", []),
                key_concepts=data.get("key_concepts", []),
                workflow_steps=data.get("workflow_steps", []),
                dependencies=data.get("dependencies", []),
                suggested_structure=data.get("suggested_structure", {})
            )

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return Intent(
                name=command_name,
                type="command",
                purpose=f"Command for {command_name}",
                use_cases=["To be determined from command content"],
                key_concepts=[],
                workflow_steps=[],
                dependencies=[],
                suggested_structure={}
            )

    async def analyze_skill(self, skill_content: str, skill_name: str) -> Intent:
        """
        Analyze a skill using Thoughtbox reasoning.

        Args:
            skill_content: Full markdown content of SKILL.md
            skill_name: Name of the skill

        Returns:
            Intent with deep understanding of the skill
        """
        # Note: Content truncated to 2000 chars for context window
        prompt = f"""
Analyze this Agent Skill and deeply understand its intent:

Skill: {skill_name}

Content:
{skill_content[:2000]}

Your task:
1. What is the core PURPOSE of this skill?
2. What USE CASES does it enable?
3. What are the KEY CONCEPTS it teaches?
4. What are the typical WORKFLOW STEPS when using this skill?
5. What DEPENDENCIES does it have (tools, knowledge, APIs)?
6. How should the corresponding SLASH COMMAND be structured?

Think about how to distill this skill into a concise, actionable command.
Output your analysis as structured JSON with these keys:
- purpose: string
- use_cases: array of strings
- key_concepts: array of strings
- workflow_steps: array of strings
- dependencies: array of strings
- suggested_structure: object with command_name, usage_example, key_sections

Be concise but thorough. Focus on enabling command generation.
"""

        reasoning = await self.reason(prompt)

        # Parse JSON from reasoning
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', reasoning)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {
                    "purpose": "Extracted from skill documentation",
                    "use_cases": ["General skill usage"],
                    "key_concepts": [],
                    "workflow_steps": [],
                    "dependencies": [],
                    "suggested_structure": {}
                }

            return Intent(
                name=skill_name,
                type="skill",
                purpose=data.get("purpose", ""),
                use_cases=data.get("use_cases", []),
                key_concepts=data.get("key_concepts", []),
                workflow_steps=data.get("workflow_steps", []),
                dependencies=data.get("dependencies", []),
                suggested_structure=data.get("suggested_structure", {})
            )

        except json.JSONDecodeError:
            # Fallback
            return Intent(
                name=skill_name,
                type="skill",
                purpose=f"Skill for {skill_name}",
                use_cases=["To be determined from skill content"],
                key_concepts=[],
                workflow_steps=[],
                dependencies=[],
                suggested_structure={}
            )


def verify_connection():
    """Verify Thoughtbox MCP connection is available."""
    if not MCP_AVAILABLE:
        print("❌ MCP client not installed")
        print("   Install with: pip install mcp[cli]")
        return False

    try:
        client = ThoughtboxClient()
        # Try a simple connection test
        async def test():
            try:
                result = await client.reason("Test connection")
                return True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return False

        result = asyncio.run(test())
        if result:
            print("✅ Thoughtbox MCP connection successful")
        return result

    except Exception as e:
        print(f"❌ Thoughtbox MCP not available: {e}")
        return False


async def main_async(args):
    """Async main function."""
    client = ThoughtboxClient()

    # Read file
    with open(args.file, 'r') as f:
        content = f.read()

    # Analyze based on type
    if args.type == "command":
        intent = await client.analyze_command(content, os.path.basename(args.file).replace('.md', ''))
    elif args.type == "skill":
        skill_name = os.path.basename(os.path.dirname(args.file))
        intent = await client.analyze_skill(content, skill_name)
    else:
        raise ValueError(f"Unknown type: {args.type}")

    # Output
    result_json = json.dumps(asdict(intent), indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(result_json)
        if args.verbose:
            print(f"✅ Intent analysis written to {args.output}")
    else:
        print(result_json)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze commands/skills using Thoughtbox MCP"
    )
    parser.add_argument(
        "--type",
        choices=["command", "skill"],
        required=True,
        help="Type of item to analyze"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to command .md or SKILL.md file"
    )
    parser.add_argument(
        "--output",
        help="Output file for JSON intent (default: stdout)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if not MCP_AVAILABLE:
        print("❌ MCP client not available")
        print("   Install with: pip install mcp[cli]")
        return 1

    asyncio.run(main_async(args))
    return 0


if __name__ == "__main__":
    exit(main())
