# PROJ-228 Phase 2: Screen & Window Base Classes

## DUP-PAT-005: BaseScene
- [ ] Analyze common lifecycle patterns across IScene implementors:
  - `game/ui/screens/menu_scene.py`
  - `game/ui/screens/keybindings_scene.py`
  - `game/ui/screens/test_lab/screen.py`
  - `game/ui/screens/strategy_screen.py`
  - `game/ui/screens/setup_screen.py`
  - `game/ui/screens/workshop_screen.py`
  - `game/ui/screens/battle_screen.py`
  - `game/ui/research/research_scene.py`
- [ ] Design `BaseScene` class with shared lifecycle
- [ ] Write tests for BaseScene
- [ ] Implement BaseScene in `game/ui/`
- [ ] Migrate scene classes to use BaseScene
- [ ] Verify all scene tests pass

## DUP-PAT-006 / DUP-SCR-012: CallbackWindow
- [ ] Analyze callback/event wiring patterns across UIWindow subclasses
- [ ] Design `CallbackWindow` base class
- [ ] Write tests for CallbackWindow
- [ ] Implement CallbackWindow
- [ ] Migrate applicable windows to use CallbackWindow
- [ ] Verify all window tests pass

## DUP-PAT-007 / DUP-SCR-004: SelectionDialog
- [ ] Analyze selection dialog pattern across:
  - `game/ui/screens/fleet_selection_window.py`
  - `game/ui/screens/planet_selection_window.py`
  - `game/ui/screens/system_selection_window.py`
  - `game/ui/screens/design_selector_window.py`
- [ ] Design `SelectionDialog` base class
- [ ] Write tests for SelectionDialog
- [ ] Implement SelectionDialog
- [ ] Migrate selection dialogs to use base class
- [ ] Verify all selection dialog tests pass

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 2 items verified
