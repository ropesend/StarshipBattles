# Phase 6: Strategic-Modifier Battle-Math Restoration (Bounded)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** MED-HIGH (battle behavior changes)
**Depends On:** Phase 1
**Objective:** Re-enable the strategic modifiers that pre-PROJ-269 affected battle math but post-PROJ-269 silently skip (placeholder stat_key decision). Scope is **bounded**: only 1:1 multiplier mappings to existing stat_keys (storm `shield_capacity_mult`, fleet `shield_mult` → `shield_capacity_mult`, fleet `damage_mult` → `damage_mult`). `flat_shield_bonus` (needs new additive stat_key binding) and suppressor effects (need opponent-team routing) are **deferred to PROJ-271 if Phase 6 exceeds 3 implementation days** (see decisions.md Decision 1).

---

## Tasks

### Task 6.0: Scope trim decision [Simple — decision-driven]
**File:** `decisions.md` (append)
**Tests:** None — decision-only task

**BEFORE WRITING ANY CODE**, time-box this decision:

- [ ] Read the audit findings in [design.md](design.md) §Initial-Analysis Finding 7 + the battle-math audit agent's report (preserved in [findings/](findings/) if captured, else in the original [PROJ-270 initiation prompt])
- [ ] Read [game/simulation/components/abilities/stat_keys.py](../../../game/simulation/components/abilities/stat_keys.py) — confirm current `StatKey` enum includes `damage_mult`, `shield_capacity_mult` (required for Task 6.1/6.2)
- [ ] Decide: **Track A (included in Phase 6)** multipliers only; **Track B (deferred to PROJ-271)** flat-bonus + suppressors. Document decision in [decisions.md](decisions.md) with timestamp
- [ ] If Track B is included: expand this checklist with Tasks 6.7 (flat-bonus), 6.8 (suppressors). If deferred: create `Projects/active_projects/PROJ-271/` (planning-only, not implementation) with the deferred scope pre-populated

**Notes:** Decision locked here becomes load-bearing for downstream phase estimation.

---

### Task 6.1: Storm `shield_capacity_mult` — real stat_key [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler_battle_math.py --tb=short` (new)

- [ ] Write failing test in [tests/unit/strategy/combat/test_spec_compiler_battle_math.py](../../../tests/unit/strategy/combat/test_spec_compiler_battle_math.py):
  - Given: a `StrategicBattleContext` with `environmental_effects.shield_capacity_mult = 0.5` (storm hex)
  - When: `build_strategy_battle_spec(...)` compiles a spec → `run_battle(spec, ...)` runs a 1-tick battle
  - Then: `outcome.teams[i].ships[j].components[...].current_hp` shows reduced max_shields (the storm effect applied)
  - Compare against a control run without storm — should see different shield values in the outcome
- [ ] Run test — confirm it fails (current placeholder emission does nothing)
- [ ] Locate the storm placeholder emission in [game/strategy/combat/spec_compiler.py](../../../game/strategy/combat/spec_compiler.py) (grep for `_entries_from_environmental_effects` — around lines 357–377 per audit)
- [ ] Change `stat_key="placeholder"` → `stat_key=StatKey.SHIELD_CAPACITY_MULT.value` (or the string `"shield_capacity_mult"` per existing convention)
- [ ] Change `value=0.0` → `value=effects.shield_capacity_mult` (propagate the real multiplier)
- [ ] Run test — confirm it passes
- [ ] Run `pytest tests/unit/strategy/ --testmon` — baseline maintained
- [ ] Run `python -m combat_lab.run_tests --fast --no-history` — 162/162 green (Combat Lab scenarios don't use storms; no regression expected)

**Notes:** [Filled during implementation]

---

### Task 6.2: Fleet `shield_mult` + `damage_mult` — real stat_keys [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler_battle_math.py --tb=short`

- [ ] Extend the Task 6.1 test file with two more failing tests:
  - Fleet with `FleetCombatModifiers.shield_mult = 2.0` → outcome shows increased effective shields
  - Fleet with `FleetCombatModifiers.damage_mult = 2.0` → outcome shows increased damage dealt
- [ ] Run tests — confirm they fail
- [ ] Locate the fleet-modifier placeholder emission in `_entries_from_fleet_combat_modifiers` (strategy compiler, around lines 380–417 per audit)
- [ ] Map `shield_mult` → `stat_key="shield_capacity_mult"`, value = `mods.shield_mult`
- [ ] Map `damage_mult` → `stat_key="damage_mult"`, value = `mods.damage_mult`
- [ ] Leave `flat_shield_bonus` as placeholder IF Task 6.0 chose Track A (deferred); otherwise Task 6.7 handles it
- [ ] Run tests — confirm they pass
- [ ] Verify via `FleetAuraManager` logging that the entries are picked up and applied via `ExternalModifier`
- [ ] Run full strategy unit suite — baseline maintained
- [ ] Run Combat Lab — 162/162 green

**Notes:** [Filled during implementation]

---

### Task 6.3: Battle Setup complex toggles — best-effort mapping [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py --tb=short`

- [ ] Audit complex design JSONs (e.g. `data/designs/qs_system_shield_booster_complex.json`) — each complex contains components with ability definitions (e.g. `ShieldModifier { multiplier: 1.25 }`)
- [ ] For each live toggle handled by the compiler (shield booster, damage booster, shield suppressor, damage suppressor, plus any others): determine whether a 1:1 stat_key mapping exists given the component ability
- [ ] Known mappings:
  - `shield_booster_complex` → `stat_key="shield_capacity_mult"`, value from the ability's `multiplier` field
  - `damage_booster_complex` → `stat_key="damage_mult"`, value from ability
  - Suppressors: DEFERRED to PROJ-271 (need opponent-team routing)
- [ ] Write failing tests per mappable toggle — spec contains right stat_key/value
- [ ] Implement: either hardcode the mappings (simpler) or add a lightweight mapping table in code (e.g., Python dict), NOT a new JSON file (content authoring bridge is out of scope — see Scope section of plan.md)
- [ ] Run tests — pass
- [ ] Manual smoke (end of Phase 6): Battle Setup 2v2 with shield booster toggled → shields visibly higher in battle

**Notes:** [Filled during implementation — record which complexes were mappable vs deferred]

---

### Task 6.4: Stop silent-skipping in `FleetAuraManager` [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager.py --tb=short`

- [ ] Write failing test asserting `_append_external_from_entry` logs a warning (at WARNING level via `logging`) when given an entry whose `stat_key` is not in the registered `AbilityStatBinding` map (e.g., `stat_key="placeholder"` or any unknown key)
- [ ] Run test — confirm it fails (current code silently returns)
- [ ] Modify [game/simulation/combat/fleet_aura_manager.py](../../../game/simulation/combat/fleet_aura_manager.py) `_append_external_from_entry`:
  - Keep the early-return for `stat_key == "placeholder"` BUT emit a WARNING log once (use a `functools.lru_cache`d helper keyed by `(stat_key, source)` to avoid log spam on repeated emissions)
  - For unknown stat_keys (anything not "placeholder" and not in `StatKey` enum), emit WARNING as well
- [ ] **Sub-task 6.4a** (deferred from Phase 1.4): delete the legacy `if config:` branch in `FleetAuraManager.initialize` at [game/simulation/combat/fleet_aura_manager.py:90-107](../../../game/simulation/combat/fleet_aura_manager.py#L90-L107). The branch reads `config.team_modifiers` / `config.global_modifiers` which are fields that were **deleted from `BattleConfig` by PROJ-269 Phase 6** — the branch is dead in production. Migrating requires rewriting 5 tests:
  - [tests/unit/simulation/combat/test_fleet_aura_extended.py](../../../tests/unit/simulation/combat/test_fleet_aura_extended.py) `test_includes_external_modifiers`, `test_includes_global_modifiers`, `test_team_modifiers_applied`, `test_global_modifiers_applied_to_all_teams`, `test_no_config_no_externals`
  - [tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py](../../../tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py) `mgr.initialize([ship], config=config, modifier_stack=stack)` call
  - Rewrite each to drive via `modifier_stack=ModifierStack(...)` with real `ModifierEntry` entries instead of a mock config
  - Remove the `config` parameter from `initialize` entirely (only `modifier_stack` remains)
- [ ] Run test — passes
- [ ] Verify that the warning fires during a strategy battle with storm effects (manual smoke)
- [ ] Verify no new warnings in the Combat Lab run (scenarios don't emit placeholders today)

**Notes:** This task prevents the Phase 5.5 regression from repeating: future compiler authors who add a new modifier source will immediately see the warning in logs and know they need a stat_key mapping. Sub-task 6.4a is a System Migration Policy cleanup — the legacy config-based loader is dead in production and its comment `"(legacy path)"` was flagged by PROJ-270 Phase 1.4 audit.

---

### Task 6.5: End-to-end battle-math integration test [Medium]
**File:** `tests/integration/strategy/combat/test_storm_shield_interference.py` (new)
**Tests:** `pytest tests/integration/strategy/combat/test_storm_shield_interference.py --tb=short`

- [ ] Write integration test (real ships, real battles, NOT mocks) asserting:
  - Ship in storm hex (shield_capacity_mult 0.5) takes more hull damage than the same ship in a non-storm hex, all else equal
  - Fleet with shield_mult 2.0 survives a battle that the same fleet without the modifier would lose
  - Fleet with damage_mult 2.0 destroys enemies faster
- [ ] Run test — confirm it passes after Tasks 6.1 + 6.2
- [ ] This test plus `test_damage_persistence.py` forms the end-to-end coverage for strategic modifiers

**Notes:** [Filled during implementation]

---

### Task 6.6: Phase 6 regression gate [Simple]
**Tests:** Full suites + manual smoke

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline (no unexpected regressions from modifier changes)
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Tasks 6.1, 6.2, 6.3, 6.4, 6.5 tests all green
- [ ] Grep audit: strategy compiler no longer emits `stat_key="placeholder"` for storm, shield_mult, damage_mult (only for deferred flat-bonus/suppressor if Track A was chosen)
- [ ] Manual smoke: Battle Setup 2v2 with shield booster — effect visible in battle

**Notes:** [Filled during implementation]

---

### Task 6.7: (CONDITIONAL) Flat shield bonus via new `SHIELD_BONUS_ADD` stat_key [Complex]
**Condition:** Only if Task 6.0 chose Track B (full scope in PROJ-270).
**File:** `game/simulation/components/abilities/stat_keys.py`, `game/strategy/combat/spec_compiler.py`

- [ ] Add `SHIELD_BONUS_ADD` to `StatKey` enum with `operation=ADD`, `target_attribute="max_shields"`, `base_attribute="base_max_shields"`
- [ ] Add `AbilityStatBinding` for the new stat_key
- [ ] Map `FleetCombatModifiers.flat_shield_bonus` → `stat_key="shield_bonus_add"` in strategy compiler
- [ ] Failing test → implementation → passing test
- [ ] Note shield-bonus-add is ADDITIVE (not multiplicative) — ensure `FleetAuraManager` pipeline handles the distinction correctly (check existing `accuracy_add` binding for precedent)

**Notes:** [Filled if Track B chosen; else mark N/A]

---

### Task 6.8: (CONDITIONAL) Suppressor effects via opponent-team routing [Complex]
**Condition:** Only if Task 6.0 chose Track B.
**File:** `game/strategy/combat/spec_compiler.py`, `combat_modifier_collector.py`

- [ ] Extend compiler: when collecting modifiers from opponent planets, emit entries targeted at the opponent's `team_id` in `ModifierStack.per_team[opponent_id]`
- [ ] Verify `FleetAuraManager` correctly applies per-team entries to the right team's ships (existing tests in `tests/unit/simulation/combat/` should cover this; add if missing)
- [ ] Failing test → implementation → passing test

**Notes:** [Filled if Track B chosen; else mark N/A]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked (Tasks 6.7 + 6.8 marked N/A if Track A chosen)
- [ ] Tests for Tasks 6.1, 6.2, 6.3, 6.4, 6.5 passing
- [ ] Regression gate (Task 6.6) passed including manual smoke
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State
- [ ] If Track A was chosen: verify PROJ-271 planning package was created for the deferred scope
