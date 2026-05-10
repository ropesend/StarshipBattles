# PROJ-228 Phase 1: Scrollable Panel Infrastructure

## DUP-PAT-001: ScrollState Utility
- [x] Design `ScrollState` class API (offset, max_offset, handle_mousewheel, clamp)
- [x] Write unit tests for ScrollState
- [x] Implement `ScrollState` in `game/ui/widgets/scroll_state.py`
- [x] Verify tests pass (33 tests)

## DUP-SCR-003: Scroll Pattern Migration
- [x] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/test_run_details.py`
- [x] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/results_panel.py`
- [x] N/A: `game/ui/screens/test_lab/screen_input_handler.py` — delegates to viewmodel.scroll(), no local scroll_offset
- [x] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/dialogs.py`
- [x] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/json_viewer.py`
- [x] N/A: `game/ui/screens/test_lab/renderer.py` — reads viewmodel.scroll_offset (a property), no local state
- [x] N/A: `game/ui/screens/test_lab/viewmodel.py` — pygame-free ViewModel with EventBus integration, intentionally separate
- [x] Replace scroll_offset in `game/ui/screens/setup_screen.py`
- [x] N/A: `game/ui/screens/battle_screen.py` — MOUSEWHEEL delegates to ui.handle_scroll(); dead stats_scroll_offset attr
- [x] Replace scroll_offset in `game/ui/screens/battle_state_viewer.py` (calls scroll.reset() on panels)
- [x] N/A: `game/ui/screens/builder/weapons_panel.py` — scroll_offset computed from pygame_gui UIVerticalScrollBar percentage
- [x] N/A: `game/ui/screens/formation_editor.py` — MOUSEWHEEL used for camera zoom, not scrolling
- [x] N/A: `game/ui/screens/strategy_input_handler.py` — MOUSEWHEEL delegated to camera, not scrolling
- [x] N/A: `game/ui/screens/planet_list_window.py` — MOUSEWHEEL delegated to VirtualTable scrollbar
- [x] N/A: `game/ui/screens/galaxy_test/screen.py` — MOUSEWHEEL delegated to camera, not scrolling
- [x] N/A: `game/ui/screens/empire_build_queue_window.py` — MOUSEWHEEL delegated to VirtualTable scrollbar
- [x] Replace scroll_offset + MOUSEWHEEL in `game/ui/panels/modifier_impact_grid.py`
- [x] Replace scroll_offset in `game/ui/panels/battle_panels.py`
- [x] Replace scroll_offset + MOUSEWHEEL in `game/ui/widgets/scrollable_json_panel.py`
- [x] N/A: `game/ui/renderer/camera.py` — MOUSEWHEEL used for camera zoom, not scrolling
- [x] N/A: `game/ui/research/research_scene.py` — MOUSEWHEEL delegated to camera, not scrolling

**Notes:** Files marked N/A either use MOUSEWHEEL for zoom (not scroll), delegate to other systems (camera, VirtualTable, viewmodel), or have scroll driven by pygame_gui scrollbar widgets. Only files with local scroll_offset + MOUSEWHEEL handling were migrated to ScrollState.

## Completion
- [x] Run full test suite: `pytest tests/ -n 12` — 13467 passed, 2 skipped
- [x] All Phase 1 items verified
