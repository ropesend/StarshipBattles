# PROJ-240: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Ship.py is 850 lines with 20 identifiable responsibility blocks (see plan.md Initial Analysis).
Seven delegates already extracted in prior projects: ShipStatsCalculator, ShipCombatEngine,
ShipSerializer, ShipStatQuerier, ShipValidatorHelper, ShipFormation, ShipPhysicsMixin.

The two remaining extractable responsibilities are:
1. **Component lifecycle** (lines 275-278, 501-582, 671-800): 210+ lines of add/remove/cache/query
2. **Combat orchestration** (lines 253-269, 299-373): 115+ lines of update loop, death, derelict

After extraction, Ship retains only: identity, layers, class change, stat delegation, resource
references, AI state properties, and thin facade methods.

## Swarm Findings Summary

### Architecture

**Existing delegate pattern (docs/02_PATTERNS.md section 5):**
- Ship lazily creates delegates; delegates take `ship` reference
- Ship keeps public API; all methods become one-line delegations
- Delegates use `TYPE_CHECKING` import for Ship to avoid circular imports
- Precedent: ShipStatQuerier (PROJ-88), ShipCombatEngine (PROJ-44), ShipSerializer (PROJ-38)

**Ship.__init__ attribute inventory (160 lines, 48 attributes):**
- Identity: 8 attrs (id, name, color, team_id, ship_class, theme_id, vehicle_type, source_file)
- Stats (calculator-populated): 17 attrs (mass, hp, max_hp, thrust, speed, turn, shields, armor, etc.)
- Resources: 4 attrs (resources, _resources_initialized, _prev_max_resources, _prev_max_shields)
- Combat state: 6 attrs (is_alive, is_derelict, bridge_destroyed, retreat_status, comp_trigger_pulled, aim_point)
- Firing state: 2 attrs (just_fired_projectiles, total_shots_fired)
- Cache state: 4 attrs (_components_cache, _components_dirty, _weapons_cache, _weapons_cache_tick)
- AI state: 3 attrs (current_target, secondary_targets, ai_strategy)
- Physics: 4 attrs (current_speed, acceleration_rate, is_thrusting, target_speed)
- Delegates: 4 attrs (stats_calculator, _stat_querier, _validator_helper, _combat_engine)

### Key Patterns to Reuse

- **Lazy delegate initialization**: `ship_stat_querier.py:26-28` -- `__init__` takes ship reference
- **Facade one-liner**: `ship.py:625` -- `return self.stat_querier.get_ability_total(ability_name)`
- **TYPE_CHECKING import**: `ship_stat_querier.py:9` -- avoids circular import
- **Late import for circular deps**: `ship.py:519` -- ModifierService imported inside method body

### Dependencies and Risks

1. **`just_fired_projectiles` direct assignment** -- battle_engine.py assigns `s.just_fired_projectiles = []`
   Mitigation: Ship exposes a property with setter that delegates to combat_manager.

2. **`comp_trigger_pulled` direct assignment** -- ai/controllable.py writes `self._ship.comp_trigger_pulled = value`
   Mitigation: Ship exposes a property with setter.

3. **`update()` ordering is critical** -- Resources -> Components -> Stats -> Physics -> Combat -> Firing.
   Mitigation: Move the entire method as-is; document ordering in ShipCombatManager docstring.

4. **`_attach_component` has late import** -- ModifierService circular dep at line 519.
   Mitigation: Keep late import in ShipComponentManager.

5. **`add_component` calls `get_or_create_validator`** -- uses global registry provider at line 530.
   Mitigation: Move import to ShipComponentManager; no change in behavior.

6. **`recalculate_stats` is called from BOTH managers** -- add_component calls it, update() calls it.
   Mitigation: recalculate_stats stays on Ship (it delegates to ShipStatsCalculator already).
   Both managers call `self._ship.recalculate_stats()`.

### Opportunities Discovered

- **Mutable cache bug** (line 688): `get_all_components()` returns internal `_components_cache` list.
  Any caller doing `comps = ship.get_all_components(); comps.append(x)` corrupts the cache.
  Fix: return `list(self._components_cache)`.

- **Weapons cache tick coupling** (lines 740-743): Requires caller to pass `current_tick`.
  Only one caller exists (internal). Dirty-flag invalidation is simpler and more reliable.

- **change_class silent fallback** (lines 462-465): Unknown class silently uses empty dict.
  Should raise ValidationException -- already guarded at line 446 for `change_class` entry.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
