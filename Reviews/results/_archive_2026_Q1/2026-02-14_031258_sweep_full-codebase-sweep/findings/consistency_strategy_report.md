# Consistency Violations Sweep: Strategy

## Summary
- **Shard:** Strategy (game/strategy/)
- **Files Scanned:** 93
- **Total Issues Found:** 14
- **Critical:** 0 | **Major:** 4 | **Minor:** 8 | **Info:** 2

## Findings

#### MAJOR: Inconsistent Method Verb Prefixes for Lookup Operations
**ID:** CON-STR-001
**Location:** Multiple files across `game/strategy/`
**Issue:** Lookup operations use inconsistent verb prefixes: `get_` (dominant), `find_`, and `load_`. The pattern varies without clear semantic distinction.
**Examples:**
- `get_planet_by_id()` vs `find_ship_with_colony_pod()` vs `load_design_data()`
- `get_system_by_name()` vs `find_path_interstellar()` vs `find_nearest_system()`
- `get_race()` in `race_library.py` vs `load_test_race()` in `quickstart_builder.py`

**Established Convention:** `get_` is used 60+ times for retrieval, `find_` 8 times, `load_` 5 times.
**Impact:** Cognitive overhead when determining which method to use; inconsistent API expectations.
**Recommendation:** Standardize on:
- `get_X()` for simple lookups by ID/key (returns object or None)
- `find_X()` for complex searches with conditions (may return None or list)
- `load_X()` for I/O operations from disk/network
**Effort:** Medium

---

#### MAJOR: Mixed Return Type Patterns for Not-Found Cases
**ID:** CON-STR-002
**Location:** `game/strategy/services/ship_stats_calculator.py:70`, `game/strategy/engine/game_config.py:159-163`, `game/strategy/systems/design_library.py:207-224`
**Issue:** Some methods raise exceptions on invalid input while similar methods return None. No clear pattern for when to use which approach.
**Examples:**
- `ShipStatsCalculator.__init__()` raises `TypeError` if registries is None
- `DesignLibrary.load_design_data()` returns None if design not found
- `GameConfig.__init__()` raises `ValueError` for invalid player count
- `Galaxy.get_planet_by_id()` returns None if planet not found

**Impact:** Callers cannot predict error handling behavior; may miss error cases or add unnecessary try/catch blocks.
**Recommendation:** Establish convention:
- Raise exceptions for programmer errors (missing required dependencies)
- Return None for runtime "not found" cases
- Document pattern in CLAUDE.md under Key Conventions
**Effort:** Medium

---

#### MAJOR: Inconsistent Static Method vs Instance Method Usage
**ID:** CON-STR-003
**Location:** `game/strategy/validation/*.py`, `game/strategy/services/ship_stats_calculator.py`
**Issue:** Similar validation/calculation operations use different method types without clear rationale.
**Examples:**
- `ColonizeValidator.validate()` is `@staticmethod`
- `TransferValidator.validate()` is `@staticmethod`
- `ShipStatsCalculator.calculate_stats()` is instance method
- `ShipStatsCalculator.get_component_effectiveness()` is `@staticmethod`
- Helper functions like `_gaussian_factor()` in `habitability.py` are module-level functions

**Impact:** Inconsistent calling patterns; unclear when to instantiate vs use static methods.
**Recommendation:** Validators with no state should use class methods or be converted to module-level functions. Methods that need registries should consistently use instance methods with DI.
**Effort:** Medium

---

#### MAJOR: Inconsistent Type Hint Coverage
**ID:** CON-STR-004
**Location:** `game/strategy/data/pathfinding.py`, `game/strategy/engine/fleet_order_processor.py`, `game/strategy/engine/production_engine.py`
**Issue:** Type hint usage is inconsistent. Some modules have complete type hints; others have partial or missing hints.
**Examples with missing/partial hints:**
- `pathfinding.py:162` `find_hybrid_path(galaxy, start_hex, end_hex, fleet=None)` - no type hints on parameters
- `fleet_order_processor.py:119` `empire` parameter has no type hint: `def process_join_fleet(self, fleet: Fleet, empire, galaxy)`
- `production_engine.py:339` `def process_production(self, empires: List, galaxy=None...)` - `List` without type parameter

**Established Convention:** Per CLAUDE.md - "Use type hints for function signatures"
**Impact:** Reduced IDE support; harder static analysis; inconsistent documentation quality.
**Recommendation:** Add complete type hints to all public method signatures.
**Effort:** Simple (but tedious)

---

#### MINOR: Inconsistent Boolean Naming Prefixes
**ID:** CON-STR-005
**Location:** `game/strategy/data/fleet.py`, `game/strategy/data/planet.py`, `game/strategy/facade/dto/fleet_dto.py`
**Issue:** Boolean attributes/methods use inconsistent prefixes: `is_`, `has_`, `can_` mixed with unprefixed booleans.
**Examples:**
- `fleet.is_building` (correct)
- `fleet.has_space_shipyard` (correct)
- `fleet.can_use_warp()` (correct)
- `FleetInfo.has_orders` (correct)
- `PlanetaryFacility.is_operational` (correct)
- However: `fleet.orders` checked with `len(fleet.orders) > 0` instead of a `has_orders` property

**Impact:** Minor cognitive load; generally good consistency in this area.
**Recommendation:** Add `has_orders` property to `Fleet` class for consistency with `FleetInfo.has_orders`.
**Effort:** Simple

---

#### MINOR: Inconsistent Docstring Format
**ID:** CON-STR-006
**Location:** Multiple files across `game/strategy/`
**Issue:** Docstrings use mixed formats (Google style vs simple descriptions). Some public methods lack docstrings entirely.
**Examples:**
- `ship_stats_calculator.py` uses Google-style docstrings with Args/Returns sections
- `pathfinding.py` has mixed: some functions have full docstrings, `_ChaserProxy` class has detailed docstring, but helper functions are sparse
- `fleet_resource_aggregator.py` methods have minimal or no docstrings
- `habitability.py` has excellent, consistent Google-style docstrings

**Established Convention:** Per CLAUDE.md - "Add docstrings to public APIs"
**Impact:** Inconsistent documentation quality; harder onboarding for new developers.
**Recommendation:** Standardize on Google-style docstrings for all public methods. Add docstrings to undocumented public methods.
**Effort:** Medium

---

#### MINOR: Inconsistent Import Organization
**ID:** CON-STR-007
**Location:** `game/strategy/engine/command_handlers.py`, `game/strategy/adapters/simulation_adapter.py`
**Issue:** Some files import at module level while others import inside functions. Import grouping is inconsistent.
**Examples:**
- `command_handlers.py` imports `FleetOrder, OrderType` inside each handler method
- `simulation_adapter.py` imports simulation layer at module level
- `fleet_order_processor.py` imports `ColonizeValidator` inside methods

**Impact:** Harder to see dependencies at a glance; potential performance impact from repeated imports (though Python caches).
**Recommendation:** Move stable, non-circular imports to module level. Only use function-level imports to break circular dependencies, and document why.
**Effort:** Simple

---

#### MINOR: Mixed Parameter Ordering Conventions
**ID:** CON-STR-008
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`
**Issue:** Validator methods use slightly different parameter orderings for similar operations.
**Examples:**
- `ColonizeValidator.validate(galaxy, fleet, target_planet, component_registry, skip_chain_check)`
- `TransferValidator.validate(galaxy, fleet, planet, cargo_type, direction, amount, species_id)`

The `galaxy` parameter comes first in both, which is good. However:
- `ColonizeValidator` has optional `component_registry` as 4th param
- The `fleet` parameter is consistently second (good)

**Impact:** Low - the pattern is mostly consistent.
**Recommendation:** This is acceptable natural variation due to different requirements. Document the pattern (galaxy first, then subject entity).
**Effort:** None needed

---

#### MINOR: Inconsistent `__init__.py` Export Patterns
**ID:** CON-STR-009
**Location:** `game/strategy/*/` package directories
**Issue:** Some packages export their public API explicitly in `__init__.py`, others are empty or partial.
**Examples:**
- `game/strategy/services/__init__.py` - empty
- `game/strategy/validation/__init__.py` - exports validators
- `game/strategy/interfaces/__init__.py` - exports interfaces
- `game/strategy/facade/__init__.py` - empty (should export facade classes)
- `game/strategy/engine/__init__.py` - file doesn't exist (missing)

**Impact:** Inconsistent import patterns required; `from game.strategy.services import ShipStatsCalculator` doesn't work.
**Recommendation:** Add public API exports to all package `__init__.py` files for consistent imports.
**Effort:** Simple

---

#### MINOR: Inconsistent Use of Dataclass vs Regular Class
**ID:** CON-STR-010
**Location:** `game/strategy/data/`, `game/strategy/facade/dto/`
**Issue:** Similar data-holding classes use different patterns. Some use `@dataclass`, others use regular classes with `__init__`.
**Examples:**
- `FleetOrder` uses `@dataclass` (correct for simple data)
- `Fleet` uses regular class with `__init__` (correct - has complex logic)
- `Event` uses `@dataclass` (correct)
- `ShipInstance` uses regular class (correct - has complex methods)
- DTOs in `facade/dto/` all use `@dataclass(frozen=True)` (excellent consistency)

**Impact:** Low - the pattern is mostly appropriate to each case.
**Recommendation:** This is acceptable. DTOs should use `@dataclass(frozen=True)`, domain objects with behavior use regular classes.
**Effort:** None needed

---

#### MINOR: Inconsistent Error Message Format
**ID:** CON-STR-011
**Location:** `game/strategy/systems/save_game_service.py`, `game/strategy/engine/command_handlers.py`
**Issue:** Error messages use different formats: some include context, others are brief.
**Examples:**
- `SaveGameService`: "Save file corrupted: Missing metadata fields: {fields}" (good - contextual)
- `ColonizeCommandHandler`: "Fleet not found." (brief)
- `TransferValidator`: returns `ValidationResult(is_valid=False, errors=["Planet not at fleet location"])` (good)
- Some validators return error codes, others don't

**Impact:** Inconsistent user experience; harder debugging.
**Recommendation:** Standardize error messages to include: what failed, why, and context (IDs where applicable).
**Effort:** Simple

---

#### MINOR: Magic Numbers Not Extracted to Constants
**ID:** CON-STR-012
**Location:** `game/strategy/formulas/habitability.py`, `game/strategy/data/pathfinding.py`, `game/strategy/engine/population_engine.py`
**Issue:** Some numeric values are extracted to named constants, others are inline.
**Examples:**
- `habitability.py:20` `STANDARD_GRAVITY_MS2 = 9.81` (correct)
- `habitability.py:44-50` `FACTOR_WEIGHTS` dict (correct)
- `pathfinding.py:110` `radius: int = 50` - default search radius is hardcoded
- `fleet_order_processor.py:481` `founding_pop = 100` - magic number for minimum seed population
- `project_fleet_path()` uses `max_turns=10` and `max_turns=50` in different places

**Impact:** Harder to tune game balance; unclear what values represent.
**Recommendation:** Extract gameplay-significant values to named constants in a constants module or config.
**Effort:** Simple

---

#### INFO: Intentional Pattern Variations
**ID:** CON-STR-013
**Location:** `game/strategy/data/pathfinding.py:275-296`
**Issue:** `_ChaserProxy` class is documented as an intentional adapter pattern, not legacy compatibility.
**Context:** The docstring explicitly states "This is an intentional adapter pattern (not legacy compatibility)" which is excellent documentation of a design decision.
**Impact:** None - this is good practice.
**Recommendation:** This pattern of documenting intentional deviations is excellent. Adopt it elsewhere.
**Effort:** N/A

---

#### INFO: Well-Organized Facade Pattern
**ID:** CON-STR-014
**Location:** `game/strategy/facade/`
**Issue:** The facade package follows excellent organizational patterns with DTOs in a sub-package and clear separation.
**Context:** `StrategySessionFacade` provides a clean public API, DTOs are immutable with `@dataclass(frozen=True)`, and factory methods (`from_fleet()`) provide clean conversion.
**Impact:** Positive - this is a model for other packages.
**Recommendation:** Document this as the reference implementation for facade patterns in the project.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **CON-STR-001 - Inconsistent Method Verb Prefixes**: Establish clear `get_`/`find_`/`load_` conventions to reduce API confusion. High cognitive impact across the entire codebase.

2. **CON-STR-002 - Mixed Return Type Patterns**: Document and enforce when to raise vs return None. This affects error handling reliability throughout the strategy layer.

3. **CON-STR-004 - Inconsistent Type Hint Coverage**: Per CLAUDE.md requirements, all public method signatures should have type hints. Critical for IDE support and static analysis.

4. **CON-STR-003 - Static vs Instance Method Confusion**: Clarify when validators/calculators should use static methods vs instance methods with DI.

5. **CON-STR-009 - Missing `__init__.py` Exports**: Add public API exports for consistent import patterns. Simple fix with broad usability improvement.
