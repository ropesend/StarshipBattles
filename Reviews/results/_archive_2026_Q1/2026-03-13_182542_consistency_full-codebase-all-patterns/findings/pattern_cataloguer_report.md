# Pattern Cataloguer Report

**Scope:** Full codebase (`game/` - 429 files, `tests/` - 900 files)
**Date:** 2026-03-13

---

### Summary
- Total issues found: 18
- Critical: 0, Major: 3, Minor: 8, Info: 7

---

### Findings

---

## 1. Error Handling Patterns

#### INFO: Error Handling - Custom Exception Hierarchy Well-Established
**ID:** PC-01
**Location:** `game/core/exceptions.py`, `game/core/error_codes.py`
**Issue:** The codebase has a well-defined custom exception hierarchy rooted at `GameException` with specialized subclasses (`StateException`, `ValidationException`, `ResourceException`, `PersistenceException`, `SimulationException`, `ComponentException`, `FormulaException`). Error codes are centralized in `ErrorCode` enum (V/S/R/P/F/C categories). 56 files import from `game.core.exceptions`. However, the total number of `try/except` blocks is relatively low (~175 across 429 files), suggesting many modules rely on exception propagation rather than local handling.
**Impact:** Low - the hierarchy is clean and consistent.
**Recommendation:** Current pattern is the standard. Continue using custom exceptions with error codes.
**Effort:** N/A (already standardized)

#### MINOR: Error Handling - Broad `except Exception` Catches
**ID:** PC-02
**Location:** 14 files with 20 occurrences (e.g., `game/ui/services/tkinter_utils.py:6`, `game/ui/services/screenshot_manager.py:2`, `game/simulation/formula_system.py:1`)
**Issue:** 20 uses of `except Exception` (broad catch) versus 110 uses of specific exception types (`except ValueError`, `except KeyError`, etc.). The broad catches are concentrated in UI/service boundary code (tkinter_utils alone has 6). No bare `except:` clauses exist anywhere (good).
**Impact:** Broad catches can mask bugs, especially in `formula_system.py` and `modifier_effects.py` where simulation correctness matters.
**Recommendation:** Replace `except Exception` with specific exception types, especially in simulation code. Acceptable at UI boundaries where third-party exceptions are unpredictable.
**Effort:** Simple

#### INFO: Error Handling - Return-Value vs Exception Error Patterns
**ID:** PC-03
**Location:** `game/core/json_utils.py` (return-value), `game/simulation/` (exception-based)
**Issue:** Two error signaling patterns coexist: (1) Functions like `load_json()` return default values on failure (return-value pattern), and (2) `load_json_required()` raises exceptions. The simulation layer consistently uses exception-based error handling. The UI layer often uses return-value patterns (returning `None`, empty lists, or `False`). Approximately 100+ methods return `None` on failure paths.
**Impact:** Low - the dual pattern is intentional and documented in `json_utils.py`.
**Recommendation:** Maintain current approach: return-value for optional/recoverable operations, exceptions for mandatory/critical operations. Document which pattern each module uses.
**Effort:** N/A

---

## 2. Logging/Print Patterns

#### INFO: Logging - Consistent Logger Initialization
**ID:** PC-04
**Location:** 136 files across all modules
**Issue:** 136 files use `import logging` and virtually all use the same pattern: `logger = logging.getLogger(__name__)` at module level. Only 2 files create loggers inside methods rather than at module level (`game/ui/panels/design_report_panel.py:216`, `game/strategy/data/galaxy.py:606`, `game/ui/screens/strategy_window_manager.py:617`). No files use `log = logging.getLogger(...)` (alternative variable name).
**Impact:** Very low - the 3 method-level loggers are minor inconsistencies.
**Recommendation:** Move the 3 method-level logger declarations to module level for consistency. The `logger` variable name is the universal standard.
**Effort:** Simple

#### MINOR: Logging - Print Statement Usage
**ID:** PC-05
**Location:** 7 files with `print()` calls (e.g., `game/core/input_actions.py:1`, `game/core/protocols.py:2`, `game/simulation/interfaces/entity_protocols.py:1`)
**Issue:** 7 occurrences of `print()` across game code versus 136 files using the logging framework. Print statements bypass the logging infrastructure and cannot be filtered or redirected.
**Impact:** Minor - print output mixed with logging output reduces log quality.
**Recommendation:** Replace all `print()` calls with `logger.debug()` or `logger.info()`. These are likely debug leftovers.
**Effort:** Simple

---

## 3. Data Access Patterns

#### INFO: Data Access - Centralized JSON Loading
**ID:** PC-06
**Location:** `game/core/json_utils.py` (canonical), 34 files using `load_json`
**Issue:** JSON loading is centralized through `game.core.json_utils` with `load_json()`, `load_json_required()`, and `save_json()`. Only 5 files use raw `json.load()`/`json.loads()` directly (e.g., `game/ui/widgets/scrollable_json_panel.py`, `game/simulation/battle_state.py`, `game/ui/screens/battle_state_viewer.py`). No files use raw `open()` with JSON files - all go through the utility.
**Impact:** Very low - the raw json.load uses are for in-memory string parsing, not file I/O.
**Recommendation:** Current pattern is well-established. The few raw `json.loads()` uses are appropriate for string deserialization.
**Effort:** N/A

#### MINOR: Data Access - Serialization Pattern Consistency
**ID:** PC-07
**Location:** 23 files with `from_dict`/`to_dict` patterns, 113 files with `@dataclass`
**Issue:** Three data representation approaches coexist: (1) `@dataclass` classes (113 occurrences in 59 files), (2) `from_dict`/`to_dict` manual serialization (62 occurrences in 23 files), (3) Only 1 `NamedTuple` use (`game/strategy/engine/production_engine.py`). The `from_dict`/`to_dict` pattern is dominant for persistence-layer objects (strategy data like Fleet, Empire, Galaxy, Ship). Dataclasses are used for DTOs, config objects, and value objects. This split is actually logical - domain entities need custom serialization while DTOs/configs use dataclasses.
**Impact:** Low - the split is intentional and well-organized.
**Recommendation:** Maintain current approach. Use `@dataclass` for simple data containers and `from_dict`/`to_dict` for complex domain entities that need custom serialization logic.
**Effort:** N/A

---

## 4. API/Interface Patterns

#### MAJOR: Interface Design - Protocol vs ABC Duplication
**ID:** PC-08
**Location:** `game/core/protocols.py` (25 Protocols), `game/simulation/interfaces/` (15 Protocols), `game/ai/protocols.py` (5 Protocols), `game/strategy/interfaces/engines.py` (12 ABCs), `game/simulation/combat/battle_mode_handler.py` (1 ABC)
**Issue:** Two interface definition mechanisms are used concurrently: **Protocol** (structural typing, 57 total Protocol classes) and **ABC** (nominal typing, 16 ABC classes). The split appears to follow a pattern: Protocols for cross-layer interfaces (core protocols, simulation interfaces), ABCs for within-layer interfaces (strategy engine interfaces, battle mode handlers, validation rules, gallery base). However, there's a naming inconsistency: some Protocols use `I` prefix (`ICombatShip`, `IFleet`) while others don't (`BuildContext`, `DropTarget`, `GroupingStrategy`). Additionally, `ICombatShip` is defined in BOTH `game/core/protocols.py:601` AND `game/simulation/interfaces/entity_protocols.py:43`.
**Impact:** The duplicate `ICombatShip` definition creates confusion about which to import. The mixed naming convention makes it unclear whether a class is a Protocol or ABC.
**Recommendation:** (1) Resolve the duplicate `ICombatShip` - one should re-export the other. (2) Standardize on `I` prefix for all Protocol interfaces. (3) Document the ABC-vs-Protocol decision criteria.
**Effort:** Medium

#### MINOR: Return Type Consistency - Optional Typing Styles
**ID:** PC-09
**Location:** Across 103 files with `Optional[...]` and various files with `X | None`
**Issue:** Two optional type annotation styles coexist: `Optional[X]` (207 occurrences across 103 files, dominant) and `X | None` (5 occurrences across 3 files, rare). The vast majority use `Optional[X]` from `typing`. Only 51 files use `from __future__ import annotations` (which enables `X | None` syntax).
**Impact:** Minor cosmetic inconsistency. Both are valid Python.
**Recommendation:** Standardize on `Optional[X]` since it's overwhelmingly dominant (97%+ of usage). Only adopt `X | None` when the project-wide minimum Python version is 3.10+.
**Effort:** Simple

#### INFO: API Design - Property Usage
**ID:** PC-10
**Location:** 464 `@property` decorations across 57 files, 163 `@staticmethod` across 40 files, 82 `@classmethod` across 37 files
**Issue:** Properties are heavily used (464 instances), especially in Protocol definitions (`game/core/protocols.py:115`, `game/simulation/interfaces/entity_protocols.py:56`) and entity classes. Static methods are common in calculator/formula classes. Class methods are primarily used for factory patterns (`from_dict`, `default_resolution`, etc.). This is consistent and well-organized.
**Impact:** None - well-structured usage.
**Recommendation:** Current pattern is clean. Continue using properties for computed attributes, classmethods for factories, staticmethods for utility functions.
**Effort:** N/A

---

## 5. Naming Conventions

#### MAJOR: Naming - File Naming Inconsistency in Tests
**ID:** PC-11
**Location:** `tests/` directory (900 files)
**Issue:** Test files follow multiple organization patterns: (1) Flat files: `tests/unit/ai/test_ai.py`, `tests/unit/ai/test_combat_utils.py` (majority pattern). (2) Subdirectory grouping: `tests/unit/simulation/battle_controller/test_state.py`, `tests/unit/strategy/save_game_service/test_error_handling.py`. (3) Repro files at root: `tests/repro_warp_bug.py`, `tests/repro_load_cargo_bug.py` (not in any organized folder). (4) Repro files in subfolder: `tests/repro_issues/test_bug_01_crew_delay.py` through `test_bug_27_ordertype.py`. Tests use both `class TestXxx` grouping (count varies by file) and standalone `def test_xxx` functions. The naming convention `test_xxx_should_yyy` is used in ~1397 occurrences across 349 files, indicating a strong BDD-style naming preference.
**Impact:** Root-level repro scripts are disorganized. The dual flat-file vs subdirectory structure makes it harder to find tests.
**Recommendation:** (1) Move root-level `repro_*.py` files into `tests/repro_issues/`. (2) For large test modules, prefer the subdirectory pattern with conftest.py. (3) Continue the `test_xxx_should_yyy` naming convention as it's well-established.
**Effort:** Simple

#### MINOR: Naming - Enum Naming Patterns
**ID:** PC-12
**Location:** 18 files with Enum definitions
**Issue:** All enums use `Enum` base class (15 classes) except `GameState` which uses `IntEnum` (in `game/core/constants.py:25`). No `StrEnum` usage. Enum naming is consistent: `PascalCase` class names with `UPPER_SNAKE_CASE` values. All enum classes are well-organized in domain-specific modules.
**Impact:** None - consistent pattern.
**Recommendation:** Current pattern is clean. Consider `StrEnum` for string-valued enums if Python 3.11+ is adopted.
**Effort:** N/A

#### MINOR: Naming - Constant Naming Patterns
**ID:** PC-13
**Location:** `game/ui/colors.py` (266 constants), `game/core/config.py`, `game/core/constants.py`
**Issue:** Constants use `UPPER_SNAKE_CASE` consistently. Configuration is organized into classes with class-level attributes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig` in `game/core/config.py`). Color constants are in a dedicated module (`game/ui/colors.py` with 266 constants). Some builder/UI modules define local constants using `UPPER_SNAKE_CASE` (e.g., `game/ui/screens/builder/stats_config.py:13` constants). This is well-organized.
**Impact:** None.
**Recommendation:** Continue current pattern. Config classes group related constants logically.
**Effort:** N/A

---

## 6. Structural Patterns

#### MAJOR: Structure - Singleton Usage
**ID:** PC-14
**Location:** `game/core/singleton.py` (24 references), `game/core/registry.py` (16), `game/assets/asset_manager.py` (6), `game/ai/strategy_manager.py` (6)
**Issue:** Multiple singleton patterns coexist: (1) A dedicated `Singleton` metaclass in `game/core/singleton.py`. (2) `RegistryManager` in `game/core/registry.py` uses singleton pattern for global registry access. (3) `AssetManager` uses singleton with `_instance` class variable. (4) `StrategyManager` uses singleton. (5) `ShipThemeManager`, `SpriteManager`, `ScreenshotManager`, `ProfilingManager`, `StrategyMetadata` also use singletons. Total: ~10 singleton classes. The project's CLAUDE.md explicitly says "Dependency injection over singletons" should be preferred.
**Impact:** Singletons make testing harder (require reset between tests), create hidden dependencies, and violate the project's own stated preference for DI. The root conftest already needs special handling (`set_default_registries()` after `mgr.hydrate()`) because of singleton state leakage.
**Recommendation:** Continue the ongoing DI migration (PROJ-87 through PROJ-89 are active). Prioritize eliminating singletons that cause test isolation issues. The `RegistryManager` singleton is the most critical to address since it's the foundation other singletons depend on.
**Effort:** Complex (ongoing project work)

#### MINOR: Structure - __init__.py Patterns
**ID:** PC-15
**Location:** 48 `__init__.py` files
**Issue:** Three patterns for `__init__.py` files: (1) **Re-export with __all__**: Many packages re-export key symbols and define `__all__` (50 files have `__all__`). Largest: `game/simulation/components/abilities/__init__.py` (184 lines), `game/core/__init__.py` (147 lines). (2) **Docstring + imports**: Package modules with documentation and selective imports. (3) **Empty/minimal**: Some packages have minimal init files. The re-export pattern is dominant and well-organized with section headers.
**Impact:** Low - the pattern is mostly consistent.
**Recommendation:** Continue the re-export pattern for public packages. Keep `__init__.py` files as the public API surface with `__all__` declarations.
**Effort:** N/A

#### MINOR: Structure - Import Organization
**ID:** PC-16
**Location:** Across all 429 game files
**Issue:** Import organization follows a consistent pattern: (1) Standard library imports first, (2) Third-party imports, (3) Local imports. `TYPE_CHECKING` guards are used in 176 files for avoiding circular imports - this is well-adopted. `from __future__ import annotations` is used in only 51 files (12% of codebase), while the rest use runtime type evaluation. The dominant import style is `from game.xxx import YYY` rather than `import game.xxx` (only 1 file uses the latter style).
**Impact:** Low - imports are generally well-organized.
**Recommendation:** Continue current patterns. Consider adopting `from __future__ import annotations` more broadly if forward references become an issue.
**Effort:** Simple

---

## 7. Testing Patterns

#### MINOR: Testing - Fixture Organization
**ID:** PC-17
**Location:** 51 `conftest.py` files, `tests/fixtures/` directory (7 fixture modules)
**Issue:** Fixtures are organized at three levels: (1) **Root conftest.py**: Session-scoped data loading, DI fixtures (`session_registries`, `fresh_registries`, `minimal_registries`), pygame initialization. (2) **Subdirectory conftest.py files** (51 total): Provide domain-specific fixtures, some quite large (e.g., `tests/unit/test_framework/services/conftest.py` with 18 fixtures). (3) **tests/fixtures/ modules**: Shared fixture helpers (`paths.py`, `common.py`, `components.py`, `ships.py`, `battle.py`, `ai.py`, `test_scenarios.py`). Mock usage: ~149 uses of `@patch`/`Mock`/`MagicMock` across 30 files - relatively low, indicating preference for real objects over mocks. `pytest.raises` is used in 295 occurrences across 99 files. `pytest.mark.parametrize` appears 85 times in 19 files.
**Impact:** Low - well-structured but the conftest hierarchy can be deep.
**Recommendation:** Current fixture organization is solid. The preference for real objects over mocks aligns with the project's DI approach. Consider using `pytest.mark.parametrize` more broadly for data-driven tests.
**Effort:** N/A

#### MINOR: Testing - Test Naming Convention
**ID:** PC-18
**Location:** All test files
**Issue:** Two test naming styles: (1) **BDD-style** `test_xxx_should_yyy_when_zzz` - 1397 occurrences across 349 files (dominant). (2) **Simple descriptive** `test_xxx_yyy` - used in remaining tests. Test classes use `class TestXxx:` grouping (varies by file). Some files mix both styles. The BDD-style is clearly the preferred convention and provides better documentation of test intent.
**Impact:** Minor inconsistency - the simple style tests could benefit from more descriptive names.
**Recommendation:** Standardize on BDD-style naming for new tests. The pattern `test_<unit>_should_<expected>_when_<condition>` provides the most informative test names.
**Effort:** Simple (for new tests only; renaming existing tests is not worth the churn)

---

## 8. Configuration Patterns

#### INFO: Configuration - Centralized Config Classes
**ID:** PC-19
**Location:** `game/core/config.py`, `game/core/paths.py`, `game/core/constants.py`
**Issue:** Configuration is organized into static classes with class-level attributes: `DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig` in `config.py`. Path management uses `Paths` class in `paths.py` (7 classmethods). Game constants are in `constants.py` with enums and class-based groupings (`LayerDefaults`, `CombatConstants`). No external config files (INI, YAML, TOML) - all configuration is in Python code. This is appropriate for a game where configuration doesn't change at runtime.
**Impact:** None - clean and consistent.
**Recommendation:** Current pattern is appropriate for the project. If user-configurable settings are needed later, consider a settings file loaded at startup.
**Effort:** N/A

---

### Top 5 Priority Issues

1. **PC-08 (MAJOR): Protocol vs ABC Duplication** - The duplicate `ICombatShip` definition in two modules creates real confusion about which to import. The inconsistent `I` prefix naming makes interface identification harder across the codebase. Medium effort to resolve.

2. **PC-14 (MAJOR): Singleton Usage vs DI Preference** - ~10 singleton classes exist despite the project explicitly preferring dependency injection. This causes test isolation issues (documented in MEMORY.md). Complex effort but already being addressed by PROJ-87 through PROJ-89.

3. **PC-11 (MAJOR): Test File Organization** - Root-level repro scripts and mixed flat/subdirectory structures reduce discoverability. Simple effort to reorganize.

4. **PC-02 (MINOR): Broad Exception Catches** - 20 uses of `except Exception` including in simulation code where correctness matters. Simple effort to fix.

5. **PC-05 (MINOR): Stray Print Statements** - 7 print() calls bypass the logging framework. Trivial to fix and improves log consistency.
