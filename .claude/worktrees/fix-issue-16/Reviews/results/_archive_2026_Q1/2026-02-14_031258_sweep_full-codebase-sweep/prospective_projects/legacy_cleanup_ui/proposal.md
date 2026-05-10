# Project Proposal: Legacy Cleanup - UI and Services

## Overview

This project addresses legacy system holdovers in the UI layer, including unused code, defensive patterns from incomplete migrations, and obsolete modules. The focus is on removing dead code and cleaning up migration artifacts.

## Rationale

The UI layer has accumulated legacy artifacts:
- BattleOrchestrator (99 lines) is completely unused dead code (CRITICAL)
- Defensive getattr patterns mask bugs rather than handling them
- VehicleClassService has unused methods
- Various singleton patterns should be migrated to DI
- Fallback patterns suggest incomplete migrations

Cleaning these up reduces maintenance burden and eliminates confusion.

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| LEG-UI2-001 | Critical | BattleOrchestrator is Defined but Never Used | game/ui/orchestration/battle_orchestrator.py | Medium |
| LEG-FND-002 | Major | Singleton Pattern Pervasive Despite DI Push | game/core/singleton.py | Complex |
| LEG-FND-003 | Major | Defensive getattr Fallbacks in AI Module | game/ai/controller.py | Medium |
| LEG-SIM-002 | Major | Unused BattleConfig.isolated Field | game/simulation/battle_config.py | Simple |
| LEG-SIM-003 | Major | Unused validate_state Method in BattleState | game/simulation/managers/battle_state.py | Simple |
| LEG-UI2-002 | Major | Defensive getattr Checks for Attributes | game/ui/services/battle_ui_service.py | Medium |
| LEG-UI2-003 | Major | VehicleClassService Methods Appear Unused | game/ui/services/vehicle_class_service.py | Simple |
| LEG-UI1-001 | Major | Legacy Single-Selection Fields Maintained | game/ui/screens/empire_build_queue.py | Simple |
| LEG-UI1-003 | Major | Fallback Pattern to Direct scene.ships Access | game/ui/panels/battle_panels.py | Medium |
| LEG-FND-001 | Minor | Unused Error Codes in error_codes.py | game/core/error_codes.py | Simple |
| LEG-FND-004 | Minor | Strategy Fallback Patterns in AI Documentation | game/ai/__init__.py | Medium |
| LEG-UI1-002 | Minor | Unused Imports Across Multiple Files | game/ui/screens/ | Simple |
| LEG-FND-006 | Minor | is_camera TypeGuard Never Used | game/core/protocols.py | Simple |
| LEG-FND-007 | Minor | Profiling Module Has Inconsistent API | game/core/profiling.py | Simple |
| LEG-FND-008 | Minor | Mock Detection Pattern in combat_utils | game/ai/combat_utils.py | Simple |
| LEG-SIM-004 | Minor | Unused Documentation Constants in physics_constants | game/simulation/physics_constants.py | Simple |
| LEG-SIM-005 | Minor | Singleton Pattern in ComponentCacheManager | game/simulation/components/ | Complex |
| LEG-SIM-006 | Minor | KNOWN_ISSUE Comment for Module Identity | game/simulation/components/abilities/ | Medium |
| LEG-SIM-008 | Minor | Fallback Comments Suggesting Incomplete Migration | game/simulation/ | Medium |
| LEG-UI2-004 | Minor | ComponentService.is_modifier_allowed Duplicates | game/ui/services/component_service.py | Simple |
| LEG-UI2-007 | Minor | Inconsistent DI Patterns Across Services | game/ui/services/ | Simple |
| LEG-UI1-004 | Minor | Empty __init__ Method | game/ui/screens/race_asset_loader.py | Simple |
| LEG-UI1-005 | Minor | Disabled Feature Left as pass Statement | game/ui/screens/builder/schematic_view.py | Simple |
| LEG-UI1-006 | Minor | get_component_at Returns None Unconditionally | game/ui/screens/builder/schematic_view.py | Simple |
| LEG-UI1-007 | Minor | Legacy Pattern Comment Without Active Code | game/ui/screens/builder/stats_config.py | Simple |
| LEG-UI1-009 | Minor | Formation File Format Comment Suggests Rework | game/ui/screens/formation_editor.py | Simple |
| LEG-UI1-010 | Minor | Fallback Mode in Build Queue Controller | game/ui/panels/build_queue_controller.py | Medium |

## Summary Statistics

- **Total Findings:** 27
- **Critical:** 1 | **Major:** 8 | **Minor:** 18
- **Estimated Effort:** Medium (many simple deletions)
- **Primary Location:** game/ui/services/, game/ui/screens/

## Overlap with Active Projects

Potential overlap with:
- PROJ-144: 4_legacy_code_cleanup (likely duplicate)
- PROJ-134: Legacy Code Cleanup (likely duplicate)
- PROJ-129: legacy-system-cleanup (overlapping)
- PROJ-121: PROJ-B_legacy-eradication (overlapping)
- PROJ-58: Eradicate Backward Compatibility Shims (overlapping)

**Recommendation:** Review PROJ-144 status before starting. This sweep provides fresh findings.

## Success Criteria

1. BattleOrchestrator module deleted
2. Unused VehicleClassService methods removed
3. Defensive getattr patterns replaced with proper types
4. Unused error codes removed
5. Dead code reduced by measurable amount
