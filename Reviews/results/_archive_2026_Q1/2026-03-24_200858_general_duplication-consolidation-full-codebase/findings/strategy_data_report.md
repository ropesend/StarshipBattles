# Strategy Data Duplication Report

**Scope:** `game/strategy/data/` (39 Python files)
**Date:** 2026-03-24
**Reviewer:** Claude Code Agent

## Summary

The `game/strategy/data/` layer has been through extensive refactoring (PROJ-87, PROJ-173, PROJ-204, PROJ-210, PROJ-212) and is generally well-decomposed. The delegate pattern is applied consistently across Fleet, Galaxy, and ShipInstance. However, several duplication patterns remain, primarily around:

1. **Star generation companion placement** -- nearly identical code in two methods
2. **Planet registration / spatial indexing** -- duplicated between `register_planet` and `restore_planet`
3. **HexCoord deserialization error handling** -- repeated boilerplate across 3+ entity classes
4. **to_dict/from_dict boilerplate** -- structural repetition across many entity classes
5. **Mass generation with constraints** -- similar logic in both StarGenerator and PlanetGenerator
6. **Cargo load/unload fleet aggregation** -- structural mirror pattern

Total findings: 10 (4 MAJOR, 6 MINOR)

---

## Findings

#### MAJOR: Duplicated Companion Star Generation Logic
**ID:** DUP-SD-01
**Location:** `stars.py:445-550` (`generate_from_blueprint`) and `stars.py:552-625` (`_generate_random_stars`)
**Issue:** The companion star generation loop (lines 509-548 in blueprint, lines 591-623 in random) is nearly identical. Both methods:
1. Generate mass for companion
2. Call `_determine_type_and_radius`
3. Call `_map_solar_radius_to_hex_radius`
4. Call `_generate_spectrum`
5. Calculate `target_ring` with same formula `min_dist_hex + (i * 10) + random.randint(2, 8)`
6. Choose location from `hex_ring(target_ring)` with same collision avoidance loop
7. Create `Star(...)` with identical field mapping except `age` uses `primary.age`

The only differences are: (a) mass generation method (`_generate_mass_constrained` vs `_generate_mass`), and (b) how `count` is determined (blueprint vs probability roll).
**Impact:** ~70 lines of near-identical code. Any bug fix or feature change to companion placement must be applied twice.
**Recommendation:** Extract a `_generate_companions(count, primary, mass_generator_fn, min_dist_hex, system_name)` method that both `generate_from_blueprint` and `_generate_random_stars` call.
**Effort:** Simple

---

#### MAJOR: Duplicated Planet Registration (register_planet vs restore_planet)
**ID:** DUP-SD-02
**Location:** `galaxy_entity_registry.py:34-59` (`register_planet`) and `galaxy_entity_registry.py:61-85` (`restore_planet`)
**Issue:** These two methods share the same spatial indexing logic (lines 47-59 and 71-85):
```python
# Add to ID registry
self._galaxy.planets_by_id[planet.id] = planet
# Add to reverse lookup
self._galaxy._planet_to_system[planet] = system
# Add to spatial index (global hex)
global_hex = system.global_location + planet.location
if global_hex not in self._galaxy._global_hex_planets:
    self._galaxy._global_hex_planets[global_hex] = []
self._galaxy._global_hex_planets[global_hex].append(planet)
# Register zone if planet has multi-hex footprint (PROJ-139)
if planet.radius_hexes > 0:
    self.register_zone(system, planet)
```
The ONLY difference is that `register_planet` assigns a new ID first (`planet.id = self._galaxy._next_planet_id`), while `restore_planet` preserves the existing ID.
**Impact:** ~15 lines of identical code. If spatial indexing logic changes, must update both methods.
**Recommendation:** Extract a `_index_planet(system, planet)` private method containing the shared spatial indexing logic. Have `register_planet` call it after ID assignment, and `restore_planet` call it directly.
**Effort:** Simple

---

#### MAJOR: Repeated HexCoord Deserialization Error Handling
**ID:** DUP-SD-03
**Location:** `planet.py:296-309`, `stars.py:178-191`, `storm.py:133-145`, `galaxy.py:52-65` (WarpPoint.from_dict)
**Issue:** Four `from_dict` methods contain the same boilerplate pattern for deserializing a HexCoord with error wrapping:
```python
try:
    location = hex_from_dict(data['location'])
except (KeyError, TypeError) as e:
    raise PersistenceException(
        f"<EntityName>: invalid location data - {type(e).__name__}: {e}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={
            "source": "<EntityName>",
            "field": "location",
            "error_type": type(e).__name__,
            "error": str(e),
        }
    ) from e
```
Each copy differs only in the entity name string and occasionally the context dict fields.
**Impact:** ~12 lines duplicated 4 times = ~48 lines. Error handling changes must be applied to all four.
**Recommendation:** Add a `hex_from_dict_safe(data, field_name, entity_name)` utility function to `game/core/hex_math.py` or `game/core/validation_helpers.py` that wraps the try/except pattern. All four call sites reduce to a single line.
**Effort:** Simple

---

#### MAJOR: Structural Cargo Load/Unload Mirroring in FleetResourceAggregator
**ID:** DUP-SD-04
**Location:** `fleet_resource_aggregator.py:283-307` (`load_cargo_to_fleet`) and `fleet_resource_aggregator.py:309-333` (`unload_cargo_from_fleet`)
**Issue:** These two methods are structural mirrors:
```python
def load_cargo_to_fleet(self, cargo_type, amount):
    remaining = amount; total_loaded = 0
    for ship in self._fleet.ships:
        if remaining <= 0: break
        loaded = ship.load_cargo(cargo_type, remaining)
        total_loaded += loaded; remaining -= loaded
    return total_loaded

def unload_cargo_from_fleet(self, cargo_type, amount):
    remaining = amount; total_unloaded = 0
    for ship in self._fleet.ships:
        if remaining <= 0: break
        unloaded = ship.unload_cargo(cargo_type, remaining)
        total_unloaded += unloaded; remaining -= unloaded
    return total_unloaded
```
The structure is identical -- only the ship method called differs (`load_cargo` vs `unload_cargo`).
**Impact:** ~25 lines of structural duplication. Pattern is already well-established with `_accumulate_ship_costs` and `_verify_and_consume_resources` for other fleet operations -- this one was missed.
**Recommendation:** Extract a `_distribute_to_ships(self, ships, operation_fn, amount)` helper that iterates ships and distributes the amount. Both methods become one-liners.
**Effort:** Simple

---

#### MINOR: Constrained Mass Generation in Both StarGenerator and PlanetGenerator
**ID:** DUP-SD-05
**Location:** `stars.py:627-650` (`StarGenerator._generate_mass_constrained`) and `planet_gen.py:197-240` (`PlanetGenerator._generate_mass_constrained`)
**Issue:** Both generators have similar constrained mass generation methods that:
1. Take min/max constraints
2. Use a log-space distribution (lognormvariate / gauss in log10)
3. Loop up to 100 attempts
4. Fall back to uniform in log space

The implementations differ in details (StarGenerator uses `lognormvariate` on natural log, PlanetGenerator uses `gauss` on log10, and PlanetGenerator adds a `bias` parameter). But the core algorithm structure is the same.
**Impact:** Conceptual duplication rather than exact copy-paste. Both are constrained-random-in-log-space generators.
**Recommendation:** Consider extracting a shared `log_constrained_random(min_val, max_val, center, sigma, max_attempts)` utility to `game/core/math_utils.py` or similar. Low priority since the implementations have legitimate differences.
**Effort:** Medium (need to reconcile log base and bias parameter differences)

---

#### MINOR: Duplicated `_generate_mass` in PlanetGenerator
**ID:** DUP-SD-06
**Location:** `planet_gen.py:197-240` (`_generate_mass_constrained`) and `planet_gen.py:406-428` (`_generate_mass`)
**Issue:** `PlanetGenerator` has two mass generation methods within the same class. `_generate_mass` (the older one) is a simpler version that hardcodes MASS_CERES/MASS_JUPITER range with a fixed gauss(24.5, 1.5). `_generate_mass_constrained` is the newer, more flexible version that accepts constraints and bias.
**Impact:** `_generate_mass` appears to be dead code -- it is not called from `_generate_orbital_slots` (which uses `_generate_mass_constrained`) and not from `_generate_moons` (which uses `_generate_moon_mass`). Need to verify no external callers.
**Recommendation:** Verify `_generate_mass` has no callers and delete it. If it does have callers, replace them with `_generate_mass_constrained(MASS_CERES, MASS_JUPITER)`.
**Effort:** Simple

---

#### MINOR: Repeated `to_dict`/`from_dict` Serialization Boilerplate
**ID:** DUP-SD-07
**Location:** All entity classes: `Fleet`, `Empire`, `Planet`, `ShipInstance`, `Star`, `Storm`, `StormEffect`, `WarpPoint`, `StarSystem`, `Spectrum`, `PlanetaryFacility`, `SpeciesPopulation`, `RaceConfig`, `DesignMetadata`, `FleetOrder`
**Issue:** Every entity class implements nearly the same `to_dict`/`from_dict` pattern:
- `to_dict`: Manual field-by-field dict construction
- `from_dict`: `require_keys()` validation + manual field extraction with `.get()` defaults

This is structural duplication driven by the lack of a serialization framework. Each class does it slightly differently (some use `require_keys`, some use `validate_enum`, some use `safe_from_dict`).
**Impact:** Large volume of boilerplate (~1000+ lines total across all entities), but each class has specific serialization needs (nested objects, enum conversion, validation). Not easily unified without introducing a serialization framework.
**Recommendation:** This is inherent to manual serialization. A `@serializable` decorator or mixin could reduce boilerplate for simple dataclasses, but the complex entities (Fleet, Galaxy, Empire) have enough custom logic that a generic solution would add complexity without much benefit. **Accept as-is** unless a serialization library is adopted project-wide.
**Effort:** Complex (project-wide change for marginal benefit)

---

#### MINOR: Duplicate `can_build_type` Logic Between Planet and FleetCapabilityCalculator
**ID:** DUP-SD-08
**Location:** `planet.py:166-186` (`Planet.can_build_type`) and `fleet_capability_calculator.py:141-169` (`FleetCapabilityCalculator.can_build_type`)
**Issue:** Both implement vehicle type build checks with similar logic:
- Planet: complexes always OK, ships/fighters/satellites need shipyard
- Fleet: needs shipyard for all, complexes additionally need planet proximity

The logic is intentionally different (planet vs fleet have different rules), but the vehicle type string matching (`"ship"`, `"fighter"`, `"satellite"`, `"complex"`) is duplicated. If a new vehicle type is added, both must be updated.
**Impact:** Low -- the BuildContext protocol ensures both are called through the same interface, but the vehicle type constants are not centralized.
**Recommendation:** Extract vehicle type constants (e.g., `VEHICLE_TYPES = {"ship", "fighter", "satellite", "complex"}` and `SHIPYARD_VEHICLE_TYPES = {"ship", "fighter", "satellite"}`) to a shared constants module. This makes it impossible to add a vehicle type in one place but forget the other.
**Effort:** Simple

---

#### MINOR: Duplicated `occupied_hexes` Property Pattern
**ID:** DUP-SD-09
**Location:** `stars.py:116-127` (`Star.occupied_hexes`), `planet.py:117-131` (`Planet.occupied_hexes`), `storm.py:90-99` (`Storm.occupied_hexes`)
**Issue:** Three classes implement the `occupied_hexes` property for the `IZoneOccupant` protocol. Star and Planet both use `hex_circle_filled(self.location, max(0, self.radius_hexes - 1))`. Storm uses `frozenset(self.location + offset for offset in self.hex_offsets)`.
**Impact:** Star and Planet have identical implementations (2 occurrences, ~5 lines each). Storm's is necessarily different. Not severe since `IZoneOccupant` is a protocol, not a base class.
**Recommendation:** Could add a `hex_zone_from_radius(center, radius_hexes)` helper to `hex_math.py` to replace the `hex_circle_filled(location, max(0, radius_hexes - 1))` pattern. Low priority.
**Effort:** Simple

---

#### MINOR: `_facility_is_shipyard` Wrapper in build_queue_source.py
**ID:** DUP-SD-10
**Location:** `build_queue_source.py:114-126` (`_facility_is_shipyard`) and `planetary_facility.py:111-131` (`PlanetaryFacility.is_shipyard`)
**Issue:** `_facility_is_shipyard` is a one-line wrapper that just calls `facility.is_shipyard`. It exists as an intermediate abstraction that adds no value:
```python
def _facility_is_shipyard(facility):
    return facility.is_shipyard
```
This is called in two places within `build_queue_source.py`. It could simply call `facility.is_shipyard` directly.
**Impact:** Trivial code indirection. Not harmful but adds confusion about where the logic actually lives.
**Recommendation:** Inline `_facility_is_shipyard` -- replace all calls with `facility.is_shipyard` directly.
**Effort:** Simple

---

## Top 5 Priority List

| Priority | ID | Title | Effort | Impact |
|----------|----|-------|--------|--------|
| 1 | DUP-SD-01 | Duplicated Companion Star Generation | Simple | ~70 lines, bug risk |
| 2 | DUP-SD-02 | Duplicated Planet Registration/Indexing | Simple | ~15 lines, consistency risk |
| 3 | DUP-SD-03 | Repeated HexCoord Deserialization Boilerplate | Simple | ~48 lines across 4 files |
| 4 | DUP-SD-04 | Mirrored Cargo Load/Unload in Fleet | Simple | ~25 lines, missed consolidation |
| 5 | DUP-SD-06 | Dead `_generate_mass` Method | Simple | Dead code removal |

## Overall Assessment

The codebase is in good shape after the PROJ-87/PROJ-173/PROJ-204 refactoring campaigns. The remaining duplication is mostly in the "last 10%" category -- small patterns that were not caught during larger restructurings. The top 4 findings are all Simple effort and could be addressed in a single focused session. Finding DUP-SD-07 (serialization boilerplate) is the largest by volume but is inherent to manual serialization and not worth addressing without a broader architectural decision.
