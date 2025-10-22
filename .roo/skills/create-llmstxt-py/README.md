# Firecrawl LLMs.txt Generator

A Python script that generates `llms.txt` and `llms-full.txt` files for any website using Firecrawl and OpenAI APIs.

## What is llms.txt?

`llms.txt` is a standardized format for making website content more accessible to Large Language Models (LLMs). It provides:

- **llms.txt**: A concise index of all pages with titles and descriptions
- **llms-full.txt**: Complete content of all pages for comprehensive access

## Features

- 🗺️ **Website Mapping**: Automatically discovers all URLs on a website using Firecrawl's map endpoint
- 📄 **Content Scraping**: Extracts markdown content from each page
- 🤖 **AI Summaries**: Uses OpenAI's GPT-4o-mini to generate concise titles and descriptions
- ⚡ **Parallel Processing**: Processes multiple URLs concurrently for faster generation
- 🎯 **Configurable Limits**: Set maximum number of URLs to process
- 📁 **Flexible Output**: Choose to generate both files or just llms.txt

## Prerequisites

- Python 3.7+
- Firecrawl API key ([Get one here](https://firecrawl.dev))
- OpenAI API key ([Get one here](https://platform.openai.com))

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up API keys (choose one method):

   **Option A: Using .env file (recommended)**

   ```bash
   cp env.example .env
   # Edit .env and add your API keys
   ```

   **Option B: Using environment variables**

   ```bash
   export FIRECRAWL_API_KEY="your-firecrawl-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

   **Option C: Using command line arguments**
   (See usage examples below)

## Usage

### Basic Usage

Generate llms.txt and llms-full.txt for a website:

```bash
python generate-llmstxt.py https://example.com
```

### With Options

```bash
# Limit to 50 URLs
python generate-llmstxt.py https://example.com --max-urls 50

# Save to specific directory
python generate-llmstxt.py https://example.com --output-dir ./output

# Only generate llms.txt (skip full text)
python generate-llmstxt.py https://example.com --no-full-text

# Enable verbose logging
python generate-llmstxt.py https://example.com --verbose

# Specify API keys via command line
python generate-llmstxt.py https://example.com \
  --firecrawl-api-key "fc-..." \
  --openai-api-key "sk-..."
```

### Command Line Options

- `url` (required): The website URL to process
- `--max-urls`: Maximum number of URLs to process (default: 20)
- `--output-dir`: Directory to save output files (default: current directory)
- `--firecrawl-api-key`: Firecrawl API key (defaults to .env file or FIRECRAWL_API_KEY env var)
- `--openai-api-key`: OpenAI API key (defaults to .env file or OPENAI_API_KEY env var)
- `--no-full-text`: Only generate llms.txt, skip llms-full.txt
- `--verbose`: Enable verbose logging for debugging

## Output Format

### llms.txt

```
# https://example.com llms.txt

- [Page Title](https://example.com/page1): Brief description of the page content here
- [Another Page](https://example.com/page2): Another concise description of page content
```

### llms-full.txt

```
# https://example.com llms-full.txt

<|firecrawl-page-1-lllmstxt|>
## Page Title
Full markdown content of the page...

<|firecrawl-page-2-lllmstxt|>
## Another Page
Full markdown content of another page...
```

## How It Works

1. **Website Mapping**: Uses Firecrawl's `/map` endpoint to discover all URLs on the website
2. **Batch Processing**: Processes URLs in batches of 10 for efficiency
3. **Content Extraction**: Scrapes each URL to extract markdown content
4. **AI Summarization**: For each page, GPT-4o-mini generates:
   - A 3-4 word title
   - A 9-10 word description
5. **File Generation**: Creates formatted llms.txt and llms-full.txt files

## Error Handling

- Failed URL scrapes are logged and skipped
- If no URLs are found, the script exits with an error
- API errors are logged with details for debugging
- Rate limiting is handled with delays between batches

## Performance Considerations

- Processing time depends on the number of URLs and response times
- Default batch size is 10 URLs processed concurrently
- Small delays between batches prevent rate limiting
- For large websites, consider using `--max-urls` to limit processing

## Examples

### Small Website

```bash
python generate-llmstxt.py https://small-blog.com --max-urls 20
```

### Large Website with Limited Scope

```bash
python generate-llmstxt.py https://docs.example.com --max-urls 100 --verbose
```

### Quick Index Only

```bash
python generate-llmstxt.py https://example.com --no-full-text --max-urls 50
```

## Configuration Priority

The script checks for API keys in this order:

1. Command line arguments (`--firecrawl-api-key`, `--openai-api-key`)
2. `.env` file in the current directory
3. Environment variables (`FIRECRAWL_API_KEY`, `OPENAI_API_KEY`)

## Troubleshooting

### No API Keys Found

Ensure you've either:

- Created a `.env` file with your API keys (copy from `env.example`)
- Set environment variables: `FIRECRAWL_API_KEY` and `OPENAI_API_KEY`
- Or pass them via command line arguments

### Rate Limiting

If you encounter rate limits:

- Reduce concurrent workers in the code
- Add longer delays between batches
- Process fewer URLs at once

### Memory Issues

For very large websites:

- Use `--max-urls` to limit the number of pages
- Process in smaller batches
- Use `--no-full-text` to skip full content generation

## License

MIT License - see LICENSE file for details
