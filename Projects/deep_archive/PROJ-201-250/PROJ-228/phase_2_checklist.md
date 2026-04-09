# PROJ-228 Phase 2: Screen & Window Base Classes

## DUP-PAT-005: BaseScene
- [x] Analyze common lifecycle patterns across IScene implementors:
  - `game/ui/screens/menu_scene.py`
  - `game/ui/screens/keybindings_scene.py`
  - `game/ui/screens/test_lab/screen.py`
  - `game/ui/screens/strategy_screen.py`
  - `game/ui/screens/setup_screen.py`
  - `game/ui/screens/workshop_screen.py`
  - `game/ui/screens/battle_screen.py`
  - `game/ui/research/research_scene.py`
- [x] Decision: **No extraction recommended.** Each scene stores width/height and creates a UIManager, but 90%+ of each scene is unique logic. The common code is 3-5 lines of boilerplate. Extracting a BaseScene would add coupling and inheritance overhead for negligible duplication reduction. The IScene protocol already provides the contract.

## DUP-PAT-006 / DUP-SCR-012: CallbackWindow
- [x] Analyze callback/event wiring patterns across UIWindow subclasses
- [x] Decision: **No extraction recommended.** UIWindow subclasses already inherit from `pygame_gui.elements.UIWindow`. The callback patterns vary: some use `on_selection_callback`, some use `on_close_callback`, some use button callbacks. No consistent shared boilerplate to extract beyond what UIWindow already provides.

## DUP-PAT-007 / DUP-SCR-004: SelectionDialog
- [x] Analyze selection dialog pattern across:
  - `game/ui/screens/fleet_selection_window.py`
  - `game/ui/screens/planet_selection_window.py`
  - `game/ui/screens/system_selection_window.py`
  - `game/ui/screens/design_selector_window.py`
- [x] Decision: **No extraction recommended.** Selection windows share the pattern of UIWindow + UISelectionList + Confirm/Cancel, but differ significantly in details (PlanetSelection has a detail panel and "Any Planet" button, FleetSelection is simpler, SystemSelection has hex coordinates, DesignSelector has ship design previews). A base class would need so many hooks/overrides that it would be more complex than the current straightforward implementations.

## Completion
- [x] Run full test suite: `pytest tests/ -n 12` — 13467 passed, 2 skipped
- [x] All Phase 2 items verified — all items analyzed, no extractions needed
