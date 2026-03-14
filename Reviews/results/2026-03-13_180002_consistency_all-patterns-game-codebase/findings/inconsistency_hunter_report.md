# Inconsistency Hunter Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~95K lines)
**Reviewer:** Claude Code (Inconsistency Hunter agent)

---

## Summary

- **Total issues found:** 12
- **Critical:** 2
- **Major:** 4
- **Minor:** 4
- **Info:** 2

---

## Findings

---

### CRITICAL: Duplicate ICombatShip Protocol Definitions with Different Semantics

**ID:** IH-001
**Location:**
- `game/core/protocols.py:601` - `ICombatShip(Protocol)` with `is_combat_ship` checking `team_id, hp, is_derelict`
- `game/simulation/interfaces/entity_protocols.py:43` - `ICombatShip(Protocol)` with `is_combat_ship` checking `angle, layers`

**Issue:** Two separate `ICombatShip` Protocol classes exist with the same name but different member requirements and different type guard implementations. The core version checks for combat-oriented attributes (`team_id`, `hp`, `is_derelict`) while the simulation version checks for structural attributes (`angle`, `layers`). Importers can get different behavior depending on which module they import from, and both `is_combat_ship()` functions are exported but test for completely different things.

**Impact:** This can cause subtle type checking failures and runtime bugs. Code importing from `game.core.protocols` gets a different contract than code importing from `game.simulation.interfaces`. The different `is_combat_ship()` guard functions will return different results for the same object, leading to inconsistent behavior depending on import source.

**Recommendation:** Consolidate into one canonical `ICombatShip` definition. The `game/core/protocols.py` version is the better location (core layer is importable by all). The simulation-layer version should re-export from core, or be eliminated. The `is_combat_ship()` implementations need to be merged into a single guard that checks a canonical set of attributes.

**Effort:** Medium

---

### CRITICAL: Ship Portrait Loading - 5 Divergent Implementations

**ID:** IH-002
**Location:**
- `game/ui/screens/design_image_helper.py:60-90` (uses `replace(" ", "_").replace("-", "_")` for class normalization)
- `game/ui/panels/design_report_panel.py:185-214` (uses regex `r"(.*)\s+\((.*)\)"` parsing, includes `resources/Portraits/` fallback)
- `game/ui/panels/build_queue_portraits.py:95-124` (uses same regex, includes `resources/Portraits/` fallback, but shorter path list than design_report)
- `game/ui/screens/builder/right_panel.py:235-267` (uses same regex, different conditional branching, no path list)
- `game/ui/assets/ship_theme_manager.py:250-280` (canonical theme loading, different normalization entirely)

**Issue:** Five different implementations of "load a ship portrait image from a class name and theme" exist. They differ in:
1. **Class name normalization:** `design_image_helper` replaces spaces/hyphens with underscores. `design_report_panel`, `build_queue_portraits`, and `right_panel` use regex to handle `"Type (Subtype)"` format. `ship_theme_manager` has its own format.
2. **Fallback path lists:** `design_report_panel` checks 4 paths including `resources/Portraits/`. `build_queue_portraits` checks 3 paths. `design_image_helper` checks 3 paths but different ones. `right_panel` uses conditional if/else branching.
3. **Error handling:** Some catch `pygame.error` only, others catch `(FileNotFoundError, OSError, pygame.error)`.
4. **Fallback image:** Different approaches to creating placeholders when image is missing.

**Impact:** Adding a new ship theme or changing portrait file naming requires updating 5 different locations. Class names with parentheses (e.g., "Fighter (Medium)") will resolve to different filenames depending on which loader is used, causing inconsistent portrait display.

**Recommendation:** Extract a canonical `resolve_portrait_path(theme: str, ship_class: str) -> Optional[str]` function (in `design_image_helper.py` or `ship_theme_manager.py`). All 5 locations should call this single function. The normalization logic and search paths should live in exactly one place.

**Effort:** Medium

---

### MAJOR: Resource Icon Loading - 3 Divergent Copy-Paste Implementations

**ID:** IH-003
**Location:**
- `game/ui/panels/empire_treasury_panel.py:299-321` - Module-level `load_resource_icons()`, loads from `"Images/Resource Icons/"`, no fallback on failure (just skips), fixed 20x20 size
- `game/ui/panels/planet_report_panel.py:401-431` - Instance method `_load_resource_icons()`, loads from `"Images/Resource Portraits/"`, creates colored square fallback, configurable size
- `game/ui/panels/build_queue_portraits.py:195-224` - Instance method `load_resource_icons()`, loads from `"Images/Resource Portraits/"`, creates colored square fallback with logging, configurable size

**Issue:** Three implementations of resource icon loading that:
1. Load from **different directories** (`Resource Icons` vs `Resource Portraits`)
2. Use different filename mapping strategies (`resource_{type}_icon.png` vs `RESOURCE_PORTRAIT_FILES` dict)
3. Handle missing icons differently (skip silently vs create colored fallback square)
4. `planet_report_panel` and `build_queue_portraits` are near-clones but with slight differences in error handling

**Impact:** If resource icon files are reorganized, three locations must be updated. The `empire_treasury_panel` uses a completely different directory than the other two, which may or may not be intentional. Missing icons silently disappear in the treasury panel but show colored fallbacks elsewhere.

**Recommendation:** Create a shared `ResourceIconLoader` service or utility function that encapsulates icon loading, caching, and fallback generation. All three call sites should use this shared implementation.

**Effort:** Simple

---

### MAJOR: Path Resolution - Mixed os.getcwd() vs Paths Constants

**ID:** IH-004
**Location:**
- `game/core/paths.py` - Centralized `Paths` class with `ROOT_DIR`, `DATA_DIR`, etc.
- `game/ui/services/ship_io.py:95,142` - `os.path.join(os.getcwd(), ShipIO.default_ships_folder)`
- `game/ui/screens/builder/stats_config.py:305` - `os.path.join(os.getcwd(), 'data', 'stats_layout.json')`
- `game/strategy/data/galaxy.py:178,185` - `os.path.join(os.getcwd(), 'data', ...)`
- `game/ui/screens/workshop_data_reloader.py:102,115,123` - `os.path.join(os.getcwd(), "data")`
- `game/ui/screens/workshop_data_loader.py:56` - `os.path.join(os.getcwd(), "data")`

**Issue:** The project has a well-designed centralized `Paths` class that resolves the project root at import time by walking up directory trees. However, 6+ files still use `os.getcwd()` to construct paths to data files. `os.getcwd()` is fragile -- it depends on where the process was started, which can vary between IDE launches, command-line runs, and test runners.

**Impact:** Running the game from a non-root directory (e.g., `python -m game.app` from a subdirectory) will break these path resolutions while `Paths.DATA_DIR` will work correctly. Test environments may also have different working directories.

**Recommendation:** Replace all `os.getcwd()` path constructions with the equivalent `Paths.DATA_DIR`, `Paths.SHIPS_DIR`, etc. constants. The `Paths` class already provides all needed directories.

**Effort:** Simple

---

### MAJOR: Singleton Pattern - Two Implementations Coexist

**ID:** IH-005
**Location:**
- `game/core/singleton.py` - `SingletonMeta` metaclass (used by 8 classes: AssetManager, StrategyManager, RegistryManager, Profiler, StrategyMetadataService, ShipThemeManager, ScreenshotManager, SpriteManager)
- `game/simulation/components/component.py:444-474` - `ComponentCacheManager` with hand-rolled `_instance = None` / `_lock = threading.Lock()` singleton

**Issue:** The project has a canonical `SingletonMeta` metaclass with proper double-checked locking, thread safety, and `reset()` for test isolation. However, `ComponentCacheManager` implements its own singleton pattern manually with the same double-checked locking logic duplicated. The manual version's `reset()` also behaves differently -- it clears instance fields rather than destroying the instance.

**Impact:** The duplicate implementation adds maintenance burden and the different `reset()` semantics could cause subtle test isolation issues. The `ComponentCacheManager.reset()` clears cache fields but keeps the same instance, while `SingletonMeta.reset()` destroys the instance entirely so `__init__` runs fresh.

**Recommendation:** Convert `ComponentCacheManager` to use `SingletonMeta`. This is a simple change: `class ComponentCacheManager(metaclass=SingletonMeta):` and remove the `_instance`, `_lock`, `instance()`, and `reset()` boilerplate. Adjust any code that calls `ComponentCacheManager.reset()` if needed.

**Effort:** Simple

---

### MAJOR: ABC vs Protocol for Interface Definitions

**ID:** IH-006
**Location:**
- **ABC-based interfaces (13 classes):** `game/ai/interfaces/controllable.py` (`IControllable`), `game/strategy/interfaces/engines.py` (11 engine interfaces: `IMovementEngine`, `IProductionEngine`, etc.), `game/strategy/interfaces/battle_resolver.py` (`IBattleResolver`)
- **Protocol-based interfaces (37+ classes):** `game/core/protocols.py` (20+), `game/simulation/interfaces/` (12+), `game/ai/protocols.py` (3), `game/strategy/engine/command_handlers.py` (`ICommandHandler`), `game/ui/interfaces/battle_ui.py` (`IBattleUI`)

**Issue:** The codebase uses two fundamentally different approaches for defining interfaces:
- **ABC** (Abstract Base Class): Requires explicit inheritance, raises `TypeError` at instantiation if methods not implemented. Used exclusively in `strategy/interfaces/engines.py` and `ai/interfaces/controllable.py`.
- **Protocol**: Structural (duck) typing, no inheritance required. Used everywhere else.

The strategy engine interfaces all use ABC, while similar interfaces in simulation and core use Protocol. Both approaches prefix with `I` following the same naming convention, making it unclear which pattern a new interface should follow.

**Impact:** Contributors don't know which pattern to use for new interfaces. ABC requires explicit subclassing while Protocol enables structural typing -- these are architecturally different choices with different trade-offs. Mixing them creates confusion about the project's interface philosophy.

**Recommendation:** Standardize on **Protocol** for all interfaces, as it is already the dominant pattern (37+ vs 13 classes) and aligns better with Python's duck typing philosophy. The `strategy/interfaces/engines.py` ABC interfaces can be converted to Protocol. `IControllable` in AI would need a more careful migration since `ShipControllableAdapter` explicitly inherits from it.

**Effort:** Complex

---

### MINOR: JSON File I/O - Direct json.load/json.dump Usage Persists

**ID:** IH-007
**Location:**
- `game/core/json_utils.py` - Canonical module with `load_json()`, `load_json_required()`, `save_json()`
- Files that `import json` but don't use json_utils for file I/O:
  - `game/simulation/services/registry_loader.py:15` - imports json for JSONDecodeError catches
  - `game/strategy/systems/race_library.py:7` - imports json (uses for JSONDecodeError)
  - `game/strategy/data/naming.py:36` - uses raw `yaml.safe_load()` with `open()` (YAML, not JSON, but same pattern of raw file I/O)
  - `game/ui/screens/test_lab/validation_manager.py:238,295` - uses raw `open()` for reading/writing Python scenario files

**Issue:** The `json_utils.py` module header explicitly states "Do NOT use json.load/json.dump directly for file operations in game/". Most of the codebase has been migrated (35+ files import from json_utils), but a few modules still import `json` directly. Some of these import it only for `JSONDecodeError` exception types (which is acceptable), but the pattern looks inconsistent at first glance.

**Impact:** Low -- the remaining direct `json` imports are mostly for exception types or non-JSON files. The migration is 95%+ complete.

**Recommendation:** For files that import `json` only for `JSONDecodeError`, consider importing the exception directly: `from json import JSONDecodeError`. This makes the intent clearer and avoids the visual inconsistency of `import json` alongside `from game.core.json_utils import ...`.

**Effort:** Simple

---

### MINOR: Path Style - os.path vs pathlib.Path Mixed Throughout

**ID:** IH-008
**Location:**
- `game/core/paths.py` - `Paths` class uses `os.path.join()` for all string attributes but provides `pathlib.Path` accessors via `get_root()`, `get_data_dir()`, etc.
- `game/core/json_utils.py` - Accepts `Union[str, Path]`, converts to `Path` internally
- `game/simulation/services/registry_loader.py` - Uses `pathlib.Path` directly
- `game/strategy/generation/loaders/` - Uses `pathlib.Path` for `DEFAULT_PATH` constants
- Most other files - Use `os.path.join()` string manipulation

**Issue:** The codebase mixes `os.path` string operations and `pathlib.Path` objects. The `Paths` class itself stores paths as strings using `os.path.join()` but provides `pathlib.Path` accessors that are rarely used. Newer code (loaders, json_utils) tends to use `pathlib.Path`, while older code uses `os.path.join()`.

**Impact:** Low -- both approaches work. The inconsistency is mainly aesthetic and represents a natural evolution of the codebase. `pathlib.Path` is more Pythonic but `os.path` strings are more compatible with legacy code.

**Recommendation:** For new code, prefer `pathlib.Path`. Consider gradually migrating `Paths` class attributes to `Path` objects (keeping string accessors via `str()` for backward compatibility). Not urgent.

**Effort:** Complex (widespread, but low priority)

---

### MINOR: strategy_detail_fmt.py vs strategy_detail_formatter.py - Confusing Module Split

**ID:** IH-009
**Location:**
- `game/ui/screens/strategy_detail_fmt.py` - Free functions for formatting HTML reports (format_spectrum_html, format_planet_info, etc.)
- `game/ui/screens/strategy_detail_formatter.py` - Class `StrategyDetailFormatter` extracted from strategy_ui.py (PROJ-86)

**Issue:** Two similarly-named modules handle detail formatting for the strategy screen. `strategy_detail_fmt.py` contains pure formatting functions, while `strategy_detail_formatter.py` is a class that imports from `strategy_detail_fmt.py` and adds UI management (planet report panels, raw data popups). The `strategy_detail_formatter.py` file even documents "Thin Wrappers to strategy_detail_fmt" on line 121.

**Impact:** The similar names are confusing. A developer looking for detail formatting code has to figure out which module to look at. The thin wrapper methods in `StrategyDetailFormatter` that just delegate to `strategy_detail_fmt` functions add unnecessary indirection.

**Recommendation:** Rename `strategy_detail_fmt.py` to something more distinctive like `strategy_html_formatting.py` or merge the pure functions into the formatter class. Alternatively, inline the thin wrapper methods to eliminate the indirection.

**Effort:** Simple

---

### MINOR: Thin Adapter Layer for Design Loading

**ID:** IH-010
**Location:**
- `game/simulation/services/design_loader.py` - `SimulationDesignLoader` (the real implementation)
- `game/ui/services/design_loader_adapter.py` - `DesignLoaderAdapter` (delegates 100% to SimulationDesignLoader)

**Issue:** `DesignLoaderAdapter` is a pure passthrough adapter -- every method simply calls the corresponding method on `SimulationDesignLoader` with the same parameters. It was created as part of PROJ-43 to provide a "clean interface for UI code" but provides no additional logic, transformation, or abstraction. Similarly, `ShipIOAdapter` in `game/ui/services/ship_io_adapter.py` is a thin wrapper around `ShipIO`.

**Impact:** The adapter adds a layer of indirection with no behavioral difference. It increases the number of files to navigate and maintain without providing meaningful abstraction. However, it does exist for a legitimate architectural reason (layer separation).

**Recommendation:** Keep these adapters if strict layer separation is important to the project. If not, UI code could import `SimulationDesignLoader` directly (simulation layer is a valid dependency for UI). The adapters are harmless but add cognitive overhead.

**Effort:** N/A (architectural decision)

---

### INFO: Validation Return Patterns - Mostly Consistent

**ID:** IH-011
**Location:**
- `game/core/validation.py:64` - `ValidationResult` dataclass (canonical)
- All validation methods return `ValidationResult` consistently

**Issue:** The codebase uses a single `ValidationResult` dataclass from `game/core/validation.py` consistently across simulation, strategy, and UI layers. A few validation methods in older code use `tuple[bool, str]` returns (e.g., `race_config.py:337` `_validate_required_fields`, `race_setup_screen.py:735` `_validate_for_save`), but these are private helper methods that feed into a public method returning `ValidationResult`.

**Impact:** Very low -- the public API is consistent. The private tuple-returning helpers are internal implementation details.

**Recommendation:** No action needed. The public validation API is well-standardized.

**Effort:** N/A

---

### INFO: Logging Setup - Consistent Pattern

**ID:** IH-012
**Location:** 40+ files across all layers

**Issue:** The codebase consistently uses `logger = logging.getLogger(__name__)` at module level. One exception: `game/ui/panels/design_report_panel.py:215-216` creates a logger inside a method body. Another: `game/ai/__init__.py:57-59` and `game/core/event_logging.py:7-8` create loggers inside `if` blocks (intentional for conditional imports).

**Impact:** Negligible -- the inline logger creation is a minor deviation, not a bug.

**Recommendation:** Move the `design_report_panel.py` logger to module level for consistency. No other action needed.

**Effort:** Simple

---

## Top 5 Priority Issues

1. **IH-001 (CRITICAL): Duplicate ICombatShip Protocol** - Two conflicting definitions of the same interface with different type guard implementations. High risk of subtle bugs. Fix by consolidating to one canonical definition.

2. **IH-002 (CRITICAL): Ship Portrait Loading - 5 Divergent Implementations** - Same logic copy-pasted and modified 5 times with different normalization, path lists, and error handling. Extract to one shared function.

3. **IH-003 (MAJOR): Resource Icon Loading - 3 Copy-Paste Variants** - Three near-identical implementations loading resource icons from different directories with different fallback behavior. Consolidate into one utility.

4. **IH-004 (MAJOR): os.getcwd() vs Paths Constants** - 6+ files use fragile `os.getcwd()` despite a robust centralized `Paths` class. Simple fix: replace with `Paths.DATA_DIR` etc.

5. **IH-005 (MAJOR): Duplicate Singleton Pattern** - `ComponentCacheManager` hand-rolls the same singleton logic that `SingletonMeta` provides. Convert to use the canonical metaclass.
