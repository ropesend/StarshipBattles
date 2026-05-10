# Verified — Shard 11 Skeptical Verification Report

**Verifier**: OpenCode (skeptical) | **Date**: 2026-05-04 | **Parent**: `SHARD_11.md`

---

## Summary

| Claim | Original Tier | Verified Tier | Status |
|-------|--------------|--------------|--------|
| 1. `system_slice.py` | CRITICAL | **CONFIRMED** | No test file exists |
| 2. `build_queue_dto.py` | CRITICAL | **CONFIRMED** | No test file exists |
| 3. `facility.py` (ability_sources) | CRITICAL | **DOWNGRADED → MINOR** | DISPUTED — test file exists with 8 tests |
| 4. `system_archetype.py` | CRITICAL | **DOWNGRADED → MINOR** | DISPUTED — test file exists with 7 tests |
| 5. `generation/__init__.py` | ADVISORY | **CONFIRMED** | Init-only, advisory |
| 6. `collision.py` | MAJOR | **DOWNGRADED → MINOR** | DISPUTED — test file exists with extensive ramming tests |
| 7. `weapon_firing_system.py` | MAJOR | **DOWNGRADED → MINOR** | DISPUTED — 1298-line test file covers all methods via public API |
| 8. `galaxy_warp_generator.py` | MAJOR | **CONFIRMED** | 3 boundary tests only; 11/12 symbols lack direct coverage |
| 9. `ability_iterator.py` | MAJOR | **CONFIRMED (corrected counts)** | 2/9 providers tested indirectly; 7 untested |
| 10. `component_activation_engine.py` | MAJOR | **DOWNGRADED → MINOR** | DISPUTED — `_tick_facility` IS tested through public API |
| --- | --- | --- | --- |
| superweapons.py (correction) | CORRECTED | **CONFIRMED** | Matrix error — tests exist, correctly identified by discovery |

**Outcome**: 2 CRITICAL confirmed (unchanged), 3 CRITICAL disputes (→ MINOR), 1 MAJOR confirmed, 3 MAJOR disputes (→ MINOR), 1 MAJOR confirmed with corrected counts. The discovery agent overcounted gaps by treating public-API-tested private methods as "untested" and missed test files due to naming mismatches.

---

## CONFIRMED Gaps (3)

### CRITICAL-1: `game/strategy/facade/slices/system_slice.py` (132 LOC)

**Status**: CONFIRMED — no dedicated test file. No test anywhere in the repo imports `SystemSlice` or `system_slice`.

**Untested symbols**: `__init__`, `get_all_systems`, `get_all_stars`, `get_system_at_hex`, `get_system_containing_fleet`, `get_system_near_hex`, `get_storm_names_at_hex`.

**Risk remains High**. This is the primary CQRS read-slice used by the UI for system/star resolution.

**Recommended tests** (unchanged from Phase 2): Mock `FacadeSessionState` with a `Galaxy` containing known systems + storms. Verify `get_system_at_hex`, `get_system_near_hex` fallback path, `get_all_stars` cache invalidation, `get_storm_names_at_hex`.

---

### CRITICAL-2: `game/strategy/facade/dto/build_queue_dto.py` (41 LOC)

**Status**: CONFIRMED — no dedicated test file.

**Untested symbols**: `BuildQueueSourceDTO` dataclass (11 frozen fields), `BuildQueueSourceDTO.from_domain` (cloning logic with `[dict(item) for item in list(...)]`).

**Risk remains Medium**. Shallow copy bugs could allow UI to mutate domain queue data.

**Recommended tests** (unchanged): Verify `from_domain` produces detached copies. Test with missing `owner_entity` attributes (fallback to `entity_id=0`, `empire_id=None`).

---

### MAJOR-1: `game/strategy/data/galaxy_warp_generator.py` (444 LOC)

**Status**: CONFIRMED — test file `test_galaxy_warp_generator.py` (54 lines, 3 tests) exists but only covers boundary cases (N=0, N=1, N=2). All 11 internal methods (`_calculate_warp_distance`, `_is_angle_clear`, `create_warp_link`, `_build_edge_candidates`, `_apply_mst_edges`, `_should_add_density_edge`, `_add_density_edges`, `generate_warp_lanes`, `_load_warp_point_types`, `_roll_warp_type`, and module-level helpers) lack direct test coverage.

**Correction to Phase 2**: The Phase 2 report claimed "1/12 symbols tested" via a heuristic match from `test_intrinsic_rng_determinism.py`. The actual test file IS dedicated to warp generation (3 tests via `GameInitializer.initialize`). The coverage count is ~3/12 exercised at integration level, not 1/12.

**Risk remains High**. MST correctness and angle validation are critical for galaxy connectivity.

**Recommended tests** (unchanged): Test MST with 3-system triangle. Test `_is_angle_clear`. Test `_roll_warp_type` determinism. Test `create_warp_link` bidirectionality.

---

### MAJOR-2: `game/strategy/services/ability_iterator.py` (316 LOC)

**Status**: CONFIRMED — test file `test_ability_iterator.py` (205 lines, ~9 tests) exists and thoroughly covers:
- `register_source_provider_at_hex`, `register_source_provider_in_system`, `unregister_source_provider`
- `iter_ability_sources_at_hex`, `iter_ability_sources_in_system` (storm/facility + deduping)
- `_facility_provider` and `_storm_provider` (tested indirectly through registration+iteration)

**Correction to Phase 2**: The Phase 2 report claimed "all 9 provider functions untested." In reality, `_facility_provider` and `_storm_provider` are exercised through the iterator tests. The untested count is 7:
- `_planet_global_hex` (helper for `_facility_provider`)
- `_star_provider` (PROJ-302)
- `_planet_intrinsic_provider` (PROJ-301)
- `_warp_point_provider` (PROJ-303)
- `_system_archetype_provider` (PROJ-304)
- `_fleet_provider` + `set_fleet_lookups` (PROJ-305)

**Risk remains High** for providers that plug in PROJ-301..305 integration seams.

**Recommended tests**: Add mock systems with planets having `intrinsic_abilities`, stars, warp points, and archetypes to exercise each provider.

---

## DISPUTED Claims — Downgraded

| # | File | Original | Verified | Reason |
|---|------|----------|----------|--------|
| 3 | `ability_sources/facility.py` | CRITICAL | **MINOR** | Test file `test_facility.py` (100 lines, 8 tests) exists at `tests/unit/strategy/services/ability_sources/test_facility.py`. Covers source_kind, source_label, source_id, owner_id, get_abilities (empty/non-operational, walks components, list collisions), protocol conformance. Only `affects_hex` and `affects_system` (trivial `return True`) lack explicit assertions. |
| 4 | `ability_sources/system_archetype.py` | CRITICAL | **MINOR** | Test file `test_system_archetype.py` (68 lines, 7 tests) exists at `tests/unit/strategy/services/ability_sources/test_system_archetype.py`. Covers source_kind, source_label, source_id, owner_id, get_abilities, protocol conformance, StarSystem serialization roundtrip. Only trivial property return values (`affects_hex=True`, `affects_system=identity`, `get_activation_state=None`) lack assertions. |
| 6 | `collision.py` | MAJOR | **MINOR** | Test file `test_beam_ramming.py` (792 lines) exists at `tests/unit/engine/collision_edge_cases/test_beam_ramming.py`. `process_ramming` has 8 dedicated tests (non-kamikaze ignored, no target, dead target, equal HP mutual destruction, zero radius, missing HP attribute ×2, no logger) plus 1 real-ship integration test. `process_beam_attack` has extensive raycasting geometry validation. Also exercised by `test_beam_hit_tracking.py` and `test_battle_rng_isolation.py`. MINOR gap: `__init__` trivial, no direct test for `rng` attribute default. |
| 7 | `weapon_firing_system.py` | MAJOR | **MINOR** | Test file `test_weapon_firing_system.py` (1298 lines, 12 test classes) exists. All internal methods (`_process_hangar_launch`, `_process_weapon_fire`, `_find_valid_target`, `_create_attack`, `_create_seeker_projectile`, `_create_standard_projectile`) are thoroughly exercised through the public `fire_weapons` API. Tests cover beam/projectile/seeker creation, hangar launch, PDC integration, firing conditions, shot tracking, inactive weapons, secondary targets. MINOR gap: no test for `_create_seeker_projectile` firing arc when target is OUTSIDE arc (falls back to `launch_vec`). |
| 10 | `component_activation_engine.py` | MAJOR | **MINOR** | Test file `test_component_activation_engine.py` (190 lines, 8 tests) exists. `_tick_facility` IS extensively tested through `process_activation_tick`: activating ticks, activation completion, deactivation completion, 3 parallel components, INACTIVE/ACTIVE skipping, no activations. The Phase 2 claim that `_tick_facility` is "the only untested symbol" is incorrect — it is the most thoroughly tested method. MINOR gap: `__init__` trivial, `_validate_tick_inputs` (None colony check) untested directly. |

---

## Inconclusive

None. All claims were resolved to CONFIRMED or DISPUTED with clear evidence.

---

## Discovery Agent Errors

The Phase 2 discovery agent made the following systematic errors:

### Error 1: Naming-based test file discovery failure
The agent failed to find test files when the test path used a different naming convention than expected:
- `test_facility.py` (under `ability_sources/`) vs glob `test*ability_source*` — missed because glob used `*ability_source*` not `*facility*`
- `test_system_archetype.py` — same cause
- `test_beam_ramming.py` — the collision test file doesn't contain "collision" in the filename; glob `test*collision*` failed

**Impact**: 3 CRITICAL claims (25% of all CRITICALs) were false positives.

### Error 2: Overly-aggressive private-method counting
The agent flagged private methods as "untested" even when they are exercised through the public API. This caused 3 MAJOR claims (30% of all MAJORs) to be false positives:
- `weapon_firing_system.py`: `fire_weapons` exercises all private methods; counting them as "7 untested" is inaccurate
- `component_activation_engine.py`: `process_activation_tick` exercises `_tick_facility` in every test
- `collision.py`: `process_ramming` tested through 9 methods in the test file

**Impact**: 3 MAJOR claims inflated.

### Error 3: Under-counting existing coverage
For `galaxy_warp_generator.py`, the agent credited "1/12 symbols" but the test file `test_galaxy_warp_generator.py` actually exercises the `generate_warp_lanes` path with 3 boundary tests. The correct count is ~3/12 at integration level.

### Error 4: Registry-indirection blind spot
The agent correctly identified this as a matrix error for `superweapons.py` (tests access via `ABILITY_REGISTRY` + `create_ability()` rather than direct class imports). This suggests the coverage matrix scanner has a systemic blind spot for registry-indirection testing patterns.

---

## Verified Tally

| Tier | Phase 2 Count | Verified Count | Change |
|------|--------------|----------------|--------|
| CRITICAL | 5 | **2** | -3 downgraded |
| MAJOR | 5 | **2** | -3 downgraded |
| MINOR | 9 | **12** | +3 upgraded from CRITICAL, +3 from MAJOR, -3→CONFIRMED MAJOR |
| ADVISORY | 8 | 8 | Unchanged |
| CONFIRMED (Tier 3) | 12 | 12 | Unchanged |
| MATRIX CORRECTION | 1 | 1 | Unchanged |

---

## Prioritized Recommendations (Revised)

1. **CRITICAL**: `system_slice.py` — primary facade query API, 0 tests, 132 LOC
2. **CRITICAL**: `build_queue_dto.py` — DTO cloning contract, 0 tests, 41 LOC
3. **MAJOR**: `galaxy_warp_generator.py` — MST + density edge generation, 3 integration tests only, 444 LOC
4. **MAJOR**: `ability_iterator.py` — 7 of 9 provider functions lack any test coverage, 316 LOC
5. **MINOR**: `collision.py` — `__init__` trivial, `process_ramming` logger=None path implicitly tested; consider explicit edge test for rng=None
6. **MINOR**: `weapon_firing_system.py` — `_create_seeker_projectile` out-of-arc launch vector fallback untested
7. **MINOR**: `component_activation_engine.py` — `_validate_tick_inputs` None-colony path untested
8. **MINOR**: `ability_sources/facility.py` — `affects_hex`/`affects_system` trivial but unasserted
9. **MINOR**: `ability_sources/system_archetype.py` — `affects_hex`/`affects_system`/`get_activation_state` trivial but unasserted
