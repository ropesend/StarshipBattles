# FEAT-07: Add 'W' Hotkey for Explicit Warp Orders

## Description
Add a 'W' hotkey on the strategy map that activates a warp order mode. When active, clicking on a warp point issues an explicit warp order to the selected fleet — moving the fleet to the warp point and then warping through it.

The backend infrastructure already exists:
- `OrderType.WARP` is defined in `order_types.py`
- `IssueWarpCommand` / `WarpCommandHandler` in `command_handlers.py` handles validation, auto-queuing a MOVE to the warp point if needed, and queuing the WARP order
- `FleetCapabilityCalculator.can_use_warp()` checks warp capability

What's needed:
1. Add `FLEET_WARP` to `InputAction` enum in `input_actions.py`, mapped to 'W'
2. Add a `WARP_TARGET` input mode in `strategy_fleet_command_router.py`
3. Handle the click dispatch in `strategy_click_dispatcher.py` to find the warp point at the clicked hex and issue `IssueWarpCommand`
4. Gate the hotkey on fleet warp capability — if the selected fleet is not warp-capable, the order should not be queued (show feedback to the user)

## Priority
Medium

## Status
Awaiting Confirmation

## Analysis Report

### Architecture Impact
- **Layers affected:** Core (enum addition only) and UI (input routing, click dispatch)
- **Strategy layer:** Untouched — all backend infrastructure already exists (IssueWarpCommand, WarpCommandHandler, FleetCapabilityCalculator.can_use_warp())
- **Cross-layer communication:** UI issues IssueWarpCommand via StrategySessionFacade.handle_command() — follows existing CQRS-lite pattern exactly
- **Layer compliance:** All dependencies flow downward (UI→Strategy→Core) ✓

### Dependency Map
**Files requiring changes (4-5 production files):**
1. `game/core/input_actions.py` — Add `FLEET_WARP` enum + ACTION_DISPLAY_NAMES + ACTION_GROUPS
2. `game/ui/screens/strategy_fleet_command_router.py` — Add FLEET_WARP handler in handle_fleet_action(), add 'WARP_TARGET' to cancel mode list
3. `game/ui/screens/strategy_click_dispatcher.py` — Add 'WARP_TARGET' to _mode_handlers dict + implement _handle_warp_target_click()
4. `game/ui/screens/strategy_input_handler.py` — Add 'WARP_TARGET' to context filter tuple (line ~112)
5. `data/default_keybindings.json` — Add "fleet.warp": {"key": "K_w", "modifiers": []} (K_w with no modifiers is available; Ctrl+W is already open_warp_point)

**Backend (NO changes needed — already complete):**
- `game/strategy/engine/commands.py:299` — IssueWarpCommand exists
- `game/strategy/engine/command_handlers.py:576` — WarpCommandHandler exists (validates capability, auto-queues MOVE if needed)
- `game/strategy/data/fleet_capability_calculator.py:171` — can_use_warp() exists
- `game/strategy/data/order_types.py:21` — OrderType.WARP exists
- `game/strategy/data/galaxy.py:172` — _global_hex_warp_points O(1) lookup exists

**Blast radius:** ~5 production files, ~4-6 test files, ~55-90 LOC production + ~80-120 LOC tests

### Similar Patterns Found
The codebase has a well-established **hotkey → input mode → click dispatch → command** pattern used by:
- FLEET_MOVE → 'MOVE' mode → _handle_move_mode_click → IssueMoveCommand
- FLEET_COLONIZE → 'COLONIZE_TARGET' mode → _handle_colonize_mode_click → IssueColonizeCommand
- FLEET_OPEN_WARP_POINT → 'OPEN_WARP_TARGET' mode → _handle_open_warp_click → QueueOpenWarpPointMissionCommand
- FLEET_CLOSE_WARP_POINT → 'CLOSE_WARP_TARGET' mode → _handle_close_warp_click → QueueCloseWarpPointMissionCommand

The warp order implementation follows this pattern exactly. No new patterns or abstractions needed.

**Key implementation details from pattern analysis:**
- FleetCommandRouter.handle_fleet_action() checks fleet selected, sets input_mode string, logs debug
- ClickModeDispatcher uses dict-based dispatch table (_mode_handlers) for O(1) lookup
- Click handlers call operations subsystems, issue commands via facade, return to 'SELECT' mode
- Right-click always cancels mode → 'SELECT'
- Input mode must be added to context filter tuple in strategy_input_handler.py for "fleet" context to remain active during targeting

### Scope Assessment
**Rating: Simple** (1-3 files core changes, single layer primary impact, existing patterns, <100 LOC production)

- ✓ Self-contained to UI layer (plus 1 Core enum entry)
- ✓ Reuses 100% of existing backend
- ✓ Follows established input/dispatch patterns exactly
- ✓ No architectural changes, no new patterns, no new services
- ✓ No cross-layer violations or side effects
- ✓ No documentation updates needed (backend already documented)

### Documentation Discrepancies
**None found.** Code follows documented patterns in docs/02_PATTERNS.md (CQRS-lite, Facade, CommandHandlerRegistry) precisely.

## Requirements Context

**Capability gating:** Silently ignore 'W' keypress if selected fleet cannot use warp (no WarpJump ability). Do not show error message; key simply does nothing.

**Edge case handling (Standard):**
- Click on non-warp hex: log warning, stay in WARP_TARGET mode (let user try again)
- Click on valid warp point: issue IssueWarpCommand, return to SELECT mode
- Right-click: cancel mode, return to SELECT
- Fleet already has warp order queued: allowed (WarpCommandHandler handles validation)
- Fleet already at warp point: allowed (WarpCommandHandler handles this case)

**Behavior:** Purely additive. The W hotkey adds an explicit warp option alongside existing auto-warp behavior. No changes to how auto-warp-on-move works.

**Visual feedback:** Include a move preview line from fleet to cursor while in WARP_TARGET mode (same pattern as MOVE mode in strategy_renderer.py). This is part of the initial implementation, not a follow-up.

## Complexity Assessment

**Rating: Simple-to-Moderate**

| Dimension | Estimate |
|-----------|----------|
| Files requiring changes | 5-6 production files |
| Layers touched | Core (1 enum), UI (4-5 files) |
| New LOC (production) | ~60-90 lines |
| New LOC (tests) | ~80-120 lines |
| New abstractions | None |
| Cross-layer changes | No |
| Test infrastructure | Existing fixtures sufficient |

Bumped from Simple to Simple-to-Moderate due to including visual feedback (renderer changes).

## Implementation Strategy

**Ordered implementation steps (TDD):**

1. **Add FLEET_WARP to InputAction enum** (`game/core/input_actions.py`)
   - Add `FLEET_WARP = "fleet.warp"` to enum
   - Add to `ACTION_DISPLAY_NAMES`
   - Add to `ACTION_GROUPS["Fleet Commands"]`
   - Test: verify enum exists and has correct properties

2. **Add default keybinding** (`data/default_keybindings.json`)
   - Add `"fleet.warp": {"key": "K_w", "modifiers": []}` (plain W is available; Ctrl+W = open_warp_point)

3. **Add WARP_TARGET mode activation** (`game/ui/screens/strategy_fleet_command_router.py`)
   - Add `elif action == InputAction.FLEET_WARP:` in `handle_fleet_action()`
   - Gate on `selected_fleet` AND `selected_fleet.capabilities.can_use_warp()` — silently ignore if either fails
   - Set `self.input_mode = 'WARP_TARGET'`
   - Add `'WARP_TARGET'` to FLEET_CANCEL_MODE condition tuple
   - Test: W key with warp-capable fleet → WARP_TARGET mode; W key without fleet → no-op; W key with non-warp fleet → no-op

4. **Add context filter update** (`game/ui/screens/strategy_input_handler.py`)
   - Add `'WARP_TARGET'` to the input mode tuple in `_handle_keydown_mapped()` context filter

5. **Add click dispatch handler** (`game/ui/screens/strategy_click_dispatcher.py`)
   - Add `'WARP_TARGET': self._handle_warp_target_click` to `_mode_handlers`
   - Implement `_handle_warp_target_click()`:
     - Left click: resolve hex, check for warp point, issue IssueWarpCommand via facade, return to SELECT on success, stay in WARP_TARGET on invalid hex
     - Right click: cancel → SELECT
   - Test: click on warp point → command issued; click on non-warp hex → stays in mode; right-click → SELECT

6. **Add visual feedback** (`game/ui/screens/strategy_renderer.py`)
   - Add rendering for WARP_TARGET mode similar to MOVE preview line
   - Draw line from fleet position to mouse cursor while in WARP_TARGET mode
   - Test: manual verification (visual rendering)

7. **Run full test suite** (`pytest tests/ -n 12`)

**Reusable code identified:**
- MOVE mode click handler pattern (strategy_click_dispatcher.py)
- MOVE preview line rendering (strategy_renderer.py)
- Superweapon mode activation pattern (strategy_fleet_command_router.py)
- IssueWarpCommand already exists (strategy/engine/commands.py)

## Work Log
- 2026-03-22: Created from QA Session 20260322_051459.
- 2026-03-22: Deep dive Phase 1 complete — 4-agent swarm analysis. Feature is Simple complexity, follows established patterns exactly. All backend exists; only UI wiring needed.
- 2026-03-22: Deep dive Phase 2-4 complete — User interview, complexity assessment, implementation strategy. Simple-to-Moderate rating (visual feedback included). Ready for implementation.
- 2026-03-22: Implementation complete. All 6 steps done. 10 new tests pass. Full suite: 13,340 passed (1 pre-existing failure in test_build_queue_queue_data_source unrelated to this feature).
