#!/bin/bash

# Stateless Refactor Loop Runner
# Executes Claude CLI in a loop, one phase at a time, until all tasks complete

set -e  # Exit on error

# Configuration
PLAN_FILE="refactor_loop/refactor_plan.md"
WORKSPACE_DIR="C:/Dev/Starship Battles"
SLEEP_DURATION=10
MAX_ITERATIONS=1000  # Safety limit

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if plan file exists
if [ ! -f "$PLAN_FILE" ]; then
    log_error "Plan file not found: $PLAN_FILE"
    exit 1
fi

log_info "Starting Stateless Refactor Loop"
log_info "Plan file: $PLAN_FILE"
log_info "Workspace: $WORKSPACE_DIR"
echo ""

iteration=0

while [ $iteration -lt $MAX_ITERATIONS ]; do
    iteration=$((iteration + 1))
    
    echo ""
    log_info "========================================="
    log_info "Iteration $iteration"
    log_info "========================================="
    
    # Check if all projects are complete
    if python Projects/scripts/check_completion.py "$PLAN_FILE"; then
        log_success "All projects complete! 🎉"
        log_success "Total iterations: $iteration"
        exit 0
    fi
    
    # Display current status
    log_info "Checking for next work item..."
    
    # Run Claude CLI in YOLO mode with WORKER.md system prompt
    log_info "Starting Claude CLI session..."
    echo ""
    
    # Use --system-prompt-file to load refactor_loop/WORKER.md instead of CLAUDE.md
    # This ensures the CLI agent is a "Worker Drone" (silent, obedient, rigid)
    # while VS Code sessions use CLAUDE.md as a "Consultant" (chatty, helpful)
    #
    # The prompt tells Claude to follow Protocol 08 for automated loop execution
    # This includes:
    # - Reading refactor_loop/refactor_plan.md
    # - Finding next incomplete project
    # - Executing next phase OR running audit if project complete
    # - Updating plan and exiting
    claude \
        --dangerously-skip-permissions \
        --system-prompt-file refactor_loop/WORKER.md \
        -p "Follow Protocol 08 (Automated Loop). Read refactor_loop/refactor_plan.md. Execute next work item (phase or audit). Update plan. Commit. Exit." \
        || {
            log_error "Claude CLI failed with exit code $?"
            log_warning "Check the output above for errors"
            log_info "You can manually fix issues and restart the loop"
            exit 1
        }
    
    echo ""
    log_success "Claude session completed"
    
    # Verify changes were made
    if git diff --quiet HEAD; then
        log_warning "No changes detected - this might indicate an issue"
        log_info "Checking plan file for updates..."
    else
        log_success "Changes detected in git"
    fi
    
    # Sleep to ensure file locks are cleared and system is stable
    log_info "Waiting ${SLEEP_DURATION}s before next iteration..."
    sleep $SLEEP_DURATION
done

log_error "Maximum iterations ($MAX_ITERATIONS) reached"
log_warning "This might indicate an infinite loop or stuck task"
log_info "Check refactor_loop/refactor_plan.md Agent Context for details"
exit 1
