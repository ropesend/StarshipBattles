# Phase 1: Inline 1 caller and delete to_roman wrapper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-418 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the single call site at `planet_naming.py:64` with a direct call to `NameRegistry.to_roman(planet_idx)`, then delete the module-level `to_roman()` wrapper at lines 16-28.

Severity tier: Major (small inline + wrapper deletion).

---

## Tasks

### Task 1.1: Inline 1 internal caller and delete wrapper
**File:** `game/strategy/data/planet_naming.py`
**Tests:** `pytest tests/ -k naming`

- [x] Inline `to_roman(planet_idx)` at `planet_naming.py:64` with `NameRegistry.to_roman(planet_idx)` (NameRegistry is already imported in this file)
- [x] Delete the `to_roman()` wrapper function at `planet_naming.py:16-28`
- [x] Verify: `pytest tests/ -k naming` passes; `grep -rn 'planet_naming.to_roman\|from game.strategy.data.planet_naming import to_roman' .` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
