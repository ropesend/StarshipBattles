# Architecture Review: Facade Bypass & CQRS Layering Violations
## Reviewer: Architecture Reviewer 1 (Screens & Windows)

**Date:** 2026-02-27
**Scope:** Strategy-facing UI screens and windows
**Files Reviewed:** 14

---

### Summary
- **Total issues found:** 24
- **Critical:** 7
- **Major:** 8
- **Minor:** 7
- **Info:** 2

---

### Findings

---

#### CRITICAL: FleetReportWindow directly mutates Fleet.remove_ship()
**ID:** AR-001
**Location:** `game/ui/screens/fleet_report_window.py:239-248`
**Violation Type:** Direct Mutation
**Issue:** The `_on_remove_ship` method directly calls `self.fleet.remove_ship(ship)` to remove a ship from a fleet. This is a direct domain model mutation from the UI layer, completely bypassing the command pipeline.
**Impact:** State changes happen outside the command pipeline, making them invisible to validation, event logging, undo systems, and any other cross-cutting concerns. This also creates inconsistency with other fleet operations that use commands.
**Recommendation:** Create a `RemoveShipFromFleetCommand` (or `SplitFleetCommand`) in `game/strategy/engine/commands.py` and dispatch it via `facade.handle_command()`. The FleetReportWindow should receive a facade reference to issue the command.
**Effort:** Medium

---

#### CRITICAL: FleetReportWindow directly calls Empire.add_fleet()
**ID:** AR-002
**Location:** `game/ui/screens/fleet_report_window.py:247`
**Violation Type:** Direct Mutation
**Issue:** After removing a ship, the code calls `self.empire.add_fleet(new_fleet)` to add a newly created fleet to the empire. This directly mutates the Empire domain object from the UI layer.
**Impact:** The empire's fleet list is modified outside of any command pipeline. No validation, no event logging, no way for game logic to react to the new fleet's creation.
**Recommendation:** This should be part of the `RemoveShipFromFleetCommand` / `SplitFleetCommand`. The command handler in GameSession should handle both removing the ship and creating the new fleet.
**Effort:** Medium

---

#### CRITICAL: FleetReportWindow instantiates Fleet domain object
**ID:** AR-003
**Location:** `game/ui/screens/fleet_report_window.py:276-286`
**Violation Type:** Domain Instantiation
**Issue:** The `_create_fleet_for_ships` method directly instantiates `Fleet` from `game.strategy.data.fleet`, calls `empire.get_next_fleet_id()`, and constructs a new domain object in the UI layer.
**Impact:** Domain object creation logic in the UI layer violates separation of concerns. Fleet ID generation, initialization, and registration should be handled by the strategy engine, not the UI.
**Recommendation:** Move fleet creation logic into the command handler. The UI should only issue a command with the ship IDs to split; the engine handles fleet creation and registration.
**Effort:** Medium

---

#### CRITICAL: FleetReportWindow bulk removes ships and creates fleet
**ID:** AR-004
**Location:** `game/ui/screens/fleet_report_window.py:250-274`
**Violation Type:** Direct Mutation
**Issue:** `_on_remove_selected_ships` iterates through selected ships, calls `self.fleet.remove_ship(ship)` for each, then creates a new fleet and calls `self.empire.add_fleet()`. This is the multi-ship version of AR-001/AR-002/AR-003.
**Impact:** Multiple domain mutations performed directly from UI without command pipeline. Same issues as AR-001/002/003 but amplified by the batch nature.
**Recommendation:** Create a `SplitFleetCommand` that accepts a fleet_id and a list of ship_ids to split off. The command handler performs all the mutations atomically.
**Effort:** Medium

---

#### CRITICAL: FleetOrdersWindow directly mutates Fleet.orders list
**ID:** AR-005
**Location:** `game/ui/screens/fleet_orders_window.py:281-293`
**Violation Type:** Direct Mutation
**Issue:** The `move_order` method directly swaps items in `self.fleet.orders` list and directly sets `self.fleet.path = []`. This is a direct mutation of domain model internal state from the UI.
**Impact:** Order reordering bypasses the command pipeline entirely. Path invalidation is done ad-hoc in the UI rather than being handled by game logic.
**Recommendation:** Create `ReorderFleetOrderCommand(fleet_id, order_index, new_index)` and dispatch via facade. The command handler should handle path invalidation.
**Effort:** Medium

---

#### CRITICAL: FleetOrdersWindow directly deletes from Fleet.orders
**ID:** AR-006
**Location:** `game/ui/screens/fleet_orders_window.py:295-307`
**Violation Type:** Direct Mutation
**Issue:** The `delete_order` method directly calls `self.fleet.orders.pop(index)` and sets `self.fleet.path = []`. This removes an order from the domain model's internal list from the UI layer.
**Impact:** Order deletion bypasses validation, event logging, and any other command pipeline concerns. The undo stack is maintained in the UI rather than at the domain level.
**Recommendation:** Create `DeleteFleetOrderCommand(fleet_id, order_index)` and dispatch via facade. Move undo tracking to the domain layer or provide an undo command.
**Effort:** Medium

---

#### CRITICAL: FleetOrdersWindow directly inserts into Fleet.orders (undo)
**ID:** AR-007
**Location:** `game/ui/screens/fleet_orders_window.py:309-328`
**Violation Type:** Direct Mutation
**Issue:** The `undo_delete` method directly calls `self.fleet.orders.insert(original_index, order)` and sets `self.fleet.path = []`. This restores a previously deleted order by directly manipulating the domain model's internal list.
**Impact:** Undo functionality is implemented entirely in the UI layer by directly mutating domain state. No validation occurs, and the operation is invisible to the command pipeline.
**Recommendation:** Create `InsertFleetOrderCommand(fleet_id, order_index, order_data)` or implement undo at the command pipeline level with `UndoDeleteFleetOrderCommand`.
**Effort:** Complex

---

#### MAJOR: FleetOrdersWindow reads Fleet.orders directly for rendering
**ID:** AR-008
**Location:** `game/ui/screens/fleet_orders_window.py:96-98, 109`
**Violation Type:** Direct Property Access
**Issue:** The window reads `self.fleet.orders` directly (a mutable list of domain Order objects) and monitors its length for change detection. The `rebuild_list` method iterates over `self.fleet.orders` to build UI.
**Impact:** The UI holds a direct reference to the mutable internal orders list of the Fleet domain object. Changes to this list from anywhere are immediately visible, breaking encapsulation. The UI also accesses `order.target` which may be mutable domain objects (Planet, Fleet).
**Recommendation:** Use `facade.get_fleet(fleet_id)` to obtain a `FleetInfo` DTO which already contains `FleetOrderInfo` tuples. Render from the DTO's immutable order data.
**Effort:** Medium

---

#### MAJOR: FleetOrdersWindow accesses Fleet.construction_queue
**ID:** AR-009
**Location:** `game/ui/screens/fleet_orders_window.py:194`
**Violation Type:** Direct Property Access
**Issue:** `_get_order_description` reads `self.fleet.construction_queue` directly to get the queue size for BUILD order descriptions.
**Impact:** Direct access to domain model's internal construction queue from UI layer.
**Recommendation:** The `FleetOrderInfo` DTO should contain sufficient data for description rendering. Add a `detail_text` or `context_data` field to `FleetOrderInfo` populated during DTO creation.
**Effort:** Simple

---

#### MAJOR: FleetReportWindow holds direct reference to Fleet domain object
**ID:** AR-010
**Location:** `game/ui/screens/fleet_report_window.py:46-47`
**Violation Type:** Direct Property Access
**Issue:** The constructor stores `self.fleet = fleet` and `self.empire = empire`, holding direct references to mutable domain objects throughout the window's lifecycle.
**Impact:** The window can read and mutate domain state at will. All subsequent method calls operate on the live domain objects rather than immutable DTOs. This is the root cause enabling AR-001 through AR-004.
**Recommendation:** The window should receive fleet_id and empire_id, then query the facade for DTOs. For mutation operations, it should issue commands through the facade.
**Effort:** Complex

---

#### MAJOR: FleetReportWindow reads Fleet.ships directly
**ID:** AR-011
**Location:** `game/ui/screens/fleet_report_window.py:57, 143`
**Violation Type:** Direct Property Access
**Issue:** `FleetListViewModel(fleet.ships)` and `self.view_model.update_ships(self.fleet.ships)` directly access the fleet's internal ships list.
**Impact:** The view model operates on live domain ship objects. Any mutations to ships are immediately reflected, and the view model could potentially mutate them.
**Recommendation:** Use `FleetInfo.ships` (tuple of `ShipInfo` DTOs) from the facade query. The view model should work with immutable ShipInfo DTOs.
**Effort:** Medium

---

#### MAJOR: StrategyWindowManager passes domain objects to windows
**ID:** AR-012
**Location:** `game/ui/screens/strategy_window_manager.py:111-122, 137-148, 163-176, 247-257, 267-289, 295-315`
**Violation Type:** Direct Property Access
**Issue:** `StrategyWindowManager` passes domain objects (`self.scene.current_empire`, `self.scene.galaxy`, `fleet`) directly to window constructors throughout: `open_planet_list`, `open_build_queue_list`, `open_empire_build_queue_window`, `open_empire_panel`, `open_orders_window`, `open_fleet_report_window`.
**Impact:** All windows receive live mutable domain objects instead of DTOs or facade references. This is the root architectural gap that enables all the window-level violations.
**Recommendation:** Windows should receive either (a) the facade + entity IDs, then query for DTOs, or (b) pre-built DTOs from the window manager. For mutation operations, windows need a facade reference.
**Effort:** Complex

---

#### MAJOR: StrategyWindowManager dispatches command via session.handle_command (bypassing facade)
**ID:** AR-013
**Location:** `game/ui/screens/strategy_window_manager.py:280-284`
**Violation Type:** Command Bypass
**Issue:** The `clear_orders_callback` lambda calls `self.scene.session.handle_command(cmd)` directly instead of `self.scene.facade.handle_command(cmd)`. While functionally equivalent today, this bypasses the facade which is the intended single entry point.
**Impact:** Violates the CQRS-lite pattern. If the facade adds validation, logging, or other cross-cutting concerns in the future, this call site would miss them.
**Recommendation:** Change `self.scene.session.handle_command(cmd)` to `self.scene.facade.handle_command(cmd)` (or `self.scene._facade.handle_command(cmd)`).
**Effort:** Simple

---

#### MAJOR: EmpireBuildQueueWindow directly appends to construction_queue
**ID:** AR-014
**Location:** `game/ui/screens/empire_build_queue_window.py:361`
**Violation Type:** Direct Mutation
**Issue:** `batch_add_to_selected` directly appends items to `source.construction_queue.append(dict(item))`. The `BuildQueueSource.construction_queue` is a live reference to the domain object's queue.
**Impact:** Build queue modifications bypass the command pipeline. No validation occurs, no events are logged, and there is no way to undo.
**Recommendation:** Create an `AddToBuildQueueCommand(entity_id, entity_type, item)` and dispatch via facade. The batch operation should issue one command per queue.
**Effort:** Medium

---

#### MAJOR: BuildQueueScreen directly pops from construction_queue
**ID:** AR-015
**Location:** `game/ui/screens/build_queue_screen.py:309`
**Violation Type:** Direct Mutation
**Issue:** `_handle_remove` directly calls `remove_queue.pop(self.selected_queue_index)` to remove an item from the active construction queue. This is a direct mutation of the domain model's build queue.
**Impact:** Build queue removal bypasses the command pipeline. No validation, no event logging. The `BuildQueueController` may have additional logic, but the queue pop itself is raw domain mutation.
**Recommendation:** Create a `RemoveFromBuildQueueCommand(entity_id, entity_type, queue_index)` and dispatch via facade.
**Effort:** Medium

---

#### MINOR: StrategyScreen exposes session properties directly
**ID:** AR-016
**Location:** `game/ui/screens/strategy_screen.py:134-162`
**Violation Type:** Direct Property Access
**Issue:** StrategyScreen exposes `galaxy`, `empires`, `systems`, `player_empire`, `enemy_empire`, `human_player_ids`, and `current_empire` as direct passthrough properties to `self.session`. These return live domain objects.
**Impact:** Any code with a reference to the StrategyScreen can access live domain objects directly, bypassing the facade. While the code comment acknowledges this is for "internal convenience," it provides an easy bypass path.
**Recommendation:** Gradually migrate consumers to use facade queries. Mark these properties with deprecation warnings. Eventually, only the facade property should remain as the public interface.
**Effort:** Complex

---

#### MINOR: StrategyScreen.on_ui_selection works with domain objects
**ID:** AR-017
**Location:** `game/ui/screens/strategy_screen.py:288-314`
**Violation Type:** Direct Property Access
**Issue:** `on_ui_selection` receives domain objects (Fleet, Planet, StarSystem), checks their type via protocol guards, accesses `obj.owner_id`, `obj.planets`, `obj.warp_points`, and stores them as `self.selected_fleet` and `self.selected_object`.
**Impact:** The main selection flow works entirely with domain objects. The `selected_fleet` is a live Fleet domain object used by many downstream operations.
**Recommendation:** Convert selections to IDs and DTOs. Store `selected_fleet_id` instead of `selected_fleet`, and query the facade for FleetInfo when needed.
**Effort:** Complex

---

#### MINOR: StrategyScreen.on_design_click passes session.player_empire
**ID:** AR-018
**Location:** `game/ui/screens/strategy_screen.py:337-343`
**Violation Type:** Direct Property Access
**Issue:** `on_design_click` packages `self.session.player_empire` (a live Empire domain object) and `self.session` (the entire GameSession) into context_data and passes them to the scene callback for the design workshop.
**Impact:** The design workshop receives direct access to both the Empire domain object and the entire GameSession, enabling arbitrary domain manipulation.
**Recommendation:** Pass only the empire_id and a facade reference. The design workshop should query the facade for any empire data it needs.
**Effort:** Medium

---

#### MINOR: FleetOrdersWindow backward-compat fallback calls fleet.clear_orders()
**ID:** AR-019
**Location:** `game/ui/screens/fleet_orders_window.py:404`
**Violation Type:** Direct Mutation
**Issue:** The `handle_global_event` method has a fallback path (`else: self.fleet.clear_orders()`) when no `_clear_orders_callback` is provided. This directly mutates the fleet domain object.
**Impact:** While the primary path uses the command pipeline (PROJ-207), the backward-compatibility fallback directly mutates domain state. Per project policy, backward compatibility layers should be eradicated.
**Recommendation:** Remove the fallback. If `_clear_orders_callback` is None, either raise an error or do nothing. The callback should always be provided.
**Effort:** Simple

---

#### MINOR: BuildQueueListWindow directly accesses Empire.colonies and Empire.fleets
**ID:** AR-020
**Location:** `game/ui/screens/build_queue_list_window.py:54-87`
**Violation Type:** Direct Property Access
**Issue:** `_build_list` iterates over `self.empire.colonies` and `self.empire.fleets` directly, accessing `planet.construction_queue`, `planet.name`, `fleet.construction_queue`, and `fleet.name`.
**Impact:** The window reads internal domain model data directly instead of querying through the facade. It accesses mutable construction queue lists.
**Recommendation:** Add a facade query method like `get_empire_build_queues(empire_id)` that returns a list of immutable build queue summary DTOs.
**Effort:** Medium

---

#### MINOR: PlanetListWindow directly accesses Galaxy and Empire domain objects
**ID:** AR-021
**Location:** `game/ui/screens/planet_list_window.py:40-42, 53`
**Violation Type:** Direct Property Access
**Issue:** The window receives and stores `galaxy` and `empire` domain objects directly. `gather_planets(galaxy, empire)` traverses the galaxy's internal data structures to collect planet data.
**Impact:** The planet list window operates entirely on live domain objects. While read-only in practice, it has full access to mutable domain state.
**Recommendation:** Add a facade query like `get_all_planets_for_empire(empire_id)` returning a list of enriched `PlanetInfo` DTOs with system names and owner info. The PlanetListWindow should work with DTOs.
**Effort:** Complex

---

#### MINOR: EmpirePanelWindow directly accesses Empire domain properties
**ID:** AR-022
**Location:** `game/ui/screens/empire_panel_window.py:73-74, 194, 217, 281, 294`
**Violation Type:** Direct Property Access
**Issue:** The window stores `self.empire` and accesses `empire.race_config`, `empire.portrait_id`, `empire.flag_id`, and passes the empire to `EmpireEconomyCalculator.calculate(self.empire)`.
**Impact:** The window reads deeply into the Empire domain model's properties. While read-only, it couples the UI tightly to the domain model's internal structure.
**Recommendation:** Extend `EmpireInfo` DTO with the race config data, portrait_id, flag_id, and treasury snapshot. Alternatively, create a dedicated `EmpireDetailInfo` DTO for this window.
**Effort:** Medium

---

#### INFO: SystemSelectionWindow receives domain objects (acceptable for read-only display)
**ID:** AR-023
**Location:** `game/ui/screens/system_selection_window.py:27-29`
**Violation Type:** Direct Property Access
**Issue:** The window receives `systems` (list of StarSystem domain objects) and `current_system` (a StarSystem) and accesses `system.global_location` and `system.name` for display purposes.
**Impact:** Low risk as the window is read-only and short-lived. However, it still couples the UI to the domain model's structure.
**Recommendation:** In a future pass, consider accepting a list of `SystemInfo` DTOs. The facade already provides `get_all_systems()` which returns `SystemInfo` DTOs.
**Effort:** Simple

---

#### INFO: DesignSelectorWindow and SaveSelectionWindow are properly layered
**ID:** AR-024
**Location:** `game/ui/screens/design_selector_window.py`, `game/ui/screens/save_selection_window.py`
**Violation Type:** N/A (No violation)
**Issue:** These windows interact with dedicated service objects (`DesignLibrary`, `SaveGameService`) rather than domain models directly. `DesignSelectorWindow` uses `DesignLibrary.search_designs()` and `DesignLibrary.mark_obsolete()`. `SaveSelectionWindow` uses `SaveGameService` static methods. The `EventLogWindow` receives pre-built event dicts from the facade.
**Impact:** N/A - These are examples of correct layering.
**Recommendation:** No changes needed. These can serve as reference implementations for migrating other windows.
**Effort:** N/A

---

### Top 5 Priority Issues

1. **AR-001/002/003/004 (Critical) - FleetReportWindow directly mutates Fleet and Empire:** This is the most severe cluster of violations. Ship removal, fleet creation, and empire registration all happen directly in the UI layer. A `SplitFleetCommand` should be created to handle the entire operation atomically through the command pipeline.

2. **AR-005/006/007 (Critical) - FleetOrdersWindow directly mutates Fleet.orders:** Order reordering, deletion, and undo all manipulate the fleet's order list directly. These need dedicated commands (`ReorderFleetOrderCommand`, `DeleteFleetOrderCommand`) routed through the facade.

3. **AR-012 (Major) - StrategyWindowManager passes domain objects to all windows:** This is the systemic architectural gap that enables most other violations. The window manager should be refactored to pass facade references and entity IDs (or pre-built DTOs) rather than live domain objects.

4. **AR-014/015 (Major) - Build queue screens directly mutate construction_queue:** Both `EmpireBuildQueueWindow.batch_add_to_selected` and `BuildQueueScreen._handle_remove` directly manipulate domain construction queues. These need `AddToBuildQueueCommand` and `RemoveFromBuildQueueCommand`.

5. **AR-013 (Major) - Command dispatch bypasses facade:** The clear orders callback routes through `session.handle_command` instead of `facade.handle_command`. This is the simplest fix -- a one-line change -- and should be addressed immediately.
