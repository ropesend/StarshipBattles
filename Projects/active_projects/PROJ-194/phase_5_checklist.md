# Phase 5: Remaining Scattered Instances

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up the remaining scattered hasattr/getattr instances across builder files. Run full test suite for final verification.

---

## Tasks

### Task 5.1: interaction_controller.py — Interface method hasattr removal [Simple]
**File:** `game/ui/screens/builder/interaction_controller.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 146: `if hasattr(self.builder.left_panel, 'get_add_count'):` → remove check (BuilderLeftPanel always has get_add_count at left_panel.py:452)
- [ ] Line 152: `if hasattr(target, 'suppress_toggle'):` → remove check (LayerPanel always has suppress_toggle at layer_panel.py:368; it's the only drop target)
- [ ] Verify: Run tests

**Notes:** Both methods are defined on the concrete classes always used.

---

### Task 5.2: layer_panel.py — Item method/property cleanup [Simple]
**File:** `game/ui/screens/builder/layer_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 349: `if hasattr(item, 'handle_event'):` → remove check (all item types — IndividualComponentItem, LayerComponentItem, LayerHeaderItem — define handle_event)
- [ ] Line 377: `if getattr(item, 'is_selected', False):` → `if item.is_selected:` (already guarded by isinstance check on line 376 for types that have is_selected)
- [ ] Verify: Run tests

**Notes:** Line 377 is inside `isinstance(item, (LayerComponentItem, IndividualComponentItem))` guard, so is_selected is always present.

---

### Task 5.3: grouping_strategies.py — Modifier definition property [Simple]
**File:** `game/ui/screens/builder/grouping_strategies.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 42: `if getattr(m.definition, 'readonly', False):` → check if ModifierDefinition always has `readonly` attribute. If yes, replace with `if m.definition.readonly:`. If no, keep getattr (legitimate optional attr).
- [ ] Verify: Run tests

**Notes:** Check ModifierDefinition class to confirm.

---

### Task 5.4: structure_list_items.py — Event handler timer check [Simple]
**File:** `game/ui/screens/builder/structure_list_items.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 434: `if getattr(self.event_handler, 'toggle_suppress_timer', 0) > 0:` → check if event_handler (LayerPanel) always has toggle_suppress_timer. If yes, replace with `if self.event_handler.toggle_suppress_timer > 0:`.
- [ ] Verify: Run tests

**Notes:** LayerPanel.suppress_toggle() sets toggle_suppress_timer, and it's initialized in LayerPanel.__init__ (check to confirm).

---

### Task 5.5: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite (not --testmon) to verify no regressions
- [ ] Confirm baseline: 12,718+ passed, 0 failures
- [ ] Verify: All tests pass

**Notes:**

---

### Task 5.6: Final grep audit [Simple]
- [ ] Run `grep -rn "getattr\|hasattr" game/ui/screens/builder/ game/ui/screens/workshop_*.py game/ui/panels/design_report_panel.py game/ui/panels/modifier_impact_grid.py` to confirm all in-scope instances are addressed
- [ ] Document any remaining instances with justification (e.g., StatDefinition.get_value intentional dispatch)
- [ ] Verify: Only intentionally-kept instances remain

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
