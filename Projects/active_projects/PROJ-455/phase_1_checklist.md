# PROJ-455 Phase 1: End-to-end fixture construction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-455 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Construct the fixture scaffold needed to drive `ActionExecutionEngine.process_action_ticks(...)` end-to-end against a single planet with one queued FMS order. Land a single smoke test for the LAY_MINES scenario as the Phase-1 deliverable; Phase 2 extends to all 5 order types.

**Cross-bucket file-ownership rule:** This phase creates a single new test file under `tests/integration/`. No production code touched. Do NOT touch any file PROJ-452 / PROJ-453 / PROJ-454 owns.

**Source-of-truth findings:** [`findings/PROJ-455_findings.md`](findings/PROJ-455_findings.md) — read the DI-001 ActionExecutionEngine half full text, the "Context" subsection, and especially the "Fixture sizing" section at the bottom (canonical fixture spec).

**Reading order before starting:**
1. `findings/PROJ-455_findings.md` (full file)
2. `tests/integration/test_fms_planet_lay_mines.py` (full file — precedent)
3. `game/strategy/engine/action_execution_engine.py:81-329` (the `process_action_ticks` + `_process_fleet_action_tick` + `_process_planet_action_tick` + `_execute_planet_action` chain)
4. `game/strategy/engine/issuer_adapter.py` (`PlanetStagingYardIssuerAdapter`)
5. `game/strategy/services/action_time_resolver.py` (the resolver — to decide between injection vs static)

---

## Tasks

### Task 1.1: Create the new test file with the `_StubPlanet` adaptation [Simple]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py` (new)
**Tests:** `pytest tests/integration/test_process_planet_action_tick_end_to_end.py -v` (will be empty / collect-only at first)

- [x] Create the new file under `tests/integration/`. Pick the canonical name `test_process_planet_action_tick_end_to_end.py` so the filename mirrors the symbol-under-test.
- [x] Copy the module docstring shape from `tests/integration/test_fms_planet_lay_mines.py:1-26` (lines 1-26 — the multi-paragraph header explaining the test's purpose), but rewrite to reflect PROJ-455's scope: "end-to-end coverage for `_process_planet_action_tick` via `process_action_ticks`, not the direct `_execute_planet_action` precedent."
- [x] Copy the imports block from the precedent (`test_fms_planet_lay_mines.py:27-38`). The same imports are needed for PROJ-455.
- [x] Copy the `_StubPlanet` class verbatim from `test_fms_planet_lay_mines.py:41-83`. **Do not modify it** — the precedent stub already satisfies `_process_planet_action_tick`'s preconditions per the verification in `findings/PROJ-455_findings.md` "Minimum `_StubPlanet` shape".
- [x] Run `pytest tests/integration/test_process_planet_action_tick_end_to_end.py --collect-only` — should report `collected 0 items` (or whatever pytest's empty-file output is). Verifies the file imports cleanly.

**Notes:** 2026-05-19: Adopted Phase 1's Task 1.4 "sibling fixture" path — added `engine_with_fixed_resolver` rather than mutating `engine_and_processor` — to keep the precedent's fixture untouched. Picked deterministic `_FixedActionTimeResolver(action_time=1)` so the LAY_MINES order completes on tick 1. Duplicated the precedent's `_StubPlanet`, item factories (`_mine_typed` / `_fighter_typed` / `_satellite_typed` — typed `CarriedVehicle` shape post-PROJ-450 Phase 4), scenario builders, `_SCENARIO_BUILDERS` dict, and `_item_mass` helper inline rather than extracting a sibling fixture module (the duplicate is ~120 LOC; under the threshold the checklist set for extraction).

---

### Task 1.2: Copy the 5 scenario builders + item-dict factories [Simple]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`

- [x] Copy the 4 item-dict factories verbatim from `test_fms_planet_lay_mines.py:86-135`:
  - `_mine_dict(design_id: str = "mine_alpha")` (lines 86-93)
  - `_fighter_dict(design_id: str = "fighter_alpha")` (lines 96-103)
  - `_satellite_dict(design_id: str = "sat_alpha")` (lines 106-113)
  - `_fighter_ship(instance_id, owner_id) -> ShipInstance` (lines 116-124)
  - `_satellite_ship(instance_id, owner_id) -> ShipInstance` (lines 127-135)
- [x] Copy the 5 scenario builders verbatim from `test_fms_planet_lay_mines.py:138-220`:
  - `_build_lay_mines_scenario(planet, empire)` (138-149)
  - `_build_launch_fighters_scenario(planet, empire)` (152-165)
  - `_build_launch_satellites_scenario(planet, empire)` (168-181)
  - `_build_recover_fighters_scenario(planet, empire)` (184-195)
  - `_build_recover_satellites_scenario(planet, empire)` (198-211)
- [x] Copy the `_SCENARIO_BUILDERS` dict verbatim (lines 214-220) — maps each OrderType to its scenario builder.
- [x] Run `pytest tests/integration/test_process_planet_action_tick_end_to_end.py --collect-only` — still 0 items, but should still import cleanly.

**Notes:**

---

### Task 1.3: Add the `engine_and_processor` fixture [Simple]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`

- [x] Copy the `engine_and_processor` fixture verbatim from `test_fms_planet_lay_mines.py:223-227`:
  ```python
  @pytest.fixture
  def engine_and_processor() -> tuple[ActionExecutionEngine, OrderProcessor]:
      processor = OrderProcessor()
      engine = ActionExecutionEngine(order_processor=processor)
      return engine, processor
  ```
- [x] Verify the fixture imports — `OrderProcessor` and `ActionExecutionEngine` are already in the imports block from Task 1.1.

**Notes:**

---

### Task 1.4: Add a deterministic `_FixedActionTimeResolver` test double [Simple]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`

- [x] Read `game/strategy/services/action_time_resolver.py` to confirm the resolver's public surface. The `ActionExecutionEngine` constructor accepts an optional `action_time_resolver: Optional[ActionTimeResolver] = None` per `action_execution_engine.py:58`.
- [x] Add a deterministic test double at the top of the new test file (after the imports, before the `_StubPlanet` class):
  ```python
  class _FixedActionTimeResolver:
      """Test double: always returns 1 so the order completes on the first tick.
  
      Phase 1 uses this to keep the end-to-end test deterministic — the
      static ActionTimeResolver may return a configurable value depending
      on component_registry shape; the fixture should not depend on that
      indirection.
      """
      def __init__(self, action_time: int = 1) -> None:
          self._action_time = action_time
      def resolve_action_time(self, _issuer, _order, _component_registry) -> int:
          return self._action_time
  ```
- [x] Modify the `engine_and_processor` fixture (or add a sibling `engine_with_fixed_resolver` fixture) so the engine is constructed with `action_time_resolver=_FixedActionTimeResolver(1)`. This makes one-tick completion deterministic.

**Notes:** Verify by inspection that `ActionExecutionEngine._process_planet_action_tick` reads from `self._action_time_resolver` (it does — see lines 269-276 of `action_execution_engine.py`). The fallback to the static method only fires when the resolver is None.

---

### Task 1.5: Add the LAY_MINES smoke test driving `process_action_ticks` end-to-end [Medium]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`
**Tests:** `pytest tests/integration/test_process_planet_action_tick_end_to_end.py::test_lay_mines_e2e_smoke -v`

- [x] Add `test_lay_mines_e2e_smoke(engine_and_processor)`:
  ```python
  def test_lay_mines_e2e_smoke(engine_and_processor) -> None:
      engine, _processor = engine_and_processor
  
      hex_c = HexCoord(0, 0)
      planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
      empire = SimpleNamespace(
          id=7,
          name="E",
          fleets=[],
          colonies=[planet],
          deployed_groups=[],
      )
      empire.deployed_groups_of = lambda cls, _e=empire: [
          g for g in _e.deployed_groups if isinstance(g, cls)
      ]
  
      _build_lay_mines_scenario(planet, empire)
      assert planet.get_current_order() is not None
      assert planet.get_current_order().type is OrderType.LAY_MINES
  
      # Drive the FULL engine entry point, not the _execute_planet_action shortcut.
      results = engine.process_action_ticks(
          empires=[empire],
          galaxy=None,
          tick=1,
          component_registry=None,
      )
  
      # The action should complete on tick 1 (resolver returns action_time=1).
      assert len(results) == 1
      assert results[0].order_type is OrderType.LAY_MINES
      assert results[0].action_completed is True
      assert planet.get_current_order() is None, (
          "Planet order queue should advance after the engine-mediated "
          "LAY_MINES dispatch."
      )
  ```
- [x] **RED**: run the test. With the `_FixedActionTimeResolver(1)` from Task 1.4 wired into the engine fixture, the test should pass — but verify by **temporarily** removing the resolver injection (so the engine falls back to the static resolver) and re-running. The test should either fail or take an indeterminate number of ticks. Re-add the resolver; confirm green.
- [x] **Alternative RED**: temporarily mutate `_build_lay_mines_scenario` to not push the mine dict onto the staging yard. Verify the test fails (the handler would have nothing to lay). Restore.

**Notes:** This smoke test is the Phase-1 deliverable. Phase 2 parametrises it across all 5 order types.

---

## Phase Completion Checklist

When all tasks above are checked off:

- [x] `tests/integration/test_process_planet_action_tick_end_to_end.py` exists with the smoke test + fixtures
- [x] `pytest tests/integration/test_process_planet_action_tick_end_to_end.py -v` green (1 test)
- [x] `pytest tests/integration/test_fms_planet_lay_mines.py -v` still green (PROJ-445 Phase 1 precedent — must not regress)
- [x] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [x] Run `python Projects/scripts/validate_phase.py PROJ-455 1` — PASSED
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

## Notes / Deferrals

- **Shared fixture extraction** — if Task 1.1 + Task 1.2 result in >100 LOC of duplicated content from the precedent file, extract the shared bits into `tests/integration/_planet_fms_fixtures.py` and import from both. Document the decision in `decisions.md`. Otherwise duplicate inline.
- **Static `ActionTimeResolver` fallback** — Phase 1 uses the deterministic test double for control. Phase 2 may add a separate test for the static-resolver path if it adds coverage value; that decision is deferred to Phase 2.
- **`component_registry=None`** — verified safe at engine call site; the resolver receives `None` and the handlers tolerate it. No fixture must build a component registry.
