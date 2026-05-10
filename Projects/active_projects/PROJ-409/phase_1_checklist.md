# Phase 1: Close MAJ-013 and MAJ-014

**Status:** Complete
**Objective:** Land definitive closure (active or ratified) on the two PROJ-395 deferrals.

---

## Tasks

### Task 1.1: Investigate MAJ-013 — EventBus Pattern #10 shim [Medium]
**File:** TBD — discover

- [x] Read `Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-395_report.md` for the MAJ-013 writeup.
- [x] Read PROJ-395's findings/source_review.md (verification_report.md does not exist — PROJ-395 used `findings/source_review.md`) and the original audit at `Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/findings/07_architecture_rules_report.md` (the canonical MAJ-013 writeup, line 101-103).
- [x] Located the shim's original site: `game/core/event_logging.py:57-88` (module-level `log_event` / `set_event_handler` / `get_event_handler`). Verified it is **already deleted** by PROJ-390 — see docstring at `game/core/event_logging.py:30-32` and `Projects/active_projects/PROJ-390/plan.md:21`. No remaining call sites: imports only `EventBus` (4 import sites in `game/`).
- [x] Decided: closure mode **(b) ratified — already actively closed by PROJ-390**. The PROJ-395 reviewer flagged the file but did not pick up the prior closure. Documented fully in `decisions.md`.
- [x] No code change needed for MAJ-013.

**Notes:** The remaining `Pattern #10` references in `game/simulation/entities/projectile.py`, `game/strategy/data/empire.py`, `game/strategy/data/fleet.py`, `game/ui/screens/builder/event_bus.py` are PROJ-382 Phase 2 *constructor-injection* breadcrumbs — the canonical Pattern #10 implementation, not the retired shim. Confirmed by reading each cite.

### Task 1.2: TDD — write failing test for MAJ-014 canonical path [Medium]
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py` (or closest)

- [x] Read `game/ui/screens/strategy_game_state_manager.py:19, 149-158` to see the current import + defensive catch.
- [x] Test module already exists at `tests/unit/ui/screens/test_strategy_game_state_manager.py`.
- [x] Wrote `TestProcessFullTurnErrorBoundary` with two tests:
  - `test_turn_failed_error_opens_dialog_clears_overlay_skips_autosave` — canonical path: `_show_turn_failed_dialog` is called once, `current_tick`/`total_ticks` cleared in `finally`, `turn_processing` cleared, `SaveGameService.save_game` NOT called, `open_event_log_with_events` NOT called.
  - `test_raw_engine_phase_error_propagates_uncaught` — raw `EnginePhaseError` is re-raised out of `process_full_turn` (architectural contract: facade is the only converter).
- [x] First test PASSED against unmodified code; second test FAILED against unmodified code (the defensive catch swallowed it). RED confirmed.

**Notes:** RED captured pytest log line ``Turn processing failed in phase 'bypass' (raw EnginePhaseError — facade conversion bypassed): raw bypass`` — exactly the dead-code path we're deleting.

### Task 1.3: Remove the defensive `EnginePhaseError` catch [Simple]
**File:** `game/ui/screens/strategy_game_state_manager.py:19, 149-158`

- [x] Deleted the `EnginePhaseError` import at line 19 (only `TurnFailedError` remains).
- [x] The `except` block was structurally separate (two `except` clauses); deleted the entire `except EnginePhaseError as e:` branch (lines 149-158).
- [x] Tightened `_show_turn_failed_dialog` signature from `TurnFailedError | EnginePhaseError` to just `TurnFailedError`.
- [x] Regression test passes (raw `EnginePhaseError` now propagates uncaught).
- [x] Focused suite `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`: 24/24 PASS.
- [x] Broader UI suite `pytest tests/integration/ui/ -k turn`: 37/37 PASS — required updating `tests/integration/ui/test_strategy_turn_error_boundary.py` to inject `TurnFailedError` (matching production after facade conversion) and to wrap the real-engine `EnginePhaseError` through the same conversion.

**Notes:** Commit `c0ff79f92`.

### Task 1.4: Document the closure in `decisions.md` [Simple]

- [x] MAJ-013 row in `decisions.md` — closure mode "ratified — already actively closed by PROJ-390"; rationale documented with file:line citations.
- [x] MAJ-014 row in `decisions.md` — closure mode "actively deleted"; commit `c0ff79f92`; PROJ-408 C-02 unit-test reference recorded.
- [x] Cross-reference added in `Projects/active_projects/PROJ-395/decisions.md`.

**Notes:**

### Task 1.5: Cross-reference closure in PROJ-395 plan
**File:** `Projects/active_projects/PROJ-395/{plan,decisions}.md`

- [x] Added a note in `Projects/active_projects/PROJ-395/decisions.md` pointing to PROJ-409 commit `c0ff79f92` as the final closure of MAJ-013 + MAJ-014.
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-395` — PASS.

**Notes:**

### Task 1.6: Closeout
- [x] Phase 1 status `Complete`
- [x] Plan.md updated
- [x] `Projects/projects_index.md` row for PROJ-409 set to `Complete`
- [x] Validators PASS
- [x] Commits: `c0ff79f92` (MAJ-014 fix) + closeout commit (this).
- [x] Verification report at `findings/verification_report.md`

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] Focused suites pass
- [x] `python Projects/scripts/validate_phase.py PROJ-409 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-409` PASSED
