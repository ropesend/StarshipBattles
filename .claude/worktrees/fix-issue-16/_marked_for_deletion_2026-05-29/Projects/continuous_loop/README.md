# Continuous Improvement Loop

An autonomous system that continuously reviews and improves the Starship Battles codebase by chaining the **analysis-sweep** code review pipeline with the **refactor loop** project execution engine.

## How It Works

```
┌─── Cycle N ──────────────────────────────────────────────┐
│                                                          │
│  1. Create branch: sweep-cycle-N                         │
│  2. Run analysis-sweep (25 agents, 5 review categories)   │
│  3. Validate findings (5 skeptical agents, 1 per shard)  │
│  4. Filter: keep only confirmed/downgraded findings      │
│  5. Auto-approve ALL validated projects                  │
│  6. Build cycle_plan.md                                  │
│  7. Execute projects (one phase per CLI session)         │
│  8. Merge branch to main                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
         │
         └── Repeat with Cycle N+1
```

Each cycle creates a git branch, performs a full codebase review, validates findings with skeptical agents, creates projects from confirmed findings, executes them all, then merges to main. The next sweep sees the improved code and finds new issues.

## Quick Start

```powershell
cd "C:\Dev\Starship Battles"
.\Projects\continuous_loop\continuous_loop.ps1
```

That's it. The loop runs until one of the stopping conditions is met.

## Stopping Conditions

| Condition | Default | Effect |
|-----------|---------|--------|
| Max cycles | 10 | Graceful stop |
| Max runtime | 48 hours | Graceful stop |
| Diminishing returns | < 20 findings | Graceful stop |
| Zero projects | Sweep creates 0 projects | Graceful stop |
| Consecutive failures | 3 in a row | Circuit breaker |
| Merge conflict | Git merge fails | Stop, manual fix needed |
| Manual stop | Ctrl+C | Immediate |

## Configuration

Edit the top of `continuous_loop.ps1` to change defaults:

```powershell
$MAX_CYCLES = 10                  # Max sweep-execute cycles
$MAX_RUNTIME_HOURS = 48           # Max total runtime
$RATE_LIMIT_SLEEP_MINUTES = 15    # Sleep on rate limit
$MIN_FINDINGS_THRESHOLD = 20      # Stop if fewer findings
$MAX_CONSECUTIVE_FAILURES = 3     # Circuit breaker threshold
```

## Files

| File | Purpose |
|------|---------|
| `continuous_loop.ps1` | Outer loop orchestrator (manages cycles, branches) |
| `inner_loop.ps1` | Inner loop (executes projects, one phase per session) |
| `SWEEP_WORKER.md` | System prompt for sweep CLI sessions (includes validation) |
| `CYCLE_WORKER.md` | System prompt for project execution CLI sessions |
| `populate_cycle_plan.py` | Builds cycle_plan.md from newly-created projects |
| `cycle_plan.md` | Per-cycle project execution plan (auto-generated) |
| `cycle_state.json` | Persistent state across cycles (auto-generated) |
| `compute_quality_score.py` | Computes 0-100 quality scores per cycle, appends to JSONL archive |
| `quality_scores.jsonl` | Append-only archive of quality scores over time (auto-generated) |
| `Reviews/Prompts/Sweep - Validate Findings.txt` | Prompt template for skeptical validator agents |
| `Reviews/scripts/filter_validated_findings.py` | Applies validation verdicts to filter report.md |

## Architecture

### Two-Layer Design

**Outer loop** (`continuous_loop.ps1`):
- Manages the cycle lifecycle
- Creates/merges git branches
- Runs sweep via Claude CLI
- Handles rate limits and crash recovery

**Inner loop** (`inner_loop.ps1`):
- Spawns Claude CLI sessions (one per project phase)
- Each session reads `cycle_plan.md`, executes one phase, commits, exits
- Loops until all cycle projects are complete

### Skeptical Validation Layer

After the 25 sweep agents produce findings, a second wave of 5 **skeptical validator agents** (one per shard) independently verify each finding against the actual source code. Only confirmed findings proceed to project generation.

```
25 sweep agents → compile_findings.py → report.md (unfiltered)
                                              ↓
5 validator agents (1/shard) → validation/*.md
                                              ↓
filter_validated_findings.py → report.md (validated only)
                               report_unvalidated.md (backup)
                               validation/validation_summary.json
```

Each validator:
- Reads the actual source code at the stated location
- Verifies the claim is accurate
- Checks if the issue was already fixed
- Assesses whether severity is appropriate
- Detects common false positive patterns (TYPE_CHECKING imports, active decomposition projects, cross-sweep duplicates)
- Renders a verdict: **CONFIRMED**, **DOWNGRADED(NewSeverity)**, or **REJECTED**

Typically 15-25% of sweep findings are rejected as false positives, exaggerated, or already addressed.

### Quality Scoring

After each sweep, `compute_quality_score.py` produces a 0-100 quality score (higher = better) for the overall codebase and each of the 5 shards. Scores are appended to `quality_scores.jsonl` for trend tracking.

**Formula:** Severity-weighted demerits (Critical=10, Major=3, Minor=1, Info=0.2) normalized by file count, mapped via exponential decay: `score = 100 * exp(-0.5 * demerits_per_file)`.

| Score | Grade |
|-------|-------|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| 40-59 | Needs Improvement |
| 20-39 | Poor |
| 0-19 | Critical |

**Example output:**
```
Quality: 43/100 (Needs Improvement) [+19] | FND:22(+14) SIM:35(+11) STR:55(+15) UI1:52(+14) UI2:18(+14) | 210 findings (12C/98M/72m/28I) | 372 files
```

### Relationship to Existing Systems

This system is **completely independent** of:
- `Projects/refactor_loop/loop_runner.ps1` (still works for manual project execution)
- `Projects/refactor_loop/refactor_plan.md` (not touched or read)
- `Projects/refactor_loop/WORKER.md` (not used)

It **reuses** these existing components:
- All `Reviews/scripts/*.py` (sweep pipeline scripts)
- All `Reviews/Prompts/*.txt` (review agent prompts)
- All `Projects/scripts/*.py` (project management scripts)
- `Projects/active_projects/` (projects are created here)
- `Projects/protocols/*.md` (worker agents follow these)

## Git Branching

Each cycle creates a branch (`sweep-cycle-N`) and merges to main when done:

```
main ──○──────────○─────────────○──
       │          ↑             ↑
       └─ cycle-1 ┘             │
                    └── cycle-2 ┘
```

To revert an entire cycle: `git revert -m 1 <merge-commit>`

## Rate Limit Handling

When Claude API rate limits are detected:
1. The current operation is paused
2. The system sleeps for 15 minutes (configurable)
3. Execution resumes exactly where it left off

Detection works at both levels:
- **During sweep**: Outer loop retries the sweep session
- **During project execution**: Inner loop exits with code 2, outer loop sleeps and restarts

## Crash Recovery

If the loop is interrupted (Ctrl+C, power loss, etc.), restart it:

```powershell
.\Projects\continuous_loop\continuous_loop.ps1
```

It reads `cycle_state.json` and resumes from the last known state:
- If sweeping: Re-runs the sweep
- If executing: Re-runs inner loop (picks up from cycle_plan.md)
- If merging: May need manual git cleanup

## Monitoring

Watch `cycle_state.json` for real-time status:

```powershell
Get-Content Projects/continuous_loop/cycle_state.json | ConvertFrom-Json | Format-List
```

Or watch the PowerShell terminal output - all operations are logged with timestamps.
