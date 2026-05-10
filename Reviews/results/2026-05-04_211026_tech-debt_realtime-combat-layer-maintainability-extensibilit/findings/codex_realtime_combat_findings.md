# Codex Findings: Realtime Combat Layer Technical Debt

## Summary

This file contains the raw ranked findings that support `../report.md`.

### HIGH: Legacy battle path still competes with BattleSpec

- **Files:** `game/simulation/services/battle_service.py:40`, `game/simulation/battle_controller.py:103`, `game/simulation/battle_controller.py:204`, `game/simulation/battle_controller.py:612`
- **Issue:** A legacy two-team service/controller path still exists beside the modern `BattleSpec` / `run_battle` path.
- **Risk:** New combat behavior can diverge between headless, visual, test, and restored battle flows.
- **Recommendation:** Add parity tests, then make all battle creation pass through `BattleSpec`.

### HIGH: Aura providers are not tied to component identity

- **File:** `game/simulation/combat/fleet_aura_manager.py:207`
- **Issue:** Aura providers track ability class and value, but not the concrete component or ability instance.
- **Risk:** Disabling one of multiple same-class aura components can leave stale provider values active.
- **Recommendation:** Track provider component identity and recompute from live ability instances.

### MEDIUM: Combat stat effects are spread across string registries

- **Files:** `game/simulation/combat/ability_stat_registry.py:53`, `game/simulation/components/abilities/base.py:258`, `game/simulation/entities/ship_stats.py:440`
- **Issue:** External stat effects depend on hardcoded string keys, known-key lists, suffix semantics, and scattered consumers.
- **Risk:** New abilities can appear registered but have no combat effect.
- **Recommendation:** Replace string conventions with typed stat contribution objects and validation.

### MEDIUM: Weapon behavior is hardcoded in several systems

- **Files:** `game/simulation/combat/weapon_firing_system.py:198`, `game/simulation/combat/targeting_system.py:123`, `game/engine/collision.py:68`, `game/simulation/projectile_manager.py:130`
- **Issue:** Beam, projectile, seeker, and PDC behavior are split across multiple concrete type checks.
- **Risk:** New weapon families require multi-file edits and can drift between targeting and hit resolution.
- **Recommendation:** Introduce typed attack contracts and a weapon family registry/protocol.

### MEDIUM: Ship stat calculation is a monolithic special-case engine

- **File:** `game/simulation/entities/ship_stats.py:111`
- **Issue:** `ShipStatsCalculator` owns many stat domains and hardcoded ability-name checks.
- **Risk:** New stats and abilities require editing a large, fragile production file.
- **Recommendation:** Split into tested stat-domain contributors.

### MEDIUM: Ability parsing bypasses the documented template hook

- **Files:** `game/simulation/components/abilities/planetary.py:35`, `game/simulation/components/abilities/base.py:98`
- **Issue:** Several ability classes parse fields in `__init__` rather than `_parse_attrs`.
- **Risk:** Formula sync and data reload behavior can become stale.
- **Recommendation:** Move parsing to `_parse_attrs` and add sync tests.

### MEDIUM: Battle runner silently accepts component drift

- **File:** `game/simulation/battle_runner.py:580`
- **Issue:** Spec components with no materialized ship match are ignored.
- **Risk:** Invalid specs and stale designs can enter combat without a clear failure.
- **Recommendation:** Validate component mapping before engine start and raise a domain error on drift.

### MEDIUM: BattleEngine owns too much construction policy

- **File:** `game/simulation/systems/battle_engine.py:604`
- **Issue:** The engine constructs launched fighter ships directly inside attack processing.
- **Risk:** Launched entities can diverge from normal design/materialization behavior.
- **Recommendation:** Extract launch materialization to an injected service or factory.

### HIGH: AI PDC capability cache checks a non-existent ability

- **File:** `game/ai/controller.py:184`
- **Issue:** AI capability cache checks `PDCAbility`, while PDC is tag-based through `has_pdc_ability()`.
- **Risk:** AI cached capability data can lie about PDC weapons.
- **Recommendation:** Use the tag-based helper and test the cache.

### MEDIUM: Battle DTOs still use phase-era object contracts

- **Files:** `game/simulation/battle_spec.py:182`, `game/simulation/battle_outcome.py:185`, `game/simulation/battle_runner.py:386`
- **Issue:** Major battle spec and outcome fields remain typed as `object`.
- **Risk:** Invalid integration inputs are caught late, if at all.
- **Recommendation:** Replace `object` with concrete dataclasses or protocols and validate before engine construction.
