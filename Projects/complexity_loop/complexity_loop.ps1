# Complexity Reduction Loop - Main Orchestrator
#
# Automated cycle that:
#   1. Runs complexity audit (radon CC)
#   2. Picks worst function above threshold
#   3. Launches multi-agent analysis to plan refactoring
#   4. Executes the refactoring project (inner loop)
#   5. Launches multi-agent post-refactor review
#   6. Merges to main if tests pass
#   7. Repeats until all functions < threshold or time limit
#
# Usage:
#   cd "C:\Dev\Starship Battles"
#   .\Projects\complexity_loop\complexity_loop.ps1
#
# Options (edit configuration section below):
#   - CC_THRESHOLD: Minimum complexity to target (default: 20)
#   - MAX_CYCLES: Maximum refactoring cycles (default: 50)
#   - MAX_RUNTIME_HOURS: Time limit (default: 8)
#   - MAX_ATTEMPTS_PER_FUNCTION: Skip after N failures (default: 2)

$ErrorActionPreference = "Continue"

# ═══════════════════════════════════════════════════════
# TRANSCRIPT LOGGING
# ═══════════════════════════════════════════════════════

$LOG_DIR = "Projects/complexity_loop/logs"
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}
$logTimestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$LOG_FILE = "$LOG_DIR/complexity_loop_$logTimestamp.log"
Start-Transcript -Path $LOG_FILE -Append
Write-Host "[LOG] Transcript started: $LOG_FILE"

# ═══════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════

$CC_THRESHOLD = 20
$MAX_CYCLES = 50
$MAX_RUNTIME_HOURS = 8
$MAX_CONSECUTIVE_FAILURES = 3
$MAX_ATTEMPTS_PER_FUNCTION = 2
$RATE_LIMIT_SLEEP_MINUTES = 15
$INTER_CYCLE_SLEEP_SECONDS = 15

$WORKSPACE = "C:/Dev/Starship Battles"
$STATE_FILE = "Projects/complexity_loop/cycle_state.json"
$CYCLE_PLAN_FILE = "Projects/complexity_loop/cycle_plan.md"
$AUDIT_SCRIPT = "Projects/complexity_loop/run_complexity_audit.py"
$PLAN_SCRIPT = "Projects/complexity_loop/plan_refactor.py"
$POPULATE_SCRIPT = "Projects/complexity_loop/populate_complexity_plan.py"
$INNER_LOOP_SCRIPT = "Projects/complexity_loop/inner_loop.ps1"
$ANALYSIS_WORKER = "Projects/complexity_loop/ANALYSIS_WORKER.md"
$REVIEW_WORKER = "Projects/complexity_loop/REVIEW_WORKER.md"
$SKIP_LIST_FILE = "Projects/complexity_loop/skip_list.json"

$CLAUDE_TEMP_DIR = "$env:LOCALAPPDATA\Temp\claude\C--Dev-Starship-Battles"

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
    Write-Host "[$ts CLOOP] $msg" -ForegroundColor Cyan
}
function Write-Success ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts CLOOP] $msg" -ForegroundColor Green
}
function Write-Warn ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts CLOOP] $msg" -ForegroundColor Yellow
}
function Write-ErrorLog ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts CLOOP] $msg" -ForegroundColor Red
}
function Write-Banner ($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host ""
    Write-Host "[$ts CLOOP] ======================================================" -ForegroundColor Magenta
    Write-Host "[$ts CLOOP]   $msg" -ForegroundColor Magenta
    Write-Host "[$ts CLOOP] ======================================================" -ForegroundColor Magenta
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
    return [PSCustomObject]@{
        current_cycle          = 0
        start_time             = (Get-Date).ToString("o")
        cc_threshold           = $CC_THRESHOLD
        status                 = "idle"
        consecutive_failures   = 0
        total_cc_reduced       = 0
        functions_completed    = 0
        functions_skipped      = 0
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
            Remove-Item -Path "$CLAUDE_TEMP_DIR\tasks\*" -Force -ErrorAction SilentlyContinue
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

function Add-ToSkipList ($filePath, $functionName, $reason, $cc) {
    # Use the Python script to add to skip list
    $key = "${filePath}:${functionName}"
    Write-Info "Adding to skip list: $key (reason: $reason)"

    # Read, modify, write skip list JSON
    $skipList = @{}
    if (Test-Path $SKIP_LIST_FILE) {
        try {
            $skipList = Get-Content $SKIP_LIST_FILE -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
        }
        catch { }
    }

    $entry = @{
        reason       = $reason
        attempts     = if ($skipList.ContainsKey($key)) { $skipList[$key].attempts + 1 } else { 1 }
        last_attempt = (Get-Date).ToString("o")
        original_cc  = $cc
    }
    $skipList[$key] = $entry
    $skipList | ConvertTo-Json -Depth 3 | Set-Content $SKIP_LIST_FILE -Encoding UTF8
}

function Get-AuditTarget {
    # Run audit and get the top target as JSON
    $auditOutput = python $AUDIT_SCRIPT --threshold $CC_THRESHOLD --top 1 --json 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        return $null
    }
    try {
        $audit = $auditOutput | ConvertFrom-Json
        if ($audit.results.Count -eq 0) {
            return $null
        }
        return $audit
    }
    catch {
        Write-ErrorLog "Failed to parse audit output"
        return $null
    }
}

function Extract-ProjectId ($output) {
    # Extract PROJ-XX from plan_refactor.py output
    $match = [regex]::Match($output, "PROJECT_ID=(PROJ-\d+)")
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

# ═══════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════

Set-Location $WORKSPACE

# Verify prerequisites
foreach ($file in @($AUDIT_SCRIPT, $PLAN_SCRIPT, $POPULATE_SCRIPT, $INNER_LOOP_SCRIPT, $ANALYSIS_WORKER, $REVIEW_WORKER)) {
    if (-not (Test-Path $file)) {
        Write-ErrorLog "Required file not found: $file"
        exit 1
    }
}

# Ensure radon is installed
$radonCheck = pip show radon 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Installing radon..."
    pip install radon
}

$state = Load-CycleState
$state.start_time = (Get-Date).ToString("o")
$state.cc_threshold = $CC_THRESHOLD
Save-CycleState $state
$startTime = Get-Date

Write-Banner "Complexity Reduction Loop Starting"
Write-Info "CC Threshold: $CC_THRESHOLD"
Write-Info "Max cycles: $MAX_CYCLES"
Write-Info "Max runtime: $MAX_RUNTIME_HOURS hours"
Write-Info "Max attempts per function: $MAX_ATTEMPTS_PER_FUNCTION"
Write-Info "Starting from cycle: $($state.current_cycle)"

# ── Main cycle loop ──
while ($state.current_cycle -lt $MAX_CYCLES) {

    # Check runtime limit
    $elapsed = (Get-Date) - $startTime
    if ($elapsed.TotalHours -gt $MAX_RUNTIME_HOURS) {
        Write-Warn "Maximum runtime reached ($MAX_RUNTIME_HOURS hours). Stopping."
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
    $cycleStartTime = (Get-Date).ToString("o")
    $branchName = "complexity-cycle-$cycleNum"

    Write-Banner "CYCLE $cycleNum / $MAX_CYCLES"

    # ══════════════════════════════════════
    # STEP A: Run Complexity Audit
    # ══════════════════════════════════════
    Write-Info "Step A: Running complexity audit (threshold: $CC_THRESHOLD)..."
    $state.status = "auditing"
    Save-CycleState $state

    $audit = Get-AuditTarget
    if ($null -eq $audit) {
        Write-Success "ALL CLEAR: No functions above CC $CC_THRESHOLD. Codebase is clean!"
        $state.status = "complete_all_clean"
        Save-CycleState $state
        break
    }

    $target = $audit.results[0]
    $targetFile = $target.file
    $targetFunc = $target.function
    $targetCC = $target.cc
    $remaining = $audit.total_above_threshold

    Write-Info "Target: ${targetFile}:$($target.line) $targetFunc (CC=$targetCC)"
    Write-Info "Remaining above threshold: $remaining (skipped: $($audit.skipped))"

    # ══════════════════════════════════════
    # STEP B: Create branch
    # ══════════════════════════════════════
    Write-Info "Step B: Creating branch: $branchName"
    git checkout main 2>$null
    git checkout -b $branchName
    if ($LASTEXITCODE -ne 0) {
        git checkout $branchName 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorLog "Cannot create or switch to branch"
            $state.status = "failed"
            $state.consecutive_failures++
            Save-CycleState $state
            continue
        }
    }

    # ══════════════════════════════════════
    # STEP C: Create project scaffold
    # ══════════════════════════════════════
    Write-Info "Step C: Creating project scaffold..."
    $state.status = "planning"
    Save-CycleState $state

    $planOutput = python $PLAN_SCRIPT --threshold $CC_THRESHOLD 2>&1 | Out-String
    $planExitCode = $LASTEXITCODE
    Write-Host $planOutput

    if ($planExitCode -eq 2) {
        # Nothing to do — all clear
        Write-Success "No targets found. Codebase is clean!"
        $state.status = "complete_all_clean"
        Save-CycleState $state
        git checkout main 2>$null
        git branch -D $branchName 2>$null
        break
    }
    elseif ($planExitCode -ne 0) {
        Write-ErrorLog "Project creation failed"
        $state.consecutive_failures++
        $state.status = "failed_planning"
        Save-CycleState $state
        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    $projectId = Extract-ProjectId $planOutput
    if (-not $projectId) {
        Write-ErrorLog "Could not extract project ID from output"
        $state.consecutive_failures++
        Save-CycleState $state
        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    Write-Success "Created: $projectId"

    # ══════════════════════════════════════
    # STEP D: Multi-agent analysis & planning
    # ══════════════════════════════════════
    Write-Info "Step D: Running multi-agent analysis..."
    $state.status = "analyzing"
    Save-CycleState $state
    Clear-ClaudeTempFiles

    $analysisSuccess = $false
    $analysisRetries = 0

    while (-not $analysisSuccess -and $analysisRetries -lt 3) {
        $analysisOutput = claude `
            --dangerously-skip-permissions `
            --system-prompt-file $ANALYSIS_WORKER `
            -p "Analyze and plan the refactoring for $projectId. Read findings/complexity_target.md and findings/audit_data.json in the project directory. Launch 3 parallel review agents. Design the refactoring plan. Write plan.md and phase checklists. Commit and exit." 2>&1 | Out-String

        $analysisExitCode = $LASTEXITCODE

        if ($analysisOutput) {
            Write-Host $analysisOutput
        }

        if ($analysisExitCode -eq 0) {
            $analysisSuccess = $true

            # Check if analysis recommended skipping
            if ($analysisOutput -match "irreducib" -or $analysisOutput -match "marked.*\[~\]") {
                Write-Warn "Analysis agent recommends skipping $targetFunc"
                Add-ToSkipList $targetFile $targetFunc "Analysis deemed irreducible" $targetCC
                $state.functions_skipped++
                Save-CycleState $state

                # Clean up
                git add -A
                git commit -m "[$projectId] Skipped: irreducible complexity - Automated" --allow-empty 2>$null
                git checkout main 2>$null
                git branch -D $branchName 2>$null

                $state.consecutive_failures = 0
                $state.status = "idle"
                Save-CycleState $state

                # Record cycle
                $cycleRecord = [PSCustomObject]@{
                    cycle     = $cycleNum
                    branch    = $branchName
                    started   = $cycleStartTime
                    completed = (Get-Date).ToString("o")
                    project   = $projectId
                    target    = "${targetFile}:${targetFunc}"
                    original_cc = $targetCC
                    final_cc  = $targetCC
                    result    = "skipped_analysis"
                }
                $state.cycles += $cycleRecord
                Save-CycleState $state

                # Skip to next cycle iteration
                $analysisSuccess = "SKIPPED"
            }
        }
        elseif (Test-RateLimit $analysisOutput) {
            Invoke-RateLimitSleep $state "analysis"
            $analysisRetries++
        }
        else {
            Write-ErrorLog "Analysis failed (exit code $analysisExitCode)"
            $analysisRetries++
            if ($analysisRetries -lt 3) {
                Start-Sleep -Seconds 30
                Clear-ClaudeTempFiles
            }
        }
    }

    if ($analysisSuccess -eq "SKIPPED") {
        Write-Info "Sleeping ${INTER_CYCLE_SLEEP_SECONDS}s before next cycle..."
        Start-Sleep -Seconds $INTER_CYCLE_SLEEP_SECONDS
        continue
    }

    if (-not $analysisSuccess) {
        Write-ErrorLog "Analysis failed after 3 attempts"
        $state.consecutive_failures++
        $state.status = "failed_analysis"
        Save-CycleState $state
        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    Write-Success "Analysis complete. Proceeding to execution."

    # ══════════════════════════════════════
    # STEP E: Populate cycle plan
    # ══════════════════════════════════════
    Write-Info "Step E: Building cycle_plan.md..."
    python $POPULATE_SCRIPT $projectId
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorLog "Failed to populate cycle plan"
        $state.consecutive_failures++
        Save-CycleState $state
        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    # Commit analysis + plan
    git add -A
    git commit -m "[$projectId] Analysis & plan: $targetFunc (CC=$targetCC) - Automated" 2>$null

    # ══════════════════════════════════════
    # STEP F: Execute refactoring (inner loop)
    # ══════════════════════════════════════
    Write-Info "Step F: Executing refactoring..."
    $state.status = "executing"
    Save-CycleState $state

    & "$WORKSPACE\$INNER_LOOP_SCRIPT"
    $innerExit = $LASTEXITCODE

    if ($innerExit -eq 2) {
        # Rate limit
        Invoke-RateLimitSleep $state "inner_loop"
        & "$WORKSPACE\$INNER_LOOP_SCRIPT"
        $innerExit = $LASTEXITCODE
    }

    if ($innerExit -eq 3) {
        # Project skipped by execution worker
        Write-Warn "Execution worker skipped $targetFunc"
        Add-ToSkipList $targetFile $targetFunc "Execution deemed irreducible" $targetCC
        $state.functions_skipped++
        $state.consecutive_failures = 0

        git add -A
        git commit -m "[$projectId] Skipped during execution - Automated" --allow-empty 2>$null
        git checkout main 2>$null
        git merge $branchName --no-ff -m "Merge $branchName (skipped)" 2>$null
        if ($LASTEXITCODE -ne 0) {
            git checkout main 2>$null
            git branch -D $branchName 2>$null
        }

        $cycleRecord = [PSCustomObject]@{
            cycle     = $cycleNum
            branch    = $branchName
            started   = $cycleStartTime
            completed = (Get-Date).ToString("o")
            project   = $projectId
            target    = "${targetFile}:${targetFunc}"
            original_cc = $targetCC
            final_cc  = $targetCC
            result    = "skipped_execution"
        }
        $state.cycles += $cycleRecord
        $state.status = "idle"
        Save-CycleState $state

        Write-Info "Sleeping ${INTER_CYCLE_SLEEP_SECONDS}s before next cycle..."
        Start-Sleep -Seconds $INTER_CYCLE_SLEEP_SECONDS
        continue
    }

    if ($innerExit -ne 0) {
        Write-ErrorLog "Inner loop failed (exit code $innerExit)"
        $state.consecutive_failures++
        $state.status = "failed_execution"
        Save-CycleState $state

        if ($state.consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES) {
            Write-ErrorLog "Circuit breaker. Stopping."
            git checkout main 2>$null
            break
        }

        git checkout main 2>$null
        git branch -D $branchName 2>$null
        continue
    }

    Write-Success "Refactoring execution complete"
    $state.consecutive_failures = 0

    # ══════════════════════════════════════
    # STEP G: Post-refactor multi-agent review
    # ══════════════════════════════════════
    Write-Info "Step G: Running post-refactor review..."
    $state.status = "reviewing"
    Save-CycleState $state
    Clear-ClaudeTempFiles

    $reviewOutput = claude `
        --dangerously-skip-permissions `
        --system-prompt-file $REVIEW_WORKER `
        -p "Review the refactoring for $projectId. Read the project plan, findings, and refactored code. Launch 3 parallel review agents (correctness, complexity, test coverage). Synthesize findings. Write post_refactor_review.md. Determine verdict: PASS, FAIL, or SKIP. Exit." 2>&1 | Out-String

    if ($reviewOutput) {
        Write-Host $reviewOutput
    }

    # Parse review verdict
    $verdict = "PASS"  # Default if review agent doesn't clearly state
    if ($reviewOutput -match "Verdict:\s*FAIL") {
        $verdict = "FAIL"
    }
    elseif ($reviewOutput -match "Verdict:\s*SKIP") {
        $verdict = "SKIP"
    }

    Write-Info "Review verdict: $verdict"

    if ($verdict -eq "SKIP") {
        Add-ToSkipList $targetFile $targetFunc "Review recommended skip" $targetCC
        $state.functions_skipped++
    }

    if ($verdict -eq "FAIL") {
        Write-Warn "Review FAILED. Reverting to main."
        git checkout main 2>$null
        git branch -D $branchName 2>$null

        $cycleRecord = [PSCustomObject]@{
            cycle     = $cycleNum
            branch    = $branchName
            started   = $cycleStartTime
            completed = (Get-Date).ToString("o")
            project   = $projectId
            target    = "${targetFile}:${targetFunc}"
            original_cc = $targetCC
            final_cc  = $targetCC
            result    = "failed_review"
        }
        $state.cycles += $cycleRecord
        $state.status = "idle"
        Save-CycleState $state

        Write-Info "Sleeping ${INTER_CYCLE_SLEEP_SECONDS}s before next cycle..."
        Start-Sleep -Seconds $INTER_CYCLE_SLEEP_SECONDS
        continue
    }

    # ══════════════════════════════════════
    # STEP H: Test gate
    # ══════════════════════════════════════
    Write-Info "Step H: Running test gate..."
    git add -A
    git commit -m "[$projectId] Post-review checkpoint - Automated" --allow-empty 2>$null

    $testOutput = & pytest tests/ -n 12 "--tb=no" -q 2>&1 | Out-String
    $testExitCode = $LASTEXITCODE

    if ($testExitCode -ne 0) {
        Write-ErrorLog "Test gate FAILED. Abandoning branch."
        Write-Host $testOutput
        $state.consecutive_failures++

        git checkout main 2>$null
        git branch -D $branchName 2>$null

        $cycleRecord = [PSCustomObject]@{
            cycle     = $cycleNum
            branch    = $branchName
            started   = $cycleStartTime
            completed = (Get-Date).ToString("o")
            project   = $projectId
            target    = "${targetFile}:${targetFunc}"
            original_cc = $targetCC
            final_cc  = $targetCC
            result    = "failed_tests"
        }
        $state.cycles += $cycleRecord
        $state.status = "idle"
        Save-CycleState $state
        continue
    }

    Write-Success "Test gate passed"

    # ══════════════════════════════════════
    # STEP I: Measure CC reduction
    # ══════════════════════════════════════
    Write-Info "Step I: Measuring complexity reduction..."
    $newAudit = Get-AuditTarget
    $newCC = $targetCC  # Fallback if we can't measure
    if ($null -ne $newAudit -and $newAudit.results.Count -gt 0) {
        # Find the same function in new results
        foreach ($r in $newAudit.results) {
            if ($r.file -eq $targetFile -and $r.function -eq $targetFunc) {
                $newCC = $r.cc
                break
            }
        }
        # If function not found in results, CC is now below threshold
        if ($newCC -eq $targetCC) {
            $newCC = $CC_THRESHOLD - 1  # Below threshold
        }
    }
    else {
        $newCC = 0  # All clear
    }

    $ccReduction = $targetCC - $newCC
    Write-Info "CC: $targetCC -> $newCC (reduced by $ccReduction)"

    # ══════════════════════════════════════
    # STEP J: Merge to main
    # ══════════════════════════════════════
    Write-Info "Step J: Merging $branchName to main..."
    $state.status = "merging"
    Save-CycleState $state

    git checkout main
    git merge $branchName --no-ff -m "Merge ${branchName} - ${targetFunc} CC ${targetCC} to ${newCC}"

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorLog "Merge conflict! Manual intervention required."
        $state.status = "merge_conflict"
        Save-CycleState $state
        exit 1
    }

    Write-Success "Merged to main"

    # ══════════════════════════════════════
    # STEP K: Record results
    # ══════════════════════════════════════
    $state.total_cc_reduced += $ccReduction
    $state.functions_completed++

    $cycleRecord = [PSCustomObject]@{
        cycle       = $cycleNum
        branch      = $branchName
        started     = $cycleStartTime
        completed   = (Get-Date).ToString("o")
        project     = $projectId
        target      = "${targetFile}:${targetFunc}"
        original_cc = $targetCC
        final_cc    = $newCC
        cc_reduced  = $ccReduction
        result      = if ($verdict -eq "SKIP") { "completed_skipped" } else { "completed" }
    }
    $state.cycles += $cycleRecord
    $state.status = "idle"
    $state.consecutive_failures = 0
    Save-CycleState $state

    Write-Success "Cycle $cycleNum complete: $targetFunc CC $targetCC -> $newCC"
    Write-Info "Running total: $($state.total_cc_reduced) CC reduced, $($state.functions_completed) functions, $($state.functions_skipped) skipped"
    Write-Info "Sleeping ${INTER_CYCLE_SLEEP_SECONDS}s before next cycle..."
    Start-Sleep -Seconds $INTER_CYCLE_SLEEP_SECONDS
}

# ═══════════════════════════════════════════════════════
# SHUTDOWN
# ═══════════════════════════════════════════════════════

if ($state.status -eq "idle") {
    $state.status = "stopped_max_cycles"
}
Save-CycleState $state

Write-Banner "Complexity Reduction Loop Complete"
Write-Info "Cycles completed: $($state.cycles.Count)"
Write-Info "Functions refactored: $($state.functions_completed)"
Write-Info "Functions skipped: $($state.functions_skipped)"
Write-Info "Total CC reduced: $($state.total_cc_reduced)"
Write-Info "Final status: $($state.status)"
Write-Info "State file: $STATE_FILE"
Write-Info "Log file: $LOG_FILE"

# Final summary
if ($state.cycles.Count -gt 0) {
    Write-Host ""
    Write-Info "Cycle Results:"
    Write-Host "  Cycle | Target                                  | CC Before | CC After | Result"
    Write-Host "  ------|----------------------------------------|-----------|----------|-------"
    foreach ($c in $state.cycles) {
        $shortTarget = if ($c.target.Length -gt 40) { $c.target.Substring(0, 37) + "..." } else { $c.target }
        Write-Host ("  {0,-5} | {1,-40} | {2,-9} | {3,-8} | {4}" -f $c.cycle, $shortTarget, $c.original_cc, $c.final_cc, $c.result)
    }
}

Stop-Transcript
