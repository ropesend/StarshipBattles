# Project Proposal: UI Duplication Consolidation

## Overview
This project addresses Critical and Major duplication findings in the UI layer, focusing on extracting shared utilities and consolidating repeated patterns. The UI layer has the most immediate duplication debt, including identical Tkinter initialization across 4 files, screenshot toast patterns in 3 locations, and inconsistent DI patterns across services.

## Priority
**High** - Contains 4 Critical findings and 10 Major findings affecting UI code quality and maintainability.

## Scope

### Included Findings (16 total)
| ID | Severity | Title |
|----|----------|-------|
| DUP-UI2-001 | Critical | Tkinter Root Initialization Duplicated Across 4 Files |
| DUP-UI1-001 | Critical | Screenshot Toast Notification Pattern Duplicated in 3+ Locations |
| CON-UI2-001 | Critical | Inconsistent Dependency Injection Patterns Across Services |
| DUP-UI2-002 | Major | Battle Factory Functions Follow Identical Structural Pattern |
| DUP-UI2-004 | Major | BattleUIService Repeated Null-Check Pattern |
| DUP-UI1-003 | Major | Filter State Management Pattern Repeated |
| DUP-UI1-004 | Major | Compact Number Formatting Logic Isolated |
| DUP-UI2-006 | Minor | Ship Cloning Logic in create_hypothetical_battle |
| DUP-UI1-005 | Minor | RaceThemeGallery Not Using BaseGallery |
| CON-UI2-007 | Minor | Inconsistent Type Hint Coverage |
| CON-UI2-008 | Minor | Inconsistent Error Logging Patterns |
| CON-UI2-010 | Minor | Boolean Parameter Naming Inconsistency |
| CON-UI2-011 | Minor | Inconsistent Import Organization |
| CON-UI2-012 | Minor | Magic Numbers in Rendering Code |
| CON-UI2-013 | Info | Inconsistent __all__ Export Patterns |
| DUP-UI1-009 | Info | Well-Refactored Gallery System (positive reference) |

### Excluded
- Test coverage gaps (separate project)
- Architecture drift findings (separate project)
- Module-level side effects (addressed in legacy cleanup)

## Estimated Effort
**Medium** - 6-8 days of focused work

### Phase Breakdown
1. **Phase 1: Tkinter Utility Extraction** (2 days)
   - Create `game/ui/services/tkinter_utils.py` with unified initialization
   - Update 4 files to use shared utility

2. **Phase 2: DI Pattern Standardization** (2 days)
   - Create `RegistryConsumerMixin` base class
   - Standardize 5 services on lazy DI pattern

3. **Phase 3: UI Utility Consolidation** (2 days)
   - Extract screenshot toast to shared utility
   - Extract compact number formatting
   - Consolidate BattleUIService null-check pattern

4. **Phase 4: Minor Cleanups** (1-2 days)
   - Standardize error logging format
   - Extract magic numbers to config
   - Fix import organization

## Success Criteria
- All 4 Tkinter initialization sites use shared utility
- DI pattern is consistent across UI services
- No duplicate utility code in screens/panels
- All tests pass

## Overlap with Existing Projects
- **PROJ-127 (code-duplication-reduction)**: Planning status - this project is a focused subset
- **PROJ-128 (codebase-consistency)**: Overlaps on consistency findings - coordinate to avoid duplicated work
- **PROJ-133 (Consistency Standardization)**: Planning - coordinate on CON-UI2-* findings

## Risks
- Filter state consolidation (DUP-UI1-003) may require touching 3 different window implementations
- DI standardization may surface hidden dependencies in services
