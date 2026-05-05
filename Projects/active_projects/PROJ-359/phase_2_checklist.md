# Phase 2: AttackRequest / AttackResolution + Registry Skeleton

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-359 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** game/simulation/combat/attack_contract.py, game/simulation/combat/weapon_registry.py, tests/unit/simulation/combat/test_weapon_registry.py
**Objective:** Introduce the typed contract and registry behind the existing dispatch. Production behavior unchanged. Phase 1 golden tests must remain green.

---

## Tasks

### Task 2.1: Audit dict-carrier consumers [Simple]
**File:** Read-only audit
**Tests:** None

- [ ] Grep for `attack['type']`, `attack.get('source')`, `attack['damage']`, etc. across `game/simulation/` and `game/engine/`
- [ ] List every consumer of the dict-shaped attack carrier in [decisions.md](decisions.md)
- [ ] Each consumer becomes either: a typed-contract caller (Phase 3) or a deletion (Phase 4)

**Notes:**

---

### Task 2.2: Define `AttackRequest` / `AttackResolution` [Medium]
**File:** `game/simulation/combat/attack_contract.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_registry.py -v` (after 2.4)

- [ ] `AttackRequest` dataclass: source ship, weapon component, weapon ability, target, aim_pos, aim_vec, family
- [ ] `AttackResolution` union or dataclass: capture all current outputs (BeamHit, ProjectileLaunched, MissileLaunched) so any handler returns a typed object
- [ ] `WeaponFamily` enum or string literal type: `BEAM`, `PROJECTILE`, `SEEKER`, `PDC`
- [ ] `WeaponHandler` protocol: `fire(request: AttackRequest) -> AttackResolution`
- [ ] Document the contract at top of file (mirrors `ability_stat_registry.py` doc style)

**Notes:**

---

### Task 2.3: Build `WeaponRegistry` [Medium]
**File:** `game/simulation/combat/weapon_registry.py` (new)
**Tests:** Same module

- [ ] `WEAPON_REGISTRY: Dict[WeaponFamily, WeaponHandler]` (mirror `ABILITY_STAT_REGISTRY` shape)
- [ ] `register(family, handler)` (or decorator)
- [ ] `dispatch(request: AttackRequest) -> AttackResolution`
- [ ] Family-detection helper: given a `Component`, return the `WeaponFamily` (uses `has_ability` / tags — single point that owns the legacy lookup until Phase 4)
- [ ] An unregistered family raises a domain-specific error (don't fall back silently)

**Notes:**

---

### Task 2.4: Registry contract test with fake family [Medium]
**File:** `tests/unit/simulation/combat/test_weapon_registry.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_registry.py -v`

- [ ] Define `TestWeaponFamily` handler in the test
- [ ] Register it; build an `AttackRequest`; assert `dispatch` routes to the handler and returns the handler's `AttackResolution`
- [ ] Test: unregistered family raises
- [ ] Test: family-detection helper resolves a known component to the right `WeaponFamily`

**Notes:**

---

### Task 2.5: Phase 1 golden tests still pass [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_weapon_dispatch_golden.py -v`

- [ ] All 4 golden tests pass unchanged — no production code in firing/targeting/collision/projectile is touched in this phase

**Notes:**

---

### Task 2.6: Sharded sweep [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes
- [ ] Pass count matches Phase 1 baseline + new registry tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
