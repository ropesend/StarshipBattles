# FEAT-08: Fleet Join Order — Target Selection Dialog and Fleet ID Display

## Description
Two improvements to the fleet join order ('J' hotkey):

### 1. Target Fleet Selection Dialog
When the user presses 'J' and clicks a hex containing multiple fleets, a selection dialog should appear listing the available fleets so the user can choose which fleet to join. Currently, `get_fleet_at_hex()` in `strategy_fleet_ops.py` silently takes `fleets[0]` without prompting. The facade's `get_fleets_at_hex()` already returns all fleets at a hex, so the data is available — a selection UI is needed.

The existing `PlanetSelectionWindow` (using `UISelectionList`) can serve as a reference pattern for the fleet picker.

### 2. Fleet ID in Order Queue
The orders window (`fleet_orders_window.py`) currently displays a join order without clearly identifying the target fleet. It should display the target fleet's ID so the player knows exactly which fleet they are joining.

## Priority
Medium

## Status
Awaiting Confirmation

## Analysis Report

### Architecture Impact
- **Layers affected:** UI only. No strategy/simulation/core changes needed.
- **Cross-layer dependencies introduced:** None. Uses existing `StrategySessionFacade.get_fleets_at_hex()` and `IssueJoinFleetCommand`.
- **All data structures already support this feature:**
  - `FleetInfo` DTO has `fleet_id`, `owner_id`, `flagship_name`, `ship_count`
  - `IssueJoinFleetCommand` accepts `fleet_id` and `target_fleet_id`
  - `FleetOrder` stores Fleet reference as `target` for JOIN_FLEET orders
  - `FleetOrderInfo` DTO has `target_id` field

### Dependency Map
**Files requiring changes (4-7):**
1. `game/ui/screens/strategy_fleet_ops.py` — Modify `handle_join_designation()` to return `{'type': 'choice', 'fleets': [...]}` when multiple fleets at hex
2. `game/ui/screens/strategy_click_dispatcher.py` — Add join choice flow (mirror move pattern at lines 93-114)
3. `game/ui/screens/strategy_window_manager.py` — Add `prompt_fleet_selection()` method
4. `game/ui/screens/strategy_ui.py` — Add `prompt_fleet_selection()` proxy method
5. Possibly new file: `game/ui/screens/fleet_selection_window.py` (or lightweight dialog in window_manager)

**Files that need NO changes (already correct):**
- `game/strategy/facade/strategy_session_facade.py` — `get_fleets_at_hex()` already returns all fleets
- `game/strategy/engine/commands.py` — `IssueJoinFleetCommand` already exists
- `game/strategy/engine/command_handlers.py` — `JoinCommandHandler` works correctly
- `game/strategy/data/order_types.py` — `OrderType.JOIN_FLEET` already defined

**Part 2 finding:** `fleet_orders_window.py` already displays `"JOIN Fleet {f_id}"` at line 198-200. The fleet ID display may already be working — needs verification.

### Similar Patterns Found
- **Primary reference:** `PlanetSelectionWindow` (`game/ui/screens/planet_selection_window.py`) — UIWindow with UISelectionList, callback-driven, Confirm/Cancel buttons
- **Alternative reference:** `SystemSelectionWindow` (`game/ui/screens/system_selection_window.py`) — simpler list picker with display mapping
- **Integration pattern:** `strategy_window_manager.py:prompt_planet_selection()` (lines 441-456) shows how to launch selection dialogs
- **Choice result pattern:** `handle_move_designation()` already returns `{'type': 'choice'}` when multiple fleets at hex — same pattern needed for join

### Scope Assessment
**Rating: Simple-to-Moderate**
- 4-7 files modified, 1 possible new file
- Single layer (UI only)
- Follows well-established existing patterns
- Estimated ~100-200 LOC new code
- **Recommendation: Feature (not Project)**

### Documentation Discrepancies
- **Undocumented pattern:** The "Selection Dialog" pattern (PlanetSelectionWindow, SystemSelectionWindow, callback flow) is well-established in code but not documented in `docs/02_PATTERNS.md`
- **No code-vs-docs violations** in the affected area

## Requirements Context

**Dialog display format:** Fleet ID + flagship name + ship count (e.g., "Fleet 5 — FSS Enterprise (3 ships)")
**Orders window (Part 2):** Already sufficient — current `"JOIN Fleet {id}"` display is fine. No changes needed.
**Single fleet behavior:** Auto-join immediately when only one valid target fleet at hex. Only show dialog when multiple valid targets.
**Filtering:** Show only valid targets (own-empire fleets, excluding the selected/source fleet). Don't show invalid targets.

## Complexity Assessment

**Lines of Code Affected:** ~100-150 new, ~20 modified
**Files Requiring Changes:** 4-5 (all UI layer)
**New Abstractions Needed:** None — follows existing PlanetSelectionWindow / prompt_move_choice patterns
**Test Infrastructure:** Existing UI test patterns sufficient
**Cross-Layer Changes:** None — pure UI layer

**Rating: Moderate** (4-5 files, single layer, existing patterns, ~120-170 LOC)

## Implementation Strategy

### Sub-task 1: Modify `handle_join_designation()` to detect multiple fleets
- File: `game/ui/screens/strategy_fleet_ops.py`
- When `get_fleets_at_hex()` returns multiple valid targets (same owner, excluding source fleet), return `{'type': 'choice', 'fleets': filtered_list}`
- When only one valid target, proceed with current auto-join behavior

### Sub-task 2: Create fleet selection dialog
- New file: `game/ui/screens/fleet_selection_window.py`
- Follow `PlanetSelectionWindow` pattern (UIWindow + UISelectionList)
- Display entries as `"Fleet {id} — {flagship_name} ({ship_count} ships)"`
- Confirm/Cancel buttons, callback-driven

### Sub-task 3: Add dialog integration to window manager
- File: `game/ui/screens/strategy_window_manager.py` — add `prompt_fleet_selection()`
- File: `game/ui/screens/strategy_ui.py` — add proxy method

### Sub-task 4: Handle choice result in click dispatcher
- File: `game/ui/screens/strategy_click_dispatcher.py` — add fleet choice handling in `_handle_join_mode_click()`, mirroring the move choice pattern

### Sub-task 5: Tests
- Test fleet selection dialog construction and callback
- Test handle_join_designation returns choice when multiple fleets
- Test single fleet auto-joins without dialog

## Work Log
- 2026-03-22: Created from QA Session 20260322_051459.
- 2026-03-22: Deep Investigation — Phase 1 (Agent Swarm) complete. Feature is UI-only, Simple-to-Moderate complexity. All backend infrastructure ready.
- 2026-03-22: Implementation complete. All 1786 UI tests + 84 fleet ops tests passing. Changes:
  - `game/ui/screens/fleet_selection_window.py` (new) — Fleet picker dialog with UISelectionList
  - `game/ui/screens/strategy_fleet_ops.py` — `handle_join_designation()` now filters valid targets and returns choice dict for multiple; extracted `execute_join()`
  - `game/ui/screens/strategy_click_dispatcher.py` — `_handle_join_mode_click()` handles choice result with dialog callback
  - `game/ui/screens/strategy_window_manager.py` — Added `prompt_fleet_selection()` method
  - `game/ui/screens/strategy_ui.py` — Added `prompt_fleet_selection()` proxy
  - `tests/integration/ui/test_fleet_ops_facade.py` — Updated join tests for new API, added `test_join_returns_choice_for_multiple_valid_targets`
