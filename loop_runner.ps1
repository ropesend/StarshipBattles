# Stateless Refactor Loop Runner (PowerShell Version)
# Executes Claude CLI in a loop, one phase at a time, until all tasks complete

$ErrorActionPreference = "Stop"

# Configuration
$PLAN_FILE = "refactor_plan.md"
$WORKSPACE_DIR = "C:/Dev/Starship Battles"
$SLEEP_DURATION = 10
$MAX_ITERATIONS = 1000

# Colors
function Write-Info ($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success ($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warning ($msg) { Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-ErrorLog ($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Check properties
if (-not (Test-Path $PLAN_FILE)) {
    Write-ErrorLog "Plan file not found: $PLAN_FILE"
    exit 1
}

Write-Info "Starting Stateless Refactor Loop"
Write-Info "Plan file: $PLAN_FILE"
Write-Info "Workspace: $WORKSPACE_DIR"
Write-Host ""

$iteration = 0

while ($iteration -lt $MAX_ITERATIONS) {
    $iteration++
    
    Write-Host ""
    Write-Info "========================================="
    Write-Info "Iteration $iteration"
    Write-Info "========================================="

    # Check completion
    try {
        python Projects/scripts/check_completion.py "$PLAN_FILE"
        if ($LASTEXITCODE -eq 0) {
            Write-Success "All projects complete! 🎉"
            Write-Success "Total iterations: $iteration"
            exit 0
        }
    } catch {
        Write-Warning "Check completion script failed to run properly"
    }

    Write-Info "Checking for next work item..."
    Write-Info "Starting Claude CLI session..."
    Write-Host ""

    # Run Claude CLI
    try {
        # Using cmd /c ensuring proper execution of the claude.cmd batch file if present
        # and handling the arguments correctly
        claude `
            --dangerously-skip-user-approval `
            --system-prompt-file WORKER.md `
            -p "Follow Protocol 08 (Automated Loop). Read refactor_plan.md. Execute next work item (phase or audit). Update plan. Commit. Exit."
            
        if ($LASTEXITCODE -ne 0) {
            throw "Claude CLI exited with error code $LASTEXITCODE"
        }
    } catch {
        Write-ErrorLog "Claude CLI failed: $_"
        Write-Warning "Check output above for errors"
        Write-Info "You can manually fix issues and restart"
        exit 1
    }

    Write-Host ""
    Write-Success "Claude session completed"

    # Verify git changes
    $gitStatus = git diff --quiet HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Success "Changes detected in git"
    } else {
        Write-Warning "No changes detected - this might indicate an issue or purely metadata update"
        Write-Info "Checking plan file for updates..."
    }

    Write-Info "Waiting ${SLEEP_DURATION}s before next iteration..."
    Start-Sleep -Seconds $SLEEP_DURATION
}

Write-ErrorLog "Maximum iterations ($MAX_ITERATIONS) reached"
exit 1
