---
protocol: interagent-discussion/v1
revision: 2
author: codex
status: draft
supersedes: uiwindow_mvvm_refactor_plan_r001.md
created_at_utc: 2026-05-04T04:23:26Z
---

# UIWindow MVVM Refactor Plan

## Consensus Direction

Use a two-stage construction pattern for UIWindow classes, then apply MVVM depth class-by-class.

The goal is not pure MVVM everywhere and not a universal panel registry. The goal is production-readable UI code whose cheap state/delegate layer can be constructed in tests without a real pygame_gui window shell.

## Existing Pattern Read

The local MVVM precedent is pragmatic:

- `docs/02_PATTERNS.md` Pattern #8 and `docs/03_CONVENTIONS.md` section 2.4 define Controller, ViewModel, Renderer, InputHandler, panel-factory, and helper delegates as the preferred shape for complex UI.
- `game/ui/screens/battle_setup/screen.py` is the cleanest structural exemplar: the screen wires state, view_model, renderer, controller, and input_handler, then delegates behavior through small protocol-like surfaces and property shims.
- `game/ui/screens/workshop_screen.py` is useful precedent but not the structural target; it is still a large composition-heavy screen.
- Therefore the screen/window can remain the local composition root. For complex classes, delegate construction should go through a small default factory/bundle for readability and test injection. For small modals, a row model plus renderer is often clearer than a full MVVM stack.

## Core Construction Pattern

Every refactored UIWindow class should separate these phases:

1. Cheap state and dependency/delegate setup. No `pygame_gui` element construction.
2. UIWindow shell initialization. This calls `super().__init__` in production, or uses `bypass_init` in tests.
3. Widget-tree construction through a per-class UI builder/renderer.

For direct UIWindow subclasses:

```python
def __init__(self, rect, manager, ..., *, ui_builder=None, delegate_factory=None):
    self._init_state(...)
    self._init_widget_refs()
    self._delegates = (delegate_factory or DefaultDelegateFactory()).build(self)

    if getattr(type(self), "bypass_init", False):
        self.ui_manager = manager
        self.rect = rect
        self._window_init_bypassed = True
        return

    super().__init__(rect, manager, ...)
    (ui_builder or PygameFooUiBuilder()).build(self)
```

For `StrategyModalWindow`, update the base bypass path so subclasses receive a minimal usable shell:

```python
if getattr(type(self), "bypass_init", False):
    self._window_manager = window_manager
    self.ui_manager = resolved_manager
    self.rect = resolved_rect
    self._window_init_bypassed = True
    return
```

Subclasses can then initialize cheap fields, call `super().__init__`, and return before layout/widget construction when `_window_init_bypassed` is true.

## Widget Reference Policy

Use explicit placeholder initialization, not lazy properties.

- `_init_widget_refs()` should assign the canonical widget slots to `None` or empty lists/dicts.
- This makes the bypassed object honest: widget tree absent, cheap delegates present.
- Tests that need clickable/show-hide widget behavior should use a `MockFooUiBuilder`, not per-test manual wiring.
- Tests that exercise only delegate/state behavior can use a `NullFooUiBuilder` that leaves slots empty.

For RaceSetup specifically:

- `NullRaceSetupUiBuilder`: no-op builder for delegate-only tests.
- `MockRaceSetupUiBuilder`: fills `step_panels`, `tab_buttons`, `btn_save`, `btn_cancel`, `btn_randomize`, `btn_randomize_all`, `error_label`, and panel/gallery slots with MagicMocks matching the old helper's expectations.
- Production builder wraps the current `_create_ui()` flow.

This keeps widget mocks centralized and prevents the old 100+ lines of `__new__` helper wiring from reappearing one test at a time.

## Cheap Delegate Boundary

A collaborator is cheap for this refactor if its constructor does not create pygame_gui elements or require a live display.

It may store a screen/window reference and may later draw or build widgets when one of its methods is called. `RaceSetupRenderer(screen=self)` qualifies: construction is cheap; drawing methods are not.

The practical test is constructor behavior, not lifetime purity. ViewModels should remain pygame-free. Controllers and renderers may know about UI-facing callbacks and screens where the existing pattern already does that, but widget creation belongs in builders/renderers, not in ViewModel constructors.

## Class-by-Class Application

| Class | Recommendation |
|---|---|
| `RaceSetupScreen` | PROJ-325 proof of concept. Use `DefaultRaceSetupDelegateFactory` returning a `RaceSetupDelegates` bundle (`view_model`, `renderer`, `controller`, `llm_service`, `input_handler`). Extract `_create_ui()` behind `RaceSetupUiBuilder`. Initialize widget refs explicitly. Tests should use `bypass_init` plus `MockRaceSetupUiBuilder` or `NullRaceSetupUiBuilder`, with real cheap delegates by default. Do not move `RaceConfig` ownership into the ViewModel in this pass; the controller currently owns mutation and that matches the tests. |
| `NewGameSetupScreen` | Real MVVM split, after RaceSetup. Add `NewGameSetupViewModel` for player count, galaxy type, system count, player races, and active modal state. Add `NewGameSetupController` for save-name validation, config building, race-modal callbacks, and start/cancel flow. Use a UI builder for pygame widgets. |
| `FleetReportWindow` | Already mostly decomposed via `FleetListViewModel`, `FleetDataSource`, `VirtualTable`, and sidebar. Extract layout construction into `FleetReportLayoutBuilder`; add a small action controller only if remove/split behavior remains hard to test. |
| `OrdersWindow` | Light refactor only. Use a pure order-row description model plus `OrdersListRenderer`. Keep callbacks simple. Full MVVM is ceremony here. |
| `TransferDialog` | Separate deep refactor. Split pending-transfer state and row data into a ViewModel, facade queries and `IssueTransferCommand` emission into a controller, and grid/dropdown widgets into a renderer. Add focused tests around pending math and command issuance before moving UI code. |
| `BuildQueueListWindow` | Very small. Extract pure row collection/formatting and a simple renderer; no full MVVM stack needed. |
| `BuildQueueScreen` / `WorkshopScreen` | Outside the UIWindow-unblock sequence. `BuildQueueScreen` already uses PanelFactory/Renderer/Controller. `WorkshopScreen` is a later UI-wide cleanup if the user wants all UI brought closer to the modern pattern. |

## PROJ-325 Phase 3 Acceptance Criteria

1. `RaceSetupScreen.__init__` follows the two-stage pattern: cheap state/delegates before the bypass point, UIWindow shell behind `bypass_init`, widget construction behind a builder.
2. `RaceSetupScreen` constructed with `with bypass_init(RaceSetupScreen): make_ui_widget(..., ui_builder=MockRaceSetupUiBuilder())` has `race_config`, `is_editing`, `race_library`, `race_registry`, `_asset_loader`, `_view_model`, `_renderer`, `_controller`, `_input_handler`, and `_llm_service` populated.
3. The old `_make_race_setup_screen` helper in `tests/unit/ui/screens/test_race_setup_screen.py` no longer patches `RaceSetupScreen.__init__` or manually assigns the delegate graph. The helper LOC delta is measured in the project notes, not asserted inside pytest.
4. Widget slots needed by existing tests are supplied by `MockRaceSetupUiBuilder`, not repeated per test.
5. All existing `tests/unit/ui/screens/test_race_setup_screen.py` tests pass after migration.
6. The resulting constructor structurally resembles `BattleSetupScreen.__init__`: delegate wiring is compact, behavior lives on delegates, and legacy property shims remain only where needed for compatibility with current tests/callers.
7. Do not document the new pattern in `docs/02_PATTERNS.md` until the proof of concept has landed and survived targeted tests.
8. If RaceSetup PoC grows beyond the PROJ-325 Phase 3 stop condition already documented in `Projects/active_projects/PROJ-325/design.md`, stop and spin out the remaining work rather than ballooning the project.

## Project Sequence

1. PROJ-325 Phase 3: RaceSetupScreen proof of concept.
   - Write the failing construction test first.
   - Implement two-stage constructor, delegate factory/bundle, and RaceSetup UI builders.
   - Migrate the RaceSetup helper and targeted tests.

2. PROJ-328A: StrategyModalWindow shell and low/medium modals.
   - Update base bypass shell.
   - Apply light builders to `BuildQueueListWindow`, `OrdersWindow`, and `FleetReportWindow`.

3. PROJ-328B: NewGameSetupScreen MVVM split.

4. PROJ-328C: TransferDialog deep split.

5. Optional later project: WorkshopScreen and broader UI consistency if the user wants MVVM beyond the UIWindow blocker.

## Estimate

Three focused sessions is plausible only for RaceSetup plus the smallest modal windows. With NewGameSetupScreen, TransferDialog, tests, and docs included, use 5-8 focused LLM sessions as the expectation. WorkshopScreen would be additional.

## What Not To Do

- Do not claim a panel registry removes the need for `bypass_init`.
- Do not create one universal `PanelRegistry`, `WindowFactory`, or global MVVM protocol for all target classes.
- Do not force MVVM purity where a row model plus renderer is clearer.
- Do not move pygame imports or widget references into ViewModels.
- Do not keep delegate construction as a long inline block for RaceSetup/NewGame; use a small default factory/bundle while still allowing the screen to remain the local composition root.
- Do not convert RaceSetup/FleetReport unit coverage wholesale to integration tests.
- Do not let bypass return a bare object as the final state.
