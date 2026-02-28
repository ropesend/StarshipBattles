# Phase 4: Strategy Core Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit tests for the core strategy layer screens: StrategyScreen, StrategyInputHandler (extending existing), and StrategyRenderer.
**Findings covered:** TCG-UI1-002, TCG-UI1-011, TCG-UI1-012
**Estimated tests:** ~80-100

---

## Task 4.1: StrategyScreen Core Tests [Complex]
**Finding:** TCG-UI1-002
**Source:** `game/ui/screens/strategy_screen.py` (834 lines, 26+ methods)
**Tests:** `tests/unit/ui/screens/test_strategy_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock session, facade, ui, renderer, input_handler, camera_nav

- [x] Create `tests/unit/ui/screens/test_strategy_screen.py`

**Initialization:**
- [x] Test `__init__` sets screen dimensions and creates sub-objects
- [x] Test initialization with existing session vs None session
- [x] Test initialization with input_mapper parameter

**Turn advancement:**
- [x] Test `advance_turn()` calls facade.advance_turn()
- [x] Test `advance_turn()` updates UI after turn
- [x] Test `advance_turn()` handles facade errors gracefully

**Menu option dispatch (extends test_strategy_menu_actions.py):**
- [x] Test `on_menu_option("design_workshop")` triggers scene_callback with "open_builder"
- [x] Test `on_menu_option("quit_to_menu")` shows confirmation dialog
- [x] Test `on_menu_option("settings")` (coming soon or actual handler)

**Fleet/planet selection:**
- [x] Test `on_fleet_selected()` sets `selected_fleet` and updates UI
- [x] Test `on_planet_selected()` sets `selected_planet` and updates UI
- [x] Test selection with None (deselect)

**Build queue interaction:**
- [x] Test `on_build_yard_click()` opens build queue screen
- [x] Test `on_colonize_click()` initiates colonization workflow

**Screen lifecycle:**
- [x] Test `update(dt)` delegates to renderer and sub-systems
- [x] Test `handle_event()` delegates to input_handler
- [x] Test `draw()` delegates to renderer

- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

**Notes:** Use bypass-init pattern from `test_strategy_menu_actions.py`. Set all sub-objects as MagicMock. StrategyScreen delegates to extracted modules, so tests focus on dispatch correctness.

---

## Task 4.2: StrategyInputHandler Core Coverage [Medium]
**Finding:** TCG-UI1-011
**Source:** `game/ui/screens/strategy_input_handler.py` (952 lines)
**Tests:** `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` (existing, extend) + `tests/unit/ui/screens/test_strategy_input_handler_core.py` (NEW)
**Mocks:** Mock scene, mock InputMapper

Existing tests cover: hotkey resolution via InputMapper (39 tests), transfer mode. Missing:

**Input mode transitions:**
- [x] Create `tests/unit/ui/screens/test_strategy_input_handler_core.py`
- [x] Test all input modes: NORMAL, MOVE, JOIN, TRANSFER, COLONIZE_TARGET, SUPERWEAPON_TARGET
- [x] Test mode transition guards: cannot enter MOVE without fleet selected
- [x] Test mode transition: entering new mode cancels previous mode
- [x] Test ESC key returns to NORMAL mode from any active mode

**Click handling:**
- [x] Test left-click on hex with fleet -> selects fleet
- [x] Test left-click on hex with planet -> selects planet
- [x] Test left-click on empty hex -> deselects
- [x] Test left-click in MOVE mode -> dispatches move command
- [x] Test left-click in COLONIZE_TARGET mode -> dispatches colonize

**Mouse/scroll events:**
- [x] Test mouse scroll dispatches to camera zoom
- [x] Test right-click drag initiates camera pan
- [x] Test middle-click behavior

**Edge cases:**
- [x] Test handle_event with non-keyboard/mouse event type -> ignored
- [x] Test handle_event with no fleet selected and fleet-requiring hotkey -> no-op
- [x] Test handle_event with build_queue_screen open (input blocked)

- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_core.py -v`

**Notes:** Follow existing fixture pattern (`mock_scene`, `mapper`, `_keydown` helper).

---

## Task 4.3: StrategyRenderer Tests [Medium]
**Finding:** TCG-UI1-012
**Source:** `game/ui/screens/strategy_renderer.py` (672 lines, 30+ methods)
**Tests:** `tests/unit/ui/screens/test_strategy_renderer.py` (NEW - base file) + existing `test_strategy_renderer_animation.py`
**Mocks:** Mock scene with camera, galaxy, systems, empires; mock asset_manager; mock pygame surfaces

- [x] Create `tests/unit/ui/screens/test_strategy_renderer.py`

**Initialization:**
- [x] Test `__init__` stores scene reference and initializes caches
- [x] Test `update(dt)` increments elapsed_time

**Coordinate conversion:**
- [x] Test hex-to-pixel conversion produces correct screen positions for known hex coords
- [x] Test rendering at different zoom levels (0.5x, 1.0x, 2.0x) scales positions correctly

**System rendering (mock-level):**
- [x] Test `_draw_systems()` iterates over scene.systems and draws each
- [x] Test system rendering skips systems outside camera viewport (culling)
- [x] Test system rendering draws star with correct color

**Fleet rendering (mock-level):**
- [x] Test `_draw_fleets()` iterates over scene fleets and draws each
- [x] Test fleet rendering draws fleet icon at correct hex position
- [x] Test move preview line rendering (`_draw_move_preview()`)

**Warp lane rendering:**
- [x] Test `_draw_warp_lanes()` draws lines between connected systems
- [x] Test warp lane rendering with no warp lanes (empty list)

**Animation:**
- [x] Test warp point rotation animation updates with elapsed time
- [x] Test animation state reset

**Asset loading:**
- [x] Test asset loading fallback when asset not found

- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_renderer.py tests/unit/ui/screens/test_strategy_renderer_animation.py -v`

**Notes:** Renderer takes a `scene` reference in __init__. Create mock scene with all required attributes (camera, systems, galaxy, empires, selected_fleet, etc.). Focus on logic paths, not pixel-perfect rendering.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All new tests passing
- [x] No regressions: `pytest tests/ -n 12` - 9277 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
