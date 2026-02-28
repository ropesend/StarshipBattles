# Review Report: 2026-02-27_211111_general_facade-bypass-layering-violations

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review — Architectural Layering Focus
- **Description:** Full UI layer scan for CQRS/facade bypass violations
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 54
- **Critical:** 10 | **Major:** 22 | **Minor:** 14 | **Info:** 8
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 58
- **Confirmed:** 54 | **Downgraded:** 9 | **Rejected:** 4
- **Rejection Rate:** 6.9%
- **Findings Without Verdict:** 0

## Priority Findings (Top 10)

### 1. CRITICAL: FleetReportWindow directly mutates Fleet
**ID:** AR-001
**Agent:** Validated
**Location:** `game/ui/screens/fleet_report_w`
**Effort:** Medium

**Location:** `game/ui/screens/fleet_report_w`

---

### 2. CRITICAL: FleetReportWindow directly calls Empire.
**ID:** AR-002
**Agent:** Validated
**Location:** `game/ui/screens/fleet_report_w`
**Effort:** Medium

**Location:** `game/ui/screens/fleet_report_w`

---

### 3. CRITICAL: FleetReportWindow instantiates Fleet dom
**ID:** AR-003
**Agent:** Validated
**Location:** `game/ui/screens/fleet_report_w`
**Effort:** Medium

**Location:** `game/ui/screens/fleet_report_w`

---

### 4. CRITICAL: FleetOrdersWindow directly mutates Fleet
**ID:** AR-005
**Agent:** Validated
**Location:** `game/ui/screens/fleet_orders_w`
**Effort:** Medium

**Location:** `game/ui/screens/fleet_orders_w`

---

### 5. CRITICAL: FleetOrdersWindow directly deletes from
**ID:** AR-006
**Agent:** Validated
**Location:** `game/ui/screens/fleet_orders_w`
**Effort:** Medium

**Location:** `game/ui/screens/fleet_orders_w`

---

### 6. CRITICAL: FleetOrdersWindow directly inserts into
**ID:** AR-007
**Agent:** Validated
**Location:** `game/ui/screens/fleet_orders_w`
**Effort:** Complex

**Location:** `game/ui/screens/fleet_orders_w`

---

### 7. CRITICAL: BuildQueueController directly mutates do
**ID:** AR2-001
**Agent:** Validated
**Location:** `game/ui/panels/build_queue_con`
**Effort:** Complex

**Location:** `game/ui/panels/build_queue_con`

---

### 8. CRITICAL: BuildQueueDragHandler directly pops item
**ID:** AR2-002
**Agent:** Validated
**Location:** `game/ui/panels/build_queue_dra`
**Effort:** Complex

**Location:** `game/ui/panels/build_queue_dra`

---

### 9. CRITICAL: Fleet Splitting Logic Lives Entirely in
**ID:** CQ-001
**Agent:** Validated
**Location:** `game/ui/screens/fleet_report_w`
**Effort:** Complex

**Location:** `game/ui/screens/fleet_report_w`

---

### 10. CRITICAL: Direct Order Array Mutation Bypasses Com
**ID:** CQ-002
**Agent:** Validated
**Location:** `game/ui/screens/fleet_orders_w`
**Effort:** Complex

**Location:** `game/ui/screens/fleet_orders_w`

---


## Findings by Severity

### Critical (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | FleetReportWindow directly mutates Fleet | `game/ui/screens/fleet_report_w` | Medium |
| AR-002 | FleetReportWindow directly calls Empire. | `game/ui/screens/fleet_report_w` | Medium |
| AR-003 | FleetReportWindow instantiates Fleet dom | `game/ui/screens/fleet_report_w` | Medium |
| AR-005 | FleetOrdersWindow directly mutates Fleet | `game/ui/screens/fleet_orders_w` | Medium |
| AR-006 | FleetOrdersWindow directly deletes from | `game/ui/screens/fleet_orders_w` | Medium |
| AR-007 | FleetOrdersWindow directly inserts into | `game/ui/screens/fleet_orders_w` | Complex |
| AR2-001 | BuildQueueController directly mutates do | `game/ui/panels/build_queue_con` | Complex |
| AR2-002 | BuildQueueDragHandler directly pops item | `game/ui/panels/build_queue_dra` | Complex |
| CQ-001 | Fleet Splitting Logic Lives Entirely in | `game/ui/screens/fleet_report_w` | Complex |
| CQ-002 | Direct Order Array Mutation Bypasses Com | `game/ui/screens/fleet_orders_w` | Complex |

### Major (22)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-004 | FleetReportWindow bulk removes ships and | `game/ui/screens/fleet_report_w` | Medium |
| AR2-003 | BuildQueueController directly accesses G | `game/ui/panels/build_queue_con` | Medium |
| CQ-003 | Direct Path State Mutation from UI Layer | `game/ui/screens/fleet_orders_w` | Medium |
| CQ-004 | Domain Object Instantiation in UI Layer | `game/ui/screens/fleet_report_w` | Medium |
| AR-008 | FleetOrdersWindow reads Fleet.orders dir | `game/ui/screens/fleet_orders_w` | Medium |
| AR-009 | FleetOrdersWindow accesses Fleet.constru | `game/ui/screens/fleet_orders_w` | Simple |
| AR-010 | FleetReportWindow holds direct reference | `game/ui/screens/fleet_report_w` | Complex |
| AR-011 | FleetReportWindow reads Fleet.ships dire | `game/ui/screens/fleet_report_w` | Medium |
| AR-012 | StrategyWindowManager passes domain obje | `game/ui/screens/strategy_windo` | Complex |
| AR-013 | StrategyWindowManager dispatches command | `game/ui/screens/strategy_windo` | Simple |
| AR-014 | EmpireBuildQueueWindow directly appends | `game/ui/screens/empire_build_q` | Medium |
| AR-015 | BuildQueueScreen directly pops from cons | `game/ui/screens/build_queue_sc` | Medium |
| AR2-004 | PlanetReportPanel holds and operates on | `game/ui/panels/planet_report_p` | Complex |
| AR2-005 | SystemTreePanel receives and stores raw | `game/ui/panels/system_tree_pan` | Complex |
| AR2-007 | ResearchControlPanel directly mutates Re | `game/ui/research/research_cont` | Medium |
| AR2-008 | ResearchTreeScene directly instantiates | `game/ui/research/research_scen` | Complex |
| CQ-005 | Backward Compatibility Fallback Violates | `game/ui/screens/fleet_orders_w` | Simple |
| CQ-006 | Window Manager Passes Live Domain Object | `game/ui/screens/strategy_windo` | Complex |
| CQ-007 | No Empty-Fleet Guard in Ship Removal | `game/ui/screens/fleet_report_w` | Simple |
| CQ-009 | FleetReportWindow Holds Mutable Referenc | `game/ui/screens/fleet_report_w` | Complex |
| CQ-010 | Strategy Screen Exposes Session Internal | `game/ui/screens/strategy_scree` | Complex |
| CQ-011 | Window Manager Bypasses Facade for Comma | `game/ui/screens/strategy_windo` | Simple |

### Minor (14)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR2-006 | BuildQueuePortraitLoader accesses sessio | `game/ui/panels/build_queue_por` | Simple |
| AR2-009 | compute_planet_production accesses domai | `game/ui/panels/planet_report_p` | Medium |
| AR2-010 | ShipDetailPanel operates on raw ShipInst | `game/ui/panels/ship_detail_pan` | Medium |
| CQ-008 | 63 Lines of Dead Comments Left in Produc | `game/ui/screens/fleet_orders_w` | Simple |
| AR-016 | StrategyScreen exposes session propertie | `game/ui/screens/strategy_scree` | Complex |
| AR-017 | StrategyScreen.on_ui_selection works wit | `game/ui/screens/strategy_scree` | Complex |
| AR-018 | StrategyScreen.on_design_click passes se | `game/ui/screens/strategy_scree` | Medium |
| AR-019 | FleetOrdersWindow backward-compat fallba | `game/ui/screens/fleet_orders_w` | Simple |
| AR-020 | BuildQueueListWindow directly accesses E | `game/ui/screens/build_queue_li` | Medium |
| AR-021 | PlanetListWindow directly accesses Galax | `game/ui/screens/planet_list_wi` | Complex |
| CQ-012 | Inconsistent Error Handling in Ship Remo | `game/ui/screens/fleet_report_w` | Simple |
| CQ-013 | Magic Number for Fleet Speed in UI Code | `game/ui/screens/fleet_report_w` | Simple |
| CQ-014 | Stale Order Count Detection Misses Conte | `game/ui/screens/fleet_orders_w` | Simple |
| CQ-015 | FleetOrdersWindow Stores Direct Referenc | `game/ui/screens/fleet_orders_w` | Simple |

### Info (8)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-022 | EmpirePanelWindow directly accesses Empi | `game/ui/screens/empire_panel_w` | Medium |
| AR-023 | SystemSelectionWindow receives domain ob | `game/ui/screens/system_selecti` | Simple |
| AR-024 | DesignSelectorWindow and SaveSelectionWi | `game/ui/screens/design_selecto` | N |
| AR2-015 | BattleOrchestrator cross-layer imports a | `game/ui/orchestration/battle_o` | N |
| AR2-016 | EmpireTreasuryPanel uses EmpireEconomySn | `game/ui/panels/empire_treasury` | N |
| CQ-016 | PROJ-207 Partial Migration Pattern | `game/ui/screens/fleet_orders_w` | Medium |
| CQ-017 | Window Manager Has Scene Reference Creat | `game/ui/screens/strategy_windo` | Medium |
| CQ-018 | Strategy Screen Uses Facade Inconsistent | `game/ui/screens/strategy_scree` | N |


## Agent Reports

- [Architecture Reviewer 1 Report](findings/architecture_reviewer_1_report.md)
- [Architecture Reviewer 2 Report](findings/architecture_reviewer_2_report.md)
- [Code Quality Analyst Report](findings/code_quality_analyst_report.md)
- [Command Gap Analyst Report](findings/command_gap_analyst_report.md)
- [Dto Coverage Analyst Report](findings/dto_coverage_analyst_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 54 |
| Critical | 10 |
| Major | 22 |
| Minor | 14 |
| Info | 8 |
| Agents Used | 25 |

---
*Report generated: 2026-02-27 21:26*
