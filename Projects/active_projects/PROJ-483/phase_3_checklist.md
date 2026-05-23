# Phase 3: Minor narrowings + AI protos + Protocol narrowings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-483 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete

> Notes:
> - `IPlanet.planet_type` narrowed to `PlanetType` (enum confirmed at `game/strategy/data/planet.py`).
> - Optional/judgment narrowings (`populations`, `facilities`, `capabilities`, `resources`, `battle`, `system`, `calculate_radiation`) left as `Any` — shapes not well-known or would risk cycles.
> - `IAbilitySource.source_kind` already narrowed by PROJ-470 (verified); not re-touched.
> - TYPE_CHECKING imports use `game.core.math.Vector2` (the codebase's framework-agnostic wrapper) rather than `pygame.math.Vector2` — caught a regression in `combat_utils.get_position` during verification.
**Objective:** Bulk-apply TYPE_CHECKING string-annotation pattern to Protocol modules (16 items) and AI controllable/protocol modules (5 items). User opted in to both clusters via Phase D Step 2/3. Plus 1 cross-project coordination: `IPlanetMutator.pop_construction_item` Protocol-side narrowing.

> **Pattern reminder:** Each Protocol module already imports concrete types under `if TYPE_CHECKING:` blocks (or can add one easily). Then change `-> Any` to `-> 'TypeName'` (string forward-ref). Zero runtime cost; concrete types resolve at type-check time only.

---

## Tasks

### Task 3.1: AI controllable + protocols narrowings [Simple]
**Files:** `game/ai/interfaces/controllable.py`, `game/ai/protocols.py`
**Tests:** `pytest tests/ -k 'ai_controllable or ai_protocols'` then `mypy` on files

- [x] Narrow `IControllable.get_position` (`controllable.py:41`) from `-> Any` to `-> 'Vector2'` (TYPE_CHECKING import of `Vector2`)
- [x] Narrow `IControllable.get_velocity` (`controllable.py:46`) to `-> 'Vector2'`
- [x] Narrow `ShipControllableAdapter.get_position` (`controllable.py:258`) to `-> 'Vector2'`
- [x] Narrow `IGridEntity.position` (`protocols.py:42`) to `-> 'Vector2'`
- [x] Narrow `IProjectile.type` (`protocols.py:75`) to `-> 'AttackType'` (TYPE_CHECKING import of `AttackType`)
- [x] Verify: tests pass; `mypy` clean

### Task 3.2: core/protocols/strategy_entities.py Protocol narrowings [Medium]
**File:** `game/core/protocols/strategy_entities.py`
**Tests:** `pytest tests/` for affected protocol-dependent modules; `mypy game/core/protocols/strategy_entities.py`

- [x] Add (or extend) `if TYPE_CHECKING:` block importing `HexCoord`, `StarType`, `PlanetType` (verify enum), and any other concrete types used below
- [x] Narrow `IStarSystem.global_location` (line 30) to `-> 'HexCoord'`
- [x] Narrow `IStar.star_type` (line 64) to `-> 'StarType'`
- [x] Narrow `IPlanet.planet_type` (line 77) to `-> 'PlanetType'` (only if a `PlanetType` enum exists — otherwise leave as `Any` and note)
- [x] Narrow `IPlanet.location` (line 104) to `-> 'HexCoord | None'`
- [x] (Optional/judgment) Narrow `IPlanet.populations` (line 115) — only if the shape is well-known; otherwise leave
- [x] (Optional/judgment) Narrow `IPlanet.facilities` (line 125) — only if shape is well-known
- [x] Narrow `IFleet.location` (line 250) to `-> 'HexCoord'`
- [x] (Optional/judgment) Narrow `IFleet.capabilities`, `.resources`, `.battle` (lines 290, 295, 300) — judge if narrow is feasible without cycles
- [x] Narrow `IWarpPoint.location` (line 313) to `-> 'HexCoord'`
- [x] (Optional/judgment) Narrow `ISectorEnvironment.local_hex` (line 322), `.system` (line 327), `.calculate_radiation` (line 331) — judge case-by-case
- [x] Verify: tests pass; `mypy` clean (and that **no concrete Protocol implementer breaks** — the implementer must still satisfy the narrowed contract)

### Task 3.3: core/protocols/ui.py ICamera narrowings [Simple]
**File:** `game/core/protocols/ui.py`
**Tests:** `pytest tests/ -k 'protocols_ui or icamera'` then `mypy` on file

- [x] Add TYPE_CHECKING import for `Vector2`
- [x] Narrow `ICamera.position` (line 62) to `-> 'Vector2'`
- [x] Narrow `ICamera.world_to_screen` (line 66) — both parameter and return: `(self, world_pos: 'Vector2') -> 'Vector2'`
- [x] Narrow `ICamera.screen_to_world` (line 78) — same shape: `(self, screen_pos: 'Vector2') -> 'Vector2'`
- [x] Verify: tests pass; `mypy` clean

### Task 3.4: core/protocols/strategy_domain.py IEmpire narrowings [Simple]
**File:** `game/core/protocols/strategy_domain.py`
**Tests:** `pytest tests/ -k 'protocols_strategy_domain or iempire'` then `mypy` on file

- [x] Narrow `IEmpire.color` (line 32) from `-> Any` to `-> tuple[int, int, int]`
- [x] Narrow `IEmpire.built_ship_designs` (line 107) to `-> set[str]`
- [x] Verify: tests pass; `mypy` clean

### Task 3.5: core/protocols/strategy_mutators.py pop_construction_item narrowing [Simple — coordinate with PROJ-482]
**File:** `game/core/protocols/strategy_mutators.py`
**Tests:** `pytest tests/ -k 'planet_write_service or strategy_mutators'` then `mypy` on file

- [x] Narrow `IPlanetMutator.pop_construction_item` (line 118) from `-> Any` to `-> dict | None`
- [x] Coordinate: PROJ-482 Phase 3 Task 3.6 narrows the implementation in `planet_write_service.pop_construction_item` to the same return type. Both ends must match
- [x] Verify: tests pass; `mypy` clean

### Task 3.6: simulation/interfaces/entity_protocols.py narrowings [Medium]
**File:** `game/simulation/interfaces/entity_protocols.py`
**Tests:** `pytest tests/ -k 'entity_protocols or icombatship or iprojectile'` then `mypy` on file

- [x] Add TYPE_CHECKING import for `Vector2`, `AttackType`
- [x] Narrow `ICombatShip.position` (line 88) to `-> 'Vector2'`
- [x] Narrow `ICombatShip.velocity` (line 93) to `-> 'Vector2'`
- [x] (Optional/judgment) Narrow `ICombatShip.resources` (line 199), `.combat_engine` (line 204) — judge case-by-case
- [x] Narrow `IProjectile.position` (line 265) to `-> 'Vector2'`
- [x] Narrow `IProjectile.velocity` (line 270) to `-> 'Vector2'`
- [x] Narrow `IProjectile.type` (line 304) to `-> 'AttackType'`
- [x] Verify: tests pass; `mypy` clean

### Task 3.7: Phase verification [Simple]
- [x] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [x] Verify: `mypy` clean across all touched files
- [x] Verify: every Protocol implementer still satisfies the narrowed contract (no `[misc]` or `[override]` errors introduced)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
