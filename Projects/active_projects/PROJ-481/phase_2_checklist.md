# Phase 2: Major UI narrowings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-481 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow ~40 MAJOR `-> Any` returns across UI list filters, list windows, strategy delegation property clusters, battle screen, workshop, and builder modules. All items audit-cited and re-verified against source.

---

## Tasks

### Task 2.1: planet_list_filters narrowings [Medium]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/ -k planet_list` then `mypy game/ui/screens/planet_list_filters.py`

- [ ] Narrow `gather_planets` (line 38) from `-> Any` to `-> list[Planet]`
- [ ] Narrow `filter_planets` (line 174 / current ~177) to `-> list[Planet]`
- [ ] Narrow `sort_planets` (line 215 / current ~218) to `-> list[Planet]`
- [ ] Narrow `get_column_value` (line 252 / current ~255) to `-> str`
- [ ] Narrow `compute_planet_ranges` (line 280 / current ~283) to `-> dict[str, tuple[float, float]]`
- [ ] Narrow `get_system_name` (line 333 / current ~336) to `-> str`
- [ ] Narrow `get_owner_name` (line 348 / current ~351) to `-> str`
- [ ] Verify: `pytest tests/ -k planet_list` passes; `mypy` clean on file

### Task 2.2: planet_list_window property narrowings [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/ -k planet_list_window` then `mypy game/ui/screens/planet_list_window.py`

- [ ] Narrow `filter_types` property (line 211) from `-> Any` to `-> dict[str, bool]`
- [ ] Narrow `filter_owner` property (line 221) to `-> dict[str, bool]`
- [ ] Narrow `filter_effects` property (line 231) to `-> dict[str, FilterState]`
- [ ] Narrow `filter_ranges` property (line 241) to `-> dict[str, list[float]]`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.3: star_list_filters narrowings [Medium]
**File:** `game/ui/screens/star_list_filters.py`
**Tests:** `pytest tests/ -k star_list` then `mypy game/ui/screens/star_list_filters.py`

- [ ] Narrow `gather_stars` (line 20) to `-> list[Star]`
- [ ] Narrow `filter_stars` (line 67 / current ~70) to `-> list[Star]`
- [ ] Narrow `sort_stars` (line 121 / current ~124) to `-> list[Star]`
- [ ] Narrow `compute_star_ranges` (line 163 / current ~166) to `-> dict[str, tuple[float, float]]`
- [ ] Narrow `get_system_name` (line 203 / current ~206) to `-> str`
- [ ] Narrow `get_star_type_display` (line 217 / current ~220) to `-> str`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.4: star_list_window property narrowings [Simple]
**File:** `game/ui/screens/star_list_window.py`
**Tests:** `pytest tests/ -k star_list_window` then `mypy game/ui/screens/star_list_window.py`

- [ ] Narrow `filter_types` property (line 277) to `-> dict[str, bool]`
- [ ] Narrow `filter_ranges` property (line 285) to `-> dict[str, list[float]]`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.5: setup_data_io narrowings [Medium]
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/ -k setup` then `mypy game/ui/screens/setup_data_io.py`

- [ ] Narrow `get_base_path` (line 34) to `-> str`
- [ ] Narrow `scan_ship_designs` (line 39) to `-> list[dict[str, Any]]`
- [ ] Narrow `load_ships_from_entries` (line 65) to `-> list[Ship]`
- [ ] Narrow `load_battle_setup` (line 171) to `-> tuple[list[dict[str, Any]], list[dict[str, Any]]] | tuple[None, None]`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.6: setup_renderer and setup_screen [Simple]
**Files:** `game/ui/screens/setup_renderer.py`, `game/ui/screens/setup_screen.py`
**Tests:** `pytest tests/ -k setup` then `mypy` on both files

- [ ] Narrow `draw_available_ships` in `setup_renderer.py` (line 35) to `-> int`
- [ ] Narrow `get_team_display_groups` in `setup_screen.py` (line 133) to `-> list[dict[str, str | int]]`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.7: strategy_renderer delegation property cluster [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ -k strategy_render` then `mypy game/ui/screens/strategy_renderer.py`

- [ ] Narrow `_get_font` (line 115) to `-> pygame.Font`
- [ ] Narrow `camera` property (line 121) to `-> Camera` (TYPE_CHECKING import)
- [ ] Narrow `galaxy` property (line 125) to `-> Galaxy`
- [ ] Narrow `systems` property (line 129) to `-> list[StarSystem]`
- [ ] Narrow `empires` property (line 133) to `-> list[Empire]`
- [ ] Narrow `hex_size` property (line 137) to `-> float`
- [ ] Narrow `screen_width` property (line 141) to `-> int`
- [ ] Narrow `screen_height` property (line 145) to `-> int`
- [ ] Narrow `SIDEBAR_WIDTH` property (line 149) to `-> int`
- [ ] Narrow `TOP_BAR_HEIGHT` property (line 153) to `-> int`
- [ ] Narrow `empire_assets` property (line 157) to `-> dict[int, Any]`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.8: strategy_screen delegation property cluster [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ -k strategy_screen` then `mypy game/ui/screens/strategy_screen.py`

- [ ] Narrow the 12 delegation properties at lines 161-536 (galaxy, empires, systems, facade, camera, etc.) — use TYPE_CHECKING imports for concrete types. Reference shard 03 report for the per-property breakdown
- [ ] Verify: tests pass; `mypy` clean

### Task 2.9: strategy_superweapons delegation properties [Simple]
**File:** `game/ui/screens/strategy_superweapons.py`
**Tests:** `pytest tests/ -k superweapon` then `mypy` on file

- [ ] Narrow 4 properties at lines 73-85: `systems` → `list[StarSystem]`, `camera` → `Camera`, `hex_size` → `float`, `galaxy` → `Galaxy`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.10: strategy_fleet_ops properties + handlers [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/ -k fleet_ops` then `mypy` on file

- [ ] Narrow `camera` (line 61) to `-> Camera`
- [ ] Narrow `empires` (line 65) to `-> list[Empire]`
- [ ] Narrow `hex_size` (line 69) to `-> float`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.11: battle_screen property and method narrowings [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/ -k battle_screen` then `mypy game/ui/screens/battle_screen.py`

- [ ] Narrow `engine` property (line 172) to `-> BattleEngine`
- [ ] Narrow `show_overlay` property (line 199) to `-> bool`
- [ ] Narrow `stats_panel_width` property (line 207) to `-> int`
- [ ] Narrow `ships` property (line 211) to `-> list[Ship]`
- [ ] Narrow `projectiles` property (line 215) to `-> list[Projectile]`
- [ ] Narrow `ai_controllers` property (line 219) to `-> list[AIController]`
- [ ] Narrow `is_battle_over` (line 481) to `-> bool`
- [ ] Narrow `get_winner` (line 485) to `-> int`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.12: workshop_viewmodel + workshop_viewmodel_ship_ops + weapons_viewmodel [Medium]
**Files:** `game/ui/screens/workshop_viewmodel.py`, `workshop_viewmodel_ship_ops.py`, `builder/weapons_viewmodel.py`
**Tests:** `pytest tests/ -k workshop or weapons_viewmodel` then `mypy` on files

- [ ] Narrow `WorkshopViewModel.validate_design` (line 407) to `-> DesignResult`
- [ ] Narrow `WorkshopShipOps.validate_design` (line 207) to `-> ValidationResult | None`
- [ ] Narrow `WeaponsViewModel.hovered_weapon` property (line 110) to `-> Component | None`
- [ ] Narrow `calc_damage_at_range` (line 392) to `-> float`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.13: builder helpers [Simple]
**Files:** `game/ui/screens/builder/left_panel.py`, `builder/modifier_logic.py`
**Tests:** `pytest tests/ -k builder` then `mypy` on files

- [ ] Narrow `get_add_count` in `left_panel.py` (line 453) to `-> int`
- [ ] Narrow `calculate_snap_value` in `modifier_logic.py` (line 150) to `-> float`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.14: test_lab essentials [Simple]
**Files:** `game/ui/screens/test_lab/component_dropdown.py`, `test_lab/test_executor.py`
**Tests:** `pytest tests/ -k test_lab` then `mypy` on files

- [ ] Narrow `get_selected_component_id` (component_dropdown.py:101) to `-> str | None`
- [ ] Narrow `run_headless` (test_executor.py:175) to `-> bool`
- [ ] Verify: tests pass; `mypy` clean

### Task 2.15: design_selector_window + dyson_spheres + battle_setup_controller [Simple]
**Files:** `game/ui/screens/design_selector_window.py`, `strategy_render/dyson_spheres.py`, `battle_setup/controller.py`
**Tests:** `pytest tests/` for affected paths; `mypy` on files

- [ ] Narrow `_get_role_filter_options` (`design_selector_window.py:396` — was 388, line drifted) to `-> list[str]`
- [ ] Narrow `load_dyson_sphere_image` (`dyson_spheres.py:116`) to `-> pygame.Surface | None`
- [ ] Narrow `_build_end_condition` (`battle_setup/controller.py:411`) to `-> IEndCondition` (import the protocol from `game/simulation/systems/battle_end_conditions.py`)
- [ ] Verify: tests pass; `mypy` clean

### Task 2.16: Final phase verification [Simple]
- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [ ] Verify: `mypy` shows no new errors on any touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
