# Phase 7: Builder Screens [23+ instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix builder screen duck typing using `ICombatShip` Protocol. stats_config.py dynamic dispatch stays as-is (docstring only).

---

## Tasks

### Task 7.1: weapons_viewmodel.py [Simple]
**File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add TYPE_CHECKING import: `from game.core.protocols import ICombatShip`
- [x] Lines 304, 383, 474: Replace `hasattr(ship, 'get_total_sensor_score')` → type ship param with `'ICombatShip'` (builder always has simulation Ship)
- [x] Line 147: Replace `getattr(ship, 'total_defense_score', 0.0)` → `ship.total_defense_score` (in ICombatShip Protocol)
- [x] Line 396: `hasattr(ab, 'get_damage')` → **keep** (abilities are polymorphic, not all have `get_damage`)
- [x] Verify: Run tests

**Notes:** Typed set_target, load_weapons, _get_all_weapons, calculate_threshold_ranges, get_points_of_interest, calculate_tooltip_data with ICombatShip. Replaced 3 hasattr checks with direct method calls.

### Task 7.2: stats_config.py [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add docstring to `StatDefinition` class documenting the dynamic dispatch pattern:
  - Explain that `get_value()` uses `getattr(ship, self.attr_key, 0)` intentionally
  - This is the core mechanism for declaratively mapping stat names to ship attributes
  - Must NOT be replaced with typed access — the attr_key is a runtime string
- [x] Fix non-dynamic getattr in helper functions where ship type is known:
  - Lines 111, 124, 133-134, 143-149: **KEEP** - these receive ships through generic getter lambdas defined in JSON config, ships may be mocks. Intentional fallback defaults.
- [x] **Leave** `StatDefinition.get_value()` with getattr (legitimate dynamic dispatch)
- [x] Verify: Run tests

**Notes:** Added comprehensive docstring explaining dynamic dispatch pattern. All getattr in helper functions are intentional fallbacks for ships that may not have all attributes.

### Task 7.3: Other builder files [Medium]
**Files:** `components.py`, `left_panel.py`, `right_panel.py`, `detail_panel.py`, `layer_panel.py`, `interaction_controller.py`, `modifier_row.py`, `grouping_strategies.py`, `schematic_view.py`, `structure_list_items.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Audit each file for hasattr/getattr instances
- [x] Classify each instance:
  - **(self-guard)** `hasattr(self, 'widget')` → leave: right_panel.py:56,332, left_panel.py:214
  - **(framework)** `hasattr(event, 'ui_element')` → leave: modifier_row.py:269
  - **(fixable)** `getattr(obj, 'known_attr', default)` where type is known → NONE FOUND - all are intentional fallbacks
- [x] Add `ICombatShip` or other Protocol type hints where types are known → NONE NEEDED - builder uses polymorphic types
- [x] Replace fixable instances with direct typed access → NONE FOUND
- [x] Keep UI framework/self-init guards
- [x] Verify: Run tests

**Notes:**
All remaining patterns classified as intentional:
- **Self-init guards:** right_panel.py:56,332, left_panel.py:214
- **Framework checks:** modifier_row.py:269,177
- **Polymorphic interface checks:** layer_panel.py:349,377, left_panel.py:352, interaction_controller.py:146,152, detail_panel.py:94,144
- **Optional attributes with fallbacks:** right_panel.py:79,91,172,181,241, schematic_view.py:70, left_panel.py:254, structure_list_items.py:434, grouping_strategies.py:42
- **Different ship types (Ship vs ShipDesign):** components.py:84-92,123,125

### Task 7.4: Run tests [Simple]
**Tests:** `pytest tests/unit/ui/ -n 4`

- [x] Run: `pytest tests/unit/ui/ -n 4` — all pass (3148 passed)

**Notes:** Full test suite: 12711 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
