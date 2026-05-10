# PROJ-378 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/fixtures/galaxy_fixtures.py` | Test (NEW) | 1 | **Canonical implementation module** for `make_galaxy_stub()`. Mirrors the established `tests.fixtures.*` convention (see `tests/fixtures/README.md`, `tests/fixtures/ai.py`, `tests/fixtures/battle.py`, `tests/fixtures/common.py`). Importable cross-tree by both unit and integration tests. ~30 LOC. |
| `tests/unit/strategy/data/conftest.py` | Test (NEW, optional) | 1 | Optional thin pytest fixture bridge: imports `make_galaxy_stub` from `tests.fixtures.galaxy_fixtures` and exposes a `@pytest.fixture` wrapper named `galaxy_stub` for ergonomic injection inside this directory. |
| `tests/unit/strategy/data/test_galaxy_cleanup.py` | Test (modified) | 1 | Migrate 3 fixtures (`galaxy_with_planet` `:58-104`, `galaxy_with_warp_link` `:163-190`, `galaxy_with_fleets` `:245-294`) to call `make_galaxy_stub()` then layer state. Removes the `with patch.object(Galaxy, '__init__', lambda ...)` blocks at `:62`, `:166`, `:248`. |
| `tests/integration/strategy/test_empire.py` | Test (modified) | 2 | Replace 5 `Galaxy.__new__(Galaxy)` sites at `:11, :19, :26, :37, :45` with `make_galaxy_stub()`. Imports updated to `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`. |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py` | Test (modified) | 2 | Consolidate the inline factory at `:74-80` to call `make_galaxy_stub(radius=300)`; preserve `gal.warp_points = []` test-specific extension. Imports updated to `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`. |
| `docs/02_PATTERNS.md` | Doc (optional) | 2 | Optional: short note on `make_galaxy_stub()` as the canonical "minimal galaxy" pattern. |

## Out-of-manifest (read-only references)

| File | Why |
|------|------|
| `game/strategy/data/galaxy.py` | Read-only reference for property forwarders + `_ensure_state()`. |
| `game/strategy/data/galaxy_state.py` | Read-only reference for the dataclass shape. |
| `game/strategy/data/galaxy_entity_registry.py` | Constructor signature reference: `GalaxyEntityRegistry(state)`. |
| `game/strategy/data/galaxy_spatial_index.py` | Constructor signature reference: `GalaxySpatialIndex(state)`. |
