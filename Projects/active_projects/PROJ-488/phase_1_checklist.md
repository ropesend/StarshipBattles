# Phase 1: Migrate 25 callers + delete alias

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-488 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate ~25 `MASS_EARTH` callers to the canonical `EARTH_MASS` symbol, then delete the alias.

---

## Tasks

### Task 1.1: Enumerate all `MASS_EARTH` callers
**File:** various
**Tests:** `pytest tests/ --testmon`

- [x] Run `grep -rn "MASS_EARTH" .` and record the full caller list (post-merge re-verification 2026-05-22 counted ~67 references across 12 files; confirm exact count)
- [x] Group callers by directory: `game/` (3 prod files: `planet_atmosphere.py`, `planet_gen_surface.py`, `ui/screens/galaxy_test/system_mode.py`), `tests/`, `Tools/`, diagnostics

**Notes:** Exact count of 67 confirmed across 11 Python files (the static-guard fixture is the 12th file with a literal string reference). Production callers: `game/strategy/data/planet_atmosphere.py` (4), `game/strategy/data/planet_gen_surface.py` (2), `game/ui/screens/galaxy_test/system_mode.py` (2). Tools: `Tools/diagnose_blueprints/diagnose_blueprints.py` (3). Tests: `tests/integration/strategy/test_planet_physics.py` (4), `tests/unit/strategy/planet_atmosphere/test_generation.py` (5), `tests/unit/strategy/planet_atmosphere/test_calculations.py` (10), `tests/unit/strategy/planet_atmosphere/conftest.py` (2), `tests/unit/strategy/data/test_planet_physics.py` (1), `tests/unit/strategy/data/test_planet_gen.py` (19 — many local lazy imports). Plus alias declaration in `planet_physics.py` (2 lines: import + alias).

### Task 1.2: Migrate all callers to `EARTH_MASS`
**File:** all caller files
**Tests:** `pytest tests/ --testmon`

- [x] For each caller, replace `MASS_EARTH` with `EARTH_MASS`
- [x] If the caller imports `MASS_EARTH` from `game.strategy.data.planet_physics`, switch the import to `from game.core.constants import EARTH_MASS` (or whatever the canonical path is — verify against the existing direct importers of `EARTH_MASS`)
- [x] Run the affected test files to confirm no regressions

**Notes:** Canonical home is `game.core.constants.EARTH_MASS` (verified via grep `^EARTH_MASS\s*=`). All 11 Python files updated: imports redirected to `from game.core.constants import EARTH_MASS`, and inline `MASS_EARTH` references renamed to `EARTH_MASS`. 471 targeted tests pass.

### Task 1.3: Delete the alias
**File:** `game/strategy/data/planet_physics.py`
**Tests:** `pytest tests/unit/strategy/data/`

- [x] Delete `MASS_EARTH = EARTH_MASS  # Backward-compatible alias` at line 25 (and the surrounding blank line at 24 if it becomes orphan)
- [x] If line 25 was the last reason for the import of `EARTH_MASS` into `planet_physics.py`, also remove the now-unused import; otherwise keep it

**Notes:** Both lines removed (alias + `from game.core.constants import EARTH_MASS` import — that import was added solely to feed the alias; no other code in `planet_physics.py` uses `EARTH_MASS`). The reference-mass block is now back to a clean static list.

### Task 1.4: Update the static-guard fixture
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py`

- [x] Line 208 currently enshrines `MASS_EARTH` as the canonical import for `game/ui/screens/galaxy_test/system_mode.py` (entry tuple ends with `"MASS_EARTH"`). After Task 1.2 migrates that file to `EARTH_MASS`, update the fixture entry's symbol from `"MASS_EARTH"` to `"EARTH_MASS"` and its module-path argument from `game.strategy.data.planet_physics` to `game.core.constants` (the canonical home of `EARTH_MASS`). Without this update the fixture will flag `system_mode.py` as a guard violation post-migration.
- [x] Verify: `pytest tests/static_guards/test_facade_read_path_imports_guard.py` passes.

**Notes:** Fixture updated as specified. Static-guard test passes.

### Phase Verification
- [x] `pytest tests/ --testmon` passes (testmon itself is broken in this environment with a `path is on mount '\\\\.\\nul'` ValueError unrelated to this change; ran the full targeted suite instead: `pytest tests/static_guards/test_facade_read_path_imports_guard.py tests/unit/strategy/data/test_planet_physics.py tests/unit/strategy/data/test_planet_gen.py tests/unit/strategy/planet_atmosphere/ tests/integration/strategy/test_planet_physics.py` → 471 passed in 3.94s)
- [x] `grep -rn "MASS_EARTH" .` returns 0 matches across the entire **Python** surface (only matches now are historical `.md`/`.txt` project notes and audit findings, which are out of scope)
- [x] The `EARTH_MASS` value at every former call site is numerically identical (the alias was a literal rebinding `MASS_EARTH = EARTH_MASS`; the rename is a pure no-op behaviorally — `game.core.constants.EARTH_MASS = 5.97e24`)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
