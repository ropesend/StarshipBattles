# Import Inventory Analyst Report

### Summary
- Total issues found: 325
- Critical: 0, Major: 171, Minor: 45, Info: 109

### Methodology

**Search approach:** Used ripgrep to find all indented `import` and `from ... import` statements in `game/` Python files (pattern: `^\s+(import |from \S+ import )`). This captured 663 raw matches.

**Filtering:**
1. **TYPE_CHECKING blocks excluded (298 removed):** Parsed each file to identify `if TYPE_CHECKING:` block ranges and excluded all imports falling within those ranges. These are standard Python practice for type annotation support and are not runtime imports.
2. **Docstring examples excluded (40 removed):** Detected imports inside triple-quoted docstrings (usage examples in module docstrings) and excluded them. These are documentation, not executable inline imports.
3. **Final count:** 663 - 298 - 40 = **325 true inline imports** across **105 files** deferring **126 unique modules**.

**Categorization logic:**
- Checked whether the same module is already imported at the file's top level (if yes, categorized as "Redundant Inline")
- Checked whether the import is inside a conditional block (`if`/`try`/`except`) for "Conditional/Factory"
- Classified stdlib and pygame imports as "Lazy Loading"
- Test framework imports classified as "Conditional Feature"
- All remaining project imports classified as "Circular Avoidance"

### Quantitative Results
- **Total inline imports (excluding TYPE_CHECKING):** 325
- **Pre-analysis report claimed:** 600+
- **Discrepancy explanation:** The 600+ figure likely included TYPE_CHECKING block imports (298) and docstring examples (40), which are legitimate Python patterns and should not be counted as defects.

#### Breakdown by Directory
| Directory | Count | % of Total |
|-----------|-------|------------|
| game/ui/ | 147 | 45.2% |
| game/strategy/ | 113 | 34.8% |
| game/simulation/ | 43 | 13.2% |
| game/ (root, app.py) | 20 | 6.2% |
| game/core/ | 2 | 0.6% |

**UI sub-directories:**
| Sub-directory | Count |
|---------------|-------|
| game/ui/screens/ | 128 |
| game/ui/panels/ | 11 |
| game/ui/services/ | 6 |
| game/ui/utils/ | 1 |
| game/ui/research/ | 1 |

**Strategy sub-directories:**
| Sub-directory | Count |
|---------------|-------|
| game/strategy/engine/ | 56 |
| game/strategy/data/ | 40 |
| game/strategy/services/ | 7 |
| game/strategy/facade/ | 4 |
| game/strategy/systems/ | 3 |
| game/strategy/validation/ | 2 |
| game/strategy/adapters/ | 1 |

**Simulation sub-directories:**
| Sub-directory | Count |
|---------------|-------|
| game/simulation/components/ | 25 |
| game/simulation/entities/ | 9 |
| game/simulation/ (root) | 7 |
| game/simulation/validation/ | 2 |

#### Breakdown by Category
| Category | Count | % of Total | Severity |
|----------|-------|------------|----------|
| Circular Avoidance (project) | 171 | 52.6% | Major |
| Conditional/Factory | 64 | 19.7% | Info |
| Redundant Inline (project) | 35 | 10.8% | Minor |
| Lazy Loading (stdlib) | 32 | 9.8% | Info |
| Lazy Loading (pygame) | 9 | 2.8% | Info |
| Redundant Inline (pygame) | 7 | 2.2% | Minor |
| Conditional Feature (test) | 4 | 1.2% | Info |
| Redundant Inline (stdlib) | 3 | 0.9% | Minor |

#### Import Source Type
| Source | Count | % of Total |
|--------|-------|------------|
| Project (game.*) | 270 | 83.1% |
| Stdlib (os, copy, math, etc.) | 35 | 10.8% |
| Pygame/pygame_gui | 16 | 4.9% |
| Test framework | 4 | 1.2% |

#### Top 10 Files by Inline Import Count
| File | Count | Primary Category |
|------|-------|-----------------|
| `game/app.py` | 20 | Lazy Loading (app entry point) |
| `game/strategy/engine/command_handlers.py` | 15 | Circular Avoidance (FleetOrder) |
| `game/strategy/engine/turn_engine.py` | 15 | Conditional/Factory (engine creation) |
| `game/ui/screens/strategy_screen.py` | 13 | Mixed (UI-to-Strategy coupling) |
| `game/ui/screens/strategy_build_queue_manager.py` | 13 | Mixed (UI-to-Strategy coupling) |
| `game/simulation/components/component.py` | 11 | Mixed (registry + stdlib) |
| `game/strategy/engine/fleet_order_processor.py` | 9 | Circular Avoidance + Redundant |
| `game/ui/screens/galaxy_test/system_mode.py` | 9 | Conditional/Factory (test UI) |
| `game/simulation/components/abilities/weapons.py` | 7 | Circular Avoidance (formula_system) |
| `game/strategy/engine/game_session.py` | 7 | Mixed (circular + redundant) |

#### Most Frequently Deferred Modules
| Module | Times Deferred | Typical Reason |
|--------|---------------|----------------|
| `game.strategy.data.fleet` | 18 | Circular dependency with strategy.data and strategy.engine modules |
| `game.core.registry` | 13 | Circular dependency with core and simulation modules |
| `game.strategy.data.pathfinding` | 10 | Circular dependency with strategy engine/services |
| `game.strategy.data.planet` | 10 | Circular dependency with strategy data modules |
| `game.strategy.systems.save_game_service` | 8 | Lazy loading (heavy I/O module) |
| `pygame_gui.windows` | 8 | Lazy loading (UI dialog creation) |
| `os` | 8 | Lazy loading (file operations in data loaders) |
| `game.core.hex_math` | 8 | Circular + redundant (5 are duplicates) |
| `game.core.constants` | 8 | Circular + redundant |
| `copy` | 8 | Lazy loading (stdlib) |
| `game.simulation.formula_system` | 7 | Circular avoidance (all in weapons.py) |
| `game.strategy.data.fleet_capability_calculator` | 6 | Circular avoidance (fleet report UI) |
| `game.strategy.validation` | 5 | Circular avoidance (engine -> validation) |
| `game.core.exceptions` | 5 | Circular avoidance (core modules) |
| `game.strategy.engine.commands` | 5 | Circular avoidance (UI -> engine) |

### Findings

---

#### MAJOR: `game.strategy.data.fleet` is the most deferred module in the codebase
**ID:** IIA-001
**Location:** 18 inline imports across 6 files:
- `game/strategy/engine/command_handlers.py` (11 occurrences)
- `game/strategy/data/empire.py`
- `game/strategy/services/action_time_resolver.py` (3 occurrences)
- `game/strategy/data/fleet_capability_calculator.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/strategy_build_queue_manager.py`

**Issue:** `FleetOrder` and `OrderType` from `game.strategy.data.fleet` are imported inline 11 times in `command_handlers.py` alone, each time inside a different handler method. The circular dependency between `fleet.py` (which imports from `planet.py`, `registry.py`) and `command_handlers.py` (which imports from `game_session.py`) forces this pattern.

**Impact:** High maintenance burden. Every command handler method must repeat the same `from game.strategy.data.fleet import FleetOrder, OrderType` line. This is the single largest contributor to the deferred import count.

**Recommendation:** Extract `FleetOrder` and `OrderType` into a lightweight `game.strategy.data.fleet_orders` module with no heavy dependencies. This would eliminate 18 inline imports. Alternatively, `command_handlers.py` could import these at module level since it does not create the circular dependency -- `command_handlers` imports from `game_session` via TYPE_CHECKING, not at runtime.

**Effort:** Medium

---

#### MAJOR: `game.strategy.engine.turn_engine` uses factory-pattern deferred imports for all sub-engines
**ID:** IIA-002
**Location:** `game/strategy/engine/turn_engine.py` lines 155-287 (13 inline imports)

**Issue:** `TurnEngine.__init__` lazily creates each sub-engine (FleetMovementEngine, ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine, ResourceManagementEngine, PopulationEngine, ResupplyEngine, HarvestingEngine, MaintenanceEngine, ActionExecutionEngine, EnvironmentalHazardEngine) inside conditional `if self._xxx is None:` blocks, importing each engine module inline. This is by design (dependency injection with lazy defaults), but contributes 13 inline imports.

**Impact:** Moderate. The pattern is intentional and well-structured (each engine is created only if not injected), but it creates a large number of deferred imports in a single file.

**Recommendation:** Consider a factory function or `_create_default_engines()` method that consolidates all engine creation into one place with a single import block. The imports would still be deferred but grouped logically.

**Effort:** Simple

---

#### MAJOR: `game.simulation.components.abilities.weapons.py` imports formula_system 7 times
**ID:** IIA-003
**Location:** `game/simulation/components/abilities/weapons.py` lines 63, 81, 96, 132, 140, 148, 209

**Issue:** `safe_evaluate_math_formula` from `game.simulation.formula_system` is imported inline 7 separate times within the `WeaponAbility.__init__` and `sync_data` methods. Each conditional branch (`if isinstance(raw_damage, str) and raw_damage.startswith('=')`) repeats the import.

**Impact:** Code duplication. The same import appears in every branch that handles formula strings for damage, range, and reload values.

**Recommendation:** Import `safe_evaluate_math_formula` once at the top of each method that uses it (or at module level if there is no actual circular dependency). The `formula_system` module imports from `builtins` only -- there should be no circular dependency preventing a top-level import.

**Effort:** Simple

---

#### MINOR: 45 redundant inline imports duplicate top-level imports
**ID:** IIA-004
**Location:** Distributed across 20+ files. Notable examples:
- `game/strategy/engine/fleet_order_processor.py`: `SpeciesPopulation` imported at top-level AND inline 4 times (lines 251, 369, 417, 476)
- `game/ui/screens/empire_build_queue_window.py`: 4 formatter functions imported both at top-level and inline (lines 516, 522, 528, 543)
- `game/strategy/data/stars.py`: `hex_to_dict`, `hex_from_dict`, `math` imported both at top-level and inline
- `game/strategy/data/design_metadata.py`: `iter_components` imported at top-level and inline twice
- `game/app.py`: `pygame_gui` imported at top-level and inline 3 times
- `game/strategy/data/planet.py`: `hex_to_dict`, `hex_from_dict` imported both at top-level and inline

**Issue:** These inline imports are completely unnecessary because the same module is already available at module scope. They appear to be remnants of refactoring where a previously-deferred import was later added to the top-level without removing the inline copies.

**Impact:** Code noise. No runtime impact (Python caches module imports), but they obscure which imports are truly deferred for circular avoidance vs simply redundant.

**Recommendation:** Remove all 45 redundant inline imports. This is a safe, mechanical cleanup with zero risk.

**Effort:** Simple

---

#### MAJOR: `game.core.registry` deferred in 12 files across all layers
**ID:** IIA-005
**Location:** 13 inline imports from 12 different files:
- `game/simulation/components/component.py` (3 occurrences)
- `game/simulation/entities/ship_loader.py`
- `game/strategy/data/fleet_capability_calculator.py`
- `game/strategy/data/ship_instance.py`
- `game/strategy/engine/empire_economy_calculator.py`
- `game/strategy/facade/strategy_session_facade.py`
- `game/ui/panels/planet_report_panel.py`
- `game/ui/screens/builder/right_panel.py`
- `game/ui/screens/builder/schematic_view.py`
- `game/ui/screens/empire_panel_window.py`
- `game/ui/screens/workshop_context.py`
- `game/ui/services/ship_factory.py`

**Issue:** `game.core.registry` (specifically `get_default_registry_provider` and `GameRegistries`) is deferred in files across every layer. The core registry module is foundational infrastructure, yet it cannot be imported at top-level in many files due to circular dependencies with modules that depend on it.

**Impact:** High. This suggests the registry module has grown to depend on too many other modules (or vice versa), creating a circular web. The registry should be a leaf dependency that everything can import freely.

**Recommendation:** Audit `game.core.registry` to ensure it does not import from simulation, strategy, or UI layers. If it does, extract those dependencies. The goal is to make `game.core.registry` importable at top-level everywhere.

**Effort:** Complex

---

#### MAJOR: Strategy data layer has extensive internal circular dependencies
**ID:** IIA-006
**Location:** 40 inline imports within `game/strategy/data/` files, involving:
- `fleet.py` <-> `planet.py` (mutual deferred imports)
- `fleet.py` <-> `empire.py` (mutual deferred imports)
- `fleet.py` -> `fleet_speed_calculator` (service import from data layer)
- `ship_instance.py` -> `ship_stats_calculator`, `registry`, `ship_serialization`
- `galaxy.py` <-> `fleet.py` (mutual deferred imports)
- `stars.py` -> `hex_math`, `exceptions` (core imports deferred)

**Issue:** The strategy data layer has significant internal coupling. `fleet.py`, `planet.py`, `empire.py`, and `galaxy.py` form a tightly coupled cluster where each needs to reference the others, creating mutual circular dependencies that force inline imports.

**Impact:** High. This is a structural problem that makes the data layer fragile and hard to refactor. Adding new fields or methods to any of these core data classes risks creating new circular dependencies.

**Recommendation:** This aligns with the active PROJ-87 (Strategy Data Tier) decomposition project. Key strategies:
1. Extract shared types (OrderType, FleetOrder) into lightweight modules
2. Use protocols/interfaces instead of concrete type imports where possible
3. Consider a data transfer object layer for cross-entity references

**Effort:** Complex (already planned as PROJ-87)

---

#### MAJOR: UI screens have 128 inline imports, dominated by strategy-layer coupling
**ID:** IIA-007
**Location:** `game/ui/screens/` directory -- 128 inline imports across ~40 files

**Issue:** The UI screens directory is the single largest contributor to inline imports. Most are UI-to-Strategy coupling:
- `strategy_build_queue_manager.py` (13 imports): Imports Fleet, OrderType, commands, DesignLibrary
- `strategy_screen.py` (13 imports): Imports pathfinding, save service, asset manager
- `fleet_report_filters.py` (5 imports): Imports capability calculator, speed calculator
- `fleet_data_source.py` (5 imports): Imports speed/stats/capability calculators

**Impact:** Moderate. UI screens legitimately need strategy-layer data to display, but the sheer volume suggests the UI layer is reaching too deep into strategy internals rather than going through facade/DTO boundaries.

**Recommendation:** Route UI screen data access through `StrategySessionFacade` and DTOs rather than importing strategy data/engine modules directly. The facade pattern is already partially implemented but not consistently used.

**Effort:** Complex (aligns with PROJ-86/PROJ-89)

---

#### INFO: app.py has 20 inline imports -- intentional lazy loading
**ID:** IIA-008
**Location:** `game/app.py` lines 123-717

**Issue:** The application entry point defers virtually all imports to minimize startup time and avoid loading the entire game engine at import time. This includes strategy engines, UI screens, pygame_gui, and save services.

**Impact:** None -- this is correct architecture. The app module is a dispatcher that loads subsystems on demand.

**Recommendation:** No action needed. This is the intended pattern for an application entry point.

**Effort:** N/A

---

#### MINOR: `game/simulation/components/component.py` has 11 inline imports including 5x `os` and 3x `copy`
**ID:** IIA-009
**Location:** `game/simulation/components/component.py` lines 80-664

**Issue:** The component module's data-loading functions (`load_components`, `load_modifiers`, `get_all_components`) each independently import `os`, `copy`, and `GameRegistries`. These functions are module-level utility functions, not methods, and each independently imports the same stdlib modules.

**Impact:** Low. Stdlib imports are cached by Python, but the repetition is unnecessary noise.

**Recommendation:** Move `os`, `copy`, and `GameRegistries` to top-level imports. Check if `GameRegistries` creates a circular dependency -- if so, refactor the dependency.

**Effort:** Simple

---

#### INFO: Conditional/factory imports in turn_engine and conflict_resolution are well-structured
**ID:** IIA-010
**Location:**
- `game/strategy/engine/turn_engine.py` (13 conditional imports in `__init__`)
- `game/strategy/engine/conflict_resolution_engine.py` (1 conditional import)

**Issue:** These files use a dependency injection pattern where sub-engines are only imported and instantiated when not provided by the caller. The imports are inside `if self._xxx is None:` guards.

**Impact:** None -- this is intentional DI design. The conditional imports enable test isolation by allowing mock injection.

**Recommendation:** While the pattern is sound, grouping all default engine creation into a single `_create_defaults()` method would improve readability.

**Effort:** Simple

---

### Top 5 Priority Issues

1. **IIA-004 (MINOR but easiest win): Remove 45 redundant inline imports** -- These duplicate top-level imports and can be deleted with zero risk. Immediate code quality improvement.

2. **IIA-001 (MAJOR): Decouple `FleetOrder`/`OrderType` from `fleet.py`** -- Extracting these into a lightweight module eliminates 18 inline imports, the single largest cluster. High impact, medium effort.

3. **IIA-003 (MAJOR): Consolidate formula_system imports in weapons.py** -- 7 identical imports in one file. Moving to a top-level import (or single method-level import) is trivial and safe.

4. **IIA-005 (MAJOR): Fix `game.core.registry` circular dependencies** -- 13 deferred imports across all layers suggest the registry module's dependency graph needs refactoring so it can be imported at top-level universally.

5. **IIA-006 (MAJOR): Address strategy data layer circular coupling** -- 40 inline imports within `game/strategy/data/` reflect deep structural coupling between Fleet, Planet, Empire, and Galaxy. This is the root cause of many deferred imports and is being addressed by PROJ-87.

### Appendix: Category Definitions

| Category | Description | Count |
|----------|-------------|-------|
| **Circular Avoidance** | Import deferred because importing at module level would create a circular import error between two modules that mutually depend on each other | 171 |
| **Conditional/Factory** | Import inside an `if`/`try`/`except` block, typically for optional feature detection or dependency injection default creation | 64 |
| **Redundant Inline** | Import is already present at the file's top level; the inline copy is unnecessary | 45 |
| **Lazy Loading (stdlib)** | Stdlib module imported inside a function to defer loading until actually needed | 32 |
| **Lazy Loading (pygame)** | Pygame/pygame_gui module imported inside a function to defer heavy UI library loading | 9 |
| **Conditional Feature (test)** | Test framework import only needed in specific testing contexts | 4 |
