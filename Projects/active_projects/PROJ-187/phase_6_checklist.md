# Phase 6: WARP Order Implementation [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-187 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement the WARP order primitive so players can explicitly order fleets through specific warp points.

---

## Tasks

### Task 6.1: Add WARP handling to FleetNavigationService [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/unit/strategy/services/ -k "navigation"`

- [x] In `get_destination()`: handle `OrderType.WARP` — return the warp point hex as destination
- [x] In `compute_path()`: for WARP orders, path = [current_location, warp_point_hex, exit_hex]
- [x] In `compute_next_step()`: handle WARP same as MOVE for pathfinding
- [x] WARP target = HexCoord of warp point to enter. Navigation resolves exit point via galaxy warp index

**Notes:** Added `compute_path_for_warp()` and `_resolve_warp_exit()` methods. Updated `compute_next_step()` to handle warp transit when fleet is at warp point.

### Task 6.2: Add WARP handling to FleetMovementEngine [Simple]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/ -k "movement"`

- [x] In `collect_movements()`: treat WARP like MOVE (don't skip it — it's a movement order)
- [x] `apply_movement()` already handles warp detection via `hex_distance > 1` — no changes needed
- [x] Verify WARP is NOT in `ACTION_ORDER_TYPES` (it's in `MOVEMENT_ORDER_TYPES`)

**Notes:** WARP was already in MOVEMENT_ORDER_TYPES from Phase 1. No code changes needed.

### Task 6.3: Add WARP command and handler [Medium]
**Files:** `game/strategy/engine/commands.py`, `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/ -k "command"`

- [x] Create `IssueWarpCommand(fleet_id, warp_point_hex: HexCoord)` dataclass in commands.py
- [x] Create `WarpCommandHandler` that:
  - Validates warp point exists at target hex (via `galaxy._global_hex_warp_points`)
  - Validates fleet has warp capability (`fleet.can_use_warp()`)
  - If fleet is not at warp point, auto-queues: MOVE(warp_point_hex) -> WARP(warp_point_hex)
  - If fleet is at warp point, queues: WARP(warp_point_hex)
- [x] Register `'IssueWarpCommand'` -> `WarpCommandHandler` in `create_default_registry()`

**Notes:** Handler properly validates warp capability and warp point existence before queuing orders.

### Task 6.4: Add WARP to FleetOrder serialization [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k "fleet and serial"`

- [x] Verify WARP order target (HexCoord) is handled by existing `hasattr(target, 'to_dict')` path in `to_dict()`
- [x] Verify deserialization handles HexCoord target via existing HexCoord path in `from_dict()`
- [x] If no special handling needed, just confirm with a test

**Notes:** Existing serialization handles WARP targets via HexCoord path (line 90-92 already mentions WARP in comment). Added roundtrip test.

### Task 6.5: Update UI order display [Simple]
**Files:** `game/ui/screens/fleet_orders_window.py`, `game/ui/screens/strategy_detail_formatter.py`
**Tests:** Manual visual check

- [x] Add WARP order type to order display formatting
- [x] Show "Warping through [hex coords]" or "Warp to [System Name]"

**Notes:** Added WARP case to `_format_orders()` in strategy_detail_fmt.py. Displays "WARP through {hex}".

### Task 6.6: Write WARP integration tests [Medium]
**File:** `tests/integration/strategy/test_warp_orders.py` (new)
**Tests:** `pytest tests/integration/strategy/test_warp_orders.py`

- [x] Test: Fleet at warp point issues WARP, moves through on movement tick
- [x] Test: Fleet NOT at warp point auto-queues MOVE then WARP
- [x] Test: WARP consumes warp resources
- [x] Test: Fleet without warp capability rejects WARP order
- [x] Test: WARP order serialization round-trip

**Notes:** Created comprehensive test file with 8 tests covering command handling, navigation, and serialization.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (12,459 passed, 1 skipped)
- [x] WARP order works end-to-end: command -> queue -> execute on tick -> fleet moves through warp
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
