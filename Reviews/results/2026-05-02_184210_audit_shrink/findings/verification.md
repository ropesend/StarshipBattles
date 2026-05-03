# Cross-Verification Report
## Date: 2026-05-02
## Source Reviews: deep_review_01.md, deep_review_02.md, deep_review_03.md, deep_review_04.md, dead_code_validation.md

---

## Critical Finding Verification

| Finding ID | Symbol | Test refs? | Doc refs? | Data refs? | Verdict |
|------------|--------|------------|-----------|------------|---------|
| DEEP-01-001 | `GameState.FORMATION = 4` in `constants.py:29` | No — `FORMATION_ENGINE_THROTTLE`, `FORMATION_SLOWDOWN_THROTTLE` (AIConfig) and `_SENTINEL_FORMATION` (test sentinel) are unrelated symbols | No — zero matches in `docs/` | No — only `formation` appears in `system_blueprints.json` for "planetary formation", unrelated | **CONFIRMED SAFE DELETION** |
| DEEP-02-001 | `_extract_weapon_summaries()` in `battle_runner.py:647-671` | No — zero matches in `tests/` | No — zero matches in `docs/` | No — zero matches in `data/` | **CONFIRMED SAFE DELETION** |
| DEEP-03-001 | `GroupTargetCoordinator` in `group_target_coordinator.py:17-124` | **YES** — `tests/unit/ai/test_group_target_coordinator.py` has 33 matches across 16 test methods | **YES** — `docs/01_ARCHITECTURE.md:188` documents it: `GroupTargetCoordinator -- focus fire, reserve commitment, flagship succession` | No | **DOWNGRADE TO PRODUCT_DECISION** |

---

## Downgraded to Product Decision

| Finding ID | Symbol | Evidence | Recommendation |
|------------|--------|----------|----------------|
| DEEP-03-001 | `GroupTargetCoordinator` (entire file, 124 LOC) | Full test suite (`tests/unit/ai/test_group_target_coordinator.py`, 16 tests) + architecture doc reference (`docs/01_ARCHITECTURE.md:188`). This is a planned-but-unwired AI subsystem. | **Do NOT delete.** The test suite and architecture doc confirm this is a partially-wired planned feature. If the feature is cancelled, file a feature ticket and remove tests, doc, and code together. Keep as-is otherwise. |

---

## Confirmed Safe Deletions

| Finding ID | Symbol | LOC | Evidence |
|------------|--------|-----|----------|
| DEEP-01-001 | `GameState.FORMATION = 4` (enum member) | 1 | Zero references in `tests/`, `docs/`, or `data/`. The Formation screen was removed but the enum value was never cleaned up. No migration needed. |
| DEEP-02-001 | `_extract_weapon_summaries()` | 25 | Zero references in `tests/`, `docs/`, or `data/`. Superseded by `WeaponSummaryAggregator` in `telemetry.py`. |

---

## Product Decision Verification

### Deep Review Product Decisions

| Finding ID | Symbol | Original Category | Test refs? | Doc refs? | Data refs? | Production? | Verification |
|------------|--------|-------------------|------------|-----------|------------|-------------|--------------|
| DEEP-01-003 | `DisplayConfig.test_resolution()` + `windowed_resolution()` | PRODUCT_DECISION | YES — `test_config.py`, `test_config_edge_cases.py`, `conftest.py` | YES — `docs/guides/testing_infrastructure.md:26` | No | `conftest.py` uses `test_resolution()` for headless display | **CONFIRMED CORRECT** — test + doc refs. Used in headless test infrastructure. |
| DEEP-01-004 | `SuperweaponMarker._parse_attrs()` and `weapon_name` | PRODUCT_DECISION | YES — `test_superweapons.py`, `test_design_load_warp_capability.py` (comment reference) | YES — `docs/systems/combat_simulation.md:864` | YES — `data/components.json` | Used by ability system | **CONFIRMED CORRECT** — test + doc + data refs. |
| DEEP-01-005 | `ORDER_TO_TIME_FIELD` empty dict in `action_time_resolver.py` | PRODUCT_DECISION | YES — `test_action_time_resolver.py`, `test_fleet_navigation_action_timing.py` test the resolver module | No | No | Used inline by resolver code | **CONFIRMED CORRECT** — tests exercise the resolver module. Dict is an extension point. |
| DEEP-02-002 | `create_brick()` in `designs.py` | PRODUCT_DECISION | YES — `test_designs.py` (7 test methods) | No | No | None | **CONFIRMED CORRECT** — test-only function. |
| DEEP-02-003 | `create_interceptor()` in `designs.py` | PRODUCT_DECISION | YES — `test_designs.py` (5 test methods) | No | No | None | **CONFIRMED CORRECT** — test-only function. |
| DEEP-02-004 | `BattleController.load_state()` | PRODUCT_DECISION | YES — `test_state.py` (battle_controller tests: 2 test methods) | No | No | None | **CONFIRMED CORRECT** — test-only, saves are disposable per AGENTS.md. |
| DEEP-03-002 | AI interfaces re-exports (`game/ai/interfaces/__init__.py`) | PRODUCT_DECISION | YES — tests under `tests/unit/ai/` | YES — `docs/01_ARCHITECTURE.md:168`, `docs/systems/strategy_layer.md:395`, `docs/systems/ai_system.md:188`, `docs/03_CONVENTIONS.md:401` | No — `data/group_policies.json` referenced but doesn't match `IAIPolicyProvider` directly | Partially wired via `IControllable` | **CONFIRMED CORRECT** — test + doc refs. |
| DEEP-03-003 | `IAIControllerFactory` protocol | PRODUCT_DECISION | YES — `test_combat_shortcut_paths.py:491,495` | YES — `docs/01_ARCHITECTURE.md:352`, `docs/04_SERVICES.md:222,238`, `docs/systems/combat_simulation.md:427` | No | Wired via `BattleEngine.start()` | **CONFIRMED CORRECT** — test + doc refs. Active infrastructure. |
| DEEP-03-004 | `_eval_least_armor_rule` | PRODUCT_DECISION | YES — `test_target_evaluator_rules.py:524-545`, `test_projectile_candidate_guards.py:83-89` | YES — `docs/systems/ai_system.md` references targeting policies | **YES — `data/targeting_policies.json:46` has `"type": "least_armor"` in the "sniper" policy** | Used via data-driven dispatch | **FALSE FINDING — code is alive** The reviewer claimed `least_armor` has no entry in `targeting_policies.json`, but it DOES (line 46, "sniper" policy). The `_eval_least_armor_rule` code path IS reachable via data-driven dispatch. This finding should be dismissed (no action needed). |
| DEEP-04-P1 | `ShieldRegeneratingArmor` ability class | PRODUCT_DECISION | YES — 4 test files (`test_design_load_warp_capability.py`, `test_create_ability_formula_skip.py`, `test_damage_calculator.py`, `test_damage_reduction.py`) | YES — `docs/systems/ability_reference.md` (9 references, full documentation), `docs/guides/simulation_testing.md` (2 references) | YES — `data/components.json:201`, `data/stats_sections.json:138` | Reviewer says no combat code path consumes it, but extensive doc+test+data indicates planned infrastructure | **CONFIRMED CORRECT** — extensive test + doc + data references. Planned/supported infrastructure. |
| DEEP-04-P2 | `load_test_data()` in `workshop_data_reloader.py` | PRODUCT_DECISION | **NO** — the test file `tests/unit/ui/screens/test_workshop_data_reloader.py` does **not exist**. Reviewer cited a non-existent file. | No | No | **YES** — called from `workshop_event_router.py:405` at runtime! | **CATEGORY ERROR** — this code is NOT dead. It has a live production call site at `workshop_event_router.py:405`. The quality concern (test-only data loading in production) is valid, but the code is actively used. |

### Dead Code Validation Product Decisions

| Finding ID | Symbol | Original Category | Test refs? | Doc refs? | Data refs? | Production? | Verification |
|------------|--------|-------------------|------------|-----------|------------|-------------|--------------|
| PD1 | `STAR_FALLBACK` import in `system_mode.py:17` | PRODUCT_DECISION | **NO** | YES — but for the constant in `colors.py:415`, NOT the import in system_mode.py. `STAR_FALLBACK` at system_mode.py:17 is only the import line — never used in module body (grep-verified: only appears at line 17). | No | No — import exists but `STAR_FALLBACK` is never used in the body of `system_mode.py` | **SHOULD BE SAFE DELETION** — The import has no references supporting its USE. The constant in `colors.py` is alive and documented; only the unused import should be deleted. Upgraded from PRODUCT_DECISION to CONFIRMED SAFE DELETION. |

---

## Summary of Corrections

| Issue | Details |
|-------|---------|
| **DEEP-03-001 downgrade** | `GroupTargetCoordinator` was marked CRITICAL (delete entire file) but has a full test suite + architecture doc reference. Downgraded to PRODUCT_DECISION. |
| **DEEP-03-004 false finding** | `_eval_least_armor_rule` was flagged as unreachable because reviewer claimed `least_armor` has no data file entry. It DOES — `targeting_policies.json:46` ("sniper" policy). Code is alive and reachable. |
| **DEEP-04-P2 category error** | `load_test_data()` marked as test-only dead code but actually has a live production call site (`workshop_event_router.py:405`). The test file referenced by reviewer does not exist. |
| **PD1 upgrade** | `STAR_FALLBACK` import in `system_mode.py` had doc refs to the constant itself (not the import). The import is never used in the module body. Upgraded from PRODUCT_DECISION to CONFIRMED SAFE DELETION. |

## Final Tally

| Category | Count |
|----------|-------|
| CRITICAL findings reviewed | 3 |
| Confirmed as CRITICAL (safe deletion) | 2 |
| Downgraded CRITICAL → PRODUCT_DECISION | 1 |
| PRODUCT_DECISION findings verified | 11 |
| PRODUCT_DECISION findings confirmed correct | 8 |
| PRODUCT_DECISION findings with issues | 2 (DEEP-03-004 false positive, DEEP-04-P2 category error) |
| PRODUCT_DECISION upgraded → SAFE DELETION | 1 (PD1) |
| Total safe deletions identified | 3 findings (11 LOC confirmed + 1 import) |
