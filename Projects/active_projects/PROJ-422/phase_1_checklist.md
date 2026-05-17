# Phase 1: Introduce the engines package

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):** game/strategy/interfaces/engines.py, game/strategy/interfaces/engines/__init__.py, game/strategy/interfaces/engines/movement.py, game/strategy/interfaces/engines/orders.py, game/strategy/interfaces/engines/combat.py, game/strategy/interfaces/engines/production.py, game/strategy/interfaces/engines/logistics.py, game/strategy/interfaces/engines/population.py, game/strategy/interfaces/engines/planet_ops.py, game/strategy/interfaces/engines/terraforming.py, game/strategy/interfaces/engines/components.py
**Objective:** Convert `engines.py` into a package with 9 domain-scoped leaf modules + symbol-preserving `__init__.py` re-export; delete the monolith; Phase-0 layout test goes green.

---

## Tasks

### Task 1.1: Create the engines package directory and leaf modules [Medium]
**Files:** new files under `game/strategy/interfaces/engines/`
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q` (still partly red until 1.2 + 1.3 complete)

For each ABC, **cut** (do not duplicate) the class plus its TYPE_CHECKING imports verbatim from `engines.py` into the target leaf module. Keep docstrings, PROJ tags, and method signatures byte-identical. Each leaf gets `from __future__ import annotations`, a minimal TYPE_CHECKING block (only the symbols the ABCs in that module reference), and an `__all__` listing its ABCs.

- [x] Create `game/strategy/interfaces/engines/movement.py` — `IMovementEngine` (96 LOC).
- [x] Create `game/strategy/interfaces/engines/orders.py` — `IOrderProcessor`, `IActionExecutionEngine` (136 LOC).
- [x] Create `game/strategy/interfaces/engines/combat.py` — `IConflictEngine`, `IEnvironmentalHazardEngine` (112 LOC).
- [x] Create `game/strategy/interfaces/engines/production.py` — `IProductionEngine` (60 LOC).
- [x] Create `game/strategy/interfaces/engines/logistics.py` — `IConsumableEngine`, `IResupplyEngine`, `IHarvestingEngine` (153 LOC).
- [x] Create `game/strategy/interfaces/engines/population.py` — `IPopulationEngine`, `IOrganicsConsumptionEngine`, `IHappinessEngine` (134 LOC).
- [x] Create `game/strategy/interfaces/engines/planet_ops.py` — `IPlanetEnergyEngine`, `IPlanetActionEngine` (89 LOC).
- [x] Create `game/strategy/interfaces/engines/terraforming.py` — `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` (72 LOC).
- [x] Create `game/strategy/interfaces/engines/components.py` — `IComponentActivationEngine` (47 LOC).
- [x] Verify each leaf module is well under 200 LOC (max: `logistics.py` at 153, well under).

**Notes:** Each ABC was cut verbatim from `engines.py` with TYPE_CHECKING imports narrowed to only the symbols referenced by the ABCs in that leaf. Docstrings, PROJ tags, and method signatures byte-identical.

### Task 1.2: Author the package `__init__.py` re-export seam [Medium]
**File:** `game/strategy/interfaces/engines/__init__.py` (new)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q`

- [x] Add a module docstring that states: "Package entry point for the strategy engine ABC contracts. Re-exports every leaf-module ABC. This is the public seam, not a backward-compat shim — delete only when all 30 consumers are rewritten to use leaf module paths."
- [x] Add explicit per-leaf import blocks (9 blocks total, sorted by leaf name).
- [x] Declare `__all__` listing **all 18 names**, sorted by domain. This closes the existing drift where `IComponentActivationEngine` was missing.

**Notes:** `engines/__init__.py` is 96 LOC, contains explicit re-exports of all 18 ABCs from the 9 leaf modules, and `__all__` matches the design's domain-sorted layout.

### Task 1.3: Delete the old monolith [Simple]
**File:** `game/strategy/interfaces/engines.py` (delete)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q` — should now be **green**

- [x] Delete `game/strategy/interfaces/engines.py`. This is the root-cause fix per AGENTS.md — no parallel "old + new" path.
- [x] Confirm `git status --short` shows exactly one `D` (the deleted monolith) plus the 10 added files (9 leaves + `__init__.py`).
- [x] Re-run the layout test — 5 of 6 green; `test_top_level_interfaces_reexports_all_engines` remains red (Phase 2 closes that).

**Notes:** Smoke-test `from game.strategy.interfaces.engines import (all 18 names)` is green. Monolith fully replaced; no parallel old path.

### Task 1.4: Confirm no concrete engine file was edited [Simple]
**Files:** all 14 concrete engine modules under `game/strategy/engine/`
**Tests:** `git status --short`

- [x] `git status --short` shows zero modifications to any file under `game/strategy/engine/`.
- [x] If a concrete engine file is modified, **stop** and prove with a failing test that package-root re-exports are insufficient — that would mean the split design is wrong. (N/A — none modified.)

**Notes:** `git status` confirms only one deletion (`engines.py`) and one new untracked directory (`engines/`). No concrete engine touched.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/strategy/interfaces/engines.py` no longer exists
- [x] `game/strategy/interfaces/engines/` is a package containing `__init__.py` + 9 leaf modules
- [x] Phase-0 layout test is green (`test_top_level_interfaces_reexports_all_engines` is still red — Phase 2 closes that)
- [x] No concrete engine files under `game/strategy/engine/` were modified
- [x] `python Projects/scripts/validate_phase.py PROJ-422 1` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
