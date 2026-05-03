# Consistency Violations Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 95
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 4 | **Minor:** 6 | **Info:** 2

## Findings

#### MAJOR: Logging Pattern Inconsistency - Mixed Module Logger vs Core Logger
**ID:** CON-STR-001
**Location:** Multiple files across `game/strategy/`
**Issue:** The strategy layer uses two different logging patterns inconsistently:
- **Pattern A (game.core.logger):** Used by 24 files - imports `log_info`, `log_warning`, `log_error`, `log_debug` from `game.core.logger`
- **Pattern B (stdlib logging):** Used by 4 files - imports `logging` and creates module logger via `log = logging.getLogger(__name__)` or `logger = logging.getLogger(__name__)`

Files using stdlib logging (minority pattern):
- `game/strategy/generation/placement_strategies.py:18` - `log = logging.getLogger(__name__)`
- `game/strategy/generation/loaders/galaxy_layouts_loader.py:15` - `log = logging.getLogger(__name__)`
- `game/strategy/generation/density/density_map.py:26` - `log = logging.getLogger(__name__)`
- `game/strategy/engine/harvesting_engine.py:29` - `logger = logging.getLogger(__name__)`

**Impact:** Different logging configuration, inconsistent log output format, potential confusion about which logging interface to use in new code. The `harvesting_engine.py` also uses inconsistent variable naming (`logger` vs `log`).
**Recommendation:** Standardize on `game.core.logger` module functions which is the dominant pattern (24 files). Refactor the 4 files using stdlib logging to use the core logger.
**Effort:** Simple

---

#### MAJOR: Protocol Interface Decorator Inconsistency
**ID:** CON-STR-002
**Location:** `game/strategy/engine/command_handlers.py:24` vs other Protocol definitions
**Issue:** The `ICommandHandler` Protocol class is NOT decorated with `@runtime_checkable`, while other Protocol classes in the strategy layer ARE decorated with `@runtime_checkable`.

Files with `@runtime_checkable`:
- `game/strategy/generation/placement_strategies.py:21-22` - `ISystemPlacementStrategy`
- `game/strategy/data/build_context.py:12-13` - `BuildContext`
- `game/strategy/generation/density/primitives/density_primitive.py:11-12` - `DensityPrimitive`

File missing `@runtime_checkable`:
- `game/strategy/engine/command_handlers.py:24` - `ICommandHandler(Protocol)` - no decorator

**Impact:** Without `@runtime_checkable`, `isinstance()` checks against `ICommandHandler` will fail at runtime, while they work for other Protocol interfaces. This inconsistency could cause confusion and runtime errors.
**Recommendation:** Add `@runtime_checkable` decorator to `ICommandHandler` to match the established pattern.
**Effort:** Simple

---

#### MAJOR: Inconsistent Return Type for validate() Methods
**ID:** CON-STR-003
**Location:** `game/strategy/data/race_config.py:280`
**Issue:** The `RaceConfig.validate()` method returns `tuple[bool, str]` while all other validator classes return `ValidationResult` from `game.core.validation`.

Validator pattern (dominant):
- `ColonizeValidator.validate()` returns `ValidationResult`
- `TransferValidator.validate()` returns `ValidationResult`
- `SuperweaponValidator.validate()` returns `ValidationResult`

Exception:
- `RaceConfig.validate()` returns `tuple[bool, str]`

**Impact:** API inconsistency requiring special handling at call sites. Cannot use consistent validation result processing.
**Recommendation:** Refactor `RaceConfig.validate()` to return `ValidationResult` for consistency with other validators.
**Effort:** Medium

---

#### MAJOR: Inconsistent `from __future__ import annotations` Usage
**ID:** CON-STR-004
**Location:** `game/strategy/` - only 3 of 95 files use future annotations
**Issue:** Only 3 files use `from __future__ import annotations`:
- `game/strategy/events/event_log.py:3`
- `game/strategy/data/build_queue_source.py:12`
- `game/strategy/data/build_context.py:7`

These files use Python 3.10+ style annotations like `dict[str, Any]` and `list[Event]` without the import in most files. However, these 3 files use the future import while 92 other files use `Dict`, `List`, `Optional` from `typing`.

**Impact:** Inconsistent annotation style across the codebase. The `event_log.py` file uses `list[Event]` and `dict[str, Any]` (lowercase) while most other files use `List[Event]` and `Dict[str, Any]` (capitalized from typing).
**Recommendation:** Either standardize on using `from __future__ import annotations` everywhere and switch to lowercase type hints, OR remove the future import from these 3 files and use capitalized typing imports. The dominant pattern (92 files) uses capitalized typing imports.
**Effort:** Medium

---

#### MINOR: Method Naming Inconsistency - lookup_ vs get_ Pattern
**ID:** CON-STR-005
**Location:** `game/strategy/engine/harvesting_engine.py:60,197`
**Issue:** The `lookup_harvester_in_registry()` and `_lookup_storage_in_registry()` functions use `lookup_` prefix while all other registry lookup operations use `get_` prefix.

Dominant pattern (~90 usages): `get_*`
- `get_system_by_name`, `get_planet_by_id`, `get_fleet_by_id`, `get_race`, etc.

Exception (2 usages): `lookup_*`
- `lookup_harvester_in_registry()` at line 60
- `_lookup_storage_in_registry()` at line 197

**Impact:** Cognitive overhead when choosing method names for new code.
**Recommendation:** Replace `lookup_*` functions with `get_*` naming to match the dominant pattern.
**Effort:** Simple

---

#### MINOR: Missing Type Hints on Public API Methods
**ID:** CON-STR-006
**Location:** `game/strategy/data/naming.py:67`, `game/strategy/data/stars.py` multiple methods
**Issue:** Several public methods lack return type annotations while the majority of the codebase has complete type hints.

Examples missing type hints:
- `NameRegistry.to_roman(n)` - no return type (line 67)
- `StarGenerator._generate_mass()` - no return type (line 127)
- `StarGenerator._determine_type_and_radius()` - no return type (line 149)
- `StarGenerator._kelvin_to_rgb()` - no return type (line 222)
- `Spectrum.get_total_output()` - no return type (line 41)

**Impact:** Inconsistent documentation quality, IDE type inference issues.
**Recommendation:** Add return type annotations to these methods.
**Effort:** Simple

---

#### MINOR: Missing Docstrings in stars.py Methods
**ID:** CON-STR-007
**Location:** `game/strategy/data/stars.py`
**Issue:** Several methods in `stars.py` lack docstrings while the codebase convention is Google-style docstrings on all public methods.

Methods missing docstrings:
- `Spectrum.get_total_output()` (line 41)
- `Star.to_dict()` (line 90)
- `Star.from_dict()` (line 107)

Other serialization methods like `Planet.to_dict()` and `Fleet.to_dict()` have proper docstrings.

**Impact:** Inconsistent documentation quality.
**Recommendation:** Add Google-style docstrings to these methods.
**Effort:** Simple

---

#### MINOR: Missing `__all__` Export in Package `__init__.py` Files
**ID:** CON-STR-008
**Location:** Multiple `__init__.py` files
**Issue:** Several package `__init__.py` files are empty or lack `__all__` exports while others properly export their public API.

Files with proper exports:
- `game/strategy/facade/dto/__init__.py` - has complete `__all__` list
- `game/strategy/interfaces/__init__.py` - has exports

Files missing exports:
- `game/strategy/services/__init__.py` - empty file
- `game/strategy/data/__init__.py` - empty file
- `game/strategy/adapters/__init__.py` - empty file

**Impact:** Unclear public API for these packages.
**Recommendation:** Add explicit `__all__` exports to package init files.
**Effort:** Simple

---

#### MINOR: Inconsistent Engine Constructor DI Patterns
**ID:** CON-STR-009
**Location:** Engine classes in `game/strategy/engine/`
**Issue:** Engine classes have different constructor patterns for dependency injection:

**Pattern A - Required registries (strict):**
```python
def __init__(self, *, registries: GameRegistries):
    if registries is None:
        raise TypeError("registries is required")
```
Used by: `ResupplyEngine`, `ResourceManagementEngine`, `ShipStatsCalculator`

**Pattern B - Optional registries (lenient):**
```python
def __init__(self, *, registries: Optional[GameRegistries] = None):
    self._registries = registries
```
Used by: `HarvestingEngine`, `EmpireEconomyCalculator`

**Pattern C - No registries parameter:**
Used by: `MaintenanceEngine`, `PopulationEngine`, `FleetMovementEngine`

**Impact:** Inconsistent initialization behavior - some engines require registries, others allow None.
**Recommendation:** Document the DI convention clearly. Pattern A should be used when registry is truly required.
**Effort:** Simple (documentation)

---

#### MINOR: Duplicate MAINTENANCE_RATE Constant
**ID:** CON-STR-010
**Location:** `game/strategy/engine/maintenance_engine.py:25,97`
**Issue:** The `MAINTENANCE_RATE = 0.05` constant is defined both at module level (line 25) AND as a class attribute (line 97) in `MaintenanceEngine`.

```python
# Module level
MAINTENANCE_RATE = 0.05  # Line 25

class MaintenanceEngine:
    MAINTENANCE_RATE = 0.05  # Line 97 - duplicate
```

**Impact:** Minor confusion about which constant to reference. The class attribute shadows the module constant.
**Recommendation:** Remove the duplicate class-level constant, use only the module-level constant.
**Effort:** Simple

---

#### INFO: Well-Established Consistent Patterns
**ID:** CON-STR-011
**Location:** Throughout `game/strategy/`
**Issue:** None - this is positive observation.

The strategy layer demonstrates excellent consistency in several areas:
- **Command/Handler Pattern:** All handlers follow identical structure (resolve, validate, apply, return)
- **DTO Pattern:** Frozen dataclasses with `from_*` factory methods
- **Serialization Pattern:** `to_dict()` / `from_dict()` pairs on all domain objects
- **Calculator Pattern:** Pure calculation logic extracted to `*Calculator` classes
- **Validator Pattern:** Dedicated stateless validator classes with static methods
- **Interface Pattern:** Protocol-based dependency inversion in `interfaces/`

**Recommendation:** Continue following these established patterns.
**Effort:** N/A

---

#### INFO: Consistent Class Naming Suffixes
**ID:** CON-STR-012
**Location:** Throughout `game/strategy/`
**Issue:** None - this is positive observation.

The codebase uses consistent class naming suffixes:
- `*Engine` for turn processing engines (7 classes)
- `*Calculator` for pure calculation classes (4 classes)
- `*Processor` for order/command processors (2 classes)
- `*Validator` for validation classes (3 classes)
- `*Adapter` for layer bridges (2 classes)
- `*Service` for services (3 classes)
- `*Info` / `*Summary` for DTOs (8 classes)
- `*Result` for operation results (6 classes)

**Recommendation:** Continue following these naming conventions.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **CON-STR-001 (MAJOR):** Logging pattern inconsistency - 4 files use stdlib logging while 24 use core logger. Standardize on `game.core.logger`.

2. **CON-STR-002 (MAJOR):** `ICommandHandler` Protocol missing `@runtime_checkable` decorator, inconsistent with other Protocol definitions.

3. **CON-STR-003 (MAJOR):** `RaceConfig.validate()` returns `tuple[bool, str]` while all other validators return `ValidationResult`.

4. **CON-STR-004 (MAJOR):** Inconsistent `from __future__ import annotations` usage - 3 files use it while 92 don't, causing mixed annotation styles.

5. **CON-STR-005 (MINOR):** `lookup_` function naming should be replaced with `get_` to match the dominant registry lookup pattern.
