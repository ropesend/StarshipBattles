# Phase 1: CAT-9 Simplification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-323 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Simplify the 32 verified CAT-9 cases identified by review `2026-05-02_204633_test-review` (smallest deltas first — repeated imports, micro-duplications).

---

## Tasks

### Task 1.1: test_json_utils.py [Simple]
**File:** `tests/unit/core/test_json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils.py`

- [ ] [S10-CAT9-003] `TestLoadJsonRequired success path` (lines 277-307): Remove the success-path duplicate; keep error-path tests in TestLoadJsonRequired.

- [ ] Verify: `pytest tests/unit/core/test_json_utils.py` passes; LOC delta ≈ 15

**Notes:** _(none yet)_

---

### Task 1.2: test_protocols.py [Simple]
**File:** `tests/unit/core/test_protocols.py`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [ ] [S09-CAT9-002] `Repeated local imports` (lines 14-220): Move imports to module top-level.

- [ ] Verify: `pytest tests/unit/core/test_protocols.py` passes; LOC delta ≈ 40

**Notes:** _(none yet)_

---

### Task 1.3: test_projectile_weapon_bindings.py [Simple]
**File:** `tests/unit/modifiers/test_projectile_weapon_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_projectile_weapon_bindings.py`

- [ ] [S10-CAT9-001] `Repeated imports` (lines 16-34): Hoist imports; consider merging tests.

- [ ] Verify: `pytest tests/unit/modifiers/test_projectile_weapon_bindings.py` passes; LOC delta ≈ 19

**Notes:** _(none yet)_

---

### Task 1.4: test_callbacks.py [Simple]
**File:** `tests/unit/research/research_scene/test_callbacks.py`
**Tests:** `pytest tests/unit/research/research_scene/test_callbacks.py`

- [ ] [S03-CAT9-004] `Identical mock setup repeated` (lines 17-323): Extract a shared fixture.

- [ ] Verify: `pytest tests/unit/research/research_scene/test_callbacks.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 1.5: test_cycle_detection.py [Simple]
**File:** `tests/unit/research/research_scene/test_cycle_detection.py`
**Tests:** `pytest tests/unit/research/research_scene/test_cycle_detection.py`

- [ ] [S03-CAT9-006] `Repeated cycle-node structure` (lines 109-182): Extract helper for cycle setup.

- [ ] Verify: `pytest tests/unit/research/research_scene/test_cycle_detection.py` passes; LOC delta ≈ 74

**Notes:** _(none yet)_

---

### Task 1.6: test_initialization.py [Simple]
**File:** `tests/unit/research/research_scene/test_initialization.py`
**Tests:** `pytest tests/unit/research/research_scene/test_initialization.py`

- [ ] [S03-CAT9-005] `Identical mock setup across 7 tests` (lines 13-262): Extract a shared fixture.

- [ ] Verify: `pytest tests/unit/research/research_scene/test_initialization.py` passes; LOC delta ≈ 60

**Notes:** _(none yet)_

---

### Task 1.7: test_fleet_aura_manager_modifier_stack.py [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] [S10-CAT9-002] `4 similar helper functions` (lines 34-53, 173-189, 288-302): Consolidate into one parametrized factory; ~15 LOC savings.

- [ ] Verify: `pytest tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py` passes; LOC delta ≈ 30

**Notes:** _(none yet)_

---

### Task 1.8: test_projectile_manager.py [Simple]
**File:** `tests/unit/simulation/projectile/test_projectile_manager.py`
**Tests:** `pytest tests/unit/simulation/projectile/test_projectile_manager.py`

> **PRE-CONDITION:** The original verification flagged this finding's line ranges as fictitious. **BEFORE starting**, run `grep -n "proj.position = Vector2" tests/unit/simulation/projectile/test_projectile_manager.py` and update the task with the actual line numbers. Estimated 27 occurrences exist somewhere in the file.

- [ ] [S09-CAT9-004] `Repeated MagicMock projectile boilerplate` (lines throughout (27 occurrences)): Extract a _make_projectile(position, velocity, ...) helper; verify accurate line ranges before refactor.
      _(verification adjusted from review's "Extract _make_projectile helper across cited lines 1831-1840 and 1997-2007." — see verification_report.md)_

- [ ] Verify: `pytest tests/unit/simulation/projectile/test_projectile_manager.py` passes; LOC delta ≈ 200

**Notes:** _(none yet)_

---

### Task 1.9: test_battle_engine_end_conditions.py [Simple]
**File:** `tests/unit/simulation/systems/test_battle_engine_end_conditions.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_end_conditions.py`

- [ ] [S08-CAT9-002] `Near-identical mock_ship/mock_ship_team1` (lines 21-60): Parametrize fixture.

- [ ] Verify: `pytest tests/unit/simulation/systems/test_battle_engine_end_conditions.py` passes; LOC delta ≈ 40

**Notes:** _(none yet)_

---

### Task 1.10: test_fleet_cargo_resources.py [Simple]
**File:** `tests/unit/strategy/data/test_fleet_cargo_resources.py`
**Tests:** `pytest tests/unit/strategy/data/test_fleet_cargo_resources.py`

- [ ] [S06-CAT9-002] `_make_ship duplicates _make_cargo_ship` (lines 14-45): Extract to shared fixture.

- [ ] Verify: `pytest tests/unit/strategy/data/test_fleet_cargo_resources.py` passes; LOC delta ≈ 32

**Notes:** _(none yet)_

---

### Task 1.11: test_empire_economy_calculator.py [Simple]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [ ] [S04-CAT9-003] `_mock_race_registry duplicated` (lines 826-835, 1064-1068): Promote to module-level fixture.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py` passes; LOC delta ≈ 15

**Notes:** _(none yet)_

---

### Task 1.12: test_harvesting_engine.py [Simple]
**File:** `tests/unit/strategy/engine/test_harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_harvesting_engine.py`

- [ ] [S04-CAT9-002] `_make_engine duplicated in 3 classes` (lines 148-150, 517-519, 694-696): Promote to module-level fixture.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_harvesting_engine.py` passes; LOC delta ≈ 9

**Notes:** _(none yet)_

---

### Task 1.13: test_organics_consumption_engine.py [Simple]
**File:** `tests/unit/strategy/engine/test_organics_consumption_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [ ] [S08-CAT9-003] `_colony helper` (lines 42-67): Promote to class-scoped fixture.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py` passes; LOC delta ≈ 26

**Notes:** _(none yet)_

---

### Task 1.14: test_planetary_yard_requirement.py [Simple]
**File:** `tests/unit/strategy/engine/test_planetary_yard_requirement.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planetary_yard_requirement.py`

- [ ] [S11-CAT9-001] `_make_yard_facility duplicates helper` (lines 15-25): Move to shared fixture.

- [ ] Verify: `pytest tests/unit/strategy/engine/test_planetary_yard_requirement.py` passes; LOC delta ≈ 11

**Notes:** _(none yet)_

---

### Task 1.15: test_service_edge_cases.py [Simple]
**File:** `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py`

- [ ] [S10-CAT9-004] `Repeated mock fleet boilerplate` (lines 392-510): Extract _make_mock_fleet helper.

- [ ] Verify: `pytest tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` passes; LOC delta ≈ 35

**Notes:** _(none yet)_

---

### Task 1.16: test_system_archetype.py [Simple]
**File:** `tests/unit/strategy/services/ability_sources/test_system_archetype.py`
**Tests:** `pytest tests/unit/strategy/services/ability_sources/test_system_archetype.py`

- [ ] [S02-CAT9-002] `Repeated _MockSystem` (lines 16, 21, 26, 32, 41, 46): Create @pytest.fixture for _MockSystem and parametrize archetype/abilities.

- [ ] Verify: `pytest tests/unit/strategy/services/ability_sources/test_system_archetype.py` passes; LOC delta ≈ 20

**Notes:** _(none yet)_

---

### Task 1.17: test_command_handlers.py [Simple]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`

- [ ] [S12-CAT9-001] `Duplicate _make_session_with_real_fleets` (lines 303-353): Promote to module-level helper.

- [ ] Verify: `pytest tests/unit/strategy/test_command_handlers.py` passes; LOC delta ≈ 14

**Notes:** _(none yet)_

---

### Task 1.18: test_engine_event_emission.py [Simple]
**File:** `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py`

- [ ] [S04-CAT9-001] `3 module helpers encode internals` (lines 34-61): Convert to fixtures that minimize implementation coupling.

- [ ] Verify: `pytest tests/unit/strategy/test_engine_event_emission.py` passes; LOC delta ≈ 28

**Notes:** _(none yet)_

---

### Task 1.19: test_fleet_speed_calculator.py [Simple]
**File:** `tests/unit/strategy/test_fleet_speed_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_speed_calculator.py`

- [ ] [S02-CAT9-001] `Repeated mock construction across 7 tests` (lines 13-131): Extract _make_mock_ship_with_stats(mass, speed) helper.

- [ ] Verify: `pytest tests/unit/strategy/test_fleet_speed_calculator.py` passes; LOC delta ≈ 50

**Notes:** _(none yet)_

---

### Task 1.20: test_quickstart_builder.py [Simple]
**File:** `tests/unit/strategy/test_quickstart_builder.py`
**Tests:** `pytest tests/unit/strategy/test_quickstart_builder.py`

- [ ] [S09-CAT9-001] `Repeated spawn_initial_complexes setup` (lines 216-409): Extract a fixture and parametrize.

- [ ] Verify: `pytest tests/unit/strategy/test_quickstart_builder.py` passes; LOC delta ≈ 150

**Notes:** _(none yet)_

---

### Task 1.21: test_colonize_validator.py [Simple]
**File:** `tests/unit/strategy/validation/test_colonize_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_colonize_validator.py`

- [ ] [S05-CAT9-001] `Repeated _make_planet helpers` (lines 753-774, 890-913, 620-635): Move to a module fixture with kwargs overrides.

- [ ] Verify: `pytest tests/unit/strategy/validation/test_colonize_validator.py` passes; LOC delta ≈ 61

**Notes:** _(none yet)_

---

### Task 1.22: test_tri_state_widget.py [Simple]
**File:** `tests/unit/ui/components/filters/test_tri_state_widget.py`
**Tests:** `pytest tests/unit/ui/components/filters/test_tri_state_widget.py`

- [ ] [S06-CAT9-003] `Repeated UIButton/UILabel patches` (lines 27-141): Move shared patches to class level.

- [ ] Verify: `pytest tests/unit/ui/components/filters/test_tri_state_widget.py` passes; LOC delta ≈ 40

**Notes:** _(none yet)_

---

### Task 1.23: test_selection.py [Simple]
**File:** `tests/unit/ui/components/table/test_selection.py`
**Tests:** `pytest tests/unit/ui/components/table/test_selection.py`

- [ ] [S08-CAT9-001] `Delayed imports per test method` (lines 9-203): Move imports to module top-level.

- [ ] Verify: `pytest tests/unit/ui/components/table/test_selection.py` passes; LOC delta ≈ 40

**Notes:** _(none yet)_

---

### Task 1.24: test_component_modifier_grid_panel.py [Simple]
**File:** `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_component_modifier_grid_panel.py`

- [ ] [S03-CAT9-002] `Repeated bypass-init pattern` (lines 38-437): Extract helper.

- [ ] Verify: `pytest tests/unit/ui/panels/test_component_modifier_grid_panel.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 1.25: test_race_identity_panel.py [Simple]
**File:** `tests/unit/ui/panels/test_race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py`

- [ ] [S03-CAT9-001] `Repeated bypass-init pattern` (lines 55-428): Extract bypass-init into helper or move imports to module scope.

- [ ] Verify: `pytest tests/unit/ui/panels/test_race_identity_panel.py` passes; LOC delta ≈ 120

**Notes:** _(none yet)_

---

### Task 1.26: test_system_tree_panel.py [Complex]
**File:** `tests/unit/ui/panels/test_system_tree_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_system_tree_panel.py`

- [ ] [S04-CAT9-004] `30+ __init__ patches duplicated` (lines 61-660): Address by switching to real construction; this duplication becomes moot.

- [ ] Verify: `pytest tests/unit/ui/panels/test_system_tree_panel.py` passes; LOC delta ≈ 120

**Notes:** _(Plan-review M-06 (2026-05-03): "switch to real construction" requires real pygame_gui elements + StrategySessionFacade + registry data — effectively converts unit tests to integration tests, not a simplification.)_

---

### Task 1.27: test_modifier_logic_smart_floor.py [Simple]
**File:** `tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py`

- [ ] [S09-CAT9-005] `Weak assertion` (lines 37-44): Tighten to `result == pytest.approx(0.1, abs=0.01)`.

- [ ] Verify: `pytest tests/unit/ui/screens/builder/test_modifier_logic_smart_floor.py` passes; LOC delta ≈ 8

**Notes:** _(none yet)_

---

### Task 1.28: test_build_queue_list_window.py [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

- [ ] [S05-CAT9-003] `Redundant @patch decorators` (lines 95, 126, 156, 189, 213): Remove redundant decorators; rely on the fixture's existing patch.

- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_list_window.py` passes; LOC delta ≈ 15

**Notes:** _(none yet)_

---

### Task 1.29: test_fleet_data_source.py [Simple]
**File:** `tests/unit/ui/screens/test_fleet_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py`

- [ ] [S06-CAT9-001] `Repeated view_model creation` (lines 88-549): Extract a fixture/factory.

- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_data_source.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 1.30: test_race_flag_gallery.py [Simple]
**File:** `tests/unit/ui/test_race_flag_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_flag_gallery.py`

- [ ] [S03-CAT9-003] `Repeated bypass-init pattern` (lines 61-323): Extract helper.

- [ ] Verify: `pytest tests/unit/ui/test_race_flag_gallery.py` passes; LOC delta ≈ 80

**Notes:** _(none yet)_

---

### Task 1.31: test_formatters.py [Simple]
**File:** `tests/unit/ui/utils/test_formatters.py`
**Tests:** `pytest tests/unit/ui/utils/test_formatters.py`

- [ ] [S09-CAT9-003] `12 method-level imports` (lines 9-57): Hoist the import to module scope.

- [ ] Verify: `pytest tests/unit/ui/utils/test_formatters.py` passes; LOC delta ≈ 12

**Notes:** _(none yet)_

---

### Task 1.32: test_portraits.py [Simple]
**File:** `tests/unit/ui/utils/test_portraits.py`
**Tests:** `pytest tests/unit/ui/utils/test_portraits.py`

- [ ] [S05-CAT9-002] `7 method-level imports` (lines 7-52): Move imports to module top-level.

- [ ] Verify: `pytest tests/unit/ui/utils/test_portraits.py` passes; LOC delta ≈ 15

**Notes:** _(none yet)_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
