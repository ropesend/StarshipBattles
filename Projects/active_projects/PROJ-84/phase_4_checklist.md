# Phase 4: Update UI Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert all UI code that reads or mutates layer data from dict access to LayerData attribute access.

---

## Tasks

### Task 4.1: Update Builder layer_panel.py [Medium]
**File:** `game/ui/screens/builder/layer_panel.py`
**Tests:** `pytest tests/unit/builder/ -x`

- [ ] Line ~137: `data['components']` → `data.components`
- [ ] Line ~140: `data.get('max_mass_pct', 1.0)` → `data.max_mass_pct`
- [ ] Lines ~316-320: Component list access for drag/drop → `.components`
- [ ] Search entire file for any remaining `['` or `.get(` dict patterns on layer data
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.2: Update Builder main.py [Simple]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x`

- [ ] Lines ~1041-1045: Clear operation — replace manual field resets (`layer_data['components'] = []`, `layer_data['hp_pool'] = 0`, etc.) with `layer_data.clear()`
- [ ] Lines ~508-544: Any other layer dict access → attribute access
- [ ] Search for remaining dict-style access patterns
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.3: Update WorkshopEventRouter [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/workshop/ -x`

- [ ] Line ~223: `gui.ship.layers[target_layer]['components']` → `.components`
- [ ] Lines ~267, ~309: Same pattern
- [ ] Search for remaining dict-style access
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.4: Update GameRenderer [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/unit/ui/ -x`

- [ ] Line ~189: `ship.layers[ltype]['components']` → `.components`
- [ ] Search for remaining dict-style access
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.5: Update ShipStatsRenderer [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ -x`

- [ ] Layer `.get()` calls → attribute access
- [ ] Search for remaining dict-style access
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.6: Update BattleUIService [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/services/battle_ui_service/ -x`

- [ ] Layer iteration access → attribute access
- [ ] Search for remaining dict-style access
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.7: Update Builder stats_config.py [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/builder/ -x`

- [ ] Line ~118: `.get('max_hp_pool', 0)` → `.max_hp_pool`
- [ ] Search for remaining dict-style access
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.8: Update AI interface [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/ -x`

- [ ] Update `get_layers()` return type annotation to `Dict[LayerType, LayerData]`
- [ ] Add import for LayerData
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.9: Incremental test run [Simple]
**Tests:** `pytest tests/unit/builder/ tests/unit/ui/ tests/unit/workshop/ tests/unit/ai/ -x`

- [ ] Run combined test suite for Phase 4 scope
- [ ] Fix any failures
- [ ] Verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
