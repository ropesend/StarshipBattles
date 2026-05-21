# Phase 4: Codex-audit remediation

**Status:** In Progress
**Objective:** Address the 4 VERIFIED findings from the one-round Codex audit (`AgentCoordination/Scratchpad/Consult/proj466_audit/verification.md`). The CRITICAL is a Phase 1 composition bug: in the real callback wiring the router-level `SessionInitializationError` catch makes the controller-level catch dead, so the setup window is still killed AND `showing_new_game_setup` is left stuck `True`. The other 3 are a weak test, a missing test, and a logging-visibility regression.

---

## Tasks

### Task 4.1: Fix the new-game session-init composition bug [Medium]
**Files:** `game/screen_router.py`, `game/ui/screens/new_game_setup_controller.py`
**Tests:** `pytest tests/ -k "screen_router or new_game_setup or session_init"`

Root cause: the new-game path goes `NewGameSetupScreen` -> `controller.on_start_clicked()` -> `router._on_new_game_start()`. Both the controller and the router now catch `SessionInitializationError`. The controller is the correct owner of the failure UX (keep window alive + error label), so the router must NOT swallow on this path. Quickstart (`_start_quickstart`) is wired directly to menu buttons (no controller), so it KEEPS its router-level catch + `_show_session_init_error` dialog.

- [x] Remove the `try/except SessionInitializationError` from `ScreenRouter._on_new_game_start` (let it propagate to the controller, which keeps the window alive and sets the error label). Keep `_show_session_init_error` for the quickstart path.
- [x] Confirm `_start_quickstart` retains its catch + dialog (quickstart has no controller).
- [x] Update the screen_router new-game regression test: a `SessionInitializationError` from `_on_new_game_start` now PROPAGATES (the controller catches it), it does not show a router dialog. Quickstart test unchanged (still shows dialog).
- [x] Add an integration-style regression that exercises the REAL chain (controller.on_start_clicked with a callback that raises SessionInitializationError) and asserts: window NOT killed, error label set, and the failure does not leave a stuck overlay flag.
- [x] Verify: `pytest` passes

### Task 4.2: Tighten run_battle missing-dependency test [Simple]
**File:** `tests/unit/simulation/test_battle_runner_di.py`
**Tests:** `pytest tests/ -k battle_runner_di`

- [x] Change `pytest.raises((ValidationException, TypeError))` to `pytest.raises(ValidationException)` (and assert `code == MISSING_DEPENDENCY`) so a regression to a generic builtin fails.
- [x] Verify: `pytest` passes

### Task 4.3: Add load_planet_image OSError regression [Simple]
**File:** `tests/unit/core/test_asset_manager.py` (or the asset-manager test home)
**Tests:** `pytest tests/ -k asset_manager`

- [x] Add a test that forces `load_external_image` to raise `OSError` and asserts `load_planet_image` degrades to the next resolution / fallback (does not propagate) and logs a warning.
- [x] Verify: `pytest` passes

### Task 4.4: Restore missing-file WARNING for minefield balance [Simple]
**File:** `game/strategy/engine/minefield_balance.py`
**Tests:** `pytest tests/ -k minefield`

- [x] Keep the `json_utils.load_json` routing but restore an explicit `logger.warning` when the canonical `Paths.MINES_BALANCE_FILE` is missing (an actionable config problem should not be hidden at DEBUG).
- [x] Verify: `pytest` passes; no direct `json.load` reintroduced

**Phase 4 Notes:** 4.1 — root cause: the new-game path runs through `NewGameSetupController.on_start_clicked`, which already catches `SessionInitializationError` and keeps the window alive; the redundant catch in `ScreenRouter._on_new_game_start` swallowed it first, making the controller's catch dead and still killing the window (and leaving `showing_new_game_setup` stuck True). Fix: removed the router-level catch on the new-game path (it now propagates to the controller); quickstart keeps its own catch + `_show_session_init_error` dialog since it has no controller. Updated the screen_router new-game test to assert propagation, added a real-chain composition test binding the actual `ScreenRouter._on_new_game_start` as the controller callback. 4.2 — tightened run_battle DI test to `ValidationException` + `MISSING_DEPENDENCY` code (was `(ValidationException, TypeError)`). 4.3 — added `load_planet_image` OSError regression; this surfaced that the stellar-object fallback loop still lacked `OSError`, so added it there for full parity. 4.4 — restored an explicit missing-file WARNING in minefield_balance (json_utils.load_json logs missing at DEBUG) while keeping the json_utils routing. Full suite: 23473 passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State

_Source: Codex audit `AgentCoordination/Scratchpad/Consult/proj466_audit/audit.md`; verification `verification.md` in the same leaf._
