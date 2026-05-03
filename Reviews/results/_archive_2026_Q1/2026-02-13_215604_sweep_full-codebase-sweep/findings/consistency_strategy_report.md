# Consistency Violations Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 92
- **Total Issues Found:** 17
- **Critical:** 1 | **Major:** 6 | **Minor:** 7 | **Info:** 3

## Findings

#### CRITICAL: Method Returns Inconsistent Types for Not-Found
**ID:** CON-STR-001
**Location:** `game/strategy/data/pathfinding.py:26-105` vs `game/strategy/data/galaxy.py`
**Issue:** `find_path_interstellar()` returns `None` when no path exists, while most path/find methods throughout the codebase return empty lists. This mixed return type pattern can cause subtle bugs where callers check `if path:` expecting empty list behavior.
**Impact:** Code calling pathfinding functions must handle both `None` and empty list cases, increasing bug risk and cognitive load.
**Recommendation:** Standardize on returning empty list `[]` for "no path found" across all pathfinding functions. The established pattern in `find_path_deep_space()` returns a list - follow that.
**Effort:** Simple

---

#### MAJOR: Inconsistent Method Verb Prefixes for Retrieval
**ID:** CON-STR-002
**Location:** Multiple files
**Issue:** Mixed verb prefixes for retrieval operations:
- `get_*`: `get_planets_at_global_hex()`, `get_system_by_name()`, `get_next_fleet_id()`
- `find_*`: `find_path_deep_space()`, `find_hybrid_path()`, `find_nearest_system()`, `find_ship_with_ability()`
- `collect_*`: `collect_build_queues_at_hex()`, `collect_movements()`
- `calculate_*`: `calculate_intercept_point()` (which also finds/returns data)
**Impact:** Developers cannot predict method names without looking them up. `get_` implies direct lookup, `find_` implies search, but usage is inconsistent.
**Recommendation:** Establish convention: `get_*` for O(1) lookups, `find_*` for searches that may fail (return None), `collect_*` for aggregating multiple items into a list. Update method names to match.
**Effort:** Medium

---

#### MAJOR: Validator Classes Use Static Methods While Other Services Use Instance Methods
**ID:** CON-STR-003
**Location:** `game/strategy/validation/*.py` vs `game/strategy/services/*.py`
**Issue:** All validators (`ColonizeValidator`, `SuperweaponValidator`, `TransferValidator`) use `@staticmethod` for all methods, while services (`ShipStatsCalculator`, `FleetSpeedCalculator`, `HarvestingEngine`) use instance methods with constructor injection. This is inconsistent DI approach.
**Impact:** Validators cannot benefit from DI - they require registry/galaxy to be passed to every call. Makes testing harder and violates the project's DI preference.
**Recommendation:** Convert validators to instance-based pattern with constructor injection like `ShipStatsCalculator`:
```python
class ColonizeValidator:
    def __init__(self, registries: GameRegistries):
        self._registries = registries

    def validate(self, galaxy, fleet, target_planet, ...):
        ...
```
**Effort:** Medium

---

#### MAJOR: Mixed Error Handling Patterns
**ID:** CON-STR-004
**Location:** `game/strategy/validation/*.py`, `game/strategy/engine/fleet_order_processor.py`
**Issue:** `ValidationResult` uses `errors=["message"]` list, but some code checks `validation.message` (singular). Return patterns vary:
- Validators return `ValidationResult(is_valid=False, errors=[...])`
- Some methods return `Optional[T]` with `None` for failure
- Order processors return dataclass results like `ColonizeResult(colonized=False)`
**Impact:** Inconsistent error handling forces callers to know each function's return style.
**Recommendation:** Standardize: business validation returns `ValidationResult`, operations return operation-specific result dataclasses with success/failure booleans. Never use `None` to indicate failure when a result type exists.
**Effort:** Medium

---

#### MAJOR: Inconsistent Parameter Naming for Same Concepts
**ID:** CON-STR-005
**Location:** Multiple files
**Issue:** Same concept uses different parameter names:
- Planet references: `planet`, `colony`, `target_planet`, `final_planet`, `colony_or_fleet`
- Fleet references: `fleet`, `target_fleet`, `chaser`, `source_fleet`
- Component lookup: `component_registry`, `comp_registry`, `registries.components`
- Save path: `save_path`, `savegame_path`
**Impact:** Increases cognitive load; developers must remember multiple names for the same thing.
**Recommendation:** Standardize:
- `planet` for planet objects, `colony` only when discussing owned planets
- `fleet` for fleet objects, `target_fleet` when there's a source/target distinction
- `component_registry` (never abbreviated `comp_registry`)
- `save_path` consistently
**Effort:** Medium

---

#### MAJOR: Inconsistent Docstring Style
**ID:** CON-STR-006
**Location:** Multiple files
**Issue:** Mix of docstring formats:
- Google-style with Args/Returns sections (majority): `game/strategy/engine/*.py`
- Single-line summaries only (no Args): some `game/strategy/data/*.py` methods
- Missing docstrings entirely: several private helper methods
**Impact:** Inconsistent documentation quality across the module.
**Recommendation:** Standardize on Google-style docstrings with Args/Returns for all public methods. Private methods (`_*`) should have at least a one-line summary.
**Effort:** Medium

---

#### MAJOR: Import Organization Inconsistency
**ID:** CON-STR-007
**Location:** Multiple files
**Issue:** Import organization varies:
- Most files: stdlib, then third-party, then local
- Some files mix `from game.core.logger import ...` with `from game.strategy.data.fleet import ...` without blank line separation
- TYPE_CHECKING imports sometimes at top, sometimes after regular imports
**Impact:** Makes code harder to scan and violates PEP8 convention.
**Recommendation:** Enforce consistent pattern:
```python
# Standard library
from typing import ...

# Third-party (if any)

# Local imports - game.core first
from game.core.logger import ...
from game.core.hex_math import ...

# Local imports - game.strategy
from game.strategy.data.fleet import ...

# TYPE_CHECKING block at end
if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy
```
**Effort:** Simple

---

#### MINOR: Boolean Naming Inconsistency
**ID:** CON-STR-008
**Location:** `game/strategy/data/fleet.py`, `game/strategy/engine/*.py`
**Issue:** Boolean attribute/method naming inconsistent:
- Properties with `is_*`: `is_building`, `is_operational`, `is_combat_capable()`
- Properties with `has_*`: `has_space_shipyard`, `has_resources()`
- Properties with `can_*`: `can_use_warp()`, `can_build_ships`
- No prefix: `merged`, `colonized`, `stranded` (in result dataclasses)
**Impact:** Minor inconsistency but predictable - result dataclass booleans describe outcomes.
**Recommendation:** Formalize: instance properties use `is_/has_/can_`, result dataclasses use bare past-tense verbs (`merged`, `colonized`). This pattern is actually consistent, just undocumented.
**Effort:** Simple (documentation only)

---

#### MINOR: Magic Numbers in Formulas
**ID:** CON-STR-009
**Location:** `game/strategy/services/fleet_speed_calculator.py:30-32`, `game/strategy/formulas/habitability.py:44-50`
**Issue:** Some magic numbers are properly named constants:
```python
K_STRATEGIC = 25  # Good - named constant
MAX_HEXES_PER_TURN = 10
```
But others are inline:
```python
founding_pop = 100  # fleet_order_processor.py:481
sigma = max(tolerance, 0.01)  # habitability.py - min_sigma default
```
**Impact:** Hard to understand meaning of bare numbers; harder to tune gameplay.
**Recommendation:** Extract all gameplay-tuning numbers to named constants at module or class level.
**Effort:** Simple

---

#### MINOR: Inconsistent __all__ Exports
**ID:** CON-STR-010
**Location:** Various `__init__.py` files
**Issue:** Some packages define `__all__` exports, others don't:
- `game/strategy/interfaces/__init__.py`: No `__all__`, just imports
- `game/strategy/services/__init__.py`: Empty file
- `game/strategy/validation/__init__.py`: Has `__all__` with exports
- `game/strategy/facade/dto/__init__.py`: Has exports
**Impact:** Unclear public API surface; IDE autocomplete less useful.
**Recommendation:** Add `__all__` to all `__init__.py` files that export anything. Empty `__init__.py` is acceptable for package markers.
**Effort:** Simple

---

#### MINOR: Result Dataclass Naming Convention
**ID:** CON-STR-011
**Location:** `game/strategy/engine/fleet_order_processor.py`, `game/strategy/engine/fleet_movement_engine.py`
**Issue:** Most result dataclasses use `*Result` suffix (`ColonizeResult`, `JoinFleetResult`, `TransferResult`, `MovementResult`), but `game/strategy/interfaces/battle_resolver.py` uses `BattleResult` which could conflict with simulation layer naming.
**Impact:** Minor - naming is consistent within strategy layer.
**Recommendation:** Keep current convention - `*Result` for operation outcomes. Document that `BattleResult` in strategy layer is distinct from simulation layer concepts.
**Effort:** Simple (documentation only)

---

#### MINOR: Engine Class Naming vs Interface Naming
**ID:** CON-STR-012
**Location:** `game/strategy/interfaces/engines.py`, `game/strategy/engine/*.py`
**Issue:** Interfaces use `I*Engine` pattern (`IMovementEngine`, `IProductionEngine`), implementations drop the `I` prefix (`FleetMovementEngine`, `ProductionEngine`). This is correct, but some engines don't have interfaces:
- `GameSession`: No interface
- `EmpireEconomyCalculator`: No interface (is it an engine or calculator?)
**Impact:** Unclear which engines are meant to be injected via interface vs direct instantiation.
**Recommendation:** Either create interfaces for all engines used by TurnEngine, or document which engines are injectable vs internal implementation details.
**Effort:** Medium

---

#### MINOR: Underscore Prefix Inconsistency for Private Members
**ID:** CON-STR-013
**Location:** `game/strategy/engine/harvesting_engine.py`, `game/strategy/data/pathfinding.py`
**Issue:** Module-level helper functions sometimes use underscore prefix, sometimes don't:
- `_iterate_colony_pods()` - private helper (correct)
- `_ChaserProxy` - private class (correct)
- `get_harvester_info()` - module-level, no underscore (should be `_get_harvester_info`?)
- `find_path_deep_space()` - public API (correctly no underscore)
**Impact:** Unclear which functions are internal implementation vs public API.
**Recommendation:** Use underscore for all module-level helpers not meant for external use. Only export public functions in `__all__`.
**Effort:** Simple

---

#### MINOR: Type Hint Usage Gaps
**ID:** CON-STR-014
**Location:** Various engine files
**Issue:** Most files have comprehensive type hints, but some methods skip return types or use `Any`:
- `process_harvesting(self, empires: List) -> None` - `List` without type parameter
- `_spawn_ship(..., galaxy, ...)` - `galaxy` has no type hint
- Heavy use of `Dict[str, Any]` for design_data when more specific types exist
**Impact:** Reduced IDE support and type checking effectiveness.
**Recommendation:** Use `List[Empire]` instead of bare `List`, add type hints to all parameters. Consider creating TypedDict for design_data structures.
**Effort:** Medium

---

#### INFO: Adapter Pattern Usage
**ID:** CON-STR-015
**Location:** `game/strategy/adapters/simulation_adapter.py`, `game/strategy/data/pathfinding.py:275-296`
**Issue:** Two adapter patterns exist - one in dedicated `adapters/` folder, one inline in pathfinding (`_ChaserProxy`). Both are valid but located differently.
**Impact:** Low - both are documented and intentional.
**Recommendation:** Consider moving `_ChaserProxy` to adapters if it grows. Current location is acceptable for a small internal adapter.
**Effort:** Simple (optional)

---

#### INFO: Formula Module Organization
**ID:** CON-STR-016
**Location:** `game/strategy/formulas/`
**Issue:** Only one formula module (`habitability.py`) exists while other formulas are embedded in calculators (`FleetSpeedCalculator`). The project has a clear formulas pattern in `game/simulation/formulas/`.
**Impact:** Low - current organization is acceptable for small number of formulas.
**Recommendation:** As formula count grows, consider extracting more to `formulas/` module (e.g., `formulas/movement.py` for `K_STRATEGIC` and speed calculations).
**Effort:** Simple (future consideration)

---

#### INFO: Event System Pattern Adherence
**ID:** CON-STR-017
**Location:** `game/strategy/events/`
**Issue:** Event system uses `EventType` enum and `EventCategory` enum with `log_event()` function. This pattern is consistently followed across engines. Good adherence to established pattern.
**Impact:** None - this is an observation of good consistency.
**Recommendation:** Continue following this pattern for all new event logging.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **CON-STR-001 (CRITICAL)**: `find_path_interstellar()` returns `None` vs empty list inconsistency - can cause runtime bugs when callers assume list return type.

2. **CON-STR-003 (MAJOR)**: Validators use static methods instead of constructor injection - violates project's DI preference and makes testing harder.

3. **CON-STR-005 (MAJOR)**: Inconsistent parameter naming (`planet` vs `colony`, `component_registry` variations) - increases cognitive load across the codebase.

4. **CON-STR-002 (MAJOR)**: Mixed `get_/find_/collect_/calculate_` verb prefixes - developers cannot predict method names without looking them up.

5. **CON-STR-007 (MAJOR)**: Import organization inconsistency - while individually minor, this affects every file and violates PEP8 conventions.
