# PROJ-228 Phase 1: Scrollable Panel Infrastructure

## DUP-PAT-001: ScrollState Utility
- [ ] Design `ScrollState` class API (offset, max_offset, handle_mousewheel, clamp)
- [ ] Write unit tests for ScrollState
- [ ] Implement `ScrollState` in `game/ui/widgets/` or `game/ui/components/`
- [ ] Verify tests pass

## DUP-SCR-003: Scroll Pattern Migration
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/test_run_details.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/results_panel.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/screen_input_handler.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/dialogs.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/test_lab/json_viewer.py`
- [ ] Replace scroll_offset in `game/ui/screens/test_lab/renderer.py`
- [ ] Replace scroll_offset in `game/ui/screens/test_lab/viewmodel.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/setup_screen.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/battle_screen.py`
- [ ] Replace scroll_offset in `game/ui/screens/battle_state_viewer.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/screens/builder/weapons_panel.py`
- [ ] Replace MOUSEWHEEL in `game/ui/screens/formation_editor.py`
- [ ] Replace MOUSEWHEEL in `game/ui/screens/strategy_input_handler.py`
- [ ] Replace MOUSEWHEEL in `game/ui/screens/planet_list_window.py`
- [ ] Replace MOUSEWHEEL in `game/ui/screens/galaxy_test/screen.py`
- [ ] Replace MOUSEWHEEL in `game/ui/screens/empire_build_queue_window.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/panels/modifier_impact_grid.py`
- [ ] Replace scroll_offset in `game/ui/panels/battle_panels.py`
- [ ] Replace scroll_offset + MOUSEWHEEL in `game/ui/widgets/scrollable_json_panel.py`
- [ ] Replace MOUSEWHEEL in `game/ui/renderer/camera.py`
- [ ] Replace MOUSEWHEEL in `game/ui/research/research_scene.py`

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 1 items verified
