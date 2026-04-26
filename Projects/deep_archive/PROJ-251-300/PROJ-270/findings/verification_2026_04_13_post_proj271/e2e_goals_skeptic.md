# End-to-End Goals — Skeptical Audit (post-PROJ-271)

**Date:** 2026-04-13
**Scope:** Verifying user-visible goals of PROJ-269, PROJ-270, PROJ-271
**Method:** Code trace from user action to observable effect. No runtime.

## Executive summary

- **PROJ-269 goal (single entry)** — the production code path is intact: `app.py::start_battle(spec)` routes into `BattleController.set_spec` / `run_battle`. The Strategy path (`SimulationBattleResolver.resolve_battle` → `build_strategy_battle_spec` → `run_battle`) is wired. Battle Setup path (`_start_battle` → `build_manual_battle_spec` → `run_battle`) is wired.
- **PROJ-270 goal (storm + friendly booster)** — wired end-to-end. `ConflictResolutionEngine._resolve_combat_simulated` does call `collect_combat_modifiers(f1, f2, ...)` and `collect_combat_modifiers(f2, f1, ...)` before `resolver.resolve_battle`, so team0/team1 modifiers flow through. `_entries_from_environmental_effects` emits a real `shield_capacity_mult`. `FleetAuraManager._apply_bonuses` writes `ship.external_stats` and triggers `recalculate_stats`. Works.
- **PROJ-271 goal (flat shield bonus + suppressor)** — plumbing is in place; `ship_stats.py::_apply_aggregated_stats` reads `shield_bonus_add` from `external_stats` and applies `(base + flat) × mult`. Strategy compiler emits real `shield_bonus_add`. Battle Setup compiler parses complex design JSON. Works **in simulation**.
- **HOWEVER — the user CANNOT SEE most of this.** `BattleResultsScreen._draw_ship_card` (lines 212–258) renders only `hp_percent` and weapon accuracy. `ShipResult.max_shields` and `current_shields` are populated but never drawn. A +50 flat shield bonus is invisible to the user post-battle. No live "active modifiers" panel in Battle Screen either. **This is the load-bearing user-visible gap.**
- **Second load-bearing gap:** external `ModifierStack` entries always SUM in `FleetAuraManager._recalculate` (lines 299–310) **without honoring `stack_group`**. Two `flat_shield_bonus` sources (e.g., two "shield_projector_complex" toggles on the same side, or storm_shield × fleet_shield_mult for shields) will SUM when they should have MAXed per PROJ-271 decisions (two-phase stacking). This is a silent correctness bug.

---

## MANUAL SMOKE SCRIPT (user-operated)

> Run via `python launcher.py`. Report numeric observations, not "works/doesn't". Where a number is "invisible", NOTE "cannot observe — need dev-console/logs".

### Step 1 — Battle Setup: baseline shields (PROJ-269)
1. Launch → "Battle Setup".
2. Side 0: add one Frigate (or smallest combat ship). Side 1: add one target dummy / frigate.
3. All complex toggles **OFF** on both sides.
4. Click **Start Battle**.
5. On the Battle Screen, hover a ship to see its shield bar. **Record `current/max shields`** (e.g., `200/200`).
6. Wait for battle to end. Click through to Results screen.
7. **Expected**: HP bars render. **Observe**: are `current_shields`/`max_shields` numbers displayed anywhere on the Results screen? *Likely answer: NO — only `HP: X%` is rendered per ship card.* → **FINDING H-1**.

### Step 2 — Battle Setup: friendly shield-projector complex (PROJ-271 core)
1. Return to Battle Setup. Same ships as Step 1.
2. Side 0: toggle ON a **system-scope** shield-projector complex (or sector-scope if UI only exposes sector).
3. Start Battle. On the Battle Screen, within the first 5 ticks, check Side 0's frigate max_shields (dev console: `ship.max_shields`, or watch shield bar).
4. **Expected**: Side 0 max_shields = baseline + flat_bonus (e.g., 200 → 250 for +50). Side 1 unchanged.
5. **Likely-to-be-wrong**: if two shield-projector complexes are toggled and they share `stack_group`, they SUM instead of MAX. → **FINDING H-3**.
6. Results screen: observe that the +50 bonus is **invisible** — `ShipResult.max_shields` is set to 250 but not drawn. → **FINDING H-1**.

### Step 3 — Battle Setup: opposing damage-suppressor complex (PROJ-271 routing)
1. Same battle. Add Side 0: toggle ON a sector-scope "damage suppressor" complex whose DamageModifier has `scope="enemy_sector"`.
2. Start Battle. Observe Side 1 ship weapon damage per tick (watch HP attrition on Side 0).
3. **Expected**: Side 1's ships deal ~20% less damage (or whatever the DamageModifier multiplier is). So Side 0 HP attrition over 100 ticks < baseline Step 1.
4. **Verify routing**: If the suppressor is on **Side 0's** complex with enemy_*, Side 1 should be debuffed. If on **Side 1's** complex with enemy_*, Side 0 should be debuffed.
5. **Likely-to-be-wrong**: shipping a complex without `enemy_*` scope sets of abilities means the suppressor toggle literally does nothing (the compiler skips SELF scope). → **FINDING M-1**.

### Step 4 — Strategy mode: storm shield interference (PROJ-270)
1. Load a saved strategy game (or seed) where an empire fleet can be moved into a storm hex that is also occupied/adjacent to an opposing fleet.
2. End turn so `ConflictResolutionEngine.resolve_all_conflicts` runs.
3. Watch the log output (INFO level): look for `"Fleet N: strategic combat modifiers - shield=X.XXx, damage=Y.YYx, flat_shield=+Z"`.
4. **Expected**: combat log shows shield_mult < 1.0 when a fleet is in a storm; BattleResult winner reflects the shield reduction.
5. **Likely-to-be-wrong**: if no planet is at/near the storm hex, `_find_reference_planet` returns None and the collector short-circuits → no modifiers collected → storm effect doesn't reach combat. → **FINDING M-2**.

### Step 5 — Strategy mode: opposing damage-suppressor planet (PROJ-271)
1. Same save. Build a facility on **opponent's** planet (or load one) that has a DamageModifier with `scope="enemy_sector"`.
2. Move own fleet into the opposing fleet's hex that resolves via that sector scope.
3. End turn. Read the log line from Step 4.
4. **Expected**: `damage=0.80x` (or whatever) printed for YOUR fleet — meaning YOUR damage output is reduced.
5. **Likely-to-be-wrong**: if the suppressor is on a planet in a different sector but same system, the "sector" scope won't pick it up → no suppression. (Is that intended?) → **FINDING M-3**.

### Step 6 — Results screen visibility check (PROJ-270/271 user feedback)
1. After any battle with modifiers applied, land on BattleResultsScreen.
2. **Observe what is rendered**: team winner, HP bars per ship, weapon accuracy. That's it.
3. **NOT rendered**: `current_shields`, `max_shields`, any modifier list, any "+50 from shield projector", any storm indicator.
4. **Impact**: user has no way to know modifiers actually applied. → **FINDING H-1**.

### Step 7 — Destruction of shield-projector provider (edge case)
1. User scenario (PROJ-271 decisions): "If the complex providing shield bonus is destroyed during battle, shield points go away. If the complex is NOT in the sector, bonus stays until drained."
2. Battle Setup complexes are **not ships** — they enter the ModifierStack as static external entries. They cannot be destroyed during battle.
3. **Observe**: toggle a complex + start. There is no in-battle representation of the complex. User's destruction scenario is **impossible to set up via Battle Setup**. → **FINDING M-4**.

### Step 8 — Regression: empty ModifierStack
1. Battle Setup with zero complexes toggled. Start battle.
2. **Expected**: battle runs normally, no errors in logs.
3. `FleetAuraManager.initialize(ships, modifier_stack=stack)` handles `stack.per_team={}` / `stack.global_=()` — both loops iterate zero entries. Safe.

---

## Findings

### CRITICAL — goal not met

None. All three goals' simulation-layer plumbing is in place and integration-tested. The goals are substantially achieved in the engine.

### HIGH — observable bug / visible gap

#### H-1 (NEW PROJ-270 phase): Post-battle shield values are invisible on results screen
- **User scenario**: user toggles shield-projector, expects to see "max shields 250 (base 200 + 50 aura)" on results.
- **Evidence**: `game/ui/screens/battle_results_screen.py:212-258` (`_draw_ship_card`) renders `hp_percent` and `weapons[:3]` accuracy only. `ShipResult.max_shields` (line 38 of `battle_results_data.py`) is set from `ShipOutcome.max_shields` but never painted.
- **Impact**: PROJ-271 integration tests assert `ship_outcome.max_shields == 575` — the DATA is right; the PAINT is missing. User cannot verify the flat bonus without code instrumentation.
- **New phase?** YES — trivial: add a "Shields: C/M" line to `_draw_ship_card`, plus a "Active Modifiers" sidebar summarizing which ModifierStack entries applied per team. Should be a PROJ-272 cosmetic/visibility pass.

#### H-2 (NEW PROJ-270 phase): Battle Screen has no live modifier indicator
- **User scenario**: during a battle, user wants to verify "my storm debuff is actually active".
- **Evidence**: `battle_screen.py` has no hook to draw the list from `FleetAuraManager.get_active_bonuses(team_id)` — the method exists (line 364) but has zero UI consumers found in grep.
- **Impact**: modifiers may silently fail to apply and user never notices.
- **New phase?** YES — small visibility pass (HUD overlay listing active per-team modifiers + global modifiers).

#### H-3 (NEW PROJ-270 phase): External modifiers ignore `stack_group`; always SUM
- **User scenario**: two friendly shield-projector complexes on the same side, both sharing `stack_group="shield_projection"`. User expects MAX (per two-phase aggregation decision).
- **Evidence**: `fleet_aura_manager.py:299-309` — `for ext in self._external:` unconditionally `current + ext.value`. No grouping. Compare to ship-provider path at line 258-296 which DOES use `_aggregate_ability_groups`.
- **Impact**: silent multiplier/additive explosion when complexes overlap. Two +50 complexes → +100 instead of +50. Two 0.5x suppressors from different enemies → 1.0x (SUM) when they should have been 0.5x (MAX). Breaks user's own stacking decision from `decisions.md` (2026-04-13 row 3).
- **Evidence**: `battle_setup/spec_compiler.py:371` DOES set `stack_group=ability_data.get("stack_group")` on each `ModifierEntry` — the data is there. The consumer just ignores it.
- **New phase?** YES, this is a **correctness bug**, not polish. Fix: route `external` entries through `_aggregate_ability_groups` like ship-provider entries.

### MEDIUM — edge case

#### M-1: Battle Setup complex with only SELF-scoped abilities emits no entries
- **Evidence**: `battle_setup/spec_compiler.py:352` `if scope_str == "self": continue`. Most complex designs (e.g., "shield complex") may have their ability scoped to the complex's own components (SELF). The compiler silently skips it and no modifier is emitted.
- **Impact**: user toggles a visually-promising complex, sees no effect, file no log warning distinct from the already-muted placeholder path. Unlike the strategy path, there's no log warning for "zero mapped abilities".
- **Recommend**: compiler should log a WARNING (once per design) when a toggled complex produces zero ModifierEntries.

#### M-2: `_find_reference_planet` returns None → strategy modifiers silently skip
- **Evidence**: `combat_modifier_collector.py:57-60`. If the battle hex has no planet and no system with planets, `ref_planet is None` → early return with empty `FleetCombatModifiers`. Means storm-only battles in empty space get `shield_mult=1.0`, `damage_mult=1.0`, even though PROJ-270 Phase 6.1 wanted storm to work independently of planets.
- **Impact**: storm shield interference in deep space (no colonized systems) is a no-op. The `environmental_effects` path in `conflict_resolution_engine.py:297-302` is collected independently of the planet — but the `team0_mods`/`team1_mods` path is planet-gated. So storms DO reach the battle (via `environmental_effects` → `_entries_from_environmental_effects`), but per-team boosters require a reference planet. Partially by design, but easy to confuse.
- **Recommend**: comment/doc clarification + consider relaxing `_find_reference_planet` (use system root even without planets).

#### M-3: 3+ team scenario not covered
- **Evidence**: `battle_setup/spec_compiler.py:92` `_NUM_TEAMS = 2` + `_route_team_for_scope` returns `1 - owner_team`. Battle Setup UI has `side_0`/`side_1` (only two sides). **Cannot make a 3-team Battle Setup today.**
- **Evidence**: Strategy path `_resolve_combat_at_hex` (`conflict_resolution_engine.py:215-256`) picks TWO fleets at a time (`self._rng.sample(emp_ids, 2)`) — so 3+ empire collision resolves as a sequence of 1-vs-1 battles, never a true 3-team battle. `build_strategy_battle_spec` is called with exactly 2 fleets per call.
- **Impact**: no bug today — 3-team isn't expressible. But `build_strategy_battle_spec` accepts `fleets: List[Fleet]` with N>2 and the modifier routing has no 3+ team concept; if future code ever calls it with N=3, suppressor "opponent" routing is undefined.
- **Recommend**: add an assertion `assert len(fleets) == 2` to both compilers until 3+ team is a real feature.

#### M-4: Ship-destruction-removes-bonus only works for ship-providers, not Battle Setup complex toggles
- **User scenario** (decisions.md): "If the complex providing bonus is destroyed mid-battle, bonus goes away."
- **Evidence**: Battle Setup complexes become `ExternalModifier` entries (`fleet_aura_manager.py:37`), which are `permanent for the battle` per the dataclass docstring. There is no "provider component" to destroy.
- **Impact**: the user's destruction semantics are only honored for SHIP-mounted non-SELF abilities (`ShieldProjection` on an actual fleet ship). Battle Setup complexes can never be destroyed because they aren't in the battle as ships. The spec doesn't currently encode "this complex is represented by X ship instances".
- **Recommend**: document this limitation in `decisions.md` or in a Battle Setup UI tooltip. If the user wants destroyable complexes, they need a separate feature (complex-as-ship spawning at compile time).

### LOW — polish

#### L-1: No UI preview of complex effects
- Battle Setup toggles are opaque labels. User can't see "shield projector complex = +50 flat, system-scope, stack_group=shield_projection" without opening JSON.
- **Recommend**: hovering a toggle should show its parsed stat_keys and scope.

#### L-2: `_log_placeholder_once` spams UI logs silently
- `FleetAuraManager._log_placeholder_once` writes WARNING to `logger`. In production, this goes to console only — users never see it. Might deserve promotion to a visible notification in dev/test builds.

#### L-3: Save/load during a battle is undocumented relative to `external_stats`
- `external_stats` is re-applied on `FleetAuraManager.initialize` (battle start) and `update` (per tick). Mid-battle save/load: if the save captures `ship.external_stats` without capturing the ModifierStack, restoring mid-battle would leave stale stats. Worth a test.

---

## Regression scenarios (actionable test candidates)

1. **Empty ModifierStack**: `build_strategy_battle_spec([f1, f2])` with no env/team modifiers → `ModifierStack.per_team={}, global_=()`. Battle runs. Already covered by tests.
2. **Same-team battle (error)**: `build_strategy_battle_spec([f1_team0, f2_team0])` — not prevented. Both fleets get `team_id=0/1` positionally, so it becomes a misconfigured battle where "team1" has team0's fleet. No assertion catches it. Recommend adding a Rule 3 guard in the strategy compiler (raise on `len({fleet.owner_id for fleet in fleets}) < 2`? — but could be legitimate for test battles).
3. **Zero-base-shield ship with `flat_shield_bonus=+50`**: `_apply_aggregated_stats` line 456 sets `ship.max_shields = acc['max_shields']` (0), then line 469 adds `flat_shield_bonus * shield_capacity_mult` → ship has 50 max_shields. Then `_initialize_resources` line 609-610 fills `current_shields = max_shields`. Works correctly (ship with 0 shield gens gets 50 shields from the aura). **No test covers this.**
4. **`flat_shield_bonus` + `shield_capacity_mult`**: ordering `(base + flat) × mult` — if mult comes from a separate entry in the same ModifierStack, the compile-time `_apply_aggregated_stats` math is `acc['max_shields']` (already has `shield_capacity_mult` applied inside `ShieldProjection.recalculate()` per comment line 460-461) + `flat * mult`. Means base-shields get mult, flat also gets mult. Matches decision. But if a user has ONLY flat (no real shield component), the `acc['max_shields']` is 0 and mult applies only to flat — still correct. Worth a dedicated integration test.
5. **Mid-battle save/load**: `ship.external_stats` is re-derived from `FleetAuraManager` on every tick where provider state changes — so load-from-save should trigger `FleetAuraManager.initialize` and repopulate. But if save/load restores ships without re-running `initialize`, stats are stale. **Untested.**

---

## New-phase recommendations (for PROJ-270 or successor)

| Priority | Item | Finding | Effort |
|----------|------|---------|--------|
| HIGH | Fix external modifier stack_group aggregation | H-3 | ~30 LOC + 3 tests — route through `_aggregate_ability_groups` |
| HIGH | Render shield C/M + active modifier list on Results screen | H-1, H-2 | ~60 LOC + 2 tests |
| MEDIUM | Warn on complex with zero mapped abilities | M-1 | ~10 LOC + test |
| MEDIUM | Assert `len(fleets) == 2` in compilers, or implement N-team routing | M-3 | ~5 LOC (assert) or larger (full N-team) |
| MEDIUM | Add integration test: zero-base-shield ship + flat bonus | Regression #3 | ~30 LOC test |
| MEDIUM | Add integration test: mid-battle save/load preserves external_stats | Regression #5 | ~50 LOC |
| LOW | Document Battle Setup complex vs ship-provider destruction semantics | M-4 | ~10 lines of `decisions.md` |
| LOW | UI hover tooltip for complex toggles showing parsed effects | L-1 | ~40 LOC |

**Archival recommendation**: PROJ-271 is archivable — its narrow scope ("flat bonus + scope-routed suppressors wired end-to-end") is met and integration-tested. H-1/H-2/H-3 are **not** PROJ-271 regressions — H-3 is a pre-existing PROJ-270-Phase-9 defect never caught, and H-1/H-2 are de-novo visibility gaps. Suggest: archive PROJ-271, open PROJ-272 "Modifier Visibility & Stack-Group Correctness" for the three HIGH items.
