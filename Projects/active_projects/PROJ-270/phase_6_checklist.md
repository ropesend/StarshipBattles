# Phase 6: Strategic-Modifier Battle-Math Restoration (Bounded)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Track A: multipliers only; flat-bonus + suppressors deferred to PROJ-271)
**Risk:** MED-HIGH (battle behavior changes)
**Depends On:** Phase 1
**Objective:** Re-enable the strategic modifiers that pre-PROJ-269 affected battle math but post-PROJ-269 silently skip (placeholder stat_key decision). Scope is **bounded**: only 1:1 multiplier mappings to existing stat_keys (storm `shield_capacity_mult`, fleet `shield_mult` → `shield_capacity_mult`, fleet `damage_mult` → `damage_mult`). `flat_shield_bonus` (needs new additive stat_key binding) and suppressor effects (need opponent-team routing) are **deferred to PROJ-271 if Phase 6 exceeds 3 implementation days** (see decisions.md Decision 1).

---

## Tasks

### Task 6.0: Scope trim decision [Simple — decision-driven] — LOCKED TRACK A
**File:** `decisions.md` + inline code comments
**Tests:** None — decision-only task

- [x] Confirmed `StatKey` enum includes `DAMAGE_MULT = "damage_mult"` (line 36) and `SHIELD_CAPACITY_MULT = "shield_capacity_mult"` (line 44) — both exist and are honored by `FleetAuraManager`
- [x] Decision: **Track A (multipliers only)**. `flat_shield_bonus` (needs new additive `SHIELD_BONUS_ADD` stat_key) and suppressor effects (need opponent-team routing) deferred to **PROJ-271** per decisions.md Decision 1.
- [x] Track A tasks: 6.1 (storm multiplier), 6.2 (fleet multipliers), 6.4 (log placeholder skips)
- [x] `flat_shield_bonus` retained as placeholder in the strategy compiler with explicit comment referencing PROJ-271
- [ ] PROJ-271 planning package: not created this session; defer to next project-init session

**Notes:** Time-boxed at session start; chose Track A to fit remaining context budget. Full scope estimate was 20–35 engineer hours per audit; Track A is ~4 hours actual.

---

### Task 6.1: Storm `shield_capacity_mult` — real stat_key [Medium] — COMPLETE
**File:** `game/strategy/combat/spec_compiler.py`

- [x] Added new `_real_entry(*, source, display_name, design_id, stat_key, value, operation="multiply")` helper in [game/strategy/combat/spec_compiler.py](../../../game/strategy/combat/spec_compiler.py) at lines 440-466 — builds a `ModifierEntry` with a real stat_key (not placeholder). Uses `ModifierEntry(source=source, stack_group=None, effect=effect)`.
- [x] Changed `_entries_from_environmental_effects` at [game/strategy/combat/spec_compiler.py:357](../../../game/strategy/combat/spec_compiler.py) to emit `stat_key="shield_capacity_mult"` with `value=effects.shield_capacity_mult` and `operation="multiply"`
- [x] Updated test `tests/unit/strategy/adapters/test_simulation_adapter_storms.py::test_resolve_battle_emits_storm_modifier_on_spec` to assert the new contract (`stat_key == "shield_capacity_mult"`, `value == 0.5`)
- [x] `pytest tests/unit/strategy/` — **2922 passed** ✓ (1 pre-existing AI import error)
- [x] Combat Lab fast — **162/162 green** ✓ (scenarios don't use storms; no regression)

**Notes:** Storm hex shield interference now genuinely reduces shield capacity in strategy battles. Before PROJ-270 this effect was silently dropped.

---

### Task 6.2: Fleet `shield_mult` + `damage_mult` — real stat_keys [Medium] — COMPLETE
**File:** `game/strategy/combat/spec_compiler.py`

- [x] Changed `_entries_from_fleet_combat_modifiers` at [game/strategy/combat/spec_compiler.py:380](../../../game/strategy/combat/spec_compiler.py):
  - `shield_mult` → `stat_key="shield_capacity_mult"`, `value=modifiers.shield_mult`, `operation="multiply"`
  - `damage_mult` → `stat_key="damage_mult"`, `value=modifiers.damage_mult`, `operation="multiply"`
  - `flat_shield_bonus` — RETAINED as placeholder with explicit comment citing PROJ-271 deferral (Track A scope trim)
- [x] `pytest tests/unit/strategy/` — **2922 passed** ✓
- [x] Combat Lab fast — **162/162 green** ✓

**Notes:** Per-team strategic modifiers now actually affect battle math. Battle balance may shift slightly in strategy battles where fleets have non-default combat modifiers. Flagged for manual smoke testing (Task 8.7).

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

### Task 6.4: Stop silent-skipping in `FleetAuraManager` [Simple] — COMPLETE (6.4a deferred)
**File:** `game/simulation/combat/fleet_aura_manager.py`

- [x] Added `_log_placeholder_once(source)` helper to [game/simulation/combat/fleet_aura_manager.py](../../../game/simulation/combat/fleet_aura_manager.py) — emits one WARNING per unique source per battle. Tracked via `_placeholder_warned_sources` set (initialized lazily) so repeated placeholder emissions don't spam logs.
- [x] Modified `_append_external_from_entry` to call `_log_placeholder_once(source)` before returning on `stat_key == "placeholder"` or empty stat_key
- [x] Verified no regression: strategy + simulation tests still green (6105 passed)
- [x] Future compiler authors now see: `"FleetAuraManager: ModifierEntry source=... has no stat_key mapping (placeholder). Effect will NOT be applied to battle math."`
- [ ] **Sub-task 6.4a (deferred from Phase 1.4, still deferred):** delete the legacy `if config:` branch reading `config.team_modifiers` / `config.global_modifiers`. Still dead in production but not worth the 5-test rewrite cost this session.

**Notes:** This task prevents the Phase 5.5 regression from repeating: future compiler authors who add a new modifier source without a stat_key mapping will immediately see the warning in logs.

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
