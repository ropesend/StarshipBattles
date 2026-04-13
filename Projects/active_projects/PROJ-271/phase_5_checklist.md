# Phase 5: Evaluate + Eliminate Legacy `capture_battle_state`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Identified 4 live call sites:
  - `combat_lab/battle_state_capture.py` — the module itself, defines `capture_battle_state`, `BattleStateCapture`, `load_battle_state`, `load_battle_state_json`.
  - `game/ui/screens/test_lab/test_executor.py:247` — **PRODUCTION**: writes JSON for each test run.
  - `game/ui/screens/test_lab/screen.py:471-481` — **UI**: `_on_view_battle_states` loads and displays JSON via `load_battle_state_json`.
  - `game/ui/screens/test_lab/test_run_details.py:100, 226` — **UI**: checks `run_record.has_battle_states()` to show "View Battle States" button.
  - `combat_lab/test_history.py:127` — defines `has_battle_states()` on `TestRunRecord`.
- [x] Classification: 1 production write-path + 3 UI read-paths + 1 history record method. All actively used.
- [x] UI feature check: "View Battle States" button in test details panel loads both initial and final state JSON for comparison. **Genuine forensic feature.**
- [x] `combat_lab/battle_states/` is gitignored; populated by current Combat Lab runs (confirmed dozens of recent JSON files on disk).
- [x] Decision → Option C (retain + harden). See `decisions.md` 2026-04-13 entry.

**Notes:** Audit confirmed the module serves a live UI feature ("View Battle States" in test run details). Files in `combat_lab/battle_states/` are actively populated by each Combat Lab run. Option A (delete) would break the UI; Option B (refactor to BattleOutcome) would lose initial-state capture. Option C hardens the module against the original-sin broad-except pattern.

### Task 5.2: Architectural decision — retain, refactor, or delete [Medium]
**File:** `decisions.md` (new decision entry)

- [x] **Option C (retain + harden) selected.** Rationale:
  - `BattleOutcome` is emitted at battle **end** — it cannot capture **initial** state. Option B (refactor to consume outcomes) would require either a new "initial outcome" concept or would lose feature parity.
  - The UI feature is live; Option A (delete) would break "View Battle States".
  - The original sin was the broad `except Exception` wrapper that swallowed `TypeError: unexpected keyword 'mode'` for months. Narrowing that to `OSError` makes future API drift fail LOUDLY.
- [x] Documented in `decisions.md` 2026-04-13 "Phase 5: Option C (retain + harden)" entry.

**Notes:** Documented in decisions.md with full rationale: (a) BattleOutcome is battle-end-only, cannot capture initial state; (b) UI feature ("View Battle States") is live; (c) original sin was broad except. Option C minimum-invasive fix.

### Task 5.3: Execute chosen option [Medium]

If Option A (NOT CHOSEN — UI feature is live):
- [x] N/A — Option C selected instead
- [x] N/A — directory stays, still used by UI
- [x] N/A
- [x] N/A

If Option B (NOT CHOSEN — BattleOutcome has no initial-state capture):
- [x] N/A — feature parity cost too high
- [x] N/A
- [x] N/A

If Option C (CHOSEN):
- [x] Added 3 hardening tests to `tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py`:
  - `test_capture_battle_state_does_not_swallow_programming_errors` — text-based guard: the `except Exception` pattern must not return in `capture_battle_state()`.
  - `test_capture_battle_state_propagates_type_error_instead_of_swallowing` — behavioral: pass a broken engine stub, assert that `TypeError`/`AttributeError` propagates (not silently returns None).
  - `test_capture_battle_state_still_handles_disk_errors_gracefully` — behavioral: OSError (disk full / permission denied) IS caught and returns None (preserves "batch run doesn't crash on single-file write failure" semantics).
- [x] Narrowed `except Exception as e:` → `except OSError as e:` in `combat_lab/battle_state_capture.py::capture_battle_state`. Programming errors (AttributeError, TypeError, ValueError) now propagate.
- [x] Added explanatory comment citing PROJ-271 Phase 5.3 and the specific months-long silent-failure scenario.

### Task 5.4: Regression gate
**Tests:** Full suites

- [x] `pytest tests/` green (14683 passed post-Phase 5 hardening).
- [x] `python -m combat_lab.run_tests --no-history` — 170/170 green.
- [x] Grep audit: `except Exception` in `capture_battle_state` body is gone; narrowed to `except OSError`.

**Notes:** Final regression gate after Phase 5 hardening: 14683 passed / 3 pre-existing build-queue fails / 3 pre-existing AI import errors. Combat Lab fast 162/162, full 170/170. All Phase 5 hardening tests green (5/5 in `test_battle_state_capture_no_mode_kwarg.py`).

## Phase Completion Checklist

- [x] All task checkboxes above are checked
- [x] Decision recorded in `decisions.md`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table

## Rationale (origin of this phase)

This phase was created during a PROJ-270 Phase 13 follow-up crash-fix session on 2026-04-13. The user hit a crash while running `python launcher.py` that surfaced ~40 lines of silent warning spam:

```
Failed to capture initial state: BattleState.capture_from_engine() got an unexpected keyword argument 'mode'
Failed to capture final state: BattleState.capture_from_engine() got an unexpected keyword argument 'mode'
```

The minimal fix (deleting the `mode="test"` kwarg from 2 callers) restored the module to working order — but "working order" means: the module captures battle-state JSON on every Combat Lab run, and that capture path had been completely broken for an unknown duration with zero user impact visible. That invites the question: **does anyone actually read those files?** This phase answers that question instead of accepting the silent-works-as-intended-or-not state.
