# Phase 1: Empire-wide populace upkeep + treasury line

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-290 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Aggregate multi-resource population upkeep across every empire colony into `EmpireEconomySnapshot.total_population_upkeep`. Render as a new expense row in `EmpireTreasuryPanel`. Hide the row when all values are zero.

---

## Tasks

### Task 1.1: Write failing tests for aggregation [Medium]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py::TestPopulationUpkeepAggregation`

- [ ] Test: empire with no colonies → `total_population_upkeep == {}`.
- [ ] Test: empire with colonies but no populations → `total_population_upkeep == {}` (or all-zero; confirm with convention).
- [ ] Test: single colony with 1000 humans → `total_population_upkeep == {"organics": 1.0, "metals": 0.1, "radioactives": 0.01}`.
- [ ] Test: multi-colony → values sum across colonies per resource.
- [ ] Test: multi-species colony → upkeep aggregates both species per resource.
- [ ] Test: food_allocation scales upkeep linearly.

**Notes:**

### Task 1.2: Add `total_population_upkeep` to `EmpireEconomySnapshot` [Medium]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [ ] Add field `total_population_upkeep: Dict[str, float]` to the dataclass.
- [ ] In the calculator's main compute path, iterate `empire.colonies` and call `PlanetEconomyProjector.project(colony)`; accumulate each `ResourceProjection.upkeep` into `total_population_upkeep[res_id]`.
- [ ] Inject `PlanetEconomyProjector` via constructor (or lazy-init the projector with the facade's dependencies).

**Notes:**

### Task 1.3: Write failing tests for treasury row rendering [Medium]
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py` (create if missing)
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] Test: snapshot with `total_population_upkeep={"organics": 5.0}` renders a "Population Upkeep" row with `-5.0` cell in the organics column.
- [ ] Test: snapshot with `total_population_upkeep={}` (or all zeros) HIDES the row.
- [ ] Test: multi-resource snapshot renders one signed cell per resource in order.

**Notes:**

### Task 1.4: Render "Population Upkeep" row in `EmpireTreasuryPanel` [Medium]
**File:** `game/ui/panels/empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] Add a new row in the Expenses section labeled "Population Upkeep".
- [ ] Populate cells from `snapshot.total_population_upkeep` via `format_signed_float(-value, 1)` (negated — it's a drain).
- [ ] Skip rendering the row when all dict values are <= 0.0 (hidden on fresh-game / no-pop state).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: uncolonized habitability)
