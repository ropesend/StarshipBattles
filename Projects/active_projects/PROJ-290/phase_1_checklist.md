# Phase 1: Empire-wide populace upkeep + treasury line

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-290 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Aggregate multi-resource population upkeep across every empire colony into `EmpireEconomySnapshot.total_population_upkeep`. Render as a new expense row in `EmpireTreasuryPanel`. Hide the row when all values are zero.

---

## Tasks

### Task 1.1: Write failing tests for aggregation [Medium]
**File:** `tests/unit/strategy/engine/test_empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py::TestPopulationUpkeepAggregation`

- [x] Test: empire with no colonies → `total_population_upkeep == {}`.
- [x] Test: empire with colonies but no populations → `total_population_upkeep == {}` (or all-zero; confirm with convention).
- [x] Test: single colony with 1000 humans → `total_population_upkeep == {"organics": 1.0, "metals": 0.1, "radioactives": 0.01}`.
- [x] Test: multi-colony → values sum across colonies per resource.
- [x] Test: multi-species colony → upkeep aggregates both species per resource.
- [x] Test: food_allocation scales upkeep linearly.

**Notes:** Convention landed: sparse dict (only resources with non-zero demand), empty `{}` when zero populations (drives treasury row hiding). Also added a backward-compat test: calculator constructed with just `registries=` (no economy/race_registry) leaves the field as `{}`. Plus snapshot-default test at `TestEmpireEconomySnapshot.test_empty_snapshot_defaults_to_empty_dicts`.

### Task 1.2: Add `total_population_upkeep` to `EmpireEconomySnapshot` [Medium]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy_calculator.py`

- [x] Add field `total_population_upkeep: Dict[str, float]` to the dataclass.
- [x] In the calculator's main compute path, iterate `empire.colonies` and call `PlanetEconomyProjector.project(colony)`; accumulate each `ResourceProjection.upkeep` into `total_population_upkeep[res_id]`.
- [x] Inject `PlanetEconomyProjector` via constructor (or lazy-init the projector with the facade's dependencies).

**Notes:** Chose lazy-init inside `_aggregate_population_upkeep` over constructor injection — keeps existing callers (`EmpireEconomyCalculator(registries=...)`) backward-compatible. New kwargs `economy_config: Optional[EconomyConfig] = None` + `race_registry: Optional[IRaceRegistry] = None` default to None; when either is missing the upkeep dict stays `{}` and the treasury row hides. Production callsite updated: [empire_panel_window.py:189](game/ui/screens/empire_panel_window.py#L189) threads both via `get_default_economy_config()` + `facade.get_race_registry()` (wired through `strategy_window_manager._open_empire_panel_window`). Zero-upkeep entries skipped during accumulation (the projector returns 0 upkeep for missing resources; we only emit resources with non-zero demand).

### Task 1.3: Write failing tests for treasury row rendering [Medium]
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py` (create if missing)
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [x] Test: snapshot with `total_population_upkeep={"organics": 5.0}` renders a "Population Upkeep" row with `-5.0` cell in the organics column.
- [x] Test: snapshot with `total_population_upkeep={}` (or all zeros) HIDES the row.
- [x] Test: multi-resource snapshot renders one signed cell per resource in order.

**Notes:** 5 tests in new `TestPopulationUpkeepRow` class. Also pinned the insertion order (row goes BEFORE the Total row) so future refactors can't accidentally rearrange the expense section.

### Task 1.4: Render "Population Upkeep" row in `EmpireTreasuryPanel` [Medium]
**File:** `game/ui/panels/empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [x] Add a new row in the Expenses section labeled "Population Upkeep".
- [x] Populate cells from `snapshot.total_population_upkeep` via `format_signed_float(-value, 1)` (negated — it's a drain).
- [x] Skip rendering the row when all dict values are <= 0.0 (hidden on fresh-game / no-pop state).

**Notes:** Reused the existing `_build_row`'s `_format_value` pipeline rather than introducing `format_signed_float` — the panel already shows negatives for other drain rows via pre-negation. The row tuple carries `{res: -value}` so the standard formatter writes `"-5"` etc.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: uncolonized habitability)
