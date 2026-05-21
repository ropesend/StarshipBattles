# Phase 4: Codex-audit remediation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-471 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remediate the VERIFIED findings from the one-round Codex audit
(`AgentCoordination/Scratchpad/Consult/proj471_audit/audit.md.invalid-output-*.txt` —
Codex completed the audit; the harness only rejected the file for missing
`consult/v1` frontmatter, not for content). 4 findings, all verified against
live code. Each fixed via TDD.

---

## Tasks

### Task 4.1: Fix `BattleSetupState.from_dict` duplicate fleet IDs after load [Medium] — VERIFIED (Major)
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_fleet_id_isolation.py tests/unit/ui/screens/test_battle_setup_state.py`

- [x] Codex finding 1: `from_dict` reset the per-state counter to `_FLEET_ID_BASE + 1` but never advanced it past the IDs of the loaded fleets, so the next `create_fleet()` reused an existing id (reproduced `[1001, 1001, 1002]`). Save/load identity regression on a serialized UI payload.
- [x] Fix: after loading sides, advance the state counter to `max(loaded fleet ids) + 1` (start the `itertools.count` above the highest loaded id).
- [x] Regression test: load a state with fleets and assert a post-load `create_fleet()` id does not collide with any loaded id.
- [x] Verify: pytest green.

### Task 4.2: Make `reset_component_caches` not diverge from a live ctx [Medium] — VERIFIED (Major)
**File:** `game/simulation/components/component_loader.py`
**Tests:** `pytest tests/unit/simulation/components/test_cache_manager_setter.py tests/unit/core/test_application_context.py`

- [x] Codex finding 2: `reset_component_caches()` swapped in a NEW `ComponentCacheManager`, so a live `ctx.component_cache` reference diverged from the module default after reset (reproduced `ctx.component_cache is get_default_cache_manager()` flipping `True`->`False`). This is exactly the singleton-divergence surface the task aimed to close.
- [x] Fix: `reset_component_caches()` now clears the EXISTING manager's cache fields in place (does not replace the instance), so `ctx.component_cache` stays valid and consistent with the module default across resets.
- [x] Regression test: assert `ctx.component_cache is get_default_cache_manager()` BEFORE and AFTER `reset_component_caches()`, and that the cache fields are actually cleared.
- [x] Verify: pytest green.

### Task 4.3: Strengthen the Phase 1 determinism characterization [Simple] — VERIFIED (test-strength gap; no code regression)
**File:** `tests/unit/simulation/systems/test_battle_combat_subsystems.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_combat_subsystems.py`

- [x] Codex finding 3: the determinism test only compared ten raw `rng.random()` values; it did not assert identical battle outcome through the refactored `CombatSubsystems` path. (Codex confirmed NO actual regression — `tests/integration/fleet_combat/test_battle_determinism.py` passes — this is a proof-strength gap only.)
- [x] Fix: added a test that runs the same seeded battle twice through `run_battle`/`BattleEngine` and asserts identical winner + per-ship HP outcome (real combat-behavior equivalence), not just raw rng draws.
- [x] Verify: pytest green.

### Task 4.4: Fix serializable-registry seam test cleanup [Low] — VERIFIED
**File:** `tests/unit/core/test_serializable_registry_seam.py`
**Tests:** `pytest tests/unit/core/test_serializable_registry_seam.py`

- [x] Codex finding 4: the second test called `clear_serializable_registry()` twice with no baseline restore, leaving the process-global registry empty (the seam is opt-in / not autouse-reset, so a leaking test matters).
- [x] Fix: snapshot the baseline with `get_serializable_registry()` and restore it via `clear_serializable_registry(baseline)` in cleanup.
- [x] Verify: pytest green; registry restored to baseline after the test.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
