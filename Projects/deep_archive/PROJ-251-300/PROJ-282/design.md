# PROJ-282: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current FleetBattleSetupScreen responsibilities (1172 lines)

Per Combat Lab/Battle Setup Explore agent's review:
- **Lines 91-179** — `__init__` — instantiates state, registries, complex toggles dict, references to all panels
- **Lines 180-627** — three `_build_*_panel` methods constructing UI elements for left/center/right panels
- **Lines 650-774** — event handler dispatch (`handle_event`) with inline `hasattr(element, '_fleet_index')` style checks
- **Lines 824-972** — fleet/TF/squadron CRUD: create, duplicate, delete operations. `_duplicate_task_force` (854-912) and `_duplicate_squadron` (925-958) duplicate ship-cloning boilerplate
- **Lines 1022-1084** — battle launch: calls `build_manual_battle_spec`, syncs complex toggles to state, fires callback
- **Throughout** — `self._complex_toggles` dict (line ~118) holds toggle state that should live on `BattleSetupState`

### Symptoms of god-class

- Single class accounts for ~10% of all UI screen code in the project
- Adding a new toggle, button, or fleet operation requires touching this file (no natural extension point)
- Tests must mock the whole screen to test any one behavior
- The `_complex_toggles` dict is a private implementation detail of the screen — but it's *data* (selected complexes) and should belong to `BattleSetupState` so save/load handles it

### TestLab MVVM exemplar

[game/ui/screens/test_lab/screen.py](../../../game/ui/screens/test_lab/screen.py) and its sibling files demonstrate the pattern to follow:
- `screen.py` — `TestLabScreen(IScene)` — lifecycle, layout, delegate wiring (~150 lines target)
- `view_model.py` — `TestLabViewModel` — derived view state (filtered scenarios, selection, expanded groups)
- `renderer.py` — drawing
- `input_handler.py` — event dispatch
- `controller.py` — mutation operations + service orchestration

This project applies the same shape to Battle Setup.

## Architecture

### Target file structure

```
game/ui/screens/battle_setup/
├── __init__.py                     # re-exports BattleSetupScreen alias
├── screen.py                       # FleetBattleSetupScreen(IScene) — thin shell
├── view_model.py                   # BattleSetupViewModel
├── renderer.py                     # BattleSetupRenderer (orchestrates panels)
├── input_handler.py                # BattleSetupInputHandler
├── controller.py                   # BattleSetupController
├── fleet_hierarchy_editor.py       # FleetHierarchyEditor
├── spec_compiler.py                # UNCHANGED — already exists, well-structured
└── panels/
    ├── __init__.py
    ├── left_panel.py               # fleet/complex selection
    ├── center_panel.py             # fleet hierarchy tree
    └── right_panel.py              # design library
```

### Responsibility split

**screen.py — `FleetBattleSetupScreen(IScene)` (~150 lines target):**
- Implements the `IScene` protocol (`handle_event`, `update`, `draw`, `handle_resize`)
- Owns `BattleSetupState` instance
- Wires up ViewModel, Renderer, InputHandler, Controller
- Delegates everything else

**view_model.py — `BattleSetupViewModel`:**
- Derived view state: selected fleet index, expanded TF/SQ nodes, current panel scroll positions, currently-highlighted design in library
- Pure state object — no behavior
- Tests construct directly

**renderer.py — `BattleSetupRenderer`:**
- Orchestrates the three panel renderers
- Owns layout calculation (panel widths, positions for the 2560×1600+ display)

**panels/{left,center,right}_panel.py — per-panel renderers:**
- Each builds its panel's UI elements from `state` + `view_model`
- One file per panel — keeps each renderer focused

**input_handler.py — `BattleSetupInputHandler`:**
- Translates pygame_gui events into Controller method calls
- No direct mutation — calls Controller methods

**controller.py — `BattleSetupController`:**
- Mutation operations on `BattleSetupState` (fleet CRUD, ship CRUD, complex toggle, side add/remove)
- Save/load (delegates to existing `setup_data_io.py` if it exists)
- Battle launch: calls `build_manual_battle_spec` + the registered launch callback
- Holds reference to `BattleSetupState` and emits "state changed" signal so view model can refresh

**fleet_hierarchy_editor.py — `FleetHierarchyEditor`:**
- Pure helper for fleet/TF/squadron CRUD
- Owns the ship-cloning logic that `_duplicate_task_force` and `_duplicate_squadron` currently duplicate
- Stateless — operates on a `Fleet` argument

### Data model change: `_complex_toggles` → `BattleSetupState`

Currently:
```python
# battle_setup_screen.py
self._complex_toggles: Dict[str, bool] = {}  # complex_id → enabled
# ... synced to state.system_complexes / state.sector_complexes at battle launch
```

After:
```python
# battle_setup_state.py — new field
class BattleSetupSide:
    system_complex_toggles: Dict[str, bool] = field(default_factory=dict)
    sector_complex_toggles: Dict[str, bool] = field(default_factory=dict)
```

The screen no longer holds toggle state. Save/load already covers it (via existing `to_dict`/`from_dict`).

### Anti-rebloat documentation (Phase 9)

Add to [docs/03_CONVENTIONS.md](../../../docs/03_CONVENTIONS.md):

> **UI screen line budgets**
>
> UI screen classes (anything implementing `IScene`) should stay under 300 lines.
> Logic for mutation, derived view state, rendering, and event handling should live in
> sibling delegate classes (Controller, ViewModel, Renderer, InputHandler) following the
> MVVM pattern established by `TestLabScreen` and `FleetBattleSetupScreen`.
>
> If you find yourself adding a method to a screen class that has more than 300 lines,
> stop and identify which delegate it belongs in.

This is a discoverable rule that reviewers can cite. It's deliberately a soft limit — the
goal is to make rebloat visible, not to enforce a brittle hard cap.

### Migration order (matches phases)

1. **Audit** — read current screen end-to-end; map each method to its target delegate
2. **State model fix** — move `_complex_toggles` to `BattleSetupState` first (separate concern, easy win)
3. **Extract delegates** in dependency order — ViewModel (pure data) → Renderer (uses VM) → InputHandler (calls Controller) → Controller (uses State + emits signals)
4. **Extract FleetHierarchyEditor** — kills the existing duplication
5. **Slim screen** — final cleanup, screen becomes a thin shell
6. **Document** — add line-budget convention
7. **Smoke** — manual verification

Each phase is independently testable and reviewable.

## Key Patterns to Reuse
- **TestLab MVVM** — [game/ui/screens/test_lab/](../../../game/ui/screens/test_lab/) is the exemplar
- **IScene protocol** — [game/core/protocols.py](../../../game/core/protocols.py) defines the screen contract
- **Pygame_gui event dispatch** — existing patterns in BattleScreen and StrategyScreen for `UI_BUTTON_PRESSED` / `UI_DROPDOWN_MENU_CHANGED` handling

## Dependencies & Risks
1. **Pygame_gui element lifecycle** — recreating panels on resize / state change is a known footgun. The current screen probably handles this; preserve the pattern. **Mitigation:** Phase 1 audit documents the lifecycle pattern; carry it through to the new Renderer
2. **Save/load compatibility** — moving `_complex_toggles` onto state changes the serialized shape. **Mitigation:** add migration in `BattleSetupState.from_dict` that reads legacy keys if present (per [memory: "Save files are disposable"], could also just discard legacy saves — escalate to user if any are in active use)
3. **Test coverage today is unknown** — if FleetBattleSetupScreen has poor test coverage, refactor risk is high. **Mitigation:** Phase 1 includes test-coverage audit
4. **N-team support (PROJ-275) is recent** — must verify the decomposition preserves dynamic side count (2-8). **Mitigation:** explicit smoke checklist for 2/3/8-side cases
5. **Pygame_gui panel reconstruction performance** — adding indirection may add per-frame cost. **Mitigation:** profile if slowdown reported during smoke; optimize then
6. **Multiple parallel UI changes** — if PROJ-281 is in flight, BattleScreen changes might affect Battle Setup→Battle transition wiring. **Mitigation:** sequencing prevents this (PROJ-281 lands first)

## Opportunities Discovered
- The MVVM extraction creates natural seams for future features (e.g. "save/load setup presets" becomes a Controller method, not a screen method)
- `FleetHierarchyEditor` could later serve other screens that edit fleet hierarchy (e.g. fleet-orders window)
- The line-budget convention can apply project-wide once established here

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
