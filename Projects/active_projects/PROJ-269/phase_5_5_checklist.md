# Phase 5.5: ModifierStack Engine Application

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-269 5_5` (if supported; else spot-check)
> 2. Only proceed if green
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Close the Phase-5 scope gap. The engine now **consumes** `BattleSpec.modifier_stack` at init and applies modifier effects via the existing `FleetAuraManager` pipeline. `HitLogRecorder` populates `HitRecord.modifiers_applied` with the active modifier set so DETAILED telemetry can explain where hit-shaping came from.

After this phase:
- `run_battle` threads `spec.modifier_stack` to `BattleEngine`.
- Engine's `FleetAuraManager.initialize(ships, config)` receives a translation of `ModifierStack` entries in the format it already understands (`{"ability", "value", "source"}` dicts).
- `SimulationBattleResolver`'s `_apply_shield_interference` / `_apply_strategic_modifiers` can be safely deleted in Phase 6 without losing functionality (the ModifierStack pipeline replaces them).
- `HitRecord.modifiers_applied` is populated at DETAILED telemetry with a snapshot of modifiers active on the attacker's team + globals.

---

### Task 5.5.1: Thread `ModifierStack` from spec → engine [Medium]
**Files:**
- `game/simulation/systems/battle_engine.py`
- `game/simulation/battle_runner.py`

**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_modifier_stack.py --testmon`

- [ ] Write failing tests:
  - `BattleEngine` accepts an optional `modifier_stack` kwarg at construction (default None)
  - `engine.modifier_stack` is accessible as a field
  - When `run_battle(spec)` runs with `spec.modifier_stack` populated, the engine's `modifier_stack` field matches
- [ ] Implement `BattleEngine.__init__(modifier_stack=None)` — stored as `self.modifier_stack`
- [ ] Implement `run_battle` → `engine.modifier_stack = spec.modifier_stack`
- [ ] Verify: tests pass

**Notes:**

---

### Task 5.5.2: Apply `ModifierStack` via `FleetAuraManager` [Medium]
**File:** `game/simulation/combat/fleet_aura_manager.py`

**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py --testmon`

- [ ] Write failing tests:
  - A `ModifierStack` with a `ModifierEntry` whose effect `stat_key="ToHitAttackModifier"` for team 0 produces a non-zero `fleet_attack_bonus` on team-0 ships after `aura_manager.initialize(ships, modifier_stack=stack)`
  - A `ModifierStack` with a global entry applies the bonus to every team
  - Placeholder effects (stat_key="placeholder") are silently ignored — no crash, no phantom bonus
- [ ] Extend `FleetAuraManager.initialize(ships, config=None, modifier_stack=None)`:
  - Keep existing `config.team_modifiers` / `config.global_modifiers` path (backwards compat)
  - When `modifier_stack` is provided, iterate `per_team` and `global_`; for each `ModifierEntry`, convert to `ExternalModifier(ability_name=effect.stat_key, value=effect.value, source_name=entry.source, team_id=...)` and append to `self._external`
  - Skip entries whose `stat_key == "placeholder"` (compilers emit these for Phase-1 unresolved modifier content)
- [ ] Update `BattleEngine.start` / `start_teams` to pass `engine.modifier_stack` to `aura_manager.initialize(...)`
- [ ] Verify: tests pass; existing BattleConfig-based modifier tests still work

**Notes:** Placeholder effect skipping is intentional — Phase 5's compiler MVP emits them as records of "a modifier was toggled here" without real effect evaluation. Later content work maps toggles to real effects; the plumbing in this task is ready for that.

---

### Task 5.5.3: Populate `HitRecord.modifiers_applied` at DETAILED [Medium]
**File:** `game/simulation/combat/telemetry.py`

**Tests:** `pytest tests/unit/simulation/combat/test_hit_log_modifier_trace.py --testmon`

- [ ] Write failing tests:
  - `HitLogRecorder(event_bus, modifier_stack=stack)` stores the stack
  - When a COMPONENT_HIT event fires with an attacker on team 0 and a non-empty per_team[0] entry in the stack, the resulting `HitRecord.modifiers_applied` contains a `ModifierApplication` matching the entry's source + effect value
  - Global entries show up regardless of attacker team
  - Entries for other teams do NOT appear
- [ ] Extend `HitLogRecorder.__init__(event_bus, tick_provider=None, modifier_stack=None)`
- [ ] On each hit event, compute `modifiers_applied` from:
  - `modifier_stack.global_` (always)
  - `modifier_stack.per_team[attacker_team_id]` (if attacker context known)
  - Filter out placeholders
- [ ] Wire `run_battle._attach_telemetry` to pass the spec's modifier_stack into `HitLogRecorder`
- [ ] Verify: tests pass

**Notes:** For Phase 5.5 MVP, `modifiers_applied` is the set of modifiers **active** at hit time, not the modifiers that specifically contributed to the damage value. Real contribution tracing requires thread-through-damage-pipeline plumbing that's out of scope. This MVP is still useful — a DETAILED hit log shows "with these modifiers in play" which is enough for forensic UI until someone demands per-hit contribution.

---

### Task 5.5.4: Documentation + phase wrap [Simple]
**Files:**
- `docs/systems/combat_simulation.md`
- `Projects/active_projects/PROJ-269/plan.md`
- `Projects/active_projects/PROJ-269/decisions.md`

- [ ] Update `combat_simulation.md` §0 — mark `modifier_stack` as fully wired (placeholder effects ignored; real effects flow through FleetAuraManager)
- [ ] Add a `decisions.md` entry documenting the "placeholder effects are silently ignored" decision + the "modifiers_applied = active-at-hit-time set" MVP choice
- [ ] Verify: regression pytest + combat_lab fast still green

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/` fully green (baseline maintained)
- [ ] `python -m combat_lab.run_tests --fast` — 162+ passing
- [ ] New tests for modifier-stack engine application + hit-log trace pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row (add Phase 5.5 row) and Current State to point to Phase 6 Task 6.1
