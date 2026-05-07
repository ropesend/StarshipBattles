# PROJ-378 — Initial Review (Pattern Catalogue + Perf Finding)

**Architect:** Claude (planning only)
**Date:** 2026-05-06
**Status:** Read-only investigation; no code changes.

## TL;DR

- **3 fixtures × 18 distinct tests, 15 of which currently error in setup with `AttributeError: 'Galaxy' object has no attribute '_state'`** in `tests/unit/strategy/data/test_galaxy_cleanup.py` (the remaining 3 are the `TestDysonSpherePlanetType` class, which doesn't use a fixture and passes). All errors stem from `galaxy.radius = 100` invoking the post-PROJ-372 `radius.setter` at `galaxy.py:73-75` while `_state` is still missing.
- The `_ensure_state()` lazy escape hatch at `galaxy.py:96-105` is only invoked from `_next_planet_id` and `_next_fleet_id` setters/getters — **NOT from `radius` or any of the 9 dict-field forwarders**. That's why `test_empire.py` (touches `_next_fleet_id` first) works while `test_galaxy_cleanup.py` (touches `radius` first) crashes.
- **Galaxy construction cost (measured):** import = 118 ms; first `Galaxy(radius=100)` = 39 ms; steady-state = 33 ms / call. Heavy enough that "use real `Galaxy(radius=N)` everywhere" would add ~0.5 s to the failing file alone, with linear scaling as more `Galaxy.__new__` sites adopt the pattern.
- **Recommendation:** option (b) — single shared `make_galaxy_stub()` in `tests/fixtures/galaxy_fixtures.py` (canonical implementation; cross-tree-importable per the `tests.fixtures.*` convention) plus an optional thin `tests/unit/strategy/data/conftest.py` `@pytest.fixture` bridge, wiring `_state`, `_registry`, `_spatial`. ~30 LOC, fixes all 15 errors, generalizes to the 6 other legacy-pattern call sites. *(Originally proposed location was the conftest itself; relocated in r004 because `tests/unit/strategy/data/__init__.py` does not exist, so cross-tree imports from integration tests would have failed.)*

## Pattern Catalogue (exhaustive grep over `tests/`)

### Pattern 1: `Galaxy.__new__(Galaxy)` + direct attribute assignment

**Total:** 9 call sites across 3 files. **Status post-PROJ-372:** 8 passing, 1 file with 15 errors.

| File | Line | First mutation | Status | Why |
|------|------|----------------|--------|-----|
| `tests/unit/strategy/data/test_galaxy_cleanup.py` | 63 | `galaxy.radius = 100` | **ERROR** | `radius.setter` calls `self._state.radius`; `_state` absent. |
| `tests/unit/strategy/data/test_galaxy_cleanup.py` | 167 | `galaxy.radius = 100` | **ERROR** | Same. |
| `tests/unit/strategy/data/test_galaxy_cleanup.py` | 249 | `galaxy.radius = 100` | **ERROR** | Same. |
| `tests/integration/strategy/test_empire.py` | 11 | `galaxy._next_fleet_id = 1` | passing | `_next_fleet_id.setter` → `_ensure_state()` → lazy-creates state. |
| `tests/integration/strategy/test_empire.py` | 19 | `galaxy._next_fleet_id = 1` | passing | Same. |
| `tests/integration/strategy/test_empire.py` | 26 | `galaxy._next_fleet_id = 1` | passing | Same. |
| `tests/integration/strategy/test_empire.py` | 37 | `galaxy2._next_fleet_id = saved_counter` | passing | Same. |
| `tests/integration/strategy/test_empire.py` | 45 | `galaxy._next_fleet_id = 1` | passing | Same. |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py` | 75 | `gal._state = GalaxyState(radius=300)` | passing | Already does the right thing — directly assigns `_state`. (This is the model the new shared fixture generalizes.) |

**Concrete error:**
```
AttributeError: 'Galaxy' object has no attribute '_state'
File "game/strategy/data/galaxy.py", line 75, in radius (setter)
    self._state.radius = value
```

### Pattern 2: Real `Galaxy(radius=N)` construction

**Total:** 24 files. All passing. **Out of scope** for PROJ-378 — these are correct usage. Listed for completeness:

`tests/performance/bench_galaxy_planet_star.py`, `tests/integration/strategy/test_save_round_trip.py`, `tests/integration/strategy/test_save_round_trip_phase4.py`, `tests/integration/strategy/test_save_round_trip_phase3.py`, `tests/unit/strategy/data/test_galaxy_protocols.py`, `tests/unit/strategy/engine/test_transfer_order.py`, `tests/integration/gameplay_loop/conftest.py`, `tests/integration/colonization/conftest.py`, `tests/integration/strategy/test_superweapon_integration.py`, `tests/unit/strategy/data/test_galaxy_system_generator.py`, `tests/unit/strategy/engine/test_game_initializer.py`, `tests/unit/strategy/data/test_galaxy_warp_generator.py`, `tests/unit/strategy/services/test_system_destroyer.py`, `tests/integration/strategy/test_galaxy_gen.py`, `tests/integration/strategy/test_warp_logic_rework.py`, `tests/integration/strategy/test_galaxy_generation_storms.py`, `tests/unit/strategy/data/test_storm.py`, `tests/integration/strategy/test_stabilizer_blocks_superweapon.py`, `tests/integration/strategy/test_system_destruction.py`, `tests/unit/strategy/data/test_fleet_id_global.py`, `tests/unit/strategy/data/test_galaxy.py`, `tests/integration/strategy/test_planet_serialization.py`, `tests/integration/strategy/test_planet_gen.py`, `tests/integration/save_load/test_roundtrip_galaxy.py`.

### Pattern 3: `MockGalaxy` test doubles

**Total:** 6 files (UI test fixtures + colonization tests). **Out of scope** — these are hand-rolled mocks for non-Galaxy tests, not the same pattern.

`tests/integration/colonization/test_planet_specific_colonization.py`, `tests/integration/ui/test_build_queue_formatting.py`, `tests/integration/ui/test_build_queue_drag_drop.py`, `tests/integration/ui/build_queue_screen/*.py`, `tests/integration/strategy/test_economy_e2e.py`, `tests/integration/strategy/test_command_handlers.py`, `tests/integration/strategy/test_fleet_navigation_consistency.py`.

## What each failing test class needs

### `TestGalaxyUnregisterPlanet` (test_galaxy_cleanup.py:55-157, 5 tests)
- **Method exercised:** `galaxy.unregister_planet(planet)` at `galaxy.py:205-207`, which delegates to `self._registry.unregister_planet(planet)`.
- **State required:** `_state` (so property forwarders for `systems`, `name_map`, `planets_by_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`, `fleets_by_id` resolve), and `_registry` (the `GalaxyEntityRegistry(state)` service that owns the unregister logic).
- **Stub coverage:** `make_galaxy_stub()` provides both. ✅

### `TestGalaxyRemoveWarpLink` (test_galaxy_cleanup.py:160-239, 4 tests)
- **Method exercised:** `galaxy.remove_warp_link(a, b)` at `galaxy.py:209-232`, which reads `self._state.name_map` and `self._state.global_hex_warp_points` directly. **Not a service delegation** — it's still inline on Galaxy.
- **State required:** `_state` only.
- **Stub coverage:** `make_galaxy_stub()` provides `_state` + extras. ✅

### `TestGalaxyGetAllFleetsInSystem` (test_galaxy_cleanup.py:242-366, 6 tests)
- **Method exercised:** `galaxy.get_all_fleets_in_system(system, empires)` at `galaxy.py:238-240`, which delegates to `self._spatial.get_all_fleets_in_system(...)`.
- **State required:** `_state` + `_spatial`.
- **Stub coverage:** `make_galaxy_stub()` provides both. ✅

## Performance: how heavy is `Galaxy.__init__`?

Measured on this dev box (Windows 11, Python 3.13.13):

| Operation | Time | Notes |
|---|---|---|
| Cold import `from game.strategy.data.galaxy import Galaxy` | **118 ms** | One-shot per process; pytest amortizes across the test session. |
| First `Galaxy(radius=100)` | **39 ms** | Includes JSON loads (NameRegistry, StormGenerator), image registry init, generator init. |
| Subsequent `Galaxy(radius=100)` (avg over 10) | **33 ms** | Steady-state cost — JSON re-reads dominate. |

Risk R5 in PROJ-372 design.md called this out explicitly:

> "**R5: `Galaxy.__init__` is heavy** (loads JSON, instantiates 4 generators, 4 services). Tests that construct `Galaxy()` pay this cost. Mitigation: PROJ-372 doesn't change this in scope; future work could add a `Galaxy.empty()` factory that lazy-loads, but that's out of scope. Document, don't fix."

This effectively answers the brief's question "Could the legacy `Galaxy.__new__` pattern have been a perf optimization, or just a test-isolation pattern?" — **both**. It dodges 33 ms of disk I/O per test setup AND avoids loading registries the test doesn't exercise. The shared `make_galaxy_stub()` preserves both wins.

## Existing fixture infrastructure check

There is **no existing `tests/fixtures/galaxy_fixtures.py` or `tests/unit/strategy/data/conftest.py`** — both new files are clean additions.

The closest existing precedent is `tests/integration/strategy/test_fleet_registration_lifecycle.py:62-80`, which already does the post-PROJ-372 stub manually inline (with `gal._state = GalaxyState(radius=300)` + manual `_registry` / `_spatial` wiring). That's exactly the pattern PROJ-378 generalizes into a shared factory.

PROJ-279's `tests/fixtures/test_scenarios.py::patch_spec_compiler_to_delegate_to_mock_scenario` is a near-precedent for "shared test-helper module accessed across `tests/unit/` and `tests/integration/`" — confirms the cross-tree import works fine.

## Closing observations

- **`_ensure_state()` is technically unused after PROJ-378 ships.** The shared fixture sets `_state` directly, so no test reaches `_ensure_state()`. Logged as a future cleanup opportunity in `decisions.md`. Out of scope for PROJ-378 (test-only project).
- **Phase 1 is the ~99% value delivery.** Phase 2 is consistency + sweep + optional doc note; if time pressure forces a single phase, Phase 1 alone gets the 15 errors fixed.
- **Risk of breakage during migration is near-zero.** Each test fixture is a self-contained block; the `make_galaxy_stub()` substitution is a 5-line change per fixture. Tests that already pass (`test_empire.py`, `test_fleet_registration_lifecycle.py`) get a syntactic refactor, not a semantic change.
