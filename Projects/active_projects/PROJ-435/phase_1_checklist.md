# Phase 1: Audit gap + pick label-home policy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-435 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Decide where UI display labels live (registry vs UI) and
whether `GravityModifier` and `RadiationShield` should be registered.
Output: an updated `decisions.md` row plus a Phase 2 plan.

---

## Tasks

### Task 1.1: Confirm scope of literal sets [Simple]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py`
**Tests:** N/A (audit only)

- [x] Grep for additional hardcoded ability-name lists in
      `game/ui/screens/builder/` that would benefit from the same
      migration (e.g. `_PLANETARY_ABILITIES`, `_SUPERWEAPON_LABELS`)
- [x] Document each list with: ability names, registered status,
      closest matching kind tag
- [x] Note duplications across UI files if any

### Task 1.2: Decide registry-label policy [Medium]
**File:** `Projects/active_projects/PROJ-435/decisions.md`
**Tests:** N/A

- [x] Evaluate Option A vs B vs C from `design.md`
- [x] Consider whether `EffectFacet.display_name` precedent extends
      naturally to a top-level `AbilityMetadata.display_name`
- [x] Record decision with rationale

### Task 1.3: Decide `GravityModifier` / `RadiationShield` status [Simple]
**File:** `Projects/active_projects/PROJ-435/decisions.md`
**Tests:** N/A

- [x] Inspect the simulation classes to confirm they are real
      planet-scope activatable abilities
- [x] Decide: register them with kind tags (e.g.
      `PLANETARY_DEFENSE` or `ENERGY_DRAINING`) OR document them as
      UI-only legacy and plan to remove them

### Task 1.4: Sketch Phase 2 migration plan [Medium]
**File:** `Projects/active_projects/PROJ-435/plan.md`
**Tests:** N/A

- [x] Phase 2 file list (production + tests)
- [x] TDD test names (regression guards against new literals)
- [x] Estimate file diff size

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
