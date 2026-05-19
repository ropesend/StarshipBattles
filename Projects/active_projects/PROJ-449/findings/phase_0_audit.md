# PROJ-449 Phase 0 — Pre-flight audit (call-site footprint)

> Date: 2026-05-18 (executing agent: Group A — Claude on `group-a` branch)
> Baseline: 23368 tests passing, full sharded suite green at branch creation.

## Methodology

1. Raw `rg` counts for every legacy public-kwarg spelling in `tests/` and `game/`.
2. Constructor-context filter via Python script + multiline `Grep` (`ShipInstance\(` + 15-line trailing context).
3. Helper definition lookups for every helper named in raw matches (`_make_*`, `create_*`, `_ship`, etc.) to determine whether the helper:
   - constructs `ShipInstance(...)` / `Planet(...)` / `PlanetaryFacility(...)` directly with the legacy kwarg → **in scope**
   - constructs but uses a property-setter on the result (e.g. `ship.consumable_levels = X` at `turn_engine/conftest.py:58`) → **in scope (Phase 4 deletes that setter)**
   - returns a `MagicMock` or `SimpleNamespace` and the kwarg is just a parameter name on the mock factory → **out of scope (mock, never reaches the real constructor)**
   - targets `PlanetaryFacility` (where `consumable_levels` is still a public dataclass field per F-A-012 deferral) → **out of scope for PROJ-449**

## Section A — ShipInstance Phase-2/Phase-4 sweep set (kwargs that reach `ShipInstance.__init__`)

These files contain test code where `consumable_levels=` or `cargo_contents=` either (a) is passed to a literal `ShipInstance(...)` constructor — directly or via a local helper that does the literal constructor call — or (b) is set on the constructed ship via the legacy `@property.setter` shim that Phase 4 deletes.

| # | File | Sites | Path to constructor |
|---|------|-------|---------------------|
| 1 | `tests/unit/strategy/data/test_ship_instance_container_views.py` | `:25` (direct ctor in `_ship` helper at L20) + 7 call sites inside test bodies (L47, L55, L77, L85, L95, L103, L108) | Direct ShipInstance(...) ctor |
| 2 | `tests/unit/strategy/ship_instance/test_capacity_levels.py` | `:73, :108, :149, :209, :231, :254, :276` (7 direct ctor sites; one `:73` plus 6 elsewhere) | Direct ShipInstance(...) ctor |
| 3 | `tests/unit/strategy/ship_instance/test_convenience_methods.py` | `:46` (direct, inside ShipInstance ctor at L40) | Direct ShipInstance(...) ctor |
| 4 | `tests/unit/strategy/ship_instance/test_serialization.py` | `:237, :298` (2 direct ctors at L231, L292) | Direct ShipInstance(...) ctor |
| 5 | `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` | `:27` (direct ctor in local helper at L14) | Direct ShipInstance(...) ctor |
| 6 | `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | `:27, :29` (direct ctor in local helper at L15; both `consumable_levels=` and `cargo_contents=`) | Direct ShipInstance(...) ctor |
| 7 | `tests/integration/save_load/test_roundtrip_ships.py` | `:46, :56, :62` (passes kwargs to `create_test_ship_instance` which forwards through `**defaults` to `ShipInstance(...)`) | Helper passthrough |
| 8 | `tests/integration/strategy/turn_engine/conftest.py` + `tests/integration/strategy/turn_engine/test_resources.py` | conftest `:37`, tests `:23, :54` (passes to `create_mock_ship_instance` which constructs ShipInstance then calls `ship.consumable_levels = X` at conftest L58 — the property setter Phase 4 deletes) | Property-setter shim |

**Distinct files: 8** (treating the conftest+test_resources pair as one logical helper site since they share a helper). Far below the 25-file gate.

Phase 1 (`tests/fixtures/strategy_entities.py:318, 320`) is NOT counted here — it is the Phase-1 commit's scope.

### False positives confirmed out of scope (kwarg target is not ShipInstance)

- `tests/fixtures/cargo_mock_ship.py` — `make_cargo_mock_ship(cargo_contents=...)` returns a `MagicMock`; not a ShipInstance.
- `tests/unit/strategy/data/test_fleet_cargo_resources.py` — `_make_ship(cargo_contents=...)` thinly aliases `make_cargo_mock_ship` → MagicMock.
- `tests/integration/strategy/test_resource_transfer.py:20` — `_make_cargo_ship(cargo_contents=...)` returns a MagicMock; the `cargo_contents=` kwarg only seeds a dict on the mock.
- `tests/unit/strategy/data/test_facility_resource_tracking.py` (many sites) — all go to `_make_fuel_facility` which constructs `PlanetaryFacility` WITHOUT `consumable_levels=`, then sets `facility.consumable_levels = X` (the public dataclass field).
- `tests/unit/strategy/data/test_planetary_facility_characterization.py:105` — direct `PlanetaryFacility(consumable_levels=...)`. F-A-012 deferred; PlanetaryFacility's public field stays.
- `tests/unit/strategy/engine/test_resupply_engine.py` — uses `_make_fuel_facility` (same as above).
- `tests/integration/save_load/test_resupply_persistence.py:117, 238` — direct `PlanetaryFacility(consumable_levels=...)`; same F-A-012 deferral.
- `tests/integration/save_load/test_roundtrip_planet.py:86, 92` — `create_test_facility(consumable_levels=...)` → PlanetaryFacility public field.
- `tests/fixtures/saves/_build_galaxy_fixture.py:129` — direct `PlanetaryFacility(consumable_levels=...)`; F-A-012 deferred.

## Section B — Planet Phase-2/Phase-3 sweep set (kwargs that reach `Planet.__init__` or the legacy property setters)

| # | File | Sites | Path |
|---|------|-------|------|
| 1 | `tests/integration/strategy/test_save_round_trip_phase2.py` | `:38, :39, :40` (`_populated_planet()` helper at L15-57 does direct `Planet(stockpile=..., max_stockpile=..., staging_yard=...)`) | Direct Planet(...) ctor |
| 2 | `tests/integration/strategy/test_resource_transfer.py` | `:107, :128, :147, :169, :170, :193` (test sites pass `stockpile=` / `max_stockpile=` to `create_test_planet` which forwards via `**overrides` → `Planet(**defaults)`) | Helper passthrough |
| 3 | `tests/fixtures/saves/_build_galaxy_fixture.py` | `:115, :116` (`planet.max_stockpile = ...`, `planet.staging_yard = ...` — property setters Phase 3 deletes) | Property-setter shim |

**Distinct files: 3** (excluding Phase 1's `strategy_entities.py:425`). Well below the 15-file gate.

### Other tests that pass `stockpile=`/`max_stockpile=`/`staging_yard=` to `create_test_planet`

Spot-checked from the raw rg list. Confirmed Phase 2 will need to sweep these as helper-passthrough sites:
- `tests/unit/strategy/data/test_planet_stockpile.py`
- `tests/integration/test_empire_resource_aggregation.py` (via `create_test_empire` → `create_test_planet`)

Additional possible helper-passthrough sites (need Phase 2 walk-through but not gate-relevant):
- `tests/unit/strategy/test_habitability.py`
- `tests/unit/strategy/test_empire_economy_calculator.py`
- `tests/integration/strategy/test_treasury_panel_e2e.py`
- `tests/integration/strategy/test_habitability_on_economy.py`
- `tests/unit/strategy/engine/test_harvesting_engine.py`
- `tests/unit/strategy/engine/test_harvesting_engine_habitability.py`

Phase 2's job is to enumerate and migrate; Phase 0 only confirms the count fits the planned phase structure.

## Section C — Production-code call sites

`rg "ShipInstance\(|Planet\(|PlanetaryFacility\(" game/` cross-referenced with `consumable_levels=`, `cargo_contents=`, `stockpile=`, `max_stockpile=`, `staging_yard=`: **zero direct constructor sites in `game/`** pass any legacy public kwarg. Production code either uses the private spellings on construction or routes through manager APIs (`ship._resource_mgr.set_level(...)`, `planet.add_to_stockpile(...)`, etc.).

This is consistent with PROJ-436 having migrated production code to private spellings; only test fixtures retained the public names.

## Section D — Serde dependencies

`game/strategy/data/planet_serde.py`:

- **`planet_to_dict` (L26-77)**: reads via property names (`planet.stockpile`, `planet.max_stockpile`, `planet.staging_yard` at lines 50, 51, 52). After Phase 3 deletes the properties, the serializer must read directly from `_stockpile`, `_max_stockpile`, `_staging_yard`. **Phase 3 rewrite required.**
- **`planet_from_dict_kwargs` (L80-182)**: emits kwargs using legacy public names at lines 157-159: `stockpile=`, `max_stockpile=`, `staging_yard=`. After Phase 3 deletes the wrapper, `planet_from_dict_kwargs` must emit private spellings. **Phase 2 rewrite required (per plan.md).**

Save-format key names (`"stockpile"`, `"max_stockpile"`, `"staging_yard"` in the dict) stay unchanged — save backward-compatibility is preserved at the JSON level. Only the in-process kwarg names change.

## Section E — Fixture file site count

`tests/fixtures/strategy_entities.py`:

| Line | Function | Kwarg | Constructor target |
|------|----------|-------|---------------------|
| 140 | `create_test_facility` | `consumable_levels=` | `PlanetaryFacility(...)` (Task 1.1 keeps this — F-A-012 deferred) |
| 318 | `create_test_ship_instance` | `consumable_levels=` | dict-literal kwarg in `defaults = dict(...)`; unpacked via `ShipInstance(**defaults)` at L329 |
| 320 | `create_test_ship_instance` | `cargo_contents=` | same `defaults` dict |
| 425 | `create_test_empire` | `stockpile=` | passed to `create_test_planet` → `Planet(**defaults)` |

**4 sites confirmed.** No additional in-scope sites found.

## Section F — PROJ-443 Phase 5b cross-reference

PROJ-443 Phase 5b's audit-of-record (2026-05-17) reported 18 files for the ShipInstance sweep. My audit lands at **8 files** (Section A). The 10-file delta is explained by:

1. **F-A-012 deferral**: ~6 of the original 18 files were PlanetaryFacility sites. Those are now out of scope because the F-A-012 constructor-kwarg rename did not land. (Verified at `game/strategy/data/planetary_facility.py:32` where `consumable_levels` is still a public dataclass field.)
2. **MagicMock false positives**: PROJ-443's audit treated `cargo_mock_ship` / `_make_cargo_ship` / `_make_ship` (test_fleet_cargo_resources.py) as Phase-4 sites. They return MagicMock and never construct ShipInstance — out of scope.
3. **Manager-API migrations between 2026-05-17 and 2026-05-18**: a handful of intermediate projects (PROJ-444 through PROJ-447) appear to have migrated some ship-construction tests to manager APIs, shrinking the sweep.

The 8-file count is small enough that Phase 2 should land in a single commit; Phase 4 has minimal risk.

## Section G — Gate decision

- **Section A (ShipInstance sweep): 8 files ≤ 25** → **PROCEED clean**
- **Section B (Planet sweep): 3 files ≤ 15** → **PROCEED clean**
- **Section C (production): 0 sites** → clean
- **Section D (serde): confirmed 2 sites need Phase-2/3 rewrites; planned in plan.md**
- **Section E (fixture): 4 sites confirmed; matches plan.md exactly**

Phase 1 may begin. Wrapper retention rationale (PROJ-443 5b sized for 18 files) is now strictly over-budget — actual sweep is 8 files on the ShipInstance side and 3 on the Planet side, well within the planned phase structure.

## Phase 0 outputs

- This document (`Projects/active_projects/PROJ-449/findings/phase_0_audit.md`).
- No code changes.
- No new findings; existing findings (F-A-002/003/004/005/011, F-C-013/014/020) remain accurate.
