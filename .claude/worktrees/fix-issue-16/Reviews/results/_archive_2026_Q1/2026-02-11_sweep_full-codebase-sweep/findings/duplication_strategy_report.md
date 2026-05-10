# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 95
- **Total Issues Found:** 10
- **Critical:** 2 | **Major:** 4 | **Minor:** 3 | **Info:** 1

## Findings

#### CRITICAL: Mission Command Handlers are Copy-Paste Clones
**ID:** DUP-STR-001
**Location:** `game/strategy/engine/superweapon_command_handlers.py:182-393` (5 classes, ~210 lines)
AND `game/strategy/engine/command_handlers.py:227-289` (ColonizeMissionCommandHandler, ~60 lines)
**Issue:** All six "Mission" command handlers (`ImplodePlanetMissionCommandHandler`, `StellerateStarMissionCommandHandler`, `OpenWarpPointMissionCommandHandler`, `CloseWarpPointMissionCommandHandler`, `CreateDysonSphereMissionCommandHandler`, and `ColonizeMissionCommandHandler`) share an identical 15-line boilerplate pattern: resolve fleet, determine start hex from last MOVE order, calculate hybrid path, queue MOVE order with path assignment, then queue the action-specific order. The only differences are (a) which action order type/target is appended and (b) whether a planet resolution step is included. Each class repeats the exact same "determine start hex" block (lines 197-202 in each), the same "calculate path" block, and the same "queue MOVE if not at target" block with identical path-stripping logic.
**Impact:** Any bug fix to the move+path logic must be applied to 6 separate classes. This has already led to subtle inconsistency: `ColonizeMissionCommandHandler` includes an auto-load population step (BUG-70 fix) that none of the superweapon mission handlers include, suggesting future mission handlers could miss important cross-cutting concerns. With 6 copies, this is the highest-risk duplication in the strategy layer.
**Recommendation:** Extract a shared `MissionCommandBase` class or a `queue_move_then_action()` utility function that accepts the action order as a parameter. Each concrete handler becomes a 5-line class that calls the shared function with its specific order type and target.
**Effort:** Simple

#### CRITICAL: _calculate_maintenance_cost Duplicated Across 3 Classes
**ID:** DUP-STR-002
**Location:** `game/strategy/engine/maintenance_engine.py:189-228` AND `game/strategy/engine/empire_economy_calculator.py:256-295` AND `game/strategy/engine/production_engine.py:58-82` (similar `_calculate_design_cost`)
**Issue:** The method `_calculate_maintenance_cost` is implemented identically in both `MaintenanceEngine` and `EmpireEconomyCalculator` - same docstring, same logic, same constant (`MAINTENANCE_RATE = 0.05`). Both iterate `design_data['layers']`, handle dict-with-components and list layer formats, sum `resource_cost` fields, and multiply by 0.05. Additionally, `ProductionEngine._calculate_design_cost` performs the same layer iteration and resource_cost summation pattern (without the 0.05 multiplier). All three classes independently parse the same design_data structure to extract build costs.
**Impact:** The maintenance rate constant is defined in two places (`MaintenanceEngine.MAINTENANCE_RATE` and `EmpireEconomyCalculator.MAINTENANCE_RATE`). If maintenance rate changes, both must be updated. The three implementations handle layer format differences (dict vs list) independently, risking format-handling divergence if a third layer format is introduced.
**Recommendation:** Extract a shared `calculate_total_build_cost(design_data) -> Dict[str, float]` utility function to `game/strategy/services/` or `game/core/`. `MaintenanceEngine` and `EmpireEconomyCalculator` call it and multiply by `MAINTENANCE_RATE` (defined once as a module constant). `ProductionEngine` calls it directly.
**Effort:** Simple

#### MAJOR: _find_system_at_location Duplicated in Validator and Processor
**ID:** DUP-STR-003
**Location:** `game/strategy/validation/superweapon_validator.py:36-69` AND `game/strategy/engine/superweapon_order_processor.py:47-78`
**Issue:** The `_find_system_at_location` method is implemented identically in both `SuperweaponValidator` and `SuperweaponOrderProcessor`. Both check `galaxy.systems` for direct location match, then iterate all systems checking planet, star, and warp point offsets. The code is 32 lines per copy and character-for-character identical. Meanwhile, `Galaxy.get_system_of_object()` (galaxy.py:132-168) performs a simpler version of the same lookup but only checks direct system location match - it does NOT check planet/star/warp point offsets, making it incomplete for this use case.
**Impact:** Three implementations of "find system containing location" exist with different completeness levels. Bugs fixed in one copy will be missed in others. The Galaxy method is the natural home for this logic but is incomplete.
**Recommendation:** Enhance `Galaxy.get_system_of_object()` (or add `Galaxy.get_system_at_location(hex)`) to include the planet/star/warp point offset checks. Remove both private copies from `SuperweaponValidator` and `SuperweaponOrderProcessor` in favor of calling the Galaxy method.
**Effort:** Simple

#### MAJOR: _get_harvester_info / _lookup_harvester_in_registry Duplicated
**ID:** DUP-STR-004
**Location:** `game/strategy/engine/harvesting_engine.py:201-243` AND `game/strategy/engine/empire_economy_calculator.py:172-213`
**Issue:** Both `HarvestingEngine` and `EmpireEconomyCalculator` implement `_get_harvester_info` and `_lookup_harvester_in_registry` methods with identical logic. Both check inline abilities, fall back to registry lookup by component ID, and return `ResourceHarvester` ability data. The methods are structurally identical (~42 lines per class).
**Impact:** The `EmpireEconomyCalculator` was created to replicate `HarvestingEngine` formulas for display purposes (as noted in its docstring). Any change to how harvesters are discovered must be made in both places.
**Recommendation:** Extract a shared `FacilityAbilityResolver` utility or add the harvester lookup to `component_inspector.py` (which already consolidates component ability iteration). Both engines would call the shared utility.
**Effort:** Simple

#### MAJOR: _get_storage_info / _lookup_storage_in_registry Pattern Duplication
**ID:** DUP-STR-005
**Location:** `game/strategy/engine/harvesting_engine.py:123-165` AND `game/strategy/engine/resupply_engine.py:126-156` (similar pattern for fuel)
**Issue:** `HarvestingEngine._get_storage_info` and `_lookup_storage_in_registry` follow the exact same "check inline abilities then fall back to registry" pattern as the harvester methods. `ResupplyEngine._get_fuel_generation_rate` uses a similar pattern (iterate layers, get comp_id, lookup in registry, extract ability). The three-step pattern (inline check -> registry lookup -> ability extraction) is repeated across 4 methods in 3 different engines, each looking for a different ability name but using identical structural code.
**Impact:** The "resolve component ability from design_data" pattern should be a first-class utility. `component_inspector.py` already provides `iterate_design_components()` which handles registry lookup, but these engines don't use it - they each re-implement the pattern independently.
**Recommendation:** Refactor these engines to use `component_inspector.iterate_design_components()` or create a higher-level `find_ability_in_design(design_data, ability_name, registry)` function. This would eliminate ~100 lines of repeated code across the three engines.
**Effort:** Medium

#### MAJOR: _spawn_complex Duplicated Between Colony and Fleet Paths
**ID:** DUP-STR-006
**Location:** `game/strategy/engine/production_engine.py:434-475` (`_spawn_complex`) AND `game/strategy/engine/production_engine.py:659-731` (`_spawn_fleet_complex`)
**Issue:** Within `ProductionEngine`, `_spawn_complex` and `_spawn_fleet_complex` share ~25 lines of identical code: loading design data via `DesignLibrary`, creating a `PlanetaryFacility` with `uuid.uuid4()`, appending to planet facilities, and logging the `COMPLEX_BUILT` event. The fleet version adds planet lookup logic and a `target_planet_id` parameter but the core "load design -> create facility -> append -> log" sequence is the same. Similarly, `_spawn_ship` (lines 477-541) and `_spawn_fleet_ship` (lines 603-657) share the same "load design -> create ShipInstance -> increment built count -> log event" pattern (~20 shared lines).
**Impact:** Bug fixes or enhancements to facility/ship creation (e.g., adding a new field to PlanetaryFacility) must be applied in two places within the same file.
**Recommendation:** Extract `_create_facility_from_design(design_id, empire, save_path) -> PlanetaryFacility` and `_create_ship_instance(design_id, empire, save_path) -> ShipInstance` private helper methods. Both colony and fleet spawn methods call these helpers, adding their own placement logic around the shared core.
**Effort:** Simple

#### MINOR: Direct Superweapon Command Handlers Follow Repetitive Pattern
**ID:** DUP-STR-007
**Location:** `game/strategy/engine/superweapon_command_handlers.py:27-175` (6 classes, ~150 lines)
**Issue:** The six direct superweapon command handlers (`ImplodePlanetCommandHandler`, `StellerateStarCommandHandler`, `OpenWarpPointCommandHandler`, `CloseWarpPointCommandHandler`, `CreateDysonSphereCommandHandler`, `SelfDestructCommandHandler`) all follow the same 4-step pattern: (1) resolve fleet via `session._get_fleet_by_id`, (2) optionally resolve another entity, (3) call the appropriate `SuperweaponValidator.validate_*` method, (4) if valid, create `FleetOrder` and add to fleet. While each handler has unique validation and target resolution, the resolve-fleet and create-order boilerplate is repeated 6 times.
**Impact:** Low risk since each handler's validation step is genuinely different. The duplication is structural rather than behavioral. However, the fleet resolution and "if valid, add order" bookends are pure boilerplate.
**Recommendation:** Consider a base class or decorator that handles fleet resolution and order creation, letting each handler define only the validation and target resolution steps. However, given the variation in validation parameters, a simple approach may not reduce complexity significantly. Acceptable as-is with monitoring.
**Effort:** Medium

#### MINOR: Fleet Lookup Pattern Duplicated in ColonizeCommandHandler
**ID:** DUP-STR-008
**Location:** `game/strategy/engine/command_handlers.py:83-89` (ColonizeCommandHandler) vs `game/strategy/engine/command_handlers.py:325-329` (TransferCommandHandler)
**Issue:** `ColonizeCommandHandler` performs fleet lookup by iterating `session.empires` to find both the fleet and its owning empire (O(n) scan), while all other handlers use `session._get_fleet_by_id()` for fleet lookup. `TransferCommandHandler` also needs the owning empire but finds it separately after the fleet lookup. The "find fleet AND owning empire" pattern exists in two handlers but with different code paths.
**Impact:** Minor inconsistency. `ColonizeCommandHandler` doesn't use the O(1) galaxy fleet registry path that other handlers use via `_get_fleet_by_id()`.
**Recommendation:** Refactor `ColonizeCommandHandler` to use `session._get_fleet_by_id()` for fleet lookup. If owning empire is needed, add a `session._get_empire_for_fleet(fleet_id)` helper or a shared utility method to eliminate the manual empire iteration in both ColonizeCommandHandler and TransferCommandHandler.
**Effort:** Simple

#### MINOR: Superweapon Order Processing Has Repeated Ship-Finding-and-Removal Pattern
**ID:** DUP-STR-009
**Location:** `game/strategy/engine/superweapon_order_processor.py` - lines 110-123 (implode_planet), 284-292 (open_warp_point), 376-384 (close_warp_point), 454-462 (create_dyson_sphere)
**Issue:** Four of the six superweapon processor methods repeat the same "find ship with ability -> fallback to first ship -> remove ship -> check fleet empty" pattern. Each block is ~12 lines and structurally identical, differing only in the ability name string. The pattern is: `ship = SuperweaponValidator.find_ship_with_ability(fleet, ABILITY_NAME, registry); if ship is None: ship = fleet.ships[0]; ... fleet.remove_ship(ship); fleet_consumed = len(fleet.ships) == 0`.
**Impact:** Each superweapon shares the same "consume ship" mechanic. If the consumption logic changes (e.g., consuming multiple ships, or checking ship capacity), four blocks must be updated.
**Recommendation:** Extract `_consume_ability_ship(fleet, ability_name, component_registry) -> bool` that finds, removes, and returns whether fleet is now empty.
**Effort:** Simple

#### INFO: Design Data Layer Iteration Pattern Used Everywhere
**ID:** DUP-STR-010
**Location:** Multiple files - `planet.py:220-231`, `maintenance_engine.py:207-221`, `empire_economy_calculator.py:274-288`, `production_engine.py:75-79`, `harvesting_engine.py:188-199`, `resupply_engine.py:142-155`
**Issue:** The pattern `for layer_data in design_data.get('layers', {}).values(): if not isinstance(layer_data, list): continue; for comp in layer_data: ...` appears in at least 6 different files. Each implements its own version of iterating through design_data layers to find components. The `component_inspector.py` module provides `iterate_design_components()` which handles this pattern with registry lookup, but several callers (particularly the economic engines) don't use it because they need inline ability data or don't have a registry reference.
**Impact:** This is the most pervasive structural pattern in the strategy layer. `component_inspector.iterate_design_components()` was created specifically to consolidate this (per its PROJ-108 docstring), but adoption is incomplete. The remaining instances handle the dual-format issue (list vs dict layers) inconsistently.
**Recommendation:** Extend `iterate_design_components()` to work without a registry (returning inline abilities only) or add a simpler `iterate_layer_components(design_data)` that just handles the layer format normalization. Migrate all callers to use it. This is a high-value consolidation that would eliminate a class of format-handling bugs.
**Effort:** Medium

## Top 5 Priority Issues

1. **DUP-STR-001 (CRITICAL):** 6 mission command handlers with identical boilerplate - highest maintenance risk, simplest fix via base class extraction. ~210 lines reducible to ~60.

2. **DUP-STR-002 (CRITICAL):** `_calculate_maintenance_cost` in 3 classes with duplicated constant - financial calculation code must be authoritative in one place. Risk of rate divergence.

3. **DUP-STR-003 (MAJOR):** `_find_system_at_location` duplicated between validator and processor, with incomplete Galaxy method. Natural consolidation point on Galaxy class.

4. **DUP-STR-004 + DUP-STR-005 (MAJOR):** Harvester/storage ability resolution duplicated across 3 engines (~100 lines). Should use existing `component_inspector` infrastructure.

5. **DUP-STR-006 (MAJOR):** `_spawn_complex` / `_spawn_fleet_complex` duplication within ProductionEngine - same file, same class, easy internal refactor with ~25 shared lines.
