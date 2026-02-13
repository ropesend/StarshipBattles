# PROJ-114: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-11_sweep_full-codebase-sweep](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/)
- **Type:** Sweep Review (automated parallel analysis)
- **Date:** 2026-02-11
- **Report:** [View Full Report](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 396 total findings identified.
- **Critical:** 5
- **Major:** 27
- **Selected for remediation:** 79

## Selected Findings Summary

### CON-FND-009: Inconsistent Error Handling Strategy Bet
- **Severity:** Critical
- **Location:** `game/core/resources.py:55-98`
- **Effort:** Simple

### CON-STR-011: Facade `_find_fleet_by_id` Does O(n) Sca
- **Severity:** Critical
- **Location:** `game/strategy/facade/strategy_`
- **Effort:** Small

### CON-UI2-001: Inconsistent DI Pattern Across Services
- **Severity:** Critical
- **Location:** `game/ui/services/vehicle_class`
- **Effort:** Medium

### CON-UI1-001: Duplicate Class Name `ModifierEditorPane
- **Severity:** Critical
- **Location:** `game/ui/panels/builder_widgets`
- **Effort:** Medium

### CON-UI1-002: Duplicate Class Name `ColumnManager` in
- **Severity:** Critical
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Medium

### CON-FND-001: Mixed Singleton Patterns Across Core Lay
- **Severity:** Major
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Simple

### CON-FND-002: Inconsistent Logging Approach Between ga
- **Severity:** Major
- **Location:** `game/ai/combat_utils.py:19`
- **Effort:** Medium

### CON-FND-010: __init__.py Export Inconsistency Across
- **Severity:** Major
- **Location:** `game/core/__init__.py`
- **Effort:** Simple

### CON-FND-011: Unused json Import in registry.py
- **Severity:** Major
- **Location:** `game/core/registry.py:45`
- **Effort:** Simple

### CON-FND-014: Mixed Return Conventions for "Not Found"
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Medium

### CON-FND-015: StrategyManager Methods Lack Type Hints
- **Severity:** Major
- **Location:** `game/ai/strategy_manager.py:83`
- **Effort:** Simple

### CON-FND-017: StrategyMetadataService Uses Manual Sing
- **Severity:** Major
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Simple

### CON-STR-001: Duplicate `to_roman` Implementation
- **Severity:** Major
- **Location:** `game/strategy/data/naming.py:5`
- **Effort:** Small

### CON-STR-002: Inconsistent Entity Lookup Verb Prefixes
- **Severity:** Major
- **Location:** `game/strategy/facade/strategy_`
- **Effort:** Small

### CON-STR-006: Duplicated `_calculate_maintenance_cost`
- **Severity:** Major
- **Location:** `game/strategy/engine/maintenan`
- **Effort:** Small

### CON-STR-007: Duplicated `_get_harvester_info` / `_loo
- **Severity:** Major
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Small

### CON-STR-008: Duplicated `_find_system_at_location` O(
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Small

### CON-STR-012: Inconsistent `__eq__` Return Value Conve
- **Severity:** Major
- **Location:** `game/strategy/data/fleet.py:41`
- **Effort:** Small

### CON-STR-013: Missing Type Hints on Public Methods
- **Severity:** Major
- **Location:** `game/strategy/data/fleet.py`
- **Effort:** Medium

### CON-STR-016: `SectorEnvironment` Class Missing Type H
- **Severity:** Major
- **Location:** `game/strategy/data/physics.py:`
- **Effort:** Small

### CON-UI2-002: Complete Absence of Type Hints in render
- **Severity:** Major
- **Location:** `game/ui/renderer/camera.py:all`
- **Effort:** Medium

### CON-UI2-003: Complete Absence of Type Hints in widget
- **Severity:** Major
- **Location:** `game/ui/widgets.py:1-102`
- **Effort:** Simple

### CON-UI2-004: Singleton Pattern Used in renderer/ and
- **Severity:** Major
- **Location:** `game/ui/renderer/sprites.py:7`
- **Effort:** Complex

### CON-UI2-005: Missing Docstrings on Public Methods in
- **Severity:** Major
- **Location:** `game/ui/renderer/sprites.py:27`
- **Effort:** Medium

### CON-UI2-006: Inconsistent Error Handling - traceback
- **Severity:** Major
- **Location:** `game/ui/renderer/sprites.py:11`
- **Effort:** Simple

### CON-UI1-003: Mixed Event Handling Method Names (`hand
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Complex

### CON-UI1-004: Mixed `draw()` Parameter Naming (`screen
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-005: Mixed `update()` Parameter Naming (`dt`
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-006: Two Logging Systems Used in Parallel
- **Severity:** Major
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Simple

### CON-UI1-007: UIWindow Base Class Import Inconsistency
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### CON-UI1-008: Confusing Sibling File Names `strategy_d
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_detai`
- **Effort:** Simple

### CON-UI1-009: Mixed Class Suffix Convention for Strate
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_colon`
- **Effort:** Simple

### CON-FND-003: Inconsistent os.path vs pathlib Usage in
- **Severity:** Minor
- **Location:** `game/core/paths.py:50-103`
- **Effort:** Medium

### CON-FND-004: Missing Type Hints on HexCoord Methods
- **Severity:** Minor
- **Location:** `game/core/hex_math.py:75-119`
- **Effort:** Simple

### CON-FND-005: Missing Type Hints on game/engine/ Class
- **Severity:** Minor
- **Location:** `game/engine/spatial.py:6-35`
- **Effort:** Simple

### CON-FND-006: Duplicate Enum Import in constants.py
- **Severity:** Minor
- **Location:** `game/core/constants.py:1`
- **Effort:** Simple

### CON-FND-007: Inconsistent Docstring Presence on game/
- **Severity:** Minor
- **Location:** `game/engine/spatial.py`
- **Effort:** Simple

### CON-FND-008: ResourceType Uses Class Constants Instea
- **Severity:** Minor
- **Location:** `game/core/constants.py:95-104`
- **Effort:** Simple

### CON-FND-012: Missing Module Docstring in logger.py
- **Severity:** Minor
- **Location:** `game/core/logger.py:1`
- **Effort:** Simple

### CON-FND-013: Inconsistent Method Naming in Logger Cla
- **Severity:** Minor
- **Location:** `game/core/logger.py:43-57`
- **Effort:** Simple

### CON-FND-016: Inconsistent Naming Between is_alive Pro
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### CON-FND-022: Inconsistent Use of import Inside Functi
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:443,452`
- **Effort:** Simple

### CON-STR-003: Inconsistent Logging Module Usage
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-STR-004: Inconsistent Type Annotation Styles
- **Severity:** Minor
- **Location:** `game/strategy/engine/empire_ec`
- **Effort:** Small

### CON-STR-009: Inconsistent DI Patterns Across Engines
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Medium

### CON-STR-010: Inconsistent Delegate/Facade Naming
- **Severity:** Minor
- **Location:** `game/strategy/data/`
- **Effort:** Medium

### CON-STR-014: Inconsistent Validation Return Types
- **Severity:** Minor
- **Location:** `game/strategy/validation/`
- **Effort:** Medium

### CON-STR-015: Module-Level Functions vs Static Methods
- **Severity:** Minor
- **Location:** `game/strategy/services/compone`
- **Effort:** None

### CON-STR-017: Global Module-Level Cache Pattern (Poten
- **Severity:** Minor
- **Location:** `game/strategy/data/homeworld_p`
- **Effort:** Small

### CON-STR-018: Duplicate `import math` in `stars.py`
- **Severity:** Minor
- **Location:** `game/strategy/data/stars.py`
- **Effort:** Trivial

### CON-STR-020: `pathfinding.py` Contains Dead/Questiona
- **Severity:** Minor
- **Location:** `game/strategy/data/pathfinding`
- **Effort:** Small

### CON-STR-021: `build_queue_source.py` Contains Heavily
- **Severity:** Minor
- **Location:** `game/strategy/data/build_queue`
- **Effort:** Small

### CON-STR-022: `DesignLibrary` Uses Late Imports Inside
- **Severity:** Minor
- **Location:** `game/strategy/systems/design_l`
- **Effort:** Small

### CON-UI2-007: Hardcoded Magic Colors in renderer/game_
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### CON-UI2-008: Hardcoded Font Creation in game_renderer
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### CON-UI2-009: game/ui/__init__.py Imports Screens but
- **Severity:** Minor
- **Location:** `game/ui/__init__.py:14-16`
- **Effort:** Simple

### CON-UI2-010: Mixed Naming for Internal Provider Acces
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** Simple

### CON-UI2-011: Inconsistent Return Patterns for load_sh
- **Severity:** Minor
- **Location:** `game/ui/services/ship_io_adapt`
- **Effort:** Medium

### CON-UI2-012: Camera.fit_objects Sets zoom Directly, B
- **Severity:** Minor
- **Location:** `game/ui/renderer/camera.py:153`
- **Effort:** Simple

### CON-UI2-013: draw_ship Contains Inline Import of Ship
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### CON-UI1-010: Panel Classes Scattered Between `screens
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Complex

### CON-UI1-011: Missing Module-Level Docstrings in 18 Fi
- **Severity:** Minor
- **Location:** `battle_ui.py`
- **Effort:** Simple

### CON-UI1-012: `__init__.py` Export Patterns Inconsiste
- **Severity:** Minor
- **Location:** `screens/__init__.py`
- **Effort:** Simple

### CON-UI1-013: Scene vs Screen Class Naming Convention
- **Severity:** Minor
- **Location:** `MenuScene`
- **Effort:** Simple

### CON-UI1-014: Function-Level Logger Imports in `design
- **Severity:** Minor
- **Location:** `game/ui/screens/design_selecto`
- **Effort:** Simple

### CON-UI1-015: `builder/main.py` Has Scattered Imports
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Simple

### CON-UI1-016: Broad Exception Catch Without Justificat
- **Severity:** Minor
- **Location:** `game/ui/panels/race_environmen`
- **Effort:** Simple

### ADR-STR-010: Misleading Docstring in ShipStatsCalcula
- **Severity:** Info
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Simple

### CON-FND-018: Screenshot Manager Accesses Private Rend
- **Severity:** Info
- **Location:** `game/core/screenshot_manager.p`
- **Effort:** Medium

### CON-FND-019: game/engine/ Is Internally Consistent Bu
- **Severity:** Info
- **Location:** `game/engine/spatial.py`
- **Effort:** Simple

### CON-FND-020: game/research/ Has Clean Internal Consis
- **Severity:** Info
- **Location:** `game/research/`
- **Effort:** N

### CON-FND-021: game/ai/ Has Mostly Good Internal Consis
- **Severity:** Info
- **Location:** `game/ai/`
- **Effort:** Simple

### CON-STR-005: NameRegistry Class Style Inconsistencies
- **Severity:** Info
- **Location:** `game/strategy/data/naming.py`
- **Effort:** Small

### CON-STR-019: Superweapon Mission Command Handlers Hav
- **Severity:** Info
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Small

### CON-UI2-014: Service Class Naming Convention - "Servi
- **Severity:** Info
- **Location:** `game/ui/services/`
- **Effort:** N

### CON-UI2-015: colors.py Has No Module Docstring and No
- **Severity:** Info
- **Location:** `game/ui/colors.py:1-35`
- **Effort:** Simple

### CON-UI2-016: Inconsistent Docstring Style Between ren
- **Severity:** Info
- **Location:** `game/ui/renderer/camera.py:24-`
- **Effort:** Simple

### CON-UI1-017: Return Type Annotations Present on Only
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### CON-UI1-018: `from __future__ import annotations` Use
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Simple


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
