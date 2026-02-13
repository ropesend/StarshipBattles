# Consistency Review: game/strategy/

**Review Date:** 2026-02-13
**Scope:** 95 Python files in `game/strategy/`
**Reviewer:** Sweep Agent (Opus 4.5)

---

## Executive Summary

The strategy layer demonstrates strong overall consistency with well-established patterns. The codebase follows Registry pattern, Command/Handler pattern, DTO pattern for facade, and clean interface separation. Most deviations are MINOR or INFO level, with a few MAJOR items warranting attention.

**Findings by Severity:**
- CRITICAL: 0
- MAJOR: 4
- MINOR: 12
- INFO: 8

---

## MAJOR Findings

### M1. Inconsistent Return Type: validate() Methods

**Location:** Multiple validator classes
**Pattern Violated:** API design consistency - return type patterns

**Files Affected:**
- `validation/colonize_validator.py` - Returns `ValidationResult`
- `validation/transfer_validator.py` - Returns `ValidationResult`
- `validation/superweapon_validator.py` - Returns `ValidationResult`
- `data/race_config.py` - Returns `tuple[bool, str]` (line 280)

**Issue:** `RaceConfig.validate()` returns `tuple[bool, str]` while all other validators return `ValidationResult`. This breaks the consistent validator pattern and requires special handling at call sites.

**Recommendation:** Refactor `RaceConfig.validate()` to return `ValidationResult` for consistency with other validators.

---

### M2. Missing Type Hints on Public API Methods

**Location:** Multiple files
**Pattern Violated:** Type hint consistency for public APIs

**Files Affected:**
- `data/naming.py` - `to_roman(n)` missing return type hint (line 67)
- `data/planet_gen.py` - Several methods missing full type hints (`_generate_surface_flags`, `_determine_type`)
- `data/stars.py` - `StarGenerator` methods missing type hints (`_generate_mass`, `_determine_type_and_radius`, `_kelvin_to_rgb`)

**Recommendation:** Add complete type hints to all public methods following the pattern established in newer files.

---

### M3. Inconsistent Error Handling: Some Methods Use Exceptions, Others Return Validation

**Location:** Multiple engine and service files
**Pattern Violated:** Error handling pattern consistency

**Examples:**
- `data/classification_config.py:get_classification_config()` - Catches broad exception list and falls back silently (lines 140-144)
- `data/naming.py:NameRegistry.load_data()` - Catches broad exceptions but only logs
- `systems/design_library.py` - Mixed approach between raising and returning

**Recommendation:** Establish clear convention: validators return ValidationResult, load operations should use Optional return or explicit exceptions with documented contract.

---

### M4. Inconsistent Docstring Format in Validation Helpers

**Location:** `data/race_config.py`
**Pattern Violated:** Docstring consistency

**Issue:** Private validation helper methods (`_validate_required_fields`, `_validate_environment_ranges`, etc.) lack docstrings, while similar private methods in other files have them.

**Recommendation:** Add brief docstrings to validation helper methods for consistency.

---

## MINOR Findings

### m1. Naming Convention: `_get_default_*` vs `get_default_*` Functions

**Location:** Module-level functions
**Pattern Violated:** Naming consistency for factory functions

**Examples:**
- `engine/game_config.py` - `_get_default_asset_path()` (private prefix)
- `engine/game_config.py` - `_get_default_players()` (private prefix)
- `data/fleet_capability_calculator.py` - `_get_default_component_registry()` (private prefix)

**Observation:** These are module-level factory functions. The underscore prefix is technically correct since they're module-private, but could be public utilities. Consistent with codebase pattern.

---

### m2. Inconsistent Parameter Naming: `data` vs `data_dict` vs `config`

**Location:** `from_dict()` class methods
**Pattern Violated:** Parameter naming consistency

**Examples:**
- Most classes use `data` parameter
- `engine/game_config.py:GameConfig.from_dict()` uses `data`
- Pattern is consistent across codebase

**Status:** Verified consistent - no action needed.

---

### m3. Static Method vs Class Method Inconsistency

**Location:** Validator classes
**Pattern Violated:** Method type consistency

**Issue:** All validator methods are `@staticmethod` but could benefit from being class methods if class-level configuration is added later. This is a minor design consideration.

**Files:**
- `validation/colonize_validator.py` - All static
- `validation/transfer_validator.py` - All static
- `validation/superweapon_validator.py` - All static

**Recommendation:** Document that validators are intentionally stateless with static methods.

---

### m4. Inconsistent Import Grouping Order

**Location:** Various files
**Pattern Violated:** Import ordering (stdlib, third-party, local)

**Examples with minor deviations:**
- `data/physics.py` - TYPE_CHECKING import between stdlib and local
- `data/stars.py` - Missing blank line between import groups

**Recommendation:** Run isort or similar tool to standardize import ordering.

---

### m5. Inconsistent Class Suffix Patterns

**Location:** Various data classes
**Pattern Violated:** Class naming conventions

**Observation:** The codebase uses several suffixes consistently:
- `*Engine` for turn processing engines (correct)
- `*Calculator` for pure calculation classes (correct)
- `*Processor` for order/command processors (correct)
- `*Validator` for validation classes (correct)
- `*Adapter` for layer bridges (correct)
- `*Service` for services (correct)
- `*Info` / `*Summary` for DTOs (correct)

**Status:** Naming conventions are well-established and consistently followed.

---

### m6. Missing `__all__` Export in Some `__init__.py` Files

**Location:** Package init files
**Pattern Violated:** Module export consistency

**Files Missing `__all__`:**
- `services/__init__.py` - Empty file
- `data/__init__.py` - Empty file
- `facade/__init__.py` - Has docstring but no exports

**Recommendation:** Add explicit `__all__` exports to all package init files for clarity.

---

### m7. Inconsistent Late Import Documentation

**Location:** Various files with late imports
**Pattern Violated:** Import documentation pattern

**Good Example (documented):**
```python
# INTENTIONAL LATE IMPORT: Query operation, service encapsulates warp logic
# See docs/ARCHITECTURE.md "Intentional Late Imports" section
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
```

**Examples Missing Documentation:**
- Several files have late imports without the standard comment block
- `engine/game_initializer.py` line 62 - late import of RaceConfig
- Various validation methods with late imports

**Recommendation:** Add consistent "INTENTIONAL LATE IMPORT" comments to all late imports.

---

### m8. Dataclass vs Regular Class Inconsistency

**Location:** Data model classes
**Pattern Violated:** Class type consistency

**Observation:**
- DTOs correctly use `@dataclass(frozen=True)` pattern
- Domain objects use `@dataclass` appropriately
- Some configuration classes use plain classes where dataclasses would fit

**Example:**
- `ClassificationConfig` is a plain class storing config values - could be a dataclass

**Status:** Generally consistent; this is a minor observation.

---

### m9. Inconsistent Property vs Method Naming

**Location:** Query methods on domain objects
**Pattern Violated:** Naming pattern for computed values

**Pattern Observed:**
- Properties for simple computed values (`@property`)
- Methods for operations that may have side effects or complex computation

**Example Inconsistency:**
- `Fleet.has_space_shipyard` is a property
- `Fleet.can_use_warp()` is a method (delegates to calculator)
- `Fleet.get_combat_capable_ships()` is a method

**Recommendation:** Document convention: properties for O(1) lookups, methods for O(n) operations.

---

### m10. Missing Protocol Usage for Duck-Typed Parameters

**Location:** Engine and processor classes
**Pattern Violated:** Type safety with protocols

**Issue:** Many methods accept `Any` type for parameters that actually expect specific duck-type interfaces.

**Examples:**
- `empire_economy_calculator.py:calculate(empire)` - empire param is `Any`
- `command_handlers.py` - cmd param is `Any` (could be Protocol)
- Various validator methods accept `Any` for galaxy, fleet, planet

**Recommendation:** Define protocols for commonly duck-typed interfaces (Empire, Galaxy, Fleet, Planet protocols).

---

### m11. Inconsistent Logging Patterns

**Location:** Various files
**Pattern Violated:** Logging consistency

**Observation:** Codebase uses `game.core.logger` with consistent functions:
- `log_info()` for information
- `log_warning()` for warnings
- `log_error()` for errors
- `log_event()` for game events
- `log_debug()` for debug info

**Minor Issue:** Some files import all log functions, others only what they need.

**Status:** Functional pattern is consistent; import style varies slightly.

---

### m12. Optional Parameter Default Values

**Location:** Various method signatures
**Pattern Violated:** None vs Optional pattern consistency

**Observation:** Codebase consistently uses:
- `param: Optional[Type] = None` pattern
- `param: Type = None` (less explicit but acceptable)

**Status:** Generally consistent.

---

## INFO Findings

### i1. Well-Structured Facade Pattern

**Location:** `facade/` directory
**Pattern:** CQRS-lite with DTOs

**Observation:** The facade pattern is well-implemented:
- Commands for mutations
- DTOs for reads (frozen dataclasses)
- Clear separation of concerns
- Consistent `from_*` factory methods on DTOs

**Status:** Exemplary pattern implementation.

---

### i2. Clean Interface Definitions

**Location:** `interfaces/` directory
**Pattern:** Dependency inversion with Protocol

**Observation:** Interface definitions are clean and well-documented:
- `IBattleResolver` for battle resolution abstraction
- Engine interfaces (`IMovementEngine`, `IProductionEngine`, etc.)
- Clear Protocol definitions

**Status:** Good practice.

---

### i3. Consistent Command Handler Pattern

**Location:** `engine/command_handlers.py`, `engine/superweapon_command_handlers.py`
**Pattern:** Command/Handler with registry dispatch

**Observation:** All command handlers follow identical structure:
1. Resolve entities
2. Validate
3. Apply if valid
4. Return ValidationResult

**Status:** Excellent consistency.

---

### i4. Good Separation of Validation Logic

**Location:** `validation/` directory
**Pattern:** Dedicated validator classes

**Observation:** Validators are properly extracted:
- `ColonizeValidator` - colonization rules
- `TransferValidator` - cargo transfer rules
- `SuperweaponValidator` - superweapon rules

**Status:** Clean separation.

---

### i5. Density Primitive Pattern

**Location:** `generation/density/primitives/`
**Pattern:** Strategy pattern for density fields

**Observation:** Well-designed composable density system:
- Abstract `DensityPrimitive` base class
- Concrete implementations (Radial, Ring, Spiral, etc.)
- `DensityMap` composes primitives

**Status:** Good extensible design.

---

### i6. Consistent Serialization Pattern

**Location:** Domain classes with `to_dict()` / `from_dict()`
**Pattern:** JSON serialization

**Observation:** All serializable classes follow pattern:
- `to_dict()` instance method for serialization
- `from_dict(cls, data)` classmethod for deserialization
- Consistent field mapping

**Status:** Good consistency.

---

### i7. Event System Design

**Location:** `events/` directory
**Pattern:** Event log with typed events

**Observation:** Clean event system:
- `EventType` enum for event classification
- `EventCategory` for grouping
- `Event` dataclass for individual events
- `EventLog` for aggregation

**Status:** Well-designed.

---

### i8. Calculator Extraction Pattern

**Location:** Various `*_calculator.py` files
**Pattern:** Extracted calculation logic

**Observation:** Calculations properly extracted from domain objects:
- `FleetCapabilityCalculator`
- `FleetSpeedCalculator`
- `EmpireEconomyCalculator`
- `ShipStatsCalculator`

**Status:** Good separation of concerns.

---

## Summary of Established Patterns

The `game/strategy/` layer demonstrates these consistent patterns:

1. **Validation Pattern:** Validators return `ValidationResult` (with one exception)
2. **Command/Handler Pattern:** Registry-based dispatch with consistent handler structure
3. **DTO Pattern:** Frozen dataclasses with `from_*` factory methods
4. **Calculator Pattern:** Extracted pure calculation logic
5. **Interface Pattern:** Protocol-based dependency inversion
6. **Serialization Pattern:** `to_dict()` / `from_dict()` pairs
7. **Event Pattern:** Typed event logging
8. **Density/Generation Pattern:** Composable primitives

---

## Recommended Actions

### Priority 1 (MAJOR)
1. Refactor `RaceConfig.validate()` to return `ValidationResult`
2. Add missing type hints to public methods in `naming.py`, `planet_gen.py`, `stars.py`

### Priority 2 (MINOR)
3. Add `__all__` exports to empty `__init__.py` files
4. Add "INTENTIONAL LATE IMPORT" comments to undocumented late imports
5. Add docstrings to `RaceConfig` validation helper methods

### Priority 3 (Maintenance)
6. Consider defining Protocol types for commonly duck-typed parameters
7. Run import sorting tool for consistent import ordering

---

*Report generated by Sweep Agent - Consistency Review*
