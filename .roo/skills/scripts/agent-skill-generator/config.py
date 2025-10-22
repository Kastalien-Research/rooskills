"""
Configuration management for Agent Skill Generator.
Handles environment variables and settings validation.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All API keys must be provided via environment variables.
    Never hardcode sensitive values.
    """
    
    # Required API Keys
    firecrawl_api_key: str
    openai_api_key: str
    anthropic_api_key: str
    
    # Optional Exa API Key (for Exa MCP server)
    exa_api_key: Optional[str] = None
    
    # Processing limits
    max_urls: int = 20
    character_limit: int = 25000
    batch_size: int = 10
    max_workers: int = 5
    
    # Output configuration
    output_dir: str = ".roo/skills"
    
    # Retry configuration
    api_retry_attempts: int = 3
    api_retry_backoff: float = 2.0
    
    # Rate limiting (requests per minute)
    firecrawl_rate_limit: int = 10
    openai_rate_limit: int = 60
    
    # Validation rules
    max_skill_lines: int = 500
    
    # Firecrawl configuration
    firecrawl_base_url: str = "https://api.firecrawl.dev/v1"
    
    # OpenAI configuration
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.3
    
    # MCP configuration
    exa_mcp_command: str = "npx"
    exa_mcp_args: list[str] = ["-y", "exa-mcp-server"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_required_keys(self) -> None:
        """Validate that all required API keys are present."""
        missing_keys = []
        
        if not self.firecrawl_api_key:
            missing_keys.append("FIRECRAWL_API_KEY")
        if not self.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            missing_keys.append("ANTHROPIC_API_KEY")
        
        if missing_keys:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_keys)}"
            )


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance with validated configuration
        
    Raises:
        ValueError: If required environment variables are missing
    """
    settings = Settings()
    settings.validate_required_keys()
    return settings