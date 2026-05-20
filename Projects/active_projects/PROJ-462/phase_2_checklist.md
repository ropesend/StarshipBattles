# Phase 2: Major (core/engine narrowing + ignore removal)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-462 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow the verified MAJOR foundation `-> Any` returns and tighten the core protocol contracts, applying the boundary-preserving carve-out: narrow strategy-map-specific protocol surfaces to core types only; leave intentionally polymorphic seams as `Any`.

---

## Tasks

### Task 2.1: Narrow core formula evaluator [Medium]
**File:** `game/core/formula_evaluator.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/formula_evaluator.py`

- [ ] Narrow `_eval_node` (line 81) from `-> Any` to `-> int | float | bool | list[float] | tuple[float, ...]` so `FormulaEvaluator.evaluate()` stops flowing `Any`
- [ ] Verify: pytest passes; `mypy game/core/formula_evaluator.py` shows no new errors

### Task 2.2: Narrow registry validator getters [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/registry.py`

- [ ] Narrow `RegistryManager.get_validator` (line 248) from `-> Any` to `-> ShipDesignValidator | None`
- [ ] Narrow module-level `get_validator` (line 339) from `-> Any` to `-> ShipDesignValidator | None`
- [ ] Verify: pytest passes; `mypy game/core/registry.py` shows no new errors

### Task 2.3: Narrow screen state machine accessors [Simple]
**File:** `game/core/state_machine.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/state_machine.py`

- [ ] Narrow `ScreenStateMachine.state` property (line 69) from `-> Any` to `-> GameState`
- [ ] Narrow `ScreenStateMachine.pop_and_return` (line 133) from `-> Any` to `-> GameState`
- [ ] Verify: pytest passes; `mypy game/core/state_machine.py` shows no new errors

### Task 2.4: Tighten core entity protocol Any returns (boundary-preserving) [Medium]
**File:** `game/core/protocols/strategy_entities.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/protocols/strategy_entities.py`

- [ ] Narrow strategy-map-specific surfaces that can point at core types: `IStarSystem.global_location` (line 30) → `HexCoord`; `IPlanet.location` (line 104), `IFleet.location` (line 250), `IWarpPoint.location`, `ISectorEnvironment.local_hex` (line 322) → `HexCoord`
- [ ] Narrow `IStarSystem.stars/planets/warp_points/storms` `list[Any]` to `list[Star]`/`list[Planet]`/`list[WarpPoint]`/`list[Storm]` where the element type is a core/same-module protocol type
- [ ] CARVE-OUT: leave `ICombatant.position`, `ICombatShip.position` (combat.py), and `ILocatable.location` (common.py) as `-> Any` — these are intentionally polymorphic (Vector2 in simulation vs HexCoord in strategy). Do NOT import strategy concrete types into `game/core/protocols/`
- [ ] Verify: pytest passes; `mypy game/core/protocols/strategy_entities.py` shows no new errors

### Task 2.5: Tighten core mutator protocol Any params [Simple]
**File:** `game/core/protocols/strategy_mutators.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/protocols/strategy_mutators.py`

- [ ] Tighten `IPlanetMutator` params: `set_owner_id(owner_id: Any)` → `int | None`; `set_atmosphere`/`set_atmosphere_target(value: Any)` → `dict[str, float]`; `set_gravity_target`/`set_water_target` → `float`
- [ ] Tighten `IFleetMutator`: `add_ship`/`remove_ship(ship: Any)` → `ShipInstance`; `add_task_force`/`remove_task_force` → `TaskForce`; `set_fleet_policy` → `CombatPolicy`
- [ ] Tighten `IEmpireMutator.remove_fleet`/`prune_empty_fleets` `event_bus: Any` → `EventBus | None`
- [ ] Tighten `IShipInstanceMutator.set_activation_state(state: Any)` → `str` (or the activation enum)
- [ ] Verify: pytest passes; `mypy game/core/protocols/strategy_mutators.py` shows no new errors

### Task 2.6: Fix core json_utils implicit Optional [Simple]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/core/json_utils.py`

- [ ] Fix `register_serializable` (line 56) `type_name: str = None` → `str | None = None`
- [ ] Verify: pytest passes; `mypy game/core/json_utils.py` shows no new errors

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
