# Phase 4: Update UI Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert all UI code that reads or mutates layer data from dict access to LayerData attribute access.

---

## Tasks

### Task 4.1: Update Builder layer_panel.py [Medium]
**File:** `game/ui/screens/builder/layer_panel.py`
**Tests:** `pytest tests/unit/builder/ -x`

- [x] Line ~137: `data['components']` → `data.components`
- [x] Line ~140: `data.get('max_mass_pct', 1.0)` → `data.max_mass_pct`
- [x] Lines ~316-320: Component list access for drag/drop → `.components`
- [x] Search entire file for any remaining `['` or `.get(` dict patterns on layer data
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.2: Update Builder main.py [Simple]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x`

- [x] Lines ~1041-1045: Clear operation — replace manual field resets (`layer_data['components'] = []`, `layer_data['hp_pool'] = 0`, etc.) with `layer_data.clear()`
- [x] Lines ~508-544: Any other layer dict access → attribute access
- [x] Search for remaining dict-style access patterns
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.3: Update WorkshopEventRouter [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/workshop/ -x`

- [x] Line ~223: `gui.ship.layers[target_layer]['components']` → `.components`
- [x] Lines ~267, ~309: Same pattern
- [x] Search for remaining dict-style access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.4: Update GameRenderer [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/unit/ui/ -x`

- [x] Line ~189: `ship.layers[ltype]['components']` → `.components`
- [x] Search for remaining dict-style access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.5: Update ShipStatsRenderer [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ -x`

- [x] Layer `.get()` calls → attribute access
- [x] Search for remaining dict-style access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.6: Update BattleUIService [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/battle_ui_service/ -x`

- [x] Layer iteration access → attribute access
- [x] Search for remaining dict-style access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.7: Update Builder stats_config.py [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/builder/ -x`

- [x] Line ~118: `.get('max_hp_pool', 0)` → `.max_hp_pool`
- [x] Search for remaining dict-style access
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.8: Update AI interface [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/ -x`

- [x] Update `get_layers()` return type annotation to `Dict[LayerType, LayerData]`
- [x] Add import for LayerData
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 4.9: Incremental test run [Simple]
**Tests:** `pytest tests/unit/builder/ tests/unit/ui/ tests/unit/workshop/ tests/unit/ai/ -x`

- [x] Run combined test suite for Phase 4 scope
- [x] Fix any failures
- [x] Verify all pass

**Notes:** 1635 tests passed during Phase 4 verification.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
