#!/usr/bin/env bash
###############################################################################
# Deep Codebase Research Script
# 
# Purpose: Systematically research codebases by spawning one Claude subagent
#          per important root-level directory using the --agents CLI flag.
#
# Usage: ./deep_research.sh [--dirs "dir1,dir2"] [--output ./path] [--dry-run]
#
# Outputs:
#   - CLAUDE.md (project knowledge base)
#   - Updated .roomodes (new codebase-researcher mode)
#   - .claude/agents/*.md (persistent subagents per directory)
#   - references/codebase_structure.md (detailed findings)
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-.}"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT}"
DRY_RUN=false
SPECIFIC_DIRS=""

# Function to print colored messages
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dirs)
      SPECIFIC_DIRS="$2"
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      log_error "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Get list of directories to research
get_important_directories() {
  local dirs=()
  
  if [[ -n "$SPECIFIC_DIRS" ]]; then
    # Use specified directories
    IFS=',' read -ra dirs <<< "$SPECIFIC_DIRS"
  else
    # Auto-detect important directories
    while IFS= read -r dir; do
      # Skip hidden, dependencies, and build dirs
      [[ "$dir" =~ ^\. ]] && continue
      [[ "$dir" =~ ^(node_modules|venv|.venv|env|dist|build|out|target|__pycache__)$ ]] && continue
      
      # Include if it looks important
      if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        case "$dir" in
          src|lib|app|cli|scripts|docs|specs|tests|__tests__|spec|config|.roo|.claude)
            dirs+=("$dir")
            ;;
          *)
            # Include if it contains code files
            if find "$PROJECT_ROOT/$dir" -maxdepth 2 -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.md" \) -print -quit | grep -q .; then
              dirs+=("$dir")
            fi
            ;;
        esac
      fi
    done < <(ls -1 "$PROJECT_ROOT")
  fi
  
  printf '%s\n' "${dirs[@]}"
}

# Generate subagents JSON for --agents flag
generate_subagents_json() {
  local dirs=("$@")
  local json="{"
  
  for i in "${!dirs[@]}"; do
    local dir="${dirs[$i]}"
    local agent_name="${dir/\//-}-analyzer"
    
    # Determine focus based on directory type
    local focus="general code and structure"
    case "$dir" in
      cli|scripts) focus="CLI tools, commands, and automation scripts" ;;
      src|lib|app) focus="application logic, core functionality, and architecture" ;;
      docs|specs) focus="documentation, specifications, and architecture decisions" ;;
      tests|__tests__|spec) focus="test coverage, patterns, and quality assurance" ;;
      config|.roo|.claude) focus="configuration, skills, and project setup" ;;
    esac
    
    # Build subagent definition
    json+="\"$agent_name\": {"
    json+="\"description\": \"Analyze $dir/ directory for $focus\","
    json+="\"prompt\": \"You are a senior software engineer analyzing the $dir/ directory. Your task is to:\n1. Map the directory structure and key files\n2. Identify primary patterns and conventions\n3. Document key components and their purposes\n4. Note dependencies and relationships\n5. Highlight any issues or technical debt\n\nFocus on $focus. Provide a concise summary suitable for CLAUDE.md.\","
    json+="\"tools\": [\"Read\", \"Glob\", \"Grep\", \"Bash\"]"
    json+="}"
    
    # Add comma if not last item
    [[ $i -lt $((${#dirs[@]} - 1)) ]] && json+=","
  done
  
  json+="}"
  echo "$json"
}

# Main execution
main() {
  log_info "Starting deep codebase research..."

  # Get directories to research
  DIRS=()
  while IFS= read -r dir; do
    DIRS+=("$dir")
  done < <(get_important_directories)

  if [[ ${#DIRS[@]} -eq 0 ]]; then
    log_warning "No directories found to research"
    exit 0
  fi

  log_info "Found ${#DIRS[@]} key directories: ${DIRS[*]}"

  if [[ "$DRY_RUN" = true ]]; then
    log_warning "DRY RUN - Would execute research on: ${DIRS[*]}"
    exit 0
  fi

  # Create output directory
  mkdir -p "$OUTPUT_DIR/references"

  # Execute research with Claude Code - let agent decide research strategy
  log_info "Launching research agent with full autonomy..."

  RESEARCH_PROMPT="You are conducting deep research on this codebase to create comprehensive documentation.

**Key directories identified**: ${DIRS[*]}

**Your Task**:
Perform systematic research of this codebase and create a comprehensive CLAUDE.md file. You have complete freedom to:

1. **Choose your research approach** - Use subagents (via Task tool), direct exploration, or any combination
2. **Determine research scope** - Focus on what's most important, not necessarily every directory
3. **Structure findings** - Organize information in the most useful way
4. **Prioritize depth** - Deep analysis of critical areas > shallow coverage of everything

**Expected Output** (CLAUDE.md should include):
- Project overview and purpose
- Architecture and key components
- Directory structure and organization
- Important files and their roles
- Patterns, conventions, and design decisions
- Dependencies and relationships
- Technical debt and recommendations
- Quick start guide for contributors

**Guidelines**:
- Use specific file references (file:line format)
- Focus on actionable insights
- Highlight security issues or critical problems
- Be thorough but concise

You have access to all tools. Decide the best research strategy and execute it."

  # Execute with output capture
  if RESULT=$(claude -p "$RESEARCH_PROMPT" \
                     --permission-mode plan 2>&1); then

    log_success "Research completed successfully"

    # Check if CLAUDE.md was created by the agent
    if [[ -f "$OUTPUT_DIR/CLAUDE.md" ]]; then
      log_success "CLAUDE.md created by research agent"
    else
      log_warning "CLAUDE.md not found - saving agent output"
      echo "$RESULT" > "$OUTPUT_DIR/CLAUDE.md"
    fi

  else
    log_error "Research failed"
    echo "$RESULT"
    exit 1
  fi

  # Note: Agent files (.claude/agents/) are NOT auto-generated
  # The research agent can create them if needed based on its analysis
  
  # Update .roomodes with codebase-researcher mode
  log_info "Updating .roomodes with codebase knowledge..."
  
  python3 <<PYTHON
import json
import sys

roomodes_path = "$PROJECT_ROOT/.roomodes"

try:
    with open(roomodes_path, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"customModes": []}

# Check if codebase-researcher mode exists
existing_mode = next((m for m in config['customModes'] if m['slug'] == 'codebase-researcher'), None)

if existing_mode:
    # Update existing mode to reference skill
    existing_mode['skill_ref'] = {
        'path': '.roo/skills/codebase-researcher/SKILL.md',
        'merge_strategy': 'override'
    }
    print("Updated existing codebase-researcher mode", file=sys.stderr)
else:
    # Add new mode
    new_mode = {
        'slug': 'codebase-researcher',
        'name': '🔍 Codebase Researcher',
        'roleDefinition': 'You perform systematic deep research of codebases using the standard algorithm: start at root level and analyze each important directory with specialized subagents.',
        'skill_ref': {
            'path': '.roo/skills/codebase-researcher/SKILL.md',
            'merge_strategy': 'override'
        },
        'groups': ['read', 'edit', 'command'],
        'source': 'project'
    }
    config['customModes'].append(new_mode)
    print("Added new codebase-researcher mode", file=sys.stderr)

# Save updated config
with open(roomodes_path, 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')

print(f"Updated {roomodes_path}", file=sys.stderr)
PYTHON
  
  log_success "Research complete!"
  echo ""
  log_info "Generated artifacts:"
  echo "  📄 $OUTPUT_DIR/CLAUDE.md - Project knowledge base"
  echo "  ⚙️  .roomodes - Updated configuration"
  echo ""
  log_info "Next steps:"
  echo "  1. Review CLAUDE.md for comprehensive project understanding"
  echo "  2. Use the codebase knowledge for development"
}

# Run main function
main "$@"