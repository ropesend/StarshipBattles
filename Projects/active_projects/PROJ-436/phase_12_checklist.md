# Phase 12: Fix Fleet fractional resource-cost contract drift

**Status:** Not Started (authored from Phase 11 Codex finding #1)
**Depends on:** phase_11
**Review Mode:** standard

## Provenance

Phase 11 end-of-project Codex consult (`AgentCoordination/Scratchpad/Consult/20260518T145950Z_proj436-phase11-end-of-project/response.md`) Finding #1, verified+actionable.

## The bug

`ProductionEngine` (`game/strategy/engine/production_engine.py:639-644`) computes per-step costs as floats and records them into `item["resources_consumed"]` after calling `production_consume_resource`:

```python
for res, amount in cost_this_step.items():
    if amount > 0:
        colony_or_fleet.production_consume_resource(res, amount)
        item['resources_consumed'][res] = (
            item.get('resources_consumed', {}).get(res, 0.0) + amount
        )
```

`Fleet.production_consume_resource` (Phase 8 delegator, `fleet.py:300-304`) forwards to `Fleet.consume_cargo_resource` (`fleet.py:275-279`), which `int(round(amount))`s before unloading. The underlying `ShipCargoManager` cargo store is integer-typed throughout (`ship_cargo_manager.py:101-148`, `:371-463`).

Codex's read-only reproduction:
- Starting cargo = 1, ten calls of `production_consume_resource("metals", 0.1)` → remaining cargo stays at 1.0 (each `int(round(0.1))` = 0, nothing unloaded), but `item["resources_consumed"]["metals"]` reaches 0.9999... → **fleet builds for free**.
- Starting cargo = 2, one call of `production_consume_resource("metals", 0.6)` → `int(round(0.6))` = 1, cargo becomes 1, but `item["resources_consumed"]["metals"]` records 0.6 → **fleet overpays** by 0.4.

The bug **predates PROJ-436** (the `int(round(amount))` was introduced by commit `6d9d6fe15` "feat: implement fleet management and carrier-based combat systems"), but PROJ-436 Phase 8 explicitly defined the `IProductionResourceSource.production_consume_resource(amount: float)` Protocol signature that the Fleet implementation silently violates. The bug is latent today (production cost/rate ratios in `data/components.json` happen to produce integer per-step costs in common cases) but real.

The Phase 8 tests don't pin the fractional seam: the integration suite only exercises whole-number fleet consumption (`tests/integration/test_production_engine_container_unified.py:142-193`), and the unit dispatch tests use `MagicMock(spec=Fleet)` (`test_production_engine_consumption.py:125-137`).

## Design options for the user

### Option A — Make Fleet honor float quantities end-to-end

Drop the `int(round(amount))` in `Fleet.consume_cargo_resource`; rewrite `FleetResourceAggregator.unload_cargo_from_fleet` to accept floats; widen the underlying `ShipCargoManager` cargo store from integer-typed `Dict[str, int]` to `Dict[str, float]`.

- **Pros:** matches the Protocol contract exactly; no engine changes; fleet cargo becomes mass-priced like planet stockpile.
- **Cons:** substantial change to the cargo manager substrate (the integer-typed cargo store predates PROJ-436 and is one of the surfaces PROJ-436 explicitly did NOT touch); ripples through save shape; ripples through UI display ("3 metals" → "3.0 metals" or similar formatting).
- **Estimated scope:** 5–8 production files + 15–20 test files.

### Option B — Engine quantizes Fleet amounts (Protocol per-caller branching)

Engine asks the source whether it supports floats (new Protocol method `production_supports_float_consumption() -> bool`) and quantizes amounts before calling for Fleet sources.

- **Pros:** keeps fleet cargo integer-typed; smaller change.
- **Cons:** **re-introduces the engine-side dispatch that Phase 8 explicitly deleted**, just under a different name (capability detection instead of `context_type`). Defeats the substrate-unification goal.
- **Not recommended.**

### Option C — Truth-up the tracking via read-back (recommended)

Engine reads back the actual consumed amount by diffing before/after, and records the diff (not the requested amount) into `item["resources_consumed"]`:

```python
for res, amount in cost_this_step.items():
    if amount > 0:
        before = colony_or_fleet.production_get_resource(res)
        colony_or_fleet.production_consume_resource(res, amount)
        after = colony_or_fleet.production_get_resource(res)
        actually_consumed = before - after
        item['resources_consumed'][res] = (
            item.get('resources_consumed', {}).get(res, 0.0)
            + actually_consumed
        )
```

- **Pros:** smallest blast radius (one engine helper change, ~5 LOC); fleet cargo stays integer-typed; production tracking matches actual charge; Protocol contract gains an honest "amount may be partially consumed" docstring.
- **Cons:** for fractional cost-per-step on fleet builds, fleet may charge 0 (`int(round(0.1)) = 0`), so production effectively pauses for that resource. **Visible to UI as a stuck queue** rather than silent free-building — arguably the correct behavior, but a behavior change for any latent fractional-cost configurations.
- **Estimated scope:** 1 production file + new pinning tests (RED-then-GREEN integration test + unit test). ~15 LOC.

### Option D — Document the contract honestly without a behavior change

Update the Protocol docstring to declare that fleet consumption rounds to integer; update the engine to apply `int(round(amount))` BEFORE calling and record the rounded amount in `resources_consumed`. Planet path unaffected.

- **Pros:** explicitly aligns Protocol contract with implementation reality.
- **Cons:** Planet path gets quantized too (Planet's stockpile is float-typed and CAN consume fractional), so Planet production would lose fractional precision. Could split the rounding to Fleet-only with a capability check (which is Option B's smell again).
- **Not preferred.**

### Recommendation

Pick **Option C** unless the user wants the wider Cargo-Manager-floats overhaul (Option A). Option C is the smallest faithful fix that:
1. Closes the correctness bug (free-build / overpay both go away).
2. Matches the substrate-unification spirit (no engine-side type dispatch).
3. Surfaces the stuck-queue UX as a real UI signal for under-rated fleet construction designs (rather than masking it).

## Tasks (assuming Option C)

### Task 12.1: RED [Simple]
- [ ] Write `tests/integration/test_production_engine_fractional_fleet_cost.py` with two failing tests:
  - `test_fractional_step_cost_does_not_build_free_against_int_cargo`
  - `test_fractional_step_cost_does_not_overpay_against_int_cargo`
- [ ] Both seed a real Fleet with integer cargo, drive `_apply_resource_consumption` with `{"metals": 0.6}` / `{"metals": 0.1}` and assert the post-call diff between `fleet.get_cargo_resource(res)` and `item["resources_consumed"][res]` matches.

### Task 12.2: GREEN [Simple]
- [ ] Patch `ProductionEngine._apply_resource_consumption` to diff before/after via `production_get_resource` and record actually-consumed.
- [ ] Update the `IProductionResourceSource.production_consume_resource` docstring to declare "amount may be partially consumed by an integer-typed source; the engine reconciles via `production_get_resource` diff."
- [ ] RED tests go GREEN. Existing Phase 8 integration tests must stay green (they all use whole numbers and should not regress).
- [ ] Full sharded suite green.

### Task 12.3: Codex pre-final-check consult [Simple]
- [ ] Standard end-of-phase Codex consult per `feedback_consult_at_project_end.md`. Verify the contract drift is closed and the doc + Protocol signature both reflect the reality.

### Task 12.4: Project artifacts [Simple]
- [ ] Update `plan.md` Quick Status + Current State.
- [ ] Update `phase_state.json` phase_12 entry.
- [ ] Add `decisions.md` row dating the design choice and the disposition.

## Phase Completion Checklist
- [ ] User has picked an option (or explicitly asked to defer the bug to a separate project).
- [ ] RED tests committed and confirmed failing on a clean main.
- [ ] GREEN patch committed; sharded suite green.
- [ ] Codex consult complete; findings dispositioned.
- [ ] Artifacts updated.
