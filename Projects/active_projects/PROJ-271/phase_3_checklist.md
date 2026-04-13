# Phase 3: Scope-driven team routing for boosters/suppressors

> **SCOPE REVISED 2026-04-13:** User clarified there is no separate
> "suppressor architecture" — a suppressor is just a `*_mult < 1.0`
> combined with `enemy_*` scope; a booster is `*_mult > 1.0` combined
> with `player_*/allied_*/fleet/system` scope. Compilers must interpret
> `ability.scope` at compile time and route `enemy_*` to
> `per_team[opponent_id]`. See [decisions.md](decisions.md) 2026-04-13
> entries.

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** MEDIUM (scope interpretation + cross-team routing in Battle Setup compiler; strategy path already works)
**Depends On:** Phases 1 + 2 (both Task 2.4 scope-aware implementation + SHIELD_BONUS_ADD plumbing)
**Objective:** Both spec compilers interpret `ability.scope` to route modifier entries to the correct team. `enemy_*` → opponent team; everything else → owner team. Works identically for multiplicative and additive modifiers. Strategy compiler path is already scope-correct via `CombatModifierCollector`; Battle Setup compiler needs scope-aware routing added by Phase 2.4.

---

## Tasks

### Task 3.1: Strategy compiler scope-routing verification [Medium]
**File:** `tests/unit/strategy/combat/test_spec_compiler.py` (or new file)
**Tests:** Targeted pytest run

Strategy path notes: `CombatModifierCollector.collect_combat_modifiers(fleet, opponent_fleet, ...)` at `game/strategy/services/combat_modifier_collector.py:108-127` already walks `opponent_empire`'s facilities, filters to `enemy_*`-scoped abilities, and aggregates them into the RECEIVER fleet's `FleetCombatModifiers`. So by the time the strategy compiler sees the modifiers, routing is already resolved: fleet N's modifiers go into `per_team[N]`. No compiler changes needed — just a test locking this behavior.

- [x] Write test: collector sees opponent empire's `enemy_sector` `DamageModifier` → `FleetCombatModifiers.damage_mult` on RECEIVER. Added `test_strategy_compiler_routes_enemy_suppressor_to_receiver_team` to `TestStrategyCompilerBehavioralStatKeys`.
- [x] Verify: friendly fleet with the same sector has NO `damage_mult=0.8` entry — already covered by `test_enemy_shield_suppressor_applies_to_fleet` in `test_combat_modifier_collector.py:156-179`.
- [x] Run — passes.

**Notes:** Strategy compiler doesn't do scope routing itself — the `CombatModifierCollector` pre-computes enemy-scoped abilities into the RECEIVER fleet's `FleetCombatModifiers` BEFORE the compiler sees anything. So the compiler just emits per_team[receiver_id]. The collector-level test (existing) + the compiler-level test (new) together lock the whole chain.

---

### Task 3.2: Battle Setup compiler scope-routing implementation [Complex]
**File:** `game/ui/screens/battle_setup/spec_compiler.py` (`_complex_entries` from Phase 2.4)
**Tests:** `pytest tests/unit/ui/battle_setup/ --tb=short`

Completes the Phase 2.4 scope-routing hook. Phase 2.4 did the ability→stat_key map; Phase 3.2 does the scope→team routing.

- [x] Implemented scope routing helper `_route_team_for_scope(scope_str, owner_team)` in `game/ui/screens/battle_setup/spec_compiler.py`. Uses `_OPPONENT_SCOPES = {"enemy_sector", "enemy_system"}` set for clarity; everything else routes to owner. For 3+ team battles a follow-up extension is needed (current impl assumes 2 teams; logged via `_NUM_TEAMS = 2` constant).
- [x] Failing test written (Phase 2.4): `test_compiler_damage_suppressor_routes_to_opponent_team`, `test_compiler_shield_suppressor_routes_to_opponent_team`, `test_shield_suppressor_routes_to_opponent` (in guard file).
- [x] Failing test written (Phase 2.4): `test_compiler_shield_projector_complex_emits_shield_bonus_add` — shield projector routes to owner team.
- [x] Implemented as part of Phase 2.4 — routing baked into `_complex_to_entries`.
- [x] Run — 16/16 battle_setup tests + 22/22 guard tests pass.

**Notes:** Phase 2.4 and Phase 3.2 landed together since scope interpretation + ability→stat_key mapping are tightly coupled — routing is "per ability emission". Separating them would have required two passes over the same data.

---

### Task 3.3: `FleetAuraManager` per-team application end-to-end [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py` (extend)
**Tests:** Targeted pytest run

- [x] Added `test_shield_bonus_add_per_team_does_not_bleed_to_other_teams` — per_team[0] `shield_bonus_add=100.0` does not appear on team 1's external_stats.
- [x] Added `test_mixed_add_and_mult_per_team_isolation` — per_team[0] additive + per_team[1] multiplicative stay isolated, with NEITHER stat_key appearing on the wrong team.
- [x] Original multiplicative per-team test (`test_per_team_attack_modifier_applies_only_to_target_team`) already in place from PROJ-270 Phase 5.5.

**Notes:** FleetAuraManager per-team isolation works correctly for both additive and multiplicative stat_keys. 35/35 tests green in guard + fleet_aura test files.

---

### Task 3.4: Scope-routing regression guard [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [x] Behavioral tests in Phase 2.4/2.5 already cover this: `test_compiler_shield_suppressor_routes_to_opponent_team`, `test_compiler_damage_suppressor_routes_to_opponent_team`, `test_shield_suppressor_routes_to_opponent` (in guard file).
- [x] No additional grep-based guard needed — the behavioral tests exercise the code path and would fail if routing regressed.

**Notes:** Phase 2.5's `TestBattleSetupCompilerBehavioralStatKeys` doubles as Phase 3.4's scope-routing guard.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Strategy compiler verified scope-correct (no code change needed — collector handles it pre-compile)
- [x] Battle Setup compiler correctly routes `enemy_*` scopes to opponent team
- [x] Additive stats (shield_bonus_add) AND multiplicative stats (damage_mult, shield_capacity_mult) both route correctly
- [x] Scope-routing guard test green
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
