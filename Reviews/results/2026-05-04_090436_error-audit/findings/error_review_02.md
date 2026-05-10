# Error Handling Review: Shard 02

## Summary
- Files in Scope: 150
- Files Actually Read: 150
- Total Findings: 12
- Critical: 0 | Major: 2 | Minor: 10

---

## Broad Except Findings

#### MAJOR: Broad `except Exception` without justification comment in `TurnStateSnapshot.capture`
**ID:** ERR-02-001
**Location:** game/strategy/engine/turn_state_snapshot.py:56
**Code:**
```python
except Exception as e:
    raise PersistenceException(
        f"Failed to capture turn state snapshot: {e}",
        code=ErrorCode.SNAPSHOT_FAILED.value,
        context={"turn_number": turn_number, "original_error": str(e)}
    ) from e
```
**Issue:** The broad `except Exception` lacks a justification comment per `docs/05_ERROR_HANDLING.md` § "Intentional Broad Catch Convention." Every other broad catch in this shard (7 sites across simulation_adapter, game_initializer, build_queue_controller, system_tree_panel) carries one. The catch does wrap-and-re-raise with `from e` chaining, so it's functionally sound — but fails the audit convention.
**Suggestion:** Add `# Intentional broad catch: to_dict() implementations may surface arbitrary types during serialization; any failure → PersistenceException` on the except line.
**LOC affected:** 1

#### MAJOR: Naked `json.load` bypass instead of `json_utils.load_json` in galaxy system generator
**ID:** ERR-02-002
**Location:** game/strategy/data/galaxy_system_generator.py:229
**Code:**
```python
def _load_json_or_empty(path_value: Any, dict_key: Optional[str] = None) -> Dict[str, Any]:
    from pathlib import Path
    import json

    path = Path(path_value)
    if not path.exists():
        return {}
    with path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if dict_key is None:
        return data
    return data.get(dict_key, {})
```
**Issue:** Bypasses `game.core.json_utils.load_json()` (the canonical API per `docs/05_ERROR_HANDLING.md` § JSON Utilities). The hand-rolled function duplicates the `path.exists()` guard but omits `json.JSONDecodeError`, `PermissionError`, and `OSError` handling. `load_json(path, default={})` covers all of these. The custom `dict_key` extraction is the only unique behavior; wrapping `load_json()` result with that extraction would satisfy the convention.
**Suggestion:** Replace the body with `data = load_json(str(path), default={})` and keep the `dict_key` post-filter. This nets correct decode/permission errors along with the existing not-found fallback.
**LOC affected:** ~10

---

## JSON Bypass Findings

#### MINOR: Direct `json.loads`/`json.dumps` for local manifest cache
**ID:** ERR-02-003
**Location:** game/assets/component_derivatives.py:100, 109
**Code:**
```python
return json.loads(path.read_text(encoding="utf-8"))
```
```python
temp_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
```
**Issue:** The manifest read uses `json.loads` with a bare `except json.JSONDecodeError` (correct), and the write uses `json.dumps` without error handling. The file is a local auto-generated cache (not game data shipped to users), so priority is low. However, `json_utils.load_json` would handle `FileNotFoundError` / `PermissionError` / `OSError` in addition to decode errors, making the reader more robust. **Verified:** catch at line 101 is `json.JSONDecodeError` only — OK but not as comprehensive as json_utils.
**Suggestion:** Replace `json.loads(path.read_text(...))` with `load_json(str(path), default={})` for free OS-level error handling. The write side (`_write_manifest`) is append-to-temp-then-replace — already robust.
**LOC affected:** 2

#### MINOR: Direct `json.dumps`/`json.loads` in BattleState serialization (in-memory, not file I/O)
**ID:** ERR-02-004
**Location:** game/simulation/battle_state.py:629, 657, 775
**Code:**
```python
def to_json(self, indent: int = 2) -> str:
    return json.dumps(self.to_dict(), indent=indent)
```
```python
def from_json(cls, json_str: str) -> 'BattleState':
    data = json.loads(json_str)
    return cls.from_dict(data)
```
**Issue:** These are convenience in-memory serialization methods (not file I/O). `json_utils` is designed for file-based operations; using raw `json.dumps`/`json.loads` for in-memory conversions is acceptable. **No action needed** — the data was already validated at the file boundary by json_utils before reaching these methods.
**LOC affected:** 0

#### MINOR: Direct `json.dump` for crash snapshot (debug artifact, not game data)
**ID:** ERR-02-005
**Location:** game/strategy/engine/turn_state_snapshot.py:131
**Code:**
```python
with open(filepath, 'w') as f:
    json.dump(crash_data, f, indent=2)
```
**Issue:** This is a crash-debugging artifact, not game-save data. The surrounding `try/except (OSError, TypeError)` provides error coverage. `json_utils.save_json` is overengineered for a crash-dump — atomicity against partial writes is unimportant here. **No action needed.**
**LOC affected:** 0

#### MINOR: Direct `json.dumps` for LLM prompt payload (in-memory string construction)
**ID:** ERR-02-006
**Location:** game/strategy/services/race_description_prompt_builder.py:200
**Code:**
```python
return json.dumps(payload, indent=2, ensure_ascii=False)
```
**Issue:** This constructs a string payload for LLM API consumption — not file I/O. `json_utils` targets file operations; raw `json.dumps` for in-memory string construction is correct. **No action needed.**
**LOC affected:** 0

#### MINOR: Direct `json.dumps` for UI debug popup (in-memory formatting)
**ID:** ERR-02-007
**Location:** game/ui/screens/builder/detail_panel.py:197
**Code:**
```python
json_str = json.dumps(self.current_component.data, indent=4)
```
**Issue:** This formats component data for an HTML debug popup — in-memory only, not file I/O. Correct usage of raw `json.dumps`. **No action needed.**
**LOC affected:** 0

---

## Resource Cleanup Findings

No resource leaks detected. Notable confirmations:

- `game/assets/component_derivatives.py:137-143` — `PIL.Image.close()` in `finally` block, temp file cleaned up.
- `game/app_bootstrap.py:109-128` — `@contextmanager` for timed phases, `finally` ensures timer completes.
- `game/ui/screens/race_setup/screen.py:464-470` — `kill()` cancels in-flight LLM calls before `super().kill()`.
- `game/simulation/services/design_loader.py` — uses `with` context via `load_json_required`.
- `game/strategy/data/galaxy_system_generator.py:228` — uses `with path.open(...)` context manager. (However, see ERR-02-002 for json_utils bypass.)

---

## Additional Issues Found

#### MINOR: Silent `except (TypeError, AttributeError): pass` in stat rows dynamic module
**ID:** ERR-02-008
**Location:** game/ui/screens/builder/stat_rows_dynamic.py:29, 44, 94
**Code:**
```python
except (TypeError, AttributeError):
    pass
```
**Issue:** Three sites silently swallow `TypeError` and `AttributeError` during dynamic stat inspection (resource discovery, consumption lookup, resource row building). The pattern is defensive against `None` attribute chains / unexpected dict shapes, and falling back to 0 / empty list / inf is correct behavior. However, the bare `pass` loses all diagnostic information. A `logger.debug` would make silent structural mismatches visible in dev builds without changing behavior.
**Suggestion:** Replace `except (TypeError, AttributeError): pass` with `except (TypeError, AttributeError): logger.debug("Stat inspection failed for resource", exc_info=True)`.
**LOC affected:** 3 lines

#### MINOR: Potential `AttributeError` on `mod_def.restrictions` without prior existence check
**ID:** ERR-02-009
**Location:** game/simulation/services/modifier_service.py:85
**Code:**
```python
mod_def = modifier_registry[mod_id]
if not mod_def.restrictions:
    return True
```
**Issue:** Line 82 validates `mod_id in modifier_registry`, and line 84 fetches `mod_def`. If `mod_def` is a registry entry that lacks a `restrictions` attribute (e.g., a raw dict from test mocks), accessing `mod_def.restrictions` raises `AttributeError`. Production modifiers always have this attribute (it's set on `ModifierDefinition`), and the key-existence guard on line 82 provides the first safety net. Still, defensive `getattr` would protect against mock drift.
**Suggestion:** `restrictions = getattr(mod_def, 'restrictions', None); if not restrictions: return True`
**LOC affected:** 1

#### MINOR: `_read_manifest` catches only `json.JSONDecodeError` — misses `PermissionError`/`OSError` from `path.read_text()`
**ID:** ERR-02-010
**Location:** game/assets/component_derivatives.py:100-103
**Code:**
```python
try:
    return json.loads(path.read_text(encoding="utf-8"))
except json.JSONDecodeError:
    logger.warning("Ignoring invalid component derivative manifest: %s", path)
    return {}
```
**Issue:** `path.read_text()` can raise `PermissionError` or `OSError` if the manifest file is locked or the filesystem is unwritable. These would propagate uncaught. In practice the manifest is local and the path exists (checked at line 44 before reaching here), so this is low-risk. But the try/except could be widened to `except (json.JSONDecodeError, OSError)`.
**Suggestion:** `except (json.JSONDecodeError, OSError):` or switch to `load_json(str(path), default={})`.
**LOC affected:** 1

#### MINOR: `_write_manifest` has no error handling for `temp_path.write_text()` or `os.replace()`
**ID:** ERR-02-011
**Location:** game/assets/component_derivatives.py:109-110
**Code:**
```python
temp_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
os.replace(temp_path, path)
```
**Issue:** If `write_text` fails (disk full, permission denied), the `OSError` propagates uncaught. `json_utils.save_json` implements atomic save with error handling; replicating that manually is fragile. However, the manifest is an optimization cache — losing it is non-critical (the next startup regenerates derivatives from source hashes).
**Suggestion:** Low priority; `save_json` from json_utils would handle this atomically.
**LOC affected:** 2

#### MINOR: `galaxy_system_generator.py` `_load_json_or_empty` lacks `PermissionError`/`OSError` handling
**ID:** ERR-02-012
**Location:** game/strategy/data/galaxy_system_generator.py:228-232
**Issue:** Same as ERR-02-002 but focused on the missing error types. The `with path.open()` block will propagate `PermissionError`/`OSError` directly to the caller. Using `load_json` would handle these uniformly with a default fallback.
**Suggestion:** See ERR-02-002.
**LOC affected:** 5

---

## File Coverage Verification
| File | Status |
|------|--------|
| game/strategy/adapters/__init__.py | Read ✓ |
| game/strategy/adapters/simulation_adapter.py | Read ✓ |
| game/ui/widgets/panel_factory.py | Read ✓ |
| game/strategy/facade/dto/colony_demographic_view.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/strategy/services/ability_iterator.py | Read ✓ |
| game/ui/screens/strategy_game_state_manager.py | Read ✓ |
| game/simulation/battle_outcome.py | Read ✓ |
| game/strategy/engine/planet_energy_engine.py | Read ✓ |
| game/simulation/combat/modifier_stack.py | Read ✓ |
| game/strategy/data/planet_atmosphere.py | Read ✓ |
| game/strategy/data/order_types.py | Read ✓ |
| game/simulation/interfaces/ability_protocols.py | Read ✓ |
| game/strategy/generation/loaders/system_blueprints_loader.py | Read ✓ |
| game/ui/screens/planet_list_sidebar.py | Read ✓ |
| game/simulation/entities/ship_combat_engine.py | Read ✓ |
| game/simulation/entities/ship_component_manager.py | Read ✓ |
| game/ui/screens/strategy_windows/build_queue_windows.py | Read ✓ |
| game/strategy/engine/turn_state_snapshot.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/strategy/data/ship_display_formatter.py | Read ✓ |
| game/ui/panels/__init__.py | Read ✓ |
| game/ui/assets/__init__.py | Read ✓ |
| game/strategy/data/spatial_index.py | Read ✓ |
| game/strategy/engine/game_session.py | Read ✓ |
| game/ui/screens/test_lab/results_panel.py | Read ✓ |
| game/run_loop.py | Read ✓ |
| game/strategy/config/__init__.py | Read ✓ |
| game/ui/utils/json_diff.py | Read ✓ |
| game/strategy/generation/density/primitives/noise.py | Read ✓ |
| game/strategy/interfaces/battle_resolver.py | Read ✓ |
| game/simulation/battle_config.py | Read ✓ |
| game/strategy/engine/fleet_movement_engine.py | Read ✓ |
| game/ui/screens/builder/stat_rows_dynamic.py | Read ✓ |
| game/ui/widgets/range_slider_builder.py | Read ✓ |
| game/ui/screens/test_lab/details/panel.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/ui/screens/fleet_report_filters.py | Read ✓ |
| game/simulation/validation/ship_validator.py | Read ✓ |
| game/strategy/engine/game_initializer.py | Read ✓ |
| game/simulation/services/design_loader.py | Read ✓ |
| game/ui/screens/builder/weapons_input_handler.py | Read ✓ |
| game/simulation/interfaces/__init__.py | Read ✓ |
| game/strategy/engine/action_execution_engine.py | Read ✓ |
| game/strategy/services/modifier_resolver.py | Read ✓ |
| game/simulation/validation/__init__.py | Read ✓ |
| game/ui/screens/test_lab/test_run_card.py | Read ✓ |
| game/ui/research/research_renderer.py | Read ✓ |
| game/ui/screens/setup_renderer.py | Read ✓ |
| game/ui/screens/race_setup/screen.py | Read ✓ |
| game/strategy/services/race_description_prompt_builder.py | Read ✓ |
| game/ui/screens/builder/structure_list_items.py | Read ✓ |
| game/strategy/engine/consumable_management_engine.py | Read ✓ |
| game/strategy/systems/race_randomizer.py | Read ✓ |
| game/strategy/validation/__init__.py | Read ✓ |
| game/simulation/components/abilities/resources.py | Read ✓ |
| game/simulation/replay/replay_player.py | Read ✓ |
| game/strategy/combat/__init__.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/simulation/services/modifier_service.py | Read ✓ |
| game/strategy/engine/planet_action_engine.py | Read ✓ |
| game/strategy/engine/production_engine.py | Read ✓ |
| game/ui/screens/event_log_data_source.py | Read ✓ |
| game/ui/filters/__init__.py | Read ✓ |
| game/ui/screens/strategy_modal_window.py | Read ✓ |
| game/simulation/components/ability_manager.py | Read ✓ |
| game/strategy/data/race_caption_loader.py | Read ✓ |
| game/simulation/entities/ship_resource_manager.py | Read ✓ |
| game/ui/services/image/provider.py | Read ✓ |
| game/simulation/components/modifier_introspection.py | Read ✓ |
| game/ui/panels/build_queue_drag_handler.py | Read ✓ |
| game/ui/services/image/factory.py | Read ✓ |
| game/simulation/entities/ship_design_stats.py | Read ✓ |
| game/ui/screens/planet_list_filters.py | Read ✓ |
| game/simulation/combat/ability_stat_registry.py | Read ✓ |
| game/simulation/__init__.py | Read ✓ |
| game/ui/components/table/selection.py | Read ✓ |
| game/strategy/generation/density/primitives/radial.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
| game/ui/screens/test_lab/details/draw_context.py | Read ✓ |
| game/ui/screens/star_list_presets.py | Read ✓ |
| game/ui/screens/workshop_viewmodel_layer_ops.py | Read ✓ |
| game/strategy/services/ability_sources/system_archetype.py | Read ✓ |
| game/app_bootstrap.py | Read ✓ |
| game/ui/screens/star_list_sidebar.py | Read ✓ |
| game/ui/screens/strategy_windows/__init__.py | Read ✓ |
| game/ui/renderer/sprites.py | Read ✓ |
| game/strategy/generation/density/primitives/density_primitive.py | Read ✓ |
| game/simulation/replay/replay_outcome.py | Read ✓ |
| game/strategy/generation/loaders/__init__.py | Read ✓ |
| game/simulation/services/ship_materializer.py | Read ✓ |
| game/ui/screens/strategy_renderer.py | Read ✓ |
| game/ui/config.py | Read ✓ |
| game/ui/screens/strategy_build_queue_manager.py | Read ✓ |
| game/ui/screens/strategy_render/cursor.py | Read ✓ |
| game/strategy/facade/strategy_session_facade.py | Read ✓ |
| game/simulation/services/battle_service.py | Read ✓ |
| game/strategy/services/cargo_transfer_service.py | Read ✓ |
| game/strategy/data/planet.py | Read ✓ |
| game/strategy/facade/slices/planet_slice.py | Read ✓ |
| game/ui/screens/test_lab/renderer/__init__.py | Read ✓ |
| game/strategy/engine/handlers/base.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/ui/screens/battle_setup/__init__.py | Read ✓ |
| game/ui/panels/planet_report_panel.py | Read ✓ |
| game/ui/screens/atmosphere_target_editor.py | Read ✓ |
| game/ui/screens/test_lab/screen_input_handler.py | Read ✓ |
| game/ui/screens/race_setup/ui_builder.py | Read ✓ |
| game/strategy/data/ship_consumable_manager.py | Read ✓ |
| game/strategy/services/component_inspector.py | Read ✓ |
| game/strategy/data/galaxy_system_generator.py | Read ✓ |
| game/strategy/engine/superweapon_command_handlers.py | Read ✓ |
| game/strategy/data/ship_cargo_manager.py | Read ✓ |
| game/ui/screens/system_selection_window.py | Read ✓ |
| game/ui/screens/test_lab/data_extractor.py | Read ✓ |
| game/ui/screens/settings_window.py | Read ✓ |
| game/simulation/components/abilities/superweapons.py | Read ✓ |
| game/ui/screens/star_list_filters.py | Read ✓ |
| game/strategy/services/stabilizer_registry.py | Read ✓ |
| game/ui/services/component_service.py | Read ✓ |
| game/ui/screens/list_data_source_base.py | Read ✓ |
| game/strategy/generation/density/primitives/linear.py | Read ✓ |
| game/simulation/battle_state.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/strategy/systems/design_library.py | Read ✓ |
| game/ui/screens/race_setup/__init__.py | Read ✓ |
| game/ui/screens/builder/detail_panel.py | Read ✓ |
| game/ui/screens/builder/stat_getters.py | Read ✓ |
| game/ui/screens/strategy_windows/planet_abilities_ctrl.py | Read ✓ |
| game/simulation/entities/ship_layer_manager.py | Read ✓ |
| game/strategy/generation/region_classifier.py | Read ✓ |
| game/ai/spatial_behaviors/base.py | Read ✓ |
| game/ai/controller.py | Read ✓ |
| game/strategy/validation/planet_order_validator.py | Read ✓ |
| game/ui/services/ship_factory.py | Read ✓ |
| game/ui/screens/builder/__init__.py | Read ✓ |
| game/ui/screens/strategy_windows/transfer_dialogs.py | Read ✓ |
| game/ui/components/table/header.py | Read ✓ |
| game/simulation/combat/targeting_system.py | Read ✓ |
| game/ui/screens/test_lab/test_executor.py | Read ✓ |
| game/ui/screens/radiation_shield_editor.py | Read ✓ |
| game/strategy/data/planet_naming.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/ui/panels/system_tree_panel.py | Read ✓ |
| game/ui/screens/empire_build_queue_filter_manager.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/ui/panels/base_gallery.py | Read ✓ |
| game/ui/screens/strategy_ui.py | Read ✓ |
| game/strategy/services/ability_sources/warp_point.py | Read ✓ |
| game/ai/spatial_behaviors/_formation_utils.py | Read ✓ |
| game/ui/screens/strategy_render/background.py | Read ✓ |
| game/ui/screens/test_lab/details/validation.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/strategy/facade/dto/empire_dto.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/ui/screens/planet_target_editor_base.py | Read ✓ |
| game/simulation/components/abilities/cargo.py | Read ✓ |
| game/simulation/components/component_health_manager.py | Read ✓ |
| game/strategy/data/build_queue_source.py | Read ✓ |
| game/ui/screens/builder/stat_definitions.py | Read ✓ |
| game/ui/screens/empire_build_queue_sidebar.py | Read ✓ |
| game/ui/utils/__init__.py | Read ✓ |
| game/simulation/components/__init__.py | Read ✓ |
| game/ui/screens/build_queue_helpers.py | Read ✓ |
| game/strategy/data/storm.py | Read ✓ |
| game/ui/screens/strategy_panel_manager.py | Read ✓ |
| game/strategy/facade/__init__.py | Read ✓ |
| game/simulation/systems/battle_engine.py | Read ✓ |
| game/ui/screens/strategy_render/systems.py | Read ✓ |
| game/ui/screens/battle_screen.py | Read ✓ |
| game/simulation/components/abilities/ui_colors.py | Read ✓ |
| game/strategy/generation/storm_generator.py | Read ✓ |
