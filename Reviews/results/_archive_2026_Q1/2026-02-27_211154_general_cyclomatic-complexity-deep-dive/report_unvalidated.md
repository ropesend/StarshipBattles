# Review Report: 2026-02-27_211154_general_cyclomatic-complexity-deep-dive

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review (Complexity Focus)
- **Description:** 
- **Agents Used:** 5

## Executive Summary
- **Total Findings:** 103
- **Critical:** 14 | **Major:** 39 | **Minor:** 34 | **Info:** 16
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Latent Bug in Production Cost Fallback
**ID:** AR-01
**Agent:** Architecture Reviewer
**Location:** `game/strategy/engine/production_engine.py:255`
**Effort:** Medium

**ID:** AR-01
**Location:** `game/strategy/engine/production_engine.py:255`
**Issue:** When `total_cost` is missing from a queue item, `self._calculate_design_cost(item)` is called, passing the queue item dict where the method expects a `design_data` dict (with `layers` containing components). A queue item has `design_id`, `type`, `turns_remaining` -- it does not have `layers`. This means `DesignCostCalculator.calculate_total_cost()` would iterate an empty `layers` dict and return `{}`, making t...

---

### 2. CRITICAL: Private Attribute Access on Galaxy Object
**ID:** AR-02
**Agent:** Architecture Reviewer
**Location:** `game/strategy/services/fleet_navigation_service.py:272`
**Effort:** Medium

**ID:** AR-02
**Location:** `game/strategy/services/fleet_navigation_service.py:272`
**Issue:** `_resolve_warp_exit` accesses `galaxy._global_hex_warp_points` -- a private attribute (underscore-prefixed). This creates tight coupling between FleetNavigationService and Galaxy's internal implementation. Any refactoring of Galaxy's warp point storage would break this service.
**Impact:** Fragile coupling that violates encapsulation. The Galaxy class could not safely refactor its warp point index wit...

---

### 3. CRITICAL: Single Responsibility Violation - Function Does 5+ Distinct Jobs
**ID:** CQ-001
**Agent:** Code Quality Analyst
**Location:** `game/strategy/engine/production_engine.py:177-351`
**Effort:** Medium

**ID:** CQ-001
**Location:** `game/strategy/engine/production_engine.py:177-351`
**Issue:** This function handles (1) queue item validation, (2) fleet location constraints, (3) cost initialization fallback, (4) remaining cost calculation, (5) limiting resource/time calculation, (6) per-resource consumption calculation, (7) affordability checks, (8) resource mutation on the empire, (9) UI turns_remaining estimation, and (10) completion detection with delegation. These are at least 5 distinct resp...

---

### 4. CRITICAL: Defensive Code Masking Bugs - Silent `pass` After Fallback
**ID:** CQ-002
**Agent:** Code Quality Analyst
**Location:** `game/strategy/engine/production_engine.py:253-260`
**Effort:** Simple

**ID:** CQ-002
**Location:** `game/strategy/engine/production_engine.py:253-260`
**Issue:** When `total_cost` is missing from a queue item, the code attempts `self._calculate_design_cost(item)` but then immediately follows with `pass`. The comment says "Should have been set by controller, but safety fallback" and "we can assume if it's missing, we can't process it accurately yet." The `_calculate_design_cost` expects `design_data` (a full design dict with layers), not a queue item dict. This fal...

---

### 5. CRITICAL: Monolithic Accumulation Loop - 136 Lines of Sequential Ability Processing
**ID:** CQ-011
**Agent:** Code Quality Analyst
**Location:** `game/strategy/services/ship_stats_calculator.py:161-285`
**Effort:** Complex

**ID:** CQ-011
**Location:** `game/strategy/services/ship_stats_calculator.py:161-285`
**Issue:** The main component iteration loop (lines 161-285) processes 8 different ability types sequentially: mass, HP, ResourceStorage, CargoStorage, StrategicMovement, ResourceConsumption, WarpJump, and warp resource costs. Each ability type has its own block of 5-20 lines with similar patterns (get ability data, evaluate formula, apply multiplier, accumulate). This violates Single Responsibility -- the fun...

---

### 6. CRITICAL: Warp Jump Handling is Highest CC Driver in calculate_stats But Not Specifically Targeted
**ID:** CX-001
**Agent:** Complexity Analyst
**Location:** `game/strategy/services/ship_stats_calculator.py:252-284`
**Effort:** Medium

**ID:** CX-001
**Location:** `game/strategy/services/ship_stats_calculator.py:252-284`
**Issue:** The warp jump handling block contributes 8 CC points (31% of the function's complexity) through nested type checks, effectiveness gates, dual iteration of ResourceConsumption abilities, and a particularly ugly ternary chain for warp data parsing. The proposed decomposition's `_accumulate_component_stats` would absorb this complexity wholesale without reducing it.
**Impact:** The proposed refactor wo...

---

### 7. CRITICAL: _process_queue_tick_dynamic Has 130-Line While Loop Body With 6 Mutable Variables
**ID:** CX-002
**Agent:** Complexity Analyst
**Location:** `game/strategy/engine/production_engine.py:221-350`
**Effort:** Medium

**ID:** CX-002
**Location:** `game/strategy/engine/production_engine.py:221-350`
**Issue:** The while loop body spans 130 lines and mutates `tick_capacity`, `item['resources_consumed']`, `item['turns_remaining']`, `remaining_cost`, `cost_this_step`, and calls `empire.consume_resources()`. The proposed decomposition covers only 52% of the CC drivers, leaving the completion check (4 CC) and cost initialization (4 CC) in the orchestrator.
**Impact:** After the proposed 3 extractions, the residual f...

---

### 8. CRITICAL: project_path Threads 5 Mutable Variables Through Nested Loops
**ID:** CX-003
**Agent:** Complexity Analyst
**Location:** `game/strategy/services/fleet_navigation_service.py:439-562`
**Effort:** Medium

**ID:** CX-003
**Location:** `game/strategy/services/fleet_navigation_service.py:439-562`
**Issue:** The function manually threads `state`, `moves_left_in_turn`, `current_turn`, `is_first_order`, and `first_order_progress` through a while loop with an inner while loop for action time. The turn-advancement logic is duplicated at lines 486-488 and 558-560.
**Impact:** High cognitive complexity. The interleaving of action-order handling and movement-order handling in the same loop body makes it ver...

---

### 9. CRITICAL: Proposed `_accumulate_component_stats` does not actually decompose
**ID:** DS-005
**Agent:** Decomposition Strategist
**Location:** `game/strategy/services/ship_stats_calculator.py:161-284`
**Effort:** Medium

**ID:** DS-005
**Location:** `game/strategy/services/ship_stats_calculator.py:161-284`
**Issue:** The proposed extraction `_accumulate_component_stats` would contain nearly all the cyclomatic complexity (CC ~20 of 26). It moves the code into a new method but does not reduce the complexity of any single function. The proposed signature `(components, modifiers, damage)` is also incomplete -- it's missing formula_context, component_toggles, modifier_registry, and all 8 accumulators.
**Impact:** Imp...

---

### 10. CRITICAL: No proposed strategy addresses the real CC driver: nested loops with early returns
**ID:** DS-017
**Agent:** Decomposition Strategist
**Location:** `Unknown`
**Effort:** Medium

**ID:** DS-017
**Location:** All four functions
**Issue:** Three of the four functions (production_engine, ship_stats_calculator, fleet_navigation_service) share a pattern: a main loop with multiple conditional branches that contain `return` or `break` statements, plus nested inner loops. The proposed extractions generally try to extract the loop body into a single large method, which does not decompose the nesting. The most effective decomposition pattern for nested-loop-with-early-return code ...

---


## Findings by Severity

### Critical (14)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-01 | Latent Bug in Production Cost Fallback | `game/strategy/engine/productio` | Medium |
| AR-02 | Private Attribute Access on Galaxy Objec | `game/strategy/services/fleet_n` | Medium |
| CQ-001 | Single Responsibility Violation - Functi | `game/strategy/engine/productio` | Medium |
| CQ-002 | Defensive Code Masking Bugs - Silent `pa | `game/strategy/engine/productio` | Simple |
| CQ-011 | Monolithic Accumulation Loop - 136 Lines | `game/strategy/services/ship_st` | Complex |
| CX-001 | Warp Jump Handling is Highest CC Driver  | `game/strategy/services/ship_st` | Medium |
| CX-002 | _process_queue_tick_dynamic Has 130-Line | `game/strategy/engine/productio` | Medium |
| CX-003 | project_path Threads 5 Mutable Variables | `game/strategy/services/fleet_n` | Medium |
| DS-005 | Proposed `_accumulate_component_stats` d | `game/strategy/services/ship_st` | Medium |
| DS-017 | No proposed strategy addresses the real  | `Unknown` | Medium |
| TC-001 | No Tests for Invalid Queue Items in Prod | `game/strategy/engine/productio` | Simple |
| TC-002 | No Tests for Zero Production Rate in Pro | `game/strategy/engine/productio` | Simple |
| TC-003 | WARP Order Type Not Tested in project_pa | `game/strategy/services/fleet_n` | Medium |
| TC-004 | WarpJump Non-Dict Value Branch Untested  | `game/strategy/services/ship_st` | Simple |

### Major (39)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-03 | Implicit Dict Contract for Queue Items ( | `game/strategy/engine/productio` | Medium |
| AR-04 | 8-Parameter Method Signature | `game/strategy/engine/productio` | Simple |
| AR-05 | Fake Fleet Object in compute_path | `game/strategy/services/fleet_n` | Medium |
| AR-06 | Interleaved Validation and Mutation in P | `game/strategy/engine/productio` | Medium |
| AR-07 | Warp Jump Logic Embedded in Stats Calcul | `game/strategy/services/ship_st` | Medium |
| AR-08 | Excessive Exception Handling Breadth in  | `game/strategy/systems/save_gam` | Simple |
| AR-18 | ProductionEngine Has No Dependency Injec | `game/strategy/engine/productio` | Medium |
| CQ-003 | Magic Numbers Throughout | `game/strategy/engine/productio` | Simple |
| CQ-004 | Feature Envy - Excessive Manipulation of | `game/strategy/engine/productio` | Medium |
| CQ-005 | Inconsistent Error Handling - Mix of `re | `game/strategy/engine/productio` | Medium |
| CQ-012 | Open/Closed Violation - Adding Abilities | `game/strategy/services/ship_st` | Complex |
| CQ-013 | DRY Violation - Repeated Ability Process | `game/strategy/services/ship_st` | Medium |
| CQ-014 | Nested Conditional Complexity in WarpJum | `game/strategy/services/ship_st` | Simple |
| CQ-015 | Data Clump - Formula Context Passed to E | `game/strategy/services/ship_st` | Simple |
| CQ-019 | Excessive Exception Handling - 7 Separat | `game/strategy/services/save_ga` | Medium |
| CQ-020 | DRY Violation - Duplicate Error Handling | `game/strategy/services/save_ga` | Simple |
| CQ-021 | Redundant Outer Exception Handler Catche | `game/strategy/services/save_ga` | Simple |
| CQ-025 | Mixed Abstraction Levels in Main Loop | `game/strategy/services/fleet_n` | Medium |
| CQ-026 | NavigationState Reconstruction Repeated  | `game/strategy/services/fleet_n` | Simple |
| CX-004 | Duplicate Exception Handler Patterns in  | `game/strategy/systems/save_gam` | Simple |
| CX-005 | Outer Exception Handler in load_game Is  | `game/strategy/systems/save_gam` | Simple |
| CX-006 | ResourceConsumption Abilities Iterated T | `game/strategy/services/ship_st` | Medium |
| CX-007 | Dead Code Path in _process_queue_tick_dy | `game/strategy/engine/productio` | Simple |
| CX-008 | Warp Data Parsing Ternary Chain | `game/strategy/services/ship_st` | Simple |
| CX-009 | Action Order Handling Block is 32% of pr | `game/strategy/services/fleet_n` | Medium |
| CX-010 | While Loop Condition in _process_queue_t | `game/strategy/engine/productio` | Simple |
| DS-001 | Proposed `_apply_production_progress` co | `game/strategy/engine/productio` | Simple |
| DS-006 | WarpJump block is the highest-CC section | `game/strategy/services/ship_st` | Medium |
| DS-007 | Policy pattern is overengineered for thi | `game/strategy/services/ship_st` | N |
| DS-009 | CC is driven by repetitive exception han | `game/strategy/systems/save_gam` | Simple |
| DS-010 | Outer exception handlers (lines 213-221) | `game/strategy/systems/save_gam` | Simple |
| DS-013 | `_project_action_order` signature is sig | `game/strategy/services/fleet_n` | Medium |
| DS-014 | Inner while loop for action_time consump | `game/strategy/services/fleet_n` | Simple |
| TC-005 | Complex-Only Filter Path Not Directly Te | `game/strategy/engine/productio` | Simple |
| TC-006 | Relative Path Resolution Not Tested in l | `game/strategy/systems/save_gam` | Simple |
| TC-007 | Outer Exception Handlers in load_game Ne | `game/strategy/systems/save_gam` | Medium |
| TC-008 | No Test for Pathfinding Failure Mid-Proj | `game/strategy/services/fleet_n` | Medium |
| TC-009 | Production Engine Iteration Safety Limit | `game/strategy/engine/productio` | Medium |
| TC-010 | vehicle_classes Context Never Tested in  | `game/strategy/services/ship_st` | Simple |

### Minor (34)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-09 | NavigationState Missing execution_progre | `game/strategy/services/fleet_n` | Simple |
| AR-10 | Redundant Completion Check in Production | `game/strategy/engine/productio` | Simple |
| AR-11 | Stats Calculator Fallback to expected_st | `game/strategy/services/ship_st` | Simple |
| AR-12 | Untyped `galaxy` Parameter Across All Fu | `Unknown` | Simple |
| AR-13 | Hardcoded Constants in Production Engine | `game/strategy/engine/productio` | Simple |
| AR-14 | Lazy Import Pattern Inconsistency | `game/strategy/engine/productio` | Simple |
| CQ-006 | Narrative Comments Replace Readable Code | `game/strategy/engine/productio` | Simple |
| CQ-007 | Long Parameter List (8 Parameters) | `game/strategy/engine/productio` | Medium |
| CQ-008 | `process_construction_tick` Contains Str | `game/strategy/engine/productio` | Simple |
| CQ-009 | Untyped `empire` and `galaxy` Parameters | `game/strategy/engine/productio` | Simple |
| CQ-016 | 9-Key Return Dictionary - Implicit Contr | `game/strategy/services/ship_st` | Medium |
| CQ-017 | Inconsistent Static vs Instance Method U | `game/strategy/services/ship_st` | Simple |
| CQ-022 | Validation Logic Embedded in Loading Flo | `game/strategy/services/save_ga` | Simple |
| CQ-023 | Inconsistent Return Type Documentation | `game/strategy/services/save_ga` | Simple |
| CQ-027 | Inconsistent First-Order Progress Tracki | `game/strategy/services/fleet_n` | Medium |
| CQ-028 | Magic Number for Safety Limit Calculatio | `game/strategy/services/fleet_n` | Simple |
| CQ-029 | Untyped `galaxy` Parameter Across All 4  | `Unknown` | Simple |
| CX-011 | `is_first_order` Flag Pattern in project | `game/strategy/services/fleet_n` | Simple |
| CX-012 | Turn Advancement Logic Duplicated in pro | `game/strategy/services/fleet_n` | Simple |
| CX-013 | calculate_stats Has 8 Accumulator Variab | `game/strategy/services/ship_st` | Medium |
| CX-014 | load_game Missing Keys Validation is Rep | `game/strategy/systems/save_gam` | Simple |
| CX-015 | Epsilon Comparison in Completion Check | `game/strategy/engine/productio` | Simple |
| CX-016 | Compound Except Clause in load_game Oute | `game/strategy/systems/save_gam` | Simple |
| DS-002 | Free/zero-cost item completion path not  | `game/strategy/engine/productio` | Simple |
| DS-003 | Lazy cost initialization fallback is a s | `game/strategy/engine/productio` | Simple |
| DS-008 | `_initialize_base_stats` extraction has  | `game/strategy/services/ship_st` | Simple |
| DS-011 | Turn number resolution should be in `_lo | `game/strategy/systems/save_gam` | Simple |
| DS-015 | `_advance_tick` is too broad -- step exe | `game/strategy/services/fleet_n` | Simple |
| DS-016 | `first_order_progress` tracking adds acc | `game/strategy/services/fleet_n` | Simple |
| TC-011 | Epsilon Completion Check Not Specificall | `game/strategy/engine/productio` | Simple |
| TC-012 | turns_remaining UI Update Never Asserted | `game/strategy/engine/productio` | Simple |
| TC-013 | consumption_mult Modifier Not Tested in  | `game/strategy/services/ship_st` | Simple |
| TC-014 | Max Iterations Safety in project_path Ne | `game/strategy/services/fleet_n` | Medium |
| TC-015 | Fleet with Path But No Orders Not Tested | `game/strategy/services/fleet_n` | Simple |

### Info (16)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-15 | SaveGameService is Well-Architected for  | `game/strategy/systems/save_gam` | Simple |
| AR-16 | ShipStatsCalculator DI Pattern is Exempl | `game/strategy/services/ship_st` | N |
| AR-17 | FleetNavigationService Pure Function Arc | `game/strategy/services/fleet_n` | N |
| CQ-010 | `queue.pop(0)` is O(n) on Python Lists | `game/strategy/engine/productio` | Simple |
| CQ-018 | Expected Stats Fallback May Hide Missing | `game/strategy/services/ship_st` | Simple |
| CQ-024 | Static Method Could Benefit from Instanc | `game/strategy/services/save_ga` | Medium |
| CQ-030 | Consistent Use of Dict Returns Instead o | `production_engine.py` | Medium |
| CX-017 | calculate_stats Fallback to expected_sta | `game/strategy/services/ship_st` | Simple |
| CX-018 | _process_queue_tick_dynamic Has Extensiv | `game/strategy/engine/productio` | Simple |
| CX-019 | process_construction_tick Has Extensive  | `game/strategy/engine/productio` | Simple |
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
| Total Findings | 103 |
| Critical | 14 |
| Major | 39 |
| Minor | 34 |
| Info | 16 |
| Agents Used | 5 |

---
*Report generated: 2026-02-27 21:21*
