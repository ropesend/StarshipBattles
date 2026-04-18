# Phase 4: FoodAllocationEditor UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Per-colony per-species food-allocation slider UI. Label text comes from the configured food resource (auto-relabels if mod swaps the food). Mirror the `atmosphere_target_editor.py` pattern.

---

## Tasks

### Task 4.1: `FoodAllocationEditor` screen [Complex]
**File:** `game/ui/screens/food_allocation_editor.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_food_allocation_editor.py`

- [ ] Model after `atmosphere_target_editor.py` structure: `pygame_gui.elements.UIWindow` with scrollable rows.
- [ ] Window title: `f"{resource_display_name} Allocation — {planet.name}"` where `resource_display_name = ResourceCatalog.get(economy_config.population_food_resource).name`.
- [ ] One row per species present on `planet.populations`:
  - Species race name (via `RaceLibrary.get_race(race_id).name`)
  - Slider 0.0 to 5.0, step 0.05
  - Typed numeric input to override (supports values > 5.0)
  - Live label showing current value + total consumption preview (`pop * allocation * food_per_pop`)
- [ ] Apply button writes `colony.get_species_config(race_id).food_allocation` for each row.
- [ ] Cancel / close button.
- [ ] Emit an event via facade for the command-handler pattern (or direct mutation — follow the local pattern in `atmosphere_target_editor`).

### Task 4.2: Hook editor into planet detail panel [Medium]
**File:** `game/ui/screens/planet_abilities_window.py` (OR wherever planet editors are listed)
**Tests:** Manual smoke + `pytest tests/unit/ui/screens/test_planet_abilities_window.py`

- [ ] Add a button "Food Allocation" to the planet detail panel's environment-editor buttons list.
- [ ] Button opens the new `FoodAllocationEditor` via `strategy_window_manager.py` delegation (copy `_open_atmosphere_editor` style).
- [ ] Show button only when the planet is a colony (has at least one species).

### Task 4.3: `FoodAllocationEditor` tests [Medium]
**File:** `tests/unit/ui/screens/test_food_allocation_editor.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_food_allocation_editor.py`

- [ ] Editor constructs for a planet with one species.
- [ ] Editor constructs for a planet with multiple species; renders one row per species.
- [ ] Slider change -> `food_allocation` writes on Apply.
- [ ] Typed input accepts values > 5.0.
- [ ] Title text updates when `economy_config.population_food_resource` is swapped to "metals" via `set_default_economy_config` (label reads "Metals Allocation — <planet>").
- [ ] Cancel does not write.

### Task 4.4: Docs & UX polish [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Add a short UX note under the demographics section: "Per-colony per-species food allocation slider. Default 1.0. Range 0-∞ (UI slider capped at 5.0 with typed override)."

### Task 4.5: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite green.

### Task 4.6: Manual smoke test [Simple]
**Tests:** Manual

- [ ] Launch game, open a colony, click "Food Allocation" button.
- [ ] Slider default at 1.0.
- [ ] Drop to 0.5 -> apply -> close -> next turn: consumption halves, happiness drops.
- [ ] Raise to 2.0 -> apply -> next turn: consumption doubles, happiness rises.
- [ ] Multi-species colony: independent sliders for each species.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
