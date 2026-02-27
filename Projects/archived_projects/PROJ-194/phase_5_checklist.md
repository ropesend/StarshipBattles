# Phase 5: Remaining Scattered Instances

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clean up the remaining scattered hasattr/getattr instances across builder files. Run full test suite for final verification.

---

## Tasks

### Task 5.1: interaction_controller.py — Interface method hasattr removal [Simple]
**File:** `game/ui/screens/builder/interaction_controller.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 146: `if hasattr(self.builder.left_panel, 'get_add_count'):` → remove check (BuilderLeftPanel always has get_add_count at left_panel.py:452)
- [x] Line 152: `if hasattr(target, 'suppress_toggle'):` → remove check (LayerPanel always has suppress_toggle at layer_panel.py:368; it's the only drop target)
- [x] Verify: Run tests

**Notes:** Both methods are defined on the concrete classes always used. Added suppress_toggle() to DropTarget protocol.

---

### Task 5.2: layer_panel.py — Item method/property cleanup [Simple]
**File:** `game/ui/screens/builder/layer_panel.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 349: `if hasattr(item, 'handle_event'):` → remove check (all item types — IndividualComponentItem, LayerComponentItem, LayerHeaderItem — define handle_event)
- [x] Line 377: `if getattr(item, 'is_selected', False):` → `if item.is_selected:` (already guarded by isinstance check on line 376 for types that have is_selected)
- [x] Verify: Run tests

**Notes:** Line 377 is inside `isinstance(item, (LayerComponentItem, IndividualComponentItem))` guard, so is_selected is always present.

---

### Task 5.3: grouping_strategies.py — Modifier definition property [Simple]
**File:** `game/ui/screens/builder/grouping_strategies.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 42: `if getattr(m.definition, 'readonly', False):` → replaced with `if m.definition.readonly:`. Modifier class always has `readonly` attribute (component_constants.py:35).
- [x] Verify: Run tests

**Notes:** ModifierDefinition (Modifier class) always sets self.readonly in __init__.

---

### Task 5.4: structure_list_items.py — Event handler timer check [Simple]
**File:** `game/ui/screens/builder/structure_list_items.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 434: `if getattr(self.event_handler, 'toggle_suppress_timer', 0) > 0:` → replaced with `if self.event_handler.toggle_suppress_timer > 0:`.
- [x] Verify: Run tests

**Notes:** LayerPanel.toggle_suppress_timer is initialized in LayerPanel.__init__ (line 58).

---

### Task 5.5: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite (not --testmon) to verify no regressions
- [x] Confirm baseline: 12721 passed, 1 skipped
- [x] Verify: All tests pass

**Notes:** Fixed MockDropTarget in test_builder_interaction.py to include suppress_toggle() method.

---

### Task 5.6: Final grep audit [Simple]
- [x] Run `grep -rn "getattr\|hasattr" game/ui/screens/builder/ game/ui/screens/workshop_*.py game/ui/panels/design_report_panel.py game/ui/panels/modifier_impact_grid.py` to confirm all in-scope instances are addressed
- [x] Document any remaining instances with justification (e.g., StatDefinition.get_value intentional dispatch)
- [x] Verify: Only intentionally-kept instances remain

**Notes:** Remaining instances documented below:
- `stats_config.py:42,44` - INTENTIONAL: StatDefinition.get_value() generic dispatch
- `modifier_row.py:269` - Pygame event boundary (out of scope)
- `modifier_impact_grid.py:175` - Legitimate class feature check (STAT_BINDINGS)
- `detail_panel.py:94,144` - Type checking for Union types
- `left_panel.py:214,254,352` - Optional attrs / init-order patterns
- `schematic_view.py:70` - Optional attr
- `workshop_viewmodel.py:166` - Type checking for Union type

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
