# Phase 1: Critical (None-guards + GameSession ignores)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-463 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the CRITICAL domain findings verified by audit `2026-05-19_223900_type-audit` — the seeker None-guard and the 10 GameSession `# type: ignore[no-untyped-def]` properties (the single highest-impact type-loss site).

---

## Tasks

### Task 1.1: Add seeker ability None-guard [Simple]
**File:** `game/simulation/combat/families/seeker.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/simulation/combat/families/seeker.py`

- [ ] Add a None guard for `seeker_ab` (line 38, from `comp.get_ability('SeekerWeaponAbility')`) before the attribute accesses at lines 52, 68-76 (`.projectile_speed`, `.projectile_damage`, `.endurance`, `.turn_rate`, `.projectile_hp`, `.to_hit_defense`)
- [ ] Verify: pytest passes; `mypy game/simulation/combat/families/seeker.py` shows no new errors

### Task 1.2: Annotate GameSession mutator/service properties [Low effort, high impact]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/ --testmon` and `mypy game/strategy/engine/game_session.py`

- [ ] Replace `# type: ignore[no-untyped-def]` with `-> EventBus` on `_event_bus` (line 202)
- [ ] Add `-> IFleetMutator` to `fleet_mutator` (line 217) and `_fleet_mutator` (line 227)
- [ ] Add `-> IPlanetMutator` to `planet_mutator` (line 231) and `_planet_mutator` (line 236)
- [ ] Add `-> IEmpireMutator` to `empire_mutator` (line 240) and `_empire_mutator` (line 245)
- [ ] Add `-> IShipInstanceMutator` to `ship_mutator` (line 249) and `_ship_mutator` (line 254)
- [ ] Add `-> CommandRegistry` to `_command_registry` (line 258)
- [ ] Verify: pytest passes; `mypy game/strategy/engine/game_session.py` shows no new errors (expect ~30% of strategy errors to clear)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
