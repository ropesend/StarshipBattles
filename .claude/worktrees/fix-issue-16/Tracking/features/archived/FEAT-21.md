# FEAT-21: Strategy screen — numpad +/- keyboard zoom controls

## Description
Add keyboard zoom controls on the strategy screen using the numpad `+` and
`-` keys. Each press performs a relatively large zoom step (coarser than
the per-tick mouse wheel) — the goal is functional, not finely-tuned: the
user wants to be able to navigate the galaxy view without depending on the
scroll wheel.

Motivation: BUG-121 reports the scroll wheel zoom is broken on the strategy
screen. This feature provides a permanent secondary control so the user
isn't blocked while that bug is investigated, and so the game has more than
one way to zoom going forward.

## Required changes
- Strategy input handler (`game/ui/screens/strategy_input_handler.py`) —
  handle `KEYDOWN` events for `K_KP_PLUS` / `K_KP_MINUS` (and optionally the
  main-row `K_PLUS` / `K_MINUS` / `K_EQUALS` for laptops without numpads).
- On press, call the camera's zoom method with a coarse step (e.g., ~25% of
  the current zoom range per press).
- Skip handling when the user is typing into a text input (focus check).

## Acceptance
- Pressing numpad `+` zooms in by a noticeable step.
- Pressing numpad `-` zooms out by a noticeable step.
- Repeated presses keep stepping until min/max zoom is reached.
- Keys are ignored while a text input has focus.
- Works regardless of BUG-121 (independent code path).

## Out of scope
- Animated/smoothed zoom transitions.
- Zoom-to-cursor on keyboard (zoom around screen centre is fine).
- Configurable step size or rebindable keys.

## Priority
Medium (user wants it as a workaround for BUG-121)

## Status
Awaiting Confirmation

## Related
- BUG-121 — scroll wheel zoom regression on strategy screen.

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Implemented. Plugged into the existing PROJ-71 data-driven
  keybinding system rather than adding raw KEYDOWN checks. Two new
  `InputAction` values (`STRATEGY_ZOOM_IN` / `STRATEGY_ZOOM_OUT`) bound to
  `K_KP_PLUS` / `K_KP_MINUS` in `default_keybindings.json`. Routed via
  `UIActionRouter.handle_ui_action` to two new `CameraNavigator` methods
  (`zoom_in_step` / `zoom_out_step`) that mutate `camera.target_zoom`
  geometrically by `ZOOM_KEYBOARD_STEP = 1.5` (≈3 wheel ticks per press),
  clamped to `[min_zoom, max_zoom]`. Existing `Camera.update()` exponential
  interpolation smooths the visible animation.
  - Files modified:
    - `game/core/input_actions.py` (enum + display names + group + numpad
      special-key display)
    - `data/default_keybindings.json` (2 new bindings)
    - `game/ui/screens/strategy_camera_nav.py` (constant + 2 methods)
    - `game/ui/screens/strategy_ui_action_router.py` (2 dispatch cases)
    - `tests/unit/ui/screens/test_camera_navigator.py` (5 new tests)
    - `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` (2 new tests)
  - Test results: targeted 233/233 pass; full sharded 15824/15824 pass; zero
    regressions.
  - BUG-121 independence verified — paths share only `camera.target_zoom`
    (a float attribute, not a method that BUG-121 could break).
  - Note: `K_KP_PLUS` / `K_KP_MINUS` require NumLock on most keyboards.
    Standard pygame/SDL behavior; users without numpads can rebind via the
    settings UI to `K_EQUALS` / `K_MINUS`.
