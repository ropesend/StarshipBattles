# Phase 1: Zero-call-site deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-484 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete one side-effect-import line that has zero call sites across the entire repo.

> **Scope correction (2026-05-22):** The original Phase 1 also included deletion of `from game.core.constants import CombatConstants` at `ship.py:23` (LEG-A-01). After Codex audit during PROJ-484 execution, that finding was REJECTED — the symbol is used internally at `ship.py:190`, so the line is not a dead re-export. Task removed. See `findings/verification_report.md` Rejected section.

---

## Tasks

### Task 1.1: Delete unused `_null_provider` side-effect import
**File:** `game/ui/services/image/__init__.py`
**Tests:** `pytest tests/unit/ui/services/image/`

- [x] Delete `from game.ui.services.image import null_provider as _null_provider  # noqa: F401` at line 37 (0 call sites — single-PR deletion)
- [x] Verify the explicit `register_image_provider("null", NullImageProvider)` registration at line 42 remains and is the sole source of the "null" provider binding
- [x] Confirm `null_provider.py` has no module-level side effects that would now be missed (verifier confirmed it has no `register_image_provider` call)

### Phase Verification
- [x] `grep -rn "_null_provider" game/` returns 0 matches

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
