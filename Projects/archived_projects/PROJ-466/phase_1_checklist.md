# Phase 1: Critical session-init boundary

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-466 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Close the 1 CRITICAL boundary failure and its coupled MAJOR finding from audit `2026-05-20_065518_error-audit`: `GameSession(...)` construction can raise `SessionInitializationError` (galaxy-generation failure) and no UI-layer caller guards it, so the exception propagates to the top-level `main()` crash handler (`app.py:518`) as a hard crash instead of a recoverable error dialog.

---

## Tasks

### Task 1.1: Guard GameSession construction in screen_router [Medium]
**File:** `game/screen_router.py`
**Tests:** `pytest tests/ -k "screen_router or session_init or new_game_start"` (add coverage if none exists)

- [x] Wrap `GameSession(config=..., ai_factory=...)` in `ScreenRouter._on_new_game_start` (line 209) with `except SessionInitializationError as e:` and surface a user-facing error (`UIMessageWindow` / setup-screen error label) instead of letting it propagate
- [x] Wrap `GameSession(config=config)` in `ScreenRouter._start_quickstart` (line 266) with `except SessionInitializationError as e:` and display a `UIMessageWindow` error dialog
- [x] Add a regression test that forces `GameSession.__init__` to raise `SessionInitializationError` (planet-shortage config or patched initializer) and asserts the UI surfaces an error dialog rather than propagating to the crash handler
- [x] Verify: `pytest` passes; no new `except Exception` without `# Intentional` comment introduced; `grep -rn "except:" game/` returns nothing in modified files

**Notes:** Both construction sites now wrap `GameSession(...)` in `try/except SessionInitializationError`. Added shared `ScreenRouter._show_session_init_error()` helper that opens a `UIMessageWindow` (matches the existing save-failed dialog pattern) and returns without switching scenes. No broad catch introduced — narrow domain-exception catch only. Tests added: `test_PROJ466_new_game_start_session_init_failure_shows_dialog_not_crash`, `test_PROJ466_quickstart_session_init_failure_shows_dialog_not_crash`.

### Task 1.2: Guard the start callback in the setup controller [Medium]
**File:** `game/ui/screens/new_game_setup_controller.py`
**Tests:** `pytest tests/ -k "new_game_setup_controller or on_start"`

- [x] Wrap `self._on_start_callback(config)` in `NewGameSetupController.on_start_clicked` (line 186) with `except SessionInitializationError as e:` — keep the setup window alive (do NOT call `self._screen.kill()` at line 187 on failure) and set `self._screen.error_label.set_text(...)`
- [x] Add a regression test that the callback raising `SessionInitializationError` leaves the window alive and shows the error label (not killed, not propagated)
- [x] Verify: `pytest` passes; the failure path no longer leaves the session in an indeterminate state via premature `kill()`

**Notes:** `on_start_clicked` now wraps `self._on_start_callback(config)` in `try/except SessionInitializationError`; on failure it sets `error_label` and returns BEFORE `self._screen.kill()`, keeping the window alive. Imported `SessionInitializationError` alongside the existing `ValidationException`. Test added: `TestOnStartClicked::test_PROJ466_session_init_error_keeps_window_alive_shows_error`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_065518_error-audit/`. See `findings/source_audit.md` for the link._
