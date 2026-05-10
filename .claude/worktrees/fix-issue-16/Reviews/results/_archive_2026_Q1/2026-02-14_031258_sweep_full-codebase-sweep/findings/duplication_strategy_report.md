# Duplication & Fragmentation Sweep: Strategy

## Summary
- **Shard:** Strategy (game/strategy/)
- **Files Scanned:** 82
- **Total Issues Found:** 9
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 2

## Findings

#### MAJOR: Component Ability Extraction Pattern Repeated Across Engines
**ID:** DUP-STR-001
**Location:** `game/strategy/engine/harvesting_engine.py:30-75` AND `game/strategy/engine/resupply_engine.py:126-156` AND `game/strategy/data/build_queue_source.py:80-111`
**Issue:** Three engines implement nearly identical patterns for extracting abilities from component definitions:
1. `get_harvester_info()` / `get_harvester_from_registry()` for ResourceHarvester
2. `_get_fuel_generation_rate()` / `_get_storage_info()` for ResourceGeneration/EmpireStorage
3. `_get_facility_production_rates()` for SpaceShipyard

All follow the same structure:
- Iterate design_data layers
- Check if layer_data is list
- Get component from registry
- Extract specific ability from `getattr(comp_def, 'abilities', {}) or {}`

**Impact:** When ability extraction logic needs to change (e.g., new ability format), all three locations must be updated identically. Risk of drift between implementations.
**Recommendation:** Extract a generic `extract_ability_from_design(design_data, ability_name, registries)` function to `component_inspector.py` or a new `ability_extractor.py` module. Each engine can then specialize only the post-extraction processing.
**Effort:** Medium

#### MAJOR: Layer Iteration Pattern Duplicated in 7+ Locations
**ID:** DUP-STR-002
**Location:**
- `game/strategy/engine/harvesting_engine.py:152-160`
- `game/strategy/engine/harvesting_engine.py:234-245`
- `game/strategy/engine/resupply_engine.py:141-154`
- `game/strategy/engine/maintenance_engine.py:47-62`
- `game/strategy/engine/empire_economy_calculator.py:151-159`
- `game/strategy/engine/resource_management_engine.py:117-138`
- `game/strategy/data/build_queue_source.py:93-111`

**Issue:** The same layer iteration structure appears repeatedly:
```python
for layer_data in design_data.get("layers", {}).values():
    if not isinstance(layer_data, list):
        continue
    for comp in layer_data:
        # ... process component
```
Some locations handle both list format `[comp1, comp2]` and dict format `{"components": [...]}`, others only handle list format, creating inconsistency.

**Impact:** High cognitive overhead understanding which format each location supports. Bug risk when data format varies.
**Recommendation:** The existing `iterate_design_components()` in `component_inspector.py` already handles this pattern. Migrate remaining usages to use this canonical iterator.
**Effort:** Medium

#### MAJOR: Maintenance Cost Calculation Has Near-Duplicate in EmpireEconomyCalculator
**ID:** DUP-STR-003
**Location:** `game/strategy/engine/maintenance_engine.py:28-68` AND `game/strategy/engine/empire_economy_calculator.py:221-233`
**Issue:** Both files implement maintenance cost calculation. While `EmpireEconomyCalculator._calculate_maintenance_cost()` correctly delegates to `calculate_maintenance_cost()`, the iteration over facilities/ships to collect maintenance costs follows similar patterns in both:
- `MaintenanceEngine._process_colony_facilities()` (lines 146-192)
- `MaintenanceEngine._process_fleet_ships()` (lines 194-232)
- `EmpireEconomyCalculator._aggregate_maintenance()` (lines 181-220)

Both iterate: colonies -> facilities -> design_data, and fleets -> ships -> design_data.

**Impact:** Logic for what constitutes "operational" or what should be included is split between two files. Shared constant `MAINTENANCE_RATE` is correctly factored out, but iteration logic is duplicated.
**Recommendation:** Create a `collect_entity_design_data(empire)` generator that yields (entity_type, entity, design_data) tuples for all facilities and ships. Both engine and calculator can consume this.
**Effort:** Medium

#### MINOR: Distance Calculation From Center Repeated
**ID:** DUP-STR-004
**Location:**
- `game/strategy/data/planet_gen.py:304`
- `game/strategy/data/planet_naming.py:52-54`
**Issue:** Both locations compute hex distance to origin using the same formula:
```python
orbit_dist = max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))  # planet_gen.py
key=lambda loc: max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))  # planet_naming.py
```
This is the cube-coordinate hex distance to origin.

**Impact:** Low - formula is simple and correct in both places. Minor cognitive overhead.
**Recommendation:** Could add `hex_distance_to_origin(coord)` helper to `hex_math.py`. Existing `hex_distance(a, b)` could be called with `hex_distance(loc, HexCoord(0,0))` but the direct formula is slightly more efficient.
**Effort:** Simple

#### MINOR: Density Primitive Gaussian Falloff Pattern
**ID:** DUP-STR-005
**Location:**
- `game/strategy/generation/density/primitives/radial.py:45-59`
- `game/strategy/generation/density/primitives/ring.py:47-61`
- `game/strategy/formulas/habitability.py:23-40`
**Issue:** All three files implement Gaussian falloff calculation:
```python
raw_density = peak * math.exp(-distance_sq / (2.0 * sigma_sq))
```
Habitability's `_gaussian_factor()` is well-extracted. Density primitives implement inline.

**Impact:** Low - density primitives are leaf classes unlikely to change. Habitability already factored out the helper.
**Recommendation:** Consider extracting `gaussian_falloff(distance, sigma, peak)` to a shared math utilities module, but this is low priority given the simplicity of the calculation.
**Effort:** Simple

#### MINOR: Fleet-Like Object Creation for Pathfinding
**ID:** DUP-STR-006
**Location:**
- `game/strategy/data/pathfinding.py:275-295` (`_ChaserProxy`)
- `game/strategy/services/fleet_navigation_service.py:173-179` (inline type creation)
**Issue:** Both locations create minimal fleet-like objects to satisfy `find_hybrid_path()` warp capability check:
- `_ChaserProxy` in pathfinding.py is a proper class with `id` and `can_use_warp()`
- `fleet_navigation_service.py` creates an anonymous type with same attributes

**Impact:** Minor inconsistency. If `find_hybrid_path()` signature changes, both must be updated.
**Recommendation:** Use `_ChaserProxy` in both locations, or refactor `find_hybrid_path()` to accept `can_warp: bool` directly instead of requiring a fleet-like object.
**Effort:** Simple

#### MINOR: Roman Numeral Conversion Delegation
**ID:** DUP-STR-007
**Location:**
- `game/strategy/data/naming.py:66-91` (`NameRegistry.to_roman()`)
- `game/strategy/data/planet_naming.py:16-28` (`to_roman()`)
**Issue:** `planet_naming.to_roman()` is a thin wrapper that delegates to `NameRegistry.to_roman()`. The docstring correctly describes this delegation.

**Impact:** None - this is proper delegation pattern, not duplication. The wrapper exists for convenience.
**Recommendation:** None needed. Pattern is intentional and well-documented.
**Effort:** N/A (not an issue)

#### INFO: Consistent Use of Component Inspector
**ID:** DUP-STR-008
**Location:**
- `game/strategy/services/component_inspector.py` (consolidated utilities)
- `game/strategy/data/fleet_capability_calculator.py:67-186` (using `ship_has_ability`, `count_ability`)
- `game/strategy/validation/superweapon_validator.py` (using `find_ship_with_ability`)
- `game/strategy/validation/colonize_validator.py` (using inspector functions)
**Issue:** PROJ-108 successfully consolidated component iteration patterns into `component_inspector.py`. Most validators and capability calculators now use this shared service.

**Impact:** Positive - this is an example of good consolidation. The service provides `get_component_abilities()`, `iterate_design_components()`, `ship_has_ability()`, `find_ship_with_ability()`, and `count_ability()`.
**Recommendation:** Continue migrating remaining ability extraction patterns (DUP-STR-001, DUP-STR-002) to use this inspector.
**Effort:** N/A (observation)

#### INFO: DTO Pattern Well-Applied
**ID:** DUP-STR-009
**Location:**
- `game/strategy/facade/dto/fleet_dto.py`
- `game/strategy/facade/dto/planet_dto.py`
- `game/strategy/facade/dto/empire_dto.py`
- `game/strategy/facade/dto/system_dto.py`
**Issue:** Each DTO has a consistent `from_entity()` class method pattern for converting domain objects to immutable DTOs. This is not duplication but good consistent design.

**Impact:** Positive - each DTO handles its own domain object conversion, there's no shared code that should be extracted since each conversion is domain-specific.
**Recommendation:** None - pattern is correct and consistent.
**Effort:** N/A (observation)

## Top 5 Priority Issues

1. **DUP-STR-002 (MAJOR): Layer Iteration Pattern** - Most widespread duplication (7+ locations). Migrating to `iterate_design_components()` would significantly reduce code repetition and ensure consistent handling of both layer formats.

2. **DUP-STR-001 (MAJOR): Component Ability Extraction** - Three engines have similar ability extraction code. A generic extraction utility would reduce maintenance burden when ability format changes.

3. **DUP-STR-003 (MAJOR): Maintenance Iteration Duplication** - MaintenanceEngine and EmpireEconomyCalculator both iterate empire entities. A shared entity collector would ensure consistent behavior.

4. **DUP-STR-006 (MINOR): Fleet-Like Object for Pathfinding** - Low effort fix that would improve consistency. Could either reuse `_ChaserProxy` or refactor `find_hybrid_path()` signature.

5. **DUP-STR-004 (MINOR): Distance to Origin** - Simple helper extraction. Low priority but would be a clean improvement to hex_math module.
