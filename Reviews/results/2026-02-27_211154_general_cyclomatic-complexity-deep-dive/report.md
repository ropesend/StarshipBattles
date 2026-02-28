# Review Report: 2026-02-27_211154_general_cyclomatic-complexity-deep-dive

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review (Complexity Focus)
- **Description:** 
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 95
- **Critical:** 7 | **Major:** 35 | **Minor:** 37 | **Info:** 16
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 103
- **Confirmed:** 95 | **Downgraded:** 18 | **Rejected:** 8
- **Rejection Rate:** 7.8%
- **Findings Without Verdict:** 0

## Priority Findings (Top 10)

### 1. CRITICAL: Latent Bug in Production Cost Fallback
**ID:** AR-01
**Agent:** Validated
**Location:** `game/strategy/engine/productio`
**Effort:** Medium

**Location:** `game/strategy/engine/productio`

---

### 2. CRITICAL: Defensive Code Masking Bugs - Silent `pa
**ID:** CQ-002
**Agent:** Validated
**Location:** `game/strategy/engine/productio`
**Effort:** Simple

**Location:** `game/strategy/engine/productio`

---

### 3. CRITICAL: Warp Jump Handling is Highest CC Driver
**ID:** CX-001
**Agent:** Validated
**Location:** `game/strategy/services/ship_st`
**Effort:** Medium

**Location:** `game/strategy/services/ship_st`

---

### 4. CRITICAL: _process_queue_tick_dynamic Has 130-Line
**ID:** CX-002
**Agent:** Validated
**Location:** `game/strategy/engine/productio`
**Effort:** Medium

**Location:** `game/strategy/engine/productio`

---

### 5. CRITICAL: project_path Threads 5 Mutable Variables
**ID:** CX-003
**Agent:** Validated
**Location:** `game/strategy/services/fleet_n`
**Effort:** Medium

**Location:** `game/strategy/services/fleet_n`

---

### 6. CRITICAL: No Tests for Zero Production Rate in Pro
**ID:** TC-002
**Agent:** Validated
**Location:** `game/strategy/engine/productio`
**Effort:** Simple

**Location:** `game/strategy/engine/productio`

---

### 7. CRITICAL: WarpJump Non-Dict Value Branch Untested
**ID:** TC-004
**Agent:** Validated
**Location:** `game/strategy/services/ship_st`
**Effort:** Simple

**Location:** `game/strategy/services/ship_st`

---

### 8. MAJOR: Single Responsibility Violation - Functi
**ID:** CQ-001
**Agent:** Validated
**Location:** `game/strategy/engine/productio`
**Effort:** Medium

**Location:** `game/strategy/engine/productio`

---

### 9. MAJOR: Monolithic Accumulation Loop - 136 Lines
**ID:** CQ-011
**Agent:** Validated
**Location:** `game/strategy/services/ship_st`
**Effort:** Complex

**Location:** `game/strategy/services/ship_st`

---

### 10. MAJOR: Proposed `_accumulate_component_stats` d
**ID:** DS-005
**Agent:** Validated
**Location:** `game/strategy/services/ship_st`
**Effort:** Medium

**Location:** `game/strategy/services/ship_st`

---


## Findings by Severity

### Critical (7)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-01 | Latent Bug in Production Cost Fallback | `game/strategy/engine/productio` | Medium |
| CQ-002 | Defensive Code Masking Bugs - Silent `pa | `game/strategy/engine/productio` | Simple |
| CX-001 | Warp Jump Handling is Highest CC Driver | `game/strategy/services/ship_st` | Medium |
| CX-002 | _process_queue_tick_dynamic Has 130-Line | `game/strategy/engine/productio` | Medium |
| CX-003 | project_path Threads 5 Mutable Variables | `game/strategy/services/fleet_n` | Medium |
| TC-002 | No Tests for Zero Production Rate in Pro | `game/strategy/engine/productio` | Simple |
| TC-004 | WarpJump Non-Dict Value Branch Untested | `game/strategy/services/ship_st` | Simple |

### Major (35)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-001 | Single Responsibility Violation - Functi | `game/strategy/engine/productio` | Medium |
| CQ-011 | Monolithic Accumulation Loop - 136 Lines | `game/strategy/services/ship_st` | Complex |
| DS-005 | Proposed `_accumulate_component_stats` d | `game/strategy/services/ship_st` | Medium |
| DS-017 | No proposed strategy addresses the real | `Unknown` | Medium |
| TC-003 | WARP Order Type Not Tested in project_pa | `game/strategy/services/fleet_n` | Medium |
| AR-03 | Implicit Dict Contract for Queue Items ( | `game/strategy/engine/productio` | Medium |
| AR-04 | 8-Parameter Method Signature | `game/strategy/engine/productio` | Simple |
| AR-05 | Fake Fleet Object in compute_path | `game/strategy/services/fleet_n` | Medium |
| AR-07 | Warp Jump Logic Embedded in Stats Calcul | `game/strategy/services/ship_st` | Medium |
| AR-08 | Excessive Exception Handling Breadth in | `game/strategy/systems/save_gam` | Simple |
| AR-18 | ProductionEngine Has No Dependency Injec | `game/strategy/engine/productio` | Medium |
| CQ-004 | Feature Envy - Excessive Manipulation of | `game/strategy/engine/productio` | Medium |
| CQ-012 | Open/Closed Violation - Adding Abilities | `game/strategy/services/ship_st` | Complex |
| CQ-013 | DRY Violation - Repeated Ability Process | `game/strategy/services/ship_st` | Medium |
| CQ-014 | Nested Conditional Complexity in WarpJum | `game/strategy/services/ship_st` | Simple |
| CQ-015 | Data Clump - Formula Context Passed to E | `game/strategy/services/ship_st` | Simple |
| CQ-019 | Excessive Exception Handling - 7 Separat | `game/strategy/services/save_ga` | Medium |
| CQ-020 | DRY Violation - Duplicate Error Handling | `game/strategy/services/save_ga` | Simple |
| CQ-025 | Mixed Abstraction Levels in Main Loop | `game/strategy/services/fleet_n` | Medium |
| CQ-026 | NavigationState Reconstruction Repeated | `game/strategy/services/fleet_n` | Simple |
| CX-004 | Duplicate Exception Handler Patterns in | `game/strategy/systems/save_gam` | Simple |
| CX-005 | Outer Exception Handler in load_game Is | `game/strategy/systems/save_gam` | Simple |
| CX-006 | ResourceConsumption Abilities Iterated T | `game/strategy/services/ship_st` | Medium |
| CX-007 | Dead Code Path in _process_queue_tick_dy | `game/strategy/engine/productio` | Simple |
| CX-009 | Action Order Handling Block is 32% of pr | `game/strategy/services/fleet_n` | Medium |
| DS-006 | WarpJump block is the highest-CC section | `game/strategy/services/ship_st` | Medium |
| DS-009 | CC is driven by repetitive exception han | `game/strategy/systems/save_gam` | Simple |
| DS-010 | Outer exception handlers (lines 213-221) | `game/strategy/systems/save_gam` | Simple |
| DS-013 | `_project_action_order` signature is sig | `game/strategy/services/fleet_n` | Medium |
| DS-014 | Inner while loop for action_time consump | `game/strategy/services/fleet_n` | Simple |
| TC-005 | Complex-Only Filter Path Not Directly Te | `game/strategy/engine/productio` | Simple |
| TC-006 | Relative Path Resolution Not Tested in l | `game/strategy/systems/save_gam` | Simple |
| TC-007 | Outer Exception Handlers in load_game Ne | `game/strategy/systems/save_gam` | Medium |
| TC-008 | No Test for Pathfinding Failure Mid-Proj | `game/strategy/services/fleet_n` | Medium |
| TC-010 | vehicle_classes Context Never Tested in | `game/strategy/services/ship_st` | Simple |

### Minor (37)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-02 | Private Attribute Access on Galaxy Objec | `game/strategy/services/fleet_n` | Medium |
| TC-001 | No Tests for Invalid Queue Items in Prod | `game/strategy/engine/productio` | Simple |
| AR-06 | Interleaved Validation and Mutation in P | `game/strategy/engine/productio` | Medium |
| CQ-005 | Inconsistent Error Handling - Mix of `re | `game/strategy/engine/productio` | Medium |
| CQ-021 | Redundant Outer Exception Handler Catche | `game/strategy/services/save_ga` | Simple |
| CX-008 | Warp Data Parsing Ternary Chain | `game/strategy/services/ship_st` | Simple |
| CX-010 | While Loop Condition in _process_queue_t | `game/strategy/engine/productio` | Simple |
| DS-001 | Proposed `_apply_production_progress` co | `game/strategy/engine/productio` | Simple |
| DS-007 | Policy pattern is overengineered for thi | `game/strategy/services/ship_st` | N |
| TC-009 | Production Engine Iteration Safety Limit | `game/strategy/engine/productio` | Medium |
| AR-10 | Redundant Completion Check in Production | `game/strategy/engine/productio` | Simple |
| AR-11 | Stats Calculator Fallback to expected_st | `game/strategy/services/ship_st` | Simple |
| AR-12 | Untyped `galaxy` Parameter Across All Fu | `Unknown` | Simple |
| AR-13 | Hardcoded Constants in Production Engine | `game/strategy/engine/productio` | Simple |
| CQ-006 | Narrative Comments Replace Readable Code | `game/strategy/engine/productio` | Simple |
| CQ-009 | Untyped `empire` and `galaxy` Parameters | `game/strategy/engine/productio` | Simple |
| CQ-016 | 9-Key Return Dictionary - Implicit Contr | `game/strategy/services/ship_st` | Medium |
| CQ-022 | Validation Logic Embedded in Loading Flo | `game/strategy/services/save_ga` | Simple |
| CQ-023 | Inconsistent Return Type Documentation | `game/strategy/services/save_ga` | Simple |
| CQ-027 | Inconsistent First-Order Progress Tracki | `game/strategy/services/fleet_n` | Medium |
| CQ-028 | Magic Number for Safety Limit Calculatio | `game/strategy/services/fleet_n` | Simple |
| CQ-029 | Untyped `galaxy` Parameter Across All 4 | `Unknown` | Simple |
| CX-011 | `is_first_order` Flag Pattern in project | `game/strategy/services/fleet_n` | Simple |
| CX-012 | Turn Advancement Logic Duplicated in pro | `game/strategy/services/fleet_n` | Simple |
| CX-013 | calculate_stats Has 8 Accumulator Variab | `game/strategy/services/ship_st` | Medium |
| CX-014 | load_game Missing Keys Validation is Rep | `game/strategy/systems/save_gam` | Simple |
| CX-015 | Epsilon Comparison in Completion Check | `game/strategy/engine/productio` | Simple |
| CX-016 | Compound Except Clause in load_game Oute | `game/strategy/systems/save_gam` | Simple |
| DS-002 | Free/zero-cost item completion path not | `game/strategy/engine/productio` | Simple |
| DS-003 | Lazy cost initialization fallback is a s | `game/strategy/engine/productio` | Simple |
| DS-015 | `_advance_tick` is too broad -- step exe | `game/strategy/services/fleet_n` | Simple |
| DS-016 | `first_order_progress` tracking adds acc | `game/strategy/services/fleet_n` | Simple |
| TC-011 | Epsilon Completion Check Not Specificall | `game/strategy/engine/productio` | Simple |
| TC-012 | turns_remaining UI Update Never Asserted | `game/strategy/engine/productio` | Simple |
| TC-013 | consumption_mult Modifier Not Tested in | `game/strategy/services/ship_st` | Simple |
| TC-014 | Max Iterations Safety in project_path Ne | `game/strategy/services/fleet_n` | Medium |
| TC-015 | Fleet with Path But No Orders Not Tested | `game/strategy/services/fleet_n` | Simple |

### Info (16)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-14 | Lazy Import Pattern Inconsistency | `game/strategy/engine/productio` | Simple |
| DS-008 | `_initialize_base_stats` extraction has | `game/strategy/services/ship_st` | Simple |
| AR-15 | SaveGameService is Well-Architected for | `game/strategy/systems/save_gam` | Simple |
| AR-16 | ShipStatsCalculator DI Pattern is Exempl | `game/strategy/services/ship_st` | N |
| AR-17 | FleetNavigationService Pure Function Arc | `game/strategy/services/fleet_n` | N |
| CQ-010 | `queue.pop(0)` is O(n) on Python Lists | `game/strategy/engine/productio` | Simple |
| CQ-018 | Expected Stats Fallback May Hide Missing | `game/strategy/services/ship_st` | Simple |
| CX-017 | calculate_stats Fallback to expected_sta | `game/strategy/services/ship_st` | Simple |
| CX-018 | _process_queue_tick_dynamic Has Extensiv | `game/strategy/engine/productio` | Simple |
| CX-019 | process_construction_tick Has Extensive | `game/strategy/engine/productio` | Simple |
| DS-004 | Orchestrator CC after proposed extractio | `game/strategy/engine/productio` | N |
| DS-012 | Overall strategy is sound | `game/strategy/systems/save_gam` | Simple |
| DS-018 | Implementation ordering recommendation | `Unknown` | N |
| TC-016 | calculate_stats Has Excellent Test Organ | `tests/unit/strategy/ship_stats` | N |
| TC-017 | load_game Tests Use Real Filesystem (Goo | `tests/unit/strategy/save_game_` | N |
| TC-018 | Integration Consistency Tests Provide St | `tests/integration/strategy/tes` | N |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Code Quality Analyst Report](findings/code_quality_analyst_report.md)
- [Complexity Analyst Report](findings/complexity_analyst_report.md)
- [Decomposition Strategist Report](findings/decomposition_strategist_report.md)
- [Test Coverage Analyst Report](findings/test_coverage_analyst_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 95 |
| Critical | 7 |
| Major | 35 |
| Minor | 37 |
| Info | 16 |
| Agents Used | 25 |

---
*Report generated: 2026-02-27 21:29*
