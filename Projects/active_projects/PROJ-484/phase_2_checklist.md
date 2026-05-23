# Phase 2: Single-test-caller migrations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-484 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate two test files to import from canonical modules. Where the re-export line itself is also dead, delete it.

> **Scope correction (2026-05-22):** Task 2.2 originally deleted `from game.simulation.physics_constants import DEFAULT_MAX_MASS` at `ship.py:22` (LEG-A-02). After Codex audit during PROJ-484 execution, that finding was REJECTED — the symbol is used internally at `ship.py:116`, so the line is not a dead re-export. The test-caller migration in `test_ship.py:472` to the canonical path is still beneficial and remains in scope; only the production-side deletion was dropped. See `findings/verification_report.md` Rejected section.

---

## Tasks

### Task 2.1: Migrate `DamageContext` test caller, then delete re-export
**File:** `game/simulation/combat/combat_events.py`
**Tests:** `pytest tests/unit/simulation/combat/test_combat_events.py`

- [x] Update `tests/unit/simulation/combat/test_combat_events.py:14` — change the import of `DamageContext` from `game.simulation.combat.combat_events` to the canonical `game.core.combat_types`. Keep any other imports from `combat_events` intact.
- [x] Delete `from game.core.combat_types import DamageContext  # noqa: F401` at `game/simulation/combat/combat_events.py:62` (and the two-line preamble comment above it that referred specifically to the re-export)
- [x] Verify `grep -rn "from game.simulation.combat.combat_events import DamageContext" .` returns 0 matches

### Task 2.2: Migrate `DEFAULT_MAX_MASS` test caller to canonical path
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [x] Update `tests/unit/entities/test_ship.py:472` — change the import of `DEFAULT_MAX_MASS` from `game.simulation.entities.ship` to the canonical `game.simulation.physics_constants`.
- [x] **Do NOT delete `ship.py:22`.** Per the audit correction (see Status note above), the line is a live internal import used at `ship.py:116`, not a dead re-export.

### Phase Verification
- [x] `combat_events.py:62` re-export is gone; both test callers now use canonical imports
- [x] No new imports through the `combat_events.DamageContext` legacy re-export path

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to project completion

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
