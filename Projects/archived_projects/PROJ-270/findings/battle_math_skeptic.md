# Strategic Modifier Battle-Math — Skeptical Audit

## Verdict

**Track A is BROKEN end-to-end. It works at the compiler level and terminates at `FleetAuraManager._team_bonuses` — a dead-end dict that is never read for `shield_capacity_mult` or `damage_mult`. The user-visible gameplay regression from PROJ-269 Phase 5.5 is NOT fixed. The "live and functioning" claim in Task 6.5 notes is false.**

Direct reproduction (ran locally):

```
team_bonuses: {0: {'shield_capacity_mult': 0.5}}
external:     [ExternalModifier(ability_name='shield_capacity_mult', value=0.5, ...)]
ship.max_shields: 1000          <- should be 500 if Track A worked
ship.fleet_attack_bonus: 0.0
```

Storm entry was translated into an `ExternalModifier`, aggregated into `_team_bonuses[0]['shield_capacity_mult'] = 0.5`, then **silently ignored** because nothing downstream consumes it.

## Pipeline Trace (the authoritative evidence)

1. `game/strategy/combat/spec_compiler.py:357-379` — `_entries_from_environmental_effects` emits `ModifierEntry(effect.stat_key="shield_capacity_mult", value=0.5)`. CORRECT.
2. `game/strategy/combat/spec_compiler.py:382-432` — `_entries_from_fleet_combat_modifiers` emits `stat_key="shield_capacity_mult"` / `"damage_mult"`. CORRECT.
3. `run_battle` passes `spec.modifier_stack` to `FleetAuraManager.initialize(ships, modifier_stack=stack)`.
4. `game/simulation/combat/fleet_aura_manager.py:111-140` — `_append_external_from_entry` builds `ExternalModifier(ability_name="shield_capacity_mult", value=0.5)` and appends to `self._external`. CORRECT.
5. `game/simulation/combat/fleet_aura_manager.py:299-309` — `_recalculate` folds externals into `self._team_bonuses[team_id][ability_name]`. CORRECT so far.
6. **DEAD END** — `game/simulation/combat/fleet_aura_manager.py:313-322` `_apply_bonuses`:
   ```python
   ship.fleet_attack_bonus = team.get('ToHitAttackModifier', 0.0)
   ship.fleet_defense_bonus = team.get('ToHitDefenseModifier', 0.0)
   ```
   Only `ToHitAttackModifier` / `ToHitDefenseModifier` keys are read. Every other `ability_name` in `_team_bonuses` is dropped on the floor.
7. `game/engine/collision.py:115-120` — only consumers are `fleet_attack_bonus` / `fleet_defense_bonus` (full-codebase grep).
8. `game/simulation/components/abilities/defense.py:43-46` — `ShieldProjection.recalculate()` reads `self.get_effective_stat('shield_capacity_mult', 1.0)` from `component.stats`.
9. `component.stats` is populated in `game/simulation/components/component_stats_calculator.py:317-321` exclusively from `component.modifiers` (the on-component AppliedModifier list). **Nothing syncs `_team_bonuses` into `component.stats`.** There is no bridge.

Same trace for `damage_mult` via `WeaponAbility.recalculate()` → `self.get_effective_stat('damage_mult', 1.0)` → `component.stats` (never touched by the aura manager).

## Findings

### Finding 1: `_apply_bonuses` is a hardcoded two-key sink
**Severity:** Critical
**Location:** `game/simulation/combat/fleet_aura_manager.py:313-322`
**What's wrong:** `_apply_bonuses` reads only `ToHitAttackModifier` and `ToHitDefenseModifier` from `_team_bonuses`. All other aggregated abilities (`shield_capacity_mult`, `damage_mult`, `shield_mult`, etc.) are accumulated and then discarded. Storm and fleet multipliers reach step 5 of the pipeline, then drop to the floor.
**Evidence:** Repro above. Grep confirms no other reader of `_team_bonuses`.
**Recommended fix:** Either (a) write a real bridge that pushes team-wide stat_key multipliers into each alive ship's `component.stats` (or into an ability-stats layer that `get_effective_stat` checks), and trigger `ship.recalculate_stats()` on change; or (b) add per-entry component-modifier synthesis — the engine synthesizes a synthetic `AppliedModifier` onto each alive ship's components so the existing modifier pipeline picks it up. Requires invalidating recalculation on death/retreat/regeneration so `_recalculate` propagates.

### Finding 2: Storm/fleet multiplier unit tests only assert compiler output, not pipeline effect
**Severity:** High
**Location:** `tests/unit/strategy/adapters/test_simulation_adapter_storms.py:73-107`
**What's wrong:** `test_resolve_battle_emits_storm_modifier_on_spec` asserts `stat_key == "shield_capacity_mult"` and `value == 0.5` on the compiled `ModifierStack`. It patches `run_battle` to a no-op fake. No assertion on ship state, ship max_shields, or hull damage. "Test passes" proves only that step 1 works.
**Evidence:** The test body uses `patch("...simulation_adapter.run_battle", side_effect=_fake_run_battle)`.
**Recommended fix:** Add a real integration test (the one Task 6.5 deferred) that runs a real ship through `FleetAuraManager.initialize` with a storm modifier_stack and asserts `ship.max_shields` actually halved.

### Finding 3: `TestNoPlaceholderStatKeyInStrategyCompiler` is a source-file grep
**Severity:** High
**Location:** `tests/unit/simulation/test_unified_entry_guard.py:258-307`
**What's wrong:** The "guard" does `path.read_text()` and regex-greps for the literal string `stat_key="placeholder"` inside two compiler functions. It proves the compiler source doesn't contain a forbidden string. It proves nothing about whether the modifier reaches ship stats.
**Recommended fix:** Keep the grep as cheap guardrail, but add a behavioral test that compiles a real spec, runs `run_battle` (or at least `FleetAuraManager.initialize`) with it, and asserts ship stats changed.

### Finding 4: `test_fleet_aura_extended.py` integration tests only exercise the `ToHitAttackModifier` sink
**Severity:** High
**Location:** `tests/unit/simulation/combat/test_fleet_aura_extended.py:222-244`
**What's wrong:** `test_team_modifiers_applied` asserts `ship.fleet_attack_bonus == 3.0` — i.e. it hits the hardcoded reader at line 318. It does not exercise `shield_capacity_mult` or `damage_mult` sinks because there are none. Naming these tests "Extended External Modifier" creates the illusion of broader coverage than they provide.
**Recommended fix:** Add tests for each stat_key claimed to work end-to-end: given `modifier_stack` with `shield_capacity_mult=0.5` for team 0, after `initialize`, assert that team-0 ship's max_shields recomputed to half. Those tests would currently fail.

### Finding 5: Task 6.3 (Battle Setup complex toggles) is not implemented
**Severity:** High
**Location:** `game/ui/screens/battle_setup/spec_compiler.py:265-293`, phase_6_checklist.md lines 58-73
**What's wrong:** Battle Setup still emits `stat_key="placeholder"` for every complex toggle. The promised "Battle Setup 2v2 with shield booster toggled → shields visibly higher" manual smoke is impossible because (a) the toggle emits a placeholder, and (b) even if it emitted the real stat_key, Finding 1 would consume it silently. Checklist Task 6.3 shows only unchecked `- [ ]` items but the Phase 6 status reads "Complete".
**Recommended fix:** Only mark Phase 6 "Complete" after Finding 1 is addressed AND Task 6.3 is actually implemented. Currently the status is misleading.

### Finding 6: Task 6.5 "deferral" reasoning is inverted
**Severity:** High
**Location:** `Projects/active_projects/PROJ-270/phase_6_checklist.md:90-101`
**What's wrong:** Task 6.5 notes claim "Track A battle math itself IS live and functioning — PROJ-270 Phase 6.1/6.2 unit tests + `test_fleet_aura_extended.py` integration tests guarantee correctness." This is verifiably false (see repro). The deferral isn't "ergonomic scope grouping"; it is hiding that an end-to-end integration test could not be written because the feature doesn't work. If the integration test had been attempted, it would have failed immediately and surfaced Finding 1.
**Recommended fix:** Revise the deferral note to state accurately that Track A is not yet end-to-end. Create PROJ-271 Phase 4's integration test as a failing test today, to act as the acceptance gate for the real fix (Finding 1).

### Finding 7: `_log_placeholder_once` logging is not test-covered
**Severity:** Medium
**Location:** `game/simulation/combat/fleet_aura_manager.py:142-159`
**What's wrong:** No test asserts the WARNING is emitted once per source. It may work, but "claimed" != "tested". The checklist (Task 6.4) reads "6.4 COMPLETE" but there is no test capturing the logging behavior.
**Recommended fix:** Add `caplog`-based pytest covering the warn-once-per-source semantic.

### Finding 8: Combat Lab green proves nothing about Track A
**Severity:** Medium (documentation/process issue)
**Location:** Phase 6 Tasks 6.1/6.2 completion claims
**What's wrong:** "Combat Lab fast — 162/162 green" is cited as evidence for Task 6.1 / 6.2 correctness. Combat Lab scenarios pass a `modifier_stack=ModifierStack.empty()` (or none). None exercise storm shield interference or fleet shield/damage multipliers. Combat Lab green is a necessary regression gate (no unrelated breakage) but zero signal on the feature under review. Treating it as evidence of correctness is misleading.
**Recommended fix:** Stop citing Combat Lab as evidence for Track A correctness. Add explicit Combat Lab scenarios that drive a modifier_stack with storm / shield_mult / damage_mult entries and validate per-layer damage changes.

### Finding 9: Spirit of PROJ-269 "ships enter engine unmutated" vs. concrete fix requires mutation
**Severity:** Medium (architectural)
**Location:** PROJ-269 `decisions.md` row "Modifiers live in a single `ModifierStack`"
**What's wrong:** The PROJ-269 architectural decision says "Ships are NOT pre-mutated with modifier effects." Yet the only existing path for `shield_capacity_mult` to reach `ShieldProjection` is `component.stats` — which is populated from `component.modifiers` (a per-component list). To honor the spirit, the fix in Finding 1 should introduce an "ambient stats" layer the ability system reads in addition to `component.stats` (so the source of truth remains the `ModifierStack`, not a mutation on the ship). The obvious shortcut — synthesize an `AppliedModifier` on the fly and inject into `component.modifiers` — would violate the "no pre-mutation" principle.
**Recommended fix:** Extend `Ability.get_effective_stat` (or add a parallel layer) to check a `ship.external_stats: Dict[str, float]` dict that `FleetAuraManager._apply_bonuses` populates. That keeps the ModifierStack as the single source and avoids per-tick mutation of `component.modifiers`.

## Summary

The Track A implementation is a three-quarters-built bridge. The compiler emits the right entries, the manager ingests them, the aggregator sums them — and then the terminal sink is a hardcoded two-key dict read that only exposes `ToHitAttackModifier` and `ToHitDefenseModifier`. The regression from PROJ-269 Phase 5.5 is NOT actually closed. The tests that "prove" closure are either source-greps or shim tests that hit the same hardcoded sinks that worked pre-PROJ-269 for a different ability. The explicit end-to-end integration test was deferred with a rationale that, on inspection, contradicts the observable behavior.

Report path: `c:/Dev/Starship Battles/.agent_reports/proj-269-270-skeptic-review/battle_math_skeptic.md`
