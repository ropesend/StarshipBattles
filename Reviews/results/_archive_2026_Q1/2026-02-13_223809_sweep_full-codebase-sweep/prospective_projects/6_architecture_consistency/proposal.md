# Project Proposal: Architecture and Consistency Standardization

## Overview
This project addresses architecture drift findings and remaining consistency violations across all layers. The simulation layer has dependencies on game.engine that need clarification, there are circular import risks, and god class indicators that warrant monitoring. Additionally, there are consistency issues around naming, type hints, and patterns that span multiple modules.

## Priority
**Medium** - Contains 7 Major architecture findings and multiple consistency issues. Most findings are structural improvements rather than urgent fixes.

## Scope

### Included Findings (35 total)
| ID | Severity | Title |
|----|----------|-------|
| ADR-SIM-001 | Major | Simulation Depends on game.engine (PhysicsBody) |
| ADR-SIM-002 | Major | Simulation Depends on game.engine (SpatialGrid, CollisionSystem) |
| ADR-SIM-003 | Major | Circular Import Risk - Ship and ModifierService |
| ADR-STR-001 | Major | Strategy Layer Imports AI Layer |
| ADR-STR-002 | Major | Galaxy Class Approaching God Class Territory |
| ADR-UI2-001 | Major | ShipFactory uses pygame.math.Vector2 |
| ADR-UI2-003 | Major | Camera class uses pygame.math.Vector2 |
| CON-STR-004 | Major | Inconsistent Constructor DI Pattern Application |
| CON-STR-005 | Major | Mixed Static Methods and Instance Methods |
| ADR-SIM-004 | Minor | Circular Import Risk - ShipSerializer |
| ADR-SIM-005 | Minor | God Class Indicator - Ship Class (810 LOC) |
| ADR-SIM-006 | Minor | God Class Indicator - Component Class (723 LOC) |
| ADR-STR-003 | Minor | Production Engine Approaching 500+ LOC |
| ADR-STR-004 | Minor | FleetOrderProcessor Approaching 500+ LOC |
| ADR-UI2-006 | Minor | Inconsistent use of Any type hints |
| CON-FND-009 | Minor | Inconsistent Use of clear() vs reset() |
| CON-FND-011 | Minor | Incomplete __all__ Exports |
| CON-FND-013 | Minor | Error Code Enum Incomplete Coverage |
| CON-SIM-009 | Minor | Magic Numbers in Physics Calculations |
| CON-SIM-012 | Minor | Component Type Checking Inconsistency |
| ADR-FND-004 | Info | Core Layer Properly Isolates (positive) |
| ADR-SIM-007 | Info | TYPE_CHECKING Used Extensively (positive) |
| ADR-STR-005 | Info | Cross-Layer Imports via TYPE_CHECKING (positive) |
| ADR-UI2-007 | Info | DesignLoaderAdapter imports Simulation |
| ADR-UI2-008 | Info | Screenshot manager hardcoded strategies |
| CON-SIM-018 | Info | Singleton Pattern Usage |
| CON-SIM-019 | Info | Ability Registry as Module-Level Dict |
| CON-SIM-020 | Info | Late Import Comments |
| CON-STR-014 | Info | Natural Variation in Method Signatures |
| CON-STR-015 | Info | Facade vs Direct Access Pattern |
| CON-STR-016 | Info | Delegate Pattern Consistency |
| CON-STR-017 | Info | Event System Consistency |
| CON-STR-018 | Info | Interface Naming Convention |
| DUP-FND-008 | Info | Singleton Pattern Consistency |
| DUP-FND-009 | Info | Combat Utils Consolidation Success (positive) |

## Estimated Effort
**Medium-Complex** - 8-12 days of focused work

### Phase Breakdown
1. **Phase 1: Architecture Documentation** (2 days)
   - Document game.engine as "Core-adjacent infrastructure"
   - Add architecture.md clarifying layer relationships
   - Document acceptable cross-layer patterns

2. **Phase 2: Circular Import Remediation** (3 days)
   - Refactor Ship/ModifierService circular import
   - Review Ship/ShipSerializer pattern
   - Extract modifier application to standalone function

3. **Phase 3: God Class Monitoring** (2 days)
   - Set up LOC monitoring for Ship/Component/Galaxy
   - Document decomposition strategy if thresholds exceeded
   - Review existing helper class extractions

4. **Phase 4: Consistency Standardization** (3 days)
   - Standardize clear() vs reset() naming
   - Complete __all__ exports
   - Add missing error codes
   - Extract magic numbers to constants

## Success Criteria
- Architecture document clarifies engine layer role
- Circular imports documented or resolved
- God class sizes monitored with thresholds
- Naming conventions standardized
- All tests pass

## Overlap with Existing Projects
- **PROJ-132 (Architecture Layer Violations)**: Planning - direct overlap
- **PROJ-126 (architecture-layer-fixes)**: Planning - direct overlap
- **PROJ-123 (PROJ-D_architecture-cleanup)**: Planning - partial overlap
- **PROJ-133 (Consistency Standardization)**: Planning - overlaps on CON findings
- **PROJ-128 (codebase-consistency)**: Planning - overlaps on consistency
- **PROJ-125 (PROJ-F_code-consistency)**: Planning - overlaps

## Risks
- Engine layer documentation may reveal need for actual refactoring
- Circular import fixes may require significant restructuring
- God class decomposition is complex and touches many call sites

## Dependencies
- Should complete after other projects to minimize churn
- Architecture decisions affect all other projects

## Notes
Many findings in this project are "monitoring" or "documentation" rather than code changes. The goal is to establish clear architectural guidelines and address the most impactful structural issues while documenting decisions on others.
