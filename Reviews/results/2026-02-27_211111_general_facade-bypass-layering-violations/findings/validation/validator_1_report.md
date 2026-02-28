# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 40
- **Confirmed:** 28
- **Downgraded:** 7
- **Rejected:** 5
- **Rejection Rate:** 12.5%

## Verdicts

---

### Architecture Reviewer 1 Findings

#### Finding: AR-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:239`. The `_on_remove_ship` method directly calls `self.fleet.remove_ship(ship)` from the UI layer, bypassing the command pipeline entirely. This is a genuine direct mutation of domain state.

#### Finding: AR-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:247`. The code calls `self.empire.add_fleet(new_fleet)` directly from the UI layer. This is a genuine domain mutation bypassing the command pipeline.

#### Finding: AR-003
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:276-286`. The `_create_fleet_for_ships` method imports `Fleet` from `game.strategy.data.fleet`, calls `self.empire.get_next_fleet_id()`, and constructs the domain object directly in the UI layer.

#### Finding: AR-004
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The finding is accurate -- `_on_remove_selected_ships` (lines 250-274) does iterate ships, call `remove_ship`, create a fleet, and call `add_fleet`. However, this is functionally a duplicate of AR-001/002/003 (same code paths, batch version). Classifying as a separate Critical overstates the issue count; it is the same architectural gap manifested in a batch operation. Downgrading to Major as a distinct but related finding.

#### Finding: AR-005
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:281-293`. The `move_order` method directly swaps items in `self.fleet.orders` and sets `self.fleet.path = []`. This is direct domain state mutation from the UI layer.

#### Finding: AR-006
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:295-307`. The `delete_order` method directly calls `self.fleet.orders.pop(index)` and sets `self.fleet.path = []`. This is direct domain mutation from the UI.

#### Finding: AR-007
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:309-328`. The `undo_delete` method directly calls `self.fleet.orders.insert(original_index, order)` and sets `self.fleet.path = []`. This is direct domain mutation from the UI.

#### Finding: AR-008
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:96` and `109`. The window reads `self.fleet.orders` directly (mutable list) and monitors its length. The `rebuild_list` method at line 109 iterates `self.fleet.orders`. The window holds a direct reference to the mutable orders list.

#### Finding: AR-009
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:194`. The code reads `self.fleet.construction_queue` directly to get queue size for BUILD order descriptions. This is a direct property access from UI into the domain model.

#### Finding: AR-010
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:46-47`. The constructor stores `self.fleet = fleet` and `self.empire = empire`, holding direct references to mutable domain objects. This is the root cause enabling AR-001 through AR-004.

#### Finding: AR-011
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:57` (`FleetListViewModel(fleet.ships)`) and line 143 (`self.view_model.update_ships(self.fleet.ships)`). The view model directly operates on live domain ship objects.

#### Finding: AR-012
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified across `strategy_window_manager.py`. Multiple methods pass `self.scene.current_empire`, `self.scene.galaxy`, and `fleet` domain objects directly to window constructors (lines 111-122, 137-148, 163-176, 247-257, 267-289, 295-315). This is the systemic architectural gap enabling other violations.

#### Finding: AR-013
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_window_manager.py:284`. The `clear_orders_callback` lambda calls `self.scene.session.handle_command(cmd)` instead of `self.scene.facade.handle_command(cmd)`. While functionally equivalent today, this bypasses the facade which is the intended single entry point for commands.

#### Finding: AR-014
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `empire_build_queue_window.py:361`. The `batch_add_to_selected` method directly calls `source.construction_queue.append(dict(item))`, mutating the domain object's construction queue from the UI layer without going through the command pipeline.

#### Finding: AR-015
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_screen.py:309`. The `_handle_remove` method directly calls `remove_queue.pop(self.selected_queue_index)`. The `remove_queue` is obtained from `_get_active_queue()` which returns `active_queue_source.construction_queue` -- a live domain object's list. This is direct domain mutation from the UI.

#### Finding: AR-016
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_screen.py:134-162`. Properties like `galaxy`, `empires`, `systems`, `player_empire`, `enemy_empire`, `human_player_ids`, and `current_empire` are direct passthroughs to `self.session`. These return live domain objects. The code comment acknowledges this ("for internal convenience"), and the `facade` property exists as the intended public interface. Minor severity is appropriate as this is a design choice with documented rationale.

#### Finding: AR-017
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_screen.py:288-314`. The `on_ui_selection` method receives domain objects (Fleet, Planet, StarSystem), uses protocol type guards to check types, accesses `obj.owner_id`, `obj.planets`, `obj.warp_points`, and stores them as `self.selected_fleet` and `self.selected_object`. This is direct domain object handling in the UI layer.

#### Finding: AR-018
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_screen.py:337-343`. The `on_design_click` method packages `self.session.player_empire` (a live Empire domain object) and `self.session` (the entire GameSession) into `context_data` and passes them via scene callback to the design workshop.

#### Finding: AR-019
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:404`. The fallback path `self.fleet.clear_orders()` exists when `_clear_orders_callback` is None. This directly mutates domain state. The comment on line 403 ("Fallback for backward compatibility") confirms the backward-compat nature, which the project policy says should be eradicated.

#### Finding: AR-020
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_list_window.py:54-87`. The `_build_list` method iterates `self.empire.colonies` and `self.empire.fleets`, accessing `planet.construction_queue`, `planet.name`, `fleet.construction_queue`, and `fleet.name` directly.

#### Finding: AR-021
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `planet_list_window.py:40-42, 53`. The window stores `self.galaxy = galaxy` and `self.empire = empire` directly. The `gather_planets(galaxy, empire)` call traverses galaxy's internal data structures.

#### Finding: AR-022
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The finding is accurate -- `empire_panel_window.py:73-74` stores `self.empire`, and lines 194, 217, 281, 294 access `empire.race_config`, `empire.portrait_id`, `empire.flag_id`, and pass empire to `EmpireEconomyCalculator.calculate()`. However, this is a read-only window, and the empire panel actually does the right thing for the treasury tab (using `EmpireEconomyCalculator` to produce a snapshot DTO at line 194, then delegating to `EmpireTreasuryPanel` which uses the DTO). The population tab reads `race_config` which is an immutable dataclass. This is well-structured code with minimal risk; Info is more appropriate.

#### Finding: AR-023
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified at `system_selection_window.py:27-29, 50-53`. The window receives `systems` (list of StarSystem domain objects) and `current_system`, accessing `system.global_location` and `system.name`. Info severity is appropriate -- this is read-only, short-lived, and low risk.

#### Finding: AR-024
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified. The finding correctly identifies `DesignSelectorWindow` and `SaveSelectionWindow` as well-layered. `EventLogWindow` uses pre-built event dicts from the facade. These are accurate observations of good patterns. Info/no-violation is appropriate.

---

### Architecture Reviewer 2 Findings

#### Finding: AR2-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_controller.py:413, 416, 450, 453, 491, 535, 538`. The controller calls `.insert()` and `.append()` directly on `source.construction_queue` in multiple methods: `_add_to_single_queue` (lines 413, 416), `_add_item_with_target_planet` (lines 450, 453), `_add_to_multiple_queues` (line 491), and `_add_to_fallback` (lines 535, 538). All seven mutation sites bypass the command pipeline.

#### Finding: AR2-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_drag_handler.py:182`. The handler calls `construction_queue.pop(idx)` to remove an item during a drag-reorder operation. This is direct domain list mutation from a UI mouse event handler.

#### Finding: AR2-003
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The finding is accurate -- the controller holds `self.galaxy` and `self.empire` references and calls `self.galaxy.get_planets_at_global_hex(self.hex_coord)` with `p.owner_id == self.empire.id` filtering in three places (lines 313-316, 344-349, 376-379). However, this is read-only property access (not mutation), making Critical severity too high. The existing facade query `get_planets_at_hex()` could replace these calls. Major is more appropriate as this is a bypass of the query path, not a state mutation.

#### Finding: AR2-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `planet_report_panel.py:72, 188, 220-222, 251`. The panel stores `self.planet` as a raw domain object, accesses `planet.planet_type.name` (line 220), and `update_planet()` accepts a raw Planet object. The complexes list iterates `planet.facilities`. Major severity is appropriate.

#### Finding: AR2-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `system_tree_panel.py:7, 135-344`. The `set_items()` method receives raw domain objects and stores them in `SystemTreeItem.obj`. It accesses `star.name` (line 209), `wp.destination_id` (lines 237, 249), `p.name` (lines 296, 309), `p.location` (line 266), `p.mass` (lines 273, 325). The selection callback passes raw domain objects back to callers via `item.obj`.

#### Finding: AR2-006
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The finding is accurate -- `build_queue_portraits.py:69` accepts a `session` object and at line 93-94 accesses `self.session.player_empire.empire_theme_id`. However, this is a read-only access for a display concern (theme lookup for portrait rendering). The fix is trivially simple (pass theme_id directly), making Major overstated. Minor is more appropriate.

#### Finding: AR2-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `research_controls.py:269, 281, 352, 357`. The control panel directly calls `self.tracker.set_rp_budget(new_budget)` (line 269), `self.tracker.set_allocation(node_id, new_allocation)` (line 281), `self.tracker.auto_spread_enabled = not self.tracker.auto_spread_enabled` (line 352), and `self.tracker.spread_rp_evenly(self.tech_tree)` (line 357). These are state mutations performed from UI code.

#### Finding: AR2-008
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `research_scene.py:76-82, 341, 362-368`. The scene directly instantiates `TechTree.load_from_json()` (line 76), `ResearchTracker()` (line 79), calls `self.tech_tree.resolve_all_requirements()` (line 82), `self.tech_tree.validate_requirements()` (line 85), `ResearchService.process_turn()` (line 341), and creates a new `ResearchTracker()` on reset (line 365). The UI scene acts as both controller and service layer.

#### Finding: AR2-009
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The finding is accurate -- `compute_planet_production()` at `planet_report_panel.py:457-501` is business logic in a UI module, iterating `planet.facilities` and performing production calculations. However, the function is a pure calculation utility (no side effects, no mutations), and it is used as a shared helper across multiple UI panels. While it belongs in a strategy service, its impact as a read-only utility is lower than Major. Minor is more appropriate.

#### Finding: AR2-010
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The finding accurately describes `ship_detail_panel.py:163-178` operating on `ShipInstance` objects with many property accesses. However, as the report itself notes, `ShipInstance` is specifically designed as a strategy-layer data class with display-oriented methods (`get_hp_display()`, `get_status_text()`). It serves a DTO-like role by design. The coupling is intentional and acceptable. Minor is more appropriate.

#### Finding: AR2-011
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The report itself concludes "No action needed" and states the `ICombatShip` protocol "serves as the 'DTO boundary' for combat display." The finding acknowledges this is the correct pattern. A finding with no actionable issue and an explicit "no action needed" recommendation should not be reported as a violation at all.

#### Finding: AR2-012
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The report itself states "Low priority" and acknowledges the Design Workshop is "a special case where the UI must interact with a live mutable Ship" in an MVC editing context. This is an intentional, acceptable design pattern for a live editor, not a violation.

#### Finding: AR2-013
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Same rationale as AR2-012. The report acknowledges these panels are "used in the Design Workshop context where components are being actively edited" and marks them "Low priority for the same reason as AR2-012." This is an acceptable pattern for a live editing context.

#### Finding: AR2-014
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The report states these are "pure rendering widgets that read data for visualization" using "protocol-based access (`is_star`, `IPlanet`) which provides a controlled interface." The coupling is described as "minimal." Protocol-based read-only rendering is the correct pattern, not a violation.

#### Finding: AR2-015
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified at `battle_orchestrator.py:1-21`. The cross-layer imports are documented in the module docstring as intentional. The finding correctly identifies this as good architecture with "No action needed." Info severity is appropriate.

#### Finding: AR2-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified at `empire_treasury_panel.py:57`. The panel receives an `EmpireEconomySnapshot` dataclass and only reads its fields. The finding correctly identifies this as exemplary code following the correct CQRS pattern. Info severity is appropriate.
