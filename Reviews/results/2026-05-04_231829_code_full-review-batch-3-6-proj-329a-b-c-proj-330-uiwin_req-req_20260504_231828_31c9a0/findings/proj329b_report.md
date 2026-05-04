# PROJ-329B Review Findings

## CRITICAL

*None found.*

## MAJOR

- **[M1] StarListWindow: Missing `self.virtual_table` placeholder in Stage 1 — same gap as MAJ-001** | `game/ui/screens/star_list_window.py:468` | `kill()` accesses `self.virtual_table` but the attribute is never initialized to `None` in Stage 1 (above `super().__init__()`). The MAJ-001 fix (commit `fc18cfc78`) added exactly this pattern to `EmpireBuildQueueWindow`: 8 widget-ref placeholders set to `None` in Stage 1 + `None` guard in `kill()`. `StarListWindow` has the `None` guard but forgets the placeholder. Under a `NullStarListWindowUiBuilder` bypass test (which exists at `tests/unit/ui/screens/test_star_list_window.py:155`), calling `kill()` would raise `AttributeError` on `self.virtual_table` before the `if self.virtual_table:` guard can evaluate. This is the identical pattern-level gap MAJ-001 closed.

- **[M2] SystemSelectionWindow: Missing `btn_confirm`/`btn_cancel` placeholders** | `game/ui/screens/system_selection_window.py:143,153` | `update()` accesses `self.btn_confirm.check_pressed()` and `self.btn_cancel.check_pressed()`, but neither attribute is initialized to `None` in Stage 1. Both are set only by the `SystemSelectionUiBuilder` in Stage 3. Under bypass with a Null-builder, any call to `update()` raises `AttributeError`. While `update()` is not `kill()`, the same root cause applies: widget-ref attributes accessed in lifecycle methods must carry a Stage-1 `None` placeholder when the builder may be swapped out.

- **[M3] SaveSelectionWindow: `update()` peeks `pygame.event.get()` outside the event loop** | `game/ui/screens/save_selection_window.py:432` | The `update()` method calls `pygame.event.get(pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED)` which drains global event queue events. This was present in the pre-refactor version as well (not a regression from PROJ-329B), but the two-stage construction now means `self.ui_manager` is a bare `MagicMock` under bypass tests — if `update()` were called, the `pygame.event.get()` call leaks mock-mode events into the test runner's global queue. Surfaces as a latent risk because the mock infrastructure now makes this call path reachable in more test scenarios. Recommend a follow-up: route confirmation-dialog handling through `process_event` instead of `update()` polling.

## PASS

- **Behavioral parity — EmpireBuildQueueWindow**. Production `__init__` sequence (cheap state → `super().__init__` → builder widgets) produces identical final attribute state as pre-refactor `super().__init__` first then inline widget construction. `process_event`, `update`, and `kill` logic is unchanged save for the `None` guard on `_virtual_table`, which is a no-op in production (the builder always sets it). No observable behavior difference.

- **Behavioral parity — SaveSelectionWindow**. Production `__init__` calls `SaveSelectionUiBuilder.build(self)` which is a 1:1 extraction of the old `_create_ui()` with identical layout math, widget types, and `disable()` calls. `_load_saves()` is called immediately after the builder in both versions. `process_event` and `update` logic are identical. No observable behavior difference.

- **Pattern §33 conformance — all 8 classes**. All 8 classes place cheap state + delegates above the bypass guard, accept an explicit `ui_builder` parameter defaulting to `None`, use the correct guard shape (`getattr(type(self), 'bypass_init', False)` for direct `UIWindow` subclasses; `getattr(self, '_window_init_bypassed', False)` for `StrategyModalWindow` subclasses after `super().__init__()`), and have no pygame_gui widget construction above the guard. The `StrategyModalWindow` subclasses all check `_window_init_bypassed` immediately after `super().__init__()` with no intervening code.

- **Mixed UIWindow base classes — DesignSelectorWindow, RaceBrowserDialog, SaveSelectionWindow**. All 3 correctly assign `self.ui_manager` in the bypass branch, set `self._window_init_bypassed = True`, return before `super().__init__()`, and do NOT touch `self.rect` (explicit warning comment in `SaveSelectionWindow` at line 136). The inline bypass guard shape matches `new_game_setup_screen.py` exactly.

- **Widget-ref placeholder discipline — EmpirePanelWindow, EventLogWindow**. `EmpirePanelWindow.kill()` only accesses `self.on_close_callback` (Stage 1). `EventLogWindow` sets `self.virtual_table`, `self.data_source`, `self.column_manager`, `self.sidebar` all to `None` in Stage 1 and guards `kill()` with `if self.virtual_table:`. Both correct.

- **Widget-ref placeholder discipline — DesignSelectorWindow, RaceBrowserDialog, SaveSelectionWindow**. None of these override `kill()`, so there are no widget-ref holes in the kill path. Inherited `UIWindow.kill()` handles cleanup.

- **MAJ-001 fix — EmpireBuildQueueWindow**. The `fc18cfc78` post-fix correctly added 8 placeholder attributes set to `None` in Stage 1 and a `None` guard in `kill()`. The `EmpireBuildQueueUiBuilder` overwrites all 8 in Stage 3, so production behavior is unchanged. Verified correct.

- **Bypass branch ui_builder dispatch**. All 8 classes handle the two-branch pattern correctly:
  - Bypass + `ui_builder is None`: no builder invoked (clean no-op).
  - Bypass + `ui_builder` supplied: builder invoked to populate widget slots (Mock-builder use case).
  - Production (no bypass): `(ui_builder or DefaultFooUiBuilder()).build(self)` always runs the production builder.
