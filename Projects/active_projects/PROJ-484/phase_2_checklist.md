# Phase 2: Single-test-caller deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-484 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate two test files to import from canonical modules, then delete the corresponding re-export lines. Each migration is one-line in the test plus one-line deletion in production.

---

## Tasks

### Task 2.1: Migrate `DamageContext` test caller, then delete re-export
**File:** `game/simulation/combat/combat_events.py`
**Tests:** `pytest tests/unit/simulation/combat/test_combat_events.py`

- [ ] Update `tests/unit/simulation/combat/test_combat_events.py:14` — change the import of `DamageContext` from `game.simulation.combat.combat_events` to the canonical `game.core.combat_types`. Keep any other imports from `combat_events` intact.
- [ ] Delete `from game.core.combat_types import DamageContext  # noqa: F401` at `game/simulation/combat/combat_events.py:62`
- [ ] Verify `grep -rn "from game.simulation.combat.combat_events import DamageContext" .` returns 0 matches

### Task 2.2: Migrate `DEFAULT_MAX_MASS` test caller, then delete re-export
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [ ] Update `tests/unit/entities/test_ship.py:472` — change the import of `DEFAULT_MAX_MASS` from `game.simulation.entities.ship` to the canonical `game.simulation.physics_constants`.
- [ ] Delete `from game.simulation.physics_constants import DEFAULT_MAX_MASS` at `game/simulation/entities/ship.py:22`
- [ ] If `CombatConstants` re-export at line 23 was already removed in Phase 1 of this project, also remove the now-orphan re-export header comment at line 21 ("Re-export for backward compatibility and convenient access") if it has not already been removed
- [ ] Verify `grep -rn "from game.simulation.entities.ship import DEFAULT_MAX_MASS" .` returns 0 matches

### Phase Verification
- [ ] `pytest tests/ --testmon` passes
- [ ] Both re-export lines are gone; both test callers now use canonical imports
- [ ] No new imports through the legacy re-export paths

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to project completion

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
