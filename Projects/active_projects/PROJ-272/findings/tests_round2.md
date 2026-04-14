# PROJ-272 Round-2 Test Coverage Audit

Round-1 findings were addressed. Round-2 lens: what was still missed, what gaps Phases 6-12 introduced, what the "unified ModifierEntry path" left under-tested.

Codebase touched:
- `game/simulation/combat/fleet_aura_manager.py` (unified aggregation, lines 258-330)
- `game/strategy/combat/spec_compiler.py` (Phase 9 deletion, lines 307-345)
- `game/ai/target_evaluator.py` (lines 166-193)
- `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`
- `tests/unit/simulation/test_unified_entry_guard.py`
- `tests/unit/ai/test_ai_capabilities_cache.py`
- `tests/unit/ui/screens/test_battle_screen_modifier_labels.py`

---

## HIGH — Real gaps that could hide regressions

### H1. Phase 7 stack_group tests don't cover provider-aura × external-entry interaction

Location: `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py` lines 283-395.

The Phase 7 refactor (`_recalculate`, fleet_aura_manager.py:305-323) routes external `ModifierEntry` values **through the same `team_ability_groups` structure** as ship-provider `AuraProvider` values. Same `stack_group` → MAX, different → SUM. Both code paths converge in `_aggregate_ability_groups`.

The current tests cover external-vs-external MAX/SUM but **do not cover provider-vs-external in the same `stack_group`** — the exact cross-path the refactor enabled. A ship with a shield-booster component (ship provider, `stack_group="shield_boost"`, value=1.5) on team 0 plus a complex-sourced external entry (stack_group="shield_boost", value=1.25) on team 0 should MAX to 1.5. If `_scan_ship` populates provider values but the external ingestion re-uses the same group name and a future refactor changes the keying, this silently becomes SUM = 2.75 and no test catches it.

Concrete failing test to add (file: `test_fleet_aura_manager_modifier_stack.py`):

```
def test_ship_provider_and_external_entry_same_stack_group_max():
    # Build a minimal ship with a ShieldModifier-like ability instance
    # scope=FLEET, stack_group="shield_boost", value=1.5 → provider
    # Add external ModifierEntry stack_group="shield_boost", value=1.25
    # Assert external_stats["shield_capacity_mult"] == 1.5 (MAX, not 2.75)
```

Also missing: `ext.team_id is None` (global) **+** `per_team[0]` entry sharing a `stack_group`. Code paths at lines 314-317 decide target_teams independently per entry; aggregation happens per-team downstream. A global `stack_group="shield_boost"` value=1.4 + per_team[0] same group value=1.1 should yield team 0 MAX=1.4 (global wins) and team 1 = 1.4 (global alone). Never verified.

### H2. 3+ team routing: silent failure, not loudly failing

Phase 11 checklist note: "document the expected failure mode." Verification:

- `_build_modifier_stack` (`spec_compiler.py:307-345`) iterates `range(team_count)` — supports N teams.
- `FleetAuraManager._recalculate` (`fleet_aura_manager.py:264`) uses `{s.team_id for s in ships}` — supports N teams.
- `ext.team_id is None` branch at line 314 yields `target_teams = team_ids` — **silently applies to ALL teams including a hypothetical team 2**.

There is **no test** asserting what happens with 3 teams. Per-team entries for team 0 and team 1 leave team 2 with zero bonuses; global entries hit all three. That may be correct behavior, but nothing in the suite locks it. A future refactor that hardcodes `[0, 1]` anywhere in the aggregation path (tempting shortcut) would pass all current tests.

Recommended test (new file or additions to `test_fleet_aura_manager_modifier_stack.py`):

```
def test_three_team_per_team_isolation_and_global_fanout():
    # Ships on team 0, 1, 2.
    # per_team = {0: [mult=2.0], 1: [mult=3.0]}, global_ = [add=10]
    # Assert team 0 sees mult=2.0 and add=10
    # Assert team 1 sees mult=3.0 and add=10
    # Assert team 2 sees NO mult entries, but add=10
```

Also: does the strategy pipeline (`conflict_resolution_engine`) support 3+ teams? Probably not — but without a test we don't know if the engine silently truncates, crashes, or gives undefined behavior. This is a "PROJ-272 candidate: test + document fail-loud behavior."

### H3. External_stats not cleared between consecutive battles — no regression guard

User note: "ship carried over to next battle must start with `external_stats == {}`". The only similar test is `tests/integration/strategy/combat/test_damage_persistence.py` (runs two consecutive battles, focuses on HP persistence, **not on `external_stats` reset**).

Concrete risk: if battle 1 sets `ship.external_stats = {"shield_capacity_mult": 2.0}` and battle 2 has no modifiers, `_apply_bonuses` line 346-356 writes `new_external_stats = {}` on the next `_recalculate` IF the aura manager is re-initialized. But the reset relies on `FleetAuraManager.initialize()` being called — if the same manager instance is reused or `ship.external_stats` isn't cleared between battles before init, stale data survives.

Recommended test (file: `tests/integration/strategy/combat/test_external_stats_reset_between_battles.py`):

```
def test_second_battle_sees_clean_external_stats():
    # Run battle 1 with a modifier_stack that applies shield_capacity_mult=2.0 to team 0.
    # Run battle 2 with empty modifier_stack. Reuse the same ship.
    # Assert ship.external_stats == {} after battle 2 init.
    # Assert ship.max_shields equals base (not 2x).
```

### H4. External_stats on destroyed ship — behavior undocumented

`_apply_bonuses` at line 357-359 sets `fleet_attack_bonus = 0.0` and `fleet_defense_bonus = 0.0` on non-alive ships. **But** line 346 assigns `new_external_stats = {}` only inside the `if ship.is_alive:` branch — the `else` branch never assigns `new_external_stats`, so on line 366 `ship.external_stats = new_external_stats` writes `{}` (initialized outside the if). Behavior is correct by accident: the `new_external_stats = {}` default at line 347 is inside the loop, so every iteration starts fresh. This is correct but fragile — refactor risk.

Recommended test:

```
def test_destroyed_ship_external_stats_cleared():
    # Ship alive → receives external entry → external_stats["shield_capacity_mult"] == 1.5
    # Flip ship.is_alive = False → call mgr.update([ship])
    # Assert ship.external_stats == {}
    # Assert ship.fleet_attack_bonus == 0.0 and fleet_defense_bonus == 0.0
```

### H5. TargetEvaluator projectile-candidate crash paths untested

`target_evaluator.py:177` — `_eval_has_weapons_rule` fallback path (when no capabilities_cache supplied) calls `candidate.get_components_by_ability('WeaponAbility', operational_only=False)`. `Projectile` does not implement `get_components_by_ability`. Phase 6 fix in `_build_capabilities_cache` skips projectiles from the cache — so for projectile candidates, `candidate_id not in ship_capabilities_cache` → fallback path → **AttributeError on Projectile**.

Same at line 189 — `_eval_least_armor_rule`: `candidate.get_components_by_layer(LayerType.ARMOR)`. No cache path. Runs on every candidate unconditionally. A projectile candidate with a `least_armor` rule crashes.

The round-1 fix only hardened `_build_capabilities_cache`. The TargetEvaluator rules themselves still assume `candidate` is a ship. `tests/unit/ai/test_target_evaluator_edge_cases.py` has tests using mocks with `is_projectile()` semantics but it never tests a projectile-shaped candidate flowing into `has_weapons` or `least_armor` rules.

Concrete failing tests to add (file: `tests/unit/ai/test_target_evaluator_projectile_safety.py`):

```
def test_has_weapons_rule_with_projectile_candidate_without_cache():
    # Projectile-like candidate (no get_components_by_ability attr), no cache
    # Rule = [{'type': 'has_weapons', 'weight': 100}]
    # Must NOT raise AttributeError. Return (0, True) — projectiles have no weapons.

def test_least_armor_rule_with_projectile_candidate():
    # Same setup — no get_components_by_layer attr.
    # Rule = [{'type': 'least_armor', 'weight': 1}]
    # Must NOT raise. Return neutral score.
```

The fix requires a `is_combat_ship` TypeGuard in each rule evaluator, or TargetEvaluator should filter candidates up front. Either way, a test locks the contract.

---

## MEDIUM — Coverage gaps unlikely to regress silently but worth closing

### M1. Battle Screen modifier labels test misses mixed team/global case

`test_battle_screen_modifier_labels.py:53-90` verifies per-team distinct bonuses via `fake_get_active_bonuses`. But `FleetAuraManager.get_active_bonuses` (line 383-412) returns per-team bonuses **including global** (line 403: `if ext.team_id is None or ext.team_id == team_id`). The mock at line 57-66 returns only the one-team-specific entry per call — never exercises the "global + team-scoped combined on the same team" path through the formatting logic. If the label formatter double-counts a global or deduplicates incorrectly, no test fails.

Concrete addition to `TestGetActiveModifierLabels`:

```
def test_team_sees_both_own_and_global_bonuses(self):
    # Configure fake so team 0 returns [team_bonus, global_bonus]
    # Assert the label list has BOTH labels for T0
```

### M2. Shield-row rendering: robustness to mocked font / color

No file named `test_battle_screen_shield_row*` found. Round-1 claimed a test exists ("shield row renders") — possibly inside `test_battle_screen_modifier_labels.py` or `test_battle_screen_edge_cases.py`. If the shield-row test asserts exact pixel color or font-rendered surface equality, it is brittle to any font-render mock change. Worth verifying the test asserts **structural** properties (row is drawn, label contains the team's bonus value as text) rather than pixel equality.

Recommendation: locate the shield-row test; if pixel-based, refactor to assert the list of text strings passed to `font.render` instead.

### M3. No integration test: real battle → labels show expected strings

`test_battle_screen_modifier_labels.py` is pure unit — `BattleScreen.__new__` bypass. No test spins up a headless battle, calls `BattleController.update()`, then asserts labels match expected. A regression in `get_active_bonuses` itself (e.g., a filter change excluding `scope="external"`) would not be caught.

Low priority (the unit test covers the formatter), but an integration test would lock the full visual-mode pipeline once.

### M4. Grouped vs ungrouped coexistence semantics

Audit prompt Q7: "one grouped entry value=1.5 + one ungrouped entry value=1.2 → MAX then add, or SUM?"

Per `fleet_aura_manager.py:312-323` + `_aggregate_ability_groups`: ungrouped gets `group = f"_default_ext_{idx}"` (unique key). Grouped `stack_group="shield_boost"` is its own key. Two different keys → SUM across groups. Result: 1.5 + 1.2 = 2.7. Never explicitly locked in a test. If someone changes `f"_default_ext_{idx}"` to `f"_default_ext"` (constant key), all ungrouped externals collapse into one group and MAX — silent behavior change.

Recommended test:

```
def test_grouped_entry_sums_with_ungrouped_entry():
    # stack_group="shield_boost" value=1.5 + stack_group=None value=1.2
    # Expected: 1.5 + 1.2 = 2.7 (different groups → SUM)
```

### M5. Text-regex behavioral tests — false-positive risk

`TestStrategyCompilerBehavioralStatKeys` (line 372-472) and `TestBattleSetupCompilerBehavioralStatKeys` (line 500-578) invoke the real compiler functions and assert stat_keys on emitted entries. These are **not** regex-based — they're behavioral and will survive reformatting.

But `TestNoPlaceholderStatKeyInBattleSetupCompiler` (line 475-497) and `TestNoPlaceholderStatKeyInStrategyCompiler` (line 626-684) **are regex-based** on function bodies. If the body of `_entries_from_fleet_combat_modifiers` is refactored into helper functions (e.g., `_emit_shield_mult_entry(...)`), the regex `re.search(r"if shield_mult != 1\.0:.*?(?=if damage_mult)")` stops matching — test silently skips its assertion and passes. The `assert shield_mult_block and ...` form protects against that, but only the `assert match` on the outer regex fires; the `and "placeholder" not in shield_mult_block.group(0)` short-circuits to `True` if `shield_mult_block` is `None`.

Actually — re-reading: `assert shield_mult_block and "placeholder" not in shield_mult_block.group(0)` — if `shield_mult_block` is None, `shield_mult_block and X` is falsy, assert fails. OK, safe.

But `TestNoPlaceholderStatKeyInBattleSetupCompiler.test_complex_entries_body_contains_no_placeholder_literal`: `assert match, "Could not locate _complex_to_entries helper"`. If someone renames `_complex_to_entries` to `_build_complex_entries`, assert fires — OK.

Verdict: the text-regex guards are more robust than they look. **Area is clean.**

---

## LOW — Observations / nits

### L1. `test_apply_bonuses_invokes_ship_recalculate_stats` only verifies the call happens

Line 348-372 of `test_fleet_aura_manager_modifier_stack.py`. It asserts `recalculate_stats.assert_called()` but doesn't verify it was called **with updated external_stats** (i.e., the order of operations: `ship.external_stats = new_external_stats` line 366, then `recalc()` line 373). A regression that calls `recalc()` BEFORE the assignment would leave stale `max_shields`. Current test passes either way.

Tighter assertion: use a `side_effect` on `recalculate_stats` that captures `ship.external_stats` at call time and asserts it already equals the new value.

### L2. Mid-battle complex destruction — missing FEATURE, not just missing test

User's feedback: "complex destroyed → bonus gone, never landed because Battle Setup complexes aren't ships." Confirmed: `_build_modifier_stack` snapshots `team_modifiers` at battle start. Nothing removes a ModifierEntry mid-battle. This is a PROJ-272 scope item (feature gap), not a test gap. **Do not file as missing test** — file as missing feature with a tombstone comment in the compiler.

### L3. `_real_entry` helper naming

`_real_entry(...)` in spec_compiler.py hints at the ghost of `_entries_from_modifier_source` (the deleted placeholder emitter). Naming is OK but in 6 months the "_real_" prefix reads as suspicious. Consider renaming to `_entry` in a future cosmetic pass.

---

## Areas Clean (verified during audit)

- **Phase 9 deletion regression check**: `_entries_from_modifier_source` has zero production references. The comment at `spec_compiler.py:319` documents deletion. No tests were asserting on the deleted path's outputs (checked `test_fleet_aura_manager_modifier_stack.py` entries — all build `ModifierStack` directly, not via the deleted helper).
- **external_stats save/load leak guard** — `test_ship_external_stats_serialization_guard.py` covers it (file exists, from round-1 fix).
- **Whitelist meta-assertion** — `TestNoDirectBattleEngineConstruction.test_whitelist_size_locked` locked at 3 (line 70-78).
- **Glob-based complex discovery** — `test_no_placeholder_from_any_real_complex` (line 550-578) globs `data/designs/qs_*_complex.json` — round-1 fix confirmed.
- **shield_bonus_add placeholder warning guard** — line 397-417 asserts `caplog.records` absence of "placeholder" substring.
- **shield_bonus_add per-team isolation** — line 243-281 locks both add and mult isolation.
- **Phase 7 intra/inter-group MAX/SUM, None = unique** — lines 305-394. Three tests cover the external-only paths.
- **Behavioral stat_key tests survive text refactors** — they call real compiler functions (lines 372-472, 500-578).
- **`_complex_to_entries` non-placeholder guard** — inline regex still catches literal `stat_key="placeholder"`.

---

## Summary

5 HIGH findings (provider × external stack_group, 3+ team silence, two consecutive-battle leak, destroyed-ship clearing, projectile crash in TargetEvaluator fallbacks). 5 MEDIUM (label formatter coverage, shield-row robustness, integration label test, grouped×ungrouped lock, text-regex nuance). 3 LOW (call-order precision, mid-battle complex as feature gap, naming nit).

Of the 5 HIGH, **H5 (projectile crash in TargetEvaluator)** is most likely to bite in production — the code path is reachable any time a ship with `pdc_arc` targeting also has `has_weapons` or `least_armor` in its targeting rules, and the cache-miss fallback is uncovered. H3 (consecutive-battle external_stats reset) is the next most important — strategy-mode campaigns reuse ships across battles.
