# PROJ-328 UIWindow MVVM Rollout — Agent Review Report

## Summary

6 classes reviewed: `StrategyModalWindow` (base), `BuildQueueListWindow`,
`OrdersWindow`, `FleetReportWindow`, `NewGameSetupScreen`, `TransferDialog`.
The first 4 pass all core checks. Two findings for `TransferDialog` (behavioral
regression) and `NewGameSetupScreen` (incomplete MVVM extraction).

---

## Findings

### MAJOR FND-001: TransferDialog `_on_confirm` always closes window (behavioral regression)

**File:** `game/ui/screens/transfer_dialog.py:372-378`

**Description:** The post-refactor `_on_confirm` wraps `controller.confirm_pending()` in
`try/finally: self.kill()`, so the dialog now closes unconditionally on confirm.
The pre-refactor (`909bfbecf^`) had two **early-return** paths that kept the
dialog open:

1. `if not self._current_source or not self._current_target: return` — no kill
2. "Transfer between two non-fleet entities not supported." — `return`, no kill

The `finally` guarantee is correct for the dispatch-failure case (PROJ-321..328
audit S1.2), but it also swallows the benign early-exit paths. When no source or
target is selected (or both endpoints are planets/colonies), the dialog now
closes instead of staying open for user correction.

**Recommendation:** Move the `kill()` out of `finally` and gate it on a success
flag returned by the controller, or add an early-return guard before the
try/finally:

```python
def _on_confirm(self) -> None:
    if self.view_model.current_source is None or self.view_model.current_target is None:
        return
    try:
        self._controller.confirm_pending()
    finally:
        self.kill()
```

---

### MAJOR FND-002: NewGameSetupScreen widget construction not extracted from screen class

**File:** `game/ui/screens/new_game_setup_ui_builder.py:37-38`

**Description:** The production builder `NewGameSetupUiBuilder.build()` is a
one-line pass-through:

```python
def build(self, screen: "NewGameSetupScreen") -> None:
    screen._create_ui()
```

The actual widget construction code (`_create_ui`, `_create_empire_inputs`,
`_update_empire_visibility`, `_update_race_display`) — approximately 400 lines
of pygame_gui widget construction — remains on `NewGameSetupScreen`. The builder
is a thin seam rather than a real extraction.

This violates the intent of Pattern §33 (UI Widget Test Factory): the builder
exists so tests can swap widget construction, but the production builder does
not own the construction logic. The screen class is 733 lines, with widget
construction as the dominant contributor.

Compare with `TransferDialog` where `TransferGridRenderer` actually owns
the widget construction (366 lines in `transfer_grid_renderer.py`), and
the dialog is a thin orchestrator (475 lines including back-compat shims).

**Recommendation:** Move `_create_ui`, `_create_empire_inputs`,
`_update_empire_visibility`, and `_update_race_display` into
`NewGameSetupUiBuilder`, leaving `NewGameSetupScreen` with only the
Stage-1 state, delegate wiring, back-compat property shims, and
event dispatch.

---

## Overall Verdict

**PROJ-328 passes core structural requirements.** All 6 classes correctly implement
the two-stage `__init__` pattern. The `bypass_init` guard in `StrategyModalWindow`
uses the correct `getattr(type(self), 'bypass_init', False)` form. All subclasses
consume `_window_init_bypassed` correctly. All 5 non-base classes have
corresponding `Null*UiBuilder` / `Mock*UiBuilder` fixtures in `tests/fixtures/`.
The TransferDialog Phase C deep MVVM split is clean and behaviorally equivalent
in its primary code paths.

Two gaps remain:

| Finding | Severity | Item |
|---------|----------|------|
| FND-001 | MAJOR | TransferDialog `_on_confirm` always kills window |
| FND-002 | MAJOR | NewGameSetupScreen widget construction not extracted |

No CRITICAL findings. No broken cross-references, no false-positive tests, no
production behavior regressions outside the `_on_confirm` edge case.
