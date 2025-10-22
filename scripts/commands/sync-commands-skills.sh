#!/bin/bash
set -euo pipefail

# Sync Commands-Skills Script
# Bidirectionally synchronize slash commands and skills using Thoughtbox reasoning

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SYNC_ORCHESTRATOR_DIR="$PROJECT_ROOT/scripts/sync-orchestrator"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Print usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Bidirectionally synchronize slash commands and skills using Thoughtbox reasoning.

Options:
    --dry-run           Show what would be created without creating
    --parallel N        Maximum concurrent subagents (default: 3)
    --verbose           Enable verbose logging
    -h, --help          Show this help message

Examples:
    # Basic sync
    $0

    # Dry run to preview changes
    $0 --dry-run

    # Custom parallelism
    $0 --parallel 5

    # Verbose output
    $0 --verbose

EOF
    exit 1
}

# Parse arguments
DRY_RUN=""
PARALLEL=3
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --parallel)
            PARALLEL="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown argument: $1"
            usage
            ;;
    esac
done

# Header
log_info "Sync Commands-Skills v$VERSION"
echo

# Change to project root
cd "$PROJECT_ROOT"

# Check Python is available
if ! command -v python3 &> /dev/null; then
    log_error "python3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Check if sync-orchestrator directory exists
if [ ! -d "$SYNC_ORCHESTRATOR_DIR" ]; then
    log_error "Sync orchestrator not found at: $SYNC_ORCHESTRATOR_DIR"
    exit 1
fi

# Check if MCP is installed (optional for now)
log_info "Checking dependencies..."

MCP_AVAILABLE=false

if python3 -c "import mcp" 2>/dev/null; then
    MCP_AVAILABLE=true
    log_success "MCP client found"

    # Verify Thoughtbox connection
    log_info "Verifying Thoughtbox MCP connection..."

    if python3 -c "from scripts.sync_orchestrator.thoughtbox_client import verify_connection; verify_connection()" 2>/dev/null; then
        log_success "Thoughtbox MCP connected - will use deep reasoning"
    else
        log_warning "Thoughtbox MCP connection could not be verified"
        log_info "Will use fallback template-based generation"
        MCP_AVAILABLE=false
    fi
else
    log_warning "MCP client not installed"
    log_info "Will use fallback template-based generation without Thoughtbox reasoning"
    log_info ""
    log_info "To enable Thoughtbox reasoning, install dependencies:"
    log_info "  pip install --user -r $SYNC_ORCHESTRATOR_DIR/requirements.txt"
    log_info "Or:"
    log_info "  python3 -m venv venv && source venv/bin/activate"
    log_info "  pip install -r $SYNC_ORCHESTRATOR_DIR/requirements.txt"
fi

echo

# Execute sync orchestrator
log_info "Starting synchronization..."
echo

# Build command
CMD="python3 -m scripts.sync_orchestrator.sync_orchestrator"
CMD="$CMD --commands .claude/commands"
CMD="$CMD --skills .claude/skills"
CMD="$CMD --parallel $PARALLEL"

if [ -n "$DRY_RUN" ]; then
    CMD="$CMD --dry-run"
fi

if [ -n "$VERBOSE" ]; then
    CMD="$CMD --verbose"
fi

# Run the orchestrator
if eval "$CMD"; then
    echo
    log_success "Synchronization complete!"
    exit 0
else
    echo
    log_error "Synchronization failed"
    exit 1
fi
