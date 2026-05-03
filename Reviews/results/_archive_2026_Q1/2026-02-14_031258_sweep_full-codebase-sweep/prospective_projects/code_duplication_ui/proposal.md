# Project Proposal: Code Duplication - UI Layer

## Overview

This project addresses code duplication findings in the UI layer, including duplicate utility functions, redundant pattern implementations, and classes that should share base implementations. The focus is on consolidating UI utilities and establishing shared patterns.

## Rationale

The UI layer has significant code duplication:
- Three separate ColumnManager implementations with overlapping functionality (CRITICAL)
- HP color calculation duplicated in 3+ locations with inconsistent thresholds
- Number formatting (k/M suffixes) implemented in 4+ locations
- Gallery classes don't share a common base despite identical patterns
- Various utility patterns repeated across files

This duplication creates maintenance burden and visual inconsistency risks.

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| DUP-UI1-001 | Critical | Duplicate ColumnManager Classes | game/ui/screens/column_manager.py, planet_list_columns.py | Medium |
| DUP-UI1-002 | Major | Duplicate draw_stat_bar Implementations | game/ui/panels/ | Simple |
| DUP-UI1-003 | Major | Duplicate HP Color Calculation Logic | game/ui/panels/ | Simple |
| DUP-UI1-004 | Major | Duplicate Number Magnitude Formatting | game/ui/screens/ | Simple |
| DUP-UI1-005 | Major | RaceThemeGallery Does Not Extend BaseGallery | game/ui/panels/race_theme_gallery.py | Medium |
| DUP-FND-001 | Major | Strategy Data Loading Duplication | game/core/strategy_metadata.py | Simple |
| DUP-SIM-001 | Major | Ability Pattern Boilerplate Duplication | game/simulation/components/abilities/ | Medium |
| DUP-SIM-002 | Major | Formula Evaluation Pattern Duplication | game/simulation/components/abilities/ | Simple |
| DUP-SIM-003 | Major | Resource Type Handling Duplication | game/simulation/entities/ship_resources.py | Medium |
| DUP-SIM-004 | Major | Validation Pattern Repetition in Loaders | game/simulation/components/ | Medium |
| DUP-STR-001 | Major | Component Ability Extraction Pattern Repetition | game/strategy/engine/ | Medium |
| DUP-STR-002 | Major | Layer Iteration Pattern Duplicated in 7+ Files | game/strategy/ | Medium |
| DUP-UI2-010 | Major | Registry Provider Access Pattern Duplication | game/ui/services/ | Medium |
| DUP-UI2-012 | Major | Singleton Manager Pattern Duplication | game/ui/assets/ | Medium |
| DUP-UI1-006 | Minor | Duplicate Portrait Loading Logic | game/ui/screens/ | Simple |
| DUP-UI1-008 | Minor | Filter/Sort Pattern Duplication | game/ui/screens/ | Medium |
| DUP-FND-002 | Minor | Singleton Clear Pattern Repetition | game/core/ | Medium |
| DUP-STR-003 | Minor | Maintenance Cost Calculation Near-Duplication | game/strategy/engine/ | Medium |
| DUP-UI2-011 | Minor | Service Adapter Boilerplate Pattern | game/ui/services/ | Medium |
| DUP-SIM-005 | Minor | Target Validation Pattern Duplication | game/simulation/combat/ | Simple |
| DUP-SIM-007 | Minor | UI Row Generation Pattern | game/simulation/components/abilities/ | Medium |
| DUP-SIM-008 | Minor | Physics Constants Duplication | game/simulation/entities/ | Simple |
| DUP-STR-004 | Minor | Distance Calculation From Center Repeated | game/strategy/ | Simple |
| DUP-STR-005 | Minor | Density Primitive Gaussian Falloff Pattern | game/strategy/ | Simple |
| DUP-STR-006 | Minor | Fleet-Like Object Creation for Pathfinding | game/strategy/ | Simple |
| DUP-UI2-015 | Minor | Image Loading Exception Handling Pattern | game/ui/assets/ | Simple |
| DUP-UI2-016 | Minor | Empty __init__.py Files | game/ui/renderer/ | Simple |

## Summary Statistics

- **Total Findings:** 27
- **Critical:** 1 | **Major:** 13 | **Minor:** 13
- **Estimated Effort:** Medium (many simple fixes, one medium refactor)
- **Primary Location:** game/ui/screens/, game/ui/panels/, game/simulation/

## Overlap with Active Projects

Potential overlap with:
- PROJ-141: 1_ui_duplication_consolidation (likely duplicate)
- PROJ-127: code-duplication-reduction (overlapping)

**Recommendation:** This sweep provides comprehensive findings. Review PROJ-141 status before starting.

## Success Criteria

1. Single BaseColumnManager class used by all column managers
2. Single get_hp_color() function used everywhere
3. Single format_quantity() function for k/M formatting
4. RaceThemeGallery extends BaseGallery
5. draw_stat_bar wrapper removed
