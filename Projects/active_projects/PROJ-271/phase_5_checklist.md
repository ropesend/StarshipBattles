# Phase 5: Evaluate + Eliminate Legacy `capture_battle_state`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW (evaluation + likely deletion of test-only module)
**Depends On:** None — independent from Phases 1-4
**Objective:** Carefully evaluate `combat_lab/battle_state_capture.py` for whether it still adds value. The module had 2 broken callers passing `mode="test"` to `BattleState.capture_from_engine` — the kwarg was deleted by PROJ-270 Phase 5.3, and every `BattleStateCaptureContext` invocation silently raised `TypeError` (swallowed by a try/except) for months. PROJ-270 Phase 13 fixed the immediate bug (deleted the kwargs) but that only restored the module to its pre-PROJ-270 behavior — which may no longer add value now that `BattleOutcome` + `CombatLabTelemetry` replaced the live-engine capture pattern.

## Context

- **`combat_lab/battle_state_capture.py`** has ~290 lines; exposes `capture_battle_state()` function + `BattleStateCaptureContext` context manager
- Writes battle-state JSON files to `combat_lab/battle_states/` for side-by-side comparison in the Combat Lab UI
- PROJ-270 Phase 13 grep-verified no production callers — only test paths
- Fix history:
  - `mode="test"` kwarg deletion landed in PROJ-270 Phase 13 follow-up (crash-fix session on 2026-04-13)
  - Callers have been silently raising TypeError since PROJ-270 Phase 5.3 deleted `BattleState.mode`
  - So: zero production runs captured state successfully for an extended period, nobody noticed

## Tasks

### Task 5.1: Audit current callers + usage [Simple]
**File:** grep audit of callers across `game/`, `combat_lab/`, `tests/`

- [ ] Identify every caller of `capture_battle_state`, `BattleStateCaptureContext`, `BattleStateCapture` (context-manager alias if any)
- [ ] Classify each caller: production | test | dev-tool | UI
- [ ] Check UI — does the Combat Lab UI actually load the JSON files this module writes? Is there a "compare initial vs final state" feature?
- [ ] Verify whether `combat_lab/battle_states/` directory is gitignored (ephemeral files) and whether it's populated by current runs
- [ ] Document findings in `findings/capture_battle_state_audit.md`

### Task 5.2: Architectural decision — retain, refactor, or delete [Medium]
**File:** `decisions.md` (new decision entry)

Based on audit, decide:

- **Option A (DELETE):** `BattleOutcome` carries enough state + `CombatLabTelemetry` carries enough forensic detail that per-tick or per-battle state snapshots are redundant. Delete the whole module.
- **Option B (REFACTOR):** The UI compare-states feature is valuable but the implementation should use `BattleOutcome` round-trips, not live-engine captures. Rewrite module to consume outcomes.
- **Option C (RETAIN):** The snapshot has genuine forensic value that outcomes don't cover (e.g., mid-battle state at arbitrary ticks). Keep + add integration tests so the silent-TypeError-spam failure mode can't recur.

Record decision + reasoning.

### Task 5.3: Execute chosen option [Medium]

If Option A:
- [ ] Delete `combat_lab/battle_state_capture.py`
- [ ] Delete `combat_lab/battle_states/` directory (add to gitignore if not already)
- [ ] Update any UI paths that referenced the module
- [ ] Grep-guard regression test: `grep -rn "capture_battle_state\|BattleStateCaptureContext"` in live code should be zero

If Option B:
- [ ] Rewrite module API to consume `BattleOutcome` round-trips
- [ ] Migrate UI compare-states feature to new API
- [ ] Add integration test that snapshots round-trip correctly

If Option C:
- [ ] Add integration test that exercises both callers with real engines — they must produce valid JSON files without silent failures
- [ ] Delete the broad try/except pattern that was swallowing the TypeError for months, or narrow it to specific IOError/OSError (never catch all Exceptions)

### Task 5.4: Regression gate
**Tests:** Full suites

- [ ] `pytest tests/` green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Grep audit verifies chosen option was fully executed

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Decision recorded in `decisions.md`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table

## Rationale (origin of this phase)

This phase was created during a PROJ-270 Phase 13 follow-up crash-fix session on 2026-04-13. The user hit a crash while running `python launcher.py` that surfaced ~40 lines of silent warning spam:

```
Failed to capture initial state: BattleState.capture_from_engine() got an unexpected keyword argument 'mode'
Failed to capture final state: BattleState.capture_from_engine() got an unexpected keyword argument 'mode'
```

The minimal fix (deleting the `mode="test"` kwarg from 2 callers) restored the module to working order — but "working order" means: the module captures battle-state JSON on every Combat Lab run, and that capture path had been completely broken for an unknown duration with zero user impact visible. That invites the question: **does anyone actually read those files?** This phase answers that question instead of accepting the silent-works-as-intended-or-not state.
