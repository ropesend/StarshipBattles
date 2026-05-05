# Test Coverage Audit — Shard 16 Skeptical Verification

**Date:** 2026-05-04
**Phase:** 3 — Skeptical Verification
**Verification scope:** All 3 CRITICAL claims and 5 MAJOR claims from Phase 2 Discovery Report
**Methodology:** Read every cited production file (line ranges + context), searched for all candidate test files via glob and grep, traced imports, verified indirect coverage paths.

---

## Summary of Verification Results

| Original Severity | Claims | CONFIRMED | DOWNGRADED | OVERTURNED (→ VERIFIED) |
|--------------------|--------|-----------|------------|-------------------------|
| CRITICAL | 3 | 0 | 2 (→ MINOR) | 1 (fully tested) |
| MAJOR | 5 | 1 (partially) | 4 (→ MINOR) | 0 |

**Discovery Agent Errors:** 3 (2 CRITICAL claims had test files the agent missed; 1 MAJOR had tests the agent understated)

---

## CRITICAL Claims — Verification Results

### CRITICAL #1: `game/core/protocols/strategy_entities.py` (456 LOC)

**Discovery Agent Claim:** TIER_0_NO_TESTS — "Zero tests exist. No tests verify that concrete implementations satisfy the protocols." "No tests exercise the TypeGuard functions."

**Verification Result: DISPUTED — DOWNGRADE to MINOR**

**Evidence:** `tests/unit/core/test_protocols.py` (459 lines) imports and tests 8 of the 10 protocols and 7 of the 9 TypeGuard functions defined in this file:

Protocol compliance tests (all on real concrete instances):
- `test_fleet_satisfies_ifleet` — Fleet satisfies IFleet
- `test_planet_satisfies_iplanet` — Planet satisfies IPlanet
- `test_star_system_satisfies_istarsystem` — StarSystem satisfies IStarSystem
- `test_star_satisfies_istar` — Star satisfies IStar
- `test_warp_point_satisfies_iwarppoint` — WarpPoint satisfies IWarpPoint
- `test_sector_environment_satisfies_isectorenvironment` — SectorEnvironment satisfies ISectorEnvironment
- `test_star_satisfies_izoneoccupant` — Star satisfies IZoneOccupant (IZoneOccupant full test class, 5 tests)
- `test_planet_satisfies_izoneoccupant` — Planet satisfies IZoneOccupant
- `IAbilitySource` tested in 7 separate ability source test files (storm, fleet, facility, planet, star, warp_point, system_archetype — each calls `isinstance(src, IAbilitySource)` and `is_ability_source(src)`)

TypeGuard positive tests:
- `test_is_fleet_returns_true_for_fleet`
- `test_is_planet_returns_true_for_planet`
- `test_is_star_system_returns_true_for_system`
- `test_is_star_returns_true_for_star`
- `test_is_warp_point_returns_true_for_warppoint`
- `test_is_sector_environment_returns_true_for_sector`
- `test_is_zone_occupant` positive (2 tests: star + planet)

TypeGuard negative tests:
- 10 parametrized false-returns (is_fleet-str/int/dict, is_planet-str/none, is_star_system-str/none, is_star-str, is_warp_point-str, is_sector_environment-dict)
- `test_none_does_not_satisfy_any_protocol` — all 6 protocols vs None
- `test_typeguards_return_false_for_none` — all 7 guards vs None

**Actual untested gaps (MINOR):**
| Symbol | Why untested | Severity |
|--------|-------------|----------|
| `IOrderable` protocol compliance | Not tested with concrete instances (though `test_orders_window.py` uses minimal stand-in) | MINOR |
| `IStorm` protocol compliance | Not tested with concrete Storm instances | MINOR |
| `is_storm` TypeGuard | Only mock-patched in UI tests, never tested with real Storm instance | MINOR |
| `IAbilitySource` in this test file | Tested in 7 other test files — coverage exists but fragmented | ADVISORY |

**Discovery Agent Error:** The agent searched for `tests/unit/core/protocols/test_strategy_entities.py` (exact file name match) but the actual test file is `tests/unit/core/test_protocols.py`. The agent also failed to find the 7 ability source test files that exercise `IAbilitySource` / `is_ability_source`.

---

### CRITICAL #2: `game/strategy/services/ability_sources/storm.py` (77 LOC)

**Discovery Agent Claim:** TIER_0_NO_TESTS — "0 candidate test files. No tests for affects_hex with global-coordinate translation. No tests for affects_hex fallback path."

**Verification Result: DISPUTED — DOWNGRADE to MINOR**

**Evidence:** `tests/unit/strategy/services/ability_sources/test_storm.py` (106 lines) exists and comprehensively tests:

| Production symbol | Test coverage | Test name |
|-------------------|--------------|-----------|
| `source_kind` | ✓ | `test_source_kind_is_storm` |
| `source_label` | ✓ | `test_source_label_is_storm_name` |
| `source_id` | ✓ | `test_source_id_stable_and_prefixed` |
| `owner_id` | ✓ | `test_owner_id_is_none` |
| `get_abilities` (valid dict) | ✓ | `test_get_abilities_returns_storm_abilities_dict` |
| `get_abilities` (empty) | ✓ | `test_get_abilities_empty_when_storm_has_no_abilities` |
| `affects_hex` (unparented, true) | ✓ | `test_affects_hex_true_for_occupied_unparented_storm` |
| `affects_hex` (unparented, false) | ✓ | `test_affects_hex_false_outside_unparented_storm` |
| `affects_hex` (global translation) | ✓ | `test_affects_hex_translates_local_to_global_when_system_provided` |
| `get_activation_state` | ✓ | `test_get_activation_state_is_none` |
| `IAbilitySource` protocol | ✓ | `test_satisfies_iability_source_protocol` |

The test at line 72 `test_affects_hex_translates_local_to_global_when_system_provided` explicitly tests BOTH code paths: the global-frame translation path (lines 65-68 in production) AND the local-frame fallback when system is None (lines 58-64), matching the "BUG-119 regression" scenario.

**Actual untested gaps (MINOR):**
| Gap | Lines | Why untested |
|-----|-------|-------------|
| `affects_hex` AttributeError fallback | 62-63 | When `storm.occupied_hexes` raises AttributeError (not just missing), returns False. Trivial branch. |
| `affects_hex` TypeError catch in global path | 67-68 | When `sys_loc + storm_loc + off` raises TypeError. Edge case. |

---

### CRITICAL #3: `game/strategy/engine/handlers/build.py` (66 LOC)

**Discovery Agent Claim:** TIER_0_NO_TESTS — "0 candidate test files. No tests verify BUILD order insertion, path clearance, error paths, or delegation."

**Verification Result: OVERTURNED — VERIFIED (fully tested)**

**Evidence:** `tests/unit/strategy/engine/test_build_order_command_handler.py` (219 lines) tests ALL 4 claimed gaps:

| Discovery Agent Claim | Test covering it | Test name |
|----------------------|-----------------|-----------|
| "BUILD order insertion at position 0" | ✓ | `test_handler_inserts_at_position_0` (BUILD at index 0, MOVE at index 1) |
| "Path clearance on BUILD" | ✓ | `test_handler_clears_path` (path explicitly asserted `== []`) |
| "Error path when fleet_id not found" | ✓ | `test_handler_returns_error_if_fleet_not_found` (asserts "Fleet not found" error) |
| "Remove BUILD order correctly delegates" | ✓ | `test_handler_removes_build_orders` (asserts `remove_orders_by_type` called with `OrderType.BUILD`) |

Additional tests present:
- `test_handler_creates_build_order` — full create + path clear
- `test_handler_does_nothing_if_no_build_order` — idempotent remove
- `test_build_order_handler_registered` — handler dispatch registration
- `test_remove_build_order_handler_registered` — handler dispatch registration

The test imports `BuildOrderCommandHandler` and `RemoveBuildOrderCommandHandler` from `game.strategy.engine.command_handlers`. These are the SAME classes — `command_handlers` re-exports from `handlers/build.py`. The test exercises the exact production code.

**Discovery Agent Error:** The agent searched for filenames like `test_build.py` but the actual test file is named `test_build_order_command_handler.py`. This is a filename-pattern search failure.

---

## MAJOR Claims — Verification Results

### MAJOR #4: `game/strategy/combat/spec_compiler.py` (683 LOC)

**Discovery Agent Claim:** "3/10 symbols tested. Seven internal helpers untested. `_pick_formation_for_fleet` task_forces attribute check, `_ship_spec_from_instance` design_data branching, `_build_modifier_stack` PROJ-343 ownerful routing, `_team_spec_for_fleet_group` multi-fleet path are not explicitly tested."

**Verification Result: PARTIALLY CONFIRMED — RETAIN as MAJOR (with corrections)**

The discovery agent's count of "3/10 symbols tested" is misleading — the internal helpers are exercised through the public `build_strategy_battle_spec` entry point, tested across 3 test files totaling ~933 LOC:

**Verified TESTED (correcting Discovery Agent):**
| Claimed untested | Actual status | Evidence |
|-----------------|---------------|---------|
| `_team_spec_for_fleet_group` multi-fleet path | TESTED | `test_compiler_groups_multi_fleet_per_empire_into_one_team` (3 fleets, 2 owners, ship counts verified) |
| `_ship_spec_from_instance` component sorting | TESTED | `test_compiler_populates_ship_spec_components_from_instance` (damaged laser_cannon HP roundtrips, ComponentStateSpec verified) |
| `_build_modifier_stack` PROJ-343 ownerful routing | TESTED | `tests/integration/strategy/test_combat_owned_sector_effect_isolation.py` (4 tests with `empire_to_team_id` routing) |
| `_pick_formation_for_fleet` task_forces attribute | TESTED | `test_explicit_task_force_formation_overrides_default` (explicit TF formation overrides default) |
| `_hook` closure | TESTED | `test_three_team_post_battle_hook_routes_outcomes_to_each_team` (3-team outcome routing) |
| `_entries_from_sector_effects` | TESTED | `test_storm_entry_has_no_stack_group_per_d6` + integration tests |
| `_entries_from_fleet_combat_modifiers` | TESTED | 3 tests verifying shield_mult, damage_mult, flat_shield_bonus stack groups |
| N-fleet entry vectors | TESTED | 5 tests (3-team, ring layout, legacy 2-team, 1-fleet error, 9-fleet error) |
| Boundary resolution | TESTED | Tests for CircleBoundary and UnboundedRegion fallback |
| `max_ticks` kwarg | TESTED | 3 tests (Issue #8 truncated run) |

**Actually untested (MAJOR):**
| Gap | Lines | Why still untested |
|-----|-------|-------------------|
| `_ship_spec_from_instance` `design_data` fallback | 378 | When `hasattr(ship, "design_data")` is False or `design_data` is not a dict, `theme_id` falls back to "Federation". Not explicitly tested. |
| `_pick_formation_for_fleet` empty/missing task_forces | 366 | When `getattr(fleet, "task_forces", [])` returns empty list or None, falls back to `resolve_default_for_task_force`. The empty-list path is covered by default formation tests; the explicit-None/different-type path is untested. |
| `_team_spec_for_fleet_group` empty-fleet raise | 308-311 | `ValueError` raise when `owner_fleets` is empty. Not directly tested (the compiler catches this upstream at `num_teams < _MIN_TEAMS`). |
| `_build_modifier_stack` `environmental_effects is None` | 450 | When no environmental_effects, the global+per_team branch is skipped. Covered indirectly but the "no effects" path isn't explicitly asserted. |
| `_build_strategy_post_battle_hook` empires-by-team-id  | 271-276 | The `empires.get(team_id)` vs `empires.get(owner_id)` fallback logic — only tested with empty `empires={}`. |

**Assessment:** MAJOR is appropriate — the compiler has 683 LOC of high-risk logic. While the discovery agent understated coverage (many claimed untested paths ARE tested), genuine branch gaps remain in `design_data` fallback and post-battle-hook empire key resolution.

---

### MAJOR #5: `game/simulation/entities/ship_combat_engine.py` (252 LOC)

**Discovery Agent Claim:** "6/9 symbols tested. `select_target` and `calculate_firing_solution` delegation paths not explicitly unit-tested."

**Verification Result: DISPUTED — DOWNGRADE to MINOR**

**Evidence:** The `ShipCombatEngine` is a **delegation facade** — every method it exposes delegates to a subsystem that IS independently tested:

| ShipCombatEngine method | Delegates to | Subsystem test file | Tested? |
|------------------------|-------------|-------------------|---------|
| `select_target` (line 99-111) | `TargetingSystem.select_target` | `test_targeting_system.py` — 8 tests (valid enemy, excludes friendlies, excludes dead, closest, empty candidates, dying mid-list, all dead, None filtering) | ✓ |
| `calculate_firing_solution` (line 113-126) | `TargetingSystem.calculate_firing_solution` | `test_targeting_system.py` — 3 tests (beam, projectile, seeker) | ✓ |
| `solve_lead` (line 69-97) | `TargetingSystem.solve_lead` | Tested in `test_targeting_system.py` | ✓ |
| `fire_weapons` (line 132-144) | `WeaponFiringSystem.fire_weapons` | `test_weapon_firing_system.py` | ✓ |
| `take_damage` (line 150-174) | `DamageCalculator.apply_damage` | `test_damage_calculator.py` + `test_combat_ops.py` + `test_damage_reduction.py` | ✓ |
| `update_combat_cooldowns` (line 180-215) | In-engine | `test_cooldowns.py` — ~30 tests (shield regen, repair, cooldown interaction) | ✓ |
| `_apply_repair` (line 217-252) | In-engine | Exercised via `update_combat_cooldowns` in `test_cooldowns.py` | ✓ |

**Actual untested gap (MINOR):**
| Gap | Lines | Details |
|-----|-------|---------|
| `take_damage` → `SHIP_DESTROYED` event emission | 165-174 | The `was_alive` gating + `CombatEvent(SHIP_DESTROYED)` emission path. The damage application IS tested, but the event emission side effect is not explicitly asserted. |

**Assessment:** The discovery agent's framing of "6/9 symbols tested" is misleading because the "untested" symbols are thin delegation wrappers. The underlying logic IS tested at the subsystem level. The only real gap is the event emission side effect in `take_damage`.

---

### MAJOR #6: `game/simulation/interfaces/ai_controller.py` (140 LOC)

**Discovery Agent Claim:** "3/7 symbols tested. `IAIControllerFactory` protocol methods (set_grid, create_for_ship, create_for_ships) flagged as untested."

**Verification Result: DISPUTED — DOWNGRADE to MINOR**

**Evidence:** This file defines two **protocols** (interfaces with no implementation). Protocol testing is inherently about structural conformance, not runtime behavior:

| Symbol | Status | Evidence |
|--------|--------|---------|
| `IAIController` | TESTED | `tests/unit/simulation/interfaces/test_ai_controller_interface.py` (101 lines): 7 tests covering protocol existence, runtime_checkable, update() requirement, ship property requirement, package export, real controller compliance, structural match |
| `IAIControllerFactory.set_grid` | TESTED (implicitly) | `tests/unit/simulation/factories/test_ai_factory.py` — tests the concrete `AIControllerFactory` which implements this method |
| `IAIControllerFactory.create_for_ship` | TESTED (implicitly) | Same factory test file — creates controllers via this method |
| `IAIControllerFactory.create_for_ships` | TESTED (implicitly) | Same factory test file |

**Assessment:** Protocols have no runtime implementation to break. The existing tests verify protocol existence, structural requirements, and concrete implementation compliance. No protocol compliance test for `IAIControllerFactory` as a standalone structural check, but the concrete factory IS tested.

---

### MAJOR #7: `game/simulation/components/modifier_manager.py` (330 LOC)

**Discovery Agent Claim:** "10/15 symbols tested. `__init__`, `_load_initial_modifiers`, `remove_modifier_inplace`, `get_all_effects_static`, `get_stat_summary_static` untested."

**Verification Result: CONFIRMED with corrections — DOWNGRADE to MINOR**

**Evidence:** `tests/unit/simulation/components/test_modifier_manager.py` (409 lines) comprehensively tests all instance methods:

| Symbol | Status | Details |
|--------|--------|---------|
| `__init__` + `_load_initial_modifiers` | TESTED (implicitly) | `test_construction_no_initial_modifiers`, `test_construction_loads_modifiers_from_data`, `test_construction_skips_unknown_modifiers` |
| `modifiers` property | TESTED | `test_modifiers_property_iterable`, `_truthy_when_non_empty`, `_falsy_when_empty` |
| `add_modifier` (instance) | TESTED | 6 tests: success, nonexistent, replaces existing, deny_types, allow_types (reject/permit) |
| `remove_modifier` (instance) | TESTED | `test_remove_modifier_by_id`, `test_remove_modifier_preserves_others` |
| `get_modifier` (instance) | TESTED | `test_get_modifier_returns_correct`, `test_get_modifier_returns_none_for_missing` |
| `get_all_effects` (instance) | TESTED | `test_get_all_effects_returns_effects`, `test_get_all_effects_empty_when_no_modifiers` (stat_keys verified) |
| `get_stat_summary` (instance) | TESTED | `test_get_stat_summary_groups_by_stat`, `test_get_stat_summary_empty_when_no_modifiers`, `test_get_modifier_stat_summary_multiplicative_stacking` |

**Actually untested (ADVISORY — deprecated code):**
| Symbol | Lines | Details |
|--------|-------|---------|
| `add_modifier_static` | 223-251 | DEPRECATED. Marked for removal in Task 1.3. |
| `remove_modifier_static` | 253-259 | DEPRECATED. Returns new list (differs from in-place instance version). |
| `remove_modifier_inplace` | 261-274 | Used internally by `add_modifier_static`. Not directly tested. |
| `get_modifier_static` | 276-282 | DEPRECATED. Functionally identical to instance version. |
| `get_all_effects_static` | 287-294 | DEPRECATED. Functionally identical to instance version. |
| `get_stat_summary_static` | 296-330 | DEPRECATED. Functionally identical to instance version. |

**Assessment:** All instance methods are well tested. The untested symbols are ALL deprecated static wrappers marked for removal. The discovery agent correctly identified this but classified it as MAJOR. Since the deprecated code is slated for deletion and the instance equivalents are tested, this should be MINOR.

---

### MAJOR #8: `game/simulation/components/abilities/__init__.py` (303 LOC)

**Discovery Agent Claim:** "1/3 symbols tested. `_contains_unevaluated_formula` and `get_ability_default_scope` untested."

**Verification Result: PARTIALLY CONFIRMED — RETAIN as MAJOR**

| Symbol | Status | Evidence |
|--------|--------|---------|
| `ABILITY_REGISTRY` | TESTED | Exercised through all ability tests |
| `create_ability` | TESTED | `test_create_ability_formula_skip.py` (115 lines): 5 tests + 1 integration test |
| `_contains_unevaluated_formula` | TESTED (indirectly) | All 3 type branches (str, dict, list) exercised through `create_ability` → `_contains_unevaluated_formula`. Data flow verified in `test_dict_with_formula_value_skipped_silently` (dict), `test_string_formula_does_not_warn` (str), `test_nested_list_with_formula_value_does_not_warn` (list). |
| `get_ability_default_scope` | **ZERO TESTS** | Confirmed by grep — 0 matches across entire test suite. This function has 3 branches: known ability with default_scope, known ability without default_scope (fallback "self"), and unknown ability (warning log + fallback "self"). NONE are tested. |

**Assessment:** MAJOR is appropriate. `get_ability_default_scope` (lines 191-221) is the single source of truth for default scope resolution — it's used by compilers and collectors that pre-compute scope for routing. If it malfunctions (wrong default, bad fallback), abilities silently route to wrong scopes. The 3 branches (known-with-default, known-without-default, unknown) need coverage.

---

## Discovery Agent Errors Summary

| # | Error | Production file | Actual test file | Impact |
|---|-------|----------------|-----------------|--------|
| 1 | Claimed 0 tests for `strategy_entities.py` | `game/core/protocols/strategy_entities.py` | `tests/unit/core/test_protocols.py` (459 LOC) + 7 ability source tests | CRITICAL → MINOR |
| 2 | Claimed 0 tests for `ability_sources/storm.py` | `game/strategy/services/ability_sources/storm.py` | `tests/unit/strategy/services/ability_sources/test_storm.py` (106 LOC) | CRITICAL → MINOR |
| 3 | Claimed 0 tests for `handlers/build.py` | `game/strategy/engine/handlers/build.py` | `tests/unit/strategy/engine/test_build_order_command_handler.py` (219 LOC) | CRITICAL → VERIFIED |
| 4 | Understated `spec_compiler.py` coverage | `game/strategy/combat/spec_compiler.py` | 3 test files (~933 LOC) covering multi-fleet, formation, PROJ-343 | MAJOR retained (corrected) |
| 5 | Flagged delegation wrappers as untested | `game/simulation/entities/ship_combat_engine.py` | Subsystem tests in `test_targeting_system.py`, `test_cooldowns.py`, etc. | MAJOR → MINOR |
| 6 | Flagged factory protocol as untested | `game/simulation/interfaces/ai_controller.py` | `test_ai_controller_interface.py` (101 LOC) + `test_ai_factory.py` | MAJOR → MINOR |

**Root cause:** The discovery agent used filename-pattern matching (`test_build.py` for `handlers/build.py`, `test_strategy_entities.py` for `protocols/strategy_entities.py`) rather than content-based import tracing. Three of six errors are filename-mismatch failures.

---

## Final Severity Map (Post-Verification)

### CONFIRMED Gaps

| # | File | Original | Verified | Key rationale |
|---|------|----------|----------|--------------|
| 4 | `game/strategy/combat/spec_compiler.py` | MAJOR | MAJOR | ~5 branch gaps in internal helpers; bulk of code IS tested via public API |
| 8 | `game/simulation/components/abilities/__init__.py` | MAJOR | MAJOR | `get_ability_default_scope` has 3 branches, ZERO tests |

### Downgraded Gaps

| # | File | Original → Verified | Key rationale |
|---|------|---------------------|--------------|
| 1 | `game/core/protocols/strategy_entities.py` | CRITICAL → MINOR | 459 LOC test file exists; 8/10 protocols + 7/9 TypeGuards tested |
| 2 | `game/strategy/services/ability_sources/storm.py` | CRITICAL → MINOR | 106 LOC test file covers all public API; 2 edge-case branches untested |
| 5 | `game/simulation/entities/ship_combat_engine.py` | MAJOR → MINOR | Delegation facade; all subsystems independently tested |
| 6 | `game/simulation/interfaces/ai_controller.py` | MAJOR → MINOR | Protocols only; concrete implementations tested |
| 7 | `game/simulation/components/modifier_manager.py` | MAJOR → MINOR | All instance methods tested; deprecated statics only |

### Verified — Adequately Covered (Discovery Agent Made Errors)

| # | File | Original | Verified |
|---|------|----------|---------|
| 3 | `game/strategy/engine/handlers/build.py` | CRITICAL | VERIFIED (219 LOC test file covers all 4 claimed gaps) |

---

## Prioritized Remediation (Updated)

### Immediate (MAJOR retained)
1. **`game/simulation/components/abilities/__init__.py`**: Test `get_ability_default_scope` for 3 branches (known-with-scope, known-without-scope, unknown fallback). ~30 LOC.
2. **`game/strategy/combat/spec_compiler.py`**: Test `_ship_spec_from_instance` design_data fallback (no design_data / non-dict design_data). Test post-battle-hook empire key resolution (empire_id vs owner_id). ~40 LOC.

### Short-term (MINOR)
3. Test `IStorm` protocol compliance + `is_storm` TypeGuard with concrete Storm.
4. Test `IOrderable` protocol compliance.
5. Test `ShipCombatEngine.take_damage` → `SHIP_DESTROYED` event emission.
6. Test `affects_hex` AttributeError/TypeError edge cases in StormAbilitySource.
7. Remove deprecated static methods from `modifier_manager.py` (Task 1.3).

### Not needed
- `game/strategy/engine/handlers/build.py` — already fully tested.
