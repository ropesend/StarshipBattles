# Project Proposal: Legacy System Eradication

## Summary

**Project ID:** PROJ-B (Prospective)
**Theme:** Legacy System Holdovers
**Priority:** High
**Estimated Effort:** Medium
**Findings Count:** 37

## Problem Statement

Per the project's System Migration Policy: "When a new system replaces an old one, ERADICATE the old system completely." The codebase contains numerous backward compatibility shims, deprecated code paths, and legacy API holdovers that should be removed.

Two Critical findings and 14 Major findings identify code that explicitly uses phrases like "backward compatibility", "legacy", "migration support", or implements fallback patterns for deprecated APIs.

## Scope

### Key Files Affected

**Simulation Layer:**
- `game/simulation/systems/battle_engine.py` - String-to-Enum migration support
- `game/simulation/components/modifier_schema.py` - V1 format detection
- `game/simulation/systems/battle_engine.py` - hasattr checks
- `game/simulation/managers/retreat_manager.py` - hasattr checks

**UI Layer:**
- `game/ui/panels/race_portrait_gallery.py` - Backward compatibility aliases
- `game/ui/screens/builder/main.py` - Legacy BuilderScreen
- `game/ui/screens/builder/detail_panel.py` - Legacy tuple format
- `game/ui/screens/empire_build_queue_window.py` - Legacy single-selection
- `game/ui/panels/build_queue_controller.py` - Fallback mode

**Core/Foundation:**
- `game/core/exceptions.py` - Unused exception classes
- `game/core/resources.py` - Backward compatibility wrapper

### Pattern Categories

1. **String/Enum Migration Code** - Code that converts strings to enums "for migration"
2. **Hasattr Defensive Patterns** - Checking for attributes that should always exist
3. **Dual Format Support** - Code supporting both old and new data formats
4. **Backward Compatibility Aliases** - Properties/methods that alias to new names
5. **Unused Legacy Code** - Dead code from previous versions

## Findings Included

| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| LEG-SIM-001 | Critical | String-to-Enum Migration Support Code | Medium |
| LEG-UI1-001 | Critical | Backward Compatibility Aliases in RacePortraitGallery | Simple |
| LEG-FND-001 | Major | Unused Exception Classes | Simple |
| LEG-FND-002 | Major | Backward Compatibility Wrapper - load_resources | Simple |
| LEG-SIM-002 | Major | V1 Modifier Format Validation Code | Simple |
| LEG-SIM-003 | Major | Defensive hasattr Check for Always-Present Attribute | Simple |
| LEG-SIM-004 | Major | retreat_status Attribute via hasattr | Simple |
| LEG-UI2-001 | Major | Dead Code - draw_hud and draw_bar | Simple |
| LEG-UI2-002 | Major | Unused Method - create_ai_for_ship | Simple |
| LEG-UI2-003 | Major | Unused Method - capture_step | Simple |
| LEG-UI1-002 | Major | Legacy BuilderScreen Parallel to WorkshopScreen | Complex |
| LEG-UI1-003 | Major | Legacy Tuple Format Support | Medium |
| LEG-UI1-004 | Major | Legacy API Comment in FleetReportWindow | Simple |
| LEG-UI1-005 | Major | Legacy Single-Selection Fields | Medium |
| LEG-UI1-006 | Major | Fallback Mode in BuildQueueController | Medium |
| LEG-FND-003 | Minor | Backward Compatibility Comment in Validation | Simple |
| LEG-FND-004 | Minor | Extensive getattr() with Defaults | Medium |
| LEG-FND-005 | Minor | Raw Ship vs Adapter Access Pattern | Medium |
| LEG-FND-006 | Minor | DEBUG_SCREENSHOTS Hardcoded True | Simple |
| LEG-FND-007 | Minor | Singleton Pattern Despite DI | Complex |
| LEG-SIM-005 | Minor | Fallback Pattern Comments | Simple |
| LEG-SIM-006 | Minor | Ability Manager Fallback | Medium |
| LEG-SIM-007 | Minor | Component Fallback Delegation | Simple |
| LEG-SIM-008 | Minor | Unused AbilityStatBinding.describe() | Simple |
| LEG-UI2-004 | Minor | Duplicate Exception Handlers | Simple |
| LEG-UI2-005 | Minor | "legacy behavior" Comment | Medium |
| LEG-UI2-006 | Minor | Basic Color Constants | Simple |
| LEG-UI2-007 | Minor | ShipIOAdapter vs ShipIO Direct Access | Medium |
| LEG-UI2-008 | Minor | Excessive getattr() with Defaults | Medium |
| LEG-UI1-007 | Minor | Backward Compat Attribute Exposure | Simple |
| LEG-UI1-008 | Minor | Backward Compatibility in WorkshopEventRouter | Simple |
| LEG-UI1-009 | Minor | Test Lab Screen Legacy Game Parameter | Medium |
| LEG-UI1-010 | Minor | Compatibility Setter in BuilderStateManager | Simple |
| LEG-UI1-011 | Minor | Deprecated Properties in StrategyScreen | Complex |
| LEG-UI2-009 | Info | Singleton Pattern for Assets | N/A |
| LEG-UI2-010 | Info | Anticipatory Code | Simple |
| LEG-UI1-012 | Info | Legacy Keys Filtering | Simple |

## Overlap Analysis

**PROJ-58 (Eradicate Backward Compatibility Shims):** This prospective project has significant overlap with PROJ-58 which is in Planning status. Recommendation: Review PROJ-58 scope and either merge findings or coordinate efforts.

## Success Criteria

1. All "migration support" code paths removed
2. All hasattr checks for always-present attributes removed
3. All backward compatibility aliases removed
4. All dual-format support consolidated to new format only
5. Tests updated to use canonical APIs
6. No regressions in test suite

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Legacy BuilderScreen may have unique test usage | Audit test dependencies before removal |
| Some "legacy" comments may be stale | Verify each finding before removing code |
| String-to-Enum migration may have hidden callers | Search entire codebase for string attack types |

## Recommended Phases

### Phase 1: Simple Removals (Days 1-2)
- Remove unused exception classes
- Remove backward compatibility aliases
- Remove dead code (draw_hud, capture_step, etc.)
- Remove hasattr checks for always-present attributes

### Phase 2: Format Consolidation (Days 3-4)
- Remove V1 modifier format detection
- Migrate tuple format to ComponentRef
- Remove string-to-enum migration code
- Update tests to use new formats

### Phase 3: Complex Removals (Days 5-7)
- Evaluate Legacy BuilderScreen removal
- Remove dual-selection system
- Remove fallback modes
- Clean up deprecated properties

## Dependencies

- Should coordinate with or run after PROJ-58
- May require test updates as legacy APIs are removed
