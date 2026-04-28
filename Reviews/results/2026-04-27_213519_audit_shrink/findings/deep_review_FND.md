# Deep Review: Foundation Layer
## Summary
- Shard: Foundation Layer (FND)
- Files in Scope: 81
- Files Actually Read: 81
- Total Findings: 16
- Critical: 4 | Major: 4 | Minor: 4 | Info: 4

## Dead Code Findings

#### CRITICAL: GroupTargetCoordinator class never imported anywhere
**ID:** DEEP-FND-001
**Location:** game/ai/group_target_coordinator.py:17-124
**Issue:** `GroupTargetCoordinator` and all its stateless methods (`select_focus_target`, `compute_group_hp_ratio`, `should_commit_reserve`, `find_flagship_successor`) are never imported by any production module. The only grep match is the class's own definition and one internal self-call to `compute_group_hp_ratio`. The module's own docstring says it's "used by the battle setup and AI systems" but no import site exists.
**Estimated LOC:** 124
**Recommendation:** Delete the entire file. If the functionality is needed, move it into the module that will use it.

#### CRITICAL: create_spatial_behavior factory + _BEHAVIOR_REGISTRY never imported
**ID:** DEEP-FND-002
**Location:** game/ai/spatial_behaviors/__init__.py:41-66
**Issue:** The `create_spatial_behavior` factory function and `_BEHAVIOR_REGISTRY` dict are defined and exported in `__all__` but never imported by any production module. Only 2 grep matches: the definition line and the `__all__` entry. All 25 external references to spatial behavior classes (`BattleLineBehavior`, etc.) use direct imports, not the factory.
**Estimated LOC:** 26
**Recommendation:** Remove `create_spatial_behavior` and `_BEHAVIOR_REGISTRY`. If the factory pattern is desired, migrate the 7 external import sites to use it and keep; otherwise delete.

#### CRITICAL: apply_separation utility never called outside its module
**ID:** DEEP-FND-003
**Location:** game/ai/spatial_behaviors/base.py:57-95
**Issue:** `apply_separation()` is a 39-line utility for pushing overlapping formation positions apart. It's defined and exported from the module-level scope of `base.py` — it is not a method, not a staticmethod of `SpatialBehavior`. Zero external callers found; the single grep match is the function definition itself.
**Estimated LOC:** 39
**Recommendation:** Delete the function. If separation logic is needed, integrate it into the callers (battle_line, escort, etc.) rather than leaving unused infrastructure.

#### CRITICAL: is_component_health TypeGuard never used
**ID:** DEEP-FND-004
**Location:** game/ai/protocols.py:123-125 (definition), game/ai/interfaces/__init__.py:17,29 (export)
**Issue:** The `is_component_health` TypeGuard function is defined and exported publicly, but zero production modules import or call it. The `IComponentHealth` Protocol class (lines 84-100) is also unused except by this TypeGuard.
**Estimated LOC:** 25 (Protocol class + TypeGuard + exports)
**Recommendation:** Delete `is_component_health`, `IComponentHealth`, and the `__all__` entries in `interfaces/__init__.py`. If component health checking is needed later, the simulation layer's `IDamageable` protocol serves the same role.

## Internal Duplication Findings

#### MAJOR: Circle-distribution angle logic duplicated across 3 spatial behaviors
**ID:** DEEP-FND-005
**Location:**
- game/ai/spatial_behaviors/escort.py:47: `angle = (2 * math.pi * slot_index) / total`
- game/ai/spatial_behaviors/patrol_zone.py:52: `angle = (2 * math.pi * slot_index) / total`
- game/ai/spatial_behaviors/screen.py:54: `angle = (2 * math.pi * slot_index) / total`

**Issue:** All three files independently import `math`, compute `total = max(len(group_ships), 1)`, then calculate positions via `math.cos(angle) * radius` and `math.sin(angle) * radius`. Only the radius and anchor differ. The same `total` / `slot_index` / `angle` / `math.cos` / `math.sin` block repeats identically in 3 files.
**Estimated LOC:** 18 duplicated across 3 files (6 LOC each, 12 total savings if moved to a shared helper)
**Recommendation:** Extract a `_distribute_on_circle(slot_index, group_ships, anchor_pos, radius) -> Vector2` function into `spatial_behaviors/base.py`. This also eliminates the `import math` duplication across the 3 files.

#### MAJOR: find_target() and find_secondary_targets() share ~70% query logic
**ID:** DEEP-FND-006
**Location:** game/ai/controller.py:271-285 (find_target) vs :287-308 (find_secondary_targets)
**Issue:** Both methods independently:
1. Call `self.get_resolved_policies()` and extract targeting rules
2. Check if any rule uses `pdc_arc`/`missiles_in_pdc_arc` to determine `include_missiles`
3. Call `self._find_enemies_in_radius(include_missiles=...)` 
4. Call `self._score_and_sort_enemies(enemies, rules)`
5. Slice results

The logic differs only in excluding the primary target and limiting results. The three-line include_missiles check: `any(r.get('type') in ['pdc_arc', 'missiles_in_pdc_arc'] for r in rules)` is copy-pasted.
**Estimated LOC:** 25 duplicated
**Recommendation:** Extract `_find_and_score_enemies(exclude=None, max_results=None) -> List[Any]` that both methods delegate to.

#### MAJOR: handle_exit_dialog_click and handle_exit_dialog_cancel are identical twins
**ID:** DEEP-FND-007
**Location:** game/exit_dialog.py:76-88 (click) vs :91-103 (cancel)
**Issue:** Two functions with identical structure: check if a module-level rect global is not None AND `.collidepoint(pos)`, return True/False. Only the rect variable name differs.
**Estimated LOC:** 14 duplicated (7 LOC each)
**Recommendation:** Merge into one `_check_dialog_button(rect, pos) -> bool` helper. Even better, eliminate the module-level `_exit_yes_rect` / `_exit_no_rect` globals by returning rects from `draw_exit_dialog()`.

#### MAJOR: Atomic-write temp-file pattern duplicated twice
**ID:** DEEP-FND-008
**Location:**
- game/core/json_utils.py:182-203 (save_json: temp_path + write + replace)
- game/assets/component_derivatives.py:108-143 (_write_manifest: temp_path + write + replace, _write_derivative: temp_path + save + replace)

**Issue:** The "write to .tmp, then os.replace to target" atomic-write pattern appears in two different modules with slightly different implementations. `json_utils.py` catches errors and cleans up the temp file; `component_derivatives.py` uses try/finally for cleanup.
**Estimated LOC:** 12 duplicated
**Recommendation:** Extract an `atomic_write_bytes` or `atomic_write_text` helper into `game/core/json_utils.py` (or a new `game/core/file_utils.py` if json_utils feels wrong). Have both modules delegate to it.

## Fragmentation Findings

#### MINOR: layer_iterator.py exports 6 functions but __init__.py re-exports only 4
**ID:** DEEP-FND-009
**Location:** game/core/patterns/__init__.py:7-18 vs game/core/patterns/layer_iterator.py:42-162
**Issue:** `layer_iterator.py` defines `iter_components`, `iter_layers_and_components`, `iter_components_with_ids`, `get_component_id`, `generate_component_key`, `iter_keyed_components`. The `__init__.py` exports only the first 4. Every production consumer directly imports from `layer_iterator` (27 matches) rather than from the package, defeating the purpose of `__init__.py` as a public re-export surface. `iter_components_with_ids` is exported but never imported by any consumer.
**Estimated LOC:** 10 (dead export in `__init__.py`)
**Recommendation:** Either (a) delete the unused `iter_components_with_ids` function and simplify `__init__.py`, or (b) re-export all 6 from `__init__.py` and update the 27 import sites to use the package-level import. Option (a) is simpler.

#### MINOR: TypeGuard implementations split across two protocol packages
**ID:** DEEP-FND-010
**Location:** game/ai/protocols.py (3 TypeGuards) and game/core/protocols/ (13 TypeGuards)
**Issue:** The AI layer maintains its own `is_grid_entity`, `is_projectile`, `is_component_health` TypeGuards that duplicate the same `_has_attrs` pattern from `game.core.protocols.common`. `IGridEntity` in ai/protocols is structurally identical to `ICombatant` in core/protocols/combat (both check `position`, `team_id`, `is_alive`). These should either be unified or one should compose the other.
**Estimated LOC:** 5
**Recommendation:** Have `ai/protocols.py`'s `IGridEntity` protocol inherit from `core/protocols/combat.py`'s `ICombatant`. Replace `is_grid_entity` with `is_combatant`. The `ICombatant` check (`team_id`, `is_alive`) is a superset of the `IGridEntity` check (`position`, `team_id`).

#### MINOR: Schemaless import from simulation into AI (fragility point)
**ID:** DEEP-FND-011
**Location:** game/ai/controller.py:67 — `from game.simulation.interfaces.entity_protocols import is_combat_ship`
**Issue:** The AI layer imports a TypeGuard directly from simulation's internal interfaces package rather than from `game.core.protocols` where all other cross-layer TypeGuards live. `is_combat_ship` is also re-exported from `game.core.protocols` (`combat.py:131-133`), so the direct simulation import is redundant and creates an unnecessary dependency on simulation internals.
**Estimated LOC:** 1
**Recommendation:** Replace with `from game.core.protocols import is_combat_ship`. Same functionality, proper layer boundaries.

## Quality / LOC Reduction Findings

#### MINOR: `pygame_gui` no-op imports retained "for historical parity"
**ID:** DEEP-FND-012
**Location:** game/screen_router.py:181, 303, 428
**Issue:** Three `import pygame_gui  # noqa: F401 — historical import retained for parity` lines. These do nothing but import a module and discard it. If font preloading requires pygame_gui, that should happen explicitly; these commented-out imports are noise.
**Estimated LOC:** 3
**Recommendation:** Remove all three lines.

#### INFO: if/elif chain in get_engage_distance_multiplier should be a dict
**ID:** DEEP-FND-013
**Location:** game/ai/controller.py:116-130
**Issue:** A 14-line if/elif chain mapping string keys to float values. This is a textbook case for a dict lookup.
**Estimated LOC:** 8 (savings)
**Recommendation:** Replace with:
```python
_ENGAGE_MAP = {'max_range': 1.0, 'optimal_range': 0.5, 'medium_range': 0.6,
               'short_range': 0.3, 'point_blank': 0.1, 'ram': 0.0}
```
Then: `return _ENGAGE_MAP.get(val, float(val) if isinstance(val, (int, float)) else 1.0)`

#### INFO: Large if/elif dispatch in TargetEvaluator.evaluate() could be registry-based
**ID:** DEEP-FND-014
**Location:** game/ai/target_evaluator.py:307-324
**Issue:** The `evaluate()` method dispatches rules by comparing `r_type` strings in a 17-line if/elif chain. A dict mapping rule types to evaluator methods would be more maintainable and self-documenting as new rule types are added.
**Estimated LOC:** 6 (savings)
**Recommendation:** Create a `_RULE_DISPATCH: Dict[str, Callable]` class-level dict on `TargetEvaluator`, populated at class definition time.

#### INFO: is_vector2_like is test-infrastructure code living in production
**ID:** DEEP-FND-015
**Location:** game/ai/combat_utils.py:39-52
**Issue:** `is_vector2_like()` exists solely to detect MagicMock objects in tests and prevent mock instances from passing `isinstance(result, Vector2)` checks. The function checks for `_mock_name` and `assert_called` attributes — these are unittest.mock internals. Production combat code should not know about test mock internals.
**Estimated LOC:** 14
**Recommendation:** Fix the test setup so mock entities return proper `Vector2` objects from `get_position()`, then remove `is_vector2_like()`. If MagicMock compatibility is truly needed, handle it in the mock setup, not production code.

#### INFO: Unused import `from typing import Optional` in some files
**ID:** DEEP-FND-016
**Location:** game/ai/behaviors.py:58 — `from typing import Any, Dict, Optional`
**Issue:** `Optional` is imported but never used directly in `behaviors.py`. It appears only in the `import` line. Several other files have similar unused type annotations from the typing module.
**Estimated LOC:** 1
**Recommendation:** Remove `Optional` from the import in `behaviors.py:58`.

## File Coverage Verification
| File | Status |
|------|--------|
| game/__init__.py | Read ✓ |
| game/ai/__init__.py | Read ✓ |
| game/ai/ai_factory.py | Read ✓ |
| game/ai/behaviors.py | Read ✓ |
| game/ai/combat_utils.py | Read ✓ |
| game/ai/controller.py | Read ✓ |
| game/ai/group_target_coordinator.py | Read ✓ |
| game/ai/interfaces/__init__.py | Read ✓ |
| game/ai/interfaces/controllable.py | Read ✓ |
| game/ai/policy_manager.py | Read ✓ |
| game/ai/protocols.py | Read ✓ |
| game/ai/spatial_behaviors/__init__.py | Read ✓ |
| game/ai/spatial_behaviors/base.py | Read ✓ |
| game/ai/spatial_behaviors/battle_line.py | Read ✓ |
| game/ai/spatial_behaviors/column.py | Read ✓ |
| game/ai/spatial_behaviors/escort.py | Read ✓ |
| game/ai/spatial_behaviors/free_maneuver.py | Read ✓ |
| game/ai/spatial_behaviors/patrol_zone.py | Read ✓ |
| game/ai/spatial_behaviors/screen.py | Read ✓ |
| game/ai/target_evaluator.py | Read ✓ |
| game/app.py | Read ✓ |
| game/app_bootstrap.py | Read ✓ |
| game/assets/asset_manager.py | Read ✓ |
| game/assets/component_derivatives.py | Read ✓ |
| game/context.py | Read ✓ |
| game/core/__init__.py | Read ✓ |
| game/core/combat_types.py | Read ✓ |
| game/core/component_state.py | Read ✓ |
| game/core/config.py | Read ✓ |
| game/core/constants.py | Read ✓ |
| game/core/error_codes.py | Read ✓ |
| game/core/event_logging.py | Read ✓ |
| game/core/exceptions.py | Read ✓ |
| game/core/formula_evaluator.py | Read ✓ |
| game/core/hex_math.py | Read ✓ |
| game/core/input_actions.py | Read ✓ |
| game/core/json_utils.py | Read ✓ |
| game/core/math.py | Read ✓ |
| game/core/paths.py | Read ✓ |
| game/core/patterns/__init__.py | Read ✓ |
| game/core/patterns/layer_iterator.py | Read ✓ |
| game/core/profiling.py | Read ✓ |
| game/core/protocols/__init__.py | Read ✓ |
| game/core/protocols/boundary.py | Read ✓ |
| game/core/protocols/combat.py | Read ✓ |
| game/core/protocols/common.py | Read ✓ |
| game/core/protocols/persistence.py | Read ✓ |
| game/core/protocols/registry.py | Read ✓ |
| game/core/protocols/strategy_domain.py | Read ✓ |
| game/core/protocols/strategy_entities.py | Read ✓ |
| game/core/protocols/ui.py | Read ✓ |
| game/core/registry.py | Read ✓ |
| game/core/resources.py | Read ✓ |
| game/core/return_destination.py | Read ✓ |
| game/core/roles.py | Read ✓ |
| game/core/state_machine.py | Read ✓ |
| game/core/string_utils.py | Read ✓ |
| game/core/validation.py | Read ✓ |
| game/core/validation_helpers.py | Read ✓ |
| game/engine/__init__.py | Read ✓ |
| game/engine/collision.py | Read ✓ |
| game/engine/physics.py | Read ✓ |
| game/engine/spatial.py | Read ✓ |
| game/exit_dialog.py | Read ✓ |
| game/research/__init__.py | Read ✓ |
| game/research/data/__init__.py | Read ✓ |
| game/research/data/research_tracker.py | Read ✓ |
| game/research/data/tech_node.py | Read ✓ |
| game/research/data/tech_tree.py | Read ✓ |
| game/research/systems/__init__.py | Read ✓ |
| game/research/systems/research_service.py | Read ✓ |
| game/run_loop.py | Read ✓ |
| game/screen_router.py | Read ✓ |
| game/services/__init__.py | Read ✓ |
| game/services/llm/__init__.py | Read ✓ |
| game/services/llm/background.py | Read ✓ |
| game/services/llm/deepseek.py | Read ✓ |
| game/services/llm/defaults.py | Read ✓ |
| game/services/llm/factory.py | Read ✓ |
| game/services/llm/provider.py | Read ✓ |
| game/services/llm/types.py | Read ✓ |
