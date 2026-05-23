# Phase 1: Zero-call-site deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-484 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete two re-export / side-effect-import lines that have zero call sites across the entire repo. Both ship as a single quick-deletion PR with no migration required.

---

## Tasks

### Task 1.1: Delete `CombatConstants` re-export in `ship.py`
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/ -k test_ship`

- [ ] Delete `from game.core.constants import CombatConstants` at line 23 (0 call sites — single-PR deletion)
- [ ] If `DEFAULT_MAX_MASS` line 22 has also been removed by Phase 2 (same PR), delete the re-export header comment at line 21 ("Re-export for backward compatibility and convenient access")
- [ ] Verify `Ship` class's internal use of `CombatConstants.DEFAULT_MAX_TARGETS` (line ~190) continues to resolve through the existing direct import inside `ship.py` (not via the deleted re-export)

### Task 1.2: Delete unused `_null_provider` side-effect import
**File:** `game/ui/services/image/__init__.py`
**Tests:** `pytest tests/unit/ui/services/image/`

- [ ] Delete `from game.ui.services.image import null_provider as _null_provider  # noqa: F401` at line 37 (0 call sites — single-PR deletion)
- [ ] Verify the explicit `register_image_provider("null", NullImageProvider)` registration at line 42 remains and is the sole source of the "null" provider binding
- [ ] Confirm `null_provider.py` has no module-level side effects that would now be missed (verifier confirmed it has no `register_image_provider` call)

### Phase Verification
- [ ] `pytest tests/ --testmon` passes
- [ ] `grep -rn "from game.simulation.entities.ship import CombatConstants" .` returns 0 matches
- [ ] `grep -rn "_null_provider" game/` returns 0 matches

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
