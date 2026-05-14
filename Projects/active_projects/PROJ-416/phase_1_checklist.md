# Phase 1: Migrate 26 race_setup_screen.py imports + 4 test patches, then delete the shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-416 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 26 production and test imports off the 31-line `race_setup_screen.py` shim onto canonical paths. Relocate the 4 test patches that target `RaceRandomizer` via this module path. Delete the shim file.

Severity tier: Major (whole-file deletion after migration).

---

## Tasks

### Task 1.1: Migrate 26 imports + 4 test patches and delete shim file
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon`

Actual caller breakdown (spot-verified; see decisions.md for codex consult):
- Production imports: 2 files (`game/screen_router.py:439`, `game/ui/screens/new_game_setup_controller.py:112`)
- Test imports: ~23 lines across `tests/fixtures/test_race_setup_ui_builders.py:20`,
  `tests/unit/ui/screens/test_race_setup_screen.py` (~20 inline imports), and
  `tests/unit/ui/screens/test_race_setup_screen_public_api.py:35,62`
- Test patches (mock.patch / sys.modules):
  - `tests/unit/ui/test_new_game_setup.py:423,438` — patch `RaceSetupScreen` (must move to `game.ui.screens.race_setup.screen.RaceSetupScreen`)
  - `tests/unit/ui/screens/test_race_setup_screen_public_api.py:44` — patch `RaceRandomizer` (removed with that file)
  - `tests/unit/test_screen_router.py:283-287` — `sys.modules` injection (must move to `game.ui.screens.race_setup.screen`)

Note: shard 04 claimed `game/app.py` imports from the shim; this is false (confirmed by grep). The shim docstring reference to `app.py:522` is stale. See decisions.md.

- [ ] Produce exact list: grep `from game.ui.screens.race_setup_screen import` and `sys.modules.*race_setup_screen` across repo
- [ ] Rewrite each production caller: `RaceSetupScreen` → `from game.ui.screens.race_setup.screen import RaceSetupScreen` (keep import lazy/inside-method where currently lazy, per circular-import note); `RaceBrowserDialog` → `from game.ui.screens.race_browser_dialog import RaceBrowserDialog`; `RaceRandomizer` → `from game.strategy.systems.race_randomizer import RaceRandomizer`
- [ ] Update `game/ui/screens/new_game_setup_controller.py` comment at lines 109-112 to name the canonical module path, not the legacy shim
- [ ] For `tests/unit/ui/screens/test_race_setup_screen.py`: hoist the ~20 inline `RaceSetupScreen` imports to a single module-level import from the canonical path
- [ ] DELETE `tests/unit/ui/screens/test_race_setup_screen_public_api.py` — this is a shim contract test; it must not be migrated (rewriting it would produce redundant smoke tests with no behavior coverage)
- [ ] Relocate `mock.patch` strings in `tests/unit/ui/test_new_game_setup.py:423,438` from `game.ui.screens.race_setup_screen.RaceSetupScreen` to `game.ui.screens.race_setup.screen.RaceSetupScreen` (the path actually imported by the production caller)
- [ ] Rewrite `sys.modules` injection in `tests/unit/test_screen_router.py:283-287` to target `game.ui.screens.race_setup.screen` instead of the shim path
- [ ] Delete the entire shim file `game/ui/screens/race_setup_screen.py`
- [ ] Update docs: `docs/02_PATTERNS.md` lists this file as a current re-export shim — remove/update that entry
- [ ] Update stale source docstrings: `game/ui/screens/race_setup/__init__.py:21-22`, `game/ui/screens/race_setup/screen.py:12-15,27-29` mention the shim as still active; update to say the shim has been removed
- [ ] Verify: `pytest tests/fixtures/test_race_setup_ui_builders.py tests/unit/ui/screens/test_race_setup_screen.py tests/unit/ui/test_new_game_setup.py tests/unit/test_screen_router.py` passes; then `pytest tests/ --testmon`; shim file no longer exists; `grep -rn "from game.ui.screens.race_setup_screen import" game/ tests/` returns zero executable matches

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
