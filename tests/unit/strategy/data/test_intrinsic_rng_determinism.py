"""PROJ-301/302/303/304: seeded-RNG determinism tests for the four
intrinsic-ability generation helpers. Closes the skeptical-review finding
that all four generators previously used unseeded `random.Random()`."""
import random

from game.strategy.data.galaxy_system_generator import (
    _apply_planet_intrinsic_abilities,
    _apply_star_intrinsic_abilities,
    _apply_system_archetype,
)
from game.strategy.data.galaxy_warp_generator import _apply_warp_point_intrinsic_abilities


class _FakePlanetType:
    def __init__(self, name): self.name = name


class _FakePlanet:
    def __init__(self, type_name):
        self.planet_type = _FakePlanetType(type_name)
        self.intrinsic_abilities = {}


class _FakeStarType:
    def __init__(self, name): self.name = name


class _FakeStar:
    def __init__(self, type_name):
        self.star_type = _FakeStarType(type_name)
        self.intrinsic_abilities = {}


class _FakeWarpPoint:
    def __init__(self):
        self.warp_type = 'stable'
        self.intrinsic_abilities = {}


class _FakeSystem:
    def __init__(self):
        self.warp_points = [_FakeWarpPoint(), _FakeWarpPoint(), _FakeWarpPoint()]
        self.archetype = None
        self.intrinsic_abilities = {}


def test_planet_intrinsic_rolls_deterministic_with_seeded_rng():
    """Same seed → same intrinsic ability values across two runs."""
    planets1 = [_FakePlanet('MAGMA'), _FakePlanet('CRYOPLANET'), _FakePlanet('JOVIAN')]
    planets2 = [_FakePlanet('MAGMA'), _FakePlanet('CRYOPLANET'), _FakePlanet('JOVIAN')]
    _apply_planet_intrinsic_abilities(planets1, rng=random.Random(42))
    _apply_planet_intrinsic_abilities(planets2, rng=random.Random(42))
    for p1, p2 in zip(planets1, planets2):
        assert p1.intrinsic_abilities == p2.intrinsic_abilities


def test_star_intrinsic_rolls_deterministic_with_seeded_rng():
    stars1 = [_FakeStar('NEUTRON_STAR'), _FakeStar('BLUE_GIANT')]
    stars2 = [_FakeStar('NEUTRON_STAR'), _FakeStar('BLUE_GIANT')]
    _apply_star_intrinsic_abilities(stars1, rng=random.Random(42))
    _apply_star_intrinsic_abilities(stars2, rng=random.Random(42))
    for s1, s2 in zip(stars1, stars2):
        assert s1.intrinsic_abilities == s2.intrinsic_abilities


def test_warp_point_intrinsic_rolls_deterministic_with_seeded_rng():
    systems1 = [_FakeSystem()]
    systems2 = [_FakeSystem()]
    _apply_warp_point_intrinsic_abilities(systems1, rng=random.Random(42))
    _apply_warp_point_intrinsic_abilities(systems2, rng=random.Random(42))
    for sys1, sys2 in zip(systems1, systems2):
        for wp1, wp2 in zip(sys1.warp_points, sys2.warp_points):
            assert wp1.warp_type == wp2.warp_type
            assert wp1.intrinsic_abilities == wp2.intrinsic_abilities


def test_system_archetype_rolls_deterministic_with_seeded_rng():
    sys1 = _FakeSystem()
    sys2 = _FakeSystem()
    _apply_system_archetype(sys1, random.Random(42))
    _apply_system_archetype(sys2, random.Random(42))
    assert sys1.archetype == sys2.archetype
    assert sys1.intrinsic_abilities == sys2.intrinsic_abilities


def test_different_seeds_produce_different_rolls():
    """Sanity check — RNG actually drives the rolls."""
    planets1 = [_FakePlanet('MAGMA') for _ in range(20)]
    planets2 = [_FakePlanet('MAGMA') for _ in range(20)]
    _apply_planet_intrinsic_abilities(planets1, rng=random.Random(1))
    _apply_planet_intrinsic_abilities(planets2, rng=random.Random(999))
    # MAGMA rolls EnvironmentalDamage rate in [0.1, 0.5]; over 20 rolls
    # the two seeded streams will produce different first-rolls.
    rates1 = [p.intrinsic_abilities.get('EnvironmentalDamage', {}).get('rate') for p in planets1]
    rates2 = [p.intrinsic_abilities.get('EnvironmentalDamage', {}).get('rate') for p in planets2]
    assert rates1 != rates2
