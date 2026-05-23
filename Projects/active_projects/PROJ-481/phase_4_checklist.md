# Phase 4: Audit remediation (Codex consult 2026-05-22)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-481 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address 3 VERIFIED + IN-SCOPE findings from the Codex mid-project audit. See `findings/audit_verification.md` for the full verdict table.

---

## Tasks

### Task 4.1: Narrow `dragged_item` to concrete type (F2) [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/ -k workshop_screen`

- [x] At line 381, change `def dragged_item(self) -> Any:` to `def dragged_item(self) -> "Component | None":` (use string-quoted forward ref consistent with the rest of the file's pattern, e.g. line 373)
- [x] Remove the trailing comment `# narrowing requires concrete drag-item type` (stale after the narrowing)
- [x] Confirm `Component` is already imported (TYPE_CHECKING block) or add it
- [x] Verify: workshop_screen tests pass; mypy clean on file

**Notes:** Per `interaction_controller.py:28,45,96,103` the backing slot is only ever a Component or None. Phase 3 checklist task at line 62 explicitly asked for "(concrete)".

---

### Task 4.2: Modernize `Optional[UIButton]` → `UIButton | None` (F4) [Simple]
**File:** `game/ui/screens/defeat_dialog.py`, `game/ui/screens/turn_failed_dialog.py`
**Tests:** `pytest tests/ -k "defeat_dialog or turn_failed"`

- [x] In `defeat_dialog.py` at line 83: change `self._dismiss_button: Optional[UIButton] = None` → `self._dismiss_button: "UIButton | None" = None` (string-quote to avoid runtime import requirement; or use plain `UIButton | None` if the import is already module-level non-TYPE_CHECKING — check the file)
- [x] In `turn_failed_dialog.py` at line 98: same fix
- [x] If `Optional` is no longer used in the file, remove the import (typing or typing_extensions)
- [x] Verify: targeted tests pass; mypy clean

**Notes:** `docs/03_CONVENTIONS.md:489-492` forbids legacy `Optional[X]` in new/touched code. Phase 3 checklist literally specified `Optional[UIButton]` wording — that's a plan-vs-conventions bug. Mechanical fix.

---

### Task 4.3: Modernize `Optional[Sequence[int]]` → `Sequence[int] | None` (F5) [Simple]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ -k ship_theme`

- [x] At line 241, change `expected: Optional[Sequence[int]]` → `expected: Sequence[int] | None`
- [x] If `Optional` is no longer used in the file, remove the import (N/A — still used at multiple other sites in this file)
- [x] Verify: ship_theme tests pass; mypy clean on file

**Notes:** `phase_3_checklist.md:150` explicitly specified `Sequence[int] | None` modern syntax. Implementer used legacy `Optional[]` — direct deviation from plan wording.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (or close)
