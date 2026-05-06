# Phase 4: Delete String-Class Branches + Dict Carriers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-359 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):** game/simulation/combat/weapon_firing_system.py, game/simulation/combat/targeting_system.py, game/engine/collision.py, game/simulation/projectile_manager.py
**Objective:** Remove the legacy string-class dispatch branches and any remaining dict-carrier paths now that every family routes through the typed contract. Pure deletion.

---

## Tasks

### Task 4.1: Confirm zero remaining legacy callers [Simple]
**File:** Read-only audit
**Tests:** None

- [x] Grep `comp.has_ability('BeamWeaponAbility' | 'SeekerWeaponAbility' | 'ProjectileWeaponAbility')` across `game/`
- [x] Every match must be either: in a family handler (legitimate, kept) OR in a path slated for deletion (this phase)
- [x] Grep `attack['type']`, `attack.get('source')`, etc. — match against the Phase 2 audit; every consumer must be a typed-contract caller now
- [x] Record the inventory in [decisions.md](decisions.md)

**Notes:**

---

### Task 4.2: Delete legacy string branches in `_create_attack` [Medium]
**File:** `game/simulation/combat/weapon_firing_system.py:198-243`
**Tests:** `pytest tests/unit/simulation/combat/ -v`

- [x] Remove the if/else string branches that this phase's audit confirmed are unreachable
- [x] `_create_attack` becomes thin: build `AttackRequest` → `WEAPON_REGISTRY.dispatch` → return resolution
- [x] Phase 1 golden tests still PASS bit-for-bit

**Notes:**

---

### Task 4.3: Delete dict carriers from engine layer [Medium]
**File:** `game/engine/collision.py`, related projectile-hit paths
**Tests:** `pytest tests/unit/engine/ tests/unit/simulation/combat/ -v`

- [x] Replace any remaining dict-shaped attack inputs in `collision.py` with `AttackResolution`
- [x] Engine no longer reads simulation-layer ability semantics
- [x] All collision tests PASS

**Notes:**

---

### Task 4.4: Delete `_create_seeker_projectile` / `_create_standard_projectile` if dead [Simple]
**File:** `game/simulation/combat/weapon_firing_system.py:245-313`
**Tests:** Grep for callers

- [x] If callers all route through registry handlers now, delete these methods entirely
- [x] If they survive as helpers used by family handlers, document the boundary in [decisions.md](decisions.md) and leave them

**Notes:**

---

### Task 4.5: Telemetry shape audit [Simple]
**File:** `game/simulation/combat/telemetry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_*telemetry* -v` (or equivalent)

- [x] `HitLogRecorder._on_hit_event` consumes the typed resolution (or equivalent) — not the deleted dict shape
- [x] No regression in telemetry output

**Notes:**

---

### Task 4.6: Update docs [Simple]
**File:** `docs/systems/combat_simulation.md`, `docs/02_PATTERNS.md`
**Tests:** None

- [x] Document the weapon registry pattern in `docs/02_PATTERNS.md` (mirror the Ability-Stat Registry entry)
- [x] Update `combat_simulation.md` to describe `AttackRequest` / `AttackResolution` and family handlers as the extension point for new weapon families
- [x] Per AGENTS.md "Documentation First" — update docs in the same change as the behavior change

**Notes:**

---

### Task 4.7: Final sharded sweep [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite passes
- [x] Pass count >= Phase 1 baseline + all new tests across Phases 2-4
- [x] Document final count in [decisions.md](decisions.md)

**Notes:**

---

### Task 4.8: Demo: register a fake weapon family [Simple]
**File:** `tests/unit/simulation/combat/test_weapon_registry.py` (extend)
**Tests:** Same module

- [x] Acceptance test: a fake weapon family registers and fires WITHOUT editing `weapon_firing_system.py`, `targeting_system.py`, `collision.py`, or `projectile_manager.py`
- [x] This is the extensibility goal of the project — codify it as an executable test

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to closure / awaiting user verification
- [x] Update [manifest.md](manifest.md) with the final file set touched
