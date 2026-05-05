# Realtime Combat Layer Technical Debt Review

## Metadata
- **Date:** 2026-05-04
- **Type:** Technical Debt Review
- **Status:** Complete
- **Reviewer:** Codex
- **User request:** Identify the top ten realtime combat layer issues for technical debt, maintainability, and extensibility.

## Executive Summary

The realtime combat layer is functional, but it is carrying several large architectural transitions at once. The most important pattern is split ownership: combat startup, combat effects, weapon execution, stat aggregation, AI capability discovery, and battle result extraction each have more than one partial source of truth.

The highest-risk issues are:

1. Legacy battle startup paths still compete with the modern `BattleSpec` / `run_battle` path.
2. Fleet aura providers are not tied to concrete component identity and can leave stale aura values active.
3. Combat stat effects are routed through multiple string registries and suffix conventions.
4. Weapon behavior is hardcoded across firing, targeting, collision, and projectile code.

The recommended remediation is not a broad rewrite. The safer path is a TDD project that first adds characterization tests for the current behavior, then consolidates entry points and typed extension contracts one subsystem at a time.

## Scope

Reviewed areas:

- `game/simulation/`
- `game/simulation/combat/`
- `game/simulation/systems/battle_engine.py`
- `game/simulation/battle_runner.py`
- `game/engine/`
- `game/ai/`
- `game/strategy/combat/`
- Combat, ability, modifier, simulation testing, architecture, pattern, and convention docs.

Excluded:

- Generated and archived material.
- `docs/_ignore/`.
- Product code changes.

## Method

Context read:

- `AGENTS.md`
- `.agents/CODEX.md`
- `docs/README.md`
- `docs/01_ARCHITECTURE.md`
- `docs/02_PATTERNS.md`
- `docs/03_CONVENTIONS.md`
- `docs/systems/combat_simulation.md`
- `docs/systems/ai_system.md`
- `docs/guides/component_system.md`
- `docs/guides/modifier_system.md`
- `docs/guides/adding_abilities.md`
- `docs/guides/simulation_testing.md`

Static analysis:

- `python -m radon cc game/simulation game/ai game/engine game/strategy/combat -s -n C`
- `python -m radon mi game/simulation game/ai game/engine game/strategy/combat -s`
- `python -m vulture game/simulation game/ai game/engine game/strategy/combat --min-confidence 100`

Notes:

- `rg` was unavailable in this checkout due to access denial, so PowerShell file search was used.
- No tests were run because this was a review-only task.

## Ranking Criteria

Findings were ranked by:

- Risk of divergent realtime combat behavior.
- Number of files a future feature must modify.
- Likelihood of silent failure.
- Conflict with documented architecture and conventions.
- Difficulty of testing the behavior in isolation.

## Top Ten Findings

### 1. P1: Legacy battle path still competes with `BattleSpec`

**Primary files:**

- `game/simulation/services/battle_service.py:40`
- `game/simulation/battle_controller.py:103`
- `game/simulation/battle_controller.py:204`
- `game/simulation/battle_controller.py:612`

**Evidence:**

`BattleSpec` and `run_battle(spec)` are documented as the sanctioned headless path, and `BattleController.start_from_spec` is the newer visual path. However, `BattleService` still owns direct two-team state and startup, while `BattleController.start()` and `load_state()` still route through the older service path.

**Why it matters:**

This forces new combat features to ask whether they belong in the spec runner, the visual controller, the old service, or all of them. Boundary handling, retreat behavior, modifier stacks, ownership effects, and telemetry can diverge depending on which path created the battle.

**Recommended remediation:**

- Add characterization tests that compare visual and headless startup from equivalent battle specs.
- Make `BattleController` a thin adapter over `BattleSpec` startup.
- Remove or isolate direct `BattleService.start_battle()` use after parity is proven.
- Treat restore/load behavior as current-format-only, consistent with the no save migration rule.

**Suggested tests:**

- Visual controller starts from a spec and preserves boundary, retreat, modifier stack, and seed.
- Legacy direct service startup is unused or delegates to the spec path.
- Restored current-format battle state does not bypass spec validation.

### 2. P1: Fleet aura providers are not tied to component identity

**Primary file:** `game/simulation/combat/fleet_aura_manager.py:207`

**Evidence:**

`AuraProvider` records the provider ship, ability class name, value, stack group, and scope. During recalculation, the manager scans the provider ship for any live component with the same ability class and non-self scope. It does not track the original component or ability instance.

**Why it matters:**

If a ship has multiple same-class aura components, disabling one component can leave its provider record active as long as another same-class aura remains operational. That is both a correctness bug and a symptom of weak provider identity.

**Recommended remediation:**

- Store component identity and ability identity, not only ability class.
- Recompute provider values from live ability instances during recalculation.
- Make stale provider removal explicit and testable.
- Keep stacking behavior in one place after identity is fixed.

**Suggested tests:**

- Two same-class aura providers with different values on one ship.
- Disable one source component and verify only its value is removed.
- Disable the provider ship and verify all provider entries are removed.

### 3. P2: Combat stat effects are spread across string registries

**Primary files:**

- `game/simulation/combat/ability_stat_registry.py:53`
- `game/simulation/components/abilities/base.py:258`
- `game/simulation/entities/ship_stats.py:440`

**Evidence:**

Combat stat effects require coordination between `ABILITY_STAT_REGISTRY`, `KNOWN_EXTERNAL_STAT_KEYS`, `ship.external_stats`, suffix conventions such as `_mult` and `_add`, `Ability.get_effective_stat()`, `ShipStatsCalculator`, and direct fleet bonus fields.

**Why it matters:**

Adding a new combat-affecting ability is not a local operation. A new stat key can be accepted by one layer, displayed by another, and ignored by the actual stat reader. That creates silent non-effects and makes feature work dependent on tribal knowledge.

**Recommended remediation:**

- Introduce typed combat stat contribution objects with merge policy, target stat, and consumer contract.
- Replace suffix-derived semantics with explicit contribution metadata.
- Fail validation for registered combat stat keys that have no consumer.
- Keep fleet aura, planetary effects, and direct ship stats on the same contribution path.

**Suggested tests:**

- Unknown combat stat key fails validation instead of silently doing nothing.
- A fake test ability can contribute to a stat without editing unrelated stat readers.
- Multiplicative and additive contributions compose in deterministic order.

### 4. P2: Weapon behavior is hardcoded in several systems

**Primary files:**

- `game/simulation/combat/weapon_firing_system.py:198`
- `game/simulation/combat/targeting_system.py:123`
- `game/engine/collision.py:68`
- `game/simulation/projectile_manager.py:130`

**Evidence:**

Weapon firing dispatches by concrete ability classes such as beam, projectile, and seeker. Targeting separately knows PDC and seeker rules. Collision separately processes beam attacks from dictionaries. Projectile hit application has its own damage path.

**Why it matters:**

Every new weapon family requires a coordinated edit across firing, targeting, collision, projectile behavior, telemetry, and outcome handling. The lack of a typed attack contract also lets simulation semantics leak into the low-level engine through dictionaries and ability-name lookups.

**Recommended remediation:**

- Introduce a typed `AttackRequest` / `AttackResolution` model.
- Define a weapon execution protocol or registry per weapon family.
- Move beam, projectile, seeker, PDC, and future families behind that contract.
- Keep targeting constraints and hit application in the same registered weapon behavior where possible.

**Suggested tests:**

- A fake registered weapon family can fire without editing the central firing system.
- Beam and projectile damage paths produce equivalent damage event contracts.
- PDC target restrictions are validated through weapon metadata.

### 5. P2: Ship stat calculation is a monolithic special-case engine

**Primary file:** `game/simulation/entities/ship_stats.py:111`

**Evidence:**

`ShipStatsCalculator.calculate()` runs many mutable phases and hardcodes ability names for movement, shields, regeneration, launch capacity, multiplex tracking, armor, command priority, and engine priority. The file is also above the production 500 LOC convention.

**Why it matters:**

The calculator is a single source of truth, but it is too broad. New stats and ability classes must modify a large file that already owns multiple unrelated concerns. This increases regression risk and discourages narrow extension points.

**Recommended remediation:**

- Split calculation into stat-domain contributors, such as movement, defense, weapons, command, and launch capacity.
- Convert hardcoded ability-name checks into registered stat contributors.
- Preserve the current output contract with characterization tests before splitting.

**Suggested tests:**

- Golden stat output for representative ship designs.
- Domain-level tests for movement, shields, armor, command, and launch capacity.
- Regression test that a contributor can be added without editing unrelated domains.

### 6. P2: Ability parsing bypasses the documented template hook

**Primary files:**

- `game/simulation/components/abilities/planetary.py:35`
- `game/simulation/components/abilities/base.py:98`

**Evidence:**

The ability guide says subclasses should parse via `_parse_attrs`, and the base class calls that hook from sync behavior. Several combat-relevant ability classes parse fields directly in `__init__` instead. `planetary.py` is also a 900+ LOC file containing many unrelated ability classes.

**Why it matters:**

If formula data or ability data is synced after construction, direct `__init__` parsing can become stale unless every subclass mirrors the parsing in `sync_data()`. This is easy to miss when adding new abilities.

**Recommended remediation:**

- Move combat-relevant ability parsing into `_parse_attrs`.
- Add sync tests for formula-backed ability values.
- Split large ability modules by domain once tests lock behavior.

**Suggested tests:**

- Updating ability data and calling sync updates parsed combat fields.
- Planetary shield, damage modifier, and thrust modifier parsing use the same hook path.
- A new ability subclass only needs `_parse_attrs` for construction and sync.

### 7. P2: Battle runner silently accepts component drift

**Primary file:** `game/simulation/battle_runner.py:580`

**Evidence:**

`_apply_spec_components_to_ship()` explicitly ignores components from the battle spec that do not map to the materialized ship. The docstring calls this design drift but treats it as acceptable at runtime.

**Why it matters:**

The battle runner is the point where strategy data, designs, and realtime combat meet. Silent drift at this boundary hides invalid specs, stale designs, and materialization bugs until later combat behavior looks wrong.

**Recommended remediation:**

- Validate all spec component entries before battle start.
- Raise a domain-specific validation error with ship id, component id, and design id.
- Allow explicit test-only relaxed behavior only if a test fixture needs it.

**Suggested tests:**

- Missing spec component fails before engine start.
- Component HP maps to the intended materialized component.
- Valid specs remain accepted with unchanged combat results.

### 8. P2: `BattleEngine` still owns too much construction policy

**Primary file:** `game/simulation/systems/battle_engine.py:604`

**Evidence:**

`BattleEngine` constructs many collaborators directly and also constructs launched fighter ships in `_process_attacks()`. That launch path creates a `Ship` from class/theme data inside the engine rather than using the same battle materialization path as other combatants.

**Why it matters:**

The engine should be a tick coordinator, not the owner of design/materialization policy. Direct ship construction risks launched entities diverging from normal design stats, component initialization, telemetry, and future spec-driven behavior.

**Recommended remediation:**

- Extract fighter launch into a launch/materialization service.
- Inject factories for combat entities and tick collaborators.
- Keep `BattleEngine` focused on ticking systems and enforcing battle state.

**Suggested tests:**

- Launched fighters receive expected design stats and components.
- Launch behavior uses the same materialization contract as initial combatants.
- Engine update tests can run with fake factories.

### 9. P1: AI PDC capability cache checks a non-existent ability

**Primary file:** `game/ai/controller.py:184`

**Evidence:**

The AI capability cache searches for `PDCAbility`, but PDC appears to be tag-based via `has_pdc_ability()`. Source search found `PDCAbility` only in this controller path, while component data uses a `pdc` tag.

**Why it matters:**

This is a concrete drift bug in AI capability discovery. Even if current targeting happens to use other code paths, the cache is now misleading and future targeting rules may build on false capability data.

**Recommended remediation:**

- Replace the `has_ability("PDCAbility")` check with `has_pdc_ability()`.
- Add capability cache tests for tagged PDC weapons.
- Consider injecting behavior and policy registries instead of hardcoding them in the controller.

**Suggested tests:**

- A weapon component with the `pdc` tag appears in cached PDC weapons.
- A non-PDC weapon with normal weapon ability does not appear in cached PDC weapons.
- PDC targeting rules consume the cache consistently.

### 10. P2: Battle DTOs still use phase-era `object` contracts

**Primary files:**

- `game/simulation/battle_spec.py:182`
- `game/simulation/battle_outcome.py:185`
- `game/simulation/battle_runner.py:386`

**Evidence:**

`BattleSpec` keeps major fields typed as `object`, including boundary, end condition, modifier stack, and telemetry level. `BattleOutcome` also uses loosened types. The runner contains tolerance for placeholder objects from earlier phases.

**Why it matters:**

Weak contracts shift integration errors from construction time to runtime. They also make tests less precise because almost anything can be passed until a later path tries to use a method or attribute.

**Recommended remediation:**

- Replace `object` fields with concrete dataclasses or protocols.
- Add battle spec validation before engine construction.
- Remove placeholder tolerance after tests and callers use typed values.

**Suggested tests:**

- Invalid boundary, telemetry level, or modifier stack fails validation.
- Valid typed battle specs run headless and visual paths.
- Outcome extraction produces stable typed records for retreated, destroyed, and surviving ships.

## Static Analysis Notes

Radon complexity hotspots:

- `game/simulation/combat/fleet_aura_manager.py` - `FleetAuraManager._recalculate` D(26)
- `game/simulation/combat/formation.py` - `_compute_local_positions` D(24)
- `game/simulation/entities/combat_endurance.py` - `calculate_combat_endurance` D(21)
- `game/simulation/entities/ability_aggregator.py` - `calculate_ability_totals` C(20)
- `game/simulation/entities/ship_design_stats.py` - `calculate_design_stats` C(20)
- `game/simulation/components/abilities/base.py` - `Ability.get_effective_stat` C(17)
- `game/simulation/combat/telemetry.py` - `HitLogRecorder._on_hit_event` C(17)
- `game/engine/collision.py` - `CollisionSystem.process_beam_attack` C(15)
- `game/strategy/combat/spec_compiler.py` - `build_strategy_battle_spec` C(13)

Large production files over the 500 LOC convention:

- `game/simulation/components/abilities/planetary.py` - 913 LOC
- `game/simulation/battle_controller.py` - 828 LOC
- `game/simulation/battle_state.py` - 805 LOC
- `game/simulation/systems/battle_engine.py` - 768 LOC
- `game/simulation/battle_runner.py` - 676 LOC
- `game/simulation/entities/ship_stats.py` - 643 LOC
- `game/simulation/entities/ship.py` - 607 LOC
- `game/simulation/components/abilities/base.py` - 535 LOC
- `game/simulation/services/vehicle_design_service.py` - 516 LOC

Vulture at 100 percent confidence found only unused variables in `BattleLogger.__exit__` at `game/simulation/systems/battle_engine.py:98`. That is cleanup-level, not a top-ten realtime combat architecture issue.

## Recommended Remediation Plan

### Phase 0: Characterization tests

Add tests before product changes:

- Same-class multi-provider aura disable behavior.
- Tagged PDC capability cache behavior.
- BattleSpec startup parity between headless and visual paths.
- Component drift fails validation.
- Representative ship stat golden outputs.

### Phase 1: Consolidate combat startup

- Make `BattleSpec` the only battle creation contract.
- Retire direct two-team `BattleService` startup or make it delegate to spec construction.
- Keep current-format restore/load behavior only if it passes through the same validation.

### Phase 2: Introduce typed combat extension contracts

- Typed stat contribution model.
- Typed attack request/resolution model.
- Weapon family registry or protocol.
- Spec validation for all typed battle inputs.

### Phase 3: Split broad calculators and coordinators

- Decompose `ShipStatsCalculator` by stat domain.
- Extract launch/materialization from `BattleEngine`.
- Move ability parsing to the documented `_parse_attrs` path.
- Split oversized ability modules by domain after tests are in place.

### Phase 4: Delete obsolete compatibility and drift tolerance

- Remove placeholder-object tolerance once typed specs are enforced.
- Remove silent component ignore behavior.
- Delete or quarantine legacy startup paths after parity is proven.
- Update docs in the same change as behavior changes.

## Open Questions

- Should mid-battle load remain a supported current-format feature, or should it be treated as test-only scaffolding?
- Are more than two teams planned for realtime combat?
- Should launched fighters be fully design-backed entities or a lighter combat-only entity type?
- Should unknown combat stat keys fail at data validation time or at battle spec compilation time?

## Conclusion

The realtime combat layer does not need a rewrite, but it does need consolidation. The safest project shape is to start with characterization tests around aura identity, PDC capability detection, spec startup parity, and component drift. After those tests exist, the highest leverage change is making `BattleSpec` the single creation path and replacing string/dictionary extension points with typed stat and weapon contracts.
