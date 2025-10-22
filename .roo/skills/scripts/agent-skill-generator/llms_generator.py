"""
LLMS Generator Module - Documentation scraping and summarization.
Uses Firecrawl API for scraping and OpenAI for generating summaries.
"""

import re
import time
import logging
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Settings
from .schemas import KnowledgeBundle, ScrapedPage

logger = logging.getLogger(__name__)


class LLMSGenerator:
    """
    Handles documentation scraping and summarization.
    
    Uses Firecrawl to map and scrape websites, then OpenAI to generate
    concise titles and descriptions for each page.
    """
    
    def __init__(self, settings: Settings):
        """Initialize with settings containing API keys."""
        self.settings = settings
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.headers = {
            "Authorization": f"Bearer {settings.firecrawl_api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    def _map_website(self, url: str, limit: int) -> List[str]:
        """
        Discover all documentation URLs using Firecrawl /map endpoint.
        
        Args:
            url: Base URL to map
            limit: Maximum number of URLs to return
            
        Returns:
            List of discovered URLs
        """
        logger.info(f"Mapping website: {url} (limit: {limit})")
        
        response = requests.post(
            f"{self.settings.firecrawl_base_url}/map",
            headers=self.headers,
            json={
                "url": url,
                "limit": limit,
                "includeSubdomains": False,
                "ignoreSitemap": False
            },
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("success") and data.get("links"):
            urls = data["links"]
            logger.info(f"Found {len(urls)} URLs")
            return urls
        
        logger.warning(f"No URLs found for {url}")
        return []
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    def _scrape_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single URL using Firecrawl /scrape endpoint.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict with url, markdown, and metadata, or None if failed
        """
        logger.debug(f"Scraping URL: {url}")
        
        response = requests.post(
            f"{self.settings.firecrawl_base_url}/scrape",
            headers=self.headers,
            json={
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "timeout": 30000
            },
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("success") and data.get("data"):
            return {
                "url": url,
                "markdown": data["data"].get("markdown", ""),
                "metadata": data["data"].get("metadata", {})
            }
        
        logger.error(f"Failed to scrape {url}")
        return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    def _generate_summary(self, url: str, markdown: str) -> Tuple[str, str]:
        """
        Generate title and description using OpenAI.
        
        Args:
            url: Page URL
            markdown: Page content in markdown
            
        Returns:
            Tuple of (title, description)
        """
        logger.debug(f"Generating summary for: {url}")
        
        prompt = f"""Generate a 9-10 word description and a 3-4 word title of the entire page based on ALL the content one will find on the page for this url: {url}. This will help in a user finding the page for its intended purpose.

Return the response in JSON format:
{{
    "title": "3-4 word title",
    "description": "9-10 word description"
}}"""
        
        response = self.openai_client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates concise titles and descriptions for web pages."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nPage content:\n{markdown[:4000]}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=self.settings.openai_temperature,
            max_tokens=100
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return (
            result.get("title", "Page"),
            result.get("description", "No description available")
        )
    
    def _process_url(self, url: str, index: int) -> Optional[ScrapedPage]:
        """
        Process a single URL: scrape and generate summary.
        
        Args:
            url: URL to process
            index: Index in the batch
            
        Returns:
            ScrapedPage object or None if failed
        """
        scraped_data = self._scrape_url(url)
        if not scraped_data or not scraped_data.get("markdown"):
            return None
        
        title, description = self._generate_summary(
            url,
            scraped_data["markdown"]
        )
        
        return ScrapedPage(
            url=url,
            title=title,
            description=description,
            markdown=scraped_data["markdown"],
            index=index
        )
    
    def _remove_page_separators(self, text: str) -> str:
        """Remove page separators from text."""
        return re.sub(r'<\|firecrawl-page-\d+-lllmstxt\|>\n', '', text)
    
    def extract_knowledge(
        self,
        url: str,
        max_pages: int = 50
    ) -> KnowledgeBundle:
        """
        Extract structured knowledge from documentation URL.
        
        Args:
            url: Base documentation URL
            max_pages: Maximum number of pages to process
            
        Returns:
            KnowledgeBundle with llms_txt and llms_full_txt
        """
        logger.info(f"Generating knowledge bundle for {url}")
        
        # Step 1: Map the website
        urls = self._map_website(url, max_pages)
        if not urls:
            raise ValueError(f"No URLs found for {url}")
        
        # Limit to max_pages
        urls = urls[:max_pages]
        
        # Initialize output strings
        llmstxt = f"# {url} llms.txt\n\n"
        llms_fulltxt = f"# {url} llms-full.txt\n\n"
        
        # Process URLs in batches
        all_results: List[ScrapedPage] = []
        batch_size = self.settings.batch_size
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(
                f"Processing batch {i//batch_size + 1}/"
                f"{(len(urls) + batch_size - 1)//batch_size}"
            )
            
            # Process batch concurrently
            with ThreadPoolExecutor(max_workers=self.settings.max_workers) as executor:
                futures = {
                    executor.submit(self._process_url, url, i + j): (url, i + j)
                    for j, url in enumerate(batch)
                }
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            all_results.append(result)
                    except Exception as e:
                        url, idx = futures[future]
                        logger.error(f"Failed to process {url}: {e}")
            
            # Rate limiting between batches
            if i + batch_size < len(urls):
                time.sleep(1)
        
        # Sort results by index
        all_results.sort(key=lambda x: x.index)
        
        # Build output strings
        for i, result in enumerate(all_results, 1):
            llmstxt += f"- [{result.title}]({result.url}): {result.description}\n"
            llms_fulltxt += (
                f"<|firecrawl-page-{i}-lllmstxt|>\n"
                f"## {result.title}\n{result.markdown}\n\n"
            )
        
        # Create knowledge bundle
        return KnowledgeBundle(
            llms_txt=llmstxt,
            llms_full_txt=self._remove_page_separators(llms_fulltxt),
            source_url=url,
            page_count=len(all_results),
            metadata={
                "total_urls_discovered": len(urls),
                "successfully_processed": len(all_results)
            }
        )