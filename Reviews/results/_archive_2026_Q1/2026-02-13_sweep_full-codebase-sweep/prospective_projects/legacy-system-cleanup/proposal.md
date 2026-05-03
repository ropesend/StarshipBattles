# Project Proposal: Legacy System Cleanup

## Overview

**Project ID:** PROJ-D_legacy-system-cleanup
**Theme:** Legacy System Holdovers (LEG)
**Total Findings:** 20
**Severity Breakdown:** Critical: 0 | Major: 3 | Minor: 11 | Info: 6

## Problem Statement

The codebase contains various legacy code patterns that should be removed according to the project's "System Migration Policy" which states:

> **When a new system replaces an old one, ERADICATE the old system completely.**
> - DO NOT add "fallback" code paths to old systems
> - DO NOT keep backward compatibility layers "just in case"
> - **Save files are disposable.** Old saves are not migrated.

The identified legacy holdovers include:

1. **Backward compatibility branches** - Code paths that handle "old" data formats
2. **Legacy behavior comments** - Explicit comments marking code as "legacy"
3. **Singleton patterns** - Despite DI being the preferred approach
4. **Unused error codes and test utilities** - Dead code
5. **Save file compatibility shims** - Violates disposal policy

## Scope

### In Scope
- All LEG (Legacy System Holdovers) findings from all shards
- Removal of backward compatibility branches
- Cleanup of legacy comments and code
- Audit of singleton patterns for DI conversion

### Out of Scope
- Test coverage (separate project)
- Architecture violations (separate project)
- Code consistency (separate project)

## Findings Summary

### Major (3)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-STR-001 | Legacy Behavior Branch in FleetOrderProcessor | `game/strategy/engine/fleet_order_processor.py` | Medium |
| LEG-STR-002 | Backward Compatibility Comment in GameSession | `game/strategy/engine/game_session.py` | Medium |
| LEG-STR-003 | Legacy Items in ProductionEngine | `game/strategy/engine/production_engine.py` | Medium |

### Minor (11)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-003 | Raw Ship vs Adapter Access Pattern | `game/ai/behaviors.py` | Medium |
| LEG-FND-004 | Singleton Pattern Still in Use Despite DI | Multiple files | Complex |
| LEG-FND-005 | Unused AI_STATE_ERROR ErrorCode | `game/core/error_codes.py` | Simple |
| LEG-SIM-006 | Module Identity Drift Fallback in Abilities | `game/simulation/components/abilities/` | Medium |
| LEG-SIM-007 | Component Ability Index Fallback Pattern | `game/simulation/components/component.py` | Simple |
| LEG-STR-004 | Backward Compatibility Comment in FleetNavigation | `game/strategy/services/fleet_navigation_service.py` | Simple |
| LEG-STR-005 | Backward Compat Default in Planet.from_dict | `game/strategy/data/planet.py` | Simple |
| LEG-STR-006 | Backward Compat Defaults in RaceConfig.from_dict | `game/strategy/data/race_config.py` | N/A |
| LEG-STR-007 | Old Layer Format Detection in DesignMetadata | `game/strategy/data/design_metadata.py` | Simple |
| LEG-STR-008 | Save Compatibility Field in DesignMetadata | `game/strategy/data/design_metadata.py` | Simple |
| LEG-UI2-003 | Excessive getattr() with Defaults | `game/ui/services/battle_ui_service.py` | Medium |
| LEG-UI2-004 | ModifierEditorPanel Marked as Legacy | `game/ui/screens/builder/modifier_editor.py` | Medium |

### Info (6)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-SIM-009 | TechPresetLoader Only Used in Tests | `game/simulation/systems/tech_preset_loader.py` | Unknown |
| LEG-STR-009 | Test Mock Compatibility in FleetOrderProcessor | `game/strategy/engine/fleet_order_processor.py` | Simple |
| LEG-STR-010 | Intercept Function Accepts Both Fleet and NavigationState | `game/strategy/data/pathfinding.py` | N/A |
| LEG-UI2-005 | Singleton Pattern Still in Use for AssetManagers | `game/ui/assets/ship_theme_manager.py` | N/A |
| LEG-UI2-006 | hasattr() Check in Camera for Defensive Coding | `game/ui/renderer/camera.py` | Simple |

## Effort Estimate

- **Simple tasks:** 8 findings
- **Medium tasks:** 7 findings
- **Complex tasks:** 1 finding
- **N/A (acceptable):** 4 findings

**Estimated Duration:** 1-2 sprints

## Recommended Phases

### Phase 1: Strategy Engine Legacy Branches (Major)
Remove explicit "legacy behavior" branches in engine code.
1. LEG-STR-001 - Update callers to pass component_registry, remove legacy path
2. LEG-STR-002 - Update tests to register fleets properly, remove O(n) fallback
3. LEG-STR-003 - Verify no legacy queue items exist, remove old code paths

### Phase 2: Save File Compatibility (Simple)
Remove save file compatibility code per disposal policy.
4. LEG-STR-005 - Remove backward compat default in Planet.from_dict
5. LEG-STR-007, LEG-STR-008 - Remove old format handling in DesignMetadata
6. LEG-SIM-006, LEG-SIM-007 - Remove fallback patterns in component system

### Phase 3: Dead Code Removal (Simple)
Remove unused code.
7. LEG-FND-005 - Remove unused AI_STATE_ERROR ErrorCode
8. LEG-UI2-004 - Remove or modernize legacy ModifierEditorPanel

### Phase 4: Pattern Modernization (Medium/Complex)
Update legacy patterns to modern approaches.
9. LEG-FND-003 - Standardize ship adapter access
10. LEG-UI2-003 - Replace getattr() defensive patterns
11. LEG-FND-004 - Audit singleton usage, convert to DI where appropriate

### Phase 5: Cleanup (Simple)
Address remaining minor items.
12. LEG-STR-004 - Evaluate if path_as_dicts is still needed
13. LEG-STR-009 - Update test mocks to properly implement interfaces
14. LEG-UI2-006 - Evaluate camera hasattr() necessity

## Potential Overlaps

Per `overlap_check.md`:
- **PROJ-121 (PROJ-B_legacy-eradication)** - Status: Planning - Direct overlap
- **PROJ-58 (Eradicate Backward Compatibility Shims)** - Status: Planning - Related overlap

**Recommendation:** Review PROJ-121 and PROJ-58 scopes. This proposal may be a superset or subset. Consider merging.

## Success Criteria

1. All MAJOR legacy branches removed
2. All backward compatibility code for save files removed
3. No explicit "legacy behavior" comments remaining
4. Unused error codes and dead code removed
5. Legacy patterns documented for future reference
