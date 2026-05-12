# GP-22: Design Document

> This is a reference document. Do not modify during implementation.

## Architecture analysis (incorporates codex round-1 review)

`MenuScene` (`game/ui/screens/menu_scene.py`) is already config-driven:
`__init__` accepts `button_config: List[Tuple[str, Callable[[], None]]]`
and `_create_buttons` (lines 60-79) iterates and creates pygame_gui
`UIButton` instances. The button config is supplied at construction time
by `Game` via `_get_menu_button_config()` (`game/app.py:141-154`).

`MenuScene` owns its own pygame_gui `UIManager` (lines 44-49), processes
events through it (lines 81-89), updates and draws it (lines 91-98). That
manager is exposed by `ScreenRouter.menu_ui_manager`
(`game/screen_router.py:98-100`, accessed by `game/app.py:238`).

A `pygame_gui.windows.UIMessageWindow` rendered on this manager is
sufficient for the About display. The existing lifecycle pattern at
`game/ui/screens/strategy_screen_lifecycle.py:119-126` is the local
convention: center the window using `UIConfig.CONFIRM_DIALOG_WIDTH/HEIGHT`,
pass `html_message`, `manager`, and `window_title`. No bespoke dialog
class is needed.

## Why no new dialog file

A `game/ui/screens/about_author_dialog.py` would need lifecycle, event
handling, resize handling, and tests that `UIMessageWindow` already
provides. It would also add LOC to the UI screens directory without
behavioral need.

## Why no StrategyModalWindow

`StrategyModalWindow` is the strategy-screen pattern
(`docs/06_UI_STYLE_GUIDE.md:38`). `MenuScene` is classified as a
menu/minor scene in `docs/03_CONVENTIONS.md:19`, not a strategy screen.
Using `StrategyModalWindow` here would overreach the pattern's intended
scope.

## Why delegate via ScreenRouter

`Game` is the composition root with public methods kept as thin delegators
(`game/app.py:68-74`). `ScreenRouter` owns the menu scene and its UI
manager. Putting `UIMessageWindow` construction directly in `Game` would
erode the post-decomposition contract and push `game/app.py` (441 lines)
closer to the 500 LOC ceiling.

The delegation chain:

- Menu button tuple: `("About the Author", self._show_about_author)` on `Game`
- `Game._show_about_author()`: 1-line delegator → `self._router.show_about_author()`
- `ScreenRouter.show_about_author()`: builds the `UIMessageWindow` on
  `self._menu_scene.get_ui_manager()`

## Layout verification

Button position formula: `self.height // 2 - 320 + i * 70`
(`menu_scene.py:71`). At 1600px minimum height, button stack starts at
y=480; with 50px button height and 70px stride, the 11th button (i=10)
lands at top=1180, bottom=1230 — comfortably inside the 1600px height.
At 2160px (4K target), the stack still fits with margin.

The 200x50 button rect (`menu_scene.py:70-74`) needs visual verification
with "About the Author" text; the label is similar in length to existing
"Design Workshop" so width should be fine.

## Risks (from codex round 1)

1. **New-UI-subsystem trap.** Adding `about_author_dialog.py` would create
   a parallel-to-pygame_gui surface for one trivial display. The plan
   explicitly forbids this; reuse `UIMessageWindow` only.
2. **LOC ceiling pressure.** `game/app.py` (441/500) and
   `game/screen_router.py` (438/500) are both near ceiling. Change must
   add ≤ ~15 lines to each.
3. **Resize edge case.** `MenuScene.handle_resize()` recreates buttons
   and resets the manager resolution (`menu_scene.py:100-105`). If a
   `UIMessageWindow` is open during resize, behavior depends on
   pygame_gui's window lifecycle. Confirmation is a Phase 1 task; if the
   window doesn't survive resize cleanly, document as out of scope rather
   than build a custom overlay.
4. **Pre-existing dirty file.** The `git status --short` baseline showed
   `AgentCoordination/generated/skill_usage/by_install/...json` modified.
   The project must leave that untouched.

## Decisions

- **Reuse `UIMessageWindow`** — locked in. No `about_author_dialog.py`.
- **Delegate via `ScreenRouter`** — locked in.
  `Game._show_about_author()` is a thin delegator.
- **Single phase** — codex pointed out that a verify-only phase is
  overkill for this size of change. Verification is a checklist inside
  Phase 1.
