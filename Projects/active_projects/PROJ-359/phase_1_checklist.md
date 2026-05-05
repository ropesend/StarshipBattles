# Phase 1: Characterization (Golden) Tests for Current Dispatch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-359 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):** tests/unit/simulation/combat/test_weapon_dispatch_golden.py
**Objective:** Lock current Beam / Projectile / Seeker / PDC behavior with golden damage-event tests BEFORE any production change. Zero behavior change in this phase.

---

## Tasks

### Task 1.1: Inventory existing weapon tests [Simple]
**File:** Read-only audit
**Tests:** None (research)

- [ ] List existing tests under `tests/unit/simulation/combat/` and `tests/unit/engine/` that exercise weapon firing, targeting, projectile, or collision
- [ ] For each, note what observable contract it locks (event shape, damage value, side effects)
- [ ] Identify gaps where the new golden tests need to add coverage
- [ ] Record inventory in [decisions.md](decisions.md)

**Notes:**

---

### Task 1.2: Golden test — Beam family [Medium]
**File:** `tests/unit/simulation/combat/test_weapon_dispatch_golden.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_dispatch_golden.py::test_beam -v`

- [ ] Construct a deterministic battle: ship A (beam weapon, fixed seed) firing on ship B at fixed range
- [ ] Tick once; capture the emitted attack event(s) in their current dict-shape
- [ ] Snapshot: type, source, target, damage, range, origin, component, direction, hit
- [ ] Test passes on current main; this is the bit-for-bit baseline

**Notes:**

---

### Task 1.3: Golden test — Projectile family [Medium]
**File:** Same module
**Tests:** Same module

- [ ] Same shape as Task 1.2 with a `ProjectileWeaponAbility` weapon
- [ ] Capture the resulting `Projectile` object's fields (owner, position, velocity, damage, range_val, proj_type, source_weapon)
- [ ] Snapshot

**Notes:**

---

### Task 1.4: Golden test — Seeker / Missile family [Medium]
**File:** Same module
**Tests:** Same module

- [ ] Same shape with a `SeekerWeaponAbility` weapon
- [ ] Capture seeker-specific fields (turn_rate, max_speed, target, hp, to_hit_defense, endurance)
- [ ] Snapshot

**Notes:**

---

### Task 1.5: Golden test — PDC family [Medium]
**File:** Same module
**Tests:** Same module

- [ ] PDC weapon firing on an enemy missile (PDC's distinguishing scenario)
- [ ] Capture full chain: PDC firing event AND collision/hit application against the missile
- [ ] Snapshot

**Notes:**

---

### Task 1.6: Sharded green baseline [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes WITH the new golden tests included
- [ ] Record the test count and pass count in [decisions.md](decisions.md) — this is the post-Phase-1 baseline that Phases 2-4 must preserve

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Sharded baseline recorded
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
