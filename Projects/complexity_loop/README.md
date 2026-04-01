# Complexity Reduction Loop

Automated system that continuously reduces cyclomatic complexity across the codebase. Runs overnight, one function at a time, with multi-agent analysis and review at each step.

## Quick Start

```powershell
cd "C:\Dev\Starship Battles"
.\Projects\complexity_loop\complexity_loop.ps1
```

## How It Works

Each cycle targets the **single most complex function** above the threshold:

```
CYCLE N:
  1. Run radon complexity audit → find worst function (CC >= 20)
  2. Create git branch (complexity-cycle-N)
  3. Scaffold a PROJ-XX project for the target
  4. Launch 3 analysis agents in parallel:
     - Structure Analyst (control flow, patterns)
     - Dependency Analyst (callers, interfaces, tests)
     - Safety Analyst (edge cases, risks, coverage)
  5. Synthesize analysis → write refactoring plan
  6. Execute the plan (inner loop, one phase per CLI session)
  7. Launch 3 review agents in parallel:
     - Correctness Reviewer (behavior preservation)
     - Complexity Verifier (CC measurement)
     - Test Coverage Reviewer (full suite verification)
  8. Test gate (python scripts/test_sharded.py)
  9. Merge to main
  10. Record metrics, repeat
```

## Stopping Conditions

The loop stops automatically when:
- All functions are below the CC threshold (success)
- Maximum runtime reached (default: 8 hours)
- Maximum cycles reached (default: 50)
- 3 consecutive failures (circuit breaker)
- Merge conflict (requires manual resolution)

## Configuration

Edit the top of `complexity_loop.ps1`:

| Setting | Default | Description |
|---------|---------|-------------|
| `CC_THRESHOLD` | 20 | Target max cyclomatic complexity |
| `MAX_CYCLES` | 50 | Maximum refactoring cycles |
| `MAX_RUNTIME_HOURS` | 8 | Time limit |
| `MAX_ATTEMPTS_PER_FUNCTION` | 2 | Skip after N failed attempts |
| `MAX_CONSECUTIVE_FAILURES` | 3 | Circuit breaker threshold |
| `RATE_LIMIT_SLEEP_MINUTES` | 15 | Sleep duration on rate limit |

## Safety Features

### Skip List (`skip_list.json`)
Functions that cannot be simplified are added to a persistent skip list. The system will not attempt them again. Functions are skipped when:
- The analysis agent determines irreducible complexity
- The execution agent fails to reduce CC after genuine attempts
- The review agent recommends skipping

### Git Branch Per Cycle
Each cycle works on its own branch (`complexity-cycle-N`). If anything goes wrong, the branch is abandoned and main is untouched.

### Test Gate
Full test suite runs before every merge. Failed tests = abandoned branch.

### Revert-First Policy
The execution worker reverts any change that breaks tests rather than trying to "fix forward."

## File Structure

```
Projects/complexity_loop/
├── complexity_loop.ps1          # Main orchestrator (outer loop)
├── inner_loop.ps1               # Project execution (inner loop)
├── ANALYSIS_WORKER.md           # System prompt: multi-agent analysis
├── REFACTOR_WORKER.md           # System prompt: execution worker
├── REVIEW_WORKER.md             # System prompt: multi-agent review
├── run_complexity_audit.py      # Radon wrapper → structured JSON
├── plan_refactor.py             # Creates PROJ-XX from audit target
├── populate_complexity_plan.py  # Builds cycle_plan.md
├── check_completion.py          # Checks if cycle plan is done
├── trim_execution_log.py        # Manages context window size
├── skip_list.json               # Functions to never attempt again
├── complexity_history.jsonl     # Audit snapshots for trending
├── cycle_state.json             # Persistent execution state
├── cycle_plan.md                # Working state file (auto-generated)
├── logs/                        # Transcript logs
└── README.md                    # This file
```

## Multi-Agent Architecture

### Analysis Phase (3 agents in parallel)
| Agent | Role | Output |
|-------|------|--------|
| Structure Analyst | Control flow, patterns, extraction opportunities | `structure_analysis.md` |
| Dependency Analyst | Callers, interfaces, side effects, test coverage | `dependency_analysis.md` |
| Safety Analyst | Edge cases, risks, irreducibility assessment | `safety_analysis.md` |

### Review Phase (3 agents in parallel)
| Agent | Role | Output |
|-------|------|--------|
| Correctness Reviewer | Behavior preservation, edge cases | `correctness_review.md` |
| Complexity Verifier | CC measurement, aggregate analysis | `complexity_verification.md` |
| Test Coverage Reviewer | Suite passage, coverage gaps | `test_coverage_review.md` |

## Monitoring

While running:
- Watch PowerShell output (timestamped, color-coded)
- Read `cycle_state.json` for current state
- Read `complexity_history.jsonl` for trend data
- Check `logs/complexity_loop_*.log` for full transcript

## State Recovery

If the loop crashes or is interrupted:
- Restart `complexity_loop.ps1` — it reads `cycle_state.json` and continues
- If stuck on a branch: `git checkout main` then restart
- To force-skip a function: add it to `skip_list.json` manually

## Relationship to Other Systems

| System | Purpose | Interaction |
|--------|---------|-------------|
| `refactor_loop/` | Manual project execution | None (independent) |
| `continuous_loop/` | Full codebase sweep + fix | None (independent) |
| `complexity_loop/` | Targeted complexity reduction | Uses same project system (PROJ-XX) |

All three systems use the same project infrastructure (`active_projects/`, `create_project.py`, protocols) but operate independently and should not run concurrently.
