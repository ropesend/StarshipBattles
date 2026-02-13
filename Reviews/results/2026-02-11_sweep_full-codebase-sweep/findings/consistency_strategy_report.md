# Consistency Sweep: game/strategy/

**Date:** 2026-02-11
**Scope:** All Python files in `game/strategy/` (91 files across 12 subpackages)
**Methodology:** Exhaustive file-by-file scan with 5-phase analysis

---

## Findings

---

### Phase 1: Naming Conventions

#### MAJOR: Duplicate `to_roman` Implementation
- **ID:** CON-STR-001
- **Location:** `game/strategy/data/naming.py:54` and `game/strategy/data/planet_naming.py:19`
- **Issue:** Two independent implementations of `to_roman()` exist. `naming.py` has `NameRegistry.to_roman()` (static method, supports 1-3999) and `planet_naming.py` has `to_roman()` (module-level function, supports 1-39). They use different algorithms and have different range limits.
- **Impact:** Maintenance burden and risk of divergence. If the algorithm needs fixing, both must be updated. Violates DRY principle.
- **Recommendation:** Remove the duplicate in `naming.py` and import from `planet_naming.py`, or extract to a shared utility in `game/core/`.
- **Effort:** Small (< 1 hour)

#### MAJOR: Inconsistent Entity Lookup Verb Prefixes
- **ID:** CON-STR-002
- **Location:** `game/strategy/facade/strategy_session_facade.py` (`_find_fleet_by_id`, `_find_planet_by_id`) vs `game/strategy/engine/game_session.py` (`_get_fleet_by_id`, `_get_planet_by_id`)
- **Issue:** The facade uses `_find_` prefix while GameSession uses `_get_` prefix for semantically identical operations (locate entity by ID). This makes it unclear which verb to use when adding new lookup methods.
- **Impact:** Developers may use either prefix inconsistently. Creates confusion about whether `_find_` and `_get_` have different semantics (e.g., does `_find_` imply it may return None while `_get_` raises?).
- **Recommendation:** Standardize on one prefix. `_get_` is more conventional for direct lookups. Update facade to use `_get_fleet_by_id` / `_get_planet_by_id`.
- **Effort:** Small (< 1 hour)

#### MINOR: Inconsistent Logging Module Usage
- **ID:** CON-STR-003
- **Location:** Multiple files across `game/strategy/`
- **Issue:** Three different logging patterns are used: (1) `from game.core.logger import log_info, log_warning` (e.g., `fleet.py`, `game_initializer.py`, `maintenance_engine.py`), (2) `import logging; logger = logging.getLogger(__name__)` (e.g., `harvesting_engine.py`, `resupply_engine.py`), (3) `import logging; log = logging.getLogger(__name__)` (e.g., `placement_strategies.py`, `density_map.py`). The variable names `logger` vs `log` are also inconsistent.
- **Impact:** Makes grep/search for logging calls harder. Mixing custom logger facade with stdlib logging reduces consistency.
- **Recommendation:** Standardize on `from game.core.logger import log_info, log_warning, ...` throughout `game/strategy/` since this is the project's preferred pattern. Where stdlib logging is used, standardize on `logger` as the variable name.
- **Effort:** Medium (2-4 hours)

#### MINOR: Inconsistent Type Annotation Styles
- **ID:** CON-STR-004
- **Location:** `game/strategy/engine/empire_economy_calculator.py:172,197` (`Dict[str, any]`), `game/strategy/events/event_log.py` (`dict[str, Any]`, `list[Event]`), `game/strategy/data/race_config.py:280` (`tuple[bool, str]`)
- **Issue:** Mixed use of `Dict[str, any]` (lowercase `any` -- incorrect, should be `Any`), Python 3.9+ built-in generics (`dict[str, Any]`, `list[Event]`, `tuple[bool, str]`), and `typing` module generics (`Dict[str, float]`, `List[Empire]`, `Tuple[bool, str]`). The lowercase `any` in `empire_economy_calculator.py` is technically a reference to the builtin `any` function, not `typing.Any`.
- **Impact:** The `Dict[str, any]` is semantically wrong (references built-in `any()` function, not `typing.Any`). Mixed typing styles reduce readability and make automated linting harder.
- **Recommendation:** Fix `Dict[str, any]` to `Dict[str, Any]` immediately. Standardize the rest of the codebase on either `typing` generics or Python 3.9+ built-in generics.
- **Effort:** Small for the bug fix; Medium for full standardization

#### INFO: NameRegistry Class Style Inconsistencies
- **ID:** CON-STR-005
- **Location:** `game/strategy/data/naming.py`
- **Issue:** `NameRegistry` uses no type hints on any method (`load_data`, `get_system_name`, `to_roman`), has double-space before `n > 0` on line 73, and has no module docstring. This contrasts with the well-documented style in `planet_naming.py` which has full docstrings and type hints.
- **Impact:** Lower code quality in `naming.py` compared to the rest of the module.
- **Recommendation:** Add type hints and proper docstrings to `NameRegistry` to match the standard seen in `planet_naming.py`.
- **Effort:** Small (< 1 hour)

---

### Phase 2: Structural Patterns

#### MAJOR: Duplicated `_calculate_maintenance_cost` Method
- **ID:** CON-STR-006
- **Location:** `game/strategy/engine/maintenance_engine.py:189-228` and `game/strategy/engine/empire_economy_calculator.py:256-295`
- **Issue:** Both `MaintenanceEngine._calculate_maintenance_cost()` and `EmpireEconomyCalculator._calculate_maintenance_cost()` contain identical logic: iterate `design_data['layers']`, sum `resource_cost` from components, multiply by `MAINTENANCE_RATE` (0.05). Both handle two layer formats identically.
- **Impact:** Any change to maintenance formula must be applied in two places. Bug risk if one is updated and the other is not.
- **Recommendation:** Extract a shared `calculate_maintenance_cost(design_data, rate)` utility function (module-level in a shared location like `game/strategy/formulas/` or a new `game/strategy/engine/maintenance_formula.py`). Both classes import and delegate.
- **Effort:** Small (< 1 hour)

#### MAJOR: Duplicated `_get_harvester_info` / `_lookup_harvester_in_registry` Methods
- **ID:** CON-STR-007
- **Location:** `game/strategy/engine/harvesting_engine.py:201-243` and `game/strategy/engine/empire_economy_calculator.py:172-213`
- **Issue:** `HarvestingEngine._get_harvester_info()` and `EmpireEconomyCalculator._get_harvester_info()` contain identical logic for extracting `ResourceHarvester` info from components. Both `_lookup_harvester_in_registry()` implementations are also identical.
- **Impact:** Same as CON-STR-006. Two implementations to maintain for the same logic.
- **Recommendation:** Extract a shared component-ability lookup utility. Both HarvestingEngine and EmpireEconomyCalculator delegate to it.
- **Effort:** Small (< 1 hour)

#### MAJOR: Duplicated `_find_system_at_location` O(n) Scan
- **ID:** CON-STR-008
- **Location:** `game/strategy/engine/superweapon_order_processor.py:47-78` and `game/strategy/validation/superweapon_validator.py` (similar system lookup logic)
- **Issue:** `SuperweaponOrderProcessor._find_system_at_location()` does an O(n) scan over all systems, checking planets, stars, and warp points for each. This is duplicated with similar logic in `SuperweaponValidator`. Meanwhile, `Galaxy` already has `get_system_of_object()` and `get_system_at_hex()` methods that could serve this purpose.
- **Impact:** O(n) system scan repeated in multiple places when O(1) lookups via Galaxy's registry exist.
- **Recommendation:** Use Galaxy's existing `get_system_at_hex()` or `get_system_of_object()` methods instead of hand-written O(n) scans.
- **Effort:** Small (< 1 hour)

#### MINOR: Inconsistent DI Patterns Across Engines
- **ID:** CON-STR-009
- **Location:** Multiple engine classes in `game/strategy/engine/`
- **Issue:** Engines have three different patterns for `registries` dependency: (1) Required with TypeError on None: `ResupplyEngine`, `ResourceManagementEngine`; (2) Optional keyword-only: `HarvestingEngine`, `EmpireEconomyCalculator`; (3) Not needed at all: `MaintenanceEngine`, `PopulationEngine`, `FleetOrderProcessor`, `SuperweaponOrderProcessor`. Pattern (2) is inconsistent because HarvestingEngine uses registries for the same component lookup as ResupplyEngine, yet one requires it and the other doesn't.
- **Impact:** Inconsistent constructor signatures confuse developers about whether registries is truly optional or effectively required. Some engines silently skip functionality when registries is None.
- **Recommendation:** For engines that perform component registry lookups, make `registries` required (matching ResupplyEngine pattern). For engines that genuinely don't need it, don't accept it.
- **Effort:** Medium (2-4 hours)

#### MINOR: Inconsistent Delegate/Facade Naming
- **ID:** CON-STR-010
- **Location:** `game/strategy/data/` delegates
- **Issue:** Fleet delegates are named as descriptive roles (`FleetResourceAggregator`, `FleetCapabilityCalculator`, `FleetBattleAdapter`) while ShipInstance delegates use `Manager`/`Formatter` suffixes (`ShipResourceManager`, `ShipCargoManager`, `ShipDisplayFormatter`). The naming convention is internally consistent within each entity but inconsistent across the data layer.
- **Impact:** Minor cognitive load when searching for delegates. No functional impact.
- **Recommendation:** This is low priority but could be standardized during any future refactoring of the data layer.
- **Effort:** Medium (2-4 hours due to test updates)

---

### Phase 3: API Design Consistency

#### CRITICAL: Facade `_find_fleet_by_id` Does O(n) Scan Instead of O(1) Registry Lookup
- **ID:** CON-STR-011
- **Location:** `game/strategy/facade/strategy_session_facade.py` (`_find_fleet_by_id` method)
- **Issue:** The facade iterates over all empires' fleets in a linear scan to find a fleet by ID, while Galaxy already maintains a fleet registry (`galaxy._fleet_registry`) that provides O(1) lookup. GameSession's `_get_fleet_by_id` correctly uses the galaxy registry.
- **Impact:** Performance regression for fleet lookups in the UI layer. Every fleet info request triggers an O(E*F) scan (E empires * F fleets per empire).
- **Recommendation:** Delegate to `self._session.galaxy._get_fleet_by_id()` or `self._session._get_fleet_by_id()` instead of manual iteration.
- **Effort:** Small (< 30 minutes)

#### MAJOR: Inconsistent `__eq__` Return Value Convention
- **ID:** CON-STR-012
- **Location:** `game/strategy/data/fleet.py:415-418`, `game/strategy/data/ship_instance.py` (`__eq__`), `game/strategy/data/planet.py` (`__eq__`)
- **Issue:** Three different `__eq__` return conventions exist: Fleet returns `False` for non-Fleet comparisons, ShipInstance returns `NotImplemented` for non-ShipInstance comparisons, Planet returns `False` for non-Planet comparisons. Python's data model specifies that `NotImplemented` should be returned when a comparison is not implemented, allowing the other operand's `__eq__` to be tried.
- **Impact:** `NotImplemented` is the correct Python convention. Returning `False` directly prevents Python's comparison delegation mechanism from working.
- **Recommendation:** Standardize all `__eq__` methods to return `NotImplemented` for type mismatches (matching ShipInstance's correct pattern).
- **Effort:** Small (< 1 hour)

#### MAJOR: Missing Type Hints on Public Methods
- **ID:** CON-STR-013
- **Location:** `game/strategy/data/fleet.py` (`add_order`, `clear_orders`, `get_current_order`, `pop_order`, `merge_with`), `game/strategy/data/empire.py` (`add_colony`, `remove_colony`, `add_fleet`, `remove_fleet`), `game/strategy/data/physics.py` (`SectorEnvironment.__init__`, `calculate_radiation`), `game/strategy/data/naming.py` (all methods), `game/strategy/data/pathfinding.py` (`find_hybrid_path`, `project_fleet_path`)
- **Issue:** CLAUDE.md states "Use type hints for function signatures" and "Add docstrings to public APIs." Multiple public methods across the data and pathfinding layers lack type hints entirely.
- **Impact:** Reduces IDE support, makes refactoring harder, violates project coding standards.
- **Recommendation:** Add type hints to all public method signatures in the listed files.
- **Effort:** Medium (2-4 hours)

#### MINOR: Inconsistent Validation Return Types
- **ID:** CON-STR-014
- **Location:** `game/strategy/validation/` (returns `ValidationResult`), `game/strategy/data/race_config.py:280` (returns `tuple[bool, str]`), `game/strategy/systems/design_library.py` (returns `Tuple[bool, str]`), `game/strategy/systems/race_library.py` (returns `Tuple[bool, str]`)
- **Issue:** Validators use `ValidationResult` (from `game.core.validation`) while other validation/save operations use raw `Tuple[bool, str]`. `RaceConfig.validate()` returns `tuple[bool, str]` instead of `ValidationResult`.
- **Impact:** Callers must handle two different result formats for conceptually similar operations (did this succeed? what went wrong?).
- **Recommendation:** Consider migrating `RaceConfig.validate()`, `DesignLibrary.save_design()`, and `RaceLibrary.save_race()` to return `ValidationResult` for consistency with the validation layer.
- **Effort:** Medium (2-4 hours)

#### MINOR: Module-Level Functions vs Static Methods Inconsistency
- **ID:** CON-STR-015
- **Location:** `game/strategy/services/component_inspector.py` (module-level functions), `game/strategy/validation/` (static methods on classes), `game/strategy/data/pathfinding.py` (module-level functions), `game/strategy/formulas/habitability.py` (module-level functions)
- **Issue:** Some modules use module-level functions for stateless operations (`component_inspector.py`, `pathfinding.py`, `habitability.py`) while others wrap stateless operations in classes with static methods (`ColonizeValidator`, `TransferValidator`, `SuperweaponValidator`, `FleetSpeedCalculator`).
- **Impact:** Inconsistent calling conventions. Module-level: `component_inspector.has_colonize_module(...)`. Class static: `ColonizeValidator.validate_colonize(...)`.
- **Recommendation:** This is a stylistic choice. The current mix is acceptable since validators benefit from class grouping. Document the convention: pure formulas use module-level functions; validators and calculators that group related operations use static class methods.
- **Effort:** None needed (document convention only)

---

### Phase 4: Project Pattern Adherence

#### MAJOR: `SectorEnvironment` Class Missing Type Hints and Docstrings
- **ID:** CON-STR-016
- **Location:** `game/strategy/data/physics.py:5-17`
- **Issue:** `SectorEnvironment.__init__` has no type hints and uses inline comments instead of docstrings. `calculate_radiation` has no return type hint. The module has no module-level docstring. This violates CLAUDE.md's "Use type hints for function signatures" and "Add docstrings to public APIs" rules.
- **Impact:** Poor discoverability and IDE support for this class.
- **Recommendation:** Add proper type hints and docstrings matching the standard seen in `planet_physics.py`.
- **Effort:** Small (< 30 minutes)

#### MINOR: Global Module-Level Cache Pattern (Potential Test Pollution)
- **ID:** CON-STR-017
- **Location:** `game/strategy/data/homeworld_presets.py:16` (`_presets_cache`), `game/strategy/data/build_queue_source.py:24` (`_production_rates_cache`), `game/strategy/data/classification_config.py:127` (`@lru_cache`)
- **Issue:** Three files use module-level caching with different patterns: `homeworld_presets.py` uses a `global` variable with manual `clear_cache()`, `build_queue_source.py` uses a `global` variable with no clear function, and `classification_config.py` uses `@lru_cache`. These can cause test pollution between test cases.
- **Impact:** `build_queue_source.py` has no way to clear its cache in tests. `classification_config.py` uses `lru_cache` which can be cleared but requires `get_classification_config.cache_clear()`.
- **Recommendation:** Add `clear_cache()` function to `build_queue_source.py`. Consider using a consistent caching pattern across all three modules.
- **Effort:** Small (< 1 hour)

#### MINOR: Duplicate `import math` in `stars.py`
- **ID:** CON-STR-018
- **Location:** `game/strategy/data/stars.py` (top-level import and import inside `_map_radius_to_hexes` method)
- **Issue:** `import math` appears both at the module level and again inside a method body. The inner import is redundant.
- **Impact:** No functional impact. Minor code smell.
- **Recommendation:** Remove the duplicate import inside the method.
- **Effort:** Trivial (< 5 minutes)

#### INFO: Superweapon Mission Command Handlers Have Significant Code Duplication
- **ID:** CON-STR-019
- **Location:** `game/strategy/engine/superweapon_command_handlers.py:182-394`
- **Issue:** The six mission command handlers (`ImplodePlanetMissionCommandHandler`, `StellerateStarMissionCommandHandler`, `OpenWarpPointMissionCommandHandler`, `CloseWarpPointMissionCommandHandler`, `CreateDysonSphereMissionCommandHandler`) all share a nearly identical pattern: resolve fleet, determine start hex, calculate path, queue MOVE order, set path, queue action order. The only variation is the action order type and target.
- **Impact:** ~200 lines of nearly identical code. Updating the mission-queue pattern requires editing 5 handlers.
- **Recommendation:** Extract a shared `_queue_mission_orders(session, fleet, target_hex, action_order)` helper that all mission handlers call.
- **Effort:** Small (1-2 hours)

---

### Phase 5: Per-Module Internal Consistency

#### MINOR: `pathfinding.py` Contains Dead/Questionable Code
- **ID:** CON-STR-020
- **Location:** `game/strategy/data/pathfinding.py:53-54`
- **Issue:** Inside `find_path_interstellar`, line 53 does `current_sys = galaxy.systems[galaxy.get_system_by_name(current_name).global_location]` which is immediately overwritten by line 68: `current_sys = galaxy.get_system_by_name(current_name)`. The first assignment is dead code.
- **Impact:** Dead code confuses readers and suggests incomplete implementation or abandoned approach. Multiple inline comments in this function read like development notes rather than documentation (e.g., "Wait, galaxy.systems is keyed by location.", "We need a name lookup or pass the object map differently.").
- **Recommendation:** Remove dead code on line 53 and clean up development-note comments, replacing them with proper documentation.
- **Effort:** Small (< 30 minutes)

#### MINOR: `build_queue_source.py` Contains Heavily Duplicated Collection Logic
- **ID:** CON-STR-021
- **Location:** `game/strategy/data/build_queue_source.py:144-218` and `game/strategy/data/build_queue_source.py:221-288`
- **Issue:** `collect_build_queues_at_hex()` and `collect_all_build_queues_for_empire()` contain nearly identical code for building `BuildQueueSource` objects from planets and fleets. The only difference is the planet source (galaxy lookup by hex vs empire.colonies) and fleet filtering (by location vs all fleets).
- **Impact:** ~70 lines of duplicated BuildQueueSource construction code.
- **Recommendation:** Extract a shared `_build_planet_sources(planet)` and `_build_fleet_sources(fleet)` helper to eliminate duplication.
- **Effort:** Small (< 1 hour)

#### MINOR: `DesignLibrary` Uses Late Imports Inside Methods
- **ID:** CON-STR-022
- **Location:** `game/strategy/systems/design_library.py` (imports `log_info`, `log_debug`, `log_error` inside methods at lines 28, 72, 126)
- **Issue:** Logger functions are imported inside method bodies rather than at module level. This is done inconsistently: some methods import locally, while the module also sometimes uses them without import. This differs from the documented pattern where only "edge operation" late imports are justified (per `docs/ARCHITECTURE.md`).
- **Impact:** Slightly slower execution on each call. Inconsistent import style.
- **Recommendation:** Move logger imports to module level.
- **Effort:** Small (< 30 minutes)

#### INFO: `event_log.py` Uses Python 3.10+ `X | Y` Union Syntax
- **ID:** CON-STR-023
- **Location:** `game/strategy/events/event_log.py:77` (`category: str | EventCategory`)
- **Issue:** Uses the `str | EventCategory` syntax which requires Python 3.10+. The rest of the codebase predominantly uses `typing.Union[str, EventCategory]` or `Optional[X]` from the `typing` module.
- **Impact:** May fail on Python 3.9. Inconsistent with the predominant typing style.
- **Recommendation:** Use `Union[str, EventCategory]` for consistency, or add `from __future__ import annotations` (already present in some files).
- **Effort:** Trivial (< 5 minutes)

---

## Top 5 Priority Issues

| Rank | ID | Severity | Title | Effort |
|------|-----|----------|-------|--------|
| 1 | CON-STR-011 | CRITICAL | Facade `_find_fleet_by_id` does O(n) scan instead of O(1) registry | Small |
| 2 | CON-STR-006 | MAJOR | Duplicated `_calculate_maintenance_cost` across two engines | Small |
| 3 | CON-STR-007 | MAJOR | Duplicated `_get_harvester_info` / `_lookup_harvester_in_registry` | Small |
| 4 | CON-STR-004 | MINOR | `Dict[str, any]` (lowercase) is semantically wrong type annotation | Small |
| 5 | CON-STR-012 | MAJOR | Inconsistent `__eq__` return value convention (False vs NotImplemented) | Small |

---

## Summary Statistics

- **Total findings:** 23
- **CRITICAL:** 1
- **MAJOR:** 8
- **MINOR:** 11
- **INFO:** 3
- **Files scanned:** 91 Python files across 12 subpackages
