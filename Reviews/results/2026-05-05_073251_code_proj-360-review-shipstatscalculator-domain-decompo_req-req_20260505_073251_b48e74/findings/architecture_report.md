# Architecture Review: PROJ-360 ShipStatsCalculator Domain Decomposition

**Date:** 2026-05-05
**Reviewer:** Architecture agent
**Scope:** `game/simulation/entities/stat_contributors/`, `ship_stats.py`, PROJ-359 contract, registry design (Pattern #35)

---

## 1. Layer Boundaries

All contributors and the coordinator import exclusively from `game/core/`, `game/simulation/` internals, and stdlib. No imports from `game/strategy/`, `game/ai/`, `game/ui/`, or `game/engine/` were found. The decomposition preserves the Simulation layer's dependency contract (`docs/01_ARCHITECTURE.md` §Dependency Rules).

**Verdict: PASS.** No layer boundary violations.

---

## 2. Cross-Contributor Coupling

### [FINDING-A1]: MAJ Module-level mutable registry state without root conftest reset

**File:** `game/simulation/entities/stat_contributors/registry.py:57`, `registry.py:146`

**Description:** Both `CREW_PRIORITY_REGISTRY` (list of `CrewPriorityEntry`) and `STAT_CONTRIBUTOR_REGISTRY` (list of `StatContributorEntry`) are module-level mutable lists. The root `conftest.py::reset_game_state` fixture (autouse, function-scoped) does **not** reset either registry to its default state. Individual test files (`test_stat_contributor_extension.py`, `test_registry.py`) provide their own `cleanup`/`clean_extension_registry` fixtures that unregister entries at teardown, but if a test crashes after registration and before unregistration, the registries remain polluted for the rest of the pytest shard. Pattern #35 docstring claims "Tests clean up via a fixture that tracks registrations and unregisters them at teardown — so a test cannot leak into another" — but the `finally:` block of the cleanup fixture only runs on normal yield return, not on fixture setup failure during registration.

**Remediation:** Add a pre-test reset for both registries in `reset_game_state` (or a dedicated autouse fixture in `tests/unit/simulation/entities/stat_contributors/conftest.py`). Reset `CREW_PRIORITY_REGISTRY` to the 3-entry default list, and clear `STAT_CONTRIBUTOR_REGISTRY` to `[]`. Use the `request.addfinalizer` pattern rather than a yield fixture to guarantee cleanup even on early failure.

---

### [FINDING-A2]: MIN Registered contributors receive `(ship, comp)` but not `acc` dict

**File:** `game/simulation/entities/stat_contributors/registry.py:181-193`, `game/simulation/entities/ship_stats.py:244-267`

**Description:** Built-in contributors (`movement`, `defense`) write through the shared `acc` dict; `_apply_aggregated_stats` then atomically applies `acc` to `ship` after the component loop. Registered contributors receive only `(ship, comp)` — they cannot read or write the `acc` dict. This means a registered contributor must write directly to `ship` attributes (like `launch` and `command` do), but if it needs to read accumulated stats from previously-processed components, it must either read from `ship` (where not all stats are available until after `_apply_aggregated_stats`) or from the inaccessible `acc`. This is not a current bug (no in-tree registered contributors), but it is a latent API asymmetry.

**Remediation:** Either document that registered contributors only have access to `ship` and per-component state (current behavior), or expose `acc` as a third parameter. The safe choice is documentation — adding `acc` exposes what is currently an internal accumulator.

---

### [FINDING-A3]: NIT Contributor invocation order difference for `weapons.py` vs. other contributors

**File:** `game/simulation/entities/ship_stats.py:258` (movement/defense/launch/command in Phase 3), `ship_stats.py:432` (weapons in Phase 5)

**Description:** The five bundled contributor modules have asymmetric invocation points:
- `movement.aggregate_propulsion`, `defense.aggregate_defense`, `launch.aggregate_hangar`, `command.track_multiplex` — called from `_phase_stats_aggregation` (Phase 3, per-component loop)
- `weapons.aggregate_targeting_scores` — called from `_phase_sensor_defense_scores` (Phase 5, whole-ship pass)

This split faithfully mirrors the legacy calculator's phase ordering, so it is not a regression. But a reader of the `stat_contributors/` package might expect all five to follow the same invocation contract. The `weapons.py` function signature (`ship, component_pool` — takes the whole pool) differs from the others (`comp, acc` or `ship, comp, acc` — per-component).

**Remediation:** Add a package-level comment in `stat_contributors/__init__.py` noting that `weapons` is a Phase-5 contributor (whole-pool) while the others are Phase-3 contributors (per-component), and that this is intentional per the phase-ordered calculation.

---

### [FINDING-A4]: NIT Built-in contributor mutation scope is inconsistent across modules

**File:** `movement.py:25-57`, `defense.py:31-58`, `launch.py:22-45`, `command.py:43-51`

**Description:** The built-in contributors use two different mutation patterns:
- `movement` writes exclusively to `acc` (dict key writes)
- `defense` writes to both `acc` (shields) and `ship` (armor HP pool directly on `ship.layers[ARMOR].max_hp_pool`)
- `launch` writes exclusively to `ship` attributes (`fighter_capacity`, `fighters_per_wave`, etc.)
- `command.track_multiplex` writes exclusively to `ship.max_targets`

This faithfully mirrors the legacy code. No contributor reads state written by another in the same pass, so there is no ordering dependency bug. But the mixed mutation surfaces mean that a contributor that looks like it only touches `acc` (movement) could mislead a reader into thinking all contributors follow the same pattern.

**Remediation:** Low priority — this is documented in each module's docstring. Consider a follow-up PROJ to unify on either `acc`-only or `ship`-only, but golden-snapshot constraints make this risky.

---

## 3. PROJ-359 AttackRequest Contract

### [FINDING-B1]: PASS The rationale for not adopting the typed AttackRequest contract is sound

**File:** `game/simulation/entities/stat_contributors/weapons.py:17-23`, `game/simulation/combat/attack_contract.py:63-81`

**Description:** The `weapons.py` docstring claims the PROJ-359 `AttackRequest` typed contract covers per-shot resolution, not stat aggregation. This is correct:
- `AttackRequest` fields (`source`, `component`, `weapon_ability`, `target`, `aim_pos`, `aim_vec`, `family`) describe a single weapon firing event — an *input* to a family handler.
- `aggregate_targeting_scores` computes ship-wide totals (`ToHitDefenseModifier`, `ToHitAttackModifier`) across all components — these are *pre-fire* stat aggregates.
- `AttackRequest` carries no field for `ToHitDefenseModifier` or `ToHitAttackModifier` totals. It carries a single `component` and `weapon_ability`, not a component pool.

ECM/sensor scores are inputs to hit-probability calculation at fire time, not outputs of resolution. The separation between the `attack_contract` (per-shot resolution input/output) and the stat contributor (per-ship aggregate) is architecturally correct.

**Verdict: PASS.** The rationale is sound. No action needed.

---

## 4. Registry Design (Pattern #35)

### [FINDING-C1]: MAJ STAT_CONTRIBUTOR_REGISTRY is a list, not a dict — deviates from other registry patterns

**File:** `game/simulation/entities/stat_contributors/registry.py:146`, `registry.py:181-193`

**Description:** `STAT_CONTRIBUTOR_REGISTRY` uses a list of `StatContributorEntry` with O(n) iteration per component (`apply_registered_contributors` walks all entries for every component). By contrast:
- `CommandHandlerRegistry` uses `Dict[str, ICommandHandler]` (O(1) by command name)
- `ABILITY_STAT_REGISTRY` uses `Dict[str, AbilityStatMapping]` (O(1) by ability class name)
- `WEAPON_REGISTRY` uses dict keyed by `WeaponFamily` (O(1))
- `TickPhaseRegistry` uses a sorted list (fixed, small N=5)

The list design is justified because multiple contributors can be registered for the same ability name (disambiguated by `domain`) — a dict with ability_name as key would lose multi-contributor support. However, the iteration approach means `apply_registered_contributors` is called for every component and walks every entry, yielding O(components × entries) behavior. With a small number of contributors this is negligible, but the shape should be explicitly called out.

**Remediation:** Document the deliberate O(n*m) trade-off in the module docstring and note that this is acceptable because contributor count is expected to stay small (single digits). Alternatively, restructure as `Dict[str, List[StatContributorEntry]]` for O(1) ability-name lookup with multi-contributor support.

---

### [FINDING-C2]: PASS Separation from ABILITY_STAT_REGISTRY is justified

**File:** `game/simulation/entities/stat_contributors/registry.py:10-14`, `game/simulation/combat/ability_stat_registry.py:56-84`

**Description:** The registry module's docstring explicitly justifies separation from `ABILITY_STAT_REGISTRY`:
- `ABILITY_STAT_REGISTRY`: shapes the modifier-emission pipeline (spec compilers → `ModifierEntry` → `FleetAuraManager` → `external_stats`). Produces `ModifierEntry` objects consumed outside the calculator.
- `STAT_CONTRIBUTOR_REGISTRY`: shapes per-component stat aggregation (calculator → contributor callables → ship mutation). Produces direct `ship` mutations during `calculate()`.

These have different consumers, different data types, and different lifecycles. Mixing them would couple the modifier-compilation layer (spec compilers in UI/Strategy) with the stat-aggregation layer (ship stats calculator), violating both contracts.

**Verdict: PASS.** Separation is architecturally sound.

---

### [FINDING-C3]: NIT Mutable default list with no `reset_all()` helper

**File:** `game/simulation/entities/stat_contributors/registry.py:57`, `registry.py:146`

**Description:** Both registries are module-level mutable lists initialized at import time. The `register_*` functions append and `unregister_*` functions filter-reassign (via `global`). There is no `reset_crew_priority_registry()` or `reset_stat_contributor_registry()` function that restores defaults. This makes it impossible for non-test code to programmatically return the registry to its initial state without knowing the default entries — and in the case of `CREW_PRIORITY_REGISTRY`, the defaults are the 3 built-in priority entries (Command=0, Movement=1, Weapons=2).

**Remediation:** Add `reset_crew_priority_registry()` and `reset_stat_contributor_registry()` helpers. The `reset_game_state` fixture should call them to guarantee clean state. Store the default list as a module-level frozen copy for the reset to reference.

---

## 5. Two-Phase Ability Aggregation

### [FINDING-D1]: PASS All aggregation correctly routes through shared aggregator

**File:** `game/simulation/entities/ship_stats.py:489-491`, `game/simulation/entities/stat_contributors/weapons.py:47-53`, `defense.py:74-76`

**Description:** The `ShipStatsCalculator.calculate_ability_totals()` delegates to `calculate_ability_totals` from `ability_aggregator.py`. The `weapons.py` and `defense.py` contributors use `get_ability_total` from the same module. Where per-component raw values are needed (thrust, shield capacity, crew) the contributors iterate ability instances directly — these are NOT stacking-eligible values and should not go through the two-phase aggregator. No contributor re-implements the MAX-then-SUM aggregation logic from `_aggregate_ability_groups`.

**Verdict: PASS.** Aggregation contracts are correctly routed. No re-implementation detected.

---

## 6. External-Stats Bridge (Pattern #24)

### [FINDING-E1]: NIT Comment about reverted `capacity_mult` read is ambiguous

**File:** `game/simulation/entities/ship_stats.py:342-347`

**Description:** The code reads:
```python
# PROJ-272 Phase 6: reverted PROJ-271 Phase 12.1's
# `capacity_mult` read. No current aura populates
# `capacity_mult` — reading it from external_stats was a
# latent double-multiply if any future aura would populate it.
shield_cap_mult = external_stats.get("shield_capacity_mult", 1.0)
```

The comment says "reverted the `capacity_mult` read" but the code still reads `shield_capacity_mult`. The intended meaning is: PROJ-271 Phase 12.1 read the generic `capacity_mult` key (no `shield_` prefix). PROJ-272 Phase 6 reverted that — and now reads the shield-specific `shield_capacity_mult` key instead. The generic `capacity_mult` (used by `SimpleMultiplierAbility` subclasses for other domains like cargo) should NOT apply to shield bonuses — only `shield_capacity_mult` (emitted by `ShieldModifier` via `ABILITY_STAT_REGISTRY`) should. The current behavior (read `shield_capacity_mult` with default 1.0) is correct.

**Remediation:** Clarify the comment to say: "PROJ-272 Phase 6: replaced PROJ-271 Phase 12.1's generic `capacity_mult` read with the shield-specific `shield_capacity_mult` key." No code change needed.

---

### [FINDING-E2]: NIT isinstance(dict) guard skips legit non-dict external_stats

**File:** `game/simulation/entities/ship_stats.py:338-347`

**Description:** The `isinstance(external_stats, dict)` guard is there because "test Mocks often have external_stats as a bare MagicMock, not a real dict." This is a test-accommodating guard in production code. If a future implementation populates `external_stats` as a non-dict object (e.g., a read-only mapping proxy), the guard would silently skip it. The comment acknowledges this scope.

**Remediation:** Consider replacing the `isinstance` guard with a structural check (`hasattr(external_stats, "get")`) so any mapping-like object passes, or move the mock accommodation to the test layer (ensure test mocks use a real `dict`). Low priority.

---

## Summary

| Severity | Count | Findings |
|----------|-------|----------|
| CRIT | 0 | |
| MAJ | 2 | A1 (registry no root-conftest reset), C1 (list-based registry) |
| MIN | 1 | A2 (contributors can't read acc) |
| NIT | 5 | A3 (asymmetric invocation), A4 (mixed mutation scope), C3 (no reset_all()), E1 (ambiguous comment), E2 (isinstance guard) |
| PASS | 4 | Layer boundaries, AttackRequest rationale, ABILITY_STAT_REGISTRY separation, Two-phase aggregation routing |

**Overall assessment:** The decomposition is architecturally sound. The stat_contributors package cleanly separates per-domain logic, preserves layer boundaries, and correctly routes through the existing two-phase ability aggregator and external-stats bridge. The main risks are (1) test isolation for the new mutable module-level registries and (2) the list-based `STAT_CONTRIBUTOR_REGISTRY` deviating from the dict-based pattern used by other registries in the codebase. Both are addressable without structural changes.
