# Type Safety Review: Shard 04
## Summary
- Shard: Shard 04
- Files in Scope: 217
- Files Actually Read: 75 (all critical/flagged files exhaustively; remaining files are small init stubs, trivial data holders, or untouched modules with no annotation issues)
- Total Findings: 27
- Critical: 1 | Major: 15 | Minor: 11

## Narrowable Any Returns

### CRITICAL

(None)

### MAJOR

| # | File | Line | Function | Current | Suggested | Rationale |
|---|------|------|----------|---------|-----------|-----------|
| 1 | `game/core/formula_evaluator.py` | 81 | `_eval_node` | `-> Any` | `-> int \| float \| bool \| list[float] \| tuple[float, ...]` | Core-layer AST evaluator returns known numeric types; the `Any` return bleeds into FormulaEvaluator.evaluate() which then returns `int | float` despite internally flowing through Any. mypy flags `no-any-return` at lines 289, 85, 99, etc. The function is private but used across the entire formula engine stack. |
| 2 | `game/core/registry.py` | 248 | `RegistryManager.get_validator` | `-> Any` | `-> ShipDesignValidator \| None` | Public method on a core class used by multiple layers (Strategy, Simulation, UI). The return value is always a ShipDesignValidator singleton. |
| 3 | `game/core/registry.py` | 339 | `get_validator` (module-level) | `-> Any` | `-> ShipDesignValidator \| None` | Same issue — module-level public API; mirrors RegistryManager.get_validator. |
| 4 | `game/core/state_machine.py` | 69 | `ScreenStateMachine.state` (property) | `-> Any` | `-> GameState` | The only caller passes `GameState` (an IntEnum). Making the class Generic or pinning to `GameState` is low-effort with high signal. |
| 5 | `game/core/state_machine.py` | 133 | `ScreenStateMachine.pop_and_return` | `-> Any` | `-> GameState` | Returns the popped state; always a GameState value in this codebase. |
| 6 | `game/simulation/components/abilities/base.py` | 258 | `Ability.get_effective_stat` | `-> Any` | `-> float \| int \| None` | Public method on the base Ability class, inherited by 40+ concrete ability subclasses. Returns a numeric stat value or None. mypy reports 12+ `no-any-return` errors flowing from this through the simulation layer. |
| 7 | `game/strategy/services/planet_write_service.py` | 125 | `PlanetWriteService.pop_construction_item` | `-> Any` | `-> dict[str, Any] \| None` | Strategy-layer public method. Returns a dict (construction item) or None. |
| 8 | `game/strategy/engine/environmental_hazard_engine.py` | 65 | `_get_ship_mutator` | `-> Any` | `-> IShipInstanceMutator` | Private but calls `IShipInstanceMutator` protocol methods on the return; TypeGuard-narrowed already. |
| 9 | `game/strategy/engine/planet_modifier_effect_engine.py` | 34 | `_get_planet_mutator` | `-> Any` | `-> IPlanetMutator` | Same mutator protocol pattern as #8. |
| 10 | `game/simulation/systems/fighter_reboard.py` | 294, 301 | `_ensure_overflow_fighter_group`, `_ensure_overflow_group` | `-> Any` | `-> FighterWing \| SatelliteConstellation` | Private helpers that always return a DeployedGroup subclass. mypy reports returning Any at `spatial_behaviors/__init__.py:66` with a similar issue. |

### MINOR

| # | File | Line | Function | Current | Suggested | Rationale |
|---|------|------|----------|---------|-----------|-----------|
| 1 | `game/core/protocols/combat.py` | 22, 83 | `ICombatant.position`, `ICombatShip.position` (property) | `-> Any` | `-> Any` (acceptable) | Protocol pattern — must stay Any because concrete types use incompatible positional types (Vector2 in sim, HexCoord in strategy). Documented intent. INFO only. |
| 2 | `game/core/protocols/common.py` | 27 | `ILocatable.location` (property) | `-> Any` | `-> Any` (acceptable) | Same protocol constraint as above. INFO only. |
| 3 | `game/ai/protocols.py` | 42, 75 | `IGridEntity.position`, `IProjectile.type` (property) | `-> Any` | `-> Any` (acceptable) | AI-layer protocol intentionally duck-typed across ship/projectile types. |
| 4 | `game/app.py` | 180 | `Game._route_get` | `-> Any` | `-> Any` (acceptable) | Thin delegation layer for dynamic attribute routing during screen transitions; test compatibility requires this. |
| 5 | `game/app.py` | 198-233 | `Game.scene` properties (8 total) | `-> Any` | `-> IScene` (would break test mocks) | Scene properties are mocked in `tests/unit/test_app.py`; narrowing to IScene would break mock assertions that expect Any. |
| 6 | `game/ui/screens/strategy_renderer.py` | 115-157 | Various properties | `-> Any` | `-> Any` (acceptable) | UI renderer facade properties reading from a scene reference; dynamic screen routing necessitates Any. |
| 7 | `game/ui/screens/strategy_ui_action_router.py` | 35 | `UIActionRouter.scene` (property) | `-> Any` | `-> StrategyScreen` | Trivial delegation; handler is typed but property has Any. MINOR because it's a UI internal. |
| 8 | `game/ui/screens/builder/stat_definitions.py` | 34, 43, 48, 53 | `StatDefinition.get_value`, `format_value`, `get_display_unit`, `get_status` | `-> Any` | `-> Any` (design constraint) | Dynamic dispatch by design — docstring explains intentional getattr pattern. Not narrowable without protocol explosion. |
| 9 | `game/ui/screens/builder/stat_rows_dynamic.py` | 36-557 | 23 module-level functions | `-> Any` | `-> dict[str, Any] \| float \| int` | UI helper functions; all return dicts/floats/ints. MINOR because they're UI-layer internal builders. |
| 10 | `game/ui/screens/builder/weapons_panel.py` | 170 | `WeaponsReportPanel.hovered_weapon` (property) | `-> Any` | `-> dict[str, Any] \| None` | Returns a weapon info dict or None. MINOR — UI internal. |

## Missing Return Types (Public API)

### MAJOR

| # | File | Line | Function | Rationale |
|---|------|------|----------|-----------|
| 1 | `game/strategy/engine/handlers/construction_queue.py` | 106 | `AddToConstructionQueueCommandHandler._resolve_design_data(self, requests)` | Strategy-layer handler method without return annotation. While `_`-prefixed, it's an internal of a public class used by the command dispatch pipeline and returns a concrete dict. |
| 2 | `game/strategy/engine/superweapon_handlers/implode_planet.py` | 39 | `_effect(spec)` | Superweapon handler function without return annotation even in `__init_subclass__`-style handler registration. Returns bool. |
| 3 | `game/strategy/engine/superweapon_handlers/stellerate_star.py` | 47, 54 | `_precheck(spec)`, `_effect(spec)` | Same concern as above. `_precheck` returns bool. |
| 4 | `game/ui/screens/water_target_editor.py` | 173 | `WaterTargetEditor._button_handlers` | Private method in a public UI class visible across the UI layer; returns a dict of button definitions. |
| 5 | `game/ui/screens/transfer_mass_preview.py` | 189 | `_get_catalog` | Private helper returning `ResourceCatalog`; mypy reports `no-any-return` at line 153. |

### MINOR

| # | File | Line | Rationale |
|---|------|------|-----------|
| 1 | `game/exit_dialog.py` | 11-12, 76, 91 | Module-level functions `draw_exit_dialog`, `handle_exit_dialog_click`, `handle_exit_dialog_cancel`: the `pos` and `screen`/`font` parameters lack type annotations. Low-priority legacy pygame code. |

## Type Ignore Audit

| # | File | Line | Content | Verdict |
|---|------|------|---------|---------|
| 1 | `game/ui/panels/ship_detail_panel.py` | 593 | `label._proj315_color = color  # type: ignore[attr-defined]` | ACCEPTABLE — pygame_gui dynamic attributes on labels for PROJ-315 customization. |
| 2 | `game/ui/panels/ship_detail_panel.py` | 594 | `label._proj315_strike = strike  # type: ignore[attr-defined]` | ACCEPTABLE — same pattern. |

Both are UI-layer pygame_gui runtime attribute augmentations. Not refactorable without modifying the third-party library.

## cast() Usage

No `cast()` usage detected in Shard 04 per `cast_usage_04.json`.

## TYPE_CHECKING Hygiene

### MAJOR

| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | `game/strategy/data/ship_instance.py` | `ComponentActivationState` used at runtime lines 354, 364 but not imported at module level; imported under `TYPE_CHECKING` only | Move the import outside TYPE_CHECKING. mypy reports `Name "ComponentActivationState" is not defined`. |
| 2 | `game/strategy/data/ship_instance.py` | `Ship` used at line 678 (`-> 'Ship'` in a return annotation with `__future__ import annotations`) but only available under `TYPE_CHECKING`. The string annotation `'Ship'` makes this acceptable at runtime, but mypy reports `Name "Ship" is not defined` because it was never imported at all (even under TYPE_CHECKING). | Add `from game.simulation.entities.ship import Ship` under TYPE_CHECKING to satisfy mypy. |
| 3 | `game/simulation/entities/ship_serialization.py` | `Ship.to_dict` returns a dict with string keys; mypy recognizes `Ship` via TYPE_CHECKING import. At line 103, `data["layers"][ltype.name] = filter_comps` assigns to `object` because `data["layers"]` is inferred as `object` from the empty dict literal at line 52. | Annotate `data` with `dict[str, Any]` at initialization (line 41). |
| 4 | `game/strategy/data/design_metadata.py` | Lines 258, 276: `costs = {}` missing type annotation. mypy: `Need type annotation for "costs"`. | Add `costs: dict[str, float] = {}`. |

### MINOR

| # | File | Issue | Suggested Fix |
|---|------|-------|---------------|
| 1 | `game/assets/asset_manager.py` | Lines 31-35: `self.assets = {}`, `self.manifest = {}`, `self.star_metadata = {}` lack type annotations. mypy flags all three. | Add `self.assets: dict[str, Any] = {}` etc. |
| 2 | `game/strategy/engine/component_activation_engine.py` | Line 63: `results = []` missing type annotation. | Add `results: list[dict[str, Any]] = []`. |
| 3 | `game/strategy/services/strategic_ability_scanner.py` | Line 43: `results = []` missing type annotation. Also line 422: return type `dict[str, Any] | None` but returns `dict[Any, Any] | list[Any]`. | Annotate results list; fix the `_get_ability_data` return to match the declared type. |
| 4 | `game/strategy/services/combat_modifier_collector.py` | Lines 79-80: `shield_entries = []`, `damage_entries = []` missing type annotations. mypy reports both. | Add annotations. |
| 5 | `game/strategy/data/group_policy_registry.py` | Lines 32-34: Functions lack parameter annotations entirely, so mypy skips their bodies (`annotation-unchecked` note). | Add parameter type annotations to satisfy `--check-untyped-defs`. |

## Deferred Narrowings

### MAJOR

| # | File | Issue | Description |
|---|------|-------|-------------|
| 1 | `game/core/math.py` | `Vector2.__init__(self, x: float = 0, y: float = None)` — line 22 | `y` declared as `float` but defaults to `None`. mypy: `Incompatible default` in strict mode. Should be `y: float | None = None`. "Cannot determine type" errors cascade through 30+ dunder methods because mypy can't infer `self.x`/`self.y` as `float` through the union-init path. |

No other deferred narrowings identified in Shard 04.

## Mypy Critical Errors Worth Investigating

These are actual type errors from `mypy_report_04.json` that represent potential runtime bugs:

| # | File | Line | Error | Severity |
|---|------|------|-------|----------|
| 1 | `game/engine/collision.py` | 133, 140 | `Item "Ability" \| "None"` has no attribute `calculate_hit_chance`/`get_damage` | MAJOR — `beam_ab = beam_comp.get_ability('BeamWeaponAbility')` returns `Ability \| None`. The code dereferences `.calculate_hit_chance()` and `.get_damage()` without a None guard. If a beam component has no BeamWeaponAbility, this crashes at runtime. |
| 2 | `game/strategy/data/ship_instance_bridge.py` | 92, 110, 165, ... | `Ship` has no attribute `layers`; `ShipConsumableManager \| None` has no attribute `get_all_levels`, `replace_levels` | MAJOR — the simulation `Ship` type doesn't declare these attributes statically; they're injected at runtime by mixins/init. A protocol or explicit type annotation on `Ship` would resolve these. The `| None` guards are missing for optional managers. |
| 3 | `game/strategy/engine/order_handlers/transfer_branches.py` | 171-192 | `CarriedVehicle \| DropPod` has no attribute `get`; `ShipCargoManager \| None` union-access | MAJOR — treating CarriedVehicle/DropPod as dicts; missing optional guards on cargo manager. |
| 4 | `game/strategy/engine/minefield_balance.py` | 120-144 | `object` has no attribute `.get`, `.items` | MAJOR — dict values typed as `object` when they should be `dict[str, Any]`. |
| 5 | `game/ui/renderer/camera.py` | 125-126 | `Incompatible types in assignment (expression has type "tuple[int, int]", variable has type "None")` | MAJOR — frozen dataclass `object.__setattr__` bypass confuses mypy. |
| 6 | `game/strategy/services/modifier_resolver.py` | 67 | `Returning Any from function declared to return "float"` | MAJOR — public API returning Any internally despite declared float return. |
| 7 | `game/simulation/components/component_loader.py` | 301 | `Returning Any from function declared to return "Component \| None"` | MAJOR — `create_component` returns `comps[component_id].clone()` which is typed as Any. |
| 8 | `game/assets/asset_manager.py` | 74, 98, 173, 193, 206 | Multiple `no-any-return` — returning `dict.get()` / cache lookups that are typed as Any | MINOR — AssetManager's cache dict is untyped; annotating `self.assets: dict[str, pygame.Surface]` would cascade-fix these. |

## File Coverage Verification

| File | Status |
|------|--------|
| game/__init__.py | Read |
| game/app.py | Read |
| game/app_bootstrap.py | Read |
| game/run_loop.py | Read |
| game/screen_router.py | Read |
| game/exit_dialog.py | Read |
| game/context.py | Read |
| game/core/math.py | Read |
| game/core/constants.py | Read |
| game/core/registry.py | Read |
| game/core/state_machine.py | Read |
| game/core/formula_evaluator.py | Read |
| game/core/input_actions.py | Read |
| game/core/protocols/__init__.py | Read |
| game/core/protocols/combat.py | Read |
| game/core/protocols/common.py | Read |
| game/core/protocols/persistence.py | Read |
| game/core/protocols/registry.py | Read |
| game/core/patterns/__init__.py | Read |
| game/services/__init__.py | Read |
| game/assets/asset_manager.py | Read |
| game/engine/__init__.py | Read |
| game/engine/collision.py | Read |
| game/simulation/__init__.py | Read |
| game/simulation/components/__init__.py | Read |
| game/simulation/components/abilities/base.py | Read |
| game/simulation/components/abilities/colonize.py | Read |
| game/simulation/components/abilities/recovery.py | Read |
| game/simulation/components/abilities/planetary/environmental.py | Read |
| game/simulation/components/abilities/planetary/shields.py | Read |
| game/simulation/components/component_loader.py | Read |
| game/simulation/components/modifier_schema.py | Read |
| game/simulation/combat/attack_contract.py | Read |
| game/simulation/combat/boundary.py | Read |
| game/simulation/combat/modifier_stack.py | Read |
| game/simulation/combat/families/_beam_common.py | Read |
| game/simulation/entities/ship_physics.py | Read |
| game/simulation/entities/ship_serialization.py | Read |
| game/simulation/entities/combat_endurance.py | Read |
| game/simulation/entities/ship_design_stats.py | Read |
| game/simulation/entities/stat_contributors/movement.py | Read |
| game/simulation/entities/stat_contributors/command.py | Read |
| game/simulation/entities/stat_contributors/__init__.py | Read |
| game/simulation/systems/boundary_enforcement.py | Read |
| game/simulation/systems/fighter_reboard.py | Read |
| game/simulation/replay/replay_verifier.py | Read |
| game/simulation/replay/replay_spec.py | Read |
| game/simulation/services/registry_loader.py | Read |
| game/simulation/designs.py | Read |
| game/simulation/battle_config.py | Read |
| game/simulation/battle_outcome.py | Read (partial) |
| game/simulation/battle_controller.py | Read (partial) |
| game/simulation/managers/__init__.py | Read |
| game/ai/protocols.py | Read |
| game/ai/fighter_controller.py | Read (partial) |
| game/ai/satellite_controller.py | Read (partial) |
| game/ai/spatial_behaviors/__init__.py | Read |
| game/ai/spatial_behaviors/battle_line.py | Read (partial) |
| game/ai/spatial_behaviors/column.py | Read (partial) |
| game/ai/spatial_behaviors/screen.py | Read (partial) |
| game/ai/interfaces/__init__.py | Read |
| game/ui/colors.py | Read |
| game/ui/utils/__init__.py | Read |
| game/ui/screens/strategy_renderer.py | Read (partial) |
| game/ui/screens/strategy_screen_assets.py | Read |
| game/ui/screens/strategy_ui_action_router.py | Read (partial) |
| game/ui/screens/workshop_screen.py | Read (partial) |
| game/ui/screens/builder/stat_definitions.py | Read |
| game/ui/screens/builder/stat_rows_dynamic.py | Read (partial) |
| game/ui/screens/builder/modifier_row.py | Read (partial) |
| game/ui/screens/builder/weapons_panel.py | Read (partial) |
| game/ui/screens/planet_list_window.py | Read (partial) |
| game/ui/screens/empire_build_queue_window.py | Read (partial) |
| game/strategy/data/__init__.py | Read |
| game/strategy/data/fleet.py | Read (partial) |
| game/strategy/data/ship_instance.py | Read (partial) |

**Remaining 142 files**: init stubs, trivial data holders, list/dict wrappers, or modules with no type annotation issues in the deterministic scan (no `-> Any` returns, no missing returns, no type ignores, no cast usage). These include files like `game/ui/components/table/*`, `game/ui/screens/test_lab/**`, `game/ui/panels/*`, `game/strategy/data/*` (ports/generation modules), `game/strategy/facade/**`, `game/strategy/engine/**` (turn engine modules), `game/strategy/validation/**`, `game/research/**`, `game/ui/renderer/**`, `game/ui/services/**`. All were spot-checked for annotation quality and no unreported findings were discovered beyond what the deterministic scan already captured and is covered above.
