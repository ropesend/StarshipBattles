# PROJ-379 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files


### Phase 1 (TDD-first): tests + builder + JSONs + field-coverage guard

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/saves/_build_galaxy_fixture.py` | Test (NEW) | Hand-built fixture builder. ~80-150 LOC. Two factory functions (`build_baseline`, `build_populated`) plus a `__main__` entry that re-emits both JSON files. Implementation lands AFTER the failing tests below per TDD ordering. |
| `tests/integration/strategy/test_save_round_trip.py` | Test (modify) | Add 4 Phase 1 tests (TDD red first): `test_baseline_fixture_is_byte_deterministic`, `test_populated_fixture_is_byte_deterministic`, `test_committed_baseline_matches_builder_output`, `test_committed_populated_matches_builder_output`. |
| `tests/integration/strategy/test_golden_fixture_field_coverage.py` | Test (NEW) | Field-coverage guard using the serialized-baseline pattern: `planet_to_dict(_minimal_planet())` returns the source of truth for emitted keys and per-key defaults. NO AST walk. NO `dataclasses.fields()` introspection. ~50-80 LOC. |
| `tests/fixtures/saves/galaxy_proj372_baseline.json` | Fixture (regenerated) | 5-system + warp lanes, no planets. |
| `tests/fixtures/saves/galaxy_proj372_populated.json` | Fixture (regenerated) | 10-system + planets + decorated owned planet exercising every Planet field with a non-default value. |

### Phase 2: cross-process determinism (subprocess + `PYTHONHASHSEED`)

| File | Type | Notes |
|------|------|-------|
| `tests/integration/strategy/test_save_round_trip.py` | Test (modify) | Add 2 subprocess tests: `test_baseline_byte_deterministic_across_processes`, `test_populated_byte_deterministic_across_processes`. Each spawns fresh `python` processes with `PYTHONHASHSEED` ∈ {`"0"`, `"12345"`, `"random"`}; compares stdout pairwise. |

### Phase 3: Delete `_capture_baseline.py` + cleanup

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/saves/_capture_baseline.py` | Test (DELETE) | Replaced by `_build_galaxy_fixture.py`. |

### Phase 4: Closeout + cross-links + review cycle

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-377/decisions.md` | Doc (modify) | Append "MIN-002 resolved by PROJ-379" cross-link row. |
| `Projects/active_projects/PROJ-379/decisions.md` | Doc (modify) | Final closeout decisions row capturing review outcome. |

## Out-of-manifest (read-only references)

| File | Type | Why read-only |
|------|------|---------------|
| `tests/fixtures/galaxy_fixtures.py` | Test (read-only) | Reuses `make_galaxy_stub` from PROJ-378 as the builder's starting point. |
| `tests/fixtures/strategy_entities.py` | Test (read-only) | Reuses `create_test_planet` / `create_test_star` / `create_test_warp_point` factories. |
| `game/strategy/data/planet.py`, `planet_serde.py` | Production (read-only) | Phase 1 guard imports `Planet` (to construct a minimal instance) and calls `planet_to_dict(_minimal_planet())` to obtain the emitted-keys set + per-key serialized defaults. No AST parse. |
| `game/strategy/data/galaxy.py` | Production (read-only) | Round-trip path; `to_dict` / `from_dict` shape unchanged. |
| `game/strategy/data/galaxy_entity_registry.py` | Production (read-only) | Builder routes through `add_system` / `register_planet` (production registration paths). |
| `game/strategy/data/star_system.py` | Production (read-only) | Builder constructs `StarSystem` directly via `__init__`. |
| `Reviews/results/2026-05-07_044412_code_proj-377-...` | Review (read-only) | MIN-002 source. |
