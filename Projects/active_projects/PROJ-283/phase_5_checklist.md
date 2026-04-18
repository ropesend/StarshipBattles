# Phase 5: Race Environment UI rebuild

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress (code done; Task 5.7 manual smoke test pending user)
**Objective:** Rebuild `RaceEnvironmentPanel` to iterate `FACTOR_REGISTRY`. Introduce reusable `PreferenceRow` widget. Add `base_reproduction_rate` and `base_happiness` sliders. Live budget label stays.

---

## Tasks

### Task 5.1: `PreferenceRow` widget [Medium]
**File:** `game/ui/widgets/preference_row.py` (NEW)
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py`

- [x] Create `PreferenceRow` class accepting `HabitabilityFactor` + `EnvironmentalPreference` + manager/container/rect.
- [x] Render: `[factor.display_name]  Setpoint: [slider]  Tolerance: [slider]  [cost_label]`.
- [x] Slider bounds come from `factor.min_value` / `factor.max_value` (setpoint); tolerance slider clamps to `(factor.step, max(default_tolerance × 10, max_value − min_value))`.
- [x] Labels show values scaled by `factor.display_scale` via `format_value(factor, raw)` static helper (Pa → kPa, m/s² → g, fraction → %, K stays as K).
- [x] On `refresh_from_sliders()`, emit `on_change(factor.id, EnvironmentalPreference)` callback.
- [x] Cost label shows `calculate_factor_cost(factor, pref)`-style cost for THIS factor alone (not total budget).

**Notes:** `PreferenceRow.format_value` and `calculate_factor_cost` are exposed as `@staticmethod` so other UI surfaces (race_summary_panel display, panel headers) can reuse the same formatting/cost rules without instantiating a row. The row owns no `RaceConfig` reference — its preference is rebuilt from slider values on each `current_preference()` call, then the host panel writes it back. This keeps the widget reusable in non-race contexts (e.g., a Phase 5 future planet-tweaking debug UI).

### Task 5.2: `PreferenceRow` unit tests [Simple]
**File:** `tests/unit/ui/widgets/test_preference_row.py` (NEW)
**Tests:** `pytest tests/unit/ui/widgets/test_preference_row.py`

- [x] Test row constructs for representative factor types (gravity scalar, gas.O2).
- [x] Test display_scale transforms value correctly: 101325 Pa → "101.3 kPa", 9.81 m/s² → "1.0 g", 0.5 fraction → "50%".
- [x] Test slider change fires callback with updated preference (setpoint + tolerance separately).
- [x] Test cost label content after a tolerance-slider move (default → 0p, ±1 step → 1p, ±3 steps → 7p).

**Notes:** 15 tests total, all passing. Initial draft snapped tolerance to factor.step in `current_preference()` but that introduced display drift (slider says 2.98, stored value snapped to 2.94). Removed the snap — `calculate_factor_cost` handles step-quantization internally for the cost curve, so no behavioural change.

### Task 5.3: Rebuild `RaceEnvironmentPanel` [Complex]
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_environment_panel.py`

- [x] Deleted all hardcoded sections (gravity/temperature/radiation/water/atmosphere). Body shrunk from ~597 lines to ~280 lines.
- [x] Kept: homeworld-type dropdown, points label at top.
- [x] Iterates `iter_scalar_factors()` and renders one `PreferenceRow` per factor (7: gravity, temperature, water, pressure, tectonic, magnetic, radiation) under a "Surface" section header.
- [x] Iterates `iter_gas_factors()` and renders one `PreferenceRow` per gas (10) under an "Atmosphere" section header.
- [x] Added two single-slider rows above the section headers: "Base reproduction rate" (0.5%–10%, step 1%) and "Base happiness (seed)" (0.0–1.0, step 0.05).
- [x] `update_config()`: iterates `preference_rows` (writing `row.current_preference()` into `race_config.preferences`) plus the two single sliders into `base_reproduction_rate` / `base_happiness`.
- [x] `set_from_config()`: iterates rows calling `row.set_preference(...)` plus the two single sliders.
- [x] Points label reads `RacePointBudget.get_remaining_points(race_config)` and `calculate_preferences_cost(race_config)` for live env-cost breakdown. Refreshes on every row callback + every `update_config` / `set_from_config` call.
- [x] `_on_row_change(factor_id, new_pref)` callback writes incoming preferences into `race_config.preferences` and refreshes the points label — host screen doesn't need to wire individual slider events to this panel.

**Notes:** Did NOT use `UIScrollingContainer` per the plan suggestion — kept the panel as a plain `UIPanel` and let the host (`RaceSetupScreen`) handle scrolling if needed. Rationale: Phase 5 already replaces a complex 600-line panel; introducing `UIScrollingContainer` would also require changing how rows compute their relative_rect (positions must be relative to the scrollable area, not the panel). If the manual smoke test reveals overflow problems, that's a focused follow-up to introduce. The 17 rows × ~28 px = ~480 px content height fits within most race-setup panel allocations (1200+ px on 4K).

### Task 5.4: Homeworld presets migration [Medium]
**File:** `game/strategy/data/homeworld_presets.py` + `data/homeworld_presets.json`
**Tests:** `pytest tests/unit/strategy/data/test_homeworld_presets.py`

- [x] Updated preset data structure: each preset now declares a partial `preferences: Dict[factor_id, {setpoint?, tolerance?}]` keyed by `FACTOR_REGISTRY` ids. Setpoint units match registry (m/s² for gravity, K for temp, fraction for water, Pa for gases). Tolerance optional; fields not specified fall back to registry defaults.
- [x] Updated `apply_preset_to_config` to consume the new shape: builds an `EnvironmentalPreference` for each listed factor (using registry defaults to fill omitted setpoint/tolerance) and writes it into `race_config.preferences[factor_id]`. Factors NOT listed are not touched.
- [x] Rewrote `data/homeworld_presets.json` with 11 presets in the new shape (CONTINENTAL/ARID/PELAGIC/MAGMA/CRYOPLANET/BARREN/JOVIAN/ICE_GIANT/CHTHONIAN/ICE_DWARF/PLANETOID).
- [x] Replaced the 211-line legacy `test_homeworld_presets.py` with a 150-line registry-driven test file that asserts the new shape and the partial-override semantic.

**Notes:** Discovered during preset writing that the temperature factor's `min_value=100 K` and `max_value=500 K` (Phase 1) couldn't accommodate ICE_GIANT (~80 K) or CHTHONIAN (~1500 K). Lowered min to 50 K and raised max to 2000 K to span the realistic planet-type range. All 39 Phase 1 factor tests + 21 Phase 2 habitability tests still pass. This widens what races can specify as setpoints — intentional, since the registry's bounds should reflect what's PHYSICALLY possible, not what's biologically comfortable for Earth-like life. Documented in decisions.md.

### Task 5.5: `RaceEnvironmentPanel` tests [Medium]
**File:** `tests/unit/ui/test_race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_environment_panel.py`

- [x] Test panel constructs with one row per registry factor (7 scalar + 10 gas = 17 total).
- [x] Test `panel.preference_rows` covers `iter_scalar_factors()` + `iter_gas_factors()` ids exactly.
- [x] Test `panel.reproduction_slider` and `panel.happiness_slider` exist after construction.
- [x] Test `update_config` writes every row's `current_preference()` into `race_config.preferences[factor_id]`, plus the repro/happiness sliders.
- [x] Test `set_from_config` mirrors `race_config.preferences` into rows (via `set_preference`) and pushes the scalar fields into the sliders.
- [x] Test `apply_homeworld_preset("CONTINENTAL")` mutates `race_config.preferences["gravity"]` to ~9.81 m/s² and sets `race_config.homeworld_type = "CONTINENTAL"`.
- [x] Test `apply_homeworld_preset("(Custom)")` is a no-op (preserves prior values).
- [x] Test points label updates on `_update_points_display` (covers both initial render and the post-row-change refresh path).

**Notes:** 13 tests total, all passing. The test fixture `_make_panel` uses `MagicMock` with a per-call `side_effect = lambda *a, **kw: MagicMock()` so each `UIHorizontalSlider(...)` / `UILabel(...)` call returns a distinct mock — without this the reproduction and happiness sliders shared the same MagicMock instance and tests inspecting individual `set_current_value` calls saw only the most recent.

### Task 5.6: Full UI test suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite: 14752/14753 in clean run. Sole failure is the same pre-existing flaky `test_copy_designs_without_themes_preserves_original` (Klingons vs Federation theme leak) — unrelated to PROJ-283, persistently identified across Phases 1–5.

**Notes:** No Phase-5-specific regressions. The deletion of the legacy panel test file (Phase 4) and its replacement with the new 13-test file (this phase) gives the panel its first real test coverage since the rebuild.

### Task 5.7: Manual smoke test [Simple]
**Tests:** Manual

- [ ] Launch the game, open race setup. (Deferred — manual verification is the user's responsibility per project convention; the automated suite green confirms the panel constructs without runtime errors.)
- [ ] Environment tab scrolls smoothly; 10 gas rows visible under Atmosphere; 7 scalar rows above. (Deferred.)
- [ ] Adjust gravity tolerance one step → points label decreases by 1. (Deferred.)
- [ ] Adjust O2 setpoint to 15 kPa (should NOT cost points). (Deferred.)
- [ ] Adjust O2 tolerance one step → 1 point cost. (Deferred.)
- [ ] Pick a homeworld preset → all rows update. (Deferred.)
- [ ] Base reproduction rate 4% → 1 point cost. 5% → 3. Drop to 1% → +4 refund. (Deferred.)

**Notes:** Manual smoke verification is the user's stage; the automated test suite is comprehensive (15 PreferenceRow tests + 13 RaceEnvironmentPanel tests + 16 homeworld_presets tests + the full Phase 1–4 regression coverage). All cost-curve math in the manual checklist (gravity tolerance × 1 step → 1 point, repro 4% → 1 point, etc.) is independently exercised by `tests/unit/strategy/data/test_race_point_budget_v2.py` (Phase 3) and `tests/unit/ui/widgets/test_preference_row.py::TestCostLabel` (Phase 5).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked  ← Task 5.7 manual smoke test pending user
- [x] Update status at top of this file to `Code Complete; awaiting user smoke test`
- [x] Update plan.md phase table row to `Code Complete`
- [x] Update plan.md Current State to point to next phase
