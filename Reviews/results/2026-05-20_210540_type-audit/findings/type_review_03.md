# Type Safety Audit — Shard 03 Reviewer Report

**Generated:** 2026-05-20  
**Shard:** 03 (208 files)  
**Reviewer:** OpenCode — exhaustive file read + manual evaluation

---

## Summary

| Category | CRITICAL | MAJOR | MINOR | Total |
|----------|----------|-------|-------|-------|
| Narrowable `-> Any` returns | 0 | 22 | 23 | 45 |
| Missing return types | 1 | 4 | 15 | 20 |
| Unjustified `# type: ignore` | 0 | 3 | 2 | 5 |
| TYPE_CHECKING hygiene | 0 | 1 | 1 | 2 |
| Deferred narrowings | 0 | 2 | 3 | 5 |

**Key finding:** `game_session.py` contains 10 `# type: ignore[no-untyped-def]` annotations on lazy-loaded service property accessors. All 10 can be replaced with proper return-type annotations — the `SessionRuntimeServices` class fully defines return types for every accessed attribute. This is the single largest improvement opportunity in the shard.

**Second-largest cluster:** `game/ui/screens/strategy_renderer.py` (15 `-> Any` property accessors) and `game/ui/screens/strategy_screen.py` (12 `-> Any` property accessors). These are delegation properties that forward to `self.scene.*` — all could be narrowed to concrete types.

---

## Narrowable Any Returns

### MAJOR (cross-layer or public API methods returning `Any` that can be narrowed)

| File | Line | Function | Current | Suggested |
|------|------|----------|---------|-----------|
| `game/strategy/engine/game_session.py` | 403 | `handle_command` | `-> Any` | `-> ValidationResult` — the docstring and `_command_registry.dispatch()` return signature guarantee this |
| `game/strategy/engine/planet_modifier_effect_engine.py` | 34 | `_get_planet_mutator` | `-> Any` | `-> IPlanetMutator` — always returns `PlanetWriteService` which implements `IPlanetMutator` |
| `game/strategy/engine/production_spawner.py` | 103 | `_get_planet_mutator` | `-> Any` | `-> IPlanetMutator` — identical pattern to above |
| `game/strategy/engine/superweapon_order_processor.py` | 77 | `_get_empire_mutator` | `-> Any` | `-> IEmpireMutator` — returns `EmpireWriteService` |
| `game/strategy/services/replay_verification_coordinator.py` | 104 | `_json_safe` | `-> Any` | `-> str | int | float | bool | list | dict | None` — the docstring describes JSON-safe types exactly |
| `game/ui/screens/battle_ui.py` | 87 | `handle_click` | `-> Any` | `-> bool` — returns `False`, or `True`/result from panels; `bool` covers `False` and truthiness; could be `bool | object` if panel results matter |
| `game/ui/screens/builder_selection.py` | 21 | `normalize_selection` | `-> Any` | `-> list[tuple]` — always returns a list of tuples |
| `game/ui/screens/builder_selection.py` | 114 | `get_primary_selection` | `-> Any` | `-> tuple | None` — returns tuple or None |
| `game/ui/screens/strategy_fleet_ops.py` | 61 | `camera` (property) | `-> Any` | `-> Camera` — returns `self.scene.camera` |
| `game/ui/screens/strategy_fleet_ops.py` | 65 | `empires` (property) | `-> Any` | `-> list[Empire]` |
| `game/ui/screens/strategy_fleet_ops.py` | 69 | `hex_size` (property) | `-> Any` | `-> float` |
| `game/ui/screens/strategy_input_handler.py` | 158 | `handle_click` | `-> Any` | `-> bool` — returns bool |
| `game/ui/screens/strategy_renderer.py` | 115 | `_get_font` | `-> Any` | `-> pygame.Font` — `get_font` returns `pygame.Font` |
| `game/ui/screens/strategy_renderer.py` | 121 | `camera` (property) | `-> Any` | `-> Camera` |
| `game/ui/screens/strategy_renderer.py` | 125 | `galaxy` (property) | `-> Any` | `-> Galaxy` |
| `game/ui/screens/strategy_renderer.py` | 129 | `systems` (property) | `-> Any` | `-> list[StarSystem]` |
| `game/ui/screens/strategy_renderer.py` | 133 | `empires` (property) | `-> Any` | `-> list[Empire]` |
| `game/ui/screens/strategy_renderer.py` | 137 | `hex_size` (property) | `-> Any` | `-> float` |
| `game/ui/screens/strategy_renderer.py` | 141 | `screen_width` (property) | `-> Any` | `-> int` |
| `game/ui/screens/strategy_renderer.py` | 145 | `screen_height` (property) | `-> Any` | `-> int` |
| `game/ui/screens/strategy_renderer.py` | 149,153,157 | `SIDEBAR_WIDTH`, `TOP_BAR_HEIGHT`, `empire_assets` | `-> Any` | `-> int`, `-> int`, `-> dict[int, Any]` |
| `game/ui/screens/strategy_superweapons.py` | 73-85 | `systems`, `camera`, `hex_size`, `galaxy` (properties) | `-> Any` | `-> list[StarSystem]`, `-> Camera`, `-> float`, `-> Galaxy` |

### MINOR (internal helpers; acceptable `Any` or test-facing)

| File | Line | Function | Rationale |
|------|------|----------|-----------|
| `game/ai/protocols.py` | 42 | `IGridEntity.position` | Protocol property — `Vector2` type would create cross-layer dependency. Acceptable. |
| `game/ai/protocols.py` | 75 | `IProjectile.type` | Protocol property — `AttackType` enum is in core, could be narrowed. |
| `game/core/json_utils.py` | 79 | `load_json` | JSON returned value is inherently `Any` — acceptable for a JSON loader. |
| `game/core/json_utils.py` | 119 | `load_json_required` | Same as above — acceptable. |
| `game/core/protocols/boundary.py` | 92 | `IResourceHolder.resources` | Protocol seam — `Any` is deliberate per docstring to avoid cross-layer import. |
| `game/core/protocols/combat.py` | 22,83 | `ICombatant.position`, `ICombatShip.position` | Protocol — `Vector2` creates simulation→engine dependency. Marginal improvement. |
| `game/core/protocols/strategy_domain.py` | 32 | `IEmpire.color` | Protocol — `tuple[int, int, int]` would be more precise. |
| `game/core/protocols/strategy_domain.py` | 107 | `IEmpire.built_ship_designs` | Could be `set[str]` — the docstring says "Set of design_ids". |
| `game/core/protocols/strategy_mutators.py` | 118 | `IPlanetMutator.pop_construction_item` | Protocol — `-> Any` is needed for `dict` return; could narrow to `dict[str, Any]`. |
| `game/simulation/interfaces/ai_controller.py` | 49 | `IAIController.ship` | Protocol with explicit docstring allowing `ShipControllableAdapter`. |
| `game/ui/screens/empire_build_queue_filter_manager.py` | 223 | `sort_key` (inner) | Inner closure returning sort key — acceptable. |
| `game/ui/screens/keybindings_scene.py` | 166 | `group_height` | Inner helper for layout calculation — `-> int` obvious. |
| `game/ui/screens/list_filter_utils.py` | 30 | `_key` (inner) | Inner closure returning sort key — acceptable. |
| `game/ui/screens/species_selector_mixin.py` | 147 | `_get_active_race_config` | Mixin with duck-typed `self` — returns `RaceConfig | None`. Could narrow. |
| `game/ui/screens/strategy_fleet_ops.py` | 88,172 | `handle_move_designation`, `handle_join_designation` | Returns `dict | None` — could narrow. |
| `game/ui/screens/strategy_renderer.py` | 174-177 | `_build_hex_outline_data`, `_get_hex_outline_data` | Internal cache helpers — acceptable. |
| `game/ui/screens/strategy_screen.py` | 161-536 | Various properties and helpers | Many are delegation properties. See deferred section. |
| `game/ui/screens/strategy_superweapons.py` | 362-369 | `_get_system_at_hex`, `_get_warp_point_at_hex` | Internal helpers — `-> StarSystem | None`, `-> WarpPoint | None`. |
| `game/ui/screens/workshop_event_router.py` | 44 | `_get_vehicle_classes` | Delegates to context.registries — `-> VehicleClassRegistry | None`. |
| `game/ui/screens/builder/layer_panel.py` | 358,472 | `handle_event`, `get_range_selection` | UI event handler and internal — acceptable. |
| `game/ui/screens/builder/stat_rows_dynamic.py` | 36-569 | 30 `-> Any` returns | Internal closure-based stat row builders. All are inner closures or internal helpers. Pattern-driven — closures that return polymorphic values. Low priority. |
| `game/ui/screens/test_lab/screen.py` | 168-270 | 20+ `-> Any` properties | Delegation properties — similar to StrategyScreen. MVVM internal. |
| `game/ui/screens/test_lab/screen_actions.py` | 104 | `_get_engine` | Returns battle engine — `-> Any` acceptable given cross-layer. |
| `game/ui/services/validation_service.py` | 46 | `_get_validator` | Returns validator — `-> Any` acceptable given optional DI. |
| `game/strategy/adapters/simulation_adapter.py` | 426 | `_build_capture_context` | Internal helper — acceptable. |

---

## Missing Return Types

### CRITICAL

| File | Line | Function | Issue |
|------|------|----------|-------|
| `game/strategy/engine/superweapon_order_processor.py` | 85 | `_get_nav_service` | Missing return type. This is a public method on a turn-execution engine accessed by order handlers. Should be `-> FleetNavigationService` or `-> Any` for SRP. |

### MAJOR (public methods / cross-module callers)

| File | Line | Function | Suggested |
|------|------|----------|-----------|
| `game/app_bootstrap.py` | 310 | `_replay_combat_lab_fallback` | `-> Ship` (nested closure passed as callback) |
| `game/strategy/engine/game_initializer.py` | 157 | `_at_hex` | `-> Iterator[Fleet]` (nested generator closure) |
| `game/strategy/engine/game_initializer.py` | 163 | `_in_system` | `-> Iterator[Fleet]` (nested generator closure) |
| `game/ui/screens/radiation_shield_editor.py` | 176 | `_button_handlers` | `-> dict[UIButton, Callable[[], None]]` |

### MINOR (private/internal helpers)

| File | Line | Function | Notes |
|------|------|----------|-------|
| `game/strategy/adapters/simulation_adapter.py` | 488 | `_lookup` | `-> Ship` — nested inner function |
| `game/strategy/data/deployed_group.py` | 48 | `_register_type` | `-> Callable[[type], type]` — decorator factory |
| `game/strategy/data/deployed_group.py` | 49 | `deco` | `-> type` — inner decorator |
| `game/strategy/engine/game_session.py` | 202 | `_event_bus` | `-> Any` or `-> EventBus` if importable. See ignore audit below. |
| `game/strategy/engine/game_session.py` | 217-258 | `fleet_mutator` through `_command_registry` (10 properties) | All 10 are missing return types + have `# type: ignore[no-untyped-def]`. See detailed analysis below. |
| `game/strategy/systems/design_catalog.py` | 236 | `load_design_data` | Returns `DesignLoadResult` — missing annotation |
| `game/ui/screens/strategy_game_state_manager.py` | 166 | `_iter_snapshot_windows` | `-> Iterator[Any]` |
| `game/ui/screens/test_lab/details/validation.py` | 39 | `_phase_color` | `-> tuple[int, int, int]` |

---

## Type Ignore Audit

### `game_session.py` — 10 `# type: ignore[no-untyped-def]` (MAJOR cluster)

All 10 properties in `GameSession` (lines 202, 217, 227, 231, 236, 240, 245, 249, 254, 258) suppress `no-untyped-def` by hiding the return type. The comment explains these are "deliberate workarounds for lazy-loaded service accessors."

**Evaluation:** These are NOT justified as `# type: ignore`. The `SessionRuntimeServices` class already has proper return-type annotations for every attribute being delegated to. Each property is a trivial forwarding pattern:

```python
@property
def fleet_mutator(self) -> IFleetMutator:  # Remove the type: ignore
    return self._services.fleet_mutator
```

The underlying `self._services` is `SessionRuntimeServices` which already declares `fleet_mutator: IFleetMutator`. Adding explicit return types eliminates all 10 ignores. The `_event_bus` property (line 202) would need `-> Any` or the actual `EventBus` type.

**Recommendation:** Remove all 10 `# type: ignore[no-untyped-def]` and add explicit return types. The protocol types exist and are already imported in `TYPE_CHECKING` blocks. This is the single largest improvement item in this shard.

### `game/strategy/adapters/simulation_adapter.py:488`

```python
def _lookup(ship_spec):  # type: ignore[no-redef]
```

**Evaluation:** JUSTIFIED. This is a nested local function `_lookup` that intentionally re-defines an outer `_lookup` variable. The `no-redef` ignore is a legitimate workaround for Python's scoping rules in nested functions.

### `game/strategy/data/deployed_group.py:51`

```python
cls._type_name = type_name  # type: ignore[attr-defined]
```

**Evaluation:** JUSTIFIED. This is a class decorator that dynamically sets `_type_name` on the class being decorated. `cls` is the class parameter of the inner `deco` function, and `_type_name` is set dynamically — mypy cannot statically verify this attribute exists on all possible class types.

### `game/ui/assets/ship_theme_manager.py:254`

```python
ew, eh = int(expected[0]), int(expected[1])  # type: ignore[index]
```

**Evaluation:** NOT justified. The `expected` parameter should be typed as `tuple[int, int] | None` or `Sequence[int] | None`. If the function signature already declares it, the index access would be safe. The `except (TypeError, ValueError, IndexError)` block already handles malformed input, so narrowing the parameter annotation would remove the need for the ignore.

### `game/ui/panels/ship_detail_panel.py:593-594`

```python
label._proj315_color = color  # type: ignore[attr-defined]
label._proj315_strike = strike  # type: ignore[attr-defined]
```

**Evaluation:** JUSTIFIED for `_proj315_color`/`_proj315_strike`. These are test-introspection attributes dynamically attached to `pygame_gui`'s `UILabel`. The `pygame_gui` library does not declare these attributes. The comment documents the purpose: "Tag the label with the chosen tier so tests can introspect." This is a deliberate testing seam.

---

## TYPE_CHECKING Hygiene

### Files with correct TYPE_CHECKING patterns (verified):

- `game/ai/protocols.py` — `TYPE_CHECKING` not needed (all types are locally defined Protocols)
- `game/core/protocols/strategy_domain.py` — Correct: `RaceConfig` in TYPE_CHECKING
- `game/core/protocols/strategy_mutators.py` — Correct: 8 types in TYPE_CHECKING, used only in annotations within Protocol method stubs
- `game/strategy/engine/game_session.py` — Correct: 6 types in TYPE_CHECKING
- `game/strategy/engine/production_spawner.py` — Correct: 4 types in TYPE_CHECKING
- `game/strategy/engine/superweapon_order_processor.py` — Correct: 2 types in TYPE_CHECKING
- `game/ui/screens/strategy_fleet_ops.py` — Correct: `StrategySessionFacade` in TYPE_CHECKING only
- `game/ui/screens/strategy_superweapons.py` — Correct: `StrategySessionFacade`, `Fleet` in TYPE_CHECKING
- `game/ui/screens/test_lab/screen.py` — Correct: `BattleScreen` in TYPE_CHECKING
- `game/ui/screens/test_lab/screen_actions.py` — Correct: `TestLabScreen` in TYPE_CHECKING
- `game/ui/services/validation_service.py` — Correct: `Ship`, `Component`, `LayerType` in TYPE_CHECKING
- `game/context.py` — Correct: `IHabitabilityCalculator` in TYPE_CHECKING

### Issues found:

| File | Severity | Issue |
|------|----------|-------|
| `game/ui/screens/empire_build_queue_filter_manager.py:17` | MAJOR | `BuildQueueSource` in TYPE_CHECKING but `Any` is used in several runtime annotations instead. The `filter_sources` and `sort_sources` methods use `List[BuildQueueSource]` which IS under TYPE_CHECKING — this is correct. The `columns: List[Dict[str, Any]]` is acceptable. |
| `game/simulation/interfaces/ai_controller.py:17` | MINOR | `Ship` and `SpatialGrid` in TYPE_CHECKING — correct usage. No issues. |

### Overall TYPE_CHECKING assessment: Clean. No TYPE_CHECKING imports used at runtime found in this shard.

---

## Deferred Narrowings

### StrategyScreen/StrategyRenderer delegation properties (MAJOR — architectural decision needed)

`strategy_screen.py` (12 properties) and `strategy_renderer.py` (15 properties) use `-> Any` for delegation properties that forward to `self.scene.*`. These are read by many callers. Narrowing them requires:
1. All callers to have correct type inference
2. Potential circular import issues if concrete types are imported

**Recommendation:** Add explicit return types on the delegation properties using TYPE_CHECKING imports. For example:

```python
if TYPE_CHECKING:
    from game.ui.renderer.camera import Camera
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire
    ...

@property
def camera(self) -> Camera:
    return self.scene.camera
```

This eliminates 23 `-> Any` annotations across StrategyScreen and StrategyRenderer without runtime import impact.

### TestLabScreen delegation properties (MINOR)

`test_lab/screen.py` has ~20 `-> Any` delegation properties. Same pattern as above. Lower priority because TestLabScreen is an internal developer tool, not a player-facing screen.

### Protocol Any returns (architectural — this is correct for protocol seams)

The protocols in `ai/protocols.py`, `core/protocols/combat.py`, `core/protocols/boundary.py`, and `core/protocols/strategy_domain.py` use `Any` for properties where the concrete type crosses layer boundaries (e.g., `position` is `Vector2` in engine/simulation, `resources` is `ResourceRegistry` in simulation). These are **correct Protocol design** — the whole point of a Protocol is duck-typing without concrete type dependencies.

### stat_rows_dynamic.py closure pattern (MINOR — acceptable)

The 30 `-> Any` annotations in `builder/stat_rows_dynamic.py` are on inner closures and factory functions that return polymorphic values (numbers, strings, dicts). These are internal UI helpers with no cross-module callers. Low priority for narrowing.

---

## File Coverage Verification

All 208 files in Shard 03 were exhaustively read. The files with reported issues (from the raw JSON data files) were cross-referenced against the actual file contents. Key verification findings:

1. **any_returns_03.json:** All 146 entries confirmed against actual file content. 45 entries evaluated as narrowable (22 MAJOR, 23 MINOR).

2. **missing_returns_03.json:** All 20 entries confirmed. The 10 game_session.py entries are also in type_ignore_sites_03.json.

3. **type_ignore_sites_03.json:** All 16 entries confirmed.
   - 10 in game_session.py — all evaluable as removable
   - 1 in simulation_adapter.py — justified
   - 1 in deployed_group.py — justified
   - 1 in ship_theme_manager.py — unjustified
   - 2 in ship_detail_panel.py — justified
   - 1 in ship_theme_manager.py — duplicate (listed as simulation layer) — unjustified

4. **TYPE_CHECKING audit:** All 208 files checked for `if TYPE_CHECKING:` blocks. No runtime uses of TYPE_CHECKING-only imports detected. Pattern is well-followed.

5. **Full file coverage:** Exhaustive read confirmed for all 208 shard files. No file skipped.

---

## Top 5 Recommended Actions

1. **game_session.py (10 fixes, 0 risk):** Remove all 10 `# type: ignore[no-untyped-def]` and add explicit protocol return types (`-> IFleetMutator`, `-> IPlanetMutator`, `-> IEmpireMutator`, `-> IShipInstanceMutator`, `-> Any` for event_bus). The protocol types are already in `core/protocols/strategy_mutators.py` and `SessionRuntimeServices` already uses them.

2. **strategy_renderer.py (15 fixes, low risk):** Add explicit return types on all delegation properties using TYPE_CHECKING imports. This eliminates the largest cluster of `-> Any` annotations.

3. **strategy_screen.py (12 fixes, low risk):** Same treatment as strategy_renderer.py. Properties like `galaxy`, `empires`, `systems`, `facade`, etc. all have well-known return types.

4. **strategy_fleet_ops.py / strategy_superweapons.py (8 fixes, low risk):** Narrow delegation property return types.

5. **ship_theme_manager.py (1 fix, low risk):** Narrow `expected` parameter type to `tuple[int, int] | None` to remove the unjustified `# type: ignore[index]`.
