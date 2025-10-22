#!/bin/bash
# feynman-batch.sh - Batch executor for sequential-feynman workflow
# Usage: ./feynman-batch.sh <topic> [iterations] [options]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_BASE_DIR="${PROJECT_ROOT}/feynman-batch-outputs"
MAX_RETRIES=3
TIMEOUT_SECONDS=14400  # 4 hours per iteration
CONCURRENCY_LIMIT=1    # Default: sequential execution

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage information
usage() {
    cat <<EOF
Usage: $0 <topic> [iterations] [options]

Arguments:
  topic           Topic to research (required)
  iterations      Number of iterations to run (default: 1)

Options:
  --parallel N    Run N iterations in parallel (default: 1)
  --output DIR    Output directory (default: feynman-batch-outputs)
  --timeout SEC   Timeout per iteration in seconds (default: 14400)
  --retries N     Max retries per iteration (default: 3)
  --help          Show this help message

Examples:
  $0 "distributed tracing systems"
  $0 "React Server Components" 3
  $0 "MCP architecture" 5 --parallel 2
  $0 "WebAssembly optimization" 3 --output ./research

Environment Variables:
  CLAUDE_API_KEY  API key for Claude (required)

EOF
    exit 1
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Parse arguments
TOPIC=""
ITERATIONS=1

while [[ $# -gt 0 ]]; do
    case $1 in
        --parallel)
            CONCURRENCY_LIMIT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_BASE_DIR="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT_SECONDS="$2"
            shift 2
            ;;
        --retries)
            MAX_RETRIES="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            ;;
        *)
            if [[ -z "$TOPIC" ]]; then
                TOPIC="$1"
            elif [[ "$ITERATIONS" == "1" ]]; then
                ITERATIONS="$1"
            else
                log_error "Unexpected argument: $1"
                usage
            fi
            shift
            ;;
    esac
done

# Validate inputs
if [[ -z "$TOPIC" ]]; then
    log_error "Topic is required"
    usage
fi

if ! [[ "$ITERATIONS" =~ ^[0-9]+$ ]] || [[ "$ITERATIONS" -lt 1 ]]; then
    log_error "Iterations must be a positive integer"
    exit 1
fi

# Check for claude CLI
if ! command -v claude &> /dev/null; then
    log_error "claude CLI not found. Please install Claude Code."
    exit 1
fi

# Generate run ID
RUN_ID="$(date +%Y%m%d-%H%M%S)-$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | cut -c1-30)"
RUN_DIR="${OUTPUT_BASE_DIR}/${RUN_ID}"
STATUS_FILE="${RUN_DIR}/STATUS.json"

# Create output directory
mkdir -p "$RUN_DIR"

# Initialize status file
init_status() {
    cat > "$STATUS_FILE" <<EOF
{
  "run_id": "$RUN_ID",
  "topic": "$TOPIC",
  "iterations": $ITERATIONS,
  "concurrency": $CONCURRENCY_LIMIT,
  "status": "running",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "completed_at": null,
  "progress": {
    "completed": 0,
    "failed": 0,
    "running": 0,
    "total": $ITERATIONS
  },
  "iterations_status": []
}
EOF
}

# Update status file
update_status() {
    local iteration=$1
    local status=$2
    local message=${3:-""}
    
    # Read current status
    local temp_file=$(mktemp)
    jq --arg iter "$iteration" \
       --arg status "$status" \
       --arg msg "$message" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.iterations_status += [{
           iteration: ($iter | tonumber),
           status: $status,
           message: $msg,
           timestamp: $timestamp
       }]' "$STATUS_FILE" > "$temp_file"
    mv "$temp_file" "$STATUS_FILE"
}

# Finalize status
finalize_status() {
    local final_status=$1
    local temp_file=$(mktemp)
    jq --arg status "$final_status" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.status = $status | .completed_at = $timestamp' \
       "$STATUS_FILE" > "$temp_file"
    mv "$temp_file" "$STATUS_FILE"
}

# Run single iteration
run_iteration() {
    local iteration=$1
    local iter_dir="${RUN_DIR}/iteration-${iteration}"
    local log_file="${iter_dir}/execution.log"
    local output_file="${iter_dir}/output.json"
    
    mkdir -p "$iter_dir"
    
    log_info "Starting iteration $iteration/$ITERATIONS: $TOPIC"
    update_status "$iteration" "running" "Started"
    
    local attempt=1
    local success=false
    
    while [[ $attempt -le $MAX_RETRIES ]] && [[ "$success" == "false" ]]; do
        log_info "Iteration $iteration - Attempt $attempt/$MAX_RETRIES"
        
        # Run claude with timeout
        if timeout "$TIMEOUT_SECONDS" claude -p "/sequential-feynman $TOPIC" \
            --output-format json \
            --allowedTools "Read,Write,Edit,Bash,Grep,Glob,WebSearch,TodoWrite,NotebookEdit" \
            --permission-mode acceptEdits \
            > "$output_file" 2> "$log_file"; then
            
            success=true
            log_success "Iteration $iteration completed successfully"
            update_status "$iteration" "completed" "Success"
            
            # Collect artifacts
            collect_artifacts "$iteration" "$iter_dir"
            
        else
            local exit_code=$?
            if [[ $exit_code -eq 124 ]]; then
                log_warning "Iteration $iteration timed out (attempt $attempt/$MAX_RETRIES)"
                update_status "$iteration" "timeout" "Timeout on attempt $attempt"
            else
                log_warning "Iteration $iteration failed with exit code $exit_code (attempt $attempt/$MAX_RETRIES)"
                update_status "$iteration" "failed" "Failed on attempt $attempt with exit code $exit_code"
            fi
            
            attempt=$((attempt + 1))
            if [[ $attempt -le $MAX_RETRIES ]]; then
                log_info "Retrying in 10 seconds..."
                sleep 10
            fi
        fi
    done
    
    if [[ "$success" == "false" ]]; then
        log_error "Iteration $iteration failed after $MAX_RETRIES attempts"
        update_status "$iteration" "failed" "Failed after $MAX_RETRIES attempts"
        return 1
    fi
    
    return 0
}

# Collect artifacts from workspace
collect_artifacts() {
    local iteration=$1
    local iter_dir=$2
    local artifacts_dir="${iter_dir}/artifacts"
    
    mkdir -p "$artifacts_dir"
    
    # Collect notebooks
    if [[ -d "${PROJECT_ROOT}/notebooks" ]]; then
        find "${PROJECT_ROOT}/notebooks" -name "feynman-*.ipynb" -newer "$STATUS_FILE" \
            -exec cp {} "${artifacts_dir}/" \; 2>/dev/null || true
    fi
    
    # Collect skills
    if [[ -d "${PROJECT_ROOT}/.claude/skills" ]]; then
        find "${PROJECT_ROOT}/.claude/skills" -type d -newer "$STATUS_FILE" \
            -exec cp -r {} "${artifacts_dir}/" \; 2>/dev/null || true
    fi
    
    # Create metadata
    cat > "${artifacts_dir}/metadata.json" <<EOF
{
  "iteration": $iteration,
  "topic": "$TOPIC",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "artifacts": $(find "$artifacts_dir" -type f | wc -l | tr -d ' ')
}
EOF
    
    log_info "Collected artifacts for iteration $iteration"
}

# Generate summary report
generate_report() {
    local report_file="${RUN_DIR}/REPORT.md"
    
    log_info "Generating summary report..."
    
    # Count successes and failures
    local completed=$(jq '[.iterations_status[] | select(.status == "completed")] | length' "$STATUS_FILE")
    local failed=$(jq '[.iterations_status[] | select(.status == "failed")] | length' "$STATUS_FILE")
    
    cat > "$report_file" <<EOF
# Sequential Feynman Batch Report

## Summary

- **Topic**: $TOPIC
- **Run ID**: $RUN_ID
- **Total Iterations**: $ITERATIONS
- **Completed**: $completed
- **Failed**: $failed
- **Started**: $(jq -r '.started_at' "$STATUS_FILE")
- **Completed**: $(jq -r '.completed_at' "$STATUS_FILE")

## Execution Status

| Iteration | Status | Message | Timestamp |
|-----------|--------|---------|-----------|
EOF
    
    # Add iteration details
    jq -r '.iterations_status[] | "| \(.iteration) | \(.status) | \(.message) | \(.timestamp) |"' \
        "$STATUS_FILE" >> "$report_file"
    
    cat >> "$report_file" <<EOF

## Artifacts

EOF
    
    # List artifacts per iteration
    for i in $(seq 1 "$ITERATIONS"); do
        local iter_dir="${RUN_DIR}/iteration-${i}"
        if [[ -d "$iter_dir/artifacts" ]]; then
            echo "### Iteration $i" >> "$report_file"
            echo "" >> "$report_file"
            find "$iter_dir/artifacts" -type f -exec basename {} \; | sort | \
                sed 's/^/- /' >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
    
    cat >> "$report_file" <<EOF

## Output Location

All outputs are stored in: \`$RUN_DIR\`

## Next Steps

1. Review notebooks in \`iteration-*/artifacts/\`
2. Compare insights across iterations
3. Integrate validated skills into \`.claude/skills/\`
4. Archive or clean up outputs

---

*Generated by feynman-batch.sh on $(date)*
EOF
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log_info "=== Sequential Feynman Batch Executor ==="
    log_info "Topic: $TOPIC"
    log_info "Iterations: $ITERATIONS"
    log_info "Concurrency: $CONCURRENCY_LIMIT"
    log_info "Output: $RUN_DIR"
    echo ""
    
    # Initialize
    init_status
    
    # Track overall success
    local total_failed=0
    
    # Run iterations
    if [[ $CONCURRENCY_LIMIT -eq 1 ]]; then
        # Sequential execution
        for i in $(seq 1 "$ITERATIONS"); do
            if ! run_iteration "$i"; then
                total_failed=$((total_failed + 1))
            fi
        done
    else
        # Parallel execution with limit
        log_info "Running with concurrency limit: $CONCURRENCY_LIMIT"
        
        local pids=()
        for i in $(seq 1 "$ITERATIONS"); do
            # Wait if at concurrency limit
            while [[ ${#pids[@]} -ge $CONCURRENCY_LIMIT ]]; do
                for pid_idx in "${!pids[@]}"; do
                    if ! kill -0 "${pids[$pid_idx]}" 2>/dev/null; then
                        wait "${pids[$pid_idx]}" || total_failed=$((total_failed + 1))
                        unset 'pids[$pid_idx]'
                    fi
                done
                sleep 1
            done
            
            # Start iteration in background
            run_iteration "$i" &
            pids+=($!)
        done
        
        # Wait for remaining
        for pid in "${pids[@]}"; do
            wait "$pid" || total_failed=$((total_failed + 1))
        done
    fi
    
    # Finalize
    if [[ $total_failed -eq 0 ]]; then
        finalize_status "completed"
        log_success "All iterations completed successfully!"
    else
        finalize_status "partial"
        log_warning "$total_failed/$ITERATIONS iterations failed"
    fi
    
    # Generate report
    generate_report
    
    echo ""
    log_info "=== Execution Complete ==="
    log_info "Results: $RUN_DIR"
    log_info "Report: ${RUN_DIR}/REPORT.md"
    log_info "Status: ${RUN_DIR}/STATUS.json"
    
    exit $total_failed
}

# Run main
main
