# PROJ-372 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files modified or created (grouped by phase)

### Phase 0: facade-delegate template + AST/protocol scaffolding

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/data/galaxy_protocols.py` | Production (new) | 0 | New protocol module: `IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`. Target ≤ 150 LOC. |
| `game/context.py` | Production (modify) | 0 | Add `get_default_planet_habitability_service()` / `set_default_planet_habitability_service()` accessors (PROJ-258 pattern). Initially returns `None` until Phase 2 lands the implementation; existing call sites (Planet.get_cached_habitability_multiplier) keep the late-import fallback during Phase 0-1. |
| `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` | Test (new) | 0 | AST guard: `galaxy.py` ≤ 689 (today's baseline; tightens each phase), `planet.py` ≤ 667, `stars.py` ≤ 770. Test starts permissive; tightens at each phase boundary. |
| `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` | Test (new) | 0 | AST guard: zero direct reads of `galaxy._global_hex_planets` / `galaxy._planet_to_system` / `galaxy._zone_to_system` / `galaxy._global_hex_warp_points` / `galaxy._global_hex_zones` outside `galaxy_entity_registry.py` / `galaxy_spatial_index.py` / `galaxy.py` itself. Initially captures current allowed list; tightens each phase. |
| `tests/perf/bench_galaxy_planet_star.py` | Test (new) | 0 | Perf baseline bench: 150-system / 600-planet synthetic galaxy; measure pathfinding (3 routes), spatial query (1000 lookups), habitability lookup (1000 calls). Captures pre-PROJ-372 baseline as JSON pinned in the test. |

### Phase 1: Star decomposition

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/data/stars.py` | Production (modify, shrink) | 1 | Today 770 LOC. Remove `Spectrum` (move to spectrum.py), remove `StarGenerator` (move to generation/star_generator.py), remove math constants (move to core/spectrum_math.py). Keep `StarType` enum + `Star` dataclass + `Star.occupied_hexes` + serde + the `intrinsic_abilities` field. Target ≤ 280 LOC. |
| `game/strategy/data/spectrum.py` | Production (new) | 1 | `Spectrum` dataclass + `get_total_output` + `to_dict` + `from_dict`. Target ≤ 80 LOC. |
| `game/strategy/generation/star_generator.py` | Production (new) | 1 | `StarGenerator` class relocated from `stars.py`. All 14 methods. Imports `kelvin_to_rgb` / Stefan-Boltzmann helpers / `_WAVELENGTHS` from `core/spectrum_math.py`. Target ≤ 500 LOC. |
| `game/core/spectrum_math.py` | Production (new) | 1 | `kelvin_to_rgb`, `stefan_boltzmann_luminosity`, `wien_peak_wavelength`, all `_KELVIN_*` and `WIEN_*` constants, `SOLAR_*` constants, `_WAVELENGTHS`. Target ≤ 200 LOC. |
| `game/strategy/data/galaxy.py` | Production (modify, import) | 1 | Update `from game.strategy.data.stars import StarGenerator, Star` to import `Star` from stars and `StarGenerator` from generation. |
| `game/strategy/data/galaxy_system_generator.py` | Production (modify, import) | 1 | Update `if TYPE_CHECKING` import for `StarGenerator` from new location. |
| Other `from game.strategy.data.stars import StarGenerator` callers | Production (modify, import) | 1 | Sweep — likely 0-2 sites; update import paths. |
| `tests/unit/strategy/data/test_stars.py` | Test (modify) | 1 | Existing tests for `Star` / `Spectrum` — split into `test_stars.py` (Star), `test_spectrum.py` (Spectrum), `test_star_generator.py` (StarGenerator) following the new file split. |
| `tests/unit/strategy/data/test_spectrum.py` | Test (new) | 1 | Spectrum unit tests. |
| `tests/unit/strategy/generation/test_star_generator.py` | Test (new) | 1 | StarGenerator unit tests. |
| `tests/unit/core/test_spectrum_math.py` | Test (new) | 1 | Pure-math tests for `kelvin_to_rgb`, Stefan-Boltzmann, Wien. |
| `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` | Test (modify) | 1 | Tighten `stars.py` LOC ceiling to ≤ 280. |

### Phase 2: Planet decomposition

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/data/planet.py` | Production (modify, shrink) | 2 | Move 4 query/calc methods (`active_abilities`, `is_ability_active`, `occupied_hexes`, `can_build_type`) to thin facade delegates. Convert `get_cached_habitability_multiplier` to a 1-line facade calling `ApplicationContext.get_default_planet_habitability_service()`. Keep all 47 dataclass fields, all stockpile / staging / order methods, `__eq__` / `__hash__` / `context_type`, serde. Target ≤ 350 LOC. |
| `game/strategy/services/planet_query_service.py` | Production (new) | 2 | `PlanetQueryService` class: `active_abilities`, `is_ability_active`, `occupied_hexes`, `can_build_type`, optional `total_pressure_atm`. All static methods or class methods. Target ≤ 250 LOC. |
| `game/strategy/services/planet_habitability_service.py` | Production (new) | 2 | `PlanetHabitabilityService` implementing `IHabitabilityCalculator`: `get_cached(planet, race_registry, turn) -> float`. Wraps `planet_habitability_multiplier` from `colony_output.py`. Manages cache fields on the planet. Target ≤ 200 LOC. |
| `game/context.py` | Production (modify) | 2 | Wire `set_default_planet_habitability_service(PlanetHabitabilityService())` at module import; the Phase-0-added accessors now have a real default implementation. |
| `tests/unit/strategy/data/test_planet.py` | Test (modify) | 2 | Existing tests for query/calc methods — point them at `PlanetQueryService` instead, with `Planet.is_ability_active(...)` integration tests proving the facade works. |
| `tests/unit/strategy/services/test_planet_query_service.py` | Test (new) | 2 | Per-method unit tests with stub planets (no facility loading). |
| `tests/unit/strategy/services/test_planet_habitability_service.py` | Test (new) | 2 | Service tests + acceptance test: register a stub `IHabitabilityCalculator` via context; `Planet.get_cached_habitability_multiplier` returns the stub's value (closes the "modders can't inject" complaint). |
| `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` | Test (modify) | 2 | Tighten `planet.py` LOC ceiling to ≤ 350. |

### Phase 3: Galaxy query/spatial-aggregation services

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/data/galaxy_state.py` | Production (new) | 3 | `GalaxyState` dataclass: `radius`, `systems`, `name_map`, `planets_by_id`, `fleets_by_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`, `zone_to_system`, `global_hex_warp_points`, `next_planet_id`, `next_fleet_id`. Target ≤ 150 LOC. |
| `game/strategy/data/galaxy.py` | Production (modify, shrink) | 3 | Replace plain attributes with `_state: GalaxyState`. Add `@property systems`, `name_map`, `planets_by_id`, `fleets_by_id` forwarding to `_state` (preserves external API). Move methods 3, 4, 5 (`_register_zones_from_system`, `_rebuild_warp_point_index`, `_rebuild_all_warp_point_indices`) into `GalaxySpatialIndex`. Move method 16 (`get_next_fleet_id`) into `GalaxyEntityRegistry`. Move method 21 (`remove_warp_link`) into `GalaxyWarpGenerator`. Move methods 26, 27 algorithmic body into `GalaxyWarpGenerator`. Target after Phase 3: ≤ 420 LOC (further reduction in Phase 4). |
| `game/strategy/data/galaxy_entity_registry.py` | Production (modify) | 3 | Switch `__init__(self, galaxy: 'Galaxy')` to `__init__(self, state: 'GalaxyState')`. Replace `self._galaxy.X` with `self._state.X` everywhere (fields renamed: `_planet_to_system` → `planet_to_system` etc.). Add `get_next_fleet_id` method. Target ≤ 250 LOC. |
| `game/strategy/data/galaxy_spatial_index.py` | Production (modify) | 3 | Switch to `_state: GalaxyState`. Receive `_register_zones_from_system`, `_rebuild_warp_point_index`, `_rebuild_all_warp_point_indices`. Target ≤ 250 LOC. |
| `game/strategy/data/galaxy_warp_generator.py` | Production (modify) | 3 | Add signature accepts `state: GalaxyState` for `generate_warp_lanes` / `create_warp_link` / `remove_warp_link` (so it can update `state.global_hex_warp_points` directly). No LOC growth budget. |
| `game/strategy/data/galaxy_system_generator.py` | Production (modify) | 3 | Update signatures to accept `state: GalaxyState` instead of `galaxy: Galaxy` for the generator entry points. No LOC growth budget. |
| `game/strategy/data/galaxy_protocols.py` | Production (modify) | 3 | Add `IGalaxySystemGraph`, `IGalaxySpatialQuery` protocol definitions actually used. |
| Various callers of `galaxy._global_hex_*` etc. | Production (modify) | 3 | Sweep for direct private-attr access; route through services. Verified zero outside `galaxy.py`/`galaxy_*.py` today (per AST guard added in Phase 0). |
| `tests/unit/strategy/data/test_galaxy.py` | Test (modify) | 3 | Existing tests touch `galaxy._planet_to_system` etc. — migrate to `galaxy._state.planet_to_system` or service calls. |
| `tests/unit/strategy/data/test_galaxy_state.py` | Test (new) | 3 | `GalaxyState` dataclass tests: default values, mutability, equality. |
| `tests/unit/strategy/data/test_galaxy_entity_registry.py` | Test (modify) | 3 | Migrate from `Galaxy()` fixture to `GalaxyState()` fixture (no JSON loading). |
| `tests/unit/strategy/data/test_galaxy_spatial_index.py` | Test (modify) | 3 | Same as above. |
| `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` | Test (modify) | 3 | Tighten `galaxy.py` LOC ceiling to ≤ 420 (final ≤ 350 hits at Phase 4). |
| `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` | Test (modify) | 3 | Tighten allowed-callers list as services take over. |

### Phase 4: Galaxy algorithmic services (pathfinding, intercept)

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/services/galaxy_pathfinding_service.py` | Production (new) | 4 | `GalaxyPathfindingService` accepting `IGalaxySystemGraph` + `GalaxyState`. Methods: `find_path_deep_space`, `find_path_interstellar`, `find_hybrid_path`, `find_nearest_system`, `get_system_at_hex`, `strip_start_hex`. Target ≤ 350 LOC. |
| `game/strategy/services/intercept_calculator.py` | Production (new) | 4 | `InterceptCalculator`: `project_fleet_path`, `calculate_intercept_point`, `_evaluate_intercept_candidates`, `_extract_chaser_info`, `_ChaserProxy`, `_ChaserProxyCapabilities`. Target ≤ 150 LOC. |
| `game/strategy/data/pathfinding.py` | Production (modify, shrink) | 4 | Each free function becomes a 1-line wrapper calling the equivalent service method. Marked `# DEPRECATED — see PROJ-372; deleted at Phase 5 close`. Emits `DeprecationWarning` on call. Target ≤ 60 LOC. |
| `game/strategy/data/galaxy.py` | Production (modify, shrink final) | 4 | Inject `_pathfinder` service in `__init__`. Final cleanup: every Galaxy public method is a 1-line facade. Target ≤ 350 LOC. |
| `game/context.py` | Production (modify) | 4 | Add `get_default_galaxy_pathfinding_service()` accessor. |
| `tests/unit/strategy/services/test_galaxy_pathfinding_service.py` | Test (new) | 4 | Per-method unit tests on a 3-system stub graph (acceptance test for goal G5 — closes "tests can't stub query layer"). |
| `tests/unit/strategy/services/test_intercept_calculator.py` | Test (new) | 4 | Intercept algorithm tests. |
| `tests/unit/strategy/data/test_pathfinding.py` | Test (modify) | 4 | Existing tests stay green via the 1-line wrappers; add a `DeprecationWarning` assertion. |
| `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` | Test (modify) | 4 | Tighten `galaxy.py` LOC ceiling to ≤ 350. |

### Phase 5: AST guards, perf bench, doc updates, final audit

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/data/pathfinding.py` | Production (DELETE) | 5 | Pathfinding free-function shims removed. Final import sweep — all 82 call sites must point at services. |
| `tests/unit/strategy/data/test_pathfinding.py` | Test (DELETE) | 5 | Replaced by `test_galaxy_pathfinding_service.py` (Phase 4) + `test_intercept_calculator.py` (Phase 4). |
| `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` | Test (modify) | 5 | Final tightening: `galaxy.py` ≤ 350, `planet.py` ≤ 350, `stars.py` ≤ 280. Add per-service LOC ceilings (≤ 500). |
| `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` | Test (modify) | 5 | Final tightening: zero direct reads of GalaxyState private indexes outside the registry/spatial-index services. |
| `tests/unit/strategy/data/test_no_method_body_over_5_loc.py` | Test (new) | 5 | AST guard: every method on `Galaxy`, `Planet`, `Star` (not on services) has body ≤ 5 LOC OR is a serde method (`to_dict`/`from_dict`/`__init__` allowed listed). |
| `tests/perf/bench_galaxy_planet_star.py` | Test (modify) | 5 | Re-run perf bench; assert within ±5% of Phase 0 baseline. |
| `tests/integration/strategy/test_save_round_trip.py` | Test (new) | 5 | Load 5 fixture saves; assert `to_dict() == loaded.to_dict()`. |
| `docs/systems/strategy_layer.md` | Documentation (modify) | 5 | Update to reflect new service surface. Update `> **Last verified:**` blockquote (per docs/03_CONVENTIONS.md §9). |
| `docs/02_PATTERNS.md` | Documentation (modify) | 5 | Add or extend the "Facade-Delegate Pattern" section to reference PROJ-372 as the canonical galaxy/planet/star example. |
| `docs/01_ARCHITECTURE.md` | Documentation (modify) | 5 | Update the strategy-layer service inventory. |
| `Projects/active_projects/PROJ-370/decisions.md` | Project doc (modify) | 5 | Backfill cross-link: PROJ-372 introduced 5 read protocols; PROJ-370 layers contract testing on top of them. |
