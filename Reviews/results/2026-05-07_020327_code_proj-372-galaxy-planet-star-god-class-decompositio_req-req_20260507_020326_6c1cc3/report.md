# PROJ-372 Galaxy/Planet/Star God-Class Decomposition — Review Report

**Review Type:** code
**Request ID:** req_20260507_020326_6c1cc3
**Review Mode:** full (no Coverage block; standard review)
**Scope:** 17+ files across strategy data/services, core, tests, docs
**Parent:** none
**Completed:** 2026-05-07

---

## Findings

### CRITICAL

*(none)*

### MAJOR

#### MAJ-001: Save round-trip test is synthetic-only — no pre-PROJ-372 fixture validation

- **File:** `tests/integration/strategy/test_save_round_trip.py:48-98`
- **Severity:** MAJOR

The five round-trip test functions construct galaxies in-memory using `Galaxy(radius=N)`, generate systems/planets/warp lanes programmatically, then assert `galaxy.to_dict()` → `Galaxy.from_dict()` → `to_dict()` identity. While this validates the current path end-to-end, it does NOT exercise any pre-PROJ-372 saved game file. A save created before this refactor series (e.g., PROJ-368 through PROJ-372) could fail to load if a serialization mismatch was introduced in any of the 8 projects.

The per-phase round-trip tests (`test_save_round_trip_phase1.py` through `_phase4.py`) are noted as "kept for now" but their coverage is unclear. No binary `.sav` file (or its JSON equivalent) from a pre-refactor version is checked into the repo or generated in CI.

**Suggested remediation:** Add at minimum a golden-file test: generate a galaxy with a known seed, serialize to a checked-in JSON fixture, then verify `from_dict` reproduces it identically. This catches future serialization drift regardless of the refactor. Alternatively, use the `tests/system/` save fixtures if they exist and verify they round-trip.

#### MAJ-002: Galaxy.from_dict duplicates add_system registration logic

- **File:** `game/strategy/data/galaxy.py:316-349`
- **Severity:** MAJOR

`Galaxy.from_dict` directly writes to `galaxy._state.systems`, `galaxy._state.name_map`, then manually calls `galaxy._registry._register_zones_from_system(system)` and `galaxy._registry._rebuild_warp_point_index_for(system)`. This duplicates the logic in `GalaxyEntityRegistry.add_system()` (lines 40-45 of that file). If `add_system` is ever modified (e.g., a new index is added), `from_dict` will silently diverge and deserialized galaxies will have missing indexes.

Additionally, `from_dict` accesses private `_register_zones_from_system` and `_rebuild_warp_point_index_for` on the registry, bypassing the public API surface.

**Suggested remediation:** Replace the manual state-assignment + index-rebuild block with `galaxy._registry.add_system(system)` (or `galaxy.add_system(system)`, which is the facade method delegating to it). If `add_system` must not be called during deserialization for a specific reason, document it in a comment and add a `from_dict` acceptance test that verifies all indexes are populated.

#### MAJ-003: planet_to_dict serializes `tectonic_activity` with spelling mismatch

- **File:** `game/strategy/data/planet_serde.py:44`
- **Severity:** MAJOR

The Planet dataclass field is named `tectonic_activity` (missing the 'c' — misspelling of "tectonic"). The serialization writes `"tectonic_activity": planet.tectonic_activity` — matching the field name. This is internally consistent but the key in saved data is misspelled. If the field is ever renamed to the correct spelling without a save migration, all existing saves break.

This is a pre-existing issue not introduced by PROJ-372, but the serde extraction makes it more visible and worth flagging since a future cleanup could introduce a break.

**Suggested remediation:** Either document the misspelling as a permanent save-format decision in `PROJ-372/decisions.md`, or add a backward-compat alias in `from_dict_kwargs` (e.g., accept both `tectonic_activity` and `tectonic_activity` keys).

### MINOR

#### MIN-001: Galaxy._intercept created in __init__ is never used

- **File:** `game/strategy/data/galaxy.py:66`
- **Severity:** MINOR

`Galaxy.__init__` creates `self._intercept = InterceptCalculator(self._pathfinder)`, but no production code uses `galaxy._intercept`. The pathfinding shim's `_intercept_for(galaxy)` helper (line 60-67 of `pathfinding.py`) always creates a **new** `InterceptCalculator` wrapping `_pathfinder_for(galaxy)`, ignoring the pre-constructed instance entirely. The existing instance is technically dead code.

The `InterceptCalculator.calculate_intercept_point` also creates its own fresh calculator via the shim (line 121, 169 of `intercept_calculator.py`) when `galaxy` is supplied, again bypassing `galaxy._intercept`.

**Suggested remediation:** Either remove `self._intercept` and let `_intercept_for` remain the sole constructor, or update `_intercept_for` and `InterceptCalculator`'s shim routing to use `galaxy._intercept` when present (with the same `isinstance` guard used in `_pathfinder_for`).

#### MIN-002: Pathfinding shim migration not complete — 14 import sites remain

- **File:** `game/strategy/data/pathfinding.py:1-10`
- **Severity:** MINOR

The shim header claims "Phase 5 will delete these shims once all 80+ caller sites migrate to the service objects." The shim is still present and actively imported by 14 sites in `game/`:

- `game/strategy/engine/game_session.py` (lines 321, 340)
- `game/strategy/engine/superweapon_order_processor.py` (line 31)
- `game/strategy/engine/handlers/base.py` (line 20)
- `game/strategy/services/fleet_navigation_service.py` (lines 36, 206)
- `game/strategy/services/intercept_calculator.py` (lines 121, 169)
- `game/strategy/facade/slices/planet_slice.py` (line 66)
- `game/ui/screens/strategy_screen.py` (lines 436, 441, 446)
- `game/ui/screens/strategy_superweapons.py` (line 350)
- `game/ui/screens/strategy_colonization.py` (line 258)

The PROJ-372 plan states this cleanup is Phase 5 work. It has not been completed.

**Suggested remediation:** Either complete the migration as Phase 5 closeout work, or file a follow-up project (e.g., PROJ-376) to track it. The shim is functional and correct in the interim.

#### MIN-003: IStockpileHolder/IStagingYardHolder leak mutation surface through read-protocol naming

- **File:** `game/strategy/data/galaxy_protocols.py:124-176`
- **Severity:** MINOR

These two protocols are named as "read" protocols in the module docstring and PROJ-372 plan.md (G5), but their method signatures include mutation operations: `add_to_stockpile`, `consume_from_stockpile`, `add_to_staging_yard`, `remove_from_staging_yard`. The docstring notes "Planet currently satisfies this structurally. Capacity / conservation contract tests are PROJ-370's responsibility." — correctly scoping the ownership.

However, naming them as part of PROJ-372's "read side" creates ambiguity with PROJ-370's mutator protocols. `IPlanetMutator` already has `set_max_stockpile`, `add_staging_item`, `pop_staging_item` — overlapping but not identical surfaces.

**Suggested remediation:** Rename to `IStockpileAccessor` / `IStagingYardAccessor` to clarify they describe both read and constrained-write (not full mutability). Alternatively, split into pure-read and write variants if PROJ-370 consolidates all writes.

#### MIN-004: `remove_warp_link` directly mutates state bypassing services

- **File:** `game/strategy/data/galaxy.py:210-233`
- **Severity:** MINOR

`Galaxy.remove_warp_link` is the only production method on the Galaxy facade that directly manipulates `self._state.global_hex_warp_points` and `system.warp_points` (lines 218-232) rather than delegating to a service. It's allow-listed in the AST guard test and the rationale ("preserved as-is per Decision; not algorithmic enough to extract") is documented. However, this creates an asymmetry: all other index mutations go through `GalaxyEntityRegistry` or `GalaxyWarpGenerator`.

**Suggested remediation:** Acceptable as-is per the documented decision. If warp-point management grows in complexity, extract to a `GalaxyWarpLinkService` and route through it.

### INFO

#### INFO-001: Save round-trip field coverage — VERIFIED CLEAN

All 47 Planet fields are serialized in `planet_serde.planet_to_dict` (lines 31-80) and deserialized in `planet_from_dict_kwargs` (lines 83-185). Default values in `from_dict_kwargs` match the dataclass defaults. Transient cache fields (`_cached_*`) are correctly excluded.

All GalaxyState fields (`radius`, `systems`, `name_map`, `planets_by_id`, `fleets_by_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`, `global_hex_warp_points`, `zone_to_system`, `next_planet_id`, `next_fleet_id`) are correctly serialized in `Galaxy.to_dict` (lines 288-299) and deserialized in `Galaxy.from_dict` (lines 301-350). Spatial indexes are rebuilt during deserialization via entity registration calls.

Star fields (10 fields + intrinsic_abilities) are serialized in `Star.to_dict` (lines 94-111) and deserialized in `Star.from_dict` (lines 113-170). Spectrum is correctly serialized/deserialized via `Spectrum.to_dict`/`from_dict`.

StarSystem fields are serialized in `StarSystem.to_dict` (lines 99-115) and deserialized in `StarSystem.from_dict` (lines 117-153). Optional fields (`region_id`, `archetype`, `intrinsic_abilities`) are correctly conditional.

No fields were lost, renamed, or changed in type during the extraction.

#### INFO-002: Facade thinness — VERIFIED CLEAN

Galaxy (350 LOC): 23 public methods are 1-line delegations to services. The only methods exceeding 1 line: `__init__` (allow-listed), `remove_warp_link` (allow-listed, 16 statements), `to_dict`/`from_dict` (allow-listed), `create_vars_link` (6 statements, allow-listed as it cross-references warp generator + spatial index), `generate_warp_lanes` (allow-listed). All other facade methods are straight `self._registry.X(...)` / `self._spatial.X(...)` / `self._sys_gen.X(...)` calls.

Planet (297 LOC): All query methods (`active_abilities`, `is_ability_active`, `occupied_hexes`, `can_build_type`) are 1-line delegations to `PlanetQueryService`. `get_cached_habitability_multiplier` is a 4-statement delegation to the habitability calculator. `to_dict`/`from_dict` are 1-line delegations to `planet_serde`. Stockpile/staging yard methods are protocol implementations (allow-listed).

Stars (181 LOC): `Star` data class only + re-exports + `__getattr__` shim for `StarGenerator` backward compatibility. No logic-bearing methods beyond `to_dict`/`from_dict`/`occupied_hexes`.

AST guard test (`test_no_method_body_over_5_loc.py`) correctly enforces the 5-statement ceiling with documented allow-lists for lifecycle/serde/protocol methods. All three files pass.

#### INFO-003: Service extraction soundness — VERIFIED CLEAN

- **PlanetQueryService** (82 LOC): Four static methods, all read-only. No mutation of planet state. No construction required.
- **PlanetHabitabilityService** (65 LOC): Implements `IHabitabilityCalculator`. Writes transient cache fields on Planet (PROJ-285 invariant — by design). Recomputation path is isolated in `_compute()`.
- **GalaxyPathfindingService** (217 LOC): Pure pathfinding algorithms over `IGalaxySystemGraph`. No side effects on galaxy state. All graph access through the protocol surface.
- **InterceptCalculator** (197 LOC): Calculates intercept points via pathfinding queries. No galaxy state mutation. Duck-typing adapter (`_ChaserProxy`) for Fleet/NavigationState is clean.
- **Spectrum** (74 LOC): Pure dataclass with serialization. No domain dependencies.
- **StarGenerator** (471 LOC): Star construction logic. Late-imports `get_star_generation_config()` to avoid circular deps. All state mutation is on newly-constructed Star objects.
- **spectrum_math** (155 LOC): Pure physics/math primitives. Zero game-layer imports. Correctly placed in `core/`.

#### INFO-004: Pathfinding shim correctness — VERIFIED CLEAN

All 8 free functions in `pathfinding.py` are genuine 1-line forwarders to `GalaxyPathfindingService` / `InterceptCalculator`. The `_pathfinder_for` helper correctly reuses `galaxy._pathfinder` when it is a `GalaxyPathfindingService` instance. The `_intercept_for` helper correctly wraps the same pathfinder instance.

`InterceptCalculator.calculate_intercept_point` routes through the shim (`from game.strategy.data import pathfinding as _pf_shim`) when `galaxy` is supplied (lines 121, 169), ensuring test patches of `pathfinding.find_hybrid_path` / `pathfinding.project_fleet_path` still take effect.

No callers were observed that should have been migrated but weren't — all 14 remaining import sites are part of the Phase 5 cleanup scope.

#### INFO-005: PROJ-370 protocol integration — VERIFIED CLEAN

`PlanetQueryService` (PROJ-372) is purely read-only. `PlanetWriteService` (PROJ-370) owns all 16 Planet write surfaces via `IPlanetMutator`. No overlap or conflict.

`IStockpileHolder` and `IStagingYardHolder` (PROJ-372) describe the Planet surface for stockpile/staging operations including constrained-write methods (add/consume/remove). PROJ-370's `IPlanetMutator` has `set_max_stockpile`, `add_staging_item`, `pop_staging_item` — a slightly different but complementary surface. The PROJ-372 protocols are lower-level (per-item), while PROJ-370's mutator methods are higher-level (batch operations). No collision.

`IHabitabilityCalculator` is injectable via `set_default_planet_habitability_service` on `ApplicationContext` (PROJ-258 pattern). Default wiring is lazy (planet.py:178-185), falling back to `PlanetHabitabilityService()` when none is registered.

#### INFO-006: GalaxyState extraction — VERIFIED CLEAN

`GalaxyState` (65 LOC) is a clean dataclass holding 11 mutable indexes + 2 ID counters + `radius`. All 11 fields are `Dict` types with appropriate type parameters. No methods that could be mistaken for business logic.

The four PROJ-173-Phase-2 delegates (`GalaxyEntityRegistry`, `GalaxySpatialIndex`, `GalaxyWarpGenerator`, `GalaxySystemGenerator`) all receive `GalaxyState` at construction time and access its fields directly. They no longer hold `_galaxy: Galaxy` back-references, breaking the circular aliasing.

No mutation entry points leak through the state object — all fields are plain dicts and ints, and the services that manipulate them are the intended owners.

#### INFO-007: General quality — VERIFIED CLEAN

- **Layering:** No violations found. All new files import downward within the architecture (strategy → core, strategy → strategy). No strategy→UI imports. No core→strategy imports.
- **Broad except:** None found in new scope files without the required `# Intentional broad catch: <reason>` comment. The only broad catches in scope exist in the round-trip test (lines 82, 95) and are properly annotated.
- **Return type annotations:** All public methods on new service classes have return type annotations. The `IGalaxySystemGraph` protocol signatures use `Optional["StarSystem"]` correctly. The `IStockpileHolder`/`IStagingYardHolder` protocols are properly typed.
- **LOC ceilings:** All three god-class files are under their ceilings (galaxy=350, planet=297, stars=181 vs ceilings of 350/350/280). All 11 new service/data files are under their per-file ceilings. The LOC ceiling test (`test_galaxy_planet_star_loc_ceilings.py`) correctly enforces these with tight constants.
- **Performance:** No performance regression flags. The lazy-default pattern in `Planet.get_cached_habitability_multiplier` adds one `get_default_*` call per lookup (cached per-turn), which is negligible.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR    | 3 |
| MINOR    | 4 |
| INFO     | 7 |

The god-class decomposition is sound. Save format is preserved — all 47 Planet fields, all GalaxyState indexes, all Star fields, and all StarSystem fields serialize and deserialize identically. The three facades are genuinely thin (1-line delegations for non-lifecycle methods, enforced by AST guard). Extracted services are cleanly separated by responsibility, with no mutation leakage from read-side services.

The primary risk (MAJ-001) is the absence of a pre-refactor save fixture in the round-trip test — the test validates the current path but doesn't guard against cumulative format drift across the 8-project sequence.
