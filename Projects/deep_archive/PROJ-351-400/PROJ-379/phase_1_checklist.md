# Phase 1: TDD-first hand-built fixture builder

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-379 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none — first phase
**Review Mode:** standard
**Files (planned):**
- `tests/integration/strategy/test_save_round_trip.py` (modify — failing tests added FIRST)
- `tests/integration/strategy/test_golden_fixture_field_coverage.py` (NEW — failing test added FIRST)
- `tests/fixtures/saves/_build_galaxy_fixture.py` (NEW — implementation)
- `tests/fixtures/saves/galaxy_proj372_baseline.json` (regenerated)
- `tests/fixtures/saves/galaxy_proj372_populated.json` (regenerated)

**Objective:** Replace the generation-then-normalize capture script with a hand-built fixture builder, **TDD-first**: byte-determinism + field-coverage + checked-in-fixture-vs-builder-output tests added first and confirmed FAILING (or erroring on missing import) before any implementation lands. Then implement `_build_galaxy_fixture.py` and regenerate JSONs until all tests pass.

---

## Reading

- [x] Read `Projects/active_projects/PROJ-379/plan.md`, `design.md`, `decisions.md` end-to-end.
- [x] Read `tests/fixtures/saves/_capture_baseline.py` end-to-end — the file being replaced.
- [x] Read `tests/fixtures/galaxy_fixtures.py::make_galaxy_stub` (PROJ-378 starting point).
- [x] Read `tests/fixtures/strategy_entities.py` for `create_test_*` factory patterns.
- [x] Read `tests/integration/strategy/test_save_round_trip.py` (existing 7 tests + `_build_minimal_planet` at lines 32-40, the `register_planet` + `system.planets.append` pattern at lines 60-61).
- [x] Read `game/strategy/data/planet.py` (47-field Planet dataclass).
- [x] Read `game/strategy/data/planet_serde.py::planet_to_dict` (the function the AST guard walks).
- [x] Read `game/strategy/data/star_system.py` (StarSystem `__init__`, `to_dict`, `from_dict`).
- [x] Read `game/strategy/data/galaxy_entity_registry.py:85-89` — `register_planet` assigns ID + indexes; **does NOT append to `system.planets`**. Caller must append explicitly.

---

## Tasks

### Task 1.1: Add the failing byte-determinism tests (TDD red) [Simple]
**File:** `tests/integration/strategy/test_save_round_trip.py`
**Tests:** `pytest tests/integration/strategy/test_save_round_trip.py::test_baseline_fixture_is_byte_deterministic tests/integration/strategy/test_save_round_trip.py::test_populated_fixture_is_byte_deterministic --override-ini="addopts=" -v`

- [x] Add import at top: `from tests.fixtures.saves._build_galaxy_fixture import build_baseline, build_populated`. **This will fail at collection** because `_build_galaxy_fixture.py` does not yet exist — confirm the failure mode is `ModuleNotFoundError` or similar, not a deeper bug.
- [x] Add `test_baseline_fixture_is_byte_deterministic`:
  ```python
  def test_baseline_fixture_is_byte_deterministic() -> None:
      """PROJ-379: re-running build_baseline() in the same process produces byte-identical output."""
      a = json.dumps(build_baseline(), indent=2, sort_keys=True)
      b = json.dumps(build_baseline(), indent=2, sort_keys=True)
      assert a == b
  ```
- [x] Add `test_populated_fixture_is_byte_deterministic` — mirror with `build_populated`.
- [x] Add `test_committed_baseline_matches_builder_output`:
  ```python
  def test_committed_baseline_matches_builder_output() -> None:
      """PROJ-379: the checked-in JSON must equal builder output exactly.

      Catches the 'developer changed the builder, forgot to re-commit the JSON' case.
      """
      committed = (_FIXTURE_DIR / "galaxy_proj372_baseline.json").read_text()
      generated = json.dumps(build_baseline(), indent=2, sort_keys=True) + "\n"
      assert committed == generated
  ```
- [x] Add `test_committed_populated_matches_builder_output` — mirror with populated.
- [x] Run focused tests; **verify** all 4 new tests fail (collection error from missing module is acceptable).

**Notes:** Phase 2 adds a cross-process / `PYTHONHASHSEED=random` subprocess test on top of these in-process checks. The two together cover G1.

### Task 1.2: Add the failing field-coverage guard (TDD red) [Medium]
**File:** `tests/integration/strategy/test_golden_fixture_field_coverage.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_golden_fixture_field_coverage.py --override-ini="addopts=" -v`

- [x] Create new file with module docstring referencing PROJ-379 and the `decisions.md` skiplist row.
- [x] **Use `planet_to_dict` directly** to compute the emitted-keys set and the per-field default baseline (NOT a `dataclasses.fields()` introspection — see `decisions.md` row "Phase 2 guard pattern: serialized-baseline, not dataclass-defaults" for rationale). Implementation outline:
  ```python
  import json
  from pathlib import Path
  from game.core.hex_math import HexCoord
  from game.strategy.data.planet import Planet, PlanetType
  from game.strategy.data.planet_serde import planet_to_dict

  _FIXTURE_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "saves"

  # Skiplist documented in PROJ-379 decisions.md row 4. image_id and
  # image_rotation are intentionally normalized to deterministic placeholders.
  _SKIP_KEYS = frozenset({"image_id", "image_rotation"})


  def _minimal_planet() -> Planet:
      """Construct a Planet with required fields only; all default-valued fields fall through."""
      return Planet(
          name="_baseline", location=HexCoord(0, 0), orbit_distance=1,
          mass=1.0, radius=1.0, surface_area=1.0, density=1.0,
          surface_gravity=1.0, surface_pressure=0.0, surface_temperature=0.0,
          surface_water=0.0, tectonic_activity=0.0, magnetic_field=0.0,
          # planet_type defaults to BARREN per Planet dataclass.
      )


  def _serialized_defaults() -> dict[str, object]:
      """Return {key: default_serialized_value} per planet_to_dict applied to a minimal Planet.

      This handles the enum-name serialization mismatch (PlanetType.BARREN -> "BARREN")
      and the default_factory mutables ([], {}) correctly — the serializer is the
      single source of truth.
      """
      return planet_to_dict(_minimal_planet())


  def _emitted_keys() -> set[str]:
      """Return the set of keys planet_to_dict emits."""
      return set(_serialized_defaults().keys())


  def test_populated_fixture_exercises_every_planet_field() -> None:
      """Every key emitted by planet_to_dict (modulo skiplist) appears with a non-default value."""
      emitted = _emitted_keys() - _SKIP_KEYS
      defaults = _serialized_defaults()
      fixture = json.loads((_FIXTURE_DIR / "galaxy_proj372_populated.json").read_text())

      planets = []
      for sys_entry in fixture["systems"]:
          planets.extend(sys_entry["system"].get("planets", []))

      assert planets, "PROJ-379: populated fixture has zero planets — builder bug."

      missing = []
      for key in sorted(emitted):
          default = defaults[key]
          if not any(p.get(key, default) != default for p in planets):
              missing.append(key)

      assert not missing, (
          f"PROJ-379 field-coverage guard: planet_to_dict emits these keys but no planet "
          f"in galaxy_proj372_populated.json has a non-default value for them: {missing}. "
          f"Update tests/fixtures/saves/_build_galaxy_fixture.py::build_populated() to "
          f"populate them. See PROJ-379 decisions.md."
      )
  ```
- [x] Run focused test; **verify** it fails because either (a) the populated fixture file does not yet match the new builder shape, or (b) it asserts on missing fields. Either failure mode is acceptable for TDD red.

**Notes:** Notice the path is `parent.parent.parent / "fixtures" / "saves"` — that already starts from `tests/integration/strategy/test_<file>.py` so three `parent` calls land in `tests/`, then `"fixtures" / "saves"` lands in `tests/fixtures/saves/`. (Earlier draft incorrectly added a `"tests"` segment, which would resolve to `tests/tests/fixtures/saves/`. Codex caught this in arc01_002.)

### Task 1.3: Implement `build_baseline()` (TDD green for some tests) [Medium]
**File:** `tests/fixtures/saves/_build_galaxy_fixture.py` (NEW)
**Tests:** Tasks 1.1 + 1.2 tests

- [x] Create file with module docstring: PROJ-379 closes PROJ-377 MIN-002; hand-built fixtures are deterministic by construction; refer to `Projects/active_projects/PROJ-379/design.md` for rationale.
- [x] Imports: `from __future__ import annotations`, `import json`, `from pathlib import Path`, `from game.core.hex_math import HexCoord`, `from game.strategy.data.galaxy import Galaxy`, `from game.strategy.data.planet import Planet, PlanetType`, `from game.strategy.data.star_system import StarSystem, WarpPoint`, `from tests.fixtures.galaxy_fixtures import make_galaxy_stub`.
- [x] Define `_FIXTURE_DIR = Path(__file__).resolve().parent`.
- [x] Implement `build_baseline() -> dict`:
  - `galaxy = make_galaxy_stub(radius=30)`.
  - Hand-build 5 `StarSystem` instances at fixed `HexCoord(q, r)` coordinates with explicit names. `StarSystem.__init__(name, global_location, stars=[])` — empty stars are acceptable for the round-trip baseline (stars are an existing concern; the decorated planet fixture exercises full coverage).
  - Add 4 mutual warp links (MST: A-B, A-C, B-D, C-E) by appending `WarpPoint(destination_id=..., location=HexCoord(...))` to each system's `warp_points` list.
  - Register each system: `galaxy._registry.add_system(system)`.
  - Return `galaxy.to_dict()`.
- [x] Run tests from Task 1.1; the in-process determinism tests should now pass for baseline. Round-trip identity test for baseline (`test_round_trip_golden_baseline_fixture`) will fail until JSON is regenerated in Task 1.5.

**Notes:** The plan.md decisions.md row "PYTHONHASHSEED-immune build" applies: do NOT iterate any `set` to populate ordered fields. Use lists/tuples explicitly.

### Task 1.4: Implement `build_populated()` with decorated planet (TDD green for field-coverage) [Medium]
**File:** `tests/fixtures/saves/_build_galaxy_fixture.py`
**Tests:** Tasks 1.1 + 1.2 tests

- [x] Implement `build_populated() -> dict`:
  - `galaxy = make_galaxy_stub(radius=50)`.
  - Hand-build 10 `StarSystem` instances at fixed coordinates with explicit names.
  - For 8 of the 10, hand-build 1-2 `Planet` instances. **For each planet:**
    1. Construct via direct `Planet(**fields)` with explicit values mirroring `_build_minimal_planet`'s pattern at `tests/integration/strategy/test_save_round_trip.py:32-40`.
    2. **Append explicitly:** `system.planets.append(planet)`.
    3. **Register:** `galaxy._registry.register_planet(system, planet)` (assigns id + indexes; does NOT append — that's why step 2 is required).
  - **One explicitly-decorated owned planet** (e.g., system 9's first planet) MUST exercise every Planet field exposed by `planet_to_dict` with a non-default value (modulo `image_id`/`image_rotation` skiplist). The Phase 2 guard will fail with a per-field list if any key is missed; iterate until green. Required non-default fields per `planet_serde.py:31-80`:
    - `owner_id = 1`
    - `atmosphere = {"O2": 0.21, "N2": 0.78, "CO2": 0.01}`
    - `deposits = {"metals": {"yield": 100.0, "depleted_at": 50.0}}`
    - `stockpile = {"metals": 50.0, "organics": 30.0}`
    - `max_stockpile = {"metals": 200.0, "organics": 100.0}`
    - `staging_yard = [...]` (one minimal entry)
    - `max_staging_mass = 1000.0`
    - `facilities = [PlanetaryFacility(...)]` (one entry)
    - `populations = [SpeciesPopulation(race_id="human", count=1000, happiness=0.8)]`
    - `construction_queue = [{"design_id": "test_ship", "type": "ship", "turns_remaining": 5.0}]`
    - `construction_queue_paused = True`
    - `image_id = "_fixture_planet_<id>.png"` (deterministic placeholder per skiplist)
    - `image_rotation = 0.0`
    - `radius_hexes`, `energy`, `energy_capacity`, `energy_generation`, `atmosphere_target`, `gravity_target`, `gravity_original`, `water_target`, `radiation_shielding`, `radiation_shielding_target`, `orders`, `species_configs`, `intrinsic_abilities` — all populated with non-default values.
  - Add 6-9 warp links (MST + a few density edges) — explicit `WarpPoint(destination_id, HexCoord(...))` constructor calls.
  - Register systems via `galaxy._registry.add_system`; for each planet, `system.planets.append(planet)` then `galaxy._registry.register_planet(system, planet)`.
  - Return `galaxy.to_dict()`.
- [x] **Verify (sanity check before running the AST guard):**
  - `sum(len(s["system"].get("planets", [])) for s in d["systems"])` equals the expected planet count from the builder (catches "registered but not appended" bug).
  - Decorated planet's serialized form has every required non-default value.
- [x] Run Task 1.2 field-coverage test; iterate the decorated planet until it passes.

**Notes:**

### Task 1.5: Add `__main__` entry; regenerate JSONs (TDD green for committed-fixture tests) [Simple]
**File:** `tests/fixtures/saves/_build_galaxy_fixture.py`
**Tests:** Tasks 1.1 + 1.2 + existing round-trip identity tests in `test_save_round_trip.py`

- [x] Add `def main() -> None:` calling `build_baseline()` + `build_populated()`, dumping each via `json.dump(d, f, indent=2, sort_keys=True)` followed by a trailing newline (matching `read_text() == json.dumps(...) + "\n"` shape from Task 1.1's committed-vs-builder test).
- [x] Add `if __name__ == "__main__": main()`.
- [x] Run: `python tests/fixtures/saves/_build_galaxy_fixture.py`. Both fixture JSONs regenerated.
- [x] Run all Phase 1 tests + the existing 5 synthetic round-trip tests in `test_save_round_trip.py`. **Verify:** all 7 existing + 4 new byte-determinism + 1 new field-coverage = 12 tests pass.
- [x] **Verify (in-process determinism):** `python tests/fixtures/saves/_build_galaxy_fixture.py && md5sum tests/fixtures/saves/*.json && python tests/fixtures/saves/_build_galaxy_fixture.py && md5sum tests/fixtures/saves/*.json` — hashes match across the two invocations.

**Notes:**

### Task 1.6: Run sharded suite + commit Phase 1 [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded green; pass count = baseline + 5 (4 byte-determinism in `test_save_round_trip.py` + 1 field-coverage in `test_golden_fixture_field_coverage.py`).
- [x] `git status --short` confirms only Phase 1 files dirty.
- [x] Commit message: `PROJ-379 phase 1: TDD-first hand-built deterministic golden-save fixture builder`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All Phase 1 task checkboxes checked.
- [x] `_build_galaxy_fixture.py` exists with `build_baseline`, `build_populated`, `__main__`.
- [x] Both JSON fixtures regenerated and committed.
- [x] 4 byte-determinism tests + 1 field-coverage test all pass.
- [x] Existing 7 round-trip tests in `test_save_round_trip.py` still pass.
- [x] Re-running the script produces byte-identical JSON (verified by `md5sum`).
- [x] Sharded suite green.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 2.
