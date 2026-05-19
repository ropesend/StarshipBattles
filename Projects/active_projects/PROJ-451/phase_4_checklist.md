# Phase 4: Stocked-fleet ratchet tests for `IProductionResourceSource` implementers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-451 4`
> 2. New ratchet test file passes for every concrete implementer
> 3. Sharded suite green
> 4. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3 (engine-side bool-return handling decision made)
**Objective:** Add a parametrized ratchet test that, for every concrete `IProductionResourceSource` implementer (Planet, Fleet, future implementers), asserts the affordability/consumption symmetry contract: `has_resources(costs)==True → consume(resource, amount)==True` for each `(resource, amount)` in `costs`. The ratchet acts as defense-in-depth against future implementers breaking the contract.

**File ownership rule:** This project owns the new ratchet test file. No production code changes.

**Source-of-truth findings:** F-B-019 closure (implementer-side ratchet) — see [findings/PROJ-451_findings.md](findings/PROJ-451_findings.md).

---

## Tasks

### Task 4.1: Identify concrete implementers [Simple]
**Tools:** `Grep`

- [ ] Run:
  ```bash
  rg "def production_consume_resource" game/
  ```
- [ ] Expected matches:
  - `game/strategy/data/planet.py:307` — `Planet.production_consume_resource` (Phase 0 verified)
  - `game/strategy/data/fleet.py` — `Fleet.production_consume_resource` (verify via direct read; the Fleet implementation likely sits near `consume_cargo_resource` at lines 271-300)
- [ ] List any other implementers found
- [ ] If a new implementer is found that doesn't already pass the ratchet semantics, log a finding for follow-up

### Task 4.2: Create the ratchet test file [Medium]
**File:** `tests/unit/strategy/data/test_production_resource_source_ratchet.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_production_resource_source_ratchet.py -v`

- [ ] Create the test file:
  ```python
  """PROJ-451 Phase 4 ratchet: stocked IProductionResourceSource
  implementers must satisfy the affordability/consumption symmetry
  contract.

  For each concrete implementer (Planet, Fleet, ...) and a range of
  realistic cost shapes, the test asserts:

      if implementer.production_has_resources(costs):
          for resource_type, amount in costs.items():
              assert implementer.production_consume_resource(
                  resource_type, amount
              ) is True

  This defends against future implementers introducing contract
  breaches that the engine assertion / defensive plumbing in Phase 3
  would catch only at runtime.
  """
  import pytest
  from game.strategy.data.fleet import Fleet
  from game.strategy.data.planet import Planet
  from tests.fixtures.strategy_entities import (
      create_test_fleet,
      create_test_planet,
  )

  @pytest.fixture
  def stocked_planet(fresh_registries):
      planet = create_test_planet(fresh_registries=fresh_registries)
      planet._stockpile = {"metals": 100.0, "organics": 50.0, "fuel": 10.0}
      return planet

  @pytest.fixture
  def stocked_fleet(fresh_registries):
      fleet = create_test_fleet(registries=fresh_registries)
      # Load fleet cargo via the resource aggregator path
      fleet.resources.load_cargo_to_fleet("metals", 100)
      fleet.resources.load_cargo_to_fleet("organics", 50)
      return fleet

  @pytest.mark.parametrize("costs", [
      {"metals": 1.0},                # integer-shaped float
      {"metals": 1.5},                # fractional
      {"metals": 0.1},                # rounds-to-zero candidate
      {"metals": 50.0, "organics": 25.0},  # multi-resource
      {"metals": 0.0},                # zero requested
  ])
  def test_planet_consume_succeeds_when_affordability_passes(
      stocked_planet, costs,
  ):
      """Planet (float stockpile) — symmetric on float comparisons."""
      if stocked_planet.production_has_resources(costs):
          for resource_type, amount in costs.items():
              if amount > 0:
                  assert stocked_planet.production_consume_resource(
                      resource_type, amount
                  ) is True, (
                      f"Planet contract breach: has_resources({costs!r}) returned True "
                      f"but consume({resource_type!r}, {amount}) returned False"
                  )

  @pytest.mark.parametrize("costs", [
      {"metals": 1.0},
      {"metals": 1.5},
      {"metals": 0.1},  # rounds to 0; has_resources should also see 0
      {"metals": 50.0, "organics": 25.0},
      {"metals": 0.0},
  ])
  def test_fleet_consume_succeeds_when_affordability_passes(
      stocked_fleet, costs,
  ):
      """Fleet (integer cargo store) — symmetric on int(round(...)) values
      (PROJ-444 Phase 2 closed the data-layer half)."""
      if stocked_fleet.production_has_resources(costs):
          for resource_type, amount in costs.items():
              if amount > 0:
                  assert stocked_fleet.production_consume_resource(
                      resource_type, amount
                  ) is True, (
                      f"Fleet contract breach: has_resources({costs!r}) returned True "
                      f"but consume({resource_type!r}, {amount}) returned False"
                  )
  ```
- [ ] Run; verify both parametrized tests pass for Planet and Fleet

**Notes**: The fixture `create_test_planet` / `create_test_fleet` come from `tests/fixtures/strategy_entities.py`. After PROJ-449 Phase 1, those fixtures use the post-rename private kwargs. If PROJ-451 lands before PROJ-449 Phase 1, the legacy kwargs are still in place — Phase 4 doesn't need to wait for PROJ-449.

### Task 4.3: Add ratchet for edge-case "rounds-to-zero" symmetry [Medium]
**File:** `tests/unit/strategy/data/test_production_resource_source_ratchet.py` (extend)
**Tests:** `pytest tests/unit/strategy/data/test_production_resource_source_ratchet.py -v`

- [ ] Add test that exercises the specific DI-006 case explicitly:
  ```python
  def test_fleet_fractional_cost_rounds_to_zero_symmetry(stocked_fleet):
      """PROJ-444 Phase 2 closed the data-layer half: Fleet.has_cargo_resources
      now rounds with int(round(amount)) symmetrically to consume_cargo_resource.
      Verify the ratchet still holds for the rounds-to-zero case.
      """
      stocked_fleet.resources.load_cargo_to_fleet("metals", 1)  # 1 integer unit
      assert stocked_fleet.production_has_resources({"metals": 0.1}) is True  # 0.1 rounds to 0 ≤ 1
      assert stocked_fleet.production_consume_resource("metals", 0.1) is True  # consume returns True
      # actually_consumed via diff is 0 (the engine's Phase 2 detection); but consume itself returns True
      assert stocked_fleet.production_has_resources({"metals": 0.4}) is True  # 0.4 rounds to 0
      assert stocked_fleet.production_consume_resource("metals", 0.4) is True
      assert stocked_fleet.production_has_resources({"metals": 0.6}) is True  # 0.6 rounds to 1; cargo=1 ≥ 1
      assert stocked_fleet.production_consume_resource("metals", 0.6) is True  # actually deducts 1
      # Now cargo is 0; further consume should still return True for amounts that round to 0
      assert stocked_fleet.production_has_resources({"metals": 0.1}) is True  # 0 ≤ 0
      assert stocked_fleet.production_consume_resource("metals", 0.1) is True
  ```
- [ ] This test pins the exact invariant the engine relies on. If a future change accidentally breaks the symmetry (e.g. `has_cargo_resources` un-rounds), the test fires immediately.

### Task 4.4: Sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green
- [ ] Commit message: `PROJ-451 Phase 4: stocked-fleet ratchet for IProductionResourceSource (closes F-B-019; defense-in-depth for affordability/consumption contract)`

---

## Phase Completion Checklist
- [ ] `tests/unit/strategy/data/test_production_resource_source_ratchet.py` exists
- [ ] Ratchet test passes for Planet (float stockpile)
- [ ] Ratchet test passes for Fleet (integer cargo store with int(round(...)) rounding)
- [ ] Edge-case rounds-to-zero symmetry test passes
- [ ] Sharded suite green
- [ ] F-B-019 closed
- [ ] Plan.md Quick Status → Complete; project ready for end-of-project Codex consult

## Notes / Risks / Coordination Touchpoints
- **Defense-in-depth.** Phase 3 added the engine-side enforcement (assertion in option b OR bool capture in option a). Phase 4 adds the implementer-side ratchet. Both layers together make the contract bulletproof.
- **PROJ-449 fixture renaming risk.** If PROJ-449 Phase 1 lands first and renames the strategy_entities fixture kwargs, this test may need its fixture calls to use the new private-kwarg spellings. Since PROJ-451 is parallel-safe, the order of commits is unpredictable — write the test to use whichever kwarg spelling matches the current HEAD at the time of writing.
- **Future implementers.** When a new IProductionResourceSource implementer lands (e.g. a Complex that satisfies the Protocol), add it to the parametrize list. The ratchet then catches contract breaches at the implementer level before they reach the engine.
- **Edge case: amount = 0.** `production_consume_resource('x', 0.0)` — should this return True or False? The Protocol contract docstring should clarify. Most implementations would return True (consuming 0 trivially succeeds), but verify with the ratchet test fixture.
