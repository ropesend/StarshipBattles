# PROJ-392 Verification Report: `_menu_scene` Rename + Controller Indirection Cleanup

**Date:** 2026-05-08
**Reviewer:** OpenCode agent

---

## Section 1: `_menu_scene` → `menu_scene` rename verification

### Check 1: No remaining `Game._menu_scene` references

**PASS** — Zero matches for `Game\._menu_scene` across the entire repo.

Grep for `\._menu_scene` returns 7 hits, all in `game/screen_router.py` (lines 99, 100, 103, 171, 384, 398, 425). These are `self._menu_scene` on the `ScreenRouter` class — the router's own private attribute holding the `MenuScene` instance. Completely unrelated to `Game._menu_scene`.

### Check 2: The setter works

**PASS** — `game/app.py:232-235`:

```python
@property
def menu_scene(self) -> Any: return self._route_get('_menu_scene')
@menu_scene.setter
def menu_scene(self, value: Any) -> None: self._route_set('_menu_scene', value)
```

The routing key string `'_menu_scene'` is an internal implementation detail passed to `_route_get`/`_route_set` (lines 185-200), which resolve to either `self._router.<name>` (production) or `self.__dict__[name]` (test bypass). The string `'_menu_scene'` is NOT a Python attribute reference — it's a dictionary key matching the router's internal attribute name `ScreenRouter._menu_scene` (see `game/screen_router.py:99`). The external Python API is `game.menu_scene` (no underscore). This follows the same pattern as `battle_scene`, `strategy_scene`, `builder_scene`, and `test_lab_scene`.

### Check 3: All external callers use public form

**PASS** — All test references use the public `game.menu_scene`:

- `tests/unit/ui/screens/test_strategy_menu_actions.py:278`: `game.menu_scene = MagicMock()`
- `tests/unit/ui/screens/test_strategy_menu_actions.py:308`: `game._switch_scene.assert_called_once_with(GameState.MENU, game.menu_scene)`

No external code references `game._menu_scene`.

### Check 4: ScreenRouter._menu_scene is unrelated

**PASS** — `game/screen_router.py:99`:

```python
self._menu_scene = MenuScene(self.width, self.height, menu_button_config)
```

This is the `ScreenRouter` class's own private attribute holding the `MenuScene` instance. The rename from `Game._menu_scene` → `Game.menu_scene` was on the `Game` class only. The router's `_menu_scene` attribute is the canonical storage that `Game.menu_scene` delegates to via `_route_get('_menu_scene')`. No conflict.

### Check 5: PROJ-381 `Game.running` area — no accidental `_menu_scene` reference

**PASS** — `game/app.py:124-127`:

```python
# Legacy `running` flag — read by `_handle_strategy_action("quit_game")
# tests via `Game.__new__`-bypass. RunLoop owns the canonical flag,
# but we keep the attribute on Game for backward compatibility.
self.running = True
```

The `running` attribute is set to `True` during `__init__`. It is also flipped to `False` at lines 266, 452, and bridged with `_loop.running` at lines 502-507. No `_menu_scene` reference was introduced anywhere near the `running` code. The "Legacy" comment at line 124 confirms this is an intentional backward-compat bridge, not a new reference leak.

### Section 1 Summary: **COMPLETE**

All five checks pass. The rename from `Game._menu_scene` to `Game.menu_scene` is clean with no residual private-form references.

---

## Section 2: Controller indirection cleanup

### Check 1: `validate_save_name` and `generate_default_save_name` static methods deleted from screen

**PASS** — Grep for `def validate_save_name` and `def generate_default_save_name` in `new_game_setup_screen.py`: **zero matches**. Both static methods were removed from the screen class.

The screen file does retain two other static methods:
- `get_player_count_options()` at line 709
- `build_game_config()` at line 714

These are NOT the indirection methods targeted by PROJ-392. `build_game_config` is a genuine screen-level helper (thin delegator to controller), and `get_player_count_options` is independent static data.

### Check 2: Methods exist on controller

**PASS** — `game/ui/screens/new_game_setup_controller.py`:

- `validate_save_name` at lines 237-266: static method with full validation logic (empty check, invalid characters, uniqueness).
- `generate_default_save_name` at lines 268-271: static method returning timestamped default name.

The controller is the canonical home for both methods. The controller itself calls `NewGameSetupController.validate_save_name(...)` at line 162 (inside `on_start_clicked`).

### Check 3: Zero remaining references to old indirection pattern in tests

**PASS** — Grep for `_screen\.validate_save_name|_screen\.generate_default_save_name` across all .py files: **zero matches**.

Note: `tests/unit/ui/screens/test_new_game_setup_controller.py:45` contains:
```python
type(screen).validate_save_name = NewGameSetupController.validate_save_name
```
This is a **test fixture helper** that patches the mock screen's class to supply `validate_save_name` so the controller can dispatch `type(self._screen).validate_save_name(...)` (controller at line 162 calls `NewGameSetupController.validate_save_name(...)` directly, NOT through the screen). This is test infrastructure, not the old indirection pattern.

### Check 4: All test callers use controller directly

**PASS** — All test invocations use `NewGameSetupController.validate_save_name(...)` and `NewGameSetupController.generate_default_save_name(...)`:

- `tests/unit/ui/test_new_game_setup.py:23,31,41,50,77,84,334,341,350,351` — all direct controller calls.
- `tests/unit/ui/screens/test_new_game_setup_extended.py:233,246` — `patch('game.ui.screens.new_game_setup_controller.NewGameSetupController.validate_save_name', ...)`.
- `tests/unit/ui/screens/test_new_game_setup_controller.py:78,83,88,93,100,108` — all direct controller calls.

### Check 5: No production code relies on old indirection

**PARTIAL** — The production controller at `new_game_setup_controller.py:162` calls `NewGameSetupController.validate_save_name(...)` directly. However:

**BUG FOUND**: `new_game_setup_screen.py:348` — inside `_create_ui()`:
```python
self.save_name_input.set_text(self.generate_default_save_name())
```

This calls `self.generate_default_save_name()` on the `NewGameSetupScreen` instance. Since the `generate_default_save_name` static method was **removed** from the screen class, and `NewGameSetupScreen` extends `pygame_gui.elements.UIWindow` (not the controller), this call will raise `AttributeError` at runtime in production.

Evidence:
- `NewGameSetupScreen` has no `__getattr__` forwarding to the controller.
- `NewGameSetupScreen` does not inherit from `NewGameSetupController`.
- The method is only defined as `NewGameSetupController.generate_default_save_name()` (a static method on the controller class).

The comment at lines 703-706 acknowledges the shims were dropped:
```
# PROJ-392 dropped the ``validate_save_name`` /
# ``generate_default_save_name`` shims; call
# ``NewGameSetupController.validate_save_name(...)`` /
# ``NewGameSetupController.generate_default_save_name(...)`` directly.
```

But line 348 was **not updated** to match. It should be:
```python
self.save_name_input.set_text(NewGameSetupController.generate_default_save_name())
```

### Section 2 Summary: **INCOMPLETE**

The indirection cleanup removed the static shims from `NewGameSetupScreen`, but missed updating `_create_ui()` at line 348 which still calls `self.generate_default_save_name()`. This is a latent `AttributeError` in production code.
