# Strategy Engine Duplication Review

## Scope
- `game/strategy/engine/` (21 files)
- `game/strategy/facade/` (7 files)
- `game/strategy/events/` (3 files)

## Summary

The strategy engine has already undergone significant decomposition (PROJ-12, PROJ-36, PROJ-43, PROJ-87, PROJ-176, PROJ-204, PROJ-209) and many patterns have been extracted into shared helpers. The codebase is in reasonably good shape. However, several duplication patterns remain:

**Critical findings:** 2 MAJOR, 7 MINOR
**Estimated total consolidation effort:** Medium (spread across multiple files, but each individual fix is small)

---

## Findings

---

#### MAJOR: Duplicated `_setup_mission_move` vs `add_move_order_if_needed` Logic
**ID:** DUP-SE-001
**Location:** `command_handlers.py:30-79` (`add_move_order_if_needed`) and `superweapon_command_handlers.py:195-230` (`_setup_mission_move`)
**Issue:** These two functions perform nearly identical logic: determine chain-aware start hex from last MOVE order, calculate path via `find_hybrid_path`, queue a MOVE order if not already at target, and set path immediately for first-order fleets. The only differences are minor (how `start_hex` is determined from existing orders -- one skips non-MOVE orders with reversed iteration, the other only checks the last order).
**Impact:** Both functions need to be updated in sync for any pathfinding or order-chaining change. The subtle difference in start_hex logic (BUG-70 fix in `add_move_order_if_needed` vs simpler logic in `_setup_mission_move`) means the superweapon missions may not handle interleaved non-MOVE orders correctly.
**Recommendation:** Delete `_setup_mission_move` entirely and have all 5 superweapon mission command handlers call `add_move_order_if_needed` instead. The function already exists in `command_handlers.py` which is imported by `superweapon_command_handlers.py`.
**Effort:** Simple

---

#### MAJOR: Duplicated Combat Event Logging in `_resolve_combat` and `_resolve_combat_simulated`
**ID:** DUP-SE-002
**Location:** `conflict_resolution_engine.py:206-231` (`_resolve_combat` RNG path) and `conflict_resolution_engine.py:283-306` (`_resolve_combat_simulated`)
**Issue:** Both methods contain nearly identical blocks for:
1. Looking up `system_name` via `self._galaxy.get_system_at_location(f1.location)` (lines 207-211 and 284-288 -- identical pattern)
2. Getting `storm_names` from `self._area_effect_manager` (lines 214-218 and 291-293 -- same logic, slightly different variable source)
3. Calling `log_event(EventType.COMBAT_RESOLVED, ...)` with identical kwargs structure (lines 220-230 and 295-305)

The total duplicated block is ~25 lines per occurrence.
**Impact:** Any change to combat event logging (e.g., adding new fields) must be made in two places. The two paths also diverge slightly in how they get `storm_names` (one re-queries, one reuses a variable), which is a maintenance risk.
**Recommendation:** Extract a private helper `_log_combat_result(self, winner, loser, location, environmental_effects=None)` that encapsulates system lookup, storm name extraction, and event logging. Both methods call this helper.
**Effort:** Simple

---

#### MINOR: Duplicated `_spawn_complex` and `_spawn_fleet_complex` Logic
**ID:** DUP-SE-003
**Location:** `production_engine.py:595-655` (`_spawn_complex`) and `production_engine.py:800-887` (`_spawn_fleet_complex`)
**Issue:** Both methods share the same pattern:
1. Load design data from `DesignLibrary` with identical error handling
2. Create `PlanetaryFacility` with identical constructor args
3. Append to `planet.facilities`
4. Look up system_name and local_hex for event logging
5. Call `log_event(EventType.COMPLEX_BUILT, ...)` with almost identical kwargs

The duplicated code is ~40 lines of the ~50-line methods. The only difference is how the planet is determined (passed in vs looked up at fleet location).
**Impact:** Changes to facility creation or event logging must be mirrored. The design loading/error handling patterns are copy-pasted.
**Recommendation:** Extract a `_create_and_place_facility(self, planet, design_id, empire, save_path, galaxy, is_fleet_production=False, fleet=None)` helper that handles design loading, facility creation, placement, and event logging. Both `_spawn_complex` and `_spawn_fleet_complex` would resolve the target planet then delegate to this helper.
**Effort:** Medium

---

#### MINOR: Duplicated `_spawn_ship` and `_spawn_fleet_ship` Design Loading
**ID:** DUP-SE-004
**Location:** `production_engine.py:657-736` (`_spawn_ship`) and `production_engine.py:738-798` (`_spawn_fleet_ship`)
**Issue:** Both methods have identical blocks for:
1. Loading design data from `DesignLibrary` (5 lines, same error handling)
2. Creating `ShipInstance.create()` with identical args (6 lines)
3. Calling `design_library.increment_built_count()` (1 line)
4. Calling `log_event(EventType.SHIP_BUILT, ...)` with similar kwargs

~20 lines of duplicated logic.
**Impact:** Any change to ship creation (new ShipInstance.create args, different logging) must be done in both methods.
**Recommendation:** Extract `_load_and_create_ship_instance(self, design_id, empire, save_path) -> Optional[ShipInstance]` that handles design loading, instance creation, and built count increment. Both spawn methods call this helper, then handle placement (new fleet vs existing fleet) and event logging.
**Effort:** Simple

---

#### MINOR: Duplicated Fleet Iteration + Empire Iteration Pattern in Tick Engines
**ID:** DUP-SE-005
**Location:** Multiple engines: `harvesting_engine.py:124`, `maintenance_engine.py:120-121`, `resource_management_engine.py:85-87`, `resupply_engine.py:92-93`, `environmental_hazard_engine.py:93-94`, `action_execution_engine.py:94-96`
**Issue:** Every tick-processing engine has the same boilerplate:
```python
for empire in empires:
    for fleet/colony in empire.fleets/colonies:
        # process
```
This is the expected pattern for engines that process all entities, so it's structural rather than truly duplicated business logic. However, some engines also copy the "for fleet in list(empire.fleets):" defensive copy pattern.
**Impact:** Low -- this is idiomatic iteration. The defensive copy (`list(empire.fleets)`) is only needed when fleets may be consumed during iteration, and some engines do it unnecessarily.
**Recommendation:** No consolidation needed. This is standard iteration and extracting it would add complexity without benefit. **Do not consolidate.**
**Effort:** N/A (no action recommended)

---

#### MINOR: Duplicated `process_join_fleet` Merge+Event Logic (Two Code Paths)
**ID:** DUP-SE-006
**Location:** `fleet_order_processor.py:79-131` (`process_join_fleet`) and `fleet_order_processor.py:656-704` (`process_instant_orders`)
**Issue:** Both methods contain JOIN_FLEET merge logic:
1. Check `fleet.location == target_fleet.location`
2. Call `fleet.merge_with(target_fleet)`
3. Call `empire.remove_fleet(fleet)`
4. Log `EventType.FLEET_JOINED` event with identical kwargs

`process_join_fleet` handles single-fleet processing and `process_instant_orders` handles batch processing, but the merge+log logic is duplicated (~15 lines per path).
**Impact:** Changes to merge logic or event logging must be made in two places. They already have identical `log_event` calls.
**Recommendation:** Extract `_execute_merge(self, fleet, target_fleet, empire)` helper that performs merge, removal, and event logging. Both `process_join_fleet` and `process_instant_orders` call this helper.
**Effort:** Simple

---

#### MINOR: Duplicated Registries Resolution Pattern in `GameSession.__init__` and `from_dict`
**ID:** DUP-SE-007
**Location:** `game_session.py:86-96` (`__init__`) and `game_session.py:291-302` (`from_dict`)
**Issue:** Both `__init__` and `from_dict` contain the identical 7-line block:
```python
provider = get_default_registry_provider()
session._registries = GameRegistries(
    components=provider.get_components(),
    modifiers=provider.get_modifiers(),
    vehicle_classes=provider.get_vehicle_classes(),
    resources=provider.get_resources(),
)
session.turn_engine = TurnEngine(registries=session._registries)
session._command_registry = create_default_registry()
```
**Impact:** If registry initialization changes (new registry types, different provider API), both paths must be updated.
**Recommendation:** Extract a static method `_init_engines(registries=None) -> Tuple[GameRegistries, TurnEngine, CommandHandlerRegistry]` or an instance method `_setup_engines()` called by both `__init__` and `from_dict`.
**Effort:** Simple

---

#### MINOR: Duplicated `session.turn_engine._registries.components` Access Pattern
**ID:** DUP-SE-008
**Location:** `superweapon_command_handlers.py` lines 48, 73, 98, 125, 157, and `command_handlers.py` line 466
**Issue:** Six superweapon command handlers and the ColonizeMissionCommandHandler all access the component registry via the same deep chain: `session.turn_engine._registries.components`. This is accessing a private attribute (`_registries`) through another object's private API, repeated 7+ times.
**Impact:** Fragile coupling to TurnEngine internals. If `_registries` is renamed or restructured, all handlers break. Also, `session.registries.components` already exists as a public property (line 118-120 of game_session.py), making the `turn_engine._registries` access redundant.
**Recommendation:** Replace all `session.turn_engine._registries.components` with `session.registries.components` (the public property). This is a find-and-replace fix.
**Effort:** Simple

---

#### MINOR: Backward Compatibility Alias `process_end_turn_orders`
**ID:** DUP-SE-009
**Location:** `fleet_order_processor.py:645-654`
**Issue:** `process_end_turn_orders` is a backward-compat alias for `execute_action_order`. Per the project's System Migration Policy, backward compatibility layers should be eradicated.
**Impact:** Keeps dead code in the codebase. Any caller should use `execute_action_order` directly.
**Recommendation:** Search for all callers of `process_end_turn_orders`, update them to `execute_action_order`, and delete the alias. If no external callers exist, delete immediately.
**Effort:** Simple

---

## Top 5 Priority List

| Priority | ID | Title | Effort | Impact |
|----------|---------|-------|--------|--------|
| 1 | DUP-SE-001 | `_setup_mission_move` vs `add_move_order_if_needed` | Simple | Potential bug (different chain logic) + maintenance burden |
| 2 | DUP-SE-008 | `session.turn_engine._registries.components` private access | Simple | Fragile coupling, easy fix via existing public API |
| 3 | DUP-SE-002 | Combat event logging duplication | Simple | Maintenance risk in frequently-changed area |
| 4 | DUP-SE-003 | `_spawn_complex` / `_spawn_fleet_complex` duplication | Medium | ~40 lines duplicated in production engine |
| 5 | DUP-SE-006 | JOIN_FLEET merge logic in two code paths | Simple | Identical event logging must be kept in sync |

## Notes

- **DUP-SE-009** should be addressed as part of the migration policy (eradicate backward compat) but is low risk since the alias is a simple delegation.
- **DUP-SE-005** (iteration patterns) is structural and should NOT be consolidated -- the "duplication" is idiomatic Python, not business logic duplication.
- **DUP-SE-007** (registries init) is a minor quality-of-life improvement since `from_dict` is only called on save game load.
- The command handler pattern itself (resolve fleet, validate, apply) is intentionally repeated across handlers -- this is the registry pattern working as designed, not duplication. Each handler has different validation and application logic.
- The `BaseCommandHandler` mixin (PROJ-176) has already successfully consolidated the fleet/planet resolution patterns that were previously duplicated across 19 handlers.
