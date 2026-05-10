# Convention Enforcer Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~95K lines)
**Reviewer:** Claude Code (Convention Enforcer Agent)

---

## Summary

- **Total issues found:** 18
- **Critical:** 1
- **Major:** 5
- **Minor:** 8
- **Info:** 4

Overall the codebase follows conventions with strong consistency. File naming is 100% snake_case, cross-layer import rules are strictly enforced (zero violations), and the `__init__.py` pattern with `__all__` is used in 38 of 42 non-empty init files. The main areas of inconsistency are: missing `__init__.py` files in several heavily-imported packages, mixed use of ABC vs Protocol for interfaces, and uneven type hint coverage across layers.

---

## Findings

### CE-01 -- CRITICAL: Missing `__init__.py` in Heavily-Imported Packages

**ID:** CE-01
**Location:** `game/simulation/entities/`, `game/simulation/systems/`, `game/strategy/engine/`, `game/strategy/systems/`
**Issue:** Six directories under `game/` lack `__init__.py` files, making them implicit namespace packages. Four of these (`simulation/entities`, `simulation/systems`, `strategy/engine`, `strategy/systems`) are heavily imported across the codebase. Meanwhile, sibling directories like `simulation/combat/`, `simulation/managers/`, `strategy/data/`, `strategy/events/` all have `__init__.py` with proper `__all__` exports.
**Impact:** Namespace packages work in Python 3 but have subtle behavior differences: they are slower to import, don't support relative imports reliably (yet `simulation/entities/ship.py` uses 7 relative imports), and break the consistent re-export pattern used everywhere else. If a third-party package ever creates a conflicting namespace, these could silently shadow.
**Affected directories:**
- `game/simulation/entities/` (13 .py files, uses relative imports)
- `game/simulation/systems/` (4 .py files)
- `game/strategy/engine/` (20 .py files -- largest missing init)
- `game/strategy/systems/` (4 .py files)
- `game/assets/` (1 .py file)
- `game/data/` (0 .py files, just JSON -- acceptable)
**Recommendation:** Add `__init__.py` with docstring, re-exports, and `__all__` to the first four directories. `game/data/` is fine without one (no Python modules). `game/assets/` should get a minimal one for consistency.
**Effort:** Simple

---

### CE-02 -- MAJOR: Mixed ABC vs Protocol for Interface Definitions

**ID:** CE-02
**Location:** `game/*/interfaces/` directories and `game/*/protocols.py` files
**Issue:** The codebase uses two different mechanisms for defining interfaces, with no clear rule for when to use which:
- **Protocol (structural typing):** Used in `simulation/interfaces/` (4 files, ~17 protocols), `core/protocols.py` (23 protocols), `ai/protocols.py` (4 protocols), `ui/interfaces/` (2 protocols), plus 5 other scattered files
- **ABC (nominal typing):** Used in `strategy/interfaces/` (11 ABCs in `engines.py`, 1 ABC in `battle_resolver.py`), `ai/interfaces/controllable.py` (1 ABC), `simulation/combat/battle_mode_handler.py` (1 ABC), `simulation/validation/base.py` (1 ABC), `ui/panels/base_gallery.py` (1 ABC)
**Impact:** Two patterns for the same purpose creates confusion about which to use for new interfaces. Protocol is the modern Python approach for duck-typing, while ABC requires explicit inheritance. The codebase leans heavily toward Protocol (54 Protocol classes vs 16 ABC classes) but ABC persists in strategy interfaces.
**Recommendation:** Standardize on Protocol for new interfaces. Existing ABCs can remain but should not be the pattern for new code. Document the convention.
**Effort:** Medium (documentation now, gradual migration)

---

### CE-03 -- MAJOR: Protocol Files Outside `interfaces/` Directories

**ID:** CE-03
**Location:** `game/ai/protocols.py`, `game/core/protocols.py`
**Issue:** The `ai` and `core` packages define protocols in top-level `protocols.py` files, while `simulation`, `strategy`, and `ui` packages organize their interfaces in `interfaces/` subdirectories. This is inconsistent: should protocols live in `<pkg>/protocols.py` or `<pkg>/interfaces/`?
- `game/ai/` has BOTH `protocols.py` (4 protocols) AND `interfaces/controllable.py` (1 ABC)
- `game/core/` has `protocols.py` (23 protocols) but no `interfaces/` directory
**Impact:** Contributors must check two locations for interface definitions within the same package. The `ai` package is the worst case with both patterns present.
**Recommendation:** Consolidate: either move `protocols.py` content into `interfaces/` subdirectories, or choose `protocols.py` as the standard and move `interfaces/` content into it. Given the codebase majority uses `interfaces/` dirs, that should be the standard.
**Effort:** Medium

---

### CE-04 -- MAJOR: Uneven Return Type Hint Coverage

**ID:** CE-04
**Location:** Across all packages
**Issue:** Return type hint coverage varies dramatically across packages:
| Package | Coverage |
|---------|----------|
| research | 95% |
| core | 91% |
| ai | 89% |
| strategy | 86% |
| simulation | 77% |
| engine | 46% |
| ui | 46% |
| assets | 23% |
| app.py | 2% |
| exit_dialog.py | 0% |

Total: 2720/4246 functions (64%) have return type hints.
**Impact:** The CLAUDE.md convention says "Use type hints for function signatures." The `ui` layer (2135 functions, 46% coverage) is the largest offender by volume. The `engine` package (46%) and `assets` (23%) are also low.
**Recommendation:** Prioritize adding return types to `engine/` (only 15 functions) and `app.py` (42 functions) as quick wins. The `ui` layer is a larger effort but should be addressed incrementally.
**Effort:** Complex (for full coverage), Simple (for engine/app.py)

---

### CE-05 -- MAJOR: Directories Without `__init__.py` Use Relative Imports

**ID:** CE-05
**Location:** `game/simulation/entities/ship.py`
**Issue:** `ship.py` uses 7 relative imports (`from .ship_stats import ...`, `from .ship_physics import ...`, etc.) despite `game/simulation/entities/` having no `__init__.py`. Relative imports in namespace packages are technically supported but fragile and against PEP 328 original intent. No other namespace package directory in this codebase uses relative imports.
**Impact:** This works today but could break if the package resolution changes. It also sets a bad precedent -- other namespace package dirs (`strategy/engine/`, `strategy/systems/`, `simulation/systems/`) use only absolute imports.
**Recommendation:** Add `__init__.py` to `game/simulation/entities/` (see CE-01) which makes relative imports proper and expected.
**Effort:** Simple

---

### CE-06 -- MAJOR: `exit_dialog.py` at `game/` Root

**ID:** CE-06
**Location:** `game/exit_dialog.py`
**Issue:** `exit_dialog.py` is a UI component placed at the `game/` root level alongside `app.py` and `__init__.py`. It should live in `game/ui/` since it is a UI dialog. `app.py` is appropriately at the root as the application entry point.
**Impact:** Violates the layer separation convention where UI code belongs in `game/ui/`. Minor but breaks the clean package boundary.
**Recommendation:** Move to `game/ui/widgets/exit_dialog.py` or `game/ui/components/exit_dialog.py`.
**Effort:** Simple

---

### CE-07 -- MINOR: `__init__.py` Missing `__all__` in `game/ui/screens/builder/`

**ID:** CE-07
**Location:** `game/ui/screens/builder/__init__.py`
**Issue:** This is the only non-empty `__init__.py` that has re-exports but no `__all__` list. All 37 other non-empty init files define `__all__`. The file imports 7 names from submodules but does not declare what the public API is.
**Impact:** `from game.ui.screens.builder import *` would export everything including private names. Inconsistent with the otherwise universal `__all__` convention.
**Recommendation:** Add `__all__` listing the 7 exported names.
**Effort:** Simple

---

### CE-08 -- MINOR: Properties Intermixed with Public Methods in 11 Classes

**ID:** CE-08
**Location:** Multiple files (listed below)
**Issue:** The dominant class organization pattern is: `__init__` -> `@property` accessors -> public methods -> private methods. 33 classes follow this pattern, but 11 classes intermix properties among public methods:
- `game/core/strategy_metadata.py`: StrategyMetadataService
- `game/simulation/battle_controller.py`: BattleController
- `game/simulation/components/component.py`: Component
- `game/simulation/components/component_health_manager.py`: ComponentHealthManager
- `game/simulation/components/abilities/base.py`: Ability
- `game/simulation/entities/ship_stat_querier.py`: ShipStatQuerier
- `game/ui/components/table/virtual_table.py`: VirtualTable
- `game/ui/screens/battle_screen.py`: BattleScreen
- `game/ui/screens/strategy_renderer.py`: StrategyRenderer
- `game/ui/screens/workshop_screen.py`: DesignWorkshopScreen
- `game/ui/screens/builder/weapons_panel.py`: WeaponsReportPanel
**Impact:** Inconsistent method ordering makes classes harder to navigate. Properties scattered throughout make the class API less discoverable.
**Recommendation:** When refactoring these classes, group properties after `__init__` and before public methods.
**Effort:** Simple per class, but low priority

---

### CE-09 -- MINOR: Mutable Module-Level Constants Using Lists/Dicts

**ID:** CE-09
**Location:** 57 instances across `core/constants.py`, `simulation/formula_system.py`, `strategy/data/race_config.py`, and others
**Issue:** Constants defined as module-level mutable collections (lists, dicts, sets) when they should be immutable. Examples:
- `PLANET_RESOURCES = ["Metals", "Organics", ...]` (should be tuple)
- `ALLOWED_MATH_FUNCTIONS = { ... }` (should be frozenset)
- `GOVERNMENT_TYPES = [ ... ]` (should be tuple)
**Impact:** These "constants" can be accidentally mutated. Using tuples/frozensets would make the intent explicit and catch accidental mutation.
**Recommendation:** Replace list literals with tuples and set literals with frozensets for true constants. Dict constants are acceptable if they serve as registries.
**Effort:** Simple (mechanical find-and-replace)

---

### CE-10 -- MINOR: Singleton Pattern Used in 8 Files

**ID:** CE-10
**Location:** `game/ai/strategy_manager.py`, `game/assets/asset_manager.py`, `game/core/profiling.py`, `game/core/registry.py`, `game/core/strategy_metadata.py`, `game/ui/assets/ship_theme_manager.py`, `game/ui/renderer/sprites.py`, `game/ui/screens/builder_utils.py`, `game/ui/services/screenshot_manager.py`
**Issue:** The codebase uses `SingletonMeta` (defined in `game/core/singleton.py`) in 8 files. This is at odds with the CLAUDE.md preference for "Dependency injection over singletons." The registry system (`RegistryManager`) is itself a singleton.
**Impact:** Singletons make testing harder and create hidden global state. The project already has a DI system via registries, so singletons for managers are arguably unnecessary.
**Recommendation:** Document which singletons are acceptable (e.g., RegistryManager as the DI root) and flag the rest for eventual migration to DI. No immediate action needed.
**Effort:** Complex (requires DI wiring changes)

---

### CE-11 -- MINOR: Dataclass Frozen/Mutable Split Inconsistent in DTOs

**ID:** CE-11
**Location:** `game/strategy/facade/dto/`, `game/strategy/engine/commands.py`
**Issue:** DTOs in `game/strategy/facade/dto/` correctly use `@dataclass(frozen=True)` (15 frozen dataclasses). However, command dataclasses in `game/strategy/engine/commands.py` (28 dataclasses) are mutable despite being value objects that should be immutable after creation. Similarly, many `strategy/engine/` dataclasses representing configuration or results are mutable.
**Impact:** Mutable command objects could be accidentally modified after dispatch. The facade DTOs show the correct pattern.
**Recommendation:** Make command dataclasses frozen. Review other mutable dataclasses in `strategy/engine/` for candidates.
**Effort:** Medium

---

### CE-12 -- MINOR: `game/ui/components/__init__.py` Has Only a Docstring

**ID:** CE-12
**Location:** `game/ui/components/__init__.py`
**Issue:** Contains only `"""Reusable UI components."""` with no re-exports. Three other files have only docstrings (`game/research/__init__.py`, `game/strategy/facade/__init__.py`). These are categorized as "docstring_only" while the dominant pattern (38 files) is "exports + `__all__`".
**Impact:** Users must import from submodules directly rather than from the package. This may be intentional for large packages but is inconsistent.
**Recommendation:** If the package has a clear public API, add re-exports. If it is intentionally a namespace-only package, document why.
**Effort:** Simple

---

### CE-13 -- MINOR: `game/strategy/events/__init__.py` Exports Without Matching `__all__`

**ID:** CE-13
**Location:** `game/strategy/events/__init__.py`
**Issue:** The file imports `Event`, `EventLog`, `EventCategory`, `EventType` but its `__all__` is either missing these or mismatched. This is the one case where imports exist but `__all__` doesn't cover them properly.
**Impact:** `from game.strategy.events import *` may not export what callers expect.
**Recommendation:** Ensure `__all__` lists all four exported names.
**Effort:** Simple

---

### CE-14 -- MINOR: Large Files Exceeding 500 Lines (54 files)

**ID:** CE-14
**Location:** 54 files across the codebase
**Issue:** 54 Python files exceed 500 lines. Top offenders:
- `ui/screens/strategy_renderer.py` (1102 lines)
- `ui/screens/test_lab/renderer.py` (1040 lines)
- `strategy/engine/command_handlers.py` (1032 lines)
- `ui/screens/race_setup_screen.py` (1029 lines)
- `core/protocols.py` (987 lines)
**Impact:** Large files are harder to navigate and often indicate classes with too many responsibilities. Some of these (like `command_handlers.py` with 19 classes, or `protocols.py` with 23 protocols) are acceptable as collections of related small classes. Renderers and screens are the main concern.
**Recommendation:** This is tracked separately by PROJ-86/87/88/89 (God Class Decomposition). No additional action needed.
**Effort:** Complex (already tracked)

---

### CE-15 -- INFO: File Naming 100% Consistent

**ID:** CE-15
**Location:** All 429 Python files
**Issue:** None -- all Python files follow `snake_case.py` naming. Zero violations found.
**Impact:** Positive finding.
**Recommendation:** Maintain this standard.
**Effort:** N/A

---

### CE-16 -- INFO: Cross-Layer Import Rules Strictly Enforced

**ID:** CE-16
**Location:** All imports across `game/`
**Issue:** None -- zero violations of the layer dependency rules found:
- `core` imports nothing from other game layers
- `engine` imports nothing from other game layers
- `simulation` does not import from `strategy`, `ui`, or `ai`
- `strategy` does not import from `ui`
**Impact:** Positive finding. The architecture boundaries are clean.
**Recommendation:** Maintain this standard. Consider automated enforcement via import linter.
**Effort:** N/A

---

### CE-17 -- INFO: Absolute Imports Strongly Preferred

**ID:** CE-17
**Location:** All imports
**Issue:** The codebase uses 1567 absolute imports vs 77 relative imports (95.3% absolute). Relative imports are concentrated in two areas:
- `game/simulation/entities/` (11 relative imports in 3 files -- see CE-05)
- `game/simulation/components/abilities/` (various submodule imports)
- `game/ui/screens/builder/` and `game/ui/screens/test_lab/` (submodule imports)
**Impact:** Positive finding. Absolute imports are clearer and the strong preference is good.
**Recommendation:** Relative imports within small sub-packages (abilities, builder, test_lab) are acceptable. The `entities/` case should be addressed per CE-05.
**Effort:** N/A

---

### CE-18 -- INFO: No Print Statements in Production Code

**ID:** CE-18
**Location:** All 429 Python files
**Issue:** None -- zero `print()` calls found in production code (AST-verified). All apparent `print()` matches were in docstring examples. 142 files use the `logging` module properly.
**Impact:** Positive finding. Logging discipline is excellent.
**Recommendation:** Maintain this standard.
**Effort:** N/A

---

## Convention Summary Table

| Convention | Expected Pattern | Violations | Key Locations |
|------------|-----------------|------------|---------------|
| File naming | `snake_case.py` | 0 | All files compliant |
| `__init__.py` presence | All packages have one | 5 dirs missing | `simulation/entities`, `simulation/systems`, `strategy/engine`, `strategy/systems`, `assets` |
| `__all__` in `__init__.py` | All non-empty inits have `__all__` | 1 | `ui/screens/builder/__init__.py` |
| `__init__.py` pattern | Docstring + imports + `__all__` | 3 | docstring-only inits in `research`, `strategy/facade`, `ui/components` |
| Interface mechanism | Protocol preferred | Mixed ABC+Protocol in `interfaces/` | `strategy/interfaces/` uses ABC; `simulation/interfaces/` uses Protocol |
| Interface location | `<pkg>/interfaces/` dir | 2 pkgs use `protocols.py` instead | `core/protocols.py`, `ai/protocols.py` |
| Return type hints | All functions typed | 35% missing (1526 funcs) | `ui` (46%), `engine` (46%), `app.py` (2%) |
| Module docstrings | All files have one | 34 files missing | `simulation` (12), `ui` (11), `strategy` (7) |
| Import style | Absolute | 77 relative imports | `simulation/entities/`, `ui/screens/builder/`, `simulation/components/abilities/` |
| Cross-layer imports | Layer rules enforced | 0 violations | All clean |
| Class method ordering | `__init__` -> props -> public -> private | 11 classes mixed | `ship.py`, `component.py`, `battle_controller.py`, etc. |
| Logging | `logging` module, no `print()` | 0 violations | All clean |
| Constants immutability | Tuples/frozensets for constants | ~57 mutable constants | `core/constants.py`, `strategy/data/race_config.py` |
| Singletons | Prefer DI | 8 singleton classes | `registry.py`, `asset_manager.py`, etc. |
| Dataclass frozen | Frozen for value objects | ~28 mutable commands | `strategy/engine/commands.py` |
| UI code placement | In `game/ui/` | 1 file misplaced | `game/exit_dialog.py` |

---

## Top 5 Priority Issues

1. **CE-01 (Critical): Missing `__init__.py` in 4 core packages** -- `simulation/entities/`, `simulation/systems/`, `strategy/engine/` (20 files!), `strategy/systems/`. These are heavily imported and should have proper package init files with `__all__` exports. Quick fix, high consistency win.

2. **CE-04 (Major): UI layer has only 46% return type hint coverage** -- 2135 functions, 994 typed. The `engine` package (46%) and `app.py` (2%) are quick wins. The `ui` layer needs a systematic effort.

3. **CE-02 (Major): Mixed ABC vs Protocol** -- Standardize on Protocol for new interface definitions. The strategy layer's `interfaces/` directory uses ABC while simulation uses Protocol. Document the convention.

4. **CE-03 (Major): Protocol files in inconsistent locations** -- `ai` has both `protocols.py` AND `interfaces/` directory. Consolidate to one pattern (prefer `interfaces/` subdirectory).

5. **CE-11 (Minor): Command dataclasses should be frozen** -- 28 command dataclasses in `strategy/engine/commands.py` are mutable. These are value objects dispatched through the command system and should be frozen to prevent accidental mutation, matching the DTO pattern.
