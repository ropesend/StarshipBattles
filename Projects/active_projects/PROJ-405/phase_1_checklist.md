# Phase 1: Thread EventBus through Projectile/Seeker construction

**Status:** Not Started
**Objective:** Make `SEEKER_EXPIRE` (and other projectile-lifecycle events) actually fire on the EventBus during normal production battle ticks, with a regression test that pins it.

---

## Tasks

### Task 1.1: Map the construction chain [Medium]
**File:** see manifest; also `rg -n "Projectile\(|Seeker\(" game/simulation/`

- [ ] Trace every place production code constructs a `Projectile` or `Seeker`. Most likely starting point: `WeaponFiringSystem` (or similar) inside `game/simulation/combat/`.
- [ ] Read `BattleState.__init__` and `BattleState.update` (or wherever the per-tick spawning happens) to find the EventBus reference. Confirm where the EventBus is attached on the `BattleState` (PROJ-252 made it session-scoped).
- [ ] Document the chain in `decisions.md` with file:line refs.

**Notes:**

### Task 1.2: TDD — write failing regression test [Medium]
**File:** `tests/unit/simulation/test_projectile_event_bus_wiring.py` (new) or extend an existing seeker/projectile test

- [ ] Construct a battle through the production-shape entry (use whatever fixture exists — probably `make_battle_state` or similar).
- [ ] Subscribe a test recorder to `SEEKER_EXPIRE` (and at least one other projectile event).
- [ ] Run a tick chain that causes a seeker to expire (out of fuel / max range).
- [ ] Assert the recorder observed at least one event.
- [ ] Run against unmodified production — confirm test fails (recorder is empty because the no-op default swallows events).

**Notes:**

### Task 1.3: Thread EventBus from `BattleState` through the spawn path [Medium]
**File:** `game/simulation/battle_state.py`, `game/simulation/combat/weapon_firing_system.py` (or equivalent)

- [ ] Add an `event_bus` (or `event_logger`) attribute to whichever spawner intermediates between `BattleState` and `Projectile/Seeker`.
- [ ] Pass it through every constructor on the chain.
- [ ] Update `Projectile.__init__` / `Seeker.__init__` to accept it as a required kwarg (or keep optional with the no-op default but wire production callers to always pass the real bus — choose per CLAUDE.md guidance: prefer required if the no-op default will hide future regressions).
- [ ] Run focused tests — they should pass; the new regression should pass.

**Notes:**

### Task 1.4: Search for any unmigrated production constructors [Simple]
**Tests:** `rg -n "Projectile\(|Seeker\(" game/`

- [ ] Confirm every production construction passes the EventBus.
- [ ] Test-only constructions (`tests/`, `simulation_tests/`, fixtures) may continue to pass mocks or no-ops — that's fine, but flag any test that's clearly meant to exercise production wiring.

**Notes:**

### Task 1.5: Run focused projectile + battle-state suites [Simple]
**Tests:** `pytest tests/unit/simulation/entities/test_projectile.py tests/unit/simulation/test_battle_state.py -v`

- [ ] Both pass.

**Notes:**

### Task 1.6: Closeout
- [ ] Update Phase 1 status to `Complete`
- [ ] Update plan.md Quick Status + Current State
- [ ] Update `Projects/projects_index.md` row for PROJ-405 to `Complete`
- [ ] Validators pass
- [ ] Commit `PROJ-405 phase 1: thread EventBus through Projectile/Seeker construction`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Status at top of this file is `Complete`
- [ ] plan.md updated
- [ ] Focused tests pass
- [ ] `python Projects/scripts/validate_phase.py PROJ-405 1` PASSED
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-405` PASSED
