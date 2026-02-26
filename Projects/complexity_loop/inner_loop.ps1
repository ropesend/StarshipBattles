# Complexity Loop - Inner Loop (Project Execution)
# Executes Claude CLI in a loop using Projects/complexity_loop/cycle_plan.md
# One phase at a time, until the project is complete.
#
# Exit codes:
#   0 = Project complete
#   1 = Fatal error (test failure, stuck, unknown error)
#   2 = Rate limit detected (outer loop should sleep and retry)
#   3 = Project skipped (function deemed irreducible)

$ErrorActionPreference = "Continue"

# Configuration
$PLAN_FILE = "Projects/complexity_loop/cycle_plan.md"
$WORKER_PROMPT = "Projects/complexity_loop/REFACTOR_WORKER.md"
$WORKSPACE_DIR = "C:/Dev/Starship Battles"
$TRIM_SCRIPT = "Projects/complexity_loop/trim_execution_log.py"
$CHECK_SCRIPT = "Projects/complexity_loop/check_completion.py"
$SLEEP_DURATION = 10
$MAX_ITERATIONS = 200
$MAX_RETRIES = 5
$CLAUDE_TEMP_DIR = "$env:LOCALAPPDATA\Temp\claude\C--Dev-Starship-Battles"

# Rate limit patterns
$RATE_LIMIT_PATTERNS = @(
    "rate.limit",
    "rate_limit",
    "overloaded",
    "too many requests",
    "Resource has been exhausted",
    "HTTP 429",
    "status.+429",
    "error.+529"
)

# Colors
function Write-Info ($msg) { Write-Host "[INNER] $msg" -ForegroundColor Cyan }
function Write-Success ($msg) { Write-Host "[INNER] $msg" -ForegroundColor Green }
function Write-Warn ($msg) { Write-Host "[INNER] $msg" -ForegroundColor Yellow }
function Write-ErrorLog ($msg) { Write-Host "[INNER] $msg" -ForegroundColor Red }

# Clean up temp files to prevent EPERM errors
function Clear-ClaudeTempFiles {
    if (Test-Path $CLAUDE_TEMP_DIR) {
        try {
            Remove-Item -Path "$CLAUDE_TEMP_DIR\tasks\*" -Force -ErrorAction SilentlyContinue
            $cutoff = (Get-Date).AddHours(-1)
            Get-ChildItem -Path $CLAUDE_TEMP_DIR -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match "^[0-9a-f]{8}-" -and $_.LastWriteTime -lt $cutoff } |
                ForEach-Object {
                    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
                }
            Write-Info "Cleaned temp files"
        }
        catch {
            Write-Warn "Could not clean temp files (may be in use)"
        }
    }
}

function Test-RateLimit ($output) {
    foreach ($pattern in $RATE_LIMIT_PATTERNS) {
        if ($output -match $pattern) {
            return $true
        }
    }
    return $false
}

function Test-ProjectSkipped ($output) {
    # Check if the agent marked the project as skipped
    if ($output -match "irreducib" -or $output -match "marked.*\[~\]" -or $output -match "skip.*list") {
        return $true
    }
    return $false
}

# Verify files exist
if (-not (Test-Path $PLAN_FILE)) {
    Write-ErrorLog "Cycle plan file not found: $PLAN_FILE"
    exit 1
}
if (-not (Test-Path $WORKER_PROMPT)) {
    Write-ErrorLog "Worker prompt not found: $WORKER_PROMPT"
    exit 1
}

Write-Info "Starting Complexity Loop Inner Loop"
Write-Info "Plan file: $PLAN_FILE"
Write-Info "Worker prompt: $WORKER_PROMPT"
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
        python $CHECK_SCRIPT --plan-file $PLAN_FILE
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Project complete!"
            Write-Success "Total iterations: $iteration"
            exit 0
        }
    }
    catch {
        Write-Warn "Check completion script failed"
    }

    # Check if plan shows project as skipped [~]
    $planContent = Get-Content $PLAN_FILE -Raw -Encoding UTF8
    if ($planContent -match "- \[~\] \*\*PROJ-") {
        Write-Warn "Project was marked as skipped (irreducible complexity)"
        exit 3
    }

    Write-Info "Executing next phase..."
    Write-Host ""

    # Run Claude CLI with retry logic
    $retryCount = 0
    $success = $false

    while (-not $success -and $retryCount -lt $MAX_RETRIES) {
        if ($retryCount -gt 0) {
            Write-Warn "Retry attempt $($retryCount + 1) of $MAX_RETRIES..."
            Clear-ClaudeTempFiles
            Start-Sleep -Seconds 5
        }

        $claudeOutput = claude `
            --dangerously-skip-permissions `
            --system-prompt-file $WORKER_PROMPT `
            -p "Follow Protocol 08 (Automated Loop). Read Projects/complexity_loop/cycle_plan.md. Execute next work item (phase or audit). Update plan. Commit. Exit. BE AGGRESSIVELY VOCAL about your progress." 2>&1 | Out-String

        $claudeExitCode = $LASTEXITCODE

        if ($claudeOutput) {
            Write-Host $claudeOutput
        }

        if ($claudeExitCode -eq 0) {
            $success = $true

            # Check if the agent decided to skip
            if (Test-ProjectSkipped $claudeOutput) {
                Write-Warn "Agent signaled skip during execution"
                exit 3
            }
        }
        elseif (Test-RateLimit $claudeOutput) {
            Write-Warn "Rate limit detected"
            exit 2
        }
        elseif ($claudeOutput -match "prompt is too long" -or $claudeOutput -match "Conversation too long" -or $claudeOutput -match "context window" -or $claudeOutput -match "token limit") {
            Write-Warn "Context window overflow. Trimming execution log..."
            try {
                python $TRIM_SCRIPT --plan-file $PLAN_FILE --keep 10
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Execution log trimmed. Retrying..."
                    $retryCount++
                    Clear-ClaudeTempFiles
                }
                else {
                    Write-ErrorLog "Failed to trim execution log"
                    exit 1
                }
            }
            catch {
                Write-ErrorLog "Trim script failed: $_"
                exit 1
            }
        }
        elseif ($claudeOutput -match "EPERM" -or $claudeOutput -match "operation not permitted" -or $claudeOutput -match "symlink") {
            $retryCount++
            Write-Warn "EPERM/symlink error. Cleaning up..."
            Clear-ClaudeTempFiles
        }
        elseif ($claudeOutput -match "only prompt commands are supported in streaming mode" -and $claudeOutput -match '"num_turns":0') {
            $retryCount++
            Write-Warn "Claude CLI startup error. Retrying..."
            Clear-ClaudeTempFiles
        }
        else {
            $retryCount++
            Write-Warn "Claude CLI failed with exit code $claudeExitCode (attempt $retryCount/$MAX_RETRIES)"
            if ($retryCount -lt $MAX_RETRIES) {
                $backoff = $retryCount * 30
                Write-Info "Retrying in ${backoff}s..."
                Start-Sleep -Seconds $backoff
                Clear-ClaudeTempFiles
            }
        }
    }

    if (-not $success) {
        Write-ErrorLog "Failed after $MAX_RETRIES retries"
        exit 1
    }

    Write-Host ""
    Write-Success "Claude session completed"

    # Verify git changes
    git diff --quiet HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Success "Changes detected in git"
    }
    else {
        Write-Warn "No changes detected"
    }

    Write-Info "Waiting ${SLEEP_DURATION}s before next iteration..."
    Start-Sleep -Seconds $SLEEP_DURATION
}

Write-ErrorLog "Maximum iterations ($MAX_ITERATIONS) reached"
exit 1
