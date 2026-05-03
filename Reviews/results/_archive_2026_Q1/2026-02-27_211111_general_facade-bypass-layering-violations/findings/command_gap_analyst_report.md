# Command Gap Analysis Report

**Date:** 2026-02-27
**Analyst:** Command Gap Analyst (Claude Code)
**Scope:** All existing commands vs UI operations that mutate game state

---

## Summary

- **Total issues found:** 14
- **Critical:** 3, **Major:** 6, **Minor:** 4, **Info:** 1
- **Commands cataloged:** 22
- **UI operations cataloged:** 28
- **Gaps identified:** 14 (6 MISSING commands, 8 MISROUTED operations)

---

## Existing Commands Catalog

| # | Command | Handler | Parameters | Purpose |
|---|---------|---------|------------|---------|
| 1 | `IssueColonizeCommand` | `ColonizeCommandHandler` | fleet_id, planet_id? | Colonize a planet at fleet location |
| 2 | `IssueMoveCommand` | `MoveCommandHandler` | fleet_id, target_hex | Move fleet to hex |
| 3 | `IssueBuildShipCommand` | `BuildShipCommandHandler` | planet_id, design_name | Add ship to planet build queue |
| 4 | `IssueInterceptCommand` | `InterceptCommandHandler` | fleet_id, target_fleet_id | Intercept another fleet |
| 5 | `IssueJoinFleetCommand` | `JoinCommandHandler` | fleet_id, target_fleet_id | Join/merge with another fleet |
| 6 | `QueueColonizeMissionCommand` | `ColonizeMissionCommandHandler` | fleet_id, target_hex, planet_id? | Move + colonize mission |
| 7 | `ClearFleetOrdersCommand` | `ClearOrdersCommandHandler` | fleet_id | Clear all fleet orders |
| 8 | `IssueTransferCommand` | `TransferCommandHandler` | fleet_id, planet_id?, cargo_type, direction, amount, species_id?, target_fleet_id? | Transfer cargo between fleet and colony/fleet |
| 9 | `IssueWarpCommand` | `WarpCommandHandler` | fleet_id, warp_point_hex | Traverse a warp point |
| 10 | `IssueBuildOrderCommand` | `BuildOrderCommandHandler` | fleet_id | Issue BUILD order to fleet with shipyard |
| 11 | `RemoveBuildOrderCommand` | `RemoveBuildOrderCommandHandler` | fleet_id | Remove BUILD orders from fleet |
| 12 | `IssueImplodePlanetCommand` | `ImplodePlanetCommandHandler` | fleet_id, planet_id | Destroy a planet |
| 13 | `IssueStellerateStarCommand` | `StellerateStarCommandHandler` | fleet_id | Destroy a star |
| 14 | `IssueOpenWarpPointCommand` | `OpenWarpPointCommandHandler` | fleet_id, target_hex, target_system_name | Create warp link |
| 15 | `IssueCloseWarpPointCommand` | `CloseWarpPointCommandHandler` | fleet_id, warp_point_destination_id | Destroy a warp link |
| 16 | `IssueCreateDysonSphereCommand` | `CreateDysonSphereCommandHandler` | fleet_id | Create a Dyson Sphere |
| 17 | `IssueSelfDestructCommand` | `SelfDestructCommandHandler` | fleet_id, ship_ids | Self-destruct selected ships |
| 18 | `QueueImplodePlanetMissionCommand` | `ImplodePlanetMissionCommandHandler` | fleet_id, target_hex, planet_id | Move + implode planet |
| 19 | `QueueStellerateStarMissionCommand` | `StellerateStarMissionCommandHandler` | fleet_id, target_hex | Move + stellerate star |
| 20 | `QueueOpenWarpPointMissionCommand` | `OpenWarpPointMissionCommandHandler` | fleet_id, target_hex, target_system_name | Move + open warp point |
| 21 | `QueueCloseWarpPointMissionCommand` | `CloseWarpPointMissionCommandHandler` | fleet_id, target_hex, warp_point_destination_id | Move + close warp point |
| 22 | `QueueCreateDysonSphereMissionCommand` | `CreateDysonSphereMissionCommandHandler` | fleet_id, target_hex | Move + create Dyson Sphere |

---

## UI Operations Catalog

| # | Operation | File | Lines | Goes Through Command? | Domain Object Touched |
|---|-----------|------|-------|-----------------------|-----------------------|
| 1 | Issue MOVE order | `strategy_fleet_ops.py` | 102-133 | YES - `IssueMoveCommand` via facade | Fleet.orders, Fleet.path |
| 2 | Issue INTERCEPT order | `strategy_fleet_ops.py` | 135-157 | YES - `IssueInterceptCommand` via facade | Fleet.orders |
| 3 | Issue JOIN order | `strategy_fleet_ops.py` | 159-201 | YES - `IssueJoinFleetCommand` via facade | Fleet.orders |
| 4 | Issue COLONIZE order | `strategy_colonization.py` | 146-165 | YES - `IssueColonizeCommand` via facade | Fleet.orders |
| 5 | Queue colonize mission | `strategy_colonization.py` | 241-267 | YES - `QueueColonizeMissionCommand` via facade | Fleet.orders |
| 6 | Implode planet mission | `strategy_superweapons.py` | 99-115 | YES - `QueueImplodePlanetMissionCommand` via facade | Fleet.orders |
| 7 | Stellerate star mission | `strategy_superweapons.py` | 117-161 | YES - `QueueStellerateStarMissionCommand` via facade | Fleet.orders |
| 8 | Open warp point mission | `strategy_superweapons.py` | 163-217 | YES - `QueueOpenWarpPointMissionCommand` via facade | Fleet.orders |
| 9 | Close warp point mission | `strategy_superweapons.py` | 219-261 | YES - `QueueCloseWarpPointMissionCommand` via facade | Fleet.orders |
| 10 | Dyson sphere mission | `strategy_superweapons.py` | 263-307 | YES - `QueueCreateDysonSphereMissionCommand` via facade | Fleet.orders |
| 11 | Self-destruct | `strategy_superweapons.py` | 309-340 | YES - `IssueSelfDestructCommand` via facade | Fleet.orders |
| 12 | Clear fleet orders | `strategy_window_manager.py` | 280-284 | YES - `ClearFleetOrdersCommand` via session | Fleet.orders |
| 13 | Issue BUILD order | `strategy_build_queue_manager.py` | 133-142 | YES - `IssueBuildOrderCommand` via session | Fleet.orders |
| 14 | Remove BUILD order | `strategy_build_queue_manager.py` | 143-146 | YES - `RemoveBuildOrderCommand` via session | Fleet.orders |
| 15 | Transfer cargo (quick dialog) | `cargo_quick_dialog.py` | 250-290 | YES - `IssueTransferCommand` via facade | Fleet.orders |
| 16 | Transfer cargo (full dialog) | `transfer_dialog.py` | 414-443 | YES - `IssueTransferCommand` via facade | Fleet.orders |
| 17 | **Reorder fleet orders** | `fleet_orders_window.py` | 281-293 | **NO** - direct `fleet.orders` swap | Fleet.orders, Fleet.path |
| 18 | **Delete single fleet order** | `fleet_orders_window.py` | 295-307 | **NO** - direct `fleet.orders.pop()` | Fleet.orders, Fleet.path |
| 19 | **Undo delete fleet order** | `fleet_orders_window.py` | 309-328 | **NO** - direct `fleet.orders.insert()` | Fleet.orders, Fleet.path |
| 20 | **Remove ship from fleet** | `fleet_report_window.py` | 235-248 | **NO** - direct `fleet.remove_ship()` + `empire.add_fleet()` | Fleet.ships, Empire.fleets |
| 21 | **Remove selected ships from fleet** | `fleet_report_window.py` | 250-274 | **NO** - direct `fleet.remove_ship()` + `empire.add_fleet()` | Fleet.ships, Empire.fleets |
| 22 | **Add to construction queue** | `build_queue_controller.py` | 242-272 | **NO** - direct `source.construction_queue.append/insert` | Planet/Fleet construction_queue |
| 23 | **Remove from construction queue** | `build_queue_screen.py` | 301-315 | **NO** - direct `queue.pop()` | Planet/Fleet construction_queue |
| 24 | **Drag-reorder construction queue** | `build_queue_drag_handler.py` | 180-198 | **NO** - direct `construction_queue.pop()` | Planet/Fleet construction_queue |
| 25 | **Batch add to build queues** | `empire_build_queue_window.py` | 352-368 | **NO** - direct `source.construction_queue.append()` | Planet/Fleet construction_queue |
| 26 | **Set RP budget** | `research_controls.py` | 268-271 | **NO** - direct `tracker.set_rp_budget()` | ResearchTracker |
| 27 | **Set RP allocation** | `research_controls.py` | 275-285 | **NO** - direct `tracker.set_allocation()` | ResearchTracker |
| 28 | **Toggle auto-spread RP** | `research_controls.py` | 350-362 | **NO** - direct `tracker.spread_rp_evenly()` | ResearchTracker |

---

## Gap Analysis

### COVERED Operations (Command Exists and Is Used)

These 16 operations are properly routed through the command pipeline:

1. **Move fleet** - `IssueMoveCommand` via `FleetOperations.execute_move()` through facade
2. **Intercept fleet** - `IssueInterceptCommand` via `FleetOperations.execute_intercept()` through facade
3. **Join fleet** - `IssueJoinFleetCommand` via `FleetOperations.handle_join_designation()` through facade
4. **Colonize (at location)** - `IssueColonizeCommand` via `ColonizationSystem.issue_colonize_order()` through facade
5. **Queue colonize mission** - `QueueColonizeMissionCommand` via `ColonizationSystem.queue_colonize_mission()` through facade
6. **Implode planet mission** - `QueueImplodePlanetMissionCommand` through facade
7. **Stellerate star mission** - `QueueStellerateStarMissionCommand` through facade
8. **Open warp point mission** - `QueueOpenWarpPointMissionCommand` through facade
9. **Close warp point mission** - `QueueCloseWarpPointMissionCommand` through facade
10. **Create Dyson sphere mission** - `QueueCreateDysonSphereMissionCommand` through facade
11. **Self-destruct** - `IssueSelfDestructCommand` through facade
12. **Clear fleet orders** - `ClearFleetOrdersCommand` through session (via window_manager callback)
13. **Issue BUILD order** - `IssueBuildOrderCommand` through session
14. **Remove BUILD order** - `RemoveBuildOrderCommand` through session
15. **Transfer cargo (quick dialog)** - `IssueTransferCommand` through facade
16. **Transfer cargo (full dialog)** - `IssueTransferCommand` through facade

### MISROUTED Operations (Command Exists but UI Bypasses It)

These operations have adjacent or matching commands but bypass the command pipeline:

1. **CGA-01** - Fleet order reordering bypasses any command (see Findings)
2. **CGA-02** - Fleet order deletion bypasses `ClearFleetOrdersCommand` (see Findings)
3. **CGA-03** - Fleet order undo-delete bypasses command pipeline (see Findings)
4. **CGA-04** - Build queue additions bypass `IssueBuildShipCommand` (see Findings)

### MISSING Commands (No Command Exists)

These operations mutate game state but have no corresponding command:

5. **CGA-05** - Split fleet / remove ships from fleet (see Findings)
6. **CGA-06** - Remove item from construction queue (see Findings)
7. **CGA-07** - Reorder construction queue (see Findings)
8. **CGA-08** - Batch add to construction queues (see Findings)
9. **CGA-09** - Set RP budget (see Findings)
10. **CGA-10** - Set RP allocation for research node (see Findings)
11. **CGA-11** - Toggle auto-spread RP (see Findings)

---

## Findings

### CRITICAL: Fleet Order Manipulation Bypasses Command Pipeline
**ID:** CGA-01
**Location:** `game/ui/screens/fleet_orders_window.py:281-293`
**Issue:** Reordering fleet orders is done by directly swapping elements in `fleet.orders` list and setting `fleet.path = []`. This bypasses the command pipeline entirely. There is no `ReorderFleetOrderCommand`.
**Impact:** No validation, no logging, no undo at the engine level. If the game were to implement network play, replays, or server-side validation, reordering would be invisible. The active order (index 0) change can silently invalidate movement state.
**Recommendation:** Create `ReorderFleetOrderCommand(fleet_id, order_index, direction)` that validates order indices and handles path invalidation.
**Effort:** Simple

---

### CRITICAL: Fleet Order Deletion Bypasses Command Pipeline
**ID:** CGA-02
**Location:** `game/ui/screens/fleet_orders_window.py:295-307`
**Issue:** Deleting a single fleet order uses `fleet.orders.pop(index)` directly from the UI. No command exists for single-order deletion. `ClearFleetOrdersCommand` clears ALL orders but cannot delete a specific one.
**Impact:** Same as CGA-01 -- no validation, no logging. Deleting the active order (index 0) directly sets `fleet.path = []` from the UI layer, which is engine state manipulation.
**Recommendation:** Create `DeleteFleetOrderCommand(fleet_id, order_index)` with validation and path invalidation logic.
**Effort:** Simple

---

### CRITICAL: Split Fleet / Remove Ships Bypasses Command Pipeline
**ID:** CGA-05
**Location:** `game/ui/screens/fleet_report_window.py:235-274`
**Issue:** Removing ships from a fleet and creating a new fleet is done entirely in the UI layer:
- `fleet.remove_ship(ship)` -- mutates fleet domain object
- `Fleet(new_fleet_id, ...)` -- creates domain object from UI
- `empire.add_fleet(new_fleet)` -- mutates empire domain object

This is a significant domain operation (fleet splitting) that has no command, no validation, and no engine involvement whatsoever.
**Impact:** Fleet splitting creates new fleet IDs via `empire.get_next_fleet_id()` from UI, potentially causing ID collisions in multiplayer. No validation that the fleet has enough ships remaining. No logging. The operation cannot be replayed or undone.
**Recommendation:** Create `SplitFleetCommand(fleet_id, ship_ids)` that validates ship ownership, creates the new fleet in the engine, and returns the new fleet ID.
**Effort:** Medium

---

### MAJOR: Build Queue Add Bypasses `IssueBuildShipCommand`
**ID:** CGA-04
**Location:** `game/ui/panels/build_queue_controller.py:242-538`
**Issue:** The `BuildQueueController.add_to_queue()` method directly manipulates `source.construction_queue.append()` and `source.construction_queue.insert()`. While `IssueBuildShipCommand` exists and has a handler (`BuildShipCommandHandler`), it delegates to `planet.add_production(design_name, 1)` which is a different code path. The UI build queue system bypasses this command entirely and manages the queue list directly.
**Impact:** `IssueBuildShipCommand` appears to be dead code or used only in a narrow legacy context. The real build queue operations (add, insert, multi-queue batch add) all bypass commands. No centralized validation of build capability, resource availability, or queue limits.
**Recommendation:** Either:
- (a) Create `AddToConstructionQueueCommand(entity_id, entity_type, design_id, category, index?)` that replaces direct manipulation, or
- (b) Refactor `IssueBuildShipCommand` to cover the full add-to-queue operation and route all UI additions through it.
**Effort:** Complex

---

### MAJOR: Remove from Construction Queue Bypasses Command Pipeline
**ID:** CGA-06
**Location:** `game/ui/screens/build_queue_screen.py:301-315`
**Issue:** Removing items from the construction queue uses `queue.pop(self.selected_queue_index)` directly. No command exists for removing a specific item from a construction queue.
**Impact:** No validation, no logging. Cannot be replayed. In fleet context, BUILD order state may become inconsistent if queue empties.
**Recommendation:** Create `RemoveFromConstructionQueueCommand(entity_id, entity_type, item_index)` that validates the index and handles BUILD order cleanup.
**Effort:** Simple

---

### MAJOR: Drag-Reorder Construction Queue Bypasses Command Pipeline
**ID:** CGA-07
**Location:** `game/ui/panels/build_queue_drag_handler.py:180-198`
**Issue:** Drag-and-drop reordering removes items from the queue with `construction_queue.pop(idx)` and later re-inserts them at the drop position via `add_to_queue()` (which itself bypasses commands per CGA-04). This is two direct mutations with no command.
**Impact:** Construction queue ordering affects what gets built first. No validation, no logging. If the drag is cancelled mid-operation, the item has already been popped from the queue (though it's held in drag state and re-inserted on drop).
**Recommendation:** Create `ReorderConstructionQueueCommand(entity_id, entity_type, from_index, to_index)` as an atomic operation.
**Effort:** Medium

---

### MAJOR: Batch Add to Construction Queues Bypasses Command Pipeline
**ID:** CGA-08
**Location:** `game/ui/screens/empire_build_queue_window.py:352-368`
**Issue:** `batch_add_to_selected()` iterates selected queue sources and directly appends to `source.construction_queue`. This is a multi-entity mutation from the UI layer with no command.
**Impact:** Batch operations are inherently higher risk since they touch multiple entities atomically. No validation per-entity, no rollback capability, no logging.
**Recommendation:** Either batch should call individual `AddToConstructionQueueCommand` per source, or create a `BatchAddToConstructionQueuesCommand(source_ids, item)` that handles validation across all targets.
**Effort:** Medium

---

### MAJOR: Fleet Order Undo-Delete Bypasses Command Pipeline
**ID:** CGA-03
**Location:** `game/ui/screens/fleet_orders_window.py:309-328`
**Issue:** Undo-delete restores orders by inserting directly into `fleet.orders` with `fleet.orders.insert(original_index, order)`. This is an inverse operation with no command and no validation.
**Impact:** The restored order may be stale (e.g., target fleet may have moved or been destroyed). No validation that the restored order is still valid. Path invalidation is done directly from UI.
**Recommendation:** Should be handled by an `InsertFleetOrderCommand(fleet_id, order, index)` or by the engine-level undo system. At minimum, the undo operation should validate the restored order.
**Effort:** Medium

---

### MAJOR: Set RP Budget Bypasses Command Pipeline
**ID:** CGA-09
**Location:** `game/ui/research/research_controls.py:268-271`
**Issue:** Setting the RP budget calls `tracker.set_rp_budget(new_budget)` directly from the UI slider handler. No command exists for research budget changes.
**Impact:** Research budget is a strategic game state mutation. Without commands, there is no validation of budget bounds at the engine level, no logging, and no replay capability.
**Recommendation:** Create `SetResearchBudgetCommand(empire_id, budget)` with validation.
**Effort:** Simple

---

### MINOR: Set RP Allocation Bypasses Command Pipeline
**ID:** CGA-10
**Location:** `game/ui/research/research_controls.py:275-285`
**Issue:** Setting RP allocation for a specific research node calls `tracker.set_allocation(node_id, new_allocation)` directly. No command exists for research allocation changes.
**Impact:** Research allocation is a per-node strategic decision. Without commands, allocations cannot be logged, replayed, or validated centrally.
**Recommendation:** Create `SetResearchAllocationCommand(empire_id, node_id, allocation)` with validation against budget and node availability.
**Effort:** Simple

---

### MINOR: Toggle Auto-Spread RP Bypasses Command Pipeline
**ID:** CGA-11
**Location:** `game/ui/research/research_controls.py:350-362`
**Issue:** Toggling auto-spread calls `tracker.spread_rp_evenly(self.tech_tree)` directly. This redistributes all RP allocations across available nodes -- a significant multi-node mutation with no command.
**Impact:** Spread affects all research nodes simultaneously. No logging, no undo capability.
**Recommendation:** Create `SpreadResearchRPCommand(empire_id)` that validates tree state and applies spread.
**Effort:** Simple

---

### MINOR: Clear Fleet Orders Fallback Bypasses Facade
**ID:** CGA-12
**Location:** `game/ui/screens/fleet_orders_window.py:400-404`
**Issue:** When `_clear_orders_callback` is not set (backward compatibility fallback), the clear orders operation calls `self.fleet.clear_orders()` directly instead of routing through the command pipeline. The comment explicitly says "Fallback for backward compatibility (e.g., tests)".
**Impact:** Low risk since the callback is always set in production (PROJ-207). However, per project conventions, backward compatibility fallbacks should be eradicated, not maintained.
**Recommendation:** Remove the fallback and make `_clear_orders_callback` required. Tests should provide the callback or mock it.
**Effort:** Simple

---

### MINOR: Build Queue Manager Routes Through Session Instead of Facade
**ID:** CGA-13
**Location:** `game/ui/screens/strategy_build_queue_manager.py:142,146`
**Issue:** The BUILD order commands (`IssueBuildOrderCommand`, `RemoveBuildOrderCommand`) are dispatched via `self._screen.session.handle_command(cmd)` instead of via the facade (`self._screen._facade.handle_command(cmd)`). While functionally identical (facade delegates to session), this bypasses the facade layer that exists specifically as the UI-to-engine boundary.
**Impact:** Violates the architectural principle that all UI-to-engine communication goes through the facade. Works correctly but sets a bad precedent.
**Recommendation:** Change to `self._screen._facade.handle_command(cmd)` for consistency. Also applies to `strategy_window_manager.py:284`.
**Effort:** Simple

---

### INFO: `IssueBuildShipCommand` May Be Dead Code
**ID:** CGA-14
**Location:** `game/strategy/engine/commands.py:43-51`, `game/strategy/engine/command_handlers.py:334-347`
**Issue:** `IssueBuildShipCommand` and its `BuildShipCommandHandler` call `planet.add_production(design_name, 1)`. However, the actual UI build queue system (`BuildQueueController`) never uses this command. It directly manipulates `construction_queue.append()`. The `add_production` method on Planet may be a separate older API.
**Impact:** If `IssueBuildShipCommand` is truly unused, it is dead code that creates confusion about how builds should work. Need to verify if anything else calls it.
**Recommendation:** Search for all callers of `IssueBuildShipCommand`. If none exist in production code, mark it for deprecation or removal, and replace with a proper `AddToConstructionQueueCommand` that matches the actual queue structure.
**Effort:** Simple (investigation)

---

## Recommended New Commands

### 1. `SplitFleetCommand`
```python
@dataclass
class SplitFleetCommand(Command):
    """Remove ships from a fleet and create a new fleet."""
    fleet_id: int
    ship_ids: List[int]
```
- **Validation:** Fleet exists, all ship_ids belong to fleet, at least one ship remains in source fleet
- **Handler logic:** Remove ships, create new Fleet with next ID, add to empire, return new fleet ID
- **Priority:** Critical -- fleet composition changes must be engine-managed

### 2. `DeleteFleetOrderCommand`
```python
@dataclass
class DeleteFleetOrderCommand(Command):
    """Remove a specific order from a fleet's order queue."""
    fleet_id: int
    order_index: int
```
- **Validation:** Fleet exists, order_index is valid
- **Handler logic:** Pop order at index, invalidate path if index 0
- **Priority:** Critical -- order manipulation is a core game operation

### 3. `ReorderFleetOrderCommand`
```python
@dataclass
class ReorderFleetOrderCommand(Command):
    """Move a fleet order up or down in the queue."""
    fleet_id: int
    order_index: int
    direction: int  # -1 for up, +1 for down
```
- **Validation:** Fleet exists, order_index valid, target index valid
- **Handler logic:** Swap orders, invalidate path if active order affected
- **Priority:** Critical -- order manipulation is a core game operation

### 4. `AddToConstructionQueueCommand`
```python
@dataclass
class AddToConstructionQueueCommand(Command):
    """Add a design to a planet or fleet construction queue."""
    entity_id: int
    entity_type: str  # "planet" or "fleet"
    design_id: str
    category: str  # "complex", "ship", "satellite", "fighter"
    index: Optional[int] = None  # None = append, int = insert at position
    target_planet_id: Optional[int] = None  # For complexes on fleet yards
```
- **Validation:** Entity exists, can build this category, design exists
- **Handler logic:** Calculate build time, create queue item with cost tracking, insert/append
- **Priority:** Major -- build operations are frequent and touch resource economy

### 5. `RemoveFromConstructionQueueCommand`
```python
@dataclass
class RemoveFromConstructionQueueCommand(Command):
    """Remove an item from a construction queue."""
    entity_id: int
    entity_type: str  # "planet" or "fleet"
    item_index: int
```
- **Validation:** Entity exists, item_index is valid
- **Handler logic:** Pop item from queue, handle BUILD order cleanup for fleets
- **Priority:** Major -- paired with AddToConstructionQueueCommand

### 6. `ReorderConstructionQueueCommand`
```python
@dataclass
class ReorderConstructionQueueCommand(Command):
    """Move a construction queue item to a new position."""
    entity_id: int
    entity_type: str
    from_index: int
    to_index: int
```
- **Validation:** Entity exists, both indices valid
- **Handler logic:** Pop from source index, insert at target index
- **Priority:** Major -- queue ordering affects build priority

### 7. `SetResearchBudgetCommand`
```python
@dataclass
class SetResearchBudgetCommand(Command):
    """Set the RP budget per turn for an empire."""
    empire_id: int
    budget: int
```
- **Validation:** Empire exists, budget within MIN/MAX bounds
- **Handler logic:** Update tracker.rp_budget, adjust allocations if over budget
- **Priority:** Minor -- research is less frequent than fleet/build operations

### 8. `SetResearchAllocationCommand`
```python
@dataclass
class SetResearchAllocationCommand(Command):
    """Set RP allocation for a specific research node."""
    empire_id: int
    node_id: str
    allocation: int
```
- **Validation:** Empire exists, node is available for research, allocation within remaining RP
- **Handler logic:** Update tracker allocation, clamp to budget
- **Priority:** Minor -- research is less frequent than fleet/build operations

---

## Top 5 Priority Issues

| Rank | ID | Severity | Title | Rationale |
|------|----|----------|-------|-----------|
| 1 | CGA-05 | Critical | Split Fleet bypasses command pipeline | Creates domain objects from UI, generates IDs from UI, mutates Empire directly. Highest architectural risk. |
| 2 | CGA-04 | Major | Build Queue Add bypasses `IssueBuildShipCommand` | Most frequently triggered bypass -- every time a player adds a build item. `IssueBuildShipCommand` may be dead code. |
| 3 | CGA-01 | Critical | Fleet Order Reordering bypasses commands | Directly mutates orders + path from UI. Combined with CGA-02 and CGA-03, the entire fleet orders window operates outside the command pipeline. |
| 4 | CGA-02 | Critical | Fleet Order Deletion bypasses commands | Part of the fleet orders window bypass cluster. Deleting the active order invalidates path from UI. |
| 5 | CGA-06 | Major | Remove from Construction Queue bypasses commands | Paired operation with CGA-04 -- if adds bypass, removes should too, but this compounds the problem. Both should go through commands together. |

---

## Architecture Notes

### What's Working Well
- **Fleet movement and combat orders** are well-covered: MOVE, INTERCEPT, JOIN, COLONIZE, WARP all go through properly structured commands via the facade.
- **Superweapon operations** are thoroughly covered with both direct and mission (move+action) variants.
- **Transfer/cargo operations** are properly routed through `IssueTransferCommand`.
- The **facade pattern** is consistently used for the covered operations.
- **BUILD order lifecycle** (issue/remove) is routed through commands since PROJ-207.

### Systemic Pattern
The bypasses cluster around three areas:
1. **Fleet management window** (`fleet_orders_window.py`, `fleet_report_window.py`) -- all order manipulation and ship splitting bypass commands.
2. **Build queue system** (`build_queue_controller.py`, `build_queue_screen.py`, `build_queue_drag_handler.py`, `empire_build_queue_window.py`) -- all queue content manipulation bypasses commands.
3. **Research system** (`research_controls.py`) -- all research allocation bypasses commands.

These are likely areas that were built before the command pipeline was established, or grew organically without being migrated to the CQRS pattern.

### Facade Consistency
Two files route commands through `session.handle_command()` instead of `facade.handle_command()`:
- `strategy_build_queue_manager.py` (lines 142, 146)
- `strategy_window_manager.py` (line 284)

While functionally equivalent, this violates the architectural principle that UI communicates only through the facade.
