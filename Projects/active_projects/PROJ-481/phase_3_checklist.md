# Phase 3: Minor UI narrowings + ignore cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-481 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Narrow ~38 MINOR `-> Any` returns and missing return types across UI helpers, viewmodels, and editors. Replace 2 unjustified `# type: ignore[assignment]` (defeat_dialog/turn_failed_dialog — same pattern, cross-shard consistency fix). Narrow one parameter to remove a `# type: ignore[index]` in ship_theme_manager.

---

## Tasks

### Task 3.1: planet_list_window + star_list_window snapshot helpers [Simple]
**Files:** `game/ui/screens/planet_list_window.py`, `star_list_window.py`
**Tests:** `pytest tests/ -k 'list_window'` then `mypy` on files

- [x] Narrow `planet_list_window._capture_current_state` (line 292) to `-> dict[str, Any]`
- [x] Narrow `star_list_window._capture_current_state` (line 448) to `-> dict[str, Any]`
- [x] Verify: tests pass; `mypy` clean

### Task 3.2: strategy_click_dispatcher [Simple]
**File:** `game/ui/screens/strategy_click_dispatcher.py`
**Tests:** `pytest tests/ -k strategy_click` then `mypy` on file

- [x] Narrow `scene` property (line 53) to `-> StrategyScreen` (TYPE_CHECKING import)
- [x] Narrow `_resolve_click_target` (line 517) to `-> HexCoord`
- [x] Verify: tests pass; `mypy` clean

### Task 3.3: strategy_colonization [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/ -k colonization` then `mypy` on file

- [x] Narrow `systems` (line 40), `camera` (line 44), `hex_size` (line 48) delegation properties to concrete types
- [x] Narrow `request_colonize_order` (line 224) to `-> dict[str, Any] | None`
- [x] Narrow `_get_system_at_hex` (line 246) to `-> StarSystem | None`
- [x] Narrow `_resolve_planet_global_hex` (line 259) to `-> HexCoord | None`
- [x] Verify: tests pass; `mypy` clean

### Task 3.4: strategy_event_router [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/ -k event_router` then `mypy` on file

- [x] Narrow `resolve_race` nested callback (line 336) to `-> RaceConfig | None`
- [x] Narrow `_get_race_config` (line 363) to `-> RaceConfig | None`
- [x] Verify: tests pass; `mypy` clean

### Task 3.5: strategy_camera_nav cluster [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py`
**Tests:** `pytest tests/ -k camera_nav` then `mypy` on file

- [x] Narrow `camera` (line 40), `systems` (line 44), `hex_size` (line 48) properties
- [x] Narrow `_resolve_global_hex` (line 79) to `-> HexCoord | None`
- [x] Narrow `cycle_selection` (line 204) to `-> Colony | Fleet | None` (TYPE_CHECKING imports)
- [x] Verify: tests pass; `mypy` clean

### Task 3.6: workshop_screen properties + helpers [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/ -k workshop` then `mypy` on file

- [x] Narrow 5 delegation properties at lines 369, 377, 386, 390, 398: `selected_component` → `Component | None`, `dragged_item` (concrete), `ship` → `Ship | None`, `selected_components` → `list[Component]`, `available_components` → `list[Component]`
- [x] Narrow `_get_vehicle_classes` (line 193) to `-> dict[str, Any]`
- [x] Narrow `_get_button_definitions` (line 578) to `-> list[tuple[str, str, int]]`
- [x] Verify: tests pass; `mypy` clean

### Task 3.7: workshop side helpers [Simple]
**Files:** `game/ui/screens/workshop_viewmodel.py`, `workshop_ship_io.py`, `workshop_event_router.py`
**Tests:** `pytest tests/ -k workshop` then `mypy` on files

- [x] Add return annotation to `_with_ship` (workshop_viewmodel.py:129) — choose `-> Any` (simplest) or `-> TypeVar('T')` (template-method). Note: this was an UNCERTAIN item; user opted to include with simplest annotation
- [x] Add return annotation to `_design_catalog` (workshop_ship_io.py:67) → `-> DesignCatalog | None`
- [x] Narrow `_get_vehicle_classes` (workshop_event_router.py:44) to `-> VehicleClassRegistry | None`
- [x] Verify: tests pass; `mypy` clean

### Task 3.8: builder/modifier_row + galaxy_test/galaxy_mode + test_lab/test_run_card [Simple]
**Files:** `game/ui/screens/builder/modifier_row.py`, `galaxy_test/galaxy_mode.py`, `test_lab/test_run_card.py`
**Tests:** `pytest tests/` for affected paths; `mypy` on files

- [x] Narrow `build_ui` (`modifier_row.py:129`) to `-> int`
- [x] Narrow `create_ui` (`galaxy_mode.py:63`) to `-> list`
- [x] Narrow `get_height` (`test_run_card.py:61`) to `-> int`
- [x] Verify: tests pass; `mypy` clean

### Task 3.9: battle_results_screen + fleet_report_filters + fleet_report_window [Simple]
**Files:** `game/ui/screens/battle_results_screen.py`, `fleet_report_filters.py`, `fleet_report_window.py`
**Tests:** `pytest tests/ -k 'battle_results or fleet_report'` then `mypy` on files

- [x] Narrow `_hp_color` (`battle_results_screen.py:34`) to `-> tuple[int, int, int]`
- [x] Narrow `get_sort_key` inner callback (`fleet_report_filters.py:274`) to `-> int | float | str`
- [x] Narrow `process_event` (`fleet_report_window.py:277` — was 248, drifted) to `-> bool`
- [x] Verify: tests pass; `mypy` clean

### Task 3.10: strategy_fleet_ops + strategy_superweapons remaining helpers [Simple]
**Files:** `game/ui/screens/strategy_fleet_ops.py`, `strategy_superweapons.py`
**Tests:** `pytest tests/ -k 'fleet_ops or superweapon'` then `mypy` on files

- [x] Narrow `handle_move_designation` (`strategy_fleet_ops.py:88`) to `-> dict | None`
- [x] Narrow `handle_join_designation` (`strategy_fleet_ops.py:172`) to `-> dict | None`
- [x] Narrow `_get_system_at_hex` (`strategy_superweapons.py:362`) to `-> StarSystem | None`
- [x] Narrow `_get_warp_point_at_hex` (`strategy_superweapons.py:369`) to `-> WarpPoint | None`
- [x] Verify: tests pass; `mypy` clean

### Task 3.11: misc helpers [Simple]
**Files:** `game/ui/screens/battle_ui.py`, `builder_selection.py`, `strategy_input_handler.py`, `species_selector_mixin.py`, `test_lab/ship_panels.py`, `transfer_view_model.py`, `transfer_mass_preview.py`, `build_queue_list_window.py`
**Tests:** `pytest tests/` for affected paths; `mypy` on files

- [x] Narrow `handle_click` (`battle_ui.py:87`) to `-> bool`
- [x] Narrow `normalize_selection` (`builder_selection.py:21`) to `-> list[tuple]`
- [x] Narrow `get_primary_selection` (`builder_selection.py:114`) to `-> tuple | None`
- [x] Narrow `handle_click` (`strategy_input_handler.py:158`) to `-> bool`
- [x] Narrow `_get_active_race_config` (`species_selector_mixin.py:147`) to `-> RaceConfig | None`
- [x] Narrow `get_selected_ship_info` (`test_lab/ship_panels.py:183`) to `-> dict | None`
- [x] Narrow `apply_arrow`, `apply_max`, `get_pending` (`transfer_view_model.py:105,122,148`) to `-> float | int`
- [x] Add return annotation to `_get_catalog` (`transfer_mass_preview.py:189`) → `-> ResourceCatalog`
- [x] Narrow `process_event` (`build_queue_list_window.py:210`) to `-> bool`
- [x] Verify: tests pass; `mypy` clean

### Task 3.12: editor _button_handlers + strategy_game_state_manager + test_lab/details/validation [Simple]
**Files:** `game/ui/screens/atmosphere_target_editor.py`, `radiation_shield_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `strategy_game_state_manager.py`, `test_lab/details/validation.py`
**Tests:** `pytest tests/` for affected paths; `mypy` on files

- [x] Add return annotation to `_button_handlers` (`atmosphere_target_editor.py:223`) → `-> dict[UIButton, Callable[[], None]]`
- [x] Add return annotation to `_button_handlers` (`radiation_shield_editor.py:176`) → same
- [x] Add return annotation to `_button_handlers` (`gravity_target_editor.py:164`) → same (audit shard 02 noted false-positive but verifier disagrees — confirm before annotating)
- [x] Add return annotation to `_button_handlers` (`water_target_editor.py:173`) → same (same caveat as above)
- [x] Add return annotation to `_iter_snapshot_windows` (`strategy_game_state_manager.py:166`) → `-> Iterator[Any]`
- [x] Add return annotation to `_phase_color` (`test_lab/details/validation.py:39`) → `-> tuple[int, int, int]`
- [x] Verify: tests pass; `mypy` clean

### Task 3.13: pygame_gui_patch helper [Simple]
**File:** `game/ui/pygame_gui_patch.py`
**Tests:** `pytest tests/` for affected paths; `mypy` on file

- [x] Add return annotation to `_to_tuple` (line 90) → `-> tuple | None`
- [x] Verify: tests pass; `mypy` clean

### Task 3.14: defeat_dialog + turn_failed_dialog ignore cleanup [Simple]
**Files:** `game/ui/screens/defeat_dialog.py`, `turn_failed_dialog.py`
**Tests:** `pytest tests/ -k 'defeat_dialog or turn_failed'` then `mypy` on files

- [x] In `defeat_dialog.py`: declare `self._dismiss_button: Optional[UIButton] = None` in the constructor **before** the bypass-check, then remove the `# type: ignore[assignment]` at line 83
- [x] In `turn_failed_dialog.py`: identical fix — declare `self._dismiss_button: Optional[UIButton] = None` before the bypass-check, remove the `# type: ignore[assignment]` at line 99 (cross-shard consistency with defeat_dialog per verification.md)
- [x] Verify: tests pass; `mypy` clean

### Task 3.15: ship_theme_manager parameter narrowing [Simple]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ -k ship_theme` then `mypy` on file

- [x] Narrow the `expected` parameter (currently `Optional[object]`, line 241 region) to `Sequence[int] | None` (or `tuple[int, int] | None`) so the index access at line 254 type-checks without the `# type: ignore[index]`
- [x] Remove the `# type: ignore[index]` at line 254
- [x] Verify: existing `except (TypeError, ValueError, IndexError)` still catches malformed input
- [x] Verify: tests pass; `mypy` clean

### Task 3.16: Final phase verification [Simple]
- [x] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [x] Verify: `mypy` shows no new errors on touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
