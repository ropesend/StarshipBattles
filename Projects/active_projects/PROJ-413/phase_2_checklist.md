# Phase 2: Migrate WarpPoint/StarSystem imports off galaxy.py, then delete shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-413 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 51 production + test import sites that pull `WarpPoint` and/or `StarSystem` from `game.strategy.data.galaxy` to the canonical `game.strategy.data.star_system`. Delete the re-export from galaxy.py once zero callers remain.

Severity tier: Major (large migration sweep, 51 callers).

---

## Tasks

### Task 2.1: Migrate 51 WarpPoint/StarSystem import sites and delete galaxy.py re-export
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Grep `from game.strategy.data.galaxy import` across game/, tests/, combat_lab/, Tools/ — verifier counts 51 files; produce exact list including `Tools/visual_test_galaxy/visual_test_galaxy.py` (confirmed in scope)
- [ ] For mixed imports like `from game.strategy.data.galaxy import Galaxy, StarSystem`, split them: `Galaxy` stays in galaxy.py; `WarpPoint`/`StarSystem` move to `game.strategy.data.star_system`
- [ ] Rewrite every WarpPoint/StarSystem caller to import from `game.strategy.data.star_system`
- [ ] Delete ONLY the `star_system` re-export line (`galaxy.py:13-15`): `from game.strategy.data.star_system import StarSystem, WarpPoint  # noqa: F401` — do NOT delete the `PlanetType` re-export on galaxy.py:10 (that is out of scope for this project)
- [ ] Update `game/strategy/data/star_system.py:3-5` docstring to drop the back-compat statement
- [ ] Verify: `pytest tests/ --testmon` passes; `grep -rn 'from game.strategy.data.galaxy import.*(WarpPoint\|StarSystem)' .` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
