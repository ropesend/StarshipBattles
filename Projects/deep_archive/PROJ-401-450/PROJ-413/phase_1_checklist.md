# Phase 1: Migrate Spectrum + solar constant imports off stars.py, then delete shim block

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-413 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate ~20 import files that pull `Spectrum` from `game.strategy.data.stars` to the canonical `game.strategy.data.spectrum`. Only 1 production caller (`game/strategy/data/physics.py:3`); the rest are test files. Delete the stars.py re-export block (lines 31-45) once zero callers remain. Solar constants have 1 caller via stars.py (`tests/unit/strategy/data/test_stars.py:17` imports `SOLAR_TEMP_K`); migrate it to `game.core.spectrum_math` and then delete the solar constant re-export lines.

**CAUTION:** `stars.py` uses `Spectrum` internally in `Star.from_dict` (line ~140). Deleting the public `from game.strategy.data.spectrum import Spectrum` re-export line does NOT remove the internal need — `stars.py` must retain a (private) canonical import of `Spectrum` for `Star.from_dict` to work. The shim is retired when the public symbol is no longer on the module's external surface (removed from `__all__` and the top-level name replaced with a private alias or inline import).

Severity tier: Major (migration sweep).

---

## Tasks

### Task 1.1: Migrate ~20 Spectrum import sites and delete stars.py re-export block
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/ --testmon`

- [x] Grep `from game.strategy.data.stars import` across game/, tests/, combat_lab/, Tools/ — capture both single-line and multiline import blocks; expect ~20 files importing Spectrum, plus test_stars.py importing SOLAR_TEMP_K
- [x] Rewrite each Spectrum caller to `from game.strategy.data.spectrum import Spectrum`
- [x] Rewrite the 1 solar constant caller (`test_stars.py:17`) to import from `game.core.spectrum_math` (NOT from `game.strategy.data.spectrum`, which only exports `Spectrum`)
- [x] Delete `tests/unit/strategy/data/test_spectrum.py::test_stars_module_re_exports_spectrum` (it asserts the re-export behavior being removed) — first confirm it fails under the new import, then delete it
- [x] Replace the public `from game.strategy.data.spectrum import Spectrum` line in `stars.py` with a private import (`_Spectrum` alias or TYPE_CHECKING import) so `Star.from_dict` continues to work, while the symbol is no longer public
- [x] Delete the solar constant re-export block in `stars.py:31-37` once all callers are migrated
- [x] Remove `Spectrum`, `SOLAR_TEMP_K`, `SOLAR_MASS_KG`, `SOLAR_RADIUS_M`, `SOLAR_LUMINOSITY_W`, and `WIEN_DISPLACEMENT_CONSTANT` from `stars.py.__all__`
- [x] Remove `StarGenerator` from `stars.py.__all__` (safe — no wildcard callers; if lazy shim is not being retired in this project, confirm __getattr__ remains)
- [x] Update `stars.py` module docstring (lines 1-13) to remove description of re-export compatibility
- [x] Update `game/strategy/data/spectrum.py` docstring to remove the "stars.py re-exports" statement
- [x] Verify: `pytest tests/ --testmon` passes; grep `from game.strategy.data.stars import` for any remaining Spectrum or SOLAR_ imports in files that should not have them

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
