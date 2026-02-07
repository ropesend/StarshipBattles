# Phase 4: Environment Tab Enhancement [Simple]

**Objective:** Add water sliders and homeworld dropdown to the existing Environment tab
**Tests:** `pytest tests/unit/ui/panels/test_race_environment_panel.py -v`

---

## Task 4.1: Add Homeworld Type Dropdown [Simple]
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_environment_panel.py -v -k "homeworld"`

- [ ] Import `get_available_homeworld_names` from `game.strategy.data.homeworld_presets`
- [ ] Add homeworld type dropdown at top of panel (before gravity section)
  - Label: "Homeworld Type:"
  - Dropdown with all PlanetType names + "(Custom)" option
  - Initial value from `race_config.homeworld_type` or "(Custom)"
- [ ] Store reference: `self.homeworld_dropdown`
- [ ] Write test: `test_panel_has_homeworld_dropdown`
- [ ] Write test: `test_homeworld_dropdown_has_all_planet_types`
- [ ] Run tests: all pass
**Notes:** The homeworld dropdown sets initial slider values but doesn't lock them.

---

## Task 4.2: Add Water Sliders [Simple]
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_environment_panel.py -v -k "water"`

- [ ] Add water section after radiation section (before atmosphere)
- [ ] Create section header: "Water Preferences:"
- [ ] Add water ideal slider: range 0.0-1.0, increment 0.05, label shows percentage
  - Store as `self.water_ideal_slider` and `self.water_ideal_label`
- [ ] Add water tolerance slider: range 0.0-1.0, increment 0.05, label shows "±X%"
  - Store as `self.water_tolerance_slider` and `self.water_tolerance_label`
- [ ] Add `_format_water(value)` method: returns `f"{value*100:.0f}%"`
- [ ] Update `update_config()` to include water sliders
- [ ] Update `update_labels()` to include water labels
- [ ] Update `set_from_config()` to include water sliders
- [ ] Write test: `test_panel_has_water_ideal_slider`
- [ ] Write test: `test_panel_has_water_tolerance_slider`
- [ ] Write test: `test_update_config_reads_water_sliders`
- [ ] Write test: `test_update_labels_formats_water_values`
- [ ] Write test: `test_set_from_config_sets_water_sliders`
- [ ] Run tests: all pass
**Notes:**

---

## Task 4.3: Implement Homeworld Preset Auto-Populate [Medium]
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_environment_panel.py -v -k "preset"`

- [ ] Import `get_preset_for_planet_type` from `game.strategy.data.homeworld_presets`
- [ ] Create `apply_homeworld_preset(planet_type_name: str)` method:
  - Load preset for given planet type
  - Set all slider values from preset (gravity, temp, water, radiation, atmosphere)
  - Update race_config.homeworld_type
  - Update all labels
- [ ] Handle "(Custom)" selection: do nothing (leave sliders as-is)
- [ ] The method should be callable from parent screen's event handler when dropdown changes
- [ ] Write test: `test_apply_homeworld_preset_continental_sets_gravity`
- [ ] Write test: `test_apply_homeworld_preset_continental_sets_temperature`
- [ ] Write test: `test_apply_homeworld_preset_jovian_sets_high_gravity`
- [ ] Write test: `test_apply_homeworld_preset_custom_does_nothing`
- [ ] Write test: `test_apply_homeworld_preset_updates_config`
- [ ] Run tests: all pass
**Notes:** Sliders remain adjustable after preset — user can customize from the preset starting point.

---

## Phase 4 Completion Checklist
- [ ] All tasks above checked off
- [ ] Run `pytest tests/unit/ui/panels/test_race_environment_panel.py -v` — all pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] Water sliders display and update correctly
- [ ] Homeworld dropdown populates all sliders from preset
