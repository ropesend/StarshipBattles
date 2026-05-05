# Phase 3: Migrate Weapon Families One at a Time

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-359 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** game/simulation/combat/families/{beam,projectile,seeker,pdc}.py, game/simulation/combat/weapon_firing_system.py, game/simulation/combat/targeting_system.py, game/engine/collision.py, game/simulation/projectile_manager.py
**Objective:** Move each weapon family behind the typed registry, one family per task. Each migration is an independent commit. Phase 1 golden tests guard each step.

---

## Tasks

### Task 3.1: Migrate Beam family [Medium]
**File:** `game/simulation/combat/families/beam.py` (new), `game/simulation/combat/weapon_firing_system.py:221`, `game/engine/collision.py:68`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_dispatch_golden.py::test_beam tests/unit/engine/test_collision.py -v`

- [ ] Implement `BeamHandler` in `families/beam.py` — produces an `AttackResolution` equivalent to the current beam dict
- [ ] Register Beam family in the registry on import
- [ ] In `_create_attack`: when family is Beam, call `WEAPON_REGISTRY.dispatch(request)` and adapt the resolution to whatever the engine expects (still dict-shaped for now if `collision.py` hasn't been migrated yet)
- [ ] OR migrate `collision.py:68` in this same task to consume the typed resolution — choose based on Phase 2 audit
- [ ] Beam golden test PASSES bit-for-bit
- [ ] Commit: `refactor(combat): migrate Beam weapon family to typed dispatch (PROJ-359 Task 3.1)`

**Notes:**

---

### Task 3.2: Migrate Projectile family [Medium]
**File:** `game/simulation/combat/families/projectile.py` (new), `game/simulation/combat/weapon_firing_system.py:289`, `game/simulation/projectile_manager.py:130`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_dispatch_golden.py::test_projectile -v`

- [ ] Implement `ProjectileHandler` — produces a `Projectile` instance via the typed contract
- [ ] Register; adapt the call site in `_create_attack`
- [ ] Projectile golden test PASSES bit-for-bit
- [ ] Commit: `refactor(combat): migrate Projectile weapon family to typed dispatch (PROJ-359 Task 3.2)`

**Notes:**

---

### Task 3.3: Migrate Seeker / Missile family [Medium]
**File:** `game/simulation/combat/families/seeker.py` (new), `game/simulation/combat/weapon_firing_system.py:245`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_dispatch_golden.py::test_seeker -v`

- [ ] Implement `SeekerHandler` — produces a seeker `Projectile` (turn_rate, max_speed, target, hp, to_hit_defense, endurance)
- [ ] Preserve the firing-arc check (currently in `_create_seeker_projectile`); decide whether it lives in the handler or stays in the firing system as a pre-dispatch guard
- [ ] Register; adapt
- [ ] Seeker golden test PASSES bit-for-bit
- [ ] Commit: `refactor(combat): migrate Seeker weapon family to typed dispatch (PROJ-359 Task 3.3)`

**Notes:**

---

### Task 3.4: Migrate PDC family + targeting metadata [Complex]
**File:** `game/simulation/combat/families/pdc.py` (new), `game/simulation/combat/targeting_system.py:123,166-172`, `game/simulation/combat/weapon_firing_system.py:184-188`
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_dispatch_golden.py::test_pdc tests/unit/ai/ -v`

- [ ] Implement `PDCHandler`; PDC's distinguishing semantics (target enemy missiles in arc, PDC-only targets) move into family metadata
- [ ] Update `targeting_system.py` to consume the family metadata for `is_pdc` checks — this also closes the loop with PROJ-356's capability cache fix
- [ ] Update `weapon_firing_system.py:184` (PDC missile-injection) to consult family metadata, not `comp.has_pdc_ability()` directly
- [ ] PDC golden test PASSES bit-for-bit
- [ ] AI tests for PDC targeting still PASS
- [ ] Commit: `refactor(combat): migrate PDC weapon family to typed dispatch (PROJ-359 Task 3.4)`

**Notes:** PROJ-356 must be merged first OR explicitly treat the controller fix as in-scope here. Coordinate with PROJ-356 status before starting this task.

---

### Task 3.5: Sharded green after each migration [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] After Task 3.1: sharded passes
- [ ] After Task 3.2: sharded passes
- [ ] After Task 3.3: sharded passes
- [ ] After Task 3.4: sharded passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
