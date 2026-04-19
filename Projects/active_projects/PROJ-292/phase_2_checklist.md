# Phase 2: M1 — Introduce empire_economy_service.py facade; remove UI→engine direct imports

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-292 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the layer violation where UI panels directly import `EmpireEconomyCalculator` from the engine layer. Introduce a service-layer facade that exposes a read-only snapshot getter.

---

## Pre-flight

> ⚠️ **DO NOT START Phase 2 until PROJ-291 Phase 1 (C1 fix) has landed.** Both touch `empire_economy_calculator.py`. PROJ-291's 1-line addition needs to land first; this phase wraps the post-fix calculator.

---

## Tasks

### Task 2.1: Verify PROJ-291 Phase 1 has landed [Simple]
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py::TestTreasuryTotalIncludesUpkeep -v`

- [ ] Run the test. If it doesn't exist or fails, STOP. Wait for PROJ-291 Phase 1 to complete.
- [ ] If green, confirm the C1 fix is at line 147-150 of `empire_economy_calculator.py` (the `total_expenses` summation includes `total_population_upkeep`).

**Notes:**

### Task 2.2: Write failing tests for the new facade [Medium]
**File:** `tests/unit/strategy/services/test_empire_economy_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_service.py -v`

- [ ] Test 1: `test_service_get_snapshot_returns_same_shape_as_calculator`. Construct an empire. Call `EmpireEconomyService(...).get_snapshot(empire)`. Call `EmpireEconomyCalculator(...).calculate(empire)` directly. Assert the two snapshots have equal field values.
- [ ] Test 2: `test_service_re_exports_snapshot_dataclass`. Verify `from game.strategy.services.empire_economy_service import EmpireEconomySnapshot` works (re-export).
- [ ] Test 3: `test_service_does_not_expose_calculator`. Verify the calculator class is NOT importable from `game.strategy.services.empire_economy_service` (i.e. `from game.strategy.services.empire_economy_service import EmpireEconomyCalculator` raises ImportError or returns the original engine-layer class — depending on `__all__` discipline).
- [ ] Run tests. Expect failures (the service doesn't exist yet).

**Notes:**

### Task 2.3: Implement the service facade [Medium]
**File:** `game/strategy/services/empire_economy_service.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_service.py -v`

- [ ] Create the file with the shape from PROJ-292 design.md § M1:
  ```python
  """Service-layer facade over EmpireEconomyCalculator (PROJ-292 M1).

  UI panels must not import from game.strategy.engine directly per
  docs/01_ARCHITECTURE.md layer rules. This facade exposes the read
  surface — calculator stays in the engine layer.
  """
  from typing import TYPE_CHECKING, Any, Optional

  from game.strategy.engine.empire_economy_calculator import (
      EmpireEconomyCalculator,
      EmpireEconomySnapshot,
  )

  if TYPE_CHECKING:
      from game.strategy.data.empire import Empire


  class EmpireEconomyService:
      """Read-only snapshot service over EmpireEconomyCalculator."""

      def __init__(self, registries, economy_config=None, race_registry=None):
          self._calculator = EmpireEconomyCalculator(
              registries=registries,
              economy_config=economy_config,
              race_registry=race_registry,
          )

      def get_snapshot(self, empire: 'Empire') -> 'EmpireEconomySnapshot':
          """Return a fresh EmpireEconomySnapshot for `empire`."""
          return self._calculator.calculate(empire)


  __all__ = ["EmpireEconomyService", "EmpireEconomySnapshot"]
  ```
- [ ] Run Task 2.2's tests — Tests 1 + 2 should pass. Test 3 may need an explicit `__all__` discipline check (the import works but the symbol shouldn't be in `__all__`).
- [ ] Run the targeted suite — green.

**Notes:** Match the constructor signature exactly to whatever the post-PROJ-291 calculator accepts.

### Task 2.4: Migrate empire_treasury_panel.py to the service [Medium]
**File:** [game/ui/panels/empire_treasury_panel.py:19](game/ui/panels/empire_treasury_panel.py#L19)
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py -v`

- [ ] Replace the import at line 19:
  ```python
  # Before:
  from game.strategy.engine.empire_economy_calculator import EmpireEconomySnapshot
  # After:
  from game.strategy.services.empire_economy_service import EmpireEconomySnapshot
  ```
- [ ] If the panel constructs the calculator directly, switch to the service: `EmpireEconomyService(...).get_snapshot(empire)`.
- [ ] Run the file's tests — green.

**Notes:**

### Task 2.5: Migrate empire_panel_window.py to the service [Medium]
**File:** [game/ui/screens/empire_panel_window.py:18](game/ui/screens/empire_panel_window.py#L18)
**Tests:** `pytest tests/unit/ui/screens/test_empire_panel_window.py -v`

- [ ] Same migration as Task 2.4.
- [ ] If the window constructs `EmpireEconomyCalculator(...)` directly, switch to `EmpireEconomyService(...).get_snapshot(empire)`.

**Notes:**

### Task 2.6: Verify the layer violation is gone [Simple]
**Tests:** `grep -rn "from game.strategy.engine" game/ui/`

- [ ] Run the grep. Expected output: ZERO results (or only `# noqa` comments explaining intentional exceptions).
- [ ] If any UI files still import directly from `game.strategy.engine.*`, migrate them in this phase.

**Notes:**

### Task 2.7: Targeted regression suite [Simple]
**Tests:** `pytest tests/unit/ui/ tests/unit/strategy/services/ -q`

- [ ] UI suite + services suite green.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
