# Phase 1: Deep Analysis of Ship Class (READ-ONLY)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-260 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Catalog every method, property, and attribute in Ship.py. Identify exact extraction targets for ShipLayerManager and ShipResourceManager. Determine if additional extractions are needed to hit the <500 line target. This phase produces NO code changes.

---

## Tasks

### Task 1.1: Catalog Ship.__init__ Attribute Groups [Simple]
**File:** `game/simulation/entities/ship.py` (lines 50-186)
**Tests:** N/A (read-only)

- [ ] List every attribute initialized in `__init__`, grouped by concern:
  - Identity (id, name, color, team_id, ship_class, theme_id)
  - Registries (_registries)
  - Layers & Hull (layers dict, via _initialize_layers / _equip_default_hull)
  - Stats (mass, hp, base_mass, vehicle_type, thrust, speed, turn, etc.)
  - Budget & Validation (max_mass_budget, mass_limits_ok, layer_status, etc.)
  - Dirty Flags (_stats_dirty)
  - Resources (resources, _resources_initialized, _prev_max_resources, _prev_max_shields)
  - Combat Stats (emissive_armor, shields, defense scores, etc.)
  - Strategic Stats (strategic_movement, warp, cargo, pod)
  - Resource Consumption (fuel/ammo/energy consumption and potential)
  - Crew Stats (crew_onboard, crew_required)
  - Combat State (is_alive, is_derelict, bridge_destroyed, retreat_status)
  - AI & Targeting (ai_strategy, current_target, secondary_targets, max_targets)
  - Formation & Physics (formation, throttles, speed, acceleration, is_thrusting)
  - Delegates (_component_manager, _combat_manager, stats_calculator, etc.)
- [ ] For each attribute, note which delegate or system writes it and reads it
- [ ] Identify attributes that can move to the new delegates vs. must stay on Ship

**Notes:** Record findings in `findings/phase_1_attribute_catalog.md`

---

### Task 1.2: Catalog All Methods and Properties on Ship [Medium]
**File:** `game/simulation/entities/ship.py` (entire file)
**Tests:** N/A (read-only)

- [ ] List every method on Ship with its line range, noting:
  - Is it a facade (delegates to another class)?
  - Is it implementation logic (should be extracted)?
  - Is it a property accessor?
- [ ] Current facade methods to verify:
  - `component_manager` property (line 248) -- facade to ShipComponentManager
  - `combat_manager` property (line 262) -- facade to ShipCombatManager
  - `combat_engine` property (line 274) -- facade to ShipCombatEngine
  - `set_event_bus()` (line 281) -- facade
  - `just_fired_projectiles` property (line 289) -- facade
  - `comp_trigger_pulled` property (line 298) -- facade
  - `aim_point` property (line 307) -- facade
  - `total_shots_fired` property (line 316) -- facade
  - `die()` (line 324) -- facade
  - `update()` (line 356) -- facade
  - `update_derelict_status()` (line 360) -- facade
  - `add_component()` (line 501) -- facade
  - `add_components_bulk()` (line 510) -- facade
  - `remove_component()` (line 517) -- facade
  - `get_all_components()` (line 621) -- facade
  - `iter_components()` (line 628) -- facade
  - `get_components_by_ability()` (line 632) -- facade
  - `get_weapon_components_cached()` (line 640) -- facade
  - `get_components_by_layer()` (line 647) -- facade
  - `has_components()` (line 651) -- facade
  - `find_component_with_index()` (line 655) -- facade
  - `clear_non_hull_components()` (line 662) -- facade
  - `check_validity()` (line 666) -- facade
  - `get_missing_requirements()` (line 565) -- facade
  - `get_validation_warnings()` (line 569) -- facade
  - `get_ability_total()` (line 573) -- facade
  - `get_total_ability_value()` (line 577) -- facade
  - `get_total_sensor_score()` (line 591) -- facade
  - `get_total_ecm_score()` (line 613) -- facade
  - `max_weapon_range` property (line 352) -- facade
  - `to_dict()` (line 673) -- facade
  - `from_dict()` (line 685) -- facade
- [ ] Implementation methods that are extraction candidates:
  - `_initialize_layers()` (line 364) -- LAYER concern
  - `_equip_default_hull()` (line 189) -- LAYER concern
  - `change_class()` (line 424) -- LAYER + COMPONENT concern
  - `get_resource_stat()` (line 595) -- RESOURCE concern
  - `recalculate_stats()` (line 538) -- ORCHESTRATION concern
  - `mark_stats_dirty()` (line 521) -- DIRTY FLAG concern
  - `recalculate_stats_if_dirty()` (line 528) -- DIRTY FLAG concern
  - `_invalidate_components_cache()` (line 332) -- CACHE concern
- [ ] Properties that are simple accessors:
  - `registries` (line 208)
  - `mass` / `mass.setter` (lines 214-221)
  - `max_hp` / `max_hp.setter` (lines 223-230)
  - `hp` / `hp.setter` (lines 232-240)
  - `stat_querier` (line 338)
  - `validator_helper` (line 344)
  - `cached_summary` (line 506)

**Notes:** Record findings in `findings/phase_1_method_catalog.md`

---

### Task 1.3: Trace External Callers of Extraction Targets [Medium]
**Tests:** N/A (read-only)

- [ ] Search codebase for all callers of `ship._initialize_layers()` (expect: Ship.__init__, change_class only)
- [ ] Search codebase for all callers of `ship._equip_default_hull()` (expect: Ship.__init__, change_class only)
- [ ] Search codebase for all callers of `ship.resources` (expect: many -- ShipCombatManager, ShipStatsCalculator, UI, combat systems)
- [ ] Search codebase for all callers of `ship.get_resource_stat()` (expect: UI panels, endurance display)
- [ ] Search codebase for all callers of `ship._resources_initialized` (expect: ShipStatsCalculator._initialize_resources only)
- [ ] Search codebase for all callers of `ship._prev_max_resources` (expect: ShipStatsCalculator._initialize_resources only)
- [ ] Search codebase for all callers of `ship._prev_max_shields` (expect: ShipStatsCalculator._initialize_resources only)
- [ ] Search codebase for all callers of `ship.fuel_consumption` / `ammo_consumption` / `energy_consumption` (expect: UI, endurance calc)
- [ ] Search codebase for all callers of `ship.change_class()` (expect: UI builder, serialization)
- [ ] Document which callers need facade properties vs. which are internal only
- [ ] Verify that `ship.layers` is accessed directly by too many callers to move (confirm decision)

**Notes:** Record findings in `findings/phase_1_caller_trace.md`

---

### Task 1.4: Determine Full Extraction Plan for <500 Lines [Medium]
**Tests:** N/A (read-only)

- [ ] Calculate current line counts by concern area (from Task 1.1 and 1.2)
- [ ] Calculate expected line reduction from ShipLayerManager extraction
- [ ] Calculate expected line reduction from ShipResourceManager extraction
- [ ] If still above 500 lines, identify additional extraction candidates:
  - Can `change_class()` (68 lines) move entirely to ShipLayerManager?
  - Can `recalculate_stats()` orchestration (25 lines) be simplified?
  - Can the `_invalidate_components_cache()` + dirty flag logic move?
  - Can more combat state attributes move to ShipCombatManager init?
  - Can resource consumption attributes (8 lines) move to ShipResourceManager?
- [ ] Write the definitive extraction plan:
  - **ShipLayerManager methods:** (exact list with current line numbers)
  - **ShipResourceManager methods:** (exact list with current line numbers)
  - **Additional extractions if needed:** (exact list)
  - **Expected final Ship line count:** (calculated)
- [ ] Verify the plan does not break any existing delegate's interface

**Notes:** Record findings in `findings/phase_1_extraction_plan.md`. Update design.md if the plan differs from initial analysis.

---

### Task 1.5: Review Existing Tests for Coverage Gaps [Simple]
**Tests:** N/A (read-only)

- [ ] Read `tests/unit/entities/test_ship.py` -- note what's tested
- [ ] Read `tests/unit/simulation/entities/test_ship_resource_stat.py` -- note coverage of `get_resource_stat()`
- [ ] Read `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` -- note coverage of `_initialize_resources()`
- [ ] Read `tests/unit/simulation/entities/test_ship_component_manager.py` -- note pattern for delegate tests
- [ ] Read `tests/unit/simulation/entities/test_ship_combat_manager.py` -- note pattern for delegate tests
- [ ] Identify which behaviors currently tested on Ship will need equivalent tests on the new delegates
- [ ] List test gaps (behaviors NOT currently tested that should be tested during extraction)

**Notes:** Record findings in `findings/phase_1_test_gaps.md`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `findings/` directory populated with 5 analysis documents
- [ ] Definitive extraction plan written (Task 1.4)
- [ ] design.md updated if extraction plan differs from initial analysis
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
