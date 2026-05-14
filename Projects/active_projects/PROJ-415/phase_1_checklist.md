# Phase 1: Migrate 61 callers off planet.py re-exports, then delete the block

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-415 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Rewrite all 61 caller **files** (64 import statements) of `PlanetaryFacility` and `SpeciesPopulation` from `planet.py` to use the canonical modules. `ColonySpeciesConfig` has zero external callers via the shim but is a runtime dependency inside `planet.py` itself (dataclass field at line 107, return annotation at line 187, constructor call at line 190) — the shim line (planet.py:25) is removed as the final step after confirming the direct import at line 25 is replaced by the existing internal usage import chain. Delete the full re-export block (planet.py:19-25) once zero external callers remain and planet.py's internal ColonySpeciesConfig usage is satisfied by a direct (non-shim) import.

Severity tier: Major (large migration sweep).

> **Caller count correction (post-codex-consult):** The original audit said "61 callers." Actual grep: 64 import statements across 61 distinct files. PlanetaryFacility=53 lines, SpeciesPopulation=12 lines, ColonySpeciesConfig=0 external lines. 35 of 64 lines are multi-symbol (comma-separated) and also import `Planet`, `PlanetType`, etc. — preserve those when rewriting.

---

## Tasks

### Task 1.1: Enumerate and migrate callers
**File:** `game/strategy/data/planet.py` + all caller files
**Tests:** `pytest tests/ --testmon`

- [x] Grep `from game.strategy.data.planet import` across game/, tests/, combat_lab/, Tools/ — filter for PlanetaryFacility / SpeciesPopulation / ColonySpeciesConfig; produce exact per-symbol list. Include: top-level imports, TYPE_CHECKING-guarded imports (build_queue_source.py:19-20, harvesting_engine.py:40-42, population_engine.py:27-30, resupply_engine.py:29-30), and local/function-scope imports (colonize.py:151-153, transfer_branches.py:211-214). Target count: ~64 import statements in 61 files. **Done: AST audit found 64 import nodes / 61 files; results in [findings/migration_table.md](findings/migration_table.md).**
- [x] Rewrite each external caller: `from game.strategy.data.planetary_facility import PlanetaryFacility` / `.species_population import SpeciesPopulation` / `.colony_species_config import ColonySpeciesConfig`. For multi-symbol lines that also import Planet/PlanetType/etc., keep those on the original `from game.strategy.data.planet import ...` line; only split out the shim symbols. **Done across 3 commits (game/, tests/unit, tests/integration).**
- [x] Confirm `game/strategy/data/planet.py` internal ColonySpeciesConfig usage (lines 107, 187, 190) is satisfied by a direct import (not the shim line). The existing import at line 25 serves double duty — once the shim is removed, ensure a direct `from game.strategy.data.colony_species_config import ColonySpeciesConfig` is present at the top of planet.py (not under `# noqa: F401`). **Done: planet.py has a direct (non-`noqa`) import of ColonySpeciesConfig; PlanetaryFacility/SpeciesPopulation moved under `TYPE_CHECKING` since they only appear as string annotations.**

### Task 1.2: Static zero verification (pre-deletion gate)
**Do this before deleting any lines from planet.py.**

- [x] Run a multiline-aware scan (or AST/token scan) confirming zero references to the three symbols via the planet.py shim path across game/, tests/, combat_lab/, Tools/. A line-oriented grep is insufficient if any parenthesized multi-line imports exist. **Done: AST scan returns 0 hits post-migration.**
- [x] Confirm `PlanetaryFacility` and `SpeciesPopulation` are NOT public attributes on the `game.strategy.data.planet` module after import (they should only survive via the shim, which will be deleted). **Verified: `python -c "from game.strategy.data import planet; print(dir(planet))"` shows neither symbol.**

### Task 1.3: Delete the re-export block and verify
**File:** `game/strategy/data/planet.py`

- [x] Delete the comment block at planet.py:19-21 and the three re-export import lines at planet.py:22-25 **Done: PROJ-210 docstring line + shim lines for PlanetaryFacility/SpeciesPopulation removed. ColonySpeciesConfig kept as direct (non-noqa) runtime import. PlanetaryFacility & SpeciesPopulation added under existing `if _TC:` block since they appear only as forward-string annotations.**
- [x] Verify: `pytest tests/ --testmon` passes **Done — single pre-existing QS Battleship `_metadata` failure (acceptable per project instructions).**
- [x] Verify: grep for `from game.strategy.data.planet import.*(PlanetaryFacility|SpeciesPopulation|ColonySpeciesConfig)` returns zero hits across the whole tree **Done — AST scan and grep return 0 production/test hits.**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
