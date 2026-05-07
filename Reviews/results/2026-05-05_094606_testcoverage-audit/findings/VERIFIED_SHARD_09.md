# VERIFIED Shard 09 — Skeptical Verification Report

**Generated**: 2026-05-05  
**Verification coverage**: 11 CRITICAL + 13 MAJOR = 24 claims verified (100%)

---

## Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED Gaps | 12 |
| DISPUTED (test exists) | 9 |
| PARTIALLY CONFIRMED | 3 |

**Agent Error Rate**: 9/24 (37.5%) claims were incorrect — the Phase 2 report wrongly marked several files as having zero unit tests despite dedicated test files existing.

---

## CONFIRMED Gaps (12)

### CRITICAL

#### 1. `game/simulation/combat/families/_beam_common.py` — No dedicated test
- **Claim**: Tier 0, zero unit tests
- **Verification**: No test file directly calls `build_beam_resolution`. `BeamResolution` objects appear in `test_weapon_registry.py`, `test_weapon_dispatch_golden.py`, and `test_beam_ramming.py`, but those tests construct `BeamResolution` directly — they never exercise `build_beam_resolution`. The zero-length aim vector guard (line 34: `aim_vec.length() > 0` → default `Vector2(1, 0)`) is completely untested.
- **Verdict**: CONFIRMED

#### 2. `game/simulation/combat/families/pdc.py` — No dedicated test
- **Claim**: Tier 0, zero unit tests
- **Verification**: No test file imports `PDCHandler` or calls `PDCHandler().fire()`. The module-level `WEAPON_REGISTRY.register(WeaponFamily.PDC, PDCHandler())` side effect is implicitly exercised by registry tests, and `test_weapon_dispatch_golden.py:419-422` checks PDC dispatch produces `BeamResolution`, but that tests the *firing system's* dispatch of PDC, not `PDCHandler.fire()` itself. The claim that "fire() method means all PDC weapon resolution is untested" is overstated (it IS exercised through integration), but the dedicated unit test gap is real.
- **Verdict**: CONFIRMED

#### 3. `game/strategy/facade/slices/event_slice.py` — Zero unit tests
- **Claim**: Tier 0, zero unit tests
- **Verification**: Grep for `EventSlice` across all `test_*.py` files returns zero matches. All 8 query methods (get_turn_events with both empire_id=None and empire_id=X paths, get_all_events, get_events_by_category, get_human_player_ids, get_turn_number, get_save_path) are completely untested. The dual-path `EventLog` API dispatch (empire_id None vs not None) highlighted as regression-prone is never exercised.
- **Verdict**: CONFIRMED

#### 4. `game/strategy/services/effect_ability_display.py` — Internal helpers untested
- **Claim**: Tier 0, zero unit tests
- **Verification**: The Phase 2 claim of zero tests is IMPRECISE — the *public* functions (`make_group_key`, `make_display_name`, `format_intrinsic_ability_magnitude`) ARE tested via `test_system_effects_collector.py` (which re-exports them). However, the *internal* helpers `_format_status` and `_is_activatable` have ZERO test coverage across the entire test suite. `_ability_kind` is tested only indirectly via `test_system_effects_collector.py` integration tests. All 3 internal helpers lack dedicated unit tests.
- **Verdict**: CONFIRMED (for internal helpers `_format_status`, `_is_activatable`, and gap in `_ability_kind` direct testing)

### MAJOR

#### 5. `game/simulation/systems/tick_phase.py` — Concrete phase classes untested
- **Claim**: MAJOR — 6 concrete phase classes untested; only `TickPhaseRegistry` protocol tested
- **Verification**: `tests/unit/simulation/systems/test_tick_phases.py` (98 LOC) tests `ITickPhase` protocol and `TickPhaseRegistry` via `MockPhase` — exactly as the report states. The 6 concrete phase classes (`RebuildGridPhase`, `AIAndShipUpdatePhase`, `BoundaryEnforcementPhase`, `AttackProcessingPhase`, `RammingPhase`, `ProjectileUpdatePhase`) are never instantiated or tested directly. `test_exit_policy.py` mentions `BoundaryEnforcementPhase` only as an integration-level reference. `create_default_phases` also untested.
- **Verdict**: CONFIRMED

#### 6. `game/strategy/data/habitability_factors.py` — `_make_scalar_extractor` untested directly
- **Claim**: MAJOR — factory function untested
- **Verification**: `tests/unit/strategy/data/test_habitability_factors.py` (375 LOC) validates extractors are callable and produce correct values *through* `FACTOR_REGISTRY.items()`, but never calls `_make_scalar_extractor` directly. The factory's None-guard and float coercion (lines 132-135) are covered by registry-level testing of the generated extractors, but the factory function itself has no dedicated unit test. The Phase 2 claim is technically correct — the factory is not *directly* tested.
- **Verdict**: CONFIRMED (indirect coverage exists but factory-specific test absent)

#### 7. `game/strategy/data/habitability_factors.py` — `_make_gas_extractor` untested directly
- **Claim**: MAJOR — factory function untested
- **Verification**: Same pattern as `_make_scalar_extractor`. Registry-level tests exercise generated extractors but the factory function `_make_gas_extractor` (atmosphere None guard, `.get(formula, 0.0)` fallback, float coercion) has no dedicated test calling it in isolation.
- **Verdict**: CONFIRMED (indirect coverage exists)

#### 8. `game/strategy/data/habitability_factors.py` — `_build_gas_factors` untested directly
- **Claim**: MAJOR — builds 10 gas HabitabilityFactor entries, untested
- **Verification**: No test calls `_build_gas_factors` directly. The output (10 gas factors in `FACTOR_REGISTRY`) is validated by registry shape tests (`test_gas_factors_count`, `test_gas_weights_sum_to_1_5`, etc.) in `test_habitability_factors.py`. O2/N2 special-cased defaults (lines 323-331) have no boundary tests verifying 21kPa/5kPa for O2 and 79kPa/20kPa for N2 vs neutral defaults for other 8 gases.
- **Verdict**: CONFIRMED (indirect coverage exists, factory-internal logic not directly tested)

#### 9. `game/strategy/generation/density/primitives/noise.py` — `_hash_coord` untested directly
- **Claim**: MAJOR — internal hash function untested
- **Verification**: `tests/unit/strategy/generation/density/test_noise.py` (85 LOC) tests `NoisePrimitive.evaluate()` which calls `_hash_coord` and `_smooth_noise` internally. The deterministic output tests and same-seed reproducibility tests exercise these functions, but `_hash_coord` has no standalone unit test for its bit-manipulation logic (XOR, multiply, right-shift at lines 18-22).
- **Verdict**: CONFIRMED (indirect only)

#### 10. `game/strategy/generation/density/primitives/noise.py` — `_smooth_noise` untested directly
- **Claim**: MAJOR — noise generation function untested
- **Verification**: Same as `_hash_coord`. Tested through `NoisePrimitive.evaluate()` integration. The smoothstep interpolation, bilinear interpolation, and integer/fractional-coordinate decomposition (lines 28-50) have no standalone unit test isolating the core algorithm.
- **Verdict**: CONFIRMED (indirect only)

#### 11. `game/ui/screens/setup_screen.py` — `_get_ship_factory` untested
- **Claim**: MAJOR — module-level lazy singleton factory getter untested
- **Verification**: Grep for `_get_ship_factory` across all test files returns zero matches. Uses global mutable state (`global _ship_factory`), `get_default_registry_provider()`, and `GameRegistries` construction. This is indeed untested.
- **Verdict**: CONFIRMED

#### 12. `game/simulation/components/abilities/harvester.py` — `_parse_attrs` + `StagingYardAbility` + `PlanetaryYardAbility` untested
- **Claim**: MAJOR — 4 `_parse_attrs` methods untested; StagingYardAbility and PlanetaryYardAbility classes untested
- **Verification**: `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py:89-100` defines *local* `PlanetaryYardAbility` and `StagingYardAbility` classes (not the production classes from `harvester.py`). No test imports or exercises the production `StagingYardAbility._parse_attrs` non-dict branch (`float(data)` coercion at line 104) or `PlanetaryYardAbility.__init__` override (line 123). All 4 `_parse_attrs` dict/non-dict branches in `ResourceHarvesterAbility`, `LocalStorageAbility`, `StagingYardAbility`, and `SpaceShipyardAbility` are untested.
- **Verdict**: CONFIRMED

---

## DISPUTED (Test Exists — 9)

### CRITICAL

#### 13. `game/ai/protocols.py` — Has dedicated tests
- **Claim**: Tier 0, zero unit tests, "No unit test file imports this module"
- **Evidence**: `tests/unit/ai/test_ai_protocols.py` (246 LOC) directly imports and tests:
  - All 3 Protocols: `IGridEntity`, `IProjectile`, `IComponentHealth` (via `isinstance` checks with real Ship/Projectile/Component objects, 7 test functions)
  - All 3 TypeGuards: `is_grid_entity`, `is_projectile`, `is_component_health` (with True/False assertions, 8 test functions)
  - Edge cases: Mock with all attrs, partial mock, dead entity, non-entity types (None, int, str, dict, list)
- **Verdict**: DISPUTED — comprehensive coverage exists

#### 14. `game/core/component_state.py` — Has dedicated tests
- **Claim**: Tier 0, zero unit tests, "No unit test file imports this module"
- **Evidence**: `tests/unit/core/test_component_state.py` (169 LOC) directly imports and tests all 3 symbols:
  - `component_state_key`: format validation ("bridge#0", "seeker_missile#3")
  - `ComponentState`: dataclass fields, to_dict/from_dict roundtrip, default is_active/max_hp, int→float coercion via `__post_init__`, is_damaged 3 cases (full hp, damaged, max_hp=0), from_dict with missing optional fields
  - `ComponentInstanceView`: frozen dataclass, construction, frozen immutability raises, equality/inequality
  - Additionally imported by 16 other test files (component_state has heavy cross-module usage)
- **Verdict**: DISPUTED — complete coverage exists

#### 15. `game/simulation/entities/stat_contributors/launch.py` — Has dedicated tests
- **Claim**: Tier 0, zero unit tests, "No unit test file imports this module"
- **Evidence**: `tests/unit/simulation/entities/stat_contributors/test_launch.py` (127 LOC) imports `launch` module and tests `contribute_vehicle_launch`:
  - No-hangar ability → no-op
  - Single hangar populates all fields (capacity, wave size, size cap, launch cycle)
  - Cross-call capacity and wave size summation
  - Size cap uses max (not sum) across components
  - Launch cycle uses max (not sum) across components
  - Note: test uses `{}` as acc argument (not StatAccumulator) — side-channel mutations on ship work as intended
- **Verdict**: DISPUTED — the function IS tested, though the VehicleLaunch guard (line 45) and missing-VehicleLaunch path are covered by test_no_hangar

#### 16. `game/simulation/entities/stat_contributors/movement.py` — Has dedicated tests
- **Claim**: Tier 0, zero unit tests, "No unit test file imports this module"
- **Evidence**: `tests/unit/simulation/entities/stat_contributors/test_movement.py` (168 LOC) imports `movement` module and tests all 4 per-ability contributors:
  - CombatPropulsion: thrust sum (100+50=150), no ability → zero
  - StrategicMovement: points sum (2.0+1.5=3.5)
  - ManeuveringThruster: turn_rate added to both turn_speed and maneuver_points
  - WarpJump: max_tonnage takes max (1000, not 500+500), energy_cost sums (180)
  - Mixed: all 4 accumulate independently from one component
- **Verdict**: DISPUTED — complete coverage exists

#### 17. `game/strategy/services/ability_sources/planet_intrinsic.py` — Has dedicated tests
- **Claim**: Tier 0, zero unit tests, "No unit test file imports this module"
- **Evidence**: `tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py` (121 LOC) directly imports `PlanetIntrinsicAbilitySource`:
  - `source_kind`, `source_label` with planet_type formatting, `source_id` with planet id
  - `owner_id` is always None (PROJ-301 D2)
  - `get_abilities` returns intrinsic dict / empty dict when None
  - `affects_hex` single-hex center match and mismatch
  - `affects_hex` multi-hex Dyson sphere (radius_hexes=2 → 7 hexes verified with all ring-1 neighbors)
  - `get_activation_state` returns None (always-on)
  - `IAbilitySource` protocol conformance
  - Note: `source_id` fallback path (id=None or id=-1) is NOT tested — the mock always has id=42. The Phase 2 report's claim about untested source_id fallback is only partially verified.
- **Verdict**: DISPUTED — the module has a dedicated test file with 12 tests, though the `source_id` fallback branch (line 37-38) is a genuine gap

#### 18. `game/strategy/validation/superweapon_validator.py` — Has dedicated tests
- **Claim**: Tier 0, zero unit tests, "No unit test file imports this module"
- **Evidence**: `tests/unit/strategy/validation/test_superweapon_validator.py` (650 LOC) directly imports `SuperweaponValidator`:
  - `find_ship_with_ability`: found, not found, empty fleet, first-match
  - `validate_implode_planet`: valid, no ability, null planet
  - `validate_stellerate_star`: valid, no ability, not at system (no stars isn't directly tested as separate case but _validate_star_targeted_superweapon covers it)
  - `validate_open_warp_point`: valid, target not exist, duplicate warp, no ability
  - `validate_close_warp_point`: valid (at warp point), no warp at location, no ability, skip_location_check allows remote, skip still checks ability
  - `validate_create_dyson_sphere`: valid, no stars, no ability
  - `validate_self_destruct`: valid multi-ship, ship not in fleet, lacks ability, empty list, single ship
- **Verdict**: DISPUTED — exhaustive coverage exists (20+ test functions)

#### 19. `game/ai/spatial_behaviors/base.py` — Has dedicated tests
- **Claim**: Tier 0 CRITICAL (from file-coverage table, though no Tier-0 section was written)
- **Evidence**: 
  - `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py` (394 LOC) tests `SpatialBehavior` base class: importability, `compute_target_position` attribute, `behavior_type` attribute
  - `tests/unit/ai/spatial_behaviors/test_anti_clumping.py` (75 LOC) directly imports and tests `apply_separation` with 5 test functions: pushes close ships apart, no-change far ships, handles single ship, handles empty list, coincident ships pushed apart
- **Verdict**: DISPUTED — both symbols from base.py have test coverage

### MAJOR

#### 20. `game/strategy/engine/planet_modifier_effect_engine.py` — Has dedicated tests
- **Claim**: MAJOR — "only process_modifier_effects_tick as tested. All private helper methods untested"
- **Evidence**: `tests/unit/strategy/engine/test_planet_modifier_effect_engine.py` (239 LOC) directly imports `PlanetModifierEffectEngine` and tests ALL helper methods through the public `process_modifier_effects_tick`:
  - Gravity apply: ACTIVE + target set → gravity changes + original stored (test line 61-77)
  - Gravity no-change: INACTIVE → no change (test line 79-95)
  - Gravity revert: INACTIVE + original stored → reverts (test line 97-114)
  - Gravity revert: facility destroyed → reverts (test line 116-130)
  - Gravity no-target: ACTIVE but target=None → no-apply (test line 132-148)
  - Gravity idempotent: already-applied → original preserved (test line 150-168)
  - Radiation apply: ACTIVE → shielding set (test line 173-188)
  - Radiation revert: INACTIVE → shielding→0 (test line 190-208)
  - Radiation revert: facility destroyed → shielding→0 (test line 210-222)
  - Radiation no-target: ACTIVE but target=None → no-apply (test line 224-239)
  - `_has_active_ability` is exercised through all the above via component_states
  - MagicMock guard branches (lines 52-55) are exercised because MockPlanet uses dataclass floats
- **Verdict**: DISPUTED — comprehensive private method coverage exists

---

## PARTIALLY CONFIRMED (3)

#### 21. `game/strategy/services/effect_ability_display.py` — Public functions tested, internals not
- **Claim**: Tier 0, all symbols untested (8 test suggestions)
- **Verification**: 
  - `make_group_key` — TESTED via `test_system_effects_collector.py:751-767` (EnvironmentalDamage+thermal, EnvironmentalDamage+radiation, ThrustModifier, ShieldModifier, FuelDrain)
  - `make_display_name` — TESTED via `test_system_effects_collector.py:771-785` (EnvironmentalDamage with thermal/radiation, ShieldModifier, ThrustModifier, FuelDrain)
  - `format_intrinsic_ability_magnitude` — TESTED via `test_system_effects_collector.py:789-828` (rate, multiplier, identity suppression, unknown ability, zero rate)
  - `_ability_kind` — INDIRECTLY tested via collector integration tests
  - `_format_status` — **UNTESTED** (zero grep matches). The 4 Active/Activating/Deactivating/Inactive branches have no coverage.
  - `_is_activatable` — **UNTESTED** (zero grep matches)
- **Verdict**: PARTIALLY CONFIRMED — Phase 2 was wrong about zero coverage but correct about significant gaps in internal helpers

#### 22. `game/ui/screens/strategy_click_dispatcher.py` — Some handlers tested, most not
- **Claim**: MAJOR — "Only _hit_test_planets, _resolve_click_target, and _handle_picking have heuristic matches. The 13 mode-specific click handlers are all untested."
- **Verification**:
  - **Tested**: `_hit_test_planets` (expanded planet, giant), `_resolve_click_target` (planet logical hex on visual hit, raw hex when zoom low), `_handle_picking` (hit-tested planet prioritized, empty space clears), `_handle_select_mode_click` (indirectly via picking + move)
  - **Tested via integration**: `dispatch_click` routing in `test_move_order_registration.py` (MOVE mode left-click, right-click cancel)
  - **Untested (12 handlers)**: `_handle_join_mode_click`, `_handle_colonize_mode_click`, `_handle_transfer_mode_click`, `_handle_edit_move_click`, `_handle_drop_cargo_mode_click`, `_handle_load_cargo_mode_click`, `_handle_warp_target_click`, `_handle_implode_planet_click`, `_handle_stellerate_star_click`, `_handle_open_warp_click`, `_handle_close_warp_click`, `_handle_dyson_sphere_click`
  - BUG-93 path (move failure → SELECT reset, line 121) is untested
- **Verdict**: PARTIALLY CONFIRMED — the report correctly identifies the gap but missed the integration-level dispatch routing test; 12 of 14 mode handlers are untested

#### 23. `game/ui/screens/transfer_view_model.py` — Some methods tested, most not
- **Claim**: MAJOR — "Phase 1 reports only apply_arrow, apply_max, build_row_data as heuristically matched. 14 methods report as untested"
- **Verification**:
  - **Tested (3 methods)**: `apply_arrow` (sentinel reset: MAX_LOAD→25, MAX_DROP→-10), `apply_max` (load/drop direction), `build_row_data` (species ordering, pod rows)
  - **Trivial/indirectly exercised**: `__init__` (implicit via all tests), `get_pending` (trivial dict.get)
  - **Untested (11 methods)**: `set_pending_zero`, `clear_all_pending`, `reset_pending`, `format_pending`, `toggle_filter_empty`, `set_sources`, `select_source` (with side effects of target rebinding), `select_target`, `target_labels`, `source_labels`, `get_amounts`, `_build_pod_rows`, `visible_rows`
  - The report slightly overstates (14 vs 11 untested) but the core gap is real
- **Verdict**: PARTIALLY CONFIRMED — most ViewModel methods are untested as claimed

---

## Agent Errors

1. **Severity: HIGH** — 6 Tier-0 CRITICAL claims were **completely false** (protocols.py, component_state.py, launch.py, movement.py, planet_intrinsic.py, superweapon_validator.py). The Phase 1 heuristic scan missed dedicated test files that exist and directly import the production modules. Root cause: the test files *do* import from their respective target modules, suggesting the Phase 1 AST scanner had false negatives.

2. **Severity: HIGH** — 1 MAJOR claim (planet_modifier_effect_engine.py) was **completely false** — a dedicated 239 LOC test file exists with 11 tests covering exactly the "untested" methods the report described.

3. **Severity: MEDIUM** — The `spatial_behaviors/base.py` table entry listed as CRITICAL with 1 finding had no corresponding Tier-0 section. Both `SpatialBehavior` and `apply_separation` have dedicated test files.

4. **Severity: MEDIUM** — `effect_ability_display.py` was listed as Tier-0 with "No unit test file imports this module" but the public functions ARE tested (via re-exports through `system_effects_collector`). The gap is narrower than reported — only `_format_status` and `_is_activatable` are genuinely untested.

5. **Severity: LOW** — Some MINOR claims (empire.py `add_colony`, battle_ui_service.py converters, formula_evaluator.py `_eval_node`) that this verifier did not audit systematically appeared to be tested indirectly, consistent with the Phase 2 report's own notes. No false positives detected in the MINOR tier based on spot-checks.

---

## Overall Shard 09 Assessment

| Metric | Phase 2 | Verified |
|--------|---------|----------|
| CRITICAL (Tier 0) claims | 10 | **4 confirmed gaps, 6 disputed** |
| MAJOR claims | 13 | **8 confirmed gaps, 1 disputed, 3 partially confirmed** |
| Agent error rate | — | **37.5% (9/24 claims incorrect)** |

**Real gaps remaining**: 4 CRITICAL + 8 MAJOR = 12 actionable gaps out of original 24 claims.

**Highest priority actual gaps** (per risk severity):
1. `event_slice.py` — all 8 event-log query methods completely untested (strategy facade surface)
2. `_beam_common.py` + `pdc.py` — beam/PDC weapon resolution chain has no unit coverage
3. `harvester.py` — 4 `_parse_attrs` methods + StagingYardAbility float-coercion path + PlanetaryYardAbility __init__ override untested
4. `effect_ability_display.py` — `_format_status` and `_is_activatable` fully untested
5. `tick_phase.py` — 6 concrete phase classes untested (battle engine tick loop)
6. `superweapon_validator.py` — DISPUTED (has full test coverage; remove from action items)
