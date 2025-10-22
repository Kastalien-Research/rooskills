#!/usr/bin/env bash
#
# generate-skill.sh - Shell wrapper for Agent Skill Generator
#
# This script provides a convenient command-line interface for generating
# Roo Code skills from documentation URLs. It validates the environment,
# parses arguments, and coordinates the Python orchestrator.
#
# Usage:
#   ./scripts/commands/generate-skill.sh <URL> [SKILL_NAME] [OPTIONS]
#
# Arguments:
#   URL           Documentation URL to process (required)
#   SKILL_NAME    Skill identifier in kebab-case (optional, auto-generated from URL)
#
# Options:
#   --max-urls N       Maximum number of URLs to process (default: 20)
#   --use-feynman      Enable Feynman technique for documentation (default: true)
#   --output-dir DIR   Output directory (default: SKILL_NAME)
#   --verbose          Enable verbose logging
#   --help             Show this help message
#
# Environment Variables (required):
#   FIRECRAWL_API_KEY      Firecrawl API key
#   OPENAI_API_KEY         OpenAI API key
#   ANTHROPIC_API_KEY      Anthropic/Claude API key
#
# Examples:
#   ./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com"
#   ./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" "fastapi-dev"
#   ./scripts/commands/generate-skill.sh "https://fastapi.tiangolo.com" --max-urls 30
#

set -euo pipefail

# ==============================================================================
# Configuration
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../../" && pwd)"
ORCHESTRATOR_MODULE="agent-skill-generator.orchestrator"
PYTHON_PATH="${PROJECT_ROOT}/.roo/skills/scripts"

# Default values
DEFAULT_MAX_URLS=20
DEFAULT_USE_FEYNMAN=true

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ==============================================================================
# Helper Functions
# ==============================================================================

print_header() {
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}${CYAN}  $1${RESET}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${RESET}"
}

print_error() {
    echo -e "${RED}✗ Error: $1${RESET}" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠ Warning: $1${RESET}"
}

print_info() {
    echo -e "${BLUE}→ $1${RESET}"
}

show_help() {
    cat << EOF
${BOLD}Agent Skill Generator - Shell Wrapper${RESET}

${BOLD}USAGE:${RESET}
    $0 <URL> [SKILL_NAME] [OPTIONS]

${BOLD}ARGUMENTS:${RESET}
    URL           Documentation URL to process (required)
    SKILL_NAME    Skill identifier in kebab-case (optional, auto-generated from URL)

${BOLD}OPTIONS:${RESET}
    --max-urls N       Maximum number of URLs to process (default: ${DEFAULT_MAX_URLS})
    --use-feynman      Enable Feynman technique for documentation (default: ${DEFAULT_USE_FEYNMAN})
    --output-dir DIR   Output directory (default: SKILL_NAME)
    --verbose          Enable verbose logging
    --help             Show this help message

${BOLD}REQUIRED ENVIRONMENT VARIABLES:${RESET}
    FIRECRAWL_API_KEY      Firecrawl API key
    OPENAI_API_KEY         OpenAI API key
    ANTHROPIC_API_KEY      Anthropic/Claude API key

${BOLD}EXAMPLES:${RESET}
    # Generate with auto-detected name
    $0 "https://fastapi.tiangolo.com"

    # Generate with custom name
    $0 "https://fastapi.tiangolo.com" "fastapi-dev"

    # Generate with custom options
    $0 "https://fastapi.tiangolo.com" --max-urls 30 --verbose

    # Generate with custom output directory
    $0 "https://fastapi.tiangolo.com" "fastapi-dev" --output-dir "./my-skills/fastapi"

${BOLD}PHASES:${RESET}
    Phase 1: Knowledge Extraction  - Scrape and summarize documentation
    Phase 2: Ecosystem Research    - Analyze positioning and best practices
    Phase 3: Skill Synthesis       - Generate SKILL.md with structured guidance
    Phase 4: File Writing          - Write all skill files to disk
    Phase 5: Mode Registration     - Register skill in .roomodes configuration

EOF
    exit 0
}

# ==============================================================================
# Validation Functions
# ==============================================================================

load_env_file() {
    # Load .env file if it exists in the project root
    local env_file="${PROJECT_ROOT}/.env"
    if [[ -f "${env_file}" ]]; then
        print_info "Loading environment variables from .env file..."
        # Export variables from .env file
        set -a
        source "${env_file}"
        set +a
        print_success "Environment variables loaded from .env"
    fi
}

validate_environment() {
    print_header "Validating Environment"
    
    # Try to load .env file first
    load_env_file
    
    local missing_keys=()
    
    # Check for required API keys
    if [[ -z "${FIRECRAWL_API_KEY:-}" ]]; then
        missing_keys+=("FIRECRAWL_API_KEY")
    else
        print_success "FIRECRAWL_API_KEY is set"
    fi
    
    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
        missing_keys+=("OPENAI_API_KEY")
    else
        print_success "OPENAI_API_KEY is set"
    fi
    
    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
        missing_keys+=("ANTHROPIC_API_KEY")
    else
        print_success "ANTHROPIC_API_KEY is set"
    fi
    
    # Report missing keys
    if [[ ${#missing_keys[@]} -gt 0 ]]; then
        echo ""
        print_error "Missing required environment variables:"
        for key in "${missing_keys[@]}"; do
            echo -e "  ${RED}- ${key}${RESET}"
        done
        echo ""
        echo -e "${YELLOW}Please set all required environment variables and try again.${RESET}"
        echo -e "${YELLOW}You can set them in a .env file or export them in your shell.${RESET}"
        echo ""
        exit 1
    fi
    
    print_success "All required environment variables are set"
}

validate_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "python3 is not installed or not in PATH"
        echo -e "${YELLOW}Please install Python 3.10 or higher${RESET}"
        exit 1
    fi
    
    local python_version
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python ${python_version} found"
}

validate_dependencies() {
    print_info "Checking Python dependencies..."
    
    cd "${PROJECT_ROOT}"
    
    if ! python3 -c "import typer, rich, pydantic_settings" &> /dev/null; then
        print_warning "Some Python dependencies are missing"
        print_info "Installing dependencies from requirements.txt..."
        
        if [[ -f ".roo/skills/scripts/agent-skill-generator/requirements.txt" ]]; then
            python3 -m pip install -q -r .roo/skills/scripts/agent-skill-generator/requirements.txt
            print_success "Dependencies installed"
        else
            print_error "requirements.txt not found"
            exit 1
        fi
    else
        print_success "All Python dependencies are available"
    fi
}

# ==============================================================================
# URL Processing Functions
# ==============================================================================

generate_skill_name_from_url() {
    local url="$1"
    
    # Extract domain from URL
    local domain
    domain=$(echo "$url" | sed -E 's|https?://([^/]+).*|\1|')
    
    # Remove common prefixes and TLDs
    domain=$(echo "$domain" | sed -E 's/^(www\.|docs\.|api\.)//g')
    domain=$(echo "$domain" | sed -E 's/\.(com|org|io|dev|net)$//g')
    
    # Convert to kebab-case
    local skill_name
    skill_name=$(echo "$domain" | tr '[:upper:]' '[:lower:]' | tr '.' '-')
    
    echo "${skill_name}"
}

# ==============================================================================
# Argument Parsing
# ==============================================================================

parse_arguments() {
    # Show help if requested
    if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
        show_help
    fi
    
    # Check if URL is provided
    if [[ $# -eq 0 ]]; then
        print_error "Missing required argument: URL"
        echo ""
        echo "Usage: $0 <URL> [SKILL_NAME] [OPTIONS]"
        echo "Run '$0 --help' for more information"
        echo ""
        exit 1
    fi
    
    # Parse URL (first argument)
    URL="$1"
    shift
    
    # Check if second argument is a skill name or an option
    if [[ $# -gt 0 ]] && [[ ! "$1" =~ ^-- ]]; then
        SKILL_NAME="$1"
        shift
    else
        # Auto-generate skill name from URL
        SKILL_NAME=$(generate_skill_name_from_url "$URL")
        print_info "Auto-generated skill name: ${SKILL_NAME}"
    fi
    
    # Parse optional arguments
    MAX_URLS="${DEFAULT_MAX_URLS}"
    USE_FEYNMAN="${DEFAULT_USE_FEYNMAN}"
    OUTPUT_DIR=""
    VERBOSE=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --max-urls)
                MAX_URLS="$2"
                shift 2
                ;;
            --use-feynman)
                USE_FEYNMAN=true
                shift
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Run '$0 --help' for usage information"
                exit 1
                ;;
        esac
    done
}

# ==============================================================================
# Main Execution
# ==============================================================================

main() {
    # Parse command-line arguments
    parse_arguments "$@"
    
    # Show banner
    echo ""
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${CYAN}║                                                                  ║${RESET}"
    echo -e "${BOLD}${CYAN}║             🚀 Agent Skill Generator - Shell Wrapper             ║${RESET}"
    echo -e "${BOLD}${CYAN}║                                                                  ║${RESET}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════════╝${RESET}"
    
    # Validate environment
    validate_environment
    validate_python
    validate_dependencies
    
    # Display configuration
    print_header "Configuration"
    echo -e "${BOLD}URL:${RESET}           ${URL}"
    echo -e "${BOLD}Skill Name:${RESET}    ${SKILL_NAME}"
    echo -e "${BOLD}Max URLs:${RESET}      ${MAX_URLS}"
    echo -e "${BOLD}Use Feynman:${RESET}   ${USE_FEYNMAN}"
    if [[ -n "${OUTPUT_DIR}" ]]; then
        echo -e "${BOLD}Output Dir:${RESET}    ${OUTPUT_DIR}"
    fi
    echo -e "${BOLD}Verbose:${RESET}       ${VERBOSE}"
    
    # Build Python command
    print_header "Generating Skill"
    
    local python_cmd=(
        python3 -m "${ORCHESTRATOR_MODULE}"
        generate
        "$URL"
        "$SKILL_NAME"
        --max-urls "$MAX_URLS"
    )
    
    if [[ -n "${OUTPUT_DIR}" ]]; then
        python_cmd+=(--output-dir "$OUTPUT_DIR")
    fi
    
    if [[ "${VERBOSE}" == true ]]; then
        python_cmd+=(--verbose)
    fi
    
    # Execute Python orchestrator
    print_info "Executing Python orchestrator..."
    echo ""
    
    cd "${PROJECT_ROOT}"
    
    # Set PYTHONPATH to allow module imports
    export PYTHONPATH="${PYTHON_PATH}:${PYTHONPATH:-}"
    
    if "${python_cmd[@]}"; then
        # Success
        print_header "Generation Complete"
        print_success "Skill successfully generated!"
        echo ""
        echo -e "${BOLD}Next steps:${RESET}"
        echo -e "  1. Review the generated SKILL.md file"
        echo -e "  2. Test the skill in Roo Code"
        echo -e "  3. Customize as needed"
        echo ""
        exit 0
    else
        # Failure
        exit_code=$?
        print_header "Generation Failed"
        print_error "Skill generation failed with exit code ${exit_code}"
        echo ""
        echo -e "${YELLOW}Troubleshooting tips:${RESET}"
        echo -e "  - Run with --verbose flag for detailed logs"
        echo -e "  - Check API key validity"
        echo -e "  - Verify URL is accessible"
        echo -e "  - Check rate limits on API services"
        echo ""
        exit "${exit_code}"
    fi
}

# ==============================================================================
# Script Entry Point
# ==============================================================================

main "$@"