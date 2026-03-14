# Code Quality Analysis Report

**Date:** 2026-03-13
**Scope:** `game/` (429 Python files), `tests/` (900 Python files)
**Analyzer:** Code Quality Analyst (Claude Opus 4.6)

---

## Summary

- **Total issues found:** 12
- **Critical:** 1, **Major:** 5, **Minor:** 4, **Info:** 2

The codebase is generally well-maintained with consistent patterns. Error handling follows deliberate conventions (broad catches are annotated with `# Intentional broad catch` comments). Logging is consistent (`logging.getLogger(__name__)` everywhere). The most impactful issues involve DRY violations in component management, magic number proliferation for ticks-per-turn, and residual DI inconsistency where Ship methods call the global registry despite having injected registries available.

---

## Findings

### CRITICAL: Ship.add_component / add_components_bulk DRY Violation and DI Bypass

**ID:** CQ-01
**Location:** `game/simulation/entities/ship.py:502-576`
**Issue:** `add_component()` and `add_components_bulk()` duplicate the same 6-line sequence: validate, append, assign layer, set ship ref, recalculate, create ModifierService, ensure mandatory modifiers. Both methods also call `get_default_registry_provider()` for validation despite `self._registries` being available on the Ship instance. This means validation bypasses the injected registries and uses the global singleton, which could behave differently in tests.

**Impact:**
1. **Bug risk:** If `get_default_registry_provider()` and `self._registries` disagree (e.g., in tests with isolated registries), validation uses stale/wrong data while the rest of the ship uses injected registries.
2. **Maintenance burden:** Any change to the add-component flow must be duplicated in both methods. The ModifierService late import is duplicated verbatim.

**Recommendation:** Extract a private `_attach_component(self, component, layer_type)` method that both `add_component` and `add_components_bulk` call. Use `self._registries` consistently for validator creation instead of `get_default_registry_provider()`.

**Effort:** Simple

---

### MAJOR: ShipValidatorHelper Uses Global Registry Instead of Ship's Injected Registries

**ID:** CQ-02
**Location:** `game/simulation/entities/ship_validator_helper.py:44,55,64`
**Issue:** All three methods (`check_validity`, `get_validation_warnings`, `get_missing_requirements`) call `get_default_registry_provider()` instead of using `self._ship._registries`. The Ship class was migrated to strict DI (PROJ-50), but ShipValidatorHelper was not updated to use the injected registries.

**Impact:** In test environments using `TestRegistryProvider`, validation may use different registry data than the ship itself, leading to inconsistent behavior. This violates the architectural decision of PROJ-50 (strict DI).

**Recommendation:** Pass the ship's registries through: `get_or_create_validator(registry_provider=self._ship.registries)`. Since `ship.registries` is a public property, this is straightforward.

**Effort:** Simple

---

### MAJOR: Magic Number `100` (Ticks Per Turn) Hardcoded Across Multiple Engines

**ID:** CQ-03
**Location:**
- `game/strategy/engine/environmental_hazard_engine.py:109-110` (`/ 100.0`)
- `game/strategy/engine/resource_management_engine.py:97` (`/ 100.0`)
- `game/strategy/engine/resupply_engine.py:121` (`/ 100.0`)
- `game/strategy/engine/harvesting_engine.py:92` (`/ 100`)
- `game/strategy/engine/production_engine.py:30` (`TICKS_PER_TURN = 100` -- the constant)

**Issue:** `TICKS_PER_TURN = 100` is defined in `production_engine.py` but 4 other engine files hardcode `/ 100.0` or `/ 100` instead of importing the constant. If the tick count ever changes, these files would silently break.

**Impact:** Changing TICKS_PER_TURN would require manually finding and updating all hardcoded `/ 100` divisions. Missing one would cause subtle balance bugs (wrong harvest rates, wrong maintenance costs, etc.).

**Recommendation:** Move `TICKS_PER_TURN` to a shared constants module (e.g., `game/strategy/constants.py` or `game/core/constants.py`) and replace all `/ 100.0` with `/ TICKS_PER_TURN`. This is a mechanical find-and-replace.

**Effort:** Simple

---

### MAJOR: 129 Potentially Unused Imports Across the Codebase

**ID:** CQ-04
**Location:** Distributed: `game/ui/` (49), `game/strategy/` (38), `game/simulation/` (30), `game/ai/` (8), `game/core/` (2), `game/research/` (1)
**Notable examples:**
- `game/app.py:32` - `UIButton` imported but unused
- `game/ai/controller.py:68` - `is_in_pdc_arc` imported but unused
- `game/simulation/components/component.py:63` - `safe_evaluate_math_formula` imported but unused
- `game/simulation/entities/combat_endurance.py:9` - `IResourceConsumptionAbility`, `IWeaponAbility` imported but unused

**Issue:** Approximately 129 imports reference names that do not appear elsewhere in the same file. While some may be needed for re-export or type checking, many appear genuinely unused.

**Impact:** Unused imports increase cognitive load, slow IDE tooling, and occasionally mask circular import issues. They also make it harder to determine actual dependencies between modules.

**Recommendation:** Run `autoflake --remove-all-unused-imports --check` or `ruff check --select F401` to identify and clean up. Preserve any imports that are intentional re-exports (document with `__all__` or comments).

**Effort:** Medium (requires verifying each import is truly unused, not a re-export)

---

### MAJOR: Fleet.from_dict Manually Parses HexCoord Instead of Using hex_from_dict Utility

**ID:** CQ-05
**Location:** `game/strategy/data/fleet.py:246-250`
**Issue:** `Fleet.from_dict()` manually parses HexCoord from dict/list with inline isinstance checks:
```python
if isinstance(location, dict) and 'q' in location and 'r' in location:
    location = HexCoord(location['q'], location['r'])
elif isinstance(location, list):
    location = HexCoord(location[0], location[1])
```
Meanwhile, `hex_from_dict()` from `game.core.hex_math` is the standard utility used by Galaxy, Planet, Star, Storm, and WarpPoint deserialization (12+ call sites).

**Impact:** The manual parsing in Fleet lacks the error handling that `hex_from_dict` provides. If the location format changes, Fleet deserialization must be updated separately. This also handles `list` format which `hex_from_dict` may not, creating inconsistent behavior depending on which code path runs.

**Recommendation:** Replace the manual parsing with `hex_from_dict(location)` (or `hex_from_dict` with list support if needed). Same for the path restoration loop at lines 272-278.

**Effort:** Simple

---

### MAJOR: Ship.__init__ is 170 Lines with 40+ Instance Variables

**ID:** CQ-06
**Location:** `game/simulation/entities/ship.py:31-200`
**Issue:** The Ship constructor initializes 40+ instance variables across 170 lines. Many of these are combat stats, resource consumption values, and caching fields that are set to defaults and immediately overwritten by `recalculate_stats()`. The Ship class overall has 42 methods and 858 lines.

**Impact:** This makes the Ship class difficult to understand, test, and modify. New developers must trace through 170 lines of initialization to understand the object model. The large number of public attributes creates a wide implicit interface that couples many systems.

**Recommendation:** This is already tracked in the God Class Decomposition projects (PROJ-88). Continue extracting state into domain-specific data objects (like the existing `ShipFormation`, `ShipStatsCalculator`, etc.). Consider grouping related stats into dataclasses (e.g., `CombatStats`, `ResourceConsumption`).

**Effort:** Complex (already planned in PROJ-88)

---

### MINOR: Deep Nesting in UI Code (331 Lines at Depth >= 7)

**ID:** CQ-07
**Location:** Primarily:
- `game/ui/screens/test_lab/test_run_details.py` (depth 12-13)
- `game/ui/panels/system_tree_panel.py` (depth 13)
- `game/ui/screens/transfer_dialog.py` (depth 12)

**Issue:** 331 lines across the codebase have indentation depth of 7 or more levels. The worst cases reach depth 13, primarily in UI rendering code that builds nested widget hierarchies.

**Impact:** Deep nesting reduces readability and makes it harder to understand control flow. While some nesting is inherent to UI tree construction, depth 13 exceeds reasonable limits.

**Recommendation:** Extract nested widget construction into helper methods. Use early-return patterns to reduce nesting in conditional logic. For tree-building code, consider builder pattern or declarative layout definitions.

**Effort:** Medium

---

### MINOR: Long Functions (25 Functions Exceeding 80 Lines)

**ID:** CQ-08
**Location:** Top offenders:
- `game/ui/screens/strategy_panel_manager.py:91` - `create_strategy_panels` (285 lines)
- `game/ui/screens/planet_list_sidebar.py:13` - `build_sidebar` (243 lines)
- `game/ui/panels/system_tree_panel.py:135` - `set_items` (212 lines)
- `game/ui/research/research_controls.py:64` - `_create_ui` (174 lines)
- `game/simulation/entities/ship.py:31` - `__init__` (170 lines)
- `game/strategy/services/ship_stats_calculator.py:87` - `calculate_stats` (157 lines)

**Issue:** 25 functions exceed 80 lines, with the worst case being 285 lines. Most are UI construction functions that create many widgets sequentially.

**Impact:** Long functions are harder to test, harder to understand at a glance, and tend to accumulate complexity over time. The project convention recommends <50 lines per function.

**Recommendation:** For UI construction functions, extract logical groups of widgets into helper methods (e.g., `_create_header_section()`, `_create_resource_panel()`). For `calculate_stats`, consider splitting accumulation logic by stat type.

**Effort:** Medium

---

### MINOR: Inconsistent from_dict Error Handling - Silent Skip vs Exception

**ID:** CQ-09
**Location:**
- `game/strategy/data/empire.py:268` - Corrupt fleets: `except Exception` + warning + skip
- `game/strategy/data/fleet.py:268` - Corrupt ships: `except Exception` + warning + skip
- `game/strategy/data/fleet_order_serializer.py:56` - Corrupt orders: `except Exception` + warning + skip
- `game/strategy/data/galaxy.py:635` - Invalid systems: `except (PersistenceException, KeyError, TypeError, ValueError)` + skip

**Issue:** Most deserialization uses broad `except Exception` to skip corrupt entries, while Galaxy.from_dict uses a specific exception list. The resilient-skip pattern is reasonable for saved game loading, but the inconsistency in exception specificity means Galaxy is more precise about what errors it handles.

**Impact:** Low -- the broad catches in Empire/Fleet/FleetOrderSerializer could mask unexpected errors during development. Since these are save-load paths, silent data loss from unexpected errors would be hard to diagnose.

**Recommendation:** Consider standardizing on specific exception types (like Galaxy does) to catch only expected deserialization errors, letting unexpected errors propagate for debugging.

**Effort:** Simple

---

### MINOR: Global Mutable State in event_logging, ship_io, build_queue_source, setup modules

**ID:** CQ-10
**Location:**
- `game/core/event_logging.py:33` - `_event_handler` global
- `game/ui/services/ship_io.py:43` - `_cached_registries` global
- `game/strategy/data/build_queue_source.py:31` - `_production_rates_cache` global
- `game/strategy/data/homeworld_presets.py:35,131` - `_presets_cache` global
- `game/ui/screens/setup_data_io.py:29` - `_ship_factory` global
- `game/ui/screens/setup_screen.py:41` - `_ship_factory` global

**Issue:** Several modules use module-level mutable globals for caching and callbacks. While documented and intentional (especially `event_logging`), these create implicit state dependencies that can cause test isolation issues.

**Impact:** Test fixtures must carefully reset these globals between tests to prevent state leakage. The project has addressed this for registries (PROJ-50 DI), but these smaller globals remain.

**Recommendation:** For caching globals, consider moving to class-level caches or using `functools.lru_cache`. For the event handler, the current pattern is acceptable given its documentation, but the ship_io and setup module globals could be injected instead.

**Effort:** Medium

---

### INFO: Well-Documented Intentional Broad Exception Catches

**ID:** CQ-11
**Location:** Multiple files (19 occurrences)
**Issue:** All `except Exception` usages in the codebase include an `# Intentional broad catch:` comment explaining why the broad catch is needed (platform-dependent code, top-level crash handler, handler isolation, etc.).

**Impact:** None -- this is positive. The team has established a good convention of annotating broad catches, making code review easier.

**Recommendation:** No action needed. Continue this convention.

**Effort:** N/A

---

### INFO: Consistent Logging Convention

**ID:** CQ-12
**Location:** 139 files across `game/`
**Issue:** All 139 files using logging consistently use `logger = logging.getLogger(__name__)` at module level. Only one exception (`game/app.py:20`) uses `logging.getLogger("game")` for the root game logger, which is intentional.

**Impact:** None -- this is positive. Consistent logger naming enables effective log filtering.

**Recommendation:** No action needed.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **CQ-01 (Critical):** Ship component attachment duplicates code and bypasses DI. Direct bug risk if registries diverge in tests.

2. **CQ-02 (Major):** ShipValidatorHelper uses global registry instead of ship's injected registries. Same DI bypass pattern as CQ-01.

3. **CQ-03 (Major):** TICKS_PER_TURN magic number hardcoded in 4 engine files. Easy fix, prevents future bugs.

4. **CQ-04 (Major):** 129 unused imports add noise and obscure actual dependencies.

5. **CQ-05 (Major):** Fleet deserialization manually parses HexCoord instead of using the shared `hex_from_dict()` utility.

---

## Methodology

Analysis performed using:
- AST-based scanning for unused imports, function length, class method count, nesting depth
- Regex pattern matching for exception handling, magic numbers, DI patterns
- Manual code review of high-risk areas identified by scanning
- Cross-reference of patterns across related modules for consistency
