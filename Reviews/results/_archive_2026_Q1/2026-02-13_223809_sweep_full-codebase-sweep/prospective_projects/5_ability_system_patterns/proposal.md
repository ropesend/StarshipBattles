# Project Proposal: Ability System Pattern Consolidation

## Overview
This project addresses duplication and consistency issues in the Simulation layer's ability system. Multiple ability classes share identical `__init__`, `sync_data`, `recalculate`, and `get_ui_rows` patterns that should be extracted to base class methods. Additionally, the component ability extraction pattern in the Strategy layer is duplicated across harvesting and fleet capability modules.

## Priority
**Medium** - Contains 1 Critical finding (ability extraction duplication) and 8 Major findings representing significant technical debt in the core component system.

## Scope

### Included Findings (18 total)
| ID | Severity | Title |
|----|----------|-------|
| DUP-STR-001 | Critical | Duplicate Component Ability Extraction Pattern |
| DUP-SIM-001 | Major | Ability `__init__` Pattern Duplication |
| DUP-SIM-002 | Major | Repeated `sync_data` Pattern Across Propulsion Abilities |
| DUP-SIM-003 | Major | Repeated `recalculate` Pattern for Single-Stat Abilities |
| DUP-SIM-004 | Major | `to_dict`/`from_dict` Serialization Pattern Duplication |
| DUP-FND-001 | Major | Singleton Clear Pattern Duplication |
| DUP-FND-003 | Major | JSON Loading with Fallback Pattern |
| CON-SIM-003 | Major | Mixed Docstring Formats |
| CON-SIM-005 | Major | Ability Class Naming Inconsistency |
| DUP-SIM-008 | Minor | WeaponAbility Formula Handling Pattern |
| DUP-STR-003 | Major | Duplicated Star Generation Logic |
| DUP-STR-004 | Major | Ship Spawning Duplication in ProductionEngine |
| DUP-STR-005 | Major | Duplicated Complex Spawning Logic |
| DUP-STR-006 | Minor | Resource Consumption Loop Pattern |
| DUP-STR-007 | Minor | has_resources/consume Pattern |
| DUP-STR-010 | Minor | Layer Iteration Pattern |
| CON-FND-001 | Major | Inconsistent Singleton Pattern Usage |
| DUP-SIM-011 | Info | Consistent Use of Helper Class Pattern (positive reference) |

## Estimated Effort
**Medium** - 6-8 days of focused work

### Phase Breakdown
1. **Phase 1: Ability Base Class Helpers** (2 days)
   - Add `_init_single_value_stat()` to Ability base class
   - Add `_sync_single_value_stat()` helper
   - Add `_ui_row()` helper for standard row format

2. **Phase 2: Ability Class Refactoring** (2 days)
   - Refactor 11+ ability classes to use new helpers
   - Standardize `recalculate` patterns using STAT_BINDINGS

3. **Phase 3: Component Ability Extraction Service** (2 days)
   - Create `ComponentAbilityExtractor` service
   - Update HarvestingEngine to use new service
   - Update FleetCapabilityCalculator to use new service

4. **Phase 4: Strategy Consolidation** (2 days)
   - Extract `_create_ship_instance()` helper
   - Extract `_create_facility()` helper
   - Extract star generation helpers
   - Extract `iterate_design_components()` utility

## Success Criteria
- Ability classes use base class helpers
- Single ability extraction service used throughout strategy layer
- Ship/facility creation consolidated in ProductionEngine
- All tests pass

## Overlap with Existing Projects
- **PROJ-127 (code-duplication-reduction)**: Planning - overlaps on DUP findings
- **PROJ-133 (Consistency Standardization)**: Planning - overlaps on CON-SIM findings

## Risks
- Ability refactoring touches hot-path code in combat simulation
- May require extensive ability test updates
- STAT_BINDINGS auto-apply may have subtle timing issues

## Dependencies
- Should complete after Test Coverage projects to ensure test coverage first
- May benefit from Legacy Cleanup completing first (cleaner starting point)
