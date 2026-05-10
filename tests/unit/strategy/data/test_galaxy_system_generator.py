"""PROJ-334 Phase 1B: characterization tests for GalaxySystemGenerator.

Targets `game/strategy/data/galaxy_system_generator.py`. Pure-algorithm
characterization: hand-rolled fakes (no unittest.mock patching) per
PROJ-334 D-005. Tests pin BEHAVIOR, not implementation details.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import pytest

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.galaxy_system_generator import (
    GalaxySystemGenerator,
    _apply_intrinsic_abilities,
    _apply_system_archetype,
    _load_json_or_empty,
)


# ---------------------------------------------------------------------------
# Hand-rolled fakes (per D-005 — no unittest.mock)
# ---------------------------------------------------------------------------


class _FakeStar:
    def __init__(self, type_name: str = "G_TYPE"):
        self.star_type = _FakeStarType(type_name)
        self.intrinsic_abilities = {}


class _FakeStarType:
    def __init__(self, name: str):
        self.name = name


class _FakePlanetType:
    def __init__(self, name: str = "TERRAN"):
        self.name = name


class _FakePlanet:
    """Planet with attributes the generator + sort key require."""

    def __init__(self, name: str, orbit_distance: float, mass: float):
        self.name = name
        self.orbit_distance = orbit_distance
        self.mass = mass
        self.planet_type = _FakePlanetType()
        self.intrinsic_abilities = {}


class _FakeStarGenerator:
    def __init__(self, stars=None):
        self._stars = stars if stars is not None else [_FakeStar()]

    def generate_system_stars(self, system_name: str):
        # Return a fresh list per call to avoid shared mutation.
        return [_FakeStar(s.star_type.name) for s in self._stars]


class _FakePlanetGenerator:
    """Planet generator that returns a deterministic planet list."""

    def __init__(self, planets_factory=None):
        self._factory = planets_factory or (lambda system_name, stars: [])

    def generate_system_bodies(self, system_name: str, stars: list):
        return self._factory(system_name, stars)


class _FakeNamingRegistry:
    def __init__(self, names=None):
        self._names = list(names) if names else None
        self._counter = 0

    def get_system_name(self) -> str:
        if self._names:
            name = self._names[self._counter % len(self._names)]
            self._counter += 1
            return name
        self._counter += 1
        return f"System_{self._counter}"


class _FakeImageRegistry:
    pass


class _FakeStormGenerator:
    """Records calls and returns a canned storms list."""

    def __init__(self, storms_to_return=None):
        self._storms = storms_to_return or []
        self.calls: list[tuple] = []

    def generate_storms(self, system, blueprint_config, rng):
        self.calls.append((system.name, dict(blueprint_config), rng))
        return list(self._storms)


class _FakeGalaxy:
    """Minimal Galaxy with the surface generate_systems requires."""

    def __init__(self, radius: int = 2000):
        self.radius = radius
        self.systems: dict[HexCoord, Any] = {}
        self.registered_planets: list[tuple[Any, Any]] = []
        self.added_systems: list[Any] = []

    def add_system(self, system) -> None:
        self.systems[system.global_location] = system
        self.added_systems.append(system)

    def register_planet(self, system, planet) -> None:
        self.registered_planets.append((system, planet))


class _RecordingPlacementStrategy:
    """Placement strategy that returns scripted coords + records the rng identity."""

    def __init__(self, coords=None, fail_after=None):
        self._coords = list(coords or [])
        self._fail_after = fail_after  # None => never fail; int => fail forever after N successes
        self._call_count = 0
        self.recorded_rngs: list[Any] = []

    def sample_location(
        self, *, radius, existing_systems, min_dist, rng=None, spatial_index=None, max_attempts=1000
    ):
        self.recorded_rngs.append(rng)
        if self._fail_after is not None and self._call_count >= self._fail_after:
            return None
        if not self._coords:
            return None
        coord = self._coords[self._call_count % len(self._coords)]
        self._call_count += 1
        return coord


class _AlwaysFailPlacementStrategy:
    """Always returns None — exercises the saturation/failure-counter path."""

    def __init__(self):
        self.call_count = 0

    def sample_location(self, **kwargs):
        self.call_count += 1
        return None


class _LimitedSuccessPlacementStrategy:
    """Succeed N times then fail forever (exercises 'fewer than count' path)."""

    def __init__(self, success_coords):
        self._coords = list(success_coords)
        self._idx = 0

    def sample_location(self, **kwargs):
        if self._idx < len(self._coords):
            coord = self._coords[self._idx]
            self._idx += 1
            return coord
        return None


def _make_generator(*, storm_generator=None, star_generator=None, planet_generator=None,
                    naming=None) -> GalaxySystemGenerator:
    return GalaxySystemGenerator(
        star_generator=star_generator or _FakeStarGenerator(),
        planet_generator=planet_generator or _FakePlanetGenerator(),
        naming=naming or _FakeNamingRegistry(),
        image_registry=_FakeImageRegistry(),
        storm_generator=storm_generator,
    )


# ---------------------------------------------------------------------------
# _load_json_or_empty
# ---------------------------------------------------------------------------


class TestLoadJsonOrEmpty:
    def test_load_json_or_empty_returns_empty_dict_when_path_missing(self, tmp_path):
        missing = tmp_path / "does_not_exist.json"
        result = _load_json_or_empty(missing)
        assert result == {}

    def test_load_json_or_empty_narrows_to_dict_key_when_provided(self, tmp_path):
        data_file = tmp_path / "types.json"
        data_file.write_text(
            json.dumps({"planet_types": {"TERRAN": {"abilities": {}}}}),
            encoding="utf-8",
        )
        result = _load_json_or_empty(data_file, dict_key="planet_types")
        assert result == {"TERRAN": {"abilities": {}}}

    def test_load_json_or_empty_returns_full_data_when_no_dict_key(self, tmp_path):
        data_file = tmp_path / "raw.json"
        data_file.write_text(json.dumps({"a": 1, "b": 2}), encoding="utf-8")
        result = _load_json_or_empty(data_file)
        assert result == {"a": 1, "b": 2}


class TestLazyTypeCaches:
    def test_load_planet_types_caches_after_first_read(self, monkeypatch):
        from game.core.paths import Paths
        from game.strategy.data import galaxy_system_generator as mod

        calls = []

        def fake_load(path_value, dict_key=None):
            calls.append((path_value, dict_key))
            return {"TERRAN": {"abilities": {}}}

        monkeypatch.setattr(mod, "_PLANET_TYPES_CACHE", None)
        monkeypatch.setattr(mod, "_load_json_or_empty", fake_load)

        first = mod._load_planet_types()
        second = mod._load_planet_types()

        assert first is second
        assert first == {"TERRAN": {"abilities": {}}}
        assert calls == [(Paths.PLANET_TYPES_FILE, "planet_types")]

    def test_load_star_types_caches_after_first_read(self, monkeypatch):
        from game.core.paths import Paths
        from game.strategy.data import galaxy_system_generator as mod

        calls = []

        def fake_load(path_value, dict_key=None):
            calls.append((path_value, dict_key))
            return {"G_TYPE": {"abilities": {}}}

        monkeypatch.setattr(mod, "_STAR_TYPES_CACHE", None)
        monkeypatch.setattr(mod, "_load_json_or_empty", fake_load)

        first = mod._load_star_types()
        second = mod._load_star_types()

        assert first is second
        assert first == {"G_TYPE": {"abilities": {}}}
        assert calls == [(Paths.STAR_TYPES_FILE, "star_types")]

    def test_load_system_archetypes_caches_after_first_read(self, monkeypatch):
        from game.core.paths import Paths
        from game.strategy.data import galaxy_system_generator as mod

        calls = []

        def fake_load(path_value, dict_key=None):
            calls.append((path_value, dict_key))
            return {"archetype_chance": 0.5, "archetypes": {}}

        monkeypatch.setattr(mod, "_SYSTEM_ARCHETYPES_CACHE", None)
        monkeypatch.setattr(mod, "_load_json_or_empty", fake_load)

        first = mod._load_system_archetypes()
        second = mod._load_system_archetypes()

        assert first is second
        assert first == {"archetype_chance": 0.5, "archetypes": {}}
        assert calls == [(Paths.SYSTEM_ARCHETYPES_FILE, None)]


# ---------------------------------------------------------------------------
# _apply_intrinsic_abilities (idempotency / no-op branches)
# ---------------------------------------------------------------------------


class TestApplyIntrinsicAbilities:
    def test_apply_intrinsic_abilities_is_idempotent_when_entity_has_existing_abilities(self):
        # Entity with pre-set intrinsic_abilities must NOT be mutated.
        entity = _FakePlanet("Pre", 1.0, 1.0)
        entity.intrinsic_abilities = {"PreExisting": {"value": 99}}
        types_data = {"TERRAN": {"abilities": {"SomeAbility": {"min": 0, "max": 1}}}}

        _apply_intrinsic_abilities(
            [entity],
            types_data,
            lambda e: e.planet_type.name,
            rng=random.Random(42),
        )

        assert entity.intrinsic_abilities == {"PreExisting": {"value": 99}}

    def test_apply_intrinsic_abilities_is_noop_when_types_data_empty(self):
        entity = _FakePlanet("X", 1.0, 1.0)
        _apply_intrinsic_abilities(
            [entity],
            {},
            lambda e: e.planet_type.name,
            rng=random.Random(42),
        )
        assert entity.intrinsic_abilities == {}


# ---------------------------------------------------------------------------
# _apply_system_archetype (idempotency / void / chance branches)
# ---------------------------------------------------------------------------


class _FakeSystemForArchetype:
    def __init__(self, archetype=None):
        self.archetype = archetype
        self.intrinsic_abilities = {}


class TestApplySystemArchetype:
    def test_apply_system_archetype_is_idempotent_when_archetype_pre_set(self):
        # Pre-set archetype must be left untouched (scenario hand-craft).
        sys = _FakeSystemForArchetype(archetype="custom_scenario")
        # Force chance to 1.0 by using a deterministic rng — irrelevant since
        # the pre-set check fires first.
        _apply_system_archetype(sys, random.Random(1))
        assert sys.archetype == "custom_scenario"
        assert sys.intrinsic_abilities == {}

    def test_apply_system_archetype_is_noop_when_random_exceeds_chance(
        self, monkeypatch
    ):
        # Inject a controlled archetypes table with chance=0 so rng.random() > chance always.
        from game.strategy.data import galaxy_system_generator as mod

        monkeypatch.setattr(
            mod,
            "_SYSTEM_ARCHETYPES_CACHE",
            {
                "archetype_chance": 0.0,
                "archetypes": {"frontier": {"abilities": {}}},
            },
        )
        sys = _FakeSystemForArchetype()
        _apply_system_archetype(sys, random.Random(0))
        assert sys.archetype is None

    def test_apply_system_archetype_skips_void_archetype_key(self, monkeypatch):
        # When the only archetype is "void", the helper bails out without setting one.
        from game.strategy.data import galaxy_system_generator as mod

        monkeypatch.setattr(
            mod,
            "_SYSTEM_ARCHETYPES_CACHE",
            {
                "archetype_chance": 1.0,  # always roll
                "archetypes": {"void": {"abilities": {}}},
            },
        )
        sys = _FakeSystemForArchetype()
        _apply_system_archetype(sys, random.Random(0))
        assert sys.archetype is None


# ---------------------------------------------------------------------------
# GalaxySystemGenerator.generate_planets
# ---------------------------------------------------------------------------


class _FakeSystemForPlanets:
    def __init__(self, name: str, stars):
        self.name = name
        self.stars = list(stars)
        self.planets: list[Any] = []


class TestGeneratePlanets:
    def test_generate_planets_returns_early_when_system_has_no_stars(self):
        gen = _make_generator()
        galaxy = _FakeGalaxy()
        sys = _FakeSystemForPlanets("Empty", stars=[])

        gen.generate_planets(galaxy, sys, rng=random.Random(0))

        assert sys.planets == []
        assert galaxy.registered_planets == []

    def test_generate_planets_sorts_by_orbit_distance_then_negative_mass(self):
        # Three planets: same orbit_distance for two of them so the secondary
        # key (-mass) determines order. Heavier mass should come FIRST when
        # orbit distances tie.
        unsorted_planets = [
            _FakePlanet("Far", orbit_distance=10.0, mass=100.0),
            _FakePlanet("Heavy", orbit_distance=5.0, mass=900.0),
            _FakePlanet("Light", orbit_distance=5.0, mass=100.0),
        ]
        planet_gen = _FakePlanetGenerator(
            planets_factory=lambda name, stars: list(unsorted_planets)
        )
        gen = _make_generator(planet_generator=planet_gen)
        galaxy = _FakeGalaxy()
        sys = _FakeSystemForPlanets("Sol", stars=[_FakeStar()])

        gen.generate_planets(galaxy, sys, rng=random.Random(0))

        ordered_names = [p.name for p in sys.planets]
        assert ordered_names == ["Heavy", "Light", "Far"]

    def test_generate_planets_registers_each_planet_with_galaxy(self):
        planets = [
            _FakePlanet("A", 1.0, 1.0),
            _FakePlanet("B", 2.0, 1.0),
            _FakePlanet("C", 3.0, 1.0),
        ]
        planet_gen = _FakePlanetGenerator(
            planets_factory=lambda name, stars: list(planets)
        )
        gen = _make_generator(planet_generator=planet_gen)
        galaxy = _FakeGalaxy()
        sys = _FakeSystemForPlanets("Reg", stars=[_FakeStar()])

        gen.generate_planets(galaxy, sys, rng=random.Random(0))

        registered_names = [p.name for (_s, p) in galaxy.registered_planets]
        assert sorted(registered_names) == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# GalaxySystemGenerator.generate_storms
# ---------------------------------------------------------------------------


class _FakeSystemForStorms:
    def __init__(self, name: str = "Storm"):
        self.name = name
        self.storms: list[Any] = []


class TestGenerateStorms:
    def test_generate_storms_is_noop_when_storm_generator_is_none(self):
        gen = _make_generator(storm_generator=None)
        sys = _FakeSystemForStorms()
        gen.generate_storms(sys, blueprint_config={"storms": {}}, rng=random.Random(0))
        assert sys.storms == []

    def test_generate_storms_assigns_storms_when_storm_generator_present(self):
        canned = ["storm_a", "storm_b"]
        storm_gen = _FakeStormGenerator(storms_to_return=canned)
        gen = _make_generator(storm_generator=storm_gen)
        sys = _FakeSystemForStorms("Hot")

        gen.generate_storms(sys, blueprint_config={"storms": {"count": {"min": 1, "max": 2}}},
                            rng=random.Random(0))

        assert sys.storms == canned
        assert len(storm_gen.calls) == 1


# ---------------------------------------------------------------------------
# GalaxySystemGenerator.generate_systems — determinism contract
# ---------------------------------------------------------------------------


def _canonical_signature(systems) -> list[tuple[str, tuple[int, int]]]:
    """Sorted, hashable representation of a generated galaxy."""
    return sorted(((s.name, (s.global_location.q, s.global_location.r)) for s in systems))


class TestGenerateSystemsDeterminism:
    def test_generate_systems_with_seed_42_produces_canonical_galaxy(self):
        # MAJ-001 fix (review req_20260504_213455_95a42d): hardcode the
        # canonical signature so this test catches behavior drift, not
        # just count/uniqueness changes. Recorded by running once on
        # 2026-05-04 against generate_systems(count=5, radius=2000,
        # min_dist=100, rng=random.Random(42)) with FakeNamingRegistry
        # iterating Sol/Vega/Lyra/Orion/Cygnus/Draco. To regenerate
        # after an intentional behavior change: run this test, copy the
        # printed CANONICAL_SEED_42 line into CANONICAL_SEED_42 below.
        CANONICAL_SEED_42 = [
            ("Cygnus", (-1644, 1372)),
            ("Lyra", (771, 1033)),
            ("Orion", (1654, 233)),
            ("Sol", (-1086, -343)),
            ("Vega", (1016, -1581)),
        ]

        gen = _make_generator(
            naming=_FakeNamingRegistry(["Sol", "Vega", "Lyra", "Orion", "Cygnus", "Draco"]),
        )
        galaxy = _FakeGalaxy(radius=2000)

        result = gen.generate_systems(
            galaxy=galaxy,
            count=5,
            min_dist=100,
            rng=random.Random(42),
        )

        signature = _canonical_signature(result)

        assert signature == CANONICAL_SEED_42, (
            f"Generator output drifted under seed=42. Got {signature}; "
            f"expected {CANONICAL_SEED_42}. If this change was intentional, "
            f"update CANONICAL_SEED_42 in this test."
        )

    def test_generate_systems_with_seed_42_is_reproducible_across_two_runs(self):
        def run_once():
            gen = _make_generator(
                naming=_FakeNamingRegistry(
                    ["Sol", "Vega", "Lyra", "Orion", "Cygnus", "Draco"]
                ),
            )
            galaxy = _FakeGalaxy(radius=2000)
            return gen.generate_systems(
                galaxy=galaxy, count=5, min_dist=100, rng=random.Random(42)
            )

        sig1 = _canonical_signature(run_once())
        sig2 = _canonical_signature(run_once())
        assert sig1 == sig2

    def test_generate_systems_with_different_seeds_produces_different_galaxies(self):
        def run_once(seed: int):
            gen = _make_generator(
                naming=_FakeNamingRegistry(
                    ["Sol", "Vega", "Lyra", "Orion", "Cygnus", "Draco"]
                ),
            )
            galaxy = _FakeGalaxy(radius=2000)
            return gen.generate_systems(
                galaxy=galaxy, count=5, min_dist=100, rng=random.Random(seed)
            )

        sig_42 = _canonical_signature(run_once(42))
        sig_43 = _canonical_signature(run_once(43))
        # Sanity check that determinism contract is non-vacuous.
        assert sig_42 != sig_43

    def test_generate_systems_seed_zero_is_deterministic(self):
        def run_once():
            gen = _make_generator(naming=_FakeNamingRegistry(["A", "B", "C"]))
            galaxy = _FakeGalaxy(radius=2000)
            return gen.generate_systems(
                galaxy=galaxy, count=3, min_dist=100, rng=random.Random(0)
            )

        assert _canonical_signature(run_once()) == _canonical_signature(run_once())

    def test_generate_systems_with_rng_none_completes_without_error(self):
        gen = _make_generator()
        galaxy = _FakeGalaxy(radius=2000)
        # Just must not raise. Output is non-deterministic so we only check shape.
        result = gen.generate_systems(galaxy=galaxy, count=2, min_dist=100, rng=None)
        assert isinstance(result, list)
        assert len(result) <= 2


# ---------------------------------------------------------------------------
# GalaxySystemGenerator.generate_systems — saturation / failure counter
# ---------------------------------------------------------------------------


class TestGenerateSystemsSaturation:
    def test_generate_systems_stops_after_max_consecutive_placement_failures(self):
        always_fail = _AlwaysFailPlacementStrategy()
        gen = _make_generator()
        galaxy = _FakeGalaxy(radius=100)

        result = gen.generate_systems(
            galaxy=galaxy,
            count=99,
            min_dist=10,
            placement_strategy=always_fail,
            rng=random.Random(0),
        )

        assert result == []
        # The implementation breaks at >=10 failures, so it calls exactly 10 times.
        assert always_fail.call_count == 10

    def test_generate_systems_returns_fewer_than_count_when_galaxy_saturated(self):
        # Succeed for first 3 placements, then fail forever.
        coords = [HexCoord(0, 0), HexCoord(50, 0), HexCoord(100, 0)]
        strategy = _LimitedSuccessPlacementStrategy(coords)
        gen = _make_generator()
        galaxy = _FakeGalaxy(radius=200)

        result = gen.generate_systems(
            galaxy=galaxy,
            count=10,  # ask for more than is achievable
            min_dist=10,
            placement_strategy=strategy,
            rng=random.Random(0),
        )

        assert len(result) == 3
        assert len(result) < 10

    def test_generate_systems_resets_failure_counter_on_successful_placement(self):
        # Pattern: succeed, fail x9, succeed, fail x10 -> stops after second failure run.
        # Verify by counting actual placements to ensure the second success was
        # accepted (failure counter reset between the two success windows).

        class _PatternStrategy:
            def __init__(self):
                # Pattern: True (success at coord 0,0), False*9, True (50,0), False forever
                pattern = [True] + [False] * 9 + [True] + [False] * 20
                self._pattern = pattern
                self._coords = [HexCoord(0, 0), HexCoord(50, 0)]
                self._success_idx = 0
                self._step = 0

            def sample_location(self, **kwargs):
                if self._step >= len(self._pattern):
                    return None
                ok = self._pattern[self._step]
                self._step += 1
                if ok:
                    coord = self._coords[self._success_idx]
                    self._success_idx += 1
                    return coord
                return None

        strategy = _PatternStrategy()
        gen = _make_generator()
        galaxy = _FakeGalaxy(radius=200)

        result = gen.generate_systems(
            galaxy=galaxy,
            count=10,
            min_dist=10,
            placement_strategy=strategy,
            rng=random.Random(0),
        )

        # Both successes accepted because the failure counter reset after the first.
        assert len(result) == 2


# ---------------------------------------------------------------------------
# GalaxySystemGenerator.generate_systems — parameter behavior
# ---------------------------------------------------------------------------


class TestGenerateSystemsParameters:
    def test_generate_systems_count_zero_returns_empty_list_and_does_not_mutate_galaxy(self):
        gen = _make_generator()
        galaxy = _FakeGalaxy(radius=2000)

        result = gen.generate_systems(
            galaxy=galaxy, count=0, min_dist=100, rng=random.Random(42)
        )

        assert result == []
        assert galaxy.added_systems == []
        assert galaxy.systems == {}

    def test_generate_systems_uses_random_placement_strategy_when_none_provided(self):
        # Verify by passing placement_strategy=None and confirming a system was
        # placed — RandomPlacementStrategy is the only default. We don't probe
        # the type; we verify the default-path code runs.
        gen = _make_generator()
        galaxy = _FakeGalaxy(radius=2000)

        result = gen.generate_systems(
            galaxy=galaxy,
            count=1,
            min_dist=100,
            placement_strategy=None,
            rng=random.Random(42),
        )

        assert len(result) == 1
        assert result[0] in galaxy.added_systems

    def test_generate_systems_uses_default_storm_blueprint_when_storm_gen_present_and_config_none(self):
        storm_gen = _FakeStormGenerator()
        coords = [HexCoord(0, 0), HexCoord(200, 0)]
        gen = _make_generator(storm_generator=storm_gen)
        galaxy = _FakeGalaxy(radius=2000)

        gen.generate_systems(
            galaxy=galaxy,
            count=2,
            min_dist=10,
            placement_strategy=_RecordingPlacementStrategy(coords=coords),
            rng=random.Random(0),
            storm_blueprint_config=None,  # explicit None to trigger default
        )

        # Storm generator was called with the default blueprint.
        assert len(storm_gen.calls) == 2
        config = storm_gen.calls[0][1]
        assert config == {"storms": {"count": {"min": 0, "max": 2}}}

    def test_generate_systems_does_not_use_default_storm_config_when_storm_gen_is_none(self):
        # When storm_gen is None, generate_storms is never called even with config=None.
        # We can verify by checking storm_blueprint_config is not used (no default applied)
        # by injecting a generator without a storm_gen and confirming no AttributeError.
        coords = [HexCoord(0, 0), HexCoord(200, 0)]
        gen = _make_generator(storm_generator=None)
        galaxy = _FakeGalaxy(radius=2000)

        result = gen.generate_systems(
            galaxy=galaxy,
            count=2,
            min_dist=10,
            placement_strategy=_RecordingPlacementStrategy(coords=coords),
            rng=random.Random(0),
            storm_blueprint_config=None,
        )

        # Generation completes with no storms attribute touched on systems.
        assert len(result) == 2
        for sys in result:
            # storms list never mutated by generate_storms.
            assert sys.storms == []


# ---------------------------------------------------------------------------
# GalaxySystemGenerator.generate_systems — dual-RNG seed derivation
# ---------------------------------------------------------------------------


class TestGenerateSystemsDualRng:
    def test_generate_systems_derives_storm_and_intrinsic_seeds_from_parent_rng(self):
        # Verify that the storm_rng + intrinsic_rng are NOT the same object as
        # the parent rng — they are derived child Random instances.
        # We instrument by recording the rng identity passed to placement vs.
        # the rng passed to storm generation.
        recorded = _RecordingPlacementStrategy(coords=[HexCoord(0, 0), HexCoord(200, 0)])
        storm_gen = _FakeStormGenerator()
        gen = _make_generator(storm_generator=storm_gen)
        galaxy = _FakeGalaxy(radius=2000)
        parent_rng = random.Random(42)

        gen.generate_systems(
            galaxy=galaxy,
            count=2,
            min_dist=10,
            placement_strategy=recorded,
            rng=parent_rng,
        )

        # Placement strategy received the PARENT rng (per implementation line 177).
        assert all(r is parent_rng for r in recorded.recorded_rngs)
        # Storm generator received a DIFFERENT rng instance (the derived storm_rng).
        assert len(storm_gen.calls) == 2
        for (_name, _config, storm_rng) in storm_gen.calls:
            assert storm_rng is not parent_rng
            assert isinstance(storm_rng, random.Random)
        # Both storm calls share the same derived storm_rng instance (not re-derived per system).
        unique_storm_rngs = {id(call[2]) for call in storm_gen.calls}
        assert len(unique_storm_rngs) == 1
