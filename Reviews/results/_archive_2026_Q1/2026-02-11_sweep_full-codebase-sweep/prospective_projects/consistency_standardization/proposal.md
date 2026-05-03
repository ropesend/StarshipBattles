# Prospective Project: Consistency Standardization

## Overview
This project addresses all consistency violations found across the codebase: inconsistent naming conventions, missing type hints, mixed error handling strategies, inconsistent DI patterns, mixed logging approaches, non-standard singleton patterns, duplicate class names, missing docstrings, and API naming inconsistencies. These findings span every layer of the application and, while individually minor, collectively create confusion and cognitive overhead for developers working across modules.

## Grouping Rationale
All 79 findings are CON (Consistency Violations) type, plus a few related architecture Info findings about naming and documentation. They share the same fix strategy (standardize to a single convention and update all call sites) and many affect naming patterns that span the entire codebase (e.g., mixed `handle_event` vs `on_event` naming spans all UI screens). Addressing consistency findings as a unified project ensures that the chosen conventions are applied uniformly rather than creating new inconsistencies by fixing them piecemeal.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 79 total (5 Critical, 27 Major, 35 Minor, 12 Info)

## Suggested Execution Order
**Execute fifth** (Order 5), after architecture and legacy cleanup. Consistency fixes are safer and more effective after dead code has been removed (less code to standardize) and layer violations are fixed (clear boundaries make it easier to choose the right convention for each layer). Many consistency findings are simple mechanical changes that can be done quickly once conventions are decided.

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-FND-009 | Inconsistent Error Handling Strategy Between load_resources and load_resources_data | `game/core/resources.py:55-98` | Simple |
| CON-STR-011 | Facade `_find_fleet_by_id` Does O(n) Scan (Performance inconsistency) | `game/strategy/facade/strategy_` | Small |
| CON-UI2-001 | Inconsistent DI Pattern Across Services | `game/ui/services/vehicle_class` | Medium |
| CON-UI1-001 | Duplicate Class Name `ModifierEditorPanel` in different modules | `game/ui/panels/builder_widgets` | Medium |
| CON-UI1-002 | Duplicate Class Name `ColumnManager` in different modules | `game/ui/screens/column_manager` | Medium |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-FND-001 | Mixed Singleton Patterns Across Core Layer | `game/core/strategy_metadata.py` | Simple |
| CON-FND-002 | Inconsistent Logging Approach Between game/ai modules | `game/ai/combat_utils.py:19` | Medium |
| CON-FND-010 | __init__.py Export Inconsistency Across core packages | `game/core/__init__.py` | Simple |
| CON-FND-011 | Unused json Import in registry.py | `game/core/registry.py:45` | Simple |
| CON-FND-014 | Mixed Return Conventions for "Not Found" (None vs raise vs empty) | `Unknown` | Medium |
| CON-FND-015 | StrategyManager Methods Lack Type Hints | `game/ai/strategy_manager.py:83` | Simple |
| CON-FND-017 | StrategyMetadataService Uses Manual Singleton Instead of DI | `game/core/strategy_metadata.py` | Simple |
| CON-STR-001 | Duplicate `to_roman` Implementation | `game/strategy/data/naming.py:5` | Small |
| CON-STR-002 | Inconsistent Entity Lookup Verb Prefixes (get_ vs find_ vs lookup_) | `game/strategy/facade/strategy_` | Small |
| CON-STR-006 | Duplicated `_calculate_maintenance_cost` naming | `game/strategy/engine/maintenan` | Small |
| CON-STR-007 | Duplicated `_get_harvester_info` / `_lookup_harvester_` naming | `game/strategy/engine/harvestin` | Small |
| CON-STR-008 | Duplicated `_find_system_at_location` O(n) naming | `game/strategy/engine/superweap` | Small |
| CON-STR-012 | Inconsistent `__eq__` Return Value Convention | `game/strategy/data/fleet.py:41` | Small |
| CON-STR-013 | Missing Type Hints on Public Methods in fleet.py | `game/strategy/data/fleet.py` | Medium |
| CON-STR-016 | `SectorEnvironment` Class Missing Type Hints | `game/strategy/data/physics.py:` | Small |
| CON-UI2-002 | Complete Absence of Type Hints in renderer/camera.py | `game/ui/renderer/camera.py:all` | Medium |
| CON-UI2-003 | Complete Absence of Type Hints in widgets.py | `game/ui/widgets.py:1-102` | Simple |
| CON-UI2-004 | Singleton Pattern Used in renderer/ and services/ (inconsistent with DI) | `game/ui/renderer/sprites.py:7` | Complex |
| CON-UI2-005 | Missing Docstrings on Public Methods in sprites.py | `game/ui/renderer/sprites.py:27` | Medium |
| CON-UI2-006 | Inconsistent Error Handling - traceback in sprites.py | `game/ui/renderer/sprites.py:11` | Simple |
| CON-UI1-003 | Mixed Event Handling Method Names (`handle_event` vs `on_event`) | `Unknown` | Complex |
| CON-UI1-004 | Mixed `draw()` Parameter Naming (`screen` vs `surface`) | `Unknown` | Simple |
| CON-UI1-005 | Mixed `update()` Parameter Naming (`dt` vs `delta_time`) | `Unknown` | Simple |
| CON-UI1-006 | Two Logging Systems Used in Parallel in builder | `game/ui/screens/builder/main.p` | Simple |
| CON-UI1-007 | UIWindow Base Class Import Inconsistency | `Unknown` | Simple |
| CON-UI1-008 | Confusing Sibling File Names (strategy_detail* files) | `game/ui/screens/strategy_detai` | Simple |
| CON-UI1-009 | Mixed Class Suffix Convention for Strategy screens | `game/ui/screens/strategy_colon` | Simple |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-FND-003 | Inconsistent os.path vs pathlib Usage in paths.py | `game/core/paths.py:50-103` | Medium |
| CON-FND-004 | Missing Type Hints on HexCoord Methods | `game/core/hex_math.py:75-119` | Simple |
| CON-FND-005 | Missing Type Hints on game/engine/ Classes | `game/engine/spatial.py:6-35` | Simple |
| CON-FND-006 | Duplicate Enum Import in constants.py | `game/core/constants.py:1` | Simple |
| CON-FND-007 | Inconsistent Docstring Presence on game/engine/ classes | `game/engine/spatial.py` | Simple |
| CON-FND-008 | ResourceType Uses Class Constants Instead of Enum | `game/core/constants.py:95-104` | Simple |
| CON-FND-012 | Missing Module Docstring in logger.py | `game/core/logger.py:1` | Simple |
| CON-FND-013 | Inconsistent Method Naming in Logger Class | `game/core/logger.py:43-57` | Simple |
| CON-FND-016 | Inconsistent Naming Between is_alive Property and Methods | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-022 | Inconsistent Use of import Inside Functions | `game/ai/behaviors.py:443,452` | Simple |
| CON-STR-003 | Inconsistent Logging Module Usage across strategy | `Unknown` | Medium |
| CON-STR-004 | Inconsistent Type Annotation Styles | `game/strategy/engine/empire_ec` | Small |
| CON-STR-009 | Inconsistent DI Patterns Across Engines | `Unknown` | Medium |
| CON-STR-010 | Inconsistent Delegate/Facade Naming | `game/strategy/data/` | Medium |
| CON-STR-014 | Inconsistent Validation Return Types | `game/strategy/validation/` | Medium |
| CON-STR-015 | Module-Level Functions vs Static Methods inconsistency | `game/strategy/services/compone` | None |
| CON-STR-017 | Global Module-Level Cache Pattern (Potential singleton) | `game/strategy/data/homeworld_p` | Small |
| CON-STR-018 | Duplicate `import math` in `stars.py` | `game/strategy/data/stars.py` | Trivial |
| CON-STR-020 | `pathfinding.py` Contains Dead/Questionable code | `game/strategy/data/pathfinding` | Small |
| CON-STR-021 | `build_queue_source.py` Contains Heavily commented code | `game/strategy/data/build_queue` | Small |
| CON-STR-022 | `DesignLibrary` Uses Late Imports Inside methods | `game/strategy/systems/design_l` | Small |
| CON-UI2-007 | Hardcoded Magic Colors in renderer/game_renderer.py | `game/ui/renderer/game_renderer` | Medium |
| CON-UI2-008 | Hardcoded Font Creation in game_renderer.py | `game/ui/renderer/game_renderer` | Medium |
| CON-UI2-009 | game/ui/__init__.py Imports Screens but Not Required | `game/ui/__init__.py:14-16` | Simple |
| CON-UI2-010 | Mixed Naming for Internal Provider Access in services | `game/ui/services/component_ser` | Simple |
| CON-UI2-011 | Inconsistent Return Patterns for load_ship across services | `game/ui/services/ship_io_adapt` | Medium |
| CON-UI2-012 | Camera.fit_objects Sets zoom Directly, Bypassing method | `game/ui/renderer/camera.py:153` | Simple |
| CON-UI2-013 | draw_ship Contains Inline Import of ShipThemeManager | `game/ui/renderer/game_renderer` | Simple |
| CON-UI1-010 | Panel Classes Scattered Between `screens/` and `panels/` | `Unknown` | Complex |
| CON-UI1-011 | Missing Module-Level Docstrings in 18 Files | `battle_ui.py` | Simple |
| CON-UI1-012 | `__init__.py` Export Patterns Inconsistent in screens/ | `screens/__init__.py` | Simple |
| CON-UI1-013 | Scene vs Screen Class Naming Convention Mismatch | `MenuScene` | Simple |
| CON-UI1-014 | Function-Level Logger Imports in design_selector | `game/ui/screens/design_selecto` | Simple |
| CON-UI1-015 | `builder/main.py` Has Scattered Imports at Multiple Levels | `game/ui/screens/builder/main.p` | Simple |
| CON-UI1-016 | Broad Exception Catch Without Justification in panels | `game/ui/panels/race_environmen` | Simple |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-FND-018 | Screenshot Manager Accesses Private Renderer internals | `game/core/screenshot_manager.p` | Medium |
| CON-FND-019 | game/engine/ Is Internally Consistent But Undocumented | `game/engine/spatial.py` | Simple |
| CON-FND-020 | game/research/ Has Clean Internal Consistency | `game/research/` | N |
| CON-FND-021 | game/ai/ Has Mostly Good Internal Consistency | `game/ai/` | Simple |
| CON-STR-005 | NameRegistry Class Style Inconsistencies | `game/strategy/data/naming.py` | Small |
| CON-STR-019 | Superweapon Mission Command Handlers Have consistent but verbose pattern | `game/strategy/engine/superweap` | Small |
| CON-STR-023 | `event_log.py` Uses Python 3.10+ union syntax | `game/strategy/events/event_log` | Trivial |
| CON-UI2-014 | Service Class Naming Convention is consistent ("Service" suffix) | `game/ui/services/` | N |
| CON-UI2-015 | colors.py Has No Module Docstring and No Type Hints | `game/ui/colors.py:1-35` | Simple |
| CON-UI2-016 | Inconsistent Docstring Style Between renderer modules | `game/ui/renderer/camera.py:24-` | Simple |
| CON-UI1-017 | Return Type Annotations Present on Only ~30% of methods | `Unknown` | Complex |
| CON-UI1-018 | `from __future__ import annotations` Used inconsistently | `Unknown` | Simple |

## Affected Files

**Core / Engine:**
- `game/core/__init__.py`
- `game/core/constants.py`
- `game/core/hex_math.py`
- `game/core/logger.py`
- `game/core/paths.py`
- `game/core/registry.py`
- `game/core/resources.py`
- `game/core/screenshot_manager.py`
- `game/core/strategy_metadata.py`
- `game/engine/spatial.py`

**AI:**
- `game/ai/behaviors.py`
- `game/ai/combat_utils.py`
- `game/ai/interfaces/controllable.py`
- `game/ai/strategy_manager.py`

**Research:**
- `game/research/` (positive observation)

**Strategy:**
- `game/strategy/data/build_queue_source.py`
- `game/strategy/data/fleet.py`
- `game/strategy/data/homeworld_presets.py`
- `game/strategy/data/naming.py`
- `game/strategy/data/pathfinding.py`
- `game/strategy/data/physics.py`
- `game/strategy/data/stars.py`
- `game/strategy/engine/empire_economy_calculator.py`
- `game/strategy/engine/harvesting_engine.py`
- `game/strategy/engine/maintenance_engine.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `game/strategy/events/event_log.py`
- `game/strategy/facade/strategy_facade.py`
- `game/strategy/services/component_service.py`
- `game/strategy/systems/design_library.py`
- `game/strategy/validation/`

**UI:**
- `game/ui/__init__.py`
- `game/ui/colors.py`
- `game/ui/panels/builder_widgets/`
- `game/ui/panels/race_environment_panel.py`
- `game/ui/renderer/camera.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`
- `game/ui/screens/builder/main.py`
- `game/ui/screens/column_manager.py`
- `game/ui/screens/design_selector/`
- `game/ui/screens/strategy_colony_screen.py`
- `game/ui/screens/strategy_detail_formatter.py`
- `game/ui/services/component_service.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/widgets.py`

## Effort Estimate
- **Simple tasks:** 55
- **Medium tasks:** 17
- **Complex tasks:** 4
- **Unknown/N/A:** 3
- **Overall scope:** Large (but predominantly simple standardization)

## Overlap with Existing Projects
- **PROJ-107** (Consistency and API Standardization) - Direct overlap. This project was likely created from an earlier analysis. Should be merged or superseded.
- **PROJ-95** (Resource API Consistency and Clean-Sheet Conventions) - Overlaps on resource API naming and DI pattern consistency.
- **PROJ-93** (Update Protocol Layer Type Annotations) - Overlaps on type hint additions in protocols and interfaces.

## Suggested Phases
1. **Phase 1: Convention Decisions** - Document the chosen convention for each inconsistency category: error handling, "not found" returns, event handler naming, draw/update parameter names, DI pattern, logging approach, singleton pattern. Record in decisions.md.
2. **Phase 2: Type Hints and Docstrings** - Add missing type hints to foundation, strategy, and UI modules. Add missing module/method docstrings.
3. **Phase 3: Naming Standardization** - Resolve duplicate class names, standardize event handler method names, standardize draw/update parameter names, fix entity lookup verb prefixes, resolve Scene vs Screen naming.
4. **Phase 4: Pattern Standardization** - Standardize DI pattern across UI services, standardize singleton usage, standardize error handling, standardize logging approach, fix return value conventions.
5. **Phase 5: Cleanup** - Fix unused imports, duplicate imports, file organization (panels vs screens), __init__.py exports, broad exception catches.
