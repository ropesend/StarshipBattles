# Phase 3: Minor narrowings + AI protos + Protocol narrowings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-483 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bulk-apply TYPE_CHECKING string-annotation pattern to Protocol modules (16 items) and AI controllable/protocol modules (5 items). User opted in to both clusters via Phase D Step 2/3. Plus 1 cross-project coordination: `IPlanetMutator.pop_construction_item` Protocol-side narrowing.

> **Pattern reminder:** Each Protocol module already imports concrete types under `if TYPE_CHECKING:` blocks (or can add one easily). Then change `-> Any` to `-> 'TypeName'` (string forward-ref). Zero runtime cost; concrete types resolve at type-check time only.

---

## Tasks

### Task 3.1: AI controllable + protocols narrowings [Simple]
**Files:** `game/ai/interfaces/controllable.py`, `game/ai/protocols.py`
**Tests:** `pytest tests/ -k 'ai_controllable or ai_protocols'` then `mypy` on files

- [ ] Narrow `IControllable.get_position` (`controllable.py:41`) from `-> Any` to `-> 'Vector2'` (TYPE_CHECKING import of `Vector2`)
- [ ] Narrow `IControllable.get_velocity` (`controllable.py:46`) to `-> 'Vector2'`
- [ ] Narrow `ShipControllableAdapter.get_position` (`controllable.py:258`) to `-> 'Vector2'`
- [ ] Narrow `IGridEntity.position` (`protocols.py:42`) to `-> 'Vector2'`
- [ ] Narrow `IProjectile.type` (`protocols.py:75`) to `-> 'AttackType'` (TYPE_CHECKING import of `AttackType`)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.2: core/protocols/strategy_entities.py Protocol narrowings [Medium]
**File:** `game/core/protocols/strategy_entities.py`
**Tests:** `pytest tests/` for affected protocol-dependent modules; `mypy game/core/protocols/strategy_entities.py`

- [ ] Add (or extend) `if TYPE_CHECKING:` block importing `HexCoord`, `StarType`, `PlanetType` (verify enum), and any other concrete types used below
- [ ] Narrow `IStarSystem.global_location` (line 30) to `-> 'HexCoord'`
- [ ] Narrow `IStar.star_type` (line 64) to `-> 'StarType'`
- [ ] Narrow `IPlanet.planet_type` (line 77) to `-> 'PlanetType'` (only if a `PlanetType` enum exists — otherwise leave as `Any` and note)
- [ ] Narrow `IPlanet.location` (line 104) to `-> 'HexCoord | None'`
- [ ] (Optional/judgment) Narrow `IPlanet.populations` (line 115) — only if the shape is well-known; otherwise leave
- [ ] (Optional/judgment) Narrow `IPlanet.facilities` (line 125) — only if shape is well-known
- [ ] Narrow `IFleet.location` (line 250) to `-> 'HexCoord'`
- [ ] (Optional/judgment) Narrow `IFleet.capabilities`, `.resources`, `.battle` (lines 290, 295, 300) — judge if narrow is feasible without cycles
- [ ] Narrow `IWarpPoint.location` (line 313) to `-> 'HexCoord'`
- [ ] (Optional/judgment) Narrow `ISectorEnvironment.local_hex` (line 322), `.system` (line 327), `.calculate_radiation` (line 331) — judge case-by-case
- [ ] Verify: tests pass; `mypy` clean (and that **no concrete Protocol implementer breaks** — the implementer must still satisfy the narrowed contract)

### Task 3.3: core/protocols/ui.py ICamera narrowings [Simple]
**File:** `game/core/protocols/ui.py`
**Tests:** `pytest tests/ -k 'protocols_ui or icamera'` then `mypy` on file

- [ ] Add TYPE_CHECKING import for `Vector2`
- [ ] Narrow `ICamera.position` (line 62) to `-> 'Vector2'`
- [ ] Narrow `ICamera.world_to_screen` (line 66) — both parameter and return: `(self, world_pos: 'Vector2') -> 'Vector2'`
- [ ] Narrow `ICamera.screen_to_world` (line 78) — same shape: `(self, screen_pos: 'Vector2') -> 'Vector2'`
- [ ] Verify: tests pass; `mypy` clean

### Task 3.4: core/protocols/strategy_domain.py IEmpire narrowings [Simple]
**File:** `game/core/protocols/strategy_domain.py`
**Tests:** `pytest tests/ -k 'protocols_strategy_domain or iempire'` then `mypy` on file

- [ ] Narrow `IEmpire.color` (line 32) from `-> Any` to `-> tuple[int, int, int]`
- [ ] Narrow `IEmpire.built_ship_designs` (line 107) to `-> set[str]`
- [ ] Verify: tests pass; `mypy` clean

### Task 3.5: core/protocols/strategy_mutators.py pop_construction_item narrowing [Simple — coordinate with PROJ-482]
**File:** `game/core/protocols/strategy_mutators.py`
**Tests:** `pytest tests/ -k 'planet_write_service or strategy_mutators'` then `mypy` on file

- [ ] Narrow `IPlanetMutator.pop_construction_item` (line 118) from `-> Any` to `-> dict | None`
- [ ] Coordinate: PROJ-482 Phase 3 Task 3.6 narrows the implementation in `planet_write_service.pop_construction_item` to the same return type. Both ends must match
- [ ] Verify: tests pass; `mypy` clean

### Task 3.6: simulation/interfaces/entity_protocols.py narrowings [Medium]
**File:** `game/simulation/interfaces/entity_protocols.py`
**Tests:** `pytest tests/ -k 'entity_protocols or icombatship or iprojectile'` then `mypy` on file

- [ ] Add TYPE_CHECKING import for `Vector2`, `AttackType`
- [ ] Narrow `ICombatShip.position` (line 88) to `-> 'Vector2'`
- [ ] Narrow `ICombatShip.velocity` (line 93) to `-> 'Vector2'`
- [ ] (Optional/judgment) Narrow `ICombatShip.resources` (line 199), `.combat_engine` (line 204) — judge case-by-case
- [ ] Narrow `IProjectile.position` (line 265) to `-> 'Vector2'`
- [ ] Narrow `IProjectile.velocity` (line 270) to `-> 'Vector2'`
- [ ] Narrow `IProjectile.type` (line 304) to `-> 'AttackType'`
- [ ] Verify: tests pass; `mypy` clean

### Task 3.7: Phase verification [Simple]
- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [ ] Verify: `mypy` clean across all touched files
- [ ] Verify: every Protocol implementer still satisfies the narrowed contract (no `[misc]` or `[override]` errors introduced)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
