# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 27
- **Confirmed:** 21
- **Downgraded:** 5
- **Rejected:** 1
- **Rejection Rate:** 3.7%

## Verdicts

#### Finding: AR-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Line 127 of `simulation_adapter.py` performs `from game.ai.ai_factory import AIControllerFactory` at runtime. The architecture docs explicitly list Strategy as allowed to depend on Simulation and Core only, not AI. The late import masks but does not eliminate the layer violation.

#### Finding: AR-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `StrategyScreen` lines 134-156 expose `session.galaxy`, `session.empires`, `session.player_empire`, etc. as direct properties, giving UI code access to mutable domain objects. A comment acknowledges this is for "internal convenience" but the facade pattern is bypassed.

#### Finding: AR-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Line 267 of `build_queue_source.py` imports `_colony_has_planetary_yard` (a private function) from `game.strategy.engine.production_engine`. This is a data/ -> engine/ upward dependency.

#### Finding: AR-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Line 12 of `cargo_transfer_service.py` has a top-level import `from game.strategy.engine.commands import IssueTransferCommand`. This is a services/ -> engine/ dependency. Commands are defined in the engine subpackage.

#### Finding: AR-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified: 12 ABC interfaces defined in `engines.py`. Only 4 engines inherit from their interface (ActionExecutionEngine, HarvestingEngine, PopulationEngine, ResupplyEngine). The other 8 (FleetMovementEngine, ProductionEngine, ConflictResolutionEngine, ConsumableManagementEngine, EnvironmentalHazardEngine, PlanetEnergyEngine, PlanetActionEngine, and AtmosphereEngine) do not formally implement their interfaces.

#### Finding: AR-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Grep confirms 334 late imports (indented `from game.*`) across 82 files in the strategy layer. The count matches exactly.

#### Finding: AR-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 268-269 of `build_queue_source.py` directly calls `RegistryManager.instance()` to get registries instead of receiving them via DI parameter.

#### Finding: AR-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `command_handlers.py` is 1062 lines. It contains BaseCommandHandler, CommandHandlerRegistry, ~14 concrete handlers, helper functions, and factory -- all in one file.

#### Finding: AR-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 12 of `planetary_facility.py` has a top-level import `from game.strategy.services.component_inspector import get_component_abilities`. This is a data/ -> services/ dependency at module level.

#### Finding: AR-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Grep confirms 15 imports from `game.strategy.services.*` in `data/` files including `fleet_capability_calculator.py`, `build_queue_source.py`, `fleet.py`, `planetary_facility.py`, `pathfinding.py`, and `ship_instance.py`. Most are late imports but represent logical upward dependencies.

#### Finding: AR-011
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Lines 83-94 of `strategy_session_facade.py` show `_get_fleet_by_id()` and `_get_empire_by_id()` return raw domain objects. While marked as private internal helpers, they could leak mutable domain objects to callers if used carelessly.

#### Finding: AR-012
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The finding claims Strategy uses HexCoord from `game/core/hex_math.py` and implies this might be an issue with `game/engine/`. But HexCoord is in Core, and the architecture docs explicitly allow Strategy to depend on Core. The finding's description is confused -- there is no actual issue described here. The docs correctly list Strategy's dependencies and HexCoord usage is compliant.

#### Finding: CQ-001
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Confirmed at 1062 lines, exceeding the 500-line target. However, "Critical" is too high for a file size issue -- this is a code quality concern, not a correctness bug or architectural violation that could cause runtime failures. Major is appropriate.

#### Finding: CQ-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 80-140 of `pathfinding.py` contain extensive "thinking aloud" comments like "Wait, galaxy.systems is keyed by location", "Optimization: Build name_to_system cache or linear search?", "For now, let's assume galaxy has a helper or we search." These are clearly development scratch notes left in production code.

#### Finding: CQ-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Three methods `_is_planet_stabilized`, `_is_system_stellar_stabilized`, and `_is_system_warp_stabilized` (lines 707-796) follow nearly identical structure. They differ only in the ability name string ("GeologicStabilizer", "StellarStabilizer", "WarpFieldStabilizer") and the scope list (planet/sector/system vs sector/system). A single parameterized method would eliminate the duplication.

#### Finding: CQ-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 188-198 of `fleet_navigation_service.py` create a `MockCapabilities` inner class and a dynamic `fleet_like` object using `type()` to satisfy `find_hybrid_path`'s API. This is a design smell -- `find_hybrid_path` should accept a simpler capability parameter rather than requiring a full fleet-like object.

#### Finding: CQ-005
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The ownership check pattern `planet.owner_id != session.player_empire.id` is repeated in 4 handlers (lines 47, 106, 124, 145). This is a real duplication, but it's a simple 2-line guard clause in short handler methods -- standard validation boilerplate. The handlers don't extend BaseCommandHandler which would provide this. Minor is more appropriate for this level of duplication.

#### Finding: CQ-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 279-292 of `strategy_session_facade.py` show `_get_planet_by_id` iterating all systems then all planets (O(N*M)). Meanwhile `Galaxy` has a `planets_by_id` dict (confirmed at galaxy.py:162) that provides O(1) lookup. The facade should use the existing index.

#### Finding: CQ-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified: command_handlers.py (1062 lines), superweapon_order_processor.py (815 lines), order_processor.py (762 lines) all exceed the 500-line convention target. The finding's claim of 9 files was not fully verified but the top 3 are confirmed.

#### Finding: CQ-008
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Three broad `except Exception as e` catches exist across data/ deserialization: empire.py:329, fleet.py:394, order_serializer.py:57. However, all three are intentional resilience patterns for loading corrupt save data -- they log warnings and skip bad entries rather than crashing. This is a reasonable defensive pattern for deserialization. Minor is more appropriate.

#### Finding: CQ-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 21-33 of `superweapon_command_handlers.py` contain two separate `if TYPE_CHECKING:` blocks, with the second (line 32) re-importing `GameSession` already imported in the first (line 22). This is dead/duplicate code.

#### Finding: CQ-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Planet command handlers in `planet_command_handlers.py` don't extend `BaseCommandHandler` but call its static methods (e.g., `BaseCommandHandler._resolve_planet()`) as standalone functions via late import. This is inconsistent with how other handlers inherit from BaseCommandHandler.

#### Finding: CQ-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Five mission handlers (lines 201-372) follow an identical 5-step pattern: resolve fleet, validate ability, add move order, queue action order, return success. The steps are structurally identical with only the specific validator method, order type, and target varying.

#### Finding: CQ-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The five main processor methods (process_implode_planet, process_stellerate_star, etc.) from line 127 onward follow the same pattern: check order type, validate target, check stabilizer protection, find ship with ability, apply effect, finalize. The `_finalize_superweapon` helper already extracts the tail end, but the leading pattern is still repetitive.

#### Finding: CQ-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 869 and 904 of `command_handlers.py` each create `DesignLibrary(session.save_path, empire_id)` in two separate methods (`_check_design_valid` and `_load_design_cost`). When both are called for the same command, the library is instantiated twice.

#### Finding: CQ-014
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** `process_self_destruct` (lines 630-705) does manually implement fleet cleanup and event logging that overlaps with `_finalize_superweapon`. However, self_destruct has genuinely different logic: it removes *multiple* ships by ID from a list (not a single superweapon ship), uses a different event type (SHIPS_SELF_DESTRUCTED), and includes ship_names in event data. The overlap is partial and the differences may justify the separate implementation. Info is more appropriate.

#### Finding: CQ-015
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 821-824 of `command_handlers.py` show step comments "5. Calculate design cost" followed by another "5. Pre-calculate initial turns estimate" -- duplicate step numbering where the second should be "6." (and actual step 6 follows as the queue item creation).
