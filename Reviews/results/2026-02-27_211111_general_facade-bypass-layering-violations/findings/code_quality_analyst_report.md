# Code Quality Analysis: Facade Bypass & Layering Violations

**Analyst:** Code Quality Analyst
**Date:** 2026-02-27
**Scope:** `fleet_report_window.py`, `fleet_orders_window.py`, `strategy_screen.py`, `strategy_window_manager.py`

---

## Summary

- **Total issues found:** 18
- **Critical:** 4
- **Major:** 7
- **Minor:** 4
- **Info:** 3

The most serious problems are concentrated in two files: `fleet_report_window.py` performs full domain object construction and multi-step fleet splitting entirely in the UI layer with zero validation, and `fleet_orders_window.py` directly mutates the fleet's order list and path state, bypassing the command pipeline that already exists for the "Clear All" action. The `strategy_window_manager.py` passes live domain objects (Empire, Fleet, Galaxy) into every window it opens, making future facade migration structurally difficult.

---

## Findings

### Critical

#### CRITICAL: Fleet Splitting Logic Lives Entirely in UI Layer with No Validation

**ID:** CQ-001
**Location:** `game/ui/screens/fleet_report_window.py:235-286`
**Issue:** The `_on_remove_ship`, `_on_remove_selected_ships`, and `_create_fleet_for_ships` methods implement a complete fleet-splitting operation directly in the UI. This involves:
1. Removing ships from the source fleet (`fleet.remove_ship(ship)`)
2. Generating a new fleet ID (`empire.get_next_fleet_id()`)
3. Constructing a `Fleet` domain object (`Fleet(...)`)
4. Adding ships to the new fleet (`new_fleet.add_ship(ship)`)
5. Registering the fleet with the empire (`empire.add_fleet(new_fleet)`)

There is **no validation** at any step:
- No check that the source fleet is not being reduced to zero ships (creating an empty fleet).
- No check that the fleet is not currently executing orders (BUILD, movement in progress).
- No check that the fleet belongs to the current player.
- The `Fleet` constructor is called with `speed=0`, which is incorrect -- it should be recalculated from ship composition. The `add_ship` calls do trigger `trigger_speed_recalculation()` but only after construction with an initial speed of 0.

**Impact:** This bypass can corrupt game state. An empty fleet left behind after removing all ships would cause crashes or undefined behavior in the turn engine. The operation is not recorded in any command log, so it cannot be serialized/replayed/undone at the engine level. No events are emitted, so other UI components (strategy sidebar, fleet list panels) won't know about the new fleet until a full refresh.

**Recommendation:** Create a `SplitFleetCommand` in the command pipeline that validates the operation (min 1 ship remains, fleet not mid-order, etc.), emits events, and handles fleet construction. The UI should only dispatch the command through the facade.

**Effort:** Complex

---

#### CRITICAL: Direct Order Array Mutation Bypasses Command Pipeline

**ID:** CQ-002
**Location:** `game/ui/screens/fleet_orders_window.py:281-328`
**Issue:** Three methods directly mutate `self.fleet.orders`, a list belonging to the Fleet domain object:
- `move_order()` (line 287): `orders[index], orders[new_index] = orders[new_index], orders[index]` -- in-place swap
- `delete_order()` (line 298): `orders.pop(index)` -- direct removal
- `undo_delete()` (line 319): `self.fleet.orders.insert(original_index, order)` -- direct insertion

These operations completely bypass the command pipeline. The project already has `ClearFleetOrdersCommand` (used via callback from the same file, line 397-401), proving that order manipulation was intended to flow through commands. But reorder, delete, and undo-insert never received equivalent commands.

**Impact:** Order mutations are invisible to the engine. No validation occurs (e.g., deleting a BUILD order while construction is in progress, reordering a COLONIZE order to execute before movement completes). No event emission means other UI panels don't refresh. The undo stack is purely local and lost on window close.

**Recommendation:** Create `ReorderFleetOrderCommand`, `DeleteFleetOrderCommand`, and `InsertFleetOrderCommand` (or a single `ModifyFleetOrdersCommand`) and dispatch through the facade. The undo stack could be maintained in the UI for quick response, but actual mutations should go through commands.

**Effort:** Complex

---

#### CRITICAL: Direct Path State Mutation from UI Layer

**ID:** CQ-003
**Location:** `game/ui/screens/fleet_orders_window.py:291,302,323`
**Issue:** Three locations directly assign `self.fleet.path = []` to clear the fleet's calculated movement path. The `path` attribute is internal engine state used by the movement system during turn processing. The UI is directly nullifying pathfinding state without going through any engine method.

The logic is: "If we modify the active order (index 0), clear the path." While the intent is correct, the implementation is wrong -- the UI should not know about or manipulate `fleet.path` directly. This is internal implementation detail of how the movement engine tracks in-progress routes.

**Impact:** If the turn engine is mid-processing (e.g., in a multi-threaded scenario or coroutine-based turn), clearing path from the UI could cause a race condition. Even in single-threaded mode, the UI is making assumptions about engine internals (that `path` is invalidated when orders change) that could break if the engine's pathfinding logic changes.

**Recommendation:** Path invalidation should be a side effect of the command that modifies orders, handled inside the engine. The UI should never touch `fleet.path`.

**Effort:** Medium (folded into CQ-002 fix)

---

#### CRITICAL: Domain Object Instantiation in UI Layer

**ID:** CQ-004
**Location:** `game/ui/screens/fleet_report_window.py:276-286`
**Issue:** The `_create_fleet_for_ships` method imports and instantiates `Fleet` from `game.strategy.data.fleet`:
```python
from game.strategy.data.fleet import Fleet
new_fleet = Fleet(new_fleet_id, self.fleet.owner_id, self.fleet.location, speed=0)
```

This is a hard dependency on the domain model's constructor signature. The UI layer is performing domain object construction -- a responsibility that belongs exclusively to the engine/service layer. If `Fleet.__init__` signature changes (e.g., adding a required `galaxy` parameter), this UI code breaks.

**Impact:** Tight coupling between UI and domain model construction. Violates the layering principle where UI should only communicate through the facade. Makes refactoring the `Fleet` class risky because UI code depends on its constructor.

**Recommendation:** Move fleet construction to a service or command handler behind the facade. The UI should never `import Fleet` for instantiation.

**Effort:** Medium (folded into CQ-001 fix)

---

### Major

#### MAJOR: Backward Compatibility Fallback Violates System Migration Policy

**ID:** CQ-005
**Location:** `game/ui/screens/fleet_orders_window.py:400-404`
**Issue:** The `handle_global_event` method has a dual code path:
```python
if self._clear_orders_callback:
    self._clear_orders_callback(self.fleet.id)
else:
    # Fallback for backward compatibility (e.g., tests)
    self.fleet.clear_orders()
```

Per the project's CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely." The comment explicitly says "Fallback for backward compatibility (e.g., tests)," which is the exact anti-pattern the project rules prohibit. Tests should be updated to provide the callback.

**Impact:** Two code paths doing the same thing. The fallback path bypasses the command pipeline, so it's silently possible to reach the old behavior. Tests using the fallback are testing the wrong code path.

**Recommendation:** Remove the `else` branch entirely. Update any tests that don't provide the callback to provide one. If a test needs the window without a callback, it should still not silently clear orders.

**Effort:** Simple

---

#### MAJOR: Window Manager Passes Live Domain Objects to All Windows

**ID:** CQ-006
**Location:** `game/ui/screens/strategy_window_manager.py:106-315`
**Issue:** Every `open_*` method accesses live domain objects through `self.scene` and passes them directly to window constructors:
- Line 111-112: `empire = self.scene.current_empire; galaxy = self.scene.galaxy` passed to PlanetListWindow
- Line 137: `empire = self.scene.current_empire` passed to BuildQueueListWindow
- Line 163-164: `empire, galaxy` passed to EmpireBuildQueueWindow
- Line 247: `empire = self.scene.current_empire` passed to EmpirePanelWindow
- Line 308: `empire = self.scene.current_empire` passed to FleetReportWindow

These are not DTOs -- they are live mutable domain objects. Any window receiving them can mutate game state directly (and FleetReportWindow does exactly this).

**Impact:** The facade pattern is structurally undermined. Even if individual windows are refactored to use commands, as long as they hold references to live domain objects, the temptation and ability to bypass the facade remains. The window manager is the primary enabler of this antipattern.

**Recommendation:** Windows should receive either (a) the facade instance + IDs to query what they need, or (b) DTOs. The window manager should be refactored to pass `self.scene.facade` instead of domain objects.

**Effort:** Complex (requires refactoring all window constructors)

---

#### MAJOR: No Empty-Fleet Guard in Ship Removal

**ID:** CQ-007
**Location:** `game/ui/screens/fleet_report_window.py:235-248`
**Issue:** `_on_remove_ship` and `_on_remove_selected_ships` allow removing all ships from a fleet without checking whether the fleet would become empty:
```python
def _on_remove_ship(self, ship):
    if ship in self.fleet.ships:
        self.fleet.remove_ship(ship)
        new_fleet = self._create_fleet_for_ships([ship])
        self.empire.add_fleet(new_fleet)
```

If the fleet has only 1 ship and the user removes it, the source fleet becomes empty (0 ships). The code does not check `len(self.fleet.ships) > 1` before proceeding.

Similarly, `_on_remove_selected_ships` (line 250-274) has no guard against selecting all ships. The `MultiSelect` selection model allows selecting all rows.

**Impact:** An empty fleet is an invalid state that can cause `ZeroDivisionError` in speed calculation, `IndexError` in fleet name property, and undefined behavior in the turn engine. The turn engine likely assumes all fleets have at least one ship.

**Recommendation:** Add pre-removal validation: refuse to create a split if it would leave zero ships in the source fleet. This validation should live in the command handler (see CQ-001), not in the UI.

**Effort:** Simple (guard) / Medium (proper command with validation)

---

#### MAJOR: 63 Lines of Dead Comments Left in Production Code

**ID:** CQ-008
**Location:** `game/ui/screens/fleet_orders_window.py:341-391`
**Issue:** Lines 341-391 contain 50+ lines of stream-of-consciousness comments discussing how to handle the confirmation dialog event routing. These are design deliberation notes, not documentation:
```python
# Note: Handling the confirmation require listening for the confirmation event
# The StrategyScreen usually handles `UI_CONFIRMATION_DIALOG_CONFIRMED`
# But since we are a window, we can also bind a listener if we were the manager?
# Actually standard practice in pygame_gui is events bubble up.
# ...
# BETTER APPROACH:
# ...
# EASIEST:
# ...
```

These 50 lines of comments are thinking-out-loud notes that were never cleaned up. They sit between `show_clear_confirmation` and `handle_global_event`, cluttering the module.

**Impact:** Significant readability and maintenance cost. New developers reading this file must parse through deliberation notes to understand the actual implementation. These comments are misleading because the implementation was already decided -- they describe rejected alternatives.

**Recommendation:** Delete all deliberation comments (lines 341-391). Replace with a single docstring comment on `handle_global_event` explaining the event routing pattern chosen.

**Effort:** Simple

---

#### MAJOR: FleetReportWindow Holds Mutable References to Both Fleet and Empire

**ID:** CQ-009
**Location:** `game/ui/screens/fleet_report_window.py:46-47`
**Issue:** The constructor stores direct references to both the `Fleet` and `Empire` domain objects:
```python
self.fleet = fleet
self.empire = empire
```

These references enable all the mutation patterns found in CQ-001, CQ-004, and CQ-007. The window then uses `self.fleet` for reads (showing ship list, stats) and writes (removing ships), and `self.empire` for writes (adding new fleets, generating IDs).

A UI window should not hold a reference to the `Empire` domain object at all. Reads should go through the facade (DTOs), and writes should go through commands.

**Impact:** The window is tightly coupled to two domain objects, making it impossible to test in isolation without constructing full domain models. It also means the window can perform arbitrary mutations on the fleet and empire at any time.

**Recommendation:** Replace `self.empire` with `self.facade` and use commands for mutations. Replace `self.fleet` with a fleet ID and query DTOs for display.

**Effort:** Complex

---

#### MAJOR: Strategy Screen Exposes Session Internals via Properties

**ID:** CQ-010
**Location:** `game/ui/screens/strategy_screen.py:134-163`
**Issue:** The StrategyScreen exposes raw domain objects through convenience properties:
```python
@property
def galaxy(self): return self.session.galaxy
@property
def empires(self): return self.session.empires
@property
def player_empire(self): return self.session.player_empire
```

These properties make `session.galaxy`, `session.empires`, `session.player_empire`, `session.systems` directly accessible to any code that has a reference to the screen. Every sub-module (renderer, input handler, window manager) reaches through `self.scene.galaxy`, `self.scene.current_empire`, etc.

While the comment on line 131 says "External callers should use the facade," there is no enforcement. The properties exist and are widely used.

**Impact:** The facade is optional rather than mandatory. Any new code can freely bypass it by accessing `scene.galaxy` or `scene.empires`. The window manager (CQ-006) uses these properties to pass domain objects to every window.

**Recommendation:** Remove these properties over time. Sub-modules that need read access should use `self.scene.facade.get_*()` queries. Sub-modules that need write access should use `self.scene.facade.handle_command()`.

**Effort:** Complex (many call sites)

---

#### MAJOR: Window Manager Bypasses Facade for Command Dispatch

**ID:** CQ-011
**Location:** `game/ui/screens/strategy_window_manager.py:280-284`
**Issue:** The `open_orders_window` method creates a closure that reaches through to the session directly:
```python
def clear_orders_callback(fleet_id: int) -> None:
    from game.strategy.engine.commands import ClearFleetOrdersCommand
    cmd = ClearFleetOrdersCommand(fleet_id=fleet_id)
    self.scene.session.handle_command(cmd)
```

This bypasses `self.scene.facade.handle_command(cmd)` and goes directly to `self.scene.session.handle_command(cmd)`. The facade exists and provides `handle_command()` (see `strategy_session_facade.py:52-64`). The facade's `handle_command` is a thin wrapper today, but it's the designated entry point for UI-to-engine commands.

**Impact:** If the facade's `handle_command` is later extended with logging, rate-limiting, or validation decorators, this call site will miss all of them. It also sets a precedent for other code to bypass the facade.

**Recommendation:** Change to `self.scene.facade.handle_command(cmd)` or `self.scene._facade.handle_command(cmd)`.

**Effort:** Simple

---

### Minor

#### MINOR: Inconsistent Error Handling in Ship Removal

**ID:** CQ-012
**Location:** `game/ui/screens/fleet_report_window.py:235-248`
**Issue:** `_on_remove_ship` has two different code paths depending on whether `self.empire` is set:
- Without empire (line 238-240): Removes ship from fleet, no new fleet created. Ship is effectively destroyed/leaked.
- With empire (line 244-248): Removes ship and creates a new fleet.

The "no empire" path silently removes a ship without placing it anywhere. The ship is lost from the game. There's no logging or user feedback for this case.

**Impact:** If the window is ever opened without an empire reference (e.g., during testing or due to a bug), ships are silently destroyed instead of split into a new fleet.

**Recommendation:** Either always require an empire (remove the `if not self.empire` branch) or at minimum log a warning when a ship is removed without being placed in a new fleet.

**Effort:** Simple

---

#### MINOR: Magic Number for Fleet Speed in UI Code

**ID:** CQ-013
**Location:** `game/ui/screens/fleet_report_window.py:281`
**Issue:** `Fleet(new_fleet_id, self.fleet.owner_id, self.fleet.location, speed=0)` uses a hardcoded `speed=0`. While `add_ship()` triggers speed recalculation, the initial value of 0 is a magic number that could confuse readers. If `add_ship` ever stopped triggering recalculation, the fleet would have speed 0.

**Impact:** Minor readability concern. The semantic meaning of `speed=0` as "will be recalculated" is not obvious.

**Recommendation:** Use a named constant or add a comment. Better yet, move this to the engine where the constructor can be called correctly.

**Effort:** Simple

---

#### MINOR: Stale Order Count Detection Misses Content Changes

**ID:** CQ-014
**Location:** `game/ui/screens/fleet_orders_window.py:89-98`
**Issue:** The `update()` method only detects order list changes by comparing `len(fleet.orders)`:
```python
if len(self.fleet.orders) != self._last_order_count:
```

This misses reordering (which the window itself does!), order target changes, and order type mutations. If an external system modifies an order in-place (e.g., changes a MOVE target), the window won't detect it.

**Impact:** Low in practice since most order modifications go through this window. But if the engine or AI modifies orders during turn processing and the window is still open, the display could be stale.

**Recommendation:** Use a hash or version counter on the orders list, or refresh on every frame (orders lists are typically small).

**Effort:** Simple

---

#### MINOR: FleetOrdersWindow Stores Direct References to Order Objects

**ID:** CQ-015
**Location:** `game/ui/screens/fleet_orders_window.py:167,173-174`
**Issue:** Each row stores `'order_ref': order`, a direct reference to the `FleetOrder` domain object. The `deleted_history` list also stores `(index, order)` tuples holding domain objects. These references persist even after the order is removed from `fleet.orders`, preventing garbage collection.

**Impact:** Minor memory concern for long sessions. More importantly, the undo system relies on object identity -- if the engine replaces the orders list (e.g., during deserialization), the undo stack would restore stale objects.

**Recommendation:** Consider storing order data (type + target) instead of object references for the undo stack.

**Effort:** Simple

---

### Info

#### INFO: PROJ-207 Partial Migration Pattern

**ID:** CQ-016
**Location:** `game/ui/screens/fleet_orders_window.py:46-47,280-284`
**Issue:** PROJ-207 Phase 4 migrated the "Clear All" action to use the command pipeline via a callback. However, the individual order operations (move, delete, undo) were not migrated. This creates a partial migration where one operation goes through commands and three others directly mutate state.

**Impact:** Inconsistent patterns within the same file. Developers may assume all order operations go through commands (since one does), or they may copy the direct-mutation pattern for new operations.

**Recommendation:** Complete the migration by adding commands for all order operations, not just clear.

**Effort:** Medium

---

#### INFO: Window Manager Has Scene Reference Creating Bidirectional Coupling

**ID:** CQ-017
**Location:** `game/ui/screens/strategy_window_manager.py:53-61,175`
**Issue:** The window manager stores a `self.scene` reference and uses it to access `scene.current_empire`, `scene.galaxy`, `scene.session`, `scene.facade`, and `scene.on_navigate_to_hex_build`. This creates a bidirectional dependency: StrategyScreen owns StrategyUI, which owns StrategyWindowManager, which reaches back into StrategyScreen.

**Impact:** The window manager cannot be tested without constructing (or mocking) a full StrategyScreen. Changes to StrategyScreen's API break the window manager. The bidirectional coupling makes it harder to reason about data flow.

**Recommendation:** Pass specific dependencies (facade, callbacks) to the window manager constructor instead of the entire scene object.

**Effort:** Medium

---

#### INFO: Strategy Screen Uses Facade Inconsistently

**ID:** CQ-018
**Location:** `game/ui/screens/strategy_screen.py:82,122-127`
**Issue:** The StrategyScreen creates a facade (`self._facade = StrategySessionFacade(self.session)`) and passes it to `FleetOperations`, `ColonizationSystem`, and `SuperweaponOperations`. However, it also maintains direct `session` access and exposes it through properties. Some sub-modules use the facade (fleet_ops, colonization, superweapons) while others use direct session access (window manager, build queue, game state).

**Impact:** Inconsistent usage patterns. The facade adoption is partial -- about half the subsystems use it and half don't.

**Recommendation:** Track which sub-modules still bypass the facade and create migration tickets for each.

**Effort:** N/A (tracking issue)

---

## Top 5 Priority Issues

1. **CQ-001 (CRITICAL):** Fleet splitting logic in UI with no validation -- highest corruption risk, no command exists for this operation. Direct domain object construction in UI.

2. **CQ-002 (CRITICAL):** Direct order array mutation in FleetOrdersWindow -- three mutation methods bypass the command pipeline that already exists for the same domain concept.

3. **CQ-007 (MAJOR):** No empty-fleet guard -- removing all ships creates an invalid state that can crash the turn engine.

4. **CQ-006 (MAJOR):** Window manager passes live domain objects -- this is the structural enabler for all UI-layer bypasses. Fixing this would prevent future bypass regressions.

5. **CQ-005 (MAJOR):** Backward compatibility fallback violates project policy -- simple fix that eliminates a dead code path and enforces command pipeline usage.
