# Project Proposal: Code Duplication Reduction

## Overview

**Project ID:** PROJ-C_code-duplication-reduction
**Theme:** Duplication & Fragmentation (DUP) + Related UNK findings
**Total Findings:** 36 (30 DUP + 6 UNK)
**Severity Breakdown:** Critical: 0 | Major: 14 | Minor: 18 | Info: 4

## Problem Statement

The codebase contains repeated patterns and duplicated logic that should be consolidated. These include:

1. **Serialization patterns** - Multiple implementations of to_dict/from_dict
2. **Iteration patterns** - Similar loops over components, teams, ships
3. **Calculation patterns** - Repeated formulas and algorithms
4. **Utility patterns** - Scattered helper functions that could be centralized

Code duplication increases maintenance burden and risk of inconsistent behavior when one copy is updated but others are not.

## Scope

### In Scope
- All DUP (Duplication & Fragmentation) findings from all shards
- UNK findings related to potential duplication
- Pattern consolidation
- Utility extraction

### Out of Scope
- Test coverage (separate project)
- Architecture violations (separate project)
- Consistency issues (separate project)

## Findings Summary

### Major (14)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-001 | Entity Position/State Access Patterns in AI | `game/ai/combat_utils.py` | Medium |
| DUP-SIM-001 | Serialization to_dict/from_dict Pattern | `game/simulation/battle_state.py` | Medium |
| DUP-SIM-002 | Resource Ability Classes Share Identical Logic | `game/simulation/components/abilities/` | Simple |
| DUP-SIM-003 | Team Iteration Pattern Duplicated in Battle | `game/simulation/systems/battle_engine.py` | Simple |
| DUP-STR-001 | Build Queue Source Collection - Near-Identical | `game/strategy/data/build_queue.py` | Simple |
| DUP-STR-002 | Facility Shipyard Detection - Duplicated | `game/strategy/data/build_queue.py` | Simple |
| DUP-STR-003 | Mission Command Handler Duplication | `game/strategy/engine/superweapon.py` | Simple |
| DUP-STR-004 | to_dict/from_dict Boilerplate Pattern | Multiple files | Complex |
| DUP-STR-005 | Fleet Resolution Pattern in Command Handlers | Multiple files | Simple |
| DUP-STR-006 | ColonizeValidator Colony Pod Iteration Pattern | `game/strategy/validation/colonize.py` | Simple |
| DUP-STR-007 | Component Layer Iteration Pattern - Repeated | Multiple files | Medium |

### Minor (18)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-004 | Flee Direction Calculation | `game/ai/behaviors.py` | Simple |
| DUP-FND-005 | Tech Tree Validation Method Patterns | `game/research/data/tech_tree.py` | Simple |
| DUP-FND-006 | Serialization to_dict/from_dict Patterns | `game/research/data/research_tracker.py` | Complex |
| DUP-SIM-004 | Vector2 Conversion Pattern in Projectile | `game/simulation/projectile_manager.py` | Simple |
| DUP-SIM-005 | get_ui_rows Color Mapping Pattern | `game/simulation/components/abilities/` | Simple |
| DUP-SIM-006 | ship_id_map Pattern Repeated in RetreatManager | `game/simulation/managers/retreat_manager.py` | Simple |
| DUP-SIM-007 | Validation Pattern in modifier_schema.py | `game/simulation/components/modifier_schema.py` | Medium |
| DUP-STR-008 | Gaussian Factor Calculation Pattern | `game/strategy/formulas/habitability.py` | Simple |
| DUP-STR-009 | Path Start Hex Determination Logic | Multiple files | Simple |
| DUP-STR-010 | Ship Ability Check Wrappers | Multiple files | Simple |
| DUP-STR-011 | Resource Dictionary Accumulation Pattern | `game/strategy/services/ship_stats.py` | Simple |
| DUP-STR-012 | Fleet and Ship Delegation Pattern | Multiple files | Medium |
| DUP-UI2-004 | Image Transform Operations Scattered | `game/ui/utils.py` | Simple |
| DUP-UI2-005 | Validation Service Pattern Has Single-Purpose Classes | `game/ui/services/validation_service.py` | N/A |
| DUP-UI2-006 | Camera Coordinate Transform Duplication | `game/ui/renderer/camera.py` | Medium |
| UNK-08 | Population/Number Formatting Duplication | Multiple files | Unknown |
| UNK-09 | RaceThemeGallery Not Using BaseGallery | Multiple files | Unknown |
| UNK-10 | Window Kill/Cleanup Pattern Slightly Inconsistent | Multiple files | Unknown |
| UNK-11 | Dropdown Recreation Utility | Multiple files | Unknown |

### Info (4)

| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-SIM-008 | Natural Similarity in Dataclass State Classes | `game/simulation/battle_state.py` | N/A |
| DUP-STR-013 | Validated Design Component Iteration | Multiple files | Medium |
| DUP-STR-014 | Well-Consolidated Component Inspector | `game/strategy/services/component_inspector.py` | N/A |
| DUP-UI2-007 | Color Constants Could Be Centralized Further | `game/ui/colors.py` | N/A |

## Effort Estimate

- **Simple tasks:** 18 findings
- **Medium tasks:** 8 findings
- **Complex tasks:** 3 findings
- **N/A (acceptable/info):** 4 findings
- **Unknown:** 3 findings

**Estimated Duration:** 2 sprints

## Recommended Phases

### Phase 1: Serialization Consolidation (Complex)
High-impact consolidation of repeated to_dict/from_dict patterns.
1. DUP-STR-004 - Create generic serialization base class or mixin
2. DUP-SIM-001, DUP-FND-006 - Apply pattern to battle_state and research

### Phase 2: Iterator Patterns (Simple/Medium)
Consolidate repeated iteration patterns.
3. DUP-SIM-003 - Extract team iteration helper
4. DUP-STR-006 - Extract component iteration helpers
5. DUP-STR-007 - Extract layer iteration pattern

### Phase 3: Calculation Utilities (Simple)
Extract repeated calculations into utility functions.
6. DUP-FND-004 - Extract flee direction calculator
7. DUP-STR-008 - Extract gaussian factor utility
8. DUP-SIM-004 - Consolidate Vector2 conversion

### Phase 4: UI Utilities (Simple/Medium)
Consolidate scattered UI helper code.
9. DUP-UI2-004 - Consolidate image transforms
10. DUP-UI2-006 - Consolidate camera transforms
11. UNK-08 - Consolidate number formatting
12. UNK-11 - Consolidate dropdown recreation

### Phase 5: Domain Helpers (Simple)
Extract repeated domain-specific helpers.
13. DUP-STR-001, DUP-STR-002 - Consolidate build queue patterns
14. DUP-STR-005 - Extract fleet resolution helper
15. DUP-SIM-002 - Consolidate resource ability logic

## Potential Overlaps

No direct overlaps identified in `overlap_check.md`.

## Success Criteria

1. All MAJOR duplication issues resolved
2. Common serialization base class/mixin created
3. Iterator helpers extracted and reused
4. Calculation utilities centralized
5. No copy-paste code patterns remaining
