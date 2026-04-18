# Phase 5: Race Environment UI rebuild

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rebuild `RaceEnvironmentPanel` to iterate `FACTOR_REGISTRY`. Introduce reusable `PreferenceRow` widget. Add `base_reproduction_rate` and `base_happiness` sliders. Live budget label stays.

---

## Tasks

### Task 5.1: `PreferenceRow` widget [Medium]
**File:** `game/ui/widgets/preference_row.py` (NEW)
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py`

- [ ] Create `PreferenceRow` class accepting `HabitabilityFactor` + `EnvironmentalPreference` + manager/container/rect.
- [ ] Render: `[factor.display_name]  Setpoint: [slider]  Tolerance: [slider]  [cost_label]`.
- [ ] Slider bounds come from `factor.min_value` / `factor.max_value`; step from `factor.step`.
- [ ] Labels show values scaled by `factor.display_scale` (Pa -> kPa for pressures).
- [ ] On slider change, emit a callback with the factor id + updated `EnvironmentalPreference`.
- [ ] Cost label shows `calculate_preferences_cost`-style cost for THIS factor alone (not total).

### Task 5.2: `PreferenceRow` unit tests [Simple]
**File:** `tests/unit/ui/widgets/test_preference_row.py` (NEW)
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py`

- [ ] Test row constructs for each representative factor type (scalar, gas).
- [ ] Test display_scale transforms value correctly in the label (101325 Pa shows as "101.3 kPa").
- [ ] Test slider change fires callback with updated preference.
- [ ] Test cost label updates when tolerance slider moves.

### Task 5.3: Rebuild `RaceEnvironmentPanel` [Complex]
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_environment_panel.py`

- [ ] Delete all hardcoded sections (gravity/temperature/radiation/water/atmosphere).
- [ ] Keep: homeworld-type dropdown, points label at top.
- [ ] Iterate `iter_scalar_factors()` and render one `PreferenceRow` per factor (gravity, temperature, water, pressure, tectonic, magnetic, radiation).
- [ ] Iterate `iter_gas_factors()` inside a collapsible, scrollable `UIPanel` labeled "Atmosphere" — one `PreferenceRow` per gas.
- [ ] Add two new single-slider rows at the top or bottom: "Base reproduction rate (0.5% - 10%)" and "Base happiness (0.0 - 3.0)".
- [ ] `update_config()`: iterate rows and write into `race_config.preferences`, `race_config.base_reproduction_rate`, `race_config.base_happiness`.
- [ ] `set_from_config()`: iterate rows and read from `race_config`.
- [ ] Points label reads `RacePointBudget.get_remaining_points(race_config)`.
- [ ] Layout: use `UIScrollingContainer` so the tall content (10 gases x 2 sliders plus 7 scalars) scrolls.

### Task 5.4: Homeworld presets migration [Medium]
**File:** `game/strategy/data/homeworld_presets.py`
**Tests:** `pytest tests/unit/strategy/data/test_homeworld_presets.py`

- [ ] Update preset data structure: each preset now emits a `preferences: Dict[str, EnvironmentalPreference]` + `base_reproduction_rate`.
- [ ] Update preset application logic in `RaceEnvironmentPanel.apply_homeworld_preset()` to call `race_config.preferences.update(preset_prefs)`.
- [ ] Rewrite the JSON/data shape if presets are stored externally.
- [ ] Update any existing preset tests.

### Task 5.5: `RaceEnvironmentPanel` tests [Medium]
**File:** `tests/unit/ui/test_race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_environment_panel.py`

- [ ] Test panel constructs for every registered factor.
- [ ] Test every factor has a visible row with setpoint + tolerance sliders (gas rows under Atmosphere group).
- [ ] Test editing a slider mutates `race_config.preferences` as expected.
- [ ] Test points label updates live.
- [ ] Test `base_reproduction_rate` and `base_happiness` slider edits flow to `race_config`.
- [ ] Test applying a homeworld preset overwrites the right prefs.

### Task 5.6: Full UI test suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite green.

### Task 5.7: Manual smoke test [Simple]
**Tests:** Manual

- [ ] Launch the game, open race setup.
- [ ] Environment tab scrolls smoothly; 10 gas rows visible under Atmosphere; 7 scalar rows above.
- [ ] Adjust gravity tolerance one step -> points label decreases by 1.
- [ ] Adjust O2 setpoint to 15 kPa (should NOT cost points).
- [ ] Adjust O2 tolerance one step -> 1 point cost.
- [ ] Pick a homeworld preset -> all rows update.
- [ ] Base reproduction rate 4% -> 1 point cost. 5% -> 3. Drop to 1% -> +4 refund.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
