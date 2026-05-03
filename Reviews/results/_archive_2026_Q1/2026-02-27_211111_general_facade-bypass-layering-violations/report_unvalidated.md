# Review Report: 2026-02-27_211111_general_facade-bypass-layering-violations

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review — Architectural Layering Focus
- **Description:** Full UI layer scan for CQRS/facade bypass violations
- **Agents Used:** 3

## Executive Summary
- **Total Findings:** 58
- **Critical:** 14 | **Major:** 22 | **Minor:** 15 | **Info:** 7
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: FleetReportWindow directly mutates Fleet.remove_ship()
**ID:** AR-001
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_report_window.py:239-248`
**Effort:** Medium

**ID:** AR-001
**Location:** `game/ui/screens/fleet_report_window.py:239-248`
**Violation Type:** Direct Mutation
**Issue:** The `_on_remove_ship` method directly calls `self.fleet.remove_ship(ship)` to remove a ship from a fleet. This is a direct domain model mutation from the UI layer, completely bypassing the command pipeline.
**Impact:** State changes happen outside the command pipeline, making them invisible to validation, event logging, undo systems, and any other cross-cutting concerns. T...

---

### 2. CRITICAL: FleetReportWindow directly calls Empire.add_fleet()
**ID:** AR-002
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_report_window.py:247`
**Effort:** Medium

**ID:** AR-002
**Location:** `game/ui/screens/fleet_report_window.py:247`
**Violation Type:** Direct Mutation
**Issue:** After removing a ship, the code calls `self.empire.add_fleet(new_fleet)` to add a newly created fleet to the empire. This directly mutates the Empire domain object from the UI layer.
**Impact:** The empire's fleet list is modified outside of any command pipeline. No validation, no event logging, no way for game logic to react to the new fleet's creation.
**Recommendation:** Th...

---

### 3. CRITICAL: FleetReportWindow instantiates Fleet domain object
**ID:** AR-003
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_report_window.py:276-286`
**Effort:** Medium

**ID:** AR-003
**Location:** `game/ui/screens/fleet_report_window.py:276-286`
**Violation Type:** Domain Instantiation
**Issue:** The `_create_fleet_for_ships` method directly instantiates `Fleet` from `game.strategy.data.fleet`, calls `empire.get_next_fleet_id()`, and constructs a new domain object in the UI layer.
**Impact:** Domain object creation logic in the UI layer violates separation of concerns. Fleet ID generation, initialization, and registration should be handled by the strategy engi...

---

### 4. CRITICAL: FleetReportWindow bulk removes ships and creates fleet
**ID:** AR-004
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_report_window.py:250-274`
**Effort:** Medium

**ID:** AR-004
**Location:** `game/ui/screens/fleet_report_window.py:250-274`
**Violation Type:** Direct Mutation
**Issue:** `_on_remove_selected_ships` iterates through selected ships, calls `self.fleet.remove_ship(ship)` for each, then creates a new fleet and calls `self.empire.add_fleet()`. This is the multi-ship version of AR-001/AR-002/AR-003.
**Impact:** Multiple domain mutations performed directly from UI without command pipeline. Same issues as AR-001/002/003 but amplified by the batch n...

---

### 5. CRITICAL: FleetOrdersWindow directly mutates Fleet.orders list
**ID:** AR-005
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_orders_window.py:281-293`
**Effort:** Medium

**ID:** AR-005
**Location:** `game/ui/screens/fleet_orders_window.py:281-293`
**Violation Type:** Direct Mutation
**Issue:** The `move_order` method directly swaps items in `self.fleet.orders` list and directly sets `self.fleet.path = []`. This is a direct mutation of domain model internal state from the UI.
**Impact:** Order reordering bypasses the command pipeline entirely. Path invalidation is done ad-hoc in the UI rather than being handled by game logic.
**Recommendation:** Create `ReorderFl...

---

### 6. CRITICAL: FleetOrdersWindow directly deletes from Fleet.orders
**ID:** AR-006
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_orders_window.py:295-307`
**Effort:** Medium

**ID:** AR-006
**Location:** `game/ui/screens/fleet_orders_window.py:295-307`
**Violation Type:** Direct Mutation
**Issue:** The `delete_order` method directly calls `self.fleet.orders.pop(index)` and sets `self.fleet.path = []`. This removes an order from the domain model's internal list from the UI layer.
**Impact:** Order deletion bypasses validation, event logging, and any other command pipeline concerns. The undo stack is maintained in the UI rather than at the domain level.
**Recommendatio...

---

### 7. CRITICAL: FleetOrdersWindow directly inserts into Fleet.orders (undo)
**ID:** AR-007
**Agent:** Architecture Reviewer 1
**Location:** `game/ui/screens/fleet_orders_window.py:309-328`
**Effort:** Complex

**ID:** AR-007
**Location:** `game/ui/screens/fleet_orders_window.py:309-328`
**Violation Type:** Direct Mutation
**Issue:** The `undo_delete` method directly calls `self.fleet.orders.insert(original_index, order)` and sets `self.fleet.path = []`. This restores a previously deleted order by directly manipulating the domain model's internal list.
**Impact:** Undo functionality is implemented entirely in the UI layer by directly mutating domain state. No validation occurs, and the operation is inv...

---

### 8. CRITICAL: BuildQueueController directly mutates domain construction_queue lists
**ID:** AR2-001
**Agent:** Architecture Reviewer 2
**Location:** `game/ui/panels/build_queue_controller.py:413, 416, 450, 453, 491, 535, 538`
**Effort:** Complex

**ID:** AR2-001
**Location:** `game/ui/panels/build_queue_controller.py:413, 416, 450, 453, 491, 535, 538`
**Violation Type:** Direct Mutation
**Issue:** The `BuildQueueController` calls `.insert()` and `.append()` directly on `source.construction_queue` (a domain object's mutable list) in seven places across `_add_to_single_queue()`, `_add_item_with_target_planet()`, `_add_to_multiple_queues()`, and `_add_to_fallback()`. This bypasses the command pipeline entirely for build queue modifications....

---

### 9. CRITICAL: BuildQueueDragHandler directly pops items from domain construction_queue
**ID:** AR2-002
**Agent:** Architecture Reviewer 2
**Location:** `game/ui/panels/build_queue_drag_handler.py:182`
**Effort:** Complex

**ID:** AR2-002
**Location:** `game/ui/panels/build_queue_drag_handler.py:182`
**Violation Type:** Direct Mutation
**Issue:** In `handle_mouse_motion()`, the drag handler calls `construction_queue.pop(idx)` to remove an item from the domain object's construction queue during a drag-reorder operation. This is a direct mutation of game state from a UI input handler.
**Impact:** Queue items are removed without any command validation. If the drag is canceled (dropped outside), the item is silently l...

---

### 10. CRITICAL: BuildQueueController directly accesses Galaxy and Empire domain objects
**ID:** AR2-003
**Agent:** Architecture Reviewer 2
**Location:** `game/ui/panels/build_queue_controller.py:313-316, 344-349, 376-379`
**Effort:** Medium

**ID:** AR2-003
**Location:** `game/ui/panels/build_queue_controller.py:313-316, 344-349, 376-379`
**Violation Type:** Direct Property Access + Command Bypass
**Issue:** The controller holds direct references to `Galaxy` and `Empire` domain objects (injected via constructor). It calls `self.galaxy.get_planets_at_global_hex(self.hex_coord)` and filters planets by `p.owner_id == self.empire.id` in three places (`_needs_planet_selection`, `_get_target_planet_id`, `_add_to_single_queue`). This gives...

---


## Findings by Severity

### Critical (14)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | FleetReportWindow directly mutates Fleet | `game/ui/screens/fleet_report_w` | Medium |
| AR-002 | FleetReportWindow directly calls Empire. | `game/ui/screens/fleet_report_w` | Medium |
| AR-003 | FleetReportWindow instantiates Fleet dom | `game/ui/screens/fleet_report_w` | Medium |
| AR-004 | FleetReportWindow bulk removes ships and | `game/ui/screens/fleet_report_w` | Medium |
| AR-005 | FleetOrdersWindow directly mutates Fleet | `game/ui/screens/fleet_orders_w` | Medium |
| AR-006 | FleetOrdersWindow directly deletes from  | `game/ui/screens/fleet_orders_w` | Medium |
| AR-007 | FleetOrdersWindow directly inserts into  | `game/ui/screens/fleet_orders_w` | Complex |
| AR2-001 | BuildQueueController directly mutates do | `game/ui/panels/build_queue_con` | Complex |
| AR2-002 | BuildQueueDragHandler directly pops item | `game/ui/panels/build_queue_dra` | Complex |
| AR2-003 | BuildQueueController directly accesses G | `game/ui/panels/build_queue_con` | Medium |
| CQ-001 | Fleet Splitting Logic Lives Entirely in  | `game/ui/screens/fleet_report_w` | Complex |
| CQ-002 | Direct Order Array Mutation Bypasses Com | `game/ui/screens/fleet_orders_w` | Complex |
| CQ-003 | Direct Path State Mutation from UI Layer | `game/ui/screens/fleet_orders_w` | Medium |
| CQ-004 | Domain Object Instantiation in UI Layer | `game/ui/screens/fleet_report_w` | Medium |

### Major (22)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-008 | FleetOrdersWindow reads Fleet.orders dir | `game/ui/screens/fleet_orders_w` | Medium |
| AR-009 | FleetOrdersWindow accesses Fleet.constru | `game/ui/screens/fleet_orders_w` | Simple |
| AR-010 | FleetReportWindow holds direct reference | `game/ui/screens/fleet_report_w` | Complex |
| AR-011 | FleetReportWindow reads Fleet.ships dire | `game/ui/screens/fleet_report_w` | Medium |
| AR-012 | StrategyWindowManager passes domain obje | `game/ui/screens/strategy_windo` | Complex |
| AR-013 | StrategyWindowManager dispatches command | `game/ui/screens/strategy_windo` | Simple |
| AR-014 | EmpireBuildQueueWindow directly appends  | `game/ui/screens/empire_build_q` | Medium |
| AR-015 | BuildQueueScreen directly pops from cons | `game/ui/screens/build_queue_sc` | Medium |
| AR2-004 | PlanetReportPanel holds and operates on  | `game/ui/panels/planet_report_p` | Complex |
| AR2-005 | SystemTreePanel receives and stores raw  | `game/ui/panels/system_tree_pan` | Complex |
| AR2-006 | BuildQueuePortraitLoader accesses sessio | `game/ui/panels/build_queue_por` | Simple |
| AR2-007 | ResearchControlPanel directly mutates Re | `game/ui/research/research_cont` | Medium |
| AR2-008 | ResearchTreeScene directly instantiates  | `game/ui/research/research_scen` | Complex |
| AR2-009 | compute_planet_production accesses domai | `game/ui/panels/planet_report_p` | Medium |
| AR2-010 | ShipDetailPanel operates on raw ShipInst | `game/ui/panels/ship_detail_pan` | Medium |
| CQ-005 | Backward Compatibility Fallback Violates | `game/ui/screens/fleet_orders_w` | Simple |
| CQ-006 | Window Manager Passes Live Domain Object | `game/ui/screens/strategy_windo` | Complex |
| CQ-007 | No Empty-Fleet Guard in Ship Removal | `game/ui/screens/fleet_report_w` | Simple |
| CQ-008 | 63 Lines of Dead Comments Left in Produc | `game/ui/screens/fleet_orders_w` | Simple |
| CQ-009 | FleetReportWindow Holds Mutable Referenc | `game/ui/screens/fleet_report_w` | Complex |
| CQ-010 | Strategy Screen Exposes Session Internal | `game/ui/screens/strategy_scree` | Complex |
| CQ-011 | Window Manager Bypasses Facade for Comma | `game/ui/screens/strategy_windo` | Simple |

### Minor (15)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-016 | StrategyScreen exposes session propertie | `game/ui/screens/strategy_scree` | Complex |
| AR-017 | StrategyScreen.on_ui_selection works wit | `game/ui/screens/strategy_scree` | Complex |
| AR-018 | StrategyScreen.on_design_click passes se | `game/ui/screens/strategy_scree` | Medium |
| AR-019 | FleetOrdersWindow backward-compat fallba | `game/ui/screens/fleet_orders_w` | Simple |
| AR-020 | BuildQueueListWindow directly accesses E | `game/ui/screens/build_queue_li` | Medium |
| AR-021 | PlanetListWindow directly accesses Galax | `game/ui/screens/planet_list_wi` | Complex |
| AR-022 | EmpirePanelWindow directly accesses Empi | `game/ui/screens/empire_panel_w` | Medium |
| AR2-011 | ship_stats_renderer accesses ICombatShip | `game/ui/panels/ship_stats_rend` | N |
| AR2-012 | DesignStatsPanel and DesignReportPanel a | `game/ui/panels/design_stats_pa` | Medium |
| AR2-013 | ComponentModifierGridPanel and ModifierI | `game/ui/panels/component_modif` | Medium |
| AR2-014 | strategy_widgets.py accepts raw domain o | `game/ui/panels/strategy_widget` | Simple |
| CQ-012 | Inconsistent Error Handling in Ship Remo | `game/ui/screens/fleet_report_w` | Simple |
| CQ-013 | Magic Number for Fleet Speed in UI Code | `game/ui/screens/fleet_report_w` | Simple |
| CQ-014 | Stale Order Count Detection Misses Conte | `game/ui/screens/fleet_orders_w` | Simple |
| CQ-015 | FleetOrdersWindow Stores Direct Referenc | `game/ui/screens/fleet_orders_w` | Simple |

### Info (7)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
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
| Total Findings | 58 |
| Critical | 14 |
| Major | 22 |
| Minor | 15 |
| Info | 7 |
| Agents Used | 3 |

---
*Report generated: 2026-02-27 21:21*
