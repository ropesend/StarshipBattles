# PROJ-207 Scope Gap Analysis Report

**Date:** 2026-02-27 (v2 - comprehensive re-analysis)
**Reviewer:** Claude Opus 4.6 (Scope Gap Analyst)
**Project:** PROJ-207 - Fleet Order System Unification
**Method:** Systematic code review of all 10 in-scope files plus adjacent integration points (DTOs, game session load path, test files, interface contracts), cross-referenced against all 14 planned tasks across 5 phases.

---

## Summary

Found **10 gaps** across all 5 phases. 3 are bugs that could cause data corruption or crashes. 4 are consistency gaps where the plan addresses one instance of a problem pattern but misses related instances. 3 are integration/test concerns that need attention for the plan to succeed.

| Severity | Count |
|----------|-------|
| Bug (data corruption/crash risk) | 3 |
| Consistency gap (same pattern, missed instance) | 4 |
| Integration/test concern | 3 |

---

## Findings

### SG-001: GameSession.from_dict() Not in Scope but Required by Task 1.1

**Location:** `game/strategy/engine/game_session.py:298-330`
**Related Goal:** Fix save/load data loss bugs (ODM-001)
**Gap Description:** Task 1.1 says "Call `resolve_order_references()` in the game session load path, after all empires and galaxy are fully restored." This call site is in `GameSession.from_dict()` (line ~322, after empires are loaded). However, `game_session.py` is NOT listed in the project's in-scope files. An implementer following scope strictly would write the `resolve_order_references()` method on Fleet but never wire it into the load path.

After `session.empires` is populated (line 311-321), a new step is needed to iterate all empires' fleets and call `fleet.resolve_order_references(session.galaxy, session.empires)` on each. Without this call, the `_fleet_ref` and `_planet_ref` marker dicts produced by `Fleet.from_dict()` are never resolved back to actual Fleet/Planet objects.

**Impact:** ODM-001 fix is incomplete. The resolution method exists but is never called. Fleet/planet references remain as dicts after loading. Every downstream consumer of `order.target` (order processors, DTO builders, UI renderers) will encounter dicts where they expect Fleet/Planet objects, causing AttributeError crashes or silent data corruption.
**Proposed Resolution:** Add `game/strategy/engine/game_session.py` to the in-scope file list in plan.md, specifically for the `from_dict()` method. No new task needed -- this is a scope omission for Task 1.1.
**Effort:** Simple

---

### SG-002: IMPLODE_PLANET Colony Removal Only Checks Attacking Empire

**Location:** `game/strategy/engine/superweapon_order_processor.py:99-104`
**Related Goal:** Close superweapon validation gaps (VC-001, VC-002, VC-007)
**Gap Description:** `process_implode_planet()` removes the destroyed planet from `empire.colonies` (the attacking empire) but NOT from the planet's actual owning empire. Line 104 has a comment acknowledging this: `# Note: For enemy planets, we'd need to iterate empires`. The `process_stellerate_star()` method at line 176 correctly iterates all empires because it receives an `empires` parameter. But `process_implode_planet()` does not receive `empires` and therefore cannot clean up the victim empire's colony list. The same bug exists in `process_create_dyson_sphere()` at lines 446-450.

**Impact:** After imploding an enemy planet, the enemy empire retains a stale reference to the destroyed planet in its `colonies` list. Any code iterating enemy colonies (growth, production, maintenance, UI) could crash with AttributeError or process a ghost planet. The `galaxy.unregister_planet()` call removes the planet from the galaxy, creating an inconsistency between galaxy state and empire state.

**Proposed Resolution:** Add to Phase 2 (superweapon execution fixes). Add `empires` parameter to `process_implode_planet()` and `process_create_dyson_sphere()` signatures. Update both to iterate all empires for colony removal like `process_stellerate_star()` does. Update the callers in `fleet_order_processor.py` (lines 650, 660) to pass `empires`.

**Effort:** Simple

---

### SG-003: Superweapon Processors Don't Remove Empty Fleets From Empire

**Location:** `game/strategy/engine/superweapon_order_processor.py:116, 293, 368, 507`
**Related Goal:** Remove duplicated code and dead lifecycle methods (EP-002)
**Gap Description:** When a superweapon consumes the only ship in a fleet (`fleet_consumed=True`), the `process_implode_planet`, `process_open_warp_point`, `process_close_warp_point`, and `process_create_dyson_sphere` methods set `fleet_consumed=True` in the result but do NOT call `empire.remove_fleet(fleet)`. The flag propagates up through `FleetOrderProcessor.process_end_turn_orders()` to `ActionExecutionEngine._execute_action()` which returns it, but the caller in TurnEngine does not act on this flag. By contrast, `process_colonize()` at line 266 and `process_join_fleet()` at line 163 both properly call `empire.remove_fleet(fleet)`.

**Impact:** After a superweapon consumes a fleet (single-ship fleet executing IMPLODE_PLANET, OPEN_WARP_POINT, CLOSE_WARP_POINT, or CREATE_DYSON_SPHERE), an empty fleet (0 ships) remains in the empire's fleet list. This ghost fleet shows up in UI fleet lists, consumes iteration cycles, and could cause issues in fleet-related logic that doesn't guard against empty fleets.

**Proposed Resolution:** Add to Phase 5 Task 5.3 (superweapon template extraction). When extracting the template method `_execute_superweapon()`, include fleet cleanup as part of the common skeleton: if `len(fleet.ships) == 0` after ship removal, call `empire.remove_fleet(fleet)`. This aligns with the pattern used by COLONIZE and JOIN_FLEET.

**Effort:** Simple (natural part of template extraction)

---

### SG-004: FleetOrdersWindow delete_order and move_order Bypass Command Pipeline

**Location:** `game/ui/screens/fleet_orders_window.py:271-318`
**Related Goal:** Bring FleetOrdersWindow into the command pipeline (CP-001, CP-002)
**Gap Description:** Task 4.2 addresses the `clear_orders()` bypass at line 386, but `FleetOrdersWindow` has three other direct fleet.orders manipulations that also bypass the command pipeline:
- `move_order()` (line 277): Directly swaps `fleet.orders[index]` and `fleet.orders[new_index]`
- `delete_order()` (line 288): Directly calls `fleet.orders.pop(index)`
- `undo_delete()` (line 309): Directly calls `fleet.orders.insert(original_index, order)`

These have the same category of concern as CP-001 (direct fleet manipulation bypassing command logging/validation).

**Impact:** Order reordering, individual deletion, and undo are not logged through the command pipeline. While less critical than clear_all (which CP-001 addresses), they represent the same pattern of bypass. If command logging or validation is later added to the pipeline, these operations will be invisible.

**Proposed Resolution:** Note for later. These are lower priority than CP-001 since they're single-order manipulations with undo support. Document as a known bypass in Task 4.2 notes. A future project could create `ReorderFleetOrderCommand` and `DeleteFleetOrderCommand` classes.

**Effort:** Medium (requires new command types, non-trivial undo semantics)

---

### SG-005: ClearOrdersCommandHandler Uses Direct Assignment Instead of fleet.clear_orders()

**Location:** `game/strategy/engine/command_handlers.py:472-474`
**Related Goal:** Eliminate dual execution paths and inconsistent error handling (EP-001, EP-005)
**Gap Description:** `ClearOrdersCommandHandler.execute()` manually sets `fleet.orders = []` and `fleet.path = []` instead of calling `fleet.clear_orders()`. This is functionally equivalent today but creates an inconsistency: the canonical method for clearing orders (`Fleet.clear_orders()`) is bypassed by the one handler that should be the authoritative clear path.

Additionally, `fleet.orders = []` creates a new list object, while `fleet.clear_orders()` calls `self.orders.clear()` which mutates the existing list. If any external code holds a reference to `fleet.orders` (e.g., `FleetOrdersWindow` storing a reference), the `= []` approach silently detaches that reference.

**Impact:** If `fleet.clear_orders()` is ever enhanced (e.g., to fire events, reset execution_progress on orders, or log), the command handler will silently diverge. This is especially relevant given Task 5.1's discussion of making lifecycle methods authoritative.

**Proposed Resolution:** Add to Phase 4 Task 4.2 notes (natural adjacency to the clear_orders pipeline work). Change lines 473-474 to call `fleet.clear_orders()` instead of direct assignment.

**Effort:** Simple (1-line change)

---

### SG-006: Task 4.2 References session.dispatch_command() Which Does Not Exist

**Location:** Phase 4 checklist, Task 4.2
**Related Goal:** Bring FleetOrdersWindow into the command pipeline (CP-001)
**Gap Description:** Task 4.2 shows example code `self.session.dispatch_command(cmd)` but the actual GameSession method is `session.handle_command(command)` (line 194 of `game_session.py`). Additionally, `FleetOrdersWindow.__init__()` only accepts `(rect, manager, fleet, input_mapper)` -- it has no `session` reference at all. The task notes this ("If session not available, thread it through from the parent screen") but the threading path is not spelled out.

The session is available on `StrategyScreen` and could be passed via the window manager, or a callback closure could be used to avoid direct session dependency in the UI layer.

**Impact:** The task as written will cause the implementer to either use the wrong method name or waste time searching for `dispatch_command`. Without a clear threading path for the session reference, the implementer may make suboptimal architectural choices.

**Proposed Resolution:** Update Task 4.2 description to reference `session.handle_command()` and explicitly note the session threading path: `StrategyScreen -> StrategyWindowManager -> FleetOrdersWindow`. The simplest approach is to pass a callback closure from StrategyScreen that calls `self.session.handle_command()`, avoiding direct session dependency in the UI layer.

**Effort:** Simple (documentation correction + plumbing)

---

### SG-007: Task 5.4 Rename Has 8+ Test Files Referencing process_end_turn_orders

**Location:** Multiple test files
**Related Goal:** Remove duplicated code and dead lifecycle methods (AU-002)
**Gap Description:** Task 5.4 renames `process_end_turn_orders()` to `execute_action_order()` and lists updating the IOrderProcessor interface and callers. However, the task does not enumerate the test impact. There are 8 test files with references to `process_end_turn_orders`:
1. `tests/unit/strategy/test_fleet_order_processor.py`
2. `tests/integration/strategy/test_colonize_logic.py`
3. `tests/unit/strategy/interfaces/test_engine_interfaces.py`
4. `tests/unit/strategy/mocks/mock_engines.py`
5. `tests/unit/test_advanced_fleet_orders.py`
6. `tests/unit/strategy/turn_engine/test_dependency_injection.py`
7. `tests/unit/strategy/engine/test_action_execution_engine.py`
8. `tests/unit/strategy/engine/test_build_order_processor.py`

The mock engine at `tests/unit/strategy/mocks/mock_engines.py` implements the `IOrderProcessor` interface and must be renamed too.

**Impact:** If the implementer doesn't update all 8 test files, tests will fail with `AttributeError: MockOrderProcessor has no attribute 'execute_action_order'` or similar. The task says "Update all callers" but doesn't quantify the test surface area.

**Proposed Resolution:** Add explicit list of test files to Task 5.4 notes. This is documentation only -- no new task needed, but the implementer needs to know the scope.

**Effort:** Simple (documentation update; the actual renames are mechanical)

---

### SG-008: CLOSE_WARP_POINT Target Serialization Uses Fragile 'raw' Path

**Location:** `game/strategy/data/fleet.py:103-104` (to_dict) and `game/strategy/data/fleet.py:469-471` (from_dict)
**Related Goal:** Fix save/load data loss bugs (ODM-001, ODM-003)
**Gap Description:** `CLOSE_WARP_POINT` orders have a string target (destination system name). In `to_dict()`, this hits the generic `else` fallback at line 103: `target_data = {'type': 'raw', 'value': str(self.target)}`. In `from_dict()`, this deserializes via the `type: 'raw'` path at line 470: `target = target_data['value']`. While the round-trip is currently correct (string -> str(string) -> string), this is fragile:
- No explicit serialization path for CLOSE_WARP_POINT targets
- If the target were ever a non-string type, `str()` would lose type information
- The `raw` type was intended as a last-resort fallback, not a production path

Phase 1 fixes COLONIZE (ODM-003) and fleet_ref/planet_ref (ODM-001) serialization but doesn't address this related serialization weakness.

**Impact:** Low immediate risk since string -> str(string) is idempotent, but this becomes a maintenance hazard. If someone changes the CLOSE_WARP_POINT target format, saves will silently corrupt.

**Proposed Resolution:** Add a dedicated serialization path for CLOSE_WARP_POINT in `to_dict()`, e.g., `{'type': 'warp_dest', 'value': self.target}` with a corresponding `from_dict()` handler. Add to Phase 1 since it's adjacent to the other serialization fixes there.

**Effort:** Simple

---

### SG-009: Task 3.2 Changes Error Behavior But Stranded Case May Need Different Treatment

**Location:** `game/strategy/engine/fleet_movement_engine.py:151-154`
**Related Goal:** Eliminate inconsistent error handling (EP-005)
**Gap Description:** Task 3.2 changes all three movement failure cases from `fleet.clear_orders()` to `fleet.pop_order()`. However, the three failure modes have different semantics:

1. **Stranded (no fuel, line 153):** Fleet has no resources for ANY movement. Subsequent MOVE orders in the queue also cannot execute. The fleet is truly stuck. Preserving orders here means the `ActionExecutionEngine` will start processing the next order (e.g., a COLONIZE), which will fail validation because the fleet is at the wrong location, and be silently discarded. The player gets a worse outcome: their COLONIZE order is destroyed one tick later instead of immediately.

2. **Warp blocked (no capability, line 165):** Fleet tried to warp but lacks capability. Normal MOVE orders can still work. Preserving subsequent orders makes sense.

3. **Warp resources (insufficient, line 170):** Fleet has warp capability but not enough resources. Normal MOVE orders can still work. Preserving subsequent orders makes sense.

The task treats all three cases identically, but the stranded case arguably should keep `clear_orders()` to avoid false hope and silent order loss.

**Impact:** In the stranded case, the behavioral change doesn't help the player. Their subsequent orders are preserved for one tick then fail validation and are discarded anyway, just with less transparency.

**Proposed Resolution:** Refine Task 3.2 to differentiate between the three failure modes:
- Stranded (no fuel, line 153): Consider keeping `clear_orders()` since fleet can't move at all
- Warp blocked (no capability, line 165): Use `pop_order()` -- fleet can still move normally
- Warp resources (insufficient, line 170): Use `pop_order()` -- fleet can still move normally
Add this design question to decisions.md for explicit resolution. Add tests verifying that preserved action orders (after a MOVE pop) fail gracefully on the next tick rather than entering an infinite loop.

**Effort:** Simple (design decision + test)

---

### SG-010: SuperweaponOrderProcessor Instantiated Fresh On Every Call

**Location:** `game/strategy/engine/fleet_order_processor.py:647`
**Related Goal:** Remove duplicated code (AU-005)
**Gap Description:** In `process_end_turn_orders()` at line 647, a new `SuperweaponOrderProcessor()` is instantiated every time a superweapon order is processed: `proc = SuperweaponOrderProcessor()`. The processor is stateless (its `__init__` is a no-op `pass`), so this works but is wasteful and will be amplified when Task 5.4 converts the dispatch chain to a registry. The template method extraction in Task 5.3 should consider whether the processor should be a singleton held by `FleetOrderProcessor` rather than instantiated per-call.

**Impact:** Minor performance waste. More importantly, if Task 5.3's template method adds state (e.g., a validator cache), per-call instantiation would discard that state. The registry pattern in Task 5.4 naturally resolves this by holding handler references.

**Proposed Resolution:** Add note to Task 5.3 or 5.4: when building the `_action_handlers` registry (Task 5.4), instantiate `SuperweaponOrderProcessor` once in `FleetOrderProcessor.__init__()` and reference it in the handler dict. This naturally resolves with the registry pattern.

**Effort:** Simple

---

## Cross-Reference: Goals vs Tasks Coverage

| Goal | Covered By Tasks | Gaps Found |
|------|------------------|------------|
| Fix save/load data loss (ODM-001, ODM-003) | Task 1.1, 1.2 | SG-001 (missing call site scope), SG-008 (CLOSE_WARP_POINT fragile serialization) |
| Close superweapon validation gaps (VC-001, VC-002, VC-007) | Task 2.1, 2.2, 2.3 | SG-002 (colony removal bug), SG-003 (empty fleet cleanup) |
| Eliminate dual paths / inconsistent errors (EP-001, EP-005) | Task 3.1, 3.2 | SG-009 (stranded vs warp error differentiation) |
| Bring BUILD/FleetOrdersWindow into pipeline (CP-001, CP-002) | Task 4.1, 4.2, 4.3 | SG-004 (delete/move also bypass), SG-005 (handler uses direct assignment), SG-006 (wrong API name) |
| Remove dead code / boilerplate (EP-002, EP-004, AU-002, AU-004, AU-005) | Task 5.1-5.5 | SG-007 (test scope), SG-010 (processor instantiation) |

---

## Recommended Priority for Addressing Gaps

### Must fix (bugs / correctness):
1. **SG-001** - GameSession.from_dict() not in scope (ODM-001 fix incomplete without it)
2. **SG-002** - Enemy planet colony cleanup (data corruption risk)
3. **SG-003** - Empty fleet removal after superweapon (ghost fleet)

### Should fix (plan accuracy):
4. **SG-006** - Wrong API name in Task 4.2 (implementer confusion)
5. **SG-007** - Test file list for Task 5.4 rename
6. **SG-009** - Error handling differentiation for stranded case

### Nice to have (quality):
7. **SG-005** - ClearOrdersHandler should use fleet.clear_orders()
8. **SG-008** - CLOSE_WARP_POINT dedicated serialization
9. **SG-010** - Processor instantiation optimization
10. **SG-004** - FleetOrdersWindow remaining bypasses (note for later)
