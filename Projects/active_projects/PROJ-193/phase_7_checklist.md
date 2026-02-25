# Phase 7: Builder Screens [23+ instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix builder screen duck typing using `ICombatShip` Protocol. stats_config.py dynamic dispatch stays as-is (docstring only).

---

## Tasks

### Task 7.1: weapons_viewmodel.py [Simple]
**File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add TYPE_CHECKING import: `from game.core.protocols import ICombatShip`
- [ ] Lines 304, 383, 474: Replace `hasattr(ship, 'get_total_sensor_score')` → type ship param with `'ICombatShip'` (builder always has simulation Ship)
- [ ] Line 147: Replace `getattr(ship, 'total_defense_score', 0.0)` → `ship.total_defense_score` (in ICombatShip Protocol)
- [ ] Line 396: `hasattr(ab, 'get_damage')` → **keep** (abilities are polymorphic, not all have `get_damage`)
- [ ] Verify: Run tests

**Notes:**

### Task 7.2: stats_config.py [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add docstring to `StatDefinition` class documenting the dynamic dispatch pattern:
  - Explain that `get_value()` uses `getattr(ship, self.attr_key, 0)` intentionally
  - This is the core mechanism for declaratively mapping stat names to ship attributes
  - Must NOT be replaced with typed access — the attr_key is a runtime string
- [ ] Fix non-dynamic getattr in helper functions where ship type is known:
  - Lines 111, 124, 133-134, 143-149: If these receive a concrete Ship, type them and use direct access
- [ ] **Leave** `StatDefinition.get_value()` with getattr (legitimate dynamic dispatch)
- [ ] Verify: Run tests

**Notes:**

### Task 7.3: Other builder files [Medium]
**Files:** `components.py`, `left_panel.py`, `right_panel.py`, `detail_panel.py`, `layer_panel.py`, `interaction_controller.py`, `modifier_row.py`, `grouping_strategies.py`, `schematic_view.py`, `structure_list_items.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Audit each file for hasattr/getattr instances
- [ ] Classify each instance:
  - **(self-guard)** `hasattr(self, 'widget')` → leave
  - **(framework)** `hasattr(event, 'ui_element')` → leave
  - **(fixable)** `getattr(obj, 'known_attr', default)` where type is known → fix
- [ ] Add `ICombatShip` or other Protocol type hints where types are known
- [ ] Replace fixable instances with direct typed access
- [ ] Keep UI framework/self-init guards
- [ ] Verify: Run tests

**Notes:**

### Task 7.4: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [ ] Run: `pytest tests/unit/ui/ -n 4` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
