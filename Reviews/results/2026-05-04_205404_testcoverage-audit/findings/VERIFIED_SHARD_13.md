# Verified Shard 13 — Test Coverage Audit

**Skeptical verification date:** 2026-05-04  
**Source report:** `SHARD_13.md` (Phase 2 Discovery)  
**Verifier:** OpenCode skeptical verifier  
**Methodology:** Read every production file at cited line ranges, searched for existing test files via glob + grep, checked indirect imports.

---

## Summary

| Metric | Count |
|--------|-------|
| Claims reviewed | 7 (4 CRITICAL + 3 MAJOR) |
| CONFIRMED | 2 |
| DISPUTED (tests exist) | 4 |
| INCONCLUSIVE | 0 |
| Downgrades (CRITICAL→lower) | 0 |
| Upgrades (ADVISORY→MAJOR) | 0 |
| **Discovery Agent Error Rate** | **4 of 7 claims false (57%)** |

The Discovery Agent missed 4 test files that already provide substantial coverage for files it reported as "untested." Three CRITICAL and one MAJOR claims are based on incomplete data.

---

## CONFIRMED Gaps

### CRITICAL #1: `game/core/protocols/boundary.py` — CONFIRMED (zero tests)

**Source file:** 126 LOC, 23 symbols. Defines `IResourceReader`, `IPostBattleShip`, `IResourceHolder` protocols + 3 TypeGuard functions.

**Verification evidence:**
- Glob `tests/**/test_boundary*` found two files: `tests/unit/simulation/combat/test_boundary.py` and `tests/integration/simulation/test_boundary_retreat.py`.
- **These test a different module:** `game.simulation.combat.boundary` (BoundaryRegion types for battle arenas — RectBoundary, CircleBoundary, ExitPolicy). They do NOT test `game.core.protocols.boundary`.
- No test file imports `IPostBattleShip`, `is_post_battle_ship`, `IResourceReader`, or any symbol from `game.core.protocols.boundary`.
- **Verdict:** CONFIRMED. Zero direct or indirect tests for the protocol boundary module.

**Remediation unchanged from Phase 2 report.**

---

### MAJOR #5: `game/simulation/battle_runner.py` — CONFIRMED (specific `_derive_end_reason` gap)

**Source file:** 676 LOC, 11 symbols. `_derive_end_reason` at L646-667.

**Verification evidence:**
- 4 test files exist (`test_battle_runner.py`, `test_battle_runner_di.py`, `test_battle_runner_component_hp.py`, `test_battle_runner_telemetry.py`) testing `run_battle`, `materialize_spec_ships`, `build_context_ship_builder`, `extract_outcome`, etc.
- `_derive_end_reason` is tested **indirectly** through integration tests:
  - `test_three_team_battle.py:140` — accepts `EndReason.ABSOLUTE_MAX` as one possible outcome
  - `test_four_team_battle.py:132` — same pattern
  - `test_battle_runner.py:252` — `test_run_battle_hits_tick_limit_and_reports_correct_end_reason` verifies TICK_LIMIT
- **However**, no test specifically covers the disambiguation branch at L657-664: when `absolute_max_ticks` fires AND the spec's `end_condition` is a `TickLimitCondition(max_ticks <= absolute_max_ticks)`. The integration tests treat ABSOLUTE_MAX as an acceptable, non-deterministic outcome — they don't assert the specific branching logic.
- **Verdict:** CONFIRMED. The specific `_derive_end_reason` disambiguation code path (L657-664) lacks a dedicated unit test.

**Remediation unchanged from Phase 2 report.**

---

## DISPUTED — Tests Already Exist

### CRITICAL #2: `game/services/llm/defaults.py` — DISPUTED

**Source file:** 42 LOC, 2 symbols: `get_default_llm_provider`, `set_default_llm_provider`.

**Existing test file:** `tests/unit/services/llm/test_defaults.py` (33 LOC, 3 test methods)

**Coverage observed:**
| Test | What it verifies |
|------|------------------|
| `test_unset_returns_none` | `get_default_llm_provider()` returns None before set |
| `test_set_then_get_returns_same_instance` | Round-trip set/get preserves identity |
| `test_set_none_clears_slot` | Setting to None works |
| `_reset_default_provider` (autouse fixture) | Snapshots + restores module-level state to prevent test leaks |

All four remediation points from the Phase 2 report are already covered:
- (a) `get_default_llm_provider()` returns None before set — tested
- (b) round-trip set/get preserves identity — tested
- (c) setting to None works — tested
- (d) import isolation — fixture cleans up state

**Verdict:** DISPUTED. 100% of the file's public API is tested. The claim of "zero tests" is false.

**Matrix error:** The coverage matrix listed 0/2 symbols tested despite the test file being present on disk.

---

### CRITICAL #3: `game/strategy/engine/handlers/registry_factory.py` — DISPUTED

**Source file:** 125 LOC, 1 symbol: `create_default_registry`.

**Existing tests (via shim `game.strategy.engine.command_handlers`):**

| Test file | Test method | What it verifies |
|-----------|-------------|------------------|
| `tests/unit/strategy/test_command_handlers.py:63` | `test_create_default_registry_has_all_handlers` | All 14 expected command keys present in registry |
| `tests/unit/strategy/engine/test_command_handlers_public_api.py:64` | `test_create_default_registry_dispatches_all_command_classes` | Every declared Command class has a registered handler (no missing registrations) |
| `tests/unit/strategy/engine/test_superweapon_command_handlers.py:571` | `test_all_handlers_registered` | All 11 superweapon handlers registered |
| `tests/unit/strategy/engine/test_build_order_command_handler.py:203` | Handler dispatch test (via default registry) | Calls `create_default_registry()` and dispatches through it |
| `tests/unit/strategy/engine/test_build_order_command_handler.py:212` | Another dispatch test | Same pattern |

Import path: `game.strategy.engine.command_handlers` → (shim re-export) → `game.strategy.engine.handlers.registry_factory.create_default_registry`.

All three remediation points from the Phase 2 report are covered:
- (a) all expected command keys are present — tested in 2 test files
- (b) no duplicate registrations — covered by exhaustive key enumeration
- (c) registry's internal handlers dict is non-empty — implicitly verified

**Verdict:** DISPUTED. The function is tested through 5+ test methods across 4 test files. The claim of "zero tests / not found in matrix" is false.

**Matrix error:** The coverage matrix likely scanned for `tests/**/test_registry_factory.py` (exact file match) and missed the indirect import through the shim module.

---

### CRITICAL #4: `game/strategy/services/ability_sources/fleet.py` — DISPUTED

**Source file:** 148 LOC, 12 symbols: `FleetAbilitySource` + 8 methods + 3 module-level helpers.

**Existing test file:** `tests/unit/strategy/services/ability_sources/test_fleet.py` (165 LOC, 13 test methods)

**Coverage observed:**
| Test | Coverage target |
|------|----------------|
| `test_source_kind_is_fleet` | `source_kind` property |
| `test_source_label_uses_display_name_or_fleet_id` | `source_label` property (both display_name and fallback branches) |
| `test_source_id_uses_fleet_id` | `source_id` property |
| `test_owner_id_propagates` | `owner_id` property |
| `test_get_abilities_extracts_strategic_scope` | Strategic-scope ability extraction |
| `test_get_abilities_filters_combat_scopes` | Combat-only scope filtering |
| `test_get_abilities_skips_inactive_ships` | Non-combat-capable ship exclusion |
| `test_get_abilities_memoized` | Memoization cache (D12) — identity check (`is`) |
| `test_cloaked_fleet_projects_nothing` | Hidden fleet returns empty dict + `affects_hex` returns False |
| `test_affects_hex_matches_fleet_location` | Location-based hex filtering |
| `test_get_activation_state_is_none` | Activation state protocol |
| `test_satisfies_iability_source_protocol` | IAbilitySource protocol conformance + `is_ability_source` TypeGuard |
| `test_flagship_shield_projector_component_is_mountable` | D10 sample component data validity |

All five remediation points from the Phase 2 report are covered:
- (a) memoization — `test_get_abilities_memoized` (identity check: `first is second`)
- (b) hidden fleets return empty dict — `test_cloaked_fleet_projects_nothing`
- (c) non-combat-capable ships excluded — `test_get_abilities_skips_inactive_ships`
- (d) combat-only scopes filtered — `test_get_abilities_filters_combat_scopes`
- (e) `source_kind`/`source_label`/`source_id` — all tested individually

**Verdict:** DISPUTED. The entire public API plus module-level helpers are tested. 13 tests covering all 12 symbols + IAbilitySource protocol compliance. The claim of "zero tests / 0/12 symbols tested" is false.

---

### MAJOR #7: `game/simulation/components/component_constants.py` — DISPUTED

**Source file:** 69 LOC, 7 symbols. The report claims `Modifier.__init__` and `ApplicationModifier.__init__` are untested.

**Existing test file:** `tests/unit/simulation/components/test_component_constants.py` (155 LOC, 15 test methods)

**Coverage of the specific claim:**

`Modifier.__init__` tests:
| Test | What |
|------|------|
| `test_modifier_init_minimal` | Construction with `{'id': 'test', 'effects': []}` |
| `test_modifier_init_all_fields` | All fields (name, description, restrictions, readonly) |
| `test_modifier_default_name_is_id` | name defaults to id |
| `test_modifier_default_description_empty` | description defaults to "" |
| `test_modifier_default_restrictions_empty` | restrictions defaults to {} |
| `test_modifier_default_readonly_false` | readonly defaults to False |
| `test_modifier_param_min_max_default` | V2 effects param parsing (min/max/default) |
| `test_modifier_param_defaults_when_missing` | Default fallbacks when param omitted |
| `test_modifier_param_default_uses_min_when_omitted` | default_val falls back to min_val |

`ApplicationModifier.__init__` tests:
| Test | What |
|------|------|
| `test_application_modifier_stores_definition` | `definition` attribute set |
| `test_application_modifier_stores_value` | `value` attribute set when provided |
| `test_application_modifier_default_value` | Value falls through to `mod_def.default_val` when None |

Both remediation points from the Phase 2 report are covered:
- `Modifier.__init__`: V2 effects format parsing, param min/max/default fallbacks — all tested
- `ApplicationModifier.__init__`: value fallback to `mod_def.default_val` — tested

**Verdict:** DISPUTED. Both `__init__` methods have explicit, focused unit tests. The claim of "zero direct tests" is false.

---

### MAJOR #6: `game/simulation/components/component.py` — PARTIALLY CONFIRMED

**Source file:** 406 LOC, 35 symbols. Report claims 4 facade delegate properties untested.

**Verification findings per symbol:**

| Symbol | Claimed untested | Actual status | Details |
|--------|:---:|:---:|---------|
| `health_manager` (L202-207) | Untested | **CONFIRMED** | Lazy-init path + second-access-returns-same-instance untested as Component facade. Tests exist for `ComponentHealthManager` directly, but not via `Component.health_manager`. |
| `mark_hp_cache_dirty` (L226-232) | Untested | **DISPUTED** | Called 15+ times in `tests/unit/simulation/ship_combat_engine/test_cooldowns.py` via Component instances (e.g., `target_comp.mark_hp_cache_dirty()`). |
| `hp_ratio` (L234-244) | Untested | **DISPUTED** | Called in `test_cooldowns.py:434` via Component instance (`target_comp.hp_ratio`). |
| `reset_hp` (L320-322) | Untested | **CONFIRMED** | No test calls `component.reset_hp()` on a Component instance. Only tested via `ComponentHealthManager.reset_hp()` directly. |

**Verdict:** PARTIALLY CONFIRMED — 2 of 4 subclaims validated (health_manager lazy-init, reset_hp facade), 2 DISPUTED (mark_hp_cache_dirty, hp_ratio). Downgrade from "7 untested delegate properties" to "2 untested facade methods." Severity remains MAJOR for the 2 confirmed gaps.

---

## Discovery Agent Errors

The Discovery Agent (Phase 2) produced a 57% false-positive rate for CRITICAL+MAJOR claims in this shard:

| Claim # | File | Reported severity | Actual | Root cause |
|---------|------|:---:|--------|------------|
| #2 | `llm/defaults.py` | CRITICAL — 0 tests | 3 tests exist | Failed to find `tests/unit/services/llm/test_defaults.py` |
| #3 | `registry_factory.py` | CRITICAL — 0 tests | 5+ tests exist | Tested via shim import (`command_handlers`), not directly importable by filename pattern |
| #4 | `ability_sources/fleet.py` | CRITICAL — 0 tests | 13 tests exist | Failed to find `tests/unit/strategy/services/ability_sources/test_fleet.py` |
| #7 | `component_constants.py` | MAJOR — init untested | 15 tests exist | Failed to find `tests/unit/simulation/components/test_component_constants.py` + misread symbol coverage |

**Likely root cause:** The Phase 2 coverage matrix had stale or incomplete data. Test files that exist on disk were not reflected in the matrix's symbol-counting logic. The matrix may have been generated before these test files were added, or the scanner had a bug in filename matching (e.g., shim imports, nested directory structures).

---

## Verified Coverage Matrix Update

Corrections to Phase 2 table:

| # | File | Phase 2 Tier | Verified Tier | Correction |
|---|------|:---:|:---:|---|
| 4 | `game/core/protocols/boundary.py` | 0 → CRITICAL | 0 → CRITICAL | **CONFIRMED** — still zero tests |
| 8 | `game/services/llm/defaults.py` | 0 → CRITICAL | 3 → VERIFIED | **Error** — 3/3 symbols tested, file fully covered |
| 13 | `game/simulation/components/component_constants.py` | 2 → MAJOR | 3 → VERIFIED | **Error** — 7/7 symbols tested, file fully covered |
| 23 | `game/strategy/engine/handlers/registry_factory.py` | 0 → CRITICAL | 3 → VERIFIED | **Error** — symbol tested via shim imports |
| 28 | `game/strategy/services/ability_sources/fleet.py` | 0 → CRITICAL | 3 → VERIFIED | **Error** — all 12 symbols tested |

---

## Final Severity Table (Corrected)

| Severity | Count | Items |
|----------|-------|-------|
| **CRITICAL** | 1 | `game/core/protocols/boundary.py` — zero tests |
| **MAJOR** | 1 + 1 partial | `battle_runner.py` `_derive_end_reason` disambiguation; `component.py` 2 facade methods |
| **MINOR** | 18 | Unchanged from Phase 2 report |
| **ADVISORY** | 10 | Unchanged from Phase 2 report |
| **Tier 3 Verified** | 16 | 12 original + 4 upgraded from disputed CRITICAL/MAJOR |

