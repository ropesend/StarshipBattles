# Shard 04 — Verified Coverage Findings

## Summary
- Shard: 04
- Claims reviewed: 18
- CONFIRMED: 4 | DISPUTED: 4 | INCONCLUSIVE: 0
- Severity downgrades: 5 (CRITICAL→CONFIRMED as covered; MAJOR→MINOR; MAJOR→covered)
- Severity upgrades (ADVISORY→MAJOR): 0

## CONFIRMED Gaps

### 1. `game/strategy/services/ability_sources/fleet.py` (148 LOC) — **CRITICAL (CONFIRMED)**
- **Layer:** Strategy services
- **Issue:** Zero behavioral tests exist for `FleetAbilitySource`. All 12 symbols untested.
- **Key symbols untested:** `FleetAbilitySource.get_abilities()`, `affects_hex()`, `source_label`, `_is_combat_capable()`, `_is_hidden()`, `_walk_strategic_abilities()`
- **Evidence:** The only test file referencing this module (`test_ability_sources_no_global_registry_access.py`, 67 LOC) performs an AST scan to verify no global registry access — it does NOT test any business logic. No other test file imports from this module.
- **Suggested tests:** `tests/unit/strategy/services/ability_sources/test_fleet_ability_source.py` covering all 12 symbols (memoization cache, strategic scope filtering, cloaked fleet empty-result, affects_hex matching/non-matching, source_label formatting, _is_combat_capable error tolerance, _walk_strategic_abilities scope filtering)
- **Verified status:** CONFIRMED

### 2. `game/simulation/components/abilities/__init__.py` (315 LOC) — **MAJOR (CONFIRMED)**
- **Issue:** `_contains_unevaluated_formula()` (line 159) has zero unit tests.
- **Evidence:** `tests/unit/simulation/components/abilities/test_ability_registry.py` (37 lines) tests only `get_ability_default_scope` (5 tests). No test imports or exercises `_contains_unevaluated_formula`. The function is called internally by `create_ability()` (line 193) but no test verifies its recursive logic for nested dicts, lists, mixed types, empty data, or `=`-prefixed strings.
- **Suggested tests:** Add parametrized tests for `_contains_unevaluated_formula` with edge cases: flat `=`-string, non-formula string, nested dict with formula, list containing formula, empty data, int/float/bool, mixed nested structures.
- **Verified status:** CONFIRMED

### 3. `game/ui/screens/workshop_viewmodel_selection.py` (138 LOC) — **MAJOR (CONFIRMED)**
- **Issue:** All three pure functions have zero test coverage.
- **Key symbols untested:** `normalize_selection()` (line 21), `apply_append_selection()` (line 62), `sync_modifiers_to_selection()` (line 117)
- **Evidence:** Zero test files import from `game.ui.screens.workshop_viewmodel_selection`. The similar-sounding `tests/unit/ui/screens/test_builder_selection.py` tests `normalize_selection` from `game.ui.screens.builder_selection` — a DIFFERENT module with its own implementation. The only mention of `_sync_modifiers_to_selection` in the test suite is a string literal in `test_workshop_viewmodel_public_api.py` that lists expected public API symbols. No test actually calls any function from this module.
- **Suggested tests:** `tests/unit/ui/screens/test_workshop_viewmodel_selection.py` covering: tuple-pass-through, component-lookup in ship layers, component-not-found (None, -1) path, append/toggle with empty current, empty incoming, homogeneity enforcement, toggle-add, toggle-remove, modifier copy to siblings (skip primary), no-selection/no-primary edge cases.
- **Verified status:** CONFIRMED

### 4. `game/strategy/engine/happiness_engine.py` (141 LOC) — **MINOR (CONFIRMED gap in `_validate_tick_inputs`)**
- **Issue:** `_validate_tick_inputs()` (line 90) raises `ValidationException` when a colony list contains None, but no test exercises this error path.
- **Evidence:** The test file `test_happiness_engine.py` (680 lines) covers: no empires, empty colony populations, zero-count populations, multi-species, multi-resource, surplus bonus, clamping, missing race config — but NO test passes a colony list with None to trigger the `ValidationException` at line 96. The method IS exercised indirectly through `process_happiness()` for the non-error path.
- **Suggested tests:** Add `test_none_colony_in_list_raises_validation_exception` to `test_happiness_engine.py`.
- **Verified status:** CONFIRMED (minor gap; private method covered indirectly for positive paths)

## Disputed & Inconclusive Claims

| Original Finding | File | Severity | Verdict | Reason |
|---|---|---|---|---|
| "No test covers BuildOrderCommandHandler" (zero tests for 4 symbols) | `game/strategy/engine/handlers/build.py` | CRITICAL | **DISPUTED** | The code IS tested. `tests/unit/strategy/engine/test_build_order_command_handler.py` (219 lines) imports from `game.strategy.engine.command_handlers` which is a **re-export shim** that re-exports the same classes from `game.strategy.engine.handlers.build` via the chain: `command_handlers.py` → `handlers/__init__.py` → `handlers/build.py`. The test covers all gaps identified in Phase 2: BUILD order creation (line 47-67), insert at position 0 (line 69-89), path clearing (line 91-107), fleet-not-found error (line 109-121), RemoveBuildOrder handler (line 124-177), and registration (line 180-217). The Phase 1 scanner marked `build.py` TIER_0 because it couldn't resolve the re-export chain — the classes are the same objects. Severity downgraded to **COVERED**. |
| "No direct test for _get_resource_registry" (check_available False when registry is None) | `game/simulation/components/abilities/resources.py` | MAJOR | **DISPUTED** | The specific gap IS tested. `test_check_available_without_registry_returns_false` (test_resource_consumption.py line 441-450) creates a `ResourceConsumption` on a mock component with `ship = None` (so `_get_resource_registry()` returns None at line 62-64), then calls `ability.check_available()` and asserts it returns False. This directly exercises the branch at line 115 where registry is None → check_available returns False. The Phase 2 claim is false. |
| "7 validation helpers untested" (`_validate_required_fields, _validate_aptitudes, _validate_identity_enums, _validate_homeworld, _validate_descriptions, _validate_preferences, _validate_reproduction_and_happiness`) | `game/strategy/data/race_config.py` | MAJOR | **DISPUTED** | All 7 private methods ARE tested through `validate()` public API. `TestRaceConfigValidation` (test_race_config.py lines 168-243) contains 11 tests exercising every validation category: missing name (line 183), missing flag (189), missing portrait (194), missing theme (199), invalid government type (204), invalid homeworld type (209), aptitude below min (214), aptitude above max (219), description too long (224), negative reproduction rate (229), happiness out of range (235). The Phase 1 scanner couldn't resolve indirect call-sites from `validate()` → private methods, but the code IS tested. Severity downgraded to **COVERED**. |
| "AddToConstructionQueue/RemoveFromConstructionQueue/ReorderConstructionQueue handlers untested" (5 symbols) | `game/strategy/engine/handlers/construction_queue.py` | MAJOR | **DISPUTED** | ALL handlers have extensive tests. `tests/unit/strategy/test_command_handlers.py` (1890 lines) has: `TestAddToConstructionQueueCommandHandler` (lines 1162-1435), `TestRemoveFromConstructionQueueCommandHandler` (lines 1436-1626), `TestReorderConstructionQueueCommandHandler` (lines 1627-1753). Same re-export chain issue as claim 1 — the test imports from `command_handlers.py` which re-exports from `handlers/construction_queue.py`. Tests cover: planet-not-found, invalid entity type, negative/out-of-range index, design validation, design cost loading, item removal, atomic reorder, fleet-not-found, facility queue resolution. Severity downgraded to **COVERED**. |

## Discovery Agent Errors

| Error Type | Details |
|---|---|
| **Re-export chain blindness** | The Phase 1 scanner marks files as TIER_0/TIER_2 when tests import through a re-export chain (`command_handlers.py` → `handlers/`). Affected: `build.py`, `construction_queue.py`. The scanner should resolve import aliases or follow package `__init__.py` re-exports. This caused 3 false CRITICAL/MAJOR claims. |
| **Indirect-call blind spot** | Scanner marks private validation helpers as untested when they're called only through a public `validate()` method but can't trace local function references stored in a list. Affected: `race_config.py` private `_validate_*` methods. |
| **False negative on already-tested branch** | Claimed `check_available()` returning False when registry is None was untested, but `test_check_available_without_registry_returns_false` explicitly tests this exact scenario. The Phase 2 agent likely didn't read far enough into the 1094-line test file. |
| **Module confusion** | Phase 2 report identified `tests/unit/ui/screens/test_builder_selection.py` as potentially testing `workshop_viewmodel_selection.py` — but this test file tests `game.ui.screens.builder_selection`, a completely different module. The mention should have been removed during Phase 2 verification. |

## Updated Remediation Plan (Post-Verification)

### Immediate (Critical)
1. **`game/strategy/services/ability_sources/fleet.py`** — Write `tests/unit/strategy/services/ability_sources/test_fleet_ability_source.py`. Only true CRITICAL gap remaining in Shard 04.

### High Priority (Major)
2. **`game/ui/screens/workshop_viewmodel_selection.py`** — Write `tests/unit/ui/screens/test_workshop_viewmodel_selection.py`. Pure algorithmic functions with no tests.
3. **`game/simulation/components/abilities/__init__.py`** — Add unit tests for `_contains_unevaluated_formula()` with recursive edge cases.

### Low Priority (Minor)
4. **`game/strategy/engine/happiness_engine.py`** — Add test for `_validate_tick_inputs` raising `ValidationException` on None colony in list.

### Claims Downgraded to COVERED by Verification
5. ~~`game/strategy/engine/handlers/build.py`~~ — Already tested through re-export chain.
6. ~~`game/simulation/components/abilities/resources.py:_get_resource_registry`~~ — Already tested.
7. ~~`game/strategy/data/race_config.py` validation helpers~~ — Already tested via `validate()`.
8. ~~`game/strategy/engine/handlers/construction_queue.py` handlers~~ — Already tested through re-export chain.
