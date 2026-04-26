# PROJ-272 Round-2 Code Audit

Scope: look for what round-1 missed, and issues created by PROJ-271 Phases 6–12 fixes.
Working state: Phase 6–12 changes all present in `game/simulation/combat/fleet_aura_manager.py`, `game/simulation/entities/ship_stats.py`, `game/ui/screens/battle_screen.py`, `game/strategy/combat/spec_compiler.py`, plus the post-archive AI-controller TypeGuard.

## Executive summary

- Two correctness concerns around Phase 7's unified `team_ability_groups` path (key-name mismatch between provider/external, and falsy filter dropping legitimate 0.0 mults).
- One live AI crash risk that round-1 patched for the capability cache but left unpatched in `_score_and_sort_enemies` / `TargetEvaluator` when heterogeneous enemy lists include projectiles.
- `BattleScreen.start(team0, team1)` compat shim is dead-but-live AND silently bypasses `engine.modifier_stack`, so if a caller ever re-appears it will silently fail Track A/B auras.
- Missing test coverage for the most important new invariant: a ship-provider aura and an external `ModifierEntry` sharing a `stack_group` must compose MAX (locks Phase 7's behavioural claim).
- `external_stats` recompute check triggers a needless full stat recalc for every ship on first tick of every battle (`prev=None != {}`), a perf cliff for large battles.

## CRITICAL

None.

## HIGH

### H1. Phase 7 key-name mismatch: provider auras and external entries can't share a stack_group
**File:** `game/simulation/combat/fleet_aura_manager.py:295-323`

Providers key into `team_ability_groups[team_id][ability][group]` using
`provider.ability_name = type(ab).__name__` (e.g. `"ShieldProjection"`),
while externals key into the same structure using
`ext.ability_name = effect.stat_key` (e.g. `"shield_capacity_mult"`).
These are different top-level keys, so a ship-provider aura and an
external modifier cannot MAX even if they share a `stack_group` — they
always SUM via different ability buckets.

This is the whole point of Phase 7's stated semantic ("external entries
participate in the two-phase MAX/SUM alongside ship-provider auras"), but
the implementation only composes intra-external and intra-provider, not
cross-source. Docstring at line 305–311 implies full composition.

**Fix (PROJ-272):** decide the intended semantic. Either (a) normalise
both to the `stat_key` the ship actually consumes, or (b) document that
cross-source composition is by design a SUM (effectively rolling back
Phase 7's claim to cross-source behaviour). Add a test that locks the
chosen behaviour — see M3 below.

**Add to PROJ-272:** yes.

### H2. `_score_and_sort_enemies` passes missiles into `TargetEvaluator`; `least_armor` and `has_weapons` fallback paths still call ship-only methods
**File:** `game/ai/target_evaluator.py:177,189`; `game/ai/controller.py:249-264`

Phase 6-post fix guarded `_build_capabilities_cache` with `is_combat_ship`,
so missiles get no cache entry. But `_score_and_sort_enemies` still
evaluates every enemy (including missiles) against every rule. When a
rule's cache lookup misses:

- `_eval_has_weapons_rule` fallback (line 177) calls
  `candidate.get_components_by_ability('WeaponAbility', ...)`
- `_eval_least_armor_rule` (line 189) calls
  `candidate.get_components_by_layer(LayerType.ARMOR)`

Projectiles don't implement either. The outer `except (AttributeError,
TypeError)` at controller.py:260 swallows the crash, but the net effect
is that for policies with `least_armor` or `has_weapons` rules, every
missile is silently dropped from scoring — PDC-arc logic can't target
them unless `pdc_arc` comes first without short-circuit.

**Fix:** pre-filter projectiles out of the `enemies` list per rule-type
(missiles should only be evaluated against `pdc_arc` / `missiles_in_pdc_arc`),
or guard `_eval_least_armor_rule` / `_eval_has_weapons_rule` fallback
paths with a projectile type-check. The exception-swallow hides a real
correctness hole in target scoring.

**Add to PROJ-272:** yes.

### H3. `BattleScreen.start(team0, team1)` bypass doesn't wire `engine.modifier_stack`
**File:** `game/ui/screens/battle_screen.py:227-261`, `game/simulation/services/battle_service.py:207-218`

The legacy path `BattleScreen.start → controller.start → battle_service.start_battle → engine.start`
never sets `engine.modifier_stack`. Round-1 concluded this method has
zero production callers and zero test callers ("dead but live" per
`code_architecture_skeptic.md` H1). PROJ-270 Phase 10 explicitly
scope-trimmed deletion. **If any future caller re-appears, fleet auras
are silently ignored** — the exact class of "silent drift" PROJ-269
Phase 9 eradicated for `_entries_from_modifier_source`.

Worse, `BattleScreen._build_fallback_outcome` (two-layer shim) is also
still live with synthesized `seed=0` / hardcoded `end_reason`.

**Fix (PROJ-272):** delete `BattleScreen.start(team0, team1)`,
`_build_fallback_outcome`, and `_get_or_build_outcome`'s fallback
branch. Tests that use them should build a minimal `BattleSpec`. Prior
audits confirmed zero remaining callers — this is ready to delete.

**Add to PROJ-272:** yes.

## MEDIUM

### M1. `_apply_bonuses` filters `if v` — 0.0 mults silently dropped
**File:** `game/simulation/combat/fleet_aura_manager.py:328`

`self._team_bonuses[team_id] = {k: v for k, v in totals.items() if v}`
treats `0.0` as absent. For `_mult` stat keys this means a modifier
stack aggregating to `damage_mult=0.0` (e.g. a debuff that zeroes damage)
is dropped, so `get_effective_stat` returns default `1.0` — inverted
behaviour. Real production sources don't emit `0.0` mults today, but
the filter hides any future "zero the stat" effect. `_add` stat keys at
zero do want to be dropped — so a naive `if v != default` won't work.

**Fix:** filter only additive-default zeros (`_add` keys with value
`0.0`), keep everything else. Or drop the filter entirely and let
`get_effective_stat` see the zero explicitly.

**Add to PROJ-272:** yes.

### M2. `prev != new_external_stats` triggers `recalculate_stats` on every ship's first tick of every battle
**File:** `game/simulation/combat/fleet_aura_manager.py:365-373`

Initial ship state has `external_stats = {}` (set in `Ship.__init__`).
On the first `_apply_bonuses` call, `prev = {}` and `new = {}` or
`dict(team)`. Actually `prev` is the pre-existing `{}`, so `prev !=
new` only triggers when team bonuses are non-empty — that's the intended
path. **However**, `getattr(ship, 'external_stats', None)` returns `None`
for freshly constructed SimpleNamespace test ships (line 365), so the
guard is correct there but triggers `recalc` for any test ship that
doesn't initialise `external_stats`. Minor test-shim noise.

**Fix:** low-priority polish — short-circuit when both dicts are empty.

**Add to PROJ-272:** optional polish.

### M3. Missing coverage: provider + external entry sharing a stack_group
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

Phase 7 docstring promises "external entries participate in two-phase
MAX/SUM *alongside* ship-provider auras". Zero tests assert the
cross-source composition (a ship aura and an external entry in the same
`stack_group` with the same effective stat → MAX, not SUM). This is the
most important invariant Phase 7 introduced and it's unverified. Cf.
H1 which may show the claim is actually unimplemented.

**Fix:** add a test registering one provider (e.g. a storm-suppressor
ship with `ShieldProjection` scope="fleet") and one external entry
(`shield_capacity_mult`, same stack_group). Assert the composed team
bonus matches whichever semantic PROJ-272 locks.

**Add to PROJ-272:** yes, together with H1.

### M4. Vestigial `sector` / `system` / `empires` kwargs on `build_strategy_battle_spec`
**File:** `game/strategy/combat/spec_compiler.py:65-89,307-331`

`build_strategy_battle_spec` accepts `sector`, `system`, `empires` and
passes them to `_build_modifier_stack`, which discards them (`_ = sector`
etc.). Production adapter at `game/strategy/adapters/simulation_adapter.py:190-196`
doesn't pass them. The API surface is stale — future contributors will
assume passing a sector with `modifiers` does something, and it doesn't.

**Fix:** delete the three kwargs and the dead lines in `_build_modifier_stack`.
Update any test callers (grep shows a handful pass them explicitly).

**Add to PROJ-272:** yes (small, mechanical).

## LOW

### L1. `_placeholder_warned_sources` set attached via `hasattr` lazy init
**File:** `game/simulation/combat/fleet_aura_manager.py:160-164`

Using `hasattr` + attribute assignment for a set that could be declared
in `__init__`. Minor; the lazy pattern works but is harder to reason
about vs. initialising `self._placeholder_warned_sources: set = set()`
in `__init__`.

**Add to PROJ-272:** no (nit).

### L2. `get_active_modifier_labels` `.get('value', 0):.2f` will crash on True marker bonuses
**File:** `game/ui/screens/battle_screen.py:806`

If a marker ability (e.g. `CommandAndControl`) ever surfaces through
`get_active_bonuses`, `value=True` will flow to `f"{value:.2f}"` and
raise. Today marker abilities don't flow through `get_active_bonuses`,
but the format-string assumption is fragile.

**Fix:** coerce with `float(value) if isinstance(value, (int, float)) else 0.0`.

**Add to PROJ-272:** no (defensive polish).

### L3. `_NUM_TEAMS = 2` hardcodes Battle Setup to 2-team
**File:** `game/ui/screens/battle_setup/spec_compiler.py:92,446`

Landmine for 3+ team extension; the docstring acknowledges it. Not
broken today.

**Add to PROJ-272:** no (scope is 2-team).

## Audit areas checked and CLEAN

- **Phase 8 UI access chain** (`battle_screen.py:774-809`): fully
  guarded with `getattr`/`try`. Fails gracefully if controller, service,
  engine, or aura_manager is None. Good.
- **Phase 9 dangling references**: grep for `_entries_from_modifier_source`
  returns only archived doc hits. Fully deleted.
- **Phase 12 semantic fix**: `ship_stats.py:460-471` correctly mirrors
  `ShieldProjection.recalculate` (`defense.py:42-47`) using BOTH
  `capacity_mult` and `shield_capacity_mult`. Unit-locked in
  `test_ship_shield_bonus_add.py::test_flat_bonus_stacks_with_capacity_mult_too`.
- **external_stats save/load leak**: `test_ship_external_stats_serialization_guard.py`
  locks it out of `ShipSerializer.to_dict`. `BattleConfig` no longer has
  `team_modifiers`/`global_modifiers` fields so there's nothing to
  serialize. Clean.
- **Unified entry grep**: every production caller routes through
  `run_battle`, `start_engine_from_spec`, or
  `BattleController.start_from_spec` (all three share the same
  modifier_stack wiring). Only `BattleScreen.start(team0, team1)`
  bypasses — see H3.
- **AI controller `_build_capabilities_cache`**: correctly guards with
  `is_combat_ship`. The remaining exposure is downstream in the
  evaluator fallbacks (H2).
- **Phase 12 dead-code cleanup**: `_noop_hook`, `_NUM_TEAMS` wiring,
  unused imports — spot-checked, no breakage found. `_NUM_TEAMS` still
  used at line 446 (not orphaned).
- **Track A end-to-end**: `tests/integration/strategy/combat/test_storm_shield_interference.py`
  + `test_suppressor_effects.py` exist and drive real `run_battle` with
  storm and suppressor effects composing against ship shields. Pipeline
  is intact.
- **Track B end-to-end**: `test_flat_shield_bonus.py` drives real
  `run_battle` with `ModifierEntry(stat_key="shield_bonus_add")`.
  Pipeline intact.
- **Phase 7 stack_group unit tests**: same/different/None stack_group
  composition all covered for external-vs-external; missing only the
  provider-vs-external case (M3).

## Summary for PROJ-272 scope

Recommended PROJ-272 phases (ordered by risk):

1. **H1 + M3** — resolve Phase 7 cross-source composition: pick
   semantic, fix keying, add test.
2. **H2** — harden target evaluation against heterogeneous enemy lists.
3. **H3** — delete `BattleScreen.start(team0, team1)` and fallback
   outcome shim.
4. **M1** — fix `_apply_bonuses` zero-mult filter.
5. **M4** — strip vestigial sector/system/empires kwargs.

L1/L2/L3 are polish; skip unless bandwidth allows.
