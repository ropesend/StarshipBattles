# PROJ-272 Round-2 E2E Goals Audit — PROJ-269/270/271

**Date:** 2026-04-13
**Scope:** Verify that archived PROJ-269/270/271 overarching user-facing goals hold end-to-end, beyond the specific smoke script.
**Method:** Static trace of production call chains; verified wiring against decisions.md of each project; no game run.

Severity convention: **CRITICAL** (user-facing functional bug), **HIGH** (latent bug or wrong-design that WILL bite), **MEDIUM** (correctness/UX issue users will notice), **LOW** (defensive gap or doc issue).

---

## CRITICAL

### C-1. Battle Setup `_extract_scope` silently defaults to `"self"`, diverging from runtime `default_scope`

**User scenario:** Designer authors a new complex in `data/designs/qs_*_complex.json` using a component whose `ShieldModifier` / `DamageModifier` / `ShieldProjection` ability entry omits an explicit `scope` field. User toggles that complex on side 0 in Battle Setup. The complex **does nothing** — ships receive no bonus.

**Evidence:**
- `game/ui/screens/battle_setup/spec_compiler.py:404-412` — `_extract_scope()` returns `"self"` when the ability data is a primitive OR when the dict lacks a `scope` key.
- `game/ui/screens/battle_setup/spec_compiler.py:352-353` — `if scope_str == "self": continue` skips the entry.
- `game/simulation/components/abilities/planetary.py:449` — `ShieldModifierAbility.default_scope = AbilityScope.ALLIED_SYSTEM`.
- `game/simulation/components/abilities/base.py:105-109` — runtime Ability instance uses `default_scope` when JSON has no `scope` key.

**Impact:** The compiler's "effective scope" disagrees with the runtime's "effective scope" for the SAME data. Today's `data/components.json` audit shows all production entries DO specify `scope` explicitly, so the bug is latent — but the first missing-scope complex component silently breaks. Violates Rule 3 clean-sheet design (should read `default_scope` from the registered ability class, not fall back to `"self"`).

**Also affects strategy:** `game/strategy/services/combat_modifier_collector.py:88,97,121` — `entry.get('scope', 'self')` has the identical latent bug. Runtime Ability construction would use `default_scope`, but this dict-scanning bypass returns `"self"` for missing-scope entries and filters them out of `_FRIENDLY_SCOPE_MAP`.

**PROJ-272 candidacy:** YES — fix by resolving the ability class and reading `cls.default_scope.value` in both compilers. Write a TDD test: complex JSON with `ShieldModifier: {"multiplier": 1.5}` (no scope field) on side 0 → side 0's ships' `max_shields` should scale by 1.5.

---

## HIGH

### H-1. 3+ empire conflicts resolved as sequential 2-fleet duels, strategic modifiers silently miscomputed

**User scenario:** Three empires' fleets meet at one hex (realistic as galaxies fill up). User clicks Resolve Battle.

**Evidence:**
- `game/strategy/engine/conflict_resolution_engine.py:227-256` — `while len(fleets_by_emp) > 1` picks two random empires, resolves via `_resolve_combat` (2-fleet only), removes loser, repeats.
- `SimulationBattleResolver.resolve_battle(fleet1, fleet2, ...)` only accepts 2 fleets.
- `collect_combat_modifiers(f1, f2, …)` computes enemy suppressors using ONLY `f2` as opponent. In a 3-empire battle round, empire A fights empire B while empire C's suppressors against A (or B) are entirely ignored for this sub-battle.

**Impact:**
- 3-empire battle order depends on RNG pair selection, so outcomes are non-deterministic relative to player expectation.
- Enemy suppressors from the third empire are invisible in the pairwise battle — breaks the "enemy_system suppressor affects me whenever I'm in system" mental model.
- No documentation for what users should expect.

**PROJ-272 candidacy:** YES for docs gap (explicit policy: "3+ empires → random pairwise"). Larger fix (N-team battles) is a much bigger project.

### H-2. `capacity_mult` multiplier in flat shield bonus scaling is a time-bomb

**User scenario (future):** Someone adds a fleet aura that sets `external_stats['capacity_mult']` (general capacity modifier, currently used by components but NOT by fleet auras). At that point, the flat shield bonus silently multiplies by BOTH `capacity_mult` AND `shield_capacity_mult`.

**Evidence:**
- `game/simulation/entities/ship_stats.py:469-471`:
  ```python
  capacity_mult = external_stats.get('capacity_mult', 1.0)
  shield_cap_mult = external_stats.get('shield_capacity_mult', 1.0)
  ship.max_shields += flat_shield_bonus * capacity_mult * shield_cap_mult
  ```
- PROJ-271 Phase 12 decision: *"`capacity_mult` isn't populated by any fleet aura today."* But the code reads it anyway.
- `ShieldProjection.recalculate()` (defense.py:44-46) multiplies by both, so the stated intent — "compose identically to real ShieldProjection" — is correct. But `capacity_mult` on a SHIP-LEVEL external_stats affects the FLAT bonus ONLY (not the component's own capacity), because real components go through their own AbilityStatBinding path, NOT through ship_stats's flat bonus line. The flat bonus would then double-count if a future aura exposes `capacity_mult` intending a ship-wide modifier.

**Impact:** Future modifier additions will silently create off-by-factor composition bugs. The `capacity_mult` is dead-code-with-landmine — the exact pattern PROJ-271 Phase 9 eradicated for `_entries_from_modifier_source`.

**PROJ-272 candidacy:** YES — either delete the `capacity_mult` read (document that ship-level capacity_mult is intentionally not supported for flat shield bonus), or wire it into real shield components' `external_stats` consumption path so semantics match.

### H-3. Strategy compiler emits `stack_group=None` for every entry — no inter-storm/inter-fleet MAX

**User scenario:** A hex has TWO overlapping storms (or two stacking environmental effects with the same `shield_capacity_mult` stack_group logically). They SUM instead of MAX.

**Evidence:**
- `game/strategy/combat/spec_compiler.py:451` — `_real_entry()` always uses `stack_group=None`.
- `game/simulation/combat/fleet_aura_manager.py:312-313` — `None` stack_group becomes a unique group (`_default_ext_{idx}`), so each entry SUMs independently.
- Contrast: `CombatModifierCollector.aggregate_multipliers` at `strategic_ability_scanner.py:102-141` DOES apply intra-group MAX for planets at the collector level — but that's pre-compile. Once rolled into `FleetCombatModifiers.shield_mult` (a single scalar) the stack_group identity is lost before reaching the compiler.
- `_entries_from_environmental_effects` also emits `stack_group=None` — two storms at same hex both emit and would SUM.

**Impact:** Today a single AreaEffect per hex is the norm, so this is latent. But the stated PROJ-271 Phase 7 goal was "stack_group respect for external modifiers." The collector-level aggregation only partially satisfies this because the compiler destroys group identity.

**PROJ-272 candidacy:** Verify with a scenario test (two storms same hex); if SUM is intended, document it; if MAX, thread `stack_group` from source data into `FleetCombatModifiers` and then into the emitted `ModifierEntry`.

### H-4. User's "destroy the shield-bonus provider mid-battle" mental model is unachievable

**User clarification (PROJ-271):** "If during battle the component that is providing the shield bonus to the ship is destroyed, then the shield points go away."

**Evidence:**
- Battle Setup complexes are UI toggles → static `ModifierStack` entries. They are NOT ships in battle, cannot be destroyed.
- Strategy battles: `collect_combat_modifiers` produces a snapshot at battle start. The friendly shield-projector planet providing the bonus is NOT a combatant in `run_battle` — it's on the galaxy map. No in-battle mechanism can destroy it.
- The provider-loses-bonus semantic DOES work for ship-mounted fleet auras (`FleetAuraManager._recalculate` rescans operational components each tick). But for external modifiers (planetary, complex-toggle), the entries persist for the whole battle regardless.

**Impact:** User's mental model doesn't match implementation. Either this is a missing feature (in-battle planet targeting?) or a documentation gap.

**PROJ-272 candidacy:** Documentation ticket at minimum. Ship-provider auras already honor the mental model; external entries are static-for-battle by design.

---

## MEDIUM

### M-1. Battle HUD modifier labels format multipliers as additive

**Evidence:** `game/ui/panels/ship_stats_renderer.py:381,384`:
```python
sign = "+" if bonus['value'] >= 0 else ""
color = HP_HEALTHY if bonus['value'] > 0 else HP_CRITICAL
```
A suppressor with `shield_capacity_mult=0.75` renders as `"+0.75 shield_capacity_mult"` in GREEN. User reads this as "+75% shield", actually a 25% shield NERF.

**Impact:** Users misunderstand buff/nerf signs. Labels also show raw stat_keys like `shield_capacity_mult` instead of human-readable names.

**PROJ-272 candidacy:** UI polish — branch on multiplicative vs additive (the `value` range vs 1.0 is the tell, or better, thread `operation` through `get_active_bonuses`).

### M-2. `get_active_modifier_labels` uses `value:.2f` without bounds check

**Evidence:** `game/ui/screens/battle_screen.py:808` — `f"T{team_id} {ability}={value:.2f} ({source})"`. If a future aura emits `value=None` or a non-numeric, this crashes the HUD. Low impact today (every path emits a float), but fragile per Rule 3.

**PROJ-272 candidacy:** Defensive: coerce to float or skip non-numeric.

### M-3. Strategy 3+ empire scenario: modifiers only account for the ONE picked pair

Already flagged in H-1 but worth stating as a separate numerics concern: `ConflictResolutionEngine._resolve_combat_at_hex` picks pairwise and calls `collect_combat_modifiers(f1, f2, …)` — every sub-battle ignores suppressors from the un-engaged third empire's facilities, even though those facilities ARE active in the system. Player will observe inconsistent "why didn't my suppressor work" behavior.

### M-4. Multi-fleet-per-empire strategic battles ignore all but the first fleet

**Evidence:** `conflict_resolution_engine.py:232-233` — `f1 = fleets_by_emp[id1][0]`. If empire A has TWO fleets on the same hex, only the first fights; the second is unengaged until next iteration.

**Impact:** User expects all fleets of the same empire to merge for combat at a hex. This is pre-existing, not a PROJ-269/270/271 regression, but user-visible nonetheless.

**PROJ-272 candidacy:** Possibly; would require merging fleets or N-fleet battle support.

---

## LOW

### L-1. `get_active_bonuses` exposes raw `stat_key` ability names

External modifiers surface as `'ability': 'shield_capacity_mult'`, ship-providers as `'ability': 'ShieldModifierAbility'`. UI has no consistent naming; users see internal identifiers.

### L-2. Save/load round-trip of a mid-battle state not verified

Nothing PROJ-269/270/271 tests or documents the behavior when a user saves mid-battle and reloads. `run_battle` is synchronous and atomic — no checkpoint exists mid-battle — so the question may be moot, but worth one sentence in documentation.

### L-3. Phase 7 external-entry aggregation test may not exercise ship-provider-only auras

PROJ-271 Phase 7 unified ship-provider and external-entry aggregation. Existing tests appear to cover the unified path. Consider adding a regression test that runs a battle with ONLY ship-provider auras (no external entries) and verifies numerical equivalence with pre-Phase-7 behavior, to prevent silent regressions.

---

## Overall Assessment

The archived PROJ-269/270/271 goals generally hold end-to-end. The critical strategic-battle chain is wired correctly:
`ConflictResolutionEngine → collect_combat_modifiers → SimulationBattleResolver → build_strategy_battle_spec → ModifierStack → FleetAuraManager._append_external_from_entry → ship.external_stats → ship_stats._apply_aggregated_stats → ship.max_shields`, and the Results screen + Battle HUD surface the numbers (Phase 8).

However, the largest user-facing gap is **C-1**: the Battle Setup compiler's `_extract_scope()` fallback to `"self"` diverges from the runtime Ability base class's `default_scope` fallback. This is a clean-sheet-design violation (Rule 3) that currently survives only because every production complex JSON explicitly specifies a scope. The first content-author omission will silently no-op their complex.

Secondary concerns: 3+ empire handling (H-1/M-3/M-4) is genuinely under-specified relative to PROJ-271's fleet-aura-modifier goals, the `capacity_mult` in shield bonus scaling (H-2) is a latent double-count, the strategy compiler's universal `stack_group=None` (H-3) undermines the Phase 7 stacking intent, and the user's destroy-the-provider mental model (H-4) applies only to ship-mounted auras, not to strategic external modifiers.

## Recommended PROJ-272 Scope

1. **C-1 fix** — compilers resolve `default_scope` from ability class (TDD, include `default_scope != SELF` complex test).
2. **H-2 fix** — remove `capacity_mult` read from `ship_stats._apply_aggregated_stats` OR thread it through properly; add a test that fails if future aura populates `capacity_mult`.
3. **H-3 decision + fix** — decide SUM-vs-MAX for overlapping storms/planet-auras at compile time; thread `stack_group` from source.
4. **M-1 UX fix** — multiplier-vs-additive display branch in HUD + ship panel.
5. **H-1/H-4 docs** — document 3+ empire sequential-pairwise policy; document that external modifiers are static-for-battle.

Items M-2, L-1/L-2/L-3 are defensive polish suitable for a cleanup batch.
