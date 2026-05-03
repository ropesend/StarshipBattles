# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 32
- **Confirmed:** 23
- **Downgraded:** 6
- **Rejected:** 3
- **Rejection Rate:** 9.4%

## Verdicts

### Code Quality Analyst Findings (CQ-001 through CQ-018)

#### Finding: CQ-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:235-286`. The `_on_remove_ship`, `_on_remove_selected_ships`, and `_create_fleet_for_ships` methods perform full fleet-splitting operations directly in the UI layer. Confirmed: `fleet.remove_ship(ship)` (line 245/269), `Fleet(...)` construction (line 281), `empire.add_fleet()` (line 247/273), `empire.get_next_fleet_id()` (line 280). No validation guards exist. Critical is appropriate -- this is domain object construction and multi-entity mutation from the UI layer with no command pipeline involvement.

#### Finding: CQ-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:281-328`. `move_order()` (line 287) performs in-place swap on `self.fleet.orders`. `delete_order()` (line 298) uses `orders.pop(index)`. `undo_delete()` (line 319) uses `self.fleet.orders.insert()`. All three bypass the command pipeline. The same file's `handle_global_event` uses `ClearFleetOrdersCommand` via callback (line 400-401), confirming that command-based order manipulation was the intended pattern. Critical severity is justified.

#### Finding: CQ-003
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Verified at lines 291, 302, 323 -- `self.fleet.path = []` is assigned directly in all three methods. The claim about the UI manipulating internal engine state is accurate. However, downgrading to Major because: (1) the game is single-threaded, so the race condition concern is speculative; (2) the path invalidation logic is correct in intent (active order changed = clear path). The primary issue is a layering violation, not a correctness bug. This would naturally be fixed as part of CQ-002.

#### Finding: CQ-004
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Verified at `fleet_report_window.py:276-286`. The `from game.strategy.data.fleet import Fleet` and `Fleet(new_fleet_id, ...)` constructor call are present. This is a genuine layering violation. However, downgrading to Major because this is a subset of CQ-001 -- the finding describes one aspect of the same fleet-splitting problem. Calling it a separate Critical inflates the count. It should be addressed as part of the CQ-001 fix.

#### Finding: CQ-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:400-404`. The `else` branch with the comment "Fallback for backward compatibility (e.g., tests)" exists exactly as described. The project's CLAUDE.md explicitly prohibits backward compatibility fallbacks ("ERADICATE the old system completely"). The fallback path calls `self.fleet.clear_orders()` directly, bypassing the command pipeline. Major severity is appropriate.

#### Finding: CQ-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_window_manager.py`. The `open_planet_list` (line 111-112), `open_build_queue_list` (line 137), `open_empire_build_queue_window` (lines 163-164), `open_empire_panel` (line 247), and `open_fleet_report_window` (line 308) all access `self.scene.current_empire` and/or `self.scene.galaxy` and pass them as live mutable domain objects to window constructors. This is accurately described and Major is appropriate as a structural enabler of bypass patterns.

#### Finding: CQ-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:235-274`. `_on_remove_ship` has no check for `len(self.fleet.ships) > 1` before removing the ship. `_on_remove_selected_ships` allows selecting all ships (via `MultiSelect`) and removing all of them from the source fleet (line 267-269) without checking whether the fleet would become empty. An empty fleet is indeed an invalid state. Major severity is appropriate.

#### Finding: CQ-008
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified at `fleet_orders_window.py:341-391`. The large block of deliberation comments exists exactly as described. However, this is purely a readability/code hygiene issue with no functional impact. Calling 50 lines of stale comments "Major" is severity inflation. This is a Minor code smell -- annoying but harmless. It does not create bugs, corrupt state, or prevent refactoring.

#### Finding: CQ-009
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:46-47`. `self.fleet = fleet` and `self.empire = empire` store direct mutable references. The empire reference is used for `empire.add_fleet()` (line 247) and `empire.get_next_fleet_id()` (line 280), and the fleet reference is used for `fleet.remove_ship()` (lines 239, 245, 269). The finding correctly identifies this as the enabler for CQ-001 and CQ-007. Major is appropriate as an architectural concern.

#### Finding: CQ-010
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_screen.py:134-163`. Properties `galaxy`, `empires`, `player_empire`, `systems`, `enemy_empire`, `human_player_ids`, and `current_empire` all expose raw domain objects from the session. Line 131 has the comment "External callers should use the facade" but there is no enforcement. The window manager (CQ-006) and other sub-modules use these freely. Major severity is appropriate as this structurally undermines the facade pattern.

#### Finding: CQ-011
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_window_manager.py:280-284`. The `clear_orders_callback` closure calls `self.scene.session.handle_command(cmd)` instead of `self.scene.facade.handle_command(cmd)`. The facade's `handle_command` method exists at `strategy_session_facade.py:52-64` and delegates to `self._session.handle_command(command)`. The bypass is real -- today it's functionally equivalent, but it sets a bad precedent and will miss any future facade-level middleware. Major is appropriate.

#### Finding: CQ-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:235-241`. The no-empire path (lines 237-240) calls `self.fleet.remove_ship(ship)` and then returns without creating a new fleet. The ship is effectively lost from the game. The `_on_remove_selected_ships` method (line 252) returns early if `not self.empire`, which is a different behavior (no removal). Minor severity is appropriate.

#### Finding: CQ-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:281`. `Fleet(new_fleet_id, self.fleet.owner_id, self.fleet.location, speed=0)` uses hardcoded `speed=0`. The `add_ship()` calls on lines 283-284 do trigger recalculation, so this is functionally correct but the magic number is a minor readability concern. Minor severity is appropriate.

#### Finding: CQ-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:96`. The comparison `len(self.fleet.orders) != self._last_order_count` only detects additions and removals, not reorders or content mutations. Since this same window performs reorders (line 287), the window immediately calls `rebuild_list()` after its own reorders so the staleness only applies to external modifications. Minor severity is appropriate.

#### Finding: CQ-015
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:173`. Each row stores `'order_ref': order` which is a direct reference to the domain object. The `deleted_history` list (lines 50, 305) also stores `(index, order)` tuples with domain object references. Minor severity is appropriate -- this is a design concern rather than an active bug.

#### Finding: CQ-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified. PROJ-207 migrated "Clear All" to the command pipeline (line 400-401) but left `move_order`, `delete_order`, and `undo_delete` as direct mutations. This creates an inconsistent pattern within the same file. Info severity is appropriate as an observation.

#### Finding: CQ-017
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_window_manager.py:53-61`. The constructor stores `self.scene` and uses it extensively (lines 111, 137, 163, 175, 201, 247, 284, 308, 349). This creates a bidirectional dependency: StrategyScreen -> StrategyUI -> StrategyWindowManager -> StrategyScreen. Info severity is appropriate.

#### Finding: CQ-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified at `strategy_screen.py:82,122-127`. The facade is created at line 82 and passed to `FleetOperations`, `ColonizationSystem`, and `SuperweaponOperations` (lines 122-124). However, `StrategyBuildQueueManager` (line 125) and `StrategyGameStateManager` (line 126) do not receive the facade. The session is also directly accessible via `self.session`. Info severity is appropriate.

---

### Command Gap Analyst Findings (CGA-01 through CGA-14)

#### Finding: CGA-01
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Verified at `fleet_orders_window.py:281-293`. The direct swap on `fleet.orders` and `fleet.path = []` is confirmed. However, this is a duplicate of the same issue described in CQ-002. More importantly, reordering fleet orders is a relatively low-risk UI convenience operation -- the orders themselves were already validated when originally issued. The absence of a command is a real gap but the risk of state corruption is lower than for fleet splitting. Major is more appropriate than Critical.

#### Finding: CGA-02
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Verified at `fleet_orders_window.py:295-307`. The `fleet.orders.pop(index)` and `fleet.path = []` are confirmed. Duplicate of the same issue in CQ-002. Downgrading for the same reasoning as CGA-01 -- deleting a previously-validated order is lower risk than creating new domain objects. The path invalidation is correct behavior. Major is more appropriate.

#### Finding: CGA-03
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_orders_window.py:309-328`. The `fleet.orders.insert(original_index, order)` is confirmed. The stale order concern is valid -- the restored order references a potentially-changed target. This is part of the same cluster as CGA-01/CGA-02. Major severity is appropriate.

#### Finding: CGA-04
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_controller.py:412-417,450-453,491`. The `source.construction_queue.insert()` and `source.construction_queue.append()` calls are confirmed across `_add_to_single_queue`, `_add_item_with_target_planet`, and `_add_to_multiple_queues`. The `IssueBuildShipCommand` exists but uses a different API (`planet.add_production`), confirming the disconnect. Major is appropriate.

#### Finding: CGA-05
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified at `fleet_report_window.py:235-274`. Duplicate of CQ-001 but from the command gap perspective. The absence of a `SplitFleetCommand` is confirmed. Critical severity is justified -- this is the most significant command gap, involving domain object construction and multi-entity mutation from the UI.

#### Finding: CGA-06
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_screen.py:301-315`. The `_handle_remove` method calls `remove_queue.pop(self.selected_queue_index)` directly. No command exists for this operation. Major severity is appropriate.

#### Finding: CGA-07
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `build_queue_drag_handler.py:180-198`. The `construction_queue.pop(idx)` during drag initiation (line 182) is confirmed. The item is then re-inserted via `add_to_queue()` on drop, which also bypasses commands (per CGA-04). Major severity is appropriate.

#### Finding: CGA-08
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified at `empire_build_queue_window.py:352-368`. The `batch_add_to_selected` method iterates sources and calls `source.construction_queue.append(dict(item))` directly (line 361). No command pipeline involvement. Major severity is appropriate.

#### Finding: CGA-09
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified at `research_controls.py:268-271`. The `tracker.set_rp_budget(new_budget)` call is confirmed. However, downgrading to Minor because: (1) research budget is a simple numeric setter, not a complex multi-entity mutation; (2) the `set_rp_budget` method likely has its own validation; (3) research budget changes are low-risk and reversible. The command gap is real but the impact is overstated.

#### Finding: CGA-10
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `research_controls.py:275-285`. The `tracker.set_allocation(node_id, new_allocation)` call is confirmed. The actual allocation is read back on line 282 (`tracker.get_state(node_id).rp_allocation`), suggesting the tracker does clamp values internally. Minor severity is appropriate.

#### Finding: CGA-11
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified at `research_controls.py:350-362`. The `_toggle_auto_spread` method sets `tracker.auto_spread_enabled` directly (line 352) and calls `tracker.spread_rp_evenly(self.tech_tree)` (line 357). Minor severity is appropriate -- this is a convenience toggle with limited corruption risk.

#### Finding: CGA-12
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** This is a direct duplicate of CQ-005, which covers the exact same code at the same location (`fleet_orders_window.py:400-404`) with the same description and recommendation. CQ-005 was already confirmed as Major. Including this as a separate finding adds no value.

#### Finding: CGA-13
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** This is a direct duplicate of CQ-011, which covers the same issue at `strategy_window_manager.py:284` and also mentions `strategy_build_queue_manager.py`. The additional reference to `strategy_build_queue_manager.py:142,146` is verified (lines 141-142 and 145-146 use `self._screen.session.handle_command(cmd)` instead of facade), but CQ-011 already covers the pattern. The finding adds one extra call site but is otherwise fully redundant.

#### Finding: CGA-14
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The finding claims `IssueBuildShipCommand` "may be dead code." Searching the codebase shows it is registered in `command_handlers.py:685`, has unit tests (`test_commands.py:126-138`), and has integration tests (`test_command_handlers.py:132-146`). While the UI build queue controller does not use it, the command is functional, registered, and tested. It may be underutilized or represent a different abstraction layer, but calling it "dead code" is inaccurate. The finding should have verified callers before reporting.
