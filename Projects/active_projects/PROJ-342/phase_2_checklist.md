# Phase 2: Refactor TestLabScreen [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Change `TestLabScreen.__init__` signature, eliminate `self.game`, add `_require_display_surface()` helper, fix all 12 `self.game.*` access sites in `screen.py`, and absorb the `BattleStateViewer` sizing/resize fix.

After this phase, the Phase 1 regression tests must turn GREEN.

---

## Tasks

### Task 2.1: Update constructor signature and init body [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py -x`

- [ ] Change [screen.py:61](../../../game/ui/screens/test_lab/screen.py#L61) `def __init__(self, game, scene_callback=None):` to:
  ```python
  def __init__(
      self,
      screen_width: int,
      screen_height: int,
      battle_scene: "BattleScreen",
      scene_callback: "Callable | None" = None,
  ) -> None:
  ```
  Add `from typing import TYPE_CHECKING, Callable` if not present; under `TYPE_CHECKING` add `from game.ui.screens.battle_screen import BattleScreen`.
- [ ] Update docstring (lines 62-69) to describe the new parameters
- [ ] Replace [line 71](../../../game/ui/screens/test_lab/screen.py#L71) `self.game = game` with `self.battle_scene = battle_scene`
- [ ] Replace [lines 73-74](../../../game/ui/screens/test_lab/screen.py#L73-L74) (with the `hasattr` fallback) with:
  ```python
  self.screen_width = screen_width
  self.screen_height = screen_height
  ```
- [ ] Update [line 84](../../../game/ui/screens/test_lab/screen.py#L84) `self.controller = TestLabUIController(game, self.registry, self.test_history)` to drop `game`: `self.controller = TestLabUIController(self.registry, self.test_history)`. (Phase 4 changes the controller signature; this line must be updated in lockstep but the controller change can land on top of the Phase 2 commit — don't run targeted tests for it until Phase 4.)
- [ ] Update [lines 137-138](../../../game/ui/screens/test_lab/screen.py#L137-L138) `BattleStateViewer(WIDTH, HEIGHT)` to `BattleStateViewer(self.screen_width, self.screen_height)`

**Notes:** [Filled during implementation]

### Task 2.2: Add `_require_display_surface()` helper [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** unit tests will exercise this implicitly via Task 2.3

- [ ] Add a private helper method to `TestLabScreen` (place after `_get_engine` or in the helper cluster around line 392):
  ```python
  def _require_display_surface(self) -> pygame.Surface:
      """Return the active pygame display surface or raise.

      `pygame.display.get_surface()` returns None if `set_mode` has not
      been called. In production this never happens (bootstrap creates
      the display before scenes exist); the explicit check exists so a
      misconfigured unit test surfaces a clear error instead of an
      opaque AttributeError downstream.
      """
      surface = pygame.display.get_surface()
      if surface is None:
          raise RuntimeError(
              "Display surface not initialized; "
              "TestLabScreen progress rendering requires pygame.display.set_mode() to have been called."
          )
      return surface
  ```

**Notes:** [Filled during implementation]

### Task 2.3: Replace all `self.game.*` accesses [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/test_lab/test_render_progress_no_game_handle.py -x` (must turn GREEN)

Replace 12 sites. Map exhaustively:

- [ ] [Line 322](../../../game/ui/screens/test_lab/screen.py#L322): `self.game.battle_scene` → `self.battle_scene`
- [ ] [Line 323](../../../game/ui/screens/test_lab/screen.py#L323): `self.game.battle_scene.test_scenario` → `self.battle_scene.test_scenario`
- [ ] [Line 325](../../../game/ui/screens/test_lab/screen.py#L325): `self.game.battle_scene.test_completed` → `self.battle_scene.test_completed`
- [ ] [Line 334](../../../game/ui/screens/test_lab/screen.py#L334): `self.game.battle_scene.test_tick_count` → `self.battle_scene.test_tick_count`
- [ ] [Line 347](../../../game/ui/screens/test_lab/screen.py#L347): `self.game.battle_scene` (in `hasattr` check) → `self.battle_scene`
- [ ] [Line 348](../../../game/ui/screens/test_lab/screen.py#L348): `self.game.battle_scene.test_completed` → `self.battle_scene.test_completed`
- [ ] [Line 349](../../../game/ui/screens/test_lab/screen.py#L349): `self.game.battle_scene` (second `hasattr`) → `self.battle_scene`
- [ ] [Line 350](../../../game/ui/screens/test_lab/screen.py#L350): `self.game.battle_scene.test_scenario` → `self.battle_scene.test_scenario`
- [ ] [Lines 382-384](../../../game/ui/screens/test_lab/screen.py#L382-L384): rewrite the surface-blit block as:
  ```python
  surface = self._require_display_surface()
  screen_center_x = self.screen_width // 2
  screen_center_y = self.screen_height // 2
  surface.blit(overlay, (screen_center_x - 300, screen_center_y - 100))
  ```
- [ ] [Lines 388-389](../../../game/ui/screens/test_lab/screen.py#L388-L389): rewrite `_draw_and_flip` body as:
  ```python
  surface = self._require_display_surface()
  surface.fill(theme.BG_PRIMARY)
  self.draw(surface)
  pygame.display.flip()
  ```
- [ ] [Line 394](../../../game/ui/screens/test_lab/screen.py#L394): `self.game.battle_scene.engine` → `self.battle_scene.engine`
- [ ] [Line 398](../../../game/ui/screens/test_lab/screen.py#L398): `self.game.battle_scene.engine` → `self.battle_scene.engine`
- [ ] [Line 400](../../../game/ui/screens/test_lab/screen.py#L400): `self.game.battle_scene._battle_service.create_battle(...)` → `self.battle_scene._battle_service.create_battle(...)`
- [ ] [Line 489](../../../game/ui/screens/test_lab/screen.py#L489): `self.game.battle_scene.start_battle(controller)` → `self.battle_scene.start_battle(controller)`
- [ ] Verify with `git grep -n "self\.game\." game/ui/screens/test_lab/screen.py` — must return zero matches after this task

**Notes:** [Filled during implementation. Line numbers drift as edits happen — re-grep before each edit.]

### Task 2.4: Forward `handle_resize` to `BattleStateViewer` [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** Add a test in Phase 5; for now exercise via `pytest tests/unit/test_lab -x`

- [ ] In [`handle_resize` (lines 623-628)](../../../game/ui/screens/test_lab/screen.py#L623-L628), after `self.ui_manager.set_window_resolution((width, height))`, add:
  ```python
  self.battle_state_viewer.handle_resize(width, height)
  ```

**Notes:** [Filled during implementation]

### Task 2.5: Targeted regression sweep [Simple]
**Tests:** `pytest tests/unit/test_lab -x`

- [ ] Run `pytest tests/unit/test_lab -x`. The Phase 1 tests MUST be green. Existing tests in this directory will likely fail due to constructor signature change — that is expected and gets resolved in Phase 5.
- [ ] Confirm the Phase 1 tests turn GREEN with the changes from Tasks 2.1-2.3.
- [ ] Do NOT run the full sharded suite yet (Phase 4 + 5 still in flight).

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All 12 `self.game.*` sites replaced (zero `self.game` references remain in `screen.py`)
- [ ] `_require_display_surface()` helper present and called in both batch-mode rendering helpers
- [ ] `BattleStateViewer` constructed with `self.screen_width/height` and `handle_resize` forwarded
- [ ] Phase 1 regression tests are GREEN
- [ ] `screen.py` LOC has not increased meaningfully (refactor is net-neutral or slightly negative)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
