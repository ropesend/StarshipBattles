# Continuous Improvement Loop - Outer Loop Orchestrator
#
# Manages the full sweep-execute-merge cycle:
#   1. Create a git branch for the cycle
#   2. Run sweep-all via Claude CLI (SWEEP_WORKER.md)
#   3. Auto-approve all projects
#   4. Build cycle_plan.md from new projects
#   5. Run inner loop to execute all projects
#   6. Merge branch to main
#   7. Repeat
#
# Usage:
#   cd "C:\Dev\Starship Battles"
#   .\Projects\continuous_loop\continuous_loop.ps1
#
# Safety:
#   - Max 10 cycles (configurable)
#   - Max 48 hours runtime (configurable)
#   - Stops if sweep finds < 20 findings (diminishing returns)
#   - Stops after 3 consecutive inner loop failures
#   - Never force-pushes or destructively modifies main
#   - Rate limit detection with 15-minute sleep + retry

$ErrorActionPreference = "Continue"

# ═══════════════════════════════════════════════════════
# TRANSCRIPT LOGGING
# ═══════════════════════════════════════════════════════

$LOG_DIR = "Projects/continuous_loop/logs"
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}
$logTimestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$LOG_FILE = "$LOG_DIR/continuous_loop_$logTimestamp.log"
Start-Transcript -Path $LOG_FILE -Append
Write-Host "[LOG] Transcript started: $LOG_FILE"

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════

$MAX_CYCLES = 10
$MAX_RUNTIME_HOURS = 48
$RATE_LIMIT_SLEEP_MINUTES = 15
$MIN_FINDINGS_THRESHOLD = 20
$MAX_CONSECUTIVE_FAILURES = 3
$INTER_CYCLE_SLEEP_SECONDS = 30

$WORKSPACE = "C:/Dev/Starship Battles"
$CYCLE_PLAN_FILE = "Projects/continuous_loop/cycle_plan.md"
$STATE_FILE = "Projects/continuous_loop/cycle_state.json"
$SWEEP_WORKER = "Projects/continuous_loop/SWEEP_WORKER.md"
$INNER_LOOP_SCRIPT = "Projects/continuous_loop/inner_loop.ps1"
$POPULATE_SCRIPT = "Projects/continuous_loop/populate_cycle_plan.py"

$CLAUDE_TEMP_DIR = "$env:LOCALAPPDATA\Temp\claude\C--Dev-Starship-Battles"

# Rate limit patterns (text patterns only - bare "429"/"529" caused false positives
# matching test counts like "5290 tests passed" or finding IDs like "DUP-UI1-429")
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

# ═══════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════

function Write-Info ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts LOOP] $msg" -ForegroundColor Cyan
}
function Write-Success ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts LOOP] $msg" -ForegroundColor Green
}
function Write-Warn ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts LOOP] $msg" -ForegroundColor Yellow
}
function Write-ErrorLog ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts LOOP] $msg" -ForegroundColor Red
}
function Write-Banner ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host ""
    Write-Host "[$ts LOOP] ======================================================" -ForegroundColor Magenta
    Write-Host "[$ts LOOP]   $msg" -ForegroundColor Magenta
    Write-Host "[$ts LOOP] ======================================================" -ForegroundColor Magenta
    Write-Host ""
}

# ═══════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════

function Load-CycleState {
    if (Test-Path $STATE_FILE) {
        try {
            $content = Get-Content $STATE_FILE -Raw -Encoding UTF8
            return $content | ConvertFrom-Json
        }
        catch {
            Write-Warn "Failed to parse cycle_state.json. Starting fresh."
        }
    }

    # Create initial state
    return [PSCustomObject]@{
        current_cycle          = 0
        start_time             = (Get-Date).ToString("o")
        status                 = "idle"
        consecutive_failures   = 0
        cycles                 = @()
        rate_limit_events      = @()
    }
}

function Save-CycleState ($state) {
    $state | ConvertTo-Json -Depth 5 | Set-Content $STATE_FILE -Encoding UTF8
}

# ═══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

function Test-RateLimit ($output) {
    foreach ($pattern in $RATE_LIMIT_PATTERNS) {
        if ($output -match $pattern) {
            return $true
        }
    }
    return $false
}

function Clear-ClaudeTempFiles {
    if (Test-Path $CLAUDE_TEMP_DIR) {
        try {
            # Clean task queue
            Remove-Item -Path "$CLAUDE_TEMP_DIR\tasks\*" -Force -ErrorAction SilentlyContinue

            # Purge old session directories (UUID-named) older than 1 hour.
            # Stale sessions from crashed CLI invocations can accumulate and
            # cause EPERM errors or prevent new sessions from starting.
            $cutoff = (Get-Date).AddHours(-1)
            Get-ChildItem -Path $CLAUDE_TEMP_DIR -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match "^[0-9a-f]{8}-" -and $_.LastWriteTime -lt $cutoff } |
                ForEach-Object {
                    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
                }
        }
        catch { }
    }
}

function Invoke-RateLimitSleep ($state, $phase) {
    Write-Warn "Rate limit detected during $phase. Sleeping $RATE_LIMIT_SLEEP_MINUTES minutes..."

    $event = [PSCustomObject]@{
        timestamp = (Get-Date).ToString("o")
        phase     = $phase
        sleep_minutes = $RATE_LIMIT_SLEEP_MINUTES
    }
    $state.rate_limit_events += $event
    Save-CycleState $state

    Start-Sleep -Seconds ($RATE_LIMIT_SLEEP_MINUTES * 60)
    Write-Info "Resuming after rate limit sleep."
}

function Get-LatestApprovalLog {
    $logs = Get-ChildItem "Reviews/results" -Recurse -Filter "approval_log.md" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending
    if ($logs.Count -gt 0) {
        return $logs[0]
    }
    return $null
}

function Get-ProjectsCreatedCount ($approvalLog) {
    if (-not $approvalLog -or -not (Test-Path $approvalLog.FullName)) {
        return 0
    }
    $content = Get-Content $approvalLog.FullName -Raw -Encoding UTF8
    $matches = [regex]::Matches($content, "PROJ-\d+")
    return $matches.Count
}

function Get-FindingsCount ($reviewFolder) {
    $reportPath = Join-Path $reviewFolder "report.md"
    if (-not (Test-Path $reportPath)) {
        return -1
    }
    $content = Get-Content $reportPath -Raw -Encoding UTF8
    # Look for "Total Issues: N" or "Total Findings: N" or count from summary
    $match = [regex]::Match($content, "Total\s+(?:Issues|Findings)[:\s]*(\d+)")
    if ($match.Success) {
        return [int]$match.Groups[1].Value
    }
    # Fallback: count individual finding IDs (pattern: XXX-YYY-NNN)
    $findingMatches = [regex]::Matches($content, "\b[A-Z]{3}-[A-Z]{2,3}-\d{3}\b")
    return $findingMatches.Count
}

function Get-LatestReviewFolder {
    # Sort by Name (YYYY-MM-DD prefix) not LastWriteTime, which can be
    # changed by OS indexing/antivirus and cause wrong folder selection.
    $folders = Get-ChildItem "Reviews/results" -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "sweep" } |
        Sort-Object Name -Descending
    if ($folders.Count -gt 0) {
        return $folders[0].FullName
    }
    return $null
}

# ═══════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════

Set-Location $WORKSPACE

# Verify prerequisites
foreach ($file in @($SWEEP_WORKER, $INNER_LOOP_SCRIPT, $POPULATE_SCRIPT)) {
    if (-not (Test-Path $file)) {
        Write-ErrorLog "Required file not found: $file"
        exit 1
    }
}

$state = Load-CycleState

# Reset start_time on fresh launch so the runtime limit counts from NOW,
# not from a previous (possibly crashed) run's original start time.
$state.start_time = (Get-Date).ToString("o")
Save-CycleState $state
$startTime = Get-Date

Write-Banner "Continuous Improvement Loop Starting"
Write-Info "Max cycles: $MAX_CYCLES"
Write-Info "Max runtime: $MAX_RUNTIME_HOURS hours"
Write-Info "Min findings threshold: $MIN_FINDINGS_THRESHOLD"
Write-Info "Starting from cycle: $($state.current_cycle)"
Write-Info "State: $($state.status)"

# ── Crash recovery ──
if ($state.status -eq "executing") {
    Write-Warn "Resuming from crashed execution phase (cycle $($state.current_cycle))"
    Write-Info "Re-running inner loop to continue project execution..."

    & "$WORKSPACE\$INNER_LOOP_SCRIPT"
    $innerExit = $LASTEXITCODE

    if ($innerExit -eq 2) {
        Invoke-RateLimitSleep $state "inner_loop_recovery"
        & "$WORKSPACE\$INNER_LOOP_SCRIPT"
        $innerExit = $LASTEXITCODE
    }

    if ($innerExit -eq 0) {
        Write-Success "Recovery: inner loop completed successfully"
        $state.consecutive_failures = 0
    }
    else {
        Write-ErrorLog "Recovery: inner loop failed (exit $innerExit)"
        $state.consecutive_failures++
    }

    # Commit and merge
    git add -A
    git commit -m "Sweep cycle $($state.current_cycle) complete (recovered)" --allow-empty 2>$null

    $currentBranch = git branch --show-current
    if ($currentBranch -ne "main") {
        git checkout main
        git merge $currentBranch --no-ff -m "Merge $currentBranch (recovered)"
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorLog "Merge conflict during recovery. Manual intervention required."
            $state.status = "merge_conflict"
            Save-CycleState $state
            exit 1
        }
    }

    $state.status = "idle"
    Save-CycleState $state
    Write-Success "Recovery complete. Proceeding to next cycle."
}
elseif ($state.status -eq "sweeping") {
    Write-Warn "Previous sweep was interrupted. Will re-run sweep in next cycle."
    # Check if we're on a branch
    $currentBranch = git branch --show-current
    if ($currentBranch -ne "main" -and $currentBranch -match "sweep-cycle") {
        Write-Info "Cleaning up interrupted branch: $currentBranch"
        git checkout main
        git branch -D $currentBranch 2>$null
    }
    $state.status = "idle"
    Save-CycleState $state
}

# ── Main cycle loop ──
while ($state.current_cycle -lt $MAX_CYCLES) {

    # Check runtime limit
    $elapsed = (Get-Date) - $startTime
    if ($elapsed.TotalHours -gt $MAX_RUNTIME_HOURS) {
        Write-Warn "Maximum runtime reached ($MAX_RUNTIME_HOURS hours). Stopping gracefully."
        $state.status = "stopped_runtime"
        Save-CycleState $state
        break
    }

    # Check consecutive failures
    if ($state.consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES) {
        Write-ErrorLog "Circuit breaker: $MAX_CONSECUTIVE_FAILURES consecutive failures. Stopping."
        $state.status = "circuit_breaker"
        Save-CycleState $state
        break
    }

    # ── Start new cycle ──
    $state.current_cycle++
    $cycleNum = $state.current_cycle
    $branchName = "sweep-cycle-$cycleNum"
    $cycleStartTime = (Get-Date).ToString("o")

    Write-Banner "CYCLE $cycleNum / $MAX_CYCLES"

    # ── Step A: Create branch ──
    Write-Info "Creating branch: $branchName"
    git checkout main 2>$null
    git checkout -b $branchName
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorLog "Failed to create branch $branchName"
        # Branch might already exist from a failed run
        git checkout $branchName 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorLog "Cannot create or switch to branch. Stopping."
            $state.status = "failed"
            Save-CycleState $state
            break
        }
    }

    # ── Step B: Run sweep ──
    $state.status = "sweeping"
    Save-CycleState $state

    $sweepSuccess = $false
    $sweepRetries = 0
    $maxSweepRetries = 3

    while (-not $sweepSuccess -and $sweepRetries -lt $maxSweepRetries) {
        Write-Info "Running codebase sweep (attempt $($sweepRetries + 1)/$maxSweepRetries)..."
        Clear-ClaudeTempFiles

        $sweepOutput = claude `
            --dangerously-skip-permissions `
            --system-prompt-file $SWEEP_WORKER `
            -p "Execute the full codebase sweep pipeline. This is cycle $cycleNum. Auto-approve ALL projects. Follow every step in SWEEP_WORKER.md. Exit when complete." 2>&1 | Out-String

        $sweepExitCode = $LASTEXITCODE

        if ($sweepOutput) {
            Write-Host $sweepOutput
        }

        if ($sweepExitCode -eq 0) {
            $sweepSuccess = $true
            Write-Success "Sweep completed successfully"
        }
        elseif (Test-RateLimit $sweepOutput) {
            Invoke-RateLimitSleep $state "sweep"
            $sweepRetries++
        }
        else {
            Write-ErrorLog "Sweep failed (exit code $sweepExitCode)"
            $sweepRetries++
            if ($sweepRetries -lt $maxSweepRetries) {
                Write-Info "Retrying sweep in 30 seconds..."
                Start-Sleep -Seconds 30
            }
        }
    }

    if (-not $sweepSuccess) {
        Write-ErrorLog "Sweep failed after $maxSweepRetries attempts. Stopping cycle."
        $state.status = "failed_sweep"
        $state.consecutive_failures++
        Save-CycleState $state

        # Clean up branch
        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    # ── Step C: Check findings (diminishing returns) ──
    $reviewFolder = Get-LatestReviewFolder
    $findingsCount = 0

    if ($reviewFolder) {
        $findingsCount = Get-FindingsCount $reviewFolder
        Write-Info "Findings count: $findingsCount"
    }

    # Check approval log for projects created
    $approvalLog = Get-LatestApprovalLog
    $projectsCreated = Get-ProjectsCreatedCount $approvalLog

    if ($projectsCreated -eq 0) {
        Write-Warn "Sweep produced 0 projects. Stopping (nothing to execute)."
        $state.status = "complete_zero_projects"
        Save-CycleState $state

        git checkout main 2>$null
        git branch -D $branchName 2>$null
        break
    }

    if ($findingsCount -ge 0 -and $findingsCount -lt $MIN_FINDINGS_THRESHOLD) {
        Write-Success "Findings ($findingsCount) below threshold ($MIN_FINDINGS_THRESHOLD). Codebase is clean!"
        $state.status = "complete_diminishing_returns"
        Save-CycleState $state

        # Still merge sweep results (projects were created)
        git add -A
        git commit -m "[Sweep] Cycle ${cycleNum}: $findingsCount findings (below threshold)" --allow-empty 2>$null
        git checkout main
        git merge $branchName --no-ff -m "Merge sweep-cycle-$cycleNum (final - diminishing returns)"
        break
    }

    Write-Info "$projectsCreated projects created. Proceeding to execution."

    # ── Step D: Populate cycle plan ──
    Write-Info "Building cycle_plan.md from approved projects..."
    python $POPULATE_SCRIPT
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorLog "Failed to populate cycle plan"
        $state.status = "failed_populate"
        $state.consecutive_failures++
        Save-CycleState $state

        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    # Commit the sweep results and plan
    git add -A
    git commit -m "[Sweep] Cycle ${cycleNum}: $findingsCount findings, $projectsCreated projects queued" 2>$null

    # ── Step E: Execute projects (inner loop) ──
    $state.status = "executing"
    Save-CycleState $state

    Write-Info "Starting inner loop for project execution..."
    $innerLoopAttempts = 0
    $maxInnerAttempts = 3
    $innerSuccess = $false

    while (-not $innerSuccess -and $innerLoopAttempts -lt $maxInnerAttempts) {
        & "$WORKSPACE\$INNER_LOOP_SCRIPT"
        $innerExit = $LASTEXITCODE

        if ($innerExit -eq 0) {
            $innerSuccess = $true
            Write-Success "Inner loop completed: all projects done"
        }
        elseif ($innerExit -eq 2) {
            # Rate limit
            Invoke-RateLimitSleep $state "inner_loop"
            $innerLoopAttempts++
        }
        else {
            Write-ErrorLog "Inner loop failed (exit code $innerExit)"
            $innerLoopAttempts++
            $state.consecutive_failures++
            Save-CycleState $state

            if ($state.consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES) {
                Write-ErrorLog "Circuit breaker triggered. Stopping."
                break
            }

            if ($innerLoopAttempts -lt $maxInnerAttempts) {
                Write-Info "Retrying inner loop in 60 seconds..."
                Start-Sleep -Seconds 60
            }
        }
    }

    if (-not $innerSuccess) {
        Write-Warn "Inner loop did not complete cleanly."

        if ($state.consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES) {
            $state.status = "circuit_breaker"
            Save-CycleState $state

            # Still merge what we have
            git add -A
            git commit -m "[Sweep] Cycle $cycleNum partial (circuit breaker)" --allow-empty 2>$null
            git checkout main
            git merge $branchName --no-ff -m "Merge sweep-cycle-$cycleNum (partial - circuit breaker)"
            break
        }

        # Not at circuit breaker yet - abandon this cycle's branch and retry next cycle
        Write-Warn "Abandoning cycle $cycleNum branch. Will retry in next cycle."
        git add -A
        git commit -m "[Sweep] Cycle $cycleNum partial (inner loop failed)" --allow-empty 2>$null
        git checkout main 2>$null
        continue
    }
    else {
        $state.consecutive_failures = 0
    }

    # ── Step F: Finalize cycle ──
    Write-Info "Finalizing cycle $cycleNum..."
    git add -A
    git commit -m "Sweep cycle $cycleNum complete" --allow-empty 2>$null

    # ── Step G: Test gate before merge ──
    Write-Info "Running test gate before merge..."
    $testOutput = & pytest tests/ -n 12 "--tb=no" -q 2>&1 | Out-String
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -ne 0) {
        Write-ErrorLog "Test gate FAILED (exit code $testExitCode). Refusing to merge broken code."
        Write-Host $testOutput
        $state.status = "failed_test_gate"
        $state.consecutive_failures++
        Save-CycleState $state

        # Abandon branch, return to main for next cycle
        git checkout main 2>$null
        continue
    }
    Write-Success "Test gate passed"

    # ── Step H: Merge to main ──
    $state.status = "merging"
    Save-CycleState $state

    Write-Info "Merging $branchName to main..."
    git checkout main
    git merge $branchName --no-ff -m "Merge sweep-cycle-$cycleNum"

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorLog "Merge conflict! Manual intervention required."
        Write-ErrorLog "Resolve the conflict, then restart the loop."
        $state.status = "merge_conflict"
        Save-CycleState $state
        exit 1
    }

    Write-Success "Merged $branchName to main"

    # ── Step I: Record cycle results ──
    $qualityScore = $null
    $qualityFile = "$WORKSPACE\Projects\continuous_loop\quality_scores.jsonl"
    if (Test-Path $qualityFile) {
        try {
            $lastLine = Get-Content $qualityFile -Tail 1
            if ($lastLine) {
                $qualityScore = ($lastLine | ConvertFrom-Json).overall.score
            }
        }
        catch { }
    }

    $cycleRecord = [PSCustomObject]@{
        cycle              = $cycleNum
        branch             = $branchName
        started            = $cycleStartTime
        completed          = (Get-Date).ToString("o")
        review_folder      = if ($reviewFolder) { Split-Path $reviewFolder -Leaf } else { "unknown" }
        findings_count     = $findingsCount
        projects_created   = $projectsCreated
        projects_completed = if ($innerSuccess) { $projectsCreated } else { 0 }
        projects_failed    = if ($innerSuccess) { 0 } else { $projectsCreated }
        quality_score      = $qualityScore
    }
    $state.cycles += $cycleRecord
    $state.status = "idle"
    Save-CycleState $state

    Write-Success "Cycle $cycleNum recorded."
    Write-Info "Sleeping $INTER_CYCLE_SLEEP_SECONDS seconds before next cycle..."
    Start-Sleep -Seconds $INTER_CYCLE_SLEEP_SECONDS
}

# ═══════════════════════════════════════════════════════
# SHUTDOWN
# ═══════════════════════════════════════════════════════

if ($state.status -eq "idle") {
    $state.status = "stopped_max_cycles"
}

Save-CycleState $state

$totalProjects = 0
$totalFindings = 0
foreach ($c in $state.cycles) {
    $totalProjects += $c.projects_created
    $totalFindings += $c.findings_count
}

Write-Banner "Continuous Improvement Loop Complete"
Write-Info "Cycles completed: $($state.cycles.Count)"
Write-Info "Total findings processed: $totalFindings"
Write-Info "Total projects created: $totalProjects"
Write-Info "Final status: $($state.status)"
Write-Info "State file: $STATE_FILE"
Write-Info "Log file: $LOG_FILE"

Stop-Transcript
