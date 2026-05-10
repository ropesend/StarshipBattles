# Project Proposal: Legacy Code Cleanup

## Overview
This project eradicates legacy system holdovers across all layers, including backward compatibility shims, dead fallback code, and obsolete patterns that violate the project's "ERADICATE old systems completely" policy. Per project guidelines, save files are disposable and compatibility code should not exist.

## Priority
**Medium-High** - Contains 0 Critical but 13 Major findings representing technical debt that adds confusion and maintenance burden. Several findings note active dual code paths where only one should exist.

## Scope

### Included Findings (25 total)
| ID | Severity | Title |
|----|----------|-------|
| LEG-FND-001 | Major | Excessive getattr() Fallbacks in AI CombatUtils |
| LEG-SIM-001 | Major | Module Identity Drift Fallback in AbilityManager |
| LEG-SIM-002 | Major | Singleton Pattern in Component Cache Manager |
| LEG-SIM-003 | Major | Dead Fallback Code in BattleController |
| LEG-STR-001 | Major | Backward Compatibility Fallback in GameSession |
| LEG-STR-002 | Major | Legacy Behavior Comments in FleetOrderProcessor |
| LEG-STR-003 | Major | Backward Compatibility Default in Planet |
| LEG-STR-004 | Major | Backward Compatibility in FleetNavigationService |
| LEG-STR-005 | Major | Legacy Production Items in ProductionEngine |
| LEG-UI2-001 | Major | BattleOrchestrator Class Is Unused |
| CON-UI2-005 | Major | Module-Level Side Effects in ship_io.py |
| ADR-UI2-002 | Major | ShipIO module-level Tkinter initialization |
| LEG-FND-004 | Minor | Defensive hasattr() Checks in AI Layer |
| LEG-FND-005 | Minor | Unused Error Codes |
| LEG-SIM-009 | Minor | Unused Parameter in _apply_results_to_fleet |
| LEG-STR-006 | Minor | Unused Import StarType in galaxy.py |
| LEG-STR-007 | Minor | Reserved/Placeholder Field sprite_preview |
| LEG-STR-009 | Minor | Backward Compatibility Comment in game_config |
| LEG-STR-010 | Minor | Support for Old Layer Format in DesignMetadata |
| LEG-UI2-003 | Minor | WHITE and BLACK Color Constants Are Dead |
| LEG-FND-007 | Info | Fallback Behaviors Are Intentional Design (review only) |
| LEG-SIM-010 | Info | Documented Technical Debt in ability_manager |
| LEG-STR-011 | Info | hasattr() Checks for Standard Attributes |
| LEG-UI2-005 | Info | Singleton Pattern Still Used in UI Layer (review only) |

### Strategy Legacy Findings (additional minor)
- Multiple stale docstrings referencing removed code

## Estimated Effort
**Medium** - 6-10 days of focused work

### Phase Breakdown
1. **Phase 1: Simulation Layer Cleanup** (2 days)
   - Remove dead BattleController fallback code
   - Clean up ability_manager identity drift (or document decision)
   - Review Component Cache singleton pattern

2. **Phase 2: Strategy Layer Cleanup** (3 days)
   - Remove GameSession fallback iteration
   - Enforce registry in FleetOrderProcessor
   - Remove legacy production item handling
   - Remove backward compat in FleetNavigationService

3. **Phase 3: Foundation/AI Cleanup** (2 days)
   - Remove excessive getattr() fallbacks in combat_utils
   - Remove unused error codes
   - Clean up defensive hasattr checks

4. **Phase 4: UI Layer Cleanup** (2 days)
   - Convert ship_io.py to lazy Tkinter init
   - Remove unused BattleOrchestrator if confirmed dead
   - Remove dead color constants

## Success Criteria
- All "backward compatibility" comments removed or explained
- No dead fallback code paths
- GameSession uses only registry lookup
- FleetOrderProcessor requires component_registry
- All tests pass

## Overlap with Existing Projects
- **PROJ-134 (Legacy Code Cleanup)**: Planning - direct overlap, should be merged or superseded
- **PROJ-129 (legacy-system-cleanup)**: Planning - direct overlap
- **PROJ-121 (PROJ-B_legacy-eradication)**: Planning - direct overlap
- **PROJ-123 (PROJ-D_architecture-cleanup)**: Planning - partial overlap on LEG findings
- **PROJ-58 (Eradicate Backward Compatibility Shims)**: Planning - direct overlap

## Risks
- Removing fallback code may expose test fixtures that don't properly set up state
- ProductionEngine legacy handling removal may require queue item migration
- FleetOrderProcessor changes may break colonization if tests use None registry

## Dependencies
- May benefit from Test Coverage projects completing first (to ensure coverage before removal)
- Strategy legacy cleanup may require updating test fixtures
