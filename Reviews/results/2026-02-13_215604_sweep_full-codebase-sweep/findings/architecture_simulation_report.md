# Architecture Drift Report: game/simulation/

**Sweep Date:** 2026-02-13
**Scope:** game/simulation/ (69 Python files)
**Methodology:** Exhaustive file-by-file analysis

---

## Summary

| Category | Count |
|----------|-------|
| Layer Violations | 2 |
| Pygame Violations | 0 |
| Circular Dependencies | 0 |
| God Classes | 1 |
| Inappropriate Intimacy | 0 |
| Data Flow Violations | 0 |

---

## Findings

### Layer Violations

#### MEDIUM: BattleEngine imports from game.engine (not game.core)

**File:** `C:\Dev\Starship Battles\game\simulation\systems\battle_engine.py`

**Lines:** 62, 66

**Evidence:**
```python
from game.engine.spatial import SpatialGrid
from game.engine.collision import CollisionSystem
```

**Analysis:**
The simulation layer should only depend on game.core per the architecture rules. The `game.engine` module appears to be an infrastructure/utility layer that sits alongside or below simulation. However, the documented rule states simulation can ONLY depend on core.

The SpatialGrid and CollisionSystem are used for:
- Efficient spatial queries (finding nearby ships/projectiles)
- Hit detection for projectiles and beams
- Ramming collision processing

**Impact:** This creates a dependency on a non-core module. If game.engine changes, simulation must change.

**Recommendation:** Either:
1. Move SpatialGrid and CollisionSystem to game.core if they are truly foundational
2. Update architecture documentation to allow simulation -> engine dependency
3. Abstract these through interfaces defined in core

---

#### LOW: AI Controller interface imports from game.engine (TYPE_CHECKING only)

**File:** `C:\Dev\Starship Battles\game\simulation\interfaces\ai_controller.py`

**Lines:** 19

**Evidence:**
```python
if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.engine.spatial import SpatialGrid
```

**Analysis:**
This is a TYPE_CHECKING import only (not runtime), used for type hints in the IAIControllerFactory protocol. The SpatialGrid type hint indicates the factory's set_grid() method expects a SpatialGrid instance.

**Impact:** Low - TYPE_CHECKING imports don't create runtime dependencies. However, they indicate architectural awareness of another layer.

**Recommendation:** Consider defining an ISpatialGrid protocol in game.simulation.interfaces to fully decouple.

---

### God Classes

#### MEDIUM: Component class exceeds 500 LOC threshold

**File:** `C:\Dev\Starship Battles\game\simulation\components\component.py`

**Lines:** 724 total

**Evidence:**
The Component class is the central component abstraction handling:
- Component instantiation and cloning
- Ability management (instantiation, querying, iteration)
- Modifier management (add/remove, stats calculation)
- Health management (damage, HP tracking)
- Resource management (activation costs)
- Stats calculation with formula evaluation
- Serialization support

**Analysis:**
The class has already been partially decomposed (per PROJ-44, PROJ-88 comments in the code):
- ComponentHealthManager (component_health_manager.py)
- ComponentResourceManager (component_resource_manager.py)
- ComponentStatsCalculator (component_stats_calculator.py)
- AbilityManager (ability_manager.py)
- ModifierManager (modifier_manager.py)

However, Component still contains significant orchestration logic and delegates to these helpers. The 724 LOC count indicates further decomposition may be beneficial.

**Impact:** High cognitive load for maintenance. Changes to Component require understanding many concerns.

**Recommendation:** Continue the decomposition effort. Consider:
1. Extract remaining orchestration to a ComponentFacade
2. Use composition more aggressively (inject managers rather than create internally)
3. Review if Component still needs to expose all manager functionality directly

---

## Clean Architecture Compliance

### Correctly Structured Modules

The following patterns were observed as **correct**:

1. **game.simulation imports from game.core** - Vast majority of imports are from:
   - `game.core.constants`
   - `game.core.config`
   - `game.core.math`
   - `game.core.logger`
   - `game.core.exceptions`
   - `game.core.error_codes`
   - `game.core.paths`
   - `game.core.registry`

2. **No pygame imports** - The simulation layer correctly avoids any pygame dependencies.

3. **No AI layer imports** - Simulation uses the IAIController protocol (interfaces/ai_controller.py) rather than importing concrete AI implementations. This maintains proper layer boundaries.

4. **No strategy layer imports** - Simulation does not import from game.strategy.

5. **No UI layer imports** - Simulation does not import from game.ui.

6. **TYPE_CHECKING pattern** - Many files correctly use TYPE_CHECKING blocks for type hints that would otherwise create circular imports.

---

## Files Reviewed

All 69 Python files in game/simulation/ were reviewed:

- `__init__.py`, `physics_constants.py`, `formula_system.py`, `designs.py`
- `battle_config.py`, `projectile_manager.py`, `battle_controller.py`, `battle_state.py`
- `entities/` (12 files): ship.py, ship_physics.py, projectile.py, ship_stats.py, ship_formation.py, layer_data.py, ability_aggregator.py, combat_endurance.py, ship_combat_engine.py, ship_serialization.py, ship_stat_querier.py, ship_validator_helper.py, ship_loader.py
- `systems/` (4 files): battle_engine.py, battle_end_conditions.py, resource_manager.py, tech_preset_loader.py
- `services/` (6 files): __init__.py, modifier_service.py, vehicle_design_service.py, battle_service.py, design_loader.py, registry_loader.py
- `interfaces/` (2 files): __init__.py, ai_controller.py
- `managers/` (3 files): __init__.py, retreat_manager.py, battle_state_manager.py
- `validation/` (3 files): __init__.py, base.py, ship_validator.py
- `components/` (16 files): component.py, __init__.py, ability_manager.py, modifier_manager.py, component_stats_calculator.py, component_resource_manager.py, component_health_manager.py, component_constants.py, modifier_schema.py, modifiers.py, modifier_effects.py, modifier_introspection.py
- `components/abilities/` (13 files): __init__.py, base.py, weapons.py, resources.py, propulsion.py, defense.py, crew.py, markers.py, colonize.py, cargo.py, superweapons.py, harvester.py, stat_keys.py
- `combat/` (5 files): __init__.py, targeting_system.py, damage_calculator.py, weapon_firing_system.py, battle_mode_handler.py

---

## Recommendations

### Priority 1: Address game.engine dependency

The BattleEngine's dependency on game.engine.spatial and game.engine.collision should be resolved:
- Option A: Move these utilities to game.core (if they have no UI dependencies)
- Option B: Define abstract interfaces in game.simulation.interfaces that game.engine implements
- Option C: Document game.engine as a permitted dependency for simulation

### Priority 2: Continue Component decomposition

The Component class at 724 LOC remains above the 500 LOC threshold. Continue the existing decomposition effort to reduce cognitive complexity.

### Priority 3: Define ISpatialGrid interface

To fully decouple the AI controller factory interface from game.engine, define an ISpatialGrid protocol in game.simulation.interfaces.

---

*Report generated by Architecture Sweep Agent*
