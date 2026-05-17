# Phase 1: Introduce the engines package

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Create `game/strategy/interfaces/engines/movement.py` — `IMovementEngine` (~85 LOC). `__all__ = ['IMovementEngine']`.
- [ ] Create `game/strategy/interfaces/engines/orders.py` — `IOrderProcessor`, `IActionExecutionEngine` (~125 LOC). `__all__ = ['IOrderProcessor', 'IActionExecutionEngine']`.
- [ ] Create `game/strategy/interfaces/engines/combat.py` — `IConflictEngine`, `IEnvironmentalHazardEngine` (~100 LOC). `__all__ = ['IConflictEngine', 'IEnvironmentalHazardEngine']`.
- [ ] Create `game/strategy/interfaces/engines/production.py` — `IProductionEngine` (~50 LOC). `__all__ = ['IProductionEngine']`.
- [ ] Create `game/strategy/interfaces/engines/logistics.py` — `IConsumableEngine`, `IResupplyEngine`, `IHarvestingEngine` (~140 LOC). `__all__ = ['IConsumableEngine', 'IResupplyEngine', 'IHarvestingEngine']`.
- [ ] Create `game/strategy/interfaces/engines/population.py` — `IPopulationEngine`, `IOrganicsConsumptionEngine`, `IHappinessEngine` (~125 LOC). `__all__ = ['IPopulationEngine', 'IOrganicsConsumptionEngine', 'IHappinessEngine']`.
- [ ] Create `game/strategy/interfaces/engines/planet_ops.py` — `IPlanetEnergyEngine`, `IPlanetActionEngine` (~80 LOC). `__all__ = ['IPlanetEnergyEngine', 'IPlanetActionEngine']`.
- [ ] Create `game/strategy/interfaces/engines/terraforming.py` — `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` (~70 LOC). `__all__ = ['IQualityEngine', 'IAtmosphereEngine', 'IWaterEngine']`.
- [ ] Create `game/strategy/interfaces/engines/components.py` — `IComponentActivationEngine` (~35 LOC). `__all__ = ['IComponentActivationEngine']`.
- [ ] Verify each leaf module is well under 200 LOC (max expected: `logistics.py` at ~140).

**Notes:** [Filled during implementation. Use **cut**, not copy — any duplicate definition is a bug.]

### Task 1.2: Author the package `__init__.py` re-export seam [Medium]
**File:** `game/strategy/interfaces/engines/__init__.py` (new)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q`

- [ ] Add a module docstring that states: "Package entry point for the strategy engine ABC contracts. Re-exports every leaf-module ABC. This is the public seam, not a backward-compat shim — delete only when all 30 consumers are rewritten to use leaf module paths."
- [ ] Add explicit per-leaf import blocks, e.g.:
  ```python
  from game.strategy.interfaces.engines.movement import IMovementEngine
  from game.strategy.interfaces.engines.orders import (
      IOrderProcessor,
      IActionExecutionEngine,
  )
  # ... one block per leaf, 9 blocks total
  ```
- [ ] Declare `__all__` listing **all 18 names**, sorted by domain (matches the order documented in `manifest.md`). This closes the existing drift where `IComponentActivationEngine` was missing.

**Notes:** [Filled during implementation]

### Task 1.3: Delete the old monolith [Simple]
**File:** `game/strategy/interfaces/engines.py` (delete)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engines_package_layout.py -q` — should now be **green**

- [ ] Delete `game/strategy/interfaces/engines.py`. This is the root-cause fix per AGENTS.md — no parallel "old + new" path.
- [ ] Confirm `git status --short` shows exactly one `D` (the deleted monolith) plus the 10 added files (9 leaves + `__init__.py`).
- [ ] Re-run the layout test — all assertions should pass except possibly `test_top_level_interfaces_reexports_all_engines` (that one flips green in Phase 2).

**Notes:** [Filled during implementation. Per TD plan §"Per-Phase Success Criteria": Phase 1 is done only when `game.strategy.interfaces.engines` is a package and the layout test is green (excluding the symmetric-re-export assertion which Phase 2 closes).]

### Task 1.4: Confirm no concrete engine file was edited [Simple]
**Files:** all 14 concrete engine modules under `game/strategy/engine/`
**Tests:** `git status --short`

- [ ] `git status --short` shows zero modifications to any file under `game/strategy/engine/`.
- [ ] If a concrete engine file is modified, **stop** and prove with a failing test that package-root re-exports are insufficient — that would mean the split design is wrong.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/strategy/interfaces/engines.py` no longer exists
- [ ] `game/strategy/interfaces/engines/` is a package containing `__init__.py` + 9 leaf modules
- [ ] Phase-0 layout test is green (`test_top_level_interfaces_reexports_all_engines` may still be red — Phase 2 closes that)
- [ ] No concrete engine files under `game/strategy/engine/` were modified
- [ ] `python Projects/scripts/validate_phase.py PROJ-422 1` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
