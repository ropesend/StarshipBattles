# Phase 4: Legacy Stats & Test Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove legacy ship stats field re-exports and update all consumers.

**Risk:** Medium - affects 33 files but legacy fields are computed, not stored

---

## Tasks

### Task 4.1: Remove legacy field re-exports from ship_stats_service.py [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

**Legacy fields to remove from return dict (Lines 247-252):**
- `max_fuel` → consumers should use `resource_storage['fuel']`
- `max_energy` → consumers should use `resource_storage['energy']`
- `max_ammo` → consumers should use `resource_storage['ammo']`
- `strategic_fuel_per_hex` → consumers should use `resource_consumption_per_hex['fuel']`
- `warp_energy_cost` → consumers should use `warp_resource_costs['energy']`
- `warp_fuel_cost` → consumers should use `warp_resource_costs['fuel']`

- [x] Remove lines 247-252 (legacy field re-exports)
- [x] Keep only the new dict-based fields in return
- [x] Verify: Return dict has no legacy field names

**Notes:** Legacy re-exports removed. Return dict now only contains new dict-based fields. Tests updated to use new format.

---

### Task 4.2: Remove legacy fallback extraction logic [Medium]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

**Lines to simplify:**
- Lines 90-98: Legacy `max_fuel`, `max_energy`, `max_ammo` extraction
- Lines 100-103: Legacy `strategic_fuel_per_hex` extraction
- Lines 105-111: Legacy `warp_energy_cost`, `warp_fuel_cost` extraction
- Lines 214-234: Legacy WarpJump `energy_cost`/`fuel_cost` support

- [x] Remove fallback extraction for legacy expected_stats fields
- [x] Use only ability-based resource system
- [x] Verify: Stats calculation uses component abilities only

**Notes:** Fallback now directly uses new dict fields from expected_stats. Legacy extraction removed. WarpJump energy_cost/fuel_cost support removed - use ResourceConsumption with warp_jump trigger instead. warp_resource_costs now only populated when warp drive is functional (100% HP).

---

### Task 4.3: Update ShipInstance convenience methods [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance_proj08.py -v`

**Methods to update to use new dict format:**

| Method | Current | New |
|--------|---------|-----|
| `get_fuel_cost_per_hex()` | `stats.get('strategic_fuel_per_hex', 0)` | `stats.get('resource_consumption_per_hex', {}).get('fuel', 0)` |
| `get_current_fuel()` | `stats.get('max_fuel', 0)` | `stats.get('resource_storage', {}).get('fuel', 0)` |
| `get_warp_energy_cost()` | `stats.get('warp_energy_cost', 0)` | `stats.get('warp_resource_costs', {}).get('energy', 0)` |
| `get_warp_fuel_cost()` | `stats.get('warp_fuel_cost', 0)` | `stats.get('warp_resource_costs', {}).get('fuel', 0)` |
| `get_current_energy()` | `stats.get('max_energy', 0)` | `stats.get('resource_storage', {}).get('energy', 0)` |

- [x] Update `get_fuel_cost_per_hex()` (line ~217)
- [x] Update `get_current_fuel()` (line ~226)
- [x] Update `get_warp_energy_cost()` (line ~256)
- [x] Update `get_warp_fuel_cost()` (line ~265)
- [x] Update `get_current_energy()` (line ~274)
- [x] Update any other methods referencing legacy fields
- [x] Verify: All methods work with new dict format

**Notes:** All convenience methods updated. Also updated `get_resource_display()` to use resource_storage dict.

---

### Task 4.4: Update has_warp_capability() [Simple]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/test_ship_stats_service.py -v`

**Current State (Lines 476-486):**
Uses legacy `warp_energy_cost` and `max_energy` fields

- [x] Update to use `warp_resource_costs` and `resource_storage` dicts
- [x] Verify: Warp capability detection still works

**Notes:** Updated in earlier phase work (PROJ-11). Now uses new dict format correctly.

---

### Task 4.5: Update UI code [Medium]
**Files:** UI layer files
**Tests:** `pytest tests/ui/ -v`

**Files to update:**

| File | Location | Change |
|------|----------|--------|
| `game/ui/screens/fleet_report_window.py` | Lines ~809-818 | Use `resource_storage['fuel']` instead of `max_fuel` |
| `game/ui/renderer/renderer.py` | Lines ~177-183 | Update resource display |

- [x] Update `fleet_report_window.py` to use new dict fields
- [x] Update `renderer.py` if it uses legacy fields
- [x] Search for other UI files: `grep -rn "max_fuel\|max_energy\|max_ammo" game/ui/`
- [x] Update all found occurrences
- [x] Verify: UI displays correctly

**Notes:** fleet_report_filters.py updated. renderer.py uses simulation layer Ship objects (out of scope).

---

### Task 4.6: Update test fixtures [Medium]
**File:** `tests/unit/strategy/conftest.py`
**Tests:** `pytest tests/unit/strategy/ -v`

**Fixtures to update:**
- `ship_stats_with_custom_resources` (lines 106-124)
- `ship_with_per_turn_component` (lines ~153-159)
- `ship_with_warp_drive` (lines ~186-192)

- [x] Remove legacy fields from `ship_stats_with_custom_resources`
- [x] Update `ship_with_per_turn_component` expected_stats
- [x] Update `ship_with_warp_drive` expected_stats
- [x] Update any other fixtures with legacy fields
- [x] Verify: Fixtures work with new format

**Notes:** All fixtures in conftest.py updated. Also updated fixtures in test_ship_stats_service.py, test_ship_detail_panel.py, test_fleet_report_filters.py to use new format.

---

### Task 4.7: Remove legacy attribute tests [Simple]
**Files:** Test files
**Tests:** Run full suite after removal

- [x] `tests/unit/strategy/test_ship_instance_proj08.py`: Remove `TestBackwardCompatibility` class (lines ~1203-1290)
- [x] `tests/unit/entities/test_ship_stats.py`: Remove `test_ability_values_match_legacy_attributes()` if exists
- [x] Remove any other tests that specifically test legacy field backward compatibility
- [x] Verify: No test references legacy fields

**Notes:** Renamed TestBackwardCompatibility to TestResourceConvenienceMethods. Legacy field tests converted to test new dict format.

---

### Task 4.8: Final audit [Simple]
**Tests:** Full test suite

- [x] Run: `grep -rn "max_fuel\|max_energy\|max_ammo" game/strategy/`
- [x] Run: `grep -rn "strategic_fuel_per_hex" game/strategy/`
- [x] Run: `grep -rn "warp_energy_cost\|warp_fuel_cost" game/strategy/`
- [x] Fix any remaining occurrences
- [x] Verify: No legacy field references in strategy layer

**Notes:** Remaining references are:
1. Comments/docstrings (documentation)
2. Local variable names extracting values from new dict format (e.g., `max_fuel = resource_storage.get('fuel', 0)`)
3. Method names on ShipInstance/Fleet (`get_warp_energy_cost()`) which internally use new format
All 1097 tests pass. Removed outdated comment about "Legacy fields for backward compatibility".

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -v` passes (full suite) - 1097 tests pass
- [x] No legacy field names in ship_stats_service.py return dict
- [x] `grep -rn "max_fuel\|max_energy\|max_ammo" game/strategy/` returns only comments/variable names
- [x] Application launches and runs correctly
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "All phases complete"
