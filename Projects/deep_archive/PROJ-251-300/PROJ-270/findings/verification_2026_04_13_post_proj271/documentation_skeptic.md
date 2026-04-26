# Documentation Skeptic Audit — PROJ-269/270/271 (2026-04-13)

Skeptical audit of `docs/` for drift against PROJ-269 (unified entry), PROJ-270 (Phase 9 external-stats bridge), and PROJ-271 (SHIELD_BONUS_ADD + scope-driven team routing).

## Executive Summary

1. **Phase 9 external-stats bridge is undocumented outside code comments.** `Ability.get_effective_stat()` now composes local + external values (`_mult` multiply, `_add` sum), but `docs/guides/adding_abilities.md` Step 5 and `docs/guides/modifier_system.md` still describe a 3-tier lookup (ability_stats → stats → default). This is the single highest-impact gap — contributors will write code that ignores the external composition path.
2. **PROJ-271 landed but docs still say "pending PROJ-271".** `docs/systems/combat_simulation.md` line 432 and `docs/systems/strategy_layer.md` lines 756-758 claim `flat_shield_bonus` and suppressors are deferred. They're not. `SHIELD_BONUS_ADD`, `_ABILITY_TO_STAT_KEY`, and `_route_team_for_scope` all shipped in PROJ-271.
3. **`SHIELD_BONUS_ADD` missing from the ability-reference additive stat_keys table** (`docs/systems/ability_reference.md:1538-1545`). A contributor looking for "what additive stat_keys exist" will not find the one PROJ-271 introduced.
4. **Stale reference to deleted `BattleFactories`** in `docs/01_ARCHITECTURE.md:162` (UI services table). File does not exist in `game/ui/services/`.
5. **No pattern-catalog coverage for the external-stats bridge or scope-driven team routing.** `docs/02_PATTERNS.md` lists 23 patterns but neither the Phase 9 `external_stats` bridge nor PROJ-271's `_route_team_for_scope` / `_ABILITY_TO_STAT_KEY` appear. These are load-bearing architectural decisions that future contributors will reinvent or contradict.

---

## CRITICAL Findings (docs describe wrong API / mislead contributors)

### C1. `docs/guides/adding_abilities.md:242-260` — Step 5 explanation of `get_effective_stat` is incomplete

**What's wrong:** The doc describes a three-step resolution (ability_stats → stats → default). PROJ-270 Phase 9 added a fourth step: compose with `ship.external_stats` using `_mult` multiply / `_add` sum semantics. The actual code in `game/simulation/components/abilities/base.py:264-297` has a 14-line PROJ-270 Phase 9 block the doc doesn't mention.

**Recommendation:** Replace the 3-step list with a 4-step one:

```
1. Targeted ability stats: component.ability_stats[ClassName][stat_key]
2. Global component stats: component.stats[stat_key]
3. External (fleet/environmental) stats: ship.external_stats[stat_key]
   (populated by FleetAuraManager from BattleSpec.modifier_stack)
4. Default value: 1.0 for _mult, 0.0 for _add, None otherwise

Composition: if BOTH local (step 1 or 2) and external (step 3) are
present, they stack:
  - _mult keys: multiply (local * external)
  - _add keys: sum (local + external)
```

Add a cross-reference to `docs/systems/combat_simulation.md` Fleet Aura System section, and note that external_stats is **read-only** from the ability's perspective (never write back). Should be a new PROJ-270 phase (or quick PROJ-271 closeout task) — this is the reference for every future ability author.

### C2. `docs/systems/combat_simulation.md:427-433` — Says PROJ-271 scope is "pending"

**What's wrong:** Text reads "`flat_shield_bonus` + suppressor effects remain placeholders pending PROJ-271 (new additive stat_key + opponent-team routing)." PROJ-271 completed all 5 phases on 2026-04-13. `SHIELD_BONUS_ADD` is live, and `_route_team_for_scope` is live in the Battle Setup compiler.

**Recommendation:** Replace the last sentence of the "Battle math on strategic modifiers" paragraph with:

> **Post-PROJ-271 Track B:** `flat_shield_bonus` now emits `StatKey.SHIELD_BONUS_ADD` (additive) from `game/strategy/combat/spec_compiler.py`. Ship-level plumbing in `ShipStatsCalculator._apply_aggregated_stats` reads `ship.external_stats['shield_bonus_add']` and adds it to `max_shields` once per ship (pipeline order `(base + flat) × mult`). Opponent-team routing (`enemy_sector` / `enemy_system` scopes) is handled by `_route_team_for_scope` in `game/ui/screens/battle_setup/spec_compiler.py` for the Battle Setup path; the strategy path routes via `CombatModifierCollector` which already consumes enemy-scoped abilities from opposing empires. No placeholder stat_keys remain for these modifier types.

### C3. `docs/systems/strategy_layer.md:752-758` — Same stale "pending PROJ-271" text

**What's wrong:** Identical stale claim in the Strategic-to-Combat Bridge section.

**Recommendation:** Append a new bullet:

> - **Post-PROJ-271 Track B:** strategy compiler now emits `StatKey.SHIELD_BONUS_ADD` for `flat_shield_bonus`; ship-level `external_stats['shield_bonus_add']` plumbing in `ShipStatsCalculator` adds the bonus once per ship (not per shield component) with pipeline ordering `(base + flat) × mult`. Enemy-scoped abilities (`enemy_sector` / `enemy_system`) are already routed to the opposing team by `CombatModifierCollector` at strategy-collector time; `FleetAuraManager` simply applies each `ModifierStack.per_team[team_id]` bucket to that team's ships.

### C4. `docs/systems/ability_reference.md:1538-1545` — `SHIELD_BONUS_ADD` missing from additive stat_keys table

**What's wrong:** The "Additive (default 0.0)" table lists `MASS_ADD`, `ARC_ADD`, `ACCURACY_ADD`, `PROJECTILE_STEALTH_LEVEL`. It does NOT include `SHIELD_BONUS_ADD` which `stat_keys.py:59` and `stat_keys.py:73-79` declare as an additive stat (defaults to 0.0 in `get_default`).

**Recommendation:** Add a row:

```
| SHIELD_BONUS_ADD | Ship-level max_shields bonus (not per-component); fed by flat_shield_bonus from planetary ShieldProjection |
```

Also, elsewhere in the file the `ShieldProjection` entry should note that when the ability is at a non-SELF scope (fleet/sector/system), its value flows through `SHIELD_BONUS_ADD` and applies at ship level, not per-component. This is an architectural distinction contributors need.

---

## HIGH Findings (missing coverage of load-bearing patterns)

### H1. `docs/02_PATTERNS.md` — No pattern entry for "External Stats Bridge" or "Ability Composition"

**What's wrong:** The catalog documents patterns through `#23 Tick Phase Registry`. The PROJ-270 Phase 9 Option A decision (`ship.external_stats` dict populated by `FleetAuraManager`, consumed by `Ability.get_effective_stat` via composition) is a named architectural choice — locked in `PROJ-270/decisions.md` — and a contributor writing a new fleet-wide ability, or debugging why a strategic modifier doesn't reach ships, needs this in the catalog.

**Recommendation:** Add a new pattern `#24 External Stats Bridge (ModifierStack → Ship)`:

- **Where:** `game/simulation/combat/fleet_aura_manager.py::_append_external_from_entry`, `_apply_bonuses`; `game/simulation/entities/ship.py:148` (`self.external_stats`); `game/simulation/components/abilities/base.py:264-297` (composition in `get_effective_stat`).
- **How it works:** `FleetAuraManager.initialize(ships, modifier_stack=...)` walks `modifier_stack.globals + modifier_stack.per_team[team_id]`, turns each `ModifierEntry.effect.stat_key` into an entry on `ship.external_stats[stat_key]`. At ability recalculation time, `Ability.get_effective_stat(stat_key)` composes local (component) and external (ship) values — `_mult` keys multiply, `_add` keys sum, unknown-shape keys take external.
- **Invariants:** `external_stats` is READ-ONLY at consumption time; `ModifierStack` remains the single source of truth. `FleetAuraManager` rewrites `external_stats` on aura recalculation (provider destroyed → entries removed), never mutates `component.stats`.
- **When to use:** Any new ability that needs to respond to fleet-, system-, or environment-level modifiers. Prefer this over ship-attribute mutation (pre-PROJ-269 `_apply_strategic_modifiers` pattern — deleted).

### H2. `docs/02_PATTERNS.md` — No pattern entry for scope-driven team routing

**What's wrong:** PROJ-271 Phase 3 introduced scope as the team-routing discriminator (`enemy_*` → opponent team, else → owner team). This is a locked decision in `PROJ-271/decisions.md:25`. Two call sites already use it (`_route_team_for_scope` in `game/ui/screens/battle_setup/spec_compiler.py`; the collector path in `game/strategy/services/combat_modifier_collector.py:108-127`). Future spec compilers will need to follow this pattern or produce wrong-team routing silently.

**Recommendation:** Add a new pattern `#25 Scope-Driven Team Routing in Spec Compilers`:

- **Where:** `game/ui/screens/battle_setup/spec_compiler.py::_route_team_for_scope`, `_OPPONENT_SCOPES`; `game/strategy/services/combat_modifier_collector.py` (collector-side equivalent).
- **How it works:** At spec-compile time (not engine runtime), an ability's `scope` value discriminates routing. Scopes in `_OPPONENT_SCOPES = {"enemy_sector", "enemy_system"}` → `per_team[1 - owner_team]`; all others → `per_team[owner_team]`. A "suppressor" is just `*_mult < 1.0` with an `enemy_*` scope; a "booster" is `*_mult > 1.0` with a `player_*`/`fleet` scope. No new ability class, no new spec field — scope IS the discriminator.
- **When to use:** Any spec compiler emitting `ModifierEntry` records to `ModifierStack.per_team`. Always key the team by scope, never by ability class.

### H3. `docs/02_PATTERNS.md` #14 — Two-Phase Aggregation mentions old "MULTIPLICATIVE_ABILITIES" conceptually but MEMORY.md says that set is deleted

**What's wrong:** MEMORY.md notes: "removed MULTIPLICATIVE_ABILITIES — all abilities now use intra-group MAX, inter-group SUM". The pattern doc (02_PATTERNS.md:1032-1067) correctly describes MAX/SUM but doesn't explicitly flag that MULTIPLICATIVE_ABILITIES is gone. Low-severity but the aggregation doc is a natural place to record that decision. Also relevant to PROJ-271 because `flat_shield_bonus` aggregation in `CombatModifierCollector` still uses MULTIPLY for `shield_mult`/`damage_mult` via `aggregate_multipliers()` (see `04_SERVICES.md:638`). The overall rule "ability aggregation = MAX/SUM, collector aggregation = MAX/MULTIPLY" is implicit and would confuse a contributor.

**Recommendation:** Add a sentence at the bottom of §14: "Two-phase aggregation in `calculate_ability_totals()` uses MAX / SUM. The separate strategic-modifier collector (`combat_modifier_collector.py`, `strategic_ability_scanner.aggregate_multipliers`) uses MAX / MULTIPLY for stacking multipliers across planetary facilities — these are distinct aggregation pipelines with different semantics."

### H4. `docs/systems/combat_simulation.md` §Fleet Aura System — Does not describe `external_stats` bridge

**What's wrong:** Lines 413-426 describe FleetAuraManager and the ModifierStack plumbing but stop at "translates each ModifierEntry into an ExternalModifier." The bridge from `FleetAuraManager` to `ship.external_stats` (PROJ-270 Phase 9) and how abilities consume it is never stated. A reader of this doc section would not realize that `external_stats` exists or how it composes.

**Recommendation:** Add a paragraph after the "External modifiers" block:

> **Ship-level external stats bridge (PROJ-270 Phase 9):** `FleetAuraManager._apply_bonuses` writes aggregated per-ship stat_key values into `ship.external_stats: Dict[str, float]`. `Ability.get_effective_stat(stat_key)` then composes local (component) and external (ship) values — `_mult` keys multiply, `_add` keys sum. `external_stats` is read-only at consumption time; `ModifierStack` remains the single source of truth. When the aura manager's provider changes (e.g., storm ends, C&C destroyed), it rewrites `external_stats` and calls `ship.recalculate_stats()` so derived values (e.g. `ShieldProjection.capacity`, `ship.max_shields`) pick up the change.

### H5. `docs/03_CONVENTIONS.md:15` — Still lists `BattleController` as a canonical Battle term

Note: `BattleController` still exists (as visual-mode wrapper) — this is fine. But the table doesn't mention `BattleSpec`, `BattleOutcome`, or `run_battle`. Contributors reading "Battle vs Combat" won't know where to find the spec/outcome DTOs. **Recommendation:** Append a row or sidenote: "See `run_battle(spec) -> BattleOutcome` in `game/simulation/battle_runner.py` for the unified entry; `BattleSpec` / `BattleOutcome` are frozen DTOs in `game/simulation/`." Low priority.

---

## MEDIUM Findings (stale-but-not-misleading)

### M1. `docs/01_ARCHITECTURE.md:162` — Lists deleted `BattleFactories`

**What's wrong:** The `game/ui/services/` row still lists `BattleFactories` — the file does not exist in that directory (confirmed via `ls`). The closest match is `battle_ui_service.py`.

**Recommendation:** Replace `BattleFactories` with `BattleUIService` (and verify that's the intended replacement). Low effort.

### M2. `docs/README.md:4` — "Last verified" block is pre-PROJ-271

Says "2026-04-12 — PROJ-270 in flight." PROJ-270 is substantially closed and PROJ-271 has landed. A contributor reading this believes current doc state is pre-PROJ-271.

**Recommendation:** Bump the stamp to 2026-04-13 and add "PROJ-271 Track B complete: `SHIELD_BONUS_ADD` additive stat_key for `flat_shield_bonus`, scope-driven team routing in Battle Setup spec compiler, `capture_battle_state` hardened with narrowed exception handling."

### M3. `docs/systems/combat_simulation.md:338-341` — `BattleScreen.start(team0, team1)` "retained for ~44 unit tests"

**What's wrong:** Described as a legacy test shim "with no production callers." Per CLAUDE.md Rule 3 (Clean-Sheet Design) + System Migration Policy, this should either be deleted (migrate the 44 tests) or formally deprecated. Docs currently present it as accepted state. Also MEMORY.md says the legacy BattleScreen.start shim still exists. Flag the tension — docs should not normalize legacy shims.

**Recommendation:** Add a line: "TODO: migrate the 44 unit tests off this shim and delete per System Migration Policy — this is a known deferred cleanup." If an audit confirms test count is now different, update. Probably a separate PROJ-xxx.

### M4. `docs/guides/adding_abilities.md` lacks guidance on ship-level vs per-ability stat_keys

**What's wrong:** PROJ-271's key architectural choice (`SHIELD_BONUS_ADD` applies ship-level, not per-component) is documented in `PROJ-271/decisions.md:23`. The "adding a new ability" guide has no guidance for a future contributor asking "should my new additive stat_key be per-ability-binding like `ACCURACY_ADD`, or ship-level like `SHIELD_BONUS_ADD`?" They'll guess wrong.

**Recommendation:** Add a new section after Step 5 ("Understand get_effective_stat"):

> ### Step 5b: Decide — per-ability binding vs ship-level plumbing
>
> Some additive bonuses naturally live on a specific ability (e.g., `ACCURACY_ADD` adds to `BeamWeaponAbility.base_accuracy` via `STAT_BINDINGS`). Others represent "virtual extra components" — bonuses that should apply once per ship regardless of how many matching components the ship has (e.g., `SHIELD_BONUS_ADD` adds a flat value to `ship.max_shields` once, not once per shield component).
>
> Rule: if the ability's base value comes from a specific component attribute and `N` components should stack naturally, use a `STAT_BINDING`. If the bonus is conceptually "+50 shield capacity whether you have 1 or 3 shield generators," use ship-level plumbing in `ShipStatsCalculator._apply_aggregated_stats` (read `ship.external_stats[stat_key]` and apply once).

Should be a new PROJ-271 Phase 6 documentation pass or a small follow-up task.

### M5. `docs/systems/ability_reference.md` — `ShieldProjection` entry doesn't document non-SELF scope semantics

**What's wrong:** When `ShieldProjection` is on a planetary facility with scope `allied_sector`, it emits `SHIELD_BONUS_ADD` via the spec compilers, not the normal capacity increase path. This cross-scope semantic is not documented at the ability's reference entry.

**Recommendation:** Add a note to the ShieldProjection entry: "**Cross-scope behavior:** When scoped to fleet / sector / system (non-SELF), the value flows through `flat_shield_bonus` (strategy compiler) or `_complex_entries` (Battle Setup compiler) and emits a `SHIELD_BONUS_ADD` stat_key on `ModifierStack`, applied once at ship level by `ShipStatsCalculator` (not per-component). See `docs/guides/adding_abilities.md` Step 5b."

### M6. `docs/systems/combat_simulation.md` §1 — No mention of `capture_battle_state` forensic JSON subsystem

PROJ-271 Phase 5 audited and retained `combat_lab/battle_state_capture.py` (Option C). It produces JSON in `combat_lab/battle_states/` consumed by the "View Battle States" UI button. Searching docs for `capture_battle_state` returns zero matches. Contributors will be blindsided.

**Recommendation:** Add a brief subsection to combat_simulation.md §1 titled "Combat Lab forensic state capture":

> `combat_lab/battle_state_capture.py::capture_battle_state` is called from `test_executor.py` after each Combat Lab run. It writes the pre-/post-battle ship state to `combat_lab/battle_states/` and is consumed by the Combat Lab "View Battle States" UI. This is intentionally retained as forensic provenance separate from `BattleOutcome` (which doesn't capture initial state). Guarded by `OSError`-only exception handling (PROJ-271 Phase 5) — programming errors propagate loudly; only disk failures degrade gracefully.

---

## LOW Findings (style, hygiene)

### L1. Code comments referencing PROJ-271 phases

`ship_stats.py:457` ("PROJ-271 Phase 1: flat shield bonus..."), `game/ui/screens/battle_setup/spec_compiler.py:67` ("PROJ-271 Phase 2.4..."), etc. Per CLAUDE.md guidance ("don't reference current task"), once the project archives these should be scrubbed to explain the invariant rather than the historical phase. However: the comments also explain *why* the code composes the way it does — they're useful. Recommend converting from "PROJ-271 Phase 1" prefix to "Invariant:" or "Pipeline ordering:" prefix without deleting the rationale.

### L2. `docs/01_ARCHITECTURE.md:9` — Diagram still labels "Simulation Layer" / "Strategy Layer" / "Core Layer" as if 6-layer — correct, but UI is labelled at top without ApplicationContext / `game.context.py` in the diagram. `context.py` is called out in the row below but not in the diagram. Minor.

### L3. `docs/README.md` still says "23 design patterns" (line 17) — if H1+H2 are adopted, bump to 25.

---

## No-Findings Sections (audit areas where docs are correct)

1. **`docs/guides/simulation_testing.md`** — Previously flagged by `acceptance_audit.md` for the stale `setup(battle_engine)` reference; the fix landed (line 225 now reads "prior versions of this doc showed a `def setup(self, battle_engine)` pattern — that API was deleted..."). The new `_run_validation(outcome, telemetry)` / `validate(outcome, telemetry)` contract is correctly described (lines 153, 204-221). No action needed.

2. **`docs/02_PATTERNS.md` §13 (Spec Compiler + run_battle)** — Accurate. `run_battle(spec) -> BattleOutcome` contract correctly described; the "old mode trait → new BattleSpec field" table (1009-1015) correctly tracks the Phase 6 deletions.

3. **`docs/01_ARCHITECTURE.md` §Battle Flow (post-PROJ-269 unified path)** — Accurate on `run_battle`, `extract_outcome`, `BattleController.start_from_spec` (PROJ-270 Phase 10). No stale references to deleted APIs (`BattleState.mode`, `BattleConfig.test_scenario`, etc. correctly deleted from surrounding text).

4. **`docs/systems/combat_simulation.md` §0 Unified Entry** — Correctly describes `run_battle(spec)` contract, `BattleController.set_spec/get_outcome`, telemetry levels, boundary ADT, component HP persistence.

5. **`docs/04_SERVICES.md`** — BattleService section correctly flags that `run_battle(spec)` is the preferred headless entry; `BattleService` is now visual-mode only.

6. **`docs/03_CONVENTIONS.md`** — Correctly describes naming; no stale references to deleted `battle_factories`, `battle_mode_handler` modules in this file.

7. **Deleted modules (`battle_factories.py`, `battle_mode_handler.py`, `create_*_battle` factories):** No live doc references found outside `docs/_ignore/` (which is excluded by CLAUDE.md).

---

## Recommended Action Plan

1. **Quick wins (≤1h):** C4 (add `SHIELD_BONUS_ADD` row), C2 + C3 (replace "pending PROJ-271" text), M1 (fix `BattleFactories`), M2 (refresh README stamp), L3 (bump pattern count).
2. **Step 5 rewrite (1-2h):** C1 (add external_stats composition to `adding_abilities.md`) + M4 (add Step 5b for ship-level vs per-ability).
3. **Pattern catalog (2-3h):** H1 (external-stats bridge) + H2 (scope-driven team routing) + H3 (aggregation clarification).
4. **Doc-section additions (1-2h):** H4 (FleetAuraManager bridge paragraph) + M5 (ShieldProjection cross-scope note) + M6 (capture_battle_state subsection).

Recommend opening a single "PROJ-271 Phase 6: Documentation sync" task that bundles items 1-4 and closes the Rule 2 contract for the PROJ-269/270/271 arc.
