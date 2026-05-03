# Module Review: game/strategy/

**Module Specialist:** MOD-STR
**Review Date:** 2026-02-23
**Scope:** Galaxy generation, fleet management, turn engine, command handlers, facade pattern

---

## Summary

**Total Findings:** 22
**Severity Distribution:**
- Critical: 3
- Major: 8
- Minor: 7
- Info: 4

**Overall Module Health Rating: 7/10 (Good)**

The strategy module is well-architected with clear separation of concerns, good use of dependency injection, and solid facade patterns. However, there are several issues ranging from potential data corruption risks to performance concerns and architectural inconsistencies.

---

## Findings

### MOD-STR-001: Galaxy Fleet Registry Out of Sync Risk
**Location:** `game/strategy/data/galaxy.py:269-294`, `game/strategy/engine/game_session.py:208-232`
**Severity:** Critical
**Deliberate:** No

**Description:**
Galaxy maintains a `fleets_by_id` registry for O(1) fleet lookup, but fleet registration/unregistration is not consistently enforced. GameSession has a fallback O(n) iteration when `galaxy.get_fleet_by_id()` returns None. Fleet registration happens during `GameInitializer.initialize()`, but there's no guaranteed registration when fleets are created during gameplay (e.g., ship production spawning new fleets).

**Evidence:**
- `ProductionEngine._spawn_ship()` creates fleets via `empire.add_fleet()` but doesn't call `galaxy.register_fleet()`
- `GameSession._get_fleet_by_id()` has defensive fallback iterating all empires' fleets

**Recommendation:**
Make `Empire.add_fleet()` automatically register with Galaxy. Remove O(n) fallback after fixing root cause.

---

### MOD-STR-002: Planet Zone Registry Desync on Dyson Sphere Creation
**Location:** `game/strategy/data/galaxy.py:191-192`, `game/strategy/data/planet.py:199-201`
**Severity:** Major
**Deliberate:** No

**Description:**
When a planet's `diameter_hexes` changes dynamically (e.g., planet imploded into Dyson Sphere), the zone registry is not updated. `Galaxy.register_zone()` is only called during initial registration, not when planet properties change.

**Recommendation:**
Add `Planet.update_zone(galaxy, old_diameter)` method called when diameter changes. Hook into superweapon handlers.

---

### MOD-STR-003: Order Target Reference Resolution Fragility
**Location:** `game/strategy/data/fleet.py:344-417`
**Severity:** Critical
**Deliberate:** No (technical debt)

**Description:**
Fleet order deserialization stores temporary marker dicts like `{'_fleet_ref': id}` and `{'_planet_ref': id}` that must be resolved later, but there's no guaranteed resolution pass. These markers can persist if resolution is forgotten, causing runtime errors when orders are processed.

**Recommendation:**
Add explicit `fleet.resolve_order_references(galaxy, empires)` method. Add runtime validation to detect unresolved references.

---

### MOD-STR-004: Command Handler Registry Inconsistent Error Handling
**Location:** `game/strategy/engine/command_handlers.py:73-133`
**Severity:** Major
**Deliberate:** No

**Description:**
Command handlers have inconsistent error handling. Some handlers (ColonizeCommandHandler) iterate empires to find fleets manually, while others use `session._get_fleet_by_id()` helper. Different failure modes and performance characteristics for similar operations.

**Recommendation:**
Standardize on `session._get_fleet_by_id()` for all handlers.

---

### MOD-STR-005: Production Engine Missing Resource Cost Initialization
**Location:** `game/strategy/engine/production_engine.py:255-262`
**Severity:** Major
**Deliberate:** No

**Description:**
`_process_queue_tick_dynamic()` has a defensive check for missing `total_cost` in queue items but doesn't properly initialize it. Comments indicate uncertainty about how to load design data at this point. Defensive-but-broken code that passes silently.

**Recommendation:**
Document queue item contract explicitly. Add validation in command handlers that enqueue production.

---

### MOD-STR-006: Pathfinding Inefficient System Name Lookups
**Location:** `game/strategy/data/pathfinding.py:53-68`
**Severity:** Minor
**Deliberate:** No (missing index)

**Description:**
`find_path_interstellar()` does repeated `galaxy.get_system_by_name()` lookups inside A* loop. Lookup is O(1) via name_map, but code comments suggest uncertainty about data structure.

**Recommendation:**
Clarify data structures with explicit types/documentation.

---

### MOD-STR-007: Facade Pattern Inconsistently Applied
**Location:** `game/strategy/facade/strategy_session_facade.py:79-104`
**Severity:** Info
**Deliberate:** Partially

**Description:**
Facade has internal helper methods that duplicate GameSession logic. Calls `session._get_fleet_by_id()` which breaks encapsulation of the underlying session.

**Recommendation:**
Either make GameSession methods public as facade API, or have facade duplicate logic.

---

### MOD-STR-008: Save/Load Strict Version Checking
**Location:** `game/strategy/systems/save_game_service.py:372-379`
**Severity:** Minor
**Deliberate:** Yes (stated policy)

**Description:**
`_is_compatible_version()` rejects any save that doesn't match exact version string. Unusually aggressive but matches "Save files are disposable" policy in CLAUDE.md.

**Recommendation:**
Accept as deliberate design choice per project policy.

---

### MOD-STR-009: Galaxy Generation Saturation Detection Fragile
**Location:** `game/strategy/data/galaxy.py:499-516`
**Severity:** Minor
**Deliberate:** No

**Description:**
`generate_systems()` detects saturation by counting consecutive failures (max 10). Heuristic that can fail early in dense galaxies or too late in sparse ones.

**Recommendation:**
Calculate theoretical maximum systems and log warning with specific numbers when saturation detected.

---

### MOD-STR-010: Warp Lane Generation Region Mode Inconsistency
**Location:** `game/strategy/data/galaxy.py:693-817`
**Severity:** Minor
**Deliberate:** Partially

**Description:**
Three region connection modes ('normal', 'limited', 'minimal') have subtle issues: 'minimal' prevents ALL inter-region density edges, 'limited' doesn't enforce symmetric limits.

**Recommendation:**
Add integration test verifying graph connectivity with different region modes.

---

### MOD-STR-011: Fleet Movement Resource Consumption Timing
**Location:** `game/strategy/engine/fleet_movement_engine.py:99-127`
**Severity:** Major
**Deliberate:** Unclear

**Description:**
Resources checked before movement but consumed during movement. Warp resources consumed separately from movement resources — if a fleet warps, it consumes both warp AND movement resources. Could be intentional double-cost or a bug.

**Recommendation:**
Document whether warp should consume movement resources. Add test coverage.

---

### MOD-STR-012: Colony Pod Chain Validation Skip Logic
**Location:** `game/strategy/validation/colonize_validator.py:56-69`
**Severity:** Minor
**Deliberate:** Yes (PROJ-140)

**Description:**
`ColonizeValidator.validate()` has `skip_chain_check` parameter that bypasses pod exhaustion checking during order execution. Dual-mode validation is fragile.

**Recommendation:**
Split into `validate_for_queueing()` and `validate_for_execution()` methods.

---

### MOD-STR-013: Production Mid-Tick Completion Iteration Limit
**Location:** `game/strategy/engine/production_engine.py:223`
**Severity:** Minor
**Deliberate:** Yes (safety)

**Description:**
`max_iterations=10` limit means a single production queue could complete at most 10 items per tick. Defensive against infinite loops with 0-cost items.

**Recommendation:**
Document whether 10 items/tick is acceptable gameplay limit. Add warning log when limit hit.

---

### MOD-STR-014: TurnEngine Scuttle Event Storage Not Thread-Safe
**Location:** `game/strategy/engine/turn_engine.py:168-169, 260, 325`
**Severity:** Info
**Deliberate:** Yes (single-threaded)

**Description:**
`last_scuttle_events` is mutable list accumulated during tick processing. Works fine in single-threaded turn processing. Would need refactoring for async/parallel.

**Recommendation:**
Document single-threaded assumption. Consider returning events from `process_turn()` instead of storing as state.

---

### MOD-STR-015: Empire Resource Pool No Atomic Operations
**Location:** `game/strategy/data/empire.py:80-114`
**Severity:** Info
**Deliberate:** Yes (single-threaded)

**Description:**
`consume_resources()` has check-then-act race condition if multi-threaded. Fine for current single-threaded design.

---

### MOD-STR-016: Pathfinding Deep Space Fallback May Be Incorrect
**Location:** `game/strategy/data/pathfinding.py:196-252`
**Severity:** Major
**Deliberate:** No

**Description:**
`find_hybrid_path()` falls back to direct hex path when interstellar path fails. If warp network is disconnected, fleets pathfind through deep space, potentially bypassing intended strategic chokepoints.

**Recommendation:**
Document whether deep space bypass of disconnected warp network is intended. Consider returning None for disconnected networks.

---

### MOD-STR-017: Fleet Battle Adapter Formation Position Calculation
**Location:** `game/strategy/data/fleet_battle_adapter.py`
**Severity:** Minor
**Deliberate:** Yes

**Description:**
Formation calculation done per-conversion not per-fleet. Same fleet fighting multiple battles could have different formations due to randomization. Likely intentional for gameplay variety.

---

### MOD-STR-018: GameSession Event Handler Closure Captures Mutable State
**Location:** `game/strategy/engine/game_session.py:103-125`
**Severity:** Minor
**Deliberate:** Yes (practical solution)

**Description:**
`_create_event_handler()` closure captures `self` and reads `self.turn_number` dynamically. Classic closure timing issue if events processed after turn increment.

**Recommendation:**
Consider passing turn_number explicitly instead of capturing via closure.

---

### MOD-STR-019: Planet Facilities Resource Levels No Validation
**Location:** `game/strategy/data/planet.py:35`
**Severity:** Minor
**Deliberate:** No

**Description:**
`PlanetaryFacility.resource_levels` is a dict with no validation. Code can set negative fuel levels, exceed max capacity, or use wrong resource type keys.

**Recommendation:**
Add validation property checking levels vs. max capacity.

---

### MOD-STR-020: Intercept Point Calculation Early Exit Logic
**Location:** `game/strategy/data/pathfinding.py:362-374`
**Severity:** Minor
**Deliberate:** Yes (optimization)

**Description:**
Early exit with `target_turn > best_intercept_time + 3` could skip better intercept points if target's path has sharp turn or loop. The +3 threshold is arbitrary.

---

### MOD-STR-021: Multiple Services Use Late/Lazy Imports
**Location:** Throughout (`fleet.py:145-146`, `turn_engine.py:175`)
**Severity:** Info
**Deliberate:** Yes (intentional pattern per ARCHITECTURE.md)

**Description:**
Several files use late imports to avoid circular dependencies. Documented as "INTENTIONAL LATE IMPORT" pattern.

**Recommendation:**
Accept as deliberate design per architecture docs.

---

### MOD-STR-022: No Validation for Malformed Queue Items in Production
**Location:** `game/strategy/engine/production_engine.py:227-231`
**Severity:** Minor
**Deliberate:** No

**Description:**
`_process_queue_tick_dynamic()` silently removes invalid queue items. No logging or warning — could hide bugs.

**Recommendation:**
Add warning log when invalid item removed. Add validation at enqueue time.

---

## Top 5 Priority Issues

1. **MOD-STR-001 (Critical):** Galaxy Fleet Registry Out of Sync Risk — data corruption risk, fix automatic registration
2. **MOD-STR-003 (Critical):** Order Target Reference Resolution Fragility — runtime crash risk from unresolved markers
3. **MOD-STR-016 (Major):** Pathfinding Deep Space Fallback — gameplay exploit bypassing warp chokepoints
4. **MOD-STR-002 (Major):** Planet Zone Registry Desync — spatial index corruption after Dyson Sphere creation
5. **MOD-STR-011 (Major):** Fleet Movement Resource Consumption Timing — unclear double-cost mechanic
