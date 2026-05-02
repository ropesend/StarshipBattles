# Stateless Refactor Loop Runner (PowerShell Version)
# Executes Claude CLI in a loop, one phase at a time, until all tasks complete

$ErrorActionPreference = "Stop"

# Configuration
$PLAN_FILE = "Projects/refactor_loop/refactor_plan.md"
$WORKSPACE_DIR = "C:/Dev/Starship Battles"
$SLEEP_DURATION = 10
$MAX_ITERATIONS = 1000
$MAX_RETRIES = 3
$CLAUDE_TEMP_DIR = "$env:LOCALAPPDATA\Temp\claude\C--Dev-Starship-Battles"

# Colors
function Write-Info ($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success ($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warning ($msg) { Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-ErrorLog ($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Clean up temp files to prevent EPERM errors
function Clear-ClaudeTempFiles {
    if (Test-Path $CLAUDE_TEMP_DIR) {
        try {
            Remove-Item -Path "$CLAUDE_TEMP_DIR\tasks\*" -Force -ErrorAction SilentlyContinue
            Write-Info "Cleaned temp files"
        }
        catch {
            Write-Warning "Could not clean temp files (may be in use)"
        }
    }
}

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
    }
    catch {
        Write-Warning "Check completion script failed to run properly"
    }

    Write-Info "Checking for next work item..."
    Write-Info "Starting Claude CLI session..."
    Write-Host ""

    # Run Claude CLI with retry logic for EPERM errors
    $retryCount = 0
    $success = $false

    while (-not $success -and $retryCount -lt $MAX_RETRIES) {
        # Clean temp files before each attempt
        if ($retryCount -gt 0) {
            Write-Warning "Retry attempt $($retryCount + 1) of $MAX_RETRIES..."
            Clear-ClaudeTempFiles
            Start-Sleep -Seconds 5
        }

        # Capture output to check for EPERM in JSON error responses
        $claudeOutput = claude `
            --dangerously-skip-permissions `
            --system-prompt-file Projects/refactor_loop/WORKER.md `
            -p "Follow Protocol 08 (Automated Loop). Read Projects/refactor_loop/refactor_plan.md. Execute next work item (phase or audit). Update plan. Commit. Exit. BE AGGRESSIVELY VOCAL about your progress." 2>&1 | Out-String

        $claudeExitCode = $LASTEXITCODE

        # Display the output
        if ($claudeOutput) {
            Write-Host $claudeOutput
        }

        if ($claudeExitCode -eq 0) {
            $success = $true
        }
        elseif ($claudeOutput -match "prompt is too long" -or $claudeOutput -match "Conversation too long") {
            # Context window overflow — not retryable, needs manual intervention
            Write-ErrorLog "Context window overflow detected. The conversation exceeded the API token limit."
            Write-Warning "Likely cause: Projects/refactor_loop/refactor_plan.md execution log is too large."
            Write-Warning "Fix: Trim the execution log (archive old rows) and restart."
            exit 1
        }
        elseif ($claudeOutput -match "EPERM" -or $claudeOutput -match "operation not permitted" -or $claudeOutput -match "symlink") {
            $retryCount++
            Write-Warning "EPERM/symlink error detected (Windows file permission issue). Cleaning up..."
            Clear-ClaudeTempFiles
        }
        elseif ($claudeOutput -match "only prompt commands are supported in streaming mode" -and $claudeOutput -match '"num_turns":0') {
            # Claude failed on startup before doing any work — safe to retry
            $retryCount++
            Write-Warning "Claude CLI startup error (streaming mode). Retrying..."
            Clear-ClaudeTempFiles
        }
        else {
            # Unknown error, fail immediately
            Write-ErrorLog "Claude CLI failed with exit code $claudeExitCode"
            Write-Warning "Check output above for errors"
            Write-Info "You can manually fix issues and restart"
            exit 1
        }
    }

    if (-not $success) {
        Write-ErrorLog "Failed after $MAX_RETRIES retries due to persistent startup errors"
        Write-Info "Try enabling Windows Developer Mode (Settings > System > For developers)"
        Write-Info "Or run PowerShell as Administrator"
        Write-Info "Or update Claude Code: npm update -g @anthropic-ai/claude-code"
        exit 1
    }

    Write-Host ""
    Write-Success "Claude session completed"

    # Verify git changes
    $gitStatus = git diff --quiet HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Success "Changes detected in git"
    }
    else {
        Write-Warning "No changes detected - this might indicate an issue or purely metadata update"
        Write-Info "Checking plan file for updates..."
    }

    Write-Info "Waiting ${SLEEP_DURATION}s before next iteration..."
    Start-Sleep -Seconds $SLEEP_DURATION
}

Write-ErrorLog "Maximum iterations ($MAX_ITERATIONS) reached"
exit 1
