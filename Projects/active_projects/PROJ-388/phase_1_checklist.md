# Phase 1: Migrate consumer + delete `ModifierLogic` class

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-388 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the `ModifierEditorPanel._build_panels` consumer to use `ModifierLogicService` directly via constructor injection, then delete the deprecated `ModifierLogic` static-wrapper class. The class is explicitly marked as a Rule-3-violating shim by its own `# Deprecated: ModifierLogic static wrapper` comment.

---

## Tasks

### Task 1.1: Enumerate consumers
**File:** `game/`, `tests/`, `combat_lab/`
**Tests:** —

- [ ] Run `grep -rn "ModifierLogic\b" game/ tests/ combat_lab/` to enumerate every reference (LEG-03-009)
- [ ] Confirm `ModifierEditorPanel._build_panels` is the primary consumer; record any additional sites

### Task 1.2: Migrate consumers to `ModifierLogicService`
**File:** `game/ui/panels/modifier_editor_panel.py` (and any other consumer found in 1.1)
**Tests:** `pytest tests/ -k modifier_editor`

- [ ] Replace `ModifierLogic.<static_method>(...)` calls with `self._modifier_logic.<method>(...)` (instance via constructor injection)
- [ ] Wire `ModifierLogicService` into the consumer's `__init__` via the existing dependency-injection path (likely `ApplicationContext` per Pattern 1)
- [ ] Verify: consumer no longer imports `ModifierLogic`

### Task 1.3: Delete the `ModifierLogic` class
**File:** `game/ui/screens/builder/modifier_logic.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Delete the entire `ModifierLogic` class starting at line 177, including the `calculate_snap_value` static (LEG-03-009 + LEG-03-015)
- [ ] Verify: file now only contains `ModifierLogicService` (the canonical class)
- [ ] Verify: pytest passes; `grep -rn "from game.ui.screens.builder.modifier_logic import ModifierLogic\b" .` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
