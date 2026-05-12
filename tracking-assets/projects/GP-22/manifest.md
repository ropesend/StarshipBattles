# GP-22 File Manifest

Initial planned-files manifest. Mutations during implementation should NOT
update this file — per the GP system design, live conflict state belongs
on GitHub (parent-issue file-reservation comments), not in
`tracking-assets/`.

## Files

| File | Type | Notes |
|---|---|---|
| `game/app.py` | Production | Phase 1: append `("About the Author", self._show_about_author)` to `_get_menu_button_config()` (currently lines 141-154). Add `Game._show_about_author()` as a thin delegator to `ScreenRouter.show_about_author()`. Expected delta: ~10 lines. |
| `game/screen_router.py` | Production | Phase 1: add `show_about_author()` method that constructs a `pygame_gui.windows.UIMessageWindow` using `self._menu_scene.get_ui_manager()`, `UIConfig.CONFIRM_DIALOG_WIDTH/HEIGHT`, `window_title="About the Author"`, `html_message="The author is Ross McLean."`. Expected delta: ~10 lines. |
| `tests/unit/ui/screens/test_menu_button_config.py` | Test | Phase 1: NEW. Two tests: (a) `_get_menu_button_config` preserves the 10 existing labels and appends "About the Author", (b) about callback creates a `UIMessageWindow` with the exact title and body strings. |

## NOT in manifest (explicit non-touches)

- `game/ui/screens/about_author_dialog.py` — rejected per codex review; reuse `UIMessageWindow` only.
- `docs/*.md` — codex search found no enumeration of menu buttons; no default docs update.
- `AgentCoordination/generated/skill_usage/by_install/...json` — pre-existing dirty file, leave untouched.
