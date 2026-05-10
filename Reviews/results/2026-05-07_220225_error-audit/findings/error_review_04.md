# Error Handling Review: Shard 04
## Summary
- **Shard:** Shard 04
- **Files in Scope:** 192
- **Files Actually Read:** 192
- **Total Findings:** 8
- **Critical:** 0 | **Major:** 2 | **Minor:** 6

## Broad Except Findings

#### MAJOR: Broad except without required comment — scan_designs() swallows per-file errors silently
**ID:** ERR-04-001
**Location:** `game/ui/screens/battle_setup/controller.py:123`
**Code:**
```python
except Exception as e:
    logger.warning(f"Failed to load design {filename}: {e}")
```
**Issue:** Broad `except Exception` catches *all* exception types when iterating starter design files. The `load_json()` call on line 118 already handles `FileNotFoundError`, `json.JSONDecodeError`, `PermissionError`, and `OSError` internally, so this catch can only fire when the parsed data triggers an attribute error or type error during dict inspection on line 119 (`data.get('vehicle_type')`). The catch lacks the required `# Intentional broad catch:` comment per `docs/05_ERROR_HANDLING.md` § Broad Catch Rule.

The behaviour is arguably correct (one corrupt design file should not block the list from populating), but the missing justification comment makes it a silent contract.
**Suggestion:** Add `# Intentional broad catch: corrupt design data must not poison the design library scan` on the same line.
**LOC affected:** 1

---

#### MAJOR: Broad except without required comment — snapshot capture wraps to_dict() failures
**ID:** ERR-04-002
**Location:** `game/strategy/engine/turn_state_snapshot.py:56`
**Code:**
```python
except Exception as e:
    raise PersistenceException(
        f"Failed to capture turn state snapshot: {e}",
        code=ErrorCode.SNAPSHOT_FAILED.value,
        context={"turn_number": turn_number, "original_error": str(e)}
    ) from e
```
**Issue:** Broad `except Exception` wraps any exception from `empire.to_dict()` / `galaxy.to_dict()` into a `PersistenceException`. The behaviour is correct (any to_dict failure MUST become a snapshot capture failure), and chaining is preserved via `from e`. However, the catch lacks the required `# Intentional broad catch:` justification comment.
**Suggestion:** Add `# Intentional broad catch: any to_dict() failure must become SNAPSHOT_FAILED` on the same line.
**LOC affected:** 1

---

## JSON Bypass Findings

#### MINOR: Direct json.load() bypass in _load_json_or_empty helper
**ID:** ERR-04-003
**Location:** `game/strategy/data/galaxy_system_generator.py:229`
**Code:**
```python
with path.open('r', encoding='utf-8') as f:
    data = json.load(f)
```
**Issue:** The `_load_json_or_empty()` helper uses `json.load()` directly rather than `game.core.json_utils.load_json()`. The helper performs its own `path.exists()` check but does not catch `json.JSONDecodeError`, `PermissionError`, or `OSError` — any corrupt JSON file will crash the galaxy generation pipeline rather than degrading gracefully via the canonical `load_json(default={})` path.
**Suggestion:** Replace with `load_json(path, default={})` and remove the manual `path.exists()` guard, since `load_json` already returns a default on missing files and logs appropriately.
**LOC affected:** 5

---

#### MINOR: Direct json.load() bypass in _load_warp_point_types()
**ID:** ERR-04-004
**Location:** `game/strategy/data/galaxy_warp_generator.py:368`
**Code:**
```python
with path.open('r', encoding='utf-8') as f:
    data = json.load(f)
```
**Issue:** Same pattern as ERR-04-003 — `_load_warp_point_types()` on line 358 uses raw `json.load()` instead of `load_json()`. Has a `path.exists()` guard but will crash on corrupt JSON.
**Suggestion:** Replace with `load_json(path, default={})`.
**LOC affected:** 3

---

#### MINOR: Direct json.dump() bypass in crash snapshot dump
**ID:** ERR-04-005
**Location:** `game/strategy/engine/turn_state_snapshot.py:131`
**Code:**
```python
with open(filepath, 'w') as f:
    json.dump(crash_data, f, indent=2)
```
**Issue:** `dump_crash_snapshot()` uses `json.dump()` directly instead of `save_json()`. The `(OSError, TypeError)` catch on line 133 covers most failure modes, but the atomic write (tmp + rename) provided by `save_json()` is lost — a crash during the write could leave a partially-written corrupt crash snapshot file.
**Suggestion:** Replace with `save_json(filepath, crash_data, indent=2)` which handles atomic writes, parent directory creation, and consistent error logging.
**LOC affected:** 2

---

## Additional Issues Found

#### MINOR: Inconsistent "Intentional" vs "Intentional broad catch" in tkinter_utils.py comments
**ID:** ERR-04-006
**Location:** `game/ui/services/tkinter_utils.py:142, :175, :206, :229`
**Code:**
```python
except Exception as e:  # Intentional: file dialog is platform-dependent
```
**Issue:** Four of six broad except lines in this file use `# Intentional:` rather than the canonical `# Intentional broad catch:` format required by `docs/05_ERROR_HANDLING.md` § Broad Catch Rule. Lines 69 and 100 use the full `# Intentional broad catch:` prefix. The shorter form "Intentional" is not the documented format. The behaviour is correct (platform-dependent Tkinter operations should never crash).
**Suggestion:** Normalize all four comments to `# Intentional broad catch: file dialog is platform-dependent` (or clipboard variant).
**LOC affected:** 4

---

#### MINOR: star_generation_config.py catches broad exception set but returns a valid fallback
**ID:** ERR-04-007
**Location:** `game/strategy/data/star_generation_config.py:192`
**Code:**
```python
except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:
    logger.warning(f"Failed to load star generation config: {e}")
    return StarGenerationConfig(None)
```
**Issue:** This is a `lru_cache`-decorated singleton factory (`get_star_generation_config()`). The catch covers 6 specific exception types, which is unusually broad. While not `except Exception`, it catches `ValueError` and `KeyError` which are often programming bugs, potentially hiding configuration errors behind a silent fallback to defaults.
**Suggestion:** Remove `ValueError` and `KeyError` from the catch tuple — these indicate likely data integrity issues rather than expected I/O failures.
**LOC affected:** 1

---

#### MINOR: Exception chaining omission in _load_json_or_empty when json.load fails
**ID:** ERR-04-008
**Location:** `game/strategy/data/galaxy_system_generator.py:228-229`
**Code:**
```python
with path.open('r', encoding='utf-8') as f:
    data = json.load(f)
```
**Issue:** `_load_json_or_empty()` has no try/except around `json.load()`. If the JSON is malformed, the exception propagates unhandled. The docstring says it returns "an empty dict if the file is missing" but does not account for corrupt files. If `planet_types.json` is corrupt, galaxy generation crashes entirely. The codebase's canonical `load_json()` already handles this case by returning the default and logging.
**Suggestion:** Use `load_json(path, default={})` from `game.core.json_utils`. This is the same root cause as ERR-04-003.
**LOC affected:** 3

---

## File Coverage Verification

| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/core/json_utils.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/core/spectrum_math.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/run_loop.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
| game/simulation/combat/attack_contract.py | Read ✓ |
| game/simulation/combat/families/__init__.py | Read ✓ |
| game/simulation/combat/families/_beam_common.py | Read ✓ |
| game/simulation/combat/families/beam.py | Read ✓ |
| game/simulation/combat/fleet_aura_manager.py | Skipped (in shard 02) |
| game/simulation/combat/formation.py | Read ✓ |
| game/simulation/combat/weapon_registry.py | Read ✓ |
| game/simulation/components/abilities/colonize.py | Skipped (in shard 03) |
| game/simulation/components/abilities/defense.py | Skipped (in shard 02) |
| game/simulation/components/abilities/propulsion.py | Skipped (in shard 03) |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/simulation/components/abilities/weapons.py | Read ✓ |
| game/simulation/components/component_stats_calculator.py | Read ✓ |
| game/simulation/components/modifier_manager.py | Skipped (in shard 03) |
| game/simulation/components/modifiers.py | Skipped (in shard 02) |
| game/simulation/entities/ship.py | Read ✓ |
| game/simulation/entities/ship_combat_manager.py | Read ✓ |
| game/simulation/entities/ship_loader.py | Read ✓ |
| game/simulation/entities/stat_contributors/accumulator.py | Read ✓ |
| game/simulation/physics_constants.py | Read ✓ |
| game/simulation/replay/__init__.py | Read ✓ |
| game/simulation/replay/replay_capture.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/simulation/replay/replay_serialization.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ (header + exception sections) |
| game/simulation/systems/resource_manager.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/simulation/validation/ship_validator.py | Read ✓ |
| game/simulation/battle_outcome.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/strategy/__init__.py | Read ✓ |
| game/strategy/combat/__init__.py | Read ✓ |
| game/strategy/data/design_role.py | Read ✓ |
| game/strategy/data/fleet_consumable_aggregator.py | Read ✓ |
| game/strategy/data/fleet_pursuer_tracker.py | Read ✓ |
| game/strategy/data/galaxy.py | Read ✓ (header + relevant sections) |
| game/strategy/data/galaxy_state.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/strategy/data/galaxy_warp_generator.py | Read ✓ |
| game/strategy/data/planet_serde.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/strategy/data/star_generation_config.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/strategy/data/task_force.py | Read ✓ |
| game/strategy/engine/conflict_resolution_engine.py | Skipped (in shard 02) |
| game/strategy/engine/empire_economy_calculator.py | Read ✓ |
| game/strategy/engine/order_handlers/__init__.py | Read ✓ |
| game/strategy/engine/order_handlers/registry_factory.py | Skipped (in shard 02) |
| game/strategy/engine/order_handlers/superweapons.py | Read ✓ |
| game/strategy/engine/production_math.py | Read ✓ |
| game/strategy/engine/turn_state_snapshot.py | Read ✓ |
| game/strategy/generation/__init__.py | Read ✓ |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| game/strategy/generation/density/primitives/linear.py | Read ✓ |
| game/strategy/generation/density/primitives/spiral_arm.py | Read ✓ |
| game/strategy/generation/loaders/astrophysics_loader.py | Read ✓ |
| game/strategy/generation/placement_strategies.py | Read ✓ |
| game/strategy/interfaces/__init__.py | Read ✓ |
| game/strategy/services/__init__.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/services/deployment_zone_calculator.py | Read ✓ |
| game/strategy/services/fleet_cargo_projector.py | Read ✓ |
| game/strategy/services/fleet_navigation_service.py | Read ✓ |
| game/strategy/services/fleet_speed_calculator.py | Read ✓ |
| game/strategy/services/race_resolver.py | Read ✓ |
| game/strategy/services/replay_ship_builder.py | Read ✓ |
| game/strategy/services/system_destroyer.py | Read ✓ |
| game/strategy/services/task_group_suggester.py | Read ✓ |
| game/strategy/systems/race_library.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/strategy/facade/slices/system_slice.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ui/__init__.py | Skipped (in shard 03) |
| game/ui/assets/__init__.py | Read ✓ |
| game/ui/components/filters/__init__.py | Read ✓ |
| game/ui/effects/__init__.py | Read ✓ |
| game/ui/interfaces/__init__.py | Read ✓ |
| game/ui/orchestration/__init__.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/panels/ship_detail_panel.py | Skipped (in shard 03) |
| game/ui/renderer/__init__.py | Read ✓ |
| game/ui/renderer/sprites.py | Read ✓ |
| game/ui/research/__init__.py | Read ✓ |
| game/ui/research/research_renderer.py | Read ✓ |
| game/ui/research/research_scene.py | Read ✓ (header + relevant sections) |
| game/ui/screens/battle_screen.py | Read ✓ (header + relevant sections) |
| game/ui/screens/battle_setup/controller.py | Read ✓ |
| game/ui/screens/battle_setup/panels/right_panel.py | Read ✓ |
| game/ui/screens/battle_setup/view_model.py | Read ✓ |
| game/ui/screens/battle_state_viewer.py | Read ✓ |
| game/ui/screens/build_queue_list_window.py | Read ✓ (header) |
| game/ui/screens/build_queue_queue_data_source.py | Read ✓ (header + relevant) |
| game/ui/screens/build_queue_renderer.py | Read ✓ (header + relevant) |
| game/ui/screens/build_queue_selector.py | Read ✓ (header + relevant) |
| game/ui/screens/builder/__init__.py | Skipped (in shard 03) |
| game/ui/screens/builder/grouping_strategies.py | Read ✓ |
| game/ui/screens/builder/left_panel.py | Read ✓ (header + relevant) |
| game/ui/screens/builder/panel_layout_config.py | Read ✓ |
| game/ui/screens/builder/right_panel.py | Read ✓ (header + relevant) |
| game/ui/screens/builder/schematic_view.py | Read ✓ (header + relevant) |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/screens/builder/weapons_input_handler.py | Read ✓ |
| game/ui/screens/data_list_window_mixin.py | Read ✓ |
| game/ui/screens/empire_build_queue_filter_manager.py | Read ✓ |
| game/ui/screens/empire_build_queue_formatter.py | Read ✓ |
| game/ui/screens/fleet_report_window.py | Read ✓ (header + relevant) |
| game/ui/screens/fleet_selection_window.py | Read ✓ (header + relevant) |
| game/ui/screens/galaxy_test/constants.py | Read ✓ |
| game/ui/screens/galaxy_test/system_mode.py | Read ✓ |
| game/ui/screens/planet_list_filters.py | Read ✓ |
| game/ui/screens/planet_selection_window.py | Skipped (in shard 02) |
| game/ui/screens/race_setup/controller.py | Read ✓ (header + relevant) |
| game/ui/screens/race_setup/llm_dialog_service.py | Read ✓ (header + relevant) |
| game/ui/screens/race_setup/screen.py | Read ✓ (header + relevant) |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/screens/strategy_click_dispatcher.py | Read ✓ (header + relevant) |
| game/ui/screens/strategy_game_state_manager.py | Read ✓ (header + relevant) |
| game/ui/screens/strategy_menu_panel.py | Read ✓ |
| game/ui/screens/strategy_render/dyson_spheres.py | Read ✓ |
| game/ui/screens/strategy_render/fleets.py | Read ✓ (header + relevant) |
| game/ui/screens/strategy_render/overlay.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ (header + relevant) |
| game/ui/screens/strategy_ui_action_router.py | Read ✓ |
| game/ui/screens/strategy_windows/event_log_window_ctrl.py | Read ✓ |
| game/ui/screens/test_lab/__init__.py | Read ✓ |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ |
| game/ui/screens/test_lab/details/__init__.py | Read ✓ |
| game/ui/screens/test_lab/details/panel.py | Read ✓ (header + relevant) |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/ui/screens/test_lab/dialogs.py | Read ✓ |
| game/ui/screens/test_lab/formatting_utils.py | Read ✓ |
| game/ui/screens/test_lab/renderer/category_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/header_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/tag_filter_panel.py | Read ✓ |
| game/ui/screens/test_lab/renderer/test_list_panel.py | Read ✓ (header + relevant) |
| game/ui/screens/test_lab/results_panel.py | Read ✓ (header + relevant) |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ (header + relevant) |
| game/ui/screens/test_lab/test_run_details.py | Read ✓ |
| game/ui/screens/test_lab/viewmodel.py | Read ✓ (header + relevant) |
| game/ui/screens/workshop_data_reloader.py | Read ✓ |
| game/ui/screens/workshop_screen.py | Read ✓ (header + relevant) |
| game/ui/screens/workshop_ship_io.py | Read ✓ (header + relevant) |
| game/ui/screens/workshop_viewmodel.py | Read ✓ (header + relevant) |
| game/ui/services/tkinter_utils.py | Read ✓ |
