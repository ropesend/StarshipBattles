# Comprehensive Docs Audit — 2026-04-13 (post-PROJ-271)

## Executive summary

1. `docs/README.md` still says "PROJ-270 in flight" and "23 design patterns" — both wrong after today's work (closure landed; pattern count is 26).
2. `docs/01_ARCHITECTURE.md:199,201` lists deleted DTOs `AIPolicy`, `TaskForceOutcome` in the `game.simulation` public exports.
3. `docs/systems/combat_simulation.md:39,40` DTO table still lists `AIPolicy` and `TaskForceOutcome`.
4. `docs/guides/adding_abilities.md` Step 3 additive-stat-keys table still missing `SHIELD_BONUS_ADD` (the reference example called out in Step 5).
5. `docs/guides/simulation_testing.md:327` tells contributors to implement `validate(engine)` — deleted API; the current contract is `validate(outcome, telemetry)`.
6. `docs/systems/strategy_layer.md:733` description of `CombatModifierCollector` omits the scope-driven pre-routing behaviour that PROJ-271 Phase 8 hard-wired — contributors will miss the enemy-scope pre-compile step.
7. Two critical load-bearing PROJ-271 flows are effectively undocumented for contributors: (a) Battle Setup `_complex_to_entries` ability-class→stat_key map; (b) the `(base + flat) × mult` pipeline ordering on `ship_stats.py::_apply_aggregated_stats`.
8. No cross-ref from `docs/guides/modifier_system.md` to patterns 24 (External-Stats Bridge) / 25 (Scope routing); contributors reading the modifier guide never learn that `ModifierStack` entries ultimately compose through `ship.external_stats`.

---

## Findings by severity

### CRITICAL

#### CRITICAL — `AIPolicy` / `TaskForceOutcome` listed as live exports but deleted
**File:** `docs/01_ARCHITECTURE.md`
**Line(s):** 199, 201
**Issue:** Both classes were deleted (PROJ-270 Phase 13). `game/simulation/battle_spec.py` and `battle_outcome.py` no longer define them. Contributors importing either will get an ImportError.
**Current text:**
> `PROJ-269 BattleSpec DTOs: AIPolicy, BattleSpec, CombatPolicies, ComponentStateSpec, EntryVector, PostBattleHook, ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec.`
>
> `PROJ-269 BattleOutcome DTOs: BattleOutcome, EndReason, HitRecord, ModifierApplication, ShipOutcome, ShipStats, ShipStatus, TaskForceOutcome, TeamOutcome, WeaponSummary.`

**Replace with:**
> `PROJ-269 BattleSpec DTOs: BattleSpec, CombatPolicies, ComponentStateSpec, EntryVector, PostBattleHook, ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec.`
>
> `PROJ-269 BattleOutcome DTOs: BattleOutcome, EndReason, HitRecord, ModifierApplication, ShipOutcome, ShipStats, ShipStatus, TeamOutcome, WeaponSummary.`

**Rationale:** Match actual exports. `AIPolicy` + `TaskForceOutcome` were removed in PROJ-270 Phase 13 as unused promises.

---

#### CRITICAL — Same deleted DTOs in combat_simulation DTO table
**File:** `docs/systems/combat_simulation.md`
**Line(s):** 39-40
**Issue:** Table headed "DTOs (introduced in Phase 1)" still advertises `AIPolicy` and `TaskForceOutcome` as classes living in those two files.
**Current text:**
> `| \`game/simulation/battle_spec.py\` | \`BattleSpec\`, \`TeamSpec\`, \`TaskForceSpec\`, \`SquadronSpec\`, \`ShipSpec\`, \`ComponentStateSpec\`, \`EntryVector\`, \`AIPolicy\`, \`CombatPolicies\`, \`PostBattleHook\` |`
> `| \`game/simulation/battle_outcome.py\` | \`BattleOutcome\`, \`TeamOutcome\`, \`TaskForceOutcome\`, \`ShipOutcome\`, \`ShipStatus\`, \`EndReason\`, \`HitRecord\`, \`WeaponSummary\`, \`ShipStats\`, \`ModifierApplication\` |`

**Replace with:**
> `| \`game/simulation/battle_spec.py\` | \`BattleSpec\`, \`TeamSpec\`, \`TaskForceSpec\`, \`SquadronSpec\`, \`ShipSpec\`, \`ComponentStateSpec\`, \`EntryVector\`, \`CombatPolicies\`, \`PostBattleHook\` |`
> `| \`game/simulation/battle_outcome.py\` | \`BattleOutcome\`, \`TeamOutcome\`, \`ShipOutcome\`, \`ShipStatus\`, \`EndReason\`, \`HitRecord\`, \`WeaponSummary\`, \`ShipStats\`, \`ModifierApplication\` |`

**Rationale:** Same deletion as above.

---

#### CRITICAL — `validate(engine)` is deleted API
**File:** `docs/guides/simulation_testing.md`
**Line(s):** 327
**Issue:** Step 7 of the "Writing Simulation Tests" checklist instructs contributors to implement `validate(engine) -> List[Check]`. The current contract (documented correctly at lines 204-210) is `validate(self, outcome, telemetry=None) -> list`. Following step 7 produces a broken scenario.
**Current text:**
> `**7. Implement \`validate(engine) -> List[Check]\`** with data, precondition, and outcome checks.`

**Replace with:**
> `**7. Implement \`validate(outcome, telemetry=None) -> List[Check]\`** with data, precondition, and outcome checks. \`outcome\` is a frozen \`BattleOutcome\`; \`telemetry\` is the optional \`CombatLabTelemetry\` bundle. See §3 for the full signature.`

**Rationale:** Post-PROJ-270, the `engine` argument was replaced with `(outcome, telemetry)`. Inline code examples in §5 already use the correct signature.

---

### HIGH

#### HIGH — README.md `Last verified` still says "PROJ-270 in flight"
**File:** `docs/README.md`
**Line(s):** 4
**Issue:** PROJ-270 Phase 10 + PROJ-271 Track B are landed. The header line needs to reflect that, and the pattern count "23" is stale (26 as of today's additions).
**Current text:**
> `> **Last verified:** 2026-04-12 — PROJ-270 in flight (closure work on top of PROJ-269). Visual-mode \`BattleController\` now emits \`BattleOutcome\`; strategy-modifier battle math (shield_capacity_mult, damage_mult) wired up; \`ReturnDestination\` moved to \`game/core/\`; \`BattleState.mode\` + \`BattleConfig.test_scenario\` deleted; \`FleetAuraManager\` legacy \`config=\` kwarg removed. See \`Projects/active_projects/PROJ-270/plan.md\`.`

**Replace with:**
> `> **Last verified:** 2026-04-13 — PROJ-270 closure complete, PROJ-271 Track B landed. Every battle compiles a \`BattleSpec\` and emits a \`BattleOutcome\`; strategy + Battle Setup modifier math emits real stat_keys (\`shield_capacity_mult\`, \`damage_mult\`, \`shield_bonus_add\`) that flow through \`FleetAuraManager\` → \`ship.external_stats\` → \`get_effective_stat\`; \`FleetAuraManager\` respects \`stack_group\` (intra-group MAX, inter-group SUM) on external entries; \`ReturnDestination\` lives at \`game/core/return_destination.py\`; \`BattleConfig\` trimmed to visual-mode operational options only. See \`Projects/active_projects/PROJ-270/plan.md\` and \`Projects/active_projects/PROJ-271/plan.md\`.`

**Rationale:** Align header with the actually-landed state so new contributors don't assume closure work is still pending.

---

#### HIGH — README "23 design patterns"
**File:** `docs/README.md`
**Line(s):** 17, 66
**Issue:** Count is now 26 (patterns 24/25/26 added today).
**Current text (line 17):**
> `| 2 | [02_PATTERNS.md](02_PATTERNS.md) | 23 design patterns with file locations and code examples |`

**Replace with:**
> `| 2 | [02_PATTERNS.md](02_PATTERNS.md) | 26 design patterns with file locations and code examples |`

**Current text (line 66):**
> `├── 02_PATTERNS.md               # 23 design patterns (ApplicationContext DI, Facade, CQRS, etc.)`

**Replace with:**
> `├── 02_PATTERNS.md               # 26 design patterns (ApplicationContext DI, Facade, CQRS, External-Stats Bridge, Scope-Driven Team Routing, Spec Compiler, ...)`

**Rationale:** Keep the pattern count in sync.

---

#### HIGH — `02_PATTERNS.md` header still claims "20 patterns"
**File:** `docs/02_PATTERNS.md`
**Line(s):** 3
**Issue:** Top-of-file subtitle reads `Each section: **Where**, **How It Works**, **When to Use**.` preceded by `(20 patterns)`. Count is now 26.
**Current text:**
> `Agent-optimized reference for every core pattern in the codebase (20 patterns).`

**Replace with:**
> `Agent-optimized reference for every core pattern in the codebase (26 patterns).`

**Rationale:** Accurate count; prevents confusion when patterns 21-26 appear in TOC.

---

#### HIGH — CombatModifierCollector doc omits scope-driven pre-routing
**File:** `docs/systems/strategy_layer.md`
**Line(s):** ~729-735 (around the `CombatModifierCollector` bullet)
**Issue:** The entry describes only `FleetCombatModifiers(shield_mult, damage_mult, flat_shield_bonus)`. It doesn't mention that PROJ-271 Phase 8 moved enemy-scope pre-routing here: `CombatModifierCollector` now pre-computes enemy-scope suppressor effects INTO the RECEIVING fleet's `FleetCombatModifiers` before the spec compiler runs, which is why the strategy spec compiler doesn't need an equivalent of Battle Setup's `_route_team_for_scope`. Missing this, contributors will mis-route new enemy-scope effects.
**Current text:**
> `Collects strategic combat modifiers (ShieldModifier, DamageModifier, scoped ShieldProjection) for fleets entering combat. Returns \`FleetCombatModifiers(shield_mult, damage_mult, flat_shield_bonus)\`.`

**Replace with:**
> `Collects strategic combat modifiers (ShieldModifier, DamageModifier, scoped ShieldProjection) for fleets entering combat. Returns \`FleetCombatModifiers(shield_mult, damage_mult, flat_shield_bonus)\`. **Scope routing (PROJ-271 Phase 8):** enemy-scope (\`enemy_sector\` / \`enemy_system\`) effects are pre-computed INTO the RECEIVING fleet's \`FleetCombatModifiers\` before the strategy spec compiler runs. The compiler therefore emits each entry to \`per_team[receiver_id]\` trivially, with no runtime scope lookup. New enemy-scope abilities must extend the collector, not the compiler.`

**Rationale:** The pattern 25 entry in 02_PATTERNS.md correctly describes this; strategy_layer.md needs the same information to prevent contributors from adding routing logic in the wrong layer.

---

#### HIGH — `adding_abilities.md` additive stat_keys table missing SHIELD_BONUS_ADD
**File:** `docs/guides/adding_abilities.md`
**Line(s):** ~186-193 (the "Additive (default 0.0)" table under Step 3)
**Issue:** Step 5 already references `shield_bonus_add` as a reference example for ship-level composition, but the Step 3 stat-key reference table only lists MASS_ADD / ARC_ADD / ACCURACY_ADD / PROJECTILE_STEALTH_LEVEL. Contributors learn about it in Step 5 but can't find it in the canonical StatKey listing where they'd look first.
**Current text:**
> `**Additive (default 0.0):**`
>
> `| StatKey | Typical Use |`
> `|---------|-------------|`
> `| \`MASS_ADD\` | Flat mass addition |`
> `| \`ARC_ADD\` | Add to firing arc |`
> `| \`ACCURACY_ADD\` | Beam accuracy bonus |`
> `| \`PROJECTILE_STEALTH_LEVEL\` | Seeker stealth level |`

**Replace with:**
> `**Additive (default 0.0):**`
>
> `| StatKey | Typical Use |`
> `|---------|-------------|`
> `| \`MASS_ADD\` | Flat mass addition |`
> `| \`ARC_ADD\` | Add to firing arc |`
> `| \`ACCURACY_ADD\` | Beam accuracy bonus |`
> `| \`PROJECTILE_STEALTH_LEVEL\` | Seeker stealth level |`
> `| \`SHIELD_BONUS_ADD\` | Flat shield HP added at ship level (composes as \`(base + flat) × mult\`). Consumed in \`ship_stats.py::_apply_aggregated_stats\`, not via \`STAT_BINDINGS\`. See Step 5 for ship-level vs per-ability guidance. |`

**Rationale:** Keep the canonical stat_key table complete so contributors can discover all available keys without hunting.

---

### MEDIUM

#### MEDIUM — `run_battle(spec, headless=...)` kwarg referenced twice but never exists
**File:** `docs/systems/combat_simulation.md`
**Line(s):** 505
**Issue:** The "Old mode trait → New BattleSpec field" table lists `run_battle(spec, headless=...)` as the replacement for `is_headless_default`. `run_battle` does not accept a `headless` kwarg — visual vs headless is determined by which driver (controller vs blocking tick loop) the caller picks. Same issue at `02_PATTERNS.md:1014`.
**Current text:**
> `| \`is_headless_default\` | \`run_battle(spec, headless=...)\` kwarg |`

**Replace with:**
> `| \`is_headless_default\` | Driver choice: blocking \`run_battle(spec, ...)\` vs per-frame \`BattleController.start_from_spec(spec, ...)\` |`

**And at `docs/02_PATTERNS.md:1014` (same row of the same table):**
**Current text:**
> `| \`is_headless_default\` | \`run_battle(spec, headless=...)\` kwarg |`

**Replace with:**
> `| \`is_headless_default\` | Driver choice: blocking \`run_battle(spec)\` vs per-frame \`BattleController.start_from_spec(spec, ...)\` |`

**Rationale:** Stops new contributors from wasting time searching for a nonexistent kwarg.

---

#### MEDIUM — `FleetAuraManager.initialize(...)` signature doc mismatches external-stats bridge
**File:** `docs/systems/combat_simulation.md`
**Line(s):** 74-86, 422-426
**Issue:** These blocks still describe the old "translate each ModifierEntry into an ExternalModifier using entry.effect.stat_key as the ability name (`ToHitAttackModifier`, `ToHitDefenseModifier`, ...)" contract. Post-PROJ-270 Phase 9 + PROJ-271, `_apply_bonuses` writes ALL team-bonus stat_keys to `ship.external_stats: Dict[str, float]` regardless of whether there's a matching ability name. The `ExternalModifier` / ability-name lookup framing is misleading.
**Current text (74-86):**
> `- \`modifier_stack\` — wired as of Phase 5.5. \`run_battle\` threads \`spec.modifier_stack\` onto \`BattleEngine.modifier_stack\`; at \`start_teams\`, \`FleetAuraManager.initialize(ships, modifier_stack=...)\` translates each \`ModifierEntry\` into an \`ExternalModifier\` using \`entry.effect.stat_key\` as the ability name (\`ToHitAttackModifier\`, \`ToHitDefenseModifier\`, ...). Entries whose \`stat_key == "placeholder"\` are silently skipped — compilers emit those as record-of-presence markers for toggles whose real effect mapping hasn't been authored yet. When a compiler wires a real \`stat_key\`, the aura manager applies it without further engine changes. \`HitLogRecorder\` also consumes the stack at DETAILED telemetry to populate \`HitRecord.modifiers_applied\` with the active modifiers (globals + attacker-team entries, placeholders filtered).`

**Replace with:**
> `- \`modifier_stack\` — wired as of Phase 5.5, retargeted in PROJ-270 Phase 9 + PROJ-271. \`run_battle\` threads \`spec.modifier_stack\` onto \`BattleEngine.modifier_stack\`; at \`start_teams\`, \`FleetAuraManager.initialize(ships, modifier_stack=...)\` registers the stack with the aura manager. Each tick \`_apply_bonuses\` aggregates team-scoped entries into \`ship.external_stats: Dict[str, float]\` keyed by \`entry.effect.stat_key\` (two-phase: intra-group MAX, inter-group SUM, respecting \`stack_group\`). Abilities read this bridge via \`Ability.get_effective_stat\` (\`_mult\` keys multiply local × external; \`_add\` keys sum local + external). Ship-level keys like \`shield_bonus_add\` are read directly in \`ship_stats.py::_apply_aggregated_stats\`. The \`_entries_from_modifier_source\` placeholder path was deleted in PROJ-271 Phase 9 — compilers emit only real stat_keys now. \`HitLogRecorder\` consumes the stack at DETAILED telemetry to populate \`HitRecord.modifiers_applied\`.`

**Current text (422-426):**
> `**External modifiers** (PROJ-270 Phase 6.4a): per-team and global battle conditions flow into the aura manager via \`spec.modifier_stack\` only — the legacy \`BattleConfig.team_modifiers\` / \`global_modifiers\` kwargs were deleted. \`FleetAuraManager.initialize(ships, *, modifier_stack=...)\` translates each \`ModifierEntry\` into an \`ExternalModifier\`. Unknown / placeholder stat_keys emit a once-per-source WARNING so compiler authors see missing mappings immediately (PROJ-270 Phase 6.4).`

**Replace with:**
> `**External modifiers** (PROJ-270 Phase 6.4a + Phase 9, PROJ-271 Phase 7): per-team and global battle conditions flow into the aura manager via \`spec.modifier_stack\` only — the legacy \`BattleConfig.team_modifiers\` / \`global_modifiers\` kwargs were deleted. \`FleetAuraManager._apply_bonuses\` writes ALL entries into \`ship.external_stats: Dict[str, float]\` (not just the two hardcoded keys that survived 5.5). \`stack_group\` is respected via two-phase MAX/SUM aggregation. Unknown stat_keys emit a once-per-source WARNING; placeholders no longer exist (Phase 9 deleted \`_entries_from_modifier_source\`).`

**Rationale:** These sections read as if the 5.5 "ExternalModifier" scaffolding is still the current design. It isn't.

---

#### MEDIUM — Ship-level vs per-ability stat_key guidance not reflected in modifier_system.md
**File:** `docs/guides/modifier_system.md`
**Line(s):** ~14-27, 119-131 (Data Flow + File Locations)
**Issue:** The data-flow diagram shows `Component.stats → Ability.recalculate()` as the ONLY path. Since PROJ-270 Phase 9, a parallel path exists: `ModifierStack → FleetAuraManager → ship.external_stats → (a) Ability.get_effective_stat composition OR (b) ship_stats._apply_aggregated_stats direct read`. Contributors writing a new modifier that needs to compose at ship level (e.g., another `shield_bonus_add`-style key) have no doc pointing them at that path.
**Current text (around line 27, end of "Data Flow" block):**
> `JSON Modifier Definition`
> `         |`
> `ModifierEffectEvaluator.evaluate_modifier()`
> `         |`
> `List[ModifierEffect] (evaluated concrete values)`
> `         |`
> `apply_modifier_effects() aggregates into stats dict`
> `         |`
> `Component.stats / Component.ability_stats`
> `         |`
> `Ability.recalculate() applies via STAT_BINDINGS`

**Replace with:**
> `JSON Modifier Definition                    ModifierStack (battle-scoped)`
> `         |                                        |`
> `ModifierEffectEvaluator.evaluate_modifier()       | (spec compilers emit ModifierEntry)`
> `         |                                        v`
> `List[ModifierEffect]                      FleetAuraManager._apply_bonuses`
> `         |                                        |`
> `apply_modifier_effects()                  ship.external_stats[stat_key]: float`
> `         |                                        |`
> `Component.stats / Component.ability_stats         +---+----------------------------+`
> `         |                                            |                            |`
> `Ability.recalculate() via STAT_BINDINGS ←────────── composition in                read directly in`
> `                                                    Ability.get_effective_stat    ship_stats._apply_aggregated_stats`
> `                                                    (per-ability keys, e.g.       (ship-level keys, e.g.`
> `                                                    damage_mult)                  shield_bonus_add)`
>
> `Component-born modifiers (left path) live on \`component.stats\`; battle-scoped team auras (right path) live on \`ship.external_stats\` and are never serialized. See patterns 24 (External-Stats Bridge) and 25 (Scope-Driven Team Routing) in [02_PATTERNS.md](../02_PATTERNS.md).`

**Rationale:** The modifier_system guide is the landing page for anyone adding modifiers; it currently hides the entire external-stats path from them.

---

#### MEDIUM — `HitRecord.modifiers_applied` "empty tuple in the MVP" claim
**File:** `docs/systems/combat_simulation.md`
**Line(s):** 125-127
**Issue:** Text says `modifiers_applied` "is an empty tuple in the MVP — real modifier-trace provenance requires wiring the ModifierStack through the damage pipeline, deferred to a follow-up." But line 84-86 of the same file (and code) says `HitLogRecorder` "consumes the stack at DETAILED telemetry to populate `HitRecord.modifiers_applied` with the active modifiers (globals + attacker-team entries, placeholders filtered)." Contradiction — one is out of date.
**Current text:**
> `**\`HitRecord.modifiers_applied\`** is an empty tuple in the MVP — real modifier-trace provenance requires wiring the ModifierStack through the damage pipeline, deferred to a follow-up.`

**Replace with:**
> `**\`HitRecord.modifiers_applied\`** is populated at DETAILED telemetry by \`HitLogRecorder\` — each record carries the globals plus attacker-team entries active at the time of the hit (placeholders already pre-filtered by the compiler, since PROJ-271 Phase 9 deleted the placeholder path). At MINIMAL/NORMAL telemetry the field is an empty tuple.`

**Rationale:** Resolves internal contradiction in favour of the newer behaviour.

---

### LOW

#### LOW — `02_PATTERNS.md` Quick Reference table missing pattern 24-26 file anchors
**File:** `docs/02_PATTERNS.md`
**Line(s):** ~1348-1378 (the Quick Reference table at the end)
**Issue:** Table lists patterns 1-23 but stops there. Patterns 24/25/26 that you added today don't appear as quick-reference rows.
**Current text:** the table ends with "Tick Phase Registry" row.
**Replace with:** append three rows:
> `| External-Stats Bridge | \`game/simulation/entities/ship.py\` + \`fleet_aura_manager.py\` | \`ship.external_stats\`, \`FleetAuraManager._apply_bonuses\` |`
> `| Scope-Driven Team Routing | \`game/ui/screens/battle_setup/spec_compiler.py\` | \`_route_team_for_scope\`, \`_OPPONENT_SCOPES\` |`
> `| Spec Compiler → run_battle | \`game/simulation/battle_runner.py\` + 3 compilers | \`run_battle\`, \`BattleSpec\`, \`build_*_battle_spec\` |`

**Rationale:** Quick-reference table is the "index" contributors skim; missing entries defeat its purpose.

---

#### LOW — "44 abilities" count vs 02_PATTERNS TOC
**File:** `docs/README.md`
**Line(s):** 39, 84
**Issue:** Both mention "44 abilities". I did not verify the ability count against the registry, but flag it for a quick sanity check since the ability catalog has grown with PROJ-271 work.
**Current text:** `All 44 component abilities: registry keys, parameters, stat bindings`
**Replace with:** Verify count in `game/simulation/components/abilities/__init__.py::ABILITY_REGISTRY` and update if it has drifted.
**Rationale:** Low-severity but trivial to sync.

---

## Suggested new sections

### NEW — `_complex_to_entries` ability-class → stat_key map

**File:** `docs/systems/strategy_layer.md` (anchor: end of the "Combat Modifier Collection (PROJ-169)" subsection, right before "Activatable Abilities & Stabilizer Pattern")
**Current text:** NEW
**Replace with:**
> `#### Battle Setup Complex-Toggle Compilation (PROJ-271 Phase 2)`
>
> `\`game/ui/screens/battle_setup/spec_compiler.py::_complex_to_entries\` walks a complex design JSON, iterates its components, and maps each relevant ability class to a \`ModifierEntry\` with a specific stat_key:`
>
> `| Ability class in complex design | Emitted stat_key | Operation |`
> `|---------------------------------|------------------|-----------|`
> `| \`ShieldProjection\` | \`shield_bonus_add\` | add |`
> `| \`ShieldModifier\` | \`shield_capacity_mult\` | multiply |`
> `| \`DamageModifier\` | \`damage_mult\` | multiply |`
>
> `Each entry is then routed to the correct team bucket by \`_route_team_for_scope(scope_str, owner_team)\` — \`enemy_*\` scopes go to the opponent team, all other scopes go to the owner's team (\`_OPPONENT_SCOPES = {"enemy_sector", "enemy_system"}\`). Adding a new complex ability type that should influence combat requires extending this mapping; adding a new enemy-scope value requires extending \`_OPPONENT_SCOPES\` AND adding a scope-routing test.`

**Rationale:** Contributors adding a new complex-level ability currently have zero doc pointer to the mapping; they'd have to read the compiler to discover it.

---

### NEW — `(base + flat) × mult` pipeline ordering

**File:** `docs/systems/combat_simulation.md` (anchor: end of §3 "Ship Entity Architecture", right before §4 "Damage Pipeline")
**Current text:** NEW
**Replace with:**
> `### Shield Stat Pipeline Ordering (PROJ-271)`
>
> `\`ShipStatsCalculator._apply_aggregated_stats\` computes \`ship.max_shields\` as:`
>
> `max_shields = (base_shield_capacity + shield_bonus_add) × capacity_mult × shield_capacity_mult`
>
> `- \`base_shield_capacity\` — sum of \`ShieldProjection\` base values from operational components`
> `- \`shield_bonus_add\` — read directly from \`ship.external_stats['shield_bonus_add']\` (flat bonus from e.g. planet shield-projector auras)`
> `- \`capacity_mult\` — aggregated per-ability multiplier (component modifiers)`
> `- \`shield_capacity_mult\` — external team-aura multiplier (storm interference, fleet boosters), also read from \`ship.external_stats\``
>
> `The flat-then-multiply ordering is load-bearing: a planet that grants +500 shield HP and a fleet with a 2× shield aura combine to +1000 HP, not +500 HP + separate-scaling. This ordering is locked by \`tests/unit/simulation/entities/test_ship_shield_bonus_add.py\`. New ship-level additive stat_keys must follow the same pattern.`

**Rationale:** This is the least-discoverable load-bearing decision from PROJ-271 Track B. Having it called out in the ship-stats section prevents future refactors from silently breaking it.

---

## Out-of-scope observations

- `docs/01_ARCHITECTURE.md:162` still has the parenthetical `(BattleFactories deleted in PROJ-270 Phase 8.2)` — this is now trivia; once the deletion is more than a month old consider stripping the marker to reduce noise.
- `docs/systems/combat_simulation.md:249-251` still calls the legacy `ShipInstance.component_damage` coexistence a "PROJ-269 transition" — if consolidation is no longer on the roadmap, this is misleading; if it is, it should have a tracking ticket reference.
- `docs/systems/combat_simulation.md:341` mentions "~44 unit tests that predate the spec-in contract" use `BattleScreen.start(team0, team1)` with a test-only shim. If those tests have since been migrated or deleted, this paragraph is stale. (Not verified in this pass — out of scope.)
- The `run_headless` term appears nowhere in `docs/` (outside `_ignore/`), which means the earlier cleanup was thorough — no finding needed.
- `game/simulation/battle_runner.py:10` and `game/simulation/battle_config.py:3` each mention `BattleMode` in code comments as historical context. Not a doc issue, but tidying those comments would complete the System Migration Policy sweep.
