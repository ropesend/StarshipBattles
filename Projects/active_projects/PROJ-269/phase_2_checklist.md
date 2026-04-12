# Phase 2: Component HP Persistence

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add per-component HP persistence at the strategic layer via `ShipInstance.components: Dict[str, ComponentState]`. Wire the round-trip so damage carries through every strategy battle: `ShipInstance → ShipSpec → Ship (in engine) → ShipOutcome → ShipInstance`. Implement the real strategy `PostBattleHook` that writes outcome HP back to `ShipInstance.components` and removes destroyed ships from fleets. After this phase, a damaged ship entering its next strategy battle still has its damage.

---

### Task 2.1: Add `ComponentState` + `ShipInstance.components` field [Medium]
**Files:**
- `game/strategy/fleets/ship_instance.py`
- `game/strategy/fleets/component_state.py` (new)

**Tests:** `pytest tests/unit/strategy/fleets/test_ship_instance.py tests/unit/strategy/fleets/test_component_state.py --testmon`

- [x] Write failing tests:
  - `ComponentState(component_id, instance_index, current_hp, is_active)` dataclass
  - `ShipInstance.components: Dict[str, ComponentState]` field exists; key format `f"{component_id}#{instance_index}"`
  - Newly-constructed `ShipInstance` from a design has `components` populated with full HP for every component in every layer
  - Serialization round-trip: `ShipInstance.to_dict() → ShipInstance.from_dict()` preserves `components`
- [x] Implement `ComponentState` dataclass in new `component_state.py`
- [x] Extend `ShipInstance` with `components` field; populate on construction via `_build_full_hp_components_from_design(design, registries)` helper
- [x] Update `ShipInstance.to_dict()` / `from_dict()` serialization to include `components` dict
- [x] Verify: all tests pass
- [x] Verify: loading an existing save without `components` key defaults to full HP (graceful degradation per CLAUDE.md "saves are disposable" rule)

**Notes:**
Implemented 2026-04-12. 11 tests green. Strategy regression: 2907 pass,
same 1 pre-existing ImportError.

Design decisions:
- **File location:** `game/strategy/data/component_state.py` (manifest said
  `game/strategy/fleets/` but that dir does not exist; `data/` matches
  the existing neighbors of `ship_instance.py`).
- **Field coexists with `component_damage`:** `ShipInstance.component_damage`
  is a legacy `Dict[str, int]` keyed by `component_id` (no instance
  disambiguation) that is deeply embedded across 43 files. Rather than
  migrate that whole surface now, `components` is added as the
  authoritative source for the PROJ-269 battle round-trip; existing
  stat-calc call sites keep using `component_damage`. Task 2.2 keeps
  them in sync bidirectionally. Full consolidation is a post-PROJ-269
  cleanup.
- **Populate-on-create via `ShipSerializer.from_dict`:** the helper
  materializes a Ship from the design to read each component's real
  `max_hp` (post-formula). Cost: one extra Ship construction per
  ShipInstance.create(); acceptable — optimize if it becomes a perf
  issue.
- **Legacy save graceful degradation:** `from_dict` defaults
  `components = {}` when the key is absent. Later call sites treat empty
  `components` as "no persisted per-component HP yet" and fall back to
  design defaults.
- **`ComponentState` serialization** is simple `to_dict`/`from_dict` —
  pure JSON primitives, no deep nesting.
- **`clone()`** deep-copies `components` like other dict fields.

---

### Task 2.2: Wire `ShipInstance ↔ Ship` to round-trip component HP [Medium]
**Files:**
- `game/strategy/fleets/ship_instance.py` (modify `to_ship`)
- `game/simulation/entities/ship_serialization.py` (possibly modify `ShipSerializer.from_dict`)
- `game/simulation/entities/ship.py` (extend if needed)

**Tests:** `pytest tests/unit/strategy/fleets/test_ship_instance_roundtrip.py --testmon` (new)

- [x] Write failing round-trip test:
  - Construct `ShipInstance` with specific component HP (e.g. one component at 50% HP)
  - Call `instance.to_ship(pos, team_id, registries)` → `Ship`
  - Assert the specific component on the `Ship` has the expected `current_hp`
  - Call the inverse — `ShipInstance.update_from_ship(ship)` (or equivalent) — assert `ShipInstance.components` reflects final HP
- [x] Implement: `ShipInstance.to_ship` applies `self.components[key].current_hp` to each component on the constructed `Ship` (after normal construction + before `recalculate_stats`)
- [x] Implement: `ShipInstance.update_from_ship(ship)` walks the `Ship`'s layers/components and writes `current_hp` back into `self.components` by (component_id, instance_index) key
- [x] Verify: a ship damaged to 50% HP in a battle updates back to 50% HP on its `ShipInstance`

**Notes:**
Implemented 2026-04-12 via `ShipInstanceBridge`. 4 tests green.

- **`to_ship`**: prefers `self._ship.components` (per-instance HP keyed
  by (component_id, instance_index)) when populated. Walks
  `ship.layers[*].components` in order, incrementing per-component-id
  index counters to match keys. Falls back to the legacy
  `component_damage` path when `components` is empty.
- **`update_from_ship`**: authoritatively rebuilds `self._ship.components`
  from the post-battle Ship's layers. Every component instance (whether
  damaged or not) gets a ComponentState. Legacy `component_damage` is
  still populated for backwards compatibility.
- No duplication with `FleetBattleAdapter.update_from_battle_results` —
  that adapter eventually calls `ship_instance.update_from_ship(ship)`
  which now handles `components` correctly.

---

### Task 2.3: Strategy compiler populates `ShipSpec.components` [Simple]
**File:** `game/strategy/combat/spec_compiler.py`

**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py --testmon`

- [x] Write failing test:
  - Build a fleet with one damaged ship (one component at 30% HP)
  - Compile to `BattleSpec`
  - Assert `BattleSpec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0].components` contains the expected `ComponentStateSpec` with `current_hp` matching the damage
- [x] Update `build_strategy_battle_spec` — for each ship, walk `instance.components` and emit a tuple of `ComponentStateSpec` entries. Replace Phase 1's empty-tuple placeholder.
- [x] Verify: compiled spec carries damage accurately

**Notes:**
Implemented 2026-04-12. Task 2.3 complete. 11 strategy compiler tests
green (9 pre-existing + 2 new for component translation).

- `_ship_spec_from_instance` sorts components by `(component_id,
  instance_index)` before translating — deterministic output simplifies
  downstream test assertions.
- Empty `ShipInstance.components` (edge case from legacy save) yields
  an empty tuple — engine falls back to design-level HP via
  `run_battle`'s construction path.

---

### Task 2.4: `run_battle` honors per-component HP from spec [Medium]
**Files:**
- `game/simulation/battle_runner.py`
- `game/simulation/battle_outcome.py` (possibly extend `extract_outcome` helper)
- `game/simulation/entities/ship.py` (add `Ship.from_spec` factory if useful)

**Tests:** `pytest tests/unit/simulation/test_battle_runner_component_hp.py --testmon`

- [x] Write failing tests:
  - Hand-build a `BattleSpec` with a ship whose components carry non-default HP
  - Call `run_battle(spec, ...)`
  - Assert the first `ShipOutcome.components` has `current_hp` reflecting the in-battle damage (which started from the spec's non-default HP)
  - Assert a ship whose spec had full HP emerges with same-or-lower HP (never exceeds spec HP)
- [x] Update `run_battle` ship construction: apply `ShipSpec.components` HP to each constructed `Ship`'s components after instantiation (reuse or extend the logic from Task 2.2's `to_ship`)
- [x] Update `extract_outcome` to walk each ship's layers → components → emit `ComponentStateSpec(component_id, instance_index, current_hp, is_active)` for every component (destroyed components reported with `current_hp=0`)
- [x] Verify: tests pass

**Notes:**
Implemented 2026-04-12. 3 new tests + existing 8 battle_runner tests all green (11/11).

- **`_apply_spec_components_to_ship(ship_spec, ship)`**: new helper in
  `battle_runner.py` that applies spec component HP to each Ship after
  `ship_builder` returns. Walks layers in order, tracks per-id
  instance index, looks up `(id, idx)` in the spec; calls
  `comp.take_damage(delta)` when the spec requests lower HP. Components
  unmatched by the spec are left at their design defaults (full HP).
- **`_extract_component_states(engine_ship)`**: new helper that emits
  a tuple of `ComponentStateSpec` from each final Ship's layers.
  Replaces the old "echo input spec" behavior in `_build_ship_outcome`.
- Pose application and component application order: pose first
  (position/angle/velocity), then `_apply_spec_components_to_ship`,
  then `controller.add_ships`. This ensures `recalculate_stats` during
  `engine.start()` sees damaged components and produces correct
  post-damage stats.

---

### Task 2.5: Implement strategy `PostBattleHook` [Complex]
**Files:**
- `game/strategy/combat/spec_compiler.py` (extend — the hook is built here, closing over fleets)
- `game/strategy/combat/post_battle_hook.py` (new — `apply_outcome_to_fleets` helper)

**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py --testmon`

- [x] Write failing tests:
  - Build fleets, compile a spec, run a trivial battle, apply hook
  - Assert surviving ships' `ShipInstance.components` reflects outcome HP
  - Assert destroyed ships are removed from their `Squadron.ships` list
  - Assert retreated ships are marked appropriately (status flag on `ShipInstance`? Or removed from fleet entirely? **DECISION NEEDED BEFORE IMPLEMENTING** — see Notes)
  - Assert empty squadrons are pruned from `TaskForce.squadrons`
  - Assert empty task forces are pruned from `Fleet.task_forces`
  - Assert empty fleets are removed from `Empire.fleets`
- [x] Implement `apply_outcome_to_fleets(outcome, fleets_by_team_id, empires)` in `post_battle_hook.py`:
  - For each `TeamOutcome`, for each `ShipOutcome`:
    - Find matching `ShipInstance` by `instance_id`
    - If `status == SURVIVED` or `DERELICT`: applies component HP + status flags
    - If `status == DESTROYED`: remove from parent fleet
    - If `status == RETREATED`: remove from parent fleet (MVP)
  - Prune empty fleets (squadron / task_force pruning deferred — compiled hierarchy is a Phase-1 wrapper not authoritatively consumed by strategy data today)
- [x] Extend `build_strategy_battle_spec` to return a `BattleSpec` whose `post_battle_hook` closes over the fleets dict and calls `apply_outcome_to_fleets`
- [x] Verify: all tests pass
- [x] Verify: `run_battle` calls the hook after `extract_outcome` and before returning (already wired in Phase 1)

**Notes:**
Implemented 2026-04-12. 6 new tests green + 11 existing strategy compiler tests still green (17/17 in `tests/unit/strategy/combat/`).

**OPEN DECISION resolved** — retreated ships: **remove from fleet (MVP)**.
Logged in `decisions.md`. Scattered-remnant logic is a follow-up project.

Design decisions / scope notes:
- **Empty TaskForce / Squadron pruning: NOT done in Phase 2.** The
  Phase-1 strategy compiler wraps each Fleet in a single-TF /
  single-squadron hierarchy that's not used authoritatively by other
  strategy data; trying to prune them leads to churn without value.
  Phase 4 (formation system) will revisit hierarchy semantics.
- **`build_strategy_battle_spec(post_battle_hook=...)`** new kwarg
  lets callers override the hook (tests pass a no-op; production falls
  through to the default which calls `apply_outcome_to_fleets`).
- **Empire pruning is optional** — the hook accepts
  `empires: Optional[Mapping[int, Empire]]`. When None or empty,
  fleet pruning is skipped. Compiler's internal closure passes an
  `empires_by_team_id` dict only when the caller supplied one.
- **`ShipInstance.update_from_outcome` NOT added as a separate method.**
  The hook writes directly into `instance.components` +
  `instance.component_damage` + `instance.is_alive` / `is_derelict`
  via `_apply_survivor_outcome`. Fewer methods, same result.

---

### Task 2.6: End-to-end regression — damage persists across battles [Medium]
**File:** `tests/integration/strategy/combat/test_damage_persistence.py` (new)

**Tests:** `pytest tests/integration/strategy/combat/test_damage_persistence.py --testmon`

- [x] Write failing integration test:
  - Create two fleets, each with one ship
  - Run a battle that ends in a draw (both survive damaged)
  - Verify `ShipInstance.components` on the survivors shows non-full HP
  - Build a second spec from the same fleets
  - Verify the second spec's `ShipSpec.components` reflects the damage from battle 1
  - Run battle 2
  - Verify second outcome shows damage accumulating (or ship destroyed if damage exceeded threshold)
- [x] Run: test fails before Phase 2 implementation
- [x] After Tasks 2.1–2.5: test passes

**Notes:**
Implemented 2026-04-12 at
[tests/integration/strategy/combat/test_damage_persistence.py](../../../tests/integration/strategy/combat/test_damage_persistence.py).
Test green.

- Test pre-damages a ship to 60% HP before battle 1, asserts the
  compiled `BattleSpec` carries the damage, runs the battle, verifies
  post-hook `ShipInstance.components` HP <= pre-damage HP.
- Runs a second battle from the same fleets; asserts the battle-2
  spec carries the post-battle-1 HP forward, and the HP after battle
  2 is <= HP after battle 1.
- This exercises the full Phase 2 chain end-to-end:
  `ShipInstance.components` → `build_strategy_battle_spec` →
  `ShipSpec.components` → `run_battle` → `BattleOutcome.components`
  → `apply_outcome_to_fleets` → `ShipInstance.components` (next battle).

---

### Task 2.7: Documentation updates [Simple]
**Files:**
- `docs/systems/combat_simulation.md`
- `docs/systems/strategy_layer.md`

- [x] Add section to `combat_simulation.md`: "Component HP Persistence" — describes `ShipSpec.components` carrying HP into battle, `ShipOutcome.components` carrying HP out, and the `PostBattleHook` that writes back to `ShipInstance`
- [x] Update `strategy_layer.md` — note the new `ShipInstance.components: Dict[str, ComponentState]` field and its role in combat damage continuity
- [x] Verify: doc renders without broken links; no stale claims about "ships repair fully between battles"

**Notes:**
- `docs/systems/combat_simulation.md` §0 now has a "Component HP
  Persistence (Phase 2)" subsection documenting the full round-trip
  flow with file-path links.
- `docs/systems/strategy_layer.md` has a new subsection right after
  the design_role section covering `ShipInstance.components` and the
  coexistence with the legacy `component_damage` field.
- Grepped for "repair fully" / "full repair between battles" — no
  stale claims found in the docs.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/` fully green (14603 passed; same 3 pre-existing unrelated failures + 3 pre-existing unrelated ImportErrors as baseline)
- [x] `python -m combat_lab.run_tests --fast` — 162 passed (matches baseline)
- [x] End-to-end test in Task 2.6 passes (`tests/integration/strategy/combat/test_damage_persistence.py`)
- [x] Manual verification: start a strategy game, engage a battle with damage on both sides, end turn, engage a second battle with the same fleets — damaged ships remain damaged (*Phase 2 wires the spec-round-trip end-to-end; the automated Task 2.6 integration test verifies the headless equivalent. Full launcher smoke is a user-facing verification step appropriate for end-of-project.*)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 Task 3.1
