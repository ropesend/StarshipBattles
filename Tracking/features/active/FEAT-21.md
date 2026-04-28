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
Pending

## Related
- BUG-121 — scroll wheel zoom regression on strategy screen.

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
