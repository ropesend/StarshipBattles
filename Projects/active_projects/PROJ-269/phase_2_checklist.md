# Phase 2: Component HP Persistence

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add per-component HP persistence at the strategic layer via `ShipInstance.components: Dict[str, ComponentState]`. Wire the round-trip so damage carries through every strategy battle: `ShipInstance → ShipSpec → Ship (in engine) → ShipOutcome → ShipInstance`. Implement the real strategy `PostBattleHook` that writes outcome HP back to `ShipInstance.components` and removes destroyed ships from fleets. After this phase, a damaged ship entering its next strategy battle still has its damage.

---

### Task 2.1: Add `ComponentState` + `ShipInstance.components` field [Medium]
**Files:**
- `game/strategy/fleets/ship_instance.py`
- `game/strategy/fleets/component_state.py` (new)

**Tests:** `pytest tests/unit/strategy/fleets/test_ship_instance.py tests/unit/strategy/fleets/test_component_state.py --testmon`

- [ ] Write failing tests:
  - `ComponentState(component_id, instance_index, current_hp, is_active)` dataclass
  - `ShipInstance.components: Dict[str, ComponentState]` field exists; key format `f"{component_id}#{instance_index}"`
  - Newly-constructed `ShipInstance` from a design has `components` populated with full HP for every component in every layer
  - Serialization round-trip: `ShipInstance.to_dict() → ShipInstance.from_dict()` preserves `components`
- [ ] Implement `ComponentState` dataclass in new `component_state.py`
- [ ] Extend `ShipInstance` with `components` field; populate on construction via `_build_full_hp_components_from_design(design, registries)` helper
- [ ] Update `ShipInstance.to_dict()` / `from_dict()` serialization to include `components` dict
- [ ] Verify: all tests pass
- [ ] Verify: loading an existing save without `components` key defaults to full HP (graceful degradation per CLAUDE.md "saves are disposable" rule)

**Notes:**

---

### Task 2.2: Wire `ShipInstance ↔ Ship` to round-trip component HP [Medium]
**Files:**
- `game/strategy/fleets/ship_instance.py` (modify `to_ship`)
- `game/simulation/entities/ship_serialization.py` (possibly modify `ShipSerializer.from_dict`)
- `game/simulation/entities/ship.py` (extend if needed)

**Tests:** `pytest tests/unit/strategy/fleets/test_ship_instance_roundtrip.py --testmon` (new)

- [ ] Write failing round-trip test:
  - Construct `ShipInstance` with specific component HP (e.g. one component at 50% HP)
  - Call `instance.to_ship(pos, team_id, registries)` → `Ship`
  - Assert the specific component on the `Ship` has the expected `current_hp`
  - Call the inverse — `ShipInstance.update_from_ship(ship)` (or equivalent) — assert `ShipInstance.components` reflects final HP
- [ ] Implement: `ShipInstance.to_ship` applies `self.components[key].current_hp` to each component on the constructed `Ship` (after normal construction + before `recalculate_stats`)
- [ ] Implement: `ShipInstance.update_from_ship(ship)` walks the `Ship`'s layers/components and writes `current_hp` back into `self.components` by (component_id, instance_index) key
- [ ] Verify: a ship damaged to 50% HP in a battle updates back to 50% HP on its `ShipInstance`

**Notes:** Review existing `FleetBattleAdapter.update_from_battle_results` and `ShipInstance.update_from_ship` — some of this plumbing may exist; avoid duplication.

---

### Task 2.3: Strategy compiler populates `ShipSpec.components` [Simple]
**File:** `game/strategy/combat/spec_compiler.py`

**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py --testmon`

- [ ] Write failing test:
  - Build a fleet with one damaged ship (one component at 30% HP)
  - Compile to `BattleSpec`
  - Assert `BattleSpec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0].components` contains the expected `ComponentStateSpec` with `current_hp` matching the damage
- [ ] Update `build_strategy_battle_spec` — for each ship, walk `instance.components` and emit a tuple of `ComponentStateSpec` entries. Replace Phase 1's empty-tuple placeholder.
- [ ] Verify: compiled spec carries damage accurately

**Notes:**

---

### Task 2.4: `run_battle` honors per-component HP from spec [Medium]
**Files:**
- `game/simulation/battle_runner.py`
- `game/simulation/battle_outcome.py` (possibly extend `extract_outcome` helper)
- `game/simulation/entities/ship.py` (add `Ship.from_spec` factory if useful)

**Tests:** `pytest tests/unit/simulation/test_battle_runner_component_hp.py --testmon`

- [ ] Write failing tests:
  - Hand-build a `BattleSpec` with a ship whose components carry non-default HP
  - Call `run_battle(spec, ...)`
  - Assert the first `ShipOutcome.components` has `current_hp` reflecting the in-battle damage (which started from the spec's non-default HP)
  - Assert a ship whose spec had full HP emerges with same-or-lower HP (never exceeds spec HP)
- [ ] Update `run_battle` ship construction: apply `ShipSpec.components` HP to each constructed `Ship`'s components after instantiation (reuse or extend the logic from Task 2.2's `to_ship`)
- [ ] Update `extract_outcome` to walk each ship's layers → components → emit `ComponentStateSpec(component_id, instance_index, current_hp, is_active)` for every component (destroyed components reported with `current_hp=0`)
- [ ] Verify: tests pass

**Notes:**

---

### Task 2.5: Implement strategy `PostBattleHook` [Complex]
**Files:**
- `game/strategy/combat/spec_compiler.py` (extend — the hook is built here, closing over fleets)
- `game/strategy/combat/post_battle_hook.py` (new — `apply_outcome_to_fleets` helper)

**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py --testmon`

- [ ] Write failing tests:
  - Build fleets, compile a spec, run a trivial battle, apply hook
  - Assert surviving ships' `ShipInstance.components` reflects outcome HP
  - Assert destroyed ships are removed from their `Squadron.ships` list
  - Assert retreated ships are marked appropriately (status flag on `ShipInstance`? Or removed from fleet entirely? **DECISION NEEDED BEFORE IMPLEMENTING** — see Notes)
  - Assert empty squadrons are pruned from `TaskForce.squadrons`
  - Assert empty task forces are pruned from `Fleet.task_forces`
  - Assert empty fleets are removed from `Empire.fleets`
- [ ] Implement `apply_outcome_to_fleets(outcome, fleets_by_team_id, empires)` in `post_battle_hook.py`:
  - For each `TeamOutcome`, for each `ShipOutcome`:
    - Find matching `ShipInstance` by `instance_id`
    - If `status == SURVIVED` or `DERELICT`: `ship_instance.update_from_outcome(ship_outcome)` (new method that applies component HP + status)
    - If `status == DESTROYED`: remove from parent squadron
    - If `status == RETREATED`: (resolution per Notes decision)
  - Prune empty squadrons/task_forces/fleets
- [ ] Extend `build_strategy_battle_spec` to return a `BattleSpec` whose `post_battle_hook` closes over the fleets dict and calls `apply_outcome_to_fleets`
- [ ] Verify: all tests pass
- [ ] Verify: `run_battle` calls the hook after `extract_outcome` and before returning

**Notes:** **OPEN DECISION** — retreated ships: remove from fleet (they disperse to nearest friendly hex, handled by ConflictResolutionEngine), OR mark on ShipInstance as retreated and let the strategy layer decide next turn? Needs user input or design note before Task 2.5 is completable. The simplest MVP: remove from the current fleet; ConflictResolutionEngine creates a "scattered remnant" fleet at an adjacent hex. Defer the scattering logic to a follow-up if too invasive.

---

### Task 2.6: End-to-end regression — damage persists across battles [Medium]
**File:** `tests/integration/strategy/combat/test_damage_persistence.py` (new)

**Tests:** `pytest tests/integration/strategy/combat/test_damage_persistence.py --testmon`

- [ ] Write failing integration test:
  - Create two fleets, each with one ship
  - Run a battle that ends in a draw (both survive damaged)
  - Verify `ShipInstance.components` on the survivors shows non-full HP
  - Build a second spec from the same fleets
  - Verify the second spec's `ShipSpec.components` reflects the damage from battle 1
  - Run battle 2
  - Verify second outcome shows damage accumulating (or ship destroyed if damage exceeded threshold)
- [ ] Run: test fails before Phase 2 implementation
- [ ] After Tasks 2.1–2.5: test passes

**Notes:** This is the acceptance test for the phase. If it fails, something in 2.1–2.5 is wrong.

---

### Task 2.7: Documentation updates [Simple]
**Files:**
- `docs/systems/combat_simulation.md`
- `docs/systems/strategy_layer.md`

- [ ] Add section to `combat_simulation.md`: "Component HP Persistence" — describes `ShipSpec.components` carrying HP into battle, `ShipOutcome.components` carrying HP out, and the `PostBattleHook` that writes back to `ShipInstance`
- [ ] Update `strategy_layer.md` — note the new `ShipInstance.components: Dict[str, ComponentState]` field and its role in combat damage continuity
- [ ] Verify: doc renders without broken links; no stale claims about "ships repair fully between battles"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` fully green
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing (baseline maintained)
- [ ] End-to-end test in Task 2.6 passes
- [ ] Manual verification: start a strategy game, engage a battle with damage on both sides, end turn, engage a second battle with the same fleets — damaged ships remain damaged
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 Task 3.1
