# Phase 4: Strategy Core Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add unit tests for the core strategy layer screens: StrategyScreen, StrategyInputHandler (extending existing), and StrategyRenderer.
**Findings covered:** TCG-UI1-002, TCG-UI1-011, TCG-UI1-012
**Estimated tests:** ~80-100

---

## Task 4.1: StrategyScreen Core Tests [Complex]
**Finding:** TCG-UI1-002
**Source:** `game/ui/screens/strategy_screen.py` (834 lines, 26+ methods)
**Tests:** `tests/unit/ui/screens/test_strategy_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock session, facade, ui, renderer, input_handler, camera_nav

- [ ] Create `tests/unit/ui/screens/test_strategy_screen.py`

**Initialization:**
- [ ] Test `__init__` sets screen dimensions and creates sub-objects
- [ ] Test initialization with existing session vs None session
- [ ] Test initialization with input_mapper parameter

**Turn advancement:**
- [ ] Test `advance_turn()` calls facade.advance_turn()
- [ ] Test `advance_turn()` updates UI after turn
- [ ] Test `advance_turn()` handles facade errors gracefully

**Menu option dispatch (extends test_strategy_menu_actions.py):**
- [ ] Test `on_menu_option("design_workshop")` triggers scene_callback with "open_builder"
- [ ] Test `on_menu_option("quit_to_menu")` shows confirmation dialog
- [ ] Test `on_menu_option("settings")` (coming soon or actual handler)

**Fleet/planet selection:**
- [ ] Test `on_fleet_selected()` sets `selected_fleet` and updates UI
- [ ] Test `on_planet_selected()` sets `selected_planet` and updates UI
- [ ] Test selection with None (deselect)

**Build queue interaction:**
- [ ] Test `on_build_yard_click()` opens build queue screen
- [ ] Test `on_colonize_click()` initiates colonization workflow

**Screen lifecycle:**
- [ ] Test `update(dt)` delegates to renderer and sub-systems
- [ ] Test `handle_event()` delegates to input_handler
- [ ] Test `draw()` delegates to renderer

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

**Notes:** Use bypass-init pattern from `test_strategy_menu_actions.py`. Set all sub-objects as MagicMock. StrategyScreen delegates to extracted modules, so tests focus on dispatch correctness.

---

## Task 4.2: StrategyInputHandler Core Coverage [Medium]
**Finding:** TCG-UI1-011
**Source:** `game/ui/screens/strategy_input_handler.py` (952 lines)
**Tests:** `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` (existing, extend) + `tests/unit/ui/screens/test_strategy_input_handler_core.py` (NEW)
**Mocks:** Mock scene, mock InputMapper

Existing tests cover: hotkey resolution via InputMapper (39 tests), transfer mode. Missing:

**Input mode transitions:**
- [ ] Create `tests/unit/ui/screens/test_strategy_input_handler_core.py`
- [ ] Test all input modes: NORMAL, MOVE, JOIN, TRANSFER, COLONIZE_TARGET, SUPERWEAPON_TARGET
- [ ] Test mode transition guards: cannot enter MOVE without fleet selected
- [ ] Test mode transition: entering new mode cancels previous mode
- [ ] Test ESC key returns to NORMAL mode from any active mode

**Click handling:**
- [ ] Test left-click on hex with fleet -> selects fleet
- [ ] Test left-click on hex with planet -> selects planet
- [ ] Test left-click on empty hex -> deselects
- [ ] Test left-click in MOVE mode -> dispatches move command
- [ ] Test left-click in COLONIZE_TARGET mode -> dispatches colonize

**Mouse/scroll events:**
- [ ] Test mouse scroll dispatches to camera zoom
- [ ] Test right-click drag initiates camera pan
- [ ] Test middle-click behavior

**Edge cases:**
- [ ] Test handle_event with non-keyboard/mouse event type -> ignored
- [ ] Test handle_event with no fleet selected and fleet-requiring hotkey -> no-op
- [ ] Test handle_event with build_queue_screen open (input blocked)

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_core.py -v`

**Notes:** Follow existing fixture pattern (`mock_scene`, `mapper`, `_keydown` helper).

---

## Task 4.3: StrategyRenderer Tests [Medium]
**Finding:** TCG-UI1-012
**Source:** `game/ui/screens/strategy_renderer.py` (672 lines, 30+ methods)
**Tests:** `tests/unit/ui/screens/test_strategy_renderer.py` (NEW - base file) + existing `test_strategy_renderer_animation.py`
**Mocks:** Mock scene with camera, galaxy, systems, empires; mock asset_manager; mock pygame surfaces

- [ ] Create `tests/unit/ui/screens/test_strategy_renderer.py`

**Initialization:**
- [ ] Test `__init__` stores scene reference and initializes caches
- [ ] Test `update(dt)` increments elapsed_time

**Coordinate conversion:**
- [ ] Test hex-to-pixel conversion produces correct screen positions for known hex coords
- [ ] Test rendering at different zoom levels (0.5x, 1.0x, 2.0x) scales positions correctly

**System rendering (mock-level):**
- [ ] Test `_draw_systems()` iterates over scene.systems and draws each
- [ ] Test system rendering skips systems outside camera viewport (culling)
- [ ] Test system rendering draws star with correct color

**Fleet rendering (mock-level):**
- [ ] Test `_draw_fleets()` iterates over scene fleets and draws each
- [ ] Test fleet rendering draws fleet icon at correct hex position
- [ ] Test move preview line rendering (`_draw_move_preview()`)

**Warp lane rendering:**
- [ ] Test `_draw_warp_lanes()` draws lines between connected systems
- [ ] Test warp lane rendering with no warp lanes (empty list)

**Animation:**
- [ ] Test warp point rotation animation updates with elapsed time
- [ ] Test animation state reset

**Asset loading:**
- [ ] Test asset loading fallback when asset not found

- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_renderer.py tests/unit/ui/screens/test_strategy_renderer_animation.py -v`

**Notes:** Renderer takes a `scene` reference in __init__. Create mock scene with all required attributes (camera, systems, galaxy, empires, selected_fleet, etc.). Focus on logic paths, not pixel-perfect rendering.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests passing
- [ ] No regressions: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
